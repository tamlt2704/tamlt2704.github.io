# 3D in the Browser — React Three Fiber

---

## What Is React Three Fiber (R3F)?

Three.js (the 3D library) wrapped in React components. Instead of imperative code, you write JSX:

```tsx
// Three.js (imperative)
const geometry = new THREE.BoxGeometry(1, 1, 1)
const material = new THREE.MeshStandardMaterial({ color: "hotpink" })
const mesh = new THREE.Mesh(geometry, material)
scene.add(mesh)

// React Three Fiber (declarative)
<mesh>
  <boxGeometry args={[1, 1, 1]} />
  <meshStandardMaterial color="hotpink" />
</mesh>
```

Same result — but R3F manages the scene, camera, renderer, and animation loop for you.

---

## Step 1: Install

```bash
npm install three @react-three/fiber @react-three/drei
npm install -D @types/three
```

| Package | What it does |
|---------|-------------|
| `three` | The 3D engine |
| `@react-three/fiber` | React renderer for Three.js |
| `@react-three/drei` | Helpers (camera controls, text, loaders, shadows, etc.) |

---

## Step 2: First 3D Scene

```tsx
"use client"

import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"

export function Scene() {
  return (
    <div className="h-[500px] w-full rounded-lg border bg-card">
      <Canvas>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />

        <mesh>
          <boxGeometry args={[2, 2, 2]} />
          <meshStandardMaterial color="hotpink" />
        </mesh>

        <OrbitControls />
      </Canvas>
    </div>
  )
}
```

**What each part does:**

| Element | What it is |
|---------|-----------|
| `<Canvas>` | Creates the WebGL renderer, scene, and camera |
| `<ambientLight>` | Soft light everywhere (no shadows) |
| `<pointLight>` | Light from a point (creates shadows) |
| `<mesh>` | A 3D object (geometry + material) |
| `<boxGeometry>` | The shape (cube: width, height, depth) |
| `<meshStandardMaterial>` | The surface (reacts to light) |
| `<OrbitControls>` | Drag to rotate, scroll to zoom |

---

## Step 3: Understanding the Coordinate System

```
        Y (up)
        │
        │
        │───────── X (right)
       ╱
      ╱
     Z (toward you)
```

- `position={[x, y, z]}` — where an object sits
- `rotation={[rx, ry, rz]}` — rotation in radians
- `scale={[sx, sy, sz]}` — size multiplier

---

## Step 4: Animation (useFrame)

`useFrame` runs every frame (~60fps). It's your animation loop:

```tsx
"use client"

import { useRef } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Mesh } from "three"

function SpinningBox() {
  const meshRef = useRef<Mesh>(null)

  useFrame((_, delta) => {
    if (!meshRef.current) return
    meshRef.current.rotation.x += delta  // rotate based on time passed
    meshRef.current.rotation.y += delta * 0.5
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="royalblue" />
    </mesh>
  )
}

export function Scene() {
  return (
    <Canvas>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <SpinningBox />
      <OrbitControls />
    </Canvas>
  )
}
```

**`delta`** = time since last frame. Multiply by delta so animation speed is consistent regardless of frame rate.

---

## Step 5: Common Geometries

```tsx
// Box
<boxGeometry args={[width, height, depth]} />

// Sphere
<sphereGeometry args={[radius, widthSegments, heightSegments]} />
<sphereGeometry args={[1, 32, 32]} />

// Cylinder
<cylinderGeometry args={[topRadius, bottomRadius, height, segments]} />
<cylinderGeometry args={[0.5, 0.5, 2, 32]} />

// Plane (flat surface)
<planeGeometry args={[width, height]} />
<planeGeometry args={[10, 10]} />

// Torus (donut)
<torusGeometry args={[radius, tubeRadius, radialSegments, tubularSegments]} />
<torusGeometry args={[1, 0.4, 16, 32]} />

// Cone
<coneGeometry args={[radius, height, segments]} />
```

---

## Step 6: Materials

| Material | Light reaction | Use for |
|----------|---------------|---------|
| `meshBasicMaterial` | None (flat color) | Wireframes, debugging, unlit scenes |
| `meshStandardMaterial` | Realistic (PBR) | Most objects |
| `meshPhongMaterial` | Shiny highlights | Glossy surfaces |
| `meshLambertMaterial` | Matte, no shine | Non-reflective surfaces |
| `meshNormalMaterial` | Colors by surface direction | Debugging normals |

```tsx
// Metallic, rough
<meshStandardMaterial color="gold" metalness={0.8} roughness={0.2} />

// Glass-like
<meshStandardMaterial color="white" transparent opacity={0.3} />

// Wireframe
<meshBasicMaterial color="lime" wireframe />
```

---

## Step 7: Interaction (Click, Hover)

```tsx
function InteractiveBox() {
  const [hovered, setHovered] = useState(false)
  const [clicked, setClicked] = useState(false)

  return (
    <mesh
      scale={clicked ? 1.5 : 1}
      onClick={() => setClicked(!clicked)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[1.5, 1.5, 1.5]} />
      <meshStandardMaterial color={hovered ? "hotpink" : "royalblue"} />
    </mesh>
  )
}
```

Events work like normal React — `onClick`, `onPointerOver`, etc.

---

## Step 8: Multiple Objects

```tsx
function Boxes() {
  const positions: [number, number, number][] = [
    [-3, 0, 0],
    [0, 0, 0],
    [3, 0, 0],
  ]

  return (
    <>
      {positions.map((pos, i) => (
        <mesh key={i} position={pos}>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color={`hsl(${i * 60}, 70%, 50%)`} />
        </mesh>
      ))}
    </>
  )
}
```

---

## Step 9: Text in 3D

```tsx
import { Text } from "@react-three/drei"

<Text
  position={[0, 3, 0]}
  fontSize={0.5}
  color="white"
  anchorX="center"
  anchorY="middle"
>
  Hello 3D World
</Text>
```

---

## Step 10: 3D Algorithm Visualisations

### 3D Bar Chart (Sorting)

```tsx
function Bars({ data }: { data: number[] }) {
  return (
    <>
      {data.map((value, i) => (
        <mesh key={i} position={[i * 1.2 - (data.length * 0.6), value / 2, 0]}>
          <boxGeometry args={[1, value, 1]} />
          <meshStandardMaterial color={`hsl(${value * 3}, 70%, 50%)`} />
        </mesh>
      ))}
    </>
  )
}
```

### 3D Graph (Nodes in Space)

```tsx
function GraphNode({ position, label }: { position: [number, number, number]; label: string }) {
  return (
    <group position={position}>
      <mesh>
        <sphereGeometry args={[0.3, 32, 32]} />
        <meshStandardMaterial color="royalblue" />
      </mesh>
      <Text position={[0, 0.5, 0]} fontSize={0.2} color="white">
        {label}
      </Text>
    </group>
  )
}

function GraphEdge({ start, end }: { start: [number, number, number]; end: [number, number, number] }) {
  const midpoint: [number, number, number] = [
    (start[0] + end[0]) / 2,
    (start[1] + end[1]) / 2,
    (start[2] + end[2]) / 2,
  ]
  const length = Math.sqrt(
    (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2 + (end[2] - start[2]) ** 2
  )

  return (
    <mesh position={midpoint}>
      <cylinderGeometry args={[0.02, 0.02, length, 8]} />
      <meshBasicMaterial color="gray" />
    </mesh>
  )
}
```

### 3D Matrix (Pathfinding in a Cube)

```tsx
function Grid3D({ grid }: { grid: CellState[][][] }) {
  return (
    <>
      {grid.map((layer, z) =>
        layer.map((row, y) =>
          row.map((cell, x) =>
            cell !== "empty" && (
              <mesh key={`${x}-${y}-${z}`} position={[x, y, z]}>
                <boxGeometry args={[0.9, 0.9, 0.9]} />
                <meshStandardMaterial
                  color={cell === "visited" ? "blue" : cell === "path" ? "yellow" : "gray"}
                  transparent
                  opacity={cell === "visited" ? 0.3 : 0.8}
                />
              </mesh>
            )
          )
        )
      )}
    </>
  )
}
```

---

## Step 11: 3D Physics (cannon-es + R3F)

```bash
npm install @react-three/cannon
```

```tsx
import { Physics, useBox, usePlane, useSphere } from "@react-three/cannon"

function Ground() {
  const [ref] = usePlane(() => ({
    rotation: [-Math.PI / 2, 0, 0],  // flat on the ground
    position: [0, -2, 0],
  }))
  return (
    <mesh ref={ref}>
      <planeGeometry args={[20, 20]} />
      <meshStandardMaterial color="#303030" />
    </mesh>
  )
}

function FallingBox({ position }: { position: [number, number, number] }) {
  const [ref] = useBox(() => ({
    mass: 1,
    position,
    args: [1, 1, 1],  // box size for physics
  }))
  return (
    <mesh ref={ref}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="tomato" />
    </mesh>
  )
}

function BouncingBall() {
  const [ref] = useSphere(() => ({
    mass: 1,
    position: [0, 5, 0],
    args: [0.5],  // radius
    restitution: 0.9,  // very bouncy
  }))
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial color="royalblue" />
    </mesh>
  )
}

export function PhysicsScene() {
  return (
    <Canvas>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <Physics gravity={[0, -9.81, 0]}>
        <Ground />
        <FallingBox position={[0, 5, 0]} />
        <FallingBox position={[0.5, 8, 0]} />
        <FallingBox position={[-0.3, 11, 0.2]} />
        <BouncingBall />
      </Physics>
      <OrbitControls />
    </Canvas>
  )
}
```

**That's it.** Wrap everything in `<Physics>`, use hooks (`useBox`, `useSphere`, `usePlane`) — objects fall, collide, and bounce automatically.

---

## Step 12: Useful drei Helpers

```tsx
import {
  OrbitControls,    // drag to rotate camera
  Stars,           // starfield background
  Environment,     // lighting presets
  Float,           // slow floating animation
  Html,            // HTML inside 3D scene
  Line,            // draw lines between points
  PerspectiveCamera,
} from "@react-three/drei"

// Floating object
<Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
  <mesh>...</mesh>
</Float>

// HTML label attached to 3D position
<Html position={[0, 2, 0]}>
  <div className="rounded bg-card px-2 py-1 text-sm text-foreground">
    Node A
  </div>
</Html>

// Line between points
<Line
  points={[[0, 0, 0], [2, 3, 0], [5, 0, 0]]}
  color="white"
  lineWidth={2}
/>

// Preset lighting (studio, sunset, forest, etc.)
<Environment preset="sunset" />

// Stars background
<Stars radius={100} depth={50} count={5000} factor={4} />
```

---

## Performance Tips

| Tip | Why |
|-----|-----|
| Use `instancedMesh` for many identical objects | 1000 boxes = 1 draw call instead of 1000 |
| Limit geometry segments | `sphereGeometry args={[1, 16, 16]}` not `[1, 64, 64]}` |
| Use `useMemo` for geometries/materials | Don't recreate every render |
| Add `frameloop="demand"` to Canvas | Only re-render when something changes |
| Dispose of textures/geometries on unmount | Prevent memory leaks |

### Instanced Mesh (1000+ Objects)

```tsx
import { useRef, useMemo } from "react"
import { InstancedMesh, Object3D, Color } from "three"

function Particles({ count = 1000 }) {
  const meshRef = useRef<InstancedMesh>(null)
  const dummy = useMemo(() => new Object3D(), [])

  useEffect(() => {
    for (let i = 0; i < count; i++) {
      dummy.position.set(
        Math.random() * 20 - 10,
        Math.random() * 20 - 10,
        Math.random() * 20 - 10
      )
      dummy.updateMatrix()
      meshRef.current!.setMatrixAt(i, dummy.matrix)
      meshRef.current!.setColorAt(i, new Color(`hsl(${Math.random() * 360}, 70%, 50%)`))
    }
    meshRef.current!.instanceMatrix.needsUpdate = true
    meshRef.current!.instanceColor!.needsUpdate = true
  }, [count])

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
      <sphereGeometry args={[0.1, 8, 8]} />
      <meshStandardMaterial />
    </instancedMesh>
  )
}
```

---

## When 2D vs 3D

| Use 2D (SVG/Canvas + Framer Motion) | Use 3D (R3F) |
|-------------------------------------|--------------|
| Sorting visualisations | 3D graph traversal |
| 2D pathfinding grids | Data landscapes |
| Tree/graph in a plane | Molecular structures |
| Simple physics demos | Full physics simulations |
| Better accessibility | Portfolio "wow" factor |
| Faster to build | Spatial data (geographic, architectural) |
| Works on all devices | Needs decent GPU |

---

## Resources

| Resource | What | Free? |
|----------|------|-------|
| [R3F docs](https://r3f.docs.pmnd.rs) | Official docs | ✅ |
| [drei docs](https://drei.docs.pmnd.rs) | Helper library | ✅ |
| [Three.js Journey](https://threejs-journey.com) | Best course (Three.js + R3F) | 💰 |
| [Bruno Simon's portfolio](https://bruno-simon.com) | Inspiration (3D portfolio) | ✅ |
| [pmndrs examples](https://github.com/pmndrs/react-three-fiber/discussions/categories/show-and-tell) | Community examples | ✅ |
| [Sketchfab](https://sketchfab.com) | Free 3D models to use | ✅ (some) |

---

## Step 13: Combining Framer Motion + React Three Fiber

They work on different layers:
- **Framer Motion (`motion/react`)** → animates 2D HTML/CSS (UI overlays, panels, page transitions)
- **React Three Fiber** → animates 3D objects inside `<Canvas>`
- **motion/three** → Framer Motion's declarative API directly on 3D objects

### Way 1: Framer Motion for UI Around 3D

```tsx
"use client"

import { motion } from "motion/react"
import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"

export function CombinedScene() {
  return (
    <div className="relative h-[600px]">
      {/* Framer Motion: animate the canvas container */}
      <motion.div
        className="h-full w-full"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Canvas>
          <ambientLight />
          <pointLight position={[10, 10, 10]} />
          <SpinningBox />
          <OrbitControls />
        </Canvas>
      </motion.div>

      {/* Framer Motion: overlay UI on top of 3D */}
      <motion.div
        className="absolute bottom-4 left-4 rounded-lg bg-card/80 p-4 backdrop-blur"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p className="text-foreground">Drag to rotate</p>
      </motion.div>
    </div>
  )
}
```

### Way 2: motion/three (Framer Motion for 3D Objects)

Import from `motion/three` instead of `motion/react` — gives you `motion.mesh`, `motion.meshStandardMaterial`, etc.:

```tsx
"use client"

import { Canvas } from "@react-three/fiber"
import { motion } from "motion/three"
import { OrbitControls } from "@react-three/drei"
import { useState } from "react"

function AnimatedBox() {
  const [clicked, setClicked] = useState(false)

  return (
    <motion.mesh
      animate={{ scale: clicked ? 1.5 : 1 }}
      transition={{ type: "spring", stiffness: 300 }}
      onClick={() => setClicked(!clicked)}
      whileHover={{ scale: 1.2 }}
    >
      <boxGeometry args={[2, 2, 2]} />
      <motion.meshStandardMaterial
        animate={{ color: clicked ? "hotpink" : "royalblue" }}
        transition={{ duration: 0.5 }}
      />
    </motion.mesh>
  )
}

export function Scene() {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <AnimatedBox />
      <OrbitControls />
    </Canvas>
  )
}
```

### What motion/three Supports

| Prop | Works? | Example |
|------|--------|---------|
| `animate` | ✅ | `animate={{ scale: 2, rotationY: Math.PI }}` |
| `initial` | ✅ | `initial={{ scale: 0 }}` |
| `whileHover` | ✅ | `whileHover={{ scale: 1.2 }}` |
| `whileTap` | ✅ | `whileTap={{ scale: 0.9 }}` |
| `transition` | ✅ | `transition={{ type: "spring" }}` |
| `variants` | ✅ | Same as 2D motion |
| `layout` | ❌ | No layout animations in 3D |
| `exit` / `AnimatePresence` | ❌ | Not yet |

### Animated Properties in motion/three

```tsx
<motion.mesh
  animate={{
    scale: 2,
    rotationX: Math.PI,
    rotationY: 0.5,
    positionX: 3,
    positionY: 1,
    positionZ: -2,
  }}
/>

<motion.meshStandardMaterial
  animate={{
    color: "#ff0000",
    opacity: 0.5,  // needs transparent={true} on the material
  }}
/>
```

### 3D Sorting Visualisation with motion/three

```tsx
"use client"

import { Canvas } from "@react-three/fiber"
import { motion } from "motion/three"
import { OrbitControls } from "@react-three/drei"

interface Bar {
  value: number
  state: "default" | "comparing" | "sorted"
}

function Bar3D({ value, index, state }: { value: number; index: number; state: string }) {
  const color = state === "comparing" ? "yellow" : state === "sorted" ? "green" : "royalblue"

  return (
    <motion.mesh
      position={[index * 1.5 - 6, value / 2, 0]}
      animate={{
        positionX: index * 1.5 - 6,
        positionY: value / 2,
        scale: state === "comparing" ? 1.1 : 1,
      }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
    >
      <boxGeometry args={[1, value, 1]} />
      <motion.meshStandardMaterial
        animate={{ color }}
        transition={{ duration: 0.3 }}
      />
    </motion.mesh>
  )
}

export function Sort3D({ data }: { data: Bar[] }) {
  return (
    <Canvas camera={{ position: [0, 5, 15], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      {data.map((bar, i) => (
        <Bar3D key={i} value={bar.value} index={i} state={bar.state} />
      ))}
      <OrbitControls />
    </Canvas>
  )
}
```

### When to Use What

| Layer | Tool | Import |
|-------|------|--------|
| 2D HTML/CSS (UI, overlays, page transitions) | Framer Motion | `motion/react` |
| 3D objects (declarative: hover, click, state) | motion/three | `motion/three` |
| 3D objects (per-frame: continuous spin, physics sync) | useFrame | `@react-three/fiber` |
| 3D physics | cannon | `@react-three/cannon` |

**Use `motion/three` when:** state-driven animations (click → scale up, hover → glow). **Use `useFrame` when:** continuous per-frame animations (constant rotation, physics sync, particle updates).
