# Chapter 4: Stagger the Nav Items on Load — Stagger

[← Chapter 3: Property Parameters](chapter-03-property-parameters.md) | [Chapter 5: Playback →](chapter-05-playback.md)

---

## The Brief

The navigation has 6 items. Mika's comp shows them cascading in from left to right, each one 80ms after the previous. The last item has a slightly different easing — a tiny overshoot that signals "end of sequence."

Currently they all appear at once. Boring.

```html
<nav class="main-nav">
  <a class="nav-item" href="#">Collections</a>
  <a class="nav-item" href="#">Heritage</a>
  <a class="nav-item" href="#">Craftsmanship</a>
  <a class="nav-item" href="#">Boutiques</a>
  <a class="nav-item" href="#">Stories</a>
  <a class="nav-item" href="#">Contact</a>
</nav>
```

---

## Basic Stagger

`anime.stagger()` distributes a value across multiple targets:

```javascript
anime({
  targets: '.nav-item',
  opacity: [0, 1],
  translateY: [-15, 0],
  delay: anime.stagger(80),  // 0ms, 80ms, 160ms, 240ms, 320ms, 400ms
  duration: 500,
  easing: 'easeOutCubic',
});
```

The first item starts immediately. The second starts at 80ms. The third at 160ms. Each item is offset by 80ms from the previous one.

`anime.stagger(value)` is shorthand for: "distribute this value incrementally across all targets."

---

## Stagger with Range

Instead of a fixed increment, define a total range:

```javascript
anime({
  targets: '.nav-item',
  opacity: [0, 1],
  translateX: [-20, 0],
  delay: anime.stagger(80),           // Fixed: 0, 80, 160, 240...
  // OR
  delay: anime.stagger([0, 500]),     // Range: spread 0→500ms across all items
  duration: 500,
  easing: 'easeOutCubic',
});
```

With `anime.stagger([0, 500])` and 6 items:
- Item 0: 0ms
- Item 1: 100ms
- Item 2: 200ms
- Item 3: 300ms
- Item 4: 400ms
- Item 5: 500ms

The range is divided evenly regardless of how many items exist. Useful when you want the total cascade duration to be fixed.

---

## Stagger Direction: from

Control where the stagger starts:

```javascript
// From the beginning (default)
anime({
  targets: '.nav-item',
  delay: anime.stagger(80, { from: 'first' }),
});

// From the end
anime({
  targets: '.nav-item',
  delay: anime.stagger(80, { from: 'last' }),
});

// From the center (radiates outward)
anime({
  targets: '.nav-item',
  delay: anime.stagger(80, { from: 'center' }),
});

// From a specific index
anime({
  targets: '.nav-item',
  delay: anime.stagger(80, { from: 2 }),  // Starts from 3rd item
});
```

### Center Stagger

With `from: 'center'` and 6 items (indices 0–5), the center items (2, 3) start first, then it radiates outward:

```
Index:  0    1    2    3    4    5
Delay: 160  80   0    0    80  160  (ms)
```

This creates a "reveal from middle" effect — great for grids and symmetric layouts.

---

## Stagger on Properties (Not Just Delay)

Stagger works on any numeric property:

```javascript
anime({
  targets: '.grid-item',
  translateY: anime.stagger([-30, 30]),  // First: -30px, Last: +30px
  opacity: [0, 1],
  delay: anime.stagger(50),
  duration: 600,
  easing: 'easeOutCubic',
});
```

Each item gets a different `translateY` value. The first item slides down from -30px, the last slides up from +30px, and items in between are interpolated.

```javascript
// Stagger rotation for a fan effect
anime({
  targets: '.card',
  rotate: anime.stagger([-15, 15]),  // Fan from -15° to +15°
  duration: 800,
  easing: 'easeOutBack',
});

// Stagger scale for depth
anime({
  targets: '.layer',
  scale: anime.stagger([0.8, 1.2]),  // Back layers smaller, front larger
  duration: 600,
});
```

---

## Grid Stagger

For 2D layouts, stagger can account for both row and column position:

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  opacity: [0, 1],
  delay: anime.stagger(50, {
    grid: [4, 5],       // 4 rows, 5 columns
    from: 'center',     // Radiates from center of grid
  }),
  duration: 600,
  easing: 'easeOutQuad',
});
```

With grid stagger, delay is calculated based on distance from the origin point in 2D space. Items equidistant from the center animate simultaneously, creating a ripple effect.

```
Grid (4×5), from: 'center':

  200  150  100  150  200
  150  100   50  100  150
  150  100   50  100  150
  200  150  100  150  200

(delay in ms — items at same distance animate together)
```

### Grid Stagger with Axis

Limit the stagger to one axis:

```javascript
// Only stagger horizontally (columns cascade, rows simultaneous)
anime({
  targets: '.grid-item',
  delay: anime.stagger(80, { grid: [4, 5], axis: 'x' }),
});

// Only stagger vertically (rows cascade, columns simultaneous)
anime({
  targets: '.grid-item',
  delay: anime.stagger(80, { grid: [4, 5], axis: 'y' }),
});
```

---

## Stagger Easing

Apply an easing to the stagger distribution itself:

```javascript
anime({
  targets: '.nav-item',
  opacity: [0, 1],
  translateX: [-20, 0],
  delay: anime.stagger(80, {
    easing: 'easeOutQuad',  // Early items are closer together, later items spread out
  }),
  duration: 500,
});
```

Without stagger easing: 0, 80, 160, 240, 320, 400 (linear distribution)
With `easeOutQuad`: 0, 45, 120, 210, 310, 400 (bunched at start, spread at end)

This makes the cascade feel like it accelerates — the first few items fire rapidly, then the pace slows.

---

## The Nav Animation: Final Version

Combining everything for Mika's spec:

```javascript
import anime from 'animejs';

// Nav items cascade from left
anime({
  targets: '.nav-item',
  opacity: [0, 1],
  translateY: [-12, 0],
  delay: anime.stagger(80, { easing: 'easeOutQuad' }),
  duration: 500,
  easing: 'easeOutCubic',
});
```

But Mika wanted the last item to have a slight overshoot. Function-based easing:

```javascript
anime({
  targets: '.nav-item',
  opacity: [0, 1],
  translateY: [-12, 0],
  delay: anime.stagger(80, { easing: 'easeOutQuad' }),
  duration: 500,
  easing: function(el, i, total) {
    // Last item gets overshoot, others get standard
    return i === total - 1 ? 'easeOutBack' : 'easeOutCubic';
  },
});
```

The last item ("Contact") bounces slightly past its final position then settles back. A subtle signal that the sequence is complete.

---

## Stagger Patterns: Real Examples

### Card Grid Reveal

```javascript
// Cards appear in a wave from top-left
anime({
  targets: '.product-card',
  opacity: [0, 1],
  translateY: [30, 0],
  scale: [0.95, 1],
  delay: anime.stagger(60, { grid: [3, 4], from: 0 }),
  duration: 600,
  easing: 'easeOutCubic',
});
```

### Feature List

```javascript
// Features cascade in from the left
anime({
  targets: '.feature-item',
  opacity: [0, 1],
  translateX: [-40, 0],
  delay: anime.stagger(120),
  duration: 700,
  easing: 'cubicBezier(0.16, 1, 0.3, 1)',
});
```

### Spec Numbers (Preview)

```javascript
// Numbers stagger in before they start counting
anime({
  targets: '.spec-value',
  opacity: [0, 1],
  translateY: [20, 0],
  delay: anime.stagger(150, { from: 'center' }),
  duration: 500,
  easing: 'easeOutQuad',
});
```

### Loading Dots

```javascript
// Three dots pulse in sequence
anime({
  targets: '.loading-dot',
  scale: [1, 1.4],
  opacity: [1, 0.5],
  delay: anime.stagger(150),
  duration: 400,
  direction: 'alternate',
  loop: true,
  easing: 'easeInOutSine',
});
```

---

## Stagger vs Function-Based Delay

When to use which:

```javascript
// Stagger: uniform pattern
delay: anime.stagger(80)
// → 0, 80, 160, 240, 320

// Function: custom logic
delay: function(el, i, total) {
  // Random delay between 0-500ms
  return Math.random() * 500;
}

// Function: based on element data
delay: function(el, i) {
  return el.dataset.order * 100;  // Use data attributes
}

// Function: distance-based
delay: function(el, i) {
  const rect = el.getBoundingClientRect();
  const distance = Math.sqrt(rect.x ** 2 + rect.y ** 2);
  return distance * 0.5;  // Further from origin = later
}
```

Use `anime.stagger()` for regular patterns. Use functions for irregular or data-driven patterns.

---

## Performance Note

Staggering 100+ elements is fine — Anime.js batches them efficiently. But each element creates a separate animation instance internally. For 1000+ elements, consider:

1. Animating a container instead of individual items
2. Using CSS animations for simple staggers (with `animation-delay`)
3. Virtualizing off-screen elements

For the Lumina site (6 nav items, 12 grid items, 4 spec numbers), stagger is perfect.

---

## Theo's Feedback

> "The nav cascade is good. But I want to see the loading state — the three dots that pulse while the watch image loads. Can you make them loop forever? And the hero subtitle should pulse once if the user hasn't scrolled after 3 seconds — a gentle 'hey, there's more below' hint."

Looping. Alternating. Autoplay control. That's playback.

---

## What You Learned

- **anime.stagger(value)** — fixed increment between targets
- **anime.stagger([start, end])** — range distributed across targets
- **from** — 'first', 'last', 'center', or index
- **grid** — 2D stagger for grid layouts [rows, cols]
- **axis** — limit grid stagger to 'x' or 'y'
- **Stagger easing** — non-linear distribution of delays
- **Stagger on properties** — not just delay, any numeric value
- **Function-based** — for custom/irregular patterns
- **Performance** — fine for dozens, careful with thousands

Six nav items cascade in 480ms total. The grid reveals in a ripple. The loading dots pulse. All with one concept: distribute a value across targets.

Next: making things loop, alternate, and respond to playback controls.

---

[← Chapter 3: Property Parameters](chapter-03-property-parameters.md) | [Chapter 5: Playback →](chapter-05-playback.md)
