# Chapter 7: Finishing Touches

[← Chapter 6: Visualizer](/blog/nextjs-ghpages/chapter-06-visualizer) | [Chapter 8: Dark Mode →](/blog/nextjs-ghpages/chapter-08-dark-mode)

---

## The Big Picture

```
┌─────────────────────────────────────────────────┐
│  [Logo]   Home   Blog                    Navbar │
├─────────────────────────────────────────────────┤
│   Home (/)         → hero + CTA                 │
│   Blog (/blog)     → list all series            │
│   Chapter (/blog/series/ch-01) → content        │
└─────────────────────────────────────────────────┘
```

We'll build it piece by piece. Each step: 5-10 lines, then refresh.

## Step 1: Inline Navbar

```
┌──────────────────────────────────────────────────┐
│  📘 Tam's Blog                    Home    Blog   │
├──────────────────────────────────────────────────┤
│                                                  │
│            (existing page content)               │
│                                                  │
└──────────────────────────────────────────────────┘
```

A navbar needs three things:

1. **A bottom border** — separates nav from content visually
2. **Padding** — breathing room so text doesn't touch edges
3. **Two sides** — logo on the left, links on the right

```
│←─ px ─→│                              │←─ px ─→│
│         Logo              Home  Blog            │
│←─────────────── max-width ──────────────────────→│
─────────────────── border-b ──────────────────────
```

In Tailwind, these map directly to class names:

| Concept            | Class                  | What it does                            |
| ------------------ | ---------------------- | --------------------------------------- |
| Bottom border      | `border-b`             | 1px line under the nav                  |
| Horizontal padding | `px-6`                 | Space on left/right                     |
| Vertical padding   | `py-3`                 | Space on top/bottom                     |
| Centered container | `mx-auto max-w-5xl`    | Content doesn't stretch on wide screens |
| Left/right split   | `flex justify-between` | Logo left, links right                  |
| Vertical centering | `items-center`         | Aligns logo and links on same baseline  |

Add a `<nav>` inside the `<body>` of `app/layout.tsx`, right before `{children}`:

```tsx
// 📁 app/layout.tsx — add the <nav> block before {children}

<body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
  {/* ─── Navbar ─── */}
  <nav className="border-b px-6 py-3">
    {" "}
    {/* border-b = bottom line, px/py = padding */}
    <div className="mx-auto flex max-w-5xl items-center justify-between">
      {" "}
      {/* centered, logo↔links */}
      <a href="/" className="text-lg font-bold">
        📘 Tam&apos;s Blog
      </a>{" "}
      {/* left side: logo */}
      <div className="flex gap-6 text-sm">
        {" "}
        {/* right side: links with spacing */}
        <a href="/">Home</a>
        <a href="/blog">Blog</a>
      </div>
    </div>
  </nav>
  {children}
</body>
```

Refresh. Navbar on every page.

## Step 2: Home Page Hero

```
┌──────────────────────────────────────────────────┐
│  📘 Tam's Blog                    Home    Blog   │
├──────────────────────────────────────────────────┤
│                                                  │
│              Learn by Doing                      │
│                                                  │
│     Interactive tutorials with quizzes,          │
│     code playgrounds, and visualizers.           │
│                                                  │
│            [ Browse Blog → ]                     │
│                                                  │
└──────────────────────────────────────────────────┘
```

Replace the content of `app/page.tsx`:

```tsx
// 📁 app/page.tsx — replace entire file

import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-24 text-center">
      {" "}
      {/* centered, big top padding */}
      <h1 className="text-4xl font-bold">Learn by Doing</h1>
      <p className="mt-4 text-lg text-gray-600">
        {" "}
        {/* mt-4 = margin top for spacing */}
        Interactive tutorials with quizzes, code playgrounds, and visualizers.
      </p>
      {/* Link = Next.js client-side navigation (no full page reload) */}
      <Link href="/blog" className="mt-8 inline-block rounded-lg bg-teal-600 px-6 py-3 text-white">
        Browse Blog →
      </Link>
    </main>
  );
}
```

Refresh `/`. Hero with a button.

## Step 3: getAllSeries Helper

Add to `lib/markdown.ts`:

```tsx
// 📁 lib/markdown.ts — add this function at the bottom

export function getAllSeries() {
  const base = path.join(process.cwd(), "content");
  if (!fs.existsSync(base)) return [];
  return fs
    .readdirSync(base, { withFileTypes: true })
    .filter((d) => d.isDirectory()) // each folder = one series
    .map((d) => ({
      slug: d.name, // folder name becomes the URL segment
      chapters: fs
        .readdirSync(path.join(base, d.name))
        .filter((f) => f.endsWith(".md"))
        .sort(), // alphabetical = chapter order
    }));
}
```

No visible change yet — this is the data layer.

## Step 4: Blog Index Page

```
┌──────────────────────────────────────────────────┐
│  📘 Tam's Blog                    Home    Blog   │
├──────────────────────────────────────────────────┤
│                                                  │
│  Blog                                            │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │  Nextjs Ghpages              24 chapters │    │
│  └──────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────┐    │
│  │  Test                         1 chapter  │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
└──────────────────────────────────────────────────┘
```

Create `app/blog/page.tsx`:

```tsx
// 📁 app/blog/page.tsx — create this new file

import Link from "next/link";
import { getAllSeries } from "@/lib/markdown"; // our helper from Step 3

export default function BlogIndex() {
  const series = getAllSeries(); // reads content/ folders at build time
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="mb-8 text-3xl font-bold">Blog</h1>
      <div className="space-y-4">
        {" "}
        {/* vertical gap between cards */}
        {series.map((s) => (
          <Link
            key={s.slug}
            href={`/blog/${s.slug}/${s.chapters[0].replace(".md", "")}`}
            className="block rounded-lg border p-5 hover:border-teal-400"
          >
            {" "}
            {/* card style */}
            <h2 className="font-semibold">{s.slug.replace(/-/g, " ")}</h2>{" "}
            {/* "nextjs-ghpages" → "nextjs ghpages" */}
            <p className="text-sm text-gray-500">{s.chapters.length} chapters</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
```

Refresh `/blog`. Series cards. Click one — lands on chapter 0.

## Step 5: Extract Navbar Component

```
Before:                          After:
app/layout.tsx                   app/layout.tsx
├── <nav>...</nav> (inline)      ├── <Navbar />
│   (10 lines of HTML)           │
└── {children}                   app/components/Navbar.tsx
                                 └── <nav>...</nav> (same code)
```

Create `app/components/Navbar.tsx`. Move the `<nav>` from layout here:

```tsx
// 📁 app/components/Navbar.tsx — create this new file

import Link from "next/link"; // Link = client-side nav (no page reload)

export function Navbar() {
  return (
    <nav className="border-b px-6 py-3">
      <div className="mx-auto flex max-w-5xl items-center justify-between">
        <Link href="/" className="text-lg font-bold">
          📘 Tam&apos;s Blog
        </Link>
        <div className="flex gap-6 text-sm">
          <Link href="/" className="text-gray-600 hover:text-gray-900">
            Home
          </Link>
          <Link href="/blog" className="text-gray-600 hover:text-gray-900">
            Blog
          </Link>
        </div>
      </div>
    </nav>
  );
}
```

## Step 6: Use It in Layout

Replace the inline `<nav>` in `app/layout.tsx` with:

```tsx
// 📁 app/layout.tsx — add import at top, replace <nav>...</nav> with <Navbar />

import { Navbar } from "@/app/components/Navbar";

// the body becomes:
<body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
  <Navbar />
  {children}
</body>;
```

Same result. `<a>` became `<Link>` (no full page reload on navigation).

## Step 7: SEO Metadata

```
Browser tab before:  "Tam's blog"         (same for every page)
Browser tab after:   "Ch 05 Code Playground — nextjs ghpages"
```

Add to `app/blog/[...slug]/page.tsx`:

```tsx
// 📁 app/blog/[...slug]/page.tsx — add this function above the default export

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const [series, fileSlug] = slug;
  // "chapter-05-code-playground" → "Ch 05 code playground"
  const title = fileSlug.replace("chapter-", "Ch ").replace(/-/g, " ");
  return { title: `${title} — ${series.replace(/-/g, " ")}` };
}
```

Each chapter gets a unique browser tab title.

## The Pattern

```
1. Inline it       → see it immediately
2. Verify          → refresh, click around
3. Extract         → move to component
4. Verify again    → same result, cleaner code
```

Make it work, make it right, make it fast.

## Final Structure

```
app/
├── layout.tsx              ← Navbar + wrapper
├── page.tsx                ← Home hero
├── components/Navbar.tsx   ← shared nav
└── blog/
    ├── page.tsx            ← Blog index
    ├── [...slug]/page.tsx  ← Chapter renderer + SEO
    └── components/         ← Quiz, CodePlayground, StepVisualizer
```

---

## Commit Your Progress

```bash
git add .
git commit -m "feat: add navbar, home page, blog index, and SEO"
git push
```

## What's Next

The site works but looks plain. Chapter 8 adds dark mode — because developers read at night, and white backgrounds at 2am are an act of violence.
