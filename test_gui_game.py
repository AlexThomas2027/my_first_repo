import unittest
import gui_game


class TestGuiGameLogic(unittest.TestCase):

    def test_all_pairs_for_total(self):
        pairs_2 = gui_game.all_pairs_for_total(2)
        pairs_7 = gui_game.all_pairs_for_total(7)
        pairs_12 = gui_game.all_pairs_for_total(12)

        self.assertEqual(pairs_2, [(1, 1)])
        self.assertEqual(len(pairs_7), 6)
        self.assertEqual(pairs_12, [(6, 6)])

    def test_roll_with_forced_total(self):
        for total in range(2, 13):
            d1, d2 = gui_game.roll_with_forced_total(total)
            self.assertEqual(d1 + d2, total)

    def test_fair_probability_sum(self):
        self.assertAlmostEqual(gui_game.fair_probability_sum(2), 1 / 36)
        self.assertAlmostEqual(gui_game.fair_probability_sum(7), 6 / 36)
        self.assertAlmostEqual(gui_game.fair_probability_sum(12), 1 / 36)

    def test_fair_probability_parity(self):
        self.assertAlmostEqual(gui_game.fair_probability_parity("odd"), 18 / 36)
        self.assertAlmostEqual(gui_game.fair_probability_parity("even"), 18 / 36)

    def test_fair_probability_highlow(self):
        self.assertAlmostEqual(gui_game.fair_probability_highlow("low"), 15 / 36)
        self.assertAlmostEqual(gui_game.fair_probability_highlow("high"), 15 / 36)

    def test_bet_win_probability(self):
        self.assertAlmostEqual(gui_game.bet_win_probability("sum", 7), 6 / 36)
        self.assertAlmostEqual(gui_game.bet_win_probability("odd/even", "odd"), 18 / 36)
        self.assertAlmostEqual(gui_game.bet_win_probability("high/low", "high"), 15 / 36)

    def test_payout_multiplier_from_probability(self):
        self.assertEqual(gui_game.payout_multiplier_from_probability(0), 0.0)

        mult = gui_game.payout_multiplier_from_probability(6 / 36)
        self.assertGreaterEqual(mult, 1.0)
        self.assertLessEqual(mult, gui_game.MAX_PAYOUT_MULTIPLIER)

    def test_did_win_bet_sum(self):
        self.assertTrue(gui_game.did_win_bet("sum", 8, 3, 5))
        self.assertFalse(gui_game.did_win_bet("sum", 7, 3, 5))

    def test_did_win_bet_odd_even(self):
        self.assertTrue(gui_game.did_win_bet("odd/even", "odd", 3, 4))
        self.assertTrue(gui_game.did_win_bet("odd/even", "even", 3, 5))
        self.assertFalse(gui_game.did_win_bet("odd/even", "odd", 3, 5))

    def test_did_win_bet_high_low(self):
        self.assertTrue(gui_game.did_win_bet("high/low", "high", 5, 4))
        self.assertTrue(gui_game.did_win_bet("high/low", "low", 2, 3))
        self.assertFalse(gui_game.did_win_bet("high/low", "high", 3, 4))  # total 7 loses
        self.assertFalse(gui_game.did_win_bet("high/low", "low", 3, 4))   # total 7 loses

    def test_compute_round_result_snake_eyes(self):
        winnings, lines = gui_game.compute_round_result(10, "sum", 2, 1, 1)
        self.assertEqual(winnings, 10 * gui_game.SNAKE_EYES_MULTIPLIER)
        self.assertTrue(any("Snake eyes" in line for line in lines))

    def test_compute_round_result_regular_win(self):
        winnings, lines = gui_game.compute_round_result(10, "sum", 8, 3, 5)
        self.assertGreater(winnings, 0)
        self.assertTrue(any("You won the bet" in line for line in lines))

    def test_compute_round_result_regular_loss(self):
        winnings, lines = gui_game.compute_round_result(10, "sum", 7, 3, 5)
        self.assertEqual(winnings, -10)
        self.assertTrue(any("You lose $10." in line for line in lines))

    def test_make_rig_always_force_total(self):
        rig = gui_game.make_rig_always_force_total(9)
        for roll_number in range(1, 6):
            d1, d2 = rig([], roll_number)
            self.assertEqual(d1 + d2, 9)

    def test_make_rig_never_allow_totals(self):
        rig = gui_game.make_rig_never_allow_totals([2, 12])
        for roll_number in range(1, 21):
            d1, d2 = rig([], roll_number)
            self.assertNotIn(d1 + d2, [2, 12])

    def test_make_rig_force_total_every_nth_roll(self):
        rig = gui_game.make_rig_force_total_every_nth_roll(3, 8)

        d1, d2 = rig([], 1)
        self.assertIn(d1 + d2, range(2, 13))

        d1, d2 = rig([], 2)
        self.assertIn(d1 + d2, range(2, 13))

        d1, d2 = rig([], 3)
        self.assertEqual(d1 + d2, 8)

        d1, d2 = rig([], 6)
        self.assertEqual(d1 + d2, 8)

    def test_make_rig_force_total_after_trigger_total(self):
        rig = gui_game.make_rig_force_total_after_trigger_total(5, 9)

        d1, d2 = rig([], 1)
        self.assertIn(d1 + d2, range(2, 13))

        history = [{"d1": 2, "d2": 3, "total": 5}]
        d1, d2 = rig(history, 2)
        self.assertEqual(d1 + d2, 9)

    def test_build_custom_rig_rule_always(self):
        code, description, rig = gui_game.build_custom_rig_rule("Always force a total", "10")
        self.assertEqual(code, "always_force_total_10")
        self.assertIn("Always force the dice to total 10", description)

        d1, d2 = rig([], 1)
        self.assertEqual(d1 + d2, 10)

    def test_build_custom_rig_rule_never(self):
        code, description, rig = gui_game.build_custom_rig_rule("Never allow certain totals", "2,12")
        self.assertEqual(code, "never_allow_totals_2_12")
        self.assertIn("Never allow totals 2, 12", description)

        for roll_number in range(1, 21):
            d1, d2 = rig([], roll_number)
            self.assertNotIn(d1 + d2, [2, 12])

    def test_build_custom_rig_rule_every_n(self):
        code, description, rig = gui_game.build_custom_rig_rule("Force a total every N rolls", "8", "4")
        self.assertEqual(code, "force_total_8_every_4th_roll")
        self.assertIn("Force total 8 every 4th roll", description)

        d1, d2 = rig([], 4)
        self.assertEqual(d1 + d2, 8)

    def test_build_custom_rig_rule_after_trigger(self):
        code, description, rig = gui_game.build_custom_rig_rule("Force a total after another total", "5", "9")
        self.assertEqual(code, "force_total_9_after_total_5")
        self.assertIn("Force total 9 after a roll totaling 5", description)

        history = [{"d1": 2, "d2": 3, "total": 5}]
        d1, d2 = rig(history, 2)
        self.assertEqual(d1 + d2, 9)

    def test_build_random_rig_rule(self):
        code, description, rig = gui_game.build_random_rig_rule()

        self.assertIsInstance(code, str)
        self.assertIsInstance(description, str)
        self.assertTrue(callable(rig))

        d1, d2 = rig([], 1)
        self.assertIn(d1, range(1, 7))
        self.assertIn(d2, range(1, 7))

    def test_ascii_dice_art_exists_for_all_faces(self):
        for face in range(1, 7):
            self.assertIn(face, gui_game.DICE_ART)
            self.assertEqual(len(gui_game.DICE_ART[face]), 5)


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Running test suite for gui_game.py")
    print("=" * 50 + "\n")
    unittest.main(verbosity=2)