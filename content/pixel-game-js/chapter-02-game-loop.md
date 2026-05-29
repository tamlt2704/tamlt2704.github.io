# The Game Loop

[prev: Canvas Basics](./chapter-01-canvas-basics.md) | [next: Sprites](./chapter-03-sprites.md)

Every game runs a loop: read input, update state, render. The challenge is making this loop consistent across different hardware speeds.

```
+--------+     +---------+     +--------+
| INPUT  | --> | UPDATE  | --> | RENDER | --+
+--------+     +---------+     +--------+   |
    ^                                       |
    +---------------------------------------+
```

## Delta Time

Without delta time, your game runs at different speeds on different machines:

```typescript
let lastTime = 0;

function gameLoop(timestamp: number) {
  const dt = (timestamp - lastTime) / 1000; // seconds
  lastTime = timestamp;

  player.x += player.speed * dt; // 60px/sec regardless of frame rate

  render();
  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

## Fixed Timestep

Physics simulations need deterministic updates. A fixed timestep runs update() at a constant rate:

```typescript
const TICK_RATE = 1 / 60;
let accumulator = 0;
let lastTime = 0;

function gameLoop(timestamp: number) {
  const frameTime = Math.min((timestamp - lastTime) / 1000, 0.25);
  lastTime = timestamp;
  accumulator += frameTime;

  while (accumulator >= TICK_RATE) {
    update(TICK_RATE);
    accumulator -= TICK_RATE;
  }

  const alpha = accumulator / TICK_RATE;
  render(alpha);
  requestAnimationFrame(gameLoop);
}
```

## FPS Counter

```typescript
let frameCount = 0;
let fpsTime = 0;
let fps = 0;

function gameLoop(timestamp: number) {
  const dt = (timestamp - lastTime) / 1000;
  lastTime = timestamp;

  frameCount++;
  fpsTime += dt;
  if (fpsTime >= 1) {
    fps = frameCount;
    frameCount = 0;
    fpsTime -= 1;
  }

  update(dt);
  render();
  ctx.fillStyle = "#0f0";
  ctx.font = "8px monospace";
  ctx.fillText(`FPS: ${fps}`, 2, 8);
  requestAnimationFrame(gameLoop);
}
```

## Input Handling

### Keyboard

```typescript
const keys: Record<string, boolean> = {};

window.addEventListener("keydown", (e) => {
  keys[e.code] = true;
  e.preventDefault();
});
window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

function update(dt: number) {
  if (keys["ArrowLeft"]) player.x -= player.speed * dt;
  if (keys["ArrowRight"]) player.x += player.speed * dt;
  if (keys["Space"]) player.jump();
}
```

### Just-Pressed Detection

```typescript
const keys: Record<string, boolean> = {};
const justPressed: Record<string, boolean> = {};

window.addEventListener("keydown", (e) => {
  if (!keys[e.code]) justPressed[e.code] = true;
  keys[e.code] = true;
});
window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

function update(dt: number) {
  if (justPressed["Space"]) player.jump();
  // Clear at end of frame
  for (const k in justPressed) delete justPressed[k];
}
```

### Mouse Input

```typescript
const mouse = { x: 0, y: 0, down: false, clicked: false };

canvas.addEventListener("mousemove", (e) => {
  const rect = canvas.getBoundingClientRect();
  mouse.x = Math.floor((e.clientX - rect.left) * (canvas.width / rect.width));
  mouse.y = Math.floor((e.clientY - rect.top) * (canvas.height / rect.height));
});
canvas.addEventListener("mousedown", () => {
  mouse.down = true;
  mouse.clicked = true;
});
canvas.addEventListener("mouseup", () => {
  mouse.down = false;
});
```

### Touch Input

```typescript
canvas.addEventListener("touchstart", (e) => {
  e.preventDefault();
  const touch = e.touches[0];
  const rect = canvas.getBoundingClientRect();
  mouse.x = Math.floor((touch.clientX - rect.left) * (canvas.width / rect.width));
  mouse.y = Math.floor((touch.clientY - rect.top) * (canvas.height / rect.height));
  mouse.down = true;
  mouse.clicked = true;
});
canvas.addEventListener("touchend", (e) => {
  e.preventDefault();
  mouse.down = false;
});
```

## Game States

```typescript
type GameState = "menu" | "playing" | "paused" | "gameover";
let state: GameState = "menu";

function update(dt: number) {
  switch (state) {
    case "menu":
      if (justPressed["Enter"]) state = "playing";
      break;
    case "playing":
      if (justPressed["Escape"]) state = "paused";
      updateGame(dt);
      break;
    case "paused":
      if (justPressed["Escape"]) state = "playing";
      break;
    case "gameover":
      if (justPressed["Enter"]) {
        resetGame();
        state = "playing";
      }
      break;
  }
}

function render() {
  ctx.fillStyle = "#1a1a2e";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  switch (state) {
    case "menu":
      ctx.fillStyle = "#fff";
      ctx.fillText("PRESS ENTER", 40, 70);
      break;
    case "playing":
      renderGame();
      break;
    case "paused":
      renderGame();
      ctx.fillStyle = "rgba(0,0,0,0.5)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#fff";
      ctx.fillText("PAUSED", 50, 70);
      break;
    case "gameover":
      ctx.fillStyle = "#e94560";
      ctx.fillText("GAME OVER", 42, 70);
      break;
  }
}
```

## State Machine (Advanced)

```typescript
interface State {
  enter?(): void;
  exit?(): void;
  update(dt: number): void;
  render(): void;
}

class StateMachine {
  private current: State | null = null;
  private states = new Map<string, State>();

  add(name: string, state: State) {
    this.states.set(name, state);
  }

  switch(name: string) {
    this.current?.exit?.();
    this.current = this.states.get(name)!;
    this.current.enter?.();
  }

  update(dt: number) {
    this.current?.update(dt);
  }
  render() {
    this.current?.render();
  }
}
```

## Complete Template

```typescript
const canvas = document.getElementById("game") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;
canvas.width = 160;
canvas.height = 144;
ctx.imageSmoothingEnabled = false;

const keys: Record<string, boolean> = {};
const justPressed: Record<string, boolean> = {};
window.addEventListener("keydown", (e) => {
  if (!keys[e.code]) justPressed[e.code] = true;
  keys[e.code] = true;
});
window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

let lastTime = 0,
  fps = 0,
  frameCount = 0,
  fpsTimer = 0;

function update(dt: number) {
  /* game logic */
}

function render() {
  ctx.fillStyle = "#1a1a2e";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#0f0";
  ctx.font = "8px monospace";
  ctx.fillText(`${fps}`, 1, 7);
}

function gameLoop(timestamp: number) {
  const dt = Math.min((timestamp - lastTime) / 1000, 0.1);
  lastTime = timestamp;
  frameCount++;
  fpsTimer += dt;
  if (fpsTimer >= 1) {
    fps = frameCount;
    frameCount = 0;
    fpsTimer -= 1;
  }
  update(dt);
  render();
  for (const k in justPressed) delete justPressed[k];
  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

[prev: Canvas Basics](./chapter-01-canvas-basics.md) | [next: Sprites](./chapter-03-sprites.md)
