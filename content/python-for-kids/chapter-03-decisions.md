---
title: "🚪 Choose Your Adventure"
date: 2026-05-29
draft: false
---

# 🚪 Chapter 3: Choose Your Adventure

Today you'll teach Python to make DECISIONS! 🤔 Just like choosing which path to take in a maze! 🏰

## 🚦 if — Checking Things

`if` is like a guard at a door 🚪. It checks if something is true before letting code through:

```python
age = int(input("How old are you? "))

if age >= 13:
    print("Welcome to the teen zone! 🎉")
```

**Fun analogy:** Think of `if` as a bouncer at a party 🕺. "Are you on the list? Yes? Come in!"

## 🔀 if/elif/else — Multiple Paths

Sometimes there are MANY doors to choose from:

```python
weather = input("What's the weather? (sunny/rainy/snowy) ")

if weather == "sunny":
    print("Let's go to the park! ☀️")
elif weather == "rainy":
    print("Movie time indoors! 🌧️")
else:
    print("SNOWBALL FIGHT! ❄️")
```

## ⚖️ Comparisons

- `==` means "is equal to?"
- `!=` means "is NOT equal to?"
- `>` means "greater than?"
- `<` means "less than?"
- `>=` and `<=` — greater/less than or equal

## 🤝 and / or — Combining Checks

```python
age = 10
has_ticket = True

if age < 12 and has_ticket:
    print("🎢 Enjoy the kids' ride!")
```

- `and` = BOTH must be true
- `or` = at least ONE must be true

## 🚀 Project 1: Choose-Your-Own-Adventure

```python
print("🏰 You enter a dark castle...")
print("Do you go LEFT or RIGHT?")
choice = input("> ")

if choice == "LEFT":
    print("🐉 A friendly dragon gives you gold!")
    print("You win! 🏆")
elif choice == "RIGHT":
    print("🧙 A wizard teaches you a spell!")
    print("You gained magic powers! ⚡")
else:
    print("🚪 You stood still and found a secret door!")
```

## 🚀 Project 2: Rock-Paper-Scissors

```python
import random

moves = ["rock", "paper", "scissors"]
computer = random.choice(moves)
player = input("rock, paper, or scissors? ")

print("Computer chose:", computer)

if player == computer:
    print("🤝 It's a tie!")
elif player == "rock" and computer == "scissors":
    print("🎉 You WIN!")
elif player == "paper" and computer == "rock":
    print("🎉 You WIN!")
elif player == "scissors" and computer == "paper":
    print("🎉 You WIN!")
else:
    print("😅 Computer wins! Try again!")
```

## 🏆 Challenge

Expand the adventure story! Add MORE choices inside choices — like a real choose-your-own-adventure book with 3 levels deep! 🌳

---

You're making smart programs now! 🧠 You're doing amazing! 🌟

[← Math Magic](../chapter-02-math-magic) | [next → 🔁 Repeat After Me](../chapter-04-loops)
