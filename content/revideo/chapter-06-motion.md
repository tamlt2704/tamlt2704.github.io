# Advanced Motion

[prev: Layout & Text](chapter-05-layout.md) | [next: Media](chapter-07-media.md)

## Following a Path

```typescript
import {makeScene2D, Circle, Line} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const path = (
    <Line
      points={[[-300, 200], [-100, -200], [100, 200], [300, -200]]}
      stroke="#333"
      lineWidth={2}
    />
  );
  view.add(path);

  const dot = <Circle size={30} fill="#e13238" />;
  view.add(dot);

  // Move along the path from 0% to 100%
  yield* dot.position(path.getPointAtPercentage(0).position, 0);
  for (let i = 0; i <= 1; i += 0.01) {
    dot.position(path.getPointAtPercentage(i).position);
    yield;
  }
});
```

## Spring Physics

```typescript
import {makeScene2D, Rect} from '@revideo/2d';
import {spring, PossibleVector2} from '@revideo/core';

export default makeScene2D(function* (view) {
  const rect = <Rect width={100} height={100} fill="#4285f4" />;
  view.add(rect);

  // Spring with custom stiffness and damping
  yield* rect.x(300, 1, spring(2, 80, 10));
  yield* rect.y(-200, 1, spring(2, 60, 8));
  yield* rect.position([0, 0] as PossibleVector2, 1, spring());
});
```

## Custom Tweening

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {tween, map} from '@revideo/core';

export default makeScene2D(function* (view) {
  const circle = <Circle size={100} fill="#e13238" />;
  view.add(circle);

  // Custom tween with manual value mapping
  yield* tween(2, value => {
    circle.x(map(-300, 300, value));
    circle.y(Math.sin(value * Math.PI * 4) * 100);
  });
});
```

## Camera (View Node)

```typescript
import {makeScene2D, Circle, Rect} from '@revideo/2d';

export default makeScene2D(function* (view) {
  // Add scene content
  view.add(<Rect width={800} height={600} stroke="#333" lineWidth={2} />);
  view.add(<Circle size={60} fill="#e13238" x={200} y={100} />);
  view.add(<Circle size={60} fill="#4285f4" x={-200} y={-100} />);

  // Zoom in
  yield* view.scale(2, 1);

  // Pan to a point
  yield* view.position([-200, -100], 1);

  // Zoom out
  yield* view.scale(1, 1);
  yield* view.position([0, 0], 0.5);
});
```

## Scene Transitions

```typescript
// src/scenes/sceneA.tsx
import {makeScene2D, Rect} from '@revideo/2d';
import {fadeTransition, waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  yield* fadeTransition(0.5);

  view.add(<Rect width={400} height={300} fill="#e13238" radius={16} />);
  yield* waitFor(2);
});
```

```typescript
// src/scenes/sceneB.tsx
import {makeScene2D, Circle} from '@revideo/2d';
import {slideTransition, Direction, waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  yield* slideTransition(Direction.Right, 0.5);

  view.add(<Circle size={300} fill="#4285f4" />);
  yield* waitFor(2);
});
```

```typescript
// src/project.ts - wire up multiple scenes
import { makeProject } from "@revideo/core";
import sceneA from "./scenes/sceneA?scene";
import sceneB from "./scenes/sceneB?scene";

export default makeProject({
  scenes: [sceneA, sceneB],
});
```

## Motion Trails

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  const main = <Circle size={40} fill="#e13238" />;
  view.add(main);

  // Create trail by spawning fading copies
  for (let i = 0; i < 60; i++) {
    const trail = <Circle size={40} fill="#e13238" opacity={0.3} />;
    trail.position(main.position());
    view.add(trail);
    trail.opacity(0, 0.5).then(() => trail.remove());

    yield* main.x(Math.sin(i * 0.1) * 300, 0.03);
    main.y(Math.cos(i * 0.1) * 200);
  }

  yield* waitFor(1);
});
```
