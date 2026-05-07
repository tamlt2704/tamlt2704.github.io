# Chapter 5: Loop the Loading Pulse Forever — Playback

[← Chapter 4: Stagger](chapter-04-stagger.md) | [Chapter 6: Timelines →](chapter-06-timelines.md)

---

## The Brief

Three things need looping behavior:

1. **Loading dots** — pulse forever while the watch image loads
2. **Scroll hint** — a gentle bounce that plays once after 3 seconds of inactivity
3. **Background gradient** — slowly shifts hue in an infinite cycle

And Theo adds: "The loading animation should stop gracefully when the image loads — not just vanish mid-pulse."

---

## Loop

The `loop` property repeats the animation:

```javascript
// Loop forever
anime({
  targets: '.loading-dot',
  scale: [1, 1.4],
  opacity: [1, 0.5],
  duration: 600,
  loop: true,  // Infinite
  easing: 'easeInOutSine',
});

// Loop 3 times
anime({
  targets: '.notification-badge',
  scale: [1, 1.2],
  duration: 300,
  loop: 3,
  easing: 'easeInOutQuad',
});
```

With `loop: true`, the animation restarts from the beginning after completing. With `loop: 3`, it plays 3 times total then stops.

---

## Direction

Control which way the animation plays:

```javascript
// Normal: 0 → 1 → 0 → 1 → 0 → 1 (snaps back to start each loop)
anime({
  targets: '.box',
  translateX: 200,
  direction: 'normal',
  loop: true,
});

// Reverse: 1 → 0 → 1 → 0 (plays backward)
anime({
  targets: '.box',
  translateX: 200,
  direction: 'reverse',
  loop: true,
});

// Alternate: 0 → 1 → 0 → 1 → 0 (ping-pong)
anime({
  targets: '.box',
  translateX: 200,
  direction: 'alternate',
  loop: true,
});
```

### Normal vs Alternate

```
normal + loop:
  ┌──╱│──╱│──╱│
  │╱  │╱  │╱  │
  └───┴───┴───┘
  (jumps back to start each iteration)

alternate + loop:
  ┌──╱╲──╱╲──╱
  │╱    ╲╱    ╲
  └──────────────
  (smoothly reverses — no jump)
```

For looping animations, `direction: 'alternate'` almost always looks better because there's no jarring snap back to the start position.

---

## The Loading Dots

```html
<div class="loading">
  <span class="loading-dot"></span>
  <span class="loading-dot"></span>
  <span class="loading-dot"></span>
</div>
```

```css
.loading {
  display: flex;
  gap: 8px;
}

.loading-dot {
  width: 8px;
  height: 8px;
  background: #c8a864;
  border-radius: 50%;
}
```

```javascript
const loadingAnimation = anime({
  targets: '.loading-dot',
  scale: [1, 1.5],
  opacity: [1, 0.4],
  delay: anime.stagger(150),
  duration: 500,
  direction: 'alternate',
  loop: true,
  easing: 'easeInOutSine',
});
```

Three dots pulse in sequence, forever. The stagger creates a wave effect. `alternate` makes them smoothly return to their original size.

---

## Autoplay

By default, animations start immediately. Disable this with `autoplay`:

```javascript
const scrollHint = anime({
  targets: '.scroll-indicator',
  translateY: [0, 10],
  opacity: [1, 0.5],
  duration: 800,
  direction: 'alternate',
  loop: 3,
  easing: 'easeInOutSine',
  autoplay: false,  // Don't start yet
});

// Start after 3 seconds of no scroll
let scrollTimeout;
function resetScrollTimer() {
  clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(() => {
    scrollHint.play();
  }, 3000);
}

window.addEventListener('scroll', resetScrollTimer);
resetScrollTimer();  // Start the timer on load
```

The scroll hint sits dormant until 3 seconds pass without scrolling. Then it gently bounces 3 times to say "there's more below."

---

## Playback Controls

Every `anime()` call returns an instance with control methods:

```javascript
const anim = anime({
  targets: '.element',
  translateX: 250,
  duration: 2000,
  easing: 'easeInOutQuad',
  autoplay: false,
});

// Control methods
anim.play();      // Start or resume
anim.pause();     // Freeze at current position
anim.restart();   // Jump to start and play
anim.reverse();   // Reverse direction
anim.seek(1000);  // Jump to 1000ms
anim.seek(anim.duration * 0.5);  // Jump to 50%
```

### Stopping the Loading Animation Gracefully

Theo said: "Don't just vanish mid-pulse." Here's how:

```javascript
// When the image loads, let the current loop finish then stop
watchImage.addEventListener('load', () => {
  // Option 1: Let current iteration complete, then stop
  loadingAnimation.loop = 1;  // Change to "play once more"

  // Option 2: Fade out the loading container
  anime({
    targets: '.loading',
    opacity: 0,
    duration: 300,
    easing: 'easeOutQuad',
    complete: () => {
      document.querySelector('.loading').style.display = 'none';
    },
  });
});
```

Option 2 is cleaner — it fades out the entire loading container regardless of where the dots are in their cycle.

---

## The completed Promise

Animation instances have a `completed` property — a Promise that resolves when the animation finishes:

```javascript
const entrance = anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [30, 0],
  duration: 800,
  easing: 'easeOutCubic',
});

// Wait for it to finish, then do something
entrance.completed.then(() => {
  console.log('Hero title is in position');
  // Start the next animation
});

// Or with async/await
async function playIntro() {
  await anime({
    targets: '.hero-title',
    opacity: [0, 1],
    translateY: [30, 0],
    duration: 800,
    easing: 'easeOutCubic',
  }).completed;

  await anime({
    targets: '.hero-subtitle',
    opacity: [0, 1],
    translateY: [20, 0],
    duration: 600,
    easing: 'easeOutCubic',
  }).completed;

  console.log('Intro complete');
}
```

This is a cleaner alternative to callback nesting. But for complex sequences, timelines (Chapter 6) are still better.

---

## EndDelay

`endDelay` adds time after the animation completes but before the next loop starts:

```javascript
anime({
  targets: '.pulse-ring',
  scale: [1, 2],
  opacity: [0.8, 0],
  duration: 1000,
  endDelay: 500,   // Wait 500ms before looping
  loop: true,
  easing: 'easeOutQuad',
});
```

Without `endDelay`, the ring immediately resets and pulses again. With it, there's a 500ms pause between pulses — feels more natural, like a heartbeat.

---

## Loop Callbacks

Track loop iterations:

```javascript
let loopCount = 0;

anime({
  targets: '.loading-dot',
  scale: [1, 1.5],
  delay: anime.stagger(150),
  duration: 500,
  direction: 'alternate',
  loop: true,
  easing: 'easeInOutSine',
  loopBegin: () => {
    loopCount++;
    console.log(`Loop ${loopCount} started`);
  },
  loopComplete: () => {
    console.log(`Loop ${loopCount} finished`);
    // Stop after 10 loops if image still hasn't loaded
    if (loopCount >= 10) {
      // Show error state
    }
  },
});
```

---

## The Background Gradient Cycle

A slow, infinite color shift for the hero background:

```javascript
anime({
  targets: '.hero-section',
  background: [
    'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
    'linear-gradient(135deg, #1a1a2e 0%, #0a0a0a 100%)',
  ],
  duration: 8000,
  direction: 'alternate',
  loop: true,
  easing: 'easeInOutSine',
});
```

Wait — Anime.js can't interpolate gradient strings directly. For complex background animations, animate a custom property instead:

```javascript
const gradientState = { angle: 135, stop1: 10, stop2: 90 };

anime({
  targets: gradientState,
  angle: [135, 225],
  stop1: [10, 40],
  stop2: [90, 60],
  duration: 8000,
  direction: 'alternate',
  loop: true,
  easing: 'easeInOutSine',
  update: () => {
    document.querySelector('.hero-section').style.background =
      `linear-gradient(${gradientState.angle}deg, #0a0a0a ${gradientState.stop1}%, #1a1a2e ${gradientState.stop2}%)`;
  },
});
```

Animate a JavaScript object, use the `update` callback to apply it to the DOM. This pattern works for anything Anime.js can't directly interpolate.

---

## Combining Playback Options

A complete loading animation with all playback features:

```javascript
const loader = anime({
  targets: '.loading-dot',
  keyframes: [
    { scale: 1, opacity: 1 },
    { scale: 1.5, opacity: 0.4 },
    { scale: 1, opacity: 1 },
  ],
  delay: anime.stagger(150),
  duration: 900,
  endDelay: 300,
  loop: true,
  easing: 'easeInOutSine',
  autoplay: false,  // Start manually
});

// Start loading
function showLoading() {
  document.querySelector('.loading').style.display = 'flex';
  loader.play();
}

// Stop loading gracefully
function hideLoading() {
  anime({
    targets: '.loading',
    opacity: [1, 0],
    duration: 300,
    easing: 'easeOutQuad',
    complete: () => {
      loader.pause();
      document.querySelector('.loading').style.display = 'none';
      document.querySelector('.loading').style.opacity = '1';  // Reset for next use
    },
  });
}
```

---

## Theo's Next Request

> "Good. The loading works. The scroll hint is subtle. Now — the big one. The watch assembly. The dial fades in, then the hour hand rotates into position, then the minute hand (overlapping with the hour hand), then the strap unfolds. It's a sequence. Each piece depends on the previous one finishing — or starting."

You could chain with `completed` promises. You could nest callbacks. But with 4+ elements and overlapping timing, you need a proper timeline.

---

## What You Learned

- **loop** — `true` for infinite, number for specific count
- **direction** — 'normal', 'reverse', 'alternate'
- **autoplay** — `false` to create dormant animations
- **Controls** — play(), pause(), restart(), reverse(), seek()
- **completed** — Promise for sequencing
- **endDelay** — pause between loop iterations
- **Loop callbacks** — loopBegin, loopComplete
- **Graceful stop** — fade out container, don't kill mid-animation
- **Object animation** — animate JS objects, apply in update callback

The loading dots pulse. The scroll hint waits. The gradient cycles. All with playback control.

But the watch assembly needs something more powerful — a timeline where animations can overlap, offset, and depend on each other. That's the real choreography tool.

---

[← Chapter 4: Stagger](chapter-04-stagger.md) | [Chapter 6: Timelines →](chapter-06-timelines.md)
