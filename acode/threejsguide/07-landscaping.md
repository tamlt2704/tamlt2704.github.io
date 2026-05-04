# Chapter 7: Landscaping

> **What you'll learn:** Environment maps, sky, fog, ground textures, and post-processing for a polished look.

### Environment Maps — Instant Realism

An environment map is a 360° image that wraps around your entire scene. It does two things:
1. **Background** — the sky/surroundings visible behind your objects
2. **Reflections** — objects reflect the environment, making materials look real

drei makes this trivial:

```tsx
import { Environment } from '@react-three/drei'

// Inside your Canvas:
<Environment preset="sunset" />
```

Available presets: `apartment`, `city`, `dawn`, `forest`, `lobby`, `night`, `park`, `studio`, `sunset`, `warehouse`.

To also use it as the scene background:

```tsx
<Environment preset="sunset" background />
```

This single line replaces the need for complex lighting setups. The environment map provides ambient light from all directions, making `meshStandardMaterial` and `meshPhysicalMaterial` look dramatically better.

### Sky Component

For a procedural sky (not an image):

```tsx
import { Sky } from '@react-three/drei'

<Sky
  sunPosition={[100, 20, 100]}
  turbidity={8}
  rayleigh={2}
/>
```

- `sunPosition` — where the sun is. Low Y = sunset, high Y = noon.
- `turbidity` — haziness. Higher = more haze.
- `rayleigh` — atmospheric scattering. Higher = more blue.

### Fog — Depth and Atmosphere

Fog fades distant objects, adding depth:

```tsx
<Canvas>
  <fog attach="fog" args={['#e0d5c0', 10, 50]} />
  {/* ... */}
</Canvas>
```

`args` = `[color, near, far]`. Objects closer than `near` are fully visible. Objects beyond `far` are fully fogged. Between them, it fades.

### Ground Texture

Replace the flat green ground with a textured one:

**`src/components/Ground.tsx`** (updated)
```tsx
'use client'

import { useTexture } from '@react-three/drei'
import { RepeatWrapping } from 'three'

export default function Ground() {
  const texture = useTexture('/textures/grass.jpg')
  texture.wrapS = texture.wrapT = RepeatWrapping
  texture.repeat.set(10, 10)

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]} receiveShadow>
      <planeGeometry args={[20, 20]} />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}
```

`RepeatWrapping` tiles the texture. `repeat.set(10, 10)` tiles it 10 times across the plane. Without this, one small image stretches across the entire ground and looks blurry.

> **Where to get textures:** [ambientCG](https://ambientcg.com) has free PBR textures (color, normal, roughness maps). For now, a simple grass photo works.

### Post-Processing — The Final 10%

Post-processing applies screen-space effects after the scene renders. Install:

```bash
npm install @react-three/postprocessing
```

```tsx
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'

// Inside Canvas:
<EffectComposer>
  <Bloom intensity={0.3} luminanceThreshold={0.8} />
  <Vignette darkness={0.4} />
</EffectComposer>
```

- **Bloom** — bright areas glow. The porch light will softly bleed light.
- **Vignette** — darkens edges of the screen. Subtle but adds focus.

Other useful effects:
- **DepthOfField** — blurs objects not at the focal distance
- **ChromaticAberration** — color fringing at edges (subtle = cinematic)
- **ToneMapping** — adjusts overall color/exposure

> **Warning:** Post-processing is expensive on mobile. Consider disabling it on low-end devices or making it optional.

### Putting It All Together

**`src/components/Scene.tsx`** (final version)
```tsx
'use client'

import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, Html, useProgress } from '@react-three/drei'
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'
import Ground from './Ground'
import House from './House'
import Lights from './Lights'
import Furniture from './Furniture'

function Loader() {
  const { progress } = useProgress()
  return <Html center><p style={{ color: 'white' }}>{Math.round(progress)}%</p></Html>
}

export default function Scene() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas shadows camera={{ position: [5, 3, 5], fov: 50 }}>
        <fog attach="fog" args={['#e0d5c0', 15, 50]} />
        <Lights />
        <Environment preset="sunset" background />
        <Ground />
        <House />
        <Suspense fallback={<Loader />}>
          <Furniture />
        </Suspense>
        <EffectComposer>
          <Bloom intensity={0.3} luminanceThreshold={0.8} />
          <Vignette darkness={0.3} />
        </EffectComposer>
        <OrbitControls
          maxPolarAngle={Math.PI / 2.1}
          minDistance={3}
          maxDistance={15}
        />
      </Canvas>
    </div>
  )
}
```

Note the `OrbitControls` constraints:
- `maxPolarAngle={Math.PI / 2.1}` — prevents the camera from going below the ground
- `minDistance={3}` / `maxDistance={15}` — limits zoom range

---

> **🏗 Progress:** The house is complete. Lit, furnished, landscaped, polished. One step left — show it to the world.

---

[← Chapter 6: Furniture](./06-furniture.md) | [Chapter 8: Open House →](./08-open-house.md)
