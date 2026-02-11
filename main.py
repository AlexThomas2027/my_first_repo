import random

# ---------------------------------------
# Dice Betting + Rig Deduction Game (console)
#
# Goal:
# - Still a betting game (bankroll, bets, payouts)
# - Now includes a hidden "rig rule" that affects dice outcomes
# - Player knows dice are rigged, but must deduce how
#
# Checkpoint-friendly:
# - Runs end-to-end
# - Functions are commented
# - Easy to extend (more bets, more rig rules)
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
    """Return all (d1,d2) pairs (1..6) that sum to total."""
    pairs = []
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            if d1 + d2 == total:
                pairs.append((d1, d2))
    return pairs


def roll_with_forced_total(total):
    """
    Force the dice to sum to `total` by randomly choosing a valid pair.
    If total is impossible (not 2..12), fall back to fair roll.
    """
    pairs = all_pairs_for_total(total)
    if not pairs:
        return roll_two_dice_fair()
    return random.choice(pairs)


# ----------------------------
# Rig rules
# Each rig rule is a function:
#   rig(history, roll_num) -> (d1, d2)
#
# history: list of dicts, each dict has {'d1','d2','total'}
# roll_num: 1-indexed roll count
# ----------------------------

def rig_always_total_7(history, roll_num):
    """Always force total = 7."""
    return roll_with_forced_total(7)


def rig_never_total_2_or_12(history, roll_num):
    """
    Never allow totals 2 or 12.
    If a fair roll produces 2 or 12, reroll (bounded attempts).
    """
    for _ in range(50):  # safety bound to avoid infinite loops
        d1, d2 = roll_two_dice_fair()
        if (d1 + d2) not in (2, 12):
            return d1, d2
    return roll_two_dice_fair()  # fallback


def rig_every_5th_roll_is_7(history, roll_num):
    """Every 5th roll is forced to total = 7, otherwise fair."""
    if roll_num % 5 == 0:
        return roll_with_forced_total(7)
    return roll_two_dice_fair()


def rig_after_8_then_9(history, roll_num):
    """
    If the previous total was 8, force the next total to 9.
    Otherwise fair.
    """
    if history and history[-1]["total"] == 8:
        return roll_with_forced_total(9)
    return roll_two_dice_fair()


# A “registry” of rig rules: keys are what the player can guess.
RIG_RULES = {
    "always_7": rig_always_total_7,
    "never_2_or_12": rig_never_total_2_or_12,
    "every_5th_is_7": rig_every_5th_roll_is_7,
    "after_8_then_9": rig_after_8_then_9,
}


def pick_secret_rig_rule():
    """Randomly choose a rig rule key and return (key, function)."""
    key = random.choice(list(RIG_RULES.keys()))
    return key, RIG_RULES[key]


def rigged_roll(history, roll_num, rig_func):
    """Produce a roll using the selected rig function."""
    return rig_func(history, roll_num)


# ----------------------------
# Betting / payout logic
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

    # Special rule: snake eyes
    if d1 == 1 and d2 == 1:
        return 5, "Snake eyes! Special 5x payout!"

    if bet_type == "sum":
        if total == bet_value:
            hard_sums = {2, 3, 11, 12}
            if total in hard_sums:
                return 4, "You hit a hard sum! 4x payout."
            return 3, "You hit the sum! 3x payout."
        return 0, "Missed the sum."

    if bet_type == "parity":
        parity = "even" if total % 2 == 0 else "odd"
        if parity == bet_value:
            return 2, "Correct parity! 2x payout."
        return 0, "Wrong parity."

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
    """Print the last few rolls so the player can try to spot the rig."""
    if not history:
        print("No roll history yet.")
        return

    print("\nRecent rolls (most recent last):")
    start = max(0, len(history) - MAX_HISTORY_TO_SHOW)
    for i in range(start, len(history)):
        h = history[i]
        print(f"  Roll {i+1}: {h['d1']} + {h['d2']} = {h['total']}")


def choose_bet(balance):
    """
    Ask the user for wager + bet type + bet value.
    Returns (wager, bet_type, bet_value).
    """
    wager = get_int(f"Enter wager (1 - {balance}): ", min_val=1, max_val=balance)

    print("\nChoose a bet type:")
    print("1) sum     (bet the total of both dice: 2-12)")
    print("2) parity  (bet odd or even)")
    print("3) highlow (bet high (8-12) or low (2-6); 7 loses)")
    bet_menu = get_choice("Type 1, 2, or 3: ", ["1", "2", "3"])

    if bet_menu == "1":
        bet_type = "sum"
        bet_value = get_int("Pick a sum (2-12): ", min_val=2, max_val=12)
    elif bet_menu == "2":
        bet_type = "parity"
        bet_value = get_choice("Pick odd or even: ", ["odd", "even"])
    else:
        bet_type = "highlow"
        bet_value = get_choice("Pick high or low: ", ["high", "low"])

    return wager, bet_type, bet_value


def guess_rig_rule():
    """
    Let the player guess the hidden rig rule.
    Returns guessed key (string).
    """
    print("\nGuess the rig rule!")
    print("Options:")
    for k in RIG_RULES.keys():
        print(f" - {k}")
    guess = get_choice("Type your guess exactly: ", list(RIG_RULES.keys()))
    return guess


# ----------------------------
# Main game loop
# ----------------------------

def main():
    print("Welcome to the Dice Betting + Rig Deduction Game!")
    print(f"Starting balance: ${STARTING_BALANCE}")
    print("Special rule: If you roll snake eyes (1 and 1), you win 5x your wager.")
    print("Twist: The dice are rigged in a secret way. Try to deduce the rig rule!\n")

    balance = STARTING_BALANCE
    history = []
    roll_num = 0

    secret_key, rig_func = pick_secret_rig_rule()
    # NOTE: In the final game, we keep this secret.
    # For debugging, you can temporarily print it:
    # print(f"[DEBUG] Secret rig rule is: {secret_key}")

    while True:
        if balance <= 0:
            print("You're out of money. Game over.")
            print(f"The rig rule was: {secret_key}")
            break

        print(f"\nCurrent balance: ${balance}")
        print_history(history)

        action = get_choice("\nChoose an action: (p)lay round, (g)uess rig, (q)uit: ", ["p", "g", "q"])
        if action == "q":
            print("Thanks for playing!")
            print(f"The rig rule was: {secret_key}")
            break

        if action == "g":
            guess = guess_rig_rule()
            if guess == secret_key:
                print("\nCorrect! You deduced the rig rule!")
                print(f"Final balance: ${balance}")
                break
            else:
                # Light penalty so guessing randomly isn't free
                penalty = min(5, balance)
                balance -= penalty
                print(f"\nWrong guess. You lose ${penalty} for guessing incorrectly.")
            continue

        # action == "p": play a betting round
        wager, bet_type, bet_value = choose_bet(balance)

        roll_num += 1
        d1, d2 = rigged_roll(history, roll_num, rig_func)
        total = d1 + d2

        print(f"\nYou rolled: {d1} and {d2} (sum = {total})")

        # Save history for deduction
        history.append({"d1": d1, "d2": d2, "total": total})

        multiplier, message = compute_payout_multiplier(bet_type, bet_value, d1, d2)
        print(message)

        if multiplier > 0:
            winnings = wager * multiplier
            balance += winnings
            print(f"You WON ${winnings}!")
        else:
            balance -= wager
            print(f"You LOST ${wager}.")

    print("\nGame ended.")


if __name__ == "__main__":
    main()