# Chapter 7: Text & UI — "Words Made of Pixels"

[← Chapter 6: Buffers](chapter-06-buffers.md) | [Chapter 8: Palettes →](chapter-08-palettes.md)

---

## Mika's Challenge

Mika plays your dodge game and immediately asks:

> "What's my score? How many lives do I have? When I die, what do I do — just stare at a frozen screen? You need *text*. Score counters. 'GAME OVER'. 'PRESS START'. A HUD. But here's the thing — at 64×64, every character is maybe 3×5 pixels. That's the charm."

She shows you a screenshot of an NES game's font:

> "These fonts are hand-drawn, pixel by pixel. Each letter is a tiny sprite. Pixel8 has a `<text>` component that handles this for you."

## The `<text>` Component

```jsx
<text x={2} y={2} value="HELLO" color="#ffffff" />
```

Pixel8's `<text>` renders strings using a built-in pixel font. Each character is rendered as actual pixels on the canvas — no browser fonts, no anti-aliasing, pure pixel text.

### Props

| Prop | Type | Description |
|------|------|-------------|
| `x` | number | Left edge position |
| `y` | number | Top edge position |
| `value` | string | The text to display |
| `color` | string | Text color (hex) |
| `font` | string | Optional font name (if custom fonts are supported) |

## Score Display

```jsx
import React, { useState } from 'react';
import { Stage } from 'pixel8';

const ScoreDemo = () => {
  const [score, setScore] = useState(0);

  return (
    <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
      {/* Score in top-left */}
      <text x={1} y={1} value={`SCORE:${score}`} color="#ffffff" />

      {/* Lives in top-right */}
      <text x={45} y={1} value="♥♥♥" color="#ff0000" />

      {/* Game content below */}
      <rect x={28} y={28} width={8} height={8} color="#4488ff" />
    </Stage>
  );
};
```

### What You Should See

"SCORE:0" in white pixels at the top-left, three red hearts at the top-right, and a blue square in the center.

## HUD Layout Pattern

At 64×64, screen real estate is precious. A common HUD layout:

```
┌────────────────────────────────┐
│ SCORE:42        ♥♥♥            │  ← Row 0-6: HUD
├────────────────────────────────┤
│                                │
│                                │
│        GAME AREA               │  ← Rows 7-57: Gameplay
│                                │
│                                │
├────────────────────────────────┤
│ LV:3           ITEMS:2         │  ← Rows 58-63: Status bar
└────────────────────────────────┘
```

```jsx
const HUD = ({ score, lives, level }) => (
  <>
    {/* Top bar */}
    <rect x={0} y={0} width={64} height={7} color="#000000" />
    <text x={1} y={1} value={`SC:${score}`} color="#ffffff" />
    <text x={40} y={1} value={`${'♥'.repeat(lives)}`} color="#ff4444" />

    {/* Bottom bar */}
    <rect x={0} y={58} width={64} height={6} color="#000000" />
    <text x={1} y={59} value={`LV:${level}`} color="#aaaaaa" />
  </>
);
```

## Game Over Screen

```jsx
const GameOverScreen = ({ score, onRestart }) => (
  <Stage width={64} height={64} scale={8} fps={0} background="#0a0a0a">
    {/* Dark overlay effect */}
    <rect x={0} y={0} width={64} height={64} color="#0a0a0a" />

    {/* GAME OVER text */}
    <text x={12} y={20} value="GAME" color="#ff0000" />
    <text x={12} y={28} value="OVER" color="#ff0000" />

    {/* Score */}
    <text x={8} y={40} value={`SCORE:${score}`} color="#ffffff" />

    {/* Restart prompt */}
    <text x={4} y={52} value="PRESS R" color="#888888" />
  </Stage>
);
```

### What You Should See

A dark screen with "GAME OVER" in red, the final score in white, and "PRESS R" in gray at the bottom.

## Title Screen

```jsx
const TitleScreen = () => (
  <Stage width={64} height={64} scale={8} fps={60} background="#1a1a2e">
    {/* Game title */}
    <text x={8} y={12} value="BIT" color="#ffd700" />
    <text x={6} y={20} value="FORGE" color="#ffd700" />

    {/* Decorative line */}
    <rect x={8} y={30} width={48} height={1} color="#333333" />

    {/* Subtitle */}
    <text x={4} y={35} value="A PIXEL" color="#888888" />
    <text x={4} y={42} value="ADVENTURE" color="#888888" />

    {/* Blinking prompt (toggle with state) */}
    <text x={4} y={54} value="PRESS START" color="#ffffff" />
  </Stage>
);
```

## Blinking Text Effect

```jsx
import React, { useState, useEffect } from 'react';

const BlinkingText = ({ x, y, value, color, interval = 500 }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => setVisible(v => !v), interval);
    return () => clearInterval(timer);
  }, [interval]);

  if (!visible) return null;
  return <text x={x} y={y} value={value} color={color} />;
};

// Usage
<BlinkingText x={4} y={54} value="PRESS START" color="#ffffff" interval={600} />
```

## Number Formatting for Scores

```jsx
// Pad score to fixed width
const formatScore = (n, width = 5) => String(n).padStart(width, '0');

<text x={1} y={1} value={formatScore(score)} color="#ffffff" />
// Displays: "00042" instead of "42"

// Timer display
const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, '0')}`;
};

<text x={24} y={1} value={formatTime(elapsed)} color="#00ff00" />
// Displays: "2:07"
```

## Pattern: Dialog Box

```jsx
const DialogBox = ({ text, speaker }) => (
  <>
    {/* Box background */}
    <rect x={2} y={44} width={60} height={18} color="#000000" />
    {/* Box border */}
    <rect x={2} y={44} width={60} height={1} color="#ffffff" />
    <rect x={2} y={61} width={60} height={1} color="#ffffff" />
    <rect x={2} y={44} width={1} height={18} color="#ffffff" />
    <rect x={61} y={44} width={1} height={18} color="#ffffff" />

    {/* Speaker name */}
    <text x={5} y={46} value={speaker} color="#ffd700" />

    {/* Dialog text */}
    <text x={5} y={53} value={text} color="#ffffff" />
  </>
);

// Usage
<DialogBox speaker="MIKA" text="NICE WORK!" />
```

### What You Should See

A bordered box at the bottom of the screen with "MIKA" in gold and "NICE WORK!" in white — like a classic RPG dialog.

## Pattern: Menu System

```jsx
const Menu = ({ options, selected }) => (
  <>
    <rect x={10} y={15} width={44} height={options.length * 10 + 6} color="#1a1a2e" />
    {options.map((option, i) => (
      <React.Fragment key={i}>
        {/* Selection arrow */}
        {i === selected && <text x={12} y={18 + i * 10} value=">" color="#ffd700" />}
        {/* Option text */}
        <text
          x={18}
          y={18 + i * 10}
          value={option}
          color={i === selected ? '#ffffff' : '#666666'}
        />
      </React.Fragment>
    ))}
  </>
);

// Usage with keyboard navigation
const [selected, setSelected] = useState(0);
const options = ['START', 'OPTIONS', 'QUIT'];

// In key handler:
// ArrowUp → setSelected(s => Math.max(0, s - 1))
// ArrowDown → setSelected(s => Math.min(options.length - 1, s + 1))
```

## Tips: Text at Low Resolution

1. **ALL CAPS reads better** — lowercase letters need descenders (g, p, y) which eat vertical space
2. **Short words** — abbreviate: "SCORE" → "SC", "LEVEL" → "LV", "HEALTH" → "HP"
3. **Leave margins** — text at x=0 looks cramped. Start at x=1 or x=2.
4. **Contrast with background** — white text on dark, or use a solid rect behind text
5. **One line at a time** — at 64px wide, you get maybe 10-12 characters per line
6. **Numbers are free** — digits are narrow and always readable

## Pattern: Typewriter Effect

```jsx
const TypewriterText = ({ x, y, fullText, color, speed = 100 }) => {
  const [charCount, setCharCount] = useState(0);

  useEffect(() => {
    if (charCount < fullText.length) {
      const timer = setTimeout(() => setCharCount(c => c + 1), speed);
      return () => clearTimeout(timer);
    }
  }, [charCount, fullText, speed]);

  return <text x={x} y={y} value={fullText.slice(0, charCount)} color={color} />;
};

// Usage
<TypewriterText x={4} y={30} fullText="HELLO WORLD" color="#00ff00" speed={80} />
```

## Exercise

1. Build a **complete HUD** with score, lives (as heart sprites), level number, and a timer
2. Create a **pause menu** that overlays the game with options: RESUME, RESTART, QUIT
3. Implement a **high score table** — display top 5 scores with initials (AAA, BBB format)
4. Make a **scrolling credits** screen — text that moves upward from the bottom

## Quick Reference

```jsx
// Basic text
<text x={2} y={2} value="HELLO" color="#ffffff" />

// Dynamic value
<text x={2} y={2} value={`SC:${score}`} color="#fff" />

// Formatted number
<text x={2} y={2} value={String(n).padStart(5, '0')} color="#fff" />
```

| Pattern | Implementation |
|---------|---------------|
| HUD | Fixed-position text + background rect |
| Blinking | Toggle visibility with setInterval |
| Dialog box | Bordered rect + speaker + message text |
| Menu | List of options + selection indicator |
| Typewriter | Incrementally reveal characters |

| Guideline | Rule |
|-----------|------|
| Max chars/line | ~10-12 at 64px width |
| Case | UPPERCASE preferred |
| Margins | Start at x=1 or x=2 |
| Background | Dark rect behind text for readability |

---

Next: Your game works but looks generic. Time to give it personality with carefully chosen color palettes.

[← Chapter 6: Buffers](chapter-06-buffers.md) | [Chapter 8: Palettes →](chapter-08-palettes.md)
