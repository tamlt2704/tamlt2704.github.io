# Defold 101 — A Game Dev Survival Story

You're a web developer. You've built dashboards, APIs, job engines. You've never shipped a game. Then your friend **Mika** texts you at midnight:

> "I entered us in a game jam. 72 hours. Theme drops Friday. You're the programmer."

You say yes. You have no idea what you're getting into.

Mika picks **Defold** — a free, open-source game engine that compiles to iOS, Android, Web, Windows, macOS, and Linux from a single codebase. The engine binary is under 5MB. Games ship in under 2MB. It uses Lua, which you've never written. The editor looks nothing like VS Code.

Over the next 12 chapters, you'll build a complete 2D game from scratch — a space survival shooter where you dodge asteroids, collect fuel, and fight a boss. Each chapter solves a real problem you hit during the jam. By the end, you'll have a published game on itch.io and the knowledge to build your next one.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | The Programmer | Web dev turned reluctant game dev |
| **Mika** | The Artist | Draws pixel art at 3am. "Just make it move." |
| **The Engine** | Defold | Tiny, fast, opinionated. Loves message passing. |
| **Lua** | The Language | Simple, elegant, zero-indexed... wait, one-indexed. |
| **The Jam Clock** | 72 hours | Ticking. Always ticking. |

## The Roadmap

| Ch | The Crisis | What You Build | What You Learn |
|---|---|---|---|
| 0 | "I've never opened this editor" | Project setup + first build | Defold editor, project structure, build targets |
| 1 | "How do I put a sprite on screen?" | Player ship on screen | Game objects, components, collections, atlases |
| 2 | "It just sits there" | Ship that moves | Lua scripting, `init`/`update`/`on_message`, input bindings |
| 3 | "I need bullets" | Shooting mechanics | Factories, spawning, game object lifecycle |
| 4 | "Things need to collide" | Collision system | Physics, collision objects, groups, masks, triggers |
| 5 | "Mika sent 200 frames" | Animated sprites | Tile sources, flip-book animation, sprite states |
| 6 | "Objects need to talk to each other" | Enemy AI + scoring | Message passing, addressing, broadcasts |
| 7 | "I need a menu and HUD" | GUI system | GUI nodes, scripts, layouts, dynamic text |
| 8 | "The level is bigger than the screen" | Camera + scrolling world | Camera component, world coordinates, parallax |
| 9 | "It needs sound" | Audio system | Sound components, groups, ducking, music loops |
| 10 | "We need levels and a boss" | Level management | Collection proxies, loading/unloading, game state |
| 11 | "It's too slow on my phone" | Performance tuning | Profiler, draw calls, texture atlases, object pooling |
| 12 | "Ship it before the deadline" | Published game | HTML5 build, itch.io deploy, mobile builds, App Store |

## How to Read This

Every chapter follows the same loop:

```
  ⏰ The jam clock is ticking
   │
   ▼
  💥 You hit a wall ("how do I make things collide?")
   │
   ▼
  🧠 You learn the concept (with analogies to web dev)
   │
   ▼
  ⌨️  You write the minimal code to solve it
   │
   ▼
  ✓  It works — Mika sends the next art asset
   │
   ▼
  ⏰ Clock keeps ticking
```

No concept appears before you need it. You won't learn about collection proxies until you need multiple levels. You won't touch the profiler until the game stutters on a phone.

## Tech Stack

| Tool | Why |
|---|---|
| Defold 1.9+ | Free, tiny engine, cross-platform, battle-tested |
| Lua 5.1 | Simple scripting, one-indexed arrays, no classes (tables instead) |
| Defold Editor | Built-in scene editor, profiler, debugger |
| Bob (build tool) | Command-line builds for CI/CD |
| itch.io | Free game hosting, HTML5 embed |

## Prerequisites

- A computer (Windows, macOS, or Linux)
- Download [Defold Editor](https://defold.com/download/) — it's a single executable, no installer
- A text editor for Lua (the built-in one works, or use VS Code with the Defold extension)
- No game dev experience required — web dev analogies provided throughout

## Web Dev → Game Dev Translation

| Web Concept | Defold Equivalent |
|---|---|
| DOM elements | Game Objects |
| CSS + HTML | Sprites + Atlases |
| JavaScript | Lua scripts |
| Event listeners | Message passing (`on_message`) |
| React components | Collections (reusable scenes) |
| `requestAnimationFrame` | `update(self, dt)` (called every frame) |
| REST API calls | `msg.post()` (async messages between objects) |
| npm packages | Defold library dependencies |
| `index.html` | `game.project` (entry point config) |
| Browser DevTools | Defold Profiler + Debugger |

Start with [Chapter 0: The Editor →](chapter-00-the-editor.md)
