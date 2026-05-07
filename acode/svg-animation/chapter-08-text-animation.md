# Chapter 8: Text Animation — Revealing Words

[← Ch 7: GSAP Timelines](chapter-07-gsap-timelines.md) | [Ch 9: Interactive SVG →](chapter-09-interactive.md)

---

## Zara's Request

> "The headline needs to reveal itself. Each letter slides up from below a mask, like rising out of the ground. Then subtext fades in word by word. Apple does this — letters appear one by one with a slight stagger. Elegant."

---

## SVG Text Basics

```svg
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <text x="200" y="60" text-anchor="middle"
        font-family="Inter, sans-serif" font-size="32" font-weight="bold" fill="#1f2937">
    Orbitly
  </text>
</svg>
```

Key: `y` is the baseline (not top), `fill` is the color (not `color`), `text-anchor` for alignment.

---

## ClipPath Text Reveal

The "rising from below" effect — clipPath masks the text:

```svg
<svg viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="text-mask">
      <rect x="0" y="30" width="400" height="50"/>
    </clipPath>
  </defs>
  <g clip-path="url(#text-mask)">
    <text class="hero-text" x="200" y="70" text-anchor="middle"
          font-size="40" font-weight="bold" fill="#1f2937">Ship faster</text>
  </g>
</svg>
```

```css
.hero-text {
  transform: translateY(50px); opacity: 0;
  animation: reveal-up 0.8s ease-out 0.3s forwards;
}
@keyframes reveal-up { to { transform: translateY(0); opacity: 1; } }
```

Text slides up into view, cropped by the clipPath — emerges from behind an invisible edge.

---

## Per-Character Stagger

Split into `<tspan>` elements, then animate:

```svg
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <text x="50" y="60" font-size="36" font-weight="bold">
    <tspan class="char">O</tspan><tspan class="char">r</tspan>
    <tspan class="char">b</tspan><tspan class="char">i</tspan>
    <tspan class="char">t</tspan><tspan class="char">l</tspan>
    <tspan class="char">y</tspan>
  </text>
</svg>
```

```javascript
gsap.from('.char', { y: 40, opacity: 0, duration: 0.5, stagger: 0.04, ease: 'back.out(1.7)' });
```

Each letter pops up with overshoot — a wave across the word.

---

## Mask-Based Wipe Reveal

```svg
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="wipe-gradient" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="white"/><stop offset="10%" stop-color="white"/>
      <stop offset="20%" stop-color="black"/><stop offset="100%" stop-color="black"/>
    </linearGradient>
    <mask id="wipe-mask">
      <rect x="-400" y="0" width="400" height="100" fill="url(#wipe-gradient)" class="wipe-rect"/>
    </mask>
  </defs>
  <text mask="url(#wipe-mask)" x="200" y="60" text-anchor="middle"
        font-size="32" font-weight="bold" fill="#6366f1">Project management, reimagined</text>
</svg>
```

```css
.wipe-rect { animation: wipe 1.5s ease-in-out forwards; }
@keyframes wipe { to { transform: translateX(800px); } }
```

Soft gradient edge sweeps left-to-right — like a spotlight revealing text.

---

## Typewriter Effect

```javascript
const chars = document.querySelectorAll('.tw-char');
const cursor = document.querySelector('.cursor');

chars.forEach((char, i) => {
  setTimeout(() => {
    char.setAttribute('opacity', '1');
    gsap.to(cursor, { x: (i + 1) * 12, duration: 0.05 });
  }, i * 80 + 500);
});

// Blink cursor
gsap.to(cursor, { opacity: 0, duration: 0.5, repeat: -1, yoyo: true });
```

Characters appear at typing speed while cursor advances and blinks.

---

## Combining Text with Graphics

```javascript
const tl = gsap.timeline({ delay: 0.5 });
tl.fromTo('.orbit-line',
    { strokeDasharray: 350, strokeDashoffset: 350 },
    { strokeDashoffset: 0, duration: 1, ease: 'power1.inOut' })
  .from('.headline', { opacity: 0, y: 20, duration: 0.6, ease: 'power2.out' }, '-=0.4')
  .fromTo('.underline',
    { strokeDasharray: 180, strokeDashoffset: 180 },
    { strokeDashoffset: 0, duration: 0.5, ease: 'power2.out' }, '-=0.2');
```

Decorative line draws → headline fades up → underline accent traces in.

---

## Common Mistakes

**SVG text `y` is the baseline** — text extends above `y`. Account for this in clipPath positioning.

**Font not loaded when measuring** — wait for `document.fonts.ready` before splitting text.

**ClipPath coordinates** — uses the same coordinate system as the SVG viewBox.

**tspan positioning** — without explicit `x`/`dx`, each continues from previous character.

---

## Exercise

Build Orbitly's landing page hero text:
1. Headline "Manage projects at light speed" split into `<tspan>` characters
2. ClipPath crops the text area
3. Characters rise from below with 30ms stagger
4. After headline, fade in subtitle "Trusted by 10,000+ teams"
5. Draw an underline accent beneath "light speed"

---

## Quick Reference

| Technique | Best For | Complexity |
|-----------|----------|-----------|
| ClipPath reveal | Clean edge reveals | Low |
| Mask wipe | Soft gradient reveals | Medium |
| Per-character stagger | Dramatic headlines | Medium |
| Typewriter | Code/terminal aesthetic | Medium |

| SVG Text Property | HTML Equivalent | Notes |
|-------------------|----------------|-------|
| `fill` | `color` | Text color |
| `text-anchor` | `text-align` | start/middle/end |
| `y` | — | Baseline position |
| `<tspan>` | `<span>` | Inline segment |

---

[← Ch 7: GSAP Timelines](chapter-07-gsap-timelines.md) | [Ch 9: Interactive SVG →](chapter-09-interactive.md)
