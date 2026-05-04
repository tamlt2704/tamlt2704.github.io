# Easing Functions

[← Layers](04-layers.md) | [Import Assets →](06-assets.md)

---

Easing functions control the **acceleration curve** of an animation. In Manim, these are called `rate_func`. In Revideo, they're easing functions passed as the third argument to any property animation.

## Usage

```tsx
import { easeInOutCubic, linear, easeOutBounce } from '@revideo/core';

// Default easing (smooth)
yield* circle().x(300, 1);

// Explicit easing
yield* circle().x(300, 1, easeInOutCubic);

// Linear (constant speed)
yield* circle().x(300, 1, linear);

// Bouncy
yield* circle().y(200, 1, easeOutBounce);
```

## Manim → Revideo Mapping

| Manim `rate_func` | Revideo Easing | Behavior |
|---|---|---|
| `smooth` | `easeInOutCubic` | Slow start, fast middle, slow end |
| `linear` | `linear` | Constant speed |
| `rush_into` | `easeInCubic` | Slow start, fast end |
| `rush_from` | `easeOutCubic` | Fast start, slow end |
| `slow_into` | `easeOutQuad` | Decelerating |
| `there_and_back` | Custom (see below) | Goes to target and back |
| `wiggle` | Custom (see below) | Oscillates |

## Available Easings

All standard CSS easing functions are available:

### Ease In (accelerating)

```tsx
easeInSine, easeInQuad, easeInCubic, easeInQuart, easeInExpo, easeInCirc, easeInBack
```

### Ease Out (decelerating)

```tsx
easeOutSine, easeOutQuad, easeOutCubic, easeOutQuart, easeOutExpo, easeOutCirc,
easeOutBack, easeOutBounce, easeOutElastic
```

### Ease In-Out (both)

```tsx
easeInOutSine, easeInOutQuad, easeInOutCubic, easeInOutQuart, easeInOutExpo,
easeInOutCirc, easeInOutBack, easeInOutBounce
```

### Special

```tsx
linear    // constant speed — no easing
```

## Visual Guide

```
linear:         ╱─────────────    constant speed
easeInCubic:    ╱              ╱  slow start, fast end
easeOutCubic:   ╱╱              ─  fast start, slow end
easeInOutCubic: ╱    ╱╱    ─     slow-fast-slow (most natural)
easeOutBounce:  ╱╱  ╲╱ ╲╱ ─      bounces at the end
easeOutElastic: ╱╱╲╱─             springs past target, settles
```

## Custom Easing (there_and_back equivalent)

Revideo doesn't have `there_and_back` built in, but you can create it:

```tsx
function thereAndBack(t: number): number {
  return t < 0.5 ? 2 * t : 2 * (1 - t);
}

yield* circle().x(300, 2, thereAndBack);
// Moves to 300, then back to 0
```

## Comparison Example

```tsx
import { all, createRefArray } from '@revideo/core';
import { Circle, Txt } from '@revideo/2d';
import { linear, easeInCubic, easeOutCubic, easeInOutCubic, easeOutBounce } from '@revideo/core';

const easings = [
  { name: 'linear', fn: linear },
  { name: 'easeIn', fn: easeInCubic },
  { name: 'easeOut', fn: easeOutCubic },
  { name: 'easeInOut', fn: easeInOutCubic },
  { name: 'bounce', fn: easeOutBounce },
];

const dots = createRefArray<Circle>();

view.add(
  <>
    {easings.map((e, i) => (
      <>
        <Txt text={e.name} x={-400} y={i * 80 - 160} fill="#888" fontSize={16} />
        <Circle ref={dots} x={-200} y={i * 80 - 160} size={30} fill="blue" />
      </>
    ))}
  </>
);

// All dots move right simultaneously, each with a different easing
yield* all(
  ...easings.map((e, i) => dots[i].x(300, 2, e.fn)),
);
```

This creates a visual comparison of all easing functions — each dot moves the same distance in the same time, but with different acceleration curves.

---

[← Layers](04-layers.md) | [Import Assets →](06-assets.md)
