from PySide6.QtCore import (
    Qt,
    QEvent,
    QPoint,
    QTimer,
    QEasingCurve,
    QPropertyAnimation,
    Signal,
)

from PySide6.QtGui import QPixmap

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
)

from config import ASSETS_DIR


# =========================================================
# ART CARD
# =========================================================
class ArtCard(QFrame):

    CARD_WIDTH = 230
    CARD_HEIGHT = 270

    def __init__(self, art_name, icon_filename):
        super().__init__()

        self.art_name = art_name
        self.icon_filename = icon_filename
        self.original_pixmap = None

        self.setFixedSize(
            self.CARD_WIDTH,
            self.CARD_HEIGHT
        )

        self.setObjectName("sideArtCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        self.setLayout(layout)

        # -------------------------------------------------
        # Image
        # -------------------------------------------------
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        # Mouse/touch should pass through to carousel
        self.image_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        layout.addStretch()
        layout.addWidget(self.image_label)

        # -------------------------------------------------
        # Name
        # -------------------------------------------------
        self.name_label = QLabel(art_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setObjectName("artName")

        self.name_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        layout.addWidget(self.name_label)

        # -------------------------------------------------
        # Selected text
        # -------------------------------------------------
        self.selected_label = QLabel("")
        self.selected_label.setAlignment(Qt.AlignCenter)
        self.selected_label.setObjectName("artSelected")

        self.selected_label.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        layout.addWidget(self.selected_label)

        layout.addStretch()

        # -------------------------------------------------
        # Load image
        # -------------------------------------------------
        icon_path = ASSETS_DIR / icon_filename

        if icon_path.exists():

            self.original_pixmap = QPixmap(
                str(icon_path)
            )

        self.set_selected(False)

    # =====================================================
    # Selected / unselected appearance
    # =====================================================
    def set_selected(self, selected):

        if selected:

            self.setObjectName("selectedArtCard")

            self.selected_label.setText(
                "Selected"
            )

            image_size = 145

        else:

            self.setObjectName("sideArtCard")

            self.selected_label.setText("")

            image_size = 105

        # Refresh stylesheet after objectName changes
        self.style().unpolish(self)
        self.style().polish(self)

        # Update image size
        if self.original_pixmap:

            pixmap = self.original_pixmap.scaled(
                image_size,
                image_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

            self.image_label.setPixmap(pixmap)

        else:

            self.image_label.setText("☕")

            font = self.image_label.font()
            font.setPointSize(
                55 if selected else 40
            )

            self.image_label.setFont(font)


# =========================================================
# SWIPE CAROUSEL
# =========================================================
class SwipeCarousel(QFrame):

    selection_changed = Signal(str)

    CARD_WIDTH = 230
    CARD_HEIGHT = 270

    SPACING = 35

    STEP = CARD_WIDTH + SPACING

    SWIPE_THRESHOLD = 45

    def __init__(self, arts):
        super().__init__()

        self.arts = arts

        self.setObjectName("swipeCarousel")

        self.setFixedSize(
            3 * self.CARD_WIDTH + 2 * self.SPACING,
            300
        )

        # -------------------------------------------------
        # Drag state
        # -------------------------------------------------
        self.dragging = False

        self.drag_start_x = 0
        self.track_start_x = 0

        # We repeat the art list 3 times:
        #
        # H T R | H T R | H T R
        #
        # This allows continuous/infinite-looking scrolling.
        self.repeated_arts = (
            self.arts
            + self.arts
            + self.arts
        )

        # Start in the middle copy
        self.current_slot = len(self.arts)

        self.cards = []

        # -------------------------------------------------
        # Track containing cards
        # -------------------------------------------------
        self.track = QWidget(self)

        track_layout = QHBoxLayout()

        track_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        track_layout.setSpacing(
            self.SPACING
        )

        self.track.setLayout(
            track_layout
        )

        # -------------------------------------------------
        # Create repeated cards
        # -------------------------------------------------
        for art in self.repeated_arts:

            card = ArtCard(
                art["name"],
                art["icon"],
            )

            self.cards.append(card)

            track_layout.addWidget(card)

            # Receive mouse events from cards
            card.installEventFilter(self)

            # Enable touch
            card.setAttribute(
                Qt.WA_AcceptTouchEvents,
                True,
            )

        # Calculate track size
        track_width = (
            len(self.cards)
            * self.CARD_WIDTH
            +
            (len(self.cards) - 1)
            * self.SPACING
        )

        self.track.setFixedSize(
            track_width,
            self.CARD_HEIGHT,
        )

        self.track.move(
            0,
            15,
        )

        # Events from track itself
        self.track.installEventFilter(self)

        self.track.setAttribute(
            Qt.WA_AcceptTouchEvents,
            True,
        )

        self.installEventFilter(self)

        self.setAttribute(
            Qt.WA_AcceptTouchEvents,
            True,
        )

        # -------------------------------------------------
        # Snap animation
        # -------------------------------------------------
        self.snap_animation = QPropertyAnimation(
            self.track,
            b"pos",
            self,
        )

        self.snap_animation.setDuration(
            260
        )

        self.snap_animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.snap_animation.finished.connect(
            self.finish_snap
        )

        # Wait until widget gets its real width
        QTimer.singleShot(
            0,
            self.reset_position
        )

    # =====================================================
    # Carousel geometry
    # =====================================================
    def center_x(self):

        return (
            self.width()
            - self.CARD_WIDTH
        ) // 2

    def target_x(self, slot):

        return (
            self.center_x()
            - slot * self.STEP
        )

    # =====================================================
    # Initial / resize position
    # =====================================================
    def reset_position(self):

        self.track.move(
            self.target_x(
                self.current_slot
            ),
            15,
        )

        self.update_selected_card()

    def resizeEvent(self, event):

        super().resizeEvent(event)

        if not self.dragging:

            self.track.move(
                self.target_x(
                    self.current_slot
                ),
                15,
            )

    # =====================================================
    # Find card nearest screen centre
    # =====================================================
    def nearest_slot(self):

        position = (
            self.center_x()
            - self.track.x()
        )

        slot = round(
            position / self.STEP
        )

        slot = max(
            0,
            min(
                slot,
                len(self.cards) - 1,
            )
        )

        return slot

    # =====================================================
    # Update selected visual
    # =====================================================
    def update_selected_card(self):

        nearest = self.nearest_slot()

        for index, card in enumerate(
            self.cards
        ):

            card.set_selected(
                index == nearest
            )

        art_index = (
            nearest
            % len(self.arts)
        )

        art_name = self.arts[
            art_index
        ]["name"]

        self.selection_changed.emit(
            art_name
        )

    # =====================================================
    # Mouse + touch event filter
    # =====================================================
    def eventFilter(
        self,
        watched,
        event,
    ):

        event_type = event.type()

        # =================================================
        # MOUSE PRESS
        # =================================================
        if (
            event_type
            == QEvent.MouseButtonPress
        ):

            if (
                event.button()
                == Qt.LeftButton
            ):

                self.start_drag(
                    event.globalPosition().x()
                )

                return True

        # =================================================
        # MOUSE MOVE
        # =================================================
        elif (
            event_type
            == QEvent.MouseMove
        ):

            if (
                self.dragging
                and
                event.buttons()
                & Qt.LeftButton
            ):

                self.drag_to(
                    event.globalPosition().x()
                )

                return True

        # =================================================
        # MOUSE RELEASE
        # =================================================
        elif (
            event_type
            == QEvent.MouseButtonRelease
        ):

            if self.dragging:

                self.end_drag(
                    event.globalPosition().x()
                )

                return True

        # =================================================
        # TOUCH BEGIN
        # =================================================
        elif (
            event_type
            == QEvent.TouchBegin
        ):

            points = event.points()

            if points:

                self.start_drag(
                    points[0]
                    .globalPosition()
                    .x()
                )

                return True

        # =================================================
        # TOUCH MOVE
        # =================================================
        elif (
            event_type
            == QEvent.TouchUpdate
        ):

            points = event.points()

            if (
                points
                and self.dragging
            ):

                self.drag_to(
                    points[0]
                    .globalPosition()
                    .x()
                )

                return True

        # =================================================
        # TOUCH END
        # =================================================
        elif (
            event_type
            == QEvent.TouchEnd
        ):

            points = event.points()

            if (
                points
                and self.dragging
            ):

                self.end_drag(
                    points[0]
                    .globalPosition()
                    .x()
                )

                return True

        return super().eventFilter(
            watched,
            event,
        )

    # =====================================================
    # Begin drag
    # =====================================================
    def start_drag(self, global_x):

        # Stop snap if user grabs it while moving
        if (
            self.snap_animation.state()
            == QPropertyAnimation.Running
        ):

            self.snap_animation.stop()

        self.dragging = True

        self.drag_start_x = global_x

        self.track_start_x = (
            self.track.x()
        )

    # =====================================================
    # Follow finger / mouse
    # =====================================================
    def drag_to(self, global_x):

        if not self.dragging:
            return

        difference = (
            global_x
            - self.drag_start_x
        )

        new_x = (
            self.track_start_x
            + difference
        )

        # THIS is the part that makes cards
        # physically follow your finger.
        self.track.move(
            int(new_x),
            15,
        )

        self.update_selected_card()

    # =====================================================
    # Release
    # =====================================================
    def end_drag(self, global_x):

        if not self.dragging:
            return

        difference = (
            global_x
            - self.drag_start_x
        )

        self.dragging = False

        nearest = self.nearest_slot()

        # If swipe clearly crossed threshold,
        # force at least one card movement.
        if abs(difference) > self.SWIPE_THRESHOLD:

            if difference < 0:

                # Swipe left → next
                nearest = (
                    self.current_slot + 1
                )

            else:

                # Swipe right → previous
                nearest = (
                    self.current_slot - 1
                )

        nearest = max(
            0,
            min(
                nearest,
                len(self.cards) - 1,
            )
        )

        self.animate_to_slot(
            nearest
        )

    # =====================================================
    # Animate snap
    # =====================================================
    def animate_to_slot(
        self,
        slot,
    ):

        self.current_slot = slot

        self.snap_animation.stop()

        self.snap_animation.setStartValue(
            self.track.pos()
        )

        self.snap_animation.setEndValue(
            QPoint(
                self.target_x(slot),
                15,
            )
        )

        self.snap_animation.start()

    # =====================================================
    # Called after snap completes
    # =====================================================
    def finish_snap(self):

        total = len(self.arts)

        # Move back into middle repeated set.
        #
        # Example:
        #
        # index 6 → index 3
        #
        # Same art, so user cannot see this reset.
        normalized_slot = (
            total
            +
            (
                self.current_slot
                % total
            )
        )

        self.current_slot = (
            normalized_slot
        )

        self.track.move(
            self.target_x(
                self.current_slot
            ),
            15,
        )

        self.update_selected_card()

    # =====================================================
    # Arrow navigation
    # =====================================================
    def previous(self):

        self.animate_to_slot(
            self.current_slot - 1
        )

    def next(self):

        self.animate_to_slot(
            self.current_slot + 1
        )

    # =====================================================
    # Current selected art
    # =====================================================
    def current_art(self):

        index = (
            self.current_slot
            % len(self.arts)
        )

        return self.arts[index]


# =========================================================
# ART SELECTION PAGE
# =========================================================
class ArtSelectionPage(QWidget):

    def __init__(self, main_window):

        super().__init__()

        self.main_window = main_window

        self.setObjectName(
            "artSelectionPage"
        )

        # =================================================
        # Art data
        # =================================================
        self.arts = [
            {
                "name": "Heart",
                "icon": "heart.png",
            },
            {
                "name": "Tulip",
                "icon": "tulip.png",
            },
            {
                "name": "Rosetta",
                "icon": "rosetta.png",
            },
        ]

        # =================================================
        # Main layout
        # =================================================
        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            30,
            15,
            30,
            20,
        )

        main_layout.setSpacing(8)

        self.setLayout(
            main_layout
        )

        # =================================================
        # Header
        # =================================================
        header = QHBoxLayout()

        self.back_button = QPushButton(
            "←"
        )

        self.back_button.setObjectName(
            "carouselBackButton"
        )

        self.back_button.setFixedSize(
            55,
            55,
        )

        back_font = (
            self.back_button.font()
        )

        back_font.setPointSize(24)
        back_font.setBold(True)

        self.back_button.setFont(
            back_font
        )

        self.back_button.clicked.connect(
            self.main_window.show_home_page
        )

        header.addWidget(
            self.back_button
        )

        header.addStretch()

        title = QLabel(
            "SELECT YOUR LATTE ART"
        )

        title.setObjectName(
            "carouselTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        font = title.font()

        font.setPointSize(27)
        font.setBold(True)

        title.setFont(font)

        header.addWidget(title)

        header.addStretch()

        spacer = QWidget()

        spacer.setFixedSize(
            55,
            55,
        )

        header.addWidget(spacer)

        main_layout.addLayout(
            header
        )

        # =================================================
        # Subtitle
        # =================================================
        subtitle = QLabel(
            "Swipe to explore your latte art"
        )

        subtitle.setObjectName(
            "carouselSubtitle"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        font = subtitle.font()
        font.setPointSize(13)

        subtitle.setFont(font)

        main_layout.addWidget(
            subtitle
        )

        # =================================================
        # Carousel + arrow buttons
        # =================================================
        carousel_row = QHBoxLayout()

        # LEFT
        self.left_button = QPushButton(
            "‹"
        )

        self.left_button.setObjectName(
            "carouselArrow"
        )

        self.left_button.setFixedSize(
            55,
            110,
        )

        arrow_font = (
            self.left_button.font()
        )

        arrow_font.setPointSize(38)
        arrow_font.setBold(True)

        self.left_button.setFont(
            arrow_font
        )

        carousel_row.addWidget(
            self.left_button
        )

        # CAROUSEL
        self.carousel = SwipeCarousel(
            self.arts
        )

        carousel_row.addWidget(
            self.carousel,
            alignment=Qt.AlignCenter,
        )

        # RIGHT
        self.right_button = QPushButton(
            "›"
        )

        self.right_button.setObjectName(
            "carouselArrow"
        )

        self.right_button.setFixedSize(
            55,
            110,
        )

        self.right_button.setFont(
            arrow_font
        )

        carousel_row.addWidget(
            self.right_button
        )

        main_layout.addLayout(
            carousel_row
        )

        self.left_button.clicked.connect(
            self.carousel.previous
        )

        self.right_button.clicked.connect(
            self.carousel.next
        )

        # =================================================
        # Indicator
        # =================================================
        self.indicator_label = QLabel(
            "●   ○   ○"
        )

        self.indicator_label.setObjectName(
            "carouselIndicator"
        )

        self.indicator_label.setAlignment(
            Qt.AlignCenter
        )

        main_layout.addWidget(
            self.indicator_label
        )

        # =================================================
        # Select button
        # =================================================
        select_row = QHBoxLayout()

        select_row.addStretch()

        self.select_button = QPushButton(
            "CREATE HEART"
        )

        self.select_button.setObjectName(
            "selectArtButton"
        )

        self.select_button.setFixedSize(
            330,
            60,
        )

        font = (
            self.select_button.font()
        )

        font.setPointSize(18)
        font.setBold(True)

        self.select_button.setFont(font)

        select_row.addWidget(
            self.select_button
        )

        select_row.addStretch()

        main_layout.addLayout(
            select_row
        )

        # =================================================
        # Connections
        # =================================================
        self.carousel.selection_changed.connect(
            self.on_selection_changed
        )

        self.select_button.clicked.connect(
            self.select_current_art
        )

        # =================================================
        # Page styling
        # =================================================
        self.setStyleSheet(
            """
            QWidget#artSelectionPage {
                background-color: #F6F1E8;
            }

            QLabel#carouselTitle {
                color: #2D2521;
            }

            QLabel#carouselSubtitle {
                color: #756A63;
            }

            QFrame#swipeCarousel {
                background-color: transparent;
                border: none;
            }

            QFrame#sideArtCard {
                background-color: #E9E1D7;

                border: 2px solid #D8CCBE;

                border-radius: 24px;
            }

            QFrame#selectedArtCard {
                background-color: white;

                border: 4px solid #6F4E37;

                border-radius: 26px;
            }

            QLabel#artName {
                color: #2D2521;

                font-size: 20px;

                font-weight: bold;
            }

            QLabel#artSelected {
                color: #8A776B;

                font-size: 12px;

                font-weight: bold;
            }

            QPushButton#carouselArrow {
                background-color: transparent;

                border: none;

                color: #6F4E37;
            }

            QPushButton#carouselArrow:hover {
                background-color: #E7DDD0;
            }

            QLabel#carouselIndicator {
                color: #6F4E37;

                font-size: 16px;

                font-weight: bold;
            }

            QPushButton#selectArtButton {
                background-color: #6F4E37;

                color: white;

                border: none;

                border-radius: 20px;
            }

            QPushButton#selectArtButton:hover {
                background-color: #805B42;
            }

            QPushButton#selectArtButton:pressed {
                background-color: #523729;
            }

            QPushButton#carouselBackButton {
                background-color: transparent;

                color: #2D2521;

                border: none;
            }

            QPushButton#carouselBackButton:hover {
                background-color: #E7DDD0;

                border-radius: 18px;
            }
            """
        )

    # =====================================================
    # Selected card changed
    # =====================================================
    def on_selection_changed(
        self,
        art_name,
    ):

        self.select_button.setText(
            f"CREATE {art_name.upper()}"
        )

        current_index = next(
            index
            for index, art
            in enumerate(self.arts)
            if art["name"] == art_name
        )

        dots = []

        for index in range(
            len(self.arts)
        ):

            if index == current_index:

                dots.append("●")

            else:

                dots.append("○")

        self.indicator_label.setText(
            "   ".join(dots)
        )

    # =====================================================
    # Confirm selection
    # =====================================================
    def select_current_art(self):

        selected_art = (
            self.carousel.current_art()
        )

        art_name = selected_art[
            "name"
        ]

        print(
            f"User selected: {art_name}"
        )

        self.main_window.start_selected_art(
            art_name
        )