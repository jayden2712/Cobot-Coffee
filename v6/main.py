import sys
from datetime import datetime

from PySide6.QtCore import QElapsedTimer, QEvent, Qt, QTimer
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import ATTRACT_AFTER_SECONDS, MANUAL_POUR_CONFIRM, SERVICE_LOG_PATH
from pages.animations import FadingStackedWidget
from pages.art_selection_page import ArtSelectionPage
from pages.attract_page import AttractPage
from pages.barista_page import BaristaPage
from pages.complete_page import CompletePage
from pages.emergency_stop_page import EmergencyStopPage
from pages.home_page import HomePage
from pages.running_page import RunningPage
from pages.status_page import StatusPage
from pages.teleop_game_page import TeleopGamePage
from pages.teleop_result_page import TeleopResultPage
from pages.teleop_setup_page import TeleopSetupPage
from service_log import (
    CHOICE_BARISTA,
    CHOICE_COBOT,
    CHOICE_TELEOP,
    PourRecord,
    append_record,
    best_score,
    load_records,
    record_pour,
    stats_from_records,
    top_score,
)
from styles import APP_STYLE
from teleop.jug import SimulatedJugController
from teleop.scoring import score_pour
from typography import CAPTION, LABEL, make_font

#: Horizontal padding inside a status chip (stylesheet padding plus margin).
CHIP_PADDING = 24

#: Touches that count as someone using the kiosk.
ACTIVITY_EVENTS = (QEvent.MouseButtonPress, QEvent.TouchBegin)


class MainWindow(QMainWindow):
    OPERATION_DURATION_MS = 5000

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CoBotics Coffee Cart")
        self.setFixedSize(1024, 600)

        self.selected_art = None
        self.estop_active = False

        # Swap in the hardware jug controller here once it is integrated.
        self.jug_controller = SimulatedJugController()

        # Today's pours, rebuilt from the log so a restart keeps the count.
        self._load_todays_stats()

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

        # Shows the attract screen when Home sits untouched.
        self.idle_timer = QTimer(self)
        self.idle_timer.setSingleShot(True)
        self.idle_timer.setInterval(ATTRACT_AFTER_SECONDS * 1000)
        self.idle_timer.timeout.connect(self._show_attract_if_idle)

        # =========================================================
        # ROOT CONTAINER
        # =========================================================
        self.central_container = QWidget()
        self.central_container.setObjectName("centralContainer")
        self.setCentralWidget(self.central_container)

        root_layout = QVBoxLayout(self.central_container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_safety_bar())

        # =========================================================
        # PAGE MANAGER
        # =========================================================
        self.pages = FadingStackedWidget()
        self.pages.setObjectName("pageStack")
        root_layout.addWidget(self.pages, 1)

        self.home_page = HomePage(self)
        self.art_selection_page = ArtSelectionPage(self)
        self.running_page = RunningPage(self)
        self.complete_page = CompletePage(self)
        self.status_page = StatusPage(self)
        self.emergency_stop_page = EmergencyStopPage(self)
        self.teleop_setup_page = TeleopSetupPage(self)
        self.teleop_game_page = TeleopGamePage(self, self.jug_controller)
        self.teleop_result_page = TeleopResultPage(self)
        self.barista_page = BaristaPage(self)
        self.attract_page = AttractPage(self)

        for page in (
            self.home_page,
            self.art_selection_page,
            self.running_page,
            self.complete_page,
            self.status_page,
            self.emergency_stop_page,
            self.teleop_setup_page,
            self.teleop_game_page,
            self.teleop_result_page,
            self.barista_page,
            self.attract_page,
        ):
            self.pages.addWidget(page)

        # The E-stop screen must never wait for a fade.
        self.pages.instant_pages.add(self.emergency_stop_page)

        self.running_page.set_manual(MANUAL_POUR_CONFIRM)
        self.status_page.set_service_stats(self.service_stats)

        self.pages.setCurrentWidget(self.home_page)
        self.setStyleSheet(APP_STYLE)

        self._watching_idle = False
        self._watch_for_idle(True)

    # =========================================================
    # SAFETY BAR
    # =========================================================
    def _build_safety_bar(self):
        self.safety_bar = QWidget()
        self.safety_bar.setObjectName("safetyBar")
        self.safety_bar.setFixedHeight(58)

        safety_layout = QHBoxLayout(self.safety_bar)
        safety_layout.setContentsMargins(18, 6, 18, 6)
        safety_layout.setSpacing(10)

        # Compact status cluster on the left.
        self.status_cluster = QWidget()
        self.status_cluster.setObjectName("statusCluster")
        self.status_cluster.setFixedHeight(44)

        cluster_layout = QHBoxLayout(self.status_cluster)
        cluster_layout.setContentsMargins(7, 2, 7, 2)
        cluster_layout.setSpacing(2)

        self.cobot_chip = QLabel("●  READY")
        self.cobot_chip.setObjectName("safetyReadyChip")

        self.connection_chip = QLabel("SIMULATION")
        self.connection_chip.setObjectName("safetyNeutralChip")

        self.safety_chip = QLabel("●  SAFETY OK")
        self.safety_chip.setObjectName("safetyReadyChip")

        # Each chip is sized for its longest state so changing the text
        # (READY -> RUNNING, SAFETY OK -> E-STOP ACTIVE) never clips it.
        chip_font = make_font(CAPTION, bold=True)
        chip_metrics = QFontMetrics(chip_font)
        chip_texts = {
            self.cobot_chip: ("●  STOPPED", "●  RUNNING", "●  TELEOP"),
            self.connection_chip: ("SIMULATION",),
            self.safety_chip: ("●  E-STOP ACTIVE", "●  SAFETY OK"),
        }

        for chip, texts in chip_texts.items():
            widest = max(chip_metrics.horizontalAdvance(text) for text in texts)
            chip.setFont(chip_font)
            chip.setMinimumWidth(widest + CHIP_PADDING)
            chip.setAlignment(Qt.AlignCenter)
            chip.setFixedHeight(36)

        cluster_layout.addWidget(self.cobot_chip)
        cluster_layout.addWidget(self._create_separator())
        cluster_layout.addWidget(self.connection_chip)
        cluster_layout.addWidget(self._create_separator())
        cluster_layout.addWidget(self.safety_chip)

        # Emergency control remains isolated on the right.
        self.estop_button = QPushButton("EMERGENCY STOP")
        self.estop_button.setObjectName("estopButton")
        self.estop_button.setProperty("active", False)
        # Wide enough for either label in whatever font the device has.
        estop_font = make_font(LABEL, bold=True)
        estop_metrics = QFontMetrics(estop_font)
        estop_width = max(
            estop_metrics.horizontalAdvance(text)
            for text in ("EMERGENCY STOP", "E-STOP ACTIVE")
        )
        self.estop_button.setFixedSize(max(200, estop_width + 44), 46)
        self.estop_button.setCursor(Qt.PointingHandCursor)
        self.estop_button.setFont(estop_font)
        self.estop_button.clicked.connect(
            self.activate_estop
        )

        safety_layout.addWidget(self.status_cluster)
        safety_layout.addStretch()
        safety_layout.addWidget(self.estop_button)

        return self.safety_bar

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
    # IDLE / ATTRACT SCREEN
    # =========================================================
    def _watch_for_idle(self, watching):
        """Only Home can go idle, so only watch touches while it is shown.

        A Python event filter sees every event in the app, so it is not
        left installed while animations run on other pages.
        """
        if watching == self._watching_idle:
            if watching:
                self.idle_timer.start()
            return

        app = QApplication.instance()
        if watching:
            app.installEventFilter(self)
            self.idle_timer.start()
        else:
            app.removeEventFilter(self)
            self.idle_timer.stop()

        self._watching_idle = watching

    def eventFilter(self, watched, event):
        if event.type() in ACTIVITY_EVENTS:
            self.idle_timer.start()
        return False

    def _show_attract_if_idle(self):
        if self.estop_active or self.pages.currentWidget() is not self.home_page:
            return

        self._watch_for_idle(False)
        self.attract_page.show_stats(
            self.service_stats.total,
            top_score(self.service_stats),
        )
        self.pages.setCurrentWidget(self.attract_page)

    # =========================================================
    # TODAY'S POURS
    # =========================================================
    def _load_todays_stats(self):
        self._stats_day = datetime.now().date()
        self.service_stats = stats_from_records(
            load_records(SERVICE_LOG_PATH, self._stats_day)
        )

    def _record_pour(self, choice, art="", score=None):
        now = datetime.now()

        # Running past midnight starts a fresh day.
        if now.date() != self._stats_day:
            self._load_todays_stats()

        record = PourRecord(
            timestamp=now,
            choice=choice,
            art=art,
            score=score,
        )
        self.service_stats = record_pour(self.service_stats, record)
        append_record(SERVICE_LOG_PATH, record)
        self.status_page.set_service_stats(self.service_stats)

    def top_challenge_score(self):
        return top_score(self.service_stats)

    # =========================================================
    # NAVIGATION GUARD
    # =========================================================
    def _show_if_safe(self, page):
        if self.estop_active:
            self.pages.setCurrentWidget(
                self.emergency_stop_page
            )
            return False

        self._watch_for_idle(page is self.home_page)
        self.pages.setCurrentWidget(page)
        return True

    # =========================================================
    # NAVIGATION
    # =========================================================
    def show_home_page(self):
        self.complete_page.stop_countdown()
        self.barista_page.stop_countdown()
        self._leave_teleop()

        if self._show_if_safe(self.home_page):
            print("Opening HOME page")

    def show_art_selection_page(self):
        if self._show_if_safe(self.art_selection_page):
            print("Opening Art Selection")

    def show_status_page(self):
        self.status_page.set_service_stats(self.service_stats)
        if self._show_if_safe(self.status_page):
            print("Opening System Status")

    def show_barista_page(self):
        if self._show_if_safe(self.barista_page):
            print("Barista pour chosen")
            self.barista_page.start_countdown()

    def finish_barista_pour(self):
        """Count the barista pour once the customer moves on, not on the first
        tap, so an accidental tap followed by Back is not logged."""
        if self.pages.currentWidget() is self.barista_page and not self.estop_active:
            self._record_pour(CHOICE_BARISTA)

        self.show_home_page()

    # =========================================================
    # TELEOP LATTE CHALLENGE
    # =========================================================
    def show_teleop_setup_page(self):
        self._leave_teleop()
        self.teleop_setup_page.refresh_best_scores(
            dict(self.service_stats.best_scores)
        )

        if self._show_if_safe(self.teleop_setup_page):
            print("Opening Latte Challenge")

    def start_teleop_challenge(self, challenge):
        if self.estop_active:
            print("Cannot start teleop: E-STOP is active.")
            self.pages.setCurrentWidget(self.emergency_stop_page)
            return

        print(f"Starting teleop challenge: {challenge.art_name}")

        self.teleop_result_page.stop_countdown()
        self.pages.setCurrentWidget(self.teleop_game_page)
        self.teleop_game_page.start(challenge)
        self._set_cobot_running("TELEOP")

    def show_teleop_result(self, challenge, stats, art_image):
        if self.estop_active:
            return

        result = score_pour(stats, challenge)
        previous_best = best_score(self.service_stats, challenge.key)
        is_new_best = previous_best is not None and result.score > previous_best

        print(f"Teleop {challenge.art_name} scored {result.score}")
        self._record_pour(CHOICE_TELEOP, challenge.key, result.score)

        self._set_cobot_ready()
        # Switch first so the score counts up after the fade, not under it.
        self.pages.setCurrentWidget(self.teleop_result_page)
        self.teleop_result_page.show_result(
            challenge,
            result,
            art_image,
            best_score(self.service_stats, challenge.key),
            is_new_best,
        )

    def _leave_teleop(self):
        """Stop any pour or result countdown when navigating away."""
        was_pouring = self.pages.currentWidget() is self.teleop_game_page

        self.teleop_game_page.abort()
        self.teleop_result_page.stop_countdown()

        if was_pouring and not self.estop_active:
            self._set_cobot_ready()

    # =========================================================
    # COBOT POUR
    # =========================================================
    def start_selected_art(self, art_name):
        if self.estop_active:
            print("Cannot start operation: E-STOP is active.")
            self.pages.setCurrentWidget(
                self.emergency_stop_page
            )
            return

        # A double tap on the pour button must not start two pours.
        if self.pages.currentWidget() is self.running_page:
            return

        self.selected_art = art_name

        print(f"Selected art: {art_name}")
        print("Starting operation...")

        self.running_page.set_selected_art(art_name)
        self.complete_page.set_selected_art(art_name)
        self.pages.setCurrentWidget(self.running_page)

        self._set_cobot_running()

        # With manual confirm, staff tap POUR FINISHED instead.
        if not MANUAL_POUR_CONFIRM:
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
        self.show_home_page()

    def complete_operation(self):
        if self.estop_active or self.pages.currentWidget() is not self.running_page:
            return

        print("Operation completed")

        self.operation_timer.stop()
        self.progress_timer.stop()
        self.operation_elapsed.invalidate()
        self.running_page.set_progress(100)

        self._record_pour(CHOICE_COBOT, self.selected_art or "")
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

    def _set_cobot_running(self, label="RUNNING"):
        self.cobot_chip.setText(f"●  {label}")
        self._set_object_name(
            self.cobot_chip,
            "safetyActiveChip",
        )

        self.safety_chip.setText("●  SAFETY OK")
        self._set_object_name(
            self.safety_chip,
            "safetyReadyChip",
        )

        self.status_page.set_cobot_status(label)

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
        self.teleop_game_page.abort()
        self.teleop_result_page.stop_countdown()
        self.complete_page.stop_countdown()
        self.barista_page.stop_countdown()
        self._watch_for_idle(False)

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
        self.show_home_page()


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
