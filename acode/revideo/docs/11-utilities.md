# Revideo Utilities

[← Signals & Reactivity](10-signals.md) | [2D Graphs & Shapes →](12-2d-graphs.md)

---

## Helpful Methods

### `waitFor` — Pause

```tsx
yield* waitFor(2); // pause for 2 seconds
```

### `waitUntil` — Wait for a named event

```tsx
yield* waitUntil('show-title'); // waits until this marker in the editor timeline
```

### `all` — Parallel animations

```tsx
yield* all(a().x(100, 1), b().y(200, 1));
```

### `chain` — Sequential animations

```tsx
yield* chain(a().x(100, 1), b().y(200, 1));
```

### `loop` — Repeat

```tsx
import { loop } from '@revideo/core';

yield* loop(3, () => chain(
  circle().scale(1.2, 0.3),
  circle().scale(1, 0.3),
));
```

### `delay` — Start after a delay

```tsx
import { delay } from '@revideo/core';

yield* all(
  circle().x(300, 1),
  delay(0.5, square().x(300, 1)), // starts 0.5s later
);
```

## Color Utilities

```tsx
// Colors can be strings
fill="red"
fill="#ff5f57"
fill="rgb(78, 201, 176)"

// Or use the Color class for manipulation
import { Color } from '@revideo/core';

const c = new Color('#ff5f57');
c.alpha(0.5);    // semi-transparent
c.brighten(0.2); // lighter
c.darken(0.2);   // darker
```

## Math Utilities

```tsx
// Degrees to radians
import { DEG2RAD, RAD2DEG } from '@revideo/core';

rotation={45}           // Revideo uses degrees by default
rotation={Math.PI / 4}  // or radians if you prefer

// Interpolation
import { map } from '@revideo/core';
const value = map(0, 100, 0.5); // → 50 (lerp between 0 and 100 at t=0.5)
```

## Manim Utility Equivalents

| Manim | Revideo |
|---|---|
| `self.wait(n)` | `waitFor(n)` |
| `AnimationGroup(a, b)` | `all(a, b)` |
| `Succession(a, b)` | `chain(a, b)` |
| `LaggedStart(...)` | `delay()` inside `all()` |
| `DEGREES` / `PI` | Degrees by default, `Math.PI` |
| `interpolate(a, b, t)` | `map(a, b, t)` |

---

[← Signals & Reactivity](10-signals.md) | [2D Graphs & Shapes →](12-2d-graphs.md)
