# Chapter 2: CSS Animations on SVG

[prev: SVG Basics](./chapter-01-svg-basics.md) | [next: SMIL](./chapter-03-smil.md)

CSS animations work on SVG elements just like HTML elements. You can animate transforms, opacity, colors, stroke properties, and more. This is the simplest way to add motion to SVGs — no JavaScript required.

## Transitions

The simplest animation: smooth property changes on state change (hover, focus, class toggle).

```html
<svg width="200" height="200" viewBox="0 0 200 200">
  <style>
    .hover-circle {
      fill: #3498db;
      transition:
        fill 0.3s ease,
        r 0.3s ease;
    }
    .hover-circle:hover {
      fill: #e74c3c;
      r: 90;
    }
  </style>
  <circle class="hover-circle" cx="100" cy="100" r="70" />
</svg>
```

Visually: A blue circle that smoothly turns red and grows larger when you hover over it.

## @keyframes Animations

### Basic Pulse

```html
<svg width="200" height="200" viewBox="0 0 200 200">
  <style>
    .pulse {
      animation: pulse 2s ease-in-out infinite;
      transform-origin: center;
    }
    @keyframes pulse {
      0%,
      100% {
        transform: scale(1);
        opacity: 1;
      }
      50% {
        transform: scale(1.2);
        opacity: 0.7;
      }
    }
  </style>
  <circle class="pulse" cx="100" cy="100" r="50" fill="#e74c3c" />
</svg>
```

Visually: A red circle that rhythmically grows and fades, then shrinks back — like a heartbeat.

### Rotation

```html
<svg width="200" height="200" viewBox="0 0 200 200">
  <style>
    .spin {
      animation: rotate 3s linear infinite;
      transform-origin: 100px 100px;
    }
    @keyframes rotate {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }
  </style>
  <g class="spin">
    <rect x="80" y="30" width="40" height="40" rx="5" fill="#3498db" />
    <rect x="130" y="80" width="40" height="40" rx="5" fill="#e74c3c" />
    <rect x="80" y="130" width="40" height="40" rx="5" fill="#2ecc71" />
    <rect x="30" y="80" width="40" height="40" rx="5" fill="#f39c12" />
  </g>
</svg>
```

Visually: Four colored squares arranged in a diamond pattern, spinning continuously around the center.

## transform-origin

Critical for SVG animations. Unlike HTML, SVG elements default to `transform-origin: 0 0` (top-left of the SVG canvas), not the element's center.

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <style>
    .rotate-corner {
      animation: rotate 3s linear infinite;
      transform-origin: 50px 50px; /* top-left of the rect */
    }
    .rotate-center {
      animation: rotate 3s linear infinite;
      transform-origin: 200px 100px; /* center of the rect */
    }
    @keyframes rotate {
      to {
        transform: rotate(360deg);
      }
    }
  </style>
  <!-- Rotates around its top-left corner -->
  <rect class="rotate-corner" x="50" y="50" width="60" height="60" fill="#3498db" />

  <!-- Rotates around its center -->
  <rect class="rotate-center" x="170" y="70" width="60" height="60" fill="#e74c3c" />
</svg>
```

Visually: The blue square orbits around its corner (wide arc). The red square spins in place around its center.

## Line Drawing Effect (stroke-dasharray)

The most iconic SVG animation technique. By setting `stroke-dasharray` equal to the path length and animating `stroke-dashoffset` from that length to 0, the path appears to draw itself.

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <style>
    .draw {
      stroke-dasharray: 800;
      stroke-dashoffset: 800;
      animation: draw 3s ease forwards;
    }
    @keyframes draw {
      to {
        stroke-dashoffset: 0;
      }
    }
  </style>
  <path
    class="draw"
    d="M 20,100 C 20,20 140,20 150,100 C 160,180 280,180 280,100"
    fill="none"
    stroke="#e74c3c"
    stroke-width="4"
    stroke-linecap="round"
  />
</svg>
```

Visually: An S-curve that draws itself from left to right over 3 seconds, as if an invisible pen is tracing it.

### Line Drawing a Complex Shape

```html
<svg width="200" height="200" viewBox="0 0 100 100">
  <style>
    .draw-check {
      stroke-dasharray: 100;
      stroke-dashoffset: 100;
      animation: draw 0.8s ease forwards 0.3s;
    }
    .draw-circle {
      stroke-dasharray: 283;
      stroke-dashoffset: 283;
      animation: draw 1s ease forwards;
    }
    @keyframes draw {
      to {
        stroke-dashoffset: 0;
      }
    }
  </style>
  <!-- Circle draws first -->
  <circle
    class="draw-circle"
    cx="50"
    cy="50"
    r="45"
    fill="none"
    stroke="#2ecc71"
    stroke-width="3"
  />
  <!-- Checkmark draws after circle (0.3s delay) -->
  <path
    class="draw-check"
    d="M 25,50 L 45,70 L 75,30"
    fill="none"
    stroke="#2ecc71"
    stroke-width="4"
    stroke-linecap="round"
    stroke-linejoin="round"
  />
</svg>
```

Visually: A green circle draws itself, then a checkmark draws inside it — like a success confirmation animation.

### Getting the Path Length

To find the correct `stroke-dasharray` value, use JavaScript:

```typescript
const path = document.querySelector("path");
console.log(path.getTotalLength()); // e.g., 523.4
```

Or set a large value (like 1000) — if it's larger than the actual path, it still works.

## Hover Effects

### Icon Hover with Color and Scale

```html
<svg width="100" height="100" viewBox="0 0 24 24">
  <style>
    .icon-path {
      fill: #666;
      transition:
        fill 0.2s ease,
        transform 0.2s ease;
      transform-origin: 12px 12px;
    }
    svg:hover .icon-path {
      fill: #e74c3c;
      transform: scale(1.1);
    }
  </style>
  <!-- Heart icon -->
  <path
    class="icon-path"
    d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 
       2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 
       19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
  />
</svg>
```

Visually: A grey heart icon that turns red and slightly enlarges on hover.

### Stroke Draw on Hover

```html
<svg width="200" height="60" viewBox="0 0 200 60">
  <style>
    .btn-border {
      stroke-dasharray: 500;
      stroke-dashoffset: 500;
      transition: stroke-dashoffset 0.6s ease;
    }
    svg:hover .btn-border {
      stroke-dashoffset: 0;
    }
    .btn-text {
      fill: #333;
      font-family: sans-serif;
      font-size: 14px;
    }
  </style>
  <rect
    class="btn-border"
    x="2"
    y="2"
    width="196"
    height="56"
    rx="8"
    fill="none"
    stroke="#3498db"
    stroke-width="2"
  />
  <text class="btn-text" x="100" y="35" text-anchor="middle">Hover Me</text>
</svg>
```

Visually: Text with an invisible border. On hover, a blue border draws itself around the text like a pen tracing the rectangle.

## Loading Spinners

### Simple Rotating Spinner

```html
<svg width="50" height="50" viewBox="0 0 50 50">
  <style>
    .spinner {
      animation: rotate 1s linear infinite;
      transform-origin: 25px 25px;
    }
    @keyframes rotate {
      to {
        transform: rotate(360deg);
      }
    }
  </style>
  <circle
    class="spinner"
    cx="25"
    cy="25"
    r="20"
    fill="none"
    stroke="#3498db"
    stroke-width="4"
    stroke-dasharray="80"
    stroke-linecap="round"
  />
</svg>
```

Visually: A partial blue circle (arc) spinning continuously — the classic loading indicator.

### Pulsing Dots Loader

```html
<svg width="80" height="40" viewBox="0 0 80 40">
  <style>
    .dot {
      animation: bounce 1.4s ease-in-out infinite;
    }
    .dot:nth-child(1) {
      animation-delay: 0s;
    }
    .dot:nth-child(2) {
      animation-delay: 0.2s;
    }
    .dot:nth-child(3) {
      animation-delay: 0.4s;
    }
    @keyframes bounce {
      0%,
      80%,
      100% {
        transform: translateY(0);
        opacity: 0.4;
      }
      40% {
        transform: translateY(-15px);
        opacity: 1;
      }
    }
  </style>
  <circle class="dot" cx="20" cy="30" r="6" fill="#3498db" />
  <circle class="dot" cx="40" cy="30" r="6" fill="#3498db" />
  <circle class="dot" cx="60" cy="30" r="6" fill="#3498db" />
</svg>
```

Visually: Three blue dots bouncing up and down in sequence — each one jumps up as the previous one comes down.

### Circular Progress Spinner

```html
<svg width="60" height="60" viewBox="0 0 60 60">
  <style>
    .track {
      stroke: #eee;
    }
    .progress {
      stroke-dasharray: 150;
      stroke-dashoffset: 150;
      animation:
        fill-progress 2s ease forwards,
        rotate 1.5s linear infinite;
      transform-origin: 30px 30px;
    }
    @keyframes fill-progress {
      to {
        stroke-dashoffset: 0;
      }
    }
    @keyframes rotate {
      to {
        transform: rotate(360deg);
      }
    }
  </style>
  <circle class="track" cx="30" cy="30" r="24" fill="none" stroke-width="5" />
  <circle
    class="progress"
    cx="30"
    cy="30"
    r="24"
    fill="none"
    stroke="#2ecc71"
    stroke-width="5"
    stroke-linecap="round"
  />
</svg>
```

Visually: A grey circle track with a green arc that grows while spinning — combining progress indication with rotation.

## Animating Multiple Properties

```html
<svg width="300" height="200" viewBox="0 0 300 200">
  <style>
    .morph-rect {
      animation: morph 4s ease-in-out infinite;
    }
    @keyframes morph {
      0% {
        rx: 0;
        fill: #3498db;
        transform: translate(0, 0);
      }
      25% {
        rx: 50;
        fill: #e74c3c;
        transform: translate(50px, 0);
      }
      50% {
        rx: 50;
        fill: #2ecc71;
        transform: translate(50px, 50px);
      }
      75% {
        rx: 0;
        fill: #f39c12;
        transform: translate(0, 50px);
      }
      100% {
        rx: 0;
        fill: #3498db;
        transform: translate(0, 0);
      }
    }
  </style>
  <rect class="morph-rect" x="75" y="25" width="100" height="100" fill="#3498db" />
</svg>
```

Visually: A square that moves in a square path while changing color and morphing between a rectangle and a circle (via border-radius).

## Staggered Animations

```html
<svg width="300" height="100" viewBox="0 0 300 100">
  <style>
    .bar {
      animation: grow 1.5s ease-in-out infinite alternate;
      transform-origin: bottom;
    }
    .bar:nth-child(1) {
      animation-delay: 0s;
    }
    .bar:nth-child(2) {
      animation-delay: 0.1s;
    }
    .bar:nth-child(3) {
      animation-delay: 0.2s;
    }
    .bar:nth-child(4) {
      animation-delay: 0.3s;
    }
    .bar:nth-child(5) {
      animation-delay: 0.4s;
    }
    @keyframes grow {
      from {
        transform: scaleY(0.3);
      }
      to {
        transform: scaleY(1);
      }
    }
  </style>
  <rect class="bar" x="40" y="10" width="30" height="80" rx="4" fill="#3498db" />
  <rect class="bar" x="80" y="10" width="30" height="80" rx="4" fill="#2ecc71" />
  <rect class="bar" x="120" y="10" width="30" height="80" rx="4" fill="#e74c3c" />
  <rect class="bar" x="160" y="10" width="30" height="80" rx="4" fill="#f39c12" />
  <rect class="bar" x="200" y="10" width="30" height="80" rx="4" fill="#9b59b6" />
</svg>
```

Visually: Five colored bars that grow and shrink in a wave pattern — each one starts slightly after the previous, creating a ripple effect like an audio equalizer.

## Morphing with CSS (Limited)

CSS can animate between simple shape values in some browsers:

```html
<svg width="200" height="200" viewBox="0 0 200 200">
  <style>
    .morph-shape {
      d: path("M 100,20 L 180,180 L 20,180 Z");
      transition: d 1s ease;
      fill: #3498db;
    }
    svg:hover .morph-shape {
      d: path("M 100,20 L 180,100 L 100,180 L 20,100 Z");
    }
  </style>
  <path class="morph-shape" />
</svg>
```

Visually: A blue triangle that morphs into a diamond shape on hover. Note: the `d` property animation works in Chrome/Edge but has limited support elsewhere. For cross-browser morphing, use GSAP MorphSVGPlugin (Chapter 4).

## Complete Example: Animated Notification Bell

```html
<svg width="100" height="100" viewBox="0 0 24 24">
  <style>
    .bell {
      transform-origin: 12px 2px;
      animation: ring 2s ease infinite;
    }
    .bell-dot {
      animation: pulse-dot 2s ease infinite;
    }
    @keyframes ring {
      0%,
      70%,
      100% {
        transform: rotate(0deg);
      }
      5% {
        transform: rotate(15deg);
      }
      10% {
        transform: rotate(-15deg);
      }
      15% {
        transform: rotate(10deg);
      }
      20% {
        transform: rotate(-10deg);
      }
      25% {
        transform: rotate(5deg);
      }
      30% {
        transform: rotate(0deg);
      }
    }
    @keyframes pulse-dot {
      0%,
      70%,
      100% {
        transform: scale(1);
        opacity: 1;
      }
      85% {
        transform: scale(1.3);
        opacity: 0.8;
      }
    }
  </style>
  <!-- Bell body -->
  <path
    class="bell"
    fill="#f39c12"
    d="M12 2C11.45 2 11 2.45 11 3v1.07C7.61 4.56 5 7.47 5 11v5l-2 2v1h18v-1l-2-2v-5c0-3.53-2.61-6.44-6-6.93V3c0-.55-.45-1-1-1z"
  />
  <!-- Bell clapper -->
  <path fill="#f39c12" d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2z" />
  <!-- Notification dot -->
  <circle class="bell-dot" cx="17" cy="6" r="3" fill="#e74c3c" />
</svg>
```

Visually: A golden bell that swings back and forth (like it's ringing), with a red notification dot that pulses. The bell swings quickly then settles, pauses, then rings again.

## Performance Tips

- Animate `transform` and `opacity` — they're GPU-accelerated
- Avoid animating `width`, `height`, `x`, `y` — they trigger layout recalculation
- Use `will-change: transform` for complex animations
- Prefer `transform-origin` in pixels for SVG (percentages can be unreliable)
- Test on mobile — complex SVG animations can be expensive

```css
/* Good: GPU-accelerated */
.fast {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Avoid: triggers layout */
.slow {
  animation: move 1s linear infinite;
}
@keyframes move {
  to {
    cx: 200;
  }
}
```

## Key Takeaways

- CSS transitions handle simple state changes (hover, active)
- `@keyframes` enables complex multi-step animations
- `transform-origin` must be set explicitly for SVG elements (use pixel values)
- `stroke-dasharray` + `stroke-dashoffset` creates the line drawing effect
- Stagger animations with `animation-delay` for wave/ripple effects
- Stick to `transform` and `opacity` for best performance
