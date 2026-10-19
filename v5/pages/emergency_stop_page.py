from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)

from typography import BODY, HEADLINE, LABEL, TITLE, make_font


class EmergencyStopPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("emergencyStopPage")

        root = QVBoxLayout(self)
        root.setContentsMargins(70, 24, 70, 28)
        root.addStretch()

        panel = QFrame()
        panel.setObjectName("emergencyPanel")
        panel.setFixedWidth(780)

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(40, 20, 40, 22)
        panel_layout.setSpacing(10)

        icon = QLabel("!")
        icon.setObjectName("estopWarningIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(76, 76)

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon)
        icon_row.addStretch()
        panel_layout.addLayout(icon_row)

        title = QLabel("EMERGENCY STOP ACTIVE")
        title.setObjectName("estopPageTitle")
        title.setAlignment(Qt.AlignCenter)

        title.setFont(make_font(HEADLINE + 2, bold=True))
        panel_layout.addWidget(title)

        message = QLabel(
            "Cobot motion is disabled. Complete the safety checks below "
            "before resetting the system."
        )
        message.setObjectName("estopMessage")
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)

        message.setFont(make_font(BODY))
        panel_layout.addWidget(message)

        panel_layout.addSpacing(5)

        self._add_step(
            panel_layout,
            "1",
            "Check the work area and make sure it is clear.",
        )
        self._add_step(
            panel_layout,
            "2",
            "Release the physical emergency stop if one is engaged.",
        )
        self._add_step(
            panel_layout,
            "3",
            "Reset only after the system is confirmed safe.",
        )

        panel_layout.addSpacing(6)

        self.reset_button = QPushButton("RESET E-STOP")
        self.reset_button.setObjectName("resetEstopButton")
        self.reset_button.setFixedSize(320, 62)
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setFont(make_font(TITLE, bold=True))

        self.reset_button.clicked.connect(
            self.main_window.reset_estop
        )

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self.reset_button)
        button_row.addStretch()
        panel_layout.addLayout(button_row)

        panel_row = QHBoxLayout()
        panel_row.addStretch()
        panel_row.addWidget(panel)
        panel_row.addStretch()

        root.addLayout(panel_row)
        root.addStretch()

    def _add_step(self, layout, number, text):
        row = QHBoxLayout()
        row.setSpacing(10)

        number_label = QLabel(number)
        number_label.setObjectName("estopStepNumber")
        number_label.setAlignment(Qt.AlignCenter)
        number_label.setFixedSize(32, 32)
        number_label.setFont(make_font(LABEL, bold=True))

        text_label = QLabel(text)
        text_label.setObjectName("estopStepText")
        text_label.setWordWrap(True)
        text_label.setFont(make_font(BODY))

        row.addWidget(number_label)
        row.addWidget(text_label, 1)
        layout.addLayout(row)
