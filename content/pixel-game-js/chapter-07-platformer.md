# Complete Platformer Project

[prev: Kaboom.js](./chapter-06-kaboom.md) | [next: RPG Project](./chapter-08-rpg.md)

Build a full platformer from scratch with raw Canvas: player movement, gravity, enemies, collectibles, and multiple levels.

## Project Structure

```
platformer/
  index.html
  src/
    main.ts
    player.ts
    enemy.ts
    level.ts
    camera.ts
  assets/
    player.png
    tileset.png
    coin.png
```

## Player Movement

```typescript
class Player {
  x = 32;
  y = 32;
  vx = 0;
  vy = 0;
  width = 12;
  height = 14;
  onGround = false;
  facing = 1; // 1=right, -1=left
  jumpBuffer = 0; // coyote time for jump
  coyoteTime = 0; // time since leaving ground

  readonly SPEED = 80;
  readonly JUMP = -180;
  readonly GRAVITY = 500;
  readonly MAX_FALL = 250;

  update(dt: number, keys: Record<string, boolean>, level: Level) {
    // Horizontal
    if (keys["ArrowLeft"]) {
      this.vx = -this.SPEED;
      this.facing = -1;
    } else if (keys["ArrowRight"]) {
      this.vx = this.SPEED;
      this.facing = 1;
    } else {
      this.vx = 0;
    }

    // Coyote time (can still jump briefly after leaving edge)
    if (this.onGround) this.coyoteTime = 0.08;
    else this.coyoteTime -= dt;

    // Jump buffer (press jump slightly before landing)
    if (keys["Space"]) this.jumpBuffer = 0.1;
    else this.jumpBuffer -= dt;

    // Jump
    if (this.jumpBuffer > 0 && this.coyoteTime > 0) {
      this.vy = this.JUMP;
      this.jumpBuffer = 0;
      this.coyoteTime = 0;
    }

    // Variable jump height (release early = lower jump)
    if (!keys["Space"] && this.vy < 0) {
      this.vy *= 0.5;
    }

    // Gravity
    this.vy += this.GRAVITY * dt;
    if (this.vy > this.MAX_FALL) this.vy = this.MAX_FALL;

    // Move and collide
    this.moveX(dt, level);
    this.moveY(dt, level);
  }

  moveX(dt: number, level: Level) {
    this.x += this.vx * dt;
    if (this.vx > 0) {
      if (
        level.isSolid(this.x + this.width, this.y) ||
        level.isSolid(this.x + this.width, this.y + this.height - 1)
      ) {
        this.x = Math.floor((this.x + this.width) / 16) * 16 - this.width;
        this.vx = 0;
      }
    } else if (this.vx < 0) {
      if (level.isSolid(this.x, this.y) || level.isSolid(this.x, this.y + this.height - 1)) {
        this.x = Math.floor(this.x / 16) * 16 + 16;
        this.vx = 0;
      }
    }
  }

  moveY(dt: number, level: Level) {
    this.onGround = false;
    this.y += this.vy * dt;
    if (this.vy > 0) {
      if (
        level.isSolid(this.x, this.y + this.height) ||
        level.isSolid(this.x + this.width - 1, this.y + this.height)
      ) {
        this.y = Math.floor((this.y + this.height) / 16) * 16 - this.height;
        this.vy = 0;
        this.onGround = true;
      }
    } else if (this.vy < 0) {
      if (level.isSolid(this.x, this.y) || level.isSolid(this.x + this.width - 1, this.y)) {
        this.y = Math.floor(this.y / 16) * 16 + 16;
        this.vy = 0;
      }
    }
  }
}
```

## Wall Jump

```typescript
// Add to Player class
wallSliding = false;
wallDir = 0;

updateWallSlide(level: Level) {
  const touchingLeft = level.isSolid(this.x - 1, this.y) || level.isSolid(this.x - 1, this.y + this.height - 1);
  const touchingRight = level.isSolid(this.x + this.width, this.y) || level.isSolid(this.x + this.width, this.y + this.height - 1);

  if (!this.onGround && (touchingLeft || touchingRight) && this.vy > 0) {
    this.wallSliding = true;
    this.wallDir = touchingLeft ? -1 : 1;
    this.vy = Math.min(this.vy, 40); // slow fall
  } else {
    this.wallSliding = false;
  }
}

wallJump(keys: Record<string, boolean>) {
  if (this.wallSliding && this.jumpBuffer > 0) {
    this.vx = -this.wallDir * 120; // push away from wall
    this.vy = this.JUMP * 0.8;
    this.jumpBuffer = 0;
    this.wallSliding = false;
  }
}
```

## Enemies (Patrol AI)

```typescript
class Enemy {
  x: number;
  y: number;
  vx: number;
  width = 14;
  height = 14;
  startX: number;
  patrolDist = 48;
  alive = true;

  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
    this.startX = x;
    this.vx = 30;
  }

  update(dt: number, level: Level) {
    if (!this.alive) return;
    this.x += this.vx * dt;

    // Reverse at patrol bounds
    if (Math.abs(this.x - this.startX) > this.patrolDist) {
      this.vx *= -1;
    }

    // Reverse at walls
    const frontX = this.vx > 0 ? this.x + this.width : this.x;
    if (level.isSolid(frontX, this.y + this.height / 2)) {
      this.vx *= -1;
    }

    // Reverse at edges (don't walk off platforms)
    const edgeX = this.vx > 0 ? this.x + this.width : this.x;
    if (!level.isSolid(edgeX, this.y + this.height + 1)) {
      this.vx *= -1;
    }
  }

  getBounds() {
    return { x: this.x, y: this.y, w: this.width, h: this.height };
  }
}
```

## Collectibles

```typescript
interface Coin {
  x: number;
  y: number;
  collected: boolean;
  frame: number;
  timer: number;
}

function updateCoins(coins: Coin[], player: Player, dt: number) {
  for (const coin of coins) {
    if (coin.collected) continue;
    // Animate
    coin.timer += dt;
    if (coin.timer > 0.15) {
      coin.timer = 0;
      coin.frame = (coin.frame + 1) % 4;
    }
    // Collect
    if (
      aabb(
        { x: player.x, y: player.y, w: player.width, h: player.height },
        { x: coin.x, y: coin.y, w: 8, h: 8 },
      )
    ) {
      coin.collected = true;
      score++;
    }
  }
}
```

## Level Design

```typescript
class Level {
  tiles: number[];
  width: number;
  height: number;
  coins: Coin[] = [];
  enemies: Enemy[] = [];
  spawn = { x: 32, y: 32 };

  constructor(data: { tiles: number[]; width: number; height: number; objects: any[] }) {
    this.tiles = data.tiles;
    this.width = data.width;
    this.height = data.height;
    for (const obj of data.objects) {
      if (obj.type === "coin")
        this.coins.push({ x: obj.x, y: obj.y, collected: false, frame: 0, timer: 0 });
      if (obj.type === "enemy") this.enemies.push(new Enemy(obj.x, obj.y));
      if (obj.type === "spawn") this.spawn = { x: obj.x, y: obj.y };
    }
  }

  isSolid(x: number, y: number): boolean {
    const col = Math.floor(x / 16);
    const row = Math.floor(y / 16);
    if (col < 0 || col >= this.width || row < 0 || row >= this.height) return true;
    return this.tiles[row * this.width + col] !== 0;
  }
}

const levels = [
  {
    tiles: [
      /* ... */
    ],
    width: 20,
    height: 15,
    objects: [{ type: "spawn", x: 32, y: 192 } /* ... */],
  },
  {
    tiles: [
      /* ... */
    ],
    width: 30,
    height: 15,
    objects: [
      /* ... */
    ],
  },
];
```

## Death and Respawn

```typescript
let lives = 3;
let currentLevel = 0;

function checkDeath(player: Player, level: Level) {
  // Fall off screen
  if (player.y > level.height * 16 + 32) {
    die();
    return;
  }
  // Enemy collision (stomp = kill enemy, side = die)
  for (const enemy of level.enemies) {
    if (!enemy.alive) continue;
    if (aabb(player.getBounds(), enemy.getBounds())) {
      if (player.vy > 0 && player.y + player.height < enemy.y + 8) {
        enemy.alive = false;
        player.vy = -120; // bounce
        score += 50;
      } else {
        die();
      }
    }
  }
}

function die() {
  lives--;
  if (lives <= 0) {
    state = "gameover";
  } else {
    respawn();
  }
}

function respawn() {
  player.x = level.spawn.x;
  player.y = level.spawn.y;
  player.vx = 0;
  player.vy = 0;
}
```

## Multiple Levels

```typescript
function checkLevelEnd(player: Player, level: Level) {
  // Reach the right edge or a door tile
  if (player.x > (level.width - 2) * 16) {
    nextLevel();
  }
}

function nextLevel() {
  currentLevel++;
  if (currentLevel >= levels.length) {
    state = "win";
    return;
  }
  level = new Level(levels[currentLevel]);
  player.x = level.spawn.x;
  player.y = level.spawn.y;
}
```

## Sound Effects

```typescript
// Using the Web Audio API for simple sfx
const audioCtx = new AudioContext();

function playSfx(freq: number, duration: number, type: OscillatorType = "square") {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
  gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
  osc.connect(gain).connect(audioCtx.destination);
  osc.start();
  osc.stop(audioCtx.currentTime + duration);
}

function jumpSfx() {
  playSfx(400, 0.1);
}
function coinSfx() {
  playSfx(800, 0.15);
}
function dieSfx() {
  playSfx(200, 0.3, "sawtooth");
}
```

## Putting It All Together

```typescript
const canvas = document.getElementById("game") as HTMLCanvasElement;
const ctx = canvas.getContext("2d")!;
canvas.width = 160;
canvas.height = 144;
ctx.imageSmoothingEnabled = false;

const keys: Record<string, boolean> = {};
window.addEventListener("keydown", (e) => {
  keys[e.code] = true;
});
window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

let level = new Level(levels[0]);
const player = new Player();
player.x = level.spawn.x;
player.y = level.spawn.y;
const camera = { x: 0, y: 0 };
let score = 0,
  state = "playing",
  lastTime = 0;

function update(dt: number) {
  if (state !== "playing") return;
  player.update(dt, keys, level);
  level.enemies.forEach((e) => e.update(dt, level));
  updateCoins(level.coins, player, dt);
  checkDeath(player, level);
  checkLevelEnd(player, level);
  // Camera
  camera.x = Math.floor(player.x - 80);
  camera.y = Math.floor(player.y - 72);
  camera.x = Math.max(0, Math.min(camera.x, level.width * 16 - 160));
  camera.y = Math.max(0, Math.min(camera.y, level.height * 16 - 144));
}

function render() {
  ctx.fillStyle = "#1a1a2e";
  ctx.fillRect(0, 0, 160, 144);
  // Draw tiles, enemies, coins, player offset by camera
  // ... (use drawImage with camera.x/y offset)
  ctx.fillStyle = "#fff";
  ctx.font = "8px monospace";
  ctx.fillText(`${score}`, 2, 8);
}

function loop(t: number) {
  const dt = Math.min((t - lastTime) / 1000, 0.1);
  lastTime = t;
  update(dt);
  render();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
```

[prev: Kaboom.js](./chapter-06-kaboom.md) | [next: RPG Project](./chapter-08-rpg.md)
