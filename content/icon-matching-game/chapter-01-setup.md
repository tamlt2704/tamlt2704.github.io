# Chapter 1: First Icons on Screen

[← Overview](/blog/icon-matching-game/chapter-00-overview) | [Chapter 2: The Card Grid →](/blog/icon-matching-game/chapter-02-grid)

---

## The Goal

By the end of this chapter, you'll have `react-icons` installed and icons from multiple sets rendering on screen — animals, tech logos, sports, and food.

## Step 1: Install react-icons

```bash
npm install react-icons
```

No CSS to link, no fonts to download. Every icon is an SVG wrapped in a React component.

---

## Concept: How react-icons Works

Each icon set lives in its own sub-path:

```tsx
import { FaReact } from "react-icons/fa"; // Font Awesome
import { SiTypescript } from "react-icons/si"; // Simple Icons
import { GiCat } from "react-icons/gi"; // Game Icons
```

Only the icons you import end up in your bundle (tree-shaking).

---

## Step 2: Create the Game Route

Create `app/games/matching/page.tsx`:

```tsx
import MatchingGame from "@/app/games/matching/MatchingGame";

export const metadata = {
  title: "Memory Game",
  description: "A simple memory card matching game",
};

export default function Page() {
  return <MatchingGame />;
}
```

---

## Step 3: Set Up the Icon Pool

Create `app/games/matching/MatchingGame.tsx`. We organize icons by topic:

```tsx
"use client";

import { FaReact, FaDocker, FaGithub, FaPython } from "react-icons/fa";
import { SiTypescript, SiKubernetes } from "react-icons/si";
import { GiCat, GiSittingDog, GiElephant, GiDolphin } from "react-icons/gi";
import type { IconType } from "react-icons";

const TOPICS: Record<string, { label: string; icons: IconType[] }> = {
  tech: {
    label: "💻 Tech",
    icons: [FaReact, FaDocker, FaGithub, FaPython, SiTypescript, SiKubernetes],
  },
  animals: {
    label: "🐾 Animals",
    icons: [GiCat, GiSittingDog, GiElephant, GiDolphin],
  },
};
```

The `IconType` type from `react-icons` lets us store icon components in arrays and render them dynamically.

---

## Step 4: Render Icons

Let's verify they work:

```tsx
export default function MatchingGame() {
  const icons = TOPICS.animals.icons;

  return (
    <div className="flex gap-4 p-8">
      {icons.map((Icon, i) => (
        <div key={i} className="flex h-16 w-16 items-center justify-center rounded border">
          <Icon style={{ fontSize: "32px", color: "#2563eb" }} />
        </div>
      ))}
    </div>
  );
}
```

Visit `/games/matching` — you should see four animal icons in blue.

---

## Key Concept: Icons as Components

In `react-icons`, every icon is a React component. That means:

```tsx
const Icon = GiCat;       // Store in a variable
<Icon />                  // Render it
<Icon style={{ color: "red", fontSize: "48px" }} />  // Style it
```

This is why we can put them in arrays and render dynamically — they're just components.

---

## Step 5: Color Variations

For larger grids, we need more unique pairs than we have icons. Solution: combine icons with colors:

```tsx
const COLORS = ["#e11d48", "#2563eb", "#16a34a", "#9333ea", "#ea580c"];

function getIconConfig(index: number, icons: IconType[]) {
  const iconIdx = index % icons.length;
  const colorIdx = Math.floor(index / icons.length) % COLORS.length;
  return { Icon: icons[iconIdx], color: COLORS[colorIdx] };
}
```

With 44 icons × 8 colors = 352 unique combos — enough for a 20×20 grid (200 pairs).

---

## What We Have

- `react-icons` installed
- Icons from `fa`, `si`, and `gi` sets rendering
- Icons organized by topic in a `TOPICS` object
- A color system for generating unique pairs at scale

## Next

We'll turn these icons into a shuffled grid of face-down cards.

[Chapter 2: The Card Grid →](/blog/icon-matching-game/chapter-02-grid)
