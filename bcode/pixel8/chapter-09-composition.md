# Chapter 9: Composition — "The Whole Is Greater"

[← Chapter 8: Palettes](chapter-08-palettes.md) | [Chapter 10: Mini-Game →](chapter-10-mini-game.md)

---

## Mika's Challenge

Mika looks at your collection of sprites, animations, and effects:

> "You've got pieces. A knight. A coin. A fire effect. Text. But a game isn't a pile of parts — it's a *scene*. Everything positioned relative to everything else. Layers that make sense. A world that feels composed, not scattered."

She opens a screenshot of Celeste's pixel art:

> "Look at how much is happening: background mountains, mid-ground platforms, foreground character, particles, UI. All at 320×180. It works because of *composition* — deliberate layering and spatial relationships. Let's build a real scene."

## Layering: Back to Front

Pixel8 renders in JSX order — earlier elements are behind, later elements are in front. Think of it as painting layers:

```
Layer 0: Background (sky, gradient buffer)
Layer 1: Far background (mountains, clouds)
Layer 2: Mid-ground (platforms, walls, terrain)
Layer 3: Objects (coins, items, enemies)
Layer 4: Player
Layer 5: Foreground effects (particles, weather)
Layer 6: UI (HUD, text, menus)
```

```jsx
const GameScene = () => (
  <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
    {/* Layer 0: Sky gradient */}
    <buffer x={0} y={0} data={skyBuffer} width={64} height={32} palette={skyPalette} />

    {/* Layer 1: Background decoration */}
    <Mountains />

    {/* Layer 2: Terrain */}
    <Ground />

    {/* Layer 3: Collectibles */}
    {coins.map(c => <Coin key={c.id} x={c.x} y={c.y} />)}

    {/* Layer 4: Player */}
    <Player x={playerX} y={playerY} />

    {/* Layer 5: Particles */}
    {particles.map(p => <pixel key={p.id} x={p.x} y={p.y} color={p.color} />)}

    {/* Layer 6: UI */}
    <HUD score={score} lives={lives} />
  </Stage>
);
```

## Component Composition

Break your scene into reusable React components:

```jsx
// components/Player.jsx
const playerData = [
  0,0,1,1,1,0,0,0,
  0,1,2,2,2,1,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,1,1,0,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,0,1,0,0,0,
  0,0,1,0,1,0,0,0,
  0,0,0,0,0,0,0,0,
];

const Player = ({ x, y, palette }) => (
  <sprite x={x} y={y} data={playerData} palette={palette} />
);

// components/Coin.jsx
const coinData = [
  0,0,1,1,1,1,0,0,
  0,1,2,2,2,2,1,0,
  1,2,2,1,1,2,2,1,
  1,2,2,1,1,2,2,1,
  1,2,2,2,2,2,2,1,
  0,1,2,2,2,2,1,0,
  0,0,1,1,1,1,0,0,
  0,0,0,0,0,0,0,0,
];

const Coin = ({ x, y }) => (
  <sprite x={x} y={y} data={coinData} palette={['transparent', '#daa520', '#ffd700']} />
);
```

## Relative Positioning

Position child elements relative to a parent concept:

```jsx
// A character with a health bar above their head
const CharacterWithHP = ({ x, y, hp, maxHp }) => (
  <>
    {/* Health bar background */}
    <rect x={x} y={y - 3} width={8} height={2} color="#333333" />
    {/* Health bar fill */}
    <rect x={x} y={y - 3} width={Math.round((hp / maxHp) * 8)} height={2} color="#00ff00" />
    {/* Character sprite */}
    <sprite x={x} y={y} data={playerData} palette={playerPalette} />
    {/* Shadow beneath */}
    <rect x={x + 1} y={y + 8} width={6} height={1} color="#0a0a1a" />
  </>
);
```

## Building a Complete Scene: The Dungeon Room

```jsx
import React from 'react';
import { Stage } from 'pixel8';

// Tile data
const wallTile = [
  1,1,1,1,1,1,1,1,
  1,2,2,2,2,2,2,1,
  1,2,2,2,2,2,2,1,
  1,2,2,2,2,2,2,1,
  1,1,1,1,1,1,1,1,
  1,2,2,2,2,2,2,1,
  1,2,2,2,2,2,2,1,
  1,2,2,2,2,2,2,1,
];

const floorTile = [
  1,1,1,1,1,1,1,1,
  1,2,2,2,2,2,2,2,
  1,2,2,2,2,2,2,2,
  1,2,2,2,2,2,2,2,
  1,2,2,2,2,2,2,2,
  1,2,2,2,2,2,2,2,
  1,2,2,2,2,2,2,2,
  1,2,2,2,2,2,2,2,
];

const wallPalette = ['transparent', '#333344', '#222233'];
const floorPalette = ['transparent', '#2a2a3a', '#1e1e2e'];

// Room layout: 0=floor, 1=wall
const room = [
  [1,1,1,1,1,1,1,1],
  [1,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,1],
  [1,0,0,0,0,0,0,1],
  [1,1,1,1,1,1,1,1],
];

const DungeonRoom = () => (
  <Stage width={64} height={64} scale={8} fps={60} background="#0a0a1a">
    {/* Render tile map */}
    {room.map((row, ry) =>
      row.map((tile, rx) => (
        <sprite
          key={`${rx}-${ry}`}
          x={rx * 8}
          y={ry * 8}
          data={tile === 1 ? wallTile : floorTile}
          palette={tile === 1 ? wallPalette : floorPalette}
        />
      ))
    )}

    {/* Items on the floor */}
    <Coin x={24} y={24} />
    <Coin x={36} y={36} />

    {/* Player */}
    <Player x={28} y={28} palette={['transparent', '#4488ff', '#ffffff']} />

    {/* Torch on wall */}
    <animation frames={torchFrames} speed={300} x={8} y={8} palette={torchPalette} />

    {/* HUD on top */}
    <rect x={0} y={0} width={64} height={7} color="#000000" />
    <text x={1} y={1} value="HP:3 G:02" color="#ffffff" />
  </Stage>
);
```

### What You Should See

A dungeon room with stone walls around the border, a darker floor in the center, two gold coins, a blue player character, a flickering torch, and a HUD bar at the top showing health and gold.

## Scene Management with React State

```jsx
const scenes = {
  title: TitleScene,
  dungeon: DungeonScene,
  shop: ShopScene,
  gameOver: GameOverScene,
};

const Game = () => {
  const [currentScene, setCurrentScene] = useState('title');
  const [gameState, setGameState] = useState({
    score: 0,
    lives: 3,
    level: 1,
    inventory: [],
  });

  const SceneComponent = scenes[currentScene];

  return (
    <SceneComponent
      gameState={gameState}
      setGameState={setGameState}
      changeScene={setCurrentScene}
    />
  );
};
```

## Pattern: Screen Transitions

```jsx
const [transitioning, setTransitioning] = useState(false);
const [fadeOpacity, setFadeOpacity] = useState(0);

const changeScene = (newScene) => {
  setTransitioning(true);
  // Fade out
  const fadeOut = setInterval(() => {
    setFadeOpacity(o => {
      if (o >= 8) {
        clearInterval(fadeOut);
        setCurrentScene(newScene);
        // Fade in
        const fadeIn = setInterval(() => {
          setFadeOpacity(o2 => {
            if (o2 <= 0) { clearInterval(fadeIn); setTransitioning(false); return 0; }
            return o2 - 1;
          });
        }, 50);
        return 8;
      }
      return o + 1;
    });
  }, 50);
};

// Render fade overlay on top of everything
{fadeOpacity > 0 && (
  <rect x={0} y={0} width={64} height={64} color={`#000000`} />
)}
```

## Pattern: Camera / Viewport

For worlds larger than 64×64, offset all positions by a camera value:

```jsx
const [camera, setCamera] = useState({ x: 0, y: 0 });

// Center camera on player
useGameLoop(() => {
  setCamera({
    x: Math.max(0, playerX - 28),
    y: Math.max(0, playerY - 28),
  });
});

// Render everything offset by camera
const worldObjects = objects.map(obj => (
  <sprite
    key={obj.id}
    x={obj.x - camera.x}
    y={obj.y - camera.y}
    data={obj.data}
    palette={obj.palette}
  />
));
```

## Pattern: Particle System

```jsx
const useParticles = () => {
  const [particles, setParticles] = useState([]);

  const emit = (x, y, count = 5) => {
    const newParticles = Array.from({ length: count }, (_, i) => ({
      id: Date.now() + i,
      x, y,
      vx: (Math.random() - 0.5) * 20,
      vy: -Math.random() * 30,
      life: 1.0,
      color: ['#ffd700', '#ff6600', '#ff0000'][Math.floor(Math.random() * 3)],
    }));
    setParticles(prev => [...prev, ...newParticles]);
  };

  const update = (dt) => {
    setParticles(prev =>
      prev
        .map(p => ({
          ...p,
          x: p.x + p.vx * dt,
          y: p.y + p.vy * dt,
          vy: p.vy + 60 * dt, // gravity
          life: p.life - dt * 2,
        }))
        .filter(p => p.life > 0)
    );
  };

  return { particles, emit, update };
};

// Render particles
{particles.map(p => (
  <pixel key={p.id} x={Math.round(p.x)} y={Math.round(p.y)} color={p.color} />
))}
```

## Tips: Scene Composition

1. **Depth through color** — darker/desaturated = farther away, brighter/saturated = closer
2. **Ground your sprites** — add 1px shadows beneath characters so they don't float
3. **Frame the action** — walls/borders guide the eye to the center where gameplay happens
4. **Negative space** — don't fill every pixel. Empty space makes important elements stand out
5. **Consistent lighting** — pick a light direction (top-left is classic) and shade all sprites accordingly

## Exercise

1. Build a **two-room dungeon** — player walks to the edge, scene switches to the next room
2. Create a **parallax background** — two layers of mountains scrolling at different speeds
3. Implement a **coin collection** effect — when player touches a coin, emit particles and remove it
4. Design a **shop scene** — display items in a grid with prices, highlight on selection

## Quick Reference

```jsx
// Layer order (back to front)
<Stage>
  <Background />    {/* Layer 0 */}
  <Terrain />       {/* Layer 1 */}
  <Objects />       {/* Layer 2 */}
  <Player />        {/* Layer 3 */}
  <Effects />       {/* Layer 4 */}
  <UI />            {/* Layer 5 */}
</Stage>

// Scene switching
const [scene, setScene] = useState('title');
const Scene = scenes[scene];
<Scene changeScene={setScene} />

// Camera offset
<sprite x={obj.x - camera.x} y={obj.y - camera.y} ... />
```

| Pattern | Purpose |
|---------|---------|
| Layer ordering | Depth and visual hierarchy |
| Component extraction | Reusable game objects |
| Relative positioning | Health bars, shadows, labels |
| Tile maps | Efficient room/level rendering |
| Scene state | Multiple screens (title, game, over) |
| Camera offset | Worlds larger than the viewport |
| Particles | Juice and feedback |

---

Next: The final chapter. We combine everything into a complete, playable mini-game. BitForge comes alive.

[← Chapter 8: Palettes](chapter-08-palettes.md) | [Chapter 10: Mini-Game →](chapter-10-mini-game.md)
