Alex Thomas & Liv MacMillan

 # Dice Betting Game with Hidden Rig Rule

## Overview

This program is a command-line dice betting game where the player bets on the outcome of two dice. However, the dice may be **rigged according to a hidden rule**, and the player must try to discover the rule in order to win the game.

For trial runs, players can create their own rig rule to test how the rigging works. 

The player starts with a balance of $100 and can play rounds while observing the results of the dice rolls. By studying the roll history, the player can attempt to guess the hidden rig rule that is affecting the dice.

## How the Game Works

Each round the player chooses one of three actions:

1. Play a round – place a bet on the outcome of the dice  
2. Guess the rig rule – try to identify how the dice are being manipulated  
3. Quit – end the game and reveal the rig rule  

If the player chooses to play a round, they must select:

- A wager amount
- A type of bet (such as betting on a specific total)

The dice are rolled and the result is displayed. The player’s balance increases or decreases depending on the outcome of the bet.

The game also displays a history of recent dice rolls so the player can analyze patterns.

## The Rigged Dice System

Unlike a normal dice game, the dice in this program may follow a **rig rule**. A rig rule changes how the dice behave under certain conditions.

Examples of possible rig rules include:

- Always forcing the dice to total a specific number
- Never allowing certain totals (such as 2 or 12)
- Forcing a specific total every N rolls
- Changing the next roll when the previous roll has a specific total

The player does **not know which rig rule is active**. By observing the roll history, the player can look for patterns in the dice results.

The goal of the game is to figure out how the dice are being manipulated.

## Guessing the Rig Rule

At any time, the player can choose the option to **guess the rig rule**.

If the player correctly identifies how the dice are being rigged, the game ends and the player wins.

If the guess is incorrect, a small penalty is applied to the player's balance and the game continues.

## Winning the Game

The player wins by correctly identifying the hidden rig rule that controls the dice.

Once the rule is correctly guessed, the game ends and the player’s final balance is displayed.

## How to Run the Program

1. Make sure Python is installed on your computer.

2. Navigate to the project folder in the terminal.

3. Run the program with:

python main.py

(or run the specific game file if it has a different name).

The game will start in the terminal and prompt the player for input.

## Libraries Used

This project uses only standard Python libraries:

- `random` – used to simulate dice rolls
- `unittest` – used to test functions in the program

No external libraries are required.

## Notes

The rig rule is intentionally hidden from the player during gameplay. The player must analyze the dice roll history to determine how the dice are being manipulated.

This creates a puzzle element in addition to the betting mechanics of the game.
