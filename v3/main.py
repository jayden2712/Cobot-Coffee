import sys

from PySide6.QtCore import Qt, QTimer
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
from styles import APP_STYLE


# =========================================================
# EXTRA STYLE
#
# Appended after APP_STYLE so the CoBotics cream theme and
# the persistent safety bar override the old global grey.
# =========================================================
SAFETY_STYLE = """
/* =====================================================
   GLOBAL COBOTICS BACKGROUND
   ===================================================== */
QMainWindow,
QWidget {
    background-color: #F8EFE5;
}


/* =====================================================
   PERSISTENT TOP SAFETY BAR
   ===================================================== */
QWidget#safetyBar {
    background-color: #F8EFE5;
    border: none;
    border-bottom: 1px solid #DDCDBD;
}


/* Group the system information as one visual unit. */
QWidget#statusCluster {
    background-color: #FBF5EE;
    border: 1px solid #E1D0BF;
    border-radius: 16px;
}


QLabel#systemBarLabel {
    background: transparent;
    color: #9A7557;

    font-size: 10px;
    font-weight: 800;

    padding-left: 2px;
    padding-right: 4px;
}


QFrame#statusSeparator {
    background-color: #DCC8B5;
    border: none;

    min-width: 1px;
    max-width: 1px;

    min-height: 20px;
    max-height: 20px;
}


/* =====================================================
   STATUS CHIPS
   ===================================================== */
QLabel#safetyReadyChip,
QLabel#safetyNeutralChip,
QLabel#safetyDangerChip {
    border-radius: 11px;

    padding-left: 10px;
    padding-right: 10px;

    font-size: 10px;
    font-weight: 700;
}


QLabel#safetyReadyChip {
    background-color: #EEE7DE;
    color: #4F6848;

    border: 1px solid #D9CDBF;
}


QLabel#safetyNeutralChip {
    background-color: transparent;
    color: #876448;

    border: 1px solid #D9C4AF;
}


QLabel#safetyDangerChip {
    background-color: #F4DAD7;
    color: #A32620;

    border: 1px solid #CB645D;
}


/* =====================================================
   E-STOP BUTTON
   ===================================================== */
QPushButton#estopButton {
    background-color: #B72A22;
    color: #FFFFFF;

    border: 2px solid #922019;
    border-radius: 14px;

    padding: 5px 16px;

    font-weight: 800;
}


QPushButton#estopButton:hover {
    background-color: #C73A31;
}


QPushButton#estopButton:pressed {
    background-color: #8F1D18;
}


QPushButton#estopButton[active="true"] {
    background-color: #8F1D18;
    border-color: #64130F;
}


/* =====================================================
   EMERGENCY STOP PAGE
   ===================================================== */
QWidget#emergencyStopPage {
    background-color: #F8EFE5;
}


QLabel#estopWarningIcon {
    background-color: #B3261E;
    color: #FFFFFF;

    border-radius: 42px;

    font-size: 44px;
    font-weight: 900;
}


QLabel#estopPageTitle {
    background: transparent;
    color: #A32620;
}


QLabel#estopMessage {
    background: transparent;
    color: #5E4940;
}


QPushButton#resetEstopButton {
    background-color: #FFFDFC;
    color: #8F1D18;

    border: 2px solid #B3261E;
    border-radius: 18px;

    padding: 10px 20px;
}


QPushButton#resetEstopButton:hover {
    background-color: #F4DAD7;
}


QPushButton#resetEstopButton:pressed {
    background-color: #EBC4C0;
}


/* System Status page: danger state */
QLabel#dangerStatus {
    color: #B3261E;
    font-weight: bold;
}
"""


# =========================================================
# EMERGENCY STOP PAGE
#
# Kept in this file so you can replace main.py directly
# without creating another Python file.
# =========================================================
class EmergencyStopPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("emergencyStopPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 28, 60, 34)
        layout.setSpacing(14)

        layout.addStretch()

        # -------------------------------------------------
        # Warning icon
        # -------------------------------------------------
        icon = QLabel("!")
        icon.setObjectName("estopWarningIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(84, 84)

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(icon)
        icon_row.addStretch()

        layout.addLayout(icon_row)

        # -------------------------------------------------
        # Main warning
        # -------------------------------------------------
        title = QLabel("EMERGENCY STOP ACTIVE")
        title.setObjectName("estopPageTitle")
        title.setAlignment(Qt.AlignCenter)

        title_font = title.font()
        title_font.setPointSize(27)
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

        layout.addSpacing(18)

        # -------------------------------------------------
        # Reset button
        # -------------------------------------------------
        self.reset_button = QPushButton("RESET E-STOP")
        self.reset_button.setObjectName("resetEstopButton")
        self.reset_button.setFixedSize(300, 68)
        self.reset_button.setCursor(Qt.PointingHandCursor)

        reset_font = self.reset_button.font()
        reset_font.setPointSize(15)
        reset_font.setBold(True)
        self.reset_button.setFont(reset_font)

        self.reset_button.clicked.connect(
            self.main_window.reset_estop
        )

        reset_row = QHBoxLayout()
        reset_row.addStretch()
        reset_row.addWidget(self.reset_button)
        reset_row.addStretch()

        layout.addLayout(reset_row)

        layout.addStretch()


# =========================================================
# MAIN WINDOW
# =========================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CoBotics Coffee Cart")
        self.setFixedSize(1024, 600)

        self.selected_art = None
        self.estop_active = False

        # =================================================
        # MOCK OPERATION TIMER
        # =================================================
        self.operation_timer = QTimer(self)
        self.operation_timer.setSingleShot(True)
        self.operation_timer.timeout.connect(
            self.complete_operation
        )

        # =================================================
        # ROOT CONTAINER
        #
        # MainWindow
        # └── central_container
        #     ├── safety bar
        #     └── stacked pages
        # =================================================
        self.central_container = QWidget()
        self.central_container.setObjectName(
            "centralContainer"
        )
        self.setCentralWidget(
            self.central_container
        )

        root_layout = QVBoxLayout(
            self.central_container
        )
        root_layout.setContentsMargins(
            0, 0, 0, 0
        )
        root_layout.setSpacing(0)

        # =================================================
        # PERSISTENT SAFETY BAR
        # =================================================
        self.safety_bar = QWidget()
        self.safety_bar.setObjectName(
            "safetyBar"
        )
        self.safety_bar.setFixedHeight(56)

        safety_layout = QHBoxLayout(
            self.safety_bar
        )
        safety_layout.setContentsMargins(
            20, 7, 22, 7
        )
        safety_layout.setSpacing(10)

        # -------------------------------------------------
        # LEFT: one grouped system-status cluster
        # -------------------------------------------------
        self.status_cluster = QWidget()
        self.status_cluster.setObjectName(
            "statusCluster"
        )
        self.status_cluster.setFixedHeight(40)

        cluster_layout = QHBoxLayout(
            self.status_cluster
        )
        cluster_layout.setContentsMargins(
            10, 3, 10, 3
        )
        cluster_layout.setSpacing(6)

        self.system_label = QLabel("SYSTEM")
        self.system_label.setObjectName(
            "systemBarLabel"
        )
        self.system_label.setAlignment(
            Qt.AlignCenter
        )

        separator = QFrame()
        separator.setObjectName(
            "statusSeparator"
        )
        separator.setFrameShape(QFrame.VLine)

        self.cobot_chip = QLabel("●  READY")
        self.cobot_chip.setObjectName(
            "safetyReadyChip"
        )

        self.connection_chip = QLabel(
            "SIMULATION"
        )
        self.connection_chip.setObjectName(
            "safetyNeutralChip"
        )

        self.safety_chip = QLabel(
            "●  SAFETY OK"
        )
        self.safety_chip.setObjectName(
            "safetyReadyChip"
        )

        for chip in (
            self.cobot_chip,
            self.connection_chip,
            self.safety_chip,
        ):
            chip.setAlignment(Qt.AlignCenter)
            chip.setFixedHeight(30)

        cluster_layout.addWidget(
            self.system_label
        )
        cluster_layout.addWidget(
            separator
        )
        cluster_layout.addWidget(
            self.cobot_chip
        )
        cluster_layout.addWidget(
            self.connection_chip
        )
        cluster_layout.addWidget(
            self.safety_chip
        )

        # -------------------------------------------------
        # RIGHT: emergency control
        # -------------------------------------------------
        self.estop_button = QPushButton(
            "EMERGENCY STOP"
        )
        self.estop_button.setObjectName(
            "estopButton"
        )
        self.estop_button.setProperty(
            "active",
            False,
        )
        self.estop_button.setFixedSize(
            150,
            38,
        )
        self.estop_button.setCursor(
            Qt.PointingHandCursor
        )

        estop_font = self.estop_button.font()
        estop_font.setPointSize(10)
        estop_font.setBold(True)
        self.estop_button.setFont(
            estop_font
        )

        self.estop_button.clicked.connect(
            self.activate_estop
        )

        # -------------------------------------------------
        # Build bar
        # -------------------------------------------------
        safety_layout.addWidget(
            self.status_cluster
        )

        safety_layout.addStretch()

        safety_layout.addWidget(
            self.estop_button
        )

        root_layout.addWidget(
            self.safety_bar
        )

        # =================================================
        # PAGE MANAGER
        # =================================================
        self.pages = QStackedWidget()
        self.pages.setObjectName("pageStack")

        root_layout.addWidget(
            self.pages,
            1,
        )

        # =================================================
        # CREATE PAGES
        # =================================================
        self.home_page = HomePage(self)

        self.art_selection_page = (
            ArtSelectionPage(self)
        )

        self.running_page = RunningPage(self)
        self.complete_page = CompletePage(self)
        self.status_page = StatusPage(self)

        self.emergency_stop_page = (
            EmergencyStopPage(self)
        )

        # =================================================
        # ADD PAGES
        # =================================================
        self.pages.addWidget(
            self.home_page
        )
        self.pages.addWidget(
            self.art_selection_page
        )
        self.pages.addWidget(
            self.running_page
        )
        self.pages.addWidget(
            self.complete_page
        )
        self.pages.addWidget(
            self.status_page
        )
        self.pages.addWidget(
            self.emergency_stop_page
        )

        # The MainWindow safety bar now owns global system
        # status, so hide duplicate status labels that are
        # still inside older page implementations.
        self._hide_duplicate_page_statuses()

        self.pages.setCurrentWidget(
            self.home_page
        )

        # Append our rules after the existing app stylesheet.
        self.setStyleSheet(
            APP_STYLE + SAFETY_STYLE
        )

    # =====================================================
    # STYLE HELPERS
    # =====================================================
    @staticmethod
    def _refresh_style(widget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def _set_object_name(
        self,
        widget,
        object_name,
    ):
        widget.setObjectName(object_name)
        self._refresh_style(widget)

    # =====================================================
    # REMOVE DUPLICATE STATUS ROWS FROM PAGE CONTENT
    # =====================================================
    def _hide_duplicate_page_statuses(self):
        """
        Home/Running/Complete were originally designed with
        their own COBOT / CONNECTION / SAFETY labels.

        The new MainWindow safety bar replaces those labels,
        so they are hidden to avoid duplicated information.
        """

        # New redesigned HomePage exposes these as attributes.
        for attr_name in (
            "cobot_status",
            "connection_status",
            "safety_status",
        ):
            widget = getattr(
                self.home_page,
                attr_name,
                None,
            )

            if widget is not None:
                widget.hide()

        # RunningPage / CompletePage create local QLabel
        # objects, so find them by their visible text.
        for page in (
            self.running_page,
            self.complete_page,
        ):
            for label in page.findChildren(QLabel):
                text = label.text().strip().upper()

                if text.startswith(
                    (
                        "COBOT:",
                        "CONNECTION:",
                        "SAFETY:",
                    )
                ):
                    label.hide()

    # =====================================================
    # NAVIGATION GUARD
    # =====================================================
    def _show_if_safe(self, page):
        """
        Once E-stop is active, normal navigation is blocked
        until the safety state is reset.
        """

        if self.estop_active:
            self.pages.setCurrentWidget(
                self.emergency_stop_page
            )
            return False

        self.pages.setCurrentWidget(page)
        return True

    # =====================================================
    # NAVIGATION
    # =====================================================
    def show_home_page(self):
        if self._show_if_safe(
            self.home_page
        ):
            print("Opening HOME page")

    def show_art_selection_page(self):
        if self._show_if_safe(
            self.art_selection_page
        ):
            print("Opening Art Selection")

    def show_status_page(self):
        if self._show_if_safe(
            self.status_page
        ):
            print("Opening System Status")

    # =====================================================
    # COBOT SIMULATION
    # =====================================================
    def start_selected_art(self, art_name):
        # E-stop always wins over operation requests.
        if self.estop_active:
            print(
                "Cannot start operation: "
                "E-STOP is active."
            )

            self.pages.setCurrentWidget(
                self.emergency_stop_page
            )
            return

        self.selected_art = art_name

        print(f"Selected art: {art_name}")
        print("Starting operation...")

        self.running_page.set_selected_art(
            art_name
        )

        self.complete_page.set_selected_art(
            art_name
        )

        self.pages.setCurrentWidget(
            self.running_page
        )

        self._set_cobot_running()

        # Simulation only
        self.operation_timer.start(5000)

    def cancel_operation(self):
        print("Operation cancelled")

        self.operation_timer.stop()

        if self.estop_active:
            self.pages.setCurrentWidget(
                self.emergency_stop_page
            )
            return

        self._set_cobot_ready()

        self.pages.setCurrentWidget(
            self.home_page
        )

    def complete_operation(self):
        # Prevent a timer callback from completing an operation
        # after an E-stop.
        if self.estop_active:
            return

        print("Operation completed")

        self._set_cobot_ready()

        self.pages.setCurrentWidget(
            self.complete_page
        )

    # =====================================================
    # NORMAL SYSTEM STATES
    # =====================================================
    def _set_cobot_ready(self):
        self.cobot_chip.setText(
            "●  READY"
        )
        self._set_object_name(
            self.cobot_chip,
            "safetyReadyChip",
        )

        self.safety_chip.setText(
            "●  SAFETY OK"
        )
        self._set_object_name(
            self.safety_chip,
            "safetyReadyChip",
        )

    def _set_cobot_running(self):
        self.cobot_chip.setText(
            "●  RUNNING"
        )
        self._set_object_name(
            self.cobot_chip,
            "safetyNeutralChip",
        )

        self.safety_chip.setText(
            "●  SAFETY OK"
        )
        self._set_object_name(
            self.safety_chip,
            "safetyReadyChip",
        )

    # =====================================================
    # EMERGENCY STOP
    # =====================================================
    def activate_estop(self):
        """
        GUI / simulation emergency stop.

        IMPORTANT:
        This GUI control is not a substitute for a
        safety-rated physical emergency-stop circuit.
        """

        if self.estop_active:
            return

        print(
            "!!! EMERGENCY STOP ACTIVATED !!!"
        )

        self.estop_active = True

        # -------------------------------------------------
        # 1. Stop simulated operation immediately
        # -------------------------------------------------
        self.operation_timer.stop()

        # -------------------------------------------------
        # 2. REAL COBOT INTEGRATION
        #
        # Add your robot/controller stop command here.
        #
        # Example architecture:
        #
        # GUI
        #   -> robot interface
        #       -> controller stop command
        #
        # Do not use the GUI as the only safety-rated E-stop.
        # -------------------------------------------------

        # -------------------------------------------------
        # 3. Update persistent safety bar
        # -------------------------------------------------
        self.cobot_chip.setText(
            "●  STOPPED"
        )
        self._set_object_name(
            self.cobot_chip,
            "safetyDangerChip",
        )

        self.safety_chip.setText(
            "●  E-STOP ACTIVE"
        )
        self._set_object_name(
            self.safety_chip,
            "safetyDangerChip",
        )

        self.estop_button.setText(
            "E-STOP ACTIVE"
        )
        self.estop_button.setProperty(
            "active",
            True,
        )
        self._refresh_style(
            self.estop_button
        )

        # -------------------------------------------------
        # 4. Synchronise System Status page
        # -------------------------------------------------
        self._update_status_page_estop(
            active=True
        )

        # -------------------------------------------------
        # 5. Lock UI on the emergency page
        # -------------------------------------------------
        self.pages.setCurrentWidget(
            self.emergency_stop_page
        )

    def reset_estop(self):
        """
        Simulation reset.

        For real hardware, only allow reset after:
        - the physical E-stop has been released,
        - the safety controller reports a safe state,
        - the required safety-reset procedure is complete.
        """

        if not self.estop_active:
            return

        reply = QMessageBox.question(
            self,
            "Reset E-Stop",
            (
                "Has the work area been checked and "
                "is it safe to reset the system?"
            ),
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        print("E-STOP RESET")

        # -------------------------------------------------
        # REAL COBOT INTEGRATION
        #
        # Verify physical E-stop state + controller safety
        # state here BEFORE clearing estop_active.
        # -------------------------------------------------

        self.estop_active = False

        self._set_cobot_ready()

        self.estop_button.setText(
            "EMERGENCY STOP"
        )
        self.estop_button.setProperty(
            "active",
            False,
        )
        self._refresh_style(
            self.estop_button
        )

        self._update_status_page_estop(
            active=False
        )

        self.pages.setCurrentWidget(
            self.home_page
        )

    # =====================================================
    # STATUS PAGE SYNCHRONISATION
    #
    # Compatible with your existing StatusPage implementation.
    # =====================================================
    def _update_status_page_estop(
        self,
        active,
    ):
        if active:
            cobot_text = "STOPPED"
            safety_text = "STOPPED"
            estop_text = "ACTIVE"
            object_name = "dangerStatus"
        else:
            cobot_text = "READY"
            safety_text = "OK"
            estop_text = "RELEASED"
            object_name = "goodStatus"

        updates = (
            (
                getattr(
                    self.status_page,
                    "cobot_value",
                    None,
                ),
                cobot_text,
            ),
            (
                getattr(
                    self.status_page,
                    "safety_value",
                    None,
                ),
                safety_text,
            ),
            (
                getattr(
                    self.status_page,
                    "estop_value",
                    None,
                ),
                estop_text,
            ),
        )

        for widget, text in updates:
            if widget is None:
                continue

            widget.setText(text)
            widget.setObjectName(
                object_name
            )
            self._refresh_style(widget)


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
