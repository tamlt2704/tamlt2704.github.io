---
title: "🔢 Math Magic"
date: 2026-05-29
draft: false
---

# 🔢 Chapter 2: Math Magic

Time to turn Python into a super-powered calculator! 🧮✨ Don't worry — this math is FUN!

## ➕ Basic Math Operators

Python can do math just like a calculator:

```python
print(5 + 3)    # Addition: 8
print(10 - 4)   # Subtraction: 6
print(3 * 7)    # Multiplication: 21
print(20 / 4)   # Division: 5.0
```

## 💪 Super Powers and Remainders

Two special tricks:

```python
print(2 ** 3)   # Power! 2x2x2 = 8
print(10 % 3)   # Remainder! 10 divided by 3 = 3 remainder 1
```

**Fun analogy:** `**` is like a power-up mushroom 🍄 — it makes numbers HUGE! `2 ** 10` = 1024!

`%` (remainder) is like sharing cookies 🍪. If you have 10 cookies and 3 friends, everyone gets 3 and there's 1 left over!

## 🎲 Random Numbers — Surprise!

Want Python to pick a random number? Like rolling dice! 🎲

```python
import random

dice = random.randint(1, 6)
print("You rolled a", dice, "! 🎲")
```

`random.randint(1, 6)` picks a number from 1 to 6 — just like a real die!

## 🚀 Project 1: Dice Roller

```python
import random

print("🎲 DICE ROLLER 🎲")
input("Press Enter to roll...")
die1 = random.randint(1, 6)
die2 = random.randint(1, 6)
print("You got:", die1, "and", die2)
print("Total:", die1 + die2, "🎉")
```

## 🚀 Project 2: Number Guessing Game

```python
import random

secret = random.randint(1, 10)
print("🔮 I'm thinking of a number 1-10...")
guess = int(input("Your guess: "))

if guess == secret:
    print("🎉 YOU GOT IT! You're a mind reader!")
else:
    print("Nope! It was", secret, "— try again! 💪")
```

## 🚀 Project 3: Calculator

```python
print("🧮 SUPER CALCULATOR 🧮")
num1 = float(input("First number: "))
num2 = float(input("Second number: "))
op = input("Operation (+, -, *, /): ")

if op == "+":
    print("Answer:", num1 + num2, "✨")
elif op == "-":
    print("Answer:", num1 - num2, "✨")
elif op == "*":
    print("Answer:", num1 * num2, "✨")
elif op == "/":
    print("Answer:", num1 / num2, "✨")
```

## 🏆 Challenge

Make the number guessing game give hints! Print "Too high! ⬆️" or "Too low! ⬇️" and let them guess again using a loop! 🎯

---

You're a math wizard now! 🧙‍♂️ High five! ✋

[← Your First Spell](../chapter-01-hello) | [next → 🚪 Choose Your Adventure](../chapter-03-decisions)
