# Complete RPG Project

[prev: Platformer Project](./chapter-07-platformer.md) | [next: Polish](./chapter-09-polish.md)

Build a top-down RPG with NPC dialogue, inventory, map transitions, turn-based combat, and save/load.

## Top-Down Movement

```typescript
class Player {
  x = 48;
  y = 48;
  width = 12;
  height = 14;
  speed = 60;
  dir = "down"; // for facing direction
  moving = false;

  update(dt: number, keys: Record<string, boolean>, level: Level) {
    let dx = 0,
      dy = 0;
    this.moving = false;

    if (keys["ArrowLeft"]) {
      dx = -1;
      this.dir = "left";
    }
    if (keys["ArrowRight"]) {
      dx = 1;
      this.dir = "right";
    }
    if (keys["ArrowUp"]) {
      dy = -1;
      this.dir = "up";
    }
    if (keys["ArrowDown"]) {
      dy = 1;
      this.dir = "down";
    }

    if (dx !== 0 || dy !== 0) {
      this.moving = true;
      // Normalize diagonal
      if (dx !== 0 && dy !== 0) {
        dx *= 0.707;
        dy *= 0.707;
      }
      const nx = this.x + dx * this.speed * dt;
      const ny = this.y + dy * this.speed * dt;

      // Separate axis collision
      if (!level.isSolid(nx, this.y, this.width, this.height)) this.x = nx;
      if (!level.isSolid(this.x, ny, this.width, this.height)) this.y = ny;
    }
  }
}
```

## NPC Dialogue System

```typescript
interface DialogLine {
  speaker: string;
  text: string;
}

interface NPC {
  x: number;
  y: number;
  width: number;
  height: number;
  name: string;
  dialog: DialogLine[];
}

class DialogSystem {
  active = false;
  lines: DialogLine[] = [];
  lineIndex = 0;
  charIndex = 0;
  timer = 0;
  speed = 30; // chars per second

  start(dialog: DialogLine[]) {
    this.active = true;
    this.lines = dialog;
    this.lineIndex = 0;
    this.charIndex = 0;
    this.timer = 0;
  }

  advance() {
    if (this.charIndex < this.lines[this.lineIndex].text.length) {
      // Skip to end of line
      this.charIndex = this.lines[this.lineIndex].text.length;
    } else {
      // Next line
      this.lineIndex++;
      this.charIndex = 0;
      this.timer = 0;
      if (this.lineIndex >= this.lines.length) {
        this.active = false;
      }
    }
  }

  update(dt: number) {
    if (!this.active) return;
    this.timer += dt;
    const line = this.lines[this.lineIndex];
    this.charIndex = Math.min(Math.floor(this.timer * this.speed), line.text.length);
  }

  render(ctx: CanvasRenderingContext2D) {
    if (!this.active) return;
    const line = this.lines[this.lineIndex];
    // Dialog box
    ctx.fillStyle = "#111";
    ctx.fillRect(4, 110, 152, 30);
    ctx.strokeStyle = "#fff";
    ctx.strokeRect(4, 110, 152, 30);
    // Speaker name
    ctx.fillStyle = "#ffcc00";
    ctx.font = "7px monospace";
    ctx.fillText(line.speaker, 8, 119);
    // Text (typewriter)
    ctx.fillStyle = "#fff";
    ctx.fillText(line.text.substring(0, this.charIndex), 8, 130);
  }
}

// Usage
const npcs: NPC[] = [
  {
    x: 80,
    y: 48,
    width: 14,
    height: 14,
    name: "Elder",
    dialog: [
      { speaker: "Elder", text: "Welcome, traveler." },
      { speaker: "Elder", text: "The forest is dangerous." },
      { speaker: "Elder", text: "Take this sword." },
    ],
  },
];

// Interact with Z key
if (justPressed["KeyZ"] && !dialog.active) {
  for (const npc of npcs) {
    const dist = Math.hypot(player.x - npc.x, player.y - npc.y);
    if (dist < 20) {
      dialog.start(npc.dialog);
      break;
    }
  }
} else if (justPressed["KeyZ"] && dialog.active) {
  dialog.advance();
}
```

## Inventory

```typescript
interface Item {
  id: string;
  name: string;
  type: "weapon" | "potion" | "key";
  value: number;
}

class Inventory {
  items: Item[] = [];
  maxSize = 10;

  add(item: Item): boolean {
    if (this.items.length >= this.maxSize) return false;
    this.items.push(item);
    return true;
  }

  remove(id: string): Item | undefined {
    const idx = this.items.findIndex((i) => i.id === id);
    if (idx === -1) return undefined;
    return this.items.splice(idx, 1)[0];
  }

  has(id: string): boolean {
    return this.items.some((i) => i.id === id);
  }

  render(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = "#111";
    ctx.fillRect(20, 20, 120, 104);
    ctx.strokeStyle = "#fff";
    ctx.strokeRect(20, 20, 120, 104);
    ctx.fillStyle = "#fff";
    ctx.font = "7px monospace";
    ctx.fillText("INVENTORY", 50, 30);
    this.items.forEach((item, i) => {
      ctx.fillText(`${item.name}`, 28, 42 + i * 9);
    });
  }
}
```

## Map Zones and Transitions

```typescript
interface Zone {
  x: number;
  y: number;
  width: number;
  height: number;
  targetMap: string;
  targetX: number;
  targetY: number;
}

interface GameMap {
  tiles: number[];
  width: number;
  height: number;
  npcs: NPC[];
  zones: Zone[];
}

const maps: Record<string, GameMap> = {
  village: {
    tiles: [
      /* ... */
    ],
    width: 20,
    height: 15,
    npcs: [
      /* ... */
    ],
    zones: [
      { x: 304, y: 112, width: 16, height: 16, targetMap: "forest", targetX: 16, targetY: 112 },
    ],
  },
  forest: {
    tiles: [
      /* ... */
    ],
    width: 30,
    height: 20,
    npcs: [],
    zones: [
      { x: 0, y: 112, width: 16, height: 16, targetMap: "village", targetX: 288, targetY: 112 },
    ],
  },
};

let currentMap = "village";

function checkZones(player: Player) {
  const map = maps[currentMap];
  for (const zone of map.zones) {
    if (
      player.x + player.width > zone.x &&
      player.x < zone.x + zone.width &&
      player.y + player.height > zone.y &&
      player.y < zone.y + zone.height
    ) {
      currentMap = zone.targetMap;
      player.x = zone.targetX;
      player.y = zone.targetY;
      break;
    }
  }
}
```

## Turn-Based Combat

```typescript
interface Combatant {
  name: string;
  hp: number;
  maxHp: number;
  atk: number;
  def: number;
}

type CombatState = "player_turn" | "enemy_turn" | "won" | "lost";

class Combat {
  player: Combatant;
  enemy: Combatant;
  state: CombatState = "player_turn";
  log: string[] = [];
  animTimer = 0;

  constructor(player: Combatant, enemy: Combatant) {
    this.player = player;
    this.enemy = enemy;
    this.log.push(`${enemy.name} appeared!`);
  }

  attack() {
    if (this.state !== "player_turn") return;
    const dmg = Math.max(1, this.player.atk - this.enemy.def + Math.floor(Math.random() * 3));
    this.enemy.hp -= dmg;
    this.log.push(`You deal ${dmg} damage!`);
    if (this.enemy.hp <= 0) {
      this.state = "won";
      this.log.push("Enemy defeated!");
      return;
    }
    this.state = "enemy_turn";
    this.animTimer = 0.5; // delay before enemy attacks
  }

  update(dt: number) {
    if (this.state === "enemy_turn") {
      this.animTimer -= dt;
      if (this.animTimer <= 0) {
        const dmg = Math.max(1, this.enemy.atk - this.player.def + Math.floor(Math.random() * 2));
        this.player.hp -= dmg;
        this.log.push(`${this.enemy.name} deals ${dmg}!`);
        if (this.player.hp <= 0) {
          this.state = "lost";
          return;
        }
        this.state = "player_turn";
      }
    }
  }

  render(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = "#111";
    ctx.fillRect(0, 0, 160, 144);
    ctx.fillStyle = "#fff";
    ctx.font = "7px monospace";
    // Enemy
    ctx.fillText(`${this.enemy.name}  HP:${this.enemy.hp}/${this.enemy.maxHp}`, 8, 20);
    // Player
    ctx.fillText(`You  HP:${this.player.hp}/${this.player.maxHp}`, 8, 100);
    // Log
    const recent = this.log.slice(-3);
    recent.forEach((line, i) => ctx.fillText(line, 8, 50 + i * 10));
    // Menu
    if (this.state === "player_turn") {
      ctx.fillStyle = "#ffcc00";
      ctx.fillText("> ATTACK", 8, 130);
    }
  }
}
```

## Save/Load with localStorage

```typescript
interface SaveData {
  currentMap: string;
  playerX: number;
  playerY: number;
  inventory: Item[];
  hp: number;
  flags: Record<string, boolean>; // quest progress
}

function saveGame() {
  const data: SaveData = {
    currentMap,
    playerX: player.x,
    playerY: player.y,
    inventory: inventory.items,
    hp: playerStats.hp,
    flags: gameFlags,
  };
  localStorage.setItem("rpg_save", JSON.stringify(data));
}

function loadGame(): boolean {
  const raw = localStorage.getItem("rpg_save");
  if (!raw) return false;
  const data: SaveData = JSON.parse(raw);
  currentMap = data.currentMap;
  player.x = data.playerX;
  player.y = data.playerY;
  inventory.items = data.inventory;
  playerStats.hp = data.hp;
  gameFlags = data.flags;
  return true;
}

// Save at save points or on menu
if (justPressed["KeyS"]) saveGame();
```

## Game Flags for Quest Progress

```typescript
const gameFlags: Record<string, boolean> = {};

// After getting sword from Elder
if (dialog.lineIndex >= dialog.lines.length - 1 && !gameFlags["got_sword"]) {
  gameFlags["got_sword"] = true;
  inventory.add({ id: "sword", name: "Iron Sword", type: "weapon", value: 5 });
}

// NPC changes dialog based on flags
function getNpcDialog(npc: NPC): DialogLine[] {
  if (npc.name === "Elder" && gameFlags["got_sword"]) {
    return [{ speaker: "Elder", text: "Good luck out there." }];
  }
  return npc.dialog;
}
```

## Main Game Loop

```typescript
type GameMode = "explore" | "dialog" | "combat" | "inventory" | "menu";
let mode: GameMode = "explore";
let combat: Combat | null = null;

function update(dt: number) {
  switch (mode) {
    case "explore":
      if (!dialog.active) player.update(dt, keys, currentLevel);
      checkZones(player);
      if (justPressed["KeyZ"]) tryInteract();
      if (justPressed["KeyI"]) mode = "inventory";
      break;
    case "dialog":
      dialog.update(dt);
      if (justPressed["KeyZ"]) dialog.advance();
      if (!dialog.active) mode = "explore";
      break;
    case "combat":
      combat!.update(dt);
      if (justPressed["KeyZ"]) combat!.attack();
      if (combat!.state === "won") mode = "explore";
      if (combat!.state === "lost") mode = "menu";
      break;
    case "inventory":
      if (justPressed["KeyI"] || justPressed["Escape"]) mode = "explore";
      break;
  }
}
```

[prev: Platformer Project](./chapter-07-platformer.md) | [next: Polish](./chapter-09-polish.md)
