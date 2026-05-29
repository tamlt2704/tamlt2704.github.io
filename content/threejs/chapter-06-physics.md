# Chapter 6: Physics with Cannon-es

[← Chapter 5: Animation](/blog/threejs/chapter-05-animation) | [Chapter 7: Shaders →](/blog/threejs/chapter-07-shaders)

---

## Setup

```bash
npm install cannon-es
```

Cannon-es handles physics (gravity, collisions). Three.js handles rendering. You sync them each frame.

## The Pattern

```typescript
import * as CANNON from "cannon-es";

// Physics world
const world = new CANNON.World({ gravity: new CANNON.Vec3(0, -9.82, 0) });

// For each object: create a Three.js mesh AND a Cannon.js body
// Each frame: copy physics body position → Three.js mesh position
```

## Step 1: Ground

```typescript
// Three.js visual
const floorMesh = new THREE.Mesh(
  new THREE.PlaneGeometry(20, 20),
  new THREE.MeshStandardMaterial({ color: 0x666666 }),
);
floorMesh.rotation.x = -Math.PI / 2;
scene.add(floorMesh);

// Cannon.js physics
const floorBody = new CANNON.Body({
  type: CANNON.Body.STATIC,
  shape: new CANNON.Plane(),
});
floorBody.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
world.addBody(floorBody);
```

## Step 2: Falling Box

```typescript
// Visual
const boxMesh = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0xff4444 }),
);
boxMesh.position.set(0, 5, 0);
scene.add(boxMesh);

// Physics
const boxBody = new CANNON.Body({
  mass: 1,
  shape: new CANNON.Box(new CANNON.Vec3(0.5, 0.5, 0.5)),
  position: new CANNON.Vec3(0, 5, 0),
});
world.addBody(boxBody);
```

## Step 3: Sync Loop

```typescript
function animate() {
  requestAnimationFrame(animate);

  // Step physics
  world.step(1 / 60);

  // Copy physics → visuals
  boxMesh.position.copy(boxBody.position as any);
  boxMesh.quaternion.copy(boxBody.quaternion as any);

  renderer.render(scene, camera);
}
```

## Spawning Multiple Objects

```typescript
const objects: { mesh: THREE.Mesh; body: CANNON.Body }[] = [];

function spawnSphere() {
  const radius = 0.3 + Math.random() * 0.5;
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(radius),
    new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff }),
  );
  scene.add(mesh);

  const body = new CANNON.Body({
    mass: 1,
    shape: new CANNON.Sphere(radius),
    position: new CANNON.Vec3((Math.random() - 0.5) * 4, 8, (Math.random() - 0.5) * 4),
  });
  world.addBody(body);

  objects.push({ mesh, body });
}

// In animate loop:
objects.forEach(({ mesh, body }) => {
  mesh.position.copy(body.position as any);
  mesh.quaternion.copy(body.quaternion as any);
});
```

## Materials & Friction

```typescript
const rubber = new CANNON.Material("rubber");
const ice = new CANNON.Material("ice");

const rubberIce = new CANNON.ContactMaterial(rubber, ice, {
  friction: 0.01,
  restitution: 0.9, // bouncy
});
world.addContactMaterial(rubberIce);

boxBody.material = rubber;
floorBody.material = ice;
```

---

[Chapter 7: Shaders & Post-Processing →](/blog/threejs/chapter-07-shaders)
