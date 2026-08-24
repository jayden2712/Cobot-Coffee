from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        status_layout = QHBoxLayout()
        self.cobot_status = QLabel("COBOT: READY")
        self.connection_status = QLabel("CONNECTION: SIMULATION")
        self.safety_status = QLabel("SAFETY: OK")

        status_layout.addWidget(self.cobot_status)
        status_layout.addStretch()
        status_layout.addWidget(self.connection_status)
        status_layout.addStretch()
        status_layout.addWidget(self.safety_status)
        main_layout.addLayout(status_layout)

        main_layout.addStretch()

        title = QLabel("CoBotics Coffee Cart")
        title.setAlignment(Qt.AlignCenter)
        title_font = title.font()
        title_font.setPointSize(30)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        subtitle = QLabel("Latte Art Cobot Control")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = subtitle.font()
        subtitle_font.setPointSize(16)
        subtitle.setFont(subtitle_font)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(20)

        functions_layout = QHBoxLayout()
        functions_layout.setSpacing(30)

        self.start_button = QPushButton("START\nPOUR")
        self.start_button.setObjectName("startButton")
        self.start_button.setFixedSize(220, 220)

        self.teleop_button = QPushButton("TELE-\nOPERATION")
        self.teleop_button.setObjectName("teleopButton")
        self.teleop_button.setFixedSize(220, 220)

        self.status_button = QPushButton("SYSTEM\nSTATUS")
        self.status_button.setObjectName("statusButton")
        self.status_button.setFixedSize(220, 220)

        for button in (self.start_button, self.teleop_button, self.status_button):
            font = button.font()
            font.setPointSize(20)
            font.setBold(True)
            button.setFont(font)

        self.start_button.clicked.connect(self.main_window.show_art_selection_page)
        self.teleop_button.clicked.connect(lambda: print("TELEOPERATION pressed"))
        self.status_button.clicked.connect(self.main_window.show_status_page)

        functions_layout.addStretch()
        functions_layout.addWidget(self.start_button)
        functions_layout.addWidget(self.teleop_button)
        functions_layout.addWidget(self.status_button)
        functions_layout.addStretch()

        main_layout.addLayout(functions_layout)
        main_layout.addStretch()
