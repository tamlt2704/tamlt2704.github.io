# Summary — What You've Learned

| Chapter | Concept | Three.js / R3F Feature |
|---|---|---|
| 1. Empty Lot | Canvas, scene setup | `<Canvas>`, coordinate system |
| 2. Foundation | Shapes and surfaces | Geometries, Materials |
| 3. Walls | Positioning and hierarchy | `position`, `rotation`, `scale`, `<group>` |
| 4. Electricity | Lighting and shadows | Light types, `castShadow`, `receiveShadow` |
| 5. Doors | Interaction and motion | Events, `useFrame`, `useRef`, `lerp` |
| 6. Furniture | External assets | `useGLTF`, `<Suspense>`, Draco |
| 7. Landscaping | Environment and polish | `<Environment>`, `<Sky>`, post-processing |
| 8. Open House | Deployment | Static export, GitHub Actions, `basePath` |

### Where to Go Next

- **Shaders** — Write custom GLSL for unique visual effects (`shaderMaterial`)
- **Physics** — Add gravity and collisions with `@react-three/rapier`
- **Scroll animation** — Drive camera/scene changes from page scroll (`@react-three/drei`'s `ScrollControls`)
- **Performance** — Instanced meshes, LOD, `drei`'s `Bvh` for faster raycasting
- **State management** — Zustand for complex scenes with many interactive parts
- **XR** — WebXR support for VR/AR via `@react-three/xr`

### Essential Resources

- [React Three Fiber docs](https://r3f.docs.pmnd.rs/)
- [drei docs](https://drei.docs.pmnd.rs/)
- [Three.js docs](https://threejs.org/docs/)
- [Three.js examples](https://threejs.org/examples/)
- [R3F examples](https://codesandbox.io/examples/package/@react-three/fiber)
- [gltf.pmnd.rs](https://gltf.pmnd.rs/) — GLB to React component converter

---

*Built with Next.js, React Three Fiber, and drei. Deployed on GitHub Pages. Zero server costs.*

---

[← Chapter 8: Open House](./08-open-house.md) | [Back to Introduction](./00-introduction.md)
