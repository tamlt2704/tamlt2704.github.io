# Chapter 1: Fade In the Hero Heading — Your First Animation

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Easing →](chapter-02-easing.md)

---

## The Brief

Theo drops a Figma link in Slack:

> "The hero section. When the page loads, the heading should fade in and slide up. Nothing fancy — just make it feel intentional. The current site just... appears. Like a PowerPoint from 2003."

You open the current code:

```html
<h1 class="hero-title">Precision in Motion</h1>
```

```css
.hero-title {
  opacity: 1;
  /* That's it. No animation. Just... there. */
}
```

Time to make it move.

---

## The Anatomy of an Anime.js Call

Every animation in Anime.js follows the same structure:

```javascript
import anime from 'animejs';

anime({
  targets: '.hero-title',      // WHAT to animate
  opacity: [0, 1],             // WHICH properties (from → to)
  translateY: [40, 0],         // Can animate multiple properties
  duration: 800,               // HOW LONG (milliseconds)
  easing: 'easeOutCubic',     // HOW it moves through time
});
```

Five concepts. That's the entire mental model for basic animations.

---

## Targets: What to Animate

The `targets` property accepts almost anything:

```javascript
// CSS selector (most common)
anime({ targets: '.hero-title', ... });

// DOM element
const el = document.querySelector('.hero-title');
anime({ targets: el, ... });

// NodeList
const items = document.querySelectorAll('.nav-item');
anime({ targets: items, ... });

// Array of elements
anime({ targets: [el1, el2, el3], ... });

// JavaScript object (animate its properties)
const obj = { progress: 0 };
anime({ targets: obj, progress: 100, ... });
```

For the hero heading, a CSS selector is cleanest:

```javascript
anime({ targets: '.hero-title', ... });
```

If the selector matches multiple elements, they all animate simultaneously. One call, many targets.

---

## Properties: What Changes

Anime.js can animate any CSS property that has a numeric value:

```javascript
anime({
  targets: '.box',
  // CSS transforms (GPU-accelerated, smooth)
  translateX: 250,        // pixels by default
  translateY: 40,
  rotate: '1turn',        // supports units
  scale: 1.5,

  // CSS properties
  opacity: 1,
  borderRadius: '50%',
  backgroundColor: '#ff0000',
  width: '200px',

  // SVG attributes
  strokeDashoffset: 0,
  points: '64 128 8.574 96 8.574 32 64 0 119.426 32 119.426 96',
});
```

### The [from, to] Syntax

The most explicit way to define property values:

```javascript
anime({
  targets: '.hero-title',
  opacity: [0, 1],         // from 0 → to 1
  translateY: [40, 0],     // from 40px down → to 0 (original position)
});
```

The element starts at `opacity: 0` and `translateY: 40px`, then animates to `opacity: 1` and `translateY: 0`.

### Without [from, to]

If you only provide a single value, Anime.js animates FROM the element's current state TO that value:

```javascript
anime({
  targets: '.box',
  translateX: 250,  // from current position → 250px right
});
```

For the hero heading, `[from, to]` is better because we want to control exactly where it starts.

---

## Duration: How Long

Duration is in milliseconds:

```javascript
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,  // 0.8 seconds
});
```

| Duration | Feels Like |
|---|---|
| 100–200ms | Instant (micro-interactions) |
| 300–500ms | Quick (button feedback) |
| 600–1000ms | Deliberate (page transitions) |
| 1000–2000ms | Dramatic (hero entrances) |
| 2000ms+ | Slow (use sparingly) |

Theo's rule: "If you can't justify why it's longer than 800ms, it's too long."

For the hero heading, 800ms feels right — deliberate but not sluggish.

---

## Easing: How It Moves

Easing defines the acceleration curve. Without it, animations feel robotic (constant speed from start to finish).

```javascript
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,
  easing: 'easeOutCubic',  // Fast start, gentle stop
});
```

Common built-in easings:

| Easing | Character | Use Case |
|---|---|---|
| `linear` | Constant speed | Progress bars, loading |
| `easeInQuad` | Slow start | Elements leaving |
| `easeOutQuad` | Slow end | Elements entering |
| `easeInOutQuad` | Slow start + end | Transitions between states |
| `easeOutCubic` | Faster deceleration | Hero entrances |
| `easeOutExpo` | Dramatic deceleration | Attention-grabbing reveals |

For elements entering the viewport, `easeOut` variants feel natural — they arrive with energy and settle into place. Like a ball rolling to a stop.

We'll go deep on easing in Chapter 2. For now, `easeOutCubic` is your default.

---

## The Complete Hero Animation

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Lumina — Swiss Precision</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #0a0a0a;
      font-family: 'Helvetica Neue', system-ui, sans-serif;
    }

    .hero {
      text-align: center;
      padding: 2rem;
    }

    .hero-title {
      font-size: clamp(2rem, 8vw, 5rem);
      font-weight: 200;
      letter-spacing: 0.05em;
      color: #f5f5f5;
      text-transform: uppercase;
    }

    .hero-subtitle {
      font-size: clamp(0.875rem, 2vw, 1.25rem);
      color: #888;
      margin-top: 1rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
    }
  </style>
</head>
<body>
  <section class="hero">
    <h1 class="hero-title">Precision in Motion</h1>
    <p class="hero-subtitle">Swiss Watchmaking Since 1847</p>
  </section>
  <script type="module" src="./main.js"></script>
</body>
</html>
```

```javascript
// main.js
import anime from 'animejs';

// Hero title: fade in + slide up
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,
  easing: 'easeOutCubic',
});

// Subtitle: same animation, slightly delayed
anime({
  targets: '.hero-subtitle',
  opacity: [0, 1],
  translateY: [20, 0],
  duration: 800,
  delay: 400,  // Wait 400ms after page load
  easing: 'easeOutCubic',
});
```

The title enters first. The subtitle follows 400ms later. A simple sequence that creates hierarchy — the title is more important, so it arrives first.

---

## Delay: When It Starts

The `delay` property offsets when the animation begins:

```javascript
anime({
  targets: '.hero-subtitle',
  opacity: [0, 1],
  translateY: [20, 0],
  duration: 800,
  delay: 400,  // Starts 400ms after anime() is called
  easing: 'easeOutCubic',
});
```

Delay is how you create sequences without timelines. Element A starts immediately, element B starts 400ms later. The viewer perceives order and hierarchy.

---

## The Initial State Problem

There's a flash. When the page loads, the heading is visible for a split second before JavaScript runs and sets `opacity: 0`. Then it fades in. That flash is unacceptable.

Fix: hide elements with CSS before JavaScript loads:

```css
.hero-title,
.hero-subtitle {
  opacity: 0;  /* Hidden by default */
}
```

Now the elements are invisible from the first paint. When Anime.js runs, it animates them from `opacity: 0` to `opacity: 1`. No flash.

But what if JavaScript fails to load? The content stays invisible forever. Add a fallback:

```html
<noscript>
  <style>
    .hero-title, .hero-subtitle { opacity: 1 !important; }
  </style>
</noscript>
```

Or use a class-based approach:

```css
.js-animate { opacity: 0; }
```

```javascript
// Only add the class if JS is running
document.querySelectorAll('[data-animate]').forEach(el => {
  el.classList.add('js-animate');
});

// Then animate
anime({
  targets: '[data-animate="hero-title"]',
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,
  easing: 'easeOutCubic',
});
```

For the Lumina project, we'll use the CSS approach since the site requires JavaScript anyway.

---

## What Anime.js Returns

`anime()` returns an animation instance — an object you can control later:

```javascript
const heroAnimation = anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,
  easing: 'easeOutCubic',
});

// The instance has properties and methods:
console.log(heroAnimation.duration);   // 800
console.log(heroAnimation.progress);   // 0 → 100 as it plays
console.log(heroAnimation.completed);  // Promise that resolves when done

// Control methods (we'll use these in Chapter 10):
// heroAnimation.pause();
// heroAnimation.play();
// heroAnimation.restart();
// heroAnimation.seek(400);  // Jump to 400ms
```

For now, just know that every `anime()` call returns something useful. We'll exploit this in later chapters.

---

## Callbacks: Knowing When Things Happen

Anime.js provides lifecycle callbacks:

```javascript
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,
  easing: 'easeOutCubic',

  begin: () => console.log('Animation started'),
  update: (anim) => console.log(`Progress: ${anim.progress}%`),
  complete: () => console.log('Animation finished'),
});
```

| Callback | When It Fires |
|---|---|
| `begin` | Once, when the animation starts (after delay) |
| `update` | Every frame while animating |
| `complete` | Once, when the animation finishes |
| `loopBegin` | At the start of each loop iteration |
| `loopComplete` | At the end of each loop iteration |

The `complete` callback is the most useful — it's how you trigger the next animation in a sequence (before you learn timelines):

```javascript
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,
  easing: 'easeOutCubic',
  complete: () => {
    // After title finishes, animate subtitle
    anime({
      targets: '.hero-subtitle',
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 600,
      easing: 'easeOutCubic',
    });
  },
});
```

This works but gets messy fast (callback hell). Timelines solve this properly in Chapter 6.

---

## Multiple Properties, Different Timings

What if the opacity should finish before the movement? Anime.js lets you set per-property parameters:

```javascript
anime({
  targets: '.hero-title',
  opacity: {
    value: [0, 1],
    duration: 400,       // Opacity finishes in 400ms
    easing: 'linear',   // Opacity looks best with linear
  },
  translateY: {
    value: [40, 0],
    duration: 800,       // Movement takes the full 800ms
    easing: 'easeOutCubic',
  },
});
```

The text becomes fully visible at 400ms but is still sliding into position until 800ms. This creates a layered feel — the content is readable before the motion completes.

---

## Theo's Feedback

You show Theo the hero animation. He watches it three times.

> "Good. The timing is right. But the subtitle delay feels arbitrary — try 300ms instead of 400ms. And the translateY on the title... 40px is too much. Try 30. Subtle movements feel more expensive."

You adjust:

```javascript
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [30, 0],  // Was 40, now 30
  duration: 800,
  easing: 'easeOutCubic',
});

anime({
  targets: '.hero-subtitle',
  opacity: [0, 1],
  translateY: [20, 0],
  duration: 800,
  delay: 300,  // Was 400, now 300
  easing: 'easeOutCubic',
});
```

> "Better. Luxury brands don't shout. The animation should whisper."

---

## Common Mistakes

### 1. Animating layout properties

```javascript
// ❌ Bad — triggers layout recalculation every frame
anime({
  targets: '.box',
  width: '200px',
  height: '200px',
  top: '100px',
  left: '200px',
});

// ✅ Good — uses GPU-accelerated transforms
anime({
  targets: '.box',
  scale: 1.5,
  translateX: 200,
  translateY: 100,
});
```

`width`, `height`, `top`, `left` trigger layout. `transform` and `opacity` don't. Always prefer transforms.

### 2. Forgetting units

```javascript
// ❌ Might not work as expected
anime({ targets: '.box', width: 200 });

// ✅ Explicit units
anime({ targets: '.box', width: '200px' });

// ✅ Transforms don't need units (pixels assumed)
anime({ targets: '.box', translateX: 200 });
```

### 3. Animating display or visibility

```javascript
// ❌ Can't animate — it's not numeric
anime({ targets: '.box', display: 'block' });

// ✅ Animate opacity instead, toggle display in callback
anime({
  targets: '.box',
  opacity: [0, 1],
  begin: () => { document.querySelector('.box').style.display = 'block'; },
});
```

---

## What You Learned

- **targets** — CSS selector, DOM element, NodeList, or JS object
- **Properties** — any numeric CSS property, transforms preferred
- **[from, to]** — explicit start and end values
- **duration** — milliseconds (800ms is a good default for entrances)
- **easing** — `easeOutCubic` for elements entering
- **delay** — offset when the animation starts
- **Callbacks** — `begin`, `update`, `complete`
- **Per-property params** — different duration/easing per property
- **Initial state** — hide with CSS, animate with JS, fallback for no-JS

The hero heading fades in. The subtitle follows. It feels intentional. But Theo watches it again and frowns:

> "The easing. It's fine. But 'fine' isn't what we're selling. The watchmaker's brand is mechanical precision — not generic cubic curves. We need custom easing."

That's Chapter 2.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Easing →](chapter-02-easing.md)
