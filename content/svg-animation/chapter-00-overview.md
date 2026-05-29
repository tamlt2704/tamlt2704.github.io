# SVG Animation: From Basics to Production

[next: SVG Basics](./chapter-01-svg-basics.md)

SVG animation brings vector graphics to life on the web. Unlike raster animations, SVG animations are resolution-independent, accessible, and performant. This course takes you from raw SVG markup to production-ready animations using industry-standard libraries.

## What You Will Learn

1. [SVG Basics](./chapter-01-svg-basics.md) — Coordinate systems, shapes, paths, transforms
2. [CSS Animation](./chapter-02-css-animation.md) — Keyframes, transitions, line drawing effects
3. [SMIL](./chapter-03-smil.md) — Native SVG animation elements
4. [GSAP](./chapter-04-gsap.md) — The industry-standard animation library
5. [Framer Motion](./chapter-05-framer-motion.md) — React-native SVG animations
6. [Lottie](./chapter-06-lottie.md) — After Effects to web pipeline
7. [Advanced Techniques](./chapter-07-techniques.md) — Morphing, particles, filters, masks
8. [Projects](./chapter-08-projects.md) — Complete real-world animation projects

## Libraries Covered

| Library       | Best For                                                              | Learning Curve            |
| ------------- | --------------------------------------------------------------------- | ------------------------- |
| Raw SVG/CSS   | Simple hover effects, loading spinners, icon animations               | Low                       |
| GSAP          | Complex timelines, scroll animations, morphing, professional projects | Medium                    |
| Framer Motion | React apps, page transitions, gesture-driven animations               | Medium                    |
| Lottie        | Designer-created animations, complex illustrations, brand animations  | Low (dev) / High (design) |
| anime.js      | Lightweight timeline animations, staggered effects                    | Low                       |
| SVG.js        | Programmatic SVG creation and manipulation                            | Medium                    |

## When to Use Each

**Raw SVG + CSS** — Use when you need simple animations without adding dependencies. Ideal for loading spinners, hover effects on icons, and subtle UI transitions. Works everywhere, zero bundle cost.

**GSAP** — Use for complex, precisely-timed animations that need to work across browsers. Scroll-triggered animations, morphing between shapes, motion along paths. The go-to for marketing sites and interactive experiences.

**Framer Motion** — Use in React applications where animations are tied to component lifecycle. Page transitions, layout animations, gesture responses. Declarative API fits React mental model.

**Lottie** — Use when designers create animations in After Effects and you need pixel-perfect playback on web. Brand animations, onboarding illustrations, micro-interactions designed by motion designers.

**anime.js** — Use for lightweight timeline-based animations when GSAP is overkill. Staggered animations, simple morphing, property-based animations. Small bundle size (~17KB).

**SVG.js** — Use when you need to programmatically create and manipulate SVG elements. Dynamic charts, generative art, interactive diagrams where SVG structure changes at runtime.

## Prerequisites

- HTML and CSS fundamentals
- Basic JavaScript/TypeScript
- For Framer Motion chapter: React basics
- A modern browser (Chrome, Firefox, Safari, Edge)

## Setup

No build tools required for most examples. Create an HTML file and open it in your browser:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>SVG Animation</title>
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
    <svg width="200" height="200" viewBox="0 0 200 200">
      <!-- Your SVG animation here -->
    </svg>
  </body>
</html>
```

For GSAP, add the CDN link:

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
```

For Framer Motion, use a React project:

```typescript
npm create vite@latest my-svg-app -- --template react-ts
cd my-svg-app
npm install framer-motion
```

Let's begin with the fundamentals of SVG itself.
