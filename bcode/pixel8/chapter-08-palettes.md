# Chapter 8: Palettes — "Four Colors Is All You Need"

[← Chapter 7: Text & UI](chapter-07-text-ui.md) | [Chapter 9: Composition →](chapter-09-composition.md)

---

## Mika's Challenge

Mika pulls out her Game Boy — the original DMG with the pea-green screen:

> "This thing has four colors. Four. And people made *masterpieces* on it. Tetris. Link's Awakening. Pokémon. The constraint isn't a limitation — it's a *style*. When you pick a palette, you're picking a mood. A feeling. An era."

She sets it down:

> "Your BitForge game uses random hex colors right now. It looks like a rainbow threw up. Pick a palette. Commit to it. Watch everything suddenly look *cohesive*."

## What Is a Palette?

A palette is a fixed set of colors that every sprite and element draws from. Instead of choosing from 16 million colors, you pick 4, 8, or 16 — and everything uses only those.

Benefits:
- **Cohesion** — everything looks like it belongs together
- **Mood** — warm palettes feel different from cool ones
- **Constraint** — forces creative solutions for shading and contrast
- **Swappability** — change the palette, change the entire look instantly

## Classic Retro Palettes

### Game Boy (4 colors)

```jsx
const gameboy = ['#0f380f', '#306230', '#8bac0f', '#9bbc0f'];
// Darkest → lightest (all green-tinted)
```

### NES (a subset — 4 colors per sprite)

```jsx
const nesClassic = ['#000000', '#fcfcfc', '#f83800', '#0058f8'];
// Black, white, red, blue — the Mario palette
```

### Commodore 64 (16 colors)

```jsx
const c64 = [
  '#000000', '#ffffff', '#880000', '#aaffee',
  '#cc44cc', '#00cc55', '#0000aa', '#eeee77',
  '#dd8855', '#664400', '#ff7777', '#333333',
  '#777777', '#aaff66', '#0088ff', '#bbbbbb',
];
```

### PICO-8 (16 colors — modern retro)

```jsx
const pico8 = [
  '#000000', '#1d2b53', '#7e2553', '#008751',
  '#ab5236', '#5f574f', '#c2c3c7', '#fff1e8',
  '#ff004d', '#ffa300', '#ffec27', '#00e436',
  '#29adff', '#83769c', '#ff77a8', '#ffccaa',
];
```

### Monochrome (2 colors)

```jsx
const mono = ['#000000', '#ffffff'];
const amber = ['#000000', '#ffb000']; // amber monitor
const green = ['#000000', '#33ff33']; // green phosphor
```

## Applying a Palette

Define your palette once, reference it everywhere:

```jsx
// palettes.js
export const bitforge = {
  bg:      '#1a1a2e',
  dark:    '#16213e',
  mid:     '#0f3460',
  accent:  '#e94560',
  light:   '#ffffff',
  gold:    '#ffd700',
  green:   '#00cc44',
  shadow:  '#0a0a1a',
};

// In components
import { bitforge as pal } from './palettes';

<Stage width={64} height={64} scale={8} fps={0} background={pal.bg}>
  <rect x={10} y={10} width={8} height={8} color={pal.accent} />
  <text x={2} y={2} value="SCORE:0" color={pal.light} />
  <sprite x={28} y={28} data={knight} palette={['transparent', pal.mid, pal.dark]} />
</Stage>
```

## Palette Swapping: Instant Reskins

Since sprites use palette indices, changing the palette array changes the look without touching the data:

```jsx
const hero = [
  0,0,1,1,1,0,0,0,
  0,1,2,2,2,1,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,1,1,0,0,0,
  0,1,1,1,1,1,0,0,
  0,0,1,0,1,0,0,0,
  0,0,1,0,1,0,0,0,
  0,0,0,0,0,0,0,0,
];

// Same sprite data, different palettes = different characters
const palettes = {
  knight:  ['transparent', '#c0c0c0', '#333333'],  // silver armor
  mage:    ['transparent', '#4400aa', '#aa00ff'],  // purple robes
  ranger:  ['transparent', '#006600', '#00cc00'],  // green outfit
  fire:    ['transparent', '#cc3300', '#ff6600'],  // fire warrior
};

// Render all four from the same data
<sprite x={8}  y={28} data={hero} palette={palettes.knight} />
<sprite x={22} y={28} data={hero} palette={palettes.mage} />
<sprite x={36} y={28} data={hero} palette={palettes.ranger} />
<sprite x={50} y={28} data={hero} palette={palettes.fire} />
```

### What You Should See

Four identical character silhouettes in different colors — silver, purple, green, and orange. Same sprite, four personalities.

## Mood Through Color

| Mood | Palette Style | Example Colors |
|------|--------------|----------------|
| Cheerful | Bright, saturated | `#ff004d`, `#ffa300`, `#00e436` |
| Spooky | Dark, desaturated, purple | `#1a0a2e`, `#3d1e5c`, `#6b3fa0` |
| Retro tech | Green/amber on black | `#000000`, `#003300`, `#00ff00` |
| Ocean | Blues and teals | `#000033`, `#003366`, `#0099cc` |
| Sunset | Warm oranges and pinks | `#1a0000`, '#cc3300', '#ff6600', '#ffcc00'` |
| Winter | Cool blues and whites | `#0a1628`, `#2244aa`, `#88aaff`, `#ffffff` |

## Pattern: Day/Night Cycle

```jsx
const palettes = {
  day:   { bg: '#87ceeb', ground: '#228b22', accent: '#ffd700' },
  dusk:  { bg: '#cc6633', ground: '#1a4d1a', accent: '#ff9900' },
  night: { bg: '#0a0a2e', ground: '#0a1a0a', accent: '#aaaaff' },
};

const [timeOfDay, setTimeOfDay] = useState('day');
const pal = palettes[timeOfDay];

<Stage width={64} height={64} scale={8} fps={0} background={pal.bg}>
  <rect x={0} y={48} width={64} height={16} color={pal.ground} />
  <circ x={50} y={12} radius={5} color={pal.accent} />
</Stage>
```

Press a key to cycle through day → dusk → night. Same scene, completely different mood.

## Pattern: Damage Flash

```jsx
const [isHit, setIsHit] = useState(false);

// Normal palette vs hit palette
const currentPalette = isHit
  ? ['transparent', '#ffffff', '#ff0000']  // flash white/red
  : ['transparent', '#c0c0c0', '#333333']; // normal

<sprite x={pos.x} y={pos.y} data={hero} palette={currentPalette} />

// On hit:
setIsHit(true);
setTimeout(() => setIsHit(false), 100); // flash for 100ms
```

## Designing Your Own Palette

Mika's rules for palette design:

1. **Start with background** — this is the most-seen color. Make it comfortable.
2. **Pick one accent** — the color that draws the eye. Use sparingly.
3. **Add a dark and a light** — for contrast, outlines, highlights.
4. **Fill the middle** — 1-2 mid-tones for shading and secondary elements.
5. **Test together** — put all colors in a row. Do they feel like a family?

```jsx
// Palette test card
const PaletteTest = ({ colors }) => (
  <Stage width={64} height={64} scale={8} fps={0} background="#000000">
    {colors.map((color, i) => (
      <rect
        key={i}
        x={4 + i * 7}
        y={28}
        width={6}
        height={8}
        color={color}
      />
    ))}
  </Stage>
);
```

## Pattern: Palette from Constraints

```jsx
// Force yourself: pick a palette FIRST, then design within it
const myPalette = ['#1a1a2e', '#e94560', '#0f3460', '#ffffff'];

// Now everything must use only these 4 colors:
// - Background: #1a1a2e
// - Primary shapes: #e94560 (crimson)
// - Secondary: #0f3460 (navy)
// - Highlights: #ffffff (white)

// Sprites get 4-color palettes too:
const spritePal = ['transparent', '#e94560', '#0f3460', '#ffffff'];
// Index 0 = transparent, indices 1-3 = your three visible colors
```

## Tips: Color Theory for Pixel Art

1. **Hue shifting** — shadows aren't just darker versions. Shift hue toward blue/purple for shadows, toward yellow for highlights.
2. **Value contrast matters most** — squint at your screen. If shapes disappear, you need more value contrast.
3. **Warm advances, cool recedes** — warm colors (red, orange) feel closer; cool colors (blue, purple) feel farther.
4. **Limit saturation** — fully saturated colors fight for attention. Desaturate backgrounds.
5. **Steal palettes** — screenshot a retro game, extract 4-8 colors. That's your starting point.

## Exercise

1. Create the **Game Boy look** — render your knight sprite using only the 4 Game Boy greens on a Game Boy green background
2. Implement **palette cycling** — press 1-4 to switch between four different palettes for the same scene
3. Design a **spooky palette** and re-render the house scene from Chapter 1 as a haunted house
4. Build a **palette editor** — click on color swatches to cycle through preset colors, see sprites update live

## Quick Reference

```jsx
// Define palette
const palette = ['transparent', '#color1', '#color2', '#color3'];

// Apply to sprite
<sprite data={spriteData} palette={palette} x={0} y={0} />

// Palette swap (same data, different colors)
<sprite data={hero} palette={isHit ? flashPalette : normalPalette} />
```

| Classic System | Colors | Vibe |
|---------------|--------|------|
| Game Boy | 4 greens | Nostalgic, monochrome |
| NES | 4 per sprite, 25 total | Colorful, iconic |
| C64 | 16 fixed | Warm, earthy |
| PICO-8 | 16 curated | Modern retro |
| Monochrome | 2 (black + one) | Stark, dramatic |

| Palette Role | Purpose |
|-------------|---------|
| Background | Most-seen, comfortable |
| Dark | Outlines, shadows |
| Mid | Body, secondary elements |
| Light | Highlights, text |
| Accent | Eye-catching, use sparingly |

---

Next: Individual sprites look great. But how do you build a *scene*? Layering, positioning, and composing complex visuals from simple parts.

[← Chapter 7: Text & UI](chapter-07-text-ui.md) | [Chapter 9: Composition →](chapter-09-composition.md)
