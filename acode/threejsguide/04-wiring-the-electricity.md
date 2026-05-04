# Chapter 4: Wiring the Electricity

> **What you'll learn:** Light types, shadows, and how lighting transforms a scene from flat to alive.

### Why Lighting Matters

Right now your house looks like a plastic toy under fluorescent office lights. That's because we only have `ambientLight` (flat, directionless) and a basic `directionalLight`. Lighting is the single biggest factor in making 3D look professional.

### Light Types

**Ambient Light** — Flat, everywhere, no direction. Like being inside a cloud. Use it to fill in shadows so they're not pitch black.
```tsx
<ambientLight intensity={0.3} color="#b0c4de" />
```

**Directional Light** — Parallel rays from infinitely far away. Like the sun. Has a position (which determines direction) but the rays don't spread out.
```tsx
<directionalLight position={[5, 8, 5]} intensity={1.5} />
```

**Point Light** — Radiates in all directions from a point. Like a light bulb. Has falloff (gets dimmer with distance).
```tsx
<pointLight position={[0, 3, 0]} intensity={1} distance={10} />
```

**Spot Light** — A cone of light from a point. Like a flashlight or stage light.
```tsx
<spotLight position={[0, 5, 0]} angle={0.3} penumbra={0.5} intensity={1} />
```
- `angle` — cone width (radians)
- `penumbra` — soft edge (0 = hard, 1 = fully soft)

### Adding Shadows

Shadows are **off by default** because they're expensive. You enable them in three places:

1. **The Canvas** — `shadows` prop
2. **The light** — `castShadow` prop
3. **Each object** — `castShadow` and/or `receiveShadow` props

Create a dedicated lights component:

**`src/components/Lights.tsx`**
```tsx
'use client'

export default function Lights() {
  return (
    <>
      {/* Soft ambient fill */}
      <ambientLight intensity={0.3} color="#b0c4de" />

      {/* Sun */}
      <directionalLight
        position={[5, 8, 5]}
        intensity={1.5}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={20}
        shadow-camera-left={-10}
        shadow-camera-right={10}
        shadow-camera-top={10}
        shadow-camera-bottom={-10}
      />

      {/* Warm porch light */}
      <pointLight
        position={[0, 2, 2]}
        intensity={0.8}
        color="#ffaa55"
        distance={5}
      />
    </>
  )
}
```

### Enable Shadows on Objects

Update your House and Ground to cast/receive shadows. Add `castShadow` and `receiveShadow` to each `<mesh>`:

```tsx
{/* Example: a wall that casts AND receives shadows */}
<mesh position={[0, 1, -1.45]} castShadow receiveShadow>
  <boxGeometry args={[3, 2, 0.1]} />
  <meshStandardMaterial color="#d4a574" />
</mesh>
```

The ground should only **receive** shadows (it doesn't cast them on anything):

```tsx
<mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]} receiveShadow>
  <planeGeometry args={[20, 20]} />
  <meshStandardMaterial color="#4a7c59" />
</mesh>
```

### Update the Scene

**`src/components/Scene.tsx`**
```tsx
'use client'

import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import Ground from './Ground'
import House from './House'
import Lights from './Lights'

export default function Scene() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas shadows camera={{ position: [5, 3, 5], fov: 50 }}>
        <Lights />
        <Ground />
        <House />
        <OrbitControls />
      </Canvas>
    </div>
  )
}
```

Note `shadows` on `<Canvas>`. Without it, all `castShadow`/`receiveShadow` props are ignored.

### Shadow Configuration Explained

```tsx
shadow-mapSize-width={2048}    // Shadow resolution. Higher = sharper, more expensive
shadow-camera-far={20}         // How far the shadow camera sees
shadow-camera-left={-10}       // Shadow camera frustum bounds
```

The directional light's shadow uses an orthographic camera internally. You're defining how large an area it covers. If your shadows are cut off, increase these bounds. If they're blurry, increase `mapSize`.

### The Lighting Recipe for Realism

A professional scene typically has:
1. **One dominant directional light** (the sun) — warm white, casts shadows
2. **Ambient light** — low intensity, slightly blue/cool to simulate sky bounce
3. **Fill/accent lights** — point or spot lights for warmth, mood, highlights
4. **Environment map** (Chapter 7) — the ultimate cheat for realistic reflections and ambient lighting

---

> **🏗 Progress:** The house has electricity. Shadows give it depth and grounding. But everything is static — next, we make it interactive.

---

[← Chapter 3: The Walls](./03-the-walls.md) | [Chapter 5: Doors & Windows →](./05-doors-and-windows.md)
