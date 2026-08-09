# Chapter 31: Three.js in Next.js — 3D on the Web with React

## What you'll learn

- Why Three.js needs special handling in Next.js (SSR vs browser APIs)
- Setting up React Three Fiber (R3F) in Next.js App Router
- Building interactive 3D scenes as React components
- Loading 3D models (GLTF/GLB)
- Post-processing effects (bloom, depth of field)
- Scroll-driven 3D animations
- Performance: lazy loading, LOD, instancing
- Build: a 3D product showcase page and an interactive portfolio hero

---

## PART 1: Setup & Fundamentals

## 31.1 The Next.js + Three.js challenge

Three.js uses browser APIs (`window`, `document`, `WebGL`, `requestAnimationFrame`). Next.js renders on the server first (SSR) where these don't exist.

**Solutions:**
1. Mark components as `"use client"` — they only hydrate on the browser
2. Use `dynamic()` import with `ssr: false` — skip server rendering entirely
3. React Three Fiber handles this gracefully with its `<Canvas>` component

## 31.2 Install dependencies

```bash
npm install three @react-three/fiber @react-three/drei
npm install -D @types/three
```

| Package | Purpose |
|---------|---------|
| `three` | The 3D engine |
| `@react-three/fiber` | React renderer for Three.js (declarative JSX) |
| `@react-three/drei` | Pre-built helpers (controls, loaders, effects, text, HTML overlays) |

## 31.3 Your first 3D scene in Next.js

Create `app/3d-demo/page.tsx`:

```tsx
import dynamic from "next/dynamic";

// Dynamic import with SSR disabled — Canvas uses WebGL (browser only)
const Scene = dynamic(() => import("@/components/3d/Scene"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] bg-gray-900 rounded-xl flex items-center justify-center">
      <p className="text-gray-400">Loading 3D scene...</p>
    </div>
  ),
});

export default function ThreeDemoPage() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-6">3D Demo</h1>
      <Scene />
    </div>
  );
}
```

Create `components/3d/Scene.tsx`:

```tsx
"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";

function RotatingBox() {
  return (
    <mesh rotation={[0.5, 0.5, 0]}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#3b82f6" metalness={0.5} roughness={0.3} />
    </mesh>
  );
}

export default function Scene() {
  return (
    <div className="w-full h-[600px] rounded-xl overflow-hidden">
      <Canvas camera={{ position: [4, 3, 5], fov: 50 }}>
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} />

        {/* Objects */}
        <RotatingBox />

        {/* Ground */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.5, 0]}>
          <planeGeometry args={[20, 20]} />
          <meshStandardMaterial color="#1e293b" />
        </mesh>

        {/* Controls */}
        <OrbitControls enableDamping />

        {/* Environment map (realistic reflections) */}
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}
```

**Why `dynamic` + `ssr: false`?**
- `<Canvas>` creates a WebGL context → crashes on the server
- `dynamic(() => import(...), { ssr: false })` ensures the component only loads in the browser
- The `loading` prop shows a placeholder during the async load

## 31.4 Animation with `useFrame`

```tsx
"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

function SpinningTorus() {
  const meshRef = useRef<THREE.Mesh>(null);

  // Runs every frame (~60fps)
  useFrame((state, delta) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.x += delta * 0.5;
    meshRef.current.rotation.y += delta * 0.3;
  });

  return (
    <mesh ref={meshRef}>
      <torusGeometry args={[1, 0.4, 32, 64]} />
      <meshStandardMaterial color="#8b5cf6" metalness={0.8} roughness={0.2} />
    </mesh>
  );
}
```

**`useFrame` callback parameters:**
- `state` — access to clock, camera, scene, pointer position, viewport size
- `delta` — time since last frame (use for frame-rate-independent animation)

```tsx
useFrame((state) => {
  // Animate based on clock (smooth oscillation)
  meshRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.5;

  // React to mouse position
  meshRef.current.rotation.y = state.pointer.x * Math.PI;
});
```

## 31.5 Responsive canvas

```tsx
<div className="w-full h-[50vh] md:h-[70vh]">
  <Canvas
    camera={{ position: [0, 2, 5], fov: 50 }}
    dpr={[1, 2]}       // device pixel ratio: min 1, max 2 (retina)
    gl={{ antialias: true, alpha: true }}  // transparent background
  >
    {/* ... */}
  </Canvas>
</div>
```

The `<Canvas>` fills its parent container. Control size with the parent `<div>` using Tailwind classes. The canvas auto-resizes on window resize.

---

## PART 2: Interactive Components

## 31.6 Click, hover, and pointer events

```tsx
"use client";

import { useState } from "react";

function InteractiveBox() {
  const [hovered, setHovered] = useState(false);
  const [clicked, setClicked] = useState(false);

  return (
    <mesh
      scale={clicked ? 1.5 : 1}
      onClick={() => setClicked(!clicked)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={hovered ? "#f59e0b" : "#3b82f6"} />
    </mesh>
  );
}
```

R3F gives you React event handlers directly on 3D objects — no raycasting code needed.

**Available events:**
| Event | Fires when |
|-------|-----------|
| `onClick` | Object is clicked |
| `onDoubleClick` | Object is double-clicked |
| `onPointerOver` | Mouse enters object |
| `onPointerOut` | Mouse leaves object |
| `onPointerDown` | Mouse button pressed on object |
| `onPointerUp` | Mouse button released on object |
| `onPointerMove` | Mouse moves over object |

## 31.7 HTML overlays in 3D space

```tsx
import { Html } from "@react-three/drei";

function AnnotatedObject() {
  return (
    <group>
      <mesh>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial color="#22c55e" />
      </mesh>

      {/* HTML element positioned in 3D space */}
      <Html position={[0, 1.5, 0]} center>
        <div className="bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full shadow-lg text-sm font-medium">
          Interactive Globe 🌍
        </div>
      </Html>
    </group>
  );
}
```

`<Html>` from `drei` renders a regular DOM element that follows a 3D position. Style it with normal Tailwind. It always faces the camera.

## 31.8 Camera controls options

```tsx
import { OrbitControls, PresentationControls, ScrollControls } from "@react-three/drei";

// Free orbit (user rotates/zooms freely)
<OrbitControls enableDamping dampingFactor={0.05} />

// Constrained (product showcase — limited rotation)
<OrbitControls
  enableZoom={false}
  minPolarAngle={Math.PI / 4}    // can't look from below
  maxPolarAngle={Math.PI / 2}    // can't look from top
  autoRotate                      // slowly spins
  autoRotateSpeed={1}
/>

// Presentation (spring-based drag — snaps back)
<PresentationControls
  global
  rotation={[0.1, 0.2, 0]}
  polar={[-0.2, 0.2]}       // vertical clamp
  azimuth={[-0.5, 0.5]}     // horizontal clamp
  speed={2}
>
  <MyModel />
</PresentationControls>
```

---

## PART 3: Loading 3D Models

## 31.9 Loading GLTF/GLB models

```tsx
"use client";

import { useGLTF } from "@react-three/drei";

function Laptop() {
  const { scene } = useGLTF("/models/laptop.glb");

  return <primitive object={scene} scale={0.5} position={[0, -1, 0]} />;
}

// Preload for instant display (no loading flash)
useGLTF.preload("/models/laptop.glb");
```

**Where to get models:**
- [Sketchfab](https://sketchfab.com) — free and paid models
- [poly.pizza](https://poly.pizza) — free low-poly models
- [gltf-viewer](https://gltf-viewer.donmccurdy.com) — preview/inspect GLTF files
- Export from Blender as `.glb` (binary GLTF — smaller file size)

Place models in `public/models/` — Next.js serves static files from `public/`.

## 31.10 Model with animations

```tsx
"use client";

import { useGLTF, useAnimations } from "@react-three/drei";
import { useEffect } from "react";

function AnimatedCharacter() {
  const { scene, animations } = useGLTF("/models/character.glb");
  const { actions } = useAnimations(animations, scene);

  useEffect(() => {
    // Play the "idle" animation on load
    actions["idle"]?.play();
  }, [actions]);

  return <primitive object={scene} scale={1} />;
}
```

## 31.11 Loading with Suspense

```tsx
import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";

function HeavyModel() {
  const { scene } = useGLTF("/models/detailed-car.glb"); // 5MB model
  return <primitive object={scene} />;
}

export default function Scene() {
  return (
    <Canvas>
      <Suspense fallback={<LoadingSpinner />}>
        <HeavyModel />
      </Suspense>
      <OrbitControls />
      <Environment preset="sunset" />
    </Canvas>
  );
}

// 3D loading indicator (renders inside the Canvas)
function LoadingSpinner() {
  const meshRef = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (meshRef.current) meshRef.current.rotation.y += delta * 2;
  });

  return (
    <mesh ref={meshRef}>
      <torusGeometry args={[0.5, 0.1, 16, 32]} />
      <meshBasicMaterial color="#6366f1" wireframe />
    </mesh>
  );
}
```

---

## PART 4: Build — Product Showcase Page

## 31.12 3D product card

```tsx
"use client";

import { Canvas } from "@react-three/fiber";
import { PresentationControls, Environment, ContactShadows } from "@react-three/drei";

function ProductModel() {
  return (
    <mesh castShadow>
      <cylinderGeometry args={[0.8, 0.8, 0.1, 64]} />
      <meshPhysicalMaterial
        color="#1e293b"
        metalness={0.9}
        roughness={0.1}
        clearcoat={1}
        clearcoatRoughness={0.1}
      />
    </mesh>
  );
}

export default function ProductCard() {
  return (
    <div className="w-full max-w-md mx-auto">
      {/* 3D viewer */}
      <div className="h-[400px] bg-gradient-to-b from-gray-100 to-gray-200 rounded-t-2xl overflow-hidden">
        <Canvas camera={{ position: [0, 2, 4], fov: 35 }}>
          <ambientLight intensity={0.5} />
          <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />

          <PresentationControls
            global
            rotation={[0.1, 0.2, 0]}
            polar={[-0.1, 0.3]}
            azimuth={[-0.5, 0.5]}
            speed={2}
          >
            <ProductModel />
          </PresentationControls>

          <ContactShadows position={[0, -0.5, 0]} opacity={0.5} blur={2} />
          <Environment preset="studio" />
        </Canvas>
      </div>

      {/* Product info */}
      <div className="bg-white p-6 rounded-b-2xl border border-t-0 border-gray-200">
        <h3 className="text-lg font-semibold">Premium Widget Pro</h3>
        <p className="text-sm text-gray-600 mt-1">
          Drag to rotate. Crafted from aerospace-grade materials.
        </p>
        <div className="flex items-center justify-between mt-4">
          <span className="text-2xl font-bold">$299</span>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
}
```

## 31.13 Scroll-driven 3D animation

```tsx
"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { ScrollControls, useScroll } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

function ScrollScene() {
  const meshRef = useRef<THREE.Group>(null);
  const scroll = useScroll();

  useFrame(() => {
    if (!meshRef.current) return;
    const offset = scroll.offset; // 0 at top, 1 at bottom

    // Rotate based on scroll
    meshRef.current.rotation.y = offset * Math.PI * 4;

    // Move along path
    meshRef.current.position.y = Math.sin(offset * Math.PI) * 2;
    meshRef.current.position.x = Math.cos(offset * Math.PI * 2) * 2;

    // Scale up in the middle of the page
    const scale = 1 + Math.sin(offset * Math.PI) * 0.5;
    meshRef.current.scale.setScalar(scale);
  });

  return (
    <group ref={meshRef}>
      <mesh>
        <icosahedronGeometry args={[1, 1]} />
        <meshStandardMaterial color="#8b5cf6" flatShading />
      </mesh>
    </group>
  );
}

export default function ScrollPage() {
  return (
    <div className="h-[400vh]"> {/* Tall page for scrolling */}
      <div className="fixed inset-0 -z-10"> {/* 3D scene fills viewport */}
        <Canvas camera={{ position: [0, 0, 5] }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[5, 5, 5]} />

          <ScrollControls pages={4} damping={0.3}>
            <ScrollScene />
          </ScrollControls>

          <Environment preset="night" />
        </Canvas>
      </div>

      {/* HTML content scrolls over the 3D scene */}
      <div className="relative z-10 pointer-events-none">
        <section className="h-screen flex items-center justify-center">
          <h1 className="text-5xl font-bold text-white pointer-events-auto">
            Scroll Down ↓
          </h1>
        </section>
        <section className="h-screen flex items-center justify-center">
          <p className="text-2xl text-white/80 max-w-md text-center pointer-events-auto">
            The 3D object reacts to your scroll position
          </p>
        </section>
      </div>
    </div>
  );
}
```

---

## PART 5: Performance & Production

## 31.14 Performance optimisation

| Technique | When to use | How |
|-----------|-------------|-----|
| `frameloop="demand"` | Static scenes (no animation) | Only renders when something changes |
| `dpr={[1, 2]}` | Mobile devices | Limits pixel ratio to save GPU |
| Instancing | Many identical objects (100+) | `<Instances>` renders one draw call |
| LOD (Level of Detail) | Objects at varying distances | `<Lod>` swaps geometry by distance |
| Lazy loading | Heavy models | `dynamic()` + Suspense |
| Texture compression | Large textures | Use KTX2 / Basis compressed textures |
| Dispose | Component unmount | Three.js resources don't auto-GC |

```tsx
// Only render when state changes (saves battery on static displays)
<Canvas frameloop="demand">

// Instancing — 1000 boxes in one draw call
import { Instances, Instance } from "@react-three/drei";

function ManyBoxes() {
  return (
    <Instances limit={1000}>
      <boxGeometry />
      <meshStandardMaterial />
      {positions.map((pos, i) => (
        <Instance key={i} position={pos} color={colors[i]} />
      ))}
    </Instances>
  );
}

// Level of Detail
import { Lod } from "@react-three/drei";

<Lod distances={[0, 20, 50]}>
  <HighDetailModel />   {/* shown when camera < 20 units away */}
  <MediumDetailModel /> {/* shown 20-50 units */}
  <LowDetailModel />    {/* shown > 50 units */}
</Lod>
```

## 31.15 Post-processing effects

```bash
npm install @react-three/postprocessing
```

```tsx
import { EffectComposer, Bloom, DepthOfField, Vignette } from "@react-three/postprocessing";

export default function Scene() {
  return (
    <Canvas>
      {/* ... scene content ... */}

      <EffectComposer>
        <Bloom luminanceThreshold={0.5} luminanceSmoothing={0.9} intensity={0.5} />
        <Vignette eskil={false} offset={0.1} darkness={0.5} />
        <DepthOfField focusDistance={0.01} focalLength={0.02} bokehScale={3} />
      </EffectComposer>
    </Canvas>
  );
}
```

## 31.16 Next.js-specific patterns

**1. Separate 3D into a dedicated component file:**
```
components/
  3d/
    Scene.tsx          ← "use client" + Canvas
    ProductModel.tsx   ← Model loading
    Effects.tsx        ← Post-processing
```

**2. Always use `dynamic` at the page level:**
```tsx
// app/page.tsx (server component)
const Hero3D = dynamic(() => import("@/components/3d/Hero3D"), { ssr: false });
```

**3. Preload models on route prefetch:**
```tsx
"use client";
import { useGLTF } from "@react-three/drei";

// Call at module level — preloads when this component's JS chunk loads
useGLTF.preload("/models/product.glb");
```

**4. Fallback for non-WebGL browsers:**
```tsx
function Scene() {
  return (
    <Canvas
      fallback={
        <div className="w-full h-full flex items-center justify-center bg-gray-900">
          <img src="/images/product-fallback.png" alt="Product" />
        </div>
      }
    >
      {/* 3D content */}
    </Canvas>
  );
}
```

---

## Summary

✅ Set up React Three Fiber in Next.js with `dynamic()` and `ssr: false`
✅ Build animated scenes with `useFrame` (frame-rate-independent with delta)
✅ Handle interaction: click, hover, pointer events directly on meshes
✅ Load GLTF/GLB models with `useGLTF` and Suspense fallbacks
✅ HTML overlays in 3D space with `<Html>` from drei
✅ Camera controls: OrbitControls, PresentationControls, ScrollControls
✅ Scroll-driven animation (3D reacts to scroll position)
✅ Product showcase with `PresentationControls` + `ContactShadows` + `Environment`
✅ Performance: `frameloop="demand"`, instancing, LOD, lazy loading
✅ Post-processing: Bloom, Vignette, Depth of Field

## Key takeaways

**`"use client"` + `dynamic(ssr: false)` is the Next.js pattern for Three.js.** The 3D scene can't render on the server — it needs WebGL. Isolate it in a client component and lazy-load it.

**React Three Fiber makes Three.js declarative.** Meshes are JSX elements. Events are React props. State drives renders. You think in React, not in imperative Three.js. The mental model is identical to building 2D UIs.

**`@react-three/drei` eliminates boilerplate.** OrbitControls, Environment, useGLTF, Html, ContactShadows, ScrollControls — these would each be 50-100 lines of imperative Three.js. Drei gives them as one-liner components.

**Performance scales differently in 3D.** One draw call with 1000 instances beats 1000 individual meshes. GPU bottleneck is different from CPU bottleneck. Profile with Chrome DevTools → Performance → GPU, not just React DevTools.

---

→ [Back to Chapter 30: Docker](./30-DOCKER.md)
