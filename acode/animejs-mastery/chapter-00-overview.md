# Anime.js Mastery: A Web Animation Survival Story

You just joined **Lumina** — a creative agency that builds high-end marketing sites for luxury brands. The sites need to feel expensive. Smooth reveals. Orchestrated entrances. Scroll-driven storytelling. Micro-interactions that make visitors say "how did they do that?"

**Theo**, the creative director, shows you the brief for the next client — a Swiss watchmaker launching a new collection:

> "The hero section: the watch assembles itself piece by piece. The dial fades in, the hands rotate into position, the strap unfolds. Below that, specs animate as you scroll — numbers count up, progress rings fill. The navigation morphs on scroll. Every interaction has weight and intention."

He pulls up the current site you inherited from the previous developer:

> "Right now it's all CSS transitions. The timing is off. Nothing is coordinated. The stagger looks random, not intentional. CSS can't do spring physics. CSS can't sequence 15 elements with precise offsets. CSS can't animate along a path. We need a real animation engine."

He drops a link in Slack:

> "Anime.js. Lightweight. Powerful. Handles everything from simple fades to complex choreography. Learn it. The client presentation is in 2 weeks."

You open the docs. 14KB gzipped. No dependencies. A clean API. This might actually be fun.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Frontend Developer | "I know CSS transitions. `transition: all 0.3s ease`. Done, right?" |
| **Theo** | Creative Director | "Ease-in-out is not a personality. Every animation needs intention." |
| **Mika** | Motion Designer | Exports After Effects comps and expects pixel-perfect code. |
| **Client** | Swiss Watchmaker | "Our brand is precision. The animation must feel mechanical, not bouncy." |
| **The Jank** | Performance bug | 60fps on your monitor. 24fps on the client's iPad. |
| **The Timeline** | That one sequence | 15 elements, 8 seconds, every offset matters. |

---

## The Stack

| Tool | What It Does |
|---|---|
| **Anime.js v4** | Lightweight JS animation library (14KB) |
| **HTML/CSS** | DOM elements to animate |
| **SVG** | Paths, shapes, morphing |
| **JavaScript** | Orchestration, interactivity |
| **ScrollTrigger (custom)** | Scroll-driven animations |
| **Vite** | Dev server for examples |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Theo or Mika needs a specific animation for the client site
   │
   ▼
  🤔 You learn the Anime.js concept that enables it
   │
   ▼
  ⌨️  You build it
   │
   ▼
  💥 The timing is off, it janks, or it doesn't match the motion comp
   │
   ▼
  🧠 You understand WHY and refine it
   │
   ▼
  📋 Next animation
```

No concept shows up before you need it. You won't hear about timelines until you need to coordinate 10 elements. You won't touch spring physics until ease-in-out feels wrong. You won't learn about SVG path animation until the watch hands need to sweep.

The motion brief comes first. The code follows.

---

## The Roadmap

### Part 1: Foundations — "Move Things"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Animation                          │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ "Fade in the hero heading"             │ Anime.js basics — targets, properties, duration, easing
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ "The entrance feels robotic"           │ Easing functions — built-in, cubic-bezier, spring, elastic
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ "Animate from/to specific values"      │ Property parameters — from, to, keyframes, units
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ "Stagger the nav items on load"        │ Stagger — grid, from center, custom functions
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ "Loop the loading pulse forever"       │ Playback — loop, alternate, direction, autoplay
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Choreography — "Coordinate Things"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Animation                          │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ "Watch assembles: dial, hands, strap"  │ Timelines — add, sequence, overlap, offsets
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ "Numbers count up to specs"            │ Value animation — DOM attributes, object properties, round
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ "Progress ring fills to 87%"           │ SVG animation — stroke-dashoffset, attributes, transforms
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ "Watch hands sweep along the dial"     │ Motion path — SVG path following, rotation alignment
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ "Pause, play, scrub with a slider"     │ Controls — play(), pause(), seek(), reverse(), callbacks
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Interaction — "Respond to Things"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Animation                          │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ "Animate on scroll (reveal sections)"  │ Scroll-driven animation — IntersectionObserver + anime
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ "Button hover: scale + glow + ripple"  │ Event-driven animation — mouseenter, click, chaining
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ "Morph the menu icon to X"             │ SVG morphing — path data animation, point matching
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ "Drag to reorder, spring back"         │ Spring physics — stiffness, damping, velocity
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ "Responsive: different on mobile"      │ Responsive animation — matchMedia, reduced motion, resize
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 4: Production — "Ship Things"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Problem                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 16 │ "It's 24fps on the client's iPad"      │ Performance — transforms vs layout, GPU, batching
────┼────────────────────────────────────────┼──────────────────────────────────────
 17 │ "Integrate with React components"      │ Framework integration — refs, useEffect, cleanup, hooks
────┼────────────────────────────────────────┼──────────────────────────────────────
 18 │ "Match the After Effects comp exactly" │ Design handoff — timing sheets, easing curves, frame-by-frame
────┼────────────────────────────────────────┼──────────────────────────────────────
 19 │ "Accessibility: motion makes me dizzy" │ prefers-reduced-motion, fallbacks, progressive enhancement
────┼────────────────────────────────────────┼──────────────────────────────────────
 20 │ Client presentation: the full site     │ Animation system — naming, reuse, choreography principles
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## Why Anime.js?

Theo draws this on the whiteboard:

```
CSS Transitions:              Anime.js:
────────────────              ─────────
One property change           Complex sequences
No timeline                   Full timeline control
No stagger                    Stagger with functions
No spring physics             Spring, elastic, custom easing
No path animation             SVG motion paths
No value animation            Animate any JS value
No callbacks                  Complete, update, begin callbacks
Good for: hover states        Good for: everything else
```

```
GSAP:                         Anime.js:
─────                         ─────────
45KB (core)                   14KB (everything)
Plugin ecosystem              All-in-one
Commercial license ($)        MIT (free)
Industry standard             Lightweight alternative
ScrollTrigger plugin          Roll your own (or use libs)
More features                 Simpler API
```

> "GSAP is a Swiss Army knife. Anime.js is a scalpel. For what we're building, the scalpel is enough — and it's half the weight." — Dev Dani (who doesn't exist yet but should)

---

## What You'll Build

| Animation | Technique |
|---|---|
| Hero text fade + slide | Basic properties, easing |
| Staggered navigation entrance | Stagger with delay functions |
| Watch assembly sequence | Timeline with precise offsets |
| Counting numbers (specs) | Value animation, round |
| Progress ring fill | SVG stroke-dashoffset |
| Watch hand sweep | Motion path |
| Scroll-triggered reveals | IntersectionObserver + anime |
| Hamburger → X morph | SVG path morphing |
| Button micro-interactions | Event-driven, spring physics |
| Full landing page choreography | Coordinated timeline system |

---

## The API at a Glance (Preview)

```javascript
import anime from 'animejs';

// The simplest animation
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,
  easing: 'easeOutCubic',
});

// Stagger
anime({
  targets: '.nav-item',
  opacity: [0, 1],
  translateX: [-20, 0],
  delay: anime.stagger(100),  // 0ms, 100ms, 200ms, 300ms...
  easing: 'easeOutQuad',
});

// Timeline
const tl = anime.timeline({ easing: 'easeOutExpo' });

tl.add({ targets: '.dial', opacity: [0, 1], scale: [0.8, 1], duration: 600 })
  .add({ targets: '.hour-hand', rotate: [0, 210], duration: 1000 }, '-=200')
  .add({ targets: '.minute-hand', rotate: [0, 45], duration: 800 }, '-=600')
  .add({ targets: '.strap', scaleY: [0, 1], duration: 500 });

// SVG stroke drawing
anime({
  targets: '.logo-path',
  strokeDashoffset: [anime.setDashoffset, 0],
  duration: 2000,
  easing: 'easeInOutSine',
});
```

14KB. No plugins. That's the entire API surface you need for 90% of web animations.

---

## Prerequisites

### Node.js + Vite (for examples)

```bash
mkdir lumina-animations && cd lumina-animations
npm init -y
npm install animejs
npm install -D vite
```

### package.json script

```json
{
  "scripts": {
    "dev": "vite"
  }
}
```

### Starter HTML

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Anime.js Lab</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #0d0d0d;
      font-family: system-ui;
      color: white;
    }
    .box {
      width: 80px;
      height: 80px;
      background: #2496ed;
      border-radius: 8px;
    }
  </style>
</head>
<body>
  <div class="box"></div>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

### Verify

```javascript
// main.js
import anime from 'animejs';

anime({
  targets: '.box',
  translateX: 250,
  rotate: '1turn',
  duration: 2000,
  easing: 'easeInOutQuad',
  loop: true,
  direction: 'alternate',
});
```

```bash
npm run dev
```

If the blue box slides and rotates — you're ready.

---

## The Mindset: Animation is Communication

Theo's rule:

> "Every animation must answer: **why is this moving?**"

| Purpose | Example |
|---|---|
| **Guide attention** | Hero text fades in → user reads it first |
| **Show connection** | Card slides to list → user knows it was added |
| **Provide feedback** | Button pulses → user knows it was clicked |
| **Create hierarchy** | First element enters, others follow → establishes order |
| **Express brand** | Mechanical easing → precision (watchmaker). Bouncy → playful (toy brand) |

Animation without purpose is decoration. Animation with purpose is communication.

---

## Anime.js v4 vs v3

This series uses **Anime.js v4** (latest). Key differences from v3:

| Feature | v3 | v4 |
|---|---|---|
| Import | `import anime from 'animejs'` | Same |
| Timelines | `anime.timeline()` | `anime.timeline()` |
| Stagger | `anime.stagger()` | `anime.stagger()` |
| ES Modules | Partial | Full |
| TypeScript | Community types | Built-in |
| Size | 17KB | 14KB |
| Performance | Good | Better (rAF batching) |

The API is nearly identical. If you've seen v3 examples online, they'll work with minor adjustments.

---

[Next: Chapter 1 — Your First Animation →](chapter-01-first-animation.md)
