# Pygame Mastery — From Blank Window to Shipped Game

A narrative-driven game development course using Pygame. You're a solo developer at a tiny indie studio trying to ship a 2D action game before the funding runs out. Over 15 chapters, you'll build every system — one broken prototype at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, game loop intuition, the cast |
| 01 | [The Blank Window](chapter-01-game-loop.md) | Nothing on screen | Display, event loop, FPS clock |
| 02 | [Something Moves](chapter-02-movement.md) | Static rectangles are boring | Sprites, velocity, delta time |
| 03 | [Responding to Input](chapter-03-input.md) | Player can't control anything | Keyboard, mouse, input buffering |
| 04 | [Collision!](chapter-04-collisions.md) | Bullets pass through enemies | Rect collision, pixel-perfect, spatial hashing |
| 05 | [Sprite Sheets](chapter-05-animation.md) | Everything is colored rectangles | Loading art, frame animation, state machines |
| 06 | [Sound & Music](chapter-06-audio.md) | Silent game feels lifeless | Mixer, channels, positional audio |
| 07 | [Tile Maps](chapter-07-tilemaps.md) | Levels are hard-coded | TMX loading, camera scrolling, layers |
| 08 | [Enemies That Think](chapter-08-enemies.md) | Enemies stand still | State machines, pathfinding, aggro |
| 09 | [Particles & Effects](chapter-09-particles.md) | Hits feel weightless | Particle systems, screen shake, flash |
| 10 | [UI & Menus](chapter-10-ui.md) | No way to start or pause | Scene management, buttons, HUD |
| 11 | [Save & Load](chapter-11-persistence.md) | Progress lost on quit | Serialization, save slots, settings |
| 12 | [Performance](chapter-12-performance.md) | 200 enemies = 15 FPS | Profiling, dirty rects, object pooling |
| 13 | [Gamepad Support](chapter-13-gamepad.md) | Keyboard-only limits players | Joystick API, dead zones, remapping |
| 14 | [Polish & Juice](chapter-14-polish.md) | Game works but feels flat | Tweening, hitstop, camera lerp |
| 15 | [Ship It](chapter-15-ship-it.md) | "How do I give this to people?" | PyInstaller, cx_Freeze, itch.io upload |

## Prerequisites

- Python 3.10+
- `pip install pygame-ce` (community edition, actively maintained)

## Philosophy

Every system is introduced because the game feels wrong without it. No engine feature without a player experience problem to solve first. The broken prototype comes first. The polished version follows.
