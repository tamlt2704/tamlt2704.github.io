# Chapter 2: Geometries & Materials

[← Chapter 1: Setup](/blog/threejs/chapter-01-setup) | [Chapter 3: Lighting →](/blog/threejs/chapter-03-lighting)

---

## Built-in Geometries

```typescript
// Primitives
new THREE.BoxGeometry(width, height, depth);
new THREE.SphereGeometry(radius, widthSegments, heightSegments);
new THREE.CylinderGeometry(radiusTop, radiusBottom, height);
new THREE.ConeGeometry(radius, height);
new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments);
new THREE.PlaneGeometry(width, height);
new THREE.CircleGeometry(radius, segments);
new THREE.RingGeometry(innerRadius, outerRadius);
new THREE.TorusKnotGeometry(radius, tube, tubularSegments, radialSegments);
```

## Materials

| Material               | Lighting? | Use Case                               |
| ---------------------- | --------- | -------------------------------------- |
| `MeshBasicMaterial`    | No        | Flat color, unaffected by light        |
| `MeshNormalMaterial`   | No        | Debug (colors based on face direction) |
| `MeshLambertMaterial`  | Yes       | Matte surfaces (fast)                  |
| `MeshPhongMaterial`    | Yes       | Shiny surfaces (specular highlights)   |
| `MeshStandardMaterial` | Yes       | PBR realistic (recommended)            |
| `MeshPhysicalMaterial` | Yes       | Glass, clearcoat, subsurface           |

```typescript
// Basic (no light needed)
new THREE.MeshBasicMaterial({ color: 0xff0000, wireframe: true });

// Standard PBR (needs light)
new THREE.MeshStandardMaterial({
  color: 0x2194ce,
  metalness: 0.3,
  roughness: 0.4,
});
```

## Material Properties

```typescript
const mat = new THREE.MeshStandardMaterial({
  color: 0xffffff, // base color
  metalness: 0.0, // 0 = plastic, 1 = metal
  roughness: 0.5, // 0 = mirror, 1 = matte
  transparent: true, // enable transparency
  opacity: 0.8, // 0 = invisible, 1 = solid
  side: THREE.DoubleSide, // render both sides
  wireframe: false, // show wireframe
});
```

## Project: Solar System

```typescript
// Sun
const sun = new THREE.Mesh(
  new THREE.SphereGeometry(2, 32, 32),
  new THREE.MeshBasicMaterial({ color: 0xffdd00 }),
);
scene.add(sun);

// Earth (orbits sun)
const earthGroup = new THREE.Group();
scene.add(earthGroup);

const earth = new THREE.Mesh(
  new THREE.SphereGeometry(0.5, 32, 32),
  new THREE.MeshStandardMaterial({ color: 0x2233ff }),
);
earth.position.x = 5;
earthGroup.add(earth);

// Moon (orbits earth)
const moon = new THREE.Mesh(
  new THREE.SphereGeometry(0.15, 16, 16),
  new THREE.MeshStandardMaterial({ color: 0xaaaaaa }),
);
moon.position.x = 1;
earth.add(moon); // child of earth — moves with it

// Animate
function animate() {
  requestAnimationFrame(animate);
  earthGroup.rotation.y += 0.005; // earth orbits sun
  earth.rotation.y += 0.02; // earth spins
  renderer.render(scene, camera);
}
```

## Scene Graph (Parent-Child)

```
Scene
├── Sun
├── EarthGroup (rotates → earth orbits)
│   └── Earth (rotates → earth spins)
│       └── Moon (inherits earth's position)
└── Light
```

Children inherit parent transforms. Move the parent, children follow.

---

[Chapter 3: Lighting & Shadows →](/blog/threejs/chapter-03-lighting)
