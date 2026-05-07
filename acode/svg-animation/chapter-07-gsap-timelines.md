# Chapter 7: GSAP Timelines — Professional Sequencing

[← Ch 6: Data Viz](chapter-06-data-viz.md) | [Ch 8: Text Animation →](chapter-08-text-animation.md)

---

## Zara's Request

> "When a user completes setup, I want a celebration. Icons fly in, text fades up, checkmark draws, confetti bursts — all choreographed. CSS animation-delay is killing me. I have 8 elements and can't visualize the sequence."

Dani: "You need GSAP timelines. CSS keyframes are fine for isolated animations. For sequencing 5+ elements with overlaps — you need a timeline."

---

## GSAP Basics

```javascript
gsap.to('.icon', { opacity: 1, y: 0, duration: 0.6 });           // animate TO
gsap.from('.icon', { opacity: 0, y: 20, duration: 0.6 });        // animate FROM
gsap.fromTo('.icon', { opacity: 0 }, { opacity: 1, duration: 0.6 }); // both

// SVG-specific
gsap.to('.circle', { attr: { r: 40, cx: 100 }, fill: '#6366f1', strokeDashoffset: 0, duration: 1 });
```

---

## Timelines

Animations play in sequence by default:

```javascript
const tl = gsap.timeline();
tl.from('.heading', { opacity: 0, y: 30, duration: 0.5 })
  .from('.subtext', { opacity: 0, y: 20, duration: 0.4 })
  .from('.cta-button', { opacity: 0, scale: 0.8, duration: 0.3 })
  .from('.icon-group', { opacity: 0, duration: 0.4 });
```

### Position Parameter — Controlling Overlap

```javascript
tl.to('.a', { x: 100, duration: 1 })
  .to('.b', { x: 100, duration: 1 })           // after .a
  .to('.c', { x: 100, duration: 1 }, '-=0.3')  // 0.3s before .b ends
  .to('.d', { x: 100, duration: 1 }, '+=0.5')  // 0.5s gap after .c
  .to('.e', { x: 100, duration: 1 }, '<');      // same start as .d
```

---

## Stagger

```javascript
gsap.from('.card', {
  opacity: 0, y: 30, scale: 0.8,
  duration: 0.5, stagger: 0.15, ease: 'back.out(1.7)'
});

// Advanced stagger
gsap.from('.card', {
  opacity: 0, y: 30, duration: 0.5,
  stagger: { each: 0.1, from: 'center', ease: 'power2.in' }
});
```

---

## Easing

| Ease | Feel | Use Case |
|------|------|----------|
| `power2.out` | Natural deceleration | Most UI animations |
| `power3.inOut` | Smooth start and end | Page transitions |
| `elastic.out(1, 0.3)` | Springy overshoot | Celebrations |
| `bounce.out` | Physical bounce | Dropped elements |
| `back.out(1.7)` | Slight overshoot | Cards entering |
| `none` (linear) | Mechanical | Progress bars |

---

## Orbitly's Celebration

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" class="celebration">
  <circle class="success-ring" cx="100" cy="100" r="60" fill="none" stroke="#10b981" stroke-width="4"/>
  <path class="checkmark" d="M 70 100 L 90 120 L 130 80" fill="none" stroke="#10b981" stroke-width="5" stroke-linecap="round"/>
  <circle class="dot" cx="100" cy="20" r="4" fill="#f59e0b"/>
  <circle class="dot" cx="160" cy="50" r="3" fill="#ec4899"/>
  <circle class="dot" cx="170" cy="120" r="4" fill="#6366f1"/>
  <circle class="dot" cx="60" cy="170" r="3" fill="#06b6d4"/>
  <circle class="dot" cx="30" cy="120" r="4" fill="#f59e0b"/>
</svg>
```

```javascript
const tl = gsap.timeline({ delay: 0.2 });
tl.fromTo('.success-ring',
    { strokeDasharray: 377, strokeDashoffset: 377 },
    { strokeDashoffset: 0, duration: 0.8, ease: 'power2.inOut' })
  .fromTo('.checkmark',
    { strokeDasharray: 80, strokeDashoffset: 80 },
    { strokeDashoffset: 0, duration: 0.4, ease: 'power2.out' }, '-=0.2')
  .from('.dot', { scale: 0, opacity: 0, duration: 0.6, stagger: 0.05, ease: 'back.out(3)' }, '-=0.1')
  .to('.dot', { y: '-=8', duration: 1.5, stagger: 0.1, ease: 'power1.inOut', yoyo: true, repeat: -1 });
```

Circle draws, checkmark traces in, dots burst outward then gently float.

---

## Timeline Controls

```javascript
const tl = gsap.timeline({ paused: true });
tl.to('.el', { x: 100, duration: 1 });

tl.play();        tl.pause();
tl.reverse();     tl.restart();
tl.progress(0.5); tl.timeScale(2);
```

---

## Common Mistakes

**Forgetting transformOrigin for SVG** — `gsap.to('.icon', { rotation: 360, transformOrigin: 'center center' })`.

**Using CSS properties for SVG attributes** — use `attr: { r: 50 }` for SVG-specific attributes.

**Timeline plays immediately** — use `{ paused: true }` to trigger manually.

---

## Exercise

Build Orbitly's feature tour entrance:
1. SVG with phone outline, 3 UI rectangles inside, cursor icon
2. Phone fades/scales in (0.5s) → UI elements stagger from below (0.3s each, back.out) → cursor slides in (0.4s) → cursor "clicks" an element (scale pulse)
3. Add 0.3s pause between UI appearing and cursor entering

---

## Quick Reference

| Method | Purpose | Example |
|--------|---------|---------|
| `gsap.to()` | Animate to state | `gsap.to('.el', { x: 100 })` |
| `gsap.from()` | Animate from state | `gsap.from('.el', { opacity: 0 })` |
| `gsap.timeline()` | Sequence container | `const tl = gsap.timeline()` |
| `stagger` | Delay between group | `stagger: 0.1` |
| `ease` | Timing curve | `ease: 'power2.out'` |
| `-=0.3` | Overlap previous | Starts 0.3s early |
| `+=0.5` | Gap after previous | Waits 0.5s |
| `<` | Same start as prev | Parallel animations |
| `attr: {}` | SVG attributes | `attr: { r: 50 }` |

---

[← Ch 6: Data Viz](chapter-06-data-viz.md) | [Ch 8: Text Animation →](chapter-08-text-animation.md)
