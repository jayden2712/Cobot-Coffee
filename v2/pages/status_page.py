from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class StatusPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        title = QLabel("SYSTEM STATUS")
        title.setAlignment(Qt.AlignCenter)
        title_font = title.font()
        title_font.setPointSize(30)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        main_layout.addSpacing(30)

        cobot_layout = QHBoxLayout()
        cobot_label = QLabel("Cobot Status")
        self.cobot_value = QLabel("READY")
        cobot_layout.addWidget(cobot_label)
        cobot_layout.addStretch()
        cobot_layout.addWidget(self.cobot_value)
        main_layout.addLayout(cobot_layout)

        connection_layout = QHBoxLayout()
        connection_label = QLabel("Connection")
        self.connection_value = QLabel("SIMULATION")
        connection_layout.addWidget(connection_label)
        connection_layout.addStretch()
        connection_layout.addWidget(self.connection_value)
        main_layout.addLayout(connection_layout)

        safety_layout = QHBoxLayout()
        safety_label = QLabel("Safety")
        self.safety_value = QLabel("OK")
        safety_layout.addWidget(safety_label)
        safety_layout.addStretch()
        safety_layout.addWidget(self.safety_value)
        main_layout.addLayout(safety_layout)

        estop_layout = QHBoxLayout()
        estop_label = QLabel("Emergency Stop")
        self.estop_value = QLabel("RELEASED")
        estop_layout.addWidget(estop_label)
        estop_layout.addStretch()
        estop_layout.addWidget(self.estop_value)
        main_layout.addLayout(estop_layout)

        status_labels = [
            cobot_label, connection_label, safety_label, estop_label,
            self.cobot_value, self.connection_value,
            self.safety_value, self.estop_value,
        ]
        for label in status_labels:
            font = label.font()
            font.setPointSize(18)
            label.setFont(font)

        self.cobot_value.setObjectName("goodStatus")
        self.safety_value.setObjectName("goodStatus")
        self.estop_value.setObjectName("goodStatus")
        self.connection_value.setObjectName("simulationStatus")

        main_layout.addStretch()

        self.back_button = QPushButton("BACK")
        self.back_button.setObjectName("backButton")
        self.back_button.setMinimumHeight(70)
        back_font = self.back_button.font()
        back_font.setPointSize(18)
        back_font.setBold(True)
        self.back_button.setFont(back_font)
        self.back_button.clicked.connect(self.main_window.show_home_page)
        main_layout.addWidget(self.back_button)
