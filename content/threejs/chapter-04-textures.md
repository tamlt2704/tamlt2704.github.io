# Chapter 4: Textures & Models

[← Chapter 3: Lighting](/blog/threejs/chapter-03-lighting) | [Chapter 5: Animation →](/blog/threejs/chapter-05-animation)

---

## Loading Textures

```typescript
const loader = new THREE.TextureLoader();
const texture = loader.load("/textures/wood.jpg");

const material = new THREE.MeshStandardMaterial({ map: texture });
```

## Texture Maps

```typescript
const material = new THREE.MeshStandardMaterial({
  map: loader.load("/color.jpg"), // base color
  normalMap: loader.load("/normal.jpg"), // surface detail (bumps)
  roughnessMap: loader.load("/rough.jpg"), // roughness variation
  metalnessMap: loader.load("/metal.jpg"), // metallic areas
  aoMap: loader.load("/ao.jpg"), // ambient occlusion (crevice shadows)
  displacementMap: loader.load("/disp.jpg"), // actual geometry displacement
});
```

## Texture Repeat & Wrap

```typescript
texture.wrapS = THREE.RepeatWrapping;
texture.wrapT = THREE.RepeatWrapping;
texture.repeat.set(4, 4); // tile 4x4
```

## Loading 3D Models (GLTF)

GLTF is the "JPEG of 3D" — the standard format:

```typescript
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

const gltfLoader = new GLTFLoader();
gltfLoader.load("/models/character.glb", (gltf) => {
  const model = gltf.scene;
  model.scale.set(0.5, 0.5, 0.5);
  model.position.set(0, 0, 0);
  scene.add(model);

  // Enable shadows on all meshes
  model.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });
});
```

## Loading with Progress

```typescript
gltfLoader.load(
  "/models/scene.glb",
  (gltf) => {
    scene.add(gltf.scene);
  }, // success
  (progress) => {
    console.log(`${((progress.loaded / progress.total) * 100).toFixed(0)}%`);
  }, // progress
  (error) => {
    console.error("Failed:", error);
  }, // error
);
```

## Environment Maps (Reflections)

```typescript
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader";

new RGBELoader().load("/env/studio.hdr", (texture) => {
  texture.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = texture; // all PBR materials reflect this
  scene.background = texture; // optional: use as skybox
});
```

## Free Resources

| Resource   | URL           | Content                       |
| ---------- | ------------- | ----------------------------- |
| Poly Haven | polyhaven.com | HDRIs, textures, models (CC0) |
| Sketchfab  | sketchfab.com | 3D models (various licenses)  |
| ambientCG  | ambientcg.com | PBR textures (CC0)            |
| Mixamo     | mixamo.com    | Animated characters (free)    |

---

[Chapter 5: Animation & Controls →](/blog/threejs/chapter-05-animation)
