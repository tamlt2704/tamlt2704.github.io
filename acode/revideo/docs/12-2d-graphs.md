# 2D Graphs & Shapes

[← Revideo Utilities](11-utilities.md) | [Generators & Flow Control →](13-generators.md)

---

## Basic Shapes

```tsx
import { Circle, Rect, Line } from '@revideo/2d';

// Circle
<Circle size={200} fill="blue" stroke="white" lineWidth={2} />

// Rectangle
<Rect width={300} height={200} fill="red" radius={12} />

// Square (equal width/height)
<Rect size={200} fill="green" />

// Line
<Line points={[[-200, 0], [200, 0]]} stroke="white" lineWidth={3} />

// Line with multiple points (polyline)
<Line points={[[-200, 100], [0, -100], [200, 100]]}
      stroke="yellow" lineWidth={2} />
```

**Manim equivalent:**

```python
Circle(radius=1, color=BLUE)
Rectangle(width=3, height=2, color=RED)
Square(side_length=2, color=GREEN)
Line(LEFT * 2, RIGHT * 2, color=WHITE)
```

## Drawing Animation (Create equivalent)

Use the `end` property to animate drawing a shape:

```tsx
const line = createRef<Line>();
view.add(
  <Line ref={line} points={[[-300, 0], [300, 0]]}
        stroke="white" lineWidth={3} end={0} />
);

// Draw the line from 0% to 100%
yield* line().end(1, 1);
```

`end` goes from 0 (nothing drawn) to 1 (fully drawn). This is the equivalent of Manim's `Create(line)`.

For shapes:

```tsx
const circle = createRef<Circle>();
view.add(
  <Circle ref={circle} size={200} stroke="blue" lineWidth={3}
          fill={null} end={0} />
);

yield* circle().end(1, 1); // draws the circle outline
```

## Bezier Curves

```tsx
<Line
  points={[[-200, 0], [-100, -200], [100, 200], [200, 0]]}
  stroke="cyan"
  lineWidth={2}
  smoothness={1}  // 0 = straight segments, 1 = smooth bezier
/>
```

## Custom Shapes with Points

```tsx
// Triangle
<Line
  points={[[0, -100], [100, 100], [-100, 100]]}
  closed={true}
  fill="orange"
  stroke="white"
  lineWidth={2}
/>

// Star (computed points)
const starPoints = Array.from({ length: 10 }, (_, i) => {
  const angle = (i * Math.PI * 2) / 10 - Math.PI / 2;
  const r = i % 2 === 0 ? 100 : 50;
  return [Math.cos(angle) * r, Math.sin(angle) * r] as [number, number];
});

<Line points={starPoints} closed fill="gold" stroke="white" lineWidth={2} />
```

## Arrows

```tsx
<Line
  points={[[-200, 0], [200, 0]]}
  stroke="white"
  lineWidth={3}
  endArrow
  arrowSize={15}
/>
```

## Grid / Axes

Revideo doesn't have built-in `Axes` like Manim. Build them with lines:

```tsx
function Axes({ width = 800, height = 600 }) {
  return (
    <>
      {/* X axis */}
      <Line points={[[-width/2, 0], [width/2, 0]]}
            stroke="#555" lineWidth={2} endArrow arrowSize={10} />
      {/* Y axis */}
      <Line points={[[0, height/2], [0, -height/2]]}
            stroke="#555" lineWidth={2} endArrow arrowSize={10} />
      {/* Grid lines */}
      {Array.from({ length: 9 }, (_, i) => {
        const x = (i - 4) * (width / 8);
        return <Line key={i} points={[[x, -height/2], [x, height/2]]}
                     stroke="#222" lineWidth={1} />;
      })}
    </>
  );
}
```

## Plotting Functions

```tsx
const fn = (x: number) => Math.sin(x) * 100;
const points: [number, number][] = [];
for (let x = -300; x <= 300; x += 5) {
  points.push([x, -fn(x / 50)]); // negate y because screen y is inverted
}

<Line points={points} stroke="cyan" lineWidth={2} />
```

**Manim equivalent:**

```python
axes = Axes(x_range=[-6, 6], y_range=[-1.5, 1.5])
graph = axes.plot(lambda x: np.sin(x), color=BLUE)
self.play(Create(graph))
```

---

[← Revideo Utilities](11-utilities.md) | [Generators & Flow Control →](13-generators.md)
