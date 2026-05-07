# Chapter 3: Animate From/To Specific Values — Property Parameters

[← Chapter 2: Easing](chapter-02-easing.md) | [Chapter 4: Stagger →](chapter-04-stagger.md)

---

## The Brief

Mika sends a motion comp with annotations:

> "The hero title slides in from 60px left. The subtitle fades up from 20px below. The watch image scales from 0.9 to 1.0 and rotates 5 degrees. Each property has its own timing. The title's opacity finishes before its movement. The watch rotation uses a different easing than its scale."

One animation call per element won't cut it anymore. You need granular control over every property — its start value, end value, duration, delay, and easing. Independently.

---

## Property Objects

Instead of passing a simple value, pass an object with full configuration:

```javascript
anime({
  targets: '.hero-title',
  translateX: {
    value: [-60, 0],       // from -60px to 0
    duration: 1000,        // takes 1 second
    easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  },
  opacity: {
    value: [0, 1],         // from invisible to visible
    duration: 400,         // finishes in 400ms
    easing: 'linear',      // linear for opacity
  },
});
```

The opacity completes at 400ms while the element is still sliding until 1000ms. The text is readable before the motion finishes — a deliberate design choice.

### Available Property Parameters

| Parameter | What It Does | Default |
|---|---|---|
| `value` | The target value or [from, to] array | Required |
| `duration` | How long this property animates | Inherits from parent |
| `delay` | When this property starts | Inherits from parent |
| `easing` | Acceleration curve for this property | Inherits from parent |

---

## From/To Syntax Options

Multiple ways to define start and end values:

```javascript
// Array: [from, to]
anime({ targets: '.box', translateX: [100, 250] });
// Starts at 100px, ends at 250px

// Single value: current → target
anime({ targets: '.box', translateX: 250 });
// Starts at current position, ends at 250px

// Property object with value array
anime({ targets: '.box', translateX: { value: [-60, 0] } });

// Relative values with operators
anime({ targets: '.box', translateX: '+=100' });  // Add 100 to current
anime({ targets: '.box', translateX: '-=50' });   // Subtract 50 from current
anime({ targets: '.box', rotate: '*=2' });        // Multiply current by 2
```

### Relative Values

Relative values are powerful for animations that build on the current state:

```javascript
// Move 100px further right from wherever it is now
anime({ targets: '.box', translateX: '+=100' });

// Rotate another 90 degrees
anime({ targets: '.box', rotate: '+=90' });

// Scale up by 20%
anime({ targets: '.box', scale: '*=1.2' });
```

---

## Units

Anime.js handles units intelligently:

```javascript
// Transforms default to pixels (no unit needed)
anime({ targets: '.box', translateX: 100 });  // 100px

// Explicit units
anime({ targets: '.box', translateX: '5rem' });
anime({ targets: '.box', rotate: '1turn' });
anime({ targets: '.box', rotate: '180deg' });

// CSS properties need units
anime({ targets: '.box', width: '200px' });
anime({ targets: '.box', fontSize: '2rem' });

// Unit conversion in [from, to]
anime({ targets: '.box', width: ['100px', '200px'] });

// Mixing units (Anime.js converts)
anime({ targets: '.box', translateX: ['0%', '100%'] });
```

### Common Units

| Property | Default Unit | Alternatives |
|---|---|---|
| translateX/Y | px | %, rem, vw, vh |
| rotate | deg | rad, turn |
| scale | (unitless) | — |
| opacity | (unitless, 0–1) | — |
| width/height | — | px, %, rem, vw |

---

## Keyframes: Multiple Steps

For animations with more than two states, use keyframes:

```javascript
anime({
  targets: '.watch-hand',
  keyframes: [
    { rotate: 0, duration: 0 },
    { rotate: 90, duration: 500 },
    { rotate: 90, duration: 200 },   // Pause at 90°
    { rotate: 180, duration: 500 },
    { rotate: 180, duration: 200 },  // Pause at 180°
    { rotate: 270, duration: 500 },
  ],
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',
});
```

Each keyframe object defines the target values and how long to take getting there. The animation plays through them sequentially.

### Per-Property Keyframes

You can also define keyframes per property:

```javascript
anime({
  targets: '.element',
  translateX: [
    { value: 100, duration: 500 },
    { value: 200, duration: 500 },
    { value: 0, duration: 1000 },
  ],
  translateY: [
    { value: -50, duration: 250 },
    { value: 50, duration: 250 },
    { value: 0, duration: 500 },
  ],
  easing: 'easeOutQuad',
});
```

`translateX` and `translateY` follow independent timelines. The element traces a complex path.

---

## Function-Based Values

When animating multiple targets, you often want different values per element. Pass a function:

```javascript
anime({
  targets: '.grid-item',
  translateY: function(el, i, total) {
    // el: the DOM element
    // i: index (0, 1, 2, ...)
    // total: total number of targets
    return (i * 20) + 'px';  // Each item moves further
  },
  opacity: [0, 1],
  duration: 800,
  easing: 'easeOutCubic',
});
```

| Parameter | What It Is |
|---|---|
| `el` | The current DOM element being animated |
| `i` | Index of this element in the targets list |
| `total` | Total number of elements being animated |

Function-based values work for any parameter — including `duration`, `delay`, and `easing`:

```javascript
anime({
  targets: '.grid-item',
  translateY: [30, 0],
  opacity: [0, 1],
  duration: function(el, i) {
    return 600 + (i * 100);  // Each item takes longer
  },
  delay: function(el, i) {
    return i * 80;  // Each item starts later
  },
  easing: 'easeOutCubic',
});
```

This creates a cascade where each element enters slightly after the previous one, with slightly longer duration. We'll formalize this pattern with `stagger` in Chapter 4.

---

## The Watch Image Animation

Mika's comp specifies:
- Scale: 0.9 → 1.0, 1200ms, mechanical easing
- Rotate: -5deg → 0deg, 1000ms, same easing, starts 200ms late
- Opacity: 0 → 1, 400ms, linear

```javascript
anime({
  targets: '.watch-hero',
  scale: {
    value: [0.9, 1],
    duration: 1200,
    easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  },
  rotate: {
    value: [-5, 0],
    duration: 1000,
    delay: 200,
    easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  },
  opacity: {
    value: [0, 1],
    duration: 400,
    easing: 'linear',
  },
});
```

Three properties, three different timings, one `anime()` call. The watch fades in instantly (400ms), starts rotating at 200ms, and the scale takes the longest to settle. It feels like the watch is being placed precisely into position.

---

## Transform Origin

CSS `transform-origin` affects where transforms originate. Anime.js doesn't animate it directly, but you set it in CSS:

```css
.watch-hand {
  transform-origin: bottom center;  /* Rotates from the base */
}

.dial-marker {
  transform-origin: center center;  /* Rotates from the middle */
}
```

```javascript
// The hand rotates from its base (like a real watch hand)
anime({
  targets: '.watch-hand',
  rotate: [0, 210],
  duration: 1500,
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',
});
```

Without the correct `transform-origin`, the hand would rotate around its center instead of its base. Always check transform-origin when rotation looks wrong.

---

## Colors

Anime.js can animate colors between any format:

```javascript
anime({
  targets: '.hero-bg',
  backgroundColor: ['#0a0a0a', '#1a1a2e'],
  duration: 2000,
  easing: 'linear',
});

// Hex, RGB, RGBA, HSL all work
anime({
  targets: '.accent',
  color: ['rgb(255, 255, 255)', 'rgb(200, 170, 100)'],  // White to gold
  duration: 1000,
});
```

Color animations interpolate through RGB space by default. For the watchmaker's gold accent:

```javascript
anime({
  targets: '.brand-accent',
  color: ['#ffffff', '#c8a864'],  // White to gold
  duration: 1200,
  easing: 'easeInOutSine',
});
```

---

## Putting It Together: The Full Hero Section

```javascript
import anime from 'animejs';

const EASING = {
  mechanical: 'cubicBezier(0.4, 0, 0.2, 1)',
  enter: 'cubicBezier(0.16, 1, 0.3, 1)',
};

// Title: slides from left
anime({
  targets: '.hero-title',
  translateX: {
    value: [-60, 0],
    duration: 1000,
    easing: EASING.mechanical,
  },
  opacity: {
    value: [0, 1],
    duration: 400,
    easing: 'linear',
  },
});

// Subtitle: fades up
anime({
  targets: '.hero-subtitle',
  translateY: {
    value: [20, 0],
    duration: 800,
    easing: EASING.enter,
  },
  opacity: {
    value: [0, 1],
    duration: 400,
    delay: 200,
    easing: 'linear',
  },
  delay: 300,
});

// Watch image: scales and rotates into position
anime({
  targets: '.watch-hero',
  scale: {
    value: [0.9, 1],
    duration: 1200,
    easing: EASING.mechanical,
  },
  rotate: {
    value: [-5, 0],
    duration: 1000,
    delay: 200,
    easing: EASING.mechanical,
  },
  opacity: {
    value: [0, 1],
    duration: 600,
    easing: 'linear',
  },
  delay: 500,
});
```

Three elements, each with unique motion characteristics, all coordinated through delays. The title leads, the subtitle follows, the watch image anchors.

---

## Mika's Feedback

Mika watches the animation frame by frame:

> "The timing is close. But look at the nav items — they all appear at once. In my comp, they cascade in one by one, left to right, with 80ms between each. And the last one has a slight overshoot."

You could use function-based delays:

```javascript
anime({
  targets: '.nav-item',
  opacity: [0, 1],
  translateY: [-10, 0],
  delay: function(el, i) { return i * 80; },
  duration: 500,
  easing: 'easeOutCubic',
});
```

But Anime.js has a dedicated feature for exactly this pattern. It's called stagger.

---

## What You Learned

- **Property objects** — per-property duration, delay, easing
- **[from, to] arrays** — explicit start and end values
- **Relative values** — `+=`, `-=`, `*=` operators
- **Units** — px, rem, %, deg, turn, rad
- **Keyframes** — multi-step animations with intermediate states
- **Per-property keyframes** — independent timelines per property
- **Function-based values** — different values per element (el, i, total)
- **Colors** — hex, rgb, rgba, hsl interpolation
- **Transform origin** — CSS controls where transforms originate

You can now animate any property with full control over its timing. But when you have 8 nav items that need to cascade, writing function-based delays is verbose. Stagger is the elegant solution.

That's Chapter 4.

---

[← Chapter 2: Easing](chapter-02-easing.md) | [Chapter 4: Stagger →](chapter-04-stagger.md)
