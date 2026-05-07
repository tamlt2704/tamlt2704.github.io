# Chapter 14: Drag to Reorder, Spring Back — Spring Physics

[← Chapter 13: SVG Morphing](chapter-13-svg-morphing.md) | [Chapter 15: Responsive Animation →](chapter-15-responsive-animation.md)

---

## The Brief

The collection page has a "favorites" section where users can reorder watches by dragging. When a card is released, it should spring into its new position — not slide linearly, but bounce slightly like it has mass.

Theo's note:
> "The spring should feel heavy. This is a luxury watch, not a rubber ball. Short overshoot, quick settle. Think: a precision mechanism clicking into place."

---

## Spring Easing in Anime.js

The `spring()` easing simulates real physics:

```javascript
anime({
  targets: '.card',
  translateX: 200,
  easing: 'spring(mass, stiffness, damping, velocity)',
});
```

| Parameter | What It Controls | Range | Effect |
|---|---|---|---|
| Mass | Weight of object | 1–10 | Heavier = slower, more momentum |
| Stiffness | Spring strength | 50–500 | Higher = snappier |
| Damping | Friction/resistance | 5–50 | Higher = less oscillation |
| Velocity | Initial speed | 0–20 | Higher = more initial energy |

---

## Finding the Right Spring

### Luxury Watch (heavy, precise)

```javascript
// Heavy, stiff, well-damped — clicks into place
easing: 'spring(2, 200, 20, 0)'
```

Short overshoot, settles quickly. Feels like a precision mechanism.

### Playful UI (light, bouncy)

```javascript
// Light, moderate stiffness, low damping — bounces
easing: 'spring(1, 100, 8, 0)'
```

Multiple oscillations before settling. Fun, energetic.

### Snappy Button (instant response)

```javascript
// Light, very stiff, high damping — almost no overshoot
easing: 'spring(1, 300, 25, 0)'
```

Barely any bounce. Just a hint of physicality.

### Lazy Drag (heavy, slow)

```javascript
// Heavy, low stiffness, low damping — slow wobble
easing: 'spring(5, 50, 5, 0)'
```

Slow, heavy oscillation. Like pushing something through water.

---

## Spring Duration

Unlike other easings, spring animations don't use the `duration` property. The spring parameters determine how long the animation takes to settle:

```javascript
anime({
  targets: '.card',
  translateX: 200,
  easing: 'spring(1, 100, 10, 0)',
  // duration is IGNORED — spring physics determines the length
});
```

Higher damping = shorter settle time. Lower damping = longer oscillation. You control duration through physics, not milliseconds.

If you need a specific duration, use `easeOutElastic` instead (which respects `duration`):

```javascript
// When you need spring-like feel WITH duration control
anime({
  targets: '.card',
  translateX: 200,
  duration: 800,  // Respected
  easing: 'easeOutElastic(1, 0.5)',
});
```

---

## Drag and Drop with Springs

A basic drag-to-reorder implementation:

```javascript
class DraggableList {
  constructor(container) {
    this.container = container;
    this.items = [...container.querySelectorAll('.drag-item')];
    this.dragItem = null;
    this.startY = 0;
    this.currentY = 0;

    this.bindEvents();
  }

  bindEvents() {
    this.items.forEach(item => {
      item.addEventListener('mousedown', (e) => this.onDragStart(e, item));
    });
    document.addEventListener('mousemove', (e) => this.onDragMove(e));
    document.addEventListener('mouseup', () => this.onDragEnd());
  }

  onDragStart(e, item) {
    this.dragItem = item;
    this.startY = e.clientY;
    item.classList.add('dragging');

    // Lift animation
    anime({
      targets: item,
      scale: 1.05,
      boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
      duration: 200,
      easing: 'easeOutCubic',
    });
  }

  onDragMove(e) {
    if (!this.dragItem) return;
    this.currentY = e.clientY - this.startY;
    this.dragItem.style.transform = `translateY(${this.currentY}px) scale(1.05)`;

    // Check for reorder
    this.checkReorder();
  }

  onDragEnd() {
    if (!this.dragItem) return;

    const item = this.dragItem;
    this.dragItem = null;
    item.classList.remove('dragging');

    // Spring back to position
    anime({
      targets: item,
      translateY: 0,
      scale: 1,
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      easing: 'spring(2, 200, 20, 0)',  // Heavy, precise spring
    });
  }

  checkReorder() {
    // Simplified: check if dragged item overlaps with siblings
    const dragRect = this.dragItem.getBoundingClientRect();

    this.items.forEach(item => {
      if (item === this.dragItem) return;
      const rect = item.getBoundingClientRect();

      if (dragRect.top < rect.top + rect.height / 2 &&
          dragRect.top > rect.top - rect.height / 2) {
        // Swap positions with spring animation
        this.swapItems(this.dragItem, item);
      }
    });
  }

  swapItems(dragged, target) {
    const targetRect = target.getBoundingClientRect();
    const draggedRect = dragged.getBoundingClientRect();
    const diff = draggedRect.top - targetRect.top;

    // Animate the displaced item
    anime({
      targets: target,
      translateY: diff > 0 ? -60 : 60,  // Move up or down
      easing: 'spring(1, 150, 15, 0)',
    });

    // Update DOM order
    if (diff > 0) {
      this.container.insertBefore(dragged, target);
    } else {
      this.container.insertBefore(dragged, target.nextSibling);
    }
  }
}

new DraggableList(document.querySelector('.favorites-list'));
```

When released, the card springs into its new position. Displaced cards spring out of the way. Everything feels physical.

---

## Spring Chains

Multiple elements connected by springs — each one follows the previous with a delay:

```javascript
const dots = document.querySelectorAll('.chain-dot');

document.addEventListener('mousemove', (e) => {
  dots.forEach((dot, i) => {
    anime({
      targets: dot,
      translateX: e.clientX,
      translateY: e.clientY,
      easing: 'spring(1, 100, 10, 0)',
      // Each dot has slightly different spring params
      // Later dots are "heavier" — they lag more
    });
  });
});
```

A simpler approach with staggered springs:

```javascript
document.addEventListener('mousemove', (e) => {
  anime({
    targets: '.chain-dot',
    translateX: e.clientX,
    translateY: e.clientY,
    delay: anime.stagger(50),  // Each dot starts 50ms later
    easing: 'spring(1, 120, 12, 0)',
  });
});
```

The dots follow the cursor in a chain, each one slightly behind the previous. Like a tail or ribbon.

---

## Comparing Spring Approaches

| Approach | Duration Control | Feel | Use Case |
|---|---|---|---|
| `spring(m, s, d, v)` | No (physics-based) | Most realistic | Drag, throw, reorder |
| `easeOutElastic(a, p)` | Yes | Bouncy, predictable | UI feedback, entrances |
| `easeOutBack` | Yes | Single overshoot | Subtle spring-like feel |

```javascript
// Spring: realistic, duration varies
anime({ targets: '.a', translateX: 200, easing: 'spring(1, 100, 10, 0)' });

// Elastic: bouncy, fixed duration
anime({ targets: '.b', translateX: 200, duration: 800, easing: 'easeOutElastic(1, 0.5)' });

// Back: single overshoot, fixed duration
anime({ targets: '.c', translateX: 200, duration: 500, easing: 'easeOutBack' });
```

For the watchmaker site: `spring(2, 200, 20, 0)` — heavy, precise, minimal bounce.

---

## Velocity from Gesture

When the user throws an element (fast drag release), capture the velocity:

```javascript
let lastY = 0;
let lastTime = 0;
let velocity = 0;

function onDragMove(e) {
  const now = Date.now();
  const dt = now - lastTime;
  if (dt > 0) {
    velocity = (e.clientY - lastY) / dt;  // pixels per ms
  }
  lastY = e.clientY;
  lastTime = now;
}

function onDragEnd() {
  // Use captured velocity in the spring
  anime({
    targets: dragItem,
    translateY: 0,
    easing: `spring(2, 200, 20, ${Math.abs(velocity) * 10})`,
    // Higher velocity = more initial energy = bigger overshoot
  });
}
```

A fast throw creates a bigger spring overshoot. A gentle release settles immediately. The animation responds to how the user interacted.

---

## When NOT to Use Springs

Springs aren't always appropriate:

```javascript
// ❌ Spring on opacity (looks weird — opacity doesn't "bounce")
anime({ targets: '.el', opacity: [0, 1], easing: 'spring(1, 100, 10, 0)' });

// ❌ Spring on color (colors don't overshoot naturally)
anime({ targets: '.el', backgroundColor: '#ff0000', easing: 'spring(...)' });

// ✅ Spring on position/scale/rotation (physical properties)
anime({ targets: '.el', translateX: 200, easing: 'spring(1, 100, 10, 0)' });
anime({ targets: '.el', scale: 1.2, easing: 'spring(1, 100, 10, 0)' });
anime({ targets: '.el', rotate: 45, easing: 'spring(1, 100, 10, 0)' });
```

Springs work for properties that have physical analogs — position, size, rotation. They look wrong on opacity, color, or other abstract properties.

---

## The Watchmaker's Spring

Final spring configuration for the Lumina site:

```javascript
const SPRINGS = {
  // Card reorder: heavy, precise
  reorder: 'spring(2, 200, 20, 0)',

  // Button press release: snappy
  button: 'spring(1, 300, 25, 0)',

  // Menu open: controlled
  menu: 'spring(1, 150, 18, 0)',

  // Notification enter: gentle
  notification: 'spring(1, 120, 15, 0)',
};
```

Each interaction has a spring tuned to its context. Heavier elements have heavier springs. Quick interactions are snappy. The brand feels consistent.

---

## What You Learned

- **spring(mass, stiffness, damping, velocity)** — physics-based easing
- **Mass** — weight (higher = slower, more momentum)
- **Stiffness** — spring strength (higher = snappier)
- **Damping** — friction (higher = less bounce)
- **Velocity** — initial energy (from gesture speed)
- **No duration** — spring physics determines settle time
- **Drag and drop** — lift, move, spring back
- **Spring chains** — staggered springs for trailing effects
- **When to use** — position, scale, rotation (not opacity/color)
- **Brand springs** — consistent spring configs per interaction type

The favorites reorder with physical weight. Cards spring into place. The motion feels real because it follows real physics.

One more interaction chapter: making all of this responsive — different animations on mobile, respecting reduced motion preferences, handling resize.

---

[← Chapter 13: SVG Morphing](chapter-13-svg-morphing.md) | [Chapter 15: Responsive Animation →](chapter-15-responsive-animation.md)
