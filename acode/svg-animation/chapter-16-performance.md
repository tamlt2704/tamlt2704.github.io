# Chapter 16: Performance — Smooth on Every Device

[← Ch 15: 3D Perspective](chapter-15-3d-perspective.md) | [Ch 17: Accessibility →](chapter-17-accessibility.md)

---

## Zara's Request

> "Animations look great on your MacBook. On the test Android? Spinner stutters. Page transition drops frames. Parallax is a slideshow."

Dani opens DevTools: "See these red bars? Jank. Frames taking longer than 16.6ms. Your animations trigger layout recalculations every frame."

---

## The 60fps Budget

60fps = 16.6ms per frame. Browser must: run JS → calculate styles → layout → paint → composite.

### GPU-Composited Properties

| Property | Composited? | Cost |
|----------|------------|------|
| `transform` | ✅ | Cheapest |
| `opacity` | ✅ | Cheapest |
| `filter` | ⚠️ Partial | Depends |
| `fill`, `stroke` | ❌ | Triggers paint |
| `cx`, `cy`, `r` | ❌ | Layout + paint |
| `d` (path) | ❌ | Layout + paint |

```css
/* GOOD: GPU-composited */
@keyframes smooth { 50% { transform: scale(1.05); opacity: 0.9; } }
/* BAD: CPU paint every frame */
@keyframes janky { 50% { r: 42; fill: #818cf8; } }
```

---

## will-change

```css
.spinner { will-change: transform; }  /* Promote to GPU layer */
/* DON'T: * { will-change: transform; } — too many layers, wastes memory */
```

Dynamic approach:
```javascript
element.style.willChange = 'transform';
gsap.to(element, { rotation: 360, onComplete: () => { element.style.willChange = 'auto'; } });
```

---

## Transform vs Attribute Animation

```javascript
// BAD: triggers layout
gsap.to('circle', { attr: { cx: 200, cy: 150, r: 50 } });

// GOOD: GPU composited
gsap.to('circle', { x: 100, y: 50, scale: 1.25 });
```

---

## requestAnimationFrame

```javascript
// BAD: setInterval doesn't sync with display
setInterval(updateParticles, 16);

// GOOD: syncs with browser paint cycle
function animate(currentTime) {
  const dt = (currentTime - lastTime) / 1000;
  lastTime = currentTime;
  particles.forEach(p => { p.x += p.vx * dt * 60; });
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
```

---

## Reducing Repaints

```javascript
// BAD: read-write-read-write (layout thrashing)
elements.forEach(el => {
  const box = el.getBBox();
  el.setAttribute('x', box.x + 10);
});

// GOOD: batch reads, then batch writes
const positions = elements.map(el => el.getBBox());
elements.forEach((el, i) => el.setAttribute('x', positions[i].x + 10));
```

---

## Pause Off-Screen Animations

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    const anim = entry.target._gsapAnimation;
    entry.isIntersecting ? anim.play() : anim.pause();
  });
});
document.querySelectorAll('.animated-section').forEach(el => observer.observe(el));

// Pause when tab is hidden
document.addEventListener('visibilitychange', () => {
  document.hidden ? gsap.globalTimeline.pause() : gsap.globalTimeline.resume();
});
```

---

## SVG-Specific Optimizations

- **Simplify paths** — 200 points = expensive morph. Reduce to 20–30.
- **Limit filter animations** — large `stdDeviation` is CPU-heavy. Animate opacity of pre-blurred elements instead.
- **Remove dead particles** — opacity-0 elements still render.
- **Reduce numOctaves** on mobile for turbulence filters.

---

## Common Mistakes

**Animating `d` on complex paths** — full layout recalc. Keep morph paths under 30 points.

**Too many will-change layers** — 50+ layers = memory issues on mobile.

**Not testing on real devices** — your machine has 10x the GPU of a budget phone.

**Infinite animations in background tabs** — use Page Visibility API to pause.

---

## Exercise

Optimize Orbitly's dashboard:
1. Profile with Chrome DevTools Performance tab
2. Convert `cx`/`cy`/`r` animations to `transform`
3. Add `will-change` to the 3 most-animated elements
4. IntersectionObserver to pause off-screen animations
5. Page Visibility listener to pause when tab hidden

---

## Quick Reference

| Optimization | Impact | Effort |
|-------------|--------|--------|
| transform/opacity only | High | Low |
| will-change (sparingly) | Medium | Low |
| Pause off-screen | High | Medium |
| Simplify paths | Medium | Low |
| requestAnimationFrame | High | Low |
| Batch DOM operations | Medium | Medium |
| Reduce filter complexity | High | Low |

| DevTools Check | What to Look For |
|---------------|-----------------|
| Red frame bars | Dropped frames |
| Long paint times | Expensive repaints |
| Layout thrashing | Forced sync layouts |
| Layer count | Too many GPU layers |

---

[← Ch 15: 3D Perspective](chapter-15-3d-perspective.md) | [Ch 17: Accessibility →](chapter-17-accessibility.md)
