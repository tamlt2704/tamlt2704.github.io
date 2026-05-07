# Generators & Flow Control

[← 2D Graphs & Shapes](12-2d-graphs.md) | [Back to Index](README.md)

---

Generators are the heart of Revideo's animation system. They're the equivalent of Manim's `construct` method — but more powerful because they give you fine-grained control over timing.

## Generator Functions

A generator function uses `function*` and `yield*`:

```tsx
export const myScene = makeScene2D('example', function* (view) {
  // This is a generator function
  // yield* pauses execution until the animation completes

  yield* circle().x(300, 1);   // wait 1 second
  yield* circle().fill('red', 0.5); // then wait 0.5 seconds
});
```

### `yield*` vs No `yield*`

```tsx
// WITH yield* — waits for animation to finish
yield* circle().x(300, 1);
// Code here runs AFTER the animation

// WITHOUT yield* — fire and forget
circle().x(300, 1);
// Code here runs IMMEDIATELY (animation plays in background)
```

This is how you create overlapping animations:

```tsx
circle().x(300, 1);        // start moving (don't wait)
yield* waitFor(0.2);       // wait 0.2s
yield* square().x(300, 1); // start square moving (overlaps with circle)
```

## `waitFor` — Pause

```tsx
yield* waitFor(2); // pause for 2 seconds
```

**Manim equivalent:** `self.wait(2)`

## `waitUntil` — Named Markers

```tsx
yield* waitUntil('intro-done');
// In the editor, you can place markers on the timeline
// The generator pauses until the marker is reached
```

Useful for syncing animations to audio or specific timestamps.

## Loops

```tsx
// Animate 5 circles one by one
for (let i = 0; i < 5; i++) {
  yield* dots[i].opacity(1, 0.2);
}

// Repeat an animation 3 times
for (let i = 0; i < 3; i++) {
  yield* circle().scale(1.2, 0.3);
  yield* circle().scale(1, 0.3);
}
```

Or use the `loop` helper:

```tsx
import { loop } from '@revideo/core';

yield* loop(3, function* () {
  yield* circle().scale(1.2, 0.3);
  yield* circle().scale(1, 0.3);
});
```

## Sequences with Timing

### Staggered entrance

```tsx
const items = createRefArray<Rect>();

view.add(
  <>{Array.from({ length: 8 }, (_, i) => (
    <Rect ref={items} x={i * 100 - 350} y={300}
          size={60} fill="blue" radius={8} opacity={0} />
  ))}</>
);

// Each item slides up and fades in, overlapping
for (const item of items) {
  item.opacity(1, 0.3);
  item.y(0, 0.5, easeOutCubic);
  yield* waitFor(0.08); // stagger delay
}
yield* waitFor(0.5); // wait for last animation
```

### Typewriter effect

```tsx
const txt = createRef<Txt>();
view.add(<Txt ref={txt} text="" fill="white" fontSize={32} fontFamily="monospace" />);

const message = "Hello, World!";
for (let i = 0; i <= message.length; i++) {
  txt().text(message.slice(0, i));
  yield* waitFor(0.05);
}
```

## Helper: Creating Reusable Animations

Extract animation patterns into generator functions:

```tsx
function* fadeIn(node: Node, duration = 0.5) {
  node.opacity(0);
  yield* node.opacity(1, duration);
}

function* fadeOut(node: Node, duration = 0.5) {
  yield* node.opacity(0, duration);
}

function* slideIn(node: Node, from: 'left' | 'right' = 'left', duration = 0.5) {
  const startX = from === 'left' ? -960 : 960;
  node.x(startX);
  yield* node.x(0, duration, easeOutCubic);
}

// Usage
yield* fadeIn(title());
yield* waitFor(1);
yield* slideIn(subtitle(), 'left');
yield* waitFor(2);
yield* all(fadeOut(title()), fadeOut(subtitle()));
```

## Manim Equivalent Summary

| Manim | Revideo |
|---|---|
| `def construct(self):` | `function* (view) {` |
| `self.play(anim)` | `yield* anim` |
| `self.wait(n)` | `yield* waitFor(n)` |
| `self.play(a, b)` (parallel) | `yield* all(a, b)` |
| Sequential `self.play` calls | `yield* chain(a, b)` or sequential `yield*` |
| `AnimationGroup(lag_ratio=0.1)` | `for` loop with `waitFor(0.1)` |
| `always_redraw(lambda: ...)` | Signals: `x={() => signal()}` |
| `ValueTracker` | `createSignal` |

---

[← 2D Graphs & Shapes](12-2d-graphs.md) | [Back to Index](README.md)
