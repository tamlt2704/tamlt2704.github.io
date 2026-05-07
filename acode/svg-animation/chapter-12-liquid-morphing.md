# Chapter 12: Liquid Effects — Organic Movement

[← Ch 11: Filters & Glow](chapter-11-filters-glow.md) | [Ch 13: Particles →](chapter-13-particles.md)

---

## Zara's Request

> "I want something organic behind the signup form. Blobs that slowly morph and flow. Like a lava lamp, but subtle. Premium without distracting from the form."

She references Stripe's gradient blob backgrounds: "feTurbulence generates noise, feDisplacementMap warps shapes. Animate the turbulence and the blob breathes."

---

## feTurbulence: Generating Noise

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="noise-demo">
      <feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="3" seed="1"/>
    </filter>
  </defs>
  <rect width="200" height="200" filter="url(#noise-demo)"/>
</svg>
```

| Attribute | Effect | Range |
|-----------|--------|-------|
| `type` | `turbulence` (sharp) or `fractalNoise` (smooth) | — |
| `baseFrequency` | Scale of noise | 0.005–0.03 for blobs |
| `numOctaves` | Detail layers | 1–3 (more = slower) |
| `seed` | Random seed | Any integer |

---

## feDisplacementMap: Warping Shapes

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="liquid-warp" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves="2" result="noise"/>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="20"
                         xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
  <circle cx="100" cy="100" r="60" fill="#6366f1" filter="url(#liquid-warp)"/>
</svg>
```

The circle becomes a blob — smooth, irregular boundaries. Displacement pushes pixels based on noise color values.

---

## Animated Turbulence

```javascript
// Breathing effect — oscillate baseFrequency
gsap.to('#turb', {
  attr: { baseFrequency: '0.025' },
  duration: 3, yoyo: true, repeat: -1, ease: 'sine.inOut'
});
```

---

## Blob Morphing with Path Animation

```javascript
const blobPaths = [
  "M 200 100 C 270 90, 330 150, 320 200 C 310 260, 250 310, 200 320 C 140 330, 80 270, 80 200 C 80 130, 130 110, 200 100 Z",
  "M 200 90 C 260 100, 310 140, 320 210 C 330 270, 270 320, 200 310 C 130 300, 90 260, 80 200 C 70 140, 140 80, 200 90 Z",
];

let current = 0;
function morphBlob() {
  current = (current + 1) % blobPaths.length;
  gsap.to('.blob', { attr: { d: blobPaths[current] }, duration: 4, ease: 'sine.inOut', onComplete: morphBlob });
}
morphBlob();
```

Displacement adds fine wobble, path morph handles overall shape. Together: convincing liquid motion.

---

## The Goo Filter (Metaballs)

```svg
<defs>
  <filter id="goo" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur"/>
    <feColorMatrix in="blur" type="matrix"
      values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -10" result="goo"/>
  </filter>
</defs>
<g filter="url(#goo)">
  <circle class="goo-blob" cx="300" cy="300" r="80" fill="#6366f1"/>
  <circle class="goo-blob" cx="500" cy="300" r="60" fill="#6366f1"/>
</g>
```

```javascript
gsap.to('.goo-blob:nth-child(1)', { cx: 400, duration: 5, yoyo: true, repeat: -1, ease: 'sine.inOut' });
gsap.to('.goo-blob:nth-child(2)', { cx: 380, duration: 4, yoyo: true, repeat: -1, ease: 'sine.inOut' });
```

The magic: `0 0 0 20 -10` on alpha creates extreme contrast — blurred edges snap to sharp boundaries. Circles merge when close, stretch apart with liquid connection.

---

## Common Mistakes

**Performance** — SVG filters are CPU-rendered. Large regions + high stdDeviation + animation = jank. Reduce `numOctaves` on low-end devices.

**baseFrequency too high** — values above 0.1 create tiny noise. Stay 0.005–0.03 for organic blobs.

**Displacement scale too large** — tears the shape apart. Start at 10–20.

**Seed animation looks jerky** — discrete jumps. Animate `baseFrequency` instead for smooth motion.

---

## Exercise

Build Orbitly's onboarding background:
1. Three overlapping blob paths (indigo, cyan, purple at 40% opacity)
2. Displacement filter with animated turbulence
3. Each blob morphs between 2–3 shape variants
4. Goo filter so blobs merge when overlapping
5. Keep it subtle — background, not focus

Bonus: Gradient overlay so blobs fade toward viewport edges.

---

## Quick Reference

| Filter Primitive | Purpose | Key Attributes |
|-----------------|---------|---------------|
| `feTurbulence` | Generate noise | `baseFrequency`, `numOctaves`, `seed` |
| `feDisplacementMap` | Warp with noise | `scale`, `xChannelSelector` |
| `feGaussianBlur` | Blur for goo | `stdDeviation` |
| `feColorMatrix` | Contrast for goo | Alpha: `0 0 0 20 -10` |

| Effect | Recipe |
|--------|--------|
| Liquid blob | Circle + displacement (scale 15–30) |
| Breathing | Animate baseFrequency (0.01–0.03) |
| Goo/metaball | Blur + high-contrast alpha |
| Organic edges | fractalNoise + low displacement |

---

[← Ch 11: Filters & Glow](chapter-11-filters-glow.md) | [Ch 13: Particles →](chapter-13-particles.md)
