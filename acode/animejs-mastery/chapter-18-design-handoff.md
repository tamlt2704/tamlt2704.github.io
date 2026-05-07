# Chapter 18: Match the After Effects Comp Exactly — Design Handoff

[← Chapter 17: Framework Integration](chapter-17-framework-integration.md) | [Chapter 19: Accessibility →](chapter-19-accessibility.md)

---

## The Problem

Mika exports the final motion comp from After Effects. It's a 12-second sequence with 23 animated elements. Each has precise timing, custom easing curves, and specific property values. Your job: make the code match the comp frame-for-frame.

Mika: "I've annotated everything. Here's the timing sheet."

---

## Reading a Timing Sheet

Mika's format:

```
ELEMENT          START    DUR    PROPERTY         FROM → TO          EASING
─────────────────────────────────────────────────────────────────────────────
.hero-title      0ms      800    opacity          0 → 1              linear
.hero-title      0ms      1000   translateY       40 → 0             [.16,1,.3,1]
.hero-subtitle   300ms    600    opacity          0 → 1              linear
.hero-subtitle   300ms    800    translateY       20 → 0             [.16,1,.3,1]
.watch-dial      600ms    700    opacity          0 → 1              [.4,0,.2,1]
.watch-dial      600ms    700    scale            0.85 → 1           [.4,0,.2,1]
.hour-hand       900ms    1200   rotate           0 → 210            [.4,0,.2,1]
.hour-hand       900ms    400    opacity          0 → 1              linear
.minute-hand     1200ms   900    rotate           0 → 60             [.4,0,.2,1]
.minute-hand     1200ms   300    opacity          0 → 1              linear
.strap           1600ms   600    scaleY           0 → 1              [.16,1,.3,1]
.strap           1600ms   400    opacity          0 → 1              linear
.nav-item[0]     2000ms   400    opacity          0 → 1              [.16,1,.3,1]
.nav-item[0]     2000ms   400    translateY       -12 → 0            [.16,1,.3,1]
.nav-item[1]     2080ms   400    opacity          0 → 1              [.16,1,.3,1]
...
```

Each row is one property animation. Multiple rows per element = multiple properties with independent timing.

---

## Translating to Code

The timing sheet maps directly to a timeline with absolute offsets:

```javascript
const EASE = {
  enter: 'cubicBezier(0.16, 1, 0.3, 1)',
  mechanical: 'cubicBezier(0.4, 0, 0.2, 1)',
};

const intro = anime.timeline({
  autoplay: false,
});

// Hero title
intro.add({
  targets: '.hero-title',
  opacity: { value: [0, 1], duration: 800, easing: 'linear' },
  translateY: { value: [40, 0], duration: 1000, easing: EASE.enter },
}, 0);

// Hero subtitle
intro.add({
  targets: '.hero-subtitle',
  opacity: { value: [0, 1], duration: 600, easing: 'linear' },
  translateY: { value: [20, 0], duration: 800, easing: EASE.enter },
}, 300);

// Watch dial
intro.add({
  targets: '.watch-dial',
  opacity: { value: [0, 1], duration: 700, easing: EASE.mechanical },
  scale: { value: [0.85, 1], duration: 700, easing: EASE.mechanical },
}, 600);

// Hour hand
intro.add({
  targets: '.hour-hand',
  rotate: { value: [0, 210], duration: 1200, easing: EASE.mechanical },
  opacity: { value: [0, 1], duration: 400, easing: 'linear' },
}, 900);

// Minute hand
intro.add({
  targets: '.minute-hand',
  rotate: { value: [0, 60], duration: 900, easing: EASE.mechanical },
  opacity: { value: [0, 1], duration: 300, easing: 'linear' },
}, 1200);

// Strap
intro.add({
  targets: '.strap',
  scaleY: { value: [0, 1], duration: 600, easing: EASE.enter },
  opacity: { value: [0, 1], duration: 400, easing: 'linear' },
}, 1600);

// Nav items (staggered)
intro.add({
  targets: '.nav-item',
  opacity: { value: [0, 1], duration: 400, easing: EASE.enter },
  translateY: { value: [-12, 0], duration: 400, easing: EASE.enter },
  delay: anime.stagger(80),
}, 2000);
```

One-to-one mapping. Each row in the timing sheet becomes a property object in the code.

---

## Extracting Easing Curves from After Effects

After Effects uses different easing terminology:

| After Effects | Anime.js Equivalent |
|---|---|
| Linear | `'linear'` |
| Easy Ease | `'easeInOutCubic'` (approximately) |
| Easy Ease In | `'easeInCubic'` |
| Easy Ease Out | `'easeOutCubic'` |
| Custom (graph editor) | `'cubicBezier(x1, y1, x2, y2)'` |

### Reading the Graph Editor

In AE's graph editor, Mika can read the bezier handles:

```
Influence: 60% / Speed: 0    →  x1 = 0.6, y1 = 0
Influence: 80% / Speed: 100% →  x2 = 0.2, y2 = 1

Result: cubicBezier(0.6, 0, 0.2, 1)
```

Or Mika can export the curve values directly. Many motion designers use tools like:
- **Flow** (AE plugin) — exports cubic-bezier values
- **Ease and Wizz** — preset curves with CSS equivalents
- **Manual** — read influence/speed from graph editor

---

## Frame-by-Frame Comparison

To verify your code matches the comp:

### 1. Record Both

```javascript
// Record animation frames
const frames = [];
const intro = anime.timeline({
  update: (anim) => {
    frames.push({
      time: anim.currentTime,
      progress: anim.progress,
    });
  },
});
```

### 2. Side-by-Side Scrubbing

Build a comparison tool:

```javascript
// Sync video playback with animation
const video = document.querySelector('.comp-video');  // Screen recording of AE comp
const timeline = anime.timeline({ autoplay: false, ... });

const scrubber = document.querySelector('#compare-scrubber');
scrubber.addEventListener('input', (e) => {
  const progress = e.target.value / 100;
  video.currentTime = progress * video.duration;
  timeline.seek(progress * timeline.duration);
});
```

Scrub both simultaneously. Any mismatch is immediately visible.

### 3. Snapshot Testing

```javascript
function captureState(time) {
  timeline.seek(time);
  const elements = document.querySelectorAll('[data-animate]');
  const state = {};

  elements.forEach(el => {
    const computed = getComputedStyle(el);
    state[el.dataset.animate] = {
      opacity: computed.opacity,
      transform: computed.transform,
    };
  });

  return state;
}

// Compare at key moments
const keyframes = [0, 300, 600, 900, 1200, 1600, 2000];
keyframes.forEach(time => {
  console.log(`At ${time}ms:`, captureState(time));
});
```

---

## Common Mismatches and Fixes

### 1. Easing Feels Different

AE's "Easy Ease" isn't exactly `easeInOutCubic`. Get the exact curve:

```javascript
// AE Easy Ease is approximately:
'cubicBezier(0.42, 0, 0.58, 1)'

// But Mika's custom curves are more precise:
'cubicBezier(0.16, 1, 0.3, 1)'  // Her "smooth enter"
```

### 2. Transform Origin Mismatch

AE anchors transforms at the layer's anchor point. CSS defaults to center:

```css
/* If AE anchor is at top-left */
.element { transform-origin: top left; }

/* If AE anchor is at a specific point */
.element { transform-origin: 30px 50px; }
```

### 3. Timing Drift

Small rounding differences accumulate over long sequences:

```javascript
// ❌ Relative offsets accumulate error
tl.add({ ... })
  .add({ ... }, '-=200')
  .add({ ... }, '-=150')  // Actual start depends on previous durations

// ✅ Absolute offsets match the timing sheet exactly
tl.add({ ... }, 0)
  .add({ ... }, 300)
  .add({ ... }, 600)
```

### 4. Subpixel Rendering

AE renders at exact positions. Browsers round to pixels:

```javascript
// AE: translateY from 40.5 to 0
// Browser: might render at 40px or 41px

// Fix: use will-change to enable subpixel rendering
// Or accept the 0.5px difference (usually invisible)
```

---

## The Handoff Workflow

```
  Mika (After Effects)              You (Code)
  ─────────────────────             ──────────────
  1. Creates motion comp     →
  2. Exports timing sheet    →      3. Translate to timeline
  3. Notes easing curves     →      4. Match cubic-bezier values
  4. Records reference video →      5. Side-by-side comparison
  5. Reviews implementation  →      6. Adjust per feedback
                             ←      7. Final sign-off
```

### Mika's Export Checklist

What you need from the motion designer:

- [ ] Timing sheet (element, start, duration, property, from/to, easing)
- [ ] Cubic-bezier values for custom curves
- [ ] Transform origins for each element
- [ ] Reference video (screen recording at 60fps)
- [ ] Key moments to verify (timestamps)
- [ ] Responsive notes (what changes on mobile)

---

## Automating the Translation

For large comps, a helper that converts timing sheet JSON to Anime.js code:

```javascript
// Timing sheet as data
const timingSheet = [
  { target: '.hero-title', start: 0, duration: 800, property: 'opacity', from: 0, to: 1, easing: 'linear' },
  { target: '.hero-title', start: 0, duration: 1000, property: 'translateY', from: 40, to: 0, easing: 'cubicBezier(0.16, 1, 0.3, 1)' },
  // ... more entries
];

// Convert to timeline
function buildTimeline(sheet) {
  const tl = anime.timeline({ autoplay: false });

  // Group by target + start time
  const groups = {};
  sheet.forEach(entry => {
    const key = `${entry.target}@${entry.start}`;
    if (!groups[key]) groups[key] = { target: entry.target, start: entry.start, props: {} };
    groups[key].props[entry.property] = {
      value: [entry.from, entry.to],
      duration: entry.duration,
      easing: entry.easing,
    };
  });

  // Add to timeline
  Object.values(groups).forEach(group => {
    tl.add({
      targets: group.target,
      ...group.props,
    }, group.start);
  });

  return tl;
}

const intro = buildTimeline(timingSheet);
intro.play();
```

Feed in the timing sheet data, get a working timeline. Useful when Mika iterates frequently.

---

## Mika's Final Review

She watches the implementation side-by-side with her comp. Frame 0. Frame 300. Frame 600. Scrubbing back and forth.

> "The hour hand rotation — it's 2 frames late. Start it at 880ms instead of 900ms."

You change one number. She watches again.

> "Perfect. Ship it."

---

## What You Learned

- **Timing sheets** — the bridge between design and code
- **Absolute offsets** — match timing sheet directly (no drift)
- **Per-property objects** — independent timing per property
- **AE easing extraction** — graph editor → cubic-bezier values
- **Transform origin** — match AE anchor points
- **Side-by-side comparison** — scrub video + animation simultaneously
- **Snapshot testing** — capture state at key moments
- **Automated translation** — timing sheet JSON → timeline code
- **Iteration workflow** — small adjustments, quick feedback

The comp matches. Every element, every frame, every curve. The motion designer's vision is preserved in code.

But there's one more consideration before shipping: not everyone can enjoy this motion. Some people need it reduced or removed entirely.

---

[← Chapter 17: Framework Integration](chapter-17-framework-integration.md) | [Chapter 19: Accessibility →](chapter-19-accessibility.md)
