"""Idle screen that draws people in the queue over to the cart.

Shown after the Home page sits untouched for a while. Any touch returns
to Home.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from pages.animations import BreathingOpacity, SteamingCup
from typography import BODY, DISPLAY, HEADLINE, LABEL, make_font


class AttractPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("attractPage")
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 16, 40, 24)
        layout.setSpacing(10)
        layout.addStretch(1)

        cup_row = QHBoxLayout()
        cup_row.addStretch()
        cup_row.addWidget(SteamingCup(size=190))
        cup_row.addStretch()
        layout.addLayout(cup_row)

        title = QLabel("LATTE ART, POURED BY A ROBOT")
        title.setObjectName("completeTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(make_font(DISPLAY, bold=True))
        layout.addWidget(title)

        subtitle = QLabel("Watch the cobot pour, or take the Latte Challenge yourself.")
        subtitle.setObjectName("heroSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(make_font(BODY))
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        self.touch_label = QLabel("TOUCH ANYWHERE TO START")
        self.touch_label.setObjectName("attractTouch")
        self.touch_label.setAlignment(Qt.AlignCenter)
        self.touch_label.setFont(make_font(HEADLINE, bold=True))
        self.touch_breath = BreathingOpacity(self.touch_label)
        layout.addWidget(self.touch_label)

        layout.addStretch(1)

        self.stats_label = QLabel()
        self.stats_label.setObjectName("attractStats")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setFont(make_font(LABEL, bold=True))
        layout.addWidget(self.stats_label)

    def show_stats(self, total_pours: int, top_score):
        parts = [f"{total_pours} LATTES POURED TODAY"]
        if top_score is not None:
            art, score = top_score
            parts.append(f"TODAY'S BEST LATTE CHALLENGE: {score} ON {art.upper()}")
        self.stats_label.setText("   ·   ".join(parts))

    def showEvent(self, event):
        super().showEvent(event)
        self.touch_breath.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.touch_breath.stop()

    def mousePressEvent(self, event):
        self.main_window.show_home_page()
