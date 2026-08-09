# Chapter 20: shadcn/ui — Navbar, Search Layout, and Component Library

## What you'll learn

- What shadcn/ui is (and why it's not a traditional component library)
- How to install and configure shadcn/ui in a Next.js project
- Building a responsive navbar with shadcn components
- Building an algorithm search/browse page with filters
- Using shadcn's Input, Button, Card, Badge, Command (search palette), Sheet (mobile menu)
- Layout patterns: search + filter sidebar + results grid

---

## PART 1: shadcn/ui Setup

## 20.1 What is shadcn/ui?

shadcn/ui is NOT a package you install from npm. It's a collection of **copy-paste components** built on:
- **Radix UI** — accessible, unstyled headless primitives
- **Tailwind CSS** — styling
- **Class Variance Authority (cva)** — variant management

When you "install" a component, it copies the source code into YOUR project. You own it. You can modify it freely.

```
Traditional library:     shadcn/ui:
npm install library      npx shadcn@latest add button
↓                        ↓
node_modules/            components/ui/button.tsx  ← YOUR file
(can't modify)           (modify freely)
```

**Why this matters:**
- No version conflicts or breaking updates
- You can read and understand every line
- Customise any component without fighting abstractions
- Bundle only what you use (no tree-shaking worries)

## 20.2 Install shadcn/ui

```bash
npx shadcn@latest init
```

It will ask you questions:

```
✔ Preflight checks passed.
✔ Which color would you like to use as the base color? › Slate
✔ Would you like to use CSS variables for theming? › yes
```

This creates:
- `components.json` — configuration file
- `components/ui/` — where components live
- `lib/utils.ts` — the `cn()` utility for merging Tailwind classes
- Updates `globals.css` with CSS variables for theming
- Updates `tailwind.config.ts` (if needed)

## 20.3 The `cn()` utility

```ts
// lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

`cn()` merges Tailwind classes intelligently:
```ts
cn("px-4 py-2", "px-6")      // → "px-6 py-2" (px-6 wins over px-4)
cn("text-red-500", condition && "text-blue-500") // conditional classes
```

## 20.4 Install components we need

```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add badge
npx shadcn@latest add command
npx shadcn@latest add sheet
npx shadcn@latest add separator
npx shadcn@latest add scroll-area
npx shadcn@latest add dropdown-menu
```

Each command copies a component file into `components/ui/`. You now have:

```
components/
  ui/
    button.tsx
    input.tsx
    card.tsx
    badge.tsx
    command.tsx
    sheet.tsx
    separator.tsx
    scroll-area.tsx
    dropdown-menu.tsx
```

---

## PART 2: The Navbar

## 20.5 Responsive navbar with shadcn

Create `components/Navbar.tsx`:

```tsx
"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";

const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/algorithms", label: "Algorithms" },
  { href: "/blog", label: "Blog" },
  { href: "/about", label: "About" },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-md">
      <div className="max-w-6xl mx-auto flex h-14 items-center px-4">
        {/* Logo */}
        <Link href="/" className="mr-6 flex items-center gap-2">
          <span className="text-lg font-bold">⚡ JavizStudio</span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1 flex-1">
          {NAV_LINKS.map((link) => (
            <Link key={link.href} href={link.href}>
              <Button variant="ghost" size="sm">
                {link.label}
              </Button>
            </Link>
          ))}
        </nav>

        {/* Desktop right side */}
        <div className="hidden md:flex items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <a href="https://github.com/javizstudio" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
          </Button>
        </div>

        {/* Mobile menu trigger */}
        <div className="flex-1 md:hidden" />
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger asChild className="md:hidden">
            <Button variant="ghost" size="icon">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <span className="sr-only">Toggle menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-72">
            <nav className="flex flex-col gap-1 mt-8">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                >
                  <Button variant="ghost" className="w-full justify-start" size="lg">
                    {link.label}
                  </Button>
                </Link>
              ))}
              <Separator className="my-4" />
              <Button variant="outline" className="w-full" asChild>
                <a href="https://github.com/javizstudio" target="_blank" rel="noopener noreferrer">
                  GitHub
                </a>
              </Button>
            </nav>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}
```

**What each shadcn component does:**

| Component | Role |
|-----------|------|
| `Button variant="ghost"` | Nav links — no background, just text with hover state |
| `Button variant="outline"` | Secondary action (GitHub link) |
| `Sheet` | Mobile slide-out panel (replaces custom hamburger menu) |
| `SheetTrigger` | The button that opens the sheet |
| `SheetContent` | The panel content |
| `Separator` | Visual divider line |

**Why `Sheet` instead of a custom mobile menu:**
- Accessible out of the box (focus trap, Escape to close, aria attributes)
- Animated slide-in/out
- Click-outside-to-close
- No custom state management for open/close

## 20.6 Understanding shadcn Button variants

```tsx
<Button variant="default">Primary action</Button>     // solid background
<Button variant="secondary">Secondary</Button>         // muted background
<Button variant="outline">Bordered</Button>            // border only
<Button variant="ghost">Minimal</Button>               // no bg, hover reveals
<Button variant="link">Like a link</Button>            // underlined text
<Button variant="destructive">Delete</Button>          // red/danger

<Button size="default">Normal</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon">🔍</Button>                        // square, for icons
```

## 20.7 Add navbar to the root layout

```tsx
// app/layout.tsx
import Navbar from "@/components/Navbar";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
```

> **`bg-background`** is a CSS variable from shadcn's theme system. It automatically adapts to light/dark mode. Same for `text-foreground`, `border`, `muted`, `accent`, etc.



---

## PART 3: Algorithm Search & Browse Page

## 20.8 The page layout structure

We're building this layout:

```
┌─────────────────────────────────────────────────────┐
│  NAVBAR (from Part 2)                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Page header: "Algorithms"                          │
│  Subtitle + search bar                              │
│                                                     │
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│ FILTERS  │  ALGORITHM CARDS (grid)                  │
│ (sidebar)│                                          │
│          │  ┌──────┐ ┌──────┐ ┌──────┐            │
│ Category │  │Card 1│ │Card 2│ │Card 3│            │
│ □ Sorting│  └──────┘ └──────┘ └──────┘            │
│ □ Search │                                          │
│ □ Graph  │  ┌──────┐ ┌──────┐ ┌──────┐            │
│ □ DP     │  │Card 4│ │Card 5│ │Card 6│            │
│          │  └──────┘ └──────┘ └──────┘            │
│ Difficulty│                                         │
│ □ Easy   │                                          │
│ □ Medium │                                          │
│ □ Hard   │                                          │
│          │                                          │
└──────────┴──────────────────────────────────────────┘
```

## 20.9 Define algorithm data

Create `lib/algorithms-data.ts`:

```ts
export type Algorithm = {
  slug: string;
  name: string;
  category: "sorting" | "searching" | "graph" | "dynamic-programming" | "tree";
  difficulty: "easy" | "medium" | "hard";
  description: string;
  timeComplexity: string;
  spaceComplexity: string;
  tags: string[];
};

export const ALGORITHMS: Algorithm[] = [
  {
    slug: "bubble-sort",
    name: "Bubble Sort",
    category: "sorting",
    difficulty: "easy",
    description: "Repeatedly swap adjacent elements if they're in the wrong order.",
    timeComplexity: "O(n²)",
    spaceComplexity: "O(1)",
    tags: ["comparison", "in-place", "stable"],
  },
  {
    slug: "merge-sort",
    name: "Merge Sort",
    category: "sorting",
    difficulty: "medium",
    description: "Divide the array in half, sort each half, then merge them back together.",
    timeComplexity: "O(n log n)",
    spaceComplexity: "O(n)",
    tags: ["divide-and-conquer", "stable", "recursive"],
  },
  {
    slug: "quick-sort",
    name: "Quick Sort",
    category: "sorting",
    difficulty: "medium",
    description: "Pick a pivot, partition around it, recursively sort the partitions.",
    timeComplexity: "O(n log n)",
    spaceComplexity: "O(log n)",
    tags: ["divide-and-conquer", "in-place", "recursive"],
  },
  {
    slug: "binary-search",
    name: "Binary Search",
    category: "searching",
    difficulty: "easy",
    description: "Halve the search space each step by comparing with the middle element.",
    timeComplexity: "O(log n)",
    spaceComplexity: "O(1)",
    tags: ["sorted-input", "divide-and-conquer"],
  },
  {
    slug: "bfs",
    name: "Breadth-First Search",
    category: "graph",
    difficulty: "medium",
    description: "Explore all neighbours at the current depth before moving deeper.",
    timeComplexity: "O(V + E)",
    spaceComplexity: "O(V)",
    tags: ["queue", "shortest-path", "level-order"],
  },
  {
    slug: "dfs",
    name: "Depth-First Search",
    category: "graph",
    difficulty: "medium",
    description: "Explore as far as possible along each branch before backtracking.",
    timeComplexity: "O(V + E)",
    spaceComplexity: "O(V)",
    tags: ["stack", "recursive", "backtracking"],
  },
  {
    slug: "dijkstra",
    name: "Dijkstra's Algorithm",
    category: "graph",
    difficulty: "hard",
    description: "Find the shortest path from a source to all other nodes in a weighted graph.",
    timeComplexity: "O((V + E) log V)",
    spaceComplexity: "O(V)",
    tags: ["priority-queue", "shortest-path", "greedy"],
  },
  {
    slug: "fibonacci-dp",
    name: "Fibonacci (DP)",
    category: "dynamic-programming",
    difficulty: "easy",
    description: "Compute Fibonacci numbers efficiently using memoization or tabulation.",
    timeComplexity: "O(n)",
    spaceComplexity: "O(n)",
    tags: ["memoization", "tabulation", "overlapping-subproblems"],
  },
  {
    slug: "edit-distance",
    name: "Edit Distance",
    category: "dynamic-programming",
    difficulty: "hard",
    description: "Find the minimum number of operations to transform one string into another.",
    timeComplexity: "O(m × n)",
    spaceComplexity: "O(m × n)",
    tags: ["tabulation", "string", "matrix"],
  },
  {
    slug: "binary-search-tree",
    name: "BST Operations",
    category: "tree",
    difficulty: "medium",
    description: "Insert, search, and delete in a binary search tree.",
    timeComplexity: "O(h)",
    spaceComplexity: "O(n)",
    tags: ["recursive", "ordered", "hierarchical"],
  },
];

export const CATEGORIES = [
  { value: "sorting", label: "Sorting", count: 3 },
  { value: "searching", label: "Searching", count: 1 },
  { value: "graph", label: "Graph", count: 3 },
  { value: "dynamic-programming", label: "Dynamic Programming", count: 2 },
  { value: "tree", label: "Tree", count: 1 },
] as const;

export const DIFFICULTIES = [
  { value: "easy", label: "Easy", color: "bg-green-100 text-green-800" },
  { value: "medium", label: "Medium", color: "bg-yellow-100 text-yellow-800" },
  { value: "hard", label: "Hard", color: "bg-red-100 text-red-800" },
] as const;
```

## 20.10 The search page — full component

Create `app/algorithms/search/page.tsx`:

```tsx
"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ALGORITHMS, CATEGORIES, DIFFICULTIES, type Algorithm } from "@/lib/algorithms-data";

export default function AlgorithmSearchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedDifficulties, setSelectedDifficulties] = useState<string[]>([]);

  // Filter algorithms based on search + filters
  const filteredAlgorithms = useMemo(() => {
    return ALGORITHMS.filter((algo) => {
      // Text search
      const matchesSearch =
        searchQuery === "" ||
        algo.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        algo.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        algo.tags.some((tag) => tag.includes(searchQuery.toLowerCase()));

      // Category filter
      const matchesCategory =
        selectedCategories.length === 0 ||
        selectedCategories.includes(algo.category);

      // Difficulty filter
      const matchesDifficulty =
        selectedDifficulties.length === 0 ||
        selectedDifficulties.includes(algo.difficulty);

      return matchesSearch && matchesCategory && matchesDifficulty;
    });
  }, [searchQuery, selectedCategories, selectedDifficulties]);

  function toggleCategory(category: string) {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  }

  function toggleDifficulty(difficulty: string) {
    setSelectedDifficulties((prev) =>
      prev.includes(difficulty)
        ? prev.filter((d) => d !== difficulty)
        : [...prev, difficulty]
    );
  }

  function clearFilters() {
    setSearchQuery("");
    setSelectedCategories([]);
    setSelectedDifficulties([]);
  }

  const hasActiveFilters =
    searchQuery !== "" || selectedCategories.length > 0 || selectedDifficulties.length > 0;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Algorithms</h1>
        <p className="text-muted-foreground mt-2">
          Browse and search algorithm visualisations. Click any card to see it in action.
        </p>
      </div>

      {/* Search bar */}
      <div className="flex gap-3 mb-8">
        <div className="relative flex-1">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <Input
            placeholder="Search algorithms... (e.g. 'sort', 'graph', 'recursive')"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        {hasActiveFilters && (
          <Button variant="ghost" onClick={clearFilters} className="shrink-0">
            Clear filters
          </Button>
        )}
      </div>

      {/* Main content: sidebar + grid */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar filters */}
        <aside className="w-full lg:w-56 shrink-0">
          <div className="sticky top-20 space-y-6">
            {/* Category filter */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Category</h3>
              <div className="space-y-2">
                {CATEGORIES.map((cat) => (
                  <label
                    key={cat.value}
                    className="flex items-center gap-2 cursor-pointer group"
                  >
                    <input
                      type="checkbox"
                      checked={selectedCategories.includes(cat.value)}
                      onChange={() => toggleCategory(cat.value)}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                      {cat.label}
                    </span>
                    <span className="text-xs text-muted-foreground ml-auto">
                      {cat.count}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <Separator />

            {/* Difficulty filter */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Difficulty</h3>
              <div className="space-y-2">
                {DIFFICULTIES.map((diff) => (
                  <label
                    key={diff.value}
                    className="flex items-center gap-2 cursor-pointer group"
                  >
                    <input
                      type="checkbox"
                      checked={selectedDifficulties.includes(diff.value)}
                      onChange={() => toggleDifficulty(diff.value)}
                      className="rounded border-gray-300"
                    />
                    <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                      {diff.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <Separator />

            {/* Active filter summary */}
            {hasActiveFilters && (
              <div>
                <h3 className="text-sm font-semibold mb-2">Active filters</h3>
                <div className="flex flex-wrap gap-1">
                  {selectedCategories.map((c) => (
                    <Badge key={c} variant="secondary" className="text-xs">
                      {c}
                    </Badge>
                  ))}
                  {selectedDifficulties.map((d) => (
                    <Badge key={d} variant="secondary" className="text-xs">
                      {d}
                    </Badge>
                  ))}
                  {searchQuery && (
                    <Badge variant="secondary" className="text-xs">
                      "{searchQuery}"
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* Results grid */}
        <div className="flex-1">
          {/* Results count */}
          <p className="text-sm text-muted-foreground mb-4">
            {filteredAlgorithms.length} algorithm{filteredAlgorithms.length !== 1 ? "s" : ""} found
          </p>

          {filteredAlgorithms.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p className="text-lg">No algorithms match your filters</p>
              <p className="text-sm mt-2">Try a different search term or clear filters</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredAlgorithms.map((algo) => (
                <AlgorithmCard key={algo.slug} algorithm={algo} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

## 20.11 The algorithm card component

```tsx
function AlgorithmCard({ algorithm }: { algorithm: Algorithm }) {
  const difficultyStyle = {
    easy: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    hard: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  }[algorithm.difficulty];

  return (
    <Link href={`/algorithms/${algorithm.slug}`}>
      <Card className="h-full hover:shadow-md hover:border-primary/50 transition-all duration-200 cursor-pointer group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-base group-hover:text-primary transition-colors">
              {algorithm.name}
            </CardTitle>
            <Badge variant="outline" className={`text-xs shrink-0 ${difficultyStyle}`}>
              {algorithm.difficulty}
            </Badge>
          </div>
          <CardDescription className="text-sm line-clamp-2">
            {algorithm.description}
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-0">
          {/* Complexity info */}
          <div className="flex gap-4 text-xs text-muted-foreground mb-3">
            <span>Time: <code className="font-mono">{algorithm.timeComplexity}</code></span>
            <span>Space: <code className="font-mono">{algorithm.spaceComplexity}</code></span>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-1">
            {algorithm.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs font-normal">
                {tag}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
```

**shadcn Card anatomy:**
- `Card` — the outer container (border + rounded + padding)
- `CardHeader` — title area with spacing
- `CardTitle` — the heading
- `CardDescription` — subtitle/description text
- `CardContent` — main body area
- `CardFooter` — optional bottom section

## 20.12 Command palette — keyboard-driven search (⌘K)

For power users, add a `⌘K` command palette using shadcn's `Command` component:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { ALGORITHMS } from "@/lib/algorithms-data";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  // ⌘K or Ctrl+K to open
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  function handleSelect(slug: string) {
    setOpen(false);
    router.push(`/algorithms/${slug}`);
  }

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search algorithms..." />
      <CommandList>
        <CommandEmpty>No algorithms found.</CommandEmpty>
        <CommandGroup heading="Sorting">
          {ALGORITHMS.filter((a) => a.category === "sorting").map((algo) => (
            <CommandItem key={algo.slug} onSelect={() => handleSelect(algo.slug)}>
              <span>{algo.name}</span>
              <span className="ml-auto text-xs text-muted-foreground">
                {algo.timeComplexity}
              </span>
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandGroup heading="Graph">
          {ALGORITHMS.filter((a) => a.category === "graph").map((algo) => (
            <CommandItem key={algo.slug} onSelect={() => handleSelect(algo.slug)}>
              <span>{algo.name}</span>
              <span className="ml-auto text-xs text-muted-foreground">
                {algo.timeComplexity}
              </span>
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandGroup heading="Dynamic Programming">
          {ALGORITHMS.filter((a) => a.category === "dynamic-programming").map((algo) => (
            <CommandItem key={algo.slug} onSelect={() => handleSelect(algo.slug)}>
              <span>{algo.name}</span>
              <span className="ml-auto text-xs text-muted-foreground">
                {algo.timeComplexity}
              </span>
            </CommandItem>
          ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
```

Add a trigger button in the navbar:

```tsx
// Inside Navbar, add this to the desktop nav area:
<Button
  variant="outline"
  size="sm"
  className="text-muted-foreground w-40 justify-start"
  onClick={() => setCommandOpen(true)}
>
  <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
  <span className="text-xs">Search...</span>
  <kbd className="ml-auto text-xs bg-muted px-1.5 py-0.5 rounded">⌘K</kbd>
</Button>
```

## 20.13 Adding the command palette to the root layout

```tsx
// app/layout.tsx
import Navbar from "@/components/Navbar";
import { CommandPalette } from "@/components/CommandPalette";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        <Navbar />
        <main>{children}</main>
        <CommandPalette />  {/* Always mounted, shown via ⌘K */}
      </body>
    </html>
  );
}
```



---

## PART 4: Theming, Dark Mode, and Tips

## 20.14 Dark mode with shadcn

shadcn uses CSS variables for theming. The variable values change when `dark` class is applied to `<html>`.

Install the theme toggle:

```bash
npx shadcn@latest add dropdown-menu
```

Create `components/ThemeToggle.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type Theme = "light" | "dark" | "system";

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("system");

  useEffect(() => {
    const saved = localStorage.getItem("theme") as Theme | null;
    if (saved) {
      setTheme(saved);
      applyTheme(saved);
    }
  }, []);

  function applyTheme(newTheme: Theme) {
    const root = document.documentElement;
    if (newTheme === "dark") {
      root.classList.add("dark");
    } else if (newTheme === "light") {
      root.classList.remove("dark");
    } else {
      // System preference
      if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        root.classList.add("dark");
      } else {
        root.classList.remove("dark");
      }
    }
  }

  function handleChange(newTheme: Theme) {
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    applyTheme(newTheme);
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          {/* Sun icon */}
          <svg className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="5" /><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
          </svg>
          {/* Moon icon */}
          <svg className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
          </svg>
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => handleChange("light")}>Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleChange("dark")}>Dark</DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleChange("system")}>System</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

Add to the navbar's desktop right side:

```tsx
<div className="hidden md:flex items-center gap-2">
  <ThemeToggle />
  <Button variant="outline" size="sm" asChild>
    <a href="https://github.com/javizstudio">GitHub</a>
  </Button>
</div>
```

## 20.15 shadcn's CSS variable system

In your `globals.css`, shadcn generates variables like:

```css
:root {
  --background: 0 0% 100%;         /* white */
  --foreground: 222.2 84% 4.9%;    /* near-black */
  --card: 0 0% 100%;
  --card-foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --border: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
}

.dark {
  --background: 222.2 84% 4.9%;    /* near-black */
  --foreground: 210 40% 98%;       /* near-white */
  --card: 222.2 84% 4.9%;
  --primary: 210 40% 98%;
  /* ... inverted values */
}
```

These are HSL values (without the `hsl()` wrapper). Tailwind uses them:

```tsx
className="bg-background"       // → uses var(--background)
className="text-foreground"     // → uses var(--foreground)
className="text-muted-foreground" // → uses var(--muted-foreground)
className="border-border"       // → uses var(--border)
className="bg-primary text-primary-foreground" // → button colours
```

**Benefit:** Change ONE variable and the entire app theme updates. No hunting for hardcoded colours.

## 20.16 Common shadcn component patterns

### Loading state on buttons

```tsx
<Button disabled={isLoading}>
  {isLoading && (
    <svg className="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )}
  {isLoading ? "Loading..." : "Submit"}
</Button>
```

### Empty states

```tsx
<div className="flex flex-col items-center justify-center py-12 text-center">
  <svg className="h-12 w-12 text-muted-foreground/50 mb-4">...</svg>
  <h3 className="text-lg font-medium">No results found</h3>
  <p className="text-sm text-muted-foreground mt-1 max-w-sm">
    Try adjusting your search or filters to find what you're looking for.
  </p>
  <Button variant="outline" className="mt-4" onClick={clearFilters}>
    Clear all filters
  </Button>
</div>
```

### Responsive sidebar → bottom sheet on mobile

```tsx
{/* Desktop: sidebar */}
<aside className="hidden lg:block w-56 shrink-0">
  <FilterPanel />
</aside>

{/* Mobile: bottom sheet trigger */}
<div className="lg:hidden mb-4">
  <Sheet>
    <SheetTrigger asChild>
      <Button variant="outline" size="sm">
        <svg className="h-4 w-4 mr-2">...</svg>
        Filters {hasActiveFilters && `(${activeCount})`}
      </Button>
    </SheetTrigger>
    <SheetContent side="bottom" className="h-[70vh]">
      <FilterPanel />
    </SheetContent>
  </Sheet>
</div>
```

## 20.17 Project file structure

```
app/
├── layout.tsx                      ← Root layout with Navbar + CommandPalette
├── page.tsx                        ← Home page
└── algorithms/
    ├── page.tsx                    ← Visualiser (existing)
    └── search/
        └── page.tsx                ← Search/browse page (this chapter)

components/
├── ui/                             ← shadcn components (auto-generated)
│   ├── button.tsx
│   ├── input.tsx
│   ├── card.tsx
│   ├── badge.tsx
│   ├── command.tsx
│   ├── sheet.tsx
│   ├── separator.tsx
│   ├── dropdown-menu.tsx
│   └── scroll-area.tsx
├── Navbar.tsx                      ← Responsive navbar
├── CommandPalette.tsx              ← ⌘K search
└── ThemeToggle.tsx                 ← Light/dark toggle

lib/
├── utils.ts                        ← cn() helper
└── algorithms-data.ts              ← Algorithm metadata
```

## Summary

✅ You installed and configured shadcn/ui (not a library — copy-paste components you own)
✅ You built a responsive navbar with Sheet for mobile and Button variants for navigation
✅ You built a full algorithm search page with text search + category/difficulty filters
✅ You used Card, Badge, Input, Button, Separator — shadcn's bread and butter
✅ You added a ⌘K command palette for keyboard-driven search
✅ You implemented dark mode with CSS variables and a dropdown toggle
✅ You understand shadcn's theming system (`--background`, `--foreground`, `--primary`)

## Key takeaways

**shadcn/ui gives you the code, not a dependency.** You can read, modify, and understand every component. When something doesn't work, you fix it directly — no "override the library's styles" hacks.

**Composition over configuration.** Instead of one mega-component with 50 props, shadcn gives you small building blocks (Card + CardHeader + CardTitle + CardContent) that you compose yourself.

**The search page pattern:** sidebar filters (desktop) + responsive collapse (mobile) + text search + results grid. This works for any browse/search interface — algorithms, blog posts, products, documentation.

**⌘K command palettes** are the pro UX pattern. They let power users navigate instantly without touching the mouse. shadcn's `Command` component (built on cmdk) makes this trivial to implement.

---

→ [Back to Chapter 19: Pro React & Next.js](./19-PRO-REACT-NEXTJS.md)
