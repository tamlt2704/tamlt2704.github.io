# Chapter 18: Three.js — Real 3D in the Browser

## What you'll learn

- The Three.js scene graph: Scene, Camera, Renderer
- How to set up Three.js in a Next.js React component
- Geometry, materials, and meshes
- Lighting and shadows
- Camera controls (OrbitControls)
- Animation loop with `requestAnimationFrame`
- Building a 3D bar chart and 3D grid for algorithm visualisation
- Performance: when to use Three.js vs SVG/Canvas

---

## PART 1: Three.js Fundamentals

## 18.1 What is Three.js?

Three.js is a JavaScript library that wraps WebGL — the browser's GPU-accelerated 3D API. Without Three.js, drawing a single triangle in WebGL requires ~100 lines of shader code. Three.js gives you objects, lights, cameras, and materials in a high-level API.

| Technology | Rendering | 3D? | Performance | Complexity |
|------------|-----------|-----|-------------|------------|
| SVG + D3 | DOM elements | 2D (fake 3D with isometric) | Good for < 1000 elements | Low |
| Canvas 2D | Pixel buffer | 2D | Good for many elements | Medium |
| Three.js / WebGL | GPU shader | Real 3D | Handles millions of triangles | Higher |

**Use Three.js when:**
- You need real 3D rotation/perspective (not isometric faking)
- You have complex scenes (1000+ objects)
- You want physically-based materials, lighting, shadows
- You're building something interactive (rotate, zoom, pick objects)

**Don't use Three.js when:**
- A 2D chart is clearer (bar charts, line charts)
- You have < 50 elements (SVG is simpler)
- You need text-heavy visualisations (text in 3D is hard)

## 18.2 Install Three.js

```bash
npm install three @types/three
```

## 18.3 The Three.js mental model

Every Three.js app has three core objects:

```
┌─────────────────────────────────────┐
│              SCENE                   │  ← Container for all objects
│                                     │
│   ┌──────┐  ┌──────┐  ┌───────┐   │
│   │ Mesh │  │ Mesh │  │ Light │   │  ← Things in the scene
│   └──────┘  └──────┘  └───────┘   │
│                                     │
└─────────────────────────────────────┘
         │
         ▼ viewed by
┌──────────────┐
│    CAMERA    │  ← Where you're looking from
└──────────────┘
         │
         ▼ drawn by
┌──────────────┐
│   RENDERER   │  ← Draws the scene to a <canvas>
└──────────────┘
```

A **Mesh** = Geometry (shape) + Material (appearance):

```
Mesh = Geometry + Material
       ┌─────────────────┐
       │ BoxGeometry      │  ← The shape (vertices, faces)
       │ (width, height,  │
       │  depth)          │
       └─────────────────┘
              +
       ┌─────────────────┐
       │ MeshStandard-   │  ← How it looks (colour, shininess)
       │ Material         │
       │ (color, metalness│
       │  roughness)      │
       └─────────────────┘
```

## 18.4 Basic Three.js setup in React

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function ThreeScene() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    // 1. Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8fafc); // light grey

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(
      75,              // field of view (degrees)
      width / height,  // aspect ratio
      0.1,             // near clipping plane
      1000             // far clipping plane
    );
    camera.position.set(5, 5, 5);   // position the camera
    camera.lookAt(0, 0, 0);          // look at the center

    // 3. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);

    // 4. Add a cube
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshStandardMaterial({ color: 0x3b82f6 });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    // 5. Add light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 10, 7);
    scene.add(directionalLight);

    // 6. Animation loop
    function animate() {
      requestAnimationFrame(animate);
      cube.rotation.y += 0.01;
      renderer.render(scene, camera);
    }
    animate();

    // 7. Cleanup
    return () => {
      renderer.dispose();
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={containerRef} className="w-full h-[500px]" />;
}
```

**What each part does:**

| Part | Purpose |
|------|---------|
| `Scene` | Container. Everything you want to render goes in here. |
| `PerspectiveCamera(75, aspect, 0.1, 1000)` | Human-like perspective. FOV=75° is natural. |
| `WebGLRenderer` | Creates a `<canvas>` element, draws using GPU |
| `BoxGeometry(1, 1, 1)` | A 1×1×1 cube shape |
| `MeshStandardMaterial` | Physically-based material that responds to light |
| `AmbientLight` | Fills shadows with soft light (otherwise dark side is black) |
| `DirectionalLight` | Like the sun — parallel rays from one direction |
| `requestAnimationFrame` | Calls your render function 60 times/second |

## 18.5 Geometries — built-in shapes

```ts
// Box (cube, rectangular prism)
new THREE.BoxGeometry(width, height, depth)

// Sphere
new THREE.SphereGeometry(radius, widthSegments, heightSegments)

// Cylinder / cone
new THREE.CylinderGeometry(topRadius, bottomRadius, height, radialSegments)

// Plane (flat surface)
new THREE.PlaneGeometry(width, height)

// Torus (donut)
new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments)

// Ring
new THREE.RingGeometry(innerRadius, outerRadius, segments)

// Custom from vertices (for complex shapes)
new THREE.BufferGeometry()
```

## 18.6 Materials — how things look

| Material | Responds to light? | Look | Performance |
|----------|--------------------|----|-------------|
| `MeshBasicMaterial` | No | Flat colour, no shading | Fastest |
| `MeshLambertMaterial` | Yes | Matte, diffuse (like paper) | Fast |
| `MeshPhongMaterial` | Yes | Shiny highlights (like plastic) | Medium |
| `MeshStandardMaterial` | Yes | Physically-based (realistic) | Slower |
| `MeshPhysicalMaterial` | Yes | Clearcoat, transmission, subsurface | Slowest |

For algorithm visualisation, `MeshStandardMaterial` is the sweet spot:

```ts
new THREE.MeshStandardMaterial({
  color: 0x3b82f6,      // hex colour
  metalness: 0.1,       // 0 = plastic, 1 = metal
  roughness: 0.7,       // 0 = mirror, 1 = matte
  transparent: true,    // enable opacity
  opacity: 0.9,         // 0 = invisible, 1 = solid
})
```

## 18.7 Lighting — making things visible

Without light, `MeshStandardMaterial` appears completely black. You need at least one light source.

```ts
// Ambient — fills everywhere equally (no shadows)
new THREE.AmbientLight(color, intensity)

// Directional — parallel rays (sun-like)
const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(10, 20, 10);

// Point — radiates from a point (light bulb)
new THREE.PointLight(color, intensity, distance)

// Hemisphere — sky colour from above, ground colour from below
new THREE.HemisphereLight(skyColor, groundColor, intensity)
```

**Recipe for good-looking algorithm visualisation:**

```ts
// Soft ambient fill
scene.add(new THREE.AmbientLight(0xffffff, 0.6));

// Main directional light (casts shadows)
const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
mainLight.position.set(5, 10, 7);
scene.add(mainLight);

// Secondary fill (reduces harsh shadows)
const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
fillLight.position.set(-5, 5, -5);
scene.add(fillLight);
```



---

## PART 2: Interactivity and Data Visualisation

## 18.8 OrbitControls — rotate, zoom, pan

Let users rotate the scene with mouse/touch:

```bash
# OrbitControls ships with Three.js (no extra install)
```

```tsx
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

// After creating camera and renderer:
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;   // smooth deceleration
controls.dampingFactor = 0.05;
controls.minDistance = 3;        // don't zoom too close
controls.maxDistance = 20;       // don't zoom too far
controls.maxPolarAngle = Math.PI / 2; // don't go below ground

// In animation loop:
function animate() {
  requestAnimationFrame(animate);
  controls.update();  // REQUIRED for damping
  renderer.render(scene, camera);
}
```

Now users can:
- **Left-click + drag** — rotate
- **Scroll wheel** — zoom
- **Right-click + drag** — pan

## 18.9 3D Bar Chart

Build a 3D version of your sorting visualisation:

```tsx
"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

type ThreeBarChartProps = {
  data: number[];
  highlightIndices?: number[];
};

export default function ThreeBarChart({ data, highlightIndices = [] }: ThreeBarChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<{
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    renderer: THREE.WebGLRenderer;
    bars: THREE.Mesh[];
  } | null>(null);

  // Setup (once)
  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1e293b); // dark slate

    // Camera
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    camera.position.set(8, 6, 8);
    camera.lookAt(0, 0, 0);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.target.set(0, 1, 0);

    // Lighting
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    const dirLight = new THREE.DirectionalLight(0xffffff, 1);
    dirLight.position.set(5, 10, 5);
    dirLight.castShadow = true;
    scene.add(dirLight);

    // Ground plane
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(20, 20),
      new THREE.MeshStandardMaterial({ color: 0x334155 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grid helper (visual reference)
    const grid = new THREE.GridHelper(20, 20, 0x475569, 0x475569);
    grid.position.y = 0.01;
    scene.add(grid);

    // Store refs
    sceneRef.current = { scene, camera, renderer, bars: [] };

    // Animate
    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // Resize handling
    function handleResize() {
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, []);

  // Update bars when data changes
  useEffect(() => {
    if (!sceneRef.current) return;
    const { scene, bars } = sceneRef.current;

    // Remove old bars
    bars.forEach((bar) => scene.remove(bar));
    bars.length = 0;

    const maxVal = Math.max(...data);
    const barWidth = 0.6;
    const spacing = 1.0;
    const offsetX = -(data.length * spacing) / 2;

    data.forEach((value, index) => {
      const height = (value / maxVal) * 5; // max height = 5 units
      const isHighlighted = highlightIndices.includes(index);

      const geometry = new THREE.BoxGeometry(barWidth, height, barWidth);
      const material = new THREE.MeshStandardMaterial({
        color: isHighlighted ? 0xf59e0b : 0x3b82f6,
        metalness: 0.2,
        roughness: 0.6,
      });

      const bar = new THREE.Mesh(geometry, material);
      bar.position.set(
        offsetX + index * spacing,
        height / 2,  // pivot at base (not center)
        0
      );
      bar.castShadow = true;

      scene.add(bar);
      bars.push(bar);
    });

    sceneRef.current.bars = bars;
  }, [data, highlightIndices]);

  return <div ref={containerRef} className="w-full h-[500px] rounded-lg overflow-hidden" />;
}
```

**Key patterns:**
- **Separate setup from data update** — setup runs once (camera, lights, renderer); data effect runs when `data` changes
- **`height / 2` for y-position** — Three.js positions from center, so half-height lifts the base to y=0
- **`castShadow` / `receiveShadow`** — enable shadows per-object (ground receives, bars cast)
- **Resize handler** — recalculates aspect ratio when window resizes

## 18.10 3D Grid (for DP tables / matrix visualisation)

```tsx
function ThreeGrid({
  cells,
  rows,
  cols,
  currentCell,
}: {
  cells: { row: number; col: number; value: number; state: string }[];
  rows: number;
  cols: number;
  currentCell?: [number, number] | null;
}) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const container = containerRef.current;
    // ... standard scene setup (same as 18.9) ...

    // Camera positioned for top-down angled view
    camera.position.set(cols / 2, Math.max(rows, cols) * 1.2, rows);
    camera.lookAt(cols / 2, 0, rows / 2);

    // Draw cells as extruded blocks
    const maxVal = Math.max(...cells.map(c => c.value), 1);

    cells.forEach((cell) => {
      const height = (cell.value / maxVal) * 3 + 0.1; // min height 0.1
      const isActive = currentCell?.[0] === cell.row && currentCell?.[1] === cell.col;

      let colour = 0xe2e8f0; // default grey
      if (isActive) colour = 0xef4444;        // red
      else if (cell.state === "computed") colour = 0x3b82f6; // blue
      else if (cell.state === "path") colour = 0x22c55e;     // green

      const geometry = new THREE.BoxGeometry(0.9, height, 0.9);
      const material = new THREE.MeshStandardMaterial({
        color: colour,
        metalness: 0.1,
        roughness: 0.8,
      });
      const block = new THREE.Mesh(geometry, material);
      block.position.set(cell.col, height / 2, cell.row);
      block.castShadow = true;
      scene.add(block);
    });

    // ... animation loop ...
  }, [cells, rows, cols, currentCell]);

  return <div ref={containerRef} className="w-full h-[500px]" />;
}
```

## 18.11 Animating transitions

Smoothly animate bars growing or swapping:

```ts
// Simple linear interpolation helper
function lerp(start: number, end: number, t: number): number {
  return start + (end - start) * t;
}

// Animate a bar growing from 0 to target height
function animateBarGrow(bar: THREE.Mesh, targetHeight: number, duration = 500) {
  const startTime = performance.now();
  const startHeight = 0.01;

  function tick() {
    const elapsed = performance.now() - startTime;
    const t = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic

    const currentHeight = lerp(startHeight, targetHeight, eased);

    // Update geometry scale (faster than recreating geometry)
    bar.scale.y = currentHeight / targetHeight;
    bar.position.y = (currentHeight) / 2;

    if (t < 1) requestAnimationFrame(tick);
  }
  tick();
}

// Animate two bars swapping positions
function animateSwap(
  barA: THREE.Mesh,
  barB: THREE.Mesh,
  duration = 400
) {
  const startTime = performance.now();
  const startXa = barA.position.x;
  const startXb = barB.position.x;

  // Lift bars up during swap
  function tick() {
    const elapsed = performance.now() - startTime;
    const t = Math.min(elapsed / duration, 1);
    const eased = t < 0.5
      ? 2 * t * t               // ease-in first half
      : 1 - Math.pow(-2 * t + 2, 2) / 2; // ease-out second half

    barA.position.x = lerp(startXa, startXb, eased);
    barB.position.x = lerp(startXb, startXa, eased);

    // Arc up then back down
    const lift = Math.sin(t * Math.PI) * 1.5;
    barA.position.y = barA.scale.y / 2 + lift;
    barB.position.y = barB.scale.y / 2 + lift;

    if (t < 1) requestAnimationFrame(tick);
  }
  tick();
}
```

## 18.12 Text labels in 3D

Text in Three.js is harder than in SVG. Options:

```ts
// Option 1: HTML labels overlaid on 3D (recommended for readability)
// Use CSS2DRenderer from Three.js examples
import { CSS2DRenderer, CSS2DObject } from "three/examples/jsm/renderers/CSS2DRenderer.js";

const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(width, height);
labelRenderer.domElement.style.position = "absolute";
labelRenderer.domElement.style.top = "0";
container.appendChild(labelRenderer.domElement);

// Create a label
const div = document.createElement("div");
div.textContent = "42";
div.className = "text-xs font-bold text-white bg-gray-900 px-1 rounded";
const label = new CSS2DObject(div);
label.position.set(bar.position.x, barHeight + 0.5, 0);
scene.add(label);

// Render labels in animation loop
labelRenderer.render(scene, camera);
```

```ts
// Option 2: 3D text geometry (looks 3D but expensive)
import { TextGeometry } from "three/examples/jsm/geometries/TextGeometry.js";
import { FontLoader } from "three/examples/jsm/loaders/FontLoader.js";

// Requires loading a font file — heavier
```

**Recommendation:** Use `CSS2DRenderer` for labels. They're always readable, always face the camera, and you can style them with regular CSS/Tailwind.



---

## PART 3: Advanced Patterns

## 18.13 React Three Fiber — Three.js the React way

Writing imperative Three.js in `useEffect` works but feels un-React. **React Three Fiber (R3F)** is a React renderer for Three.js — you write Three.js scenes as JSX:

```bash
npm install @react-three/fiber @react-three/drei
```

The same bar chart in R3F:

```tsx
"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";

type Bar3DProps = {
  position: [number, number, number];
  height: number;
  color: string;
  value: number;
};

function Bar3D({ position, height, color, value }: Bar3DProps) {
  return (
    <group position={position}>
      <mesh position={[0, height / 2, 0]} castShadow>
        <boxGeometry args={[0.6, height, 0.6]} />
        <meshStandardMaterial color={color} metalness={0.2} roughness={0.6} />
      </mesh>
      <Text
        position={[0, height + 0.4, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="bottom"
      >
        {String(value)}
      </Text>
    </group>
  );
}

type R3FBarChartProps = {
  data: number[];
  highlightIndices?: number[];
};

export default function R3FBarChart({ data, highlightIndices = [] }: R3FBarChartProps) {
  const maxVal = Math.max(...data);
  const spacing = 1.0;
  const offsetX = -(data.length * spacing) / 2;

  return (
    <div className="w-full h-[500px] rounded-lg overflow-hidden">
      <Canvas shadows camera={{ position: [8, 6, 8], fov: 50 }}>
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 10, 5]} intensity={1} castShadow />

        {/* Ground */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[20, 20]} />
          <meshStandardMaterial color="#334155" />
        </mesh>

        {/* Grid */}
        <gridHelper args={[20, 20, "#475569", "#475569"]} position={[0, 0.01, 0]} />

        {/* Bars */}
        {data.map((value, index) => (
          <Bar3D
            key={index}
            position={[offsetX + index * spacing, 0, 0]}
            height={(value / maxVal) * 5}
            color={highlightIndices.includes(index) ? "#f59e0b" : "#3b82f6"}
            value={value}
          />
        ))}

        {/* Controls */}
        <OrbitControls enableDamping dampingFactor={0.05} target={[0, 1, 0]} />
      </Canvas>
    </div>
  );
}
```

**R3F advantages:**
- Declarative — reads like React components
- Automatic disposal — no manual cleanup needed
- React ecosystem — hooks, context, suspense all work
- `@react-three/drei` — pre-built helpers (OrbitControls, Text, Environment, etc.)

**R3F disadvantages:**
- Extra dependency (adds ~50KB)
- Learning curve if you already know imperative Three.js
- Debugging is harder (can't inspect scene as easily)

## 18.14 Useful `@react-three/drei` helpers

```tsx
import {
  OrbitControls,  // camera controls
  Text,           // 3D text (uses troika-three-text under the hood)
  Html,           // HTML overlay in 3D space
  Environment,    // HDR environment maps (realistic reflections)
  Float,          // makes objects bob gently
  RoundedBox,     // box with rounded edges
  Plane,          // simple plane
} from "@react-three/drei";

// Environment for realistic lighting (no manual light setup needed)
<Environment preset="city" />

// HTML overlay positioned in 3D
<Html position={[0, 3, 0]} center>
  <div className="bg-white px-2 py-1 rounded shadow text-sm">
    Value: 42
  </div>
</Html>

// Floating animation
<Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
  <mesh>
    <sphereGeometry args={[0.5]} />
    <meshStandardMaterial color="orange" />
  </mesh>
</Float>
```

## 18.15 Performance tips

| Concern | Solution |
|---------|----------|
| Too many draw calls | Merge geometries with `THREE.BufferGeometryUtils.mergeGeometries()` |
| Re-rendering on every frame | Use R3F's `invalidate` mode — only re-render when something changes |
| Large scenes | Use `frustumCulling` (default on) — objects outside camera view aren't rendered |
| Memory leaks | Dispose geometries, materials, textures when removing objects |
| Mobile performance | Reduce `pixelRatio`, use simpler materials (`MeshLambertMaterial`), fewer lights |
| Shadow performance | Limit shadow-casting objects, reduce shadow map size |

```tsx
// R3F: Only render when needed (saves battery)
<Canvas frameloop="demand">

// R3F: Reduce pixel ratio on mobile
<Canvas dpr={[1, 2]}>  {/* min 1, max 2 — adapts to device */}
```

## 18.16 Raycasting — clicking on 3D objects

Detect which bar was clicked:

**Imperative approach:**

```ts
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener("click", (event) => {
  // Convert mouse to normalised device coordinates (-1 to +1)
  mouse.x = (event.offsetX / width) * 2 - 1;
  mouse.y = -(event.offsetY / height) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(bars);

  if (intersects.length > 0) {
    const clickedBar = intersects[0].object;
    console.log("Clicked bar:", clickedBar.userData.index);
  }
});

// Store index in userData when creating bars:
bar.userData = { index: i, value: data[i] };
```

**R3F approach (much simpler):**

```tsx
<mesh onClick={(e) => console.log("clicked", index)} onPointerOver={(e) => setHovered(true)}>
  <boxGeometry args={[0.6, height, 0.6]} />
  <meshStandardMaterial color={hovered ? "orange" : "blue"} />
</mesh>
```

## 18.17 Comparison: SVG/D3 vs Isometric/Rough.js vs Three.js

| Feature | SVG + D3 | Isometric + Rough.js | Three.js |
|---------|----------|---------------------|----------|
| Dimensions | 2D | Fake 3D (2.5D) | Real 3D |
| Rotation | No | No (fixed angle) | Yes (OrbitControls) |
| Elements | 10-1000 | 10-500 | 10-100,000+ |
| Style | Clean/precise | Hand-drawn/sketchy | Realistic/shaded |
| Text | Easy (SVG text) | Easy (SVG text) | Hard (CSS2D or 3D text) |
| Accessibility | Good (DOM elements) | Good (DOM elements) | Poor (canvas) |
| Bundle size | ~30KB (d3) | ~50KB (d3 + roughjs) | ~150KB (three) |
| Learning curve | Medium | Medium | High |
| Best for | Charts, diagrams | Educational/playful vis | Complex 3D scenes |

**For your algorithm visualiser:**
- **Default:** SVG + D3 (bar charts, trees, graphs)
- **Fun mode:** Isometric + Rough.js (adds character)
- **Wow mode:** Three.js (rotatable 3D, impressive for demos)

## 18.18 Project: 3D sorting visualiser

Combining everything — a full 3D sorting visualisation:

```tsx
"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

function AnimatedBar({
  targetX,
  height,
  color,
  value,
}: {
  targetX: number;
  height: number;
  color: string;
  value: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Smoothly interpolate to target position
  useFrame(() => {
    if (!meshRef.current) return;
    meshRef.current.position.x = THREE.MathUtils.lerp(
      meshRef.current.position.x,
      targetX,
      0.1 // smoothing factor
    );
  });

  return (
    <group>
      <mesh ref={meshRef} position={[targetX, height / 2, 0]} castShadow>
        <boxGeometry args={[0.6, height, 0.6]} />
        <meshStandardMaterial color={color} metalness={0.2} roughness={0.6} />
      </mesh>
      <Html position={[targetX, height + 0.4, 0]} center>
        <span className="text-xs font-bold text-white bg-black/70 px-1 rounded">
          {value}
        </span>
      </Html>
    </group>
  );
}

export default function ThreeSortingVis({
  data,
  comparing,
  sorted,
}: {
  data: number[];
  comparing: number[];
  sorted: number[];
}) {
  const maxVal = Math.max(...data);
  const spacing = 1.0;
  const offsetX = -(data.length * spacing) / 2;

  return (
    <div className="w-full h-[500px] rounded-xl overflow-hidden border border-gray-700">
      <Canvas shadows camera={{ position: [6, 5, 8], fov: 50 }}>
        <color attach="background" args={["#0f172a"]} />
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 10, 5]} intensity={1} castShadow />

        <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[20, 20]} />
          <meshStandardMaterial color="#1e293b" />
        </mesh>

        {data.map((value, index) => {
          let color = "#3b82f6"; // blue default
          if (sorted.includes(index)) color = "#22c55e";   // green = sorted
          if (comparing.includes(index)) color = "#f59e0b"; // amber = comparing

          return (
            <AnimatedBar
              key={index}
              targetX={offsetX + index * spacing}
              height={(value / maxVal) * 4}
              color={color}
              value={value}
            />
          );
        })}

        <OrbitControls enableDamping target={[0, 1.5, 0]} />
      </Canvas>
    </div>
  );
}
```

## Summary

✅ You understand Scene, Camera, Renderer — the Three.js trinity
✅ You can create geometries, materials, and meshes
✅ You know how to light a scene (ambient + directional)
✅ You added OrbitControls for user interaction
✅ You built a 3D bar chart with data-driven heights and colours
✅ You know how to animate objects (lerp, requestAnimationFrame, useFrame)
✅ You understand React Three Fiber as an alternative to imperative Three.js
✅ You can add labels (CSS2DRenderer or R3F Html)
✅ You know when to use Three.js vs simpler alternatives

## Key takeaways

**Three.js is a scene graph.** You add objects to a scene, point a camera at them, and a renderer draws the result 60 times per second. Everything else (lights, shadows, controls, animation) builds on this foundation.

**Separate setup from data.** Create the scene once. Update mesh positions/colours when data changes. Don't recreate the entire scene on every step.

**React Three Fiber makes Three.js declarative.** If you're building a React app, R3F lets you write 3D scenes as JSX components with hooks. It's the most natural way to integrate Three.js with React state.

**Choose your rendering layer by audience:** SVG for clarity, Isometric+Rough.js for charm, Three.js for impact.

---

→ [Back to Chapter 17: Isometric Visualisation](./17-ISOMETRIC-ROUGHJS-D3.md)
