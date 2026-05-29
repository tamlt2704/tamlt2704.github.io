---
title: "🔁 Repeat After Me"
date: 2026-05-29
draft: false
---

# 🔁 Chapter 4: Repeat After Me

Why type something 100 times when Python can do it for you? 🤯 Loops are like a music playlist on REPEAT! 🎵

## 🔄 for Loops — Do This X Times

```python
for i in range(5):
    print("🎉 Hip hip hooray!")
```

This prints the message 5 times! `range(5)` means "do this 5 times" (0, 1, 2, 3, 4).

**Fun analogy:** A `for` loop is like telling your robot 🤖 "Do 10 jumping jacks!" — it counts and repeats!

## 🔢 range() — The Counter

```python
for i in range(1, 6):
    print(i, "🌟")
```

Output: 1 🌟, 2 🌟, 3 🌟, 4 🌟, 5 🌟

- `range(5)` gives you 0, 1, 2, 3, 4
- `range(1, 6)` gives you 1, 2, 3, 4, 5
- `range(0, 10, 2)` gives you 0, 2, 4, 6, 8 (counting by 2s!)

## 🔁 while Loops — Keep Going Until...

```python
password = ""
while password != "magic":
    password = input("🔒 Say the magic word: ")
print("🚪 Door opened! Welcome! ✨")
```

**Fun analogy:** A `while` loop is like "keep knocking until someone opens the door!" 🚪

## 🚀 Project 1: Countdown Timer

```python
import time

print("🚀 ROCKET LAUNCH COUNTDOWN!")
for i in range(10, 0, -1):
    print(i, "...")
    time.sleep(1)
print("🚀 BLAST OFF!! 🌟🌟🌟")
```

## 🚀 Project 2: Times Tables Quiz

```python
import random

score = 0
for question in range(5):
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = int(input(f"What is {a} x {b}? "))
    if answer == a * b:
        print("✅ Correct! 🎉")
        score = score + 1
    else:
        print(f"❌ It was {a * b}")
print(f"Score: {score}/5 ⭐")
```

## 🚀 Project 3: Star Patterns

```python
print("⭐ STAR PYRAMID ⭐")
for i in range(1, 6):
    print("* " * i)
```

Output:

```
*
* *
* * *
* * * *
* * * * *
```

Try this diamond too:

```python
for i in range(1, 6):
    print(" " * (5 - i) + "* " * i)
for i in range(4, 0, -1):
    print(" " * (5 - i) + "* " * i)
```

## 🏆 Challenge

Make a pattern that prints YOUR NAME using `*` characters! Or create a times tables quiz that keeps going until the player gets 3 wrong! 💪

---

You've unlocked the power of repetition! 🔄 Loops are one of the most powerful tools in coding! 💪

[← Choose Your Adventure](../chapter-03-decisions) | [next → 📦 Collections](../chapter-05-lists)
