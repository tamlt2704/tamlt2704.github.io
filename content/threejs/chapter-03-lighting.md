# Chapter 3: Lighting & Shadows

[← Chapter 2: Geometries](/blog/threejs/chapter-02-geometries) | [Chapter 4: Textures →](/blog/threejs/chapter-04-textures)

---

## Light Types

| Light              | Description                          | Shadow? |
| ------------------ | ------------------------------------ | ------- |
| `AmbientLight`     | Even light everywhere (no direction) | No      |
| `DirectionalLight` | Sun-like (parallel rays)             | Yes     |
| `PointLight`       | Light bulb (radiates from a point)   | Yes     |
| `SpotLight`        | Flashlight (cone of light)           | Yes     |
| `HemisphereLight`  | Sky + ground colors                  | No      |

```typescript
// Ambient (base illumination)
const ambient = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambient);

// Directional (sun)
const sun = new THREE.DirectionalLight(0xffffff, 1);
sun.position.set(5, 10, 5);
scene.add(sun);

// Point (lamp)
const lamp = new THREE.PointLight(0xff9900, 1, 10);
lamp.position.set(0, 3, 0);
scene.add(lamp);

// Spot (flashlight)
const spot = new THREE.SpotLight(0xffffff, 1, 20, Math.PI / 6);
spot.position.set(0, 5, 0);
scene.add(spot);
```

## Enabling Shadows

Three steps:

```typescript
// 1. Enable on renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// 2. Light casts shadows
sun.castShadow = true;
sun.shadow.mapSize.width = 2048;
sun.shadow.mapSize.height = 2048;

// 3. Objects cast/receive
cube.castShadow = true;
floor.receiveShadow = true;
```

## Shadow Camera (Directional Light)

```typescript
sun.shadow.camera.left = -10;
sun.shadow.camera.right = 10;
sun.shadow.camera.top = 10;
sun.shadow.camera.bottom = -10;
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 50;
```

## Project: Lit Room

```typescript
// Floor
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(10, 10),
  new THREE.MeshStandardMaterial({ color: 0x808080 }),
);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// Objects
const sphere = new THREE.Mesh(
  new THREE.SphereGeometry(0.5, 32, 32),
  new THREE.MeshStandardMaterial({ color: 0xff4444, metalness: 0.3, roughness: 0.4 }),
);
sphere.position.set(0, 0.5, 0);
sphere.castShadow = true;
scene.add(sphere);

// Warm point light
const warmLight = new THREE.PointLight(0xffaa44, 1, 8);
warmLight.position.set(2, 3, 1);
warmLight.castShadow = true;
scene.add(warmLight);

// Cool fill light
const coolLight = new THREE.PointLight(0x4488ff, 0.3, 10);
coolLight.position.set(-3, 2, -2);
scene.add(coolLight);
```

## Light Helpers (Debug)

```typescript
scene.add(new THREE.DirectionalLightHelper(sun, 1));
scene.add(new THREE.PointLightHelper(lamp, 0.5));
scene.add(new THREE.SpotLightHelper(spot));
scene.add(new THREE.CameraHelper(sun.shadow.camera));
```

---

[Chapter 4: Textures & Models →](/blog/threejs/chapter-04-textures)
