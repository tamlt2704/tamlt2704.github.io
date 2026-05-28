# Chapter 2: The Card Grid

[← Chapter 1: Setup](/blog/icon-matching-game/chapter-01-setup) | [Chapter 3: Flip & Match →](/blog/icon-matching-game/chapter-03-flip-logic)

---

## The Goal

Turn our icon pool into a shuffled grid of face-down cards. Support grid sizes from 4×4 to 20×20, including odd sizes with a secret card.

## Step 1: The Card Interface

Each card needs to track its state:

```tsx
interface Card {
  id: number;
  pairIndex: number; // which icon pair it belongs to (-1 for secret)
  flipped: boolean;
  matched: boolean;
  isSecret: boolean; // the lone card on odd grids
}
```

---

## Step 2: Shuffle Function

Fisher-Yates shuffle — the standard unbiased shuffle:

```tsx
function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
```

We spread into a new array first so we don't mutate the input.

---

## Step 3: Building Cards

The key insight: for a grid of size N, we need N×N/2 pairs. For odd totals (5×5 = 25), we add one secret card:

```tsx
function buildCards(size: number): Card[] {
  const total = size * size;
  const isOdd = total % 2 !== 0;
  const pairCount = Math.floor(total / 2);
  const indices = [...Array(pairCount).keys()];
  const pairs: (number | "secret")[] = [...indices, ...indices];
  if (isOdd) pairs.push("secret");
  const shuffled = shuffle(pairs);
  return shuffled.map((val, id) => ({
    id,
    pairIndex: val === "secret" ? -1 : val,
    flipped: false,
    matched: false,
    isSecret: val === "secret",
  }));
}
```

`[...Array(pairCount).keys()]` creates `[0, 1, 2, ...]`. Doubling it gives each index a pair.

---

## Step 4: Grid Sizes

We support sizes 4 through 20:

```tsx
const SIZES = Array.from({ length: 17 }, (_, i) => i + 4);
```

Odd sizes (5, 7, 9...) get a secret card. Even sizes are pure pairs.

---

## Step 5: Dynamic Card Sizing

Cards must fit on screen (and on A4 paper for printing). We calculate pixel size from the grid:

```tsx
const cardPx = Math.floor(720 / size) - 4; // 720px ≈ 190mm at 96dpi
const iconSize = Math.floor(cardPx * 0.6); // icon fills 60% of card
```

A 4×4 grid gets ~176px cards. A 20×20 grid gets ~32px cards.

---

## Step 6: Rendering the Grid

CSS Grid with dynamic columns:

```tsx
<div id="print-grid" className="grid gap-1" style={{ gridTemplateColumns: `repeat(${size}, 1fr)` }}>
  {cards.map((card) => (
    <button
      key={card.id}
      style={{ width: `${cardPx}px`, height: `${cardPx}px` }}
      className="flex items-center justify-center rounded border-2 border-gray-300 bg-gray-100"
    >
      <span className="text-gray-400">?</span>
    </button>
  ))}
</div>
```

The `style` prop sets exact pixel dimensions. The `gridTemplateColumns` creates N equal columns.

---

## Step 7: Size Selector

A dropdown that resets the game when changed:

```tsx
<select value={size} onChange={(e) => reset(Number(e.target.value))}>
  {SIZES.map((s) => (
    <option key={s} value={s}>
      {s}×{s} ({Math.floor((s * s) / 2)} pairs{(s * s) % 2 !== 0 ? " + 🗝️" : ""})
    </option>
  ))}
</select>
```

The label shows pair count and a key emoji for odd grids.

---

## What We Have

- Cards generated as pairs with shuffle
- Odd grids get a secret card
- Dynamic sizing from 4×4 to 20×20
- Cards scale to fit screen and A4 paper
- CSS Grid layout with responsive columns

## Next

We'll add flip logic — click to reveal, match detection, and the mismatch timer.

[Chapter 3: Flip & Match Logic →](/blog/icon-matching-game/chapter-03-flip-logic)
