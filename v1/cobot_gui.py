import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon


# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


# =========================================================
# HOME PAGE
# =========================================================
class HomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # Status bar
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

        # Title
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

        # Three main function tiles
        functions_layout = QHBoxLayout()
        functions_layout.setSpacing(30)

        # START POUR
        self.start_button = QPushButton("START\nPOUR")
        self.start_button.setObjectName("startButton")
        self.start_button.setFixedSize(220, 220)

        start_font = self.start_button.font()
        start_font.setPointSize(22)
        start_font.setBold(True)
        self.start_button.setFont(start_font)

        # Now opens Art Selection instead of Running directly
        self.start_button.clicked.connect(
            self.main_window.show_art_selection_page
        )

        # TELEOPERATION
        self.teleop_button = QPushButton("TELE-\nOPERATION")
        self.teleop_button.setObjectName("teleopButton")
        self.teleop_button.setFixedSize(220, 220)

        teleop_font = self.teleop_button.font()
        teleop_font.setPointSize(20)
        teleop_font.setBold(True)
        self.teleop_button.setFont(teleop_font)

        self.teleop_button.clicked.connect(
            lambda: print("TELEOPERATION pressed")
        )

        # SYSTEM STATUS
        self.status_button = QPushButton("SYSTEM\nSTATUS")
        self.status_button.setObjectName("statusButton")
        self.status_button.setFixedSize(220, 220)

        status_font = self.status_button.font()
        status_font.setPointSize(20)
        status_font.setBold(True)
        self.status_button.setFont(status_font)

        self.status_button.clicked.connect(
            self.main_window.show_status_page
        )

        functions_layout.addStretch()
        functions_layout.addWidget(self.start_button)
        functions_layout.addWidget(self.teleop_button)
        functions_layout.addWidget(self.status_button)
        functions_layout.addStretch()

        main_layout.addLayout(functions_layout)
        main_layout.addStretch()


# =========================================================
# ART SELECTION PAGE
# =========================================================
class ArtSelectionPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # Page title
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

        # Art tiles
        art_layout = QHBoxLayout()
        art_layout.setSpacing(30)

        self.heart_button = self.create_art_button(
            "Heart",
            "heart.png"
        )

        self.tulip_button = self.create_art_button(
            "Tulip",
            "tulip.png"
        )

        self.rosetta_button = self.create_art_button(
            "Rosetta",
            "rosetta.png"
        )

        self.heart_button.clicked.connect(
            lambda: self.main_window.start_selected_art("Heart")
        )

        self.tulip_button.clicked.connect(
            lambda: self.main_window.start_selected_art("Tulip")
        )

        self.rosetta_button.clicked.connect(
            lambda: self.main_window.start_selected_art("Rosetta")
        )

        art_layout.addStretch()
        art_layout.addWidget(self.heart_button)
        art_layout.addWidget(self.tulip_button)
        art_layout.addWidget(self.rosetta_button)
        art_layout.addStretch()

        main_layout.addLayout(art_layout)
        main_layout.addStretch()

        # Back button
        self.back_button = QPushButton("BACK")
        self.back_button.setObjectName("backButton")
        self.back_button.setMinimumHeight(65)

        back_font = self.back_button.font()
        back_font.setPointSize(17)
        back_font.setBold(True)
        self.back_button.setFont(back_font)

        self.back_button.clicked.connect(
            self.main_window.show_home_page
        )

        main_layout.addWidget(self.back_button)

    def create_art_button(self, art_name, icon_filename):
        """
        Creates a square art-selection button.

        Put the icon file inside:
            assets/heart.png
            assets/tulip.png
            assets/rosetta.png
        """
        button = QToolButton()
        button.setObjectName("artButton")
        button.setText(art_name)
        button.setFixedSize(220, 220)

        # Put text below the icon
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        font = button.font()
        font.setPointSize(19)
        font.setBold(True)
        button.setFont(font)

        icon_path = ASSETS_DIR / icon_filename

        # If the image exists, display it.
        # If not, the button still works and simply shows the text.
        if icon_path.exists():
            button.setIcon(QIcon(str(icon_path)))
            button.setIconSize(QSize(125, 125))

        return button


# =========================================================
# RUNNING PAGE
# =========================================================
class RunningPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # Status bar
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

        # Selected art display
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

        # Cancel button
        self.cancel_button = QPushButton("CANCEL OPERATION")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setMinimumHeight(80)

        cancel_font = self.cancel_button.font()
        cancel_font.setPointSize(20)
        cancel_font.setBold(True)
        self.cancel_button.setFont(cancel_font)

        self.cancel_button.clicked.connect(
            self.main_window.cancel_operation
        )

        main_layout.addWidget(self.cancel_button)
        main_layout.addStretch()

    def set_selected_art(self, art_name):
        self.selected_art_label.setText(
            f"POURING: {art_name.upper()}"
        )


# =========================================================
# COMPLETE PAGE
# =========================================================
class CompletePage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)

        # Status bar
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

        # Complete title
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

        # Home button
        self.home_button = QPushButton("RETURN HOME")
        self.home_button.setObjectName("homeButton")
        self.home_button.setMinimumHeight(80)

        home_font = self.home_button.font()
        home_font.setPointSize(20)
        home_font.setBold(True)
        self.home_button.setFont(home_font)

        self.home_button.clicked.connect(
            self.main_window.show_home_page
        )

        main_layout.addWidget(self.home_button)
        main_layout.addStretch()

    def set_selected_art(self, art_name):
        self.message.setText(
            f"Your {art_name} latte art is ready!"
        )


# =========================================================
# SYSTEM STATUS PAGE
# =========================================================
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

        # Cobot status
        cobot_layout = QHBoxLayout()

        cobot_label = QLabel("Cobot Status")
        self.cobot_value = QLabel("READY")

        cobot_layout.addWidget(cobot_label)
        cobot_layout.addStretch()
        cobot_layout.addWidget(self.cobot_value)

        main_layout.addLayout(cobot_layout)

        # Connection status
        connection_layout = QHBoxLayout()

        connection_label = QLabel("Connection")
        self.connection_value = QLabel("SIMULATION")

        connection_layout.addWidget(connection_label)
        connection_layout.addStretch()
        connection_layout.addWidget(self.connection_value)

        main_layout.addLayout(connection_layout)

        # Safety status
        safety_layout = QHBoxLayout()

        safety_label = QLabel("Safety")
        self.safety_value = QLabel("OK")

        safety_layout.addWidget(safety_label)
        safety_layout.addStretch()
        safety_layout.addWidget(self.safety_value)

        main_layout.addLayout(safety_layout)

        # Emergency stop status
        estop_layout = QHBoxLayout()

        estop_label = QLabel("Emergency Stop")
        self.estop_value = QLabel("RELEASED")

        estop_layout.addWidget(estop_label)
        estop_layout.addStretch()
        estop_layout.addWidget(self.estop_value)

        main_layout.addLayout(estop_layout)

        status_labels = [
            cobot_label,
            connection_label,
            safety_label,
            estop_label,
            self.cobot_value,
            self.connection_value,
            self.safety_value,
            self.estop_value,
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

        self.back_button.clicked.connect(
            self.main_window.show_home_page
        )

        main_layout.addWidget(self.back_button)


# =========================================================
# MAIN WINDOW
# =========================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CoBotics Coffee Cart")
        self.setFixedSize(1024, 600)

        self.selected_art = None

        # Mock operation timer
        self.operation_timer = QTimer()
        self.operation_timer.setSingleShot(True)
        self.operation_timer.timeout.connect(
            self.complete_operation
        )

        # Pages
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        self.home_page = HomePage(self)
        self.art_selection_page = ArtSelectionPage(self)
        self.running_page = RunningPage(self)
        self.complete_page = CompletePage(self)
        self.status_page = StatusPage(self)

        self.pages.addWidget(self.home_page)           # Index 0
        self.pages.addWidget(self.art_selection_page)  # Index 1
        self.pages.addWidget(self.running_page)        # Index 2
        self.pages.addWidget(self.complete_page)       # Index 3
        self.pages.addWidget(self.status_page)         # Index 4

        self.pages.setCurrentWidget(self.home_page)

        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }

            QWidget {
                background-color: #F5F5F5;
            }

            QLabel {
                color: #222222;
            }

            QLabel#goodStatus {
                color: #2E7D32;
                font-weight: bold;
            }

            QLabel#simulationStatus {
                color: #1565C0;
                font-weight: bold;
            }

            QPushButton,
            QToolButton {
                background-color: white;
                color: #222222;
                border: 2px solid #444444;
                border-radius: 12px;
                padding: 10px;
            }

            QPushButton:hover,
            QToolButton:hover {
                background-color: #E8E8E8;
            }

            QPushButton:pressed,
            QToolButton:pressed {
                background-color: #D0D0D0;
            }

            /* HOME: START POUR */
            QPushButton#startButton {
                background-color: #2E7D32;
                color: white;
                border: none;
                border-radius: 18px;
            }

            QPushButton#startButton:hover {
                background-color: #388E3C;
            }

            QPushButton#startButton:pressed {
                background-color: #1B5E20;
            }

            /* HOME: TELEOPERATION */
            QPushButton#teleopButton {
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 18px;
            }

            QPushButton#teleopButton:hover {
                background-color: #1976D2;
            }

            QPushButton#teleopButton:pressed {
                background-color: #0D47A1;
            }

            /* HOME: SYSTEM STATUS */
            QPushButton#statusButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 18px;
            }

            QPushButton#statusButton:hover {
                background-color: #616161;
            }

            QPushButton#statusButton:pressed {
                background-color: #212121;
            }

            /* ART SELECTION */
            QToolButton#artButton {
                background-color: white;
                color: #222222;
                border: 2px solid #BDBDBD;
                border-radius: 18px;
                padding: 15px;
            }

            QToolButton#artButton:hover {
                background-color: #E8F5E9;
                border: 3px solid #2E7D32;
            }

            QToolButton#artButton:pressed {
                background-color: #C8E6C9;
            }

            /* CANCEL */
            QPushButton#cancelButton {
                background-color: #C62828;
                color: white;
            }

            QPushButton#cancelButton:hover {
                background-color: #D32F2F;
            }

            /* RETURN HOME */
            QPushButton#homeButton {
                background-color: #1565C0;
                color: white;
            }

            QPushButton#homeButton:hover {
                background-color: #1976D2;
            }

            /* BACK */
            QPushButton#backButton {
                background-color: #333333;
                color: white;
            }

            QPushButton#backButton:hover {
                background-color: #555555;
            }
        """)

    # =====================================================
    # Navigation / logic
    # =====================================================
    def show_home_page(self):
        print("Opening HOME page")
        self.pages.setCurrentWidget(self.home_page)

    def show_art_selection_page(self):
        print("Opening Art Selection")
        self.pages.setCurrentWidget(self.art_selection_page)

    def start_selected_art(self, art_name):
        self.selected_art = art_name

        print(f"Selected art: {art_name}")
        print("Starting operation...")

        self.running_page.set_selected_art(art_name)
        self.complete_page.set_selected_art(art_name)

        self.pages.setCurrentWidget(self.running_page)

        # Simulation only
        self.operation_timer.start(5000)

    def cancel_operation(self):
        print("Operation cancelled")

        self.operation_timer.stop()
        self.pages.setCurrentWidget(self.home_page)

    def complete_operation(self):
        print("Operation completed")
        self.pages.setCurrentWidget(self.complete_page)

    def show_status_page(self):
        print("Opening System Status")
        self.pages.setCurrentWidget(self.status_page)


# =========================================================
# APPLICATION
# =========================================================
def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

