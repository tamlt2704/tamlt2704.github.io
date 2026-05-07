# Chapter 9: Watch Hands Sweep Along the Dial — Motion Path

[← Chapter 8: SVG Animation](chapter-08-svg-animation.md) | [Chapter 10: Controls →](chapter-10-controls.md)

---

## The Brief

Mika's latest revision:

> "The second hand doesn't just rotate. It sweeps along the dial markers — following the circular path. And the brand's signature animation: a golden dot traces the outline of the watch case, like light catching the bezel."

Simple rotation works for the hour and minute hands. But for the second hand's precise sweep and the bezel light trace, you need motion path — making an element follow an SVG path.

---

## What Is Motion Path?

Motion path moves an element along an SVG `<path>` definition. Instead of animating `translateX` and `translateY` separately (which gives you straight lines), the element follows curves, arcs, and complex shapes.

```
Regular animation:          Motion path:
A ──────────── B            A ╭──────╮ B
(straight line)              ╰──╮  ╭─╯
                                ╰──╯
                            (follows the path shape)
```

---

## Basic Motion Path

Define an SVG path, then tell Anime.js to move an element along it:

```html
<svg viewBox="0 0 400 400" class="motion-svg">
  <!-- The path to follow (can be invisible) -->
  <path
    id="bezel-path"
    d="M200,20 A180,180 0 1,1 199.99,20"
    fill="none"
    stroke="none"
  />
</svg>

<!-- The element that moves along the path -->
<div class="light-dot"></div>
```

```javascript
const path = anime.path('#bezel-path');

anime({
  targets: '.light-dot',
  translateX: path('x'),
  translateY: path('y'),
  rotate: path('angle'),  // Rotate to follow path direction
  duration: 3000,
  easing: 'linear',
  loop: true,
});
```

### anime.path()

`anime.path(selector)` returns a function that extracts motion data from an SVG path:

```javascript
const path = anime.path('#my-path');

path('x')      // X position along the path
path('y')      // Y position along the path
path('angle')  // Rotation angle at each point (tangent)
```

These are passed as property values. Anime.js interpolates the element's position along the path over the animation duration.

---

## The Bezel Light Trace

A golden dot traces the circular bezel of the watch:

```html
<div class="watch-container">
  <svg class="watch-svg" viewBox="0 0 300 300">
    <!-- Circular bezel path -->
    <path
      id="bezel-trace"
      d="M150,15 A135,135 0 1,1 149.99,15"
      fill="none"
      stroke="none"
    />
    <!-- Watch face elements... -->
  </svg>

  <!-- The light dot -->
  <div class="bezel-light"></div>
</div>
```

```css
.watch-container {
  position: relative;
  width: 300px;
  height: 300px;
}

.bezel-light {
  position: absolute;
  top: 0;
  left: 0;
  width: 6px;
  height: 6px;
  background: #c8a864;
  border-radius: 50%;
  box-shadow: 0 0 10px #c8a864, 0 0 20px rgba(200, 168, 100, 0.5);
}
```

```javascript
const bezelPath = anime.path('#bezel-trace');

anime({
  targets: '.bezel-light',
  translateX: bezelPath('x'),
  translateY: bezelPath('y'),
  duration: 4000,
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  loop: true,
});
```

The golden dot traces the watch bezel continuously. The glow effect (box-shadow) creates the illusion of light catching the polished metal.

---

## Rotation Alignment

By default, the element doesn't rotate as it follows the path. Add `path('angle')` to make it face the direction of travel:

```javascript
// Without angle: element stays upright
anime({
  targets: '.arrow',
  translateX: path('x'),
  translateY: path('y'),
  duration: 2000,
});

// With angle: element rotates to follow path direction
anime({
  targets: '.arrow',
  translateX: path('x'),
  translateY: path('y'),
  rotate: path('angle'),  // Faces direction of travel
  duration: 2000,
});
```

For the bezel light (a circle), rotation doesn't matter visually. But for arrows, cars, or directional elements, `path('angle')` is essential.

---

## Partial Path Animation

Animate along only a portion of the path using keyframes or by manipulating the path data:

```javascript
// Full path
anime({
  targets: '.dot',
  translateX: path('x'),
  translateY: path('y'),
  duration: 3000,
});

// To animate a partial path, use the animation's seek or
// control the duration relative to the full path
```

Or create a path that only covers the desired segment:

```html
<!-- Quarter circle (90° arc) for the second hand sweep -->
<path id="quarter-sweep" d="M150,15 A135,135 0 0,1 285,150" />
```

```javascript
const quarterPath = anime.path('#quarter-sweep');

anime({
  targets: '.second-hand-tip',
  translateX: quarterPath('x'),
  translateY: quarterPath('y'),
  rotate: quarterPath('angle'),
  duration: 15000,  // 15 seconds for 90° (quarter of a minute)
  easing: 'linear',
  loop: true,
});
```

---

## The Second Hand Sweep

The second hand sweeps smoothly (not ticking) around the dial:

```html
<svg class="watch-face" viewBox="0 0 300 300">
  <!-- Full circle path for the second hand tip -->
  <path
    id="seconds-path"
    d="M150,25 A125,125 0 1,1 149.99,25"
    fill="none"
    stroke="none"
  />

  <!-- Second hand -->
  <line
    class="second-hand"
    x1="150" y1="150"
    x2="150" y2="30"
    stroke="#c8a864"
    stroke-width="1"
    stroke-linecap="round"
  />
</svg>
```

For the second hand, simple rotation is actually better than motion path (it rotates around a fixed center). Motion path is for elements that need to travel along a shape:

```javascript
// Second hand: simple rotation (better for this case)
anime({
  targets: '.second-hand',
  rotate: [0, 360],
  duration: 60000,  // 60 seconds per revolution
  easing: 'linear',
  loop: true,
});
```

Motion path shines when the path isn't a simple circle — curves, spirals, figure-eights, or the outline of a complex shape.

---

## Complex Path Examples

### Figure-Eight

```html
<path id="figure-eight"
  d="M200,150 C200,50 350,50 350,150 C350,250 200,250 200,150
     C200,50 50,50 50,150 C50,250 200,250 200,150" />
```

```javascript
const fig8 = anime.path('#figure-eight');

anime({
  targets: '.orbiting-dot',
  translateX: fig8('x'),
  translateY: fig8('y'),
  duration: 6000,
  easing: 'linear',
  loop: true,
});
```

### Spiral

```javascript
// Generate a spiral path programmatically
function spiralPath(cx, cy, startR, endR, turns) {
  let d = '';
  const steps = turns * 36;  // 36 points per turn
  for (let i = 0; i <= steps; i++) {
    const angle = (i / 36) * 2 * Math.PI;
    const r = startR + (endR - startR) * (i / steps);
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    d += (i === 0 ? 'M' : 'L') + `${x},${y} `;
  }
  return d;
}

// Create the path element
const pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
pathEl.setAttribute('d', spiralPath(200, 200, 20, 150, 3));
pathEl.setAttribute('id', 'spiral');
document.querySelector('svg').appendChild(pathEl);

const spiral = anime.path('#spiral');
anime({
  targets: '.particle',
  translateX: spiral('x'),
  translateY: spiral('y'),
  rotate: spiral('angle'),
  duration: 4000,
  easing: 'easeInQuad',  // Accelerates outward
  loop: true,
});
```

---

## Multiple Elements on One Path

Stagger multiple elements along the same path:

```javascript
const path = anime.path('#bezel-trace');

anime({
  targets: '.bezel-dot',  // Multiple dots
  translateX: path('x'),
  translateY: path('y'),
  duration: 4000,
  delay: anime.stagger(500),  // Each dot starts 500ms later
  easing: 'linear',
  loop: true,
});
```

Five dots chase each other around the bezel, evenly spaced by their stagger delay. Creates a "loading" or "processing" feel.

---

## Combining Motion Path with Other Properties

The element can animate other properties while following the path:

```javascript
const path = anime.path('#bezel-trace');

anime({
  targets: '.bezel-light',
  translateX: path('x'),
  translateY: path('y'),
  scale: [0.5, 1.5, 0.5],  // Pulses while moving
  opacity: [0.3, 1, 0.3],  // Fades in and out
  duration: 4000,
  easing: 'linear',
  loop: true,
});
```

The light dot traces the bezel while pulsing in size and opacity — like a reflection catching and releasing light as it moves around the polished surface.

---

## Performance Considerations

Motion path animations are GPU-friendly because they only use `transform` (translateX, translateY, rotate). But complex paths with many points can be expensive to calculate.

Tips:
1. Simplify paths — fewer control points = faster calculation
2. Use `will-change: transform` on the moving element
3. For many elements on one path, consider CSS `offset-path` instead (native, no JS per frame)

```css
/* Native CSS motion path (no Anime.js needed for simple cases) */
.dot {
  offset-path: path('M10,80 C40,10 65,10 95,80 S150,150 180,80');
  animation: move 3s linear infinite;
}

@keyframes move {
  100% { offset-distance: 100%; }
}
```

Use Anime.js motion path when you need: easing control, timeline integration, dynamic paths, or coordination with other animations.

---

## What You Learned

- **anime.path()** — extracts x, y, angle from SVG paths
- **path('x'), path('y')** — position along the path
- **path('angle')** — rotation to face direction of travel
- **Circular paths** — bezel traces, orbital animations
- **Complex paths** — figure-eights, spirals, custom shapes
- **Multiple elements** — stagger along the same path
- **Combined properties** — animate scale/opacity while following path
- **When to use** — complex curves; simple rotation doesn't need it
- **Performance** — GPU-friendly transforms, simplify path points

The bezel light traces the watch case. The brand animation has a signature motion. Motion path adds a dimension that simple translate animations can't achieve.

Now you have all the building blocks: properties, easing, stagger, timelines, values, SVG, and motion paths. But how do you control all of this? Play, pause, scrub, reverse — on demand. That's the control layer.

---

[← Chapter 8: SVG Animation](chapter-08-svg-animation.md) | [Chapter 10: Controls →](chapter-10-controls.md)
