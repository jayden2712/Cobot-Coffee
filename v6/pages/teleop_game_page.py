"""The live teleop pour: cup on the left, coaching and meters on the right."""

from PySide6.QtCore import QElapsedTimer, Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pages.pour_canvas import PourCanvas
from teleop.challenges import (
    PHASE_BASE,
    PHASE_LABELS,
    PHASES,
    Challenge,
    art_path,
    guide_at,
)
from teleop.jug import JugController, apply_flow_assist
from teleop.scoring import PourStats, add_sample, fill_ratio, is_on_target
from typography import BODY, HEADLINE, LABEL, TITLE, make_font

TICK_MS = 33
MAX_TICK_SECONDS = 0.1
COUNTDOWN_STEPS = ("3", "2", "1", "POUR!")
COUNTDOWN_STEP_MS = 700


class TeleopGamePage(QWidget):
    def __init__(self, main_window, controller: JugController):
        super().__init__()

        self.main_window = main_window
        self.controller = controller
        self.setObjectName("teleopGamePage")

        self.challenge = None
        self.stats = PourStats()
        self._last_elapsed = 0.0
        self._countdown_index = 0

        self.tick_timer = QTimer(self)
        self.tick_timer.setInterval(TICK_MS)
        self.tick_timer.timeout.connect(self._tick)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(COUNTDOWN_STEP_MS)
        self.countdown_timer.timeout.connect(self._advance_countdown)

        self.clock = QElapsedTimer()

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(28, 14, 32, 14)
        main_layout.setSpacing(28)

        # -------------------------------------------------
        # Cup
        # -------------------------------------------------
        self.canvas = PourCanvas(size=470)
        self.canvas.pointer_changed.connect(self._on_pointer)
        main_layout.addWidget(self.canvas, alignment=Qt.AlignVCenter)

        # -------------------------------------------------
        # Coaching panel
        # -------------------------------------------------
        panel = QVBoxLayout()
        panel.setSpacing(8)

        self.level_label = QLabel()
        self.level_label.setObjectName("gameEyebrow")
        self.level_label.setFont(make_font(LABEL, bold=True))
        panel.addWidget(self.level_label)

        self.art_label = QLabel()
        self.art_label.setObjectName("pageTitle")
        self.art_label.setFont(make_font(HEADLINE + 4, bold=True))
        panel.addWidget(self.art_label)

        phase_row = QHBoxLayout()
        phase_row.setSpacing(8)
        self.phase_chips = {}
        for phase in PHASES:
            chip = QLabel(PHASE_LABELS[phase])
            chip.setObjectName("phaseChip")
            chip.setAlignment(Qt.AlignCenter)
            chip.setFixedHeight(38)
            chip.setFont(make_font(LABEL, bold=True))
            chip.setProperty("state", "todo")
            phase_row.addWidget(chip)
            self.phase_chips[phase] = chip
        panel.addLayout(phase_row)

        panel.addSpacing(6)

        self.instruction_label = QLabel()
        self.instruction_label.setObjectName("gameInstruction")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setMinimumHeight(84)
        self.instruction_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.instruction_label.setFont(make_font(HEADLINE, bold=True))
        panel.addWidget(self.instruction_label)

        self.time_label = QLabel()
        self.time_label.setObjectName("gameTime")
        self.time_label.setFont(make_font(BODY, bold=True))
        panel.addWidget(self.time_label)

        panel.addSpacing(4)

        self.accuracy_bar, self.accuracy_value = self._add_meter(panel, "ON TARGET")
        self.fill_bar, self.fill_value = self._add_meter(panel, "CUP FILL")

        panel.addStretch(1)

        self.stop_button = QPushButton("STOP POUR")
        self.stop_button.setObjectName("cancelButton")
        self.stop_button.setFixedHeight(60)
        self.stop_button.setCursor(Qt.PointingHandCursor)
        self.stop_button.setFont(make_font(BODY, bold=True))
        self.stop_button.clicked.connect(self._stop_pressed)
        panel.addWidget(self.stop_button)

        main_layout.addLayout(panel, 1)

    def _add_meter(self, layout, title):
        header = QHBoxLayout()

        name = QLabel(title)
        name.setObjectName("meterName")
        name.setFont(make_font(LABEL, bold=True))

        value = QLabel("0%")
        value.setObjectName("meterValue")
        value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        value.setFont(make_font(TITLE, bold=True))

        header.addWidget(name)
        header.addStretch()
        header.addWidget(value)
        layout.addLayout(header)

        bar = QProgressBar()
        bar.setObjectName("pourProgress")
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        bar.setFixedHeight(20)
        layout.addWidget(bar)

        return bar, value

    # =====================================================
    # Lifecycle
    # =====================================================
    def start(self, challenge: Challenge):
        self.abort()

        self.challenge = challenge
        self.stats = PourStats()
        self._last_elapsed = 0.0
        self.controller.reset()

        self.level_label.setText(
            f"LEVEL {challenge.level}  ·  {challenge.difficulty.upper()}"
        )
        self.art_label.setText(challenge.art_name.upper())
        self.canvas.reset(art_path(challenge), challenge.position_tolerance)
        self._show_guide(guide_at(challenge, 0.0), on_target=False)
        self._set_meters(0.0, 0.0)
        self.time_label.setText(f"{challenge.duration:.0f} s pour")
        self.instruction_label.setText("Get ready. Hold the jug over the cup.")

        self._countdown_index = 0
        self.canvas.set_overlay(COUNTDOWN_STEPS[0])
        self.countdown_timer.start()

    def abort(self):
        """Stop the pour without scoring it (Stop button, E-stop, leaving)."""
        self.countdown_timer.stop()
        self.tick_timer.stop()
        self.clock.invalidate()
        self.canvas.set_overlay("")
        self.controller.reset()

    def _advance_countdown(self):
        self._countdown_index += 1

        if self._countdown_index < len(COUNTDOWN_STEPS):
            self.canvas.set_overlay(COUNTDOWN_STEPS[self._countdown_index])
            return

        self.countdown_timer.stop()
        self.canvas.set_overlay("")
        self.clock.start()
        self.tick_timer.start()

    def _stop_pressed(self):
        self.abort()
        self.main_window.show_teleop_setup_page()

    # =====================================================
    # Game loop
    # =====================================================
    def _on_pointer(self, x, y, pressed):
        if hasattr(self.controller, "set_pointer"):
            self.controller.set_pointer(x, y, pressed)

    def _tick(self):
        if self.challenge is None or not self.clock.isValid():
            return

        challenge = self.challenge
        elapsed = min(self.clock.elapsed() / 1000.0, challenge.duration)
        # A GUI stall must not dump a burst of milk into one tick.
        dt = min(max(0.0, elapsed - self._last_elapsed), MAX_TICK_SECONDS)
        self._last_elapsed = elapsed

        guide = guide_at(challenge, elapsed)
        jug = apply_flow_assist(
            self.controller.read(),
            guide,
            self.controller.is_assisted,
        )

        self.stats = add_sample(
            self.stats, guide, jug, dt, challenge.position_tolerance
        )

        # Milk poured during the base fill sinks under the crema.
        if guide.phase != PHASE_BASE:
            self.canvas.deposit(jug, dt)

        on_target = jug.tilt > 0 and is_on_target(
            guide, jug, challenge.position_tolerance
        )
        self.canvas.set_frame(guide, jug, on_target)
        self._show_guide(guide, on_target)
        self._set_meters(self.stats.steering, fill_ratio(self.stats, challenge))

        remaining = max(0.0, challenge.duration - elapsed)
        self.time_label.setText(f"{remaining:.1f} s left")

        if elapsed >= challenge.duration:
            self._finish()

    def _finish(self):
        self.tick_timer.stop()
        self.clock.invalidate()
        self.controller.reset()
        self.main_window.show_teleop_result(
            self.challenge,
            self.stats,
            self.canvas.art_image(),
        )

    # =====================================================
    # Display
    # =====================================================
    def _show_guide(self, guide, on_target):
        self.instruction_label.setText(guide.instruction)

        current = PHASES.index(guide.phase)
        for index, phase in enumerate(PHASES):
            if index < current:
                state = "done"
            elif index == current:
                state = "active"
            else:
                state = "todo"
            self._set_chip_state(self.phase_chips[phase], state)

    @staticmethod
    def _set_chip_state(chip, state):
        if chip.property("state") == state:
            return

        chip.setProperty("state", state)
        chip.style().unpolish(chip)
        chip.style().polish(chip)

    def _set_meters(self, steering, ratio):
        accuracy = int(round(steering * 100))
        fill = int(round(min(ratio, 1.5) * 100))

        self.accuracy_bar.setValue(accuracy)
        self.accuracy_value.setText(f"{accuracy}%")
        self.fill_bar.setValue(min(fill, 100))
        self.fill_value.setText(f"{fill}%")
