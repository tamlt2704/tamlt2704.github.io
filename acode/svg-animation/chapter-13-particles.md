# Chapter 13: Generative SVG — Particles and Physics

[← Ch 12: Liquid Morphing](chapter-12-liquid-morphing.md) | [Ch 14: Scroll Animations →](chapter-14-scroll-animations.md)

---

## Zara's Request

> "When a project hits 100%, I want confetti. Not a GIF — real particles that burst from the checkmark, scatter with physics, and fade out. Different colors, sizes, some spin."

Paolo: "We A/B tested celebrations at my last company. Teams with visual rewards completed 23% more projects."

---

## Creating SVG Elements with JavaScript

```javascript
const SVG_NS = 'http://www.w3.org/2000/svg';

function createParticle(svg, x, y, color) {
  const el = document.createElementNS(SVG_NS, 'circle');
  el.setAttribute('cx', x);
  el.setAttribute('cy', y);
  el.setAttribute('r', 2 + Math.random() * 3);
  el.setAttribute('fill', color);
  svg.appendChild(el);
  return el;
}
```

---

## Basic Particle System

```javascript
class ParticleSystem {
  constructor(svg) {
    this.svg = svg;
    this.particles = [];
    this.colors = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];
  }

  emit(x, y, count = 30) {
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.5;
      const speed = 2 + Math.random() * 4;
      const color = this.colors[Math.floor(Math.random() * this.colors.length)];
      const el = createParticle(this.svg, x, y, color);

      this.particles.push({
        el, x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 3,
        gravity: 0.15, friction: 0.98,
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 15,
        life: 1
      });
    }
  }

  update() {
    this.particles = this.particles.filter(p => {
      p.vx *= p.friction;
      p.vy = p.vy * p.friction + p.gravity;
      p.x += p.vx;
      p.y += p.vy;
      p.rotation += p.rotationSpeed;
      p.life -= 0.015;

      if (p.life <= 0) { p.el.remove(); return false; }
      p.el.setAttribute('opacity', p.life);
      p.el.setAttribute('transform', `translate(${p.x - parseFloat(p.el.getAttribute('cx'))}, ${p.y - parseFloat(p.el.getAttribute('cy'))}) rotate(${p.rotation})`);
      return true;
    });
  }

  animate() {
    this.update();
    if (this.particles.length > 0) requestAnimationFrame(() => this.animate());
  }
}
```

---

## Burst on Click

```javascript
const svg = document.querySelector('.burst-canvas');
const system = new ParticleSystem(svg);

document.querySelector('.burst-trigger').addEventListener('click', (e) => {
  const rect = svg.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width * 400;
  const y = (e.clientY - rect.top) / rect.height * 300;
  system.emit(x, y, 40);
  system.animate();
});
```

40 particles explode outward, arc with gravity, spin, fade, disappear.

---

## GSAP-Based Particles (Simpler)

```javascript
function gsapBurst(svg, x, y, count = 20) {
  const colors = ['#6366f1', '#ec4899', '#f59e0b', '#10b981'];
  for (let i = 0; i < count; i++) {
    const dot = document.createElementNS(SVG_NS, 'circle');
    dot.setAttribute('cx', x); dot.setAttribute('cy', y);
    dot.setAttribute('r', 2 + Math.random() * 3);
    dot.setAttribute('fill', colors[i % colors.length]);
    svg.appendChild(dot);

    const angle = (Math.PI * 2 * i) / count;
    const distance = 40 + Math.random() * 60;
    gsap.to(dot, {
      attr: { cx: x + Math.cos(angle) * distance, cy: y + Math.sin(angle) * distance - 20 },
      opacity: 0, duration: 0.8 + Math.random() * 0.4, ease: 'power2.out',
      onComplete: () => dot.remove()
    });
  }
}
```

Dots radiate outward, fading as they travel. Simpler than full physics but effective.

---

## Common Mistakes

**Too many DOM elements** — each particle is a DOM node. Cap at 50–80. Use `<canvas>` for 100+.

**Not removing dead particles** — opacity 0 elements still exist. Always `.remove()`.

**Particles escape viewBox** — still rendered off-screen. Remove out-of-bounds particles or use `overflow="hidden"`.

**setAttribute in tight loops** — triggers style recalc. GSAP batches internally; for manual loops, minimize DOM writes.

---

## Exercise

Build Orbitly's milestone celebration:
1. Progress ring hits 100% → confetti burst from ring's top
2. 40 particles: circles, rectangles, triangles
3. Physics: upward velocity, gravity, horizontal spread
4. Each spins and fades over 1.5s
5. Colors: indigo, cyan, amber, emerald, pink

Bonus: "Firework" — particles travel up, explode at peak into secondary particles.

---

## Quick Reference

| Concept | Implementation | Notes |
|---------|---------------|-------|
| Create element | `createElementNS(SVG_NS, tag)` | Must use namespace |
| Velocity | `vx`, `vy` per frame | Add gravity to vy |
| Gravity | `vy += 0.15` | Adjust for feel |
| Friction | `vx *= 0.98` | Slows particles |
| Life/fade | `life -= 0.015` | Remove at 0 |
| Burst pattern | `angle = (2π × i) / count` | Even distribution |
| Cleanup | `element.remove()` | Prevent DOM bloat |

| Performance | Guideline |
|-------------|-----------|
| Max particles | 50–80 (DOM), 1000+ (canvas) |
| Animation loop | `requestAnimationFrame` |
| Off-screen | Remove immediately |
| < 30 particles | GSAP handles well |

---

[← Ch 12: Liquid Morphing](chapter-12-liquid-morphing.md) | [Ch 14: Scroll Animations →](chapter-14-scroll-animations.md)
