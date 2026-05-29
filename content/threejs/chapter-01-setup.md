# Chapter 1: Scene, Camera, Renderer

[← Overview](/blog/threejs/chapter-00-overview) | [Chapter 2: Geometries →](/blog/threejs/chapter-02-geometries)

---

## The Three Pillars

Every Three.js app needs exactly three things:

```
Scene    → the container (holds objects, lights)
Camera   → the viewpoint (what you see)
Renderer → the painter (draws to canvas)
```

## Step 1: Minimal Setup

```typescript
import * as THREE from "three";

// 1. Scene
const scene = new THREE.Scene();

// 2. Camera (FOV, aspect ratio, near clip, far clip)
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 5;

// 3. Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
```

## Step 2: Add a Cube

```typescript
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff88 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);
```

A `Mesh` = `Geometry` (shape) + `Material` (appearance).

## Step 3: The Render Loop

```typescript
function animate() {
  requestAnimationFrame(animate);

  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;

  renderer.render(scene, camera);
}
animate();
```

`requestAnimationFrame` runs at 60fps. Each frame we rotate the cube slightly and re-render.

## Step 4: Handle Resize

```typescript
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## Camera Types

| Type                 | Use Case                                    |
| -------------------- | ------------------------------------------- |
| `PerspectiveCamera`  | Realistic 3D (objects shrink with distance) |
| `OrthographicCamera` | 2D/isometric (no perspective distortion)    |

```typescript
// Orthographic (for 2D-style games)
const ortho = new THREE.OrthographicCamera(-5, 5, 5, -5, 0.1, 100);
```

## Coordinate System

```
        Y (up)
        |
        |
        |_______ X (right)
       /
      /
     Z (toward you)
```

## Next.js Integration

```tsx
"use client";
import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function ThreeScene() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      ref.current.clientWidth / ref.current.clientHeight,
      0.1,
      1000,
    );
    camera.position.z = 5;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(ref.current.clientWidth, ref.current.clientHeight);
    ref.current.appendChild(renderer.domElement);

    const cube = new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshNormalMaterial());
    scene.add(cube);

    const animate = () => {
      requestAnimationFrame(animate);
      cube.rotation.x += 0.01;
      cube.rotation.y += 0.01;
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      renderer.dispose();
      ref.current?.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={ref} className="h-[500px] w-full" />;
}
```

---

[Chapter 2: Geometries & Materials →](/blog/threejs/chapter-02-geometries)
