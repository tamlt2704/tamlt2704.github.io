# Chapter 2: Containers & Layout — "Organize the Scene"

[← Chapter 1: First Sprite](chapter-01-first-sprite.md) | [Chapter 3: Graphics & Shapes →](chapter-03-graphics-shapes.md)

---

## The Crisis

You have six sprites floating in the Stage. Kai wants a floor layer, a character layer, and a HUD layer. When the camera moves (Chapter 7), the floor and characters should scroll, but the HUD stays fixed.

In web dev, you'd use `<div>` wrappers with `position: relative`. In PixiJS, you use `<Container>`.

## The Container Component

A `Container` groups children and gives them a shared coordinate space:

```jsx
import { Stage, Container, Sprite } from '@pixi/react';

function App() {
  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e }}>
      <Container x={100} y={50}>
        <Sprite image="./sprites/knight.png" x={0} y={0} scale={3} />
        <Sprite image="./sprites/slime.png" x={80} y={20} scale={3} />
      </Container>
    </Stage>
  );
}
```

The knight is at (100, 50) in world space. The slime is at (180, 70). Children position **relative to their parent container** — just like `position: relative` in CSS.

## Why Containers Matter

Move the container, and all children move with it:

```jsx
// Move the whole group by changing one value
<Container x={200} y={100}>
  <Sprite image="./sprites/knight.png" x={0} y={0} scale={3} />
  <Sprite image="./sprites/slime.png" x={80} y={20} scale={3} />
  <Sprite image="./sprites/chest.png" x={40} y={60} scale={3} />
</Container>
```

This is how you'll implement camera scrolling later — move the world container, and everything in the world moves together.

## Layer Architecture

For DungeonBit, we need three layers:

```jsx
function Game() {
  return (
    <>
      {/* Layer 1: World (scrolls with camera) */}
      <Container x={0} y={0}>
        {/* Floor tiles */}
        {/* Characters */}
        {/* Items */}
      </Container>

      {/* Layer 2: HUD (fixed on screen) */}
      <Container x={0} y={0}>
        {/* Health bar */}
        {/* Score text */}
        {/* Minimap */}
      </Container>
    </>
  );
}
```

The world container will move when the player walks. The HUD container stays at (0, 0) — always visible, always in the same spot.

## Nesting Containers

Containers nest just like `<div>`s:

```jsx
function Game() {
  const [cameraX, setCameraX] = useState(0);
  const [cameraY, setCameraY] = useState(0);

  return (
    <>
      {/* World layer — moves with camera */}
      <Container x={-cameraX} y={-cameraY}>

        {/* Floor sub-layer */}
        <Container>
          <Sprite image="./sprites/floor.png" x={0} y={0} scale={3} />
          <Sprite image="./sprites/floor.png" x={48} y={0} scale={3} />
          <Sprite image="./sprites/floor.png" x={96} y={0} scale={3} />
        </Container>

        {/* Characters sub-layer (drawn on top of floor) */}
        <Container>
          <Sprite image="./sprites/knight.png" x={48} y={48} scale={3} anchor={0.5} />
          <Sprite image="./sprites/slime.png" x={144} y={96} scale={3} anchor={0.5} />
        </Container>

      </Container>

      {/* HUD layer — stays fixed */}
      <Container x={10} y={10}>
        {/* We'll add health bars in Chapter 3 */}
      </Container>
    </>
  );
}
```

## The Z-Order Problem

By default, children render in **source order** — first child is drawn first (behind), last child is drawn last (in front).

```jsx
<Container>
  <Sprite image="./sprites/floor.png" />    {/* drawn first (behind) */}
  <Sprite image="./sprites/knight.png" />   {/* drawn second (in front) */}
</Container>
```

This works for simple cases. But what if you need dynamic ordering? A character walking behind a pillar, then in front of it?

## zIndex and sortableChildren

Enable sorting on a container, then use `zIndex` on children:

```jsx
<Container sortableChildren={true}>
  <Sprite image="./sprites/pillar.png" x={100} y={100} zIndex={5} scale={3} />
  <Sprite image="./sprites/knight.png" x={100} y={120} zIndex={3} scale={3} />
</Container>
```

Higher `zIndex` = drawn on top. The knight (zIndex 3) renders behind the pillar (zIndex 5).

### Dynamic Z-Ordering by Y Position

In top-down games, objects lower on screen should appear in front (closer to the viewer). A common trick: set `zIndex` to the sprite's `y` position.

```jsx
function Character({ image, x, y }) {
  return (
    <Sprite
      image={image}
      x={x}
      y={y}
      zIndex={y}        // lower on screen = higher zIndex = drawn in front
      anchor={{ x: 0.5, y: 1 }}  // anchor at feet
      scale={3}
    />
  );
}

function CharacterLayer() {
  return (
    <Container sortableChildren={true}>
      <Character image="./sprites/knight.png" x={100} y={150} />
      <Character image="./sprites/slime.png" x={120} y={180} />
      <Character image="./sprites/slime.png" x={80} y={130} />
    </Container>
  );
}
```

The slime at y=180 renders in front of the knight at y=150, which renders in front of the slime at y=130. Natural depth sorting.

## Container Props

| Prop | Type | Description |
|---|---|---|
| `x` | number | X position relative to parent |
| `y` | number | Y position relative to parent |
| `scale` | number or {x, y} | Scale all children |
| `rotation` | number | Rotate all children (radians) |
| `alpha` | number | Opacity for all children (0–1) |
| `visible` | boolean | Show/hide entire group |
| `sortableChildren` | boolean | Enable zIndex sorting |
| `interactive` | boolean | Enable pointer events on container |

## Scaling a Container

Scale the container, and all children scale with it:

```jsx
{/* Everything inside is 2x bigger */}
<Container scale={2}>
  <Sprite image="./sprites/knight.png" x={0} y={0} />
  <Sprite image="./sprites/slime.png" x={16} y={0} />
</Container>
```

This is useful for zoom effects or rendering a minimap (scale the world container down to 0.2).

## Alpha on Containers

Fade an entire group:

```jsx
{/* Fade out the whole HUD during cutscenes */}
<Container alpha={0.3}>
  <Sprite image="./sprites/health_bar.png" x={10} y={10} />
  <Sprite image="./sprites/coin_icon.png" x={10} y={40} />
</Container>
```

## Visibility Toggle

Hide a container and all its children:

```jsx
function Game() {
  const [showInventory, setShowInventory] = useState(false);

  return (
    <>
      <Container>{/* game world */}</Container>

      {/* Inventory overlay — toggled with a key */}
      <Container visible={showInventory} x={50} y={50}>
        <Sprite image="./sprites/inventory_bg.png" />
        {/* inventory items */}
      </Container>
    </>
  );
}
```

When `visible` is `false`, the container and all children are skipped during rendering. No GPU cost.

## The DungeonBit Scene Structure

Here's how we'll organize the full game:

```jsx
function DungeonBit() {
  return (
    <Stage width={480} height={320} options={{ background: 0x1a1a2e, antialias: false }}>

      {/* World layer (scrolls) */}
      <Container x={0} y={0}>

        {/* Floor tiles */}
        <Container>
          {/* tile sprites... */}
        </Container>

        {/* Objects (chests, doors, traps) */}
        <Container sortableChildren={true}>
          {/* object sprites... */}
        </Container>

        {/* Characters (player, enemies) */}
        <Container sortableChildren={true}>
          {/* character sprites with zIndex={y} */}
        </Container>

      </Container>

      {/* HUD layer (fixed) */}
      <Container x={0} y={0}>
        {/* health bar, score, minimap */}
      </Container>

      {/* Dialog layer (on top of everything) */}
      <Container visible={false}>
        {/* dialog box, text */}
      </Container>

    </Stage>
  );
}
```

## Verify

- [ ] Containers group sprites and position them relatively
- [ ] Moving a parent container moves all children
- [ ] `sortableChildren` + `zIndex` controls draw order
- [ ] `visible={false}` hides entire groups
- [ ] Nested containers work (world > floor > tiles)

Kai sends a message: "I need you to draw a health bar. It's just a rectangle that shrinks. Don't make me draw 100 frames of a health bar."

You don't need a sprite for that. You need `<Graphics>`.

That's Chapter 3.

---

[← Chapter 1: First Sprite](chapter-01-first-sprite.md) | [Chapter 3: Graphics & Shapes →](chapter-03-graphics-shapes.md)
