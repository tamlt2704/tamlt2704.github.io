# Chapter 16: It's 24fps on the Client's iPad — Performance

[← Chapter 15: Responsive Animation](chapter-15-responsive-animation.md) | [Chapter 17: Framework Integration →](chapter-17-framework-integration.md)

---

## The Problem

The client opens the site on their iPad Pro. The watch assembly stutters. The scroll reveals jank. The bezel light trace drops frames. On your MacBook Pro with a 120Hz display, everything was butter.

Theo: "Fix it. The client presents to their board next week. On that iPad."

---

## Why Animations Jank

The browser renders at 60fps (16.67ms per frame). If any frame takes longer than 16.67ms, it drops — causing visible stutter.

What happens each frame:

```
JavaScript → Style → Layout → Paint → Composite
   ↓           ↓        ↓        ↓         ↓
 anime.js   Calculate  Calculate  Draw     Combine
 updates    CSS rules  positions  pixels   layers
```

**Composite-only properties** (transform, opacity) skip Layout and Paint — they're handled entirely by the GPU. Everything else triggers expensive recalculations.

---

## The Performance Hierarchy

```
FAST (composite only — GPU):
├── transform: translateX/Y/Z
├── transform: scale
├── transform: rotate
└── opacity

MEDIUM (paint — CPU):
├── color
├── background-color
├── box-shadow
├── border-radius
└── border-color

SLOW (layout — CPU + reflow):
├── width / height
├── top / left / right / bottom
├── margin / padding
├── font-size
└── display
```

### The Rule

```javascript
// ❌ Triggers layout every frame (SLOW)
anime({
  targets: '.card',
  width: '300px',
  height: '200px',
  top: '100px',
  left: '200px',
});

// ✅ Composite only (FAST)
anime({
  targets: '.card',
  translateX: 200,
  translateY: 100,
  scale: 1.5,
  opacity: 1,
});
```

If you can express the animation with `transform` and `opacity`, do it. Always.

---

## Diagnosing Jank

### Chrome DevTools Performance Panel

1. Open DevTools → Performance tab
2. Click Record
3. Trigger the animation
4. Stop recording
5. Look for:
   - Red bars = dropped frames
   - Long "Layout" blocks = layout thrashing
   - Long "Paint" blocks = expensive repaints

### The FPS Counter

```javascript
// Quick FPS monitor
let frameCount = 0;
let lastTime = performance.now();
const fpsDisplay = document.createElement('div');
fpsDisplay.style.cssText = 'position:fixed;top:0;left:0;background:#000;color:#0f0;padding:4px 8px;font:12px monospace;z-index:99999';
document.body.appendChild(fpsDisplay);

function measureFPS() {
  frameCount++;
  const now = performance.now();
  if (now - lastTime >= 1000) {
    fpsDisplay.textContent = `${frameCount} fps`;
    frameCount = 0;
    lastTime = now;
  }
  requestAnimationFrame(measureFPS);
}
measureFPS();
```

If it drops below 55fps during animation, you have a problem.

---

## will-change

Tell the browser to prepare a GPU layer for an element before it animates:

```css
.watch-dial,
.watch-hour-hand,
.watch-minute-hand,
.watch-strap {
  will-change: transform, opacity;
}
```

This promotes elements to their own compositor layer. The GPU can animate them without involving the CPU.

### Don't Overuse will-change

```css
/* ❌ Too many layers = memory bloat */
* { will-change: transform; }

/* ✅ Only on elements that actually animate */
.animated-element { will-change: transform, opacity; }
```

Each `will-change` layer consumes GPU memory. On the iPad with limited VRAM, too many layers cause worse performance than no layers.

### Remove After Animation

```javascript
anime({
  targets: '.card',
  translateY: [30, 0],
  opacity: [0, 1],
  duration: 600,
  begin: () => {
    document.querySelector('.card').style.willChange = 'transform, opacity';
  },
  complete: () => {
    document.querySelector('.card').style.willChange = 'auto';
  },
});
```

Promote before animation, demote after. Keeps memory usage low.

---

## Reducing Animation Complexity

### Fewer Simultaneous Animations

```javascript
// ❌ 20 elements animating simultaneously
anime({
  targets: '.grid-item',  // 20 items
  translateY: [30, 0],
  opacity: [0, 1],
  scale: [0.9, 1],
  rotate: [5, 0],
  delay: anime.stagger(30),  // All start within 600ms
});

// ✅ Stagger more aggressively — fewer concurrent animations
anime({
  targets: '.grid-item',
  translateY: [20, 0],
  opacity: [0, 1],
  delay: anime.stagger(100),  // Spread over 2000ms
  duration: 400,              // Each finishes quickly
});
```

At any given moment, fewer elements are mid-animation. The GPU handles 3–5 concurrent transforms easily. 20 is a strain.

### Simpler Properties

```javascript
// ❌ box-shadow animates on CPU (expensive)
anime({
  targets: '.card',
  boxShadow: ['0 2px 4px rgba(0,0,0,0.1)', '0 20px 40px rgba(0,0,0,0.3)'],
});

// ✅ Use a pseudo-element with opacity for shadow
// CSS:
// .card::after { content: ''; box-shadow: 0 20px 40px rgba(0,0,0,0.3); opacity: 0; }
anime({
  targets: '.card::after',  // Won't work directly — use a real element
  opacity: [0, 1],          // Opacity is composite-only
});
```

Better approach for animated shadows:

```html
<div class="card">
  <div class="card-shadow"></div>
  <!-- content -->
</div>
```

```css
.card-shadow {
  position: absolute;
  inset: 0;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
  opacity: 0;
  border-radius: inherit;
  pointer-events: none;
}
```

```javascript
// Animate shadow opacity (GPU) instead of shadow itself (CPU)
card.addEventListener('mouseenter', () => {
  anime({ targets: card.querySelector('.card-shadow'), opacity: 1, duration: 300 });
  anime({ targets: card, translateY: -8, duration: 300 });
});
```

---

## Batching DOM Reads and Writes

The `update` callback runs every frame. Avoid layout thrashing:

```javascript
// ❌ Read + write in update = layout thrashing
update: () => {
  const rect = el.getBoundingClientRect();  // READ (forces layout)
  el.style.left = rect.left + 10 + 'px';   // WRITE (invalidates layout)
}

// ✅ Only write in update (reads cached outside)
const startPos = el.getBoundingClientRect();  // Read once before animation

anime({
  targets: state,
  progress: 1,
  update: () => {
    el.style.transform = `translateX(${state.progress * 100}px)`;  // Write only
  },
});
```

---

## Reducing Paint Area

When an element changes, the browser repaints the affected area. Smaller paint areas = faster frames.

```css
/* Isolate animated elements in their own layer */
.animated-section {
  isolation: isolate;  /* Creates a new stacking context */
  contain: layout paint;  /* Limits repaint to this element */
}
```

`contain: layout paint` tells the browser that changes inside this element don't affect anything outside. Repaints are contained.

---

## The iPad Fix

After profiling, the issues on the iPad were:

1. **Watch assembly**: 5 elements with `will-change` simultaneously → too many layers
2. **Scroll reveals**: 12 cards animating `box-shadow` → CPU paint
3. **Bezel light**: `box-shadow` glow animating every frame → CPU paint

Fixes:

```javascript
// 1. Promote layers only during animation
const watchTimeline = anime.timeline({
  begin: () => {
    document.querySelectorAll('.watch-part').forEach(el => {
      el.style.willChange = 'transform, opacity';
    });
  },
  complete: () => {
    document.querySelectorAll('.watch-part').forEach(el => {
      el.style.willChange = 'auto';
    });
  },
});

// 2. Remove box-shadow animation, use opacity on shadow element
// (shown above)

// 3. Bezel light: use a static glow, only animate transform
```

```css
.bezel-light {
  /* Static glow — no animation on box-shadow */
  box-shadow: 0 0 10px #c8a864, 0 0 20px rgba(200, 168, 100, 0.5);
  will-change: transform;
}
```

The glow is always there — only the position animates (transform = GPU). No per-frame box-shadow recalculation.

---

## Animation Throttling on Low-End Devices

Detect device capability and reduce animation complexity:

```javascript
function getDeviceCapability() {
  // Rough heuristic based on hardware concurrency and memory
  const cores = navigator.hardwareConcurrency || 2;
  const memory = navigator.deviceMemory || 4;  // GB

  if (cores <= 2 || memory <= 2) return 'low';
  if (cores <= 4 || memory <= 4) return 'medium';
  return 'high';
}

const capability = getDeviceCapability();

const ANIMATION_CONFIG = {
  low: {
    maxConcurrent: 3,
    enableMotionPath: false,
    enableSVGDraw: false,
    staggerMultiplier: 0.5,  // Faster staggers
  },
  medium: {
    maxConcurrent: 8,
    enableMotionPath: true,
    enableSVGDraw: true,
    staggerMultiplier: 0.8,
  },
  high: {
    maxConcurrent: Infinity,
    enableMotionPath: true,
    enableSVGDraw: true,
    staggerMultiplier: 1,
  },
};
```

---

## Performance Checklist

Before shipping:

- [ ] All animations use `transform` and `opacity` only
- [ ] `will-change` applied only during animation, removed after
- [ ] No `box-shadow` or `border-radius` animations (use opacity tricks)
- [ ] No layout properties animated (`width`, `height`, `top`, `left`)
- [ ] `update` callbacks don't read DOM (no `getBoundingClientRect`)
- [ ] Scroll handlers use `{ passive: true }` and rAF throttle
- [ ] Maximum 5–8 concurrent animations on mobile
- [ ] `contain: layout paint` on animated sections
- [ ] Tested on target device (iPad) at 60fps
- [ ] `prefers-reduced-motion` respected

---

## What You Learned

- **Composite properties** — transform + opacity = GPU = fast
- **Layout properties** — width, height, top, left = CPU = slow
- **will-change** — promote to GPU layer (use sparingly)
- **Diagnosing jank** — DevTools Performance panel, FPS counter
- **Shadow trick** — animate opacity of shadow element, not shadow itself
- **Batching** — don't read DOM in update callbacks
- **contain** — limit repaint area
- **Device detection** — reduce complexity for low-end hardware
- **Concurrent limit** — fewer simultaneous animations on mobile

The iPad now runs at 60fps. The watch assembly is smooth. The scroll reveals don't stutter. Performance is invisible — when it's good, nobody notices. When it's bad, everyone does.

Next: integrating all of this with React components.

---

[← Chapter 15: Responsive Animation](chapter-15-responsive-animation.md) | [Chapter 17: Framework Integration →](chapter-17-framework-integration.md)
