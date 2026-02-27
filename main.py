import random

# ---------------------------------------
# Dice Betting + Rig Deduction Game (console)
#
# What this program does:
# - The player starts with a bankroll (balance).
# - Each round, the player can place a bet on a dice outcome.
# - The dice are secretly "rigged" according to ONE hidden rig rule.
# - The player can view roll history to spot patterns.
#
# Win condition:
# - The player WINS THE GAME by correctly guessing the hidden rig rule.
# - The player LOSES the game if their balance reaches $0.
# ---------------------------------------

STARTING_BALANCE = 100
MAX_HISTORY_TO_SHOW = 10


# ----------------------------
# Input helpers
# ----------------------------

def get_int(prompt, min_val=None, max_val=None):
    """Safe integer input with optional bounds."""
    while True:
        s = input(prompt).strip()
        try:
            val = int(s)
        except ValueError:
            print("Please enter an integer.")
            continue

        if min_val is not None and val < min_val:
            print(f"Please enter a number >= {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print(f"Please enter a number <= {max_val}.")
            continue
        return val


def get_choice(prompt, choices):
    """
    Safe choice input.
    choices: list of strings the user is allowed to enter (case-insensitive).
    Returns the user's choice lowercased.
    """
    choices_lower = {c.lower(): c for c in choices}
    while True:
        s = input(prompt).strip().lower()
        if s in choices_lower:
            return s
        print(f"Please choose one of: {', '.join(choices)}")


# ----------------------------
# Base dice rolling
# ----------------------------

def roll_two_dice_fair():
    """Roll two fair six-sided dice."""
    return random.randint(1, 6), random.randint(1, 6)


def all_pairs_for_total(total):
    """Return all (d1, d2) pairs (1..6) that sum to `total`."""
    pairs = []
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            if d1 + d2 == total:
                pairs.append((d1, d2))
    return pairs


def roll_with_forced_total(total):
    """
    Force the dice to sum to `total` by randomly choosing a valid pair.
    If total is impossible (not 2..12), fall back to a fair roll.
    """
    pairs = all_pairs_for_total(total)
    if not pairs:
        return roll_two_dice_fair()
    return random.choice(pairs)


# ============================================================
# Rig Rule Specification
# ============================================================
# A rig rule is a function:
#       rig(history, roll_number) -> (d1, d2)
#
# Allowed dependencies:
#   - roll_number (1-indexed)
#   - history of previous rolls (list of dicts: {'d1','d2','total'})
#
# NOT allowed dependencies:
#   - bet type
#   - wager amount
#   - anything about the player's current bet choice
#
# Requirements:
#   - Must return valid dice values (1-6, 1-6)
#   - Must NOT modify history directly
# ============================================================


# ----------------------------
# Rig rule implementations
# ----------------------------

def rig_always_total_7(history, roll_number):
    """Always force total = 7."""
    return roll_with_forced_total(7)


def rig_never_total_2_or_12(history, roll_number):
    """
    Never allow totals 2 or 12.
    If a fair roll produces 2 or 12, reroll (bounded attempts).
    """
    for _ in range(50):
        d1, d2 = roll_two_dice_fair()
        if (d1 + d2) not in (2, 12):
            return d1, d2
    return roll_two_dice_fair()  # fallback


def rig_every_5th_roll_is_7(history, roll_number):
    """Every 5th roll is forced to total = 7; otherwise fair."""
    if roll_number % 5 == 0:
        return roll_with_forced_total(7)
    return roll_two_dice_fair()


def rig_after_8_then_9(history, roll_number):
    """If the previous total was 8, force the next total to 9; otherwise fair."""
    if history and history[-1]["total"] == 8:
        return roll_with_forced_total(9)
    return roll_two_dice_fair()


# Registry of rig rules (demonstrates higher-order functions: functions stored as values)
RIG_RULES = {
    "always_7": rig_always_total_7,
    "never_2_or_12": rig_never_total_2_or_12,
    "every_5th_is_7": rig_every_5th_roll_is_7,
    "after_8_then_9": rig_after_8_then_9,
}


def pick_secret_rig_rule():
    """
    Randomly choose ONE rig rule to be the hidden rig for this game.
    The player does NOT see this value until the game ends (or they win by guessing it).
    """
    key = random.choice(list(RIG_RULES.keys()))
    return key, RIG_RULES[key]


def rigged_roll(history, roll_number, rig_func):
    """
    Produce a roll using the selected rig function.
    This is higher-order programming: rig_func is a function passed as an argument.
    """
    return rig_func(history, roll_number)


# ----------------------------
# Betting logic / payout logic
# ----------------------------

def compute_payout_multiplier(bet_type, bet_value, d1, d2):
    """
    Returns (multiplier, message).

    Payout model:
    - If you win: balance increases by wager * multiplier
    - If you lose: balance decreases by wager

    Special rule:
    - Snake eyes (1,1) pays 5x wager regardless of bet type.
    """
    total = d1 + d2

    # Special rule: snake eyes overrides everything else
    if d1 == 1 and d2 == 1:
        return 5, "Snake eyes! Special 5x payout!"

    # BET TYPE: SUM
    # - Player chooses a total from 2 to 12
    # - Win if (d1 + d2) == chosen total
    if bet_type == "sum":
        if total == bet_value:
            hard_sums = {2, 3, 11, 12}
            if total in hard_sums:
                return 4, "You hit a hard sum! 4x payout."
            return 3, "You hit the sum! 3x payout."
        return 0, "Missed the sum."

    # BET TYPE: PARITY
    # - Player chooses odd or even
    # - Win if the total is odd/even matching the chosen parity
    if bet_type == "parity":
        parity = "even" if total % 2 == 0 else "odd"
        if parity == bet_value:
            return 2, "Correct parity! 2x payout."
        return 0, "Wrong parity."

    # BET TYPE: HIGH/LOW
    # - Player chooses high or low
    # - "Low" means totals 2–6
    # - "High" means totals 8–12
    # - Rolling exactly 7 is an automatic loss for this bet
    if bet_type == "highlow":
        if total == 7:
            return 0, "Rolled 7 (house wins on High/Low)."
        outcome = "high" if total > 7 else "low"
        if outcome == bet_value:
            return 2, "Correct high/low! 2x payout."
        return 0, "Wrong high/low."

    return 0, "Invalid bet type."


# ----------------------------
# UI helpers
# ----------------------------

def print_history(history):
    """Print the last few rolls so the player can try to spot the rig pattern."""
    if not history:
        print("No roll history yet.")
        return

    print("\nRecent rolls:")
    start = max(0, len(history) - MAX_HISTORY_TO_SHOW)
    for i in range(start, len(history)):
        h = history[i]
        print(f"  Roll {i+1}: {h['d1']} + {h['d2']} = {h['total']}")


def choose_bet(balance):
    """
    Ask the user for wager + bet type + bet value.
    Displays payout multipliers so the player understands
    the risk/reward tradeoff of each bet type.
    """

    wager = get_int(f"Enter wager (1 - {balance}): ", 1, balance)

    print("\nChoose bet type (risk vs reward shown below):")
    print("--------------------------------------------------")

    print("1) SUM BET")
    print("   - Pick an exact total (2-12).")
    print("   - Payout: 3x your wager if correct.")
    print("   - Hard sums (2, 3, 11, 12) pay 4x.")
    print("   - Higher risk, higher reward.")

    print("\n2) PARITY BET")
    print("   - Pick odd or even total.")
    print("   - Payout: 2x your wager if correct.")
    print("   - Medium risk, medium reward.")

    print("\n3) HIGH/LOW BET")
    print("   - Pick low (2-6) or high (8-12).")
    print("   - Rolling 7 is an automatic loss.")
    print("   - Payout: 2x your wager if correct.")
    print("   - Lower risk, lower reward.")

    print("--------------------------------------------------")

    bet_menu = get_choice("Type 1, 2, or 3: ", ["1", "2", "3"])

    if bet_menu == "1":
        return wager, "sum", get_int("Pick sum (2-12): ", 2, 12)

    elif bet_menu == "2":
        return wager, "parity", get_choice("Pick odd/even: ", ["odd", "even"])

    else:
        return wager, "highlow", get_choice("Pick high/low: ", ["high", "low"])


def guess_rig_rule_name():
    """
    Prompt user to guess the rig rule name.
    If the guess is correct, the player wins the game immediately.
    """
    print("\nGuess the rig rule (guessing correctly WINS the game):")
    for k in RIG_RULES:
        print(f" - {k}")
    return get_choice("Your guess: ", list(RIG_RULES.keys()))


# ----------------------------
# Main game loop
# ----------------------------

def main():
    print("Welcome to the Dice Betting + Rig Deduction Game!")
    print(f"Starting balance: ${STARTING_BALANCE}")
    print("Special rule: snake eyes (1 and 1) pays 5x your wager.")
    print("Goal: Deduce the rig rule from roll history and guess it correctly to WIN.\n")

    balance = STARTING_BALANCE
    history = []
    roll_number = 0

    # The computer secretly selects the rig rule at the start of the game.
    secret_key, rig_func = pick_secret_rig_rule()

    while True:
        # Lose condition
        if balance <= 0:
            print("Out of money. Game over.")
            print(f"The rig rule was: {secret_key}")
            break

        print(f"\nBalance: ${balance}")
        print_history(history)

        action = get_choice("\nChoose an action: (p)lay, (g)uess rig, (q)uit: ", ["p", "g", "q"])

        if action == "q":
            print("You quit the game.")
            print(f"The rig rule was: {secret_key}")
            break

        if action == "g":
            guess = guess_rig_rule_name()

            # WIN CONDITION:
            # If the player guesses the rig rule correctly, they win immediately.
            if guess == secret_key:
                print("\nCorrect! You guessed the rig rule and WIN the game!")
                print(f"Final balance: ${balance}")
                break
            else:
                # Small penalty to discourage random guessing
                penalty = min(5, balance)
                balance -= penalty
                print(f"\nIncorrect guess. You lose ${penalty}.")
            continue

        # action == "p": play a betting round
        wager, bet_type, bet_value = choose_bet(balance)

        roll_number += 1
        d1, d2 = rigged_roll(history, roll_number, rig_func)
        total = d1 + d2

        print(f"\nRolled: {d1} + {d2} = {total}")

        # Store roll in history for deduction
        history.append({"d1": d1, "d2": d2, "total": total})

        multiplier, message = compute_payout_multiplier(bet_type, bet_value, d1, d2)
        print(message)

        if multiplier > 0:
            winnings = wager * multiplier
            balance += winnings
            print(f"You won ${winnings}!")
        else:
            balance -= wager
            print(f"You lost ${wager}.")

    print("\nGame ended.")


if __name__ == "__main__":
    main()