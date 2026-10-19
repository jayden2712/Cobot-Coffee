from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
)

from config import ASSETS_DIR
from typography import BODY, DISPLAY, LABEL, TITLE, make_font


class RunningPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("runningPage")
        self.selected_art = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(52, 16, 52, 20)
        main_layout.setSpacing(8)

        main_layout.addStretch(1)

        eyebrow = QLabel("LATTE ART IN PROGRESS")
        eyebrow.setObjectName("runningEyebrow")
        eyebrow.setAlignment(Qt.AlignCenter)
        eyebrow.setFont(make_font(LABEL, bold=True))
        main_layout.addWidget(eyebrow)

        # ---------------------------------------------------------
        # Art icon
        # ---------------------------------------------------------
        self.art_icon = QLabel()
        self.art_icon.setObjectName("runningArtIcon")
        self.art_icon.setAlignment(Qt.AlignCenter)
        self.art_icon.setFixedSize(132, 132)

        icon_row = QHBoxLayout()
        icon_row.addStretch()
        icon_row.addWidget(self.art_icon)
        icon_row.addStretch()
        main_layout.addLayout(icon_row)

        # ---------------------------------------------------------
        # Title and stage
        # ---------------------------------------------------------
        self.selected_art_label = QLabel("POURING...")
        self.selected_art_label.setObjectName("runningTitle")
        self.selected_art_label.setAlignment(Qt.AlignCenter)

        self.selected_art_label.setFont(make_font(DISPLAY, bold=True))
        main_layout.addWidget(self.selected_art_label)

        self.stage_label = QLabel("PREPARING")
        self.stage_label.setObjectName("runningStage")
        self.stage_label.setAlignment(Qt.AlignCenter)
        self.stage_label.setFont(make_font(BODY, bold=True))
        main_layout.addWidget(self.stage_label)

        main_layout.addSpacing(6)

        # ---------------------------------------------------------
        # Progress
        # ---------------------------------------------------------
        progress_row = QHBoxLayout()
        progress_row.addStretch()

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("pourProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedSize(480, 22)

        progress_row.addWidget(self.progress_bar)
        progress_row.addStretch()
        main_layout.addLayout(progress_row)

        self.progress_text = QLabel("0%")
        self.progress_text.setObjectName("progressText")
        self.progress_text.setAlignment(Qt.AlignCenter)

        self.progress_text.setFont(make_font(TITLE, bold=True))
        main_layout.addWidget(self.progress_text)

        info = QLabel("The cobot is crafting your selected latte art")
        info.setObjectName("runningInfo")
        info.setAlignment(Qt.AlignCenter)
        info.setFont(make_font(BODY))
        main_layout.addWidget(info)

        warning = QLabel("Please keep hands clear while the cobot is moving")
        warning.setObjectName("runningWarning")
        warning.setAlignment(Qt.AlignCenter)
        warning.setFont(make_font(LABEL, bold=True))
        main_layout.addWidget(warning)

        main_layout.addSpacing(8)

        # ---------------------------------------------------------
        # Cancel is intentionally visually weaker than E-stop.
        # ---------------------------------------------------------
        self.cancel_button = QPushButton("CANCEL OPERATION")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setFixedSize(320, 62)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setFont(make_font(BODY, bold=True))

        self.cancel_button.clicked.connect(
            self.main_window.cancel_operation
        )

        cancel_row = QHBoxLayout()
        cancel_row.addStretch()
        cancel_row.addWidget(self.cancel_button)
        cancel_row.addStretch()
        main_layout.addLayout(cancel_row)

        main_layout.addStretch(1)

    def set_selected_art(self, art_name):
        self.selected_art = art_name
        self.selected_art_label.setText(
            f"POURING {art_name.upper()}"
        )

        icon_path = ASSETS_DIR / f"{art_name.lower()}.png"
        pixmap = QPixmap(str(icon_path))

        if not pixmap.isNull():
            self.art_icon.setPixmap(
                pixmap.scaled(
                    104,
                    104,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            self.art_icon.setText("☕")

        self.set_progress(0)

    def set_progress(self, value):
        value = max(0, min(100, int(value)))
        self.progress_bar.setValue(value)
        self.progress_text.setText(f"{value}%")

        if value < 20:
            stage = "PREPARING"
        elif value < 85:
            stage = "POURING"
        elif value < 100:
            stage = "FINISHING"
        else:
            stage = "COMPLETE"

        self.stage_label.setText(stage)
