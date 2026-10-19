"""Top-down cup the customer pours into during the teleop challenge.

The widget draws the cup, the milk the customer has poured so far, the
faint path of the target pattern and the moving guide. Touch or mouse
input on the cup is reported through ``pointer_changed`` in cup
coordinates (see ``teleop.challenges``).
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from teleop.challenges import GuidePoint
from teleop.jug import JugState
from typography import DISPLAY, make_font

SAUCER = QColor("#EADBCB")
CUP_RIM = QColor("#FFFDFC")
CUP_EDGE = QColor("#D2BDA7")
CREMA_CENTRE = QColor("#B9824F")
CREMA_EDGE = QColor("#6E4123")
MILK = QColor(255, 248, 236, 235)
PATH_COLOUR = QColor(255, 244, 228, 120)
ON_TARGET = QColor("#6E8B5E")
OFF_TARGET = QColor("#E0A458")
OVERLAY_FILL = QColor(47, 30, 18, 190)

#: Milk blob radius, as a fraction of the crema radius.
MIN_BLOB = 0.025
FLOW_BLOB = 0.045
POOL_BLOB = 0.30
#: Seconds of holding still before a pour reaches its widest pool.
POOL_SECONDS = 2.5
#: Faster than this (cup widths per second) and milk draws a line, not a pool.
STILL_SPEED = 0.6


class PourCanvas(QWidget):
    pointer_changed = Signal(float, float, bool)

    def __init__(self, size=440, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_AcceptTouchEvents, False)

        self._crema_radius = size * 0.40
        self._milk = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
        self._path_points = []
        self._tolerance = 0.25
        self._guide = None
        self._jug = None
        self._on_target = False
        self._overlay_text = ""
        self._last_pour = None
        self._dwell = 0.0
        self._speed = 0.0

        self.reset()

    # -----------------------------------------------------
    # State from the game
    # -----------------------------------------------------
    def reset(self, path_points=(), tolerance=0.25):
        self._milk.fill(Qt.transparent)
        self._path_points = list(path_points)
        self._tolerance = tolerance
        self._guide = None
        self._jug = None
        self._on_target = False
        self._last_pour = None
        self._dwell = 0.0
        self._speed = 0.0
        self.update()

    def set_frame(self, guide: GuidePoint, jug: JugState, on_target: bool):
        self._guide = guide
        self._jug = jug
        self._on_target = on_target
        self.update()

    def set_overlay(self, text: str):
        self._overlay_text = text
        self.update()

    def deposit(self, jug: JugState, dt: float):
        """Lay milk on the crema where the jug is pouring.

        Holding still lets the milk pool into a wide blob; moving quickly
        draws a thin line. That is what turns a pause into a tulip layer
        and a fast pass into the pull-through.
        """
        if jug.tilt <= 0.02:
            self._last_pour = None
            self._dwell = 0.0
            self._speed = 0.0
            return

        if self._last_pour is not None and dt > 0:
            moved = math.hypot(
                jug.x - self._last_pour[0],
                jug.y - self._last_pour[1],
            )
            # Smooth the speed so finger jitter does not break a pool.
            self._speed = 0.8 * self._speed + 0.2 * (moved / dt)

        self._dwell = self._dwell + dt if self._speed < STILL_SPEED else 0.0
        pooling = min(self._dwell / POOL_SECONDS, 1.0)
        radius = self._crema_radius * (
            MIN_BLOB + jug.tilt * (FLOW_BLOB + POOL_BLOB * pooling)
        )

        start = self._to_px(*self._last_pour) if self._last_pour else None
        end = self._to_px(jug.x, jug.y)

        painter = QPainter(self._milk)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setClipPath(self._crema_clip())
        painter.setPen(Qt.NoPen)
        painter.setBrush(MILK)
        painter.drawEllipse(end, radius, radius)

        # Join consecutive pours so a fast stroke stays one line.
        if start is not None:
            painter.setPen(QPen(MILK, radius * 2, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(start, end)

        painter.end()

        self._last_pour = (jug.x, jug.y)

    def art_image(self) -> QImage:
        """The finished cup, without guides, for the result screen."""
        image = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)

        painter = QPainter(image)
        self._paint_cup(painter)
        painter.end()

        return image

    # -----------------------------------------------------
    # Input
    # -----------------------------------------------------
    def mousePressEvent(self, event):
        self._emit_pointer(event.position(), pressed=True)

    def mouseMoveEvent(self, event):
        pressed = bool(event.buttons() & Qt.LeftButton)
        self._emit_pointer(event.position(), pressed=pressed)

    def mouseReleaseEvent(self, event):
        self._emit_pointer(event.position(), pressed=False)

    def _emit_pointer(self, position: QPointF, pressed: bool):
        x, y = self._to_cup(position)
        self.pointer_changed.emit(x, y, pressed)

    # -----------------------------------------------------
    # Geometry
    # -----------------------------------------------------
    def _centre(self) -> QPointF:
        return QPointF(self.width() / 2, self.height() / 2)

    def _to_px(self, x: float, y: float) -> QPointF:
        centre = self._centre()
        return QPointF(
            centre.x() + x * self._crema_radius,
            centre.y() + y * self._crema_radius,
        )

    def _to_cup(self, position: QPointF) -> tuple[float, float]:
        centre = self._centre()
        return (
            (position.x() - centre.x()) / self._crema_radius,
            (position.y() - centre.y()) / self._crema_radius,
        )

    def _crema_clip(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self._centre(), self._crema_radius, self._crema_radius)
        return path

    # -----------------------------------------------------
    # Painting
    # -----------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        self._paint_cup(painter)
        self._paint_path(painter)
        self._paint_guide(painter)
        self._paint_jug(painter)
        self._paint_overlay(painter)

    def _paint_cup(self, painter: QPainter):
        painter.setRenderHint(QPainter.Antialiasing, True)
        centre = self._centre()
        size = self.width()

        painter.setPen(Qt.NoPen)
        painter.setBrush(SAUCER)
        painter.drawEllipse(centre, size * 0.49, size * 0.49)

        painter.setPen(QPen(CUP_EDGE, 2))
        painter.setBrush(CUP_RIM)
        painter.drawEllipse(centre, size * 0.445, size * 0.445)

        crema = QRadialGradient(centre, self._crema_radius)
        crema.setColorAt(0.0, CREMA_CENTRE)
        crema.setColorAt(1.0, CREMA_EDGE)
        painter.setPen(Qt.NoPen)
        painter.setBrush(crema)
        painter.drawEllipse(centre, self._crema_radius, self._crema_radius)

        painter.drawImage(0, 0, self._milk)

    def _paint_path(self, painter: QPainter):
        if len(self._path_points) < 2:
            return

        pen = QPen(PATH_COLOUR, 3, Qt.DashLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        path = QPainterPath(self._to_px(*self._path_points[0]))
        for point in self._path_points[1:]:
            path.lineTo(self._to_px(*point))

        painter.drawPath(path)

    def _paint_guide(self, painter: QPainter):
        if self._guide is None:
            return

        centre = self._to_px(self._guide.x, self._guide.y)
        radius = self._tolerance * self._crema_radius

        colour = QColor(CUP_RIM)
        colour.setAlpha(230 if self._guide.flow > 0 else 120)
        pen = QPen(colour, 4, Qt.DashLine if self._guide.flow == 0 else Qt.SolidLine)

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(centre, radius, radius)

    def _paint_jug(self, painter: QPainter):
        if self._jug is None:
            return

        centre = self._to_px(self._jug.x, self._jug.y)
        fill = ON_TARGET if self._on_target else OFF_TARGET

        painter.setPen(QPen(CUP_RIM, 3))
        painter.setBrush(fill)
        painter.drawEllipse(centre, 14, 14)

    def _paint_overlay(self, painter: QPainter):
        if not self._overlay_text:
            return

        centre = self._centre()
        radius = self.width() * 0.22

        painter.setPen(Qt.NoPen)
        painter.setBrush(OVERLAY_FILL)
        painter.drawEllipse(centre, radius, radius)

        painter.setPen(CUP_RIM)
        painter.setFont(make_font(DISPLAY + 8, bold=True))
        painter.drawText(
            QRectF(
                centre.x() - radius,
                centre.y() - radius,
                radius * 2,
                radius * 2,
            ),
            Qt.AlignCenter,
            self._overlay_text,
        )
