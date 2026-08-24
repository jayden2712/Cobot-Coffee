from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QToolButton, QVBoxLayout, QHBoxLayout

from config import ASSETS_DIR


class ArtSelectionPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        title = QLabel("SELECT LATTE ART")
        title.setAlignment(Qt.AlignCenter)
        title_font = title.font()
        title_font.setPointSize(30)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        subtitle = QLabel("Choose the pattern you want the cobot to pour")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = subtitle.font()
        subtitle_font.setPointSize(15)
        subtitle.setFont(subtitle_font)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(15)

        art_layout = QHBoxLayout()
        art_layout.setSpacing(30)

        self.heart_button = self.create_art_button("Heart", "heart.png")
        self.tulip_button = self.create_art_button("Tulip", "tulip.png")
        self.rosetta_button = self.create_art_button("Rosetta", "rosetta.png")

        self.heart_button.clicked.connect(lambda: self.main_window.start_selected_art("Heart"))
        self.tulip_button.clicked.connect(lambda: self.main_window.start_selected_art("Tulip"))
        self.rosetta_button.clicked.connect(lambda: self.main_window.start_selected_art("Rosetta"))

        art_layout.addStretch()
        art_layout.addWidget(self.heart_button)
        art_layout.addWidget(self.tulip_button)
        art_layout.addWidget(self.rosetta_button)
        art_layout.addStretch()

        main_layout.addLayout(art_layout)
        main_layout.addStretch()

        self.back_button = QPushButton("BACK")
        self.back_button.setObjectName("backButton")
        self.back_button.setMinimumHeight(65)
        back_font = self.back_button.font()
        back_font.setPointSize(17)
        back_font.setBold(True)
        self.back_button.setFont(back_font)
        self.back_button.clicked.connect(self.main_window.show_home_page)
        main_layout.addWidget(self.back_button)

    def create_art_button(self, art_name, icon_filename):
        button = QToolButton()
        button.setObjectName("artButton")
        button.setText(art_name)
        button.setFixedSize(220, 220)
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        font = button.font()
        font.setPointSize(19)
        font.setBold(True)
        button.setFont(font)

        icon_path = ASSETS_DIR / icon_filename
        if icon_path.exists():
            button.setIcon(QIcon(str(icon_path)))
            button.setIconSize(QSize(125, 125))

        return button
