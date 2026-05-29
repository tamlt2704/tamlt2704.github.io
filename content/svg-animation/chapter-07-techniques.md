# Chapter 7: Advanced Techniques

[prev: Lottie](./chapter-06-lottie.md) | [next: Projects](./chapter-08-projects.md)

This chapter covers advanced SVG animation techniques that combine multiple concepts: line drawing tricks, path morphing, particle systems, text on paths, clip-path and mask animations, SVG filters, and responsive animation strategies.

## Line Drawing — The stroke-dasharray Trick

The classic technique revisited with advanced variations.

### Basic Principle

Every SVG stroke can be dashed. If the dash length equals the total path length and the gap equals the path length, you see the full stroke. Offset the dash by the path length and the stroke disappears. Animate the offset from full to zero — the line "draws."

```html
<svg width="400" height="200" viewBox="0 0 400 200">
  <style>
    .signature {
      fill: none;
      stroke: #333;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-dasharray: 600;
      stroke-dashoffset: 600;
      animation: draw 3s ease forwards;
    }
    @keyframes draw {
      to {
        stroke-dashoffset: 0;
      }
    }
  </style>
  <path
    class="signature"
    d="M 30,150 C 30,50 80,50 100,100 C 120,150 140,150 160,100 
       C 180,50 200,80 220,120 C 240,160 280,100 300,80 C 320,60 350,90 370,120"
  />
</svg>
```

Visually: A cursive signature drawing itself from left to right, as if someone is signing their name in real-time.

### Reverse Draw (Erase Effect)

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <style>
    .erase {
      stroke-dasharray: 500;
      stroke-dashoffset: 0;
      animation: erase 2s ease forwards 1s;
    }
    @keyframes erase {
      to {
        stroke-dashoffset: -500;
      }
    }
  </style>
  <path
    class="erase"
    d="M 20,100 C 80,20 220,180 280,100"
    fill="none"
    stroke="#e74c3c"
    stroke-width="3"
  />
</svg>
```

Visually: A red curve that's fully visible, then erases itself from the start point — the line disappears as if being rubbed out. The negative offset makes it erase from the beginning rather than the end.

### Partial Draw (Snake Effect)

```html
<svg width="400" height="200" viewBox="0 0 400 200">
  <style>
    .snake {
      stroke-dasharray: 50 450;
      animation: snake 3s linear infinite;
    }
    @keyframes snake {
      to {
        stroke-dashoffset: -500;
      }
    }
  </style>
  <path
    class="snake"
    d="M 20,100 C 20,20 180,20 200,100 C 220,180 380,180 380,100"
    fill="none"
    stroke="#3498db"
    stroke-width="4"
    stroke-linecap="round"
  />
</svg>
```

Visually: A short blue segment (50px) traveling along the S-curve path continuously — like a glowing dot racing along a track.

## Morphing Paths

### With flubber (Lightweight Morphing)

flubber interpolates between SVG path strings, handling different point counts gracefully.

```typescript
npm install flubber
```

```typescript
import { interpolate } from "flubber";

const circle = "M 100,50 A 50,50 0 1,1 99.9,50 Z";
const star =
  "M 100,10 L 120,75 L 190,75 L 135,115 L 155,180 L 100,140 L 45,180 L 65,115 L 10,75 L 80,75 Z";

const interpolator = interpolate(circle, star, { maxSegmentLength: 5 });

// Use with requestAnimationFrame
let progress = 0;
const path = document.querySelector("#morph-target");

function animate() {
  progress += 0.01;
  if (progress > 1) progress = 0;

  path.setAttribute("d", interpolator(progress));
  requestAnimationFrame(animate);
}
animate();
```

```html
<svg width="200" height="200" viewBox="0 0 200 200">
  <path id="morph-target" fill="#3498db" />
</svg>
```

Visually: A blue circle smoothly morphing into a star shape and back, continuously. flubber adds intermediate points so the transition looks natural even between shapes with different vertex counts.

### With GSAP MorphSVGPlugin

```typescript
gsap.registerPlugin(MorphSVGPlugin);

// Morph between two visible paths
gsap.to("#shape-a", {
  morphSVG: "#shape-b",
  duration: 1.5,
  ease: "power2.inOut",
  repeat: -1,
  yoyo: true,
});

// Morph with shape index control (where the morph "starts")
gsap.to("#shape", {
  morphSVG: { shape: "#target", shapeIndex: 3 },
  duration: 2,
});
```

## Particle Effects

### SVG Particle Explosion

```html
<svg width="300" height="300" viewBox="0 0 300 300" id="particles">
  <circle cx="150" cy="150" r="5" fill="#e74c3c" id="trigger" style="cursor:pointer" />
</svg>

<script>
  const svg = document.getElementById("particles");
  const trigger = document.getElementById("trigger");

  function createParticle() {
    const colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"];
    const particle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    particle.setAttribute("cx", "150");
    particle.setAttribute("cy", "150");
    particle.setAttribute("r", String(2 + Math.random() * 4));
    particle.setAttribute("fill", colors[Math.floor(Math.random() * colors.length)]);
    svg.appendChild(particle);

    const angle = Math.random() * Math.PI * 2;
    const velocity = 50 + Math.random() * 100;
    const tx = Math.cos(angle) * velocity;
    const ty = Math.sin(angle) * velocity;

    gsap.to(particle, {
      cx: 150 + tx,
      cy: 150 + ty,
      r: 0,
      opacity: 0,
      duration: 0.8 + Math.random() * 0.5,
      ease: "power2.out",
      onComplete: () => particle.remove(),
    });
  }

  trigger.addEventListener("click", () => {
    for (let i = 0; i < 30; i++) {
      setTimeout(createParticle, i * 10);
    }
  });
</script>
```

Visually: Click the center dot and 30 colored circles explode outward in all directions, shrinking and fading as they fly — like a firework burst.

### Floating Particles (Ambient)

```html
<svg width="400" height="300" viewBox="0 0 400 300" id="ambient">
  <rect width="400" height="300" fill="#1a1a2e" />
</svg>

<script>
  const svg = document.getElementById("ambient");

  for (let i = 0; i < 20; i++) {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    const cx = Math.random() * 400;
    const cy = Math.random() * 300;
    const r = 1 + Math.random() * 3;
    circle.setAttribute("cx", String(cx));
    circle.setAttribute("cy", String(cy));
    circle.setAttribute("r", String(r));
    circle.setAttribute("fill", "rgba(255,255,255,0.3)");
    svg.appendChild(circle);

    gsap.to(circle, {
      cy: cy - 50 - Math.random() * 50,
      opacity: 0,
      duration: 3 + Math.random() * 4,
      repeat: -1,
      ease: "none",
      delay: Math.random() * 3,
    });
  }
</script>
```

Visually: A dark background with small white dots slowly floating upward and fading — like dust motes or bubbles rising.

## Text Along Path (textPath)

```svg
<svg width="400" height="200" viewBox="0 0 400 200">
  <defs>
    <path id="curve" d="M 20,150 C 100,20 300,20 380,150"/>
  </defs>

  <!-- Show the path for reference -->
  <use href="#curve" fill="none" stroke="#eee" stroke-width="1"/>

  <text font-size="16" fill="#333" font-family="sans-serif">
    <textPath href="#curve" startOffset="0%">
      Text flowing along a curved path
    </textPath>
  </text>
</svg>
```

Visually: Text that follows a curved arc instead of sitting on a straight baseline — the letters bend along the path.

### Animated Text Along Path

```html
<svg width="400" height="200" viewBox="0 0 400 200">
  <defs>
    <path id="orbit" d="M 200,100 m -120,0 a 120,60 0 1,0 240,0 a 120,60 0 1,0 -240,0" />
  </defs>
  <style>
    #moving-text {
      animation: orbit-text 8s linear infinite;
    }
    @keyframes orbit-text {
      from {
        startoffset: 0%;
      }
      to {
        startoffset: 100%;
      }
    }
  </style>
  <text font-size="14" fill="#3498db" font-family="monospace">
    <textPath id="moving-text" href="#orbit">
      ★ Orbiting Text Animation ★ Orbiting Text Animation
    </textPath>
  </text>
</svg>
```

For reliable cross-browser animation, use GSAP:

```typescript
gsap.to("#moving-text", {
  attr: { startOffset: "100%" },
  duration: 8,
  ease: "none",
  repeat: -1,
});
```

Visually: Text orbiting along an elliptical path continuously — like a marquee that follows a curved track.

## Clip-Path Animations

Reveal content by animating a clipping shape.

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <clipPath id="reveal-clip">
      <circle cx="150" cy="100" r="0">
        <animate attributeName="r" from="0" to="200" dur="1.5s" fill="freeze" />
      </circle>
    </clipPath>
  </defs>

  <!-- Image/content revealed by expanding circle -->
  <g clip-path="url(#reveal-clip)">
    <rect width="300" height="200" fill="#3498db" />
    <text x="150" y="105" text-anchor="middle" font-size="24" fill="white">Revealed!</text>
  </g>
</svg>
```

Visually: A blue rectangle with "Revealed!" text that appears through an expanding circular window — starts as a dot in the center and grows to reveal the full content.

### Animated Clip-Path with CSS

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <clipPath id="wipe-clip">
      <rect x="-300" y="0" width="300" height="200">
        <animate attributeName="x" from="-300" to="0" dur="1s" fill="freeze" />
      </rect>
    </clipPath>
  </defs>

  <g clip-path="url(#wipe-clip)">
    <rect width="300" height="200" fill="#2ecc71" />
    <text x="150" y="110" text-anchor="middle" font-size="20" fill="white">Wipe Reveal</text>
  </g>
</svg>
```

Visually: Content slides in from the left as if a curtain is being pulled — a horizontal wipe transition.

## Mask Animations

Masks use luminance (white = visible, black = hidden) for soft reveals.

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <mask id="spotlight">
      <rect width="300" height="200" fill="black" />
      <circle cx="150" cy="100" r="0" fill="white">
        <animate attributeName="r" from="0" to="120" dur="2s" fill="freeze" />
      </circle>
    </mask>
  </defs>

  <!-- Dark background always visible -->
  <rect width="300" height="200" fill="#1a1a2e" />

  <!-- Content revealed by mask -->
  <g mask="url(#spotlight)">
    <rect width="300" height="200" fill="#e74c3c" />
    <circle cx="100" cy="80" r="20" fill="#f39c12" />
    <circle cx="200" cy="120" r="30" fill="#3498db" />
    <text x="150" y="180" text-anchor="middle" font-size="14" fill="white">Hidden Scene</text>
  </g>
</svg>
```

Visually: A dark scene with a growing circular "spotlight" that reveals colorful shapes underneath — like shining a flashlight in a dark room.

### Gradient Mask for Soft Edges

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <radialGradient id="soft-edge">
      <stop offset="0%" stop-color="white" />
      <stop offset="70%" stop-color="white" />
      <stop offset="100%" stop-color="black" />
    </radialGradient>
    <mask id="soft-mask">
      <circle cx="150" cy="100" r="80" fill="url(#soft-edge)">
        <animate attributeName="r" values="0;80;0" dur="3s" repeatCount="indefinite" />
      </circle>
    </mask>
  </defs>

  <rect width="300" height="200" fill="#1a1a2e" />
  <rect width="300" height="200" fill="#e74c3c" mask="url(#soft-mask)" />
</svg>
```

Visually: A red area that pulses in and out with soft, feathered edges — unlike clip-path which has hard edges, the mask gradient creates a smooth fade at the boundary.

## Filter Animations

SVG filters create effects impossible with CSS alone.

### Animated Blur (feGaussianBlur)

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <filter id="blur-filter">
      <feGaussianBlur in="SourceGraphic" stdDeviation="0">
        <animate attributeName="stdDeviation" values="0;5;0" dur="2s" repeatCount="indefinite" />
      </feGaussianBlur>
    </filter>
  </defs>

  <text
    x="150"
    y="110"
    text-anchor="middle"
    font-size="32"
    fill="#333"
    font-family="sans-serif"
    filter="url(#blur-filter)"
  >
    Focus
  </text>
</svg>
```

Visually: The word "Focus" that rhythmically blurs and sharpens — going from crisp to blurry and back.

### Displacement Map (Liquid/Distortion Effect)

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <filter id="liquid">
      <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="3" result="noise" seed="1">
        <animate
          attributeName="baseFrequency"
          values="0.01;0.04;0.01"
          dur="4s"
          repeatCount="indefinite"
        />
      </feTurbulence>
      <feDisplacementMap
        in="SourceGraphic"
        in2="noise"
        scale="20"
        xChannelSelector="R"
        yChannelSelector="G"
      >
        <animate attributeName="scale" values="0;20;0" dur="4s" repeatCount="indefinite" />
      </feDisplacementMap>
    </filter>
  </defs>

  <text
    x="150"
    y="110"
    text-anchor="middle"
    font-size="36"
    fill="#3498db"
    font-family="sans-serif"
    filter="url(#liquid)"
  >
    Liquid
  </text>
</svg>
```

Visually: The word "Liquid" that warps and distorts as if underwater — the text ripples and flows, then settles back to normal, then distorts again.

### Glow Effect

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <rect width="300" height="200" fill="#1a1a2e" />
  <circle cx="150" cy="100" r="30" fill="#00d4ff" filter="url(#glow)">
    <animate attributeName="r" values="30;35;30" dur="2s" repeatCount="indefinite" />
  </circle>
</svg>
```

Visually: A cyan circle on a dark background with a soft glow halo around it, pulsing gently — like a neon light breathing.

## Responsive SVG Animation

### ViewBox-Based Scaling

SVG animations scale naturally with viewBox. The key is using relative units:

```html
<svg viewBox="0 0 400 300" style="width: 100%; max-width: 600px;">
  <style>
    .responsive-anim {
      animation: move 3s ease-in-out infinite alternate;
    }
    @keyframes move {
      from {
        transform: translateX(0);
      }
      to {
        transform: translateX(200px);
      }
    }
  </style>
  <circle class="responsive-anim" cx="50" cy="150" r="20" fill="#3498db" />
</svg>
```

The animation works at any display size because the viewBox coordinate system is independent of the rendered size.

### Media Queries Inside SVG

```html
<svg viewBox="0 0 400 200" style="width: 100%;">
  <style>
    .detail {
      opacity: 1;
    }
    @media (max-width: 400px) {
      .detail {
        opacity: 0;
      }
      .main {
        r: 40;
      }
    }
  </style>
  <circle class="main" cx="200" cy="100" r="30" fill="#3498db">
    <animate attributeName="r" values="30;40;30" dur="2s" repeatCount="indefinite" />
  </circle>
  <circle class="detail" cx="100" cy="100" r="10" fill="#e74c3c">
    <animate attributeName="cy" values="100;80;100" dur="1.5s" repeatCount="indefinite" />
  </circle>
  <circle class="detail" cx="300" cy="100" r="10" fill="#2ecc71">
    <animate attributeName="cy" values="100;120;100" dur="1.5s" repeatCount="indefinite" />
  </circle>
</svg>
```

Visually: On wide screens, three animated circles. On narrow screens, only the main pulsing circle — detail elements hide to reduce visual noise on small displays.

### Reduce Motion Preference

Always respect users who prefer reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

```typescript
// JavaScript check
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (!prefersReducedMotion) {
  gsap.to("#element", { x: 100, duration: 1 });
} else {
  gsap.set("#element", { x: 100 }); // instant, no animation
}
```

## Key Takeaways

- Line drawing uses `stroke-dasharray` equal to path length + animated `stroke-dashoffset`
- Morphing: use flubber for lightweight needs, GSAP MorphSVGPlugin for production
- Particle effects: create SVG elements dynamically, animate with GSAP, remove on complete
- `textPath` places text along curves; animate `startOffset` for orbiting text
- Clip-path gives hard-edge reveals; masks give soft-edge reveals with gradients
- SVG filters (blur, displacement, turbulence) create effects impossible with CSS
- Responsive: use viewBox for scaling, media queries for complexity reduction
- Always respect `prefers-reduced-motion`
