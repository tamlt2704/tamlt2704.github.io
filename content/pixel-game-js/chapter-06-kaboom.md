# Kaboom.js

[prev: Phaser 3](./chapter-05-phaser.md) | [next: Platformer Project](./chapter-07-platformer.md)

Kaboom.js is the simplest game framework for JavaScript. Its API is fun, expressive, and you can build a game in under 50 lines. Perfect for beginners and game jams.

## Setup

```html
<script src="https://unpkg.com/kaboom@3000/dist/kaboom.js"></script>
<script>
  kaboom({
    width: 160,
    height: 144,
    scale: 4,
    crisp: true,
    background: [26, 26, 46],
  });
</script>
```

Or with npm:

```bash
npm install kaboom
```

```typescript
import kaboom from "kaboom";

kaboom({ width: 160, height: 144, scale: 4, crisp: true });
```

## Core Concept: Components

Everything in Kaboom is built from components. `add()` creates a game object by composing components:

```typescript
// A player is: position + sprite + physics body + collision area
const player = add([
  pos(32, 100),
  sprite("player"),
  area(),
  body(),
  health(3),
  "player", // tag for queries
]);
```

## Loading Assets

```typescript
loadSprite("player", "player.png", {
  sliceX: 4, // 4 frames horizontally
  anims: {
    idle: { from: 0, to: 0 },
    run: { from: 0, to: 3, loop: true, speed: 10 },
  },
});

loadSprite("tileset", "tileset.png", {
  sliceX: 4,
  sliceY: 4,
});

loadSound("jump", "jump.wav");
loadSound("coin", "coin.wav");
```

## Movement and Input

```typescript
const SPEED = 80;

onKeyDown("left", () => {
  player.move(-SPEED, 0);
  player.flipX = true;
  player.play("run");
});

onKeyDown("right", () => {
  player.move(SPEED, 0);
  player.flipX = false;
  player.play("run");
});

onKeyRelease(["left", "right"], () => {
  player.play("idle");
});

onKeyPress("space", () => {
  if (player.isGrounded()) {
    player.jump(200);
    play("jump");
  }
});
```

## Collision Events

```typescript
// Collect coins
player.onCollide("coin", (coin) => {
  destroy(coin);
  score += 10;
  play("coin");
  shake(2); // screen shake!
});

// Enemy kills player
player.onCollide("enemy", () => {
  player.hurt(1);
  if (player.hp() <= 0) {
    go("gameover"); // switch scene
  }
});
```

## Scenes

```typescript
scene("menu", () => {
  add([text("PRESS ENTER", { size: 8 }), pos(40, 70)]);

  onKeyPress("enter", () => go("game"));
});

scene("game", () => {
  // ... game logic
});

scene("gameover", () => {
  add([text("GAME OVER", { size: 8 }), pos(42, 70), color(233, 69, 96)]);
  onKeyPress("enter", () => go("game"));
});

go("menu"); // start with menu
```

## Level Design with ASCII

```typescript
const level = addLevel(
  ["          ", "          ", "   ===    ", "          ", " ^  c  ^  ", "=========="],
  {
    tileWidth: 16,
    tileHeight: 16,
    tiles: {
      "=": () => [sprite("tileset", { frame: 0 }), area(), body({ isStatic: true }), "ground"],
      "^": () => [sprite("enemy"), area(), body({ isStatic: true }), "enemy", patrol()],
      c: () => [sprite("coin"), area(), "coin"],
    },
  },
);
```

## Custom Components

```typescript
function patrol(speed = 30, distance = 50) {
  let dir = 1;
  let traveled = 0;
  return {
    id: "patrol",
    update(this: any) {
      this.move(speed * dir, 0);
      traveled += speed * dt();
      if (traveled >= distance) {
        dir *= -1;
        traveled = 0;
        this.flipX = dir < 0;
      }
    },
  };
}
```

## Build a Top-Down RPG

```typescript
kaboom({ width: 160, height: 144, scale: 4, crisp: true, background: [34, 40, 49] });

loadSprite("hero", "hero.png", {
  sliceX: 4,
  anims: { idle: 0, walk: { from: 0, to: 3, loop: true, speed: 6 } },
});
loadSprite("npc", "npc.png");
loadSprite("tiles", "tiles.png", { sliceX: 4, sliceY: 4 });

scene("world", () => {
  const map = addLevel(
    [
      "################",
      "#..............#",
      "#..............#",
      "#....N.........#",
      "#..............#",
      "#..............#",
      "#..............#",
      "################",
    ],
    {
      tileWidth: 16,
      tileHeight: 16,
      tiles: {
        "#": () => [sprite("tiles", { frame: 0 }), area(), body({ isStatic: true })],
        ".": () => [sprite("tiles", { frame: 1 })],
        N: () => [sprite("npc"), area(), "npc", { msg: "Hello traveler!" }],
      },
    },
  );

  const player = add([pos(48, 80), sprite("hero"), area(), body(), "player"]);
  const SPEED = 60;
  let talking = false;
  let dialogBox: any = null;

  onKeyDown("left", () => {
    if (!talking) {
      player.move(-SPEED, 0);
      player.flipX = true;
    }
  });
  onKeyDown("right", () => {
    if (!talking) {
      player.move(SPEED, 0);
      player.flipX = false;
    }
  });
  onKeyDown("up", () => {
    if (!talking) player.move(0, -SPEED);
  });
  onKeyDown("down", () => {
    if (!talking) player.move(0, SPEED);
  });

  onKeyPress("z", () => {
    if (talking) {
      destroy(dialogBox);
      talking = false;
      return;
    }
    // Check for nearby NPC
    const npcs = get("npc");
    for (const npc of npcs) {
      if (player.pos.dist(npc.pos) < 24) {
        talking = true;
        dialogBox = add([pos(8, 110), rect(144, 28), color(0, 0, 0), outline(1), z(10)]);
        add([pos(12, 114), text(npc.msg, { size: 6 }), z(11), "dialog"]);
        break;
      }
    }
  });

  player.onUpdate(() => {
    camPos(player.pos);
  });
});

go("world");
```

## Useful Built-in Functions

```typescript
shake(5); // screen shake
burp(); // play burp sound (yes, really)
dt(); // delta time this frame
time(); // total elapsed time
rand(0, 100); // random number
choose(["a", "b"]); // random pick from array
wait(2, () => {}); // delayed callback
loop(1, () => {}); // repeating callback
debug.fps(); // current FPS
```

## Why Kaboom for Beginners

- No boilerplate — `kaboom()` and you're running
- Component system is intuitive
- ASCII level maps are readable
- Built-in physics, no config needed
- Fun API (`burp()`, `shake()`)
- Great for game jams (speed over polish)

[prev: Phaser 3](./chapter-05-phaser.md) | [next: Platformer Project](./chapter-07-platformer.md)
