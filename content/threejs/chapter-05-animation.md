# Chapter 5: Animation & Controls

[← Chapter 4: Textures](/blog/threejs/chapter-04-textures) | [Chapter 6: Physics →](/blog/threejs/chapter-06-physics)

---

## The Animation Loop

```typescript
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta(); // time since last frame (seconds)
  const elapsed = clock.getElapsedTime(); // total time

  // Frame-rate independent animation
  cube.rotation.y += 1.0 * delta; // 1 radian per second regardless of FPS

  renderer.render(scene, camera);
}
```

Always use `delta` for smooth animation across different frame rates.

## OrbitControls (Mouse Interaction)

```typescript
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; // smooth deceleration
controls.dampingFactor = 0.05;
controls.maxDistance = 20;
controls.minDistance = 2;

function animate() {
  requestAnimationFrame(animate);
  controls.update(); // required when damping enabled
  renderer.render(scene, camera);
}
```

## Keyframe Animation (from GLTF)

```typescript
let mixer: THREE.AnimationMixer;

gltfLoader.load("/models/character.glb", (gltf) => {
  scene.add(gltf.scene);
  mixer = new THREE.AnimationMixer(gltf.scene);

  // Play first animation clip
  const action = mixer.clipAction(gltf.animations[0]);
  action.play();
});

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  if (mixer) mixer.update(delta);
  renderer.render(scene, camera);
}
```

## Raycasting (Click Detection)

```typescript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

window.addEventListener("click", (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children);

  if (intersects.length > 0) {
    const clicked = intersects[0].object;
    clicked.material.color.set(0xff0000); // turn red on click
  }
});
```

## Tweening (Smooth Transitions)

```typescript
// Simple lerp (linear interpolation)
function animate() {
  requestAnimationFrame(animate);

  // Smoothly move camera to target
  camera.position.lerp(targetPosition, 0.05);

  // Smoothly rotate object
  cube.rotation.y += (targetRotation - cube.rotation.y) * 0.1;

  renderer.render(scene, camera);
}
```

## Project: Interactive Globe

```typescript
const globe = new THREE.Mesh(
  new THREE.SphereGeometry(2, 64, 64),
  new THREE.MeshStandardMaterial({ map: loader.load("/earth.jpg") }),
);
scene.add(globe);

// Auto-rotate
function animate() {
  requestAnimationFrame(animate);
  globe.rotation.y += 0.002;
  controls.update();
  renderer.render(scene, camera);
}

// Click to place marker
window.addEventListener("click", (e) => {
  // ... raycasting to find point on globe
  // ... place a small sphere at intersection point
});
```

---

[Chapter 6: Physics with Cannon-es →](/blog/threejs/chapter-06-physics)
