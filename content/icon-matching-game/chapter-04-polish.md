# Chapter 4: Polish & Features

[← Chapter 3: Flip & Match](/blog/icon-matching-game/chapter-03-flip-logic) | [Overview](/blog/icon-matching-game/chapter-00-overview)

---

## The Goal

Add topic selection with checkboxes, reveal-all mode, black & white toggle, and print-to-A4 support.

## Step 1: Topic Checkboxes

Instead of a single dropdown, we use checkboxes so players can mix topics:

```tsx
const [selectedTopics, setSelectedTopics] = useState<string[]>(["animals"]);

const icons = selectedTopics.flatMap((t) => TOPICS[t].icons);

const toggleTopic = (key: string) => {
  const next = selectedTopics.includes(key)
    ? selectedTopics.filter((t) => t !== key)
    : [...selectedTopics, key];
  if (next.length === 0) return; // must have at least one
  setSelectedTopics(next);
  // Reset game with new icon pool
  setCards(buildCards(size));
  setSelected([]);
  setMoves(0);
};
```

The `icons` array is derived — it flattens all selected topics' icon arrays into one pool. Changing topics resets the game.

UI:

```tsx
<div className="flex flex-wrap gap-2">
  {Object.entries(TOPICS).map(([key, { label }]) => (
    <label key={key} className="flex cursor-pointer items-center gap-1 text-sm">
      <input
        type="checkbox"
        checked={selectedTopics.includes(key)}
        onChange={() => toggleTopic(key)}
      />
      {label}
    </label>
  ))}
</div>
```

Check "🐾 Animals" + "🍕 Food" and you get a mixed grid.

---

## Step 2: Reveal All

A toggle that shows every card — useful for previewing the board or printing an answer key:

```tsx
const [revealAll, setRevealAll] = useState(false);

// In the card render:
const show = revealAll || card.flipped || card.matched;

// In handleFlip:
if (locked || revealAll) return; // disable interaction when revealed
```

```tsx
<button onClick={() => setRevealAll((r) => !r)}>{revealAll ? "Hide All" : "Reveal All"}</button>
```

---

## Step 3: Black & White Mode

For printing on B&W printers, icons need to be distinguishable by shape alone:

```tsx
const [bw, setBw] = useState(false);

// In icon rendering:
content = <Icon style={{ color: bw ? "#000" : color, fontSize: `${iconSize}px` }} />;
```

```tsx
<label className="flex cursor-pointer items-center gap-1 text-sm">
  <input type="checkbox" checked={bw} onChange={() => setBw((v) => !v)} />
  B&W
</label>
```

When checked, all icons render in black. The different icon shapes make pairs identifiable without color.

---

## Step 4: Print Styles

CSS `@media print` hides everything except the grid:

```tsx
<style>{`
  @media print {
    body * { visibility: hidden; }
    #print-grid, #print-grid * { visibility: visible; }
    #print-grid { position: absolute; top: 0; left: 0; width: 190mm; padding: 5mm; }
    .no-print { display: none !important; }
  }
`}</style>
```

The grid is given `id="print-grid"`. All controls get `className="no-print"`.

A4 paper has ~190mm printable width. The `cardPx` calculation ensures cards fit:

```tsx
const cardPx = Math.floor(720 / size) - 4; // 720px ≈ 190mm at 96dpi
```

Print workflow:

1. Select grid size and topic
2. Click "Reveal All" to show icons (or leave hidden for a play sheet)
3. Enable "B&W" if using a mono printer
4. Click "🖨️ Print"

---

## Step 5: Putting the Controls Together

The final toolbar:

```tsx
<div className="no-print flex flex-wrap items-center gap-3">
  {/* Topic checkboxes */}
  {/* Size dropdown */}
  {/* Reveal All button */}
  {/* Print button */}
  {/* B&W checkbox */}
</div>
```

All controls have `no-print` so they disappear when printing.

---

## The Complete Feature Set

```
┌─────────────────────────────────────────────────────┐
│  [✓] 🐾 Animals  [ ] 💻 Tech  [✓] 🍕 Food         │
│  Grid: [6×6 ▾]  [Reveal All]  [🖨️ Print]  [✓] B&W │
│                                                     │
│  Moves: 12          Secret: 🗝️ Hidden...            │
│                                                     │
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐                   │
│  │🐱│ │? │ │🍕│ │? │ │🐱│ │? │                    │
│  └──┘ └──┘ └──┘ └──┘ └──┘ └──┘                   │
│  ...                                               │
│                                                     │
│              [ Reset ]                              │
└─────────────────────────────────────────────────────┘
```

---

## What We Built

Starting from zero, we built a complete memory matching game:

1. **Chapter 1** — Icon system with topics and color scaling
2. **Chapter 2** — Card generation, shuffle, dynamic grid sizing
3. **Chapter 3** — Flip logic, match detection, secret card, win state
4. **Chapter 4** — Multi-topic selection, reveal, B&W, print support

All in one `~250-line` component. No external state library. No backend. Just React hooks and a well-structured component.

---

## Ideas for Extension

- Timer mode (solve before time runs out)
- Difficulty levels (shorter mismatch delay)
- High score tracking with `localStorage`
- Multiplayer (take turns, track scores)
- Custom icon upload

[← Overview](/blog/icon-matching-game/chapter-00-overview)
