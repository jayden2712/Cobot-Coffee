"""Level picker and how-to for the teleop latte challenge."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import ASSETS_DIR
from teleop.challenges import CHALLENGES, Challenge
from typography import BODY, CAPTION, DISPLAY, HEADLINE, LABEL, TITLE, make_font

HOW_TO_STEPS = (
    "Touch the cup to pour",
    "Stay in the ring",
    "Lift off to pause",
)


class LevelCard(QPushButton):
    """A tappable card for one challenge level."""

    def __init__(self, challenge: Challenge, parent=None):
        super().__init__(parent)
        self.challenge = challenge
        self.setObjectName("levelCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(288, 262)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 14)
        layout.setSpacing(4)

        level = QLabel(f"LEVEL {challenge.level}")
        level.setObjectName("levelEyebrow")
        level.setAlignment(Qt.AlignCenter)
        level.setFont(make_font(LABEL, bold=True))

        icon = QLabel()
        icon.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(str(ASSETS_DIR / challenge.icon))
        if not pixmap.isNull():
            icon.setPixmap(
                pixmap.scaled(104, 104, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        name = QLabel(challenge.art_name.upper())
        name.setObjectName("levelName")
        name.setAlignment(Qt.AlignCenter)
        name.setFont(make_font(TITLE + 2, bold=True))

        difficulty = QLabel(challenge.difficulty)
        difficulty.setObjectName("stepText")
        difficulty.setAlignment(Qt.AlignCenter)
        difficulty.setFont(make_font(BODY))

        self.best_label = QLabel()
        self.best_label.setObjectName("levelBest")
        self.best_label.setAlignment(Qt.AlignCenter)
        self.best_label.setFont(make_font(CAPTION, bold=True))

        for child in (level, icon, name, difficulty, self.best_label):
            child.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(child)

        self.set_best(None)

    def set_best(self, best_score):
        if best_score is None:
            self.best_label.setText("No pours yet today")
        else:
            self.best_label.setText(f"Best today: {best_score}")


class TeleopSetupPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("teleopSetupPage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 12, 32, 18)
        main_layout.setSpacing(8)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------
        header = QHBoxLayout()

        back_button = QPushButton("←")
        back_button.setObjectName("pageBackButton")
        back_button.setFixedSize(54, 54)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setFont(make_font(HEADLINE, bold=True))
        back_button.clicked.connect(self.main_window.show_home_page)

        title = QLabel("LATTE CHALLENGE")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(make_font(DISPLAY, bold=True))

        spacer = QWidget()
        spacer.setFixedSize(54, 54)

        header.addWidget(back_button)
        header.addWidget(title, 1)
        header.addWidget(spacer)
        main_layout.addLayout(header)

        subtitle = QLabel("Steer the jug and the cobot copies your pour.")
        subtitle.setObjectName("heroSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(make_font(BODY))
        main_layout.addWidget(subtitle)

        main_layout.addStretch(1)

        # -------------------------------------------------
        # Level cards
        # -------------------------------------------------
        cards_row = QHBoxLayout()
        cards_row.setSpacing(18)
        cards_row.addStretch()

        self.cards = []
        for challenge in CHALLENGES:
            card = LevelCard(challenge)
            card.clicked.connect(
                lambda _=False, c=challenge: self.main_window.start_teleop_challenge(c)
            )
            cards_row.addWidget(card)
            self.cards.append(card)

        cards_row.addStretch()
        main_layout.addLayout(cards_row)

        main_layout.addStretch(1)

        # -------------------------------------------------
        # How to play
        # -------------------------------------------------
        steps_row = QHBoxLayout()
        steps_row.setSpacing(22)
        steps_row.addStretch()

        for number, text in enumerate(HOW_TO_STEPS, start=1):
            badge = QLabel(str(number))
            badge.setObjectName("stepBadge")
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(34, 34)
            badge.setFont(make_font(LABEL, bold=True))

            label = QLabel(text)
            label.setObjectName("stepText")
            label.setFont(make_font(BODY))

            steps_row.addWidget(badge)
            steps_row.addWidget(label)

        steps_row.addStretch()
        main_layout.addLayout(steps_row)

    def refresh_best_scores(self, best_scores: dict):
        for card in self.cards:
            card.set_best(best_scores.get(card.challenge.key))
