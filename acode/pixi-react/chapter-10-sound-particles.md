# Chapter 10: Sound & Particles — "Polish: Juice It Up"

[← Chapter 9: Game State](chapter-09-game-state.md) | [Chapter 11: Levels & Scenes →](chapter-11-levels-scenes.md)

---

## The Crisis

The game works. You can move, fight, collect, die, restart. But it feels... silent. Flat. No feedback. Kai picks up a key and nothing happens except a number changing. A slime hits you and there's no impact.

Kai: "It needs juice. A coin sound. Hit sparks. Screen shake when you take damage. Make it feel good."

## Sound Effects with Howler.js

PixiJS doesn't handle audio. Use Howler.js — it's simple, cross-browser, and handles the Web Audio API mess for you:

```bash
npm install howler
```

### Sound Manager

```jsx
// src/hooks/useSound.js
import { Howl } from 'howler';
import { useMemo } from 'react';

export function useSound() {
  const sounds = useMemo(() => ({
    coin: new Howl({ src: ['./audio/coin.wav'], volume: 0.5 }),
    hit: new Howl({ src: ['./audio/hit.wav'], volume: 0.6 }),
    key: new Howl({ src: ['./audio/key.wav'], volume: 0.5 }),
    door: new Howl({ src: ['./audio/door.wav'], volume: 0.4 }),
    death: new Howl({ src: ['./audio/death.wav'], volume: 0.7 }),
    step: new Howl({ src: ['./audio/step.wav'], volume: 0.2 }),
    attack: new Howl({ src: ['./audio/attack.wav'], volume: 0.5 }),
    music: new Howl({
      src: ['./audio/dungeon_loop.mp3'],
      volume: 0.3,
      loop: true,
    }),
  }), []);

  return sounds;
}
```

### Playing Sounds on Events

```jsx
function Game() {
  const sounds = useSound();
  const dispatch = useGameDispatch();

  function onCollect(item) {
    switch (item.type) {
      case 'coin':
        sounds.coin.play();
        dispatch({ type: 'ADD_SCORE', amount: 10 });
        break;
      case 'key':
        sounds.key.play();
        dispatch({ type: 'COLLECT_KEY' });
        break;
      case 'potion':
        sounds.coin.play();  // reuse coin sound
        dispatch({ type: 'HEAL', amount: 3 });
        break;
    }
  }

  function onEnemyHit() {
    sounds.hit.play();
    dispatch({ type: 'TAKE_DAMAGE', amount: 1 });
  }

  // Start music on first interaction
  useEffect(() => {
    function startMusic() {
      sounds.music.play();
      window.removeEventListener('click', startMusic);
      window.removeEventListener('keydown', startMusic);
    }
    window.addEventListener('click', startMusic);
    window.addEventListener('keydown', startMusic);
    return () => {
      window.removeEventListener('click', startMusic);
      window.removeEventListener('keydown', startMusic);
    };
  }, [sounds]);

  // ...
}
```

**Note:** Browsers block audio until the user interacts with the page. Start music on the first click or keypress.

## Particle System

Particles are small sprites that spawn, move, fade, and die. Perfect for hit sparks, dust clouds, and coin pickups.

### A Simple Particle

```jsx
function Particle({ x, y, vx, vy, life, color, onDead }) {
  const ref = useRef(null);
  const state = useRef({ x, y, vx, vy, life, maxLife: life });

  useTick((delta) => {
    if (!ref.current) return;
    const s = state.current;

    s.x += s.vx * delta;
    s.y += s.vy * delta;
    s.vy += 0.2 * delta;  // gravity
    s.life -= delta;

    ref.current.x = s.x;
    ref.current.y = s.y;
    ref.current.alpha = Math.max(0, s.life / s.maxLife);

    if (s.life <= 0) onDead();
  });

  const draw = useCallback((g) => {
    g.clear();
    g.beginFill(color);
    g.drawRect(-2, -2, 4, 4);  // 4×4 pixel particle
    g.endFill();
  }, [color]);

  return <Graphics ref={ref} draw={draw} x={x} y={y} />;
}
```

### Particle Emitter

```jsx
import { Container } from '@pixi/react';
import { useState, useCallback } from 'react';

function ParticleEmitter() {
  const [particles, setParticles] = useState([]);
  let nextId = useRef(0);

  const emit = useCallback((x, y, count, options = {}) => {
    const {
      color = 0xffffff,
      speed = 3,
      life = 30,
      spread = Math.PI * 2,
    } = options;

    const newParticles = [];
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * spread - spread / 2;
      const vel = speed * (0.5 + Math.random() * 0.5);
      newParticles.push({
        id: nextId.current++,
        x,
        y,
        vx: Math.cos(angle) * vel,
        vy: Math.sin(angle) * vel,
        life,
        color,
      });
    }
    setParticles(prev => [...prev, ...newParticles]);
  }, []);

  const removeParticle = useCallback((id) => {
    setParticles(prev => prev.filter(p => p.id !== id));
  }, []);

  return { emit, particles, removeParticle };
}
```

### Using the Emitter

```jsx
function Game() {
  const { emit, particles, removeParticle } = ParticleEmitter();

  function onEnemyHit(enemy) {
    // Spawn hit sparks
    emit(enemy.x, enemy.y, 8, {
      color: 0xff4444,
      speed: 4,
      life: 20,
    });
    sounds.hit.play();
    dispatch({ type: 'TAKE_DAMAGE', amount: 1 });
  }

  function onCoinCollect(item) {
    // Spawn gold sparkles
    emit(item.x, item.y, 5, {
      color: 0xffd700,
      speed: 2,
      life: 25,
    });
    sounds.coin.play();
    dispatch({ type: 'ADD_SCORE', amount: 10 });
  }

  return (
    <>
      {/* Game world */}
      <World onEnemyHit={onEnemyHit} onCoinCollect={onCoinCollect} />

      {/* Particles layer (on top) */}
      <Container>
        {particles.map(p => (
          <Particle
            key={p.id}
            {...p}
            onDead={() => removeParticle(p.id)}
          />
        ))}
      </Container>
    </>
  );
}
```

## Screen Shake

The most impactful juice effect. When the player takes damage, shake the entire world:

```jsx
function useScreenShake() {
  const shakeRef = useRef({ intensity: 0, duration: 0 });
  const offsetRef = useRef({ x: 0, y: 0 });

  function shake(intensity = 5, duration = 15) {
    shakeRef.current.intensity = intensity;
    shakeRef.current.duration = duration;
  }

  useTick((delta) => {
    const s = shakeRef.current;
    if (s.duration > 0) {
      s.duration -= delta;
      const decay = s.duration / 15;  // fade out
      offsetRef.current.x = (Math.random() - 0.5) * s.intensity * decay;
      offsetRef.current.y = (Math.random() - 0.5) * s.intensity * decay;
    } else {
      offsetRef.current.x = 0;
      offsetRef.current.y = 0;
    }
  });

  return { shake, offset: offsetRef };
}
```

Apply the shake offset to the world container:

```jsx
function Game() {
  const { shake, offset } = useScreenShake();
  const worldRef = useRef(null);

  function onPlayerHit() {
    shake(6, 12);  // strong shake for 12 frames
    sounds.hit.play();
    dispatch({ type: 'TAKE_DAMAGE', amount: 1 });
  }

  useTick(() => {
    if (worldRef.current) {
      // Apply camera position + shake offset
      worldRef.current.x = -cameraX + Math.round(offset.current.x);
      worldRef.current.y = -cameraY + Math.round(offset.current.y);
    }
  });

  return (
    <Container ref={worldRef}>
      {/* world content */}
    </Container>
  );
}
```

## Flash on Damage

Make the player sprite flash white when hit:

```jsx
function Player({ sheet, posRef, mapData }) {
  const ref = useRef(null);
  const flashUntil = useRef(0);

  function onHit() {
    flashUntil.current = Date.now() + 200;  // flash for 200ms
  }

  useTick(() => {
    if (!ref.current) return;
    // Flash white by toggling tint
    if (Date.now() < flashUntil.current) {
      ref.current.tint = Math.random() > 0.5 ? 0xffffff : 0xff0000;
    } else {
      ref.current.tint = 0xffffff;  // normal
    }
  });

  return <AnimatedSprite ref={ref} /* ... */ />;
}
```

## Dust Particles on Movement

Spawn tiny dust particles when the player moves:

```jsx
function useMovementDust(playerPos, isMoving, emit) {
  const lastDust = useRef(0);

  useTick(() => {
    if (!isMoving) return;
    if (Date.now() - lastDust.current < 200) return;  // throttle

    lastDust.current = Date.now();
    emit(playerPos.current.x, playerPos.current.y + 20, 2, {
      color: 0x888888,
      speed: 1,
      life: 15,
      spread: Math.PI / 4,
    });
  });
}
```

## Floating Damage Numbers

Show "-1" floating up when the player takes damage:

```jsx
function DamageNumber({ x, y, amount, onDone }) {
  const ref = useRef(null);
  const state = useRef({ y, life: 40 });

  useTick((delta) => {
    if (!ref.current) return;
    state.current.y -= 1 * delta;
    state.current.life -= delta;
    ref.current.y = state.current.y;
    ref.current.alpha = Math.max(0, state.current.life / 40);
    if (state.current.life <= 0) onDone();
  });

  return (
    <Text
      ref={ref}
      text={`-${amount}`}
      style={new PIXI.TextStyle({ fontFamily: 'monospace', fontSize: 14, fill: 0xff4444, fontWeight: 'bold' })}
      x={x}
      y={y}
      anchor={0.5}
    />
  );
}
```

## The Juice Checklist

| Event | Sound | Visual |
|---|---|---|
| Collect coin | coin.wav | Gold sparkle particles |
| Collect key | key.wav | White sparkle particles |
| Player hit | hit.wav | Screen shake + flash + damage number |
| Enemy dies | death.wav | Red particles burst |
| Door opens | door.wav | — |
| Player moves | step.wav (throttled) | Dust particles |
| Attack | attack.wav | Slash effect |

## Verify

- [ ] Sounds play on game events
- [ ] Music loops in the background
- [ ] Particles spawn, move, fade, and disappear
- [ ] Screen shake triggers on damage
- [ ] Player flashes when hit
- [ ] No memory leaks (particles are cleaned up)
- [ ] Audio starts after first user interaction

Kai plays the game. Coins sparkle. Hits shake the screen. The dungeon hums with ambient music. "This feels like a real game. But we only have one room. We need a title screen, multiple floors, and a win condition."

Scenes and levels. That's Chapter 11.

---

[← Chapter 9: Game State](chapter-09-game-state.md) | [Chapter 11: Levels & Scenes →](chapter-11-levels-scenes.md)
