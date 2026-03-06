import unittest
import main


class TestDiceGame(unittest.TestCase):

    def test_all_pairs_for_total(self):
        pairs_7 = main.all_pairs_for_total(7)
        self.assertEqual(len(pairs_7), 6)
        self.assertEqual(pairs_7[0], (1, 6))
        self.assertEqual(pairs_7[-1], (6, 1))

        pairs_2 = main.all_pairs_for_total(2)
        self.assertEqual(pairs_2, [(1, 1)])

        pairs_12 = main.all_pairs_for_total(12)
        self.assertEqual(pairs_12, [(6, 6)])

    def test_fair_probability_sum(self):
        self.assertAlmostEqual(main.fair_probability_sum(7), 6 / 36)
        self.assertAlmostEqual(main.fair_probability_sum(2), 1 / 36)

    def test_fair_probability_parity(self):
        p_even = main.fair_probability_parity("even")
        p_odd = main.fair_probability_parity("odd")
        self.assertAlmostEqual(p_even + p_odd, 1.0)

    def test_fair_probability_highlow(self):
        p_high = main.fair_probability_highlow("high")
        p_low = main.fair_probability_highlow("low")
        self.assertTrue(p_high > 0)
        self.assertTrue(p_low > 0)
        self.assertTrue(p_high + p_low < 1.0)

    def test_bet_win_probability(self):
        self.assertAlmostEqual(main.bet_win_probability("sum", 7), 6 / 36)
        self.assertAlmostEqual(main.bet_win_probability("parity", "even"), 18 / 36)
        self.assertAlmostEqual(main.bet_win_probability("highlow", "high"), 15 / 36)

    def test_did_win_bet_sum(self):
        self.assertTrue(main.did_win_bet("sum", 7, 3, 4))
        self.assertFalse(main.did_win_bet("sum", 8, 3, 4))

    def test_did_win_bet_parity(self):
        self.assertTrue(main.did_win_bet("parity", "even", 3, 3))
        self.assertFalse(main.did_win_bet("parity", "odd", 3, 3))

    def test_did_win_bet_highlow(self):
        self.assertTrue(main.did_win_bet("highlow", "high", 6, 6))
        self.assertTrue(main.did_win_bet("highlow", "low", 1, 2))
        self.assertFalse(main.did_win_bet("highlow", "high", 3, 4))

    def test_payout_multiplier_formula(self):
        mult_easy = main.payout_multiplier_from_probability(0.5)
        mult_hard = main.payout_multiplier_from_probability(1 / 36)
        self.assertTrue(mult_hard >= mult_easy)
        self.assertTrue(mult_hard <= main.PAYOUT_CAP_MULT)

    def test_snake_eyes_override(self):
        delta, lines = main.compute_round_result(10, "sum", 7, 1, 1)
        self.assertEqual(delta, 10 * main.SNAKE_EYES_MULT)
        self.assertTrue(any("Snake Eyes" in line for line in lines))

    def test_make_rig_returns_callable(self):
        rig = main.make_rig("always_7")
        self.assertTrue(callable(rig))

    def test_rig_always_7(self):
        rig = main.make_rig("always_7")
        d1, d2 = rig([], 1)
        self.assertEqual(d1 + d2, 7)

    def test_rig_never_2_or_12(self):
        rig = main.make_rig("never_2_or_12")
        for i in range(20):
            d1, d2 = rig([], i + 1)
            self.assertNotIn(d1 + d2, [2, 12])


if __name__ == "__main__":
    print("\n========================================")
    print(" Running Dice Game Test Suite")
    print("========================================\n")
    unittest.main(verbosity=2)