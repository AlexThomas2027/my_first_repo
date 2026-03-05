import random

# ============================================================
# Dice Betting + Rig Deduction Game
#
# What this game is:
# - You start with a bankroll and place bets on each dice roll.
# - The dice are secretly rigged using ONE rig rule.
# - You can keep betting, or you can guess the rig rule at any time.
# - If you guess correctly, you WIN the game immediately.
#
# IMPORTANT CLARIFICATION (per professor feedback):
# - Rig rules depend ONLY on roll history / roll number.
# - Rig rules do NOT depend on your bet type or wager amount.
#
# Rig rules allowed in this project:
# - Rules that change dice outcomes based on the roll number or past rolls
# - Rules that force certain totals sometimes or always
# - Rules that reject certain totals (reroll until allowed)
# ============================================================

STARTING_BALANCE = 100
MAX_HISTORY_TO_SHOW = 10

HOUSE_EDGE = 0.05          # 5% house edge
PAYOUT_CAP_MULT = 12       # max payout multiplier (keeps game sane)
SNAKE_EYES_MULT = 5        # special payout multiplier regardless of bet

# ------------------------------------------------------------
# Input helpers
# ------------------------------------------------------------

def get_int(prompt, min_val=None, max_val=None):
    while True:
        s = input(prompt).strip()
        try:
            val = int(s)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if min_val is not None and val < min_val:
            print(f"Please enter a number >= {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print(f"Please enter a number <= {max_val}.")
            continue
        return val


def get_choice(prompt, choices):
    choices_lower = {c.lower(): c for c in choices}
    while True:
        s = input(prompt).strip().lower()
        if s in choices_lower:
            return s
        print(f"Please choose one of: {', '.join(choices)}")


# ------------------------------------------------------------
# Dice / probability utilities
# ------------------------------------------------------------

def roll_two_dice_fair():
    return random.randint(1, 6), random.randint(1, 6)


def all_pairs_for_total(total):
    pairs = []
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            if d1 + d2 == total:
                pairs.append((d1, d2))
    return pairs


def roll_with_forced_total(total):
    pairs = all_pairs_for_total(total)
    if not pairs:
        return roll_two_dice_fair()
    return random.choice(pairs)


def fair_probability_sum(total):
    # total from 2..12
    return len(all_pairs_for_total(total)) / 36.0


def fair_probability_parity(parity):
    # parity: "odd" or "even"
    count = 0
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            s = d1 + d2
            if parity == "odd" and s % 2 == 1:
                count += 1
            if parity == "even" and s % 2 == 0:
                count += 1
    return count / 36.0


def fair_probability_highlow(choice):
    # choice: "high" means 8-12, "low" means 2-6, and 7 is a loss
    count = 0
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            s = d1 + d2
            if s == 7:
                continue
            if choice == "high" and s > 7:
                count += 1
            if choice == "low" and s < 7:
                count += 1
    return count / 36.0


# ------------------------------------------------------------
# Rig rule factory (higher-order function)
#   make_rig(rule_name) -> rig_func(history, roll_num) -> (d1, d2)
# ------------------------------------------------------------

def make_rig(rule_name):
    """
    Returns a rig function for the given rule_name.

    IMPORTANT:
    - Rig rule depends only on roll_num/history
    - Rig rule does NOT depend on bet type or wager
    """

    def always_7(history, roll_num):
        return roll_with_forced_total(7)

    def never_2_or_12(history, roll_num):
        for _ in range(50):
            d1, d2 = roll_two_dice_fair()
            if (d1 + d2) not in (2, 12):
                return d1, d2
        return roll_two_dice_fair()

    def every_5th_is_7(history, roll_num):
        if roll_num % 5 == 0:
            return roll_with_forced_total(7)
        return roll_two_dice_fair()

    def after_8_then_9(history, roll_num):
        if history and history[-1]["total"] == 8:
            return roll_with_forced_total(9)
        return roll_two_dice_fair()

    rules = {
        "always_7": always_7,
        "never_2_or_12": never_2_or_12,
        "every_5th_is_7": every_5th_is_7,
        "after_8_then_9": after_8_then_9,
    }

    if rule_name not in rules:
        raise ValueError("Unknown rig rule name.")
    return rules[rule_name]


RIG_RULE_NAMES = ["always_7", "never_2_or_12", "every_5th_is_7", "after_8_then_9"]


def pick_secret_rig():
    key = random.choice(RIG_RULE_NAMES)
    return key, make_rig(key)


# ------------------------------------------------------------
# Bet system (flexible)
# Instead of hard-coding payouts per bet type,
# we compute payout from fair win probability.
# ------------------------------------------------------------

def bet_win_probability(bet_type, bet_value):
    if bet_type == "sum":
        return fair_probability_sum(bet_value)
    if bet_type == "parity":
        return fair_probability_parity(bet_value)
    if bet_type == "highlow":
        return fair_probability_highlow(bet_value)
    return 0.0


def did_win_bet(bet_type, bet_value, d1, d2):
    total = d1 + d2
    if bet_type == "sum":
        return total == bet_value
    if bet_type == "parity":
        return ("even" if total % 2 == 0 else "odd") == bet_value
    if bet_type == "highlow":
        if total == 7:
            return False
        return ("high" if total > 7 else "low") == bet_value
    return False


def payout_multiplier_from_probability(p_win):
    """
    Uses a formula instead of hard-coding per bet type:
      expected value favors house by HOUSE_EDGE.
      multiplier approximates: (1 - HOUSE_EDGE) / p_win

    Example:
      if p_win = 0.5 and house edge = 0.05, multiplier ≈ 1.9
    """
    if p_win <= 0:
        return 0
    mult = (1.0 - HOUSE_EDGE) / p_win
    mult = max(1.0, min(mult, PAYOUT_CAP_MULT))
    # Round to 2 decimals for readability
    return round(mult, 2)


def compute_round_result(wager, bet_type, bet_value, d1, d2):
    """
    Returns (delta_balance, message_lines_list)
    delta_balance is the amount to add to balance (negative = loss).

    Special rule:
      Snake eyes pays SNAKE_EYES_MULT no matter what you bet.
    """
    total = d1 + d2
    lines = [f"You rolled {d1} + {d2} = {total}."]

    # Snake eyes override
    if d1 == 1 and d2 == 1:
        winnings = int(wager * SNAKE_EYES_MULT)
        lines.append(f"Snake Eyes! Automatic payout: {SNAKE_EYES_MULT}x.")
        lines.append(f"You win ${winnings}.")
        return winnings, lines

    # Normal win/lose
    won = did_win_bet(bet_type, bet_value, d1, d2)

    p_win = bet_win_probability(bet_type, bet_value)
    mult = payout_multiplier_from_probability(p_win)

    if won:
        winnings = int(wager * mult)
        lines.append(f"Win! Payout multiplier: {mult}x (based on difficulty).")
        lines.append(f"You win ${winnings}.")
        return winnings, lines
    else:
        lines.append("Loss. You lose your wager.")
        return -wager, lines


# ------------------------------------------------------------
# UI helpers
# ------------------------------------------------------------

def print_header():
    print("\n" + "=" * 55)
    print(" DICE BETTING: RIG DEDUCTION")
    print("=" * 55)
    print("Goal: grow your bankroll and identify the secret rig rule.")
    print("You can guess the rig rule at any time. A correct guess wins instantly.")
    print("Rig rules affect only dice outcomes (history/roll number), not your bet.\n")


def print_instructions():
    print("BETTING OPTIONS")
    print("  1) Sum Bet      - Choose a total (2 to 12). Win if dice sum to it.")
    print("  2) Odd/Even Bet - Choose odd or even. Win if sum matches.")
    print("  3) High/Low Bet - Choose high (8-12) or low (2-6). 7 always loses.")
    print("\nPAYOUTS")
    print("  Payouts are calculated from a probability formula:")
    print("  harder bets (lower chance) pay more, with a small house edge.")
    print(f"  Maximum payout multiplier is capped at {PAYOUT_CAP_MULT}x.")
    print(f"  Special rule: Snake eyes (1+1) pays {SNAKE_EYES_MULT}x no matter what.\n")


def print_history(history):
    if not history:
        print("Roll history: (none yet)")
        return
    print("Recent rolls:")
    start = max(0, len(history) - MAX_HISTORY_TO_SHOW)
    for i in range(start, len(history)):
        h = history[i]
        print(f"  Roll {i+1}: {h['d1']} + {h['d2']} = {h['total']}")


def choose_bet(balance):
    print("\nChoose your bet:")
    print("  1) Sum")
    print("  2) Odd/Even")
    print("  3) High/Low")
    b = get_choice("Enter 1, 2, or 3: ", ["1", "2", "3"])

    wager = get_int(f"Wager (1 - {balance}): ", min_val=1, max_val=balance)

    if b == "1":
        bet_type = "sum"
        bet_value = get_int("Pick a sum (2-12): ", min_val=2, max_val=12)
    elif b == "2":
        bet_type = "parity"
        bet_value = get_choice("Pick odd or even: ", ["odd", "even"])
    else:
        bet_type = "highlow"
        bet_value = get_choice("Pick high or low: ", ["high", "low"])

    # Show estimated payout (based on fair probability)
    p_win = bet_win_probability(bet_type, bet_value)
    est_mult = payout_multiplier_from_probability(p_win)
    print(f"Estimated payout multiplier (if you win): ~{est_mult}x")

    return wager, bet_type, bet_value


def guess_rig_rule():
    print("\nGuess the rig rule (type exactly):")
    for name in RIG_RULE_NAMES:
        print(f"  - {name}")
    return get_choice("Your guess: ", RIG_RULE_NAMES)


def choose_rig_mode():
    """
    Professor asked to allow user to specify a rig rule (higher-order functions).
    We keep it optional to avoid hurting the normal gameplay flow.
    """
    print("Rig setup:")
    print("  1) Secret random rig (recommended gameplay)")
    print("  2) Choose a rig rule (for testing / demonstration)")
    choice = get_choice("Enter 1 or 2: ", ["1", "2"])
    if choice == "1":
        return pick_secret_rig()
    else:
        print("\nChoose a rig rule:")
        for name in RIG_RULE_NAMES:
            print(f"  - {name}")
        key = get_choice("Rig rule: ", RIG_RULE_NAMES)
        return key, make_rig(key)


# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------

def main():
    print_header()
    print_instructions()

    balance = STARTING_BALANCE
    history = []
    roll_num = 0

    secret_key, rig_func = choose_rig_mode()

    while True:
        if balance <= 0:
            print("\nYou are out of money. Game over.")
            print(f"The rig rule was: {secret_key}")
            break

        print("\n" + "-" * 55)
        print(f"Balance: ${balance}")
        print_history(history)

        print("\nWhat would you like to do?")
        print("  p) Play a round")
        print("  g) Guess the rig rule (correct guess wins instantly)")
        print("  q) Quit")
        action = get_choice("Choice (p/g/q): ", ["p", "g", "q"])

        if action == "q":
            print("\nThanks for playing!")
            print(f"The rig rule was: {secret_key}")
            break

        if action == "g":
            guess = guess_rig_rule()
            if guess == secret_key:
                print("\nCorrect! You identified the rig rule.")
                print(f"You win with a final balance of ${balance}!")
                break
            else:
                penalty = min(5, balance)
                balance -= penalty
                print(f"\nIncorrect. Penalty: -${penalty}.")
                continue

        # Play a round
        wager, bet_type, bet_value = choose_bet(balance)

        roll_num += 1
        d1, d2 = rig_func(history, roll_num)
        total = d1 + d2
        history.append({"d1": d1, "d2": d2, "total": total})

        delta, lines = compute_round_result(wager, bet_type, bet_value, d1, d2)
        for line in lines:
            print(line)

        balance += delta

    print("\nGame ended.")


if __name__ == "__main__":
    main()