# Chapter 0: Before You Start

[Chapter 1: The Blank Window →](chapter-01-game-loop.md)

---

## The Story

This is a series about making games with Pygame — but not the kind where you follow a tutorial and end up with a Flappy Bird clone you'll never touch again.

You're the sole developer at **Pixel Forge**, a one-person indie studio. You quit your day job six months ago with enough savings for twelve months of runway. You've got a game design document, a folder of placeholder art, and a deadline: ship something playable to itch.io before the money runs out.

The game is **Void Runners** — a 2D top-down action game where the player fights through procedurally connected rooms, collects upgrades, and faces a boss every five floors. Think Enter the Gungeon meets Vampire Survivors, but scoped to what one person can build.

Your friend **Kai**, a pixel artist, is doing the art for revenue share. Your playtester **Rena** sends brutally honest feedback every Friday. Your partner **Sam** keeps asking "so when does it make money?"

Week 1. You open a new Python file. The cursor blinks.

Over the next 15 chapters, you'll build Void Runners from a blank window to a shipped game. Every system you implement solves a real problem — making things move, making them collide, making them feel good to interact with. And every first attempt will be wrong in a way that teaches you why game developers do things the way they do.

The player will clip through walls. The frame rate will tank at 200 enemies. The input will feel laggy because you forgot delta time. The animations will stutter because you're loading PNGs every frame. The save system will corrupt because you serialized a Surface object.

Each disaster teaches you something about real-time interactive systems that no documentation page could.

By the end, you'll have a playable, polished, shipped game — and you'll understand the *why* behind every game programming pattern.

## How to Read This

Every chapter is the same loop:

1. The game needs something it doesn't have
2. You try the obvious approach
3. It breaks in an instructive way
4. You learn the proper technique
5. You implement it, verify it works, and move on

No system shows up before you need it. You won't hear about spatial hashing until rect collision chokes on 500 bullets. You won't touch object pooling until the garbage collector causes frame spikes during boss fights.

The naive code comes first. The game-dev wisdom follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Solo Developer | Determined. Slightly over-scoped. |
| **Kai** | Pixel Artist | "I sent the sprite sheet. Why is it still a white rectangle?" |
| **Rena** | Playtester | "It doesn't feel good." (No further explanation.) |
| **Sam** | Your Partner | Supportive but practical. "Month 8. How's the game?" |
| **The Prototype** | Your creation | Starts ugly. Gets beautiful. Sometimes crashes. |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | Nothing on screen | Game loop, display, event handling, FPS |
| 2 | Things exist but don't move | Sprites, velocity, delta time, vectors |
| 3 | Player can't control anything | Input handling, key states, mouse aiming |
| 4 | Bullets pass through enemies | Collision detection, groups, spatial optimization |
| 5 | Everything is colored rectangles | Sprite sheets, frame animation, state machines |
| 6 | Game is silent | Sound effects, music, mixer channels |
| 7 | Levels are hard-coded | Tile maps, TMX format, camera scrolling |
| 8 | Enemies just stand there | AI state machines, pathfinding, behavior |
| 9 | Hits feel weightless | Particles, screen shake, visual feedback |
| 10 | No menus, no HUD | Scene management, UI rendering, transitions |
| 11 | Progress lost on close | Save/load, JSON serialization, settings |
| 12 | Frame rate drops with many entities | Profiling, dirty rects, pooling, culling |
| 13 | Keyboard-only limits audience | Gamepad support, dead zones, input abstraction |
| 14 | Game works but feels flat | Juice, tweening, hitstop, camera smoothing |
| 15 | "How do I give this to people?" | Packaging, distribution, itch.io |

## Prerequisites

Two things: Python 3 and a willingness to see your game look terrible before it looks good.

### Python 3.10+

```bash
python3 --version
# Python 3.10.x or higher
```

### Pygame CE (Community Edition)

We use Pygame CE — the actively maintained fork with bug fixes and new features:

```bash
pip install pygame-ce
```

Verify:

```python
import pygame
pygame.init()
print(f"Pygame CE {pygame.ver}")
pygame.quit()
```

If that prints a version number without errors, you're good.

### Why Pygame CE over regular Pygame?

Regular Pygame is in maintenance mode. Pygame CE has:
- Active development and bug fixes
- Better performance (hardware-accelerated rendering)
- New features (better controller support, modern audio)
- Drop-in compatible — same API, same imports

### A Code Editor

Any editor works. VS Code with the Python extension gives you autocomplete for Pygame's API, which helps when you're exploring.

### Optional: Art Assets

Chapters 1–4 use colored rectangles. Starting Chapter 5, you'll need sprite sheets. Options:

- **Kai's assets** (provided with each chapter as download links)
- [Kenney.nl](https://kenney.nl) — free game assets, CC0 license
- [OpenGameArt.org](https://opengameart.org) — community art
- Draw your own in [Aseprite](https://www.aseprite.org/) or [Piskel](https://www.piskelapp.com/)

### Quick Check

```python
import pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Void Runners")
print("Window created successfully")
pygame.quit()
```

If a window flashes briefly and you see the print, you're ready.

## The Game Loop (The Only Theory Upfront)

Every game — from Pong to Elden Ring — runs the same core loop:

```
while game_is_running:
    handle_input()      # What did the player do?
    update()            # What changed in the world?
    draw()             # Show the new state
```

That's it. Input → Update → Draw. 60 times per second. Everything else is details.

| Phase | What Happens | Example |
|---|---|---|
| Input | Read keyboard, mouse, gamepad | Player pressed SPACE |
| Update | Move entities, check collisions, run AI | Bullet spawns, moves 10px up |
| Draw | Render everything to screen | Bullet appears on screen |

The loop runs at a fixed rate (60 FPS = 16.6ms per frame). If your update + draw takes longer than 16.6ms, the game stutters. If it takes less, you wait. That's what the clock does.

We'll build this loop in Chapter 1. For now, just remember: games are not request-response. They're continuous simulations that happen to have a human pressing buttons.

Let's open a window.

---

[Chapter 1: The Blank Window →](chapter-01-game-loop.md)
