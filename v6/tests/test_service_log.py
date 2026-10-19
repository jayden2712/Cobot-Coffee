"""Tests for pour tracking and the CSV service log.

Run from the v6 folder:  python -m unittest discover -s tests -t .
"""

import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from service_log import (
    CHOICE_BARISTA,
    CHOICE_COBOT,
    CHOICE_TELEOP,
    PourRecord,
    ServiceStats,
    append_record,
    best_score,
    load_records,
    record_pour,
    stats_from_records,
    top_score,
)

MORNING = datetime(2026, 10, 27, 15, 40)


class ServiceStatsTests(unittest.TestCase):
    def test_counts_each_choice(self):
        stats = stats_from_records(
            [
                PourRecord(MORNING, CHOICE_COBOT, "Tulip"),
                PourRecord(MORNING, CHOICE_COBOT, "Heart"),
                PourRecord(MORNING, CHOICE_BARISTA),
                PourRecord(MORNING, CHOICE_TELEOP, "heart", 70),
            ]
        )
        self.assertEqual((stats.cobot, stats.teleop, stats.barista), (2, 1, 1))
        self.assertEqual(stats.total, 4)

    def test_record_returns_new_stats(self):
        stats = ServiceStats()
        updated = record_pour(stats, PourRecord(MORNING, CHOICE_BARISTA))
        self.assertEqual(stats.total, 0)
        self.assertEqual(updated.barista, 1)

    def test_keeps_best_score_per_art(self):
        stats = stats_from_records(
            [
                PourRecord(MORNING, CHOICE_TELEOP, "heart", 70),
                PourRecord(MORNING, CHOICE_TELEOP, "heart", 85),
                PourRecord(MORNING, CHOICE_TELEOP, "heart", 60),
                PourRecord(MORNING, CHOICE_TELEOP, "tulip", 90),
            ]
        )
        self.assertEqual(best_score(stats, "heart"), 85)
        self.assertEqual(best_score(stats, "rosetta"), None)
        self.assertEqual(top_score(stats), ("tulip", 90))

    def test_top_score_is_none_before_any_challenge(self):
        stats = record_pour(ServiceStats(), PourRecord(MORNING, CHOICE_COBOT))
        self.assertIsNone(top_score(stats))

    def test_unknown_choice_is_rejected(self):
        with self.assertRaises(ValueError):
            record_pour(ServiceStats(), PourRecord(MORNING, "robot"))


class ServiceLogFileTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "logs" / "service_log.csv"

    def tearDown(self):
        self.folder.cleanup()

    def test_round_trip_creates_folder_and_header(self):
        record = PourRecord(MORNING, CHOICE_TELEOP, "heart", 92)
        self.assertTrue(append_record(self.path, record))
        self.assertTrue(append_record(self.path, PourRecord(MORNING, CHOICE_BARISTA)))

        lines = self.path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "timestamp,choice,art,score")
        self.assertEqual(len(lines), 3)

        loaded = load_records(self.path, MORNING.date())
        self.assertEqual(loaded[0], record)
        self.assertIsNone(loaded[1].score)

    def test_only_loads_the_requested_day(self):
        append_record(self.path, PourRecord(datetime(2026, 10, 26, 11, 0), CHOICE_COBOT))
        append_record(self.path, PourRecord(MORNING, CHOICE_COBOT))
        self.assertEqual(len(load_records(self.path, date(2026, 10, 27))), 1)

    def test_missing_file_loads_nothing(self):
        self.assertEqual(load_records(self.path, MORNING.date()), [])

    def test_bad_rows_are_skipped(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(
            "timestamp,choice,art,score\n"
            "not-a-date,cobot,,\n"
            "2026-10-27T15:00:00,robot,,\n"
            "2026-10-27T15:01:00,teleop,heart,abc\n"
            "2026-10-27T15:02:00,cobot,Tulip,\n",
            encoding="utf-8",
        )
        loaded = load_records(self.path, MORNING.date())
        self.assertEqual([r.art for r in loaded], ["Tulip"])

    def test_empty_file_gets_a_header(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("", encoding="utf-8")
        append_record(self.path, PourRecord(MORNING, CHOICE_COBOT, "Heart"))
        self.assertEqual(len(load_records(self.path, MORNING.date())), 1)

    def test_corrupt_bytes_keep_earlier_rows(self):
        append_record(self.path, PourRecord(MORNING, CHOICE_COBOT, "Heart"))
        with self.path.open("ab") as handle:
            handle.write(b"\xff\xfe\x00garbage\n")
        loaded = load_records(self.path, MORNING.date())
        self.assertEqual([r.art for r in loaded], ["Heart"])

    def test_write_failure_returns_false(self):
        # A directory where the file should be makes the open fail.
        self.path.mkdir(parents=True)
        self.assertFalse(append_record(self.path, PourRecord(MORNING, CHOICE_COBOT)))


if __name__ == "__main__":
    unittest.main()
