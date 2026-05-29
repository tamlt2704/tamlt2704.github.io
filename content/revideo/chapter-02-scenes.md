# Scenes & Nodes

[prev: Setup](chapter-01-setup.md) | [next: Animations](chapter-03-animations.md)

## Scene Generator Function

Every scene is a generator function wrapped in `makeScene2D`. The `yield*` keyword pauses execution until an animation or wait completes. This is the core concept of Revideo.

```typescript
import {makeScene2D, Rect} from '@revideo/2d';
import {waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  const rect = <Rect width={200} height={200} fill="#e13238" />;
  view.add(rect);

  // yield* pauses here for 1 second
  yield* waitFor(1);

  // then animates x over 0.6 seconds
  yield* rect.x(300, 0.6);
});
```

## Node Types

```typescript
import {makeScene2D, Rect, Circle, Line, Txt, Img} from '@revideo/2d';
import {waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  // Rectangle
  view.add(<Rect width={200} height={100} fill="#4285f4" radius={8} />);

  // Circle
  view.add(<Circle size={150} fill="#ea4335" x={-300} />);

  // Line
  view.add(
    <Line
      points={[[-200, 100], [0, -100], [200, 100]]}
      stroke="#fbbc04"
      lineWidth={4}
    />
  );

  // Text
  view.add(<Txt text="Hello Revideo" fontSize={48} fill="#fff" y={200} />);

  // Image
  view.add(<Img src="/logo.png" width={100} x={300} />);

  yield* waitFor(2);
});
```

## Positioning

Nodes are positioned relative to the center of the canvas (0, 0).

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  // Position with x, y
  view.add(<Circle size={80} fill="#e13238" x={-200} y={-100} />);

  // Position with array
  view.add(<Circle size={80} fill="#4285f4" position={[200, 100]} />);

  yield* waitFor(1);
});
```

## Size, Rotation, Opacity

```typescript
import {makeScene2D, Rect} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const rect = (
    <Rect width={200} height={200} fill="#4285f4" rotation={0} opacity={1} />
  );
  view.add(rect);

  yield* rect.rotation(360, 1);
  yield* rect.opacity(0.3, 0.5);
  yield* rect.size([400, 100], 0.8);
});
```

## Fill and Stroke

```typescript
import {makeScene2D, Circle} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const circle = (
    <Circle size={200} fill="#e13238" stroke="#fff" lineWidth={4} />
  );
  view.add(circle);

  yield* circle.fill('#4285f4', 1);
  yield* circle.lineWidth(12, 0.5);
});
```

## Nesting Nodes

Children inherit parent transforms.

```typescript
import {makeScene2D, Rect, Circle} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const group = (
    <Rect layout direction="row" gap={20}>
      <Circle size={80} fill="#e13238" />
      <Circle size={80} fill="#4285f4" />
      <Circle size={80} fill="#fbbc04" />
    </Rect>
  );
  view.add(group);

  // Rotating the parent rotates all children
  yield* group.rotation(360, 2);
});
```
