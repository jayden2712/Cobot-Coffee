"""Shown when a customer would rather a person pours their latte."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pages.animations import SteamingCup
from typography import BODY, CAPTION, DISPLAY, LABEL, TITLE, make_font

AUTO_HOME_SECONDS = 15


class BaristaPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("baristaPage")
        self.seconds_remaining = 0

        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(self._tick_countdown)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 14, 50, 18)
        layout.setSpacing(8)
        layout.addStretch(1)

        cup_row = QHBoxLayout()
        cup_row.addStretch()
        cup_row.addWidget(SteamingCup(size=140))
        cup_row.addStretch()
        layout.addLayout(cup_row)

        eyebrow = QLabel("BARISTA POUR")
        eyebrow.setObjectName("completeEyebrow")
        eyebrow.setAlignment(Qt.AlignCenter)
        eyebrow.setFont(make_font(LABEL, bold=True))
        layout.addWidget(eyebrow)

        title = QLabel("OUR BARISTA WILL POUR IT")
        title.setObjectName("completeTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(make_font(DISPLAY, bold=True))
        layout.addWidget(title)

        message = QLabel(
            "Let the barista know, then collect your cup from them."
        )
        message.setObjectName("completeMessage")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setFont(make_font(BODY))
        layout.addWidget(message)

        layout.addSpacing(10)

        self.done_button = QPushButton("DONE")
        self.done_button.setObjectName("homeButton")
        self.done_button.setFixedSize(330, 64)
        self.done_button.setCursor(Qt.PointingHandCursor)
        self.done_button.setFont(make_font(TITLE, bold=True))
        self.done_button.clicked.connect(self._return_home)

        # Backing out does not count as a barista pour.
        self.back_button = QPushButton("BACK")
        self.back_button.setObjectName("secondaryActionButton")
        self.back_button.setFixedSize(180, 64)
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setFont(make_font(BODY, bold=True))
        self.back_button.clicked.connect(self._back)

        button_row = QHBoxLayout()
        button_row.setSpacing(14)
        button_row.addStretch()
        button_row.addWidget(self.back_button)
        button_row.addWidget(self.done_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        self.countdown_label = QLabel()
        self.countdown_label.setObjectName("countdownLabel")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setFont(make_font(CAPTION))
        layout.addWidget(self.countdown_label)

        layout.addStretch(1)

    def start_countdown(self):
        self.seconds_remaining = AUTO_HOME_SECONDS
        self._update_countdown_text()
        self.countdown_timer.start()

    def stop_countdown(self):
        self.countdown_timer.stop()
        self.countdown_label.clear()

    def _tick_countdown(self):
        self.seconds_remaining -= 1
        if self.seconds_remaining <= 0:
            self._return_home()
            return
        self._update_countdown_text()

    def _update_countdown_text(self):
        self.countdown_label.setText(
            f"Returning home in {self.seconds_remaining}s"
        )

    def _return_home(self):
        self.stop_countdown()
        self.main_window.finish_barista_pour()

    def _back(self):
        self.stop_countdown()
        self.main_window.show_home_page()
