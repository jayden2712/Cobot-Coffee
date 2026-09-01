from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)

from config import ASSETS_DIR


class HomePage(QWidget):
    """
    CoBotics home page.

    Visual direction:
    - Warm cream background
    - Espresso / latte brand palette
    - Large central CoBotics logo
    - One clear primary CTA: START POUR
    - Smaller technical secondary actions
    - Compact status chips at the top
    """

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("homePage")

        # =========================================================
        # ROOT LAYOUT
        # =========================================================
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(34, 20, 34, 22)
        main_layout.setSpacing(0)

        # =========================================================
        # TOP STATUS BAR
        # =========================================================
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(12)

        self.cobot_status = self._make_status_chip(
            "●  COBOT READY",
            "readyStatusChip",
        )

        self.connection_status = self._make_status_chip(
            "●  SIMULATION",
            "simulationStatusChip",
        )

        self.safety_status = self._make_status_chip(
            "●  SAFETY OK",
            "readyStatusChip",
        )

        status_layout.addWidget(self.cobot_status)
        status_layout.addStretch()
        status_layout.addWidget(self.connection_status)
        status_layout.addStretch()
        status_layout.addWidget(self.safety_status)

        main_layout.addLayout(status_layout)

        # Flexible top breathing room
        main_layout.addStretch(1)

        # =========================================================
        # BRAND / HERO
        # =========================================================
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(8)

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
                        585,
                        265,
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

        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_font.setWeight(QFont.Medium)
        self.hero_subtitle.setFont(subtitle_font)

        hero_layout.addWidget(self.hero_subtitle)

        main_layout.addLayout(hero_layout)

        # Space between branding and CTA
        main_layout.addSpacing(24)

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
        self.start_button.setFixedSize(440, 108)

        start_font = QFont()
        start_font.setPointSize(18)
        start_font.setBold(True)
        self.start_button.setFont(start_font)

        self.start_button.clicked.connect(
            self.main_window.show_art_selection_page
        )

        primary_row.addWidget(self.start_button)
        primary_row.addStretch()

        main_layout.addLayout(primary_row)

        # =========================================================
        # SECONDARY ACTIONS
        # =========================================================
        main_layout.addSpacing(18)

        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(18)
        secondary_row.addStretch()

        self.teleop_button = QPushButton(
            "TELEOPERATION\nManual robot control"
        )
        self.teleop_button.setObjectName("secondaryActionButton")
        self.teleop_button.setCursor(Qt.PointingHandCursor)
        self.teleop_button.setFixedSize(210, 92)

        self.status_button = QPushButton(
            "SYSTEM STATUS\nView system details"
        )
        self.status_button.setObjectName("secondaryActionButton")
        self.status_button.setCursor(Qt.PointingHandCursor)
        self.status_button.setFixedSize(210, 92)

        secondary_font = QFont()
        secondary_font.setPointSize(12)
        secondary_font.setBold(True)

        self.teleop_button.setFont(secondary_font)
        self.status_button.setFont(secondary_font)

        self.teleop_button.clicked.connect(
            lambda: print("TELEOPERATION pressed")
        )

        self.status_button.clicked.connect(
            self.main_window.show_status_page
        )

        secondary_row.addWidget(self.teleop_button)
        secondary_row.addWidget(self.status_button)
        secondary_row.addStretch()

        main_layout.addLayout(secondary_row)

        main_layout.addStretch(1)

        # =========================================================
        # FOOTER
        # =========================================================
        footer_row = QHBoxLayout()

        footer_line_left = QFrame()
        footer_line_left.setObjectName("footerLine")
        footer_line_left.setFrameShape(QFrame.HLine)
        footer_line_left.setFixedWidth(90)

        footer_line_right = QFrame()
        footer_line_right.setObjectName("footerLine")
        footer_line_right.setFrameShape(QFrame.HLine)
        footer_line_right.setFixedWidth(90)

        self.footer_label = QLabel("COFFEE. INNOVATED.")
        self.footer_label.setObjectName("brandTagline")
        self.footer_label.setAlignment(Qt.AlignCenter)

        footer_font = QFont()
        footer_font.setPointSize(9)
        footer_font.setBold(True)
        self.footer_label.setFont(footer_font)

        footer_row.addStretch()
        footer_row.addWidget(footer_line_left)
        footer_row.addSpacing(12)
        footer_row.addWidget(self.footer_label)
        footer_row.addSpacing(12)
        footer_row.addWidget(footer_line_right)
        footer_row.addStretch()

        main_layout.addLayout(footer_row)

        # =========================================================
        # PAGE STYLE
        # =========================================================
        self.setStyleSheet(
            """
            QWidget#homePage {
                background-color: #F8EFE5;
            }

            /* -------------------------------------------------
               STATUS CHIPS
               ------------------------------------------------- */
            QLabel#readyStatusChip,
            QLabel#simulationStatusChip {
                border-radius: 15px;
                padding: 7px 13px;
                font-size: 12px;
                font-weight: 700;
            }

            QLabel#readyStatusChip {
                background-color: #E9E1D6;
                color: #4D6A4B;
                border: 1px solid #D4C7B8;
            }

            QLabel#simulationStatusChip {
                background-color: #EADBCB;
                color: #7A5538;
                border: 1px solid #D2BDA7;
            }

            /* -------------------------------------------------
               HERO
               ------------------------------------------------- */
            QLabel#homeLogo {
                background: transparent;
            }

            QLabel#heroSubtitle {
                color: #7C6A5A;
            }

            /* -------------------------------------------------
               PRIMARY CTA
               ------------------------------------------------- */
            QPushButton#startButton {
                background-color: #3A2616;
                color: #FFFDFC;

                border: 2px solid #3A2616;
                border-radius: 24px;

                padding: 14px 24px;
            }

            QPushButton#startButton:hover {
                background-color: #5A3B25;
                border-color: #5A3B25;
            }

            QPushButton#startButton:pressed {
                background-color: #2F1E12;
                border-color: #2F1E12;
                padding-top: 17px;
                padding-bottom: 11px;
            }

            /* -------------------------------------------------
               SECONDARY ACTIONS
               ------------------------------------------------- */
            QPushButton#secondaryActionButton {
                background-color: #FFFDFC;
                color: #3A2616;

                border: 2px solid #D2BDA7;
                border-radius: 20px;

                padding: 10px 16px;
            }

            QPushButton#secondaryActionButton:hover {
                background-color: #EADBCB;
                border-color: #B89067;
            }

            QPushButton#secondaryActionButton:pressed {
                background-color: #DFC9B4;
                border-color: #B89067;
                padding-top: 12px;
                padding-bottom: 8px;
            }

            /* -------------------------------------------------
               FOOTER
               ------------------------------------------------- */
            QLabel#brandTagline {
                color: #B89067;
                letter-spacing: 2px;
            }

            QFrame#footerLine {
                border: none;
                background-color: #B89067;
                max-height: 1px;
                min-height: 1px;
            }
            """
        )

    # =========================================================
    # HELPERS
    # =========================================================
    def _make_status_chip(self, text, object_name):
        label = QLabel(text)
        label.setObjectName(object_name)
        label.setAlignment(Qt.AlignCenter)

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        label.setFont(font)

        return label

    def _use_text_logo_fallback(self):
        """
        Used when assets/cobotics_logo.png does not exist.
        The application still remains usable instead of showing
        an empty hero area.
        """
        self.logo_label.setText("CoBotics")

        fallback_font = QFont()
        fallback_font.setPointSize(42)
        fallback_font.setBold(True)

        self.logo_label.setFont(fallback_font)
        self.logo_label.setStyleSheet(
            "color: #2F1E12; background: transparent;"
        )

    # =========================================================
    # OPTIONAL STATUS UPDATE METHODS
    # =========================================================
    def set_cobot_status(self, text):
        self.cobot_status.setText(f"●  COBOT {text.upper()}")

    def set_connection_status(self, text):
        self.connection_status.setText(f"●  {text.upper()}")

    def set_safety_status(self, text):
        self.safety_status.setText(f"●  SAFETY {text.upper()}")
