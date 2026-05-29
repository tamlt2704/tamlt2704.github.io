# Setup

[prev: Overview](chapter-00-overview.md) | [next: Scenes & Nodes](chapter-02-scenes.md)

## Create a New Project

```typescript
// Run in your terminal:
// npm create @revideo@latest
// cd my-revideo-project
// npm install
// npm start
```

This scaffolds a project and opens the editor at `http://localhost:9000`.

## Project Structure

```
my-revideo-project/
├── src/
│   ├── project.ts        # Project entry point
│   └── scenes/
│       └── example.tsx   # Scene files (generator functions)
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Project Entry Point

```typescript
// src/project.ts
import { makeProject } from "@revideo/core";
import example from "./scenes/example?scene";

export default makeProject({
  scenes: [example],
});
```

## Your First Scene

```typescript
// src/scenes/example.tsx
import {makeScene2D, Circle} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const circle = <Circle size={200} fill="#e13238" />;
  view.add(circle);

  yield* circle.scale(1.5, 0.5);
  yield* circle.scale(1, 0.5);
});
```

## Running the Editor

Start the development server:

```typescript
// npm start
// Opens http://localhost:9000
```

The editor UI has three main panels:

- **Preview** - Live canvas showing your animation
- **Timeline** - Scrub through frames, see duration
- **Inspector** - View and tweak node properties in real time

Hot reload is built in. Save a file and the preview updates instantly without restarting.

## Rendering to mp4

```typescript
// From the editor UI: click the Render button
// Or from CLI:
// npx revideo render
```

This outputs an mp4 file in the `output/` directory.

## Configuration

```typescript
// src/project.ts
import { makeProject } from "@revideo/core";
import example from "./scenes/example?scene";

export default makeProject({
  scenes: [example],
  settings: {
    resolution: { x: 1920, y: 1080 },
    frameRate: 60,
    background: "#141414",
  },
});
```
