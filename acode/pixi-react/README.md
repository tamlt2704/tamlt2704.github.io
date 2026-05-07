# Pixel Art Games with @pixi/react — A Game Jam Story

You're a React developer. You've built dashboards, forms, SPAs. You've never shipped a game. Then your friend **Kai** texts you at 11pm:

> "I entered us in a game jam. 48 hours. Theme: 'Dungeon.' I'll draw the sprites. You code. We're using React."

You say yes. You have no idea what you're getting into.

Kai picks **PixiJS** with **@pixi/react** — a React renderer for the fastest 2D WebGL engine on the web. You get to use components, hooks, and JSX. Kai draws pixel art. You make it move.

Over the next 12 chapters, you'll build **DungeonBit** — a retro pixel art dungeon crawler where you explore rooms, fight slimes, collect keys, and escape. Each chapter solves a real problem you hit during the jam. By the end, you'll have a published game on GitHub Pages and the knowledge to build your next one.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | The Programmer | React dev turned reluctant game dev |
| **Kai** | The Pixel Artist | Draws 16×16 sprites at 2am. "Just make it crispy." |
| **PixiJS** | The Engine | WebGL-powered, 60fps, zero DOM |
| **React** | The Glue | Components, hooks, state — your comfort zone |
| **The Jam Clock** | 48 hours | Ticking. Always ticking. |

## The Roadmap

| Ch | The Crisis | What You Build | What You Learn |
|---|---|---|---|
| 0 | "How do I even set this up?" | Project scaffold + colored Stage | Vite + pixi.js@7 + @pixi/react, project structure |
| 1 | "Put Kai's sprite on screen" | Player sprite rendered | Stage, Sprite, positioning, SCALE_MODES.NEAREST |
| 2 | "Everything's a mess of sprites" | Organized scene layers | Container, nesting, zIndex, sortableChildren |
| 3 | "I need health bars and borders" | UI shapes drawn in code | Graphics component, draw callback, useMemo |
| 4 | "It just sits there" | Moving, bobbing sprites | useTick, delta time, useRef vs useState |
| 5 | "Kai sent a spritesheet" | Animated walk cycle | Spritesheets, AnimatedSprite, frame animation |
| 6 | "How do I move the player?" | Keyboard + touch controls | useEffect listeners, useKeyboard hook |
| 7 | "Build the dungeon rooms" | Tile map renderer | 2D arrays, tile atlas, camera scrolling, culling |
| 8 | "Player walks through walls" | Collision system | AABB, tile-based collision, collectibles |
| 9 | "Track health and score" | Game state + HUD | React context, state management, game over flow |
| 10 | "It needs juice" | Sound + particles | Howler.js, particle system, screen shake |
| 11 | "We need multiple rooms" | Scene manager + levels | Scene switching, level data, transitions |
| 12 | "Ship it before the deadline" | Live on GitHub Pages | Vite build, GitHub Actions, performance checklist |

## How to Read This

Every chapter follows the same loop:

```
  ⏰ The jam clock is ticking
   │
   ▼
  💥 You hit a wall ("how do I render a tile map?")
   │
   ▼
  🧠 You learn the concept (with React analogies)
   │
   ▼
  ⌨️  You write the minimal code to solve it
   │
   ▼
  ✓  It works — Kai sends the next sprite
   │
   ▼
  ⏰ Clock keeps ticking
```

## Tech Stack

| Tool | Why |
|---|---|
| pixi.js@7 | Fastest 2D WebGL renderer, mature, stable |
| @pixi/react | React bindings — components + hooks for PixiJS |
| React 18 | Your comfort zone — components, state, hooks |
| Vite | Fast dev server, instant HMR, clean builds |
| TypeScript (optional) | Types help, but plain JSX works fine |
| Howler.js | Simple cross-browser audio |
| GitHub Pages | Free static hosting, auto-deploy with Actions |

## Prerequisites

- React fundamentals (components, hooks, state, effects)
- Node.js 18+ and npm
- A code editor (VS Code recommended)
- No game dev experience required — React analogies provided throughout
- Kai's pixel art (or any 16×16 / 32×32 sprites — [OpenGameArt](https://opengameart.org) works)

## React Dev → Game Dev Translation

| React Concept | PixiJS Equivalent |
|---|---|
| `<div>` | `<Container>` |
| `<img src="...">` | `<Sprite image="...">` |
| `<canvas>` drawing | `<Graphics draw={...}>` |
| `<p>` text | `<Text text="..." style={...}>` |
| `useEffect` + `requestAnimationFrame` | `useTick(callback)` |
| `useContext` | `useApp()` (access PixiJS app) |
| Component tree | Container hierarchy |
| CSS `z-index` | `zIndex` prop + `sortableChildren` |
| React root | `<Stage>` component |

Start with [Chapter 0: Overview →](chapter-00-overview.md)
