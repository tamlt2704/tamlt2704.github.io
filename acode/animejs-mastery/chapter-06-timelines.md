# Chapter 6: Watch Assembles — Timelines

[← Chapter 5: Playback](chapter-05-playback.md) | [Chapter 7: Value Animation →](chapter-07-value-animation.md)

---

## The Brief

The hero animation — the one that sells the site. Theo pulls up Mika's timing sheet:

```
0ms      → Dial fades in + scales (600ms)
400ms    → Hour hand rotates to 10:10 position (1000ms)
800ms    → Minute hand rotates (overlaps with hour hand) (800ms)
1200ms   → Strap unfolds from center (500ms)
1500ms   → Brand text fades in (400ms)
```

Five elements. Overlapping timing. Precise offsets. You can't do this with delays alone — you'd be doing math in your head for every change. Move one element earlier and you'd have to recalculate every subsequent delay.

You need a timeline.

---

## Creating a Timeline

```javascript
import anime from 'animejs';

const tl = anime.timeline({
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',  // Default for all children
  duration: 600,                            // Default duration
});
```

A timeline is a container. You add animations to it, and they play in sequence by default. The timeline's properties become defaults for all child animations.

---

## Adding Animations

```javascript
const tl = anime.timeline({
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',
});

// Each .add() appends an animation to the timeline
tl.add({
  targets: '.watch-dial',
  opacity: [0, 1],
  scale: [0.8, 1],
  duration: 600,
})
.add({
  targets: '.hour-hand',
  rotate: [0, 210],  // 10:10 position
  duration: 1000,
})
.add({
  targets: '.minute-hand',
  rotate: [0, 60],
  duration: 800,
})
.add({
  targets: '.watch-strap',
  scaleY: [0, 1],
  duration: 500,
})
.add({
  targets: '.brand-text',
  opacity: [0, 1],
  duration: 400,
});
```

Without offsets, each animation starts after the previous one ends. Total duration: 600 + 1000 + 800 + 500 + 400 = 3300ms. Too long. The elements need to overlap.

---

## Time Offsets

The second parameter of `.add()` controls when the animation starts:

```javascript
tl.add({
  targets: '.watch-dial',
  opacity: [0, 1],
  scale: [0.8, 1],
  duration: 600,
})
.add({
  targets: '.hour-hand',
  rotate: [0, 210],
  duration: 1000,
}, '-=200')  // Start 200ms BEFORE the previous animation ends
.add({
  targets: '.minute-hand',
  rotate: [0, 60],
  duration: 800,
}, '-=600')  // Start 600ms before hour hand ends (overlap)
.add({
  targets: '.watch-strap',
  scaleY: [0, 1],
  duration: 500,
}, '-=300')
.add({
  targets: '.brand-text',
  opacity: [0, 1],
  duration: 400,
}, '-=100');
```

### Offset Types

| Offset | Meaning | Example |
|---|---|---|
| `'-=200'` | Start 200ms before previous ends | Overlap |
| `'+=200'` | Start 200ms after previous ends | Gap |
| `1000` | Start at absolute time 1000ms | Precise positioning |

```javascript
// Relative: overlap with previous
tl.add({ ... }, '-=200');

// Relative: gap after previous
tl.add({ ... }, '+=500');

// Absolute: start at exactly 1000ms regardless of previous
tl.add({ ... }, 1000);
```

---

## The Watch Assembly: Final Version

Matching Mika's timing sheet exactly:

```javascript
const EASING = {
  mechanical: 'cubicBezier(0.4, 0, 0.2, 1)',
  enter: 'cubicBezier(0.16, 1, 0.3, 1)',
};

const watchAssembly = anime.timeline({
  easing: EASING.mechanical,
  autoplay: false,  // We'll trigger this on scroll later
});

watchAssembly
  .add({
    targets: '.watch-dial',
    opacity: [0, 1],
    scale: [0.85, 1],
    duration: 600,
    easing: EASING.enter,
  })
  .add({
    targets: '.watch-hour-hand',
    rotate: [0, 210],
    opacity: [0, 1],
    duration: 1000,
  }, 400)  // Absolute: starts at 400ms
  .add({
    targets: '.watch-minute-hand',
    rotate: [0, 60],
    opacity: [0, 1],
    duration: 800,
  }, 800)  // Absolute: starts at 800ms
  .add({
    targets: '.watch-strap',
    scaleY: [0, 1],
    opacity: [0, 1],
    duration: 500,
    easing: EASING.enter,
  }, 1200)
  .add({
    targets: '.watch-brand-text',
    opacity: [0, 1],
    translateY: [10, 0],
    duration: 400,
  }, 1500);

// Total timeline duration: ~1900ms (1500 + 400)
// But elements overlap, so it feels cohesive, not sequential
```

Using absolute offsets makes the timing sheet directly translatable to code. Mika says "hour hand starts at 400ms" — you write `400`.

---

## Timeline Defaults

Properties set on the timeline apply to all children unless overridden:

```javascript
const tl = anime.timeline({
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',  // All children use this
  duration: 600,                            // All children default to 600ms
});

tl.add({
  targets: '.dial',
  opacity: [0, 1],
  // Uses timeline's easing and duration
})
.add({
  targets: '.hand',
  rotate: 210,
  duration: 1000,  // Overrides timeline's 600ms
  easing: 'easeOutQuart',  // Overrides timeline's easing
});
```

Set the most common values on the timeline. Override per-animation when needed.

---

## Timeline Controls

Timelines have the same controls as regular animations:

```javascript
const tl = anime.timeline({ autoplay: false, ... });

// Add animations...

tl.play();       // Start from current position
tl.pause();      // Freeze
tl.restart();    // Back to 0, play
tl.reverse();    // Play backward
tl.seek(800);    // Jump to 800ms
tl.seek(tl.duration * 0.5);  // Jump to 50%

// Properties
console.log(tl.duration);   // Total timeline duration
console.log(tl.progress);   // 0–100
console.log(tl.completed);  // Promise
```

This means you can scrub through the watch assembly with a slider, play it in reverse, or jump to any point. We'll build a scrubber in Chapter 10.

---

## Timeline Callbacks

```javascript
const tl = anime.timeline({
  easing: EASING.mechanical,
  begin: () => console.log('Assembly started'),
  complete: () => console.log('Assembly complete'),
  update: (anim) => {
    // Update progress bar
    progressBar.style.width = `${anim.progress}%`;
  },
});
```

Individual animations within the timeline can also have callbacks:

```javascript
tl.add({
  targets: '.watch-dial',
  opacity: [0, 1],
  duration: 600,
  complete: () => console.log('Dial is in place'),
})
.add({
  targets: '.watch-hour-hand',
  rotate: 210,
  duration: 1000,
  begin: () => console.log('Hour hand starting'),
  complete: () => console.log('Hour hand in position'),
});
```

---

## Nested Patterns

### Sequential Sections

Group related animations:

```javascript
const introTimeline = anime.timeline({ easing: EASING.enter });

// Section 1: Hero text
introTimeline
  .add({ targets: '.hero-title', opacity: [0, 1], translateY: [30, 0], duration: 800 })
  .add({ targets: '.hero-subtitle', opacity: [0, 1], translateY: [15, 0], duration: 600 }, '-=400');

// Section 2: Watch (starts after hero text)
introTimeline
  .add({ targets: '.watch-dial', opacity: [0, 1], scale: [0.85, 1], duration: 600 }, '+=200')
  .add({ targets: '.watch-hour-hand', rotate: [0, 210], duration: 1000 }, '-=200')
  .add({ targets: '.watch-minute-hand', rotate: [0, 60], duration: 800 }, '-=600');

// Section 3: Navigation (starts after watch)
introTimeline
  .add({
    targets: '.nav-item',
    opacity: [0, 1],
    translateY: [-10, 0],
    delay: anime.stagger(60),
    duration: 400,
  }, '+=100');
```

One timeline orchestrates the entire page entrance. Each section flows into the next.

---

## Common Timeline Mistakes

### 1. Forgetting autoplay: false

```javascript
// ❌ Starts immediately — might play before elements are visible
const tl = anime.timeline({ ... });

// ✅ Wait for the right moment
const tl = anime.timeline({ autoplay: false, ... });
// Later: tl.play();
```

### 2. Over-sequencing

```javascript
// ❌ Everything waits for the previous — feels slow
tl.add({ targets: '.a', ... })
  .add({ targets: '.b', ... })
  .add({ targets: '.c', ... })
  .add({ targets: '.d', ... });
// Total: 4 × duration. Boring.

// ✅ Overlap for energy
tl.add({ targets: '.a', ... })
  .add({ targets: '.b', ... }, '-=300')
  .add({ targets: '.c', ... }, '-=300')
  .add({ targets: '.d', ... }, '-=300');
// Total: much shorter. Dynamic.
```

### 3. Not using absolute offsets for complex timing

```javascript
// ❌ Relative offsets get confusing with many elements
tl.add({ ... })
  .add({ ... }, '-=200')
  .add({ ... }, '-=150')  // Wait, relative to what?
  .add({ ... }, '+=50');

// ✅ Absolute offsets match the timing sheet
tl.add({ ... }, 0)
  .add({ ... }, 400)
  .add({ ... }, 800)
  .add({ ... }, 1200);
```

---

## Theo's Reaction

You play the watch assembly for Theo. He watches it three times, then once more in slow motion (you scrub with `tl.seek()`).

> "The overlap between the hour and minute hand — that's the moment. They move together briefly, like gears meshing. That's mechanical. That's the brand."

He pauses.

> "Now. Below the watch, there are four spec numbers: water resistance, power reserve, case diameter, movement frequency. They need to count up from zero to their final value. Not just appear — count. Like an odometer."

Counting numbers. Animating values that aren't CSS properties. That's value animation.

---

## What You Learned

- **anime.timeline()** — container for sequenced animations
- **.add()** — append animations to the timeline
- **Offsets** — '-=200' (overlap), '+=200' (gap), 1000 (absolute)
- **Timeline defaults** — easing, duration inherited by children
- **Controls** — play, pause, seek, reverse (same as regular animations)
- **Callbacks** — on timeline and on individual animations
- **Absolute offsets** — match timing sheets directly
- **Overlap** — the key to dynamic, energetic sequences

The watch assembles in 1.9 seconds. Each piece arrives with precision. The overlaps create momentum. The timeline makes it manageable — change one offset and everything downstream adjusts.

Next: animating numbers, objects, and values that aren't CSS properties.

---

[← Chapter 5: Playback](chapter-05-playback.md) | [Chapter 7: Value Animation →](chapter-07-value-animation.md)
