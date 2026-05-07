# Chapter 9: Game State — "Track Score, Health, Levels"

[← Chapter 8: Collision](chapter-08-collision.md) | [Chapter 10: Sound & Particles →](chapter-10-sound-particles.md)

---

## The Crisis

The knight picks up keys but nothing happens. Slimes deal damage but there's no health bar. You collect coins but there's no score. The game has no memory.

Kai: "I need to see health. Score. How many keys I have. And when health hits zero — game over."

You need game state. And since you're in React, you know exactly how to do this: context + state.

## The Naive Approach: Props Drilling

You could pass `health`, `score`, `keys` as props through every component:

```jsx
// ❌ This gets messy fast
<Game health={health} setHealth={setHealth} score={score} setScore={setScore} keys={keys} setKeys={setKeys}>
  <Player health={health} setHealth={setHealth} />
  <HUD health={health} score={score} keys={keys} />
  <Enemies setHealth={setHealth} />
</Game>
```

Five levels deep, ten props each. You know this pattern. You know it's bad.

## The Proper Approach: React Context

Create a game state context that any component can access:

```jsx
// src/hooks/useGameState.js
import { createContext, useContext, useReducer } from 'react';

const GameStateContext = createContext(null);
const GameDispatchContext = createContext(null);

const initialState = {
  health: 10,
  maxHealth: 10,
  score: 0,
  keys: 0,
  level: 1,
  gameOver: false,
  paused: false,
  inventory: [],
};

function gameReducer(state, action) {
  switch (action.type) {
    case 'TAKE_DAMAGE':
      const newHealth = Math.max(0, state.health - action.amount);
      return {
        ...state,
        health: newHealth,
        gameOver: newHealth <= 0,
      };
    case 'HEAL':
      return {
        ...state,
        health: Math.min(state.maxHealth, state.health + action.amount),
      };
    case 'ADD_SCORE':
      return { ...state, score: state.score + action.amount };
    case 'COLLECT_KEY':
      return { ...state, keys: state.keys + 1 };
    case 'USE_KEY':
      return { ...state, keys: Math.max(0, state.keys - 1) };
    case 'NEXT_LEVEL':
      return { ...state, level: state.level + 1 };
    case 'GAME_OVER':
      return { ...state, gameOver: true };
    case 'RESTART':
      return { ...initialState };
    case 'PAUSE':
      return { ...state, paused: !state.paused };
    default:
      return state;
  }
}

export function GameStateProvider({ children }) {
  const [state, dispatch] = useReducer(gameReducer, initialState);

  return (
    <GameStateContext.Provider value={state}>
      <GameDispatchContext.Provider value={dispatch}>
        {children}
      </GameDispatchContext.Provider>
    </GameStateContext.Provider>
  );
}

export function useGameState() {
  return useContext(GameStateContext);
}

export function useGameDispatch() {
  return useContext(GameDispatchContext);
}
```

## Wiring It Up

Wrap your game in the provider:

```jsx
import { Stage } from '@pixi/react';
import { GameStateProvider } from './hooks/useGameState';

function App() {
  return (
    <GameStateProvider>
      <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>
        <GameContent />
      </Stage>
    </GameStateProvider>
  );
}
```

**Important:** The `GameStateProvider` wraps the `<Stage>`, not the other way around. Context providers must be above the consumers in the React tree. Since `<Stage>` creates a separate React reconciler, the context needs to be outside it.

Actually — there's a catch. @pixi/react v7's `<Stage>` creates its own React root. Context from outside doesn't flow in automatically. The fix:

```jsx
function App() {
  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>
      <GameStateProvider>
        <GameContent />
      </GameStateProvider>
    </Stage>
  );
}
```

Put the provider **inside** the Stage. Now all PixiJS components can access it.

## Using State in Components

### Player takes damage:

```jsx
function Player({ mapData, sheet, posRef }) {
  const dispatch = useGameDispatch();
  const { gameOver } = useGameState();

  // When enemy collision is detected (from Chapter 8)
  function onEnemyHit(enemy) {
    dispatch({ type: 'TAKE_DAMAGE', amount: 1 });
  }

  // Don't process input if game over
  useTick((delta) => {
    if (gameOver) return;
    // ... movement code
  });

  // ...
}
```

### Collecting items:

```jsx
function onCollect(item) {
  switch (item.type) {
    case 'key':
      dispatch({ type: 'COLLECT_KEY' });
      break;
    case 'coin':
      dispatch({ type: 'ADD_SCORE', amount: 10 });
      break;
    case 'potion':
      dispatch({ type: 'HEAL', amount: 3 });
      break;
  }
}
```

## The HUD

A heads-up display showing health, score, and keys:

```jsx
import { Container, Graphics, Text, Sprite } from '@pixi/react';
import { useGameState } from '../hooks/useGameState';
import * as PIXI from 'pixi.js';
import { useCallback } from 'react';

function HUD() {
  const { health, maxHealth, score, keys, level } = useGameState();

  return (
    <Container x={0} y={0}>
      {/* Health bar */}
      <HealthBar x={20} y={10} health={health} maxHealth={maxHealth} />

      {/* Heart icon */}
      <Sprite image="./sprites/heart.png" x={4} y={6} scale={1.5} />

      {/* Score */}
      <Text
        text={`${score}`}
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 12, fill: 0xffd700 })}
        x={20}
        y={24}
      />
      <Sprite image="./sprites/coin.png" x={4} y={24} scale={1.5} />

      {/* Keys */}
      <Text
        text={`×${keys}`}
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 12, fill: 0xcccccc })}
        x={20}
        y={40}
      />
      <Sprite image="./sprites/key.png" x={4} y={40} scale={1.5} />

      {/* Level indicator */}
      <Text
        text={`Floor ${level}`}
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 10, fill: 0x888888 })}
        x={420}
        y={6}
      />
    </Container>
  );
}
```

### The Health Bar (from Chapter 3, now connected to state):

```jsx
function HealthBar({ x, y, health, maxHealth }) {
  const barWidth = 80;
  const barHeight = 8;
  const fillWidth = (health / maxHealth) * barWidth;
  const pct = health / maxHealth;
  const color = pct > 0.5 ? 0x44ff44 : pct > 0.25 ? 0xffaa00 : 0xff4444;

  const draw = useCallback((g) => {
    g.clear();
    g.lineStyle(1, 0xffffff, 0.5);
    g.drawRect(-1, -1, barWidth + 2, barHeight + 2);
    g.lineStyle(0);
    g.beginFill(0x1a1a1a);
    g.drawRect(0, 0, barWidth, barHeight);
    g.endFill();
    g.beginFill(color);
    g.drawRect(0, 0, fillWidth, barHeight);
    g.endFill();
  }, [fillWidth, color]);

  return <Graphics draw={draw} x={x} y={y} />;
}
```

## Game Over Screen

When health hits zero:

```jsx
function GameOverScreen() {
  const { gameOver, score } = useGameState();
  const dispatch = useGameDispatch();

  if (!gameOver) return null;

  const bgDraw = useCallback((g) => {
    g.clear();
    g.beginFill(0x000000, 0.7);
    g.drawRect(0, 0, 480, 320);
    g.endFill();
  }, []);

  return (
    <Container>
      <Graphics draw={bgDraw} />
      <Text
        text="GAME OVER"
        style={new PIXI.TextStyle({
          fontFamily: 'monospace',
          fontSize: 32,
          fill: 0xff4444,
          fontWeight: 'bold',
        })}
        anchor={0.5}
        x={240}
        y={120}
      />
      <Text
        text={`Score: ${score}`}
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 16, fill: 0xffffff })}
        anchor={0.5}
        x={240}
        y={170}
      />
      <Text
        text="[SPACE] to restart"
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 12, fill: 0x888888 })}
        anchor={0.5}
        x={240}
        y={220}
      />
    </Container>
  );
}
```

### Restart Logic

```jsx
function GameManager() {
  const { gameOver } = useGameState();
  const dispatch = useGameDispatch();

  useEffect(() => {
    function handleRestart(e) {
      if (gameOver && e.key === ' ') {
        dispatch({ type: 'RESTART' });
      }
    }
    window.addEventListener('keydown', handleRestart);
    return () => window.removeEventListener('keydown', handleRestart);
  }, [gameOver, dispatch]);

  return null;  // logic-only component
}
```

## Pause Menu

```jsx
function PauseOverlay() {
  const { paused } = useGameState();
  const dispatch = useGameDispatch();

  useEffect(() => {
    function handlePause(e) {
      if (e.key === 'Escape') {
        dispatch({ type: 'PAUSE' });
      }
    }
    window.addEventListener('keydown', handlePause);
    return () => window.removeEventListener('keydown', handlePause);
  }, [dispatch]);

  if (!paused) return null;

  const bgDraw = useCallback((g) => {
    g.clear();
    g.beginFill(0x000000, 0.5);
    g.drawRect(0, 0, 480, 320);
    g.endFill();
  }, []);

  return (
    <Container>
      <Graphics draw={bgDraw} />
      <Text
        text="PAUSED"
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 24, fill: 0xffffff })}
        anchor={0.5}
        x={240}
        y={140}
      />
      <Text
        text="[ESC] to resume"
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 12, fill: 0x888888 })}
        anchor={0.5}
        x={240}
        y={180}
      />
    </Container>
  );
}
```

## The Full Game Structure

```jsx
function GameContent() {
  const { gameOver, paused } = useGameState();

  return (
    <>
      <World paused={paused || gameOver} />
      <HUD />
      <PauseOverlay />
      <GameOverScreen />
      <GameManager />
    </>
  );
}

function App() {
  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>
      <GameStateProvider>
        <GameContent />
      </GameStateProvider>
    </Stage>
  );
}
```

## Verify

- [ ] Health decreases when hit by enemies
- [ ] Score increases when collecting coins
- [ ] Key count updates on pickup
- [ ] HUD displays all values correctly
- [ ] Game over screen appears at 0 health
- [ ] Space restarts the game
- [ ] Escape pauses/unpauses
- [ ] Game loop stops when paused or game over

Kai: "It's a real game now. Health, score, game over. But it feels flat. No sound when you pick up a coin. No particles when you hit a slime. It needs juice."

Polish time. That's Chapter 10.

---

[← Chapter 8: Collision](chapter-08-collision.md) | [Chapter 10: Sound & Particles →](chapter-10-sound-particles.md)
