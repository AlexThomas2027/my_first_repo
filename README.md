# Dice Betting Game

## Overview

This project implements a dice betting game in Python.

The player places a bet, the dice are rolled, and payouts are determined based on the result and a configurable rig rule. The design uses higher-order functions to allow different rig behaviors without modifying the core game logic.

## Files

- main.py  
  Contains the core game logic and game flow.

- TestSuiteForMainGame.py  
  Contains the full unit test suite for the project.

## How to Run the Game

Run:

    python main.py

## How to Run the Tests

Run:

    python TestSuiteForMainGame.py

## Design Notes

The rig rule is implemented using a higher-order function. This means a function is passed into the game logic to determine payout behavior rather than hard-coding specific conditions. This makes the system flexible and easy to extend.
