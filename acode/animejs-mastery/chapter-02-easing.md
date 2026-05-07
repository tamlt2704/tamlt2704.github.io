# Chapter 2: The Entrance Feels Robotic — Easing Functions

[← Chapter 1: First Animation](chapter-01-first-animation.md) | [Chapter 3: Property Parameters →](chapter-03-property-parameters.md)

---

## The Problem

Theo watches the hero animation again. Then he opens After Effects and shows you Mika's motion comp:

> "See how the heading decelerates? It doesn't just slow down — it has weight. Like a pendulum settling. Your version feels like a car braking at a traffic light. Mika's feels like a grandfather clock."

You compare:

- Your animation: `easeOutCubic` — smooth deceleration, generic
- Mika's comp: custom curve — sharp initial velocity, long gentle settle

The difference is subtle but real. Easing is the personality of motion.

---

## What Easing Actually Does

An easing function maps time (0→1) to progress (0→1). Without easing, both advance at the same rate (linear). With easing, progress can rush ahead or lag behind time.

```
Linear:                    easeOutCubic:
progress                   progress
  1 ┤        ╱              1 ┤     ╭────────
    │      ╱                  │    ╱
    │    ╱                    │   ╱
    │  ╱                      │  │
  0 ┤╱─────────── time      0 ┤─╯──────────── time
    0            1              0            1
```

With `easeOutCubic`, the element covers most of the distance in the first 30% of time, then spends 70% of time on the last bit of movement. Fast start, gentle landing.

---

## Built-in Easings

Anime.js includes 31 built-in easing functions. They follow a naming pattern:

```
ease[Direction][Strength]

Direction: In, Out, InOut
Strength: Quad, Cubic, Quart, Quint, Sine, Expo, Circ, Back, Elastic, Bounce
```

### Direction

| Direction | Behavior | Use Case |
|---|---|---|
| `easeIn` | Slow start, fast end | Elements leaving the screen |
| `easeOut` | Fast start, slow end | Elements entering the screen |
| `easeInOut` | Slow start + end | State transitions, loops |

### Strength

| Strength | Intensity | Character |
|---|---|---|
| `Sine` | Gentle | Barely noticeable |
| `Quad` | Moderate | Standard UI |
| `Cubic` | Medium | Good default |
| `Quart` | Strong | Noticeable deceleration |
| `Quint` | Very strong | Dramatic |
| `Expo` | Extreme | Attention-grabbing |
| `Circ` | Circular | Mechanical feel |
| `Back` | Overshoots | Playful, bouncy |
| `Elastic` | Springs | Energetic, fun |
| `Bounce` | Bounces at end | Cartoon-like |

### Examples

```javascript
// Gentle entrance (subtle)
anime({ targets: '.card', translateY: [20, 0], easing: 'easeOutSine' });

// Standard entrance (most UI)
anime({ targets: '.card', translateY: [30, 0], easing: 'easeOutCubic' });

// Dramatic entrance (hero elements)
anime({ targets: '.card', translateY: [60, 0], easing: 'easeOutExpo' });

// Playful entrance (overshoots then settles)
anime({ targets: '.card', translateY: [40, 0], easing: 'easeOutBack' });

// Energetic entrance (springs into place)
anime({ targets: '.card', scale: [0, 1], easing: 'easeOutElastic(1, 0.5)' });
```

---

## Elastic and Spring Parameters

Elastic and spring easings accept parameters:

```javascript
// easeOutElastic(amplitude, period)
anime({
  targets: '.notification',
  scale: [0, 1],
  easing: 'easeOutElastic(1, 0.5)',
  //                       ↑    ↑
  //              amplitude=1  period=0.5
});
```

| Parameter | Effect | Range |
|---|---|---|
| Amplitude | How far it overshoots | 1–3 (1 = subtle, 3 = wild) |
| Period | How fast it oscillates | 0.1–1 (lower = more bounces) |

```javascript
// Subtle spring
anime({ targets: '.a', scale: [0, 1], easing: 'easeOutElastic(1, 0.8)' });

// Medium spring
anime({ targets: '.b', scale: [0, 1], easing: 'easeOutElastic(1, 0.5)' });

// Wild spring
anime({ targets: '.c', scale: [0, 1], easing: 'easeOutElastic(2, 0.3)' });
```

For the watchmaker site? No elastic. No bounce. Mechanical precision doesn't spring.

---

## Spring Physics Easing

Anime.js v4 includes a spring easing that simulates real physics:

```javascript
anime({
  targets: '.element',
  translateX: 200,
  easing: 'spring(mass, stiffness, damping, velocity)',
});

// Example: heavy, stiff spring (quick settle)
anime({
  targets: '.watch-hand',
  rotate: 210,
  easing: 'spring(1, 100, 10, 0)',
  //              mass=1, stiffness=100, damping=10, velocity=0
});
```

| Parameter | What It Controls | Typical Range |
|---|---|---|
| Mass | Weight of the object | 1–5 |
| Stiffness | How strong the spring pulls | 50–300 |
| Damping | How quickly oscillation dies | 5–30 |
| Velocity | Initial speed | 0–10 |

High stiffness + high damping = snappy settle (UI buttons).
Low stiffness + low damping = lazy wobble (playful elements).
High stiffness + medium damping = mechanical precision (watch hands).

---

## Custom Cubic Bezier

For precise control, define your own curve with cubic-bezier:

```javascript
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [30, 0],
  duration: 800,
  easing: 'cubicBezier(0.16, 1, 0.3, 1)',  // Custom deceleration
});
```

The four values are control points: `(x1, y1, x2, y2)`. They shape the curve between (0,0) and (1,1).

Common custom curves:

```javascript
// "Smooth deceleration" — Mika's favorite
'cubicBezier(0.16, 1, 0.3, 1)'

// "Snappy" — fast in, abrupt stop
'cubicBezier(0.2, 0, 0, 1)'

// "Dramatic entrance" — explosive start
'cubicBezier(0.05, 0.95, 0.15, 1)'

// "Mechanical" — for the watchmaker
'cubicBezier(0.4, 0, 0.2, 1)'
```

Theo's curve for the watchmaker: `cubicBezier(0.4, 0, 0.2, 1)` — controlled acceleration, precise deceleration. No overshoot. No bounce. Mechanical.

---

## Custom Easing Functions

For complete control, pass a function:

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: function(el, i, total) {
    // el: the current target element
    // i: index of the element in targets
    // total: total number of targets
    // Must return a function that maps t (0→1) to progress (0→1)
    return function(t) {
      return t * t;  // Same as easeInQuad
    };
  },
});
```

A practical custom easing — "steps" for a mechanical clock feel:

```javascript
function steps(numSteps) {
  return function(el, i, total) {
    return function(t) {
      return Math.floor(t * numSteps) / numSteps;
    };
  };
}

anime({
  targets: '.second-hand',
  rotate: 360,
  duration: 60000,
  easing: steps(60),  // Ticks 60 times, like a real second hand
  loop: true,
});
```

---

## Easing Per Property

Different properties can have different easings:

```javascript
anime({
  targets: '.hero-title',
  opacity: {
    value: [0, 1],
    duration: 400,
    easing: 'linear',  // Opacity: linear looks natural
  },
  translateY: {
    value: [30, 0],
    duration: 800,
    easing: 'cubicBezier(0.4, 0, 0.2, 1)',  // Movement: mechanical
  },
});
```

Why linear for opacity? Because human perception of transparency is already non-linear. Applying an easing curve to opacity often makes it feel wrong — the element appears to "pop" in rather than smoothly materialize.

---

## Choosing the Right Easing

Theo's decision framework:

```
What's the brand personality?
├── Luxury/Precision → cubicBezier, no overshoot
├── Playful/Fun → easeOutBack, elastic
├── Corporate/Clean → easeOutCubic, easeOutQuart
└── Energetic/Bold → easeOutExpo, spring

What's the element doing?
├── Entering → easeOut (arrives with energy, settles)
├── Leaving → easeIn (gathers speed, exits)
├── Transitioning → easeInOut (smooth state change)
└── Looping → easeInOutSine (seamless cycle)

What's the distance?
├── Small (< 20px) → Gentle easing (Sine, Quad)
├── Medium (20-60px) → Standard easing (Cubic, Quart)
└── Large (> 60px) → Strong easing (Quint, Expo)
```

---

## The Watchmaker's Easing

After experimenting, you settle on the brand's motion language:

```javascript
// The Lumina easing constants
const EASING = {
  // Primary: mechanical precision
  mechanical: 'cubicBezier(0.4, 0, 0.2, 1)',

  // Entrance: controlled reveal
  enter: 'cubicBezier(0.16, 1, 0.3, 1)',

  // Exit: gathering momentum
  exit: 'cubicBezier(0.4, 0, 1, 1)',

  // Subtle: barely perceptible
  subtle: 'easeOutSine',

  // Clock tick: stepped motion
  tick: steps(60),
};

// Hero animation with brand easing
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [30, 0],
  duration: 900,
  easing: EASING.enter,
});

anime({
  targets: '.hero-subtitle',
  opacity: [0, 1],
  translateY: [15, 0],
  duration: 900,
  delay: 300,
  easing: EASING.enter,
});
```

---

## Visualizing Easings

A quick utility to compare easings side by side:

```html
<div class="easing-demo">
  <div class="track" data-easing="linear">
    <span class="label">linear</span>
    <div class="dot"></div>
  </div>
  <div class="track" data-easing="easeOutCubic">
    <span class="label">easeOutCubic</span>
    <div class="dot"></div>
  </div>
  <div class="track" data-easing="easeOutExpo">
    <span class="label">easeOutExpo</span>
    <div class="dot"></div>
  </div>
  <div class="track" data-easing="cubicBezier(0.4, 0, 0.2, 1)">
    <span class="label">mechanical</span>
    <div class="dot"></div>
  </div>
</div>
```

```javascript
document.querySelectorAll('.track').forEach(track => {
  const dot = track.querySelector('.dot');
  const easing = track.dataset.easing;

  anime({
    targets: dot,
    translateX: 300,
    duration: 1500,
    easing: easing,
    loop: true,
    direction: 'alternate',
  });
});
```

Run this and watch how different easings feel. The mechanical curve has a distinct character — controlled, intentional, precise.

---

## Theo's Verdict

You show Theo the updated hero with the custom cubic-bezier:

> "Now it feels like it belongs to this brand. The deceleration has weight — like a precision mechanism coming to rest. Not a rubber ball. Not a car. A watch movement."

He pauses.

> "But the heading and subtitle enter the same way. Same easing, same direction, same everything. It's coordinated but not choreographed. What if the heading slides from the left and the subtitle fades from below? Different properties, different values?"

You need more control over property parameters.

---

## What You Learned

- **Built-in easings** — 31 options following the `ease[Direction][Strength]` pattern
- **Direction** — In (leaving), Out (entering), InOut (transitioning)
- **Strength** — Sine (gentle) through Bounce (dramatic)
- **Elastic parameters** — amplitude and period control overshoot
- **Spring physics** — mass, stiffness, damping, velocity
- **Cubic bezier** — four control points for custom curves
- **Custom functions** — full programmatic control (steps, etc.)
- **Per-property easing** — different curves for different properties
- **Brand easing** — define constants that match the brand personality
- **Linear for opacity** — human perception handles the curve

The hero feels right. But Theo wants different animations for different elements — different starting positions, different distances, different units. You need to understand property parameters in depth.

That's Chapter 3.

---

[← Chapter 1: First Animation](chapter-01-first-animation.md) | [Chapter 3: Property Parameters →](chapter-03-property-parameters.md)
