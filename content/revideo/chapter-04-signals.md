# Signals & Reactivity

[prev: Animations](chapter-03-animations.md) | [next: Layout & Text](chapter-05-layout.md)

## createSignal

Signals are reactive values. When a signal changes, anything depending on it updates automatically.

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {createSignal} from '@revideo/core';

export default makeScene2D(function* (view) {
  const radius = createSignal(50);

  view.add(<Circle size={() => radius() * 2} fill="#e13238" />);

  yield* radius(150, 1);
  yield* radius(50, 1);
});
```

## Computed Signals

Computed signals derive values from other signals automatically.

```typescript
import {makeScene2D, Rect, Txt} from '@revideo/2d';
import {createSignal} from '@revideo/core';

export default makeScene2D(function* (view) {
  const progress = createSignal(0);

  view.add(
    <Rect
      width={() => progress() * 400}
      height={40}
      fill="#4285f4"
      x={() => (progress() * 400) / 2 - 200}
    />
  );

  view.add(
    <Txt
      text={() => `${Math.round(progress() * 100)}%`}
      fill="#fff"
      fontSize={32}
      y={60}
    />
  );

  yield* progress(1, 2);
});
```

## Signal Dependencies

When one signal references another, changes propagate through the chain.

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {createSignal} from '@revideo/core';

export default makeScene2D(function* (view) {
  const count = createSignal(3);
  const spacing = createSignal(100);

  for (let i = 0; i < 5; i++) {
    view.add(
      <Circle
        size={60}
        fill="#fbbc04"
        x={() => (i - (count() - 1) / 2) * spacing()}
        opacity={() => (i < count() ? 1 : 0)}
      />
    );
  }

  yield* count(5, 1);
  yield* spacing(150, 0.8);
  yield* count(2, 1);
});
```

## Binding Signals to Properties

Pass a function (closure over a signal) to any property for reactive binding.

```typescript
import {makeScene2D, Rect} from '@revideo/2d';
import {createSignal} from '@revideo/core';

export default makeScene2D(function* (view) {
  const hue = createSignal(0);

  view.add(
    <Rect
      width={200}
      height={200}
      fill={() => `hsl(${hue()}, 70%, 50%)`}
      rotation={() => hue()}
    />
  );

  yield* hue(360, 3);
});
```

## useScene and useRandom

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {useRandom, waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  const random = useRandom();

  // Deterministic random - same result every render
  for (let i = 0; i < 20; i++) {
    view.add(
      <Circle
        size={random.nextInt(20, 60)}
        fill={`hsl(${random.nextInt(0, 360)}, 70%, 60%)`}
        x={random.nextInt(-400, 400)}
        y={random.nextInt(-250, 250)}
        opacity={0}
      />
    );
  }

  for (const child of view.children()) {
    yield* child.opacity(1, 0.1);
  }

  yield* waitFor(1);
});
```
