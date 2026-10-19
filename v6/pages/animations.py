"""Small, cheap animations that make the kiosk feel alive.

Everything here is drawn with QPainter or Qt property animations and only
ticks while its page is visible, so it stays light on the Raspberry Pi.
Set ``ANIMATIONS_ENABLED = False`` to turn all motion off.
"""

import math

from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
    QVariantAnimation,
)
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QLabel,
    QStackedWidget,
    QWidget,
)

ANIMATIONS_ENABLED = True

FRAME_MS = 33
PAGE_FADE_MS = 220

ESPRESSO = QColor("#2F1E12")
CUP = QColor("#FFFDFC")
CUP_EDGE = QColor("#D2BDA7")
COFFEE = QColor("#7A4A26")
CREMA = QColor("#B9824F")
MILK = QColor("#FFF6EA")
JUG = QColor("#9AA3A8")
JUG_DARK = QColor("#6F777C")
STEAM = QColor(122, 85, 56, 70)
GOOD = QColor("#4F6848")
GOOD_SOFT = QColor("#E5EBDD")


# =========================================================
# PAGE TRANSITIONS
# =========================================================
class FadingStackedWidget(QStackedWidget):
    """A QStackedWidget that cross-fades between pages.

    Pages listed in ``instant_pages`` (the E-stop page) always appear at
    once: safety screens must never wait on an animation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.instant_pages = set()
        self._overlay = None
        self._fade = None

    def setCurrentWidget(self, widget):
        current = self.currentWidget()

        if (
            not ANIMATIONS_ENABLED
            or widget is current
            or current is None
            or widget in self.instant_pages
            or not self.isVisible()
        ):
            self._clear_overlay()
            super().setCurrentWidget(widget)
            return

        snapshot = current.grab()
        self._clear_overlay()
        super().setCurrentWidget(widget)

        overlay = QLabel(self)
        overlay.setPixmap(snapshot)
        overlay.setGeometry(self.rect())
        overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        overlay.show()
        overlay.raise_()

        effect = QGraphicsOpacityEffect(overlay)
        overlay.setGraphicsEffect(effect)

        fade = QPropertyAnimation(effect, b"opacity", self)
        fade.setDuration(PAGE_FADE_MS)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)
        fade.finished.connect(self._clear_overlay)

        self._overlay = overlay
        self._fade = fade
        fade.start()

    def _clear_overlay(self):
        if self._fade is not None:
            self._fade.stop()
            self._fade.deleteLater()
            self._fade = None

        if self._overlay is not None:
            self._overlay.deleteLater()
            self._overlay = None


# =========================================================
# BUTTON GLOW
# =========================================================
class GlowPulse:
    """A soft shadow that breathes behind a button to invite a tap.

    The blur is redrawn in software, so it steps at a modest frame rate
    rather than every vsync to keep the Pi's CPU free for touch input.
    """

    STEP_MS = 80

    def __init__(self, widget, colour="#7A5538", low=8, high=24, period_ms=2400):
        self.low = low
        self.high = high
        self.period = period_ms / 1000.0
        self.elapsed = 0.0

        self.effect = QGraphicsDropShadowEffect(widget)
        self.effect.setColor(QColor(colour))
        self.effect.setOffset(0, 4)
        self.effect.setBlurRadius(low)
        widget.setGraphicsEffect(self.effect)

        self.timer = QTimer(widget)
        self.timer.setInterval(self.STEP_MS)
        self.timer.timeout.connect(self._step)

    def _step(self):
        self.elapsed += self.STEP_MS / 1000.0
        wave = 0.5 - 0.5 * math.cos(2 * math.pi * self.elapsed / self.period)
        self.effect.setBlurRadius(self.low + (self.high - self.low) * wave)

    def start(self):
        if ANIMATIONS_ENABLED:
            self.timer.start()

    def stop(self):
        self.timer.stop()


# =========================================================
# FRAME-DRIVEN WIDGET BASE
# =========================================================
class AnimatedWidget(QWidget):
    """Repaints every frame while shown, and stops ticking when hidden."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(FRAME_MS)
        self._timer.timeout.connect(self._advance)

    def showEvent(self, event):
        super().showEvent(event)
        if ANIMATIONS_ENABLED:
            self._timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._timer.stop()

    def _advance(self):
        self.phase += FRAME_MS / 1000.0
        self.update()


def _steam(painter, x, top, height, phase, offset):
    """One rising wisp of steam."""
    path = QPainterPath(QPointF(x, top + height))
    for step in range(1, 13):
        t = step / 12
        y = top + height * (1 - t)
        sway = 7 * math.sin(phase * 2.2 + offset + t * 5) * t
        path.lineTo(x + sway, y)

    rise = (phase * 0.45 + offset) % 1.0
    colour = QColor(STEAM)
    colour.setAlpha(int(STEAM.alpha() * math.sin(math.pi * rise)))

    painter.setPen(QPen(colour, 5, Qt.SolidLine, Qt.RoundCap))
    painter.setBrush(Qt.NoBrush)
    painter.drawPath(path)


def _cup(painter, rect: QRectF, fill: float):
    """A side-view cup filled to ``fill`` (0-1) with coffee and crema."""
    body = QPainterPath()
    body.moveTo(rect.left(), rect.top())
    body.lineTo(rect.right(), rect.top())
    body.lineTo(rect.right() - rect.width() * 0.12, rect.bottom())
    body.lineTo(rect.left() + rect.width() * 0.12, rect.bottom())
    body.closeSubpath()

    handle = QRectF(
        rect.right() - rect.width() * 0.08,
        rect.top() + rect.height() * 0.18,
        rect.width() * 0.3,
        rect.height() * 0.42,
    )
    painter.setPen(QPen(CUP_EDGE, 6))
    painter.setBrush(Qt.NoBrush)
    painter.drawArc(handle, -90 * 16, 180 * 16)

    painter.setPen(QPen(CUP_EDGE, 2))
    painter.setBrush(CUP)
    painter.drawPath(body)

    if fill <= 0:
        return

    level = rect.bottom() - (rect.height() - 6) * min(fill, 1.0)
    liquid = QRectF(rect.left(), level, rect.width(), rect.bottom() - level)

    gradient = QLinearGradient(0, level, 0, rect.bottom())
    gradient.setColorAt(0.0, CREMA)
    gradient.setColorAt(0.25, COFFEE)
    gradient.setColorAt(1.0, COFFEE.darker(130))

    painter.save()
    painter.setClipPath(body)
    painter.setPen(Qt.NoPen)
    painter.setBrush(gradient)
    painter.drawRect(liquid)
    painter.restore()


# =========================================================
# STEAMING CUP (home, attract screen)
# =========================================================
class SteamingCup(AnimatedWidget):
    def __init__(self, size=120, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w, h = self.width(), self.height()
        cup = QRectF(w * 0.18, h * 0.5, w * 0.5, h * 0.42)

        for index, x in enumerate((0.33, 0.43, 0.53)):
            _steam(painter, w * x, h * 0.06, h * 0.38, self.phase, index * 0.33)

        _cup(painter, cup, 0.85)


# =========================================================
# POURING JUG (running page)
# =========================================================
class PouringAnimation(AnimatedWidget):
    """A milk jug pouring into a cup.

    ``progress`` (0-1) sets the fill. With ``indeterminate`` on, the pour
    loops gently because the real pour length is unknown.
    """

    def __init__(self, width=260, height=180, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.progress = 0.0
        self.indeterminate = False
        self.pouring = True

    def set_progress(self, value: float):
        self.progress = max(0.0, min(value, 1.0))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        w, h = self.width(), self.height()
        cup = QRectF(w * 0.42, h * 0.52, w * 0.4, h * 0.44)

        if self.indeterminate:
            fill = 0.35 + 0.45 * (0.5 - 0.5 * math.cos(self.phase * 0.9))
        else:
            fill = 0.2 + 0.75 * self.progress

        _cup(painter, cup, fill)

        if self.pouring:
            self._paint_stream(painter, w, h, cup, fill)

        self._paint_jug(painter, w, h)

    def _paint_stream(self, painter, w, h, cup, fill):
        spout = QPointF(w * 0.47, h * 0.3)
        level = cup.bottom() - (cup.height() - 6) * min(fill, 1.0)
        wobble = 2.5 * math.sin(self.phase * 9)

        stream = QPainterPath(spout)
        stream.cubicTo(
            QPointF(spout.x() + 10, spout.y() + 10),
            QPointF(cup.center().x() - 6 + wobble, level - 30),
            QPointF(cup.center().x() - 4 + wobble, level),
        )
        painter.setPen(QPen(MILK, 7, Qt.SolidLine, Qt.RoundCap))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(stream)

        # Where the stream lands, the milk blooms white on the crema.
        painter.setPen(Qt.NoPen)
        painter.setBrush(MILK)
        bloom = 10 + 3 * math.sin(self.phase * 6)
        painter.drawEllipse(QPointF(cup.center().x() - 4 + wobble, level + 3), bloom, 4)

    def _paint_jug(self, painter, w, h):
        painter.save()
        painter.translate(w * 0.3, h * 0.24)
        tilt = 38 + 4 * math.sin(self.phase * 1.6)
        painter.rotate(tilt)

        body = QPainterPath()
        body.moveTo(-34, -30)
        body.lineTo(26, -30)
        body.lineTo(34, 34)
        body.lineTo(-40, 34)
        body.closeSubpath()

        gradient = QLinearGradient(-40, 0, 34, 0)
        gradient.setColorAt(0.0, JUG_DARK)
        gradient.setColorAt(0.45, JUG.lighter(125))
        gradient.setColorAt(1.0, JUG_DARK)

        painter.setPen(QPen(JUG_DARK, 2))
        painter.setBrush(gradient)
        painter.drawPath(body)

        painter.setPen(QPen(JUG_DARK, 6, Qt.SolidLine, Qt.RoundCap))
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(QRectF(-58, -18, 30, 40), 90 * 16, 180 * 16)
        painter.restore()


# =========================================================
# SUCCESS CHECK (complete pages)
# =========================================================
class SuccessCheck(QWidget):
    """A green badge whose tick draws itself in."""

    def __init__(self, size=76, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._progress = 1.0

        self.animation = QVariantAnimation(self)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(650)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self._set_progress)

    def play(self):
        if not ANIMATIONS_ENABLED:
            self._set_progress(1.0)
            return
        self.animation.stop()
        self.animation.start()

    def _set_progress(self, value):
        self._progress = float(value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        size = self.width()
        grow = min(1.0, self._progress * 1.6)
        radius = size / 2 - 2

        painter.setPen(QPen(GOOD.lighter(150), 2))
        painter.setBrush(GOOD_SOFT)
        painter.drawEllipse(QPointF(size / 2, size / 2), radius * grow, radius * grow)

        tick = QPainterPath(QPointF(size * 0.28, size * 0.52))
        tick.lineTo(size * 0.44, size * 0.67)
        tick.lineTo(size * 0.73, size * 0.36)

        draw = max(0.0, (self._progress - 0.35) / 0.65)
        if draw <= 0:
            return

        painter.setPen(QPen(GOOD, size * 0.09, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)

        partial = QPainterPath()
        length = tick.length()
        steps = 24
        partial.moveTo(tick.pointAtPercent(0))
        for i in range(1, steps + 1):
            percent = tick.percentAtLength(length * draw * i / steps)
            partial.lineTo(tick.pointAtPercent(percent))
        painter.drawPath(partial)


# =========================================================
# COUNT-UP NUMBER (teleop score)
# =========================================================
class CountUp:
    """Counts a label up to its value instead of showing it at once."""

    def __init__(self, label: QLabel, duration_ms=900):
        self.label = label
        self.animation = QVariantAnimation(label)
        self.animation.setDuration(duration_ms)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(
            lambda value: self.label.setText(str(int(round(value))))
        )

    def run_to(self, value: int):
        self.animation.stop()
        if not ANIMATIONS_ENABLED:
            self.label.setText(str(value))
            return
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(float(value))
        self.animation.start()


# =========================================================
# BREATHING TEXT (attract screen)
# =========================================================
class BreathingOpacity:
    """Slowly fades a widget between dim and full to draw the eye."""

    def __init__(self, widget, low=0.45, period_ms=1800):
        self.effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity", widget)
        self.animation.setDuration(period_ms)
        self.animation.setStartValue(1.0)
        self.animation.setKeyValueAt(0.5, low)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        self.animation.setLoopCount(-1)

    def start(self):
        if ANIMATIONS_ENABLED:
            self.animation.start()

    def stop(self):
        self.animation.stop()
        self.effect.setOpacity(1.0)
