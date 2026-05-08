# Chapter 10: Mini-Game — "Ship It"

[← Chapter 9: Composition](chapter-09-composition.md)

---

## Mika's Challenge

Mika sits across from you, arms crossed, grinning:

> "You've learned pixels, sprites, animation, input, game loops, buffers, text, palettes, and composition. Now put it all together. Build me a *game*. A real one. With a title screen, gameplay, a score, a way to lose, and a way to win. Something I can play for 5 minutes and want to beat my high score."

She taps the table:

> "Call it **BitForge: Coin Catcher**. You're a knight. Coins fall from the sky. Catch them. Avoid the skulls. Three lives. Increasing difficulty. Game over screen. That's it. Ship it."

## The Complete Game

Here's the full BitForge mini-game — every concept from the course combined into one playable experience.

### sprites.js

```jsx
// sprites.js — all game sprites as data arrays

export const knight = [
  0,0,3,3,3,0,0,0,
  0,0,1,1,1,0,0,0,
  0,1,2,1,2,1,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,1,1,0,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,0,1,0,0,0,
  0,0,1,0,1,0,0,0,
];

export const coin = [
  0,0,1,1,1,1,0,0,
  0,1,2,2,2,2,1,0,
  1,2,2,1,1,2,2,1,
  1,2,2,1,1,2,2,1,
  1,2,2,2,2,2,2,1,
  0,1,2,2,2,2,1,0,
  0,0,1,1,1,1,0,0,
  0,0,0,0,0,0,0,0,
];

export const skull = [
  0,0,1,1,1,1,0,0,
  0,1,1,1,1,1,1,0,
  1,1,2,1,1,2,1,1,
  1,1,2,1,1,2,1,1,
  0,1,1,1,1,1,1,0,
  0,0,1,2,2,1,0,0,
  0,0,2,1,1,2,0,0,
  0,0,0,0,0,0,0,0,
];

export const heart = [
  0,1,1,0,0,1,1,0,
  1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,
  0,1,1,1,1,1,1,0,
  0,0,1,1,1,1,0,0,
  0,0,0,1,1,0,0,0,
  0,0,0,0,0,0,0,0,
];

export const palettes = {
  knight: ['transparent', '#c0c0c0', '#333333', '#ff0000'],
  coin:   ['transparent', '#daa520', '#ffd700'],
  skull:  ['transparent', '#f5f5dc', '#333333'],
  heart:  ['transparent', '#ff0000'],
};
```

### hooks/useKeyboard.js

```jsx
import { useEffect, useRef } from 'react';

export function useKeyboard() {
  const keys = useRef(new Set());

  useEffect(() => {
    const down = (e) => { e.preventDefault(); keys.current.add(e.key); };
    const up = (e) => keys.current.delete(e.key);
    window.addEventListener('keydown', down);
    window.addEventListener('keyup', up);
    return () => {
      window.removeEventListener('keydown', down);
      window.removeEventListener('keyup', up);
    };
  }, []);

  return keys;
}
```

### hooks/useGameLoop.js

```jsx
import { useEffect, useRef } from 'react';

export function useGameLoop(callback, fps = 60) {
  const cbRef = useRef(callback);
  cbRef.current = callback;

  useEffect(() => {
    let frameId;
    let last = performance.now();
    const interval = 1000 / fps;

    const loop = (now) => {
      frameId = requestAnimationFrame(loop);
      const delta = now - last;
      if (delta >= interval) {
        last = now - (delta % interval);
        cbRef.current(delta / 1000);
      }
    };

    frameId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frameId);
  }, [fps]);
}
```

### Game.jsx — The Main Game Component

```jsx
import React, { useState, useRef } from 'react';
import { Stage } from 'pixel8';
import { knight, coin, skull, heart, palettes } from './sprites';
import { useKeyboard } from './hooks/useKeyboard';
import { useGameLoop } from './hooks/useGameLoop';

const STAGE_W = 64;
const STAGE_H = 64;
const PLAYER_SPEED = 50;
const SPAWN_BASE = 1.2;
const FALL_BASE = 20;

const Game = () => {
  // Game state
  const [scene, setScene] = useState('title'); // title | playing | gameOver
  const [playerX, setPlayerX] = useState(28);
  const [items, setItems] = useState([]);
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [highScore, setHighScore] = useState(0);

  // Refs for mutable game data
  const keys = useKeyboard();
  const spawnTimer = useRef(0);
  const difficulty = useRef(1);

  // Reset game
  const resetGame = () => {
    setPlayerX(28);
    setItems([]);
    setScore(0);
    setLives(3);
    spawnTimer.current = 0;
    difficulty.current = 1;
  };

  // Game loop
  useGameLoop((dt) => {
    if (scene === 'title') {
      if (keys.current.has(' ') || keys.current.has('Enter')) {
        resetGame();
        setScene('playing');
      }
      return;
    }

    if (scene === 'gameOver') {
      if (keys.current.has('r') || keys.current.has('R')) {
        resetGame();
        setScene('playing');
      }
      return;
    }

    // --- PLAYING ---

    // Move player
    if (keys.current.has('ArrowLeft') || keys.current.has('a')) {
      setPlayerX(x => Math.max(0, x - PLAYER_SPEED * dt));
    }
    if (keys.current.has('ArrowRight') || keys.current.has('d')) {
      setPlayerX(x => Math.min(STAGE_W - 8, x + PLAYER_SPEED * dt));
    }

    // Increase difficulty over time
    difficulty.current += dt * 0.05;

    // Spawn items
    spawnTimer.current += dt;
    const spawnInterval = SPAWN_BASE / difficulty.current;
    if (spawnTimer.current > spawnInterval) {
      spawnTimer.current = 0;
      const isCoin = Math.random() > 0.3; // 70% coins, 30% skulls
      setItems(prev => [...prev, {
        id: Date.now() + Math.random(),
        x: Math.floor(Math.random() * (STAGE_W - 8)),
        y: -8,
        type: isCoin ? 'coin' : 'skull',
      }]);
    }

    // Move items down
    const fallSpeed = FALL_BASE * difficulty.current;
    setItems(prev => prev.map(item => ({
      ...item,
      y: item.y + fallSpeed * dt,
    })).filter(item => item.y < STAGE_H + 8));

    // Check collisions with player
    setItems(prev => {
      const remaining = [];
      for (const item of prev) {
        const px = Math.round(playerX);
        const ix = Math.round(item.x);
        const iy = Math.round(item.y);

        // AABB collision (player is at y=52)
        const hit = ix < px + 8 && ix + 8 > px && iy < 60 && iy + 8 > 52;

        if (hit) {
          if (item.type === 'coin') {
            setScore(s => s + 10);
          } else {
            setLives(l => {
              const newLives = l - 1;
              if (newLives <= 0) {
                setHighScore(hs => Math.max(hs, score));
                setScene('gameOver');
              }
              return newLives;
            });
          }
        } else {
          remaining.push(item);
        }
      }
      return remaining;
    });
  });

  // --- RENDER ---

  if (scene === 'title') {
    return <TitleScreen />;
  }

  if (scene === 'gameOver') {
    return <GameOverScreen score={score} highScore={Math.max(highScore, score)} />;
  }

  return (
    <Stage width={STAGE_W} height={STAGE_H} scale={8} fps={60} background="#0a0a2e">
      {/* Starfield background */}
      {Array.from({ length: 20 }, (_, i) => (
        <pixel
          key={`star-${i}`}
          x={(i * 17 + 7) % 64}
          y={(i * 31 + 13) % 64}
          color={i % 3 === 0 ? '#444466' : '#222244'}
        />
      ))}

      {/* Ground line */}
      <rect x={0} y={61} width={64} height={3} color="#1a1a3e" />

      {/* Falling items */}
      {items.map(item => (
        <sprite
          key={item.id}
          x={Math.round(item.x)}
          y={Math.round(item.y)}
          data={item.type === 'coin' ? coin : skull}
          palette={item.type === 'coin' ? palettes.coin : palettes.skull}
        />
      ))}

      {/* Player */}
      <sprite x={Math.round(playerX)} y={52} data={knight} palette={palettes.knight} />

      {/* HUD */}
      <rect x={0} y={0} width={64} height={8} color="#000000" />
      <text x={1} y={1} value={`SC:${String(score).padStart(4, '0')}`} color="#ffffff" />

      {/* Lives as hearts */}
      {Array.from({ length: lives }, (_, i) => (
        <sprite
          key={`life-${i}`}
          x={44 + i * 7}
          y={0}
          data={heart}
          palette={palettes.heart}
        />
      ))}
    </Stage>
  );
};
```

### TitleScreen Component

```jsx
const TitleScreen = () => (
  <Stage width={64} height={64} scale={8} fps={60} background="#0a0a2e">
    {/* Title */}
    <text x={12} y={10} value="BIT" color="#ffd700" />
    <text x={8} y={18} value="FORGE" color="#ffd700" />

    {/* Decorative sprites */}
    <sprite x={10} y={30} data={coin} palette={palettes.coin} />
    <sprite x={28} y={30} data={knight} palette={palettes.knight} />
    <sprite x={46} y={30} data={skull} palette={palettes.skull} />

    {/* Divider */}
    <rect x={8} y={42} width={48} height={1} color="#333355" />

    {/* Instructions */}
    <text x={4} y={46} value="CATCH COINS" color="#aaaaaa" />
    <text x={4} y={53} value="AVOID SKULLS" color="#aaaaaa" />

    {/* Start prompt */}
    <text x={6} y={60} value="PRESS SPACE" color="#ffffff" />
  </Stage>
);
```

### GameOverScreen Component

```jsx
const GameOverScreen = ({ score, highScore }) => (
  <Stage width={64} height={64} scale={8} fps={0} background="#0a0000">
    {/* Game Over text */}
    <text x={12} y={10} value="GAME" color="#ff0000" />
    <text x={12} y={18} value="OVER" color="#ff0000" />

    {/* Skull decoration */}
    <sprite x={28} y={26} data={skull} palette={['transparent', '#666666', '#333333']} />

    {/* Scores */}
    <text x={4} y={38} value={`SCORE:${score}`} color="#ffffff" />
    <text x={4} y={46} value={`BEST:${highScore}`} color="#ffd700" />

    {/* Restart */}
    <text x={8} y={57} value="PRESS R" color="#888888" />
  </Stage>
);
```

### What You Should See

1. **Title screen** — "BIT FORGE" in gold, three sprites displayed, instructions, "PRESS SPACE"
2. **Gameplay** — knight at the bottom, coins and skulls falling, score counting up, hearts for lives
3. **Game over** — red "GAME OVER", final score, high score, "PRESS R" to restart

## Deploying to GitHub Pages

```bash
# Build the project
npm run build

# Install gh-pages
npm install -D gh-pages

# Add to package.json scripts:
# "deploy": "gh-pages -d build"

# Deploy
npm run deploy
```

For Vite projects, add to `vite.config.js`:

```js
export default defineConfig({
  base: '/bitforge/', // your repo name
  plugins: [react()],
});
```

### GitHub Actions (automatic deploy)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 16
      - run: npm install
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

## Game Design Checklist

| Element | Implementation |
|---------|---------------|
| ✅ Title screen | Scene state = 'title', press Space to start |
| ✅ Player movement | Arrow keys / WASD, clamped to bounds |
| ✅ Spawning | Timer-based, random x position |
| ✅ Falling objects | Two types: coins (good) and skulls (bad) |
| ✅ Collision | AABB check between player and items |
| ✅ Scoring | +10 per coin caught |
| ✅ Lives | 3 hearts, lose one per skull hit |
| ✅ Difficulty curve | Speed and spawn rate increase over time |
| ✅ Game over | Triggered at 0 lives, shows score |
| ✅ High score | Tracked across plays (in memory) |
| ✅ Restart | Press R to play again |
| ✅ HUD | Score + lives always visible |
| ✅ Visual polish | Starfield, ground line, palette cohesion |

## Enhancements to Try

Once the base game works, add:

1. **Screen shake** — offset the entire stage by ±1px for 100ms on hit
2. **Coin particles** — emit gold pixels when collecting a coin
3. **Speed powerup** — green item that temporarily boosts player speed
4. **Sound** — use the Web Audio API for a coin "ding" and skull "thud"
5. **Local storage** — persist high score between sessions
6. **Mobile controls** — touch left/right halves of screen to move

## Tips: Shipping a Pixel Game

1. **Scope small** — a 5-minute game that's polished beats a 30-minute game that's buggy
2. **Playtest early** — watch someone else play. They'll find issues you never imagined.
3. **Juice last** — get mechanics working first, then add particles, shake, and sound
4. **Fixed resolution** — don't try to be responsive. 64×64 at scale 8 = 512×512. That's your game.
5. **Version control your sprites** — they're just arrays. Git diffs work perfectly.

## The Full Project Structure

```
bitforge/
├── src/
│   ├── App.jsx              ← routes to Game
│   ├── Game.jsx             ← main game component
│   ├── sprites.js           ← all sprite data + palettes
│   ├── hooks/
│   │   ├── useKeyboard.js   ← key tracking
│   │   └── useGameLoop.js   ← requestAnimationFrame loop
│   ├── components/
│   │   ├── TitleScreen.jsx
│   │   ├── GameOverScreen.jsx
│   │   └── HUD.jsx
│   └── index.js             ← entry point
├── package.json
├── vite.config.js
└── README.md
```

## Exercise

1. Add a **combo system** — catching 3 coins in a row without missing gives 2× points
2. Implement **levels** — every 100 points, flash "LEVEL UP", increase difficulty step
3. Add a **shield powerup** — blue item that grants 3 seconds of invincibility
4. Create a **second game mode** — instead of catching, the knight shoots upward at falling skulls

## Quick Reference

| Concept | Where It's Used |
|---------|----------------|
| `<Stage>` | Root component, sets resolution and fps |
| `<sprite>` | Player, coins, skulls, hearts |
| `<rect>` | Ground, HUD background |
| `<pixel>` | Starfield background |
| `<text>` | Score, game over, title, prompts |
| `useKeyboard` | Player movement, scene transitions |
| `useGameLoop` | Frame updates, physics, spawning |
| State machine | title → playing → gameOver |
| AABB collision | Catching coins, hitting skulls |
| Palette system | Consistent visual style |

---

## Course Complete

You did it. From a single white pixel to a complete playable game — all rendered from code. No image files. No asset pipeline. Just React components, number arrays, and hex colors.

Mika sends one final message:

> "See? Constraints aren't limitations. They're *invitations*. 64×64 pixels. A handful of colors. And you built a world. Now go build another one. 🎮"

**Where to go next:**
- Try [PICO-8](https://www.lexaloffle.com/pico-8.php) — a fantasy console with similar constraints
- Explore [TIC-80](https://tic80.com/) — free and open source
- Build a larger game with [PixiJS + @pixi/react](https://pixijs.com/)
- Join pixel art communities on Twitter/X and itch.io
- Enter a game jam — constraints + deadlines = creativity

[← Chapter 9: Composition](chapter-09-composition.md)
