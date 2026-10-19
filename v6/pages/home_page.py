from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

from config import ASSETS_DIR
from pages.animations import ANIMATIONS_ENABLED, GlowPulse
from typography import BODY, CAPTION, DISPLAY, LABEL, TITLE, make_font

HINT_SECONDS = 4
STAFF_SLOT_WIDTH = 120


class HomePage(QWidget):
    """Customer-facing home screen: the three ways to get a latte."""

    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("homePage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(36, 10, 24, 12)
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
        logo_pixmap = QPixmap(str(logo_path))

        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(
                logo_pixmap.scaled(
                    450,
                    160,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
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

        main_layout.addSpacing(16)

        # =========================================================
        # PRIMARY ACTION: COBOT POUR
        # =========================================================
        primary_row = QHBoxLayout()
        primary_row.addStretch()

        self.start_button = QPushButton(
            "START POUR\nThe cobot pours your art"
        )
        self.start_button.setObjectName("startButton")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setFixedSize(470, 104)
        self.start_button.setFont(make_font(TITLE, bold=True))
        self.start_button.clicked.connect(
            self.main_window.show_art_selection_page
        )
        self.start_glow = GlowPulse(self.start_button)

        primary_row.addWidget(self.start_button)
        primary_row.addStretch()
        main_layout.addLayout(primary_row)

        main_layout.addSpacing(14)

        # =========================================================
        # OTHER WAYS TO POUR
        # =========================================================
        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(14)
        secondary_row.addStretch()

        self.teleop_button = QPushButton(
            "LATTE CHALLENGE\nPour your own art"
        )
        self.barista_button = QPushButton(
            "BARISTA POUR\nPoured by our barista"
        )

        secondary_font = make_font(LABEL, bold=True)
        for button in (self.teleop_button, self.barista_button):
            button.setObjectName("secondaryActionButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setFixedSize(260, 88)
            button.setFont(secondary_font)
            secondary_row.addWidget(button)

        self.teleop_button.clicked.connect(
            self.main_window.show_teleop_setup_page
        )
        self.barista_button.clicked.connect(
            self.main_window.show_barista_page
        )

        secondary_row.addStretch()
        main_layout.addLayout(secondary_row)

        main_layout.addStretch(1)

        # =========================================================
        # FOOTER: ROTATING HINT + STAFF ACCESS
        # =========================================================
        footer = QHBoxLayout()

        left_slot = QWidget()
        left_slot.setFixedWidth(STAFF_SLOT_WIDTH)

        self.home_hint = QLabel()
        self.home_hint.setObjectName("homeHint")
        self.home_hint.setAlignment(Qt.AlignCenter)
        self.home_hint.setFont(make_font(CAPTION + 1))

        self.hint_effect = QGraphicsOpacityEffect(self.home_hint)
        self.home_hint.setGraphicsEffect(self.hint_effect)
        self.hint_fade = QPropertyAnimation(self.hint_effect, b"opacity", self)
        self.hint_fade.setDuration(500)
        self.hint_fade.setStartValue(0.0)
        self.hint_fade.setEndValue(1.0)
        self.hint_fade.setEasingCurve(QEasingCurve.OutCubic)

        # System status is for staff, so it sits small in the corner.
        self.staff_button = QPushButton("STAFF")
        self.staff_button.setObjectName("staffButton")
        self.staff_button.setCursor(Qt.PointingHandCursor)
        self.staff_button.setFixedSize(STAFF_SLOT_WIDTH, 40)
        self.staff_button.setFont(make_font(CAPTION, bold=True))
        self.staff_button.clicked.connect(
            self.main_window.show_status_page
        )

        footer.addWidget(left_slot)
        footer.addWidget(self.home_hint, 1)
        footer.addWidget(self.staff_button)
        main_layout.addLayout(footer)

        self._hint_index = 0
        self.hint_timer = QTimer(self)
        self.hint_timer.setInterval(HINT_SECONDS * 1000)
        self.hint_timer.timeout.connect(self._next_hint)
        self._show_hint(0)

    # =========================================================
    # ANIMATION LIFECYCLE
    # =========================================================
    def showEvent(self, event):
        super().showEvent(event)
        self.start_glow.start()
        if ANIMATIONS_ENABLED:
            self.hint_timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.start_glow.stop()
        self.hint_timer.stop()

    # =========================================================
    # ROTATING HINT
    # =========================================================
    def _hints(self):
        hints = [
            "Touch START POUR to begin",
            "Try the Latte Challenge and pour your own art",
            "Prefer a person? Choose Barista pour",
        ]

        top = self.main_window.top_challenge_score()
        if top is not None:
            art, score = top
            hints.insert(1, f"Today's best Latte Challenge: {score} on {art.title()}")

        return hints

    def _next_hint(self):
        self._show_hint(self._hint_index + 1)

    def _show_hint(self, index):
        hints = self._hints()
        self._hint_index = index % len(hints)
        self.home_hint.setText(hints[self._hint_index])

        if ANIMATIONS_ENABLED:
            self.hint_fade.stop()
            self.hint_fade.start()

    def _use_text_logo_fallback(self):
        self.logo_label.setText("CoBotics")
        self.logo_label.setFont(make_font(DISPLAY + 8, bold=True))
