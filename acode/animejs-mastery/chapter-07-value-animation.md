# Chapter 7: Numbers Count Up to Specs — Value Animation

[← Chapter 6: Timelines](chapter-06-timelines.md) | [Chapter 8: SVG Animation →](chapter-08-svg-animation.md)

---

## The Brief

Below the watch hero, four spec cards display the watch's technical specifications:

| Spec | Value | Unit |
|---|---|---|
| Water Resistance | 300 | meters |
| Power Reserve | 72 | hours |
| Case Diameter | 41 | mm |
| Movement Frequency | 28800 | vph |

Mika's comp shows them counting up from 0 to their final value when they scroll into view. Like an odometer rolling. The numbers should feel mechanical — no bounce, no overshoot, just precise incrementation.

---

## Animating JavaScript Objects

Anime.js can animate any JavaScript object's numeric properties:

```javascript
const counter = { value: 0 };

anime({
  targets: counter,
  value: 300,
  duration: 2000,
  easing: 'easeOutExpo',
  round: 1,  // Round to nearest integer
  update: () => {
    document.querySelector('.spec-value').textContent = counter.value;
  },
});
```

The `targets` isn't a DOM element — it's a plain object. Anime.js interpolates `counter.value` from 0 to 300 over 2 seconds. The `update` callback runs every frame and pushes the current value to the DOM.

---

## The round Parameter

`round` controls decimal precision:

```javascript
// Round to integer (no decimals)
anime({ targets: obj, value: 100, round: 1 });
// 0, 1, 2, 3, ... 98, 99, 100

// Round to 1 decimal place
anime({ targets: obj, value: 3.14, round: 10 });
// 0.0, 0.1, 0.2, ... 3.1, 3.14

// Round to 2 decimal places
anime({ targets: obj, value: 99.99, round: 100 });
// 0.00, 0.01, ... 99.98, 99.99

// No rounding (raw float)
anime({ targets: obj, value: 100 });
// 0.0000, 0.3847, 1.2934, ... 99.8761, 100
```

The `round` value is the precision multiplier: `round: 1` = integers, `round: 10` = 1 decimal, `round: 100` = 2 decimals.

For the watch specs, integers look right. No one says "300.47 meters water resistance."

---

## The Spec Counter Component

```html
<section class="specs">
  <div class="spec-card" data-target="300" data-suffix="m">
    <span class="spec-value">0</span>
    <span class="spec-unit">meters</span>
    <span class="spec-label">Water Resistance</span>
  </div>
  <div class="spec-card" data-target="72" data-suffix="h">
    <span class="spec-value">0</span>
    <span class="spec-unit">hours</span>
    <span class="spec-label">Power Reserve</span>
  </div>
  <div class="spec-card" data-target="41" data-suffix="mm">
    <span class="spec-value">0</span>
    <span class="spec-unit">mm</span>
    <span class="spec-label">Case Diameter</span>
  </div>
  <div class="spec-card" data-target="28800" data-suffix="vph">
    <span class="spec-value">0</span>
    <span class="spec-unit">vph</span>
    <span class="spec-label">Movement Frequency</span>
  </div>
</section>
```

```javascript
function animateSpecs() {
  document.querySelectorAll('.spec-card').forEach((card, i) => {
    const target = parseInt(card.dataset.target);
    const valueEl = card.querySelector('.spec-value');
    const counter = { value: 0 };

    anime({
      targets: counter,
      value: target,
      duration: 2000,
      delay: i * 200,  // Stagger the counters
      easing: 'easeOutExpo',
      round: 1,
      update: () => {
        valueEl.textContent = counter.value.toLocaleString();
      },
    });
  });
}
```

Each card counts to its target value. The `toLocaleString()` adds thousand separators (28,800 instead of 28800). The stagger makes them cascade rather than all starting at once.

---

## Easing Matters for Counting

Different easings create different counting feels:

```javascript
// Linear: steady count (boring, feels like a timer)
easing: 'linear'
// 0, 15, 30, 45, 60, 75, 90, ... 285, 300

// easeOutExpo: fast start, slow finish (dramatic reveal)
easing: 'easeOutExpo'
// 0, 180, 250, 275, 288, 294, 297, 299, 300

// easeInOutQuad: slow start, fast middle, slow end (mechanical)
easing: 'easeInOutQuad'
// 0, 2, 8, 20, 50, 100, 200, 270, 292, 298, 300

// Steps: discrete jumps (odometer feel)
easing: 'steps(20)'
// 0, 15, 30, 45, 60, ... 285, 300 (20 discrete steps)
```

For the watchmaker, `easeOutExpo` works — the number rushes to approximately the right value then precisely settles on the exact figure. Like a precision instrument locking in.

---

## Animating DOM Attributes

Beyond CSS properties and JS objects, Anime.js can animate HTML/SVG attributes directly:

```html
<progress class="spec-progress" value="0" max="100"></progress>
```

```javascript
anime({
  targets: '.spec-progress',
  value: 87,          // Animates the 'value' attribute
  duration: 1500,
  easing: 'easeOutQuad',
  round: 1,
});
```

Any numeric attribute works: `value`, `width`, `height`, `cx`, `cy`, `r`, `viewBox` values, etc.

---

## Multiple Object Properties

Animate several properties on one object simultaneously:

```javascript
const dashboardState = {
  speed: 0,
  rpm: 0,
  fuel: 100,
  temp: 20,
};

anime({
  targets: dashboardState,
  speed: 120,
  rpm: 4500,
  fuel: 73,
  temp: 90,
  duration: 3000,
  easing: 'easeOutQuad',
  round: 1,
  update: () => {
    document.querySelector('.speed').textContent = dashboardState.speed;
    document.querySelector('.rpm').textContent = dashboardState.rpm;
    document.querySelector('.fuel').textContent = dashboardState.fuel;
    document.querySelector('.temp').textContent = dashboardState.temp;
  },
});
```

One animation call, four values changing simultaneously. The `update` callback syncs them all to the DOM every frame.

---

## Formatting Numbers

The `update` callback is where you format:

```javascript
const counter = { value: 0 };

anime({
  targets: counter,
  value: 28800,
  duration: 2500,
  easing: 'easeOutExpo',
  round: 1,
  update: () => {
    // Add thousand separators
    const formatted = counter.value.toLocaleString();
    document.querySelector('.frequency').textContent = formatted;
  },
});
```

More formatting examples:

```javascript
// Currency
update: () => {
  el.textContent = `$${counter.value.toLocaleString()}`;
}

// Percentage
update: () => {
  el.textContent = `${counter.value}%`;
}

// With decimals
anime({
  targets: counter,
  value: 3.14159,
  round: 100000,  // 5 decimal places
  update: () => {
    el.textContent = counter.value.toFixed(5);
  },
});

// Padded (like a clock)
update: () => {
  const hours = Math.floor(counter.value / 3600);
  const mins = Math.floor((counter.value % 3600) / 60);
  const secs = counter.value % 60;
  el.textContent = `${hours}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}
```

---

## Value Animation in Timelines

Combine counting with the watch assembly:

```javascript
const specTimeline = anime.timeline({
  easing: 'easeOutExpo',
  autoplay: false,
});

// First: cards fade in with stagger
specTimeline.add({
  targets: '.spec-card',
  opacity: [0, 1],
  translateY: [30, 0],
  delay: anime.stagger(100),
  duration: 600,
  easing: 'cubicBezier(0.16, 1, 0.3, 1)',
});

// Then: each counter starts counting
const counters = [];
document.querySelectorAll('.spec-card').forEach((card, i) => {
  const target = parseInt(card.dataset.target);
  const counter = { value: 0 };
  counters.push(counter);

  specTimeline.add({
    targets: counter,
    value: target,
    duration: 2000,
    round: 1,
    update: () => {
      card.querySelector('.spec-value').textContent =
        counter.value.toLocaleString();
    },
  }, 400 + (i * 150));  // Stagger the count starts
});
```

Cards slide in, then numbers start counting with a cascade. The timeline coordinates both visual entrance and value animation.

---

## Animating CSS Custom Properties

Modern approach using CSS variables:

```javascript
anime({
  targets: document.documentElement,  // :root
  '--progress': [0, 87],
  duration: 1500,
  easing: 'easeOutQuad',
  round: 1,
});
```

```css
.progress-ring {
  /* CSS uses the animated variable */
  stroke-dashoffset: calc(283 - (283 * var(--progress) / 100));
}
```

This bridges value animation with CSS — animate a variable in JS, let CSS handle the visual. Useful for complex calculations that CSS can express but JS would be verbose for.

---

## Performance: update Callback

The `update` callback fires every frame (~60 times per second). Keep it fast:

```javascript
// ✅ Good: simple DOM update
update: () => {
  el.textContent = counter.value;
}

// ❌ Bad: heavy computation every frame
update: () => {
  const result = expensiveCalculation(counter.value);
  el.innerHTML = generateComplexHTML(result);
  triggerReflow();
}
```

Rules:
1. Cache DOM references outside the animation
2. Use `textContent` not `innerHTML`
3. Avoid triggering layout/reflow in update
4. If you must do heavy work, throttle it (skip frames)

```javascript
// Throttled update (every 3rd frame)
let frameCount = 0;
update: () => {
  frameCount++;
  if (frameCount % 3 === 0) {
    el.textContent = counter.value.toLocaleString();
  }
}
```

---

## Theo's Verdict

> "The numbers feel right. The easeOutExpo gives them urgency — they rush to the answer then lock in. Mechanical. Precise. Like the movement itself."

He looks at the spec section as a whole.

> "But the progress rings next to each number — they're static. They should fill as the number counts. The water resistance ring should fill to 100% (300m is the max). The power reserve ring to 72% (out of 100 hours max). Can you animate SVG strokes?"

SVG stroke animation. The progress ring. That's next.

---

## What You Learned

- **Object animation** — animate any JS object's numeric properties
- **round** — control decimal precision (1 = integer, 10 = 1 decimal)
- **update callback** — sync animated values to the DOM every frame
- **DOM attributes** — animate `value`, `width`, any numeric attribute
- **Number formatting** — toLocaleString, toFixed, padding in update
- **Timeline integration** — combine value animation with visual animation
- **CSS custom properties** — animate variables, let CSS handle visuals
- **Performance** — keep update callbacks fast, cache references

Four numbers count from 0 to their targets. The easing makes them feel precise. The stagger creates rhythm. The formatting makes them readable.

Next: SVG strokes, progress rings, and the visual language of completion.

---

[← Chapter 6: Timelines](chapter-06-timelines.md) | [Chapter 8: SVG Animation →](chapter-08-svg-animation.md)
