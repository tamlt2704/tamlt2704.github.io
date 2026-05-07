# Basic Elements

[← Installation](00-installation.md) | [Basic Node Properties →](02-basic-node-properties.md)

---

## How Revideo Works

Revideo works as follows:

1. **TypeScript** reads your scene files.
2. **Revideo's engine** evaluates your generator functions frame by frame, computing node properties at each point in time.
3. Each frame is rendered to a **canvas** (HTML5 Canvas or headless via Puppeteer).
4. **FFmpeg** encodes the frames into a video file.

```
Your Code (.tsx)  →  Revideo Engine  →  Canvas Frames  →  FFmpeg  →  .mp4
```

The key difference from Manim: Revideo uses **JSX** for declaring nodes (like React components) and **generator functions** for timing (instead of `self.play()`).

## Basic Structure

```tsx
// src/scenes/example.tsx
import { makeScene2D, Circle } from '@revideo/2d';
import { waitFor } from '@revideo/core';

export const myScene = makeScene2D('my-scene', function* (view) {
  // Create a circle
  const circle = <Circle size={200} fill="blue" />;

  // Add it to the screen
  view.add(circle);

  // Pause for 2 seconds
  yield* waitFor(2);
});
```

```tsx
// src/project.tsx
import { makeProject } from '@revideo/core';
import { myScene } from './scenes/example';

export default makeProject({
  scenes: [myScene],
});
```

Breaking it down:

1. **Import** the library: `from '@revideo/2d'` and `from '@revideo/core'`
2. **Create a scene** using `makeScene2D('name', generatorFunction)`
3. The generator function receives `view` — the root node (equivalent to Manim's `Scene`)
4. **Add nodes** to `view` using `view.add(...)`
5. **Animate** using `yield*` — this is how you tell the engine "wait for this to finish"
6. **Register the scene** in `project.tsx`

### Manim Equivalent

```python
# Manim
from manim import *

class MyScene(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        self.add(circle)
        self.wait(2)
```

```tsx
// Revideo
export const myScene = makeScene2D('my-scene', function* (view) {
  view.add(<Circle size={200} fill="blue" />);
  yield* waitFor(2);
});
```

## Nodes

In Manim, displayable objects are called **Mobjects**. In Revideo, they're called **Nodes**.

| Manim | Revideo | Description |
|---|---|---|
| `Mobject` | `Node` | Abstract base |
| `VMobject` | `Shape` | Vector shapes (Rect, Circle, Line) |
| `ImageMobject` | `Img` | Raster images |
| `Text` | `Txt` | Text labels |
| `Group` / `VGroup` | `<Rect layout>` | Grouping with layout |

The most common nodes:

```tsx
import { Circle, Rect, Line, Txt, Img, Video, Audio } from '@revideo/2d';

// Shapes
<Circle size={200} fill="red" />
<Rect width={300} height={200} fill="blue" radius={10} />
<Line points={[[-100, 0], [100, 0]]} stroke="white" lineWidth={3} />

// Text
<Txt text="Hello World" fill="white" fontSize={48} />

// Media
<Img src="photo.png" width={400} />
<Video src="clip.mp4" />
<Audio src="music.mp3" />
```

Every node is declared using **JSX** — the same syntax React uses. But this isn't React. Revideo uses JSX as a convenient way to create node instances with properties.

## Add Nodes to Screen

There are two ways to add a node to the screen:

### 1. Directly in the generator (instant, no animation)

```tsx
export const myScene = makeScene2D('example', function* (view) {
  // Add instantly — equivalent to Manim's self.add()
  view.add(<Circle size={200} fill="blue" />);

  yield* waitFor(1);
});
```

### 2. With an animation (fade in, grow, etc.)

```tsx
import { createRef } from '@revideo/core';

export const myScene = makeScene2D('example', function* (view) {
  const circle = createRef<Circle>();

  // Add to scene tree (invisible — opacity 0)
  view.add(<Circle ref={circle} size={200} fill="blue" opacity={0} />);

  // Animate opacity from 0 to 1 (equivalent to FadeIn)
  yield* circle().opacity(1, 0.5);

  yield* waitFor(1);
});
```

> **Important**: If a scene has no `yield*` statements, it renders as a single frame (like Manim rendering a scene with no animations as a PNG).

## Animations (Generators)

In Manim, you animate with `self.play(Animation(mobject))`. In Revideo, you animate by **tweening node properties** using generator syntax.

### The `yield*` Keyword

`yield*` is how you tell the engine: "play this animation and wait for it to finish before continuing."

```tsx
// This takes 1 second — the circle moves from x=0 to x=200
yield* circle().x(200, 1);

// This takes 0.5 seconds — the circle fades out
yield* circle().opacity(0, 0.5);
```

Every animatable property on a node is a function. Call it with `(targetValue, duration)` to animate it.

### Multiple Animations at the Same Time

Use `all()` — equivalent to putting multiple animations in Manim's `self.play()`:

```tsx
import { all } from '@revideo/core';

// Both happen simultaneously
yield* all(
  circle().x(200, 1),
  circle().fill('red', 1),
);
```

**Manim equivalent:**

```python
self.play(
    circle.animate.shift(RIGHT * 2),
    circle.animate.set_color(RED),
)
```

### Sequential Animations

Use `chain()` — equivalent to multiple `self.play()` calls:

```tsx
import { chain } from '@revideo/core';

// One after another
yield* chain(
  circle().x(200, 1),
  circle().fill('red', 0.5),
  circle().opacity(0, 0.5),
);
```

**Manim equivalent:**

```python
self.play(circle.animate.shift(RIGHT * 2))
self.play(circle.animate.set_color(RED))
self.play(FadeOut(circle))
```

### Pausing

```tsx
import { waitFor } from '@revideo/core';

yield* waitFor(2); // pause for 2 seconds
```

**Manim equivalent:** `self.wait(2)`

### Common Animation Patterns

```tsx
// Fade in (equivalent to FadeIn)
yield* node().opacity(1, 0.5);

// Fade out (equivalent to FadeOut)
yield* node().opacity(0, 0.5);

// Move (equivalent to shift/move_to)
yield* node().x(300, 1);
yield* node().position([200, 100], 1);

// Scale (equivalent to scale)
yield* node().scale(2, 0.5);

// Rotate (equivalent to Rotate)
yield* node().rotation(90, 1); // degrees

// Color change
yield* node().fill('red', 0.5);

// Draw a line (equivalent to Create)
yield* line().end(1, 1); // draws from 0% to 100%
```

### Animation Duration and Easing

Every animation accepts an optional third argument — the easing function:

```tsx
import { easeInOutCubic, linear } from '@revideo/core';

yield* circle().x(200, 1, easeInOutCubic); // smooth start and end
yield* circle().x(200, 1, linear);          // constant speed
```

**Manim equivalent:** `rate_func=smooth` and `rate_func=linear`

We'll cover all easing functions in [Chapter 5](05-easing-functions.md).

### Where to See All Animatable Properties

Every node type has different animatable properties. The full list is in the [Revideo API docs](https://docs.re.video/). The most common:

| Property | Type | Example |
|---|---|---|
| `x`, `y` | number | `node().x(200, 1)` |
| `position` | [x, y] | `node().position([200, 100], 1)` |
| `rotation` | degrees | `node().rotation(90, 1)` |
| `scale` | number | `node().scale(2, 0.5)` |
| `opacity` | 0–1 | `node().opacity(0, 0.5)` |
| `fill` | color | `node().fill('red', 0.5)` |
| `stroke` | color | `node().stroke('white', 0.5)` |
| `lineWidth` | number | `node().lineWidth(5, 0.5)` |
| `width`, `height` | number | `node().width(400, 1)` |
| `radius` | number | `node().radius(20, 0.5)` |
| `end` | 0–1 | `line().end(1, 1)` (draw effect) |

---

[← Installation](00-installation.md) | [Basic Node Properties →](02-basic-node-properties.md)
