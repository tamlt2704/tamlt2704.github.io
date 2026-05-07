# Chapter 8: Collision — "Don't Walk Through Walls"

[← Chapter 7: Tilemap](chapter-07-tilemap.md) | [Chapter 9: Game State →](chapter-09-game-state.md)

---

## The Crisis

The knight walks through walls. Through doors. Through everything. The dungeon has no physics — it's just sprites drawn at coordinates. Nothing stops anything.

Kai: "He should bump into walls. And pick up keys when he walks over them. And take damage when he touches a slime."

PixiJS is a renderer, not a physics engine. You need to write collision detection yourself. For a tile-based dungeon, that's simpler than it sounds.

## AABB Collision Detection

AABB = Axis-Aligned Bounding Box. Two rectangles overlap if they overlap on both axes:

```jsx
function rectsOverlap(a, b) {
  return (
    a.x < b.x + b.width &&
    a.x + a.width > b.x &&
    a.y < b.y + b.height &&
    a.y + a.height > b.y
  );
}
```

That's it. Four comparisons. If all four are true, the rectangles overlap.

## Player Hitbox

The player sprite is 16×16 scaled to 48×48, but the collision box should be smaller — just the body, not the full sprite:

```jsx
function getPlayerHitbox(x, y) {
  // Player anchor is (0.5, 0.5), so x,y is center
  // Hitbox is smaller than the sprite (12×12 scaled to 36×36)
  const size = 12 * 3;  // 36px
  return {
    x: x - size / 2,
    y: y - size / 2,
    width: size,
    height: size,
  };
}
```

## Tile-Based Collision

For a tile map, check if the player's hitbox overlaps any solid tile:

```jsx
function isSolidTile(mapData, col, row) {
  if (row < 0 || row >= mapData.length) return true;       // out of bounds = solid
  if (col < 0 || col >= mapData[0].length) return true;
  const tile = mapData[row][col];
  return tile === 1;  // 1 = wall
}

function getTileAt(worldX, worldY, tileSize, scale) {
  const scaledSize = tileSize * scale;
  return {
    col: Math.floor(worldX / scaledSize),
    row: Math.floor(worldY / scaledSize),
  };
}
```

## Movement with Collision Resolution

The key pattern: try to move, check for collision, undo if blocked. Check X and Y separately so the player can slide along walls:

```jsx
function moveWithCollision(pos, dx, dy, mapData, tileSize, scale) {
  const scaledSize = tileSize * scale;
  const hitboxSize = 12 * scale;  // smaller than tile
  const halfHit = hitboxSize / 2;

  // Try X movement
  const newX = pos.x + dx;
  const hitboxX = {
    x: newX - halfHit,
    y: pos.y - halfHit,
    width: hitboxSize,
    height: hitboxSize,
  };

  if (!collidesWithMap(hitboxX, mapData, scaledSize)) {
    pos.x = newX;
  }

  // Try Y movement (independently)
  const newY = pos.y + dy;
  const hitboxY = {
    x: pos.x - halfHit,
    y: newY - halfHit,
    width: hitboxSize,
    height: hitboxSize,
  };

  if (!collidesWithMap(hitboxY, mapData, scaledSize)) {
    pos.y = newY;
  }
}

function collidesWithMap(hitbox, mapData, scaledSize) {
  // Check all tiles the hitbox overlaps
  const startCol = Math.floor(hitbox.x / scaledSize);
  const endCol = Math.floor((hitbox.x + hitbox.width - 1) / scaledSize);
  const startRow = Math.floor(hitbox.y / scaledSize);
  const endRow = Math.floor((hitbox.y + hitbox.height - 1) / scaledSize);

  for (let row = startRow; row <= endRow; row++) {
    for (let col = startCol; col <= endCol; col++) {
      if (isSolidTile(mapData, col, row)) {
        return true;
      }
    }
  }
  return false;
}
```

Checking X and Y separately means the player slides along walls instead of getting stuck. Hold right + down near a wall, and you'll slide along it.

## Integrating with the Player

```jsx
function Player({ sheet, mapData, posRef }) {
  const ref = useRef(null);
  const keys = useKeyboard();
  const [direction, setDirection] = useState('down');
  const [isMoving, setIsMoving] = useState(false);

  useTick((delta) => {
    if (!ref.current) return;
    const speed = 3 * delta;
    let dx = 0;
    let dy = 0;
    let moving = false;
    let dir = direction;

    if (keys.current['w'] || keys.current['ArrowUp']) { dy = -speed; dir = 'up'; moving = true; }
    if (keys.current['s'] || keys.current['ArrowDown']) { dy = speed; dir = 'down'; moving = true; }
    if (keys.current['a'] || keys.current['ArrowLeft']) { dx = -speed; dir = 'left'; moving = true; }
    if (keys.current['d'] || keys.current['ArrowRight']) { dx = speed; dir = 'right'; moving = true; }

    // Apply movement with collision
    moveWithCollision(posRef.current, dx, dy, mapData, 16, 3);

    ref.current.x = posRef.current.x;
    ref.current.y = posRef.current.y;
    if (dir !== direction) setDirection(dir);
    if (moving !== isMoving) setIsMoving(moving);
  });

  // ... AnimatedSprite with animations
  return (
    <AnimatedSprite
      ref={ref}
      textures={anims[isMoving ? `walk_${direction}` : 'idle']}
      isPlaying={isMoving}
      animationSpeed={0.12}
      x={posRef.current.x}
      y={posRef.current.y}
      anchor={0.5}
      scale={3}
    />
  );
}
```

Now the knight bumps into walls and slides along them. No more walking through solid tiles.

## Collectibles: Overlap Detection

Keys, coins, and potions don't block movement — they get picked up on contact:

```jsx
function useCollectibles(initialItems) {
  const [items, setItems] = useState(initialItems);

  function checkCollection(playerHitbox) {
    const collected = [];
    const remaining = items.filter(item => {
      const itemBox = {
        x: item.x - 16,
        y: item.y - 16,
        width: 32,
        height: 32,
      };
      if (rectsOverlap(playerHitbox, itemBox)) {
        collected.push(item);
        return false;  // remove from list
      }
      return true;  // keep
    });

    if (collected.length > 0) {
      setItems(remaining);
    }
    return collected;
  }

  return { items, checkCollection };
}
```

Usage in the game loop:

```jsx
function Game({ assets }) {
  const playerPos = useRef({ x: 240, y: 200 });
  const { items, checkCollection } = useCollectibles([
    { id: 1, type: 'key', x: 300, y: 150 },
    { id: 2, type: 'coin', x: 400, y: 250 },
    { id: 3, type: 'potion', x: 150, y: 300 },
  ]);

  useTick(() => {
    const hitbox = getPlayerHitbox(playerPos.current.x, playerPos.current.y);
    const collected = checkCollection(hitbox);
    collected.forEach(item => {
      if (item.type === 'key') console.log('Got a key!');
      if (item.type === 'coin') console.log('+10 score');
      if (item.type === 'potion') console.log('+1 health');
    });
  });

  return (
    <>
      <Player posRef={playerPos} mapData={room1} sheet={assets.knight} />
      {items.map(item => (
        <Sprite
          key={item.id}
          image={`./sprites/${item.type}.png`}
          x={item.x}
          y={item.y}
          anchor={0.5}
          scale={3}
        />
      ))}
    </>
  );
}
```

When the player walks over an item, it disappears from the list and the sprite is removed.

## Enemy Collision (Damage)

Enemies damage the player on contact. Add an invincibility window so the player doesn't take 60 damage per second:

```jsx
function useEnemyCollision(playerPos, enemies, onHit) {
  const invincibleUntil = useRef(0);

  useTick(() => {
    if (Date.now() < invincibleUntil.current) return;  // still invincible

    const playerBox = getPlayerHitbox(playerPos.current.x, playerPos.current.y);

    for (const enemy of enemies) {
      const enemyBox = {
        x: enemy.x - 18,
        y: enemy.y - 18,
        width: 36,
        height: 36,
      };

      if (rectsOverlap(playerBox, enemyBox)) {
        onHit(enemy);
        invincibleUntil.current = Date.now() + 1000;  // 1 second invincibility
        break;
      }
    }
  });
}
```

## Door/Trigger Zones

Doors trigger level transitions when the player steps on them:

```jsx
function useTriggerZones(playerPos, zones, onTrigger) {
  const triggered = useRef(new Set());

  useTick(() => {
    const playerBox = getPlayerHitbox(playerPos.current.x, playerPos.current.y);

    zones.forEach(zone => {
      const zoneBox = {
        x: zone.x,
        y: zone.y,
        width: zone.width,
        height: zone.height,
      };

      if (rectsOverlap(playerBox, zoneBox)) {
        if (!triggered.current.has(zone.id)) {
          triggered.current.add(zone.id);
          onTrigger(zone);
        }
      } else {
        triggered.current.delete(zone.id);  // reset when player leaves
      }
    });
  });
}

// Usage
const doors = [
  { id: 'door_south', x: 384, y: 630, width: 96, height: 48, target: 'room2' },
];

useTriggerZones(playerPos, doors, (zone) => {
  console.log(`Entering ${zone.target}`);
  // Load next room
});
```

## Debug: Visualize Hitboxes

Draw collision boxes during development:

```jsx
function DebugCollision({ mapData, tileSize = 16, scale = 3, visible = false }) {
  const draw = useCallback((g) => {
    if (!visible) return;
    g.clear();
    g.lineStyle(1, 0xff0000, 0.3);
    const s = tileSize * scale;

    for (let row = 0; row < mapData.length; row++) {
      for (let col = 0; col < mapData[row].length; col++) {
        if (isSolidTile(mapData, col, row)) {
          g.drawRect(col * s, row * s, s, s);
        }
      }
    }
  }, [mapData, tileSize, scale, visible]);

  return <Graphics draw={draw} />;
}
```

## Verify

- [ ] Player cannot walk through walls
- [ ] Player slides along walls (X and Y checked independently)
- [ ] Collectibles disappear on contact
- [ ] Enemy contact triggers damage (with invincibility window)
- [ ] Door zones trigger level transitions
- [ ] Debug overlay shows solid tiles

Kai: "The knight bumps into walls, picks up keys, takes damage from slimes. But where does the health go? Where's the score? I need a HUD."

Game state management. That's Chapter 9.

---

[← Chapter 7: Tilemap](chapter-07-tilemap.md) | [Chapter 9: Game State →](chapter-09-game-state.md)
