from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class CompletePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        status_layout = QHBoxLayout()
        cobot_status = QLabel("COBOT: READY")
        connection_status = QLabel("CONNECTION: SIMULATION")
        safety_status = QLabel("SAFETY: OK")

        status_layout.addWidget(cobot_status)
        status_layout.addStretch()
        status_layout.addWidget(connection_status)
        status_layout.addStretch()
        status_layout.addWidget(safety_status)
        main_layout.addLayout(status_layout)
        main_layout.addStretch()

        complete_title = QLabel("OPERATION COMPLETE")
        complete_title.setAlignment(Qt.AlignCenter)
        title_font = complete_title.font()
        title_font.setPointSize(34)
        title_font.setBold(True)
        complete_title.setFont(title_font)
        main_layout.addWidget(complete_title)

        self.message = QLabel("Your coffee is ready!")
        self.message.setAlignment(Qt.AlignCenter)
        message_font = self.message.font()
        message_font.setPointSize(22)
        self.message.setFont(message_font)
        main_layout.addWidget(self.message)
        main_layout.addSpacing(40)

        self.home_button = QPushButton("RETURN HOME")
        self.home_button.setObjectName("homeButton")
        self.home_button.setMinimumHeight(80)
        home_font = self.home_button.font()
        home_font.setPointSize(20)
        home_font.setBold(True)
        self.home_button.setFont(home_font)
        self.home_button.clicked.connect(self.main_window.show_home_page)
        main_layout.addWidget(self.home_button)
        main_layout.addStretch()

    def set_selected_art(self, art_name):
        self.message.setText(f"Your {art_name} latte art is ready!")
