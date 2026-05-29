# Animations

[prev: Scenes & Nodes](chapter-02-scenes.md) | [next: Signals & Reactivity](chapter-04-signals.md)

## Tweening Properties

Any node property can be animated by calling it with a target value and duration. `yield*` waits for the animation to finish.

```typescript
import {makeScene2D, Rect} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const rect = <Rect width={100} height={100} fill="#e13238" />;
  view.add(rect);

  yield* rect.x(300, 1);
  yield* rect.scale(2, 0.5);
  yield* rect.x(0, 1);
});
```

## Easing Functions

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {easeInOutCubic, linear, easeOutBounce, spring} from '@revideo/core';

export default makeScene2D(function* (view) {
  const circle = <Circle size={100} fill="#4285f4" x={-400} />;
  view.add(circle);

  // Default easing
  yield* circle.x(400, 1);
  yield* circle.x(-400, 0);

  // Linear - constant speed
  yield* circle.x(400, 1, linear);
  yield* circle.x(-400, 0);

  // Bounce
  yield* circle.x(400, 1, easeOutBounce);
  yield* circle.x(-400, 0);

  // Spring physics
  yield* circle.x(400, 1, spring());
});
```

## Parallel Animations with all()

```typescript
import {makeScene2D, Rect} from '@revideo/2d';
import {all} from '@revideo/core';

export default makeScene2D(function* (view) {
  const rect = <Rect width={100} height={100} fill="#e13238" />;
  view.add(rect);

  yield* all(
    rect.x(300, 1),
    rect.rotation(360, 1),
    rect.fill('#4285f4', 1),
  );
});
```

## Sequential Animations with chain()

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {chain} from '@revideo/core';

export default makeScene2D(function* (view) {
  const circle = <Circle size={100} fill="#e13238" />;
  view.add(circle);

  yield* chain(
    circle.x(200, 0.5),
    circle.y(200, 0.5),
    circle.x(-200, 0.5),
    circle.y(-200, 0.5),
  );
});
```

## Staggered Animations with sequence()

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {sequence} from '@revideo/core';

export default makeScene2D(function* (view) {
  const circles = [
    <Circle size={80} fill="#e13238" y={300} x={-200} />,
    <Circle size={80} fill="#4285f4" y={300} x={0} />,
    <Circle size={80} fill="#fbbc04" y={300} x={200} />,
  ];
  circles.forEach(c => view.add(c));

  // Stagger by 0.2 seconds between each start
  yield* sequence(
    0.2,
    ...circles.map(c => c.y(0, 0.8)),
  );
});
```

## Waiting

```typescript
import {makeScene2D, Rect} from '@revideo/2d';
import {waitFor, waitUntil} from '@revideo/core';

export default makeScene2D(function* (view) {
  const rect = <Rect width={100} height={100} fill="#e13238" />;
  view.add(rect);

  yield* rect.x(200, 0.5);
  yield* waitFor(2);
  yield* rect.x(-200, 0.5);

  // Wait until a named time marker (set in the editor timeline)
  yield* waitUntil('next-section');
  yield* rect.scale(2, 0.5);
});
```

## Looping

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {loop, all} from '@revideo/core';

export default makeScene2D(function* (view) {
  const circle = <Circle size={100} fill="#e13238" />;
  view.add(circle);

  yield* loop(4, function* () {
    yield* all(
      circle.scale(1.5, 0.3),
      circle.fill('#4285f4', 0.3),
    );
    yield* all(
      circle.scale(1, 0.3),
      circle.fill('#e13238', 0.3),
    );
  });
});
```
