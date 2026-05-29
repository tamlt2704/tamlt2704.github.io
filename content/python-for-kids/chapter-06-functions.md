---
title: "⚡ Your Own Superpowers"
date: 2026-05-29
draft: false
---

# ⚡ Chapter 6: Your Own Superpowers

Ready to create your OWN commands? 🦸 That's what **functions** are — superpowers you design yourself!

## 🛠️ What's a Function?

A function is a reusable block of code with a name:

```python
def say_hello():
    print("👋 Hello there!")
    print("Welcome to my program!")

say_hello()
say_hello()
```

**Fun analogy:** A function is like a recipe 📝. You write it once, then you can "cook" it anytime by calling its name!

## 📨 Parameters — Giving Info to Functions

```python
def greet(name):
    print(f"🌟 Hey {name}! You're awesome!")

greet("Alex")
greet("Sam")
```

Parameters are like blanks in a Mad Lib — you fill them in each time! ✏️

## 📤 return — Getting Something Back

```python
def add(a, b):
    return a + b

result = add(5, 3)
print("5 + 3 =", result)  # 8
```

`return` is like a vending machine 🎰 — you put something in, and it gives something back!

## 🚀 Project 1: Emoji Art Generator

```python
def draw_line(emoji, count):
    print(emoji * count)

def draw_box(emoji, width, height):
    for i in range(height):
        draw_line(emoji, width)

print("🎨 EMOJI ART 🎨")
draw_box("🌟", 5, 3)
print()
draw_box("🐍", 8, 2)
print()
draw_line("🌈", 10)
```

## 🚀 Project 2: Password Generator

```python
import random

def make_password(length):
    chars = "abcdefghijkmnpqrstuvwxyz23456789"
    password = ""
    for i in range(length):
        password = password + random.choice(chars)
    return password

print("🔐 PASSWORD GENERATOR 🔐")
for i in range(5):
    print(f"  Option {i+1}: {make_password(8)}")
print("Pick your favorite! 🎉")
```

## 🚀 Project 3: Simple Chatbot

```python
def respond(message):
    message = message.lower()
    if "hello" in message or "hi" in message:
        return "Hey there! 👋 How are you?"
    elif "good" in message or "great" in message:
        return "Awesome! 🎉 That makes me happy!"
    elif "bye" in message:
        return "See you later! 👋🌟"
    else:
        return "Interesting! Tell me more! 🤔"

print("🤖 ChatBot v1.0 — type 'bye' to quit")
while True:
    user = input("You: ")
    if "bye" in user.lower():
        print("Bot:", respond(user))
        break
    print("Bot:", respond(user))
```

## 🏆 Challenge

Add more responses to the chatbot! Can you make it respond to "joke" with a random joke from a list? Or respond to "game" by playing a number guessing game? 🎮

---

You just created your own superpowers! 🦸 Functions make you a REAL programmer! 💪

[← Collections](../chapter-05-lists) | [next → 🎨 Drawing with Code](../chapter-07-turtle)
