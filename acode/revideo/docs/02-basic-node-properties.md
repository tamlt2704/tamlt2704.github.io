# Basic Node Properties

[← Basic Elements](01-basic-elements.md) | [Project Settings →](03-project-settings.md)

---

## Canvas Dimensions

By default, Revideo uses **1920×1080** (Full HD). The coordinate system has `(0, 0)` at the **center** of the screen.

```
(-960, -540) ─────────────────── (960, -540)
      │                               │
      │           (0, 0)              │
      │          center               │
      │                               │
(-960, 540) ──────────────────── (960, 540)
```

**Manim equivalent:** Manim uses a coordinate system where the default frame is about 14.2 × 8 units. Revideo uses pixels directly.

## Position

### Absolute Position

Every node has `x` and `y` properties (or `position` as a tuple):

```tsx
// Place at center (default)
<Circle x={0} y={0} size={200} fill="blue" />

// Place at top-left area
<Circle x={-400} y={-200} size={200} fill="red" />

// Using position shorthand
<Circle position={[300, 150]} size={200} fill="green" />
```

### Animating Position

```tsx
const circle = createRef<Circle>();
view.add(<Circle ref={circle} size={200} fill="blue" />);

// Move right
yield* circle().x(300, 1);

// Move to specific position
yield* circle().position([200, -100], 1);

// Move relative (add to current position)
yield* circle().x(circle().x() + 200, 1);
```

**Manim equivalent:**

```python
# Manim
self.play(circle.animate.move_to(RIGHT * 3))
self.play(circle.animate.shift(RIGHT * 2))
```

### Relative Position

To position a node relative to another, read the other node's position:

```tsx
const a = createRef<Circle>();
const b = createRef<Circle>();

view.add(<Circle ref={a} x={-200} size={100} fill="red" />);
view.add(<Circle ref={b} x={a().x() + 300} size={100} fill="blue" />);
```

## Size (Width and Height)

```tsx
// Square (equal width and height)
<Rect size={200} fill="blue" />          // 200×200
<Rect size={[300, 200]} fill="blue" />   // 300×200

// Explicit
<Rect width={400} height={200} fill="blue" />

// Circle uses size as diameter
<Circle size={200} fill="red" />         // radius = 100
```

### Animating Size

```tsx
yield* rect().width(500, 1);
yield* rect().size([400, 300], 1);
yield* circle().size(400, 0.5); // grow the circle
```

**Manim equivalent:** `self.play(circle.animate.scale(2))`

## Color, Fill, Stroke

```tsx
// Fill color (interior)
<Rect size={200} fill="blue" />
<Rect size={200} fill="#ff5f57" />
<Rect size={200} fill="rgb(78, 201, 176)" />

// Stroke (border)
<Rect size={200} stroke="white" lineWidth={3} />

// Both
<Circle size={200} fill="blue" stroke="white" lineWidth={2} />

// No fill, only stroke
<Circle size={200} fill={null} stroke="red" lineWidth={4} />
```

### Animating Colors

```tsx
yield* circle().fill('red', 0.5);
yield* circle().stroke('yellow', 0.5);
yield* circle().lineWidth(8, 0.3);
```

**Manim equivalent:**

```python
self.play(circle.animate.set_color(RED))
self.play(circle.animate.set_stroke(YELLOW, width=8))
```

## Opacity

```tsx
// Fully visible (default)
<Rect size={200} fill="blue" opacity={1} />

// Semi-transparent
<Rect size={200} fill="blue" opacity={0.5} />

// Invisible (still in scene tree, just not visible)
<Rect size={200} fill="blue" opacity={0} />
```

### Fade In / Fade Out

```tsx
// Start invisible, fade in
view.add(<Circle ref={circle} size={200} fill="blue" opacity={0} />);
yield* circle().opacity(1, 0.5);  // FadeIn

// Fade out
yield* circle().opacity(0, 0.5);  // FadeOut
```

**Manim equivalent:**

```python
self.play(FadeIn(circle))
self.play(FadeOut(circle))
```

## Refs

To animate a node after creating it, you need a **ref** — a reference to the node instance.

```tsx
import { createRef } from '@revideo/core';
import { Circle } from '@revideo/2d';

export const myScene = makeScene2D('example', function* (view) {
  const circle = createRef<Circle>();

  view.add(<Circle ref={circle} size={200} fill="blue" />);

  // Now you can animate it
  yield* circle().x(300, 1);
  yield* circle().fill('red', 0.5);
});
```

`createRef<Circle>()` creates a typed reference. After `view.add(...)`, calling `circle()` returns the actual node instance.

### Multiple Refs

```tsx
import { createRef, createRefArray } from '@revideo/core';

// Single ref
const title = createRef<Txt>();

// Array of refs (for lists of similar nodes)
const dots = createRefArray<Circle>();

view.add(
  <>
    <Txt ref={title} text="Hello" fill="white" fontSize={48} />
    {[0, 1, 2, 3, 4].map(i => (
      <Circle ref={dots} x={i * 60 - 120} size={20} fill="blue" />
    ))}
  </>
);

// Animate the title
yield* title().y(-200, 0.5);

// Animate each dot
for (const dot of dots) {
  yield* dot.fill('red', 0.2);
}
```

**Manim equivalent:** In Manim, you just keep a variable reference. In Revideo, you use `createRef` because JSX creates nodes declaratively.

## Cloning and Setters

### Reading Properties

Every property is a function. Call it with no arguments to read:

```tsx
const currentX = circle().x();        // read x position
const currentFill = circle().fill();   // read fill color
const currentOpacity = circle().opacity();
```

### Setting Properties (Instant, No Animation)

Call with one argument (no duration):

```tsx
circle().x(300);          // instant move
circle().fill('red');     // instant color change
circle().opacity(0.5);    // instant opacity
```

### Setting Properties (Animated)

Call with two arguments (value + duration):

```tsx
yield* circle().x(300, 1);          // animate over 1 second
yield* circle().fill('red', 0.5);   // animate over 0.5 seconds
```

### Cloning

Revideo doesn't have a direct `.copy()` like Manim. Instead, create a new node with the same properties:

```tsx
const original = createRef<Circle>();
view.add(<Circle ref={original} x={-200} size={200} fill="blue" />);

// "Clone" by creating a new node with same properties
const clone = <Circle
  x={original().x()}
  y={original().y()}
  size={original().size()}
  fill={original().fill()}
/>;
view.add(clone);
```

## Exercises

1. Create a scene with a red circle at `(-300, 0)` and a blue square at `(300, 0)`.
2. Animate the circle moving to `(300, 0)` and the square moving to `(-300, 0)` simultaneously.
3. Fade both out.
4. Create 10 circles in a row using a loop and `createRefArray`. Animate each one turning red, one after another.

---

[← Basic Elements](01-basic-elements.md) | [Project Settings →](03-project-settings.md)
