# Chapter 8: React Three Fiber

[← Chapter 7: Shaders](/blog/threejs/chapter-07-shaders) | [Overview](/blog/threejs/chapter-00-overview)

---

## What is React Three Fiber (R3F)?

A React renderer for Three.js. Write 3D scenes as JSX components — declarative, composable, and integrated with React's ecosystem.

```bash
npm install @react-three/fiber @react-three/drei
```

## Hello World

```tsx
"use client";
import { Canvas } from "@react-three/fiber";

export default function Scene() {
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} />
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="hotpink" />
      </mesh>
    </Canvas>
  );
}
```

That's it. No manual scene/renderer setup. No cleanup. React handles it.

## Animation with useFrame

```tsx
import { useFrame } from "@react-three/fiber";
import { useRef } from "react";

function SpinningBox() {
  const ref = useRef<THREE.Mesh>(null!);

  useFrame((state, delta) => {
    ref.current.rotation.x += delta;
    ref.current.rotation.y += delta * 0.5;
  });

  return (
    <mesh ref={ref}>
      <boxGeometry />
      <meshNormalMaterial />
    </mesh>
  );
}
```

## Drei Helpers (Batteries Included)

```tsx
import { OrbitControls, Environment, Text, Float } from "@react-three/drei";

function Scene() {
  return (
    <Canvas>
      <OrbitControls enableDamping />
      <Environment preset="sunset" />
      <Float speed={2} floatIntensity={1}>
        <Text fontSize={1} color="white">
          Hello 3D
        </Text>
      </Float>
    </Canvas>
  );
}
```

Common Drei helpers:

| Helper            | Purpose                   |
| ----------------- | ------------------------- |
| `OrbitControls`   | Mouse camera control      |
| `Environment`     | HDR lighting presets      |
| `Text` / `Text3D` | 3D text rendering         |
| `Float`           | Floating animation        |
| `Stars`           | Starfield background      |
| `useGLTF`         | Load 3D models            |
| `Html`            | HTML overlays in 3D space |
| `ContactShadows`  | Soft ground shadows       |

## Loading Models

```tsx
import { useGLTF } from "@react-three/drei";

function Character() {
  const { scene } = useGLTF("/models/character.glb");
  return <primitive object={scene} scale={0.5} />;
}

// Preload for instant display
useGLTF.preload("/models/character.glb");
```

## Interaction (Click, Hover)

```tsx
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
      <boxGeometry />
      <meshStandardMaterial color={hovered ? "hotpink" : "orange"} />
    </mesh>
  );
}
```

## Physics with @react-three/rapier

```tsx
import { Physics, RigidBody } from "@react-three/rapier";

function PhysicsScene() {
  return (
    <Canvas>
      <Physics>
        {/* Falling box */}
        <RigidBody>
          <mesh position={[0, 5, 0]}>
            <boxGeometry />
            <meshStandardMaterial color="red" />
          </mesh>
        </RigidBody>

        {/* Static floor */}
        <RigidBody type="fixed">
          <mesh position={[0, -1, 0]}>
            <boxGeometry args={[20, 0.5, 20]} />
            <meshStandardMaterial color="gray" />
          </mesh>
        </RigidBody>
      </Physics>
    </Canvas>
  );
}
```

## Performance Tips

```tsx
// 1. Instancing (thousands of same object)
import { Instances, Instance } from "@react-three/drei";

<Instances limit={1000}>
  <boxGeometry />
  <meshStandardMaterial />
  {positions.map((pos, i) => <Instance key={i} position={pos} />)}
</Instances>

// 2. Level of Detail
import { Detailed } from "@react-three/drei";

<Detailed distances={[0, 10, 50]}>
  <HighPolyModel />   {/* close */}
  <MedPolyModel />    {/* medium */}
  <LowPolyModel />    {/* far */}
</Detailed>

// 3. Suspense for loading
<Suspense fallback={<LoadingSpinner />}>
  <HeavyModel />
</Suspense>
```

## R3F vs Vanilla Three.js

| Aspect    | Vanilla            | R3F                        |
| --------- | ------------------ | -------------------------- |
| Setup     | Manual (20+ lines) | `<Canvas>` (1 line)        |
| Cleanup   | Manual dispose     | Automatic                  |
| State     | External variables | React state/refs           |
| Animation | Manual rAF         | `useFrame` hook            |
| Events    | Raycaster setup    | `onClick`, `onPointerOver` |
| Ecosystem | npm packages       | React components           |

---

You now have a complete Three.js toolkit — from raw WebGL concepts to production React components.

[← Overview](/blog/threejs/chapter-00-overview)
