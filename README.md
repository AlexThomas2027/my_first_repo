Alex Thomas and Liv MacMillan

Dice Betting Game

Overview

This project is a dice betting game in which the player bets on the outcomes of two dice rolls. The main twist is that a hidden rule secretly rigs the dice, and the player must figure out what that rule is to win.

There are two versions of the game:
- `main.py` → command-line version
- `gui_game.py` → graphical version 

---

How the Game Works

You start with a set amount of money and play rounds of betting.

Each round:
1. Choose a bet type
2. Enter a bet value
3. Enter your wager
4. Play the round

After each roll, your balance updates, and the result is added to a **roll history**.

Your goal is to:
- Make money through betting
- Watch for patterns in the dice
- Guess the hidden rig rule before running out of money

---

Bet Types

- Sum → pick a number from 2–12  
- Odd/Even → choose odd or even  
- Hgh/Low 
  - Low = 2–6  
  - High = 8–12  
  - 7 always loses  

Payouts are based on probability, so harder bets pay more.

---

Hidden Rig Rules

The dice are not always random. Each game has a hidden rule that affects the results.

Examples:
- Always forcing a certain total  
- Never allowing certain totals  
- Forcing a number every few rolls  
- Changing behavior based on previous roles  

You need to use the roll history to figure out what is happening.

---

Custom Rig Rules

You can also create your own rig rule before the game starts.

This lets you:
- test different patterns
- understand how the game works better

---

GUI Version

The GUI version (`gui_game.py`) is the main version of the game.

It includes:
- A betting panel
- ASCII dice display
- Roll history tracker
- Result output box
- Rule guessing section

It is easier to use and makes the game more interactive than the command-line version.

---

How to Run

Run the GUI version:
python3 gui_game.py
