import math
import time
from collections import deque

from PySide6.QtCore import (
    Qt,
    QEvent,
    QPointF,
    QRectF,
    QTimer,
    QEasingCurve,
    QPropertyAnimation,
    Property,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsObject,
    QGraphicsScene,
    QGraphicsView,
)

from config import ASSETS_DIR


# =========================================================
# HELPERS
# =========================================================
def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * t


def lerp_point(a: QPointF, b: QPointF, t: float) -> QPointF:
    """Linear interpolation between two QPointF values."""
    return QPointF(
        lerp(a.x(), b.x(), t),
        lerp(a.y(), b.y(), t),
    )


# =========================================================
# GRAPHICS CARD
# =========================================================
class ArtCardItem(QGraphicsObject):
    """
    Lightweight latte-art card.

    The card itself keeps one logical size.
    QGraphicsScene handles pos / scale / opacity, so no QWidget
    layout recalculation happens during drag or inertia.
    """

    BASE_WIDTH = 230
    BASE_HEIGHT = 275

    def __init__(self, art_name, icon_filename, description=""):
        super().__init__()

        self.art_name = art_name
        self.description = description

        self.selected = False
        self.pressed = False
        self.art_pixmap = None

        # Mouse/touch is handled by the QGraphicsView.
        self.setAcceptedMouseButtons(Qt.NoButton)

        # Load and resize the artwork ONCE.
        icon_path = ASSETS_DIR / icon_filename

        if icon_path.exists():
            original = QPixmap(str(icon_path))

            if not original.isNull():
                self.art_pixmap = original.scaled(
                    150,
                    150,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )

    def boundingRect(self):
        return QRectF(
            -self.BASE_WIDTH / 2,
            -self.BASE_HEIGHT / 2,
            self.BASE_WIDTH,
            self.BASE_HEIGHT,
        )

    def set_selected(self, selected):
        if self.selected == selected:
            return

        self.selected = selected
        self.update()

    def set_pressed(self, pressed):
        if self.pressed == pressed:
            return

        self.pressed = pressed
        self.update()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        rect = self.boundingRect()

        # CoBotics-inspired palette
        espresso = QColor("#2F1E12")
        selected_border = QColor("#7A5538")
        side_border = QColor("#D2BDA7")
        selected_fill = QColor("#FFFDFC")
        side_fill = QColor("#EADBCB")
        pressed_fill = QColor("#DFC9B4")
        description_colour = QColor("#9A816B")

        # -------------------------------------------------
        # Soft selected shadow.
        # Painted directly instead of QGraphicsEffect.
        # -------------------------------------------------
        if self.selected:
            shadow_rect = QRectF(
                rect.left() + 8,
                rect.top() + 12,
                rect.width() - 12,
                rect.height() - 12,
            )

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(47, 30, 18, 28))
            painter.drawRoundedRect(
                shadow_rect,
                25,
                25,
            )

        # -------------------------------------------------
        # Card body
        # -------------------------------------------------
        if self.pressed:
            fill = pressed_fill
        elif self.selected:
            fill = selected_fill
        else:
            fill = side_fill

        border = (
            selected_border
            if self.selected
            else side_border
        )

        border_width = 4 if self.selected else 2

        painter.setBrush(fill)
        painter.setPen(QPen(border, border_width))

        painter.drawRoundedRect(
            rect.adjusted(4, 4, -4, -4),
            25,
            25,
        )

        # -------------------------------------------------
        # Artwork
        # -------------------------------------------------
        artwork_area = QRectF(
            rect.left() + 28,
            rect.top() + 25,
            rect.width() - 56,
            155,
        )

        if self.art_pixmap is not None:
            x = (
                artwork_area.center().x()
                - self.art_pixmap.width() / 2
            )
            y = (
                artwork_area.center().y()
                - self.art_pixmap.height() / 2
            )

            painter.drawPixmap(
                int(x),
                int(y),
                self.art_pixmap,
            )

        else:
            # Fallback placeholder
            painter.setPen(QPen(QColor("#B89067"), 3))
            painter.setBrush(QColor("#F5E8DA"))

            cup_rect = QRectF(
                artwork_area.center().x() - 45,
                artwork_area.center().y() - 32,
                90,
                64,
            )

            painter.drawRoundedRect(
                cup_rect,
                30,
                30,
            )

        # -------------------------------------------------
        # Name
        # -------------------------------------------------
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)

        painter.setFont(name_font)
        painter.setPen(espresso)

        painter.drawText(
            QRectF(
                rect.left() + 12,
                rect.top() + 188,
                rect.width() - 24,
                36,
            ),
            Qt.AlignCenter,
            self.art_name.upper(),
        )

        # -------------------------------------------------
        # Description
        # -------------------------------------------------
        description_font = QFont()
        description_font.setPointSize(10)

        painter.setFont(description_font)
        painter.setPen(description_colour)

        painter.drawText(
            QRectF(
                rect.left() + 12,
                rect.top() + 225,
                rect.width() - 24,
                25,
            ),
            Qt.AlignCenter,
            self.description,
        )


# =========================================================
# REVOLVING CAROUSEL
# =========================================================
class RevolvingCarouselView(QGraphicsView):
    """
    Three-card carousel with:

    1. Direct manipulation
       - Hold mouse/finger
       - Cards follow the pointer continuously

    2. Revolving-door depth
       - Side card moves behind the centre card
       - Scale and opacity change continuously

    3. Nearest-card snapping
       - Slow release snaps to nearest stable card

    4. Flick / inertia
       - Fast release continues spinning
       - Velocity decays with friction
       - It may pass through several cards
       - It finally snaps to the nearest card

    There are exactly THREE real ArtCardItem objects.
    """

    selection_changed = Signal(str)
    art_clicked = Signal(str)

    VIEW_WIDTH = 910
    VIEW_HEIGHT = 335

    # -----------------------------------------------------
    # Stable positions
    # -----------------------------------------------------
    LEFT_POS = QPointF(145, 175)
    CENTER_POS = QPointF(455, 165)
    RIGHT_POS = QPointF(765, 175)

    # Virtual point "behind" the carousel
    BACK_POS = QPointF(455, 142)

    # -----------------------------------------------------
    # Depth
    # -----------------------------------------------------
    SIDE_SCALE = 0.68
    CENTER_SCALE = 1.08
    BACK_SCALE = 0.38

    SIDE_OPACITY = 0.66
    CENTER_OPACITY = 1.00
    BACK_OPACITY = 0.08

    # -----------------------------------------------------
    # Direct drag tuning
    # -----------------------------------------------------
    # Pointer travel required for one complete card revolution.
    DRAG_DISTANCE = 260.0

    # Nearest-card midpoint
    SNAP_POINT = 0.50

    TAP_THRESHOLD = 10.0

    # -----------------------------------------------------
    # Snap animation
    # -----------------------------------------------------
    MIN_SNAP_MS = 100
    MAX_SNAP_MS = 250

    # -----------------------------------------------------
    # Inertia / flick physics
    # -----------------------------------------------------
    FLING_MIN_VELOCITY = 520.0      # pixels / second
    MAX_FLING_VELOCITY = 3400.0     # pixels / second

    # Larger value = stops faster.
    INERTIA_FRICTION = 4.2

    INERTIA_STOP_VELOCITY = 70.0

    # About 60 FPS
    INERTIA_INTERVAL_MS = 16

    # Only the most recent pointer movement contributes
    # to release velocity.
    VELOCITY_SAMPLE_WINDOW = 0.12   # seconds

    def __init__(self, arts):
        super().__init__()

        # =================================================
        # STATE FIRST
        # Qt can dispatch viewportEvent during setup.
        # =================================================
        self.animating = False

        self.snap_animation = None
        self.pending_art_name = None

        self.inertia_active = False
        self.inertia_velocity = 0.0
        self.inertia_last_time = 0.0

        self._rotation_progress = 0.0

        self.dragging = False
        self.drag_start_x = 0.0
        self.last_drag_x = 0.0
        self.pressed_card = None
        self.gesture_started_from_motion = False

        self.velocity_samples = deque(maxlen=16)

        # [left, center, right]
        self.order = [0, 1, 2]

        if len(arts) != 3:
            raise ValueError(
                "RevolvingCarouselView requires exactly 3 art options."
            )

        self.arts = arts

        # -------------------------------------------------
        # Inertia timer
        # -------------------------------------------------
        self.inertia_timer = QTimer(self)
        self.inertia_timer.setInterval(
            self.INERTIA_INTERVAL_MS
        )
        self.inertia_timer.setTimerType(
            Qt.PreciseTimer
        )
        self.inertia_timer.timeout.connect(
            self.update_inertia
        )

        # -------------------------------------------------
        # Scene / View
        # -------------------------------------------------
        self.scene_object = QGraphicsScene(
            0,
            0,
            self.VIEW_WIDTH,
            self.VIEW_HEIGHT,
            self,
        )

        self.setScene(self.scene_object)
        self.setFixedSize(
            self.VIEW_WIDTH,
            self.VIEW_HEIGHT,
        )

        self.setFrameShape(QGraphicsView.NoFrame)

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.setDragMode(QGraphicsView.NoDrag)

        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.SmoothPixmapTransform
        )

        self.setViewportUpdateMode(
            QGraphicsView.BoundingRectViewportUpdate
        )

        self.setOptimizationFlag(
            QGraphicsView.DontAdjustForAntialiasing,
            True,
        )

        self.setStyleSheet(
            """
            QGraphicsView {
                background: transparent;
                border: none;
            }
            """
        )

        self.viewport().setAttribute(
            Qt.WA_AcceptTouchEvents,
            True,
        )

        # -------------------------------------------------
        # EXACTLY THREE cards
        # -------------------------------------------------
        self.cards = []

        for art in self.arts:
            card = ArtCardItem(
                art["name"],
                art["icon"],
                art.get("description", ""),
            )

            self.scene_object.addItem(card)
            self.cards.append(card)

        self.apply_stable_state()

    # =====================================================
    # ORDER HELPERS
    # =====================================================
    def left_index(self):
        return self.order[0]

    def center_index(self):
        return self.order[1]

    def right_index(self):
        return self.order[2]

    def current_art(self):
        return self.arts[
            self.center_index()
        ]

    def current_art_name(self):
        return self.current_art()["name"]

    def card_position(self, card_index):
        return self.order.index(card_index)

    # =====================================================
    # ROTATION PROGRESS PROPERTY
    #
    #  0.0 = stable current centre
    # -1.0 = one full revolution left
    # +1.0 = one full revolution right
    # =====================================================
    def get_rotation_progress(self):
        return self._rotation_progress

    def set_rotation_progress(self, value):
        value = max(
            -1.0,
            min(1.0, float(value)),
        )

        self._rotation_progress = value
        self.apply_progress(value)

    rotationProgress = Property(
        float,
        get_rotation_progress,
        set_rotation_progress,
    )

    # =====================================================
    # STABLE STATE
    # =====================================================
    def apply_stable_state(self):
        self._rotation_progress = 0.0
        self.apply_progress(0.0)

        self.selection_changed.emit(
            self.current_art_name()
        )

    # =====================================================
    # CONTINUOUS VISUAL STATE
    # =====================================================
    def apply_progress(self, progress):
        left = self.cards[self.left_index()]
        center = self.cards[self.center_index()]
        right = self.cards[self.right_index()]

        # -------------------------------------------------
        # Stable
        # -------------------------------------------------
        if abs(progress) < 0.0001:
            left.setPos(self.LEFT_POS)
            center.setPos(self.CENTER_POS)
            right.setPos(self.RIGHT_POS)

            left.setScale(self.SIDE_SCALE)
            center.setScale(self.CENTER_SCALE)
            right.setScale(self.SIDE_SCALE)

            left.setOpacity(self.SIDE_OPACITY)
            center.setOpacity(self.CENTER_OPACITY)
            right.setOpacity(self.SIDE_OPACITY)

            left.setZValue(2)
            center.setZValue(4)
            right.setZValue(2)

            left.set_selected(False)
            center.set_selected(True)
            right.set_selected(False)

            return

        # -------------------------------------------------
        # Rotate LEFT
        # -------------------------------------------------
        if progress < 0:
            self._apply_left_progress(
                -progress,
                left,
                center,
                right,
            )

        # -------------------------------------------------
        # Rotate RIGHT
        # -------------------------------------------------
        else:
            self._apply_right_progress(
                progress,
                left,
                center,
                right,
            )

    # -----------------------------------------------------
    # LEFT rotation:
    #
    # LEFT   -> BACK -> RIGHT
    # CENTER -> LEFT
    # RIGHT  -> CENTER
    # -----------------------------------------------------
    def _apply_left_progress(
        self,
        t,
        left,
        center,
        right,
    ):
        t = max(0.0, min(1.0, t))

        # CENTER -> LEFT
        center.setPos(
            lerp_point(
                self.CENTER_POS,
                self.LEFT_POS,
                t,
            )
        )
        center.setScale(
            lerp(
                self.CENTER_SCALE,
                self.SIDE_SCALE,
                t,
            )
        )
        center.setOpacity(
            lerp(
                self.CENTER_OPACITY,
                self.SIDE_OPACITY,
                t,
            )
        )

        # RIGHT -> CENTER
        right.setPos(
            lerp_point(
                self.RIGHT_POS,
                self.CENTER_POS,
                t,
            )
        )
        right.setScale(
            lerp(
                self.SIDE_SCALE,
                self.CENTER_SCALE,
                t,
            )
        )
        right.setOpacity(
            lerp(
                self.SIDE_OPACITY,
                self.CENTER_OPACITY,
                t,
            )
        )

        # LEFT -> BACK -> RIGHT
        if t <= 0.5:
            u = t / 0.5

            left.setPos(
                lerp_point(
                    self.LEFT_POS,
                    self.BACK_POS,
                    u,
                )
            )
            left.setScale(
                lerp(
                    self.SIDE_SCALE,
                    self.BACK_SCALE,
                    u,
                )
            )
            left.setOpacity(
                lerp(
                    self.SIDE_OPACITY,
                    self.BACK_OPACITY,
                    u,
                )
            )

        else:
            u = (t - 0.5) / 0.5

            left.setPos(
                lerp_point(
                    self.BACK_POS,
                    self.RIGHT_POS,
                    u,
                )
            )
            left.setScale(
                lerp(
                    self.BACK_SCALE,
                    self.SIDE_SCALE,
                    u,
                )
            )
            left.setOpacity(
                lerp(
                    self.BACK_OPACITY,
                    self.SIDE_OPACITY,
                    u,
                )
            )

        left.setZValue(0)
        center.setZValue(2)
        right.setZValue(4)

        # Border emphasis transfers around halfway.
        if t < 0.5:
            center.set_selected(True)
            right.set_selected(False)
        else:
            center.set_selected(False)
            right.set_selected(True)

        left.set_selected(False)

    # -----------------------------------------------------
    # RIGHT rotation:
    #
    # RIGHT  -> BACK -> LEFT
    # CENTER -> RIGHT
    # LEFT   -> CENTER
    # -----------------------------------------------------
    def _apply_right_progress(
        self,
        t,
        left,
        center,
        right,
    ):
        t = max(0.0, min(1.0, t))

        # CENTER -> RIGHT
        center.setPos(
            lerp_point(
                self.CENTER_POS,
                self.RIGHT_POS,
                t,
            )
        )
        center.setScale(
            lerp(
                self.CENTER_SCALE,
                self.SIDE_SCALE,
                t,
            )
        )
        center.setOpacity(
            lerp(
                self.CENTER_OPACITY,
                self.SIDE_OPACITY,
                t,
            )
        )

        # LEFT -> CENTER
        left.setPos(
            lerp_point(
                self.LEFT_POS,
                self.CENTER_POS,
                t,
            )
        )
        left.setScale(
            lerp(
                self.SIDE_SCALE,
                self.CENTER_SCALE,
                t,
            )
        )
        left.setOpacity(
            lerp(
                self.SIDE_OPACITY,
                self.CENTER_OPACITY,
                t,
            )
        )

        # RIGHT -> BACK -> LEFT
        if t <= 0.5:
            u = t / 0.5

            right.setPos(
                lerp_point(
                    self.RIGHT_POS,
                    self.BACK_POS,
                    u,
                )
            )
            right.setScale(
                lerp(
                    self.SIDE_SCALE,
                    self.BACK_SCALE,
                    u,
                )
            )
            right.setOpacity(
                lerp(
                    self.SIDE_OPACITY,
                    self.BACK_OPACITY,
                    u,
                )
            )

        else:
            u = (t - 0.5) / 0.5

            right.setPos(
                lerp_point(
                    self.BACK_POS,
                    self.LEFT_POS,
                    u,
                )
            )
            right.setScale(
                lerp(
                    self.BACK_SCALE,
                    self.SIDE_SCALE,
                    u,
                )
            )
            right.setOpacity(
                lerp(
                    self.BACK_OPACITY,
                    self.SIDE_OPACITY,
                    u,
                )
            )

        right.setZValue(0)
        center.setZValue(2)
        left.setZValue(4)

        if t < 0.5:
            center.set_selected(True)
            left.set_selected(False)
        else:
            center.set_selected(False)
            left.set_selected(True)

        right.set_selected(False)

    # =====================================================
    # COMMIT ONE FULL REVOLUTION
    # =====================================================
    def commit_left_rotation(self):
        left_index = self.left_index()
        center_index = self.center_index()
        right_index = self.right_index()

        self.order = [
            center_index,
            right_index,
            left_index,
        ]

        self.selection_changed.emit(
            self.current_art_name()
        )

    def commit_right_rotation(self):
        left_index = self.left_index()
        center_index = self.center_index()
        right_index = self.right_index()

        self.order = [
            right_index,
            left_index,
            center_index,
        ]

        self.selection_changed.emit(
            self.current_art_name()
        )

    # =====================================================
    # HIT TESTING
    # =====================================================
    def card_at_view_position(self, viewport_position):
        item = self.itemAt(
            viewport_position.toPoint()
        )

        if isinstance(item, ArtCardItem):
            return item

        return None

    # =====================================================
    # VELOCITY TRACKING
    # =====================================================
    def record_velocity_sample(self, x):
        now = time.perf_counter()

        self.velocity_samples.append(
            (now, float(x))
        )

        # Keep only recent samples.
        while (
            len(self.velocity_samples) > 2
            and now - self.velocity_samples[0][0]
            > self.VELOCITY_SAMPLE_WINDOW
        ):
            self.velocity_samples.popleft()

    def calculate_release_velocity(self):
        if len(self.velocity_samples) < 2:
            return 0.0

        first_time, first_x = self.velocity_samples[0]
        last_time, last_x = self.velocity_samples[-1]

        dt = last_time - first_time

        if dt <= 0.001:
            return 0.0

        velocity = (last_x - first_x) / dt

        return max(
            -self.MAX_FLING_VELOCITY,
            min(
                self.MAX_FLING_VELOCITY,
                velocity,
            ),
        )

    # =====================================================
    # INTERRUPT ACTIVE MOTION
    # =====================================================
    def motion_is_active(self):
        snap_running = (
            self.snap_animation is not None
            and self.snap_animation.state()
            == QPropertyAnimation.Running
        )

        return (
            self.inertia_active
            or snap_running
            or self.animating
        )

    def interrupt_motion(self):
        """
        Touching the carousel while it is moving immediately stops
        inertia/snap at the current visual position.

        The user can then take direct control from that point.
        """

        if self.inertia_timer.isActive():
            self.inertia_timer.stop()

        self.inertia_active = False
        self.inertia_velocity = 0.0

        if (
            self.snap_animation is not None
            and self.snap_animation.state()
            == QPropertyAnimation.Running
        ):
            self.snap_animation.stop()

        self.snap_animation = None

        # Cancel any pending side-card auto-selection because
        # the user manually interrupted the motion.
        self.pending_art_name = None
        self.animating = False

    # =====================================================
    # DIRECT GESTURE
    # =====================================================
    def begin_gesture(self, x, pressed_card=None):
        was_moving = self.motion_is_active()

        if was_moving:
            self.interrupt_motion()

        self.gesture_started_from_motion = was_moving

        self.dragging = True
        self.drag_start_x = float(x)
        self.last_drag_x = float(x)
        self.pressed_card = pressed_card

        self.velocity_samples.clear()
        self.record_velocity_sample(x)

        if self.pressed_card is not None:
            self.pressed_card.set_pressed(True)

    def update_gesture(self, x):
        if not self.dragging:
            return

        x = float(x)

        # Incremental pointer delta lets the user drag through
        # MORE THAN ONE card while still holding.
        delta_x = x - self.last_drag_x
        self.last_drag_x = x

        self.record_velocity_sample(x)

        total_dx = x - self.drag_start_x

        if (
            abs(total_dx) > self.TAP_THRESHOLD
            and self.pressed_card is not None
        ):
            self.pressed_card.set_pressed(False)

        new_progress = (
            self._rotation_progress
            + delta_x / self.DRAG_DISTANCE
        )

        # -------------------------------------------------
        # User dragged through a complete LEFT revolution.
        # Commit it and continue from the residual progress.
        # -------------------------------------------------
        while new_progress <= -1.0:
            new_progress += 1.0
            self.commit_left_rotation()

        # -------------------------------------------------
        # Complete RIGHT revolution.
        # -------------------------------------------------
        while new_progress >= 1.0:
            new_progress -= 1.0
            self.commit_right_rotation()

        self.rotationProgress = new_progress

    def end_gesture(self, x):
        if not self.dragging:
            return

        x = float(x)
        total_dx = x - self.drag_start_x

        self.record_velocity_sample(x)

        release_velocity = (
            self.calculate_release_velocity()
        )

        tapped_card = self.pressed_card

        if self.pressed_card is not None:
            self.pressed_card.set_pressed(False)

        self.dragging = False
        self.pressed_card = None

        # -------------------------------------------------
        # Tiny movement
        # -------------------------------------------------
        if abs(total_dx) <= self.TAP_THRESHOLD:
            # If this touch was used to stop an already-moving
            # carousel, simply snap it to the nearest card.
            if self.gesture_started_from_motion:
                self.snap_to_nearest()
                return

            # Normal tap
            if tapped_card is not None:
                self.handle_card_tap(tapped_card)
            else:
                self.snap_to_nearest()

            return

        # -------------------------------------------------
        # FAST RELEASE -> inertia
        # -------------------------------------------------
        if abs(release_velocity) >= self.FLING_MIN_VELOCITY:
            self.start_inertia(
                release_velocity
            )
            return

        # -------------------------------------------------
        # SLOW RELEASE -> nearest snap
        # -------------------------------------------------
        self.snap_to_nearest()

    # =====================================================
    # NEAREST SNAP
    # =====================================================
    def snap_to_nearest(self):
        progress = self._rotation_progress

        if progress <= -self.SNAP_POINT:
            self.snap_to(-1.0)

        elif progress >= self.SNAP_POINT:
            self.snap_to(1.0)

        else:
            self.snap_to(0.0)

    def snap_to(
        self,
        target_progress,
        pending_art_name=None,
    ):
        if self.inertia_active:
            self.stop_inertia(snap=False)

        start_progress = self._rotation_progress

        self.pending_art_name = pending_art_name

        if abs(target_progress - start_progress) < 0.0001:
            self.finish_snap(target_progress)
            return

        self.animating = True

        remaining = abs(
            target_progress - start_progress
        )

        duration = int(
            lerp(
                self.MIN_SNAP_MS,
                self.MAX_SNAP_MS,
                min(1.0, remaining),
            )
        )

        animation = QPropertyAnimation(
            self,
            b"rotationProgress",
            self,
        )

        animation.setDuration(duration)
        animation.setStartValue(start_progress)
        animation.setEndValue(target_progress)
        animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.snap_animation = animation

        animation.finished.connect(
            lambda: self.finish_snap(
                target_progress
            )
        )

        animation.start()

    def finish_snap(self, target_progress):
        # -------------------------------------------------
        # Completed LEFT snap
        # -------------------------------------------------
        if target_progress <= -0.999:
            self.commit_left_rotation()

        # -------------------------------------------------
        # Completed RIGHT snap
        # -------------------------------------------------
        elif target_progress >= 0.999:
            self.commit_right_rotation()

        # New order now becomes stable.
        self._rotation_progress = 0.0
        self.animating = False
        self.snap_animation = None

        self.apply_progress(0.0)

        art_to_emit = self.pending_art_name
        self.pending_art_name = None

        if art_to_emit is not None:
            QTimer.singleShot(
                80,
                lambda: self.art_clicked.emit(
                    art_to_emit
                ),
            )

    # =====================================================
    # INERTIA / FLING
    # =====================================================
    def start_inertia(self, velocity):
        # Stop any snap that might still exist.
        if (
            self.snap_animation is not None
            and self.snap_animation.state()
            == QPropertyAnimation.Running
        ):
            self.snap_animation.stop()

        self.snap_animation = None

        self.inertia_velocity = max(
            -self.MAX_FLING_VELOCITY,
            min(
                self.MAX_FLING_VELOCITY,
                float(velocity),
            ),
        )

        self.inertia_active = True
        self.animating = True

        self.inertia_last_time = (
            time.perf_counter()
        )

        self.inertia_timer.start()

    def update_inertia(self):
        if not self.inertia_active:
            return

        now = time.perf_counter()

        dt = now - self.inertia_last_time
        self.inertia_last_time = now

        # Avoid a huge jump if one frame stalls.
        dt = max(
            0.0,
            min(dt, 0.05),
        )

        # -------------------------------------------------
        # Velocity -> carousel progress
        # -------------------------------------------------
        progress_delta = (
            self.inertia_velocity
            * dt
            / self.DRAG_DISTANCE
        )

        new_progress = (
            self._rotation_progress
            + progress_delta
        )

        # -------------------------------------------------
        # Pass through as many full cards as required.
        # -------------------------------------------------
        while new_progress <= -1.0:
            new_progress += 1.0
            self.commit_left_rotation()

        while new_progress >= 1.0:
            new_progress -= 1.0
            self.commit_right_rotation()

        self.rotationProgress = new_progress

        # -------------------------------------------------
        # Frame-rate-independent exponential friction
        # -------------------------------------------------
        decay = math.exp(
            -self.INERTIA_FRICTION * dt
        )

        self.inertia_velocity *= decay

        # -------------------------------------------------
        # Slow enough -> nearest snap
        # -------------------------------------------------
        if (
            abs(self.inertia_velocity)
            <= self.INERTIA_STOP_VELOCITY
        ):
            self.stop_inertia(
                snap=True
            )

    def stop_inertia(self, snap=False):
        if self.inertia_timer.isActive():
            self.inertia_timer.stop()

        was_active = self.inertia_active

        self.inertia_active = False
        self.inertia_velocity = 0.0

        if not was_active:
            return

        self.animating = False

        if snap:
            self.snap_to_nearest()

    # =====================================================
    # TAP CARD
    # =====================================================
    def handle_card_tap(self, tapped_card):
        card_index = self.cards.index(
            tapped_card
        )

        position = self.card_position(
            card_index
        )

        art_name = self.arts[
            card_index
        ]["name"]

        # CENTER -> choose immediately
        if position == 1:
            QTimer.singleShot(
                80,
                lambda: self.art_clicked.emit(
                    art_name
                ),
            )

        # LEFT -> revolve RIGHT into center, then choose
        elif position == 0:
            self.snap_to(
                1.0,
                pending_art_name=art_name,
            )

        # RIGHT -> revolve LEFT into center, then choose
        elif position == 2:
            self.snap_to(
                -1.0,
                pending_art_name=art_name,
            )

    # =====================================================
    # MOUSE INPUT
    # =====================================================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.begin_gesture(
                event.position().x(),
                self.card_at_view_position(
                    event.position()
                ),
            )

            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.update_gesture(
                event.position().x()
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.LeftButton
            and self.dragging
        ):
            self.end_gesture(
                event.position().x()
            )

            event.accept()
            return

        super().mouseReleaseEvent(event)

    # =====================================================
    # TOUCH INPUT
    # =====================================================
    def viewportEvent(self, event):
        event_type = event.type()

        if event_type == QEvent.TouchBegin:
            points = event.points()

            if points:
                point = points[0]

                self.begin_gesture(
                    point.position().x(),
                    self.card_at_view_position(
                        point.position()
                    ),
                )

                event.accept()
                return True

        elif event_type == QEvent.TouchUpdate:
            points = event.points()

            if points and self.dragging:
                self.update_gesture(
                    points[0].position().x()
                )

                event.accept()
                return True

        elif event_type == QEvent.TouchEnd:
            points = event.points()

            if self.dragging:
                end_x = (
                    points[0].position().x()
                    if points
                    else self.last_drag_x
                )

                self.end_gesture(end_x)

                event.accept()
                return True

        return super().viewportEvent(event)


# =========================================================
# ART SELECTION PAGE
# =========================================================
class ArtSelectionPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setObjectName("artSelectionPage")

        self.arts = [
            {
                "name": "Heart",
                "icon": "heart.png",
                "description": "Classic",
            },
            {
                "name": "Tulip",
                "icon": "tulip.png",
                "description": "Layered",
            },
            {
                "name": "Rosetta",
                "icon": "rosetta.png",
                "description": "Detailed",
            },
        ]

        # -------------------------------------------------
        # Main layout
        # -------------------------------------------------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(
            32,
            12,
            32,
            16,
        )
        main_layout.setSpacing(5)

        self.setLayout(main_layout)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------
        header_layout = QHBoxLayout()

        self.back_button = QPushButton("←")
        self.back_button.setObjectName(
            "carouselBackButton"
        )
        self.back_button.setFixedSize(
            54,
            54,
        )

        back_font = self.back_button.font()
        back_font.setPointSize(24)
        back_font.setBold(True)
        self.back_button.setFont(back_font)

        self.back_button.clicked.connect(
            self.main_window.show_home_page
        )

        header_layout.addWidget(
            self.back_button
        )
        header_layout.addStretch()

        brand_label = QLabel("CoBotics")
        brand_label.setObjectName(
            "brandLabel"
        )

        brand_font = brand_label.font()
        brand_font.setPointSize(15)
        brand_font.setBold(True)
        brand_label.setFont(brand_font)

        header_layout.addWidget(
            brand_label
        )

        main_layout.addLayout(
            header_layout
        )

        # -------------------------------------------------
        # Title
        # -------------------------------------------------
        title = QLabel(
            "CHOOSE YOUR ART"
        )
        title.setObjectName(
            "carouselTitle"
        )
        title.setAlignment(
            Qt.AlignCenter
        )

        title_font = title.font()
        title_font.setPointSize(29)
        title_font.setBold(True)
        title.setFont(title_font)

        main_layout.addWidget(title)

        subtitle = QLabel(
            "Drag to revolve  •  Flick to spin  •  Tap to choose"
        )
        subtitle.setObjectName(
            "carouselSubtitle"
        )
        subtitle.setAlignment(
            Qt.AlignCenter
        )

        subtitle_font = subtitle.font()
        subtitle_font.setPointSize(13)
        subtitle.setFont(subtitle_font)

        main_layout.addWidget(
            subtitle
        )

        # -------------------------------------------------
        # Carousel
        # -------------------------------------------------
        carousel_row = QHBoxLayout()
        carousel_row.addStretch()

        self.carousel = (
            RevolvingCarouselView(
                self.arts
            )
        )

        carousel_row.addWidget(
            self.carousel,
            alignment=Qt.AlignCenter,
        )

        carousel_row.addStretch()

        main_layout.addLayout(
            carousel_row
        )

        # -------------------------------------------------
        # Current centre art
        # -------------------------------------------------
        self.current_label = QLabel(
            "TULIP"
        )
        self.current_label.setObjectName(
            "currentArtLabel"
        )
        self.current_label.setAlignment(
            Qt.AlignCenter
        )

        current_font = (
            self.current_label.font()
        )
        current_font.setPointSize(12)
        current_font.setBold(True)

        self.current_label.setFont(
            current_font
        )

        main_layout.addWidget(
            self.current_label
        )

        # -------------------------------------------------
        # Footer
        # -------------------------------------------------
        footer = QLabel(
            "COFFEE. INNOVATED."
        )
        footer.setObjectName(
            "brandTagline"
        )
        footer.setAlignment(
            Qt.AlignCenter
        )

        footer_font = footer.font()
        footer_font.setPointSize(9)
        footer_font.setBold(True)
        footer.setFont(footer_font)

        main_layout.addWidget(
            footer
        )

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------
        self.carousel.selection_changed.connect(
            self.on_selection_changed
        )

        self.carousel.art_clicked.connect(
            self.select_art
        )

        # -------------------------------------------------
        # Theme
        # -------------------------------------------------
        self.setStyleSheet(
            """
            QWidget#artSelectionPage {
                background-color: #F7EFE6;
            }

            QLabel#brandLabel {
                color: #3A2616;
            }

            QLabel#carouselTitle {
                color: #2F1E12;
            }

            QLabel#carouselSubtitle {
                color: #7C6A5A;
            }

            QLabel#currentArtLabel {
                color: #7A5538;
                letter-spacing: 2px;
            }

            QLabel#brandTagline {
                color: #B89067;
                letter-spacing: 2px;
            }

            QPushButton#carouselBackButton {
                background-color: transparent;
                color: #3A2616;
                border: none;
                border-radius: 18px;
            }

            QPushButton#carouselBackButton:hover {
                background-color: #EADBCB;
            }

            QPushButton#carouselBackButton:pressed {
                background-color: #DFCBB6;
            }
            """
        )

    # =====================================================
    # Center card changed
    # =====================================================
    def on_selection_changed(self, art_name):
        self.current_label.setText(
            art_name.upper()
        )

    # =====================================================
    # Art chosen
    # =====================================================
    def select_art(self, art_name):
        print(
            f"User selected: {art_name}"
        )

        QTimer.singleShot(
            100,
            lambda: (
                self.main_window
                .start_selected_art(
                    art_name
                )
            ),
        )
