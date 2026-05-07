# Chapter 11: Levels & Scenes — "Multiple Rooms and Screens"

[← Chapter 10: Sound & Particles](chapter-10-sound-particles.md) | [Chapter 12: Deploy →](chapter-12-deploy.md)

---

## The Crisis

DungeonBit has one room. One screen. No title. No progression. Kai drew five dungeon floors and a boss room. You need a title screen, gameplay with multiple levels, and a victory screen.

Kai: "Title screen → press start → floor 1 → door → floor 2 → ... → boss → win. That's the game."

## Scene Architecture

In React terms, scenes are just conditional rendering. Show one component tree at a time:

```jsx
function App() {
  const [scene, setScene] = useState('title');

  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>
      {scene === 'title' && <TitleScreen onStart={() => setScene('gameplay')} />}
      {scene === 'gameplay' && <Gameplay onWin={() => setScene('victory')} onDeath={() => setScene('gameover')} />}
      {scene === 'gameover' && <GameOverScreen onRestart={() => setScene('title')} />}
      {scene === 'victory' && <VictoryScreen onRestart={() => setScene('title')} />}
    </Stage>
  );
}
```

Simple. No router needed. No complex state machine. Just a string that determines which component renders.

## Title Screen

```jsx
import { Container, Text, Sprite, Graphics } from '@pixi/react';
import * as PIXI from 'pixi.js';
import { useEffect, useRef } from 'react';
import { useTick } from '@pixi/react';

function TitleScreen({ onStart }) {
  const promptRef = useRef(null);

  // Blink "Press SPACE" text
  useTick(() => {
    if (!promptRef.current) return;
    promptRef.current.alpha = Math.sin(Date.now() / 400) * 0.4 + 0.6;
  });

  // Listen for start input
  useEffect(() => {
    function handleKey(e) {
      if (e.key === ' ' || e.key === 'Enter') {
        onStart();
      }
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onStart]);

  return (
    <Container>
      {/* Title */}
      <Text
        text="DungeonBit"
        style={new PIXI.TextStyle({
          fontFamily: 'monospace',
          fontSize: 36,
          fill: 0xffd700,
          fontWeight: 'bold',
          dropShadow: true,
          dropShadowColor: 0x000000,
          dropShadowDistance: 3,
        })}
        anchor={0.5}
        x={240}
        y={100}
      />

      {/* Subtitle */}
      <Text
        text="A 48-hour game jam dungeon crawler"
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 10, fill: 0x888888 })}
        anchor={0.5}
        x={240}
        y={140}
      />

      {/* Character preview */}
      <Sprite image="./sprites/knight.png" x={240} y={200} anchor={0.5} scale={4} />

      {/* Start prompt */}
      <Text
        ref={promptRef}
        text="[ SPACE ] to start"
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 14, fill: 0xcccccc })}
        anchor={0.5}
        x={240}
        y={280}
      />
    </Container>
  );
}
```

## Level Data Structure

Store each floor as a separate data file:

```jsx
// src/data/levels.js
export const levels = [
  {
    id: 1,
    name: "The Entrance",
    map: [
      [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
      [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
      // ... more rows
      [1,1,1,1,1,1,1,1,1,3,3,1,1,1,1,1,1,1,1,1],
    ],
    playerStart: { x: 240, y: 200 },
    enemies: [
      { type: 'slime', x: 350, y: 180 },
      { type: 'slime', x: 120, y: 250 },
    ],
    items: [
      { type: 'coin', x: 300, y: 100 },
      { type: 'coin', x: 400, y: 200 },
      { type: 'key', x: 200, y: 280 },
    ],
    doors: [
      { x: 384, y: 630, width: 96, height: 48, requiresKey: true, target: 2 },
    ],
  },
  {
    id: 2,
    name: "The Depths",
    map: [/* ... */],
    playerStart: { x: 240, y: 50 },
    enemies: [/* ... */],
    items: [/* ... */],
    doors: [/* ... */],
  },
  // ... more levels
];
```

## Level Loading in Gameplay

```jsx
function Gameplay({ onWin, onDeath }) {
  const [currentLevel, setCurrentLevel] = useState(0);
  const levelData = levels[currentLevel];

  function handleDoorEnter(door) {
    if (door.requiresKey && keys < 1) return;  // need a key

    if (door.target > levels.length) {
      onWin();  // beat the last level
      return;
    }

    // Transition to next level
    setCurrentLevel(door.target - 1);
  }

  function handlePlayerDeath() {
    onDeath();
  }

  return (
    <GameStateProvider>
      <DungeonFloor
        level={levelData}
        onDoorEnter={handleDoorEnter}
        onDeath={handlePlayerDeath}
      />
    </GameStateProvider>
  );
}
```

## The Dungeon Floor Component

```jsx
function DungeonFloor({ level, onDoorEnter, onDeath }) {
  const playerPos = useRef({ ...level.playerStart });
  const worldRef = useRef(null);
  const { gameOver } = useGameState();

  useEffect(() => {
    if (gameOver) onDeath();
  }, [gameOver, onDeath]);

  // Reset player position when level changes
  useEffect(() => {
    playerPos.current = { ...level.playerStart };
  }, [level]);

  return (
    <>
      <Container ref={worldRef}>
        <Tilemap tileSheet={assets.tiles} mapData={level.map} />
        <ItemLayer items={level.items} />
        <EnemyLayer enemies={level.enemies} />
        <Player posRef={playerPos} mapData={level.map} />
      </Container>
      <HUD />
      <LevelTitle name={level.name} />
    </>
  );
}
```

## Scene Transitions

A simple fade transition between scenes:

```jsx
function FadeTransition({ active, duration = 500, onComplete }) {
  const ref = useRef(null);
  const startTime = useRef(null);

  useTick(() => {
    if (!active || !ref.current) return;

    if (!startTime.current) startTime.current = Date.now();
    const elapsed = Date.now() - startTime.current;
    const progress = Math.min(1, elapsed / duration);

    ref.current.alpha = progress;

    if (progress >= 1) {
      startTime.current = null;
      onComplete?.();
    }
  });

  const draw = useCallback((g) => {
    g.clear();
    g.beginFill(0x000000);
    g.drawRect(0, 0, 480, 320);
    g.endFill();
  }, []);

  if (!active) return null;
  return <Graphics ref={ref} draw={draw} alpha={0} />;
}
```

### Using Transitions

```jsx
function App() {
  const [scene, setScene] = useState('title');
  const [transitioning, setTransitioning] = useState(false);
  const [nextScene, setNextScene] = useState(null);

  function transitionTo(target) {
    setNextScene(target);
    setTransitioning(true);
  }

  function onTransitionComplete() {
    setScene(nextScene);
    setTransitioning(false);
    setNextScene(null);
  }

  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>
      {scene === 'title' && <TitleScreen onStart={() => transitionTo('gameplay')} />}
      {scene === 'gameplay' && <Gameplay onWin={() => transitionTo('victory')} onDeath={() => transitionTo('gameover')} />}
      {scene === 'gameover' && <GameOverScreen onRestart={() => transitionTo('title')} />}
      {scene === 'victory' && <VictoryScreen onRestart={() => transitionTo('title')} />}

      <FadeTransition active={transitioning} onComplete={onTransitionComplete} />
    </Stage>
  );
}
```

## Level Title Card

Show the floor name briefly when entering a new level:

```jsx
function LevelTitle({ name }) {
  const ref = useRef(null);
  const startTime = useRef(Date.now());

  useTick(() => {
    if (!ref.current) return;
    const elapsed = (Date.now() - startTime.current) / 1000;

    if (elapsed < 1) {
      // Fade in
      ref.current.alpha = elapsed;
    } else if (elapsed < 3) {
      // Hold
      ref.current.alpha = 1;
    } else if (elapsed < 4) {
      // Fade out
      ref.current.alpha = 1 - (elapsed - 3);
    } else {
      ref.current.alpha = 0;
    }
  });

  return (
    <Text
      ref={ref}
      text={name}
      style={new PIXI.TextStyle({
        fontFamily: 'monospace',
        fontSize: 18,
        fill: 0xffffff,
        fontWeight: 'bold',
      })}
      anchor={0.5}
      x={240}
      y={160}
      alpha={0}
    />
  );
}
```

## Victory Screen

```jsx
function VictoryScreen({ onRestart }) {
  useEffect(() => {
    function handleKey(e) {
      if (e.key === ' ') onRestart();
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onRestart]);

  return (
    <Container>
      <Text
        text="YOU ESCAPED!"
        style={new PIXI.TextStyle({
          fontFamily: 'monospace',
          fontSize: 28,
          fill: 0x44ff44,
          fontWeight: 'bold',
        })}
        anchor={0.5}
        x={240}
        y={100}
      />
      <Text
        text="The dungeon crumbles behind you.\nDaylight. Fresh air. Freedom."
        style={new PIXI.TextStyle({
          fontFamily: 'monospace',
          fontSize: 11,
          fill: 0xcccccc,
          align: 'center',
        })}
        anchor={0.5}
        x={240}
        y={160}
      />
      <Sprite image="./sprites/knight.png" x={240} y={220} anchor={0.5} scale={4} />
      <Text
        text="[ SPACE ] to play again"
        style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 12, fill: 0x888888 })}
        anchor={0.5}
        x={240}
        y={290}
      />
    </Container>
  );
}
```

## Level Progression Flow

```
Title Screen
    │ [SPACE]
    ▼
Floor 1: "The Entrance"
    │ find key → open door
    ▼
Floor 2: "The Depths"
    │ find key → open door
    ▼
Floor 3: "The Crypt"
    │ find key → open door
    ▼
Floor 4: "The Boss Room"
    │ defeat boss
    ▼
Victory Screen
    │ [SPACE]
    ▼
Title Screen
```

## Verify

- [ ] Title screen renders with blinking prompt
- [ ] SPACE starts the game
- [ ] Multiple levels load correctly
- [ ] Doors transition to the next level
- [ ] Fade transitions work between scenes
- [ ] Level title card appears and fades
- [ ] Victory screen shows after the last level
- [ ] Game over returns to title
- [ ] Player position resets on new level

Kai: "It's done. Five floors, a title screen, a win condition. Now we need to ship it. The jam deadline is in 3 hours."

Deploy to GitHub Pages. That's Chapter 12.

---

[← Chapter 10: Sound & Particles](chapter-10-sound-particles.md) | [Chapter 12: Deploy →](chapter-12-deploy.md)
