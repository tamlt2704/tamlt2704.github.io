# Signals & Reactivity

[← Transitions](09-transitions.md) | [Revideo Utilities →](11-utilities.md)

---

Signals are Revideo's equivalent of Manim's `ValueTracker` and `always_redraw`. They let you create **reactive** relationships between values — when one changes, everything that depends on it updates automatically.

## What Are Signals

A signal is a reactive value. When you animate a signal, everything that reads it updates every frame.

```tsx
import { createSignal } from '@revideo/core';

const progress = createSignal(0);

// Read the current value
progress();  // → 0

// Set a new value
progress(0.5);

// Animate it
yield* progress(1, 2); // animate from current to 1 over 2 seconds
```

## Using Signals with Nodes

Pass a signal (the function itself, not its value) as a node property:

```tsx
const xPos = createSignal(-300);

view.add(
  <Circle x={() => xPos()} size={100} fill="blue" />
);

// The circle's x position is now reactive
// Animating the signal moves the circle
yield* xPos(300, 2);
```

The key: `x={() => xPos()}` — the arrow function makes it reactive. `x={xPos()}` would just read the value once.

## Computed Signals

Create values that depend on other signals:

```tsx
const t = createSignal(0);

view.add(
  <>
    <Circle x={() => Math.cos(t() * Math.PI * 2) * 200}
            y={() => Math.sin(t() * Math.PI * 2) * 200}
            size={40} fill="blue" />
    <Txt text={() => `t = ${t().toFixed(2)}`}
         y={300} fill="white" fontSize={24} />
  </>
);

// Animate t from 0 to 1 — the circle traces a full circle
yield* t(1, 3);
```

As `t` goes from 0 to 1, the circle moves along a circular path, and the text updates to show the current value. All from one signal.

**Manim equivalent:**

```python
t = ValueTracker(0)
circle = always_redraw(lambda:
    Dot().move_to([np.cos(t.get_value() * TAU), np.sin(t.get_value() * TAU), 0]))
label = always_redraw(lambda:
    Text(f"t = {t.get_value():.2f}").to_edge(DOWN))
self.play(t.animate.set_value(1), run_time=3)
```

## Practical Example: Progress Bar

```tsx
const progress = createSignal(0);

view.add(
  <Rect width={600} height={20} fill="#333" radius={10}>
    <Rect
      width={() => 600 * progress()}
      height={20}
      fill="#4ec9b0"
      radius={10}
    />
  </Rect>
);

yield* progress(1, 3); // fills the bar over 3 seconds
```

## Practical Example: Counter

```tsx
const count = createSignal(0);

view.add(
  <Txt text={() => Math.floor(count()).toString()}
       fill="white" fontSize={96} fontFamily="monospace" />
);

yield* count(100, 2); // counts from 0 to 100 over 2 seconds
```

---

[← Transitions](09-transitions.md) | [Revideo Utilities →](11-utilities.md)
