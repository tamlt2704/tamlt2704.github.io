# Intro To Revideo — Programmatic Video Course

Revideo is a TypeScript framework for creating videos programmatically. Think of it as "Manim but in TypeScript" — you write code, and it renders to video.

This course mirrors the structure of the [DevTaoism Manim course](https://docs.devtaoism.com/docs/html/index.html), adapted for Revideo's API.

## Contents

- [Installation](00-installation.md)
- [Basic Elements](01-basic-elements.md)
  - [How Revideo Works](#)
  - [Basic Structure](#)
  - [Nodes](#)
  - [Add Nodes to Screen](#)
  - [Animations (Generators)](#)
- [Basic Node Properties](02-basic-node-properties.md)
  - [Canvas Dimensions](#)
  - [Position](#)
  - [Size (Width and Height)](#)
  - [Color, Fill, Stroke](#)
  - [Opacity](#)
  - [Refs](#)
  - [Cloning and Setters](#)
- [Project Settings](03-project-settings.md)
  - [Resolution and Background](#)
  - [Render Config](#)
  - [Editor vs CLI Rendering](#)
- [Layers](04-layers.md)
  - [Node Ordering](#)
  - [`zIndex`](#)
- [Easing Functions](05-easing-functions.md)
- [Import Assets](06-assets.md)
  - [Images](#)
  - [Video and Audio](#)
- [Layout](07-layout.md)
  - [Flexbox Layout](#)
  - [Direction, Gap, Padding](#)
  - [Alignment](#)
- [Text](08-text.md)
  - [Txt Node](#)
  - [Font Properties](#)
  - [Code Blocks](#)
- [Transitions](09-transitions.md)
  - [Property Tweening](#)
  - [Chaining with `chain`](#)
  - [Parallel with `all`](#)
  - [Sequences](#)
- [Signals & Reactivity](10-signals.md)
  - [What Are Signals](#)
  - [createSignal](#)
  - [Computed Signals](#)
  - [Animating Signals](#)
- [Revideo Utilities](11-utilities.md)
  - [Helpful Methods](#)
  - [Color Utilities](#)
  - [Math Utilities](#)
- [2D Graphs & Shapes](12-2d-graphs.md)
  - [Line, Circle, Rect](#)
  - [Bezier Curves](#)
  - [Custom Shapes](#)
- [Generators & Flow Control](13-generators.md)
  - [Generator Functions](#)
  - [`yield*` and Timing](#)
  - [`waitFor`, `waitUntil`](#)
  - [Loops and Sequences](#)

## Manim → Revideo Cheat Sheet

| Manim (Python) | Revideo (TypeScript) |
|---|---|
| `Scene` | `makeScene2D` |
| `self.play(...)` | `yield* ...` |
| `self.wait(n)` | `yield* waitFor(n)` |
| `self.add(obj)` | `view.add(<Node />)` |
| `Mobject` | `Node` |
| `VMobject` | `Shape` (Rect, Circle, Line...) |
| `Text("hello")` | `<Txt text="hello" />` |
| `Circle()` | `<Circle size={200} />` |
| `Square()` | `<Rect size={200} />` |
| `FadeIn(obj)` | `obj.opacity(1, duration)` |
| `FadeOut(obj)` | `obj.opacity(0, duration)` |
| `Create(obj)` | `obj.end(1, duration)` |
| `Transform(a, b)` | Tween properties individually |
| `rate_func=smooth` | `easeInOutCubic` |
| `rate_func=linear` | `linear` |
| `VGroup(a, b)` | `<Rect layout>{a}{b}</Rect>` |
| `config.frame_width` | `settings.shared.size.x` |
| `self.camera` | Project settings |
| `always_redraw` | Signals (reactive) |
| `ValueTracker` | `createSignal` |

---

[Start: Installation →](00-installation.md)
