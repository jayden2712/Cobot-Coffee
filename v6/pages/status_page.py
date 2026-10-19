from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)

from service_log import CHOICE_LABELS, CHOICES, ServiceStats, top_score
from typography import BODY, CAPTION, DISPLAY, HEADLINE, LABEL, make_font


class StatusPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("statusPage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(34, 16, 34, 24)
        main_layout.setSpacing(16)

        # =========================================================
        # HEADER
        # =========================================================
        header = QHBoxLayout()

        self.back_button = QPushButton("←")
        self.back_button.setObjectName("pageBackButton")
        self.back_button.setFixedSize(52, 52)
        self.back_button.setCursor(Qt.PointingHandCursor)

        self.back_button.setFont(make_font(HEADLINE, bold=True))
        self.back_button.clicked.connect(
            self.main_window.show_home_page
        )

        title = QLabel("SYSTEM STATUS")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(make_font(DISPLAY, bold=True))

        spacer = QWidget()
        spacer.setFixedSize(52, 52)

        header.addWidget(self.back_button)
        header.addStretch()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(spacer)

        main_layout.addLayout(header)

        # =========================================================
        # 2 x 2 STATUS CARD GRID
        # =========================================================
        row_one = QHBoxLayout()
        row_one.setSpacing(16)

        cobot_card, self.cobot_value = self._create_status_card(
            "COBOT",
            "READY",
            "Current operating state",
            "statusValueGood",
        )

        connection_card, self.connection_value = self._create_status_card(
            "CONNECTION",
            "SIMULATION",
            "Robot communication mode",
            "statusValueNeutral",
        )

        row_one.addWidget(cobot_card)
        row_one.addWidget(connection_card)

        row_two = QHBoxLayout()
        row_two.setSpacing(16)

        safety_card, self.safety_value = self._create_status_card(
            "SAFETY",
            "OK",
            "Safety system state",
            "statusValueGood",
        )

        estop_card, self.estop_value = self._create_status_card(
            "EMERGENCY STOP",
            "RELEASED",
            "Emergency stop input",
            "statusValueGood",
        )

        row_two.addWidget(safety_card)
        row_two.addWidget(estop_card)

        main_layout.addLayout(row_one)
        main_layout.addLayout(row_two)
        main_layout.addWidget(self._create_today_card())
        main_layout.addStretch(1)

    def _create_status_card(
        self,
        title_text,
        value_text,
        hint_text,
        value_object_name,
    ):
        card = QFrame()
        card.setObjectName("statusCard")
        card.setMinimumHeight(118)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(5)

        title = QLabel(title_text)
        title.setObjectName("statusCardTitle")
        title.setFont(make_font(LABEL, bold=True))

        value = QLabel(value_text)
        value.setObjectName(value_object_name)
        value.setFont(make_font(HEADLINE, bold=True))

        hint = QLabel(hint_text)
        hint.setObjectName("statusCardHint")
        hint.setFont(make_font(CAPTION))

        layout.addWidget(title)
        layout.addSpacing(5)
        layout.addWidget(value)
        layout.addStretch()
        layout.addWidget(hint)

        return card, value

    def _create_today_card(self):
        """Today's pours by choice: the customer-preference evidence."""
        card = QFrame()
        card.setObjectName("statusCard")

        layout = QHBoxLayout(card)
        layout.setContentsMargins(22, 14, 22, 14)
        layout.setSpacing(20)

        title = QLabel("TODAY")
        title.setObjectName("statusCardTitle")
        title.setFont(make_font(LABEL, bold=True))
        layout.addWidget(title, alignment=Qt.AlignTop)

        self.today_values = {}
        for key in ("total", *CHOICES):
            column = QVBoxLayout()
            column.setSpacing(0)

            value = QLabel("0")
            value.setObjectName("statusValueNeutral")
            value.setFont(make_font(HEADLINE, bold=True))

            name = QLabel("All pours" if key == "total" else CHOICE_LABELS[key])
            name.setObjectName("statusCardHint")
            name.setFont(make_font(CAPTION))

            column.addWidget(value)
            column.addWidget(name)
            layout.addLayout(column)
            self.today_values[key] = value

        layout.addStretch()

        self.best_value = QLabel("—")
        self.best_value.setObjectName("statusValueGood")
        self.best_value.setAlignment(Qt.AlignRight)
        self.best_value.setFont(make_font(BODY, bold=True))
        layout.addWidget(self.best_value)

        return card

    def set_service_stats(self, stats: ServiceStats):
        self.today_values["total"].setText(str(stats.total))
        for choice in CHOICES:
            self.today_values[choice].setText(str(stats.count(choice)))

        best = top_score(stats)
        if best is None:
            self.best_value.setText("No challenge\nscores yet")
        else:
            art, score = best
            self.best_value.setText(f"Best challenge\n{score} on {art.title()}")

    @staticmethod
    def _apply_value_style(widget, object_name):
        widget.setObjectName(object_name)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def set_cobot_status(self, status):
        status = status.upper()
        self.cobot_value.setText(status)

        if status in ("READY", "COMPLETE"):
            style = "statusValueGood"
        elif status == "STOPPED":
            style = "statusValueDanger"
        else:
            style = "statusValueNeutral"

        self._apply_value_style(self.cobot_value, style)

    def set_connection_status(self, status):
        self.connection_value.setText(status.upper())
        self._apply_value_style(
            self.connection_value,
            "statusValueNeutral",
        )

    def set_estop_status(self, active):
        if active:
            self.estop_value.setText("ACTIVE")
            self.safety_value.setText("STOPPED")
            self.cobot_value.setText("STOPPED")

            for widget in (
                self.estop_value,
                self.safety_value,
                self.cobot_value,
            ):
                self._apply_value_style(
                    widget,
                    "statusValueDanger",
                )
        else:
            self.estop_value.setText("RELEASED")
            self.safety_value.setText("OK")
            self.cobot_value.setText("READY")

            for widget in (
                self.estop_value,
                self.safety_value,
                self.cobot_value,
            ):
                self._apply_value_style(
                    widget,
                    "statusValueGood",
                )
