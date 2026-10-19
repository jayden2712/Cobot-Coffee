from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

from config import ASSETS_DIR
from typography import BODY, CAPTION, DISPLAY, LABEL, TITLE, make_font


class HomePage(QWidget):
    """Clean customer-facing home screen for the CoBotics kiosk."""

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("homePage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 10, 36, 14)
        main_layout.setSpacing(0)

        main_layout.addStretch(1)

        # =========================================================
        # BRAND / HERO
        # =========================================================
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(4)

        self.logo_label = QLabel()
        self.logo_label.setObjectName("homeLogo")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )

        logo_path = ASSETS_DIR / "cobotics_logo1.png"

        if logo_path.exists():
            logo_pixmap = QPixmap(str(logo_path))

            if not logo_pixmap.isNull():
                self.logo_label.setPixmap(
                    logo_pixmap.scaled(
                        470,
                        170,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )
            else:
                self._use_text_logo_fallback()
        else:
            self._use_text_logo_fallback()

        hero_layout.addWidget(
            self.logo_label,
            alignment=Qt.AlignCenter,
        )

        self.hero_subtitle = QLabel(
            "Your latte, crafted by robotics."
        )
        self.hero_subtitle.setObjectName("heroSubtitle")
        self.hero_subtitle.setAlignment(Qt.AlignCenter)

        self.hero_subtitle.setFont(make_font(BODY))

        hero_layout.addWidget(self.hero_subtitle)
        main_layout.addLayout(hero_layout)

        main_layout.addSpacing(18)

        # =========================================================
        # PRIMARY ACTION
        # =========================================================
        primary_row = QHBoxLayout()
        primary_row.addStretch()

        self.start_button = QPushButton(
            "START POUR\nChoose your latte art"
        )
        self.start_button.setObjectName("startButton")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setFixedSize(470, 104)
        self.start_button.setFont(make_font(TITLE, bold=True))

        self.start_button.clicked.connect(
            self.main_window.show_art_selection_page
        )

        primary_row.addWidget(self.start_button)
        primary_row.addStretch()
        main_layout.addLayout(primary_row)

        main_layout.addSpacing(14)

        # =========================================================
        # SECONDARY ACTIONS
        # =========================================================
        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(14)
        secondary_row.addStretch()

        self.teleop_button = QPushButton(
            "LATTE CHALLENGE\nPour your own art"
        )
        self.teleop_button.setObjectName("secondaryActionButton")
        self.teleop_button.setCursor(Qt.PointingHandCursor)
        self.teleop_button.setFixedSize(250, 88)

        self.status_button = QPushButton(
            "SYSTEM STATUS\nView system details"
        )
        self.status_button.setObjectName("secondaryActionButton")
        self.status_button.setCursor(Qt.PointingHandCursor)
        self.status_button.setFixedSize(250, 88)

        secondary_font = make_font(LABEL, bold=True)

        self.teleop_button.setFont(secondary_font)
        self.status_button.setFont(secondary_font)

        self.teleop_button.clicked.connect(
            self.main_window.show_teleop_setup_page
        )
        self.status_button.clicked.connect(
            self.main_window.show_status_page
        )

        secondary_row.addWidget(self.teleop_button)
        secondary_row.addWidget(self.status_button)
        secondary_row.addStretch()

        main_layout.addLayout(secondary_row)

        main_layout.addStretch(1)

        # A lightweight interaction hint replaces the duplicated tagline.
        self.home_hint = QLabel("Touch START POUR to begin")
        self.home_hint.setObjectName("homeHint")
        self.home_hint.setAlignment(Qt.AlignCenter)
        self.home_hint.setFont(make_font(CAPTION))
        main_layout.addWidget(self.home_hint)

    def _use_text_logo_fallback(self):
        self.logo_label.setText("CoBotics")
        self.logo_label.setFont(make_font(DISPLAY + 8, bold=True))
