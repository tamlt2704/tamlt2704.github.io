# Chapter 20: The Landing Page — Choreographing Everything

[← Ch 19: React Integration](chapter-19-react-integration.md)

---

## Zara's Request

Final sprint. Zara, Dani, and Paolo in the war room:

**Paolo:** "Conversion: 2.3%. Competitor with animated landing page: 4.1%."

**Zara:** "Hero animation, self-drawing illustrations, animated stats, smooth scroll. Everything we've built — choreographed into one flow."

**Dani:** "Under 2 seconds load, 60fps on a $200 Android, accessible. No pressure."

---

## The Above-the-Fold Sequence

```svg
<svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg" class="hero-svg"
     role="img" aria-label="Orbitly: Project management at light speed">
  <path class="orbit-path orbit-1" d="M 400 250 m -180 0 a 180 180 0 1 1 360 0 a 180 180 0 1 1 -360 0"
        fill="none" stroke="#e0e7ff" stroke-width="1"/>
  <circle class="logo-ring" cx="400" cy="250" r="50" fill="none" stroke="#6366f1" stroke-width="3"/>
  <circle class="logo-dot" cx="450" cy="250" r="6" fill="#6366f1"/>
  <g class="feature-node node-1" transform="translate(580, 250)">
    <circle r="20" fill="white" stroke="#e5e7eb"/><path d="M -8 0 L -2 6 L 8 -4" fill="none" stroke="#10b981" stroke-width="2"/>
  </g>
  <g class="feature-node node-2" transform="translate(400, 70)">
    <circle r="20" fill="white" stroke="#e5e7eb"/><rect x="-7" y="-7" width="14" height="14" rx="2" fill="none" stroke="#6366f1" stroke-width="2"/>
  </g>
</svg>
```

---

## The Timing Hierarchy

```javascript
function createHeroTimeline() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    gsap.set('.orbit-path, .logo-ring, .logo-dot, .feature-node', { opacity: 1 });
    return;
  }

  const tl = gsap.timeline({ delay: 0.3 });

  // Phase 1: Logo (0–0.8s) — brand identity
  tl.fromTo('.logo-ring',
    { strokeDasharray: 314, strokeDashoffset: 314 },
    { strokeDashoffset: 0, duration: 0.8, ease: 'power2.inOut' })
  .from('.logo-dot', { scale: 0, opacity: 0, duration: 0.3, ease: 'back.out(3)' }, '-=0.1')

  // Phase 2: Orbits (0.6–1.2s) — context
  .fromTo('.orbit-path',
    { strokeDasharray: 1200, strokeDashoffset: 1200 },
    { strokeDashoffset: 0, duration: 1, stagger: 0.2, ease: 'power1.inOut' }, '-=0.3')

  // Phase 3: Features (1.0–1.6s) — value
  .from('.feature-node', { scale: 0, opacity: 0, duration: 0.4, stagger: 0.15, ease: 'back.out(2)' }, '-=0.5');

  return tl;
}
```

| Phase | Timing | Purpose |
|-------|--------|---------|
| Brand | 0–0.8s | Establish identity |
| Context | 0.6–1.2s | Show ecosystem |
| Value | 1.0–1.6s | Communicate features |
| Ambient | 1.6s+ | Keep alive |

Total entrance: under 2 seconds. Headline readable while animations complete.

---

## Scroll-Driven Features

```javascript
document.querySelectorAll('.feature-block').forEach(feature => {
  const tl = gsap.timeline({
    scrollTrigger: { trigger: feature, start: 'top 75%', toggleActions: 'play none none reverse' }
  });
  tl.fromTo(feature.querySelector('path'),
    { strokeDasharray: 100, strokeDashoffset: 100 },
    { strokeDashoffset: 0, duration: 0.6 })
  .from(feature.querySelector('.text'), { opacity: 0, y: 20, duration: 0.4 }, '-=0.3');
});
```

---

## Animated Statistics

```javascript
function animateCounter(element, target) {
  const obj = { value: 0 };
  gsap.to(obj, {
    value: target, duration: 2, ease: 'power2.out',
    onUpdate: () => { element.textContent = Math.round(obj.value).toLocaleString(); },
    scrollTrigger: { trigger: element, start: 'top 80%' }
  });
}
animateCounter(document.querySelector('.stat-number'), 12847);
```

---

## Loading Strategy

```javascript
// 1. Critical: hero loads immediately
const heroTimeline = createHeroTimeline();

// 2. Deferred: scroll animations load on first scroll
let loaded = false;
window.addEventListener('scroll', () => {
  if (!loaded) {
    loaded = true;
    import('gsap/ScrollTrigger').then(() => {
      gsap.registerPlugin(ScrollTrigger);
      initScrollAnimations();
    });
  }
}, { once: true });

// 3. Pause when hidden
document.addEventListener('visibilitychange', () => {
  document.hidden ? gsap.globalTimeline.pause() : gsap.globalTimeline.resume();
});
```

---

## CSS Base State (No-JS Fallback)

```css
.feature-block { opacity: 1; transform: none; }
.js-loaded .feature-block { opacity: 0; transform: translateY(20px); }
```

Elements visible by default. JS adds hidden state for animation. No flash of invisible content.

---

## The A/B Results

After 4 weeks, 50,000 visitors:

| Metric | Old | New | Change |
|--------|-----|-----|--------|
| Conversion | 2.3% | 4.8% | +109% |
| Time on page | 28s | 52s | +86% |
| Scroll depth | 45% | 78% | +73% |
| Bounce rate | 62% | 41% | -34% |

Paolo: "It's not 'animations = better.' The choreography guides attention. Self-drawing charts make users read data. Scroll reveals create narrative. Users experience features, not just see them."

---

## Common Mistakes

**Everything animates at once** — sequence: brand → context → value → ambient.

**Animations block reading** — headline readable within 0.5s.

**No fallback for slow connections** — CSS base state must be visible without JS.

**Ignoring mobile** — test on throttled 3G + 4x CPU slowdown. Simplify for mobile:

```javascript
const isMobile = window.innerWidth < 768;
const config = { duration: isMobile ? 0.3 : 0.6, stagger: isMobile ? 0.05 : 0.15 };
```

---

## Exercise

Build Orbitly's complete landing page:
1. Hero: logo draws → orbits appear → nodes pop → ambient orbit
2. Features: 3 blocks animate on scroll (icon + text + illustration)
3. Stats: 3 counters animate when visible
4. CTA: accent line draws + button hover interaction
5. Full loading strategy (critical → deferred → lazy)
6. `prefers-reduced-motion` support
7. Maintain 55+ fps on mid-range device

---

## Quick Reference

| Section | Trigger | Animation |
|---------|---------|-----------|
| Hero | Page load | Draw + pop + orbit |
| Features | Scroll 75% | Draw + fade + stagger |
| Stats | Scroll 80% | Counter + ring |
| CTA | Scroll + hover | Accent draw + micro |

| Timing Principle | Rule |
|-----------------|------|
| Above-the-fold | < 2s total |
| Headline readable | < 0.5s |
| Stagger gaps | 100–150ms |
| Scroll trigger | Start at 75% viewport |
| Page weight | < 200KB SVG |

---

[← Ch 19: React Integration](chapter-19-react-integration.md)
