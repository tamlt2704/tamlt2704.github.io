# Chapter 13: Morph the Menu Icon to X — SVG Morphing

[← Chapter 12: Event-Driven Animation](chapter-12-event-driven.md) | [Chapter 14: Spring Physics →](chapter-14-spring-physics.md)

---

## The Brief

The mobile navigation uses a hamburger icon (three horizontal lines). When tapped, it should morph into an X (close icon). Not a swap — a smooth transformation where the lines rotate and reposition into the X shape.

Mika's spec:
> "Top line rotates 45° clockwise and moves down. Bottom line rotates -45° and moves up. Middle line fades out. The whole thing takes 300ms. Mechanical easing."

---

## The Hamburger SVG

```html
<button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false">
  <svg viewBox="0 0 24 24" width="24" height="24" class="menu-icon">
    <line class="menu-line menu-line-top" x1="4" y1="6" x2="20" y2="6"
      stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    <line class="menu-line menu-line-middle" x1="4" y1="12" x2="20" y2="12"
      stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    <line class="menu-line menu-line-bottom" x1="4" y1="18" x2="20" y2="18"
      stroke="currentColor" stroke-width="2" stroke-linecap="round" />
  </svg>
</button>
```

Three lines: top at y=6, middle at y=12, bottom at y=18. Each is 16px wide (x1=4 to x2=20).

---

## The Morph Animation

```javascript
const menuToggle = document.querySelector('.menu-toggle');
let isOpen = false;
let morphAnim = null;

menuToggle.addEventListener('click', () => {
  isOpen = !isOpen;
  menuToggle.setAttribute('aria-expanded', isOpen);

  if (morphAnim) morphAnim.pause();

  if (isOpen) {
    morphAnim = anime.timeline({
      duration: 300,
      easing: 'cubicBezier(0.4, 0, 0.2, 1)',
    })
    .add({
      targets: '.menu-line-top',
      translateY: 6,    // Move down to center (y6 → y12)
      rotate: 45,       // Rotate clockwise
    }, 0)
    .add({
      targets: '.menu-line-middle',
      opacity: 0,
      scale: 0,
    }, 0)
    .add({
      targets: '.menu-line-bottom',
      translateY: -6,   // Move up to center (y18 → y12)
      rotate: -45,      // Rotate counter-clockwise
    }, 0);
  } else {
    morphAnim = anime.timeline({
      duration: 300,
      easing: 'cubicBezier(0.4, 0, 0.2, 1)',
    })
    .add({
      targets: '.menu-line-top',
      translateY: 0,
      rotate: 0,
    }, 0)
    .add({
      targets: '.menu-line-middle',
      opacity: 1,
      scale: 1,
    }, 0)
    .add({
      targets: '.menu-line-bottom',
      translateY: 0,
      rotate: 0,
    }, 0);
  }
});
```

All three lines animate simultaneously (offset 0). The top and bottom converge at the center and cross. The middle fades out. 300ms total.

---

## SVG Path Morphing

For more complex shape transformations, animate the `d` attribute of SVG paths:

```html
<svg viewBox="0 0 100 100">
  <path class="morph-shape" d="M20,20 L80,20 L80,80 L20,80 Z" fill="#c8a864" />
</svg>
```

```javascript
anime({
  targets: '.morph-shape',
  d: [
    { value: 'M20,20 L80,20 L80,80 L20,80 Z' },          // Square
    { value: 'M50,10 L90,50 L50,90 L10,50 Z' },           // Diamond
    { value: 'M50,10 L61,35 L90,35 L67,55 L78,80 L50,65 L22,80 L33,55 L10,35 L39,35 Z' },  // Star
  ],
  duration: 2000,
  easing: 'easeInOutQuad',
  direction: 'alternate',
  loop: true,
});
```

### The Point Count Rule

For path morphing to work smoothly, both paths should have the **same number of points and commands**:

```javascript
// ✅ Same structure: 4 points, all L commands
'M20,20 L80,20 L80,80 L20,80 Z'  // Square
'M50,10 L90,50 L50,90 L10,50 Z'  // Diamond

// ❌ Different structure: won't morph smoothly
'M20,20 L80,20 L80,80 L20,80 Z'           // 4 points
'M50,10 L90,50 L50,90 Z'                   // 3 points (triangle)
```

If point counts differ, Anime.js will still animate but the result looks glitchy — points appear/disappear rather than smoothly transitioning.

---

## Matching Point Counts

To morph between shapes with different natural point counts, add extra points to the simpler shape:

```javascript
// Triangle (3 points) → add a duplicate point to make 4
// Original: M50,10 L90,90 L10,90 Z
// With extra point: M50,10 L90,90 L50,90 L10,90 Z

const shapes = {
  square: 'M20,20 L80,20 L80,80 L20,80 Z',
  triangle: 'M50,10 L80,80 L50,80 L20,80 Z',  // Extra point at bottom center
  diamond: 'M50,10 L90,50 L50,90 L10,50 Z',
};

anime({
  targets: '.morph-shape',
  d: [
    { value: shapes.square },
    { value: shapes.diamond },
    { value: shapes.triangle },
  ],
  duration: 1500,
  easing: 'easeInOutQuad',
  direction: 'alternate',
  loop: true,
});
```

---

## The Play/Pause Icon Morph

A common UI pattern — play triangle morphs to pause bars:

```html
<svg viewBox="0 0 24 24" class="play-pause-icon">
  <path class="play-pause-path-left"
    d="M6,4 L6,4 L6,20 L6,20 Z" fill="currentColor" />
  <path class="play-pause-path-right"
    d="M18,4 L18,4 L18,20 L18,20 Z" fill="currentColor" />
</svg>
```

```javascript
const paths = {
  play: {
    left: 'M6,4 L6,4 L12,12 L6,20 Z',
    right: 'M12,12 L12,12 L18,12 L12,12 Z',  // Collapsed (invisible)
  },
  pause: {
    left: 'M6,4 L10,4 L10,20 L6,20 Z',
    right: 'M14,4 L18,4 L18,20 L14,20 Z',
  },
};

let isPlaying = false;

function togglePlayPause() {
  isPlaying = !isPlaying;
  const target = isPlaying ? paths.pause : paths.play;

  anime({
    targets: '.play-pause-path-left',
    d: target.left,
    duration: 300,
    easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  });

  anime({
    targets: '.play-pause-path-right',
    d: target.right,
    duration: 300,
    easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  });
}
```

Two paths morph simultaneously — the play triangle splits into two pause bars.

---

## Logo Morphing

The watchmaker's logo morphs between two states — the full logo and a simplified monogram:

```javascript
const logoStates = {
  full: 'M10,50 C10,20 30,5 50,5 C70,5 90,20 90,50 C90,80 70,95 50,95 C30,95 10,80 10,50',
  monogram: 'M30,20 L50,5 L70,20 L70,80 L50,95 L30,80 Z',
};

// Morph on scroll (logo simplifies as user scrolls down)
let lastScrollY = 0;

window.addEventListener('scroll', () => {
  const scrolled = window.scrollY > 100;

  if (scrolled && lastScrollY <= 100) {
    anime({
      targets: '.logo-path',
      d: logoStates.monogram,
      duration: 400,
      easing: 'cubicBezier(0.4, 0, 0.2, 1)',
    });
  } else if (!scrolled && lastScrollY > 100) {
    anime({
      targets: '.logo-path',
      d: logoStates.full,
      duration: 400,
      easing: 'cubicBezier(0.4, 0, 0.2, 1)',
    });
  }

  lastScrollY = window.scrollY;
}, { passive: true });
```

The logo simplifies as the user scrolls — full logo at the top, compact monogram when scrolled. A common pattern for sticky headers.

---

## Morphing with Color

Combine shape morphing with color transitions:

```javascript
anime.timeline({ easing: 'easeInOutQuad', duration: 800 })
  .add({
    targets: '.morph-shape',
    d: shapes.diamond,
    fill: '#c8a864',  // Gold
  })
  .add({
    targets: '.morph-shape',
    d: shapes.circle,
    fill: '#2496ed',  // Blue
  })
  .add({
    targets: '.morph-shape',
    d: shapes.square,
    fill: '#e74c3c',  // Red
  });
```

Shape and color change together — each state has a distinct identity.

---

## Complex Morphing: Using Libraries

For morphing between paths with very different structures (different point counts, different commands), consider preprocessing with a library like Flubber:

```javascript
import { interpolate } from 'flubber';

const circle = 'M50,10 A40,40 0 1,1 50,90 A40,40 0 1,1 50,10';
const star = 'M50,0 L61,35 L98,35 L68,57 L79,91 L50,70 L21,91 L32,57 L2,35 L39,35 Z';

const interpolator = interpolate(circle, star);

const state = { t: 0 };

anime({
  targets: state,
  t: 1,
  duration: 1000,
  easing: 'easeInOutQuad',
  update: () => {
    document.querySelector('.morph-path').setAttribute('d', interpolator(state.t));
  },
});
```

Flubber handles point matching and produces smooth intermediate shapes. Anime.js drives the timing. Best of both worlds.

---

## Accessibility for Morphing Icons

Screen readers need to know what the icon represents:

```html
<button class="menu-toggle" aria-label="Open menu" aria-expanded="false">
  <svg aria-hidden="true">...</svg>
</button>
```

```javascript
menuToggle.addEventListener('click', () => {
  isOpen = !isOpen;
  menuToggle.setAttribute('aria-expanded', isOpen);
  menuToggle.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
  // ... morph animation
});
```

The visual morph is decorative — the `aria-label` communicates the actual state change.

---

## What You Learned

- **Line-based morphing** — translate + rotate SVG lines (hamburger → X)
- **Path morphing** — animate the `d` attribute between shapes
- **Point count rule** — same number of points for smooth morphing
- **Adding points** — pad simpler shapes to match complex ones
- **Play/pause morph** — two paths splitting/merging
- **Scroll-triggered morph** — logo simplification on scroll
- **Color + shape** — combined transitions for distinct states
- **Flubber** — library for complex mismatched morphs
- **Accessibility** — aria-label updates for state changes

The hamburger morphs to X. The logo simplifies on scroll. Shapes transform fluidly between states. SVG morphing adds a layer of polish that makes interactions feel crafted.

Next: spring physics. When `easeOutCubic` isn't enough and elements need to feel like they have mass and elasticity.

---

[← Chapter 12: Event-Driven Animation](chapter-12-event-driven.md) | [Chapter 14: Spring Physics →](chapter-14-spring-physics.md)
