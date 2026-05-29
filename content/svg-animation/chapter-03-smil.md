# Chapter 3: SMIL — Native SVG Animation

[prev: CSS Animation](./chapter-02-css-animation.md) | [next: GSAP](./chapter-04-gsap.md)

SMIL (Synchronized Multimedia Integration Language) is SVG's built-in animation system. No CSS, no JavaScript — just XML elements that define motion. While partially deprecated in Chrome (then un-deprecated), SMIL remains useful for self-contained SVG files that need to animate without external dependencies.

## Browser Support Note

SMIL is supported in all modern browsers (Chrome, Firefox, Safari, Edge). Internet Explorer never supported it. Chrome briefly deprecated SMIL in 2015 but reversed that decision. It's safe to use today, though CSS/JS animations are generally preferred for new projects. SMIL shines when you need a single SVG file with embedded animation (favicons, email signatures, standalone graphics).

## The animate Element

Animates a single attribute over time.

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <!-- Circle that changes color -->
  <circle cx="100" cy="100" r="50" fill="#3498db">
    <animate attributeName="fill"
             values="#3498db;#e74c3c;#2ecc71;#3498db"
             dur="3s"
             repeatCount="indefinite"/>
  </circle>
</svg>
```

Visually: A circle that smoothly cycles through blue, red, green, and back to blue continuously.

### Animating Position

```svg
<svg width="300" height="100" viewBox="0 0 300 100">
  <circle cx="30" cy="50" r="20" fill="#e74c3c">
    <animate attributeName="cx" from="30" to="270" dur="2s"
             repeatCount="indefinite" fill="freeze"/>
  </circle>
</svg>
```

Visually: A red circle sliding from left to right across the SVG, then jumping back to start and repeating.

### Animating Size

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="20" fill="#9b59b6">
    <animate attributeName="r" values="20;60;20" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
  </circle>
</svg>
```

Visually: A purple circle that pulses — growing large and fading, then shrinking back and becoming opaque again.

## animateTransform

Animates transform attributes (rotate, scale, translate).

### Rotation

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <rect x="75" y="75" width="50" height="50" fill="#3498db">
    <animateTransform attributeName="transform" type="rotate"
                      from="0 100 100" to="360 100 100"
                      dur="3s" repeatCount="indefinite"/>
  </rect>
</svg>
```

Visually: A blue square spinning around the center of the SVG (100,100). The `from/to` format is `"angle centerX centerY"`.

### Scale

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="30" fill="#2ecc71">
    <animateTransform attributeName="transform" type="scale"
                      values="1;1.5;1" dur="1.5s"
                      repeatCount="indefinite"
                      additive="sum"/>
  </circle>
</svg>
```

Visually: A green circle that grows to 1.5x size then shrinks back, pulsing continuously. Note: `additive="sum"` prevents the scale from overriding position.

### Combined Transforms

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <rect x="80" y="80" width="40" height="40" fill="#f39c12">
    <!-- Rotate -->
    <animateTransform attributeName="transform" type="rotate"
                      from="0 100 100" to="360 100 100"
                      dur="4s" repeatCount="indefinite"/>
    <!-- Scale (additive to combine with rotation) -->
    <animateTransform attributeName="transform" type="scale"
                      values="1;1.3;1" dur="2s"
                      repeatCount="indefinite" additive="sum"/>
  </rect>
</svg>
```

Visually: An orange square that spins while pulsing in size — both animations run simultaneously.

## animateMotion — Movement Along a Path

The most powerful SMIL feature: move an element along an arbitrary path.

```svg
<svg width="300" height="200" viewBox="0 0 300 200">
  <!-- The path to follow (visible for reference) -->
  <path d="M 20,100 C 20,20 280,20 280,100 C 280,180 20,180 20,100"
        fill="none" stroke="#ddd" stroke-width="1" stroke-dasharray="5,5"/>

  <!-- Moving element -->
  <circle cx="0" cy="0" r="10" fill="#e74c3c">
    <animateMotion dur="4s" repeatCount="indefinite" rotate="auto"
                   path="M 20,100 C 20,20 280,20 280,100 C 280,180 20,180 20,100"/>
  </circle>
</svg>
```

Visually: A red circle gliding along a figure-8 path (shown as a dashed grey line). The `rotate="auto"` makes the element orient itself along the path direction.

### Motion Along Path with mpath

Reference an existing path element instead of duplicating the path data:

```svg
<svg width="300" height="200" viewBox="0 0 300 200">
  <defs>
    <path id="track" d="M 20,150 Q 150,20 280,150"/>
  </defs>

  <!-- Visible track -->
  <use href="#track" fill="none" stroke="#ccc" stroke-width="2"/>

  <!-- Arrow following the track -->
  <polygon points="-8,-5 8,0 -8,5" fill="#3498db">
    <animateMotion dur="3s" repeatCount="indefinite" rotate="auto">
      <mpath href="#track"/>
    </animateMotion>
  </polygon>
</svg>
```

Visually: A blue arrow sliding along a curved arc, always pointing in the direction of travel.

## The set Element

Instantly changes an attribute at a specific time (no interpolation).

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="50" fill="#3498db">
    <!-- Change color instantly at 2s -->
    <set attributeName="fill" to="#e74c3c" begin="2s"/>
    <!-- Change again at 4s -->
    <set attributeName="fill" to="#2ecc71" begin="4s"/>
  </circle>
</svg>
```

Visually: A blue circle that abruptly turns red at 2 seconds, then abruptly turns green at 4 seconds — no smooth transition.

## Timing: values, keyTimes, keySplines

### values and keyTimes

Control exactly when each value is reached:

```svg
<svg width="300" height="100" viewBox="0 0 300 100">
  <circle cx="30" cy="50" r="15" fill="#e74c3c">
    <animate attributeName="cx"
             values="30;150;150;270"
             keyTimes="0;0.3;0.7;1"
             dur="3s" repeatCount="indefinite"/>
  </circle>
</svg>
```

Visually: A red circle that moves quickly to the middle (0-30% of time), pauses there (30-70%), then moves quickly to the right (70-100%). The `keyTimes` maps each value to a fraction of the total duration.

### keySplines (Easing)

Custom easing curves between keyframes (requires `calcMode="spline"`):

```svg
<svg width="300" height="100" viewBox="0 0 300 100">
  <circle cx="30" cy="50" r="15" fill="#9b59b6">
    <animate attributeName="cx"
             values="30;270;30"
             keyTimes="0;0.5;1"
             keySplines="0.42 0 1 1; 0 0 0.58 1"
             calcMode="spline"
             dur="2s" repeatCount="indefinite"/>
  </circle>
</svg>
```

Visually: A purple circle bouncing left to right with ease-in on the way right and ease-out on the way back — it accelerates leaving and decelerates arriving.

Each `keySplines` value is a cubic bezier: `x1 y1 x2 y2` (same format as CSS `cubic-bezier()`).

## repeatCount and fill

```svg
<svg width="200" height="100" viewBox="0 0 200 100">
  <!-- Plays 3 times then stops at final value -->
  <circle cx="30" cy="50" r="15" fill="#3498db">
    <animate attributeName="cx" from="30" to="170"
             dur="1s" repeatCount="3" fill="freeze"/>
  </circle>
</svg>
```

- `repeatCount="indefinite"` — loops forever
- `repeatCount="3"` — plays exactly 3 times
- `fill="freeze"` — holds the final value after animation ends
- `fill="remove"` (default) — snaps back to original value

## begin/end Triggers

### Delay

```svg
<svg width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="40" fill="#3498db">
    <animate attributeName="r" from="40" to="80" dur="1s"
             begin="2s" fill="freeze"/>
  </circle>
</svg>
```

### Event-Based Triggers

```svg
<svg width="300" height="100" viewBox="0 0 300 100">
  <!-- Click the button to start the animation -->
  <rect id="btn" x="10" y="30" width="80" height="40" rx="5" fill="#2ecc71" cursor="pointer"/>
  <text x="50" y="55" text-anchor="middle" fill="white" font-size="12" pointer-events="none">Click</text>

  <circle cx="150" cy="50" r="15" fill="#e74c3c">
    <animate attributeName="cx" from="150" to="280" dur="1s"
             begin="btn.click" fill="freeze"/>
  </circle>
</svg>
```

Visually: A green button and a red circle. Clicking the button launches the circle to the right.

### Trigger on Another Animation's End

```svg
<svg width="300" height="100" viewBox="0 0 300 100">
  <circle cx="30" cy="50" r="15" fill="#3498db">
    <!-- First animation -->
    <animate id="move-right" attributeName="cx" from="30" to="270" dur="1s" fill="freeze"/>
    <!-- Second starts when first ends -->
    <animate attributeName="fill" from="#3498db" to="#e74c3c" dur="0.5s"
             begin="move-right.end" fill="freeze"/>
  </circle>
</svg>
```

Visually: A blue circle slides to the right, then immediately turns red once it arrives.

## Chaining Animations

Build sequences by referencing previous animation IDs:

```svg
<svg width="300" height="200" viewBox="0 0 300 200">
  <rect x="20" y="80" width="40" height="40" fill="#3498db">
    <!-- Step 1: Move right -->
    <animate id="step1" attributeName="x" from="20" to="240" dur="1s" fill="freeze"/>
    <!-- Step 2: Move down -->
    <animate id="step2" attributeName="y" from="80" to="140" dur="0.5s"
             begin="step1.end" fill="freeze"/>
    <!-- Step 3: Change color -->
    <animate id="step3" attributeName="fill" from="#3498db" to="#e74c3c" dur="0.3s"
             begin="step2.end" fill="freeze"/>
    <!-- Step 4: Scale up -->
    <animateTransform attributeName="transform" type="scale" from="1" to="1.5" dur="0.5s"
                      begin="step3.end" fill="freeze"/>
  </rect>
</svg>
```

Visually: A blue square that (1) slides right, (2) drops down, (3) turns red, (4) grows larger — each step waiting for the previous to finish.

## Complete Example: Animated Loading Graphic

```svg
<svg width="100" height="100" viewBox="0 0 100 100">
  <!-- Outer ring rotating -->
  <circle cx="50" cy="50" r="40" fill="none" stroke="#3498db" stroke-width="3"
          stroke-dasharray="60 190" stroke-linecap="round">
    <animateTransform attributeName="transform" type="rotate"
                      from="0 50 50" to="360 50 50" dur="1.5s" repeatCount="indefinite"/>
  </circle>

  <!-- Inner ring rotating opposite -->
  <circle cx="50" cy="50" r="25" fill="none" stroke="#e74c3c" stroke-width="3"
          stroke-dasharray="40 120" stroke-linecap="round">
    <animateTransform attributeName="transform" type="rotate"
                      from="360 50 50" to="0 50 50" dur="2s" repeatCount="indefinite"/>
  </circle>

  <!-- Center dot pulsing -->
  <circle cx="50" cy="50" r="5" fill="#2ecc71">
    <animate attributeName="r" values="5;8;5" dur="1s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0.6;1" dur="1s" repeatCount="indefinite"/>
  </circle>
</svg>
```

Visually: Two concentric ring arcs spinning in opposite directions (blue outer, red inner) with a pulsing green dot in the center. A polished loading indicator using only SMIL — no CSS or JS needed.

## SMIL vs CSS vs JavaScript

| Feature            | SMIL                   | CSS                      | JavaScript              |
| ------------------ | ---------------------- | ------------------------ | ----------------------- |
| Motion along path  | Yes (animateMotion)    | No (limited offset-path) | Yes (manual)            |
| Event triggers     | Yes (begin="el.click") | Limited (:hover, :focus) | Yes (full)              |
| Chaining           | Yes (begin="id.end")   | Limited (delays)         | Yes (promises/timeline) |
| Self-contained SVG | Yes                    | Partial (inline style)   | No                      |
| Performance        | Good                   | Best                     | Varies                  |
| Browser support    | All modern             | All modern               | All                     |
| Tooling/debugging  | Poor                   | Good (DevTools)          | Best                    |

## Key Takeaways

- SMIL embeds animation directly in SVG markup — perfect for standalone SVG files
- `animate` handles attribute changes, `animateTransform` handles transforms
- `animateMotion` moves elements along arbitrary paths — SMIL's killer feature
- `keyTimes` and `keySplines` give precise timing control
- Chain animations with `begin="previousId.end"`
- Event triggers (`begin="element.click"`) add interactivity without JS
- Use SMIL for self-contained animated SVGs; prefer CSS/JS for web app animations
