# Chapter 5: Color Palettes

[← Ch 4](chapter-04-heightmaps.md) | [Ch 6 →](chapter-06-caves.md)

---

## Juno's Request

> "Every planet needs its own color identity. Toxic worlds feel green-purple. Ice worlds are blue-white. But it can't be random colors — they need to feel harmonious. I want 4-6 colors per palette, generated from a seed, following color theory rules."

---

## HSL Color Space

RGB is terrible for procedural color. HSL is intuitive:

```
H (Hue):        0°──60°──120°──180°──240°──300°──360°
                Red  Yellow Green  Cyan  Blue  Magenta

S (Saturation): 0% (gray) ──────────────────── 100% (vivid)
L (Lightness):  0% (black) ─── 50% (color) ─── 100% (white)
```

```typescript
function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  h = h % 360; s = s / 100; l = l / 100;
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs((h / 60) % 2 - 1));
  const m = l - c / 2;
  let r = 0, g = 0, b = 0;
  if (h < 60) { r = c; g = x; } else if (h < 120) { r = x; g = c; }
  else if (h < 180) { g = c; b = x; } else if (h < 240) { g = x; b = c; }
  else if (h < 300) { r = x; b = c; } else { r = c; b = x; }
  return [Math.round((r+m)*255), Math.round((g+m)*255), Math.round((b+m)*255)];
}
```

---

## Harmony Rules

```
Complementary (180° apart):     Analogous (30° apart):      Triadic (120° apart):
     ●                               ● ● ●                      ●
    ╱ ╲                                                         ╱ ╲
   ●───●                                                       ●───●
```

```typescript
type HarmonyRule = 'complementary' | 'analogous' | 'triadic' | 'split';

function getHarmonyHues(baseHue: number, rule: HarmonyRule): number[] {
  switch (rule) {
    case 'complementary': return [baseHue, (baseHue + 180) % 360];
    case 'analogous': return [baseHue, (baseHue + 30) % 360, (baseHue + 60) % 360];
    case 'triadic': return [baseHue, (baseHue + 120) % 360, (baseHue + 240) % 360];
    case 'split': return [baseHue, (baseHue + 150) % 360, (baseHue + 210) % 360];
  }
}
```

---

## Seeded Palette Generation

```typescript
import Alea from 'alea';

interface Palette {
  background: [number, number, number];
  midtone: [number, number, number];
  highlight: [number, number, number];
  accent: [number, number, number];
  colors: [number, number, number][];
}

function generatePalette(seed: string | number): Palette {
  const rng = Alea(seed);
  const baseHue = rng() * 360;
  const rules: HarmonyRule[] = ['complementary', 'analogous', 'triadic', 'split'];
  const rule = rules[Math.floor(rng() * rules.length)];
  const hues = getHarmonyHues(baseHue, rule);

  const background = hslToRgb(hues[0], 15 + rng() * 20, 8 + rng() * 10);
  const midtone = hslToRgb(hues[0], 30 + rng() * 30, 35 + rng() * 15);
  const highlight = hslToRgb(hues[0], 40 + rng() * 30, 65 + rng() * 20);
  const accent = hslToRgb(hues[1] || (baseHue + 180) % 360, 60 + rng() * 30, 50 + rng() * 20);

  const colors: [number, number, number][] = [background, midtone, highlight, accent];
  for (let i = 1; i < hues.length && colors.length < 7; i++) {
    colors.push(hslToRgb(hues[i], 30 + rng() * 50, 25 + rng() * 50));
  }

  return { background, midtone, highlight, accent, colors };
}
```

---

## Planet-Specific Palettes

Constrain hue ranges per planet type:

```typescript
const PLANET_PALETTE_CONFIGS: Record<string, { hueRange: [number,number]; rule: HarmonyRule }> = {
  toxic:  { hueRange: [80, 160],  rule: 'analogous' },
  ice:    { hueRange: [190, 230], rule: 'analogous' },
  desert: { hueRange: [20, 50],   rule: 'split' },
  lava:   { hueRange: [0, 30],    rule: 'complementary' },
  alien:  { hueRange: [260, 320], rule: 'triadic' },
};

function generatePlanetPalette(seed: string | number, type: string): Palette {
  const rng = Alea(seed);
  const config = PLANET_PALETTE_CONFIGS[type] || PLANET_PALETTE_CONFIGS.alien;
  const baseHue = config.hueRange[0] + rng() * (config.hueRange[1] - config.hueRange[0]);
  const hues = getHarmonyHues(baseHue, config.rule);

  const colors: [number, number, number][] = hues.map(hue =>
    hslToRgb(hue, 30 + rng() * 50, 20 + rng() * 50)
  );
  return { background: colors[0], midtone: colors[1], highlight: colors[2] || colors[1],
           accent: colors[colors.length - 1], colors };
}
```

---

## Applying Palettes to Assets

Map grayscale values to palette colors:

```typescript
function applyPalette(imageData: ImageData, palette: Palette): void {
  const { colors } = palette;
  for (let i = 0; i < imageData.data.length; i += 4) {
    const gray = (imageData.data[i] * 0.299 + imageData.data[i+1] * 0.587 + imageData.data[i+2] * 0.114) / 255;
    const idx = Math.min(colors.length - 1, Math.floor(gray * colors.length));
    const [r, g, b] = colors[idx];
    imageData.data[i] = r; imageData.data[i+1] = g; imageData.data[i+2] = b;
  }
}

// Smooth interpolation between palette colors
function samplePaletteSmooth(t: number, colors: [number,number,number][]): [number,number,number] {
  const scaled = t * (colors.length - 1);
  const idx = Math.floor(scaled), frac = scaled - idx;
  if (idx >= colors.length - 1) return colors[colors.length - 1];
  const a = colors[idx], b = colors[idx + 1];
  return [Math.round(a[0]+(b[0]-a[0])*frac), Math.round(a[1]+(b[1]-a[1])*frac), Math.round(a[2]+(b[2]-a[2])*frac)];
}
```

---

## Visual Result

```
Toxic:    [██][██][██][██][██]     Ice:      [██][██][██][██][██]
           dark  olive lime purple             navy  steel  ice  white

Desert:   [██][██][██][██][██]     Lava:     [██][██][██][██][██]
           brown tan   gold  violet            black red   orange blue
```

---

## Parameter Tuning

| Parameter | Effect | Juno's Notes |
|-----------|--------|--------------|
| Harmony rule | Color relationships | "Analogous = calm. Complementary = vibrant." |
| Saturation | Vividness | "Background low-sat (15-25). Accent high-sat (60-90)." |
| Lightness spread | Contrast | "Need ≥40 points between darkest and lightest." |
| Hue constraint | Theme | "Narrow (30°) = cohesive. Wide (120°+) = chaotic." |

---

## Exercises

1. **Seasonal shift:** Rotate a palette's hue by 30° increments to create spring/summer/autumn/winter variants. Render all four side by side.

2. **Palette-driven terrain:** Color a heightmap using a procedural palette instead of hardcoded biome colors. Different seeds = completely different-looking planets from the same heightmap.

3. **Contrast check:** Implement WCAG contrast ratio calculation. Verify that your palette's lightest and darkest colors have ratio ≥ 4.5:1. Reject palettes that fail.

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| HSL | Hue (0-360°), Saturation (0-100%), Lightness (0-100%) |
| Complementary | 180° apart — high contrast |
| Analogous | 30° apart — harmonious |
| Triadic | 120° apart — balanced, colorful |
| Palette structure | Background (dark) → Midtone → Highlight → Accent (vivid) |
| Planet palettes | Constrain hue range per planet type |

---

[← Ch 4](chapter-04-heightmaps.md) | [Ch 6 →](chapter-06-caves.md)
