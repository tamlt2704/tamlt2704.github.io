# Transitions

[← Text](08-text.md) | [Signals & Reactivity →](10-signals.md)

---

## Property Tweening

Every animatable property is a transition. Call it with `(value, duration, easing)`:

```tsx
yield* circle().x(300, 1);                    // move
yield* circle().fill('red', 0.5);             // color
yield* circle().scale(2, 0.3, easeOutBack);   // scale with overshoot
```

This is the core animation primitive. There are no separate "Transform" or "ReplacementTransform" classes like in Manim — you tween individual properties.

## Parallel with `all`

Run multiple animations simultaneously:

```tsx
import { all } from '@revideo/core';

yield* all(
  circle().x(300, 1),
  circle().fill('red', 1),
  square().opacity(0, 1),
);
```

**Manim equivalent:**

```python
self.play(
    circle.animate.shift(RIGHT * 3),
    circle.animate.set_color(RED),
    FadeOut(square),
)
```

## Sequential with `chain`

Run animations one after another:

```tsx
import { chain } from '@revideo/core';

yield* chain(
  circle().x(300, 0.5),
  circle().fill('red', 0.3),
  circle().opacity(0, 0.5),
);
```

**Manim equivalent:** Three separate `self.play()` calls.

## Mixing `all` and `chain`

```tsx
yield* chain(
  // Step 1: both move simultaneously
  all(
    circle().x(300, 1),
    square().x(-300, 1),
  ),
  // Step 2: pause
  waitFor(0.5),
  // Step 3: both fade out
  all(
    circle().opacity(0, 0.5),
    square().opacity(0, 0.5),
  ),
);
```

## Staggered Animations

Animate items one by one with a delay:

```tsx
const items = createRefArray<Circle>();

// Add 5 circles
view.add(
  <>{[0,1,2,3,4].map(i =>
    <Circle ref={items} x={i * 80 - 160} size={40} fill="blue" opacity={0} />
  )}</>
);

// Stagger: each fades in 0.1s after the previous
for (const item of items) {
  yield* item.opacity(1, 0.2);
  // No waitFor needed — yield* already waits for each
}
```

For overlapping staggers (each starts before the previous finishes):

```tsx
for (let i = 0; i < items.length; i++) {
  items[i].opacity(1, 0.3); // start animation (no yield*)
  yield* waitFor(0.08);      // wait a bit before starting next
}
yield* waitFor(0.3); // wait for the last one to finish
```

## Manim Transform Equivalents

| Manim | Revideo |
|---|---|
| `Transform(a, b)` | Tween each property: `a.x(b.x(), d)`, `a.fill(b.fill(), d)` |
| `ReplacementTransform(a, b)` | Fade out `a`, fade in `b` at same position |
| `FadeTransform(a, b)` | `all(a.opacity(0, d), b.opacity(1, d))` |
| `TransformMatchingShapes` | No direct equivalent — animate individual properties |

```tsx
// ReplacementTransform equivalent
yield* all(
  oldNode().opacity(0, 0.5),
  newNode().opacity(1, 0.5),
);
```

---

[← Text](08-text.md) | [Signals & Reactivity →](10-signals.md)
