# test_game.py
# A simple test suite for main.py using assert statements.
# Run with: python3 test_game.py

from main import (
    roll_with_forced_total,
    rig_always_total_7,
    rig_never_total_2_or_12,
    rig_every_5th_roll_is_7,
    rig_after_8_then_9,
    compute_payout_multiplier
)

def run_tests():
    # ----------------------------
    # TEST 1: roll_with_forced_total always returns the correct sum
    # ----------------------------
    for _ in range(50):
        d1, d2 = roll_with_forced_total(7)
        assert 1 <= d1 <= 6 and 1 <= d2 <= 6
        assert d1 + d2 == 7
    print("Test 1 passed: roll_with_forced_total(7) always sums to 7.")

    # ----------------------------
    # TEST 2: rig_always_total_7 always produces total 7
    # ----------------------------
    history = []
    for roll_num in range(1, 51):
        d1, d2 = rig_always_total_7(history, roll_num)
        assert d1 + d2 == 7
    print("Test 2 passed: rig_always_total_7 always returns total 7.")

    # ----------------------------
    # TEST 3: rig_never_total_2_or_12 never returns 2 or 12
    # ----------------------------
    history = []
    for roll_num in range(1, 201):
        d1, d2 = rig_never_total_2_or_12(history, roll_num)
        total = d1 + d2
        assert total != 2 and total != 12
    print("Test 3 passed: rig_never_total_2_or_12 never returns 2 or 12.")

    # ----------------------------
    # TEST 4: rig_every_5th_roll_is_7 forces roll 5,10,15,... to be 7
    # ----------------------------
    history = []
    for roll_num in range(1, 51):
        d1, d2 = rig_every_5th_roll_is_7(history, roll_num)
        total = d1 + d2
        if roll_num % 5 == 0:
            assert total == 7
        # update history like the real game would
        history.append({"d1": d1, "d2": d2, "total": total})
    print("Test 4 passed: rig_every_5th_roll_is_7 forces every 5th roll to 7.")

    # ----------------------------
    # TEST 5: rig_after_8_then_9 forces 9 after an 8
    # ----------------------------
    history = [{"d1": 2, "d2": 6, "total": 8}]  # previous roll total = 8
    d1, d2 = rig_after_8_then_9(history, 2)
    assert d1 + d2 == 9
    print("Test 5 passed: rig_after_8_then_9 forces 9 after an 8.")

    # ----------------------------
    # TEST 6: Snake eyes always pays 5x regardless of bet type
    # ----------------------------
    mult, _ = compute_payout_multiplier("sum", 7, 1, 1)
    assert mult == 5
    mult, _ = compute_payout_multiplier("parity", "even", 1, 1)
    assert mult == 5
    mult, _ = compute_payout_multiplier("highlow", "high", 1, 1)
    assert mult == 5
    print("Test 6 passed: snake eyes pays 5x regardless of bet type.")

    # ----------------------------
    # TEST 7: Parity bet payout (correct vs incorrect)
    # ----------------------------
    mult, _ = compute_payout_multiplier("parity", "even", 2, 4)  # total=6 even
    assert mult == 2
    mult, _ = compute_payout_multiplier("parity", "odd", 2, 4)   # total=6 even
    assert mult == 0
    print("Test 7 passed: parity payout works for correct/incorrect.")

    # ----------------------------
    # TEST 8: High/Low rules (7 always loses)
    # ----------------------------
    mult, _ = compute_payout_multiplier("highlow", "high", 3, 4)  # total=7
    assert mult == 0
    print("Test 8 passed: high/low loses on 7.")

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    run_tests()