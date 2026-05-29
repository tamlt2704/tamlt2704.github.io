---
title: "🎨 Drawing with Code"
date: 2026-05-29
draft: false
---

# 🎨 Chapter 7: Drawing with Code

Time to make ART with Python! 🖌️ We'll use **Turtle Graphics** — imagine a little turtle 🐢 holding a pen, walking around and drawing wherever it goes!

## 🐢 Meet Your Turtle

```python
import turtle

t = turtle.Turtle()
t.forward(100)
t.left(90)
t.forward(100)
turtle.done()
```

**Fun analogy:** Your turtle is like an Etch-a-Sketch! 🎨 You tell it "go forward" and "turn left" and it draws lines wherever it walks!

## 🎮 Basic Commands

- `t.forward(100)` — Walk forward 100 steps
- `t.backward(50)` — Walk backward 50 steps
- `t.left(90)` — Turn left 90 degrees
- `t.right(90)` — Turn right 90 degrees
- `t.penup()` — Lift pen (move without drawing)
- `t.pendown()` — Put pen down (start drawing again)

## 🌈 Colors!

```python
import turtle

t = turtle.Turtle()
t.pensize(3)
t.color("red")
t.forward(100)
t.color("blue")
t.left(90)
t.forward(100)
turtle.done()
```

## 🔄 Loops + Turtle = Magic!

Draw a square with a loop:

```python
import turtle

t = turtle.Turtle()
for i in range(4):
    t.forward(100)
    t.left(90)
turtle.done()
```

## 🚀 Project 1: Draw a House

```python
import turtle

t = turtle.Turtle()
t.speed(3)
t.color("brown")
for i in range(4):
    t.forward(100)
    t.left(90)
t.color("red")
t.left(45)
for i in range(3):
    t.forward(70)
    t.left(120)
turtle.done()
```

## 🚀 Project 2: Spiral Art

```python
import turtle

t = turtle.Turtle()
t.speed(0)
colors = ["red", "orange", "yellow", "green", "blue", "purple"]

for i in range(60):
    t.color(colors[i % 6])
    t.forward(i * 3)
    t.left(61)
turtle.done()
```

This makes a BEAUTIFUL colorful spiral! 🌀✨

## 🚀 Project 3: Star Patterns

Draw a perfect 5-pointed star:

```python
import turtle

t = turtle.Turtle()
t.speed(0)
t.color("gold")

for i in range(5):
    t.forward(150)
    t.right(144)
turtle.done()
```

Want a SUPER star burst? Try this:

```python
import turtle

t = turtle.Turtle()
t.speed(0)
for i in range(36):
    t.color("blue")
    for j in range(5):
        t.forward(100)
        t.right(144)
    t.right(10)
turtle.done()
```

## 🏆 Challenge

Can you draw your initials using turtle? Or create a scene with a house, tree, and sun? Try using `t.begin_fill()` and `t.end_fill()` to color in shapes! 🎨

---

You're a code artist now! 🎨 Show your drawings to friends and family! 🌟

[← Your Own Superpowers](../chapter-06-functions) | [next → 🎮 Game Time!](../chapter-08-games)
