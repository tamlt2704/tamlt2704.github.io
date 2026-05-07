# Chapter 14: Scroll-Triggered Animations

[← Ch 13: Particles](chapter-13-particles.md) | [Ch 15: 3D Perspective →](chapter-15-3d-perspective.md)

---

## Zara's Request

> "The features section is a wall of text with static icons. Each feature should animate in as you scroll — icon draws itself, text slides up. Tied to scroll position, not just 'trigger once.' Scroll fast, it's fast. Scroll back, it reverses."

---

## GSAP ScrollTrigger Basics

```javascript
gsap.registerPlugin(ScrollTrigger);

gsap.from('.feature-icon', {
  scrollTrigger: {
    trigger: '.feature-section',
    start: 'top 80%',           // element top hits 80% of viewport
    end: 'bottom 20%',
    toggleActions: 'play none none reverse'
  },
  opacity: 0, y: 50, duration: 0.8
});
```

| toggleAction | onEnter | onLeave | onEnterBack | onLeaveBack |
|-------------|---------|---------|-------------|-------------|
| Default | `play` | `none` | `none` | `reverse` |

---

## Scrub: Progress-Based Animation

Link animation progress directly to scroll position:

```javascript
gsap.to('.illustration path', {
  scrollTrigger: {
    trigger: '.illustration-section',
    start: 'top center',
    end: 'bottom center',
    scrub: 1.5  // 1.5s smoothing lag
  },
  strokeDashoffset: 0,
  ease: 'none'
});
```

`scrub: true` = instant. `scrub: 1` = 1s lag (smoother).

---

## Self-Drawing Illustration on Scroll

```javascript
document.querySelectorAll('.draw-path').forEach(path => {
  const length = path.getTotalLength();
  path.style.strokeDasharray = length;
  path.style.strokeDashoffset = length;
});

const tl = gsap.timeline({
  scrollTrigger: { trigger: '.scroll-illustration', start: 'top 70%', end: 'bottom 30%', scrub: 1 }
});
tl.to('.draw-path', { strokeDashoffset: 0, duration: 1, ease: 'none' })
  .from('.draw-element', { opacity: 0, scale: 0.5, stagger: 0.15, duration: 0.5, ease: 'back.out(2)' });
```

Building outline draws as you scroll, then windows pop in. Scroll back — everything reverses.

---

## Parallax SVG Layers

```svg
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" class="parallax-scene">
  <path class="layer-bg" d="M 0 400 L 0 250 Q 200 150, 400 250 Q 600 350, 800 200 L 800 400 Z" fill="#c7d2fe"/>
  <path class="layer-mid" d="M 0 400 L 0 300 Q 150 250, 300 300 Q 500 350, 700 280 L 800 400 Z" fill="#818cf8"/>
  <path class="layer-fg" d="M 0 400 L 0 350 Q 200 330, 400 360 Q 600 380, 800 340 L 800 400 Z" fill="#4f46e5"/>
</svg>
```

```javascript
gsap.to('.layer-bg', { scrollTrigger: { trigger: '.parallax-scene', start: 'top bottom', end: 'bottom top', scrub: true }, y: -30 });
gsap.to('.layer-mid', { scrollTrigger: { trigger: '.parallax-scene', start: 'top bottom', end: 'bottom top', scrub: true }, y: -60 });
gsap.to('.layer-fg', { scrollTrigger: { trigger: '.parallax-scene', start: 'top bottom', end: 'bottom top', scrub: true }, y: -100 });
```

Foreground moves fastest, background slowest — convincing depth in flat SVG.

---

## Pinned Scroll Animation

```javascript
const tl = gsap.timeline({
  scrollTrigger: { trigger: '.feature-showcase', start: 'top top', end: '+=2000', pin: true, scrub: 1 }
});
tl.to('.feature-1', { opacity: 0, duration: 0.3 })
  .from('.feature-2', { opacity: 0, y: 30, duration: 0.3 })
  .to('.feature-2', { opacity: 0, duration: 0.3 }, '+=0.4')
  .from('.feature-3', { opacity: 0, y: 30, duration: 0.3 });
```

Element stays fixed while you scroll through 2000px of animation states.

---

## Common Mistakes

**Scrub feels laggy** — `scrub: true` is jittery, use `scrub: 0.5` to `2` for smoothing.

**Pin causes layout jump** — ScrollTrigger adds padding to compensate, but nested layouts can break.

**Animations fire on load** — elements already in viewport trigger immediately. Use `start: 'top 80%'`.

**Mobile performance** — scroll-linked animations can jank. Reduce complexity, increase scrub smoothing.

---

## Exercise

Build Orbitly's features page:
1. Three feature sections with SVG illustrations that draw on scroll (scrub)
2. Parallax layers in a hero illustration
3. Pin the middle section — cycle through 3 states while scrolling
4. Feature cards batch-animate with stagger on enter

Bonus: Scroll progress indicator (thin line at page top) that fills as you scroll.

---

## Quick Reference

| Option | Purpose | Example |
|--------|---------|---------|
| `trigger` | Element that triggers | `'.section'` |
| `start` | When to start | `'top 80%'` |
| `end` | When to end | `'bottom 20%'` |
| `scrub` | Link to scroll | `true`, `1`, `2` |
| `pin` | Fix during scroll | `true` |
| `toggleActions` | Enter/leave behavior | `'play none none reverse'` |

| Start/End Format | Meaning |
|-----------------|---------|
| `'top top'` | Element top hits viewport top |
| `'top 80%'` | Element top hits 80% down |
| `'center center'` | Centers align |
| `'+=2000'` | 2000px scroll distance |

---

[← Ch 13: Particles](chapter-13-particles.md) | [Ch 15: 3D Perspective →](chapter-15-3d-perspective.md)
