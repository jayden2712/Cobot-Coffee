"""Today's pours: which option customers chose and the best challenge scores.

The brief asks for customer preferences (cobot, teleop or barista pour)
to be tracked. Every completed pour becomes a :class:`PourRecord`,
appended to a CSV file so the numbers survive an app restart and can be
used as testing evidence.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from datetime import date, datetime
from pathlib import Path

CHOICE_COBOT = "cobot"
CHOICE_TELEOP = "teleop"
CHOICE_BARISTA = "barista"
CHOICES = (CHOICE_COBOT, CHOICE_TELEOP, CHOICE_BARISTA)

CHOICE_LABELS = {
    CHOICE_COBOT: "Cobot pour",
    CHOICE_TELEOP: "Latte Challenge",
    CHOICE_BARISTA: "Barista pour",
}

CSV_FIELDS = ("timestamp", "choice", "art", "score")


@dataclass(frozen=True)
class PourRecord:
    timestamp: datetime
    choice: str
    art: str = ""
    score: int | None = None


@dataclass(frozen=True)
class ServiceStats:
    cobot: int = 0
    teleop: int = 0
    barista: int = 0
    #: (art key, best score) pairs, e.g. (("heart", 92),)
    best_scores: tuple[tuple[str, int], ...] = ()

    @property
    def total(self) -> int:
        return self.cobot + self.teleop + self.barista

    def count(self, choice: str) -> int:
        return getattr(self, choice)


def record_pour(stats: ServiceStats, record: PourRecord) -> ServiceStats:
    """Return new stats with ``record`` counted."""
    if record.choice not in CHOICES:
        raise ValueError(f"Unknown choice: {record.choice!r}")

    updated = replace(
        stats,
        **{record.choice: stats.count(record.choice) + 1},
    )

    if record.choice == CHOICE_TELEOP and record.score is not None:
        updated = replace(
            updated,
            best_scores=_with_best(updated.best_scores, record.art, record.score),
        )

    return updated


def best_score(stats: ServiceStats, art_key: str) -> int | None:
    return dict(stats.best_scores).get(art_key)


def top_score(stats: ServiceStats) -> tuple[str, int] | None:
    """The highest challenge score today, as (art key, score)."""
    if not stats.best_scores:
        return None

    return max(stats.best_scores, key=lambda item: item[1])


def stats_from_records(records) -> ServiceStats:
    stats = ServiceStats()
    for record in records:
        stats = record_pour(stats, record)
    return stats


# =========================================================
# CSV storage
# =========================================================
def append_record(path: Path, record: PourRecord) -> bool:
    """Add one row to the log. Returns False instead of raising on I/O errors
    so a full disk or a locked file never stops service."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # An empty file (e.g. after a power cut) still needs the header.
        is_new = not path.exists() or path.stat().st_size == 0

        with path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            if is_new:
                writer.writerow(CSV_FIELDS)
            writer.writerow(
                (
                    record.timestamp.isoformat(timespec="seconds"),
                    record.choice,
                    record.art,
                    "" if record.score is None else record.score,
                )
            )
    except OSError as error:
        print(f"Could not write service log {path}: {error}")
        return False

    return True


def load_records(path: Path, day: date) -> list[PourRecord]:
    """Read the rows logged on ``day``.

    Unreadable rows are skipped, and a damaged file (bad bytes from a
    power cut) keeps the rows read before the damage instead of
    stopping the kiosk from starting.
    """
    if not path.exists():
        return []

    records = []
    try:
        # errors="replace" turns bad bytes into a row that fails to parse
        # instead of a decode error that would lose the whole file.
        with path.open(newline="", encoding="utf-8", errors="replace") as handle:
            for row in csv.DictReader(handle):
                record = _parse_row(row)
                if record is not None and record.timestamp.date() == day:
                    records.append(record)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Could not fully read service log {path}: {error}")

    return records


def _parse_row(row: dict) -> PourRecord | None:
    try:
        timestamp = datetime.fromisoformat(row["timestamp"])
        choice = row["choice"]
        score_text = (row.get("score") or "").strip()
        score = int(score_text) if score_text else None
    except (KeyError, TypeError, ValueError):
        return None

    if choice not in CHOICES:
        return None

    return PourRecord(
        timestamp=timestamp,
        choice=choice,
        art=row.get("art") or "",
        score=score,
    )


def _with_best(best_scores, art_key, score):
    best = dict(best_scores)
    if score > best.get(art_key, -1):
        best[art_key] = score
    return tuple(sorted(best.items()))
