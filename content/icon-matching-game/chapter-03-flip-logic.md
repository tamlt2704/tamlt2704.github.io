# Chapter 3: Flip & Match Logic

[← Chapter 2: The Grid](/blog/icon-matching-game/chapter-02-grid) | [Chapter 4: Polish & Features →](/blog/icon-matching-game/chapter-04-polish)

---

## The Goal

Make cards flip on click, detect matches, flip back mismatches after a delay, handle the secret card, and detect a win.

## Step 1: Game State

We need several pieces of state working together:

```tsx
const [cards, setCards] = useState(() => buildCards(4));
const [selected, setSelected] = useState<number[]>([]); // IDs of flipped cards (0-2)
const [moves, setMoves] = useState(0);
const [locked, setLocked] = useState(false); // prevent clicks during mismatch delay
const [secretFound, setSecretFound] = useState(false);
```

The `selected` array holds at most 2 card IDs — the current "turn".

---

## Step 2: The Flip Handler

```tsx
const handleFlip = useCallback(
  (id: number) => {
    if (locked || revealAll) return;
    const card = cards[id];
    if (card.flipped || card.matched) return;

    // Secret card — just reveal it, no pair needed
    if (card.isSecret) {
      setCards((prev) => prev.map((c) => (c.id === id ? { ...c, flipped: true } : c)));
      setSecretFound(true);
      setMoves((m) => m + 1);
      return;
    }

    // Normal card — flip and add to selection
    const next = cards.map((c) => (c.id === id ? { ...c, flipped: true } : c));
    setCards(next);
    setSelected((prev) => [...prev, id]);
  },
  [cards, locked, revealAll],
);
```

Key guards:

- `locked` — prevents clicks while mismatch animation plays
- `revealAll` — disables interaction in preview mode
- Already flipped/matched cards are ignored
- Secret card is handled separately (no pair to match)

---

## Step 3: Match Detection with useEffect

When `selected` reaches 2 cards, we check for a match:

```tsx
useEffect(() => {
  if (selected.length !== 2) return;
  setMoves((m) => m + 1);
  const [a, b] = selected;

  if (cards[a].pairIndex === cards[b].pairIndex) {
    // Match! Mark both as matched
    setCards((prev) => prev.map((c) => (c.id === a || c.id === b ? { ...c, matched: true } : c)));
    setSelected([]);
  } else {
    // Mismatch — flip back after delay
    setLocked(true);
    setTimeout(() => {
      setCards((prev) =>
        prev.map((c) => (c.id === a || c.id === b ? { ...c, flipped: false } : c)),
      );
      setSelected([]);
      setLocked(false);
    }, 800);
  }
}, [selected, cards]);
```

The 800ms timeout gives the player time to see both cards before they flip back.

---

## Step 4: Win Detection

A simple derived value — no state needed:

```tsx
const won = cards.every((c) => c.matched || c.isSecret);
```

The secret card doesn't need matching, so we exclude it from the win condition.

---

## Step 5: Conditional Card Rendering

Cards show different content based on state:

```tsx
{
  cards.map((card) => {
    const show = revealAll || card.flipped || card.matched;
    let content;
    if (show && card.isSecret) {
      content = <GiTreasureMap style={{ fontSize: `${iconSize}px` }} />;
    } else if (show) {
      const { Icon, color } = getIconConfig(card.pairIndex, icons);
      content = <Icon style={{ color, fontSize: `${iconSize}px` }} />;
    } else {
      content = <span className="text-gray-400">?</span>;
    }

    return (
      <button
        key={card.id}
        onClick={() => handleFlip(card.id)}
        className={`... ${
          card.isSecret && card.flipped
            ? "animate-pulse border-amber-400 bg-amber-50"
            : card.matched
              ? "border-green-400 bg-green-50"
              : show
                ? "border-blue-400 bg-blue-50"
                : "border-gray-300 bg-gray-100 hover:bg-gray-200"
        }`}
      >
        {content}
      </button>
    );
  });
}
```

Four visual states:

1. **Hidden** — gray border, "?" text
2. **Flipped** — blue border, icon visible
3. **Matched** — green border, stays revealed
4. **Secret found** — amber border with pulse animation

---

## Step 6: Reset

```tsx
const reset = (newSize?: number) => {
  const s = newSize ?? size;
  setSize(s);
  setCards(buildCards(s));
  setSelected([]);
  setMoves(0);
  setLocked(false);
  setRevealAll(false);
  setSecretFound(false);
};
```

Resets everything. Called by the Reset button, size selector, and topic changes.

---

## The Flow

```
Click card → handleFlip
  ├── Guard checks (locked? already flipped?)
  ├── Secret card? → reveal + done
  └── Normal card → flip + add to selected[]

selected.length === 2 → useEffect fires
  ├── Same pairIndex? → mark matched
  └── Different? → lock, wait 800ms, flip back, unlock
```

---

## What We Have

- Click-to-flip with proper guards
- Pair matching via `pairIndex` comparison
- Mismatch delay with UI lock
- Secret card reveal (no pair needed)
- Win detection
- Visual feedback for each card state

## Next

We'll add topic selection, reveal-all for printing, B&W mode, and print styles.

[Chapter 4: Polish & Features →](/blog/icon-matching-game/chapter-04-polish)
