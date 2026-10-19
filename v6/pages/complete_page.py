from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)

from config import ASSETS_DIR
from pages.animations import SuccessCheck
from typography import BODY, CAPTION, DISPLAY, LABEL, TITLE, make_font


class CompletePage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("completePage")
        self.selected_art = None
        self.seconds_remaining = 0

        self.countdown_timer = QTimer(self)
        self.countdown_timer.setInterval(1000)
        self.countdown_timer.timeout.connect(
            self._tick_countdown
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 14, 50, 18)
        main_layout.setSpacing(7)

        main_layout.addStretch(1)

        # ---------------------------------------------------------
        # Success mark
        # ---------------------------------------------------------
        self.success_check = SuccessCheck(size=70)

        success_row = QHBoxLayout()
        success_row.addStretch()
        success_row.addWidget(self.success_check)
        success_row.addStretch()
        main_layout.addLayout(success_row)

        eyebrow = QLabel("OPERATION COMPLETE")
        eyebrow.setObjectName("completeEyebrow")
        eyebrow.setAlignment(Qt.AlignCenter)
        eyebrow.setFont(make_font(LABEL, bold=True))
        main_layout.addWidget(eyebrow)

        title = QLabel("YOUR LATTE IS READY")
        title.setObjectName("completeTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(make_font(DISPLAY, bold=True))
        main_layout.addWidget(title)

        # ---------------------------------------------------------
        # Selected latte art
        # ---------------------------------------------------------
        self.art_icon = QLabel()
        self.art_icon.setObjectName("completeArtIcon")
        self.art_icon.setAlignment(Qt.AlignCenter)
        self.art_icon.setFixedSize(112, 112)

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(self.art_icon)
        icon_row.addStretch()
        main_layout.addLayout(icon_row)

        self.art_name_label = QLabel("LATTE ART")
        self.art_name_label.setObjectName("completeArtName")
        self.art_name_label.setAlignment(Qt.AlignCenter)

        self.art_name_label.setFont(make_font(TITLE, bold=True))
        main_layout.addWidget(self.art_name_label)

        self.message = QLabel("Enjoy your coffee.")
        self.message.setObjectName("completeMessage")
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setFont(make_font(BODY))
        main_layout.addWidget(self.message)

        self.next_time = QLabel(
            "Next time, try the Latte Challenge and pour it yourself."
        )
        self.next_time.setObjectName("runningWarning")
        self.next_time.setAlignment(Qt.AlignCenter)
        self.next_time.setFont(make_font(LABEL, bold=True))
        main_layout.addWidget(self.next_time)

        main_layout.addSpacing(8)

        self.home_button = QPushButton("RETURN HOME")
        self.home_button.setObjectName("homeButton")
        self.home_button.setFixedSize(330, 64)
        self.home_button.setCursor(Qt.PointingHandCursor)
        self.home_button.setFont(make_font(TITLE, bold=True))

        self.home_button.clicked.connect(
            self._return_home_now
        )

        home_row = QHBoxLayout()
        home_row.addStretch()
        home_row.addWidget(self.home_button)
        home_row.addStretch()
        main_layout.addLayout(home_row)

        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("countdownLabel")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setFont(make_font(CAPTION))
        main_layout.addWidget(self.countdown_label)

        main_layout.addStretch(1)

    def set_selected_art(self, art_name):
        self.selected_art = art_name
        self.art_name_label.setText(art_name.upper())
        self.message.setText(
            f"Collect your {art_name} latte from the tray. Enjoy!"
        )

        icon_path = ASSETS_DIR / f"{art_name.lower()}.png"
        pixmap = QPixmap(str(icon_path))

        if not pixmap.isNull():
            self.art_icon.setPixmap(
                pixmap.scaled(
                    88,
                    88,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            self.art_icon.setText("☕")

    def start_countdown(self, seconds=12):
        self.seconds_remaining = max(1, int(seconds))
        self._update_countdown_text()
        self.countdown_timer.start()
        self.success_check.play()

    def stop_countdown(self):
        self.countdown_timer.stop()
        self.countdown_label.clear()

    def _tick_countdown(self):
        self.seconds_remaining -= 1

        if self.seconds_remaining <= 0:
            self.countdown_timer.stop()
            self.countdown_label.clear()
            self.main_window.show_home_page()
            return

        self._update_countdown_text()

    def _update_countdown_text(self):
        self.countdown_label.setText(
            f"Returning home in {self.seconds_remaining}s"
        )

    def _return_home_now(self):
        self.stop_countdown()
        self.main_window.show_home_page()
