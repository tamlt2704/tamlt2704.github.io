# Projects

[prev: Media](chapter-07-media.md)

## Code Tutorial Video (Typing Effect)

```typescript
import {makeScene2D, Code, Txt, Rect} from '@revideo/2d';
import {waitFor, sequence} from '@revideo/core';

export default makeScene2D(function* (view) {
  view.add(<Txt text="Building a Function" fontSize={48} fill="#fff" y={-280} />);

  const code = <Code fontSize={24} code={``} y={50} />;
  view.add(code);

  // Type code line by line
  yield* code.code(`function add(a: number, b: number)`, 0.8);
  yield* waitFor(0.3);
  yield* code.code(`function add(a: number, b: number) {\n}`, 0.4);
  yield* waitFor(0.3);
  yield* code.code(`function add(a: number, b: number) {\n  return a + b;\n}`, 0.6);

  yield* waitFor(1);

  // Highlight the return line
  yield* code.selection([[1, 0], [1, 15]], 0.5);
  yield* waitFor(2);
});
```

## Data Visualization (Bar Chart Race)

```typescript
import {makeScene2D, Rect, Txt, Layout} from '@revideo/2d';
import {createSignal, all, waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  const data = [
    {label: 'React', value: createSignal(40)},
    {label: 'Vue', value: createSignal(30)},
    {label: 'Svelte', value: createSignal(20)},
  ];

  const bars = data.map((item, i) => (
    <Layout direction="row" gap={10} alignItems="center" y={i * 60 - 60}>
      <Txt text={item.label} fill="#fff" fontSize={20} width={80} />
      <Rect
        height={40}
        width={() => item.value() * 5}
        fill={['#61dafb', '#42b883', '#ff3e00'][i]}
        radius={4}
      />
      <Txt text={() => `${Math.round(item.value())}`} fill="#fff" fontSize={18} />
    </Layout>
  ));
  bars.forEach(b => view.add(b));

  yield* waitFor(1);

  // Animate to new values
  yield* all(
    data[0].value(80, 1),
    data[1].value(65, 1),
    data[2].value(55, 1),
  );

  yield* waitFor(0.5);

  yield* all(
    data[0].value(95, 1),
    data[1].value(70, 1),
    data[2].value(85, 1),
  );

  yield* waitFor(1);
});
```

## Explainer Video (Diagrams Step by Step)

```typescript
import {makeScene2D, Rect, Txt, Line, Circle} from '@revideo/2d';
import {waitFor, sequence} from '@revideo/core';

export default makeScene2D(function* (view) {
  // Step 1: Show boxes
  const client = <Rect width={120} height={60} fill="#4285f4" radius={8} x={-250} opacity={0} />;
  const server = <Rect width={120} height={60} fill="#34a853" radius={8} x={0} opacity={0} />;
  const db = <Rect width={120} height={60} fill="#fbbc04" radius={8} x={250} opacity={0} />;

  view.add(client);
  view.add(server);
  view.add(db);

  view.add(<Txt text="Client" fill="#fff" fontSize={18} x={-250} />);
  view.add(<Txt text="Server" fill="#fff" fontSize={18} x={0} />);
  view.add(<Txt text="Database" fill="#fff" fontSize={18} x={250} />);

  yield* sequence(0.3,
    client.opacity(1, 0.5),
    server.opacity(1, 0.5),
    db.opacity(1, 0.5),
  );

  // Step 2: Show connections
  const arrow1 = <Line points={[[-190, 0], [-60, 0]]} stroke="#fff" lineWidth={2} endArrow opacity={0} />;
  const arrow2 = <Line points={[[60, 0], [190, 0]]} stroke="#fff" lineWidth={2} endArrow opacity={0} />;
  view.add(arrow1);
  view.add(arrow2);

  yield* arrow1.opacity(1, 0.4);
  yield* waitFor(0.5);
  yield* arrow2.opacity(1, 0.4);

  yield* waitFor(2);
});
```

## YouTube Intro

```typescript
import {makeScene2D, Txt, Circle} from '@revideo/2d';
import {all, waitFor, spring} from '@revideo/core';

export default makeScene2D(function* (view) {
  const logo = <Circle size={0} fill="#e13238" />;
  const title = <Txt text="My Channel" fontSize={72} fill="#fff" y={120} opacity={0} />;
  view.add(logo);
  view.add(title);

  // Logo pops in with spring
  yield* logo.size(150, 0.8, spring());

  // Title fades in
  yield* title.opacity(1, 0.5);

  yield* waitFor(1);

  // Exit
  yield* all(
    logo.y(-500, 0.6),
    title.opacity(0, 0.4),
  );
});
```

## Presentation Slides with Animations

```typescript
import {makeScene2D, Rect, Txt, Layout} from '@revideo/2d';
import {slideTransition, Direction, waitFor, sequence} from '@revideo/core';

export default makeScene2D(function* (view) {
  yield* slideTransition(Direction.Right, 0.5);

  // Slide title
  const title = <Txt text="Key Takeaways" fontSize={56} fill="#fff" y={-250} opacity={0} />;
  view.add(title);
  yield* title.opacity(1, 0.4);

  // Bullet points appear one by one
  const bullets = [
    'Code-driven animations are reproducible',
    'Generator functions give precise timing control',
    'Signals enable reactive, dynamic content',
  ];

  const items = bullets.map((text, i) => (
    <Txt text={`• ${text}`} fontSize={28} fill="#ccc" y={-100 + i * 80} x={-200} opacity={0} />
  ));
  items.forEach(item => view.add(item));

  yield* sequence(0.4, ...items.map(item => item.opacity(1, 0.5)));

  yield* waitFor(3);
});
```
