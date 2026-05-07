# Installation

[← Index](README.md) | [Basic Elements →](01-basic-elements.md)

---

## Requirements

- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **npm** (comes with Node)
- **FFmpeg** — required for final video rendering

```bash
# Verify
node -v    # → v22.x.x
npm -v     # → 10.x.x
ffmpeg -version
```

## Create a New Project

```bash
npm init @revideo@latest my-video
cd my-video
npm install
```

This scaffolds:

```
my-video/
├── src/
│   ├── project.tsx      ← project config (scenes, settings)
│   ├── render.ts        ← headless render script
│   └── scenes/
│       └── example.tsx  ← your first scene
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Run the Editor

```bash
npm start
```

This opens the **Revideo Editor** at `http://localhost:9000/` — a browser-based preview where you can scrub through your animation, adjust timing, and see changes in real time.

## Render to Video

```bash
npm run render
```

This compiles TypeScript, runs the render script, and outputs an `.mp4` file.

## Manual Setup (From Scratch)

If you prefer to set up manually:

```bash
mkdir my-video && cd my-video
npm init -y
npm install @revideo/core @revideo/2d @revideo/renderer
npm install -D @revideo/ui @revideo/cli typescript vite
```

Create `tsconfig.json`:

```json
{
  "extends": "@revideo/2d/tsconfig.project.json",
  "include": ["src"],
  "compilerOptions": {
    "noEmit": false,
    "outDir": "dist",
    "module": "CommonJS",
    "skipLibCheck": true
  }
}
```

Create `package.json` scripts:

```json
{
  "scripts": {
    "start": "revideo editor --projectFile ./src/project.tsx",
    "render": "tsc && node dist/render.js"
  }
}
```

## Packages Overview

| Package | Purpose |
|---|---|
| `@revideo/core` | Core engine: timing, signals, generators, project config |
| `@revideo/2d` | 2D nodes: Rect, Circle, Txt, Line, Img, Video, Audio |
| `@revideo/renderer` | Headless rendering to video files |
| `@revideo/ui` | Browser-based editor UI (dev only) |
| `@revideo/cli` | CLI commands: `revideo editor`, `revideo render` |

## Manim Equivalent

In Manim, you install with `pip install manim` and render with `manim script.py SceneName -pql`.

In Revideo, you install with `npm install` and render with `npm run render`. The editor (`npm start`) is the equivalent of Manim's `-p` (preview) flag, but interactive.

---

[← Index](README.md) | [Basic Elements →](01-basic-elements.md)
