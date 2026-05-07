# Chapter 6: Animated Data Visualization

[← Ch 5: Path Morphing](chapter-05-path-morphing.md) | [Ch 7: GSAP Timelines →](chapter-07-gsap-timelines.md)

---

## Zara's Request

> "The analytics dashboard looks like a spreadsheet. Competitors have charts that draw themselves — lines trace across, bars grow up, progress rings fill. Animation isn't decoration here — it guides the eye."

Paolo: "Users spend 40% less time on our analytics page. They're not engaging with the data."

---

## Self-Drawing Line Chart

```svg
<svg viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg" class="line-chart">
  <line x1="40" y1="180" x2="380" y2="180" stroke="#e5e7eb"/>
  <polyline class="chart-line"
    points="40,160 100,140 160,90 220,120 280,60 340,80 380,30"
    fill="none" stroke="#6366f1" stroke-width="3"
    stroke-linecap="round" stroke-linejoin="round"/>
  <polygon class="chart-area"
    points="40,160 100,140 160,90 220,120 280,60 340,80 380,30 380,180 40,180"
    fill="url(#gradient)" opacity="0"/>
  <defs>
    <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#6366f1" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
    </linearGradient>
  </defs>
</svg>
```

```css
.chart-line {
  stroke-dasharray: 600; stroke-dashoffset: 600;
  animation: draw-line 2s ease-out forwards;
}
.chart-area { animation: fade-in 0.8s ease-out 1.8s forwards; }
@keyframes draw-line { to { stroke-dashoffset: 0; } }
@keyframes fade-in { to { opacity: 1; } }
```

Line traces left-to-right, then gradient area fades in beneath.

---

## Growing Bar Chart

```svg
<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg">
  <line x1="40" y1="180" x2="280" y2="180" stroke="#e5e7eb"/>
  <rect class="bar" x="55" y="100" width="30" height="80" rx="4" fill="#6366f1"/>
  <rect class="bar" x="100" y="60" width="30" height="120" rx="4" fill="#818cf8"/>
  <rect class="bar" x="145" y="130" width="30" height="50" rx="4" fill="#a5b4fc"/>
  <rect class="bar" x="190" y="40" width="30" height="140" rx="4" fill="#6366f1"/>
  <rect class="bar" x="235" y="80" width="30" height="100" rx="4" fill="#818cf8"/>
</svg>
```

```css
.bar {
  transform-origin: center bottom; transform: scaleY(0);
  animation: grow-bar 0.6s ease-out forwards;
}
.bar:nth-child(2) { animation-delay: 0.1s; }
.bar:nth-child(3) { animation-delay: 0.2s; }
.bar:nth-child(4) { animation-delay: 0.3s; }
.bar:nth-child(5) { animation-delay: 0.4s; }
.bar:nth-child(6) { animation-delay: 0.5s; }
@keyframes grow-bar { to { transform: scaleY(1); } }
```

Bars spring up from the x-axis with a staggered wave.

---

## Circular Progress Ring

```svg
<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" stroke-width="10"/>
  <circle cx="60" cy="60" r="50" fill="none" stroke="#6366f1" stroke-width="10"
          stroke-linecap="round" class="progress-value" transform="rotate(-90 60 60)"/>
  <text x="60" y="65" text-anchor="middle" font-size="20" font-weight="bold" fill="#1f2937">73%</text>
</svg>
```

```javascript
function setProgress(element, percent) {
  const circumference = 2 * Math.PI * 50; // ≈ 314
  const offset = circumference * (1 - percent / 100);
  element.style.strokeDasharray = circumference;
  element.style.strokeDashoffset = circumference;
  requestAnimationFrame(() => {
    element.style.transition = 'stroke-dashoffset 1.5s ease-out';
    element.style.strokeDashoffset = offset;
  });
}
setProgress(document.querySelector('.progress-value'), 73);
```

---

## Animated Donut Chart

```javascript
const circumference = 283; // 2π × 45
const data = [45, 30, 25]; // percentages
let offset = 0;

document.querySelectorAll('.segment').forEach((seg, i) => {
  const segLength = (data[i] / 100) * circumference;
  seg.style.strokeDasharray = `${segLength} ${circumference - segLength}`;
  seg.style.strokeDashoffset = -offset;
  seg.style.animation = `fade-segment 0.5s ease-out ${i * 0.3}s forwards`;
  offset += segLength;
});
```

---

## Common Mistakes

**Bar scaleY distorts rounded corners** — animate `height` and `y` instead, or use `clip-path`.

**Line dasharray too short** — repeating pattern instead of single stroke. Always `getTotalLength()`.

**Progress ring starts at 3 o'clock** — add `transform="rotate(-90 cx cy)"` to start from top.

**Donut segments overlap** — each segment's `stroke-dashoffset` must account for previous lengths.

---

## Exercise

Build Orbitly's weekly activity chart:
1. Line chart with 7 data points (Mon–Sun), self-drawing over 1.5s
2. Animated dots at each point (scale 0→1, staggered after line completes)
3. Gradient fill beneath the line, fading in
4. Axis labels using `<text>` elements

---

## Quick Reference

| Chart Type | Technique | Key Properties |
|-----------|-----------|---------------|
| Line chart | stroke-dasharray draw | `dasharray`, `dashoffset` |
| Bar chart | scaleY from 0 | `transform-origin: bottom` |
| Progress ring | Partial dashoffset | `circumference × (1 - pct)` |
| Donut/Pie | Multiple circles | Offset each segment |
| Area chart | Polygon + fade | `opacity` transition |

| Formula | Use |
|---------|-----|
| `2πr` | Circle circumference |
| `circumference × (1 - percent/100)` | Dashoffset for progress |
| `getTotalLength()` | Any path's total length |

---

[← Ch 5: Path Morphing](chapter-05-path-morphing.md) | [Ch 7: GSAP Timelines →](chapter-07-gsap-timelines.md)
