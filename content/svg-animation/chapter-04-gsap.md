# Chapter 4: GSAP — The Industry Standard

[prev: SMIL](./chapter-03-smil.md) | [next: Framer Motion](./chapter-05-framer-motion.md)

GSAP (GreenSock Animation Platform) is the most widely used professional animation library. It handles cross-browser quirks, provides precise timeline control, and offers plugins for SVG-specific effects like morphing and line drawing. If you're building production animations, GSAP is the default choice.

## Setup

```html
<!-- Core library -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>

<!-- Optional plugins -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
```

Or with npm:

```typescript
npm install gsap
```

```typescript
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);
```

## gsap.to / gsap.from / gsap.fromTo

### gsap.to — Animate to target values

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <circle id="ball" cx="30" cy="100" r="20" fill="#e74c3c" />
</svg>

<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script>
  gsap.to("#ball", {
    cx: 270,
    duration: 2,
    ease: "power2.inOut",
    repeat: -1,
    yoyo: true,
  });
</script>
```

Visually: A red circle sliding smoothly left to right and back, with ease-in-out timing. `repeat: -1` loops forever, `yoyo: true` reverses each cycle.

### gsap.from — Animate from values (current state is the end)

```typescript
gsap.from("#ball", {
  cx: 270,
  opacity: 0,
  duration: 1.5,
  ease: "back.out(1.7)",
});
```

Visually: The circle starts at x=270 and invisible, then bounces into its natural position with a slight overshoot.

### gsap.fromTo — Explicit start and end

```typescript
gsap.fromTo(
  "#ball",
  { cx: 30, fill: "#3498db" }, // from
  { cx: 270, fill: "#e74c3c", duration: 2, ease: "elastic.out(1, 0.3)" }, // to
);
```

Visually: Circle moves from left (blue) to right (red) with an elastic bounce at the end.

## Timelines

Timelines sequence multiple animations with precise control.

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <rect id="box" x="20" y="80" width="40" height="40" fill="#3498db" />
  <circle id="dot" cx="150" cy="100" r="0" fill="#e74c3c" />
  <text id="label" x="150" y="160" text-anchor="middle" font-size="14" opacity="0" fill="#333">
    Done!
  </text>
</svg>

<script>
  const tl = gsap.timeline({ defaults: { duration: 0.8, ease: "power2.out" } });

  tl.to("#box", { x: 200, fill: "#2ecc71" })
    .to("#box", { rotation: 360, transformOrigin: "center" })
    .to("#dot", { r: 30, duration: 0.4 }, "-=0.3") // overlap by 0.3s
    .to("#label", { opacity: 1, y: -10 });
</script>
```

Visually: (1) Blue box slides right and turns green, (2) box spins 360 degrees, (3) red dot grows from nothing (starts slightly before spin finishes), (4) "Done!" text fades in and floats up.

### Timeline Position Parameters

```typescript
const tl = gsap.timeline();

tl.to("#a", { x: 100, duration: 1 }) // starts at 0s
  .to("#b", { x: 100, duration: 1 }) // starts when #a ends (1s)
  .to("#c", { x: 100, duration: 1 }, "+=0.5") // 0.5s gap after #b
  .to("#d", { x: 100, duration: 1 }, "-=0.3") // overlaps #c by 0.3s
  .to("#e", { x: 100, duration: 1 }, 2) // absolute: starts at 2s
  .to("#f", { x: 100, duration: 1 }, "<") // same start time as previous
  .to("#g", { x: 100, duration: 1 }, "<0.2"); // 0.2s after previous starts
```

## Stagger

Animate multiple elements with automatic delays between them.

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <rect class="bar" x="30" y="160" width="25" height="0" fill="#3498db" />
  <rect class="bar" x="65" y="160" width="25" height="0" fill="#2ecc71" />
  <rect class="bar" x="100" y="160" width="25" height="0" fill="#e74c3c" />
  <rect class="bar" x="135" y="160" width="25" height="0" fill="#f39c12" />
  <rect class="bar" x="170" y="160" width="25" height="0" fill="#9b59b6" />
  <rect class="bar" x="205" y="160" width="25" height="0" fill="#1abc9c" />
  <rect class="bar" x="240" y="160" width="25" height="0" fill="#e67e22" />
</svg>

<script>
  gsap.to(".bar", {
    height: (i) => 40 + Math.random() * 100,
    y: (i, el) => -(40 + Math.random() * 100),
    duration: 0.8,
    ease: "back.out(1.7)",
    stagger: 0.1,
  });
</script>
```

Visually: Seven colored bars grow upward from the bottom one after another (0.1s apart), each to a random height with a bouncy overshoot — like a bar chart animating in.

### Stagger Options

```typescript
gsap.to(".dot", {
  scale: 1.5,
  stagger: {
    each: 0.1, // time between each
    from: "center", // start from middle elements
    grid: "auto", // auto-detect grid layout
    ease: "power2.in", // easing of the stagger timing itself
  },
});
```

## ScrollTrigger

Trigger animations based on scroll position.

```html
<svg id="infographic" width="600" height="400" viewBox="0 0 600 400" style="margin-top: 100vh;">
  <rect class="chart-bar" x="50" y="350" width="60" height="0" fill="#3498db" />
  <rect class="chart-bar" x="130" y="350" width="60" height="0" fill="#2ecc71" />
  <rect class="chart-bar" x="210" y="350" width="60" height="0" fill="#e74c3c" />
  <rect class="chart-bar" x="290" y="350" width="60" height="0" fill="#f39c12" />
  <path
    id="chart-line"
    d="M 80,300 L 160,200 L 240,250 L 320,100 L 400,150 L 480,50"
    fill="none"
    stroke="#9b59b6"
    stroke-width="3"
  />
</svg>

<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
<script>
  gsap.registerPlugin(ScrollTrigger);

  gsap.to(".chart-bar", {
    height: (i) => [150, 220, 180, 280][i],
    y: (i) => -[150, 220, 180, 280][i],
    duration: 1,
    ease: "power2.out",
    stagger: 0.15,
    scrollTrigger: {
      trigger: "#infographic",
      start: "top 80%", // when top of SVG hits 80% of viewport
      toggleActions: "play none none reverse",
    },
  });

  // Line drawing on scroll
  const line = document.querySelector("#chart-line");
  const length = line.getTotalLength();
  gsap.set("#chart-line", { strokeDasharray: length, strokeDashoffset: length });

  gsap.to("#chart-line", {
    strokeDashoffset: 0,
    duration: 2,
    ease: "none",
    scrollTrigger: {
      trigger: "#infographic",
      start: "top 60%",
      end: "bottom 40%",
      scrub: true, // ties animation progress to scroll position
    },
  });
</script>
```

Visually: As you scroll down, bars grow upward with staggered timing. The purple line draws itself proportionally to scroll position — scroll halfway, line is half drawn.

## DrawSVGPlugin — Line Drawing

GSAP's premium plugin for line drawing (free with Club GreenSock, or use the stroke-dashoffset technique for free).

```typescript
gsap.registerPlugin(DrawSVGPlugin);

// Draw from nothing to full
gsap.fromTo("#my-path", { drawSVG: "0%" }, { drawSVG: "100%", duration: 2 });

// Draw a segment
gsap.to("#my-path", { drawSVG: "20% 80%", duration: 1.5 });

// Animate segment position (like a snake)
gsap.fromTo("#my-path", { drawSVG: "0% 0%" }, { drawSVG: "0% 100%", duration: 2 });
```

Free alternative using stroke-dashoffset:

```typescript
const path = document.querySelector("#my-path");
const length = path.getTotalLength();

gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
gsap.to(path, { strokeDashoffset: 0, duration: 2, ease: "power2.inOut" });
```

### Multi-Path Line Drawing

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <path
    class="draw-path"
    d="M 20,100 C 20,20 140,20 150,100"
    fill="none"
    stroke="#3498db"
    stroke-width="3"
  />
  <path
    class="draw-path"
    d="M 150,100 C 160,180 280,180 280,100"
    fill="none"
    stroke="#e74c3c"
    stroke-width="3"
  />
  <path
    class="draw-path"
    d="M 280,100 L 280,180 L 200,180"
    fill="none"
    stroke="#2ecc71"
    stroke-width="3"
  />
</svg>

<script>
  document.querySelectorAll(".draw-path").forEach((path) => {
    const length = path.getTotalLength();
    gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
  });

  const tl = gsap.timeline();
  document.querySelectorAll(".draw-path").forEach((path, i) => {
    tl.to(path, { strokeDashoffset: 0, duration: 1, ease: "none" }, i * 0.8);
  });
</script>
```

Visually: Three connected path segments draw themselves one after another — blue curve, then red curve, then green line — like a continuous pen stroke.

## MorphSVGPlugin — Shape Morphing

Smoothly morph between any two SVG shapes (Club GreenSock plugin).

```typescript
gsap.registerPlugin(MorphSVGPlugin);

// Morph circle to star
gsap.to("#circle", {
  morphSVG: "#star",
  duration: 1.5,
  ease: "power2.inOut",
});

// Morph with path string
gsap.to("#shape", {
  morphSVG: "M 100,20 L 180,180 L 20,180 Z",
  duration: 1,
});
```

```html
<svg width="200" height="200" viewBox="0 0 200 200">
  <path id="morph-shape" d="M 100,20 A 80,80 0 1,1 99.9,20" fill="#3498db" />
  <path
    id="target-star"
    d="M 100,10 L 120,75 L 190,75 L 135,115 L 155,180 L 100,140 L 45,180 L 65,115 L 10,75 L 80,75 Z"
    fill="none"
    style="visibility:hidden"
  />
</svg>

<script>
  gsap.to("#morph-shape", {
    morphSVG: "#target-star",
    duration: 2,
    ease: "elastic.out(1, 0.5)",
    repeat: -1,
    yoyo: true,
    repeatDelay: 0.5,
  });
</script>
```

Visually: A blue circle morphs into a star shape with an elastic bounce, pauses, then morphs back. The plugin intelligently maps points between the two shapes.

## MotionPathPlugin — Follow a Path

Move elements along SVG paths (free plugin).

```html
<svg width="400" height="300" viewBox="0 0 400 300">
  <path
    id="flight-path"
    d="M 20,250 C 100,50 300,50 380,250"
    fill="none"
    stroke="#ddd"
    stroke-width="1"
    stroke-dasharray="5,5"
  />
  <circle id="plane" cx="0" cy="0" r="8" fill="#e74c3c" />
</svg>

<script>
  gsap.registerPlugin(MotionPathPlugin);

  gsap.to("#plane", {
    motionPath: {
      path: "#flight-path",
      align: "#flight-path",
      autoRotate: true,
      alignOrigin: [0.5, 0.5],
    },
    duration: 3,
    ease: "power1.inOut",
    repeat: -1,
  });
</script>
```

Visually: A red dot following a curved arc path (shown as a dashed line), rotating to face the direction of travel — like a plane following a flight path.

### Motion Path with Timeline

```typescript
const tl = gsap.timeline({ repeat: -1 });

tl.to("#element", {
  motionPath: {
    path: [
      { x: 100, y: 0 },
      { x: 200, y: -50 },
      { x: 300, y: 0 },
    ],
    curviness: 1.5,
  },
  duration: 2,
  ease: "none",
}).to("#element", {
  scale: 0,
  opacity: 0,
  duration: 0.5,
});
```

## SplitText for SVG Text Animations

Animate individual characters in SVG text (Club GreenSock plugin):

```html
<svg width="400" height="100" viewBox="0 0 400 100">
  <text
    id="title"
    x="200"
    y="60"
    text-anchor="middle"
    font-size="32"
    font-family="sans-serif"
    fill="#333"
  >
    Hello World
  </text>
</svg>

<script>
  // For SVG text, wrap in foreignObject or use character-by-character approach
  const text = document.querySelector("#title");
  const chars = text.textContent.split("");
  text.textContent = "";

  chars.forEach((char, i) => {
    const tspan = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
    tspan.textContent = char === " " ? "\u00A0" : char;
    tspan.classList.add("char");
    text.appendChild(tspan);
  });

  gsap.from(".char", {
    opacity: 0,
    y: 20,
    duration: 0.5,
    stagger: 0.05,
    ease: "back.out(1.7)",
  });
</script>
```

Visually: "Hello World" appears letter by letter, each character dropping in from above with a slight bounce.

## Complete Example: Animated Dashboard

```html
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        display: grid;
        place-items: center;
        min-height: 100vh;
        background: #1a1a2e;
      }
    </style>
  </head>
  <body>
    <svg width="500" height="350" viewBox="0 0 500 350">
      <!-- Background -->
      <rect width="500" height="350" rx="20" fill="#16213e" />

      <!-- Title -->
      <text
        id="dash-title"
        x="250"
        y="40"
        text-anchor="middle"
        font-size="18"
        fill="white"
        opacity="0"
      >
        Analytics
      </text>

      <!-- Bar chart -->
      <g id="bars">
        <rect class="data-bar" x="60" y="280" width="40" height="0" fill="#0f3460" />
        <rect class="data-bar" x="120" y="280" width="40" height="0" fill="#0f3460" />
        <rect class="data-bar" x="180" y="280" width="40" height="0" fill="#0f3460" />
        <rect class="data-bar" x="240" y="280" width="40" height="0" fill="#0f3460" />
        <rect class="data-bar" x="300" y="280" width="40" height="0" fill="#0f3460" />
      </g>

      <!-- Line chart -->
      <path
        id="trend-line"
        d="M 60,200 L 130,160 L 200,180 L 270,120 L 340,140 L 410,80"
        fill="none"
        stroke="#e94560"
        stroke-width="3"
        stroke-linecap="round"
      />

      <!-- Dots on line -->
      <circle class="data-dot" cx="60" cy="200" r="0" fill="#e94560" />
      <circle class="data-dot" cx="130" cy="160" r="0" fill="#e94560" />
      <circle class="data-dot" cx="200" cy="180" r="0" fill="#e94560" />
      <circle class="data-dot" cx="270" cy="120" r="0" fill="#e94560" />
      <circle class="data-dot" cx="340" cy="140" r="0" fill="#e94560" />
      <circle class="data-dot" cx="410" cy="80" r="0" fill="#e94560" />

      <!-- Percentage circle -->
      <circle cx="420" cy="220" r="45" fill="none" stroke="#0f3460" stroke-width="8" />
      <circle
        id="progress-ring"
        cx="420"
        cy="220"
        r="45"
        fill="none"
        stroke="#533483"
        stroke-width="8"
        stroke-linecap="round"
        stroke-dasharray="283"
        stroke-dashoffset="283"
        transform="rotate(-90, 420, 220)"
      />
      <text
        id="percent-text"
        x="420"
        y="225"
        text-anchor="middle"
        font-size="16"
        fill="white"
        opacity="0"
      >
        73%
      </text>
    </svg>

    <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
    <script>
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } });
      const barHeights = [120, 180, 90, 200, 150];

      // Title fade in
      tl.to("#dash-title", { opacity: 1, y: -5, duration: 0.6 })

        // Bars grow up
        .to(
          ".data-bar",
          {
            height: (i) => barHeights[i],
            y: (i) => -barHeights[i],
            fill: (i) => ["#533483", "#0f3460", "#e94560", "#533483", "#0f3460"][i],
            duration: 0.8,
            stagger: 0.1,
          },
          "-=0.3",
        )

        // Line draws
        .fromTo(
          "#trend-line",
          { strokeDasharray: 500, strokeDashoffset: 500 },
          { strokeDashoffset: 0, duration: 1.5, ease: "none" },
          "-=0.5",
        )

        // Dots pop in
        .to(".data-dot", { r: 5, duration: 0.3, stagger: 0.1 }, "-=0.8")

        // Progress ring fills
        .to("#progress-ring", { strokeDashoffset: 283 * 0.27, duration: 1.2 }, "-=0.5")
        .to("#percent-text", { opacity: 1, duration: 0.4 }, "-=0.5");
    </script>
  </body>
</html>
```

Visually: A dark dashboard that animates in sequence: title fades in, colored bars grow upward with stagger, a red trend line draws itself, dots pop onto the line, and a circular progress indicator fills to 73%.

## Easing Reference

```typescript
// Built-in eases
"none"; // linear
"power1.out"; // subtle deceleration
"power2.inOut"; // smooth acceleration/deceleration
"back.out(1.7)"; // overshoot then settle
"elastic.out(1, 0.3)"; // springy bounce
"bounce.out"; // ball-drop bounce
"steps(5)"; // 5 discrete steps

// Custom ease
gsap.to("#el", { x: 100, ease: "M0,0 C0.5,0 0.5,1 1,1" });
```

## Key Takeaways

- `gsap.to/from/fromTo` are the building blocks — animate any SVG attribute
- Timelines (`gsap.timeline()`) sequence animations with precise overlap control
- `stagger` animates arrays of elements with automatic delays
- ScrollTrigger ties animations to scroll position (scrub for 1:1 mapping)
- DrawSVGPlugin simplifies line drawing (or use strokeDashoffset for free)
- MorphSVGPlugin morphs between any two shapes
- MotionPathPlugin moves elements along SVG paths
- GSAP handles SVG transform quirks automatically (transform-origin, etc.)
