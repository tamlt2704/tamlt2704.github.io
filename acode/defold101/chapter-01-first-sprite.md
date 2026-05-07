# Chapter 1: First Sprite — "How Do I Put a Thing on Screen?"

[← Chapter 0: The Editor](chapter-00-the-editor.md) | [Chapter 2: Movement →](chapter-02-movement.md)

---

## The Crisis

Mika sends a PNG: `ship.png` — a 64×64 pixel spaceship. "Put it on screen. I need to see it moving by morning."

You drag the PNG into the project. Nothing happens. In web dev, you'd write `<img src="ship.png">` and it'd appear. Defold doesn't work that way.

Images don't go directly into the scene. They go into an **atlas** first.

## The Atlas: A Sprite Sheet

An atlas is a texture that packs multiple images into one. The GPU draws faster when it doesn't have to switch textures. Think of it like a CSS sprite sheet.

1. Right-click in Assets → New → Atlas
2. Name it `main.atlas`
3. Open it
4. Right-click in the Outline → Add Images
5. Select `ship.png`

The atlas editor shows your ship image with a blue border (the bounding box). Save it.

```
Web analogy:
  CSS sprite sheet + background-position
  = Defold atlas + animation groups
```

## Add the Sprite to a Game Object

Open `main/main.collection`. We need a game object for the player.

1. Right-click in Outline → **Add Game Object** → name it `player`
2. Select `player` → right-click → **Add Component** → **Sprite**
3. In Properties, set:
   - **Image**: `/main/main.atlas`
   - **Default Animation**: `ship` (the image name without extension)

The ship appears in the Scene Editor. It's at position (0, 0, 0) — the center of the world.

## Positioning

Move the player to a better starting position:

1. Select the `player` game object in the Outline
2. In Properties, set Position:
   - X: `480` (center of 960-wide screen)
   - Y: `100` (near the bottom)
   - Z: `0.5` (in front of the background)

**Z-order matters.** Higher Z = drawn on top. The background should be Z: 0, the player Z: 0.5, bullets Z: 0.6, UI Z: 1.0.

## Understanding the Hierarchy

```
main.collection
└── player (Game Object)
    └── sprite (Component)
        └── references main.atlas → "ship" animation
```

A **Game Object** is a container with a transform (position, rotation, scale).
A **Component** gives it behavior or appearance.

One game object can have multiple components:
- A sprite (how it looks)
- A script (how it behaves)
- A collision object (how it interacts physically)
- A sound (what it sounds like)

## The Game Object Lifecycle

Every game object with a script goes through these functions:

```lua
function init(self)
    -- Called once when the object is created
    -- Like a constructor or componentDidMount
end

function update(self, dt)
    -- Called every frame (60 times per second)
    -- dt = delta time (seconds since last frame, usually ~0.016)
    -- Like requestAnimationFrame
end

function on_message(self, message_id, message, sender)
    -- Called when this object receives a message
    -- Like an event listener
end

function final(self)
    -- Called when the object is destroyed
    -- Like componentWillUnmount
end
```

We'll use these in Chapter 2 for movement.

## Adding a Background

Mika sends `space_bg.png` — a 960×540 starfield.

1. Add `space_bg.png` to `main.atlas`
2. In `main.collection`, add a new Game Object → name it `background`
3. Add a Sprite component to `background`
4. Set Image: `main.atlas`, Default Animation: `space_bg`
5. Position: X: 480, Y: 270, Z: 0 (behind everything)

## Build & Run

`Ctrl+B`. The window opens. You see a starfield with a spaceship near the bottom center.

It doesn't move. It doesn't do anything. But it's *there*. Pixels on screen. A game object in a collection with a sprite referencing an atlas.

## What Just Happened (The Render Pipeline)

```
1. Engine loads main.collection (bootstrap)
2. Creates game objects: background, player
3. Each frame:
   a. Update all scripts (none yet)
   b. Render all sprites (sorted by Z-order)
   c. Background (Z:0) drawn first
   d. Player ship (Z:0.5) drawn on top
4. Display the frame
```

60 times per second. No DOM. No layout engine. No reflow. Just "draw these pixels at these coordinates."

## Multiple Images in One Atlas

As Mika sends more art, add them all to the same atlas:

```
main.atlas
├── ship (64×64)
├── space_bg (960×540)
├── bullet (8×16)        ← Chapter 3
├── asteroid_01 (48×48)  ← Chapter 4
├── asteroid_02 (32×32)  ← Chapter 4
└── explosion (64×64)    ← Chapter 5 (animated)
```

One atlas = one draw call for all these sprites. The GPU loves this.

## Verify

1. `Ctrl+B` → window shows starfield + ship
2. Ship is near the bottom center
3. Background fills the screen
4. No errors in Console
5. The Outline shows: main.collection → background (sprite) + player (sprite)

Mika looks over your shoulder. "Cool. Now make it move."

The jam clock reads 70:30:00.

---

[← Chapter 0: The Editor](chapter-00-the-editor.md) | [Chapter 2: Movement →](chapter-02-movement.md)
