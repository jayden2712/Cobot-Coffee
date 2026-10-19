from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
)

from pages.animations import PouringAnimation
from typography import BODY, DISPLAY, LABEL, TITLE, make_font

STAGES = ("MILK READY", "COBOT POURING", "COLLECT CUP")
POURING_STAGE = 1


class RunningPage(QWidget):
    """The cobot is pouring. Shows where the order is and how to stay safe."""

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("runningPage")
        self.selected_art = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(52, 12, 52, 16)
        main_layout.setSpacing(8)

        main_layout.addStretch(1)

        eyebrow = QLabel("LATTE ART IN PROGRESS")
        eyebrow.setObjectName("runningEyebrow")
        eyebrow.setAlignment(Qt.AlignCenter)
        eyebrow.setFont(make_font(LABEL, bold=True))
        main_layout.addWidget(eyebrow)

        self.pour_animation = PouringAnimation(width=280, height=160)
        animation_row = QHBoxLayout()
        animation_row.addStretch()
        animation_row.addWidget(self.pour_animation)
        animation_row.addStretch()
        main_layout.addLayout(animation_row)

        self.selected_art_label = QLabel("POURING...")
        self.selected_art_label.setObjectName("runningTitle")
        self.selected_art_label.setAlignment(Qt.AlignCenter)
        self.selected_art_label.setFont(make_font(DISPLAY, bold=True))
        main_layout.addWidget(self.selected_art_label)

        # ---------------------------------------------------------
        # Where the order is
        # ---------------------------------------------------------
        stage_row = QHBoxLayout()
        stage_row.setSpacing(10)
        stage_row.addStretch()

        self.stage_chips = []
        for index, text in enumerate(STAGES):
            chip = QLabel(text)
            chip.setObjectName("phaseChip")
            chip.setAlignment(Qt.AlignCenter)
            chip.setFixedHeight(38)
            chip.setMinimumWidth(190)
            chip.setFont(make_font(LABEL, bold=True))
            chip.setProperty("state", _stage_state(index, POURING_STAGE))
            stage_row.addWidget(chip)
            self.stage_chips.append(chip)

        stage_row.addStretch()
        main_layout.addLayout(stage_row)

        # ---------------------------------------------------------
        # Progress
        # ---------------------------------------------------------
        progress_row = QHBoxLayout()
        progress_row.setSpacing(12)
        progress_row.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("pourProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedSize(480, 22)

        self.progress_text = QLabel("0%")
        self.progress_text.setObjectName("progressText")
        self.progress_text.setFixedWidth(70)
        self.progress_text.setFont(make_font(TITLE, bold=True))

        progress_row.addWidget(self.progress_bar)
        progress_row.addWidget(self.progress_text)
        progress_row.addStretch()
        main_layout.addLayout(progress_row)

        warning = QLabel("Please keep hands clear while the cobot is moving")
        warning.setObjectName("runningWarning")
        warning.setAlignment(Qt.AlignCenter)
        warning.setFont(make_font(LABEL, bold=True))
        main_layout.addWidget(warning)

        main_layout.addSpacing(4)

        # ---------------------------------------------------------
        # Cancel is intentionally visually weaker than E-stop.
        # POUR FINISHED is for staff while the GUI does not drive
        # the cobot (config.MANUAL_POUR_CONFIRM).
        # ---------------------------------------------------------
        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setFixedSize(260, 62)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setFont(make_font(BODY, bold=True))
        self.cancel_button.clicked.connect(
            self.main_window.cancel_operation
        )

        self.finished_button = QPushButton("POUR FINISHED")
        self.finished_button.setObjectName("secondaryActionButton")
        self.finished_button.setFixedSize(300, 62)
        self.finished_button.setCursor(Qt.PointingHandCursor)
        self.finished_button.setFont(make_font(BODY, bold=True))
        self.finished_button.clicked.connect(
            self.main_window.complete_operation
        )

        button_row = QHBoxLayout()
        button_row.setSpacing(16)
        button_row.addStretch()
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.finished_button)
        button_row.addStretch()
        main_layout.addLayout(button_row)

        main_layout.addStretch(1)

        self.set_manual(False)

    def set_manual(self, manual: bool):
        """Manual: the real pour length is unknown, so show a busy bar."""
        self.finished_button.setVisible(manual)
        self.progress_text.setVisible(not manual)
        self.progress_bar.setRange(0, 0 if manual else 100)
        self.pour_animation.indeterminate = manual

    def set_selected_art(self, art_name):
        self.selected_art = art_name
        self.selected_art_label.setText(
            f"POURING {art_name.upper()}"
        )
        self.set_progress(0)

    def set_progress(self, value):
        value = max(0, min(100, int(value)))
        if self.progress_bar.maximum() > 0:
            self.progress_bar.setValue(value)
        self.progress_text.setText(f"{value}%")
        self.pour_animation.set_progress(value / 100)


def _stage_state(index, current):
    if index < current:
        return "done"
    if index == current:
        return "active"
    return "todo"
