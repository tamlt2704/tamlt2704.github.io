# Chapter 63: Revideo (Motion Canvas) — Create Videos with Code

## What you'll learn

- What Revideo/Motion Canvas is (programmatic video creation — no After Effects needed)
- Core concepts: scenes, signals, animations, timing
- Building animated videos: text, shapes, code blocks, diagrams
- Transitions: fade, slide, scale, custom easings
- Creating tutorial/explainer videos programmatically
- Rendering to MP4/WebM for YouTube
- Why developers love this (version-controlled, reproducible, reusable)

---

## PART 1: What is Motion Canvas / Revideo?

## 63.1 The concept

```
TRADITIONAL VIDEO EDITING:          PROGRAMMATIC VIDEO:
  After Effects / Premiere          Motion Canvas / Revideo
  
  • Drag & drop timeline            • Write TypeScript code
  • Manual keyframes                 • Define animations as functions
  • Click to position things         • Coordinates & math
  • Export → change → re-export      • Change code → re-render (instant)
  • Hard to version control          • Git-friendly (it's just .ts files)
  • Non-reproducible                 • Deterministic (same code = same video)
  • Can't template/loop              • Loops, variables, functions!
  
PERFECT FOR:
  • Algorithm visualisation videos (your project!)
  • Programming tutorials with animated code
  • Technical explainers (system design diagrams that build up)
  • Data visualisation animations
  • Math/science animations (3Blue1Brown style)
  • Automated video generation (parameterised templates)
```

## 63.2 Motion Canvas vs Revideo

```
MOTION CANVAS (original — MIT licence):
  • Created by Aarthificial (2023)
  • Web-based editor + TypeScript API
  • Renders in browser
  • Active open-source community

REVIDEO (fork — extends Motion Canvas):
  • Fork focused on headless rendering + automation
  • Better for: batch rendering, CI/CD pipelines, API-driven video
  • Adds: audio support, server-side rendering, parameterised templates
  • Same core API as Motion Canvas

FOR LEARNING: they share the same concepts and API.
This chapter covers both (syntax is nearly identical).
```

## 63.3 Setup

```bash
# Motion Canvas
npm create @motion-canvas@latest my-animation
cd my-animation
npm install
npm start
# Opens browser editor at http://localhost:9000

# Revideo (if you want headless/server rendering)
npm create @revideo/create@latest my-video
cd my-video
npm install
npm start
```

**Project structure:**
```
my-animation/
├── src/
│   ├── project.ts          ← Project configuration
│   └── scenes/
│       ├── example.tsx     ← Your animation (one file per scene)
│       └── intro.tsx
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## PART 2: Core Concepts

## 63.4 Scenes and the yield model

```tsx
// src/scenes/hello.tsx
import { makeScene2D } from "@motion-canvas/2d";
import { createRef } from "@motion-canvas/core";
import { Txt } from "@motion-canvas/2d/components";

export default makeScene2D(function* (view) {
  // Generator function — each yield is a pause point (waits for animation)
  
  const title = createRef<Txt>();
  
  // Add text to the scene
  view.add(
    <Txt
      ref={title}
      text="Hello, World!"
      fontSize={80}
      fontFamily="JetBrains Mono"
      fill="#ffffff"
    />
  );
  
  // Animate (yield = wait for this to finish)
  yield* title().opacity(0).opacity(1, 1);  // fade in over 1 second
  
  yield* waitFor(2);  // wait 2 seconds
  
  yield* title().opacity(0, 0.5);  // fade out over 0.5s
});
```

**The generator model:**
- `function*` = generator (can pause and resume)
- `yield*` = "play this animation and wait for it to complete"
- Animations are sequential by default (one after another)
- Use `all()` for parallel animations

## 63.5 Signals — reactive values

```tsx
import { createSignal } from "@motion-canvas/core";

export default makeScene2D(function* (view) {
  // Signals are reactive values (like React state but for animation)
  const progress = createSignal(0);
  const count = createSignal(0);
  
  // A text that reacts to signal changes
  view.add(
    <Txt
      text={() => `Count: ${count().toFixed(0)}`}
      fontSize={60}
      fill="#ffffff"
    />
  );
  
  // Animate the signal from 0 to 100 over 3 seconds
  yield* count(100, 3);
  // The text automatically updates as count changes!
});
```

## 63.6 Timing and easing

```tsx
import { easeInOutCubic, linear, easeOutBounce, spring } from "@motion-canvas/core";

// Duration + easing
yield* rect().x(400, 1, easeInOutCubic);     // move right, 1s, smooth
yield* rect().scale(2, 0.5, easeOutBounce);  // scale up, bounce
yield* rect().rotation(360, 2, linear);       // constant speed rotation

// Spring physics (no duration — settles naturally)
yield* rect().x.spring(400);

// Sequential animations
yield* rect().x(200, 0.5);    // first this
yield* rect().y(100, 0.5);    // then this

// Parallel animations (both happen at once)
yield* all(
  rect().x(200, 1),
  rect().y(100, 1),
  rect().opacity(0.5, 1),
);

// Staggered (parallel with delays)
yield* sequence(0.2,
  circle1().scale(1.5, 0.5),
  circle2().scale(1.5, 0.5),
  circle3().scale(1.5, 0.5),
);
// Each starts 0.2s after the previous
```

---

## PART 3: Drawing Things

## 63.7 Shapes

```tsx
import { Rect, Circle, Line, Polygon } from "@motion-canvas/2d/components";

export default makeScene2D(function* (view) {
  // Rectangle
  const rect = createRef<Rect>();
  view.add(
    <Rect
      ref={rect}
      width={200}
      height={150}
      fill="#3b82f6"
      radius={12}           // rounded corners
      stroke="#1d4ed8"
      lineWidth={3}
    />
  );

  // Circle
  view.add(
    <Circle
      x={300}
      y={0}
      size={100}
      fill="#22c55e"
    />
  );

  // Line / Arrow
  view.add(
    <Line
      points={[[-200, 0], [200, 0]]}
      stroke="#f59e0b"
      lineWidth={4}
      endArrow
      arrowSize={12}
    />
  );

  // Polygon
  view.add(
    <Polygon
      sides={6}             // hexagon
      size={120}
      fill="#8b5cf6"
      x={-300}
    />
  );

  // Animate: grow the rectangle
  yield* rect().size([400, 300], 1, easeInOutCubic);
  yield* rect().fill("#ef4444", 0.5);  // change colour
  yield* rect().rotation(45, 1);        // rotate
});
```

## 63.8 Text and code blocks

```tsx
import { Txt, Code, Lines } from "@motion-canvas/2d/components";
import { CODE } from "@motion-canvas/2d";

export default makeScene2D(function* (view) {
  // Styled text
  const heading = createRef<Txt>();
  view.add(
    <Txt
      ref={heading}
      text="Bubble Sort"
      fontSize={72}
      fontWeight={700}
      fill="#f8fafc"
      y={-200}
    />
  );

  // Code block (syntax highlighted!)
  const code = createRef<Code>();
  view.add(
    <Code
      ref={code}
      fontSize={28}
      fontFamily="JetBrains Mono"
      code={`\
function bubbleSort(arr) {
  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < arr.length - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j+1]] = [arr[j+1], arr[j]];
      }
    }
  }
}`}
    />
  );

  // Animate code appearing line by line
  yield* code().opacity(0).opacity(1, 1);

  // Highlight a specific line
  yield* code().selection(lines(3, 5), 0.3);  // highlight lines 3-5

  // Change code (animated diff!)
  yield* code().code(`\
function bubbleSort(arr) {
  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < arr.length - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        swap(arr, j, j + 1);  // extracted to function
      }
    }
  }
}`, 1);
  // The change animates! Old code fades out, new code fades in.
});
```

## 63.9 Layouts (Flexbox in video!)

```tsx
import { Layout, Rect, Txt } from "@motion-canvas/2d/components";

export default makeScene2D(function* (view) {
  // Flexbox-style layout (like CSS!)
  const container = createRef<Layout>();
  view.add(
    <Layout
      ref={container}
      direction="row"
      gap={20}
      alignItems="center"
    >
      <Rect width={100} height={100} fill="#ef4444" radius={8} />
      <Rect width={100} height={100} fill="#f59e0b" radius={8} />
      <Rect width={100} height={100} fill="#22c55e" radius={8} />
      <Rect width={100} height={100} fill="#3b82f6" radius={8} />
      <Rect width={100} height={100} fill="#8b5cf6" radius={8} />
    </Layout>
  );

  // Animate layout change
  yield* container().direction("column", 1);  // rearrange to vertical!
  yield* container().gap(40, 0.5);            // increase spacing
});
```

---

## PART 4: Build — Algorithm Visualisation Video

## 63.10 Animated bar chart (sorting visualisation)

```tsx
import { makeScene2D } from "@motion-canvas/2d";
import { createRef, all, sequence, waitFor } from "@motion-canvas/core";
import { Rect, Txt, Layout } from "@motion-canvas/2d/components";

export default makeScene2D(function* (view) {
  const data = [38, 27, 43, 3, 9, 82, 10];
  const maxVal = Math.max(...data);
  const barWidth = 80;
  const maxHeight = 400;
  const colors = data.map(() => "#3b82f6");

  // Create bar references
  const bars = data.map(() => createRef<Rect>());
  const labels = data.map(() => createRef<Txt>());

  // Title
  const title = createRef<Txt>();
  view.add(
    <Txt ref={title} text="Bubble Sort" fontSize={56} fill="#f8fafc" y={-280} fontWeight={700} />
  );

  // Add bars
  const barGroup = createRef<Layout>();
  view.add(
    <Layout ref={barGroup} direction="row" gap={12} alignItems="end" y={100}>
      {data.map((val, i) => {
        const height = (val / maxVal) * maxHeight;
        return (
          <Layout direction="column" alignItems="center" gap={8}>
            <Txt ref={labels[i]} text={String(val)} fontSize={24} fill="#f8fafc" />
            <Rect
              ref={bars[i]}
              width={barWidth}
              height={height}
              fill="#3b82f6"
              radius={[8, 8, 0, 0]}
            />
          </Layout>
        );
      })}
    </Layout>
  );

  // Animate bars growing from 0
  yield* sequence(0.1,
    ...bars.map((bar, i) => bar().height(0).height((data[i] / maxVal) * maxHeight, 0.5))
  );

  yield* waitFor(1);

  // Simulate bubble sort — highlight comparing pair
  const arr = [...data];
  for (let i = 0; i < arr.length - 1; i++) {
    for (let j = 0; j < arr.length - i - 1; j++) {
      // Highlight comparing pair
      yield* all(
        bars[j]().fill("#f59e0b", 0.2),
        bars[j + 1]().fill("#f59e0b", 0.2),
      );

      if (arr[j] > arr[j + 1]) {
        // Swap animation
        yield* all(
          bars[j]().x(barWidth + 12, 0.3),    // move right
          bars[j + 1]().x(-(barWidth + 12), 0.3), // move left
        );

        // Swap data
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];

        // Reset positions (bars are now swapped)
        yield* all(
          bars[j]().x(0, 0),
          bars[j + 1]().x(0, 0),
        );

        // Swap refs
        [bars[j], bars[j + 1]] = [bars[j + 1], bars[j]];
        [labels[j], labels[j + 1]] = [labels[j + 1], labels[j]];
      }

      // Reset colour
      yield* all(
        bars[j]().fill("#3b82f6", 0.2),
        bars[j + 1]().fill("#3b82f6", 0.2),
      );
    }
    // Mark sorted
    yield* bars[arr.length - 1 - i]().fill("#22c55e", 0.3);
  }
  yield* bars[0]().fill("#22c55e", 0.3);

  // Final title
  yield* title().text("Sorted! ✓", 0.5);
  yield* waitFor(2);
});
```

## 63.11 Animated diagram (system design)

```tsx
export default makeScene2D(function* (view) {
  // Build a system diagram piece by piece
  
  const client = createRef<Rect>();
  const server = createRef<Rect>();
  const db = createRef<Rect>();
  const arrow1 = createRef<Line>();
  const arrow2 = createRef<Line>();

  // Client box
  view.add(
    <Rect ref={client} x={-400} width={150} height={80} fill="#3b82f6" radius={12} opacity={0}>
      <Txt text="Client" fill="#fff" fontSize={24} />
    </Rect>
  );

  // Server box
  view.add(
    <Rect ref={server} x={0} width={150} height={80} fill="#8b5cf6" radius={12} opacity={0}>
      <Txt text="Server" fill="#fff" fontSize={24} />
    </Rect>
  );

  // Database box
  view.add(
    <Rect ref={db} x={400} width={150} height={80} fill="#22c55e" radius={12} opacity={0}>
      <Txt text="Database" fill="#fff" fontSize={24} />
    </Rect>
  );

  // Arrows
  view.add(
    <Line ref={arrow1} points={[[-300, 0], [-100, 0]]} stroke="#94a3b8" lineWidth={3} endArrow opacity={0} />
  );
  view.add(
    <Line ref={arrow2} points={[[100, 0], [300, 0]]} stroke="#94a3b8" lineWidth={3} endArrow opacity={0} />
  );

  // Animate: build up the diagram step by step
  yield* client().opacity(1, 0.5);
  yield* waitFor(0.3);
  yield* arrow1().opacity(1, 0.3);
  yield* server().opacity(1, 0.5);
  yield* waitFor(0.3);
  yield* arrow2().opacity(1, 0.3);
  yield* db().opacity(1, 0.5);

  yield* waitFor(1);

  // Animate a request flowing through
  const request = createRef<Circle>();
  view.add(
    <Circle ref={request} size={20} fill="#f59e0b" x={-400} opacity={0} />
  );

  yield* request().opacity(1, 0.1);
  yield* request().x(0, 0.8);      // client → server
  yield* request().x(400, 0.8);    // server → database
  yield* request().fill("#22c55e", 0.2);  // response colour
  yield* request().x(0, 0.8);      // database → server
  yield* request().x(-400, 0.8);   // server → client
  yield* request().opacity(0, 0.2);
});
```

---

## PART 5: Rendering & Export

## 63.12 Render to video

```tsx
// Motion Canvas: use the built-in editor
// Click "Render" button → exports frames → FFmpeg combines to video

// Revideo: headless rendering (no browser UI needed)
// src/render.ts
import { renderVideo } from "@revideo/renderer";

await renderVideo({
  projectFile: "./src/project.ts",
  output: "./output/video.mp4",
  settings: {
    fps: 60,
    resolution: { width: 1920, height: 1080 },
    codec: "h264",
    quality: 90,
  },
});
```

```bash
# Motion Canvas: render via CLI
npx motion-canvas render

# Revideo: render headlessly
npx ts-node src/render.ts

# Output: video.mp4 (ready for YouTube upload)
```

## 63.13 Project configuration

```tsx
// src/project.ts
import { makeProject } from "@motion-canvas/core";
import intro from "./scenes/intro?scene";
import bubbleSort from "./scenes/bubbleSort?scene";
import outro from "./scenes/outro?scene";

export default makeProject({
  scenes: [intro, bubbleSort, outro],  // scenes play in order
  background: "#0f172a",               // dark background
  size: { width: 1920, height: 1080 }, // 1080p
  fps: 60,
});
```

## 63.14 Parameterised templates (Revideo)

```tsx
// Generate different videos from the same template!
import { makeScene2D } from "@revideo/2d";
import { Variable } from "@revideo/core";

// Parameters (can be passed in from API/CLI)
const algorithmName = new Variable("Bubble Sort");
const data = new Variable([38, 27, 43, 3, 9]);

export default makeScene2D(function* (view) {
  view.add(
    <Txt text={algorithmName} fontSize={60} fill="#fff" />
  );
  // ... use data.get() for the visualisation
});

// Render with different parameters:
await renderVideo({
  variables: {
    algorithmName: "Merge Sort",
    data: [5, 3, 8, 1, 9, 2],
  },
});
// Same template → different video! Automated content generation.
```

---

## PART 6: Tips & Patterns

## 63.15 Scene transitions

```tsx
import { slideTransition, fadeTransition } from "@motion-canvas/core";

export default makeScene2D(function* (view) {
  // This scene slides in from the right
  yield* slideTransition(Direction.Right, 0.5);

  // ... scene content ...
});

// Or custom transition:
export default makeScene2D(function* (view) {
  // Fade in
  view.opacity(0);
  yield* view.opacity(1, 0.5);

  // ... content ...

  // Fade out at end
  yield* view.opacity(0, 0.5);
});
```

## 63.16 Reusable animation components

```tsx
// Create reusable animated components
function* typewriter(txt: Reference<Txt>, text: string, speed = 0.05) {
  for (let i = 0; i <= text.length; i++) {
    txt().text(text.slice(0, i));
    yield* waitFor(speed);
  }
}

function* flashHighlight(node: Reference<Rect>, color = "#f59e0b") {
  const original = node().fill();
  yield* node().fill(color, 0.2);
  yield* waitFor(0.3);
  yield* node().fill(original, 0.2);
}

// Use in scenes:
yield* typewriter(title, "Hello, World!");
yield* flashHighlight(codeBlock);
```

## 63.17 When to use Motion Canvas / Revideo

| Use case | Good fit? | Alternative |
|----------|-----------|-------------|
| Algorithm visualisation videos | ✅ Perfect | Manim (Python), Remotion (React) |
| Programming tutorials | ✅ Great | Screen recording + editing |
| System design explainers | ✅ Great | Excalidraw + screen record |
| Data viz animation | ✅ Good | D3 + screen capture |
| Marketing/promo videos | ❌ Not ideal | After Effects, Premiere |
| Live-action editing | ❌ No | DaVinci Resolve, Premiere |
| Social media clips | ⚠️ OK (simple ones) | CapCut, Canva |
| Automated video generation | ✅ Perfect (Revideo) | Remotion, Shotstack |

---

## Summary

✅ Motion Canvas / Revideo: create videos by writing TypeScript code
✅ Generator model: `yield*` = "play this animation and wait"
✅ Signals: reactive values that drive animations (like React state)
✅ Shapes: Rect, Circle, Line, Polygon — all animatable
✅ Text & Code: syntax-highlighted code blocks with animated diffs
✅ Layout: Flexbox-style arrangement (direction, gap, alignItems)
✅ Timing: duration, easing functions, `all()` for parallel, `sequence()` for stagger
✅ Built: sorting visualisation + system design diagram (animated)
✅ Rendering: browser editor OR headless (Revideo) → MP4/WebM
✅ Parameterised: same template, different data → automated video generation

## Key takeaways

**Code > Timeline for technical content.** When your video IS code (algorithm animation, diagram building, code walkthrough), it makes sense to CREATE it with code. Changes are a `git diff`, not re-dragging keyframes.

**The generator model is brilliant.** `yield*` makes complex sequential animations readable. "Do this, then do that, then do these in parallel" — reads like a storyboard, executes as animation.

**Parameterised templates = content at scale.** Make ONE sorting visualisation template. Feed it different algorithms and data → generate 10 different videos automatically. This is how educational YouTube channels could work at scale.

**Motion Canvas for interactive editing, Revideo for automation.** Use Motion Canvas when you're designing animations (scrub through, adjust timing). Use Revideo when you want to render headlessly (CI/CD, API-driven, batch generation).

---

→ [Back to Chapter 62: Basic Chinese](./62-BASIC-CHINESE.md)
