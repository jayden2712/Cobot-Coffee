from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class RunningPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        status_layout = QHBoxLayout()
        cobot_status = QLabel("COBOT: RUNNING")
        connection_status = QLabel("CONNECTION: SIMULATION")
        safety_status = QLabel("SAFETY: OK")

        status_layout.addWidget(cobot_status)
        status_layout.addStretch()
        status_layout.addWidget(connection_status)
        status_layout.addStretch()
        status_layout.addWidget(safety_status)
        main_layout.addLayout(status_layout)
        main_layout.addStretch()

        self.selected_art_label = QLabel("POURING...")
        self.selected_art_label.setAlignment(Qt.AlignCenter)
        running_font = self.selected_art_label.font()
        running_font.setPointSize(36)
        running_font.setBold(True)
        self.selected_art_label.setFont(running_font)
        main_layout.addWidget(self.selected_art_label)

        info = QLabel("The cobot is performing the latte art operation")
        info.setAlignment(Qt.AlignCenter)
        info_font = info.font()
        info_font.setPointSize(16)
        info.setFont(info_font)
        main_layout.addWidget(info)
        main_layout.addSpacing(40)

        self.cancel_button = QPushButton("CANCEL OPERATION")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setMinimumHeight(80)
        cancel_font = self.cancel_button.font()
        cancel_font.setPointSize(20)
        cancel_font.setBold(True)
        self.cancel_button.setFont(cancel_font)
        self.cancel_button.clicked.connect(self.main_window.cancel_operation)
        main_layout.addWidget(self.cancel_button)
        main_layout.addStretch()

    def set_selected_art(self, art_name):
        self.selected_art_label.setText(f"POURING: {art_name.upper()}")
