from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


class EmergencyStopPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("emergencyStopPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)

        layout.addStretch()

        icon = QLabel("!")
        icon.setObjectName("estopWarningIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(90, 90)

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon)
        icon_row.addStretch()

        layout.addLayout(icon_row)

        title = QLabel("EMERGENCY STOP ACTIVE")
        title.setObjectName("estopPageTitle")
        title.setAlignment(Qt.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)

        layout.addWidget(title)

        message = QLabel(
            "Cobot motion has been disabled.\n"
            "Check the work area before resetting the system."
        )
        message.setObjectName("estopMessage")
        message.setAlignment(Qt.AlignCenter)

        message_font = message.font()
        message_font.setPointSize(14)
        message.setFont(message_font)

        layout.addWidget(message)

        layout.addSpacing(25)

        self.reset_button = QPushButton("RESET E-STOP")
        self.reset_button.setObjectName("resetEstopButton")
        self.reset_button.setFixedSize(300, 70)

        reset_font = self.reset_button.font()
        reset_font.setPointSize(16)
        reset_font.setBold(True)
        self.reset_button.setFont(reset_font)

        self.reset_button.clicked.connect(
            self.main_window.reset_estop
        )

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self.reset_button)
        button_row.addStretch()

        layout.addLayout(button_row)

        layout.addStretch()