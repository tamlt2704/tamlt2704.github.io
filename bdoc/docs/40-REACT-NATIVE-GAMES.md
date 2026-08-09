# Chapter 40: Game Building with React Native

## What you'll learn

- Game loop architecture (update → render → repeat at 60fps)
- React Native game engines: Skia, Reanimated, react-native-game-engine
- Drawing with Skia (GPU-accelerated 2D canvas)
- Physics simulation (gravity, collision, velocity)
- Touch input: tap, drag, swipe for game controls
- Sprite animation and frame-based rendering
- Build 3 games: Flappy Bird, Snake, 2048
- Sound effects and haptics
- Performance: staying at 60fps under load

---

## PART 1: Game Architecture

## 40.1 The game loop

Every game follows this pattern:

```
┌─────────────────────────────────────┐
│          GAME LOOP (60fps)          │
│                                     │
│  1. PROCESS INPUT (touches, swipes) │
│         ↓                           │
│  2. UPDATE STATE (physics, logic)   │
│         ↓                           │
│  3. RENDER (draw everything)        │
│         ↓                           │
│  4. WAIT (until next frame ~16ms)   │
│         ↓                           │
│  └──── REPEAT ─────────────────┘    │
└─────────────────────────────────────┘
```

**In React Native, we have two options:**

| Approach | Rendering | Best for |
|----------|-----------|----------|
| **Skia + Reanimated** | GPU canvas (fast) | Smooth 2D games, particles, custom drawing |
| **react-native-game-engine** | React components (flexible) | Entity-based games, simpler setup |
| **React views + Reanimated** | Native views as game objects | Simple puzzle games (2048, memory) |

## 40.2 Setup

```bash
npx create-expo-app GameApp --template blank-typescript
cd GameApp

# Skia (GPU-accelerated 2D drawing)
npx expo install @shopify/react-native-skia

# Reanimated (60fps animations on UI thread)
npx expo install react-native-reanimated

# Gesture handler (touch controls)
npx expo install react-native-gesture-handler

# Audio
npx expo install expo-av

# Haptics
npx expo install expo-haptics
```

## 40.3 Game loop with Reanimated's `useFrameCallback`

```tsx
import { useFrameCallback, useSharedValue } from "react-native-reanimated";

function useGameLoop(update: (dt: number) => void) {
  const lastTime = useSharedValue(0);

  useFrameCallback((frameInfo) => {
    const now = frameInfo.timestamp;
    if (lastTime.value === 0) {
      lastTime.value = now;
      return;
    }

    const dt = (now - lastTime.value) / 1000; // delta time in seconds
    lastTime.value = now;

    update(dt); // runs on UI thread at 60fps
  });
}
```

**`dt` (delta time):** Time since last frame. Multiply velocities by `dt` for frame-rate-independent movement:
```
// Without dt: moves 5 pixels per frame (speed depends on FPS!)
position += 5;

// With dt: moves 300 pixels per second (consistent regardless of FPS)
position += 300 * dt;
```

## 40.4 Drawing with Skia

```tsx
import { Canvas, Rect, Circle, RoundedRect, Text as SkText, useFont } from "@shopify/react-native-skia";

function GameCanvas() {
  return (
    <Canvas style={{ flex: 1 }}>
      {/* Background */}
      <Rect x={0} y={0} width={400} height={800} color="#0f172a" />

      {/* Player (circle) */}
      <Circle cx={200} cy={400} r={20} color="#3b82f6" />

      {/* Obstacle (rectangle) */}
      <RoundedRect x={100} y={200} width={60} height={200} r={8} color="#ef4444" />

      {/* Score */}
      <SkText x={20} y={50} text="Score: 42" color="#f8fafc" font={font} />
    </Canvas>
  );
}
```

**Skia vs SVG:**
- SVG: each shape is a React component (re-render overhead for many shapes)
- Skia: draws directly to GPU canvas (one component, draws hundreds of shapes efficiently)

For games with 50+ moving objects, Skia is significantly faster than react-native-svg.



---

## PART 2: Build — Flappy Bird Clone

## 40.5 Game state

```tsx
// lib/flappyBird.ts
import { useSharedValue } from "react-native-reanimated";

export type Pipe = {
  x: number;
  gapY: number;     // center of the gap
  passed: boolean;
};

export type GameState = "ready" | "playing" | "gameover";

export function useFlappyBirdGame(screenWidth: number, screenHeight: number) {
  // Bird state
  const birdY = useSharedValue(screenHeight / 2);
  const birdVelocity = useSharedValue(0);

  // Pipes
  const pipes = useSharedValue<Pipe[]>([]);

  // Game
  const score = useSharedValue(0);
  const gameState = useSharedValue<GameState>("ready");

  // Constants
  const GRAVITY = 1200;         // pixels/sec²
  const JUMP_VELOCITY = -400;   // pixels/sec (negative = up)
  const PIPE_SPEED = 200;       // pixels/sec
  const PIPE_GAP = 180;         // gap between top and bottom pipe
  const PIPE_WIDTH = 60;
  const BIRD_RADIUS = 18;
  const PIPE_SPAWN_INTERVAL = 250; // pixels between pipes

  function jump() {
    "worklet";
    if (gameState.value === "ready") {
      gameState.value = "playing";
    }
    if (gameState.value === "playing") {
      birdVelocity.value = JUMP_VELOCITY;
    }
    if (gameState.value === "gameover") {
      reset();
    }
  }

  function reset() {
    "worklet";
    birdY.value = screenHeight / 2;
    birdVelocity.value = 0;
    pipes.value = [];
    score.value = 0;
    gameState.value = "ready";
  }

  function update(dt: number) {
    "worklet";
    if (gameState.value !== "playing") return;

    // Physics: apply gravity to velocity, velocity to position
    birdVelocity.value += GRAVITY * dt;
    birdY.value += birdVelocity.value * dt;

    // Floor/ceiling collision
    if (birdY.value > screenHeight - BIRD_RADIUS || birdY.value < BIRD_RADIUS) {
      gameState.value = "gameover";
      return;
    }

    // Move pipes left
    let updatedPipes = pipes.value.map((pipe) => ({
      ...pipe,
      x: pipe.x - PIPE_SPEED * dt,
    }));

    // Remove off-screen pipes
    updatedPipes = updatedPipes.filter((pipe) => pipe.x > -PIPE_WIDTH);

    // Spawn new pipes
    const lastPipe = updatedPipes[updatedPipes.length - 1];
    if (!lastPipe || lastPipe.x < screenWidth - PIPE_SPAWN_INTERVAL) {
      const gapY = 150 + Math.random() * (screenHeight - 300);
      updatedPipes.push({ x: screenWidth + 50, gapY, passed: false });
    }

    // Collision detection
    const birdX = 80; // bird is at fixed X position
    for (const pipe of updatedPipes) {
      // Bird within pipe X range?
      if (birdX + BIRD_RADIUS > pipe.x && birdX - BIRD_RADIUS < pipe.x + PIPE_WIDTH) {
        // Bird above gap top or below gap bottom?
        const gapTop = pipe.gapY - PIPE_GAP / 2;
        const gapBottom = pipe.gapY + PIPE_GAP / 2;
        if (birdY.value - BIRD_RADIUS < gapTop || birdY.value + BIRD_RADIUS > gapBottom) {
          gameState.value = "gameover";
          return;
        }
      }

      // Score: bird passed the pipe
      if (!pipe.passed && pipe.x + PIPE_WIDTH < birdX) {
        pipe.passed = true;
        score.value += 1;
      }
    }

    pipes.value = updatedPipes;
  }

  return { birdY, birdVelocity, pipes, score, gameState, jump, update, reset };
}
```

## 40.6 Rendering the game

```tsx
// app/flappy.tsx
"use client";

import { View, Text, StyleSheet, useWindowDimensions, Pressable } from "react-native";
import { Canvas, Circle, Rect, RoundedRect, Text as SkText, useFont } from "@shopify/react-native-skia";
import { useFrameCallback, useDerivedValue } from "react-native-reanimated";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import { useFlappyBirdGame } from "@/lib/flappyBird";

export default function FlappyBirdScreen() {
  const { width, height } = useWindowDimensions();
  const game = useFlappyBirdGame(width, height);

  // Game loop
  const lastTime = { current: 0 };
  useFrameCallback((info) => {
    const now = info.timestamp;
    if (lastTime.current === 0) { lastTime.current = now; return; }
    const dt = Math.min((now - lastTime.current) / 1000, 0.05); // cap dt
    lastTime.current = now;
    game.update(dt);
  });

  // Tap anywhere to jump
  const tapGesture = Gesture.Tap().onEnd(() => {
    game.jump();
  });

  return (
    <GestureDetector gesture={tapGesture}>
      <View style={styles.container}>
        <Canvas style={{ flex: 1 }}>
          {/* Sky background */}
          <Rect x={0} y={0} width={width} height={height} color="#87CEEB" />

          {/* Ground */}
          <Rect x={0} y={height - 80} width={width} height={80} color="#8B4513" />

          {/* Pipes */}
          <PipesRenderer pipes={game.pipes} pipeGap={180} pipeWidth={60} screenHeight={height} />

          {/* Bird */}
          <BirdRenderer y={game.birdY} x={80} radius={18} />

          {/* Score */}
          <ScoreRenderer score={game.score} x={width / 2} />
        </Canvas>

        {/* Game over overlay */}
        <GameOverOverlay gameState={game.gameState} score={game.score} />
      </View>
    </GestureDetector>
  );
}

// Bird component (animated circle)
function BirdRenderer({ y, x, radius }: { y: any; x: number; radius: number }) {
  return <Circle cx={x} cy={y} r={radius} color="#f59e0b" />;
}

// Pipes (derived from shared value)
function PipesRenderer({ pipes, pipeGap, pipeWidth, screenHeight }: any) {
  // useDerivedValue to read pipes on UI thread
  const pipeData = useDerivedValue(() => pipes.value);

  // Render each pipe pair (top + bottom)
  return (
    <>
      {pipeData.value.map((pipe: any, i: number) => {
        const gapTop = pipe.gapY - pipeGap / 2;
        const gapBottom = pipe.gapY + pipeGap / 2;
        return (
          <React.Fragment key={i}>
            {/* Top pipe */}
            <RoundedRect
              x={pipe.x} y={0}
              width={pipeWidth} height={gapTop}
              r={8} color="#22c55e"
            />
            {/* Bottom pipe */}
            <RoundedRect
              x={pipe.x} y={gapBottom}
              width={pipeWidth} height={screenHeight - gapBottom - 80}
              r={8} color="#22c55e"
            />
          </React.Fragment>
        );
      })}
    </>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
});
```

## 40.7 Physics concepts used

```
Gravity:
  velocity += GRAVITY × dt        (accelerate downward)
  position += velocity × dt        (move by current speed)

Jump:
  velocity = JUMP_VELOCITY         (instant upward speed)

Collision (AABB — Axis-Aligned Bounding Box):
  Two rectangles overlap if:
    rect1.left < rect2.right  AND
    rect1.right > rect2.left  AND
    rect1.top < rect2.bottom  AND
    rect1.bottom > rect2.top

Circle-Rectangle collision:
  Find closest point on rect to circle center
  If distance(closest, center) < radius → collision
```



---

## PART 3: Build — Snake Game

## 40.8 Snake game state

```tsx
// lib/snake.ts
type Point = { x: number; y: number };
type Direction = "UP" | "DOWN" | "LEFT" | "RIGHT";

export function useSnakeGame(gridSize: number = 20) {
  const GRID = gridSize;
  const TICK_RATE = 150; // ms per move

  const [snake, setSnake] = useState<Point[]>([{ x: 10, y: 10 }]);
  const [food, setFood] = useState<Point>(randomFood());
  const [direction, setDirection] = useState<Direction>("RIGHT");
  const [gameOver, setGameOver] = useState(false);
  const [score, setScore] = useState(0);

  function randomFood(): Point {
    return {
      x: Math.floor(Math.random() * GRID),
      y: Math.floor(Math.random() * GRID),
    };
  }

  function changeDirection(newDir: Direction) {
    // Prevent 180° turns (can't go opposite direction)
    const opposites: Record<Direction, Direction> = {
      UP: "DOWN", DOWN: "UP", LEFT: "RIGHT", RIGHT: "LEFT",
    };
    if (opposites[newDir] !== direction) {
      setDirection(newDir);
    }
  }

  function tick() {
    if (gameOver) return;

    setSnake((prev) => {
      const head = prev[0];
      const moves: Record<Direction, Point> = {
        UP: { x: head.x, y: head.y - 1 },
        DOWN: { x: head.x, y: head.y + 1 },
        LEFT: { x: head.x - 1, y: head.y },
        RIGHT: { x: head.x + 1, y: head.y },
      };
      const newHead = moves[direction];

      // Wall collision
      if (newHead.x < 0 || newHead.x >= GRID || newHead.y < 0 || newHead.y >= GRID) {
        setGameOver(true);
        return prev;
      }

      // Self collision
      if (prev.some((p) => p.x === newHead.x && p.y === newHead.y)) {
        setGameOver(true);
        return prev;
      }

      const newSnake = [newHead, ...prev];

      // Eat food?
      if (newHead.x === food.x && newHead.y === food.y) {
        setScore((s) => s + 1);
        setFood(randomFood());
        // Don't remove tail (snake grows)
      } else {
        newSnake.pop(); // remove tail (snake moves)
      }

      return newSnake;
    });
  }

  // Auto-tick
  useEffect(() => {
    if (gameOver) return;
    const timer = setInterval(tick, TICK_RATE);
    return () => clearInterval(timer);
  }, [direction, gameOver, food]);

  function restart() {
    setSnake([{ x: 10, y: 10 }]);
    setFood(randomFood());
    setDirection("RIGHT");
    setGameOver(false);
    setScore(0);
  }

  return { snake, food, score, gameOver, direction, changeDirection, restart, GRID };
}
```

## 40.9 Snake rendering + swipe controls

```tsx
// app/snake.tsx
import { View, StyleSheet, useWindowDimensions } from "react-native";
import { Canvas, Rect, RoundedRect } from "@shopify/react-native-skia";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import { useSnakeGame } from "@/lib/snake";

export default function SnakeScreen() {
  const { width } = useWindowDimensions();
  const cellSize = Math.floor((width - 32) / 20); // fit 20 cells in screen width
  const canvasSize = cellSize * 20;
  const game = useSnakeGame(20);

  // Swipe to change direction
  const swipeGesture = Gesture.Pan().onEnd((e) => {
    const { translationX, translationY } = e;
    if (Math.abs(translationX) > Math.abs(translationY)) {
      game.changeDirection(translationX > 0 ? "RIGHT" : "LEFT");
    } else {
      game.changeDirection(translationY > 0 ? "DOWN" : "UP");
    }
  });

  // Tap to restart when game over
  const tapGesture = Gesture.Tap().onEnd(() => {
    if (game.gameOver) game.restart();
  });

  const gesture = Gesture.Race(swipeGesture, tapGesture);

  return (
    <GestureDetector gesture={gesture}>
      <View style={styles.container}>
        <Canvas style={{ width: canvasSize, height: canvasSize }}>
          {/* Grid background */}
          <Rect x={0} y={0} width={canvasSize} height={canvasSize} color="#1a1a2e" />

          {/* Snake body */}
          {game.snake.map((segment, i) => (
            <RoundedRect
              key={i}
              x={segment.x * cellSize + 1}
              y={segment.y * cellSize + 1}
              width={cellSize - 2}
              height={cellSize - 2}
              r={4}
              color={i === 0 ? "#22c55e" : "#4ade80"} // head is darker
            />
          ))}

          {/* Food */}
          <RoundedRect
            x={game.food.x * cellSize + 2}
            y={game.food.y * cellSize + 2}
            width={cellSize - 4}
            height={cellSize - 4}
            r={cellSize / 2}
            color="#ef4444"
          />
        </Canvas>
      </View>
    </GestureDetector>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f0f23", alignItems: "center", justifyContent: "center" },
});
```

---

## PART 4: Build — 2048 Puzzle

## 40.10 2048 game logic

```tsx
// lib/game2048.ts
type Grid = (number | null)[][];

export function useGame2048() {
  const SIZE = 4;
  const [grid, setGrid] = useState<Grid>(initGrid());
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);

  function initGrid(): Grid {
    const g: Grid = Array.from({ length: SIZE }, () => Array(SIZE).fill(null));
    addRandomTile(g);
    addRandomTile(g);
    return g;
  }

  function addRandomTile(g: Grid) {
    const empty: [number, number][] = [];
    for (let r = 0; r < SIZE; r++)
      for (let c = 0; c < SIZE; c++)
        if (g[r][c] === null) empty.push([r, c]);

    if (empty.length === 0) return;
    const [r, c] = empty[Math.floor(Math.random() * empty.length)];
    g[r][c] = Math.random() < 0.9 ? 2 : 4;
  }

  function slide(row: (number | null)[]): { result: (number | null)[]; points: number } {
    // Remove nulls, merge adjacent equals, pad with nulls
    const nums = row.filter((n): n is number => n !== null);
    const merged: number[] = [];
    let points = 0;
    let skip = false;

    for (let i = 0; i < nums.length; i++) {
      if (skip) { skip = false; continue; }
      if (i + 1 < nums.length && nums[i] === nums[i + 1]) {
        merged.push(nums[i] * 2);
        points += nums[i] * 2;
        skip = true;
      } else {
        merged.push(nums[i]);
      }
    }

    // Pad with nulls to original length
    while (merged.length < SIZE) merged.push(null as any);
    return { result: merged as (number | null)[], points };
  }

  function move(direction: "UP" | "DOWN" | "LEFT" | "RIGHT") {
    if (gameOver) return;

    let newGrid = grid.map((row) => [...row]);
    let totalPoints = 0;
    let moved = false;

    function getRow(r: number, c: number): (number | null)[] {
      switch (direction) {
        case "LEFT": return newGrid[r];
        case "RIGHT": return [...newGrid[r]].reverse();
        case "UP": return newGrid.map((row) => row[c]);
        case "DOWN": return newGrid.map((row) => row[c]).reverse();
      }
    }

    function setRow(r: number, c: number, result: (number | null)[]) {
      switch (direction) {
        case "LEFT": newGrid[r] = result; break;
        case "RIGHT": newGrid[r] = [...result].reverse(); break;
        case "UP": result.forEach((val, i) => (newGrid[i][c] = val)); break;
        case "DOWN": [...result].reverse().forEach((val, i) => (newGrid[i][c] = val)); break;
      }
    }

    const iterations = direction === "UP" || direction === "DOWN" ? SIZE : SIZE;
    for (let i = 0; i < SIZE; i++) {
      const row = getRow(i, i);
      const original = [...row];
      const { result, points } = slide(row);
      totalPoints += points;
      if (JSON.stringify(original) !== JSON.stringify(result)) moved = true;
      setRow(i, i, result);
    }

    if (moved) {
      addRandomTile(newGrid);
      setGrid(newGrid);
      setScore((s) => s + totalPoints);

      // Check game over
      if (isGameOver(newGrid)) setGameOver(true);
    }
  }

  function isGameOver(g: Grid): boolean {
    // Any empty cell? Not over.
    for (let r = 0; r < SIZE; r++)
      for (let c = 0; c < SIZE; c++)
        if (g[r][c] === null) return false;

    // Any adjacent equal values? Not over.
    for (let r = 0; r < SIZE; r++)
      for (let c = 0; c < SIZE; c++) {
        if (c + 1 < SIZE && g[r][c] === g[r][c + 1]) return false;
        if (r + 1 < SIZE && g[r][c] === g[r + 1][c]) return false;
      }

    return true;
  }

  function restart() {
    setGrid(initGrid());
    setScore(0);
    setGameOver(false);
  }

  return { grid, score, gameOver, move, restart };
}
```

## 40.11 2048 rendering with tile colours

```tsx
// app/game2048.tsx
import { View, Text, StyleSheet, useWindowDimensions } from "react-native";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import { useGame2048 } from "@/lib/game2048";

const TILE_COLORS: Record<number, { bg: string; text: string }> = {
  2:    { bg: "#eee4da", text: "#776e65" },
  4:    { bg: "#ede0c8", text: "#776e65" },
  8:    { bg: "#f2b179", text: "#f9f6f2" },
  16:   { bg: "#f59563", text: "#f9f6f2" },
  32:   { bg: "#f67c5f", text: "#f9f6f2" },
  64:   { bg: "#f65e3b", text: "#f9f6f2" },
  128:  { bg: "#edcf72", text: "#f9f6f2" },
  256:  { bg: "#edcc61", text: "#f9f6f2" },
  512:  { bg: "#edc850", text: "#f9f6f2" },
  1024: { bg: "#edc53f", text: "#f9f6f2" },
  2048: { bg: "#edc22e", text: "#f9f6f2" },
};

export default function Game2048Screen() {
  const { width } = useWindowDimensions();
  const game = useGame2048();
  const tileSize = (width - 64) / 4 - 8;

  const swipeGesture = Gesture.Pan()
    .minDistance(30)
    .onEnd((e) => {
      const { translationX: tx, translationY: ty } = e;
      if (Math.abs(tx) > Math.abs(ty)) {
        game.move(tx > 0 ? "RIGHT" : "LEFT");
      } else {
        game.move(ty > 0 ? "DOWN" : "UP");
      }
    });

  return (
    <GestureDetector gesture={swipeGesture}>
      <View style={styles.container}>
        <Text style={styles.score}>Score: {game.score}</Text>

        <View style={styles.board}>
          {game.grid.map((row, r) => (
            <View key={r} style={styles.row}>
              {row.map((value, c) => {
                const colors = value ? TILE_COLORS[value] || { bg: "#3c3a32", text: "#f9f6f2" } : null;
                return (
                  <View
                    key={c}
                    style={[
                      styles.tile,
                      { width: tileSize, height: tileSize },
                      colors && { backgroundColor: colors.bg },
                    ]}
                  >
                    {value && (
                      <Text style={[
                        styles.tileText,
                        { color: colors!.text },
                        value >= 1000 && { fontSize: 20 },
                      ]}>
                        {value}
                      </Text>
                    )}
                  </View>
                );
              })}
            </View>
          ))}
        </View>

        {game.gameOver && (
          <View style={styles.overlay}>
            <Text style={styles.gameOverText}>Game Over!</Text>
            <Text style={styles.finalScore}>Final Score: {game.score}</Text>
          </View>
        )}
      </View>
    </GestureDetector>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#faf8ef", alignItems: "center", justifyContent: "center" },
  score: { fontSize: 24, fontWeight: "bold", color: "#776e65", marginBottom: 16 },
  board: { backgroundColor: "#bbada0", borderRadius: 8, padding: 8, gap: 8 },
  row: { flexDirection: "row", gap: 8 },
  tile: {
    borderRadius: 6,
    backgroundColor: "#cdc1b4",
    alignItems: "center",
    justifyContent: "center",
  },
  tileText: { fontSize: 28, fontWeight: "bold" },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(238,228,218,0.7)",
    alignItems: "center",
    justifyContent: "center",
  },
  gameOverText: { fontSize: 40, fontWeight: "bold", color: "#776e65" },
  finalScore: { fontSize: 20, color: "#776e65", marginTop: 8 },
});
```



---

## PART 5: Polish — Sound, Particles, Performance

## 40.12 Sound effects

```tsx
// lib/audio.ts
import { Audio } from "expo-av";

class GameAudio {
  private sounds: Record<string, Audio.Sound> = {};

  async load() {
    const { sound: jump } = await Audio.Sound.createAsync(require("@/assets/sounds/jump.mp3"));
    const { sound: score } = await Audio.Sound.createAsync(require("@/assets/sounds/score.mp3"));
    const { sound: hit } = await Audio.Sound.createAsync(require("@/assets/sounds/hit.mp3"));
    this.sounds = { jump, score, hit };
  }

  async play(name: "jump" | "score" | "hit") {
    const sound = this.sounds[name];
    if (!sound) return;
    await sound.replayAsync(); // restart from beginning
  }

  async cleanup() {
    for (const sound of Object.values(this.sounds)) {
      await sound.unloadAsync();
    }
  }
}

export const gameAudio = new GameAudio();

// Usage in component:
useEffect(() => {
  gameAudio.load();
  return () => { gameAudio.cleanup(); };
}, []);

// In game logic:
function jump() {
  birdVelocity.value = JUMP_VELOCITY;
  gameAudio.play("jump");
}
```

## 40.13 Particle effects (Skia)

```tsx
// components/Particles.tsx
import { Canvas, Circle } from "@shopify/react-native-skia";
import { useSharedValue, useFrameCallback } from "react-native-reanimated";

type Particle = {
  x: number; y: number;
  vx: number; vy: number;
  radius: number;
  opacity: number;
  color: string;
};

export function useParticleSystem() {
  const particles = useSharedValue<Particle[]>([]);

  function emit(x: number, y: number, count: number = 10) {
    "worklet";
    const newParticles: Particle[] = [];
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 100 + Math.random() * 200;
      newParticles.push({
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        radius: 3 + Math.random() * 5,
        opacity: 1,
        color: ["#f59e0b", "#ef4444", "#22c55e", "#3b82f6"][Math.floor(Math.random() * 4)],
      });
    }
    particles.value = [...particles.value, ...newParticles];
  }

  function update(dt: number) {
    "worklet";
    particles.value = particles.value
      .map((p) => ({
        ...p,
        x: p.x + p.vx * dt,
        y: p.y + p.vy * dt + 200 * dt, // gravity
        opacity: p.opacity - dt * 2, // fade out
        radius: p.radius * (1 - dt), // shrink
      }))
      .filter((p) => p.opacity > 0); // remove dead particles
  }

  return { particles, emit, update };
}

// Render particles in Skia Canvas
function ParticleRenderer({ particles }: { particles: any }) {
  const data = useDerivedValue(() => particles.value);

  return (
    <>
      {data.value.map((p: Particle, i: number) => (
        <Circle
          key={i}
          cx={p.x}
          cy={p.y}
          r={p.radius}
          color={p.color}
          opacity={p.opacity}
        />
      ))}
    </>
  );
}
```

## 40.14 Performance checklist for games

| Issue | Symptom | Fix |
|-------|---------|-----|
| JS thread busy | Dropped frames, laggy input | Move game logic to UI thread (worklets) |
| Too many re-renders | Stuttering | Use shared values, not useState for positions |
| Large arrays in shared values | Slow serialization | Limit particles (50 max), pool objects |
| Heavy collision checks | Lag on many objects | Spatial partitioning (grid-based) |
| GC pauses | Periodic stutters | Avoid allocations in game loop (reuse objects) |
| PNG sprites too large | High memory | Compress, use sprite sheets, limit resolution |

**Critical rule for React Native games:**

```tsx
// ❌ useState for positions = re-renders = 60 re-renders/sec = laggy
const [birdY, setBirdY] = useState(200);

// ✅ useSharedValue = updates on UI thread = no re-renders = smooth
const birdY = useSharedValue(200);
```

**Object pooling for particles:**
```tsx
// ❌ Create new objects every frame (GC pressure)
particles.value = particles.value.map(p => ({ ...p, x: p.x + p.vx }));

// ✅ Reuse a fixed-size array, toggle active flag
const MAX_PARTICLES = 50;
const pool = useSharedValue(Array.from({ length: MAX_PARTICLES }, () => ({
  active: false, x: 0, y: 0, vx: 0, vy: 0, opacity: 0,
})));
```

## 40.15 Game architecture patterns

```
┌───────────────────────────────────────────────────────┐
│                    GAME STRUCTURE                       │
├───────────────────────────────────────────────────────┤
│                                                        │
│  Screens (app/ directory):                             │
│    menu.tsx        → Start, settings, high scores      │
│    game.tsx        → Active gameplay                    │
│    gameover.tsx    → Results, retry                     │
│                                                        │
│  Game Logic (lib/):                                    │
│    useGameLoop     → Frame callback, dt calculation    │
│    usePhysics      → Gravity, velocity, collision      │
│    useInput        → Gesture → game actions            │
│    useScoring      → Points, combos, high score        │
│                                                        │
│  Rendering (components/):                              │
│    <Canvas>        → Skia GPU rendering                │
│    <GestureDetector> → Touch handling                  │
│    <Animated.View> → UI overlays (score, menus)        │
│                                                        │
│  Assets:                                               │
│    sounds/         → jump.mp3, score.mp3, hit.mp3      │
│    sprites/        → character.png, bg.png             │
│    fonts/          → pixel-font.ttf                    │
│                                                        │
└───────────────────────────────────────────────────────┘
```

## 40.16 More game ideas to build

| Game | Difficulty | Key concepts learned |
|------|-----------|---------------------|
| Tic-Tac-Toe | Easy | Grid state, win detection, two players |
| Memory Match | Easy | Card flip animation, timer, pairs matching |
| Breakout/Arkanoid | Medium | Ball physics, paddle control, brick collision |
| Wordle clone | Medium | Keyboard input, letter states, word validation |
| Platformer | Hard | Tilemap, sprite animation, jump physics, camera follow |
| Tower defence | Hard | Pathfinding, spawn waves, projectile targeting |
| Tetris | Medium | Rotation matrices, line clearing, piece preview |

---

## Summary

✅ Game loop architecture: input → update → render at 60fps
✅ Skia for GPU-accelerated 2D drawing (Canvas, Rect, Circle, RoundedRect)
✅ Reanimated shared values for lag-free game state (no useState for positions)
✅ Gesture handling: tap (Flappy Bird), swipe (Snake, 2048), pan (drag)
✅ Physics: gravity, velocity, AABB collision detection
✅ Built 3 games: Flappy Bird (physics), Snake (grid-based), 2048 (puzzle logic)
✅ Sound effects with expo-av
✅ Particle systems with Skia
✅ Performance: UI thread worklets, object pooling, spatial partitioning

## Key takeaways

**React Native CAN do games** — but it's not Unity. Good for 2D casual games (puzzle, arcade, card games). Not suitable for complex 3D or heavy physics simulations.

**Shared values are your game state.** `useSharedValue` runs on the UI thread — it's your position, velocity, and score. `useState` triggers React re-renders — use it only for UI elements (menus, overlays) that change infrequently.

**Skia is your game renderer.** It draws directly to the GPU canvas — hundreds of shapes at 60fps. Don't use React Native `<View>` elements as game objects (too slow for many moving items).

**The game loop is just `useFrameCallback`.** Calculate delta time, update physics, let Skia re-draw. The same pattern as Unity's `Update()` or Godot's `_process()`, just in JavaScript.

---

→ [Back to Chapter 39: React Native Algorithm Visualiser](./39-REACT-NATIVE-ALGO-VIZ.md)
