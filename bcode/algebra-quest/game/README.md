# Algebra Quest — The Game 🎮

A pixel-art algebra adventure game for kids (ages 10-14). Solve equations to defeat monsters and progress through 8 levels of increasing difficulty.

## Play

```bash
# Option 1: Open directly (no build needed)
# Just open index.html in a browser that supports ES modules

# Option 2: With a dev server (recommended)
npx serve .
# Then open http://localhost:3000

# Option 3: With Vite
cd ..  # go to algebra-quest root
npm init -y
npm install -D vite
npx vite game/
```

## How to Play

1. **Click** to start the game
2. **Read** the equation shown at the bottom
3. **Type** your answer for x
4. **Press Enter** or click ⚡ Solve!
5. **Correct** = damage the monster (+100 points)
6. **Wrong** = lose a life (you get a hint!)
7. **Defeat all monsters** to win

## Levels

| # | Level | Monster | Algebra Concept |
|---|-------|---------|-----------------|
| 1 | Whispering Woods | Slime | x + b = c |
| 2 | Rocky Pass | Golem | x - b = c |
| 3 | Crystal Cave | Bat | ax = c |
| 4 | Potion Lab | Wizard | x/b = c |
| 5 | Two-Lock Tower | Knight | ax + b = c |
| 6 | Subtraction Swamp | Crocodile | ax - b = c |
| 7 | Underground Kingdom | Shadow | Negative answers |
| 8 | Dragon's Lair | Dragon | Variables on both sides |

## Features

- 🎨 Pixel art sprites (no image files — all drawn from code!)
- ⭐ Twinkling star backgrounds
- 💥 Particle effects on correct answers
- 📳 Screen shake on hits
- ❤️ 3 lives with hints on wrong answers
- 🏆 Score tracking
- 📈 Progressive difficulty

## Architecture

```
game/
├── index.html      ← Entry point (open this)
├── style.css       ← UI styling
├── main.js         ← Bootstrap
├── engine.js       ← Game loop, scenes, state management
├── renderer.js     ← Canvas drawing (text, sprites, effects)
├── sprites.js      ← All pixel art as data arrays
├── levels.js       ← Level definitions + equation generators
└── README.md       ← This file
```

## No Build Required

This game uses vanilla JavaScript with ES modules. No React, no bundler, no npm install needed for playing. Just open `index.html` in a modern browser.

## Customizing

### Add a new level

Edit `levels.js` — add an entry with:
- `name` — level title
- `monster` — sprite key from `sprites.js`
- `color` — theme color (hex)
- `equations` — how many to solve
- `generator` — function that returns `{ equation, answer }`
- `hint` — shown on wrong answer
- `story` — intro text

### Add a new monster

Edit `sprites.js` — add a new sprite object with:
- `width`, `height` — dimensions in pixels
- `palette` — array of colors (index 0 = transparent)
- `data` — flat array of palette indices

### Modify difficulty

In `levels.js`, adjust the random ranges in each generator function.

## Deploy to GitHub Pages

```bash
# This is a static site — just push the game/ folder
# Or copy to your gh-pages branch root
```

## Credits

Part of the [Algebra Quest](../README.md) course — a fun algebra curriculum for kids ages 10-14.
