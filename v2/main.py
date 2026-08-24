import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from pages.home_page import HomePage
from pages.art_selection_page import ArtSelectionPage
from pages.running_page import RunningPage
from pages.complete_page import CompletePage
from pages.status_page import StatusPage
from styles import APP_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CoBotics Coffee Cart")
        self.setFixedSize(1024, 600)
        self.selected_art = None

        # Mock operation timer
        self.operation_timer = QTimer()
        self.operation_timer.setSingleShot(True)
        self.operation_timer.timeout.connect(self.complete_operation)

        # Page manager
        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        # Create pages
        self.home_page = HomePage(self)
        self.art_selection_page = ArtSelectionPage(self)
        self.running_page = RunningPage(self)
        self.complete_page = CompletePage(self)
        self.status_page = StatusPage(self)

        # Add pages
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.art_selection_page)
        self.pages.addWidget(self.running_page)
        self.pages.addWidget(self.complete_page)
        self.pages.addWidget(self.status_page)

        self.pages.setCurrentWidget(self.home_page)
        self.setStyleSheet(APP_STYLE)

    # =====================================================
    # Navigation
    # =====================================================
    def show_home_page(self):
        print("Opening HOME page")
        self.pages.setCurrentWidget(self.home_page)

    def show_art_selection_page(self):
        print("Opening Art Selection")
        self.pages.setCurrentWidget(self.art_selection_page)

    def show_status_page(self):
        print("Opening System Status")
        self.pages.setCurrentWidget(self.status_page)

    # =====================================================
    # Cobot simulation
    # =====================================================
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


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
