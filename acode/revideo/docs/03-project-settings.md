# Project Settings

[← Basic Node Properties](02-basic-node-properties.md) | [Layers →](04-layers.md)

---

## Resolution and Background

Settings are defined in `project.tsx`:

```tsx
export default makeProject({
  scenes: [myScene],
  settings: {
    shared: {
      background: '#141414',           // scene background color
      size: { x: 1920, y: 1080 },     // resolution in pixels
    },
  },
});
```

Common resolutions:

| Name | Size | Manim Equivalent |
|---|---|---|
| 480p | `{x: 854, y: 480}` | `-pql` (low) |
| 720p | `{x: 1280, y: 720}` | `-pqm` (medium) |
| 1080p | `{x: 1920, y: 1080}` | `-pqh` (high) |
| 4K | `{x: 3840, y: 2160}` | `-pqk` (4K) |

## Render Config

The render script (`src/render.ts`) controls output settings:

```tsx
import { renderVideo } from '@revideo/renderer';

async function render() {
  const file = await renderVideo({
    projectFile: './src/project.tsx',
    settings: { logProgress: true },
  });
  console.log(`Rendered to ${file}`);
}

render();
```

## Editor vs CLI Rendering

| Method | Command | Use Case |
|---|---|---|
| Editor | `npm start` | Interactive preview, scrubbing, live reload |
| CLI | `npm run render` | Final output, CI/CD, headless rendering |

The editor is for development. The CLI is for production.

**Manim equivalent:** The editor is like Manim's `-p` (preview) flag but interactive. The CLI render is like `manim script.py SceneName -qh`.

---

[← Basic Node Properties](02-basic-node-properties.md) | [Layers →](04-layers.md)
