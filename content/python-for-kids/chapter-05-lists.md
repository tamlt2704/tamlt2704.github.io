---
title: "📦 Collections"
date: 2026-05-29
draft: false
---

# 📦 Chapter 5: Collections

Time to learn about **lists** — Python's way of keeping a bunch of things together! 🎒 Like a backpack full of treasures!

## 📋 What's a List?

A list holds multiple items in order:

```python
fruits = ["apple", "banana", "cherry"]
scores = [100, 85, 92, 78]
print(fruits)
print(scores)
```

**Fun analogy:** A list is like a train 🚂 — each car holds something different, and they're all connected in order!

## 🔍 Getting Items (Indexing)

Each item has a number (starting from 0!):

```python
animals = ["cat", "dog", "fish", "bird"]
print(animals[0])  # cat (first!)
print(animals[2])  # fish (third!)
```

🧠 Remember: computers start counting at 0! It's weird but you'll get used to it!

## ➕ Adding to Lists

```python
my_list = ["pizza", "tacos"]
my_list.append("sushi")
print(my_list)  # ["pizza", "tacos", "sushi"]
```

`append()` adds something to the END of the list — like adding a new car to the train! 🚃

## 🔄 Looping Through Lists

```python
colors = ["red", "blue", "green", "yellow"]
for color in colors:
    print(color, "is awesome! 🌈")
```

## 🚀 Project 1: Shopping List App

```python
print("🛒 SHOPPING LIST 🛒")
shopping = []

while True:
    item = input("Add item (or 'done'): ")
    if item == "done":
        break
    shopping.append(item)

print("\n📋 Your list:")
for i, item in enumerate(shopping, 1):
    print(f"  {i}. {item}")
print(f"Total: {len(shopping)} items! 🎉")
```

## 🚀 Project 2: Quiz Game with Score

```python
questions = ["What color is the sky?", "What has 8 legs?", "What is 7+7?"]
answers = ["blue", "spider", "14"]
score = 0

print("🧠 QUIZ TIME! 🧠")
for i in range(len(questions)):
    guess = input(questions[i] + " ")
    if guess.lower() == answers[i]:
        print("✅ Correct! 🎉")
        score = score + 1
    else:
        print(f"❌ It was: {answers[i]}")

print(f"\nFinal score: {score}/{len(questions)} ⭐")
```

## 🚀 Project 3: Playlist Shuffler

```python
import random

songs = []
print("🎵 PLAYLIST SHUFFLER 🎵")
print("Add songs (type 'play' to shuffle!)")

while True:
    song = input("Song: ")
    if song == "play":
        break
    songs.append(song)

random.shuffle(songs)
print("\n🔀 Shuffled playlist:")
for i, song in enumerate(songs, 1):
    print(f"  {i}. 🎶 {song}")
```

## 🏆 Challenge

Make the quiz game pick random questions from a BIG list of 10+ questions, and only ask 5 each time! Hint: use `random.sample()`! 🎯

---

You're organizing data like a pro! 📊 Lists are EVERYWHERE in real programs! 🌟

[← Repeat After Me](../chapter-04-loops) | [next → ⚡ Your Own Superpowers](../chapter-06-functions)
