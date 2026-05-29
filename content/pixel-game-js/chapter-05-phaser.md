# Phaser 3

[prev: Tilemaps](./chapter-04-tilemap.md) | [next: Kaboom.js](./chapter-06-kaboom.md)

Phaser 3 is the most popular HTML5 game framework. It handles rendering, physics, input, audio, tilemaps, and more — everything you need for production games.

## Setup

### Via CDN

```html
<script src="https://cdn.jsdelivr.net/npm/phaser@3/dist/phaser.min.js"></script>
```

### Via npm

```bash
npm init -y
npm install phaser
```

```typescript
import Phaser from "phaser";
```

## Game Configuration

```typescript
const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 160,
  height: 144,
  pixelArt: true, // disables anti-aliasing
  zoom: 4,
  physics: {
    default: "arcade",
    arcade: { gravity: { x: 0, y: 300 }, debug: false },
  },
  scene: [GameScene],
};

const game = new Phaser.Game(config);
```

## Scene Lifecycle

```typescript
class GameScene extends Phaser.Scene {
  player!: Phaser.Physics.Arcade.Sprite;
  cursors!: Phaser.Types.Input.Keyboard.CursorKeys;

  constructor() {
    super("game");
  }

  preload() {
    // Load assets
    this.load.spritesheet("player", "player.png", { frameWidth: 16, frameHeight: 16 });
    this.load.image("tiles", "tileset.png");
    this.load.tilemapTiledJSON("map", "level1.json");
  }

  create() {
    // Create game objects
    this.player = this.physics.add.sprite(50, 100, "player");
    this.player.setCollideWorldBounds(true);
    this.cursors = this.input.keyboard!.createCursorKeys();

    // Animations
    this.anims.create({
      key: "run",
      frames: this.anims.generateFrameNumbers("player", { start: 0, end: 3 }),
      frameRate: 10,
      repeat: -1,
    });
  }

  update() {
    // Game logic every frame
    if (this.cursors.left.isDown) {
      this.player.setVelocityX(-80);
      this.player.setFlipX(true);
      this.player.anims.play("run", true);
    } else if (this.cursors.right.isDown) {
      this.player.setVelocityX(80);
      this.player.setFlipX(false);
      this.player.anims.play("run", true);
    } else {
      this.player.setVelocityX(0);
      this.player.anims.stop();
    }

    if (this.cursors.up.isDown && this.player.body!.blocked.down) {
      this.player.setVelocityY(-150);
    }
  }
}
```

## Tilemaps

```typescript
create() {
  const map = this.make.tilemap({ key: 'map' });
  const tileset = map.addTilesetImage('tileset-name', 'tiles')!;

  const bgLayer = map.createLayer('background', tileset)!;
  const groundLayer = map.createLayer('ground', tileset)!;

  groundLayer.setCollisionByProperty({ collides: true });

  this.player = this.physics.add.sprite(50, 100, 'player');
  this.physics.add.collider(this.player, groundLayer);
}
```

## Camera Follow

```typescript
create() {
  // ... after creating player and map
  this.cameras.main.startFollow(this.player, true, 0.1, 0.1);
  this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
  this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
}
```

## Groups

```typescript
create() {
  const coins = this.physics.add.group({
    key: 'coin',
    repeat: 5,
    setXY: { x: 20, y: 0, stepX: 30 }
  });

  coins.children.iterate((coin: any) => {
    coin.setBounceY(Phaser.Math.FloatBetween(0.2, 0.4));
    return true;
  });

  this.physics.add.collider(coins, groundLayer);
  this.physics.add.overlap(this.player, coins, this.collectCoin, undefined, this);
}

collectCoin(player: any, coin: any) {
  coin.disableBody(true, true);
  this.score += 10;
}
```

## Particles

```typescript
create() {
  const particles = this.add.particles(0, 0, 'particle', {
    speed: 100,
    scale: { start: 1, end: 0 },
    lifespan: 400,
    frequency: -1, // manual emit
  });

  // Emit on coin collect
  particles.emitParticleAt(coin.x, coin.y, 10);
}
```

## Complete Platformer

```typescript
import Phaser from "phaser";

class PlatformerScene extends Phaser.Scene {
  player!: Phaser.Physics.Arcade.Sprite;
  cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  score = 0;
  scoreText!: Phaser.GameObjects.Text;

  constructor() {
    super("platformer");
  }

  preload() {
    this.load.spritesheet("player", "player.png", { frameWidth: 16, frameHeight: 16 });
    this.load.image("tiles", "tileset.png");
    this.load.tilemapTiledJSON("map", "level.json");
    this.load.spritesheet("coin", "coin.png", { frameWidth: 8, frameHeight: 8 });
  }

  create() {
    const map = this.make.tilemap({ key: "map" });
    const tileset = map.addTilesetImage("tileset", "tiles")!;
    const ground = map.createLayer("ground", tileset)!;
    ground.setCollisionByExclusion([-1]);

    this.player = this.physics.add.sprite(32, 100, "player");
    this.player.setSize(12, 14);
    this.physics.add.collider(this.player, ground);

    this.anims.create({ key: "idle", frames: [{ key: "player", frame: 0 }] });
    this.anims.create({
      key: "run",
      frames: this.anims.generateFrameNumbers("player", { start: 1, end: 4 }),
      frameRate: 10,
      repeat: -1,
    });

    const coins = map.createFromObjects("objects", { name: "coin", key: "coin" });
    const coinGroup = this.physics.add.staticGroup(coins);
    this.physics.add.overlap(this.player, coinGroup, (_, coin: any) => {
      coin.destroy();
      this.score += 10;
      this.scoreText.setText(`${this.score}`);
    });

    this.cameras.main.startFollow(this.player);
    this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
    this.cursors = this.input.keyboard!.createCursorKeys();
    this.scoreText = this.add.text(4, 4, "0", { fontSize: "8px" }).setScrollFactor(0);
  }

  update() {
    const onGround = this.player.body!.blocked.down;
    if (this.cursors.left.isDown) {
      this.player.setVelocityX(-80);
      this.player.setFlipX(true);
      if (onGround) this.player.anims.play("run", true);
    } else if (this.cursors.right.isDown) {
      this.player.setVelocityX(80);
      this.player.setFlipX(false);
      if (onGround) this.player.anims.play("run", true);
    } else {
      this.player.setVelocityX(0);
      if (onGround) this.player.anims.play("idle", true);
    }
    if (this.cursors.up.isDown && onGround) {
      this.player.setVelocityY(-160);
    }
  }
}

new Phaser.Game({
  type: Phaser.AUTO,
  width: 160,
  height: 144,
  pixelArt: true,
  zoom: 4,
  physics: { default: "arcade", arcade: { gravity: { x: 0, y: 300 } } },
  scene: [PlatformerScene],
});
```

[prev: Tilemaps](./chapter-04-tilemap.md) | [next: Kaboom.js](./chapter-06-kaboom.md)
