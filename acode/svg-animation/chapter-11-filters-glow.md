# Chapter 11: SVG Filters — Glow, Blur, and Color

[← Ch 10: Page Transitions](chapter-10-transitions.md) | [Ch 12: Liquid Morphing →](chapter-12-liquid-morphing.md)

---

## Zara's Request

> "I need a neon glow on the active nav icon in dark mode. Not CSS box-shadow — that's boxy on paths. A proper glow that follows the shape. Like it's emitting light."

---

## SVG Filter Basics

Filters are defined in `<defs>` and applied via the `filter` attribute:

```svg
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="simple-blur">
      <feGaussianBlur in="SourceGraphic" stdDeviation="3"/>
    </filter>
  </defs>
  <circle cx="100" cy="50" r="30" fill="#6366f1" filter="url(#simple-blur)"/>
</svg>
```

Expand filter region for effects that extend beyond the element:
```svg
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
```

---

## The Neon Glow Effect

Layer a blurred, brightened copy behind the original:

```svg
<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur1"/>
      <feColorMatrix in="blur1" type="saturate" values="3" result="bright-blur"/>
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur2"/>
      <feMerge>
        <feMergeNode in="blur2"/>
        <feMergeNode in="bright-blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="200" height="100" fill="#0f172a"/>
  <path d="M 80 50 L 100 30 L 120 50 L 100 70 Z"
        fill="none" stroke="#06b6d4" stroke-width="2" filter="url(#neon-glow)"/>
</svg>
```

Diamond shape with cyan glow — tight inner glow + diffuse outer glow. Against dark background, it emits light.

---

## feColorMatrix

```svg
<feColorMatrix type="saturate" values="2"/>      <!-- boost color -->
<feColorMatrix type="hueRotate" values="90"/>    <!-- shift hue -->
<feColorMatrix type="matrix" values="            <!-- full control -->
  0.5 0   0.5 0 0
  0   0.2 0.3 0 0
  0.3 0   0.8 0 0
  0   0   0   1 0"/>
```

---

## Animated Drop Shadow

```svg
<defs>
  <filter id="hover-shadow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="shadow"/>
    <feOffset in="shadow" dx="0" dy="4" result="offset"/>
    <feColorMatrix in="offset" type="matrix"
      values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.2 0" result="colored"/>
    <feMerge>
      <feMergeNode in="colored"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>
```

---

## Animating Filter Values

```javascript
// Pulsing glow
gsap.to('#neon-glow feGaussianBlur', {
  attr: { stdDeviation: 8 }, duration: 1.5,
  yoyo: true, repeat: -1, ease: 'sine.inOut'
});
```

The glow breathes — expanding and contracting. Element pulses with energy.

---

## Common Mistakes

**Glow gets clipped** — default filter region is the bounding box. Always expand: `x="-50%" y="-50%" width="200%" height="200%"`.

**Performance on mobile** — SVG filters are CPU-rendered. Keep `stdDeviation` under 5 for animated filters.

**Dark mode only** — glow effects look like smudges on light backgrounds. Apply conditionally.

**Filter on transparent elements** — `SourceAlpha` uses the alpha channel, so semi-transparent elements produce semi-transparent blur.

---

## Exercise

Build neon navigation for Orbitly's dark mode:
1. Four SVG icons (home, projects, analytics, settings)
2. Active icon gets neon glow matching its stroke color
3. Hover animates glow from 0 to full over 0.3s
4. Inactive icons slightly desaturated
5. Cross-fade glow when switching active icon

Bonus: "Power surge" — glow spikes to stdDeviation 12 then settles when icon becomes active.

---

## Quick Reference

| Filter Primitive | Purpose | Key Attributes |
|-----------------|---------|---------------|
| `feGaussianBlur` | Blur | `stdDeviation`, `in` |
| `feColorMatrix` | Color manipulation | `type`, `values` |
| `feComposite` | Combine layers | `operator`, `in`, `in2` |
| `feOffset` | Move result | `dx`, `dy` |
| `feMerge` | Stack layers | `feMergeNode` children |
| `feFlood` | Solid color | `flood-color` |

| Glow Recipe | Steps |
|-------------|-------|
| Outer glow | Blur source → merge behind original |
| Neon | Two blurs (tight + wide) → saturate → merge |
| Drop shadow | Blur SourceAlpha → offset → color → merge behind |
| Inner glow | Blur SourceAlpha → composite `in` with source |

---

[← Ch 10: Page Transitions](chapter-10-transitions.md) | [Ch 12: Liquid Morphing →](chapter-12-liquid-morphing.md)
