import random

STARTING_BALANCE = 100
MAX_HISTORY_TO_SHOW = 10
HOUSE_EDGE = 0.05
MAX_PAYOUT_MULTIPLIER = 12
SNAKE_EYES_MULTIPLIER = 5


def get_int(prompt, min_val=None, max_val=None):
    while True:
        s = input(prompt).strip()
        try:
            value = int(s)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if min_val is not None and value < min_val:
            print(f"Please enter a number greater than or equal to {min_val}.")
            continue

        if max_val is not None and value > max_val:
            print(f"Please enter a number less than or equal to {max_val}.")
            continue

        return value


def get_choice(prompt, choices):
    valid = {choice.lower() for choice in choices}
    while True:
        s = input(prompt).strip().lower()
        if s in valid:
            return s
        print(f"Please choose one of: {', '.join(choices)}")


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
    return len(all_pairs_for_total(total)) / 36.0


def fair_probability_parity(choice):
    count = 0
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            total = d1 + d2
            if choice == "odd" and total % 2 == 1:
                count += 1
            elif choice == "even" and total % 2 == 0:
                count += 1
    return count / 36.0


def fair_probability_highlow(choice):
    count = 0
    for d1 in range(1, 7):
        for d2 in range(1, 7):
            total = d1 + d2
            if total == 7:
                continue
            if choice == "high" and total > 7:
                count += 1
            elif choice == "low" and total < 7:
                count += 1
    return count / 36.0


def bet_win_probability(bet_type, bet_value):
    if bet_type == "sum":
        return fair_probability_sum(bet_value)
    if bet_type == "parity":
        return fair_probability_parity(bet_value)
    if bet_type == "highlow":
        return fair_probability_highlow(bet_value)
    return 0.0


def payout_multiplier_from_probability(probability):
    if probability <= 0:
        return 0.0

    multiplier = (1.0 - HOUSE_EDGE) / probability
    multiplier = min(multiplier, MAX_PAYOUT_MULTIPLIER)
    multiplier = max(multiplier, 1.0)
    return round(multiplier, 2)


def did_win_bet(bet_type, bet_value, d1, d2):
    total = d1 + d2

    if bet_type == "sum":
        return total == bet_value

    if bet_type == "parity":
        actual = "even" if total % 2 == 0 else "odd"
        return actual == bet_value

    if bet_type == "highlow":
        if total == 7:
            return False
        actual = "high" if total > 7 else "low"
        return actual == bet_value

    return False


def compute_round_result(wager, bet_type, bet_value, d1, d2):
    total = d1 + d2
    lines = [f"You rolled {d1} + {d2} = {total}."]

    if d1 == 1 and d2 == 1:
        winnings = int(wager * SNAKE_EYES_MULTIPLIER)
        lines.append(f"Snake eyes! Automatic {SNAKE_EYES_MULTIPLIER}x payout.")
        lines.append(f"You win ${winnings}.")
        return winnings, lines

    if did_win_bet(bet_type, bet_value, d1, d2):
        probability = bet_win_probability(bet_type, bet_value)
        multiplier = payout_multiplier_from_probability(probability)
        winnings = int(wager * multiplier)
        lines.append(f"You won the bet. Payout multiplier: {multiplier}x.")
        lines.append(f"You win ${winnings}.")
        return winnings, lines

    lines.append(f"You lose ${wager}.")
    return -wager, lines


def make_rig_always_force_total(forced_total):
    def rig_function(history, roll_number):
        return roll_with_forced_total(forced_total)
    return rig_function


def make_rig_never_allow_totals(blocked_totals):
    blocked_totals = set(blocked_totals)

    def rig_function(history, roll_number):
        for _ in range(50):
            d1, d2 = roll_two_dice_fair()
            if (d1 + d2) not in blocked_totals:
                return d1, d2
        return roll_two_dice_fair()

    return rig_function


def make_rig_force_total_every_nth_roll(n, forced_total):
    def rig_function(history, roll_number):
        if roll_number % n == 0:
            return roll_with_forced_total(forced_total)
        return roll_two_dice_fair()
    return rig_function


def make_rig_force_total_after_trigger_total(trigger_total, forced_total):
    def rig_function(history, roll_number):
        if history and history[-1]["total"] == trigger_total:
            return roll_with_forced_total(forced_total)
        return roll_two_dice_fair()
    return rig_function


def build_random_rig_rule():
    option = random.choice(["always", "never", "every_n", "after_trigger"])

    if option == "always":
        forced_total = random.randint(2, 12)
        rule_code = f"always_force_total_{forced_total}"
        rule_description = f"Always force the dice to total {forced_total}"
        rig_function = make_rig_always_force_total(forced_total)
        return rule_code, rule_description, rig_function

    if option == "never":
        blocked_count = random.randint(1, 2)
        blocked = sorted(random.sample(range(2, 13), blocked_count))
        rule_code = "never_allow_totals_" + "_".join(str(x) for x in blocked)
        rule_description = "Never allow totals " + ", ".join(str(x) for x in blocked)
        rig_function = make_rig_never_allow_totals(blocked)
        return rule_code, rule_description, rig_function

    if option == "every_n":
        n = random.randint(2, 6)
        forced_total = random.randint(2, 12)
        rule_code = f"force_total_{forced_total}_every_{n}th_roll"
        rule_description = f"Force total {forced_total} every {n}th roll"
        rig_function = make_rig_force_total_every_nth_roll(n, forced_total)
        return rule_code, rule_description, rig_function

    trigger_total = random.randint(2, 12)
    forced_total = random.randint(2, 12)
    rule_code = f"force_total_{forced_total}_after_total_{trigger_total}"
    rule_description = f"Force total {forced_total} after a roll totaling {trigger_total}"
    rig_function = make_rig_force_total_after_trigger_total(trigger_total, forced_total)
    return rule_code, rule_description, rig_function


def build_custom_rig_rule():
    print("\nBuild a custom rig rule.")
    print("Choose a rig pattern:")
    print("1) Always force the same total")
    print("2) Never allow certain totals")
    print("3) Force a total every Nth roll")
    print("4) Force a total after another total appears")

    choice = get_choice("Enter 1, 2, 3, or 4: ", ["1", "2", "3", "4"])

    if choice == "1":
        forced_total = get_int("Enter the total to always force (2-12): ", 2, 12)
        rule_code = f"always_force_total_{forced_total}"
        rule_description = f"Always force the dice to total {forced_total}"
        rig_function = make_rig_always_force_total(forced_total)
        return rule_code, rule_description, rig_function

    if choice == "2":
        blocked_count = get_int("How many totals do you want to block? (1-4): ", 1, 4)
        blocked = []
        for i in range(blocked_count):
            total = get_int(f"Enter blocked total #{i+1} (2-12): ", 2, 12)
            if total not in blocked:
                blocked.append(total)

        blocked.sort()
        rule_code = "never_allow_totals_" + "_".join(str(x) for x in blocked)
        rule_description = "Never allow totals " + ", ".join(str(x) for x in blocked)
        rig_function = make_rig_never_allow_totals(blocked)
        return rule_code, rule_description, rig_function

    if choice == "3":
        n = get_int("Force a total every how many rolls? (2-10): ", 2, 10)
        forced_total = get_int("Enter the total to force (2-12): ", 2, 12)
        rule_code = f"force_total_{forced_total}_every_{n}th_roll"
        rule_description = f"Force total {forced_total} every {n}th roll"
        rig_function = make_rig_force_total_every_nth_roll(n, forced_total)
        return rule_code, rule_description, rig_function

    trigger_total = get_int("If the previous roll totals what number? (2-12): ", 2, 12)
    forced_total = get_int("Then force what total next? (2-12): ", 2, 12)
    rule_code = f"force_total_{forced_total}_after_total_{trigger_total}"
    rule_description = f"Force total {forced_total} after a roll totaling {trigger_total}"
    rig_function = make_rig_force_total_after_trigger_total(trigger_total, forced_total)
    return rule_code, rule_description, rig_function


def print_header():
    print("\n" + "=" * 60)
    print("               DICE BETTING: RIG DEDUCTION")
    print("=" * 60)
    print("Build your bankroll, study the roll history, and identify")
    print("the hidden rig rule controlling the dice.\n")


def print_rules():
    print("HOW THE GAME WORKS")
    print("- You begin with a bankroll and can place bets on each roll.")
    print("- The dice are secretly rigged by one hidden rule.")
    print("- The rig changes how the dice are rolled.")
    print("- The rig never depends on your wager or your bet type.")
    print("- If you correctly guess the rig rule, you win immediately.\n")

    print("BET TYPES")
    print("1) Sum Bet")
    print("   Pick an exact total from 2 to 12.")
    print("   You win if the dice add to that total.\n")

    print("2) Odd/Even Bet")
    print("   Pick odd or even.")
    print("   You win if the total matches your choice.\n")

    print("3) High/Low Bet")
    print("   Pick high or low.")
    print("   High means totals 8 through 12.")
    print("   Low means totals 2 through 6.")
    print("   A total of 7 always loses this bet.\n")

    print("PAYOUTS")
    print("- Payouts are based on probability, not fixed hard-coded values.")
    print("- Harder bets pay more.")
    print(f"- Maximum payout multiplier: {MAX_PAYOUT_MULTIPLIER}x")
    print(f"- Snake eyes (1 and 1) always pays {SNAKE_EYES_MULTIPLIER}x.\n")


def print_history(history):
    if not history:
        print("Roll history: none yet")
        return

    print("Recent roll history:")
    start = max(0, len(history) - MAX_HISTORY_TO_SHOW)
    for i in range(start, len(history)):
        roll = history[i]
        print(f"  Roll {i+1}: {roll['d1']} + {roll['d2']} = {roll['total']}")


def choose_bet(balance):
    print("\nChoose your bet:")
    print("1) Sum Bet")
    print("2) Odd/Even Bet")
    print("3) High/Low Bet")

    choice = get_choice("Enter 1, 2, or 3: ", ["1", "2", "3"])
    wager = get_int(f"Enter your wager (1-{balance}): ", 1, balance)

    if choice == "1":
        bet_type = "sum"
        bet_value = get_int("Enter a target total (2-12): ", 2, 12)
    elif choice == "2":
        bet_type = "parity"
        bet_value = get_choice("Choose odd or even: ", ["odd", "even"])
    else:
        bet_type = "highlow"
        bet_value = get_choice("Choose high or low: ", ["high", "low"])

    probability = bet_win_probability(bet_type, bet_value)
    estimated_multiplier = payout_multiplier_from_probability(probability)
    print(f"Estimated payout if you win: about {estimated_multiplier}x")

    return wager, bet_type, bet_value


def choose_rig_creation_mode():
    print("How should the secret rig rule be created?")
    print("1) Randomly generate a rig rule")
    print("2) Build a custom rig rule")

    choice = get_choice("Enter 1 or 2: ", ["1", "2"])

    if choice == "1":
        return build_random_rig_rule()
    return build_custom_rig_rule()


def main():
    print_header()
    print_rules()

    balance = STARTING_BALANCE
    history = []
    roll_number = 0

    secret_rule_code, secret_rule_description, rig_function = choose_rig_creation_mode()

    while True:
        if balance <= 0:
            print("\nYou are out of money. Game over.")
            print("The secret rig rule was:")
            print(secret_rule_description)
            break

        print("\n" + "-" * 60)
        print(f"Current balance: ${balance}")
        print_history(history)

        print("\nChoose an action:")
        print("1) Play a round")
        print("2) Guess the rig rule")
        print("3) Quit")

        action = get_choice("Enter 1, 2, or 3: ", ["1", "2", "3"])

        if action == "3":
            print("\nYou ended the game.")
            print("The secret rig rule was:")
            print(secret_rule_description)
            break

        elif action == "2":
            print("\nEnter your guess for how the rig works.")
            print("Examples:")
            print("- Always force the dice to total 5")
            print("- Never allow totals 2 and 12")
            print("- Force total 7 every 3rd roll")
            print("- Force total 9 after a roll totaling 8")

            guess = input("\nYour guess: ").strip().lower()

            correct_answers = [
                secret_rule_code.lower(),
                secret_rule_description.lower(),
                secret_rule_description.lower().replace(".", "")
            ]

            if guess in correct_answers:
                print("\nCorrect! You identified the secret rig rule.")
                print(f"You win with a final balance of ${balance}.")
                return
            else:
                penalty = min(5, balance)
                balance -= penalty
                print(f"\nIncorrect guess. You lose a ${penalty} penalty.")
                print("Study the roll history and try again.")
                continue

        else:
            wager, bet_type, bet_value = choose_bet(balance)

            roll_number += 1
            d1, d2 = rig_function(history, roll_number)
            total = d1 + d2

            history.append({
                "d1": d1,
                "d2": d2,
                "total": total
            })

            balance_change, result_lines = compute_round_result(wager, bet_type, bet_value, d1, d2)

            for line in result_lines:
                print(line)

            balance += balance_change

    print("\nGame ended.")


if __name__ == "__main__":
    main()