---
title: "🎮 Game Time!"
date: 2026-05-29
draft: false
---

# 🎮 Chapter 8: Game Time!

This is it — you're putting EVERYTHING together to build REAL games! 🏆 You've earned this!

## 🚀 Project 1: Hangman

```python
import random

words = ["python", "turtle", "wizard", "dragon", "magic"]
word = random.choice(words)
guessed = ["_"] * len(word)
tries = 6

print("🎯 HANGMAN! Guess the word!")
while tries > 0 and "_" in guessed:
    print(" ".join(guessed), f"  (tries left: {tries})")
    letter = input("Guess a letter: ").lower()
    if letter in word:
        for i in range(len(word)):
            if word[i] == letter:
                guessed[i] = letter
        print("✅ Nice! 🎉")
    else:
        tries = tries - 1
        print("❌ Nope!")

if "_" not in guessed:
    print("🏆 YOU WON! The word was:", word)
else:
    print("😅 Game over! It was:", word)
```

## 🚀 Project 2: Tic-Tac-Toe

```python
board = [" "] * 9

def show_board():
    for i in range(0, 9, 3):
        print(f" {board[i]} | {board[i+1]} | {board[i+2]} ")
        if i < 6:
            print("-----------")

def check_win(mark):
    wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for w in wins:
        if board[w[0]] == board[w[1]] == board[w[2]] == mark:
            return True
    return False

print("🎮 TIC-TAC-TOE! Spots are numbered 1-9")
turn = "X"
for round in range(9):
    show_board()
    move = int(input(f"Player {turn}, pick spot (1-9): ")) - 1
    board[move] = turn
    if check_win(turn):
        show_board()
        print(f"🏆 Player {turn} WINS! 🎉")
        break
    turn = "O" if turn == "X" else "X"
else:
    show_board()
    print("🤝 It's a tie!")
```

## 🚀 Project 3: Mini Text RPG

```python
import random

print("⚔️ DRAGON QUEST ⚔️")
print("A dragon blocks your path!")

hp = 30
dragon_hp = 25
potions = 2

while hp > 0 and dragon_hp > 0:
    print(f"\n❤️ Your HP: {hp} | 🐉 Dragon HP: {dragon_hp} | 🧪 Potions: {potions}")
    print("1. ⚔️ Attack  2. 🧪 Heal  3. 🎲 Special")
    choice = input("> ")

    if choice == "1":
        damage = random.randint(3, 8)
        dragon_hp = dragon_hp - damage
        print(f"You hit for {damage} damage! 💥")
    elif choice == "2" and potions > 0:
        hp = hp + 10
        potions = potions - 1
        print("Healed +10 HP! ✨")
    elif choice == "3":
        damage = random.randint(1, 15)
        print(f"Special attack! {damage} damage! 🌟")
        dragon_hp = dragon_hp - damage
    else:
        print("Nothing happened! 😅")

    if dragon_hp > 0:
        hit = random.randint(2, 7)
        hp = hp - hit
        print(f"Dragon hits you for {hit}! 🔥")

if hp > 0:
    print("\n🏆 YOU DEFEATED THE DRAGON! 🎉🎉🎉")
else:
    print("\n😵 Game over... Try again, hero! 💪")
```

## 🏆 Challenge

Add items to the RPG! Maybe a shield that blocks damage, or a magic sword that does more damage. Can you add multiple enemies? 🐉🧟‍♂️👻

---

You just built REAL games! 🎮 You're officially a game developer! Show these to your friends! 🌟

[← Drawing with Code](../chapter-07-turtle) | [next → 💾 Save Your Progress](../chapter-09-files)
