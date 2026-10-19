"""Latte-art challenge definitions for the teleop pour game.

Coordinates are cup-relative: (0, 0) is the cup centre, x and y run from
-1 to 1 across the cup, and y grows towards the customer (screen bottom).

A challenge is a sequence of segments. Each segment moves the guide from
``start`` to ``end`` while asking for a target ``flow`` (0 = jug upright,
1 = full pour). The game shows the guide and scores how closely the
customer's jug follows it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

PHASE_BASE = "BASE"
PHASE_ART = "ART"
PHASE_FINISH = "FINISH"
PHASES = (PHASE_BASE, PHASE_ART, PHASE_FINISH)

PHASE_LABELS = {
    PHASE_BASE: "BASE",
    PHASE_ART: "PATTERN",
    PHASE_FINISH: "FINISH",
}


@dataclass(frozen=True)
class Segment:
    phase: str
    duration: float
    start: tuple[float, float]
    end: tuple[float, float]
    flow: float
    instruction: str
    wiggle_amplitude: float = 0.0
    wiggle_hz: float = 0.0


@dataclass(frozen=True)
class GuidePoint:
    x: float
    y: float
    flow: float
    phase: str
    instruction: str
    segment_index: int


@dataclass(frozen=True)
class Challenge:
    key: str
    level: int
    difficulty: str
    art_name: str
    icon: str
    blurb: str
    position_tolerance: float
    segments: tuple[Segment, ...]

    def __post_init__(self):
        if self.position_tolerance <= 0:
            raise ValueError(f"{self.key}: position_tolerance must be > 0")
        if not self.segments:
            raise ValueError(f"{self.key}: a challenge needs segments")

    @property
    def duration(self) -> float:
        return sum(segment.duration for segment in self.segments)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def guide_at(challenge: Challenge, elapsed: float) -> GuidePoint:
    """Return where the guide is, and what flow it asks for, at ``elapsed`` s."""
    elapsed = max(0.0, min(elapsed, challenge.duration))
    segment_start = 0.0

    for index, segment in enumerate(challenge.segments):
        is_last = index == len(challenge.segments) - 1
        segment_end = segment_start + segment.duration

        if elapsed < segment_end or is_last:
            local = elapsed - segment_start
            progress = local / segment.duration if segment.duration else 1.0
            progress = max(0.0, min(progress, 1.0))

            x = _lerp(segment.start[0], segment.end[0], progress)
            y = _lerp(segment.start[1], segment.end[1], progress)

            if segment.wiggle_amplitude:
                x += segment.wiggle_amplitude * math.sin(
                    2 * math.pi * segment.wiggle_hz * local
                )

            return GuidePoint(
                x=x,
                y=y,
                flow=segment.flow,
                phase=segment.phase,
                instruction=segment.instruction,
                segment_index=index,
            )

        segment_start = segment_end

    raise ValueError(f"Challenge {challenge.key!r} has no segments")


def art_path(
    challenge: Challenge,
    step: float = 0.05,
) -> list[tuple[float, float]]:
    """Sample the guide wherever milk should land on the crema.

    The base fill pours under the crema and leaves no mark, so only the
    pattern and finish phases are returned. Used to draw the faint path
    the customer is aiming for.
    """
    points = []
    steps = int(challenge.duration / step) + 1

    for i in range(steps):
        guide = guide_at(challenge, i * step)

        if guide.phase != PHASE_BASE and guide.flow > 0:
            points.append((guide.x, guide.y))

    return points


# =========================================================
# CHALLENGES
# =========================================================
_BASE_FILL = Segment(
    phase=PHASE_BASE,
    duration=3.0,
    start=(0.0, 0.0),
    end=(0.0, 0.0),
    flow=0.5,
    instruction="Pour into the centre to fill the cup",
)

HEART = Challenge(
    key="heart",
    level=1,
    difficulty="Beginner",
    art_name="Heart",
    icon="heart.png",
    blurb="Hold steady, then pull through.",
    position_tolerance=0.30,
    segments=(
        _BASE_FILL,
        Segment(
            phase=PHASE_ART,
            duration=3.0,
            start=(0.0, 0.1),
            end=(0.0, 0.0),
            flow=0.85,
            instruction="Hold steady and let the heart grow",
            wiggle_amplitude=0.05,
            wiggle_hz=1.5,
        ),
        Segment(
            phase=PHASE_FINISH,
            duration=0.6,
            start=(0.0, 0.0),
            end=(0.0, -0.4),
            flow=0.0,
            instruction="Tilt back and move to the far edge",
        ),
        Segment(
            phase=PHASE_FINISH,
            duration=1.5,
            start=(0.0, -0.4),
            end=(0.0, 0.55),
            flow=0.25,
            instruction="Lift and pull through",
        ),
    ),
)

TULIP = Challenge(
    key="tulip",
    level=2,
    difficulty="Intermediate",
    art_name="Tulip",
    icon="tulip.png",
    blurb="Push three layers, then pull through.",
    position_tolerance=0.24,
    segments=(
        _BASE_FILL,
        Segment(
            phase=PHASE_ART,
            duration=1.2,
            start=(0.0, 0.3),
            end=(0.0, 0.25),
            flow=0.85,
            instruction="Push the first layer",
        ),
        Segment(
            phase=PHASE_ART,
            duration=0.5,
            start=(0.0, 0.25),
            end=(0.0, 0.0),
            flow=0.0,
            instruction="Pause and tilt back",
        ),
        Segment(
            phase=PHASE_ART,
            duration=1.2,
            start=(0.0, 0.0),
            end=(0.0, -0.05),
            flow=0.85,
            instruction="Push the second layer",
        ),
        Segment(
            phase=PHASE_ART,
            duration=0.5,
            start=(0.0, -0.05),
            end=(0.0, -0.3),
            flow=0.0,
            instruction="Pause and tilt back",
        ),
        Segment(
            phase=PHASE_ART,
            duration=1.0,
            start=(0.0, -0.3),
            end=(0.0, -0.33),
            flow=0.8,
            instruction="Push the last layer",
        ),
        Segment(
            phase=PHASE_FINISH,
            duration=1.6,
            start=(0.0, -0.4),
            end=(0.0, 0.6),
            flow=0.25,
            instruction="Lift and pull through",
        ),
    ),
)

ROSETTA = Challenge(
    key="rosetta",
    level=3,
    difficulty="Expert",
    art_name="Rosetta",
    icon="rosetta.png",
    blurb="Wiggle as you move back, then pull through.",
    position_tolerance=0.18,
    segments=(
        Segment(
            phase=PHASE_BASE,
            duration=2.5,
            start=(0.0, 0.0),
            end=(0.0, 0.0),
            flow=0.5,
            instruction="Pour into the centre to fill the cup",
        ),
        Segment(
            phase=PHASE_ART,
            duration=5.0,
            start=(0.0, 0.45),
            end=(0.0, -0.4),
            flow=0.8,
            instruction="Wiggle side to side as you move back",
            wiggle_amplitude=0.3,
            wiggle_hz=2.2,
        ),
        Segment(
            phase=PHASE_FINISH,
            duration=1.6,
            start=(0.0, -0.5),
            end=(0.0, 0.6),
            flow=0.25,
            instruction="Lift and pull through",
        ),
    ),
)

CHALLENGES = (HEART, TULIP, ROSETTA)


def next_challenge(challenge: Challenge) -> Challenge | None:
    """The next harder challenge, or None at the top level."""
    for candidate in CHALLENGES:
        if candidate.level == challenge.level + 1:
            return candidate

    return None
