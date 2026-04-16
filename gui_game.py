import random
import tkinter as tk
from tkinter import ttk, messagebox

STARTING_BALANCE = 100
MAX_HISTORY_TO_SHOW = 10
HOUSE_EDGE = 0.05
MAX_PAYOUT_MULTIPLIER = 12
SNAKE_EYES_MULTIPLIER = 5

DICE_ART = {
    1: [
        "+-------+",
        "|       |",
        "|   *   |",
        "|       |",
        "+-------+"
    ],
    2: [
        "+-------+",
        "| *     |",
        "|       |",
        "|     * |",
        "+-------+"
    ],
    3: [
        "+-------+",
        "| *     |",
        "|   *   |",
        "|     * |",
        "+-------+"
    ],
    4: [
        "+-------+",
        "| *   * |",
        "|       |",
        "| *   * |",
        "+-------+"
    ],
    5: [
        "+-------+",
        "| *   * |",
        "|   *   |",
        "| *   * |",
        "+-------+"
    ],
    6: [
        "+-------+",
        "| *   * |",
        "| *   * |",
        "| *   * |",
        "+-------+"
    ]
}


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
        return fair_probability_sum(int(bet_value))
    if bet_type == "odd/even":
        return fair_probability_parity(bet_value)
    if bet_type == "high/low":
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
        return total == int(bet_value)

    if bet_type == "odd/even":
        actual = "even" if total % 2 == 0 else "odd"
        return actual == bet_value

    if bet_type == "high/low":
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


def build_custom_rig_rule(rule_type, a, b=None):
    if rule_type == "Always force a total":
        forced_total = int(a)
        rule_code = f"always_force_total_{forced_total}"
        rule_description = f"Always force the dice to total {forced_total}"
        rig_function = make_rig_always_force_total(forced_total)
        return rule_code, rule_description, rig_function

    if rule_type == "Never allow certain totals":
        blocked = sorted(set(int(x.strip()) for x in a.split(",") if x.strip()))
        rule_code = "never_allow_totals_" + "_".join(str(x) for x in blocked)
        rule_description = "Never allow totals " + ", ".join(str(x) for x in blocked)
        rig_function = make_rig_never_allow_totals(blocked)
        return rule_code, rule_description, rig_function

    if rule_type == "Force a total every N rolls":
        forced_total = int(a)
        n = int(b)
        rule_code = f"force_total_{forced_total}_every_{n}th_roll"
        rule_description = f"Force total {forced_total} every {n}th roll"
        rig_function = make_rig_force_total_every_nth_roll(n, forced_total)
        return rule_code, rule_description, rig_function

    trigger_total = int(a)
    forced_total = int(b)
    rule_code = f"force_total_{forced_total}_after_total_{trigger_total}"
    rule_description = f"Force total {forced_total} after a roll totaling {trigger_total}"
    rig_function = make_rig_force_total_after_trigger_total(trigger_total, forced_total)
    return rule_code, rule_description, rig_function


class DiceGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dice Betting: Rig Deduction")
        self.root.geometry("1050x800")
        self.root.configure(bg="#f4f6f8")

        self.balance = STARTING_BALANCE
        self.history = []
        self.roll_number = 0
        self.secret_rule_code = ""
        self.secret_rule_description = ""
        self.rig_function = None
        self.game_over = False

        self.build_widgets()
        self.setup_rig_rule()

    def build_widgets(self):
        title = tk.Label(
            self.root,
            text="Dice Betting: Rig Deduction",
            font=("Helvetica", 24, "bold"),
            bg="#f4f6f8",
            fg="#1f2937"
        )
        title.pack(pady=(15, 5))

        subtitle = tk.Label(
            self.root,
            text="Build your bankroll, watch the dice, and figure out the hidden rig rule.",
            font=("Helvetica", 12),
            bg="#f4f6f8",
            fg="#4b5563"
        )
        subtitle.pack()

        self.balance_label = tk.Label(
            self.root,
            text=f"Current Balance: ${self.balance}",
            font=("Helvetica", 16, "bold"),
            bg="#f4f6f8",
            fg="#111827"
        )
        self.balance_label.pack(pady=12)

        main_frame = tk.Frame(self.root, bg="#f4f6f8")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_col = tk.Frame(main_frame, bg="#f4f6f8")
        left_col.pack(side="left", fill="y", padx=(0, 15))

        center_col = tk.Frame(main_frame, bg="#f4f6f8")
        center_col.pack(side="left", fill="both", expand=True, padx=15)

        right_col = tk.Frame(main_frame, bg="#f4f6f8")
        right_col.pack(side="right", fill="y", padx=(15, 0))

        how_frame = tk.LabelFrame(
            left_col,
            text="How to Play",
            padx=12,
            pady=12,
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="#111827"
        )
        how_frame.pack(fill="x", pady=(0, 15))

        how_text = (
            "1. Choose a bet type.\n"
            "2. Enter your bet value.\n"
            "3. Enter your wager.\n"
            "4. Click Play Round.\n"
            "5. Study the roll history.\n"
            "6. Guess the hidden rig rule when ready.\n\n"
            "Bet types:\n"
            "• Sum: pick a total from 2 to 12\n"
            "• Odd/Even: pick odd or even\n"
            "• High/Low: high = 8-12, low = 2-6\n"
            "• A total of 7 loses High/Low"
        )
        tk.Label(
            how_frame,
            text=how_text,
            justify="left",
            anchor="w",
            bg="white",
            fg="#374151",
            font=("Helvetica", 10)
        ).pack(fill="x")

        bet_frame = tk.LabelFrame(
            left_col,
            text="Place Your Bet",
            padx=12,
            pady=12,
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="#111827"
        )
        bet_frame.pack(fill="x")

        tk.Label(bet_frame, text="Bet Type", bg="white", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.bet_type_var = tk.StringVar(value="sum")
        self.bet_type_menu = ttk.Combobox(
            bet_frame,
            textvariable=self.bet_type_var,
            values=["sum", "odd/even", "high/low"],
            state="readonly",
            width=18
        )
        self.bet_type_menu.pack(fill="x", pady=(4, 10))
        self.bet_type_menu.bind("<<ComboboxSelected>>", self.update_bet_hint)

        tk.Label(bet_frame, text="Bet Value", bg="white", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.bet_value_entry = tk.Entry(bet_frame, width=20, font=("Helvetica", 11))
        self.bet_value_entry.pack(fill="x", pady=(4, 4))

        self.bet_hint_label = tk.Label(
            bet_frame,
            text="Enter a number from 2 to 12",
            bg="white",
            fg="#6b7280",
            font=("Helvetica", 9)
        )
        self.bet_hint_label.pack(anchor="w", pady=(0, 10))

        tk.Label(bet_frame, text="Wager", bg="white", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.wager_entry = tk.Entry(bet_frame, width=20, font=("Helvetica", 11))
        self.wager_entry.pack(fill="x", pady=(4, 8))

        self.payout_label = tk.Label(
            bet_frame,
            text="Estimated payout: -",
            bg="white",
            fg="#374151",
            font=("Helvetica", 10)
        )
        self.payout_label.pack(anchor="w", pady=(6, 10))

        tk.Button(
            bet_frame,
            text="Estimate Payout",
            command=self.estimate_payout,
            width=18,
            bg="#dbeafe",
            relief="flat"
        ).pack(pady=4)

        tk.Button(
            bet_frame,
            text="Play Round",
            command=self.play_round,
            width=18,
            bg="#bfdbfe",
            relief="flat"
        ).pack(pady=6)

        dice_frame = tk.LabelFrame(
            center_col,
            text="Dice",
            padx=15,
            pady=15,
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="#111827"
        )
        dice_frame.pack(fill="x", pady=(0, 15))

        self.dice_art_label = tk.Label(
            dice_frame,
            text="",
            font=("Courier", 15),
            justify="left",
            bg="white",
            fg="#111827"
        )
        self.dice_art_label.pack()

        result_frame = tk.LabelFrame(
            center_col,
            text="Round Result",
            padx=10,
            pady=10,
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="#111827"
        )
        result_frame.pack(fill="both", expand=False, pady=(0, 15))

        self.result_text = tk.Text(
            result_frame,
            height=8,
            width=55,
            font=("Courier", 11),
            bg="#f9fafb"
        )
        self.result_text.pack(fill="both", expand=True)

        history_frame = tk.LabelFrame(
            center_col,
            text="Recent Roll History",
            padx=10,
            pady=10,
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="#111827"
        )
        history_frame.pack(fill="both", expand=True)

        self.history_text = tk.Text(
            history_frame,
            height=16,
            width=55,
            font=("Courier", 11),
            bg="#f9fafb"
        )
        self.history_text.pack(fill="both", expand=True)

        guess_frame = tk.LabelFrame(
            right_col,
            text="Guess the Hidden Rig Rule",
            padx=12,
            pady=12,
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg="#111827"
        )
        guess_frame.pack(fill="x")

        guess_instructions = (
            "Use the roll history to figure out how the dice are rigged.\n"
            "Possible rule types are shown below.\n"
            "Type your guess in plain English."
        )
        tk.Label(
            guess_frame,
            text=guess_instructions,
            justify="left",
            bg="white",
            fg="#374151",
            font=("Helvetica", 10)
        ).pack(anchor="w", pady=(0, 10))

        rig_options_text = (
            "Possible rig rule formats:\n"
            "• Always force the dice to total X\n"
            "• Never allow totals A, B, ...\n"
            "• Force total X every Nth roll\n"
            "• Force total X after a roll totaling Y"
        )
        tk.Label(
            guess_frame,
            text=rig_options_text,
            justify="left",
            bg="#f9fafb",
            fg="#1f2937",
            font=("Helvetica", 10),
            relief="solid",
            bd=1,
            padx=8,
            pady=8
        ).pack(fill="x", pady=(0, 12))

        tk.Label(guess_frame, text="Your Guess", bg="white", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.guess_entry = tk.Entry(guess_frame, width=30, font=("Helvetica", 11))
        self.guess_entry.pack(fill="x", pady=(4, 4))

        tk.Label(
            guess_frame,
            text="Example: Always force the dice to total 10",
            bg="white",
            fg="#6b7280",
            font=("Helvetica", 9)
        ).pack(anchor="w", pady=(0, 10))

        tk.Button(
            guess_frame,
            text="Submit Guess",
            command=self.submit_guess,
            width=18,
            bg="#dcfce7",
            relief="flat"
        ).pack(pady=4)

        tk.Button(
            guess_frame,
            text="Quit / Reveal Rule",
            command=self.quit_game,
            width=18,
            bg="#fee2e2",
            relief="flat"
        ).pack(pady=6)

        self.update_bet_hint()
        self.update_ascii_dice(1, 1)

    def get_combined_dice_art(self, d1, d2):
        die1 = DICE_ART[d1]
        die2 = DICE_ART[d2]
        combined = []
        for line1, line2 in zip(die1, die2):
            combined.append(line1 + "   " + line2)
        return "\n".join(combined)

    def update_ascii_dice(self, d1, d2):
        self.dice_art_label.config(text=self.get_combined_dice_art(d1, d2))

    def setup_rig_rule(self):
        custom = messagebox.askyesno(
            "Rig Rule Setup",
            "Would you like to build your own hidden rig rule?\n\n"
            "Click Yes for a custom rule.\n"
            "Click No for a randomly generated rule."
        )

        if not custom:
            self.secret_rule_code, self.secret_rule_description, self.rig_function = build_random_rig_rule()
            self.write_result("A random hidden rig rule has been created.\n")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Build Custom Rig Rule")
        popup.geometry("500x420")
        popup.configure(bg="#f4f6f8")
        popup.grab_set()

        tk.Label(
            popup,
            text="Build Custom Rig Rule",
            font=("Helvetica", 16, "bold"),
            bg="#f4f6f8"
        ).pack(pady=(15, 10))

        tk.Label(
            popup,
            text="Choose how the dice should be secretly rigged.",
            bg="#f4f6f8",
            fg="#4b5563",
            font=("Helvetica", 10)
        ).pack()

        form = tk.Frame(popup, bg="#f4f6f8")
        form.pack(pady=15, padx=20, fill="both", expand=True)

        tk.Label(form, text="Rig Pattern", bg="#f4f6f8", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.rule_type_var = tk.StringVar(value="Always force a total")
        rule_menu = ttk.Combobox(
            form,
            textvariable=self.rule_type_var,
            values=[
                "Always force a total",
                "Never allow certain totals",
                "Force a total every N rolls",
                "Force a total after another total"
            ],
            state="readonly",
            width=30
        )
        rule_menu.pack(fill="x", pady=(4, 12))

        tk.Label(form, text="Primary Value", bg="#f4f6f8", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.rule_a_entry = tk.Entry(form, font=("Helvetica", 11))
        self.rule_a_entry.pack(fill="x", pady=(4, 4))

        self.rule_a_hint = tk.Label(form, text="", bg="#f4f6f8", fg="#6b7280", font=("Helvetica", 9))
        self.rule_a_hint.pack(anchor="w", pady=(0, 10))

        tk.Label(form, text="Secondary Value (if needed)", bg="#f4f6f8", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.rule_b_entry = tk.Entry(form, font=("Helvetica", 11))
        self.rule_b_entry.pack(fill="x", pady=(4, 4))

        self.rule_b_hint = tk.Label(form, text="", bg="#f4f6f8", fg="#6b7280", font=("Helvetica", 9))
        self.rule_b_hint.pack(anchor="w", pady=(0, 10))

        self.rule_example = tk.Label(form, text="", bg="#f4f6f8", fg="#374151", font=("Helvetica", 10))
        self.rule_example.pack(anchor="w", pady=(10, 15))

        def refresh_hints(*args):
            rule_type = self.rule_type_var.get()

            if rule_type == "Always force a total":
                self.rule_a_hint.config(text="Enter one total from 2 to 12")
                self.rule_b_hint.config(text="Leave this blank")
                self.rule_example.config(text="Example: Always force the dice to total 7")

            elif rule_type == "Never allow certain totals":
                self.rule_a_hint.config(text="Enter totals separated by commas, such as 2,12")
                self.rule_b_hint.config(text="Leave this blank")
                self.rule_example.config(text="Example: Never allow totals 2 and 12")

            elif rule_type == "Force a total every N rolls":
                self.rule_a_hint.config(text="Primary: total to force (2-12)")
                self.rule_b_hint.config(text="Secondary: N, meaning every how many rolls")
                self.rule_example.config(text="Example: Force total 8 every 4 rolls")

            else:
                self.rule_a_hint.config(text="Primary: trigger total (2-12)")
                self.rule_b_hint.config(text="Secondary: forced total (2-12)")
                self.rule_example.config(text="Example: If a roll totals 5, force total 9 next")

        self.rule_type_var.trace_add("write", refresh_hints)
        refresh_hints()

        def create_rule():
            try:
                self.secret_rule_code, self.secret_rule_description, self.rig_function = build_custom_rig_rule(
                    self.rule_type_var.get(),
                    self.rule_a_entry.get(),
                    self.rule_b_entry.get()
                )
                self.write_result("A custom hidden rig rule has been created.\n")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Invalid Rule", f"Could not create rule:\n{e}")

        tk.Button(
            popup,
            text="Create Rule",
            command=create_rule,
            width=18,
            bg="#bfdbfe",
            relief="flat"
        ).pack(pady=10)

    def update_bet_hint(self, event=None):
        bet_type = self.bet_type_var.get()

        if bet_type == "sum":
            self.bet_hint_label.config(text="Enter a total from 2 to 12")
        elif bet_type == "odd/even":
            self.bet_hint_label.config(text="Enter odd or even")
        else:
            self.bet_hint_label.config(text="Enter high or low")

    def estimate_payout(self):
        if self.game_over:
            return

        try:
            bet_type = self.bet_type_var.get()
            bet_value = self.bet_value_entry.get().strip().lower()

            if bet_type == "sum":
                bet_value = int(bet_value)

            probability = bet_win_probability(bet_type, bet_value)
            multiplier = payout_multiplier_from_probability(probability)
            self.payout_label.config(text=f"Estimated payout: about {multiplier}x")
        except Exception:
            self.payout_label.config(text="Estimated payout: invalid bet")

    def end_game(self, title, popup_text, result_text, is_error=False):
        self.game_over = True
        self.write_result(result_text)

        if is_error:
            messagebox.showerror(title, popup_text)
        else:
            messagebox.showinfo(title, popup_text)

        self.root.after(1200, self.root.destroy)

    def play_round(self):
        if self.game_over:
            return

        if self.rig_function is None:
            messagebox.showerror("No Rig Rule", "No rig rule has been created yet.")
            return

        try:
            wager = int(self.wager_entry.get().strip())
        except Exception:
            messagebox.showerror("Invalid Wager", "Please enter a valid whole-number wager.")
            return

        if wager < 1 or wager > self.balance:
            messagebox.showerror("Invalid Wager", f"Wager must be between 1 and {self.balance}.")
            return

        bet_type = self.bet_type_var.get()
        bet_value = self.bet_value_entry.get().strip().lower()

        try:
            if bet_type == "sum":
                bet_value = int(bet_value)
                if bet_value < 2 or bet_value > 12:
                    raise ValueError
            elif bet_type == "odd/even":
                if bet_value not in ["odd", "even"]:
                    raise ValueError
            elif bet_type == "high/low":
                if bet_value not in ["high", "low"]:
                    raise ValueError
        except Exception:
            messagebox.showerror("Invalid Bet", "Please enter a valid value for the chosen bet type.")
            return

        self.roll_number += 1
        d1, d2 = self.rig_function(self.history, self.roll_number)
        self.update_ascii_dice(d1, d2)

        self.history.append({"d1": d1, "d2": d2, "total": d1 + d2})

        balance_change, result_lines = compute_round_result(wager, bet_type, bet_value, d1, d2)
        self.balance += balance_change
        self.balance_label.config(text=f"Current Balance: ${self.balance}")

        self.write_result("\n".join(result_lines))
        self.refresh_history()

        if self.balance <= 0:
            self.end_game(
                "Game Over",
                "💸 You ran out of money. 💸\n\n"
                "The hidden rig rule beat you this time.\n"
                "The game will now close.\n\n"
                f"Hidden rig rule:\n{self.secret_rule_description}",
                "GAME OVER\n\n"
                "You ran out of money.\n"
                "The hidden rig rule outplayed you.\n\n"
                f"Hidden rig rule: {self.secret_rule_description}\n\n"
                "Closing game...",
                is_error=True
            )

    def submit_guess(self):
        if self.game_over:
            return

        guess = self.guess_entry.get().strip().lower()

        if not guess:
            messagebox.showerror("Empty Guess", "Please type a guess before submitting.")
            return

        correct_answers = [
            self.secret_rule_code.lower(),
            self.secret_rule_description.lower(),
            self.secret_rule_description.lower().replace(".", "")
        ]

        if guess in correct_answers:
            self.end_game(
                "You Win!",
                "🎉 Congratulations! 🎉\n\n"
                "You correctly identified the hidden rig rule.\n"
                "Your deduction paid off.\n\n"
                f"Final balance: ${self.balance}\n\n"
                "The game will now close.",
                "YOU WIN\n\n"
                "You correctly identified the hidden rig rule.\n"
                "Excellent deduction.\n\n"
                f"Final balance: ${self.balance}\n\n"
                "Closing game..."
            )
        else:
            penalty = min(5, self.balance)
            self.balance -= penalty
            self.balance_label.config(text=f"Current Balance: ${self.balance}")
            self.write_result(f"Incorrect guess. Penalty: -${penalty}")

            if self.balance <= 0:
                self.end_game(
                    "Game Over",
                    "💸 You ran out of money. 💸\n\n"
                    "Too many wrong guesses and bad bets cost you the game.\n\n"
                    f"Hidden rig rule:\n{self.secret_rule_description}\n\n"
                    "The game will now close.",
                    "GAME OVER\n\n"
                    "You ran out of money after an incorrect guess.\n\n"
                    f"Hidden rig rule: {self.secret_rule_description}\n\n"
                    "Closing game...",
                    is_error=True
                )

    def quit_game(self):
        if self.game_over:
            return

        self.end_game(
            "Game Ended",
            "You chose to quit the game.\n\n"
            f"Hidden rig rule:\n{self.secret_rule_description}\n\n"
            "The game will now close.",
            "GAME ENDED\n\n"
            "You chose to quit.\n\n"
            f"Hidden rig rule: {self.secret_rule_description}\n\n"
            "Closing game..."
        )

    def write_result(self, text):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)

    def refresh_history(self):
        self.history_text.delete("1.0", tk.END)
        self.history_text.insert(tk.END, "Recent Roll History\n")
        self.history_text.insert(tk.END, "-" * 38 + "\n")
        self.history_text.insert(tk.END, f"{'Roll':<6}{'Dice':<10}{'Total':<8}\n")
        self.history_text.insert(tk.END, "-" * 38 + "\n")

        start = max(0, len(self.history) - MAX_HISTORY_TO_SHOW)
        for i in range(start, len(self.history)):
            roll = self.history[i]
            dice_text = f"{roll['d1']} + {roll['d2']}"
            self.history_text.insert(
                tk.END,
                f"{i+1:<6}{dice_text:<10}{roll['total']:<8}\n"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = DiceGameGUI(root)
    root.mainloop()