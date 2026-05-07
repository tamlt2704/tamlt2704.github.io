# Chapter 2: The Foundation

> **What you'll learn:** Built-in geometries, material types, and how to make things look real.

### Built-in Geometries — Your Building Blocks

Three.js gives you primitives to build with:

| Geometry | What It Makes | Key Args |
|---|---|---|
| `boxGeometry` | Box/cube | `[width, height, depth]` |
| `sphereGeometry` | Sphere | `[radius, widthSegments, heightSegments]` |
| `planeGeometry` | Flat rectangle | `[width, height]` |
| `cylinderGeometry` | Cylinder/pillar | `[topRadius, bottomRadius, height, segments]` |
| `coneGeometry` | Cone/roof shape | `[radius, height, segments]` |
| `torusGeometry` | Donut/ring | `[radius, tubeRadius, segments, tubularSegments]` |

For our house, we'll use:
- `planeGeometry` for the ground
- `boxGeometry` for walls and the base
- `coneGeometry` for the roof
- `cylinderGeometry` for pillars or a chimney

### Materials — How Surfaces Look

Materials define how light interacts with a surface. The main ones, from simple to complex:

**`meshBasicMaterial`** — No lighting. Flat color. Useful for debugging or stylized looks.
```tsx
<meshBasicMaterial color="red" />
```

**`meshStandardMaterial`** — The workhorse. Physically-based rendering (PBR). Responds to light realistically.
```tsx
<meshStandardMaterial color="#8B4513" roughness={0.8} metalness={0.1} />
```
- `roughness` (0-1): 0 = mirror, 1 = matte chalk
- `metalness` (0-1): 0 = plastic/wood, 1 = metal

**`meshPhysicalMaterial`** — Extends standard. Adds clearcoat, transmission (glass), sheen (fabric).
```tsx
<meshPhysicalMaterial color="white" transmission={0.9} roughness={0.1} />
```
This makes glass. `transmission={0.9}` means 90% of light passes through.

### Let's Build the Ground

Replace your Scene component's content:

**`src/components/Ground.tsx`**
```tsx
'use client'

export default function Ground() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
      <planeGeometry args={[20, 20]} />
      <meshStandardMaterial color="#4a7c59" />
    </mesh>
  )
}
```

> **Why `rotation={[-Math.PI / 2, 0, 0]}`?** A plane is vertical by default (facing the camera). Rotating it -90° around the X axis lays it flat like a floor. Rotations are in **radians**, not degrees. `Math.PI / 2` = 90°.

### Build the House Base

**`src/components/House.tsx`** (starting simple)
```tsx
'use client'

export default function House() {
  return (
    <mesh position={[0, 0.5, 0]}>
      <boxGeometry args={[2, 1, 2]} />
      <meshStandardMaterial color="#d4a574" />
    </mesh>
  )
}
```

A 2×1×2 box, raised up by 0.5 so it sits on the ground (the ground is at y=-0.5, the box center is at y=0.5, so its bottom edge is at y=0 — right on the ground).

### Update the Scene

**`src/components/Scene.tsx`**
```tsx
'use client'

import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import Ground from './Ground'
import House from './House'

export default function Scene() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas camera={{ position: [5, 3, 5], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <Ground />
        <House />
        <OrbitControls />
      </Canvas>
    </div>
  )
}
```

Now you can click and drag to orbit around your scene. You should see a brown box sitting on green ground.

> **`OrbitControls`** from drei gives you mouse interaction: left-click drag to rotate, scroll to zoom, right-click drag to pan. One import, zero configuration.

### Key Concept: The Camera

We set `camera={{ position: [5, 3, 5], fov: 50 }}`:
- Position `[5, 3, 5]` — 5 units right, 3 up, 5 toward us. An elevated diagonal view.
- `fov: 50` — field of view in degrees. Lower = more telephoto/flat. Higher = more wide-angle/distorted. 50 is natural.

The camera automatically looks at `[0, 0, 0]` by default.

---

> **🏗 Progress:** Foundation poured. You have ground and a base structure. Next, we'll shape the walls and roof.

---

[← Chapter 1: The Empty Lot](./01-the-empty-lot.md) | [Chapter 3: The Walls →](./03-the-walls.md)
