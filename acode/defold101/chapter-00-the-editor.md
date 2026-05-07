# Chapter 0: The Editor — "I've Never Opened This Thing"

[Chapter 1: First Sprite →](chapter-01-first-sprite.md)

---

## The Crisis

It's Friday night. The jam theme just dropped: **"Survival."** Mika is already sketching a spaceship. You download Defold. Double-click. A window opens. It looks nothing like VS Code.

No terminal. No `package.json`. No `npm install`. Just... an editor with panels you don't understand.

Deep breath. Let's figure this out.

## Download & Launch

Defold is a single executable. No installer, no dependencies, no runtime to configure.

1. Go to [defold.com/download](https://defold.com/download/)
2. Download for your OS
3. Run it

That's it. No "install JDK 21" or "configure ANDROID_HOME." The editor *is* the engine.

## Create a Project

File → New Project → From Template → **Empty**

Name it `space-survivor`. Save it somewhere.

You get:

```
space-survivor/
├── game.project          ← THE config file (like package.json)
├── main/
│   ├── main.collection   ← the "scene" that loads on startup
│   └── main.script       ← (we'll create this)
├── input/
│   └── game.input_binding ← keyboard/mouse/touch mappings
├── builtins/             ← engine defaults (render script, fonts)
└── .internal/            ← editor cache (gitignore this)
```

### `game.project` — The Entry Point

This is your `package.json` equivalent. Open it (the editor shows a GUI for it):

```ini
[project]
title = Space Survivor

[display]
width = 960
height = 540

[bootstrap]
main_collection = /main/main.collection
```

Key settings:
- **title** — game window title
- **width/height** — the game's logical resolution (not the window size)
- **main_collection** — which scene loads first (like `index.html`)

## The Editor Layout

```
┌─────────────────────────────────────────────────────────┐
│  Menu Bar                                                │
├──────────┬──────────────────────────────┬───────────────┤
│          │                              │               │
│  Assets  │       Scene Editor           │   Properties  │
│  (files) │    (visual canvas)           │   (inspector) │
│          │                              │               │
├──────────┼──────────────────────────────┼───────────────┤
│          │                              │               │
│ Outline  │       Code Editor            │   Console     │
│ (tree)   │    (Lua scripts)             │   (logs)      │
│          │                              │               │
└──────────┴──────────────────────────────┴───────────────┘
```

- **Assets** (left) — your file browser. All game files live here.
- **Outline** (left-bottom) — tree view of the currently open collection/scene.
- **Scene Editor** (center) — visual editor for placing game objects.
- **Properties** (right) — inspector for the selected object.
- **Console** (bottom) — `print()` output, errors, build logs.

## The Mental Model: Collections Are Scenes

In web dev, you have pages. In Defold, you have **collections**.

A collection is a `.collection` file that contains:
- **Game Objects** — the "things" in your game (player, enemy, bullet, background)
- **Other Collections** — nested scenes (a level, a UI overlay)

Think of it like this:

```
Web:     index.html → <div> → <span>, <img>, <button>
Defold:  main.collection → game_object → sprite, script, collision
```

## Build & Run

Press `Ctrl+B` (or `Cmd+B` on macOS). Or click Project → Build.

A window opens. It's black. Nothing happens. That's correct — we haven't added anything to the scene yet.

But the build worked. The engine compiled your project, bundled it, and ran it. In under 2 seconds.

Compare that to `npm run build` taking 45 seconds.

## Build Targets

Defold compiles to:
- **Desktop** — Windows, macOS, Linux (what you just ran)
- **Web** — HTML5 + WebAssembly (embed in a browser)
- **Mobile** — iOS, Android
- **Console** — Nintendo Switch (with license)

All from the same project. No platform-specific code (unless you want it).

To build for web: Project → Bundle → HTML5. You get a folder with `index.html` + `.wasm` files. Drop it on itch.io. Done.

## Your First Game Object

Open `main/main.collection` in the editor. The scene is empty.

Right-click in the Outline → **Add Game Object**. Name it `background`.

A game object is just a container — it has a position, rotation, and scale, but no visual representation yet. It's like an empty `<div>`.

To make it visible, you add **components**:
- **Sprite** — an image
- **Script** — Lua code (behavior)
- **Collision Object** — physics body
- **Sound** — audio clip
- **Factory** — spawns other game objects at runtime

We'll add a sprite in Chapter 1 when Mika sends the first art asset.

## Defold vs What You Know

| You're used to | Defold equivalent | Key difference |
|---|---|---|
| Files auto-reload | Must rebuild (`Ctrl+B`) | Hot reload exists but rebuild is fast (~1s) |
| Console.log | `print("hello")` | Shows in the Console panel |
| Errors in browser | Errors in Console | Lua errors include file + line number |
| npm install | Project → Dependencies | Add URLs to `game.project` |
| .env files | `sys.get_config()` | Read from `game.project` |
| Git | Git | Same — `.internal/` in `.gitignore` |

## Add a Dependency (Library)

Defold uses URL-based dependencies (like Go modules):

1. Open `game.project`
2. Under `[project]`, find `dependencies`
3. Add a URL:

```ini
[project]
dependencies = https://github.com/britzl/defold-orthographic/archive/master.zip
```

4. Project → Fetch Libraries

The library appears in your project tree. No `node_modules` folder. No lockfile. Just fetched and available.

## .gitignore

```
/.internal
/build
.externalToolBuilders
.DS_Store
```

## Verify

1. `Ctrl+B` → black window opens → no errors in Console
2. You can see the Assets panel with your project files
3. `main.collection` is open in the Scene Editor
4. The Outline shows your empty `background` game object

The jam clock reads 71:45:00. You have an editor. You have a project. You have a build that runs.

Mika texts: "Ship sprite is done. How do I send it to you?"

That's Chapter 1.

---

[Chapter 1: First Sprite →](chapter-01-first-sprite.md)
