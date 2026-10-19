"""Scoring for the teleop pour game.

Three things make a good pour, weighted into a 0-100 score:

- Steering (50%): the pour point stays near the guide while milk flows.
- Flow (30%): the jug tilt matches the flow the guide asks for, including
  tilting back during pauses.
- Fill (20%): the cup ends up as full as a perfect pour would leave it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from functools import lru_cache

from teleop.challenges import Challenge, GuidePoint, guide_at
from teleop.jug import JugState

STEERING_WEIGHT = 0.5
FLOW_WEIGHT = 0.3
FILL_WEIGHT = 0.2

#: A tilt this far from the target flow scores zero for that moment.
FLOW_TOLERANCE = 0.5
#: Being this far over or under the ideal fill scores zero for fill.
FILL_TOLERANCE = 0.6
#: Milk ratio above which the cup visibly overflows.
OVERFLOW_RATIO = 1.15

STAR_THRESHOLDS = (85, 65, 40)
RANKS = {
    3: "LATTE ARTIST",
    2: "BARISTA",
    1: "APPRENTICE",
    0: "KEEP PRACTISING",
}


@dataclass(frozen=True)
class PourStats:
    steering_total: float = 0.0
    steering_samples: int = 0
    flow_total: float = 0.0
    flow_samples: int = 0
    milk_poured: float = 0.0

    @property
    def steering(self) -> float:
        return _average(self.steering_total, self.steering_samples)

    @property
    def flow(self) -> float:
        return _average(self.flow_total, self.flow_samples)


@dataclass(frozen=True)
class PourResult:
    score: int
    stars: int
    rank: str
    steering: float
    flow: float
    fill: float
    fill_ratio: float


def steering_score(guide: GuidePoint, jug: JugState, tolerance: float) -> float:
    distance = math.hypot(jug.x - guide.x, jug.y - guide.y)
    return _clamp01(1.0 - distance / tolerance)


def flow_score(guide: GuidePoint, jug: JugState) -> float:
    return _clamp01(1.0 - abs(jug.tilt - guide.flow) / FLOW_TOLERANCE)


def is_on_target(guide: GuidePoint, jug: JugState, tolerance: float) -> bool:
    return math.hypot(jug.x - guide.x, jug.y - guide.y) <= tolerance


def add_sample(
    stats: PourStats,
    guide: GuidePoint,
    jug: JugState,
    dt: float,
    tolerance: float,
) -> PourStats:
    """Return new stats with one game tick of ``dt`` seconds added."""
    updated = replace(
        stats,
        flow_total=stats.flow_total + flow_score(guide, jug),
        flow_samples=stats.flow_samples + 1,
        milk_poured=stats.milk_poured + jug.tilt * dt,
    )

    # Where the jug points only matters while milk is meant to flow, and
    # hovering over the guide without pouring earns nothing.
    if guide.flow > 0:
        aim = steering_score(guide, jug, tolerance) if jug.tilt > 0 else 0.0
        updated = replace(
            updated,
            steering_total=updated.steering_total + aim,
            steering_samples=updated.steering_samples + 1,
        )

    return updated


@lru_cache(maxsize=None)
def expected_milk(challenge: Challenge, step: float = 1 / 60) -> float:
    """Milk a perfect pour delivers: the integral of guide flow over time.

    Cached because the game asks for it every tick.
    """
    steps = int(round(challenge.duration / step))
    return sum(guide_at(challenge, i * step).flow * step for i in range(steps))


def fill_ratio(stats: PourStats, challenge: Challenge) -> float:
    expected = expected_milk(challenge)
    return stats.milk_poured / expected if expected else 0.0


def stars_for(score: int) -> int:
    for stars, threshold in zip((3, 2, 1), STAR_THRESHOLDS):
        if score >= threshold:
            return stars

    return 0


def score_pour(stats: PourStats, challenge: Challenge) -> PourResult:
    ratio = fill_ratio(stats, challenge)
    fill = _clamp01(1.0 - abs(ratio - 1.0) / FILL_TOLERANCE)

    total = (
        STEERING_WEIGHT * stats.steering
        + FLOW_WEIGHT * stats.flow
        + FILL_WEIGHT * fill
    )
    score = int(round(100 * total))
    stars = stars_for(score)

    return PourResult(
        score=score,
        stars=stars,
        rank=RANKS[stars],
        steering=stats.steering,
        flow=stats.flow,
        fill=fill,
        fill_ratio=ratio,
    )


def _average(total: float, count: int) -> float:
    return total / count if count else 0.0


def _clamp01(value: float) -> float:
    return max(0.0, min(value, 1.0))
