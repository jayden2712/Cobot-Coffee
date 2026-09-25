import sys

from PySide6.QtCore import Qt, QTimer, QElapsedTimer
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from pages.home_page import HomePage
from pages.art_selection_page import ArtSelectionPage
from pages.running_page import RunningPage
from pages.complete_page import CompletePage
from pages.status_page import StatusPage
from pages.emergency_stop_page import EmergencyStopPage
from styles import APP_STYLE


class MainWindow(QMainWindow):
    OPERATION_DURATION_MS = 5000

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CoBotics Coffee Cart")
        self.setFixedSize(1024, 600)

        self.selected_art = None
        self.estop_active = False

        # =========================================================
        # OPERATION TIMERS
        # =========================================================
        self.operation_timer = QTimer(self)
        self.operation_timer.setSingleShot(True)
        self.operation_timer.timeout.connect(
            self.complete_operation
        )

        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(80)
        self.progress_timer.timeout.connect(
            self._update_operation_progress
        )

        self.operation_elapsed = QElapsedTimer()

        # =========================================================
        # ROOT CONTAINER
        # =========================================================
        self.central_container = QWidget()
        self.central_container.setObjectName("centralContainer")
        self.setCentralWidget(self.central_container)

        root_layout = QVBoxLayout(self.central_container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # =========================================================
        # PERSISTENT SAFETY BAR
        # =========================================================
        self.safety_bar = QWidget()
        self.safety_bar.setObjectName("safetyBar")
        self.safety_bar.setFixedHeight(50)

        safety_layout = QHBoxLayout(self.safety_bar)
        safety_layout.setContentsMargins(20, 6, 22, 6)
        safety_layout.setSpacing(10)

        # Compact status cluster on the left.
        self.status_cluster = QWidget()
        self.status_cluster.setObjectName("statusCluster")
        self.status_cluster.setFixedHeight(36)

        cluster_layout = QHBoxLayout(self.status_cluster)
        cluster_layout.setContentsMargins(7, 2, 7, 2)
        cluster_layout.setSpacing(2)

        self.cobot_chip = QLabel("●  READY")
        self.cobot_chip.setObjectName("safetyReadyChip")

        self.connection_chip = QLabel("SIMULATION")
        self.connection_chip.setObjectName("safetyNeutralChip")

        self.safety_chip = QLabel("●  SAFETY OK")
        self.safety_chip.setObjectName("safetyReadyChip")

        for chip in (
            self.cobot_chip,
            self.connection_chip,
            self.safety_chip,
        ):
            chip.setAlignment(Qt.AlignCenter)
            chip.setFixedHeight(28)

        separator_one = self._create_separator()
        separator_two = self._create_separator()

        cluster_layout.addWidget(self.cobot_chip)
        cluster_layout.addWidget(separator_one)
        cluster_layout.addWidget(self.connection_chip)
        cluster_layout.addWidget(separator_two)
        cluster_layout.addWidget(self.safety_chip)

        # Emergency control remains isolated on the right.
        self.estop_button = QPushButton("EMERGENCY STOP")
        self.estop_button.setObjectName("estopButton")
        self.estop_button.setProperty("active", False)
        self.estop_button.setFixedSize(148, 36)
        self.estop_button.setCursor(Qt.PointingHandCursor)

        estop_font = self.estop_button.font()
        estop_font.setPointSize(10)
        estop_font.setBold(True)
        self.estop_button.setFont(estop_font)

        self.estop_button.clicked.connect(
            self.activate_estop
        )

        safety_layout.addWidget(self.status_cluster)
        safety_layout.addStretch()
        safety_layout.addWidget(self.estop_button)

        root_layout.addWidget(self.safety_bar)

        # =========================================================
        # PAGE MANAGER
        # =========================================================
        self.pages = QStackedWidget()
        self.pages.setObjectName("pageStack")
        root_layout.addWidget(self.pages, 1)

        self.home_page = HomePage(self)
        self.art_selection_page = ArtSelectionPage(self)
        self.running_page = RunningPage(self)
        self.complete_page = CompletePage(self)
        self.status_page = StatusPage(self)
        self.emergency_stop_page = EmergencyStopPage(self)

        for page in (
            self.home_page,
            self.art_selection_page,
            self.running_page,
            self.complete_page,
            self.status_page,
            self.emergency_stop_page,
        ):
            self.pages.addWidget(page)

        self.pages.setCurrentWidget(self.home_page)
        self.setStyleSheet(APP_STYLE)

    @staticmethod
    def _create_separator():
        separator = QFrame()
        separator.setObjectName("statusSeparator")
        separator.setFrameShape(QFrame.VLine)
        return separator

    @staticmethod
    def _refresh_style(widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def _set_object_name(self, widget, object_name):
        widget.setObjectName(object_name)
        self._refresh_style(widget)

    # =========================================================
    # NAVIGATION GUARD
    # =========================================================
    def _show_if_safe(self, page):
        if self.estop_active:
            self.pages.setCurrentWidget(
                self.emergency_stop_page
            )
            return False

        self.pages.setCurrentWidget(page)
        return True

    # =========================================================
    # NAVIGATION
    # =========================================================
    def show_home_page(self):
        if hasattr(self.complete_page, "stop_countdown"):
            self.complete_page.stop_countdown()

        if self._show_if_safe(self.home_page):
            print("Opening HOME page")

    def show_art_selection_page(self):
        if self._show_if_safe(self.art_selection_page):
            print("Opening Art Selection")

    def show_status_page(self):
        if self._show_if_safe(self.status_page):
            print("Opening System Status")

    # =========================================================
    # COBOT SIMULATION
    # =========================================================
    def start_selected_art(self, art_name):
        if self.estop_active:
            print("Cannot start operation: E-STOP is active.")
            self.pages.setCurrentWidget(
                self.emergency_stop_page
            )
            return

        self.selected_art = art_name

        print(f"Selected art: {art_name}")
        print("Starting operation...")

        self.running_page.set_selected_art(art_name)
        self.complete_page.set_selected_art(art_name)
        self.pages.setCurrentWidget(self.running_page)

        self._set_cobot_running()

        self.operation_elapsed.start()
        self.progress_timer.start()
        self.operation_timer.start(
            self.OPERATION_DURATION_MS
        )

    def _update_operation_progress(self):
        if not self.operation_elapsed.isValid():
            return

        elapsed = self.operation_elapsed.elapsed()
        progress = int(
            elapsed / self.OPERATION_DURATION_MS * 100
        )

        # Leave 100% for complete_operation() so the transition
        # feels intentional instead of briefly stalling at 100%.
        progress = min(progress, 99)
        self.running_page.set_progress(progress)

    def cancel_operation(self):
        print("Operation cancelled")

        self.operation_timer.stop()
        self.progress_timer.stop()
        self.operation_elapsed.invalidate()

        if self.estop_active:
            self.pages.setCurrentWidget(
                self.emergency_stop_page
            )
            return

        self._set_cobot_ready()
        self.pages.setCurrentWidget(self.home_page)

    def complete_operation(self):
        if self.estop_active:
            return

        print("Operation completed")

        self.progress_timer.stop()
        self.operation_elapsed.invalidate()
        self.running_page.set_progress(100)

        self._set_cobot_ready()
        self.pages.setCurrentWidget(self.complete_page)
        self.complete_page.start_countdown(12)

    # =========================================================
    # NORMAL SYSTEM STATES
    # =========================================================
    def _set_cobot_ready(self):
        self.cobot_chip.setText("●  READY")
        self._set_object_name(
            self.cobot_chip,
            "safetyReadyChip",
        )

        self.safety_chip.setText("●  SAFETY OK")
        self._set_object_name(
            self.safety_chip,
            "safetyReadyChip",
        )

        self.status_page.set_cobot_status("READY")

    def _set_cobot_running(self):
        self.cobot_chip.setText("●  RUNNING")
        self._set_object_name(
            self.cobot_chip,
            "safetyActiveChip",
        )

        self.safety_chip.setText("●  SAFETY OK")
        self._set_object_name(
            self.safety_chip,
            "safetyReadyChip",
        )

        self.status_page.set_cobot_status("RUNNING")

    # =========================================================
    # EMERGENCY STOP
    # =========================================================
    def activate_estop(self):
        """
        GUI / simulation emergency stop.

        This software control is an additional stop interface and
        is not a substitute for a safety-rated physical E-stop.
        """

        if self.estop_active:
            return

        print("!!! EMERGENCY STOP ACTIVATED !!!")
        self.estop_active = True

        self.operation_timer.stop()
        self.progress_timer.stop()
        self.operation_elapsed.invalidate()

        # TODO: Send the real robot/controller stop request here.

        self.cobot_chip.setText("●  STOPPED")
        self._set_object_name(
            self.cobot_chip,
            "safetyDangerChip",
        )

        self.safety_chip.setText("●  E-STOP ACTIVE")
        self._set_object_name(
            self.safety_chip,
            "safetyDangerChip",
        )

        self.estop_button.setText("E-STOP ACTIVE")
        self.estop_button.setProperty("active", True)
        self._refresh_style(self.estop_button)

        self.status_page.set_estop_status(True)
        self.pages.setCurrentWidget(
            self.emergency_stop_page
        )

    def reset_estop(self):
        if not self.estop_active:
            return

        reply = QMessageBox.question(
            self,
            "Reset E-Stop",
            (
                "Has the work area been checked and "
                "is it safe to reset the system?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        print("E-STOP RESET")

        # TODO: Verify physical E-stop and controller safety state
        # before clearing this flag on the real system.
        self.estop_active = False

        self._set_cobot_ready()

        self.estop_button.setText("EMERGENCY STOP")
        self.estop_button.setProperty("active", False)
        self._refresh_style(self.estop_button)

        self.status_page.set_estop_status(False)
        self.pages.setCurrentWidget(self.home_page)


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================
def find_touchscreen(app):
    for screen in app.screens():
        geometry = screen.geometry()

        print(
            f"Screen: {screen.name()} | "
            f"{geometry.width()}x{geometry.height()} | "
            f"Position: {geometry.x()}, {geometry.y()}"
        )

        if geometry.width() == 1024 and geometry.height() == 600:
            return screen

    return None


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    touchscreen = find_touchscreen(app)

    if touchscreen:
        window.setScreen(touchscreen)
        window.move(touchscreen.geometry().topLeft())
        window.showFullScreen()
    else:
        print("Touchscreen 1024x600 not found.")
        window.resize(1024, 600)
        window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
