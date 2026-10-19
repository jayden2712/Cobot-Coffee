"""Tests for the teleop challenge, jug input and scoring logic.

Run from the v5 folder:  python -m unittest discover -s tests
"""

import unittest

from teleop.challenges import (
    CHALLENGES,
    HEART,
    PHASE_ART,
    PHASE_BASE,
    PHASE_FINISH,
    ROSETTA,
    TULIP,
    art_path,
    guide_at,
    next_challenge,
)
from teleop.jug import JugState, SimulatedJugController, apply_flow_assist
from teleop.scoring import (
    PourStats,
    add_sample,
    expected_milk,
    flow_score,
    is_on_target,
    score_pour,
    stars_for,
    steering_score,
)

TICK = 1 / 30


def play(challenge, jug_for_guide):
    """Run a whole pour, asking ``jug_for_guide`` where the jug is each tick."""
    stats = PourStats()
    steps = int(round(challenge.duration / TICK))

    for i in range(steps):
        guide = guide_at(challenge, i * TICK)
        jug = jug_for_guide(guide)
        stats = add_sample(stats, guide, jug, TICK, challenge.position_tolerance)

    return score_pour(stats, challenge)


class ChallengeTests(unittest.TestCase):
    def test_levels_run_one_to_three_in_order(self):
        self.assertEqual([c.level for c in CHALLENGES], [1, 2, 3])

    def test_harder_levels_have_tighter_tolerance(self):
        tolerances = [c.position_tolerance for c in CHALLENGES]
        self.assertEqual(tolerances, sorted(tolerances, reverse=True))

    def test_every_challenge_goes_base_then_art_then_finish(self):
        for challenge in CHALLENGES:
            phases = []
            for segment in challenge.segments:
                if not phases or phases[-1] != segment.phase:
                    phases.append(segment.phase)
            self.assertEqual(
                phases, [PHASE_BASE, PHASE_ART, PHASE_FINISH], challenge.key
            )

    def test_guide_starts_at_first_segment(self):
        guide = guide_at(HEART, 0.0)
        self.assertEqual(guide.phase, PHASE_BASE)
        self.assertEqual((guide.x, guide.y), HEART.segments[0].start)

    def test_guide_is_clamped_after_the_end(self):
        guide = guide_at(TULIP, TULIP.duration + 5)
        last = TULIP.segments[-1]
        self.assertAlmostEqual(guide.x, last.end[0])
        self.assertAlmostEqual(guide.y, last.end[1])
        self.assertEqual(guide.segment_index, len(TULIP.segments) - 1)

    def test_guide_interpolates_within_a_segment(self):
        finish = TULIP.segments[-1]
        start_time = TULIP.duration - finish.duration
        guide = guide_at(TULIP, start_time + finish.duration / 2)
        self.assertAlmostEqual(guide.y, (finish.start[1] + finish.end[1]) / 2)

    def test_rosetta_wiggle_moves_sideways(self):
        art_start = ROSETTA.segments[0].duration
        xs = [guide_at(ROSETTA, art_start + i * 0.05).x for i in range(40)]
        self.assertGreater(max(xs), 0.2)
        self.assertLess(min(xs), -0.2)

    def test_art_path_skips_the_base_fill(self):
        base_point = ROSETTA.segments[0].start
        path = art_path(ROSETTA)
        self.assertTrue(path)
        self.assertNotIn(base_point, path[:1])

    def test_zero_tolerance_is_rejected(self):
        from dataclasses import replace

        with self.assertRaises(ValueError):
            replace(HEART, position_tolerance=0)

    def test_next_challenge_steps_up_and_stops_at_expert(self):
        self.assertIs(next_challenge(HEART), TULIP)
        self.assertIs(next_challenge(TULIP), ROSETTA)
        self.assertIsNone(next_challenge(ROSETTA))


class JugTests(unittest.TestCase):
    def test_simulated_jug_pours_only_while_pressed(self):
        jug = SimulatedJugController()
        jug.set_pointer(0.2, -0.3, pressed=True)
        self.assertEqual(jug.read(), JugState(0.2, -0.3, 1.0))
        jug.set_pointer(0.2, -0.3, pressed=False)
        self.assertEqual(jug.read().tilt, 0.0)

    def test_simulated_jug_clamps_to_the_cup(self):
        jug = SimulatedJugController()
        jug.set_pointer(3.0, -3.0, pressed=True)
        self.assertEqual((jug.read().x, jug.read().y), (1.0, -1.0))

    def test_reset_returns_to_centre_with_no_pour(self):
        jug = SimulatedJugController()
        jug.set_pointer(0.5, 0.5, pressed=True)
        jug.reset()
        self.assertEqual(jug.read(), JugState())

    def test_flow_assist_uses_guide_flow_when_tilted(self):
        guide = guide_at(HEART, 4.0)
        assisted = apply_flow_assist(JugState(0, 0, 1.0), guide, True)
        self.assertEqual(assisted.tilt, guide.flow)

    def test_flow_assist_keeps_zero_when_upright(self):
        guide = guide_at(HEART, 4.0)
        assisted = apply_flow_assist(JugState(0, 0, 0.0), guide, True)
        self.assertEqual(assisted.tilt, 0.0)

    def test_without_assist_the_real_tilt_is_kept(self):
        guide = guide_at(HEART, 4.0)
        jug = JugState(0, 0, 0.3)
        self.assertIs(apply_flow_assist(jug, guide, False), jug)


class ScoringTests(unittest.TestCase):
    def test_steering_is_full_on_the_guide_and_zero_at_tolerance(self):
        guide = guide_at(HEART, 4.0)
        on = JugState(guide.x, guide.y, 0.8)
        edge = JugState(guide.x + HEART.position_tolerance, guide.y, 0.8)
        self.assertEqual(steering_score(guide, on, HEART.position_tolerance), 1.0)
        self.assertEqual(steering_score(guide, edge, HEART.position_tolerance), 0.0)

    def test_on_target_matches_tolerance(self):
        guide = guide_at(HEART, 4.0)
        near = JugState(guide.x + 0.1, guide.y, 0)
        far = JugState(guide.x + 0.5, guide.y, 0)
        self.assertTrue(is_on_target(guide, near, HEART.position_tolerance))
        self.assertFalse(is_on_target(guide, far, HEART.position_tolerance))

    def test_flow_score_rewards_matching_tilt(self):
        guide = guide_at(HEART, 4.0)
        self.assertEqual(flow_score(guide, JugState(0, 0, guide.flow)), 1.0)
        self.assertEqual(flow_score(guide, JugState(0, 0, 0.0)), 0.0)

    def test_add_sample_returns_new_stats(self):
        stats = PourStats()
        guide = guide_at(HEART, 4.0)
        updated = add_sample(stats, guide, JugState(0, 0, 0.5), 0.1, 0.3)
        self.assertEqual(stats, PourStats())
        self.assertEqual(updated.flow_samples, 1)
        self.assertAlmostEqual(updated.milk_poured, 0.05)

    def test_pauses_do_not_count_towards_steering(self):
        pause = guide_at(TULIP, TULIP.segments[0].duration + 1.4)
        self.assertEqual(pause.flow, 0.0)
        stats = add_sample(PourStats(), pause, JugState(1, 1, 0), 0.1, 0.24)
        self.assertEqual(stats.steering_samples, 0)

    def test_expected_milk_is_positive_for_every_challenge(self):
        for challenge in CHALLENGES:
            self.assertGreater(expected_milk(challenge), 0, challenge.key)

    def test_perfect_pour_scores_full_marks(self):
        for challenge in CHALLENGES:
            result = play(
                challenge, lambda g: JugState(g.x, g.y, g.flow)
            )
            self.assertGreaterEqual(result.score, 98, challenge.key)
            self.assertEqual(result.stars, 3)
            self.assertEqual(result.rank, "LATTE ARTIST")
            self.assertAlmostEqual(result.fill_ratio, 1.0, delta=0.03)

    def test_never_pouring_scores_low(self):
        result = play(TULIP, lambda g: JugState(g.x, g.y, 0.0))
        self.assertLess(result.score, 40)
        self.assertEqual(result.steering, 0.0)
        self.assertEqual(result.fill, 0.0)

    def test_pouring_in_the_wrong_place_loses_steering(self):
        result = play(ROSETTA, lambda g: JugState(0.9, 0.9, g.flow))
        self.assertEqual(result.steering, 0.0)
        self.assertLess(result.score, 55)

    def test_star_thresholds(self):
        self.assertEqual(stars_for(100), 3)
        self.assertEqual(stars_for(85), 3)
        self.assertEqual(stars_for(84), 2)
        self.assertEqual(stars_for(65), 2)
        self.assertEqual(stars_for(40), 1)
        self.assertEqual(stars_for(39), 0)


if __name__ == "__main__":
    unittest.main()
