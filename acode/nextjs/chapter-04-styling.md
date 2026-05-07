# Chapter 4: Styling — Tailwind, Fonts, and Dark Mode

[← Chapter 3: Data Fetching](chapter-03-data-fetching.md) | [Chapter 5: Navigation & Loading States →](chapter-05-navigation.md)

---

## The Task

Mika drops a Figma link. "Trail cards with gradient overlays. Responsive grid. Dark mode toggle. Custom font. Ship it by EOD."

---

## Tailwind CSS (Already Installed)

`create-next-app` set up Tailwind for us. It's in `src/app/globals.css`:

```css
@import "tailwindcss";
```

Every component can use Tailwind classes directly. No imports, no config per file.

---

## next/font: Zero Layout Shift

Next.js downloads fonts at build time and self-hosts them. No external requests. No FOUT (Flash of Unstyled Text).

```tsx
// src/app/layout.tsx
import { Inter, JetBrains_Mono } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body className="font-sans">{/* ... */}</body>
    </html>
  );
}
```

Use in Tailwind config:

```ts
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
    },
  },
};

export default config;
```

---

## The Trail Card Component

```tsx
// src/components/TrailCard.tsx
import Link from "next/link";
import type { Trail } from "@/types";

const difficultyColors = {
  easy: "bg-green-100 text-green-800",
  moderate: "bg-amber-100 text-amber-800",
  hard: "bg-orange-100 text-orange-800",
  expert: "bg-red-100 text-red-800",
};

export function TrailCard({ trail }: { trail: Trail }) {
  return (
    <Link href={`/trails/${trail.slug}`} className="group block">
      <div className="relative overflow-hidden rounded-xl bg-white shadow-sm
                      ring-1 ring-stone-100 transition-all
                      group-hover:shadow-lg group-hover:ring-emerald-200">
        <div className="relative h-48">
          <img
            src={trail.image_url}
            alt={trail.name}
            className="h-full w-full object-cover transition-transform duration-300
                       group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
          <span className={`absolute bottom-3 left-3 rounded-full px-2.5 py-0.5
                           text-xs font-semibold ${difficultyColors[trail.difficulty]}`}>
            {trail.difficulty}
          </span>
        </div>
        <div className="p-4">
          <h3 className="font-semibold text-stone-900 group-hover:text-emerald-700 transition-colors">
            {trail.name}
          </h3>
          <p className="text-sm text-stone-500 mt-1">{trail.location}</p>
          <div className="flex items-center justify-between mt-3 text-sm">
            <span className="text-stone-600">{trail.distance_km} km · {trail.elevation_m}m ↑</span>
            <span className="text-amber-600 font-medium">★ {trail.rating.toFixed(1)}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}
```

---

## CSS Modules (Alternative)

If you prefer scoped CSS files:

```tsx
// src/components/Badge.tsx
import styles from "./Badge.module.css";

export function Badge({ label }: { label: string }) {
  return <span className={styles.badge}>{label}</span>;
}
```

```css
/* src/components/Badge.module.css */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}
```

CSS Modules scope class names automatically — no conflicts. Use them alongside Tailwind for complex animations or when you prefer traditional CSS.

---

## Dark Mode

```tsx
// src/components/ThemeToggle.tsx
"use client"; // needs interactivity (click handler, state)

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setDark(stored === "dark" || (!stored && prefersDark));
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <button
      onClick={() => setDark(!dark)}
      className="p-2 rounded-lg hover:bg-stone-100 dark:hover:bg-stone-800 transition-colors"
      aria-label="Toggle dark mode"
    >
      {dark ? "☀️" : "🌙"}
    </button>
  );
}
```

Add `"use client"` — this component uses hooks and event handlers, so it must run in the browser. Add it to your nav in `layout.tsx`.

Dark mode classes:

```tsx
<div className="bg-white dark:bg-stone-900 text-stone-900 dark:text-stone-100">
```

---

## Global Styles

```css
/* src/app/globals.css */
@import "tailwindcss";

@layer base {
  body {
    @apply bg-stone-50 text-stone-900 dark:bg-stone-950 dark:text-stone-100;
  }
}

@layer components {
  .card {
    @apply bg-white dark:bg-stone-900 rounded-xl shadow-sm ring-1 ring-stone-100 dark:ring-stone-800;
  }
}
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Feature                         │ How
────────────────────────────────┼──────────────────────────────────────
Tailwind                        │ Classes directly in JSX
CSS Modules                     │ import styles from "./X.module.css"
Global CSS                      │ src/app/globals.css
Fonts (no CLS)                  │ next/font/google + CSS variable
Dark mode                       │ darkMode: "class" + toggle component
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The pages look great. But when you click a trail card, there's a brief white flash before the detail page appears. Mika: "That flash is unacceptable. Show a skeleton. Show something."

Loading states, error boundaries, and navigation UX.

---

[← Chapter 3: Data Fetching](chapter-03-data-fetching.md) | [Chapter 5: Navigation & Loading States →](chapter-05-navigation.md)
