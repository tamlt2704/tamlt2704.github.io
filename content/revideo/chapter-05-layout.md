# Layout & Text

[prev: Signals & Reactivity](chapter-04-signals.md) | [next: Advanced Motion](chapter-06-motion.md)

## Layout Node (Flexbox)

The Layout node uses flexbox for automatic positioning of children.

```typescript
import {makeScene2D, Layout, Rect} from '@revideo/2d';
import {waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  view.add(
    <Layout direction="row" gap={20} alignItems="center">
      <Rect width={100} height={100} fill="#e13238" radius={8} />
      <Rect width={100} height={150} fill="#4285f4" radius={8} />
      <Rect width={100} height={80} fill="#fbbc04" radius={8} />
    </Layout>
  );

  yield* waitFor(2);
});
```

## Direction, Gap, Padding

```typescript
import {makeScene2D, Layout, Rect} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const layout = (
    <Layout direction="column" gap={16} padding={32} width={300}>
      <Rect height={60} fill="#e13238" radius={4} />
      <Rect height={60} fill="#4285f4" radius={4} />
      <Rect height={60} fill="#fbbc04" radius={4} />
    </Layout>
  );
  view.add(layout);

  yield* layout.direction('row', 0.8);
  yield* layout.gap(40, 0.5);
});
```

## Justify and Align

```typescript
import {makeScene2D, Layout, Circle} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const layout = (
    <Layout
      direction="row"
      width={600}
      height={300}
      justifyContent="space-between"
      alignItems="center"
    >
      <Circle size={60} fill="#e13238" />
      <Circle size={60} fill="#4285f4" />
      <Circle size={60} fill="#fbbc04" />
    </Layout>
  );
  view.add(layout);

  yield* layout.justifyContent('center', 0.8);
  yield* layout.gap(20, 0.5);
  yield* layout.alignItems('start', 0.5);
});
```

## Text with Txt Node

```typescript
import {makeScene2D, Txt} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const title = (
    <Txt
      text="Hello Revideo"
      fontSize={64}
      fontFamily="JetBrains Mono"
      fontWeight={700}
      fill="#fff"
    />
  );
  view.add(title);

  yield* title.fontSize(96, 0.5);
  yield* title.fill('#4285f4', 0.5);
  yield* title.text('Goodbye', 0.8);
});
```

## Code Node with Syntax Highlighting

```typescript
import {makeScene2D, Code, lines} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const code = (
    <Code
      fontSize={28}
      code={`function greet(name: string) {\n  return "Hello, " + name;\n}`}
    />
  );
  view.add(code);

  // Highlight a line
  yield* code.selection(lines(1), 0.5);

  // Insert code
  yield* code.code.insert([1, 2], '\n  console.log("greeting");', 0.6);
});
```

## Code Transitions

```typescript
import {makeScene2D, Code} from '@revideo/2d';
import {waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  const code = <Code fontSize={24} code={`const x = 1;`} />;
  view.add(code);

  yield* waitFor(0.5);

  // Replace entire code block with animation
  yield* code.code(`const x = 1;\nconst y = 2;\nconst sum = x + y;`, 0.8);

  yield* waitFor(0.5);

  // Remove a line
  yield* code.code.remove([1, 0], [1, 14], 0.6);
});
```
