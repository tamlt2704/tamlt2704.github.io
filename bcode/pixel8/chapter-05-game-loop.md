# Chapter 5: Game Loop — "Sixty Times a Second"

[← Chapter 4: Interaction](chapter-04-interaction.md) | [Chapter 6: Buffers →](chapter-06-buffers.md)

---

## Mika's Challenge

Mika watches you move the knight with arrow keys and frowns:

> "You're using `setInterval` for movement? That's not how games work. Games have a *loop* — a function that runs every frame. It reads input, updates state, and renders. Sixty times a second. Everything happens in that loop."

She draws on a napkin:

```
┌─────────────────────────────┐
│         GAME LOOP           │
│                             │
│  1. Read input              │
│  2. Update positions        │
│  3. Check collisions        │
│  4. Update state            │
│  5. Render (automatic)      │
│                             │
│  ← repeat every frame →     │
└─────────────────────────────┘
```

> "In Pixel8, the `fps` prop enables this. Set it to 60 and React re-renders every frame. Your state updates drive the visuals."

## Enabling the Game Loop

The `fps` prop on `<Stage>` controls the render frequency:

- `fps={0}` — static mode, renders only when state changes
- `fps={30}` — 30 frames per second (retro feel)
- `fps={60}` — 60 frames per second (smooth)

When `fps > 0`, Pixel8 triggers re-renders at that rate, giving you a game loop driven by React's render cycle.

## The Pattern: useGameLoop Hook

```jsx
import { useEffect, useRef } from 'react';

export function useGameLoop(callback, fps = 60) {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  useEffect(() => {
    let frameId;
    let lastTime = performance.now();
    const interval = 1000 / fps;

    const loop = (now) => {
      frameId = requestAnimationFrame(loop);
      const delta = now - lastTime;

      if (delta >= interval) {
        lastTime = now - (delta % interval);
        callbackRef.current(delta / 1000); // pass delta in seconds
      }
    };

    frameId = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frameId);
  }, [fps]);
}
```

## A Moving Enemy

```jsx
import React, { useState } from 'react';
import { Stage } from 'pixel8';
import { useGameLoop } from './hooks/useGameLoop';

const slime = [
  0,0,0,1,1,0,0,0,
  0,0,1,1,1,1,0,0,
  0,1,1,1,1,1,1,0,
  1,1,2,1,1,2,1,1,
  1,1,2,1,1,2,1,1,
  1,1,1,1,1,1,1,1,
  0,1,1,1,1,1,1,0,
  0,0,1,0,0,1,0,0,
];
const slimePalette = ['transparent', '#00cc44', '#000000'];

const Game = () => {
  const [enemyX, setEnemyX] = useState(0);
  const [direction, setDirection] = useState(1);

  useGameLoop((dt) => {
    setEnemyX(prev => {
      const next = prev + direction * 20 * dt; // 20 pixels per second
      if (next > 56 || next < 0) {
        setDirection(d => -d);
        return Math.max(0, Math.min(56, next));
      }
      return next;
    });
  });

  return (
    <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
      <sprite x={Math.round(enemyX)} y={40} data={slime} palette={slimePalette} />
    </Stage>
  );
};
```

### What You Should See

A green slime bouncing left and right across the bottom of the screen, reversing direction at the edges.

## Delta Time: Frame-Rate Independence

The `dt` parameter (delta time in seconds) ensures consistent speed regardless of actual frame rate:

```jsx
// ❌ Bad: speed depends on frame rate
setX(prev => prev + 1); // 60px/sec at 60fps, 30px/sec at 30fps

// ✅ Good: speed is consistent
const speed = 30; // pixels per second
setX(prev => prev + speed * dt); // always 30px/sec
```

Always multiply movement by `dt` for predictable behavior.

## Collision Detection: AABB

At low resolution, axis-aligned bounding box (AABB) collision is perfect:

```jsx
function collides(a, b) {
  return (
    a.x < b.x + b.width &&
    a.x + a.width > b.x &&
    a.y < b.y + b.height &&
    a.y + a.height > b.y
  );
}

// Usage
const player = { x: playerX, y: playerY, width: 8, height: 8 };
const enemy  = { x: enemyX,  y: enemyY,  width: 8, height: 8 };

if (collides(player, enemy)) {
  // Hit!
  setLives(l => l - 1);
}
```

## Full Example: Dodge Game

```jsx
import React, { useState, useRef } from 'react';
import { Stage } from 'pixel8';
import { useGameLoop } from './hooks/useGameLoop';
import { useKeyboard } from './hooks/useKeyboard';

const playerSprite = [
  0,0,1,1,1,0,0,0,
  0,1,1,1,1,1,0,0,
  0,1,2,1,2,1,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,1,1,0,0,0,
  0,0,1,1,1,0,0,0,
  0,1,1,0,1,1,0,0,
  0,0,0,0,0,0,0,0,
];
const playerPalette = ['transparent', '#4488ff', '#ffffff'];

const DodgeGame = () => {
  const [playerX, setPlayerX] = useState(28);
  const [enemies, setEnemies] = useState([]);
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const keys = useRef(new Set());
  const spawnTimer = useRef(0);

  // Key tracking
  React.useEffect(() => {
    const down = (e) => keys.current.add(e.key);
    const up = (e) => keys.current.delete(e.key);
    window.addEventListener('keydown', down);
    window.addEventListener('keyup', up);
    return () => {
      window.removeEventListener('keydown', down);
      window.removeEventListener('keyup', up);
    };
  }, []);

  useGameLoop((dt) => {
    if (gameOver) return;

    // Move player
    const speed = 40;
    if (keys.current.has('ArrowLeft'))  setPlayerX(x => Math.max(0, x - speed * dt));
    if (keys.current.has('ArrowRight')) setPlayerX(x => Math.min(56, x + speed * dt));

    // Spawn enemies
    spawnTimer.current += dt;
    if (spawnTimer.current > 0.8) {
      spawnTimer.current = 0;
      const newX = Math.floor(Math.random() * 56);
      setEnemies(prev => [...prev, { x: newX, y: -8 }]);
    }

    // Move enemies down
    setEnemies(prev =>
      prev
        .map(e => ({ ...e, y: e.y + 25 * dt }))
        .filter(e => e.y < 72)
    );

    // Check collisions
    setEnemies(prev => {
      for (const e of prev) {
        if (
          Math.round(e.x) < Math.round(playerX) + 8 &&
          Math.round(e.x) + 8 > Math.round(playerX) &&
          Math.round(e.y) < 52 &&
          Math.round(e.y) + 8 > 44
        ) {
          setGameOver(true);
          return prev;
        }
      }
      return prev;
    });

    // Score
    setScore(s => s + 1);
  });

  return (
    <Stage width={64} height={64} scale={8} fps={60} background="#0a0a2a">
      {/* Player at bottom */}
      <sprite x={Math.round(playerX)} y={50} data={playerSprite} palette={playerPalette} />

      {/* Falling enemies */}
      {enemies.map((e, i) => (
        <rect key={i} x={Math.round(e.x)} y={Math.round(e.y)} width={8} height={8} color="#e94560" />
      ))}

      {/* Score */}
      <text x={2} y={2} value={`${Math.floor(score / 60)}`} color="#ffffff" />

      {/* Game over */}
      {gameOver && <text x={16} y={30} value="DEAD" color="#ff0000" />}
    </Stage>
  );
};
```

### What You Should See

A blue character at the bottom dodging red squares falling from above. Score counts up. Hit a square and "DEAD" appears.

## Spawning Patterns

```jsx
// Timed spawning
spawnTimer.current += dt;
if (spawnTimer.current > spawnInterval) {
  spawnTimer.current = 0;
  spawn();
}

// Increasing difficulty
const spawnInterval = Math.max(0.3, 1.0 - score * 0.01);

// Wave spawning
if (enemies.length === 0) {
  spawnWave(waveNumber);
  setWaveNumber(w => w + 1);
}
```

## Tips: Game Loop Design

1. **Round positions for rendering** — calculate with floats, render with `Math.round()`
2. **Clean up off-screen objects** — filter out enemies that leave the canvas
3. **Separate update from render** — state updates in the loop, rendering is automatic via React
4. **Cap delta time** — if a frame takes too long (tab was hidden), cap dt at 0.1s to prevent teleporting
5. **Game states** — use a state machine: `'playing'`, `'paused'`, `'gameOver'`

## Pattern: Game State Machine

```jsx
const [gameState, setGameState] = useState('title'); // 'title' | 'playing' | 'gameOver'

useGameLoop((dt) => {
  switch (gameState) {
    case 'title':
      // Wait for key press
      if (keys.current.has(' ')) setGameState('playing');
      break;
    case 'playing':
      // Run game logic
      updatePlayer(dt);
      updateEnemies(dt);
      checkCollisions();
      break;
    case 'gameOver':
      // Wait for restart
      if (keys.current.has('r')) {
        resetGame();
        setGameState('playing');
      }
      break;
  }
});
```

## Exercise

1. Add **increasing difficulty** — enemies spawn faster and move faster as score increases
2. Implement **lives** — player gets 3 hits before game over, flash the sprite on hit
3. Add **collectible coins** — yellow circles that give bonus points when touched
4. Create a **pause system** — press P to freeze all movement, press again to resume

## Quick Reference

```jsx
// Enable game loop
<Stage fps={60} ...>

// Delta-time movement
const speed = 30; // pixels per second
newX = oldX + speed * dt;

// AABB collision
function collides(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x &&
         a.y < b.y + b.h && a.y + a.h > b.y;
}

// Round for rendering
<sprite x={Math.round(floatX)} y={Math.round(floatY)} ... />
```

| Concept | Value |
|---------|-------|
| `fps={0}` | Static — no loop |
| `fps={60}` | 60 updates/second |
| Delta time | Seconds since last frame |
| AABB | Rectangle overlap check |
| Spawn timer | Accumulate dt, spawn when threshold reached |

---

Next: Mika wants procedural textures — noise, gradients, dynamic backgrounds. Time to work with raw pixel buffers.

[← Chapter 4: Interaction](chapter-04-interaction.md) | [Chapter 6: Buffers →](chapter-06-buffers.md)
