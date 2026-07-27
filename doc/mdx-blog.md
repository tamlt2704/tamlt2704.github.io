# MDX — Markdown with React Components

---

## What is MDX?

MDX = Markdown + JSX. You write blog posts in `.mdx` files and can embed React components directly inside them.

```mdx
# My Blog Post

Here's a paragraph of text.

<BubbleSortDemo />

And the explanation continues below the interactive demo.
```

This renders as a normal blog post, but with a live React component in the middle.

---

## Why MDX?

| Feature | Plain Markdown | MDX |
|---------|---------------|-----|
| Headings, lists, code blocks | ✅ | ✅ |
| Images, links | ✅ | ✅ |
| Interactive React components | ❌ | ✅ |
| Import and use your own components | ❌ | ✅ |
| Syntax highlighting with custom themes | Hard | Easy |
| Layout control | Limited | Full |

Perfect for an algorithm visualisation blog — explanations in Markdown, live demos as React components.

---

## Step 1: Install Dependencies

```bash
npm install @next/mdx @mdx-js/mdx @mdx-js/react
```

| Package | What it does |
|---------|-------------|
| `@next/mdx` | Next.js plugin that handles `.mdx` files |
| `@mdx-js/mdx` | The MDX compiler |
| `@mdx-js/react` | Provides components to MDX content |

---

## Step 2: Configure Next.js

Update `next.config.ts`:

```ts
import createMDX from "@next/mdx"

const withMDX = createMDX({})

const nextConfig = {
  pageExtensions: ["ts", "tsx", "md", "mdx"],
}

export default withMDX(nextConfig)
```

**What this does:**
- Tells Next.js to treat `.mdx` files as pages/components
- `pageExtensions` — Next.js will recognise `.mdx` files in the `app/` directory

---

## Step 3: Create an MDX Component File

Create `mdx-components.tsx` in the **project root** (not inside `app/`):

```tsx
import type { MDXComponents } from "mdx/types"

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    ...components,
  }
}
```

This file is required by Next.js. It lets you customise how Markdown elements render (we'll use it later for styling).

---

## Step 4: Write Your First Blog Post

Create `app/blog/bubble-sort/page.mdx`:

```mdx
# Bubble Sort

Bubble sort repeatedly steps through the list, compares adjacent elements,
and swaps them if they are in the wrong order.

## How It Works

1. Compare each pair of adjacent elements
2. If the left is greater than the right, swap them
3. Repeat until no swaps are needed

## Time Complexity

- **Best:** O(n) — already sorted
- **Average:** O(n²)
- **Worst:** O(n²)

## Try It

Click "Sort" to watch bubble sort in action.
```

That's it — visit `/blog/bubble-sort` and you'll see the rendered Markdown.

---

## Step 5: Add a React Component Inside MDX

First, create a component. Create `components/demos/bubble-sort-demo.tsx`:

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export function BubbleSortDemo() {
  const [array, setArray] = useState([38, 27, 43, 3, 9, 82, 10])
  const [running, setRunning] = useState(false)

  // ... your bubble sort logic here (from framer-motion.md)

  return (
    <div className="my-8 rounded-lg border bg-card p-6">
      <div className="flex items-end gap-1">
        {array.map((value, index) => (
          <motion.div
            key={`${index}-${value}`}
            layout
            className="w-10 rounded-t-md bg-primary"
            style={{ height: `${value * 3}px` }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
          />
        ))}
      </div>
      {/* ... controls */}
    </div>
  )
}
```

Now use it in your MDX file:

```mdx
import { BubbleSortDemo } from "@/components/demos/bubble-sort-demo"

# Bubble Sort

Bubble sort repeatedly steps through the list...

## Try It

<BubbleSortDemo />

As you can see, the largest elements "bubble" to the end.
```

**That's the power of MDX** — `import` at the top, use the component anywhere in the content.

---

## Step 6: Style Markdown Elements

Raw Markdown renders unstyled `<h1>`, `<p>`, `<code>` etc. Make them look good by customising `mdx-components.tsx`:

```tsx
import type { MDXComponents } from "mdx/types"

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    h1: ({ children }) => (
      <h1 className="mb-4 mt-8 text-3xl font-bold text-foreground">{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className="mb-3 mt-6 text-2xl font-semibold text-foreground">{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className="mb-2 mt-4 text-xl font-medium text-foreground">{children}</h3>
    ),
    p: ({ children }) => (
      <p className="mb-4 leading-7 text-muted-foreground">{children}</p>
    ),
    ul: ({ children }) => (
      <ul className="mb-4 ml-6 list-disc text-muted-foreground">{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className="mb-4 ml-6 list-decimal text-muted-foreground">{children}</ol>
    ),
    li: ({ children }) => (
      <li className="mb-1">{children}</li>
    ),
    code: ({ children }) => (
      <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm">{children}</code>
    ),
    pre: ({ children }) => (
      <pre className="mb-4 overflow-x-auto rounded-lg bg-muted p-4 font-mono text-sm">
        {children}
      </pre>
    ),
    blockquote: ({ children }) => (
      <blockquote className="mb-4 border-l-4 border-border pl-4 italic text-muted-foreground">
        {children}
      </blockquote>
    ),
    a: ({ href, children }) => (
      <a href={href} className="text-primary underline hover:text-primary/80">
        {children}
      </a>
    ),
    ...components,
  }
}
```

Now all Markdown content across your blog gets consistent styling automatically.

---

## Step 7: Add a Blog Layout

Create `app/blog/[slug]/layout.tsx` to wrap all blog posts with consistent padding and max-width:

Wait — with MDX pages directly in the folder, use a simpler approach. Create `app/blog/layout.tsx`:

```tsx
export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return (
    <article className="mx-auto max-w-3xl px-4 py-12">
      {children}
    </article>
  )
}
```

Every page under `/blog/` now gets centered, readable-width layout.

---

## Step 8: Blog Post with Frontmatter (Metadata)

MDX supports `export` for metadata. At the top of your `.mdx` file:

```mdx
export const metadata = {
  title: "Bubble Sort Visualised",
  description: "Interactive bubble sort animation with step-by-step explanation",
  date: "2026-07-23",
  tags: ["sorting", "beginner"],
}

# Bubble Sort

...
```

Next.js automatically picks up `metadata` exports for `<title>` and `<meta>` tags.

---

## Step 9: Blog Index Page (List All Posts)

Create `app/blog/page.tsx` to list your posts:

```tsx
import Link from "next/link"

const posts = [
  {
    slug: "bubble-sort",
    title: "Bubble Sort Visualised",
    description: "Interactive bubble sort animation with step-by-step explanation",
    date: "2026-07-23",
  },
  {
    slug: "selection-sort",
    title: "Selection Sort Visualised",
    description: "Watch selection sort find minimums",
    date: "2026-07-24",
  },
]

export default function BlogPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="mb-8 text-3xl font-bold text-foreground">Blog</h1>
      <div className="flex flex-col gap-6">
        {posts.map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="group rounded-lg border border-border p-6 transition-colors hover:bg-accent"
          >
            <h2 className="text-xl font-semibold text-foreground group-hover:text-primary">
              {post.title}
            </h2>
            <p className="mt-2 text-muted-foreground">{post.description}</p>
            <time className="mt-2 block text-sm text-muted-foreground">{post.date}</time>
          </Link>
        ))}
      </div>
    </div>
  )
}
```

For now this is a manual list. Later you can auto-generate it by scanning the filesystem.

---

## Project Structure

```
app/
├── blog/
│   ├── page.tsx                    ← Blog index (list of posts)
│   ├── layout.tsx                  ← Shared blog layout (max-width, padding)
│   ├── bubble-sort/
│   │   └── page.mdx               ← Blog post (Markdown + components)
│   └── selection-sort/
│       └── page.mdx
components/
├── demos/
│   ├── bubble-sort-demo.tsx        ← Interactive demo component
│   └── selection-sort-demo.tsx
mdx-components.tsx                  ← Styles for Markdown elements (project root)
next.config.ts                      ← MDX plugin configured
```

---

## How It All Connects

```
User visits /blog/bubble-sort
       ↓
Next.js finds app/blog/bubble-sort/page.mdx
       ↓
MDX compiler turns Markdown → React components
       ↓
mdx-components.tsx styles the HTML elements (h1, p, code, etc.)
       ↓
Blog layout.tsx wraps it in max-width container
       ↓
<BubbleSortDemo /> renders as a live React component inside the post
       ↓
User sees styled text + interactive demo on one page
```

---

## Common Patterns

### Component with a caption

```mdx
<figure className="my-8">
  <BubbleSortDemo />
  <figcaption className="mt-2 text-center text-sm text-muted-foreground">
    Fig 1: Bubble sort comparing adjacent elements
  </figcaption>
</figure>
```

### Callout / info box

```mdx
<div className="my-4 rounded-lg border-l-4 border-yellow-400 bg-yellow-50 p-4 dark:bg-yellow-950">
  **Note:** Bubble sort is O(n²) — don't use it for large datasets in production.
</div>
```

### Show/hide explanation

```mdx
import { Details } from "@/components/ui/details"

<Details summary="Click to see the pseudocode">
```
for i from n-1 to 0:
  for j from 0 to i-1:
    if arr[j] > arr[j+1]:
      swap(arr[j], arr[j+1])
```
</Details>
```

---

## Alternatives (If MDX Doesn't Fit)

| Approach | Pros | Cons |
|----------|------|------|
| **MDX (this guide)** | Simple, fast, components inside Markdown | Posts are files in your repo |
| **Contentlayer** | Type-safe, auto-generates blog index | Extra setup, may be unmaintained |
| **CMS (Sanity, Notion)** | Edit from browser, non-devs can write | More complex, API calls |
| **Remote MDX** | MDX stored anywhere (CMS, DB) | Harder to embed custom components |

For a personal dev blog about algorithms, MDX files in the repo is the simplest and fastest approach.
