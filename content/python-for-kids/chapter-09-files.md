---
title: "💾 Save Your Progress"
date: 2026-05-29
draft: false
---

# 💾 Chapter 9: Save Your Progress

What if your program could REMEMBER things even after you close it? 🤯 That's what files are for! Like saving your game! 🎮

## 📝 Writing to a File

```python
f = open("notes.txt", "w")
f.write("Hello from Python!\n")
f.write("This is saved forever!\n")
f.close()
print("✅ File saved!")
```

**Fun analogy:** Writing to a file is like writing in a notebook 📓. Even when you close the notebook, the words are still there!

## 📖 Reading from a File

```python
f = open("notes.txt", "r")
content = f.read()
f.close()
print("📖 Your file says:")
print(content)
```

## ➕ Adding to a File (Append)

```python
f = open("notes.txt", "a")
f.write("Adding one more line!\n")
f.close()
print("✅ Added to file!")
```

- `"w"` = Write (creates new or overwrites!)
- `"r"` = Read
- `"a"` = Append (add to the end)

## 🚀 Project 1: Diary App

```python
print("📔 MY SECRET DIARY 📔")
print("1. Write entry  2. Read diary")
choice = input("> ")

if choice == "1":
    entry = input("Dear diary: ")
    f = open("diary.txt", "a")
    f.write(entry + "\n")
    f.close()
    print("✅ Saved! 🔒")
elif choice == "2":
    try:
        f = open("diary.txt", "r")
        print("📖 Your diary:")
        print(f.read())
        f.close()
    except:
        print("No diary yet! Write something first! ✏️")
```

## 🚀 Project 2: High Score Tracker

```python
import random

def get_high_score():
    try:
        f = open("highscore.txt", "r")
        score = int(f.read())
        f.close()
        return score
    except:
        return 0

def save_high_score(score):
    f = open("highscore.txt", "w")
    f.write(str(score))
    f.close()

high = get_high_score()
print(f"🏆 HIGH SCORE GAME! Current best: {high}")
score = 0
for i in range(5):
    num = random.randint(1, 10)
    guess = int(input(f"Guess 1-10: "))
    if guess == num:
        score = score + 10
        print("✅ +10 points!")
    else:
        print(f"❌ It was {num}")

print(f"Your score: {score}")
if score > high:
    save_high_score(score)
    print("🎉 NEW HIGH SCORE!! 🏆")
```

## 🚀 Project 3: Simple Database

```python
print("📇 CONTACT BOOK 📇")
print("1. Add contact  2. View all  3. Search")
choice = input("> ")

if choice == "1":
    name = input("Name: ")
    phone = input("Phone: ")
    f = open("contacts.txt", "a")
    f.write(f"{name},{phone}\n")
    f.close()
    print(f"✅ {name} saved!")
elif choice == "2":
    try:
        f = open("contacts.txt", "r")
        for line in f:
            name, phone = line.strip().split(",")
            print(f"  👤 {name}: {phone}")
        f.close()
    except:
        print("No contacts yet!")
elif choice == "3":
    search = input("Search name: ")
    f = open("contacts.txt", "r")
    for line in f:
        if search.lower() in line.lower():
            name, phone = line.strip().split(",")
            print(f"  👤 {name}: {phone}")
    f.close()
```

## 🏆 Challenge

Combine the high score tracker with the games from Chapter 8! Save the best hangman time or RPG victories to a file! 🏆

---

Your programs can remember things now! 🧠 That's a HUGE level up! 💾✨

[← Game Time!](../chapter-08-games) | [next → 🚀 Level Up!](../chapter-10-next)
