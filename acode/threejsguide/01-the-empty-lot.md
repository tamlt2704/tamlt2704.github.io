# Chapter 1: The Empty Lot

> **What you'll learn:** What `<Canvas>` does, the coordinate system, and how to place your first 3D object.

### The Canvas — Your Construction Site

In R3F, `<Canvas>` is everything. It creates:
- A **WebGL renderer** (the thing that draws pixels)
- A **scene** (the container for all 3D objects)
- A **camera** (the viewpoint — defaults to a perspective camera at `[0, 0, 5]`)
- A **render loop** (redraws 60 times per second, automatically)

You never touch these directly. `<Canvas>` manages them.

### Your First Scene

Create the scene component. This must be a Client Component because Three.js needs the browser.

**`src/components/Scene.tsx`**
```tsx
'use client'

import { Canvas } from '@react-three/fiber'

function Box() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}

export default function Scene() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas>
        <ambientLight intensity={0.5} />
        <Box />
      </Canvas>
    </div>
  )
}
```

**`src/app/page.tsx`**
```tsx
import dynamic from 'next/dynamic'

const Scene = dynamic(() => import('@/components/Scene'), { ssr: false })

export default function Home() {
  return <Scene />
}
```

> **Why `dynamic` with `ssr: false`?** Extra safety. Even though `Scene` is `'use client'`, Next.js still tries to pre-render it. `dynamic` with `ssr: false` ensures the component only loads in the browser. This avoids any `window is not defined` errors.

### What Just Happened?

You should see an orange square on a dark background. It looks flat because:
- There's only ambient light (no shadows, no direction)
- The camera is looking straight at one face of the cube

But it's actually a 3D cube. You just can't tell yet.

### The Coordinate System

Three.js uses a **right-handed coordinate system**:

```
        Y (up)
        |
        |
        |_______ X (right)
       /
      /
     Z (toward you)
```

- `[0, 0, 0]` is the center of the world
- The default camera sits at `[0, 0, 5]` — 5 units back along Z, looking at the origin
- Your box is at `[0, 0, 0]` by default

### Understanding the JSX

Every Three.js class has a JSX equivalent in R3F:

| Three.js (imperative) | R3F (declarative) |
|---|---|
| `new THREE.Mesh()` | `<mesh>` |
| `new THREE.BoxGeometry(1,1,1)` | `<boxGeometry args={[1,1,1]} />` |
| `new THREE.MeshStandardMaterial({color:'orange'})` | `<meshStandardMaterial color="orange" />` |
| `new THREE.AmbientLight(0xffffff, 0.5)` | `<ambientLight intensity={0.5} />` |

The `args` prop maps to constructor arguments. Properties become props. That's the entire mapping rule.

### Key Concept: Mesh = Geometry + Material

A **mesh** is the fundamental visible object. It's always two things:
- **Geometry** — the shape (vertices, faces). *What* it is.
- **Material** — the surface appearance (color, roughness, metalness). *How it looks.*

Think of it like building a wall: geometry is the bricks (structure), material is the paint (appearance).

### Try This

Change the box to a sphere:

```tsx
<mesh>
  <sphereGeometry args={[0.75, 32, 32]} />
  <meshStandardMaterial color="orange" />
</mesh>
```

`args={[0.75, 32, 32]}` means: radius 0.75, 32 width segments, 32 height segments. More segments = smoother sphere.

---

> **🏗 Progress:** You have an empty lot with a single object sitting on it. Next, we'll learn about different shapes and materials — pouring the foundation.

---

[← Introduction](./00-introduction.md) | [Chapter 2: The Foundation →](./02-the-foundation.md)
