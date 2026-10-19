"""Score screen after a teleop pour, with the customer's own latte art."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from teleop.challenges import Challenge, next_challenge
from teleop.scoring import OVERFLOW_RATIO, PourResult
from typography import BODY, CAPTION, HEADLINE, LABEL, SCORE, TITLE, make_font

AUTO_HOME_SECONDS = 30
STAR_ON = "#C9973B"
STAR_OFF = "#DCC8B5"


class TeleopResultPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("teleopResultPage")

        self.challenge = None
        self.seconds_remaining = 0

        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(self._tick_countdown)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(36, 16, 40, 16)
        main_layout.setSpacing(34)

        # -------------------------------------------------
        # The customer's pour
        # -------------------------------------------------
        art_column = QVBoxLayout()
        art_column.setSpacing(6)
        art_column.addStretch()

        self.art_label = QLabel()
        self.art_label.setFixedSize(380, 380)
        self.art_label.setAlignment(Qt.AlignCenter)
        art_column.addWidget(self.art_label)

        art_caption = QLabel("YOUR POUR")
        art_caption.setObjectName("gameEyebrow")
        art_caption.setAlignment(Qt.AlignCenter)
        art_caption.setFont(make_font(LABEL, bold=True))
        art_column.addWidget(art_caption)

        art_column.addStretch()
        main_layout.addLayout(art_column)

        # -------------------------------------------------
        # Score
        # -------------------------------------------------
        panel = QVBoxLayout()
        panel.setSpacing(6)
        panel.addStretch()

        self.level_label = QLabel()
        self.level_label.setObjectName("gameEyebrow")
        self.level_label.setFont(make_font(LABEL, bold=True))
        panel.addWidget(self.level_label)

        score_row = QHBoxLayout()
        score_row.setSpacing(8)

        self.score_label = QLabel("0")
        self.score_label.setObjectName("scoreValue")
        self.score_label.setFont(make_font(SCORE, bold=True))

        out_of = QLabel("/ 100")
        out_of.setObjectName("scoreOutOf")
        out_of.setFont(make_font(TITLE, bold=True))

        self.stars_label = QLabel()
        self.stars_label.setTextFormat(Qt.RichText)
        self.stars_label.setFont(make_font(HEADLINE + 6))

        score_row.addWidget(self.score_label, alignment=Qt.AlignBottom)
        score_row.addWidget(out_of, alignment=Qt.AlignBottom)
        score_row.addStretch()
        score_row.addWidget(self.stars_label, alignment=Qt.AlignVCenter)
        panel.addLayout(score_row)

        self.rank_label = QLabel()
        self.rank_label.setObjectName("rankLabel")
        self.rank_label.setFont(make_font(HEADLINE, bold=True))
        panel.addWidget(self.rank_label)

        self.best_label = QLabel()
        self.best_label.setObjectName("bestLabel")
        self.best_label.setFont(make_font(BODY, bold=True))
        panel.addWidget(self.best_label)

        panel.addSpacing(8)

        self.steering_bar, self.steering_value = self._add_breakdown(
            panel, "STEERING"
        )
        self.flow_bar, self.flow_value = self._add_breakdown(panel, "FLOW")
        self.fill_bar, self.fill_value = self._add_breakdown(panel, "FILL")

        self.tip_label = QLabel()
        self.tip_label.setObjectName("tipLabel")
        self.tip_label.setWordWrap(True)
        self.tip_label.setFont(make_font(BODY))
        panel.addWidget(self.tip_label)

        panel.addSpacing(8)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        self.again_button = self._make_button("TRY AGAIN", "secondaryActionButton")
        self.again_button.clicked.connect(self._try_again)

        self.next_button = self._make_button("NEXT LEVEL", "homeButton")
        self.next_button.clicked.connect(self._next_level)

        self.done_button = self._make_button("DONE", "secondaryActionButton")
        self.done_button.clicked.connect(self._done)

        buttons.addWidget(self.again_button)
        buttons.addWidget(self.next_button)
        buttons.addWidget(self.done_button)
        panel.addLayout(buttons)

        self.countdown_label = QLabel()
        self.countdown_label.setObjectName("countdownLabel")
        self.countdown_label.setFont(make_font(CAPTION))
        panel.addWidget(self.countdown_label)

        panel.addStretch()
        main_layout.addLayout(panel, 1)

    @staticmethod
    def _make_button(text, object_name):
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setFixedHeight(60)
        button.setCursor(Qt.PointingHandCursor)
        button.setFont(make_font(BODY, bold=True))
        return button

    @staticmethod
    def _add_breakdown(layout, title):
        row = QHBoxLayout()
        row.setSpacing(12)

        name = QLabel(title)
        name.setObjectName("meterName")
        name.setFixedWidth(130)
        name.setFont(make_font(LABEL, bold=True))

        bar = QProgressBar()
        bar.setObjectName("pourProgress")
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        bar.setFixedHeight(18)

        value = QLabel("0%")
        value.setObjectName("meterValue")
        value.setFixedWidth(84)
        value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        value.setFont(make_font(BODY, bold=True))

        row.addWidget(name)
        row.addWidget(bar, 1)
        row.addWidget(value)
        layout.addLayout(row)

        return bar, value

    # =====================================================
    # Showing a result
    # =====================================================
    def show_result(
        self,
        challenge: Challenge,
        result: PourResult,
        art: QImage,
        best_score: int,
        is_new_best: bool,
    ):
        self.challenge = challenge

        self.art_label.setPixmap(
            QPixmap.fromImage(art).scaled(
                380, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

        self.level_label.setText(
            f"{challenge.art_name.upper()}  ·  LEVEL {challenge.level}"
        )
        self.score_label.setText(str(result.score))
        self.stars_label.setText(_stars_html(result.stars))
        self.rank_label.setText(result.rank)

        if is_new_best:
            self.best_label.setText(f"New best today: {best_score}")
        else:
            self.best_label.setText(f"Best today: {best_score}")

        for bar, value, fraction in (
            (self.steering_bar, self.steering_value, result.steering),
            (self.flow_bar, self.flow_value, result.flow),
            (self.fill_bar, self.fill_value, result.fill),
        ):
            percent = int(round(fraction * 100))
            bar.setValue(percent)
            value.setText(f"{percent}%")

        self.tip_label.setText(_tip_for(result))
        self.next_button.setVisible(
            next_challenge(challenge) is not None and result.stars >= 2
        )

        self._start_countdown()

    # =====================================================
    # Actions
    # =====================================================
    def stop_countdown(self):
        self.countdown_timer.stop()
        self.countdown_label.clear()

    def _try_again(self):
        self.stop_countdown()
        self.main_window.start_teleop_challenge(self.challenge)

    def _next_level(self):
        self.stop_countdown()
        harder = next_challenge(self.challenge)
        if harder is not None:
            self.main_window.start_teleop_challenge(harder)

    def _done(self):
        self.stop_countdown()
        self.main_window.show_home_page()

    def _start_countdown(self):
        self.seconds_remaining = AUTO_HOME_SECONDS
        self._update_countdown_text()
        self.countdown_timer.start()

    def _tick_countdown(self):
        self.seconds_remaining -= 1

        if self.seconds_remaining <= 0:
            self._done()
            return

        self._update_countdown_text()

    def _update_countdown_text(self):
        self.countdown_label.setText(
            f"Returning home in {self.seconds_remaining}s"
        )


def _stars_html(stars: int) -> str:
    filled = f'<span style="color:{STAR_ON}">{"★" * stars}</span>'
    empty = f'<span style="color:{STAR_OFF}">{"★" * (3 - stars)}</span>'
    return filled + empty


def _tip_for(result: PourResult) -> str:
    """One concrete thing to try next time, from the weakest part of the pour."""
    if result.fill_ratio > OVERFLOW_RATIO:
        return "Tip: the cup overflowed. Tilt back sooner during pauses."

    weakest = min(
        ("steering", result.steering),
        ("flow", result.flow),
        ("fill", result.fill),
        key=lambda item: item[1],
    )[0]

    if result.stars == 3:
        return "Beautiful pour. Try the next level or beat your best."
    if weakest == "steering":
        return "Tip: keep the dot inside the white ring while you pour."
    if weakest == "flow":
        return "Tip: lift off when the ring turns dashed, then pour again."
    return "Tip: keep pouring until the timer ends to fill the cup."
