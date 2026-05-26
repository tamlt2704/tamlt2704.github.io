# Chapter 7: Finishing Touches

[← Chapter 6: Visualizer](/blog/nextjs-ghpages/chapter-06-visualizer) | [Chapter 8: Dark Mode →](/blog/nextjs-ghpages/chapter-08-dark-mode)

---

## What We're Building

Right now: chapters render, but there's no navigation. We need a modern-looking shell:

```
┌─────────────────────────────────────────────────┐
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │  ← sticky glass navbar
│  ▓  Tam's Blog                Home   Blog    ▓  │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │
├─────────────────────────────────────────────────┤
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ░░░░░░░░  gradient hero  ░░░░░░░░░░░░░░░░░░░  │  ← dark gradient bg
│  ░░░░░░░░  [ glowing btn ]  ░░░░░░░░░░░░░░░░░  │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
├─────────────────────────────────────────────────┤
│  Blog Index                                     │
│  ┌─────────────────────────────────────────┐    │
│  │  ● gradient border on hover             │    │  ← fancy cards
│  │    Series name          12 chapters     │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

Each step: 10-15 lines, save, refresh, see the result.

---

## Step 1: Build the Navbar (Incrementally)

We'll build the navbar in 3 passes. Start ugly, add polish.

### Pass 1: Just the structure

First, get the layout right. No styling yet — just logo left, links right:

```tsx
// 📁 app/layout.tsx — insert before {children}

<nav>
  <div className="mx-auto flex max-w-5xl items-center justify-between">
    <a href="/">Tam&apos;s Blog</a>
    <div className="flex gap-6">
      <a href="/">Home</a>
      <a href="/blog">Blog</a>
    </div>
  </div>
</nav>
```

Save. Refresh. You see text at the top — logo left, links right. Ugly but correct.

### Pass 2: Basic styling

Now add spacing, size, and a bottom line to separate from content:

```
│← px-6 →│                              │← px-6 →│
│         Tam's Blog          Home  Blog          │
──────────────────── border-b ─────────────────────
```

```tsx
// 📁 app/layout.tsx — update the <nav> tag

<nav className="border-b border-gray-800 px-6 py-4">
  {" "}
  {/* border + padding */}
  <div className="mx-auto flex max-w-5xl items-center justify-between">
    <a href="/" className="text-lg font-bold text-white">
      Tam&apos;s Blog
    </a>
    <div className="flex gap-6 text-sm text-gray-400">
      <a href="/">Home</a>
      <a href="/blog">Blog</a>
    </div>
  </div>
</nav>
```

Save. Refresh. Now it looks like a real navbar — dark text, line underneath.

### Pass 3: Make it fancy

Three effects that make it feel premium:

```
┌──────────────────────────────────────────────────┐
│  Problem: when you scroll, navbar disappears     │
│  Fix: sticky top-0 → stays at top               │
│                                                  │
│  Problem: solid bg covers content harshly        │
│  Fix: bg-gray-900/80 → 80% opacity (see-thru)   │
│       backdrop-blur-md → blurs content behind    │
│       = "frosted glass" effect                   │
│                                                  │
│  Problem: links don't react to mouse             │
│  Fix: transition hover:text-white → smooth fade  │
└──────────────────────────────────────────────────┘
```

| Effect        | Classes                       | What happens                               |
| ------------- | ----------------------------- | ------------------------------------------ |
| Stays on top  | `sticky top-0 z-50`           | Navbar follows you when scrolling          |
| See-through   | `bg-gray-900/80`              | `/80` = 80% opacity, content peeks through |
| Frosted glass | `backdrop-blur-md`            | Blurs whatever is behind the navbar        |
| Smooth hover  | `transition hover:text-white` | Links fade from gray to white              |

```tsx
// 📁 app/layout.tsx — final navbar (add sticky, bg opacity, blur, hover)

<nav className="sticky top-0 z-50 border-b border-gray-800 bg-gray-900/80 px-6 py-4 backdrop-blur-md">
  <div className="mx-auto flex max-w-5xl items-center justify-between">
    <a href="/" className="text-lg font-bold text-white">
      Tam&apos;s Blog
    </a>
    <div className="flex gap-6 text-sm">
      <a href="/" className="text-gray-400 transition hover:text-white">
        Home
      </a>
      <a href="/blog" className="text-gray-400 transition hover:text-white">
        Blog
      </a>
    </div>
  </div>
</nav>
```

Save. Refresh. Scroll down — navbar stays. Hover links — they glow white. Look behind the navbar — content blurs like frosted glass.

---

## Step 2: Gradient Hero Home Page

```
┌──────────────────────────────────────────────────┐
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ░░░░░  Learn by Doing  (gradient text)  ░░░░░  │  ← teal→blue gradient
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ░░░░░  description (gray-400)           ░░░░░  │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ░░░░░  [====== Browse Blog → ======]    ░░░░░  │  ← glowing shadow
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
└──────────────────────────────────────────────────┘
```

Modern hero tricks:

- **Gradient text**: a 3-step trick:

```
Step 1: bg-gradient-to-r from-teal-400 to-blue-500
        → creates a teal-to-blue gradient as the BACKGROUND

Step 2: bg-clip-text
        → clips the background to only show BEHIND the text shape

Step 3: text-transparent
        → makes the text color invisible, so the gradient shows through

Result: text that looks "filled" with a gradient
        (normal CSS can't color text with gradients directly)
```

- **Glow button**: `shadow-lg shadow-teal-500/30` = colored shadow underneath
- **Full viewport height**: `min-h-[80vh]` = takes 80% of screen height

```tsx
// 📁 app/page.tsx — replace entire file

import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-[80vh] items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="px-6 text-center">
        {/* Gradient text: bg creates gradient → clip to text shape → hide text color */}
        <h1 className="bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-5xl font-extrabold text-transparent">
          Learn by Doing
        </h1>
        <p className="mt-4 text-lg text-gray-400">
          Interactive tutorials with quizzes, code playgrounds, and visualizers.
        </p>
        <Link
          href="/blog"
          className="mt-8 inline-block rounded-full bg-teal-500 px-8 py-3 font-medium text-white shadow-lg shadow-teal-500/30 transition hover:bg-teal-400 hover:shadow-teal-400/40"
        >
          Browse Blog →
        </Link>
      </div>
    </main>
  );
}
```

Save. Refresh `/`. Dark gradient background, shimmering title, glowing button.

---

## Step 3: Data Helper

Before the blog index, we need a function to read series from `content/`:

```tsx
// 📁 lib/markdown.ts — add at the bottom

export function getAllSeries() {
  const base = path.join(process.cwd(), "content");
  if (!fs.existsSync(base)) return [];
  return fs
    .readdirSync(base, { withFileTypes: true })
    .filter((d) => d.isDirectory()) // each folder = one series
    .map((d) => ({
      slug: d.name, // used in URLs
      chapters: fs
        .readdirSync(path.join(base, d.name))
        .filter((f) => f.endsWith(".md"))
        .sort(), // sorted = chapter order
    }));
}
```

No visible change — this is the data layer.

---

## Step 4: Fancy Blog Index

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  Blog                                            │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │  ●  Nextjs Ghpages                      │    │  ← gradient left border
│  │     24 chapters                          │    │    on hover
│  └──────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────┐    │
│  │  ●  Test                                 │    │
│  │     1 chapter                            │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
└──────────────────────────────────────────────────┘
```

Cards with: dark background, border glow on hover, left accent.

```tsx
// 📁 app/blog/page.tsx — create new file

import Link from "next/link";
import { getAllSeries } from "@/lib/markdown";

export default function BlogIndex() {
  const series = getAllSeries();
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="mb-8 text-3xl font-bold text-white">Blog</h1>
      <div className="space-y-4">
        {series.map((s) => (
          <Link
            key={s.slug}
            href={`/blog/${s.slug}/${s.chapters[0].replace(".md", "")}`}
            className="block rounded-lg border border-gray-800 bg-gray-900 p-5 transition hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10"
          >
            <h2 className="font-semibold text-white">{s.slug.replace(/-/g, " ")}</h2>
            <p className="mt-1 text-sm text-gray-500">{s.chapters.length} chapters</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
```

Save. Refresh `/blog`. Dark cards with teal glow on hover.

---

## Step 5: Extract Navbar Component

```
Before:                          After:
┌─────────────────────┐          ┌─────────────────────┐
│ app/layout.tsx      │          │ app/layout.tsx      │
│  <nav>...10 lines   │    →    │  <Navbar />         │
└─────────────────────┘          └─────────────────────┘
                                 ┌─────────────────────┐
                                 │ app/components/     │
                                 │   Navbar.tsx        │
                                 └─────────────────────┘
```

```tsx
// 📁 app/components/Navbar.tsx — create new file

import Link from "next/link"; // Link = no full page reload

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 border-b border-gray-800 bg-gray-900/80 px-6 py-4 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between">
        <Link href="/" className="text-lg font-bold text-white">
          Tam&apos;s Blog
        </Link>
        <div className="flex gap-6 text-sm">
          <Link href="/" className="text-gray-400 transition hover:text-white">
            Home
          </Link>
          <Link href="/blog" className="text-gray-400 transition hover:text-white">
            Blog
          </Link>
        </div>
      </div>
    </nav>
  );
}
```

Update `app/layout.tsx` — delete the `<nav>` block, add:

```tsx
// 📁 app/layout.tsx — add import at top, replace <nav> with <Navbar />

import { Navbar } from "@/app/components/Navbar";

// inside <body>:
<Navbar />;
{
  children;
}
```

Save. Refresh. Same look — now a reusable component.

---

## Step 6: Dark Body Background

Right now the chapter content pages have a white background that clashes with our dark nav. Fix the body:

```tsx
// 📁 app/layout.tsx — add bg-gray-950 to the <body> className

<body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-950`}>
```

Save. Refresh. Entire site has a consistent dark background.

---

## Step 7: SEO Metadata

```
Browser tab before:  "Tam's blog"         (same for every page)
Browser tab after:   "Ch 05 code playground — nextjs ghpages"
```

```tsx
// 📁 app/blog/[...slug]/page.tsx — add above export default

import type { Metadata } from "next"; // add to imports

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const [series, fileSlug] = slug;
  const title = fileSlug.replace("chapter-", "Ch ").replace(/-/g, " ");
  return { title: `${title} — ${series.replace(/-/g, " ")}` };
}
```

Save. Open any chapter. Browser tab shows unique title.

---

## The Design System

Here's the color palette we used — consistent across the whole site:

| Element    | Colors                              | Effect                |
| ---------- | ----------------------------------- | --------------------- |
| Background | `gray-900`, `gray-950`              | Dark base             |
| Text       | `white`, `gray-400`                 | High/low contrast     |
| Accent     | `teal-400`, `teal-500`              | Links, buttons, glows |
| Borders    | `gray-800`                          | Subtle separation     |
| Hover      | `teal-500/50`, `shadow-teal-500/10` | Glow effect           |
| Glass      | `bg-gray-900/80 backdrop-blur-md`   | Frosted navbar        |

---

## The Pattern

```
1. ASCII    → picture what you're building
2. Code     → 10-15 lines, commented
3. Verify   → save, refresh, see it work
4. Extract  → clean up when it works
```

---

## Commit

```bash
git add .
git commit -m "feat: modern dark UI — glass navbar, gradient hero, glowing cards"
git push
```

## What's Next

Chapter 8 adds dark mode toggle — letting users switch between this dark theme and a light one. Because sometimes you're reading in sunlight.
