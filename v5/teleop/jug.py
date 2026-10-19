"""Jug controller input for the teleop pour game.

The physical jug controller (Vive Tracker for position, AS5600 encoder for
tilt) and the cobot motion it drives are outside this GUI's scope. Any
controller only has to provide ``read()`` returning a :class:`JugState`.

Until the hardware is wired in, :class:`SimulatedJugController` lets a
customer steer the jug with a finger or mouse on the cup.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol

from teleop.challenges import GuidePoint


@dataclass(frozen=True)
class JugState:
    """Where the milk would land and how far the jug is tilted.

    ``x`` and ``y`` use the cup coordinates from ``teleop.challenges``;
    ``tilt`` is 0 (upright, no flow) to 1 (full pour).
    """

    x: float = 0.0
    y: float = 0.0
    tilt: float = 0.0


class JugController(Protocol):
    #: True when the controller only reports pour on/off and the game
    #: should supply the target flow itself (see :func:`apply_flow_assist`).
    is_assisted: bool

    def read(self) -> JugState: ...

    def reset(self) -> None: ...


class SimulatedJugController:
    """Touch or mouse stand-in for the physical jug.

    Dragging moves the pour point. Touching the cup counts as tilting the
    jug; lifting the finger stops the pour. Flow is assisted because a
    single finger cannot also set the tilt angle.
    """

    is_assisted = True

    def __init__(self) -> None:
        self._state = JugState()

    def set_pointer(self, x: float, y: float, pressed: bool) -> None:
        self._state = JugState(
            x=_clamp(x, -1.0, 1.0),
            y=_clamp(y, -1.0, 1.0),
            tilt=1.0 if pressed else 0.0,
        )

    def read(self) -> JugState:
        return self._state

    def reset(self) -> None:
        self._state = JugState()


def apply_flow_assist(
    jug: JugState,
    guide: GuidePoint,
    is_assisted: bool,
) -> JugState:
    """With assist on, a tilted jug pours exactly the flow the guide asks for."""
    if not is_assisted:
        return jug

    flow = guide.flow if jug.tilt > 0 else 0.0
    return replace(jug, tilt=flow)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))
