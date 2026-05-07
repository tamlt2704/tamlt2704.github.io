# Chapter 10: Page Transitions — Smooth Navigation

[← Ch 9: Interactive SVG](chapter-09-interactive.md) | [Ch 11: Filters & Glow →](chapter-11-filters-glow.md)

---

## Zara's Request

> "They click 'View Project' and the page hard cuts. White flash. Content pops in. It feels broken. I want smooth transitions — old content exits gracefully, new content enters with purpose."

Dani: "We're an SPA. SVG clip-paths give us shapes CSS alone can't — diagonal wipes, circle reveals, custom curves."

---

## SVG Clip-Path Reveals

Animate the clip shape to reveal content:

```svg
<svg class="transition-overlay" viewBox="0 0 100 100" preserveAspectRatio="none"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="circle-reveal" clipPathUnits="objectBoundingBox">
      <circle cx="0.5" cy="0.5" r="0" class="reveal-circle"/>
    </clipPath>
  </defs>
</svg>
```

```javascript
gsap.to('.reveal-circle', { attr: { r: 0.75 }, duration: 0.8, ease: 'power2.inOut' });
```

New page appears as an expanding circle from center.

---

## Diagonal Wipe

```svg
<svg viewBox="0 0 100 100" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="diagonal-wipe" clipPathUnits="objectBoundingBox">
      <polygon class="wipe-shape" points="0,0 0,0 0,1 0,1"/>
    </clipPath>
  </defs>
</svg>
```

```javascript
gsap.to('.wipe-shape', { attr: { points: '0,0 1.2,0 1,1 -0.2,1' }, duration: 0.7, ease: 'power3.inOut' });
```

Diagonal edge sweeps across. Overshoot values (1.2, -0.2) ensure full corner coverage.

---

## Circle from Click Point

```javascript
function circleTransition(e) {
  const x = e.clientX / window.innerWidth;
  const y = e.clientY / window.innerHeight;
  const circle = document.querySelector('.reveal-circle');
  circle.setAttribute('cx', x);
  circle.setAttribute('cy', y);

  const maxDist = Math.sqrt(Math.max(x, 1-x)**2 + Math.max(y, 1-y)**2);
  gsap.fromTo(circle, { attr: { r: 0 } }, {
    attr: { r: maxDist + 0.1 }, duration: 0.8, ease: 'power2.inOut',
    onComplete: () => { loadNewPage(); gsap.set(circle, { attr: { r: 0 } }); }
  });
}
```

Transition originates from the exact click point — spatial connection between action and result.

---

## View Transitions API

```css
::view-transition-new(root) {
  clip-path: circle(0% at 50% 50%);
  animation: circle-in 0.7s ease-in-out;
}
@keyframes circle-in { to { clip-path: circle(100% at 50% 50%); } }
```

```javascript
document.startViewTransition(async () => { await navigateToPage('/projects/123'); });
```

---

## Curtain Transition

```javascript
class PageTransition {
  async transition(loadContent) {
    const tl = gsap.timeline();
    await tl.to('.curtain', { attr: { transform: 'translateY(0)' }, duration: 0.4, ease: 'power3.in' });
    await loadContent();
    await tl.to('.curtain', { attr: { transform: 'translateY(100)' }, duration: 0.4, ease: 'power3.out' });
    gsap.set('.curtain', { attr: { transform: 'translateY(-100)' } });
  }
}
```

Solid rectangle slides down covering the page, content swaps while hidden, rectangle exits downward.

---

## Common Mistakes

**Transition blocks interaction** — set `pointer-events: none` on overlay SVG.

**preserveAspectRatio breaks full-screen** — use `preserveAspectRatio="none"` for transition SVGs.

**Content flashes** — hide new content initially, reveal after transition covers the swap.

**Circle doesn't cover corners** — from center, need `r > 0.71` in objectBoundingBox units. From edges, calculate max distance to farthest corner.

---

## Exercise

Build Orbitly's page transition system:
1. Diagonal wipe for sidebar navigation
2. Circle-from-click for card interactions
3. Branded color flash during the covered moment
4. Works with browser back/forward

Bonus: Shared element transition — card thumbnail animates from list to detail header.

---

## Quick Reference

| Transition Type | SVG Element | Animate |
|----------------|-------------|---------|
| Circle reveal | `<circle>` in clipPath | `r` attribute |
| Diagonal wipe | `<polygon>` in clipPath | `points` |
| Curtain | `<rect>` | `transform: translateY` |
| Iris | `<path>` in clipPath | `d` attribute |

| Key Concept | Value |
|-------------|-------|
| `clipPathUnits="objectBoundingBox"` | 0–1 coordinate space |
| `preserveAspectRatio="none"` | Stretch to fill |
| Max circle radius (center) | `√(0.5² + 0.5²) ≈ 0.71` |
| View Transitions API | `document.startViewTransition()` |

---

[← Ch 9: Interactive SVG](chapter-09-interactive.md) | [Ch 11: Filters & Glow →](chapter-11-filters-glow.md)
