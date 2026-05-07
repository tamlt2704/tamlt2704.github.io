# Chapter 6: Input & Controls — "Control the Player"

[← Chapter 5: Spritesheet Animation](chapter-05-spritesheet-animation.md) | [Chapter 7: Tilemap →](chapter-07-tilemap.md)

---

## The Crisis

The knight walks in place. Beautifully animated, going nowhere. Kai says: "Arrow keys. WASD. I don't care. Just let me move him."

PixiJS doesn't have built-in keyboard handling. It's a rendering engine, not a game framework. You need to wire up browser keyboard events yourself. But you're a React dev — you know `useEffect` and event listeners.

## Naive Approach: useState + onKeyDown

Your first instinct:

```jsx
// ❌ This works but has problems
function Player() {
  const [x, setX] = useState(240);
  const [y, setY] = useState(160);

  useEffect(() => {
    function handleKey(e) {
      if (e.key === 'ArrowUp') setY(y => y - 4);
      if (e.key === 'ArrowDown') setY(y => y + 4);
      if (e.key === 'ArrowLeft') setX(x => x - 4);
      if (e.key === 'ArrowRight') setX(x => x + 4);
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  return <Sprite image="./sprites/knight.png" x={x} y={y} scale={3} anchor={0.5} />;
}
```

Problems:
1. **Key repeat delay** — hold a key and there's a pause before it repeats (OS key repeat behavior)
2. **No diagonal movement** — only one key registers at a time
3. **useState triggers re-renders** — 60 re-renders/sec when moving

## The Proper Approach: Track Key State

Track which keys are currently **held down**, then read that state in `useTick`:

```jsx
import { useEffect, useRef } from 'react';
import { Sprite } from '@pixi/react';
import { useTick } from '@pixi/react';

function Player() {
  const ref = useRef(null);
  const keys = useRef({});

  // Track key state
  useEffect(() => {
    const onDown = (e) => { keys.current[e.key] = true; };
    const onUp = (e) => { keys.current[e.key] = false; };
    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);
    return () => {
      window.removeEventListener('keydown', onDown);
      window.removeEventListener('keyup', onUp);
    };
  }, []);

  // Move based on held keys every frame
  useTick((delta) => {
    if (!ref.current) return;
    const speed = 3 * delta;

    if (keys.current['ArrowUp'] || keys.current['w']) ref.current.y -= speed;
    if (keys.current['ArrowDown'] || keys.current['s']) ref.current.y += speed;
    if (keys.current['ArrowLeft'] || keys.current['a']) ref.current.x -= speed;
    if (keys.current['ArrowRight'] || keys.current['d']) ref.current.x += speed;
  });

  return <Sprite ref={ref} image="./sprites/knight.png" x={240} y={160} scale={3} anchor={0.5} />;
}
```

Now:
- No key repeat delay — movement starts immediately
- Diagonal movement works (hold two keys at once)
- No re-renders — direct mutation via ref

## Building a Reusable useKeyboard Hook

Extract the key tracking into a custom hook:

```jsx
// src/hooks/useKeyboard.js
import { useEffect, useRef } from 'react';

export function useKeyboard() {
  const keys = useRef({});

  useEffect(() => {
    const onDown = (e) => {
      keys.current[e.key] = true;
      // Prevent arrow keys from scrolling the page
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
        e.preventDefault();
      }
    };
    const onUp = (e) => {
      keys.current[e.key] = false;
    };
    // Reset all keys when window loses focus
    const onBlur = () => {
      keys.current = {};
    };

    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);
    window.addEventListener('blur', onBlur);
    return () => {
      window.removeEventListener('keydown', onDown);
      window.removeEventListener('keyup', onUp);
      window.removeEventListener('blur', onBlur);
    };
  }, []);

  return keys;
}
```

The `blur` handler is important — if the player alt-tabs away while holding a key, the `keyup` event never fires. Resetting on blur prevents "stuck" keys.

Usage:

```jsx
import { useKeyboard } from '../hooks/useKeyboard';

function Player() {
  const ref = useRef(null);
  const keys = useKeyboard();

  useTick((delta) => {
    if (!ref.current) return;
    const speed = 3 * delta;

    if (keys.current['ArrowUp'] || keys.current['w']) ref.current.y -= speed;
    if (keys.current['ArrowDown'] || keys.current['s']) ref.current.y += speed;
    if (keys.current['ArrowLeft'] || keys.current['a']) ref.current.x -= speed;
    if (keys.current['ArrowRight'] || keys.current['d']) ref.current.x += speed;
  });

  return <Sprite ref={ref} image="./sprites/knight.png" x={240} y={160} scale={3} anchor={0.5} />;
}
```

## Connecting Input to Animation

Now combine keyboard input with the animation system from Chapter 5:

```jsx
function Player({ sheet }) {
  const ref = useRef(null);
  const keys = useKeyboard();
  const [direction, setDirection] = useState('down');
  const [isMoving, setIsMoving] = useState(false);
  const posRef = useRef({ x: 240, y: 160 });

  useTick((delta) => {
    if (!ref.current) return;
    const speed = 3 * delta;
    let moving = false;
    let dir = direction;

    if (keys.current['ArrowUp'] || keys.current['w']) {
      posRef.current.y -= speed;
      dir = 'up';
      moving = true;
    }
    if (keys.current['ArrowDown'] || keys.current['s']) {
      posRef.current.y += speed;
      dir = 'down';
      moving = true;
    }
    if (keys.current['ArrowLeft'] || keys.current['a']) {
      posRef.current.x -= speed;
      dir = 'left';
      moving = true;
    }
    if (keys.current['ArrowRight'] || keys.current['d']) {
      posRef.current.x += speed;
      dir = 'right';
      moving = true;
    }

    ref.current.x = posRef.current.x;
    ref.current.y = posRef.current.y;

    // Only update React state when direction/moving actually changes
    if (dir !== direction) setDirection(dir);
    if (moving !== isMoving) setIsMoving(moving);
  });

  const animations = useMemo(() => ({
    idle: [sheet.textures['idle_0']],
    walk_down: getFrames(sheet, 'walk_down', 4),
    walk_up: getFrames(sheet, 'walk_up', 4),
    walk_left: getFrames(sheet, 'walk_left', 4),
    walk_right: getFrames(sheet, 'walk_right', 4),
  }), [sheet]);

  const currentAnim = isMoving ? `walk_${direction}` : 'idle';

  return (
    <AnimatedSprite
      ref={ref}
      textures={animations[currentAnim]}
      isPlaying={isMoving}
      animationSpeed={0.12}
      x={240}
      y={160}
      anchor={0.5}
      scale={3}
    />
  );
}
```

Key insight: position updates happen via ref (every frame, no re-render). Direction/moving state updates happen via useState (only when they change, triggers animation swap).

## Pointer/Mouse Events

PixiJS sprites can be interactive — they respond to clicks, taps, and hover:

```jsx
function ClickableChest({ x, y, onOpen }) {
  return (
    <Sprite
      image="./sprites/chest.png"
      x={x}
      y={y}
      scale={3}
      anchor={0.5}
      interactive={true}
      pointerdown={() => onOpen()}
      cursor="pointer"
    />
  );
}
```

Available pointer events:
- `pointerdown` — mouse click or touch start
- `pointerup` — mouse release or touch end
- `pointerover` — mouse enters sprite bounds
- `pointerout` — mouse leaves sprite bounds
- `pointermove` — mouse moves over sprite
- `pointertap` — quick tap/click (down + up without moving)

## Touch Support

Pointer events work for both mouse and touch automatically. But for mobile games, you might want on-screen buttons:

```jsx
function DPad({ onDirection }) {
  return (
    <Container x={60} y={240}>
      {/* Up */}
      <Sprite
        image="./sprites/btn_up.png"
        x={24} y={0}
        interactive={true}
        pointerdown={() => onDirection('up', true)}
        pointerup={() => onDirection('up', false)}
        scale={2}
      />
      {/* Down */}
      <Sprite
        image="./sprites/btn_down.png"
        x={24} y={48}
        interactive={true}
        pointerdown={() => onDirection('down', true)}
        pointerup={() => onDirection('down', false)}
        scale={2}
      />
      {/* Left */}
      <Sprite
        image="./sprites/btn_left.png"
        x={0} y={24}
        interactive={true}
        pointerdown={() => onDirection('left', true)}
        pointerup={() => onDirection('left', false)}
        scale={2}
      />
      {/* Right */}
      <Sprite
        image="./sprites/btn_right.png"
        x={48} y={24}
        interactive={true}
        pointerdown={() => onDirection('right', true)}
        pointerup={() => onDirection('right', false)}
        scale={2}
      />
    </Container>
  );
}
```

## Action Keys (Attack, Interact)

For one-shot actions (not held), detect the key press moment:

```jsx
function useKeyPress(targetKey) {
  const pressed = useRef(false);
  const wasPressed = useRef(false);

  useEffect(() => {
    const onDown = (e) => { if (e.key === targetKey) pressed.current = true; };
    const onUp = (e) => { if (e.key === targetKey) pressed.current = false; };
    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);
    return () => {
      window.removeEventListener('keydown', onDown);
      window.removeEventListener('keyup', onUp);
    };
  }, [targetKey]);

  // Returns true only on the frame the key was first pressed
  function justPressed() {
    if (pressed.current && !wasPressed.current) {
      wasPressed.current = true;
      return true;
    }
    if (!pressed.current) wasPressed.current = false;
    return false;
  }

  return { held: pressed, justPressed };
}

// Usage in game loop
const attack = useKeyPress(' ');  // spacebar

useTick(() => {
  if (attack.justPressed()) {
    // Trigger attack animation (once, not every frame)
    setIsAttacking(true);
  }
});
```

## Putting It Together

```jsx
import { Stage, AnimatedSprite } from '@pixi/react';
import { useTick } from '@pixi/react';
import { useKeyboard } from '../hooks/useKeyboard';
import * as PIXI from 'pixi.js';

PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

function Game({ sheet }) {
  const ref = useRef(null);
  const keys = useKeyboard();
  const [direction, setDirection] = useState('down');
  const [isMoving, setIsMoving] = useState(false);
  const pos = useRef({ x: 240, y: 160 });

  useTick((delta) => {
    if (!ref.current) return;
    const speed = 2.5 * delta;
    let moving = false;
    let dir = direction;

    if (keys.current['w'] || keys.current['ArrowUp']) { pos.current.y -= speed; dir = 'up'; moving = true; }
    if (keys.current['s'] || keys.current['ArrowDown']) { pos.current.y += speed; dir = 'down'; moving = true; }
    if (keys.current['a'] || keys.current['ArrowLeft']) { pos.current.x -= speed; dir = 'left'; moving = true; }
    if (keys.current['d'] || keys.current['ArrowRight']) { pos.current.x += speed; dir = 'right'; moving = true; }

    ref.current.x = pos.current.x;
    ref.current.y = pos.current.y;
    if (dir !== direction) setDirection(dir);
    if (moving !== isMoving) setIsMoving(moving);
  });

  const anims = useMemo(() => ({
    idle: [sheet.textures['idle_0']],
    walk_down: getFrames(sheet, 'walk_down', 4),
    walk_up: getFrames(sheet, 'walk_up', 4),
    walk_left: getFrames(sheet, 'walk_left', 4),
    walk_right: getFrames(sheet, 'walk_right', 4),
  }), [sheet]);

  const anim = isMoving ? `walk_${direction}` : 'idle';

  return (
    <AnimatedSprite
      ref={ref}
      textures={anims[anim]}
      isPlaying={isMoving}
      animationSpeed={0.12}
      x={240}
      y={160}
      anchor={0.5}
      scale={3}
    />
  );
}
```

## Verify

- [ ] Arrow keys and WASD move the player smoothly
- [ ] No key repeat delay — movement is instant
- [ ] Diagonal movement works (hold two keys)
- [ ] Walk animation plays while moving, idle when stopped
- [ ] Direction changes update the animation
- [ ] Pointer events work on interactive sprites
- [ ] Keys don't get "stuck" when alt-tabbing

Kai watches you walk the knight around a blank canvas. "Cool. But there's no dungeon. He's walking on nothing. I drew tiles — floor, walls, doors. Can you build a room?"

Time to render a tile map. That's Chapter 7.

---

[← Chapter 5: Spritesheet Animation](chapter-05-spritesheet-animation.md) | [Chapter 7: Tilemap →](chapter-07-tilemap.md)
