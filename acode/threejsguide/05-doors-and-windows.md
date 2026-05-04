# Chapter 5: Doors & Windows

> **What you'll learn:** Click events, hover states, `useFrame` for animation, `useRef` for direct manipulation, and `useState` for toggling.

### Events — Making Objects Clickable

R3F supports pointer events on any mesh, just like DOM elements:

```tsx
<mesh
  onClick={(e) => console.log('clicked!')}
  onPointerOver={(e) => console.log('hovering')}
  onPointerOut={(e) => console.log('left')}
>
```

The event object `e` contains:
- `e.point` — the exact 3D coordinate where the click/hover hit
- `e.object` — the Three.js object that was hit
- `e.stopPropagation()` — prevent the event from hitting objects behind this one

### Hover Effects

Let's make the door change color on hover:

```tsx
'use client'

import { useState } from 'react'

function Door() {
  const [hovered, setHovered] = useState(false)

  return (
    <mesh
      position={[0, 0.75, 1.46]}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[0.6, 1.5, 0.05]} />
      <meshStandardMaterial color={hovered ? '#7c4a2e' : '#5c3a1e'} />
    </mesh>
  )
}
```

> **Cursor hint:** Change the cursor to indicate interactivity:
> ```tsx
> onPointerOver={() => {
>   document.body.style.cursor = 'pointer'
>   setHovered(true)
> }}
> onPointerOut={() => {
>   document.body.style.cursor = 'auto'
>   setHovered(false)
> }}
> ```

### Animation with `useFrame`

`useFrame` runs a callback every frame (~60fps). This is your animation engine.

**Rule:** Never update React state inside `useFrame`. It would trigger 60 re-renders per second. Use **refs** for per-frame mutations.

```tsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import type { Mesh } from 'three'

function SpinningBox() {
  const meshRef = useRef<Mesh>(null)

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta  // delta = time since last frame
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

`delta` is the time in seconds since the last frame. Using `delta` instead of a fixed value makes animation **frame-rate independent** — it runs at the same speed on 30fps and 144fps monitors.

### Animating the Door — Open/Close on Click

Let's make the door swing open when clicked:

```tsx
'use client'

import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import type { Group } from 'three'
import { MathUtils } from 'three'

function Door() {
  const groupRef = useRef<Group>(null)
  const [open, setOpen] = useState(false)
  const [hovered, setHovered] = useState(false)

  useFrame(() => {
    if (!groupRef.current) return
    // Smoothly interpolate toward target rotation
    const target = open ? -Math.PI / 2 : 0
    groupRef.current.rotation.y = MathUtils.lerp(
      groupRef.current.rotation.y,
      target,
      0.1
    )
  })

  return (
    // Pivot point: the group's position is at the door's hinge (left edge)
    <group ref={groupRef} position={[-0.3, 0.75, 1.46]}>
      <mesh
        position={[0.3, 0, 0]}  // offset so door swings from left edge
        onClick={() => setOpen(!open)}
        onPointerOver={() => {
          document.body.style.cursor = 'pointer'
          setHovered(true)
        }}
        onPointerOut={() => {
          document.body.style.cursor = 'auto'
          setHovered(false)
        }}
        castShadow
      >
        <boxGeometry args={[0.6, 1.5, 0.05]} />
        <meshStandardMaterial color={hovered ? '#7c4a2e' : '#5c3a1e'} />
      </mesh>
    </group>
  )
}

export default Door
```

### The Pivot Trick

The door rotates around the **group's origin**, not its own center. By placing the group at the left edge of the door and offsetting the mesh, the door swings like a real door on hinges.

```
Group position (hinge)
  │
  ├──── Mesh offset ────┐
  │                      │
  │     [  DOOR  ]       │
  │                      │
```

This is a fundamental 3D technique: **use a parent group as a pivot point**.

### `MathUtils.lerp` — Smooth Animation

`lerp(current, target, factor)` — Linear interpolation. Each frame, the value moves 10% (`0.1`) of the remaining distance toward the target. This creates smooth easing — fast at first, slowing as it approaches.

- `factor = 0.1` — smooth, gentle
- `factor = 0.3` — snappy
- `factor = 1.0` — instant (no animation)

### The `useFrame` + `useState` Pattern

Notice we use **both** `useState` and `useFrame`:
- `useState` stores the **intent** (door should be open/closed) — changes on click
- `useFrame` handles the **animation** (smoothly rotating toward the target) — runs every frame

State changes rarely. Animation runs constantly. This separation is key to performant R3F code.

### Integrate the Door into the House

Replace the static door mesh in `House.tsx` with the `<Door />` component:

```tsx
import Door from './Door'

export default function House() {
  return (
    <group>
      {/* ... walls, floor, roof ... */}

      {/* Replace the old static door mesh with: */}
      <Door />

      {/* ... rest of house ... */}
    </group>
  )
}
```

---

> **🏗 Progress:** The house is interactive! The door opens and closes, objects respond to hover. Next, we'll bring in real 3D models — furniture for the house.

---

[← Chapter 4: Wiring the Electricity](./04-wiring-the-electricity.md) | [Chapter 6: Furniture →](./06-furniture.md)
