# Chapter 6: Furniture

> **What you'll learn:** Loading 3D models (GLTF/GLB), Suspense for async loading, and where to find free models.

### Why Load Models?

Building everything from primitives (boxes, spheres, cones) works for learning, but real projects use **3D models** — complex shapes made in Blender, Maya, or downloaded from asset libraries.

The standard format is **GLTF/GLB**:
- `.gltf` — JSON file + separate binary/texture files
- `.glb` — single binary file (everything packed together)

**Always use `.glb`** for web projects. One file, smaller, faster to load.

### Where to Get Free Models

| Source | Notes |
|---|---|
| [Poly Pizza](https://poly.pizza) | Free low-poly models, CC0 |
| [Sketchfab](https://sketchfab.com) | Huge library, filter by "downloadable" |
| [Kenney](https://kenney.nl) | Free game assets, great low-poly packs |
| [gltf.pmnd.rs](https://gltf.pmnd.rs) | Paste a GLB URL → get a React component |

For our house, download a simple chair or table model as `.glb` and place it in `public/models/`.

### Loading a Model with `useGLTF`

**`src/components/Furniture.tsx`**
```tsx
'use client'

import { useGLTF } from '@react-three/drei'

function Chair() {
  const { scene } = useGLTF('/models/chair.glb')
  return <primitive object={scene} position={[0, 0, 0]} scale={0.5} />
}

export default function Furniture() {
  return (
    <group>
      <Chair />
    </group>
  )
}
```

**`useGLTF`** returns the loaded GLTF data. The `scene` property is the root Three.js object containing all meshes, materials, and animations from the file.

**`<primitive object={...} />`** is R3F's escape hatch — it takes an existing Three.js object and puts it in the scene graph. You can still apply `position`, `rotation`, `scale` as props.

### The basePath Problem with Models

Remember from setup: on GitHub Pages, your site lives at `/repo-name/`. Model paths must account for this.

```tsx
// ❌ Breaks on GitHub Pages
useGLTF('/models/chair.glb')

// ✅ Works everywhere
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || ''
useGLTF(`${basePath}/models/chair.glb`)
```

Set this in your `.env.local`:
```
NEXT_PUBLIC_BASE_PATH=
```

And in `.env.production`:
```
NEXT_PUBLIC_BASE_PATH=/my-3d-house
```

### Suspense — Handling Loading States

Models take time to download. React's `<Suspense>` handles this:

**`src/components/Scene.tsx`** (updated)
```tsx
'use client'

import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import Ground from './Ground'
import House from './House'
import Lights from './Lights'
import Furniture from './Furniture'

function Loader() {
  return (
    <mesh>
      <sphereGeometry args={[0.3, 16, 16]} />
      <meshBasicMaterial color="white" wireframe />
    </mesh>
  )
}

export default function Scene() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas shadows camera={{ position: [5, 3, 5], fov: 50 }}>
        <Lights />
        <Ground />
        <House />
        <Suspense fallback={<Loader />}>
          <Furniture />
        </Suspense>
        <OrbitControls />
      </Canvas>
    </div>
  )
}
```

While the model downloads, a wireframe sphere shows. When it's ready, the furniture appears. No loading state management needed — Suspense handles it.

### HTML Loading Screen with drei

For a more polished loading experience, drei provides `useProgress`:

```tsx
import { Html, useProgress } from '@react-three/drei'

function Loader() {
  const { progress } = useProgress()
  return <Html center>{Math.round(progress)}%</Html>
}
```

`<Html>` renders actual HTML/CSS inside the 3D scene, always facing the camera. `useProgress` tracks all asset loading progress.

### Preloading Models

To start loading before the component mounts:

```tsx
useGLTF.preload('/models/chair.glb')
```

Put this at the module level (outside the component). The model starts downloading immediately when the JS file is parsed, not when the component first renders.

### Optimizing Models for the Web

Before deploying, optimize your `.glb` files:

1. **Reduce polygon count** — Use Blender's Decimate modifier. A chair doesn't need 50,000 triangles. 2,000-5,000 is usually enough.
2. **Compress with Draco** — `npx gltf-pipeline -i model.glb -o model-draco.glb -d` reduces file size 60-90%.
3. **Compress textures** — Convert to `.webp` or use KTX2/Basis format. A 4MB PNG texture becomes 200KB.
4. **Use `gltf.pmnd.rs`** — Paste your model URL and it generates an optimized React component with proper typing.

### Enabling Draco Decoding

If your model uses Draco compression, tell `useGLTF` where to find the decoder:

```tsx
import { useGLTF } from '@react-three/drei'

function Chair() {
  const { scene } = useGLTF('/models/chair-draco.glb')
  return <primitive object={scene} scale={0.5} />
}

// Use the CDN-hosted decoder
useGLTF.preload('/models/chair-draco.glb')
```

drei's `useGLTF` automatically handles Draco decoding using a CDN-hosted decoder by default. No extra setup needed.

---

> **🏗 Progress:** The house has furniture. Real 3D models loaded from files. Next, we'll add the environment — sky, ground texture, and final polish.

---

[← Chapter 5: Doors & Windows](./05-doors-and-windows.md) | [Chapter 7: Landscaping →](./07-landscaping.md)
