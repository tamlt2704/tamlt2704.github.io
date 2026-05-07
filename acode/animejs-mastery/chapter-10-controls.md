# Chapter 10: Pause, Play, Scrub with a Slider — Controls

[← Chapter 9: Motion Path](chapter-09-motion-path.md) | [Chapter 11: Scroll Animation →](chapter-11-scroll-animation.md)

---

## The Brief

Theo wants to present the watch assembly to the client with full control:

> "I need to scrub through it. Pause at the moment the hands mesh. Play it at half speed. Reverse it. The client will want to see specific moments over and over. Build me a control panel."

And for the actual site: a scroll-scrubbed version where the user controls the animation by scrolling. But first — the manual controls.

---

## The Animation Instance

Every `anime()` and `anime.timeline()` call returns an instance with full playback control:

```javascript
const assembly = anime.timeline({
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  autoplay: false,
});

assembly
  .add({ targets: '.dial', opacity: [0, 1], scale: [0.85, 1], duration: 600 })
  .add({ targets: '.hour-hand', rotate: [0, 210], duration: 1000 }, 400)
  .add({ targets: '.minute-hand', rotate: [0, 60], duration: 800 }, 800)
  .add({ targets: '.strap', scaleY: [0, 1], duration: 500 }, 1200)
  .add({ targets: '.brand', opacity: [0, 1], duration: 400 }, 1500);
```

---

## Control Methods

```javascript
assembly.play();       // Start or resume from current position
assembly.pause();      // Freeze at current frame
assembly.restart();    // Jump to 0ms and play
assembly.reverse();    // Toggle direction (forward ↔ backward)
assembly.seek(800);    // Jump to 800ms (doesn't play, just positions)
```

### play() and pause()

```javascript
const playBtn = document.querySelector('.btn-play');
const pauseBtn = document.querySelector('.btn-pause');

playBtn.addEventListener('click', () => assembly.play());
pauseBtn.addEventListener('click', () => assembly.pause());
```

### restart()

```javascript
document.querySelector('.btn-restart').addEventListener('click', () => {
  assembly.restart();
});
```

`restart()` always plays forward from the beginning, regardless of current direction.

### reverse()

```javascript
document.querySelector('.btn-reverse').addEventListener('click', () => {
  assembly.reverse();
  // If paused, need to play after reversing
  if (assembly.paused) assembly.play();
});
```

`reverse()` toggles the direction. If playing forward, it starts playing backward from the current position. Call it again to go forward.

---

## Seeking: The Scrub Slider

`seek()` jumps to a specific time without playing:

```javascript
const slider = document.querySelector('.timeline-slider');

slider.addEventListener('input', (e) => {
  const time = (e.target.value / 100) * assembly.duration;
  assembly.seek(time);
});
```

```html
<input
  type="range"
  class="timeline-slider"
  min="0"
  max="100"
  value="0"
  step="0.1"
/>
```

The slider maps 0–100 to 0–duration. As the user drags, the animation jumps to that point. The watch assembly freezes at any frame.

### Syncing Slider with Playback

When the animation plays, the slider should follow:

```javascript
const assembly = anime.timeline({
  autoplay: false,
  update: (anim) => {
    slider.value = anim.progress;  // 0–100
  },
});

// Pause while scrubbing, resume on release
slider.addEventListener('mousedown', () => assembly.pause());
slider.addEventListener('mouseup', () => assembly.play());
slider.addEventListener('input', (e) => {
  assembly.seek((e.target.value / 100) * assembly.duration);
});
```

Now the slider and animation are bidirectionally synced — drag to scrub, or watch it advance during playback.

---

## Speed Control

Anime.js doesn't have a native speed property, but you can simulate it by adjusting how seek advances:

```javascript
// Playback speed multiplier
let speed = 1;

document.querySelector('.speed-half').addEventListener('click', () => speed = 0.5);
document.querySelector('.speed-normal').addEventListener('click', () => speed = 1);
document.querySelector('.speed-double').addEventListener('click', () => speed = 2);

// Custom playback loop with speed control
let lastTime = null;
let currentTime = 0;

function customPlay() {
  function tick(timestamp) {
    if (lastTime === null) lastTime = timestamp;
    const delta = (timestamp - lastTime) * speed;
    lastTime = timestamp;

    currentTime = Math.min(currentTime + delta, assembly.duration);
    assembly.seek(currentTime);

    if (currentTime < assembly.duration) {
      requestAnimationFrame(tick);
    }
  }
  requestAnimationFrame(tick);
}
```

For Theo's presentation, half-speed lets him narrate over the animation. Double-speed for quick reviews.

---

## The Control Panel

Complete implementation:

```html
<div class="control-panel">
  <div class="controls">
    <button class="btn" id="btn-restart">⏮</button>
    <button class="btn" id="btn-play">▶</button>
    <button class="btn" id="btn-pause">⏸</button>
    <button class="btn" id="btn-reverse">⏪</button>
  </div>
  <input type="range" id="scrubber" min="0" max="100" value="0" step="0.1" />
  <div class="time-display">
    <span id="current-time">0.00s</span> / <span id="total-time">0.00s</span>
  </div>
</div>
```

```javascript
const scrubber = document.getElementById('scrubber');
const currentTimeEl = document.getElementById('current-time');
const totalTimeEl = document.getElementById('total-time');
let isScrubbing = false;

const assembly = anime.timeline({
  autoplay: false,
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  update: (anim) => {
    if (!isScrubbing) {
      scrubber.value = anim.progress;
    }
    const currentMs = (anim.progress / 100) * anim.duration;
    currentTimeEl.textContent = (currentMs / 1000).toFixed(2) + 's';
  },
});

// Add animations to timeline...
totalTimeEl.textContent = (assembly.duration / 1000).toFixed(2) + 's';

// Button controls
document.getElementById('btn-play').addEventListener('click', () => assembly.play());
document.getElementById('btn-pause').addEventListener('click', () => assembly.pause());
document.getElementById('btn-restart').addEventListener('click', () => assembly.restart());
document.getElementById('btn-reverse').addEventListener('click', () => {
  assembly.reverse();
  if (!assembly.began || assembly.paused) assembly.play();
});

// Scrubber
scrubber.addEventListener('mousedown', () => {
  isScrubbing = true;
  assembly.pause();
});

scrubber.addEventListener('input', () => {
  const time = (scrubber.value / 100) * assembly.duration;
  assembly.seek(time);
});

scrubber.addEventListener('mouseup', () => {
  isScrubbing = false;
});
```

---

## Animation State Properties

Check what the animation is doing:

```javascript
assembly.paused;      // true if paused
assembly.began;       // true if has started at least once
assembly.completed;   // Promise (resolves when done)
assembly.progress;    // 0–100 (current progress percentage)
assembly.duration;    // Total duration in ms
assembly.currentTime; // Current time in ms
assembly.reversed;    // true if playing in reverse
```

Useful for conditional UI:

```javascript
function updateUI() {
  const playBtn = document.getElementById('btn-play');
  const pauseBtn = document.getElementById('btn-pause');

  playBtn.disabled = !assembly.paused;
  pauseBtn.disabled = assembly.paused;
}
```

---

## Controlling Individual Animations

You can control animations within a timeline independently if you keep references:

```javascript
// Store references to child animations
const dialAnim = anime({
  targets: '.dial',
  opacity: [0, 1],
  autoplay: false,
});

const handAnim = anime({
  targets: '.hour-hand',
  rotate: [0, 210],
  autoplay: false,
});

// Play them independently
dialAnim.play();
// Later...
handAnim.play();
```

But for coordinated sequences, the timeline approach is better — one control point for everything.

---

## Keyboard Shortcuts

For Theo's presentation:

```javascript
document.addEventListener('keydown', (e) => {
  switch (e.key) {
    case ' ':  // Space: toggle play/pause
      e.preventDefault();
      assembly.paused ? assembly.play() : assembly.pause();
      break;
    case 'ArrowRight':  // Right: advance 100ms
      assembly.seek(Math.min(assembly.currentTime + 100, assembly.duration));
      break;
    case 'ArrowLeft':  // Left: rewind 100ms
      assembly.seek(Math.max(assembly.currentTime - 100, 0));
      break;
    case 'r':  // R: restart
      assembly.restart();
      break;
    case 'Backspace':  // Backspace: reverse
      assembly.reverse();
      if (assembly.paused) assembly.play();
      break;
  }
});
```

Space to play/pause. Arrow keys to step frame by frame. R to restart. Theo can navigate the animation like a video editor.

---

## The Presentation Mode

For the client meeting, Theo wants specific "chapters" he can jump to:

```javascript
const chapters = {
  'dial': 0,
  'hour-hand': 400,
  'minute-hand': 800,
  'strap': 1200,
  'brand': 1500,
  'complete': assembly.duration,
};

function jumpToChapter(name) {
  assembly.pause();
  assembly.seek(chapters[name]);
}

// Chapter buttons
Object.keys(chapters).forEach(name => {
  const btn = document.createElement('button');
  btn.textContent = name;
  btn.addEventListener('click', () => jumpToChapter(name));
  document.querySelector('.chapters').appendChild(btn);
});
```

Theo clicks "hour-hand" and the animation jumps to exactly the moment the hour hand starts rotating. He can narrate each piece to the client.

---

## What You Learned

- **play(), pause()** — start/stop playback
- **restart()** — back to beginning, play forward
- **reverse()** — toggle direction
- **seek(ms)** — jump to specific time
- **progress** — 0–100 percentage
- **update callback** — sync UI with animation state
- **Scrubber** — bidirectional slider ↔ animation sync
- **Speed control** — custom rAF loop with multiplier
- **State properties** — paused, began, reversed, duration
- **Keyboard shortcuts** — presentation-friendly controls
- **Chapters** — named seek points for navigation

The watch assembly is now fully controllable. Theo can present it frame by frame. The client can see every detail.

But on the actual site, users won't have a control panel. They'll scroll. The animation should respond to scroll position — revealing the watch as the user scrolls down. That's scroll-driven animation.

---

[← Chapter 9: Motion Path](chapter-09-motion-path.md) | [Chapter 11: Scroll Animation →](chapter-11-scroll-animation.md)
