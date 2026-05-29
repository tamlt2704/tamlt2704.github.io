# Chapter 7: Shaders & Post-Processing

[← Chapter 6: Physics](/blog/threejs/chapter-06-physics) | [Chapter 8: React Three Fiber →](/blog/threejs/chapter-08-r3f)

---

## What are Shaders?

Programs that run on the GPU. Two types:

- **Vertex Shader** — positions each vertex (shape deformation)
- **Fragment Shader** — colors each pixel (visual effects)

## Custom Shader Material

```typescript
const material = new THREE.ShaderMaterial({
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    uniform float uTime;
    void main() {
      vec3 color = vec3(vUv.x, vUv.y, sin(uTime) * 0.5 + 0.5);
      gl_FragColor = vec4(color, 1.0);
    }
  `,
  uniforms: {
    uTime: { value: 0 },
  },
});

// Update in animate loop
material.uniforms.uTime.value = clock.getElapsedTime();
```

## Vertex Displacement (Wavy Surface)

```glsl
// vertex shader
uniform float uTime;
varying vec2 vUv;

void main() {
  vUv = uv;
  vec3 pos = position;
  pos.z += sin(pos.x * 3.0 + uTime) * 0.3;
  pos.z += sin(pos.y * 2.0 + uTime * 0.5) * 0.2;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
```

## Post-Processing (EffectComposer)

```typescript
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass";

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(
  new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.5, // strength
    0.4, // radius
    0.85, // threshold
  ),
);

// Replace renderer.render() with:
function animate() {
  requestAnimationFrame(animate);
  composer.render();
}
```

## Common Post-Processing Effects

| Effect     | Import                      | Use                        |
| ---------- | --------------------------- | -------------------------- |
| Bloom      | `UnrealBloomPass`           | Glowing lights             |
| FXAA       | `ShaderPass` + `FXAAShader` | Anti-aliasing              |
| Film Grain | `FilmPass`                  | Cinematic look             |
| Vignette   | Custom shader               | Dark edges                 |
| Outline    | `OutlinePass`               | Highlight selected objects |

## GLSL Cheat Sheet

```glsl
// Types
float, vec2, vec3, vec4, mat4

// Built-in functions
sin(), cos(), mix(), smoothstep(), clamp(), length(), normalize()

// Varying (vertex → fragment)
varying vec2 vUv;

// Uniforms (JS → shader)
uniform float uTime;
uniform vec3 uColor;
uniform sampler2D uTexture;
```

---

[Chapter 8: React Three Fiber →](/blog/threejs/chapter-08-r3f)
