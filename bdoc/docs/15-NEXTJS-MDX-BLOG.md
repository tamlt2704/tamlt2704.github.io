# Chapter 15: Next.js MDX Blog — Markdown with Embedded React Components

## What you'll learn

- How to build a blog with MDX (Markdown + JSX) in Next.js
- How to embed interactive React components inside markdown posts
- UI/UX layout patterns for blog sites (header, sidebar, content area, responsive design)
- How to style markdown content with Tailwind Typography
- How to deploy a static Next.js site to GitHub Pages
- How to handle frontmatter (title, date, tags) in MDX files

## 15.1 What is MDX?

MDX = Markdown + JSX. You write normal markdown, but you can also drop React components directly into it:

```mdx
# My Blog Post

This is regular markdown with **bold** and *italic* text.

Here's a list:
- Item one
- Item two

And here's an interactive React component right inside the post:

<InteractiveChart data={[5, 10, 15, 20]} />

Back to regular markdown. The component renders inline with the text.
```

This is powerful for technical blogs — you can embed:
- Live code demos
- Interactive visualisations (like your D3 charts)
- Collapsible sections
- Custom callout boxes
- Anything React can render

> **MDX vs plain Markdown:** Regular markdown produces static HTML. MDX produces React components — meaning your content can have state, effects, event handlers, and interactivity. The tradeoff: MDX requires a build step (can't be rendered by GitHub's markdown renderer).

## 15.2 Project architecture

Here's what we're building:

```
my-blog/
├── app/
│   ├── layout.tsx              ← Root layout (header, footer)
│   ├── page.tsx                ← Home/blog index
│   └── blog/
│       └── [slug]/
│           └── page.tsx        ← Dynamic route for each post
├── content/
│   ├── hello-world.mdx        ← Blog posts as MDX files
│   ├── building-with-d3.mdx
│   └── deploy-guide.mdx
├── components/
│   ├── BlogLayout.tsx          ← Blog post wrapper (prose styling)
│   ├── Header.tsx              ← Site navigation
│   ├── PostCard.tsx            ← Card for blog index
│   └── mdx/                   ← Custom components available in MDX
│       ├── Callout.tsx
│       ├── CodeBlock.tsx
│       └── InteractiveDemo.tsx
├── mdx-components.tsx          ← Global MDX component mapping
├── next.config.ts              ← MDX + static export config
└── package.json
```

---

## 15.3 Install dependencies

Starting from your existing Next.js project:

```bash
npm install @next/mdx @mdx-js/loader @mdx-js/react @types/mdx
npm install remark-gfm rehype-slug rehype-autolink-headings
npm install gray-matter
```

| Package | Purpose |
|---------|---------|
| `@next/mdx` | Next.js MDX integration |
| `@mdx-js/loader` | Webpack loader for .mdx files |
| `@mdx-js/react` | React context for MDX components |
| `@types/mdx` | TypeScript types |
| `remark-gfm` | GitHub Flavoured Markdown (tables, strikethrough, task lists) |
| `rehype-slug` | Adds `id` attributes to headings (for anchor links) |
| `rehype-autolink-headings` | Adds clickable links to headings |
| `gray-matter` | Parses YAML frontmatter from MDX files |

## 15.4 Configure Next.js for MDX

Replace `next.config.ts` with `next.config.mjs` (MDX plugins require ESM):

```js
// next.config.mjs
import createMDX from "@next/mdx";
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow .mdx files as pages
  pageExtensions: ["js", "jsx", "md", "mdx", "ts", "tsx"],

  // Static export for GitHub Pages
  output: "export",

  // GitHub Pages serves from a subpath (your repo name)
  // Remove this line if using a custom domain or username.github.io
  basePath: "/your-repo-name",

  // Disable image optimisation (not available in static export)
  images: {
    unoptimized: true,
  },
};

const withMDX = createMDX({
  options: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [rehypeSlug, rehypeAutolinkHeadings],
  },
});

export default withMDX(nextConfig);
```

> **Key config explained:**
> - `output: "export"` — generates static HTML files (no Node.js server needed)
> - `basePath` — required if your GitHub Pages URL is `username.github.io/repo-name`
> - `images.unoptimized` — Next.js Image Optimization requires a server; static export can't use it
> - `pageExtensions` — tells Next.js to treat `.mdx` files as pages

## 15.5 Create `mdx-components.tsx`

This file is **required** by `@next/mdx`. It defines how HTML elements (generated from markdown) are rendered. Create it at the project root:

```tsx
// mdx-components.tsx
import type { MDXComponents } from "mdx/types";

export function useMDXComponents(): MDXComponents {
  return {
    // Override default elements with styled versions
    h1: ({ children }) => (
      <h1 className="text-4xl font-bold mt-8 mb-4">{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-3xl font-semibold mt-8 mb-3">{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-2xl font-semibold mt-6 mb-2">{children}</h3>
    ),
    p: ({ children }) => (
      <p className="text-gray-700 leading-relaxed mb-4">{children}</p>
    ),
    a: ({ href, children }) => (
      <a href={href} className="text-blue-600 hover:underline">
        {children}
      </a>
    ),
    code: ({ children }) => (
      <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">
        {children}
      </code>
    ),
    pre: ({ children }) => (
      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4">
        {children}
      </pre>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4">
        {children}
      </blockquote>
    ),
    ul: ({ children }) => (
      <ul className="list-disc pl-6 mb-4 space-y-1">{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal pl-6 mb-4 space-y-1">{children}</ol>
    ),
    table: ({ children }) => (
      <div className="overflow-x-auto mb-4">
        <table className="min-w-full border-collapse border border-gray-200">
          {children}
        </table>
      </div>
    ),
    th: ({ children }) => (
      <th className="border border-gray-200 px-4 py-2 bg-gray-50 font-semibold text-left">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="border border-gray-200 px-4 py-2">{children}</td>
    ),
  };
}
```

> **Why not use Tailwind Typography (`prose` classes)?** You can! The `@tailwindcss/typography` plugin gives you `prose` classes that style all markdown elements at once. We're using custom components here because it gives you per-element control AND lets you use React features (onClick handlers, state, etc.) on any element. We'll show the `prose` approach too in section 15.10.



---

## PART 2: UI/UX Layout Patterns

## 15.6 Root layout — the shell of your blog

The root layout wraps every page. It contains your header, footer, and overall page structure.

`app/layout.tsx`:

```tsx
import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";

export const metadata: Metadata = {
  title: "My Dev Blog",
  description: "Tutorials and thoughts on web development",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-white text-gray-900">
        <Header />
        <main className="flex-1">{children}</main>
        <footer className="border-t py-8 text-center text-sm text-gray-500">
          © 2026 My Blog. Built with Next.js and MDX.
        </footer>
      </body>
    </html>
  );
}
```

## 15.7 Header component — navigation

`components/Header.tsx`:

```tsx
import Link from "next/link";

export default function Header() {
  return (
    <header className="border-b sticky top-0 bg-white/80 backdrop-blur-sm z-50">
      <nav className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo / site name */}
        <Link href="/" className="text-xl font-bold hover:text-blue-600 transition-colors">
          DevBlog
        </Link>

        {/* Navigation links */}
        <div className="flex gap-6 text-sm">
          <Link href="/" className="hover:text-blue-600 transition-colors">
            Home
          </Link>
          <Link href="/blog" className="hover:text-blue-600 transition-colors">
            Blog
          </Link>
          <Link href="/about" className="hover:text-blue-600 transition-colors">
            About
          </Link>
          <a
            href="https://github.com/yourusername"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-blue-600 transition-colors"
          >
            GitHub
          </a>
        </div>
      </nav>
    </header>
  );
}
```

**Layout decisions explained:**
- `sticky top-0` — header stays visible while scrolling (important for long blog posts)
- `backdrop-blur-sm` — semi-transparent with blur (modern glass effect)
- `max-w-4xl mx-auto` — content doesn't stretch too wide on large screens (readability)
- `z-50` — sits above other content

## 15.8 Blog index page — card grid layout

`app/page.tsx` (or `app/blog/page.tsx`):

```tsx
import Link from "next/link";
import { getAllPosts } from "@/lib/posts";
import PostCard from "@/components/PostCard";

export default function HomePage() {
  const posts = getAllPosts();

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Hero section */}
      <section className="mb-12">
        <h1 className="text-4xl font-bold mb-4">Welcome to DevBlog</h1>
        <p className="text-lg text-gray-600 max-w-2xl">
          Tutorials on Next.js, React, D3.js, and web development.
          Interactive examples you can play with.
        </p>
      </section>

      {/* Posts grid */}
      <section>
        <h2 className="text-2xl font-semibold mb-6">Latest Posts</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {posts.map((post) => (
            <PostCard key={post.slug} post={post} />
          ))}
        </div>
      </section>
    </div>
  );
}
```

`components/PostCard.tsx`:

```tsx
import Link from "next/link";

type Post = {
  slug: string;
  title: string;
  date: string;
  description: string;
  tags?: string[];
};

export default function PostCard({ post }: { post: Post }) {
  return (
    <Link href={`/blog/${post.slug}`}>
      <article className="border rounded-lg p-6 hover:shadow-md transition-shadow h-full flex flex-col">
        {/* Tags */}
        {post.tags && (
          <div className="flex gap-2 mb-3">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Title */}
        <h3 className="text-lg font-semibold mb-2 group-hover:text-blue-600">
          {post.title}
        </h3>

        {/* Description */}
        <p className="text-gray-600 text-sm flex-1">{post.description}</p>

        {/* Date */}
        <time className="text-xs text-gray-400 mt-4 block">
          {new Date(post.date).toLocaleDateString("en-GB", {
            day: "numeric",
            month: "long",
            year: "numeric",
          })}
        </time>
      </article>
    </Link>
  );
}
```

**UX patterns used:**
- `grid md:grid-cols-2` — single column on mobile, two columns on desktop
- `hover:shadow-md` — cards lift on hover (affordance: "this is clickable")
- `flex flex-col` + `flex-1` on description — cards have equal height regardless of content
- Tags as coloured pills — scannable at a glance

## 15.9 Blog post layout — the reading experience

The single most important UX decision for a blog: **line width**. Lines longer than ~70 characters are hard to read. Use `max-w-prose` (65ch) or `max-w-3xl`.

`app/blog/[slug]/layout.tsx`:

```tsx
export default function BlogPostLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <article className="max-w-3xl mx-auto px-4 py-12">
      {children}
    </article>
  );
}
```

For a layout WITH a sidebar (table of contents):

```tsx
export default function BlogPostLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="max-w-6xl mx-auto px-4 py-12 flex gap-12">
      {/* Main content */}
      <article className="flex-1 min-w-0 max-w-3xl">
        {children}
      </article>

      {/* Sidebar — table of contents (desktop only) */}
      <aside className="hidden lg:block w-64 shrink-0">
        <div className="sticky top-24">
          <h4 className="text-sm font-semibold text-gray-500 uppercase mb-4">
            On this page
          </h4>
          {/* TOC populated by rehype-slug + client JS */}
          <nav id="toc" className="text-sm space-y-2 text-gray-600">
            {/* Links populated at runtime or build time */}
          </nav>
        </div>
      </aside>
    </div>
  );
}
```

**Key decisions:**
- `max-w-3xl` on article — optimal reading width
- `min-w-0` — prevents flex overflow on long code blocks
- `hidden lg:block` on sidebar — only shows on large screens (no cramping on mobile)
- `sticky top-24` on TOC — stays visible while scrolling the post



---

## PART 3: MDX Content and Embedded Components

## 15.10 Alternative: Tailwind Typography (`prose`)

Instead of custom-styling every element in `mdx-components.tsx`, use the `prose` class:

```bash
npm install @tailwindcss/typography
```

Add to your Tailwind CSS (v4 — import in `globals.css`):

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

Then your layout becomes:

```tsx
<article className="prose prose-lg prose-blue max-w-3xl mx-auto">
  {children}
</article>
```

The `prose` class automatically styles all markdown HTML elements beautifully. You can still override specific elements in `mdx-components.tsx` — they take precedence.

| Approach | Pros | Cons |
|----------|------|------|
| Custom `mdx-components.tsx` | Full control, React features on any element | More code to write |
| `prose` classes | One class does everything, well-designed defaults | Less per-element control |
| Both (recommended) | `prose` for base, custom components for interactive elements | Slight redundancy |

## 15.11 Writing an MDX blog post

Create `content/hello-world.mdx`:

```mdx
export const metadata = {
  title: "Hello World — My First MDX Post",
  date: "2026-08-01",
  description: "Learn how this blog is built with Next.js and MDX.",
  tags: ["nextjs", "mdx", "tutorial"],
};

# Hello World

Welcome to my blog! This post is written in **MDX** — that means I can
mix regular markdown with React components.

## Why MDX?

Regular markdown is great for text. But sometimes you want to show
something interactive:

<Callout type="info">
  This is a custom callout component. It renders as a styled box with
  an icon. You can't do this in plain markdown!
</Callout>

## An embedded chart

Here's a D3 bar chart rendered right inside this blog post:

<BarChart data={[12, 19, 3, 5, 2, 14]} />

## Code example

```java
public void bubbleSort(int[] arr) {
  for (int i = 0; i < arr.length - 1; i++) {
    for (int j = 0; j < arr.length - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        int temp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = temp;
      }
    }
  }
}
\```

## Conclusion

MDX lets you build rich, interactive blog posts while keeping the
simplicity of markdown for regular content.
```

> **Notice:** The `export const metadata` at the top is how we do frontmatter in MDX without extra plugins. It's a regular JavaScript export that Next.js can import alongside the content.

## 15.12 Custom MDX components — Callout

`components/mdx/Callout.tsx`:

```tsx
type CalloutProps = {
  type?: "info" | "warning" | "tip" | "danger";
  children: React.ReactNode;
};

const STYLES = {
  info: "bg-blue-50 border-blue-500 text-blue-800",
  warning: "bg-yellow-50 border-yellow-500 text-yellow-800",
  tip: "bg-green-50 border-green-500 text-green-800",
  danger: "bg-red-50 border-red-500 text-red-800",
};

const ICONS = {
  info: "ℹ️",
  warning: "⚠️",
  tip: "💡",
  danger: "🚨",
};

export default function Callout({ type = "info", children }: CalloutProps) {
  return (
    <div className={`border-l-4 p-4 rounded-r-lg my-6 ${STYLES[type]}`}>
      <div className="flex gap-2">
        <span className="text-lg">{ICONS[type]}</span>
        <div className="flex-1">{children}</div>
      </div>
    </div>
  );
}
```

## 15.13 Custom MDX components — Interactive demo

`components/mdx/InteractiveDemo.tsx`:

```tsx
"use client";

import { useState } from "react";

type InteractiveDemoProps = {
  initialValue?: number;
};

export default function InteractiveDemo({ initialValue = 0 }: InteractiveDemoProps) {
  const [count, setCount] = useState(initialValue);

  return (
    <div className="border rounded-lg p-6 my-6 bg-gray-50">
      <p className="text-sm text-gray-500 mb-3">Interactive Component</p>
      <div className="flex items-center gap-4">
        <button
          onClick={() => setCount((c) => c - 1)}
          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
        >
          -
        </button>
        <span className="text-2xl font-bold">{count}</span>
        <button
          onClick={() => setCount((c) => c + 1)}
          className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
        >
          +
        </button>
      </div>
    </div>
  );
}
```

## 15.14 Register components globally

Update `mdx-components.tsx` to include your custom components:

```tsx
import type { MDXComponents } from "mdx/types";
import Callout from "@/components/mdx/Callout";
import InteractiveDemo from "@/components/mdx/InteractiveDemo";
import BarChart from "@/app/algorithms/components/BarChart";

export function useMDXComponents(): MDXComponents {
  return {
    // Custom components available in all MDX files
    Callout,
    InteractiveDemo,
    BarChart,

    // Styled HTML elements (same as before)
    h1: ({ children }) => (
      <h1 className="text-4xl font-bold mt-8 mb-4">{children}</h1>
    ),
    // ... rest of element overrides
  };
}
```

Now `<Callout>`, `<InteractiveDemo>`, and `<BarChart>` are available in ANY MDX file without importing.

## 15.15 Dynamic routing — loading posts by slug

`lib/posts.ts` — utility to read all MDX posts:

```ts
import fs from "fs";
import path from "path";

export type PostMeta = {
  slug: string;
  title: string;
  date: string;
  description: string;
  tags?: string[];
};

const CONTENT_DIR = path.join(process.cwd(), "content");

export function getAllPosts(): PostMeta[] {
  const files = fs.readdirSync(CONTENT_DIR).filter((f) => f.endsWith(".mdx"));

  const posts: PostMeta[] = [];

  for (const file of files) {
    const slug = file.replace(/\.mdx$/, "");
    // We'll import metadata at build time
    // For now, use a synchronous approach with dynamic import workaround
    posts.push({
      slug,
      title: slug.replace(/-/g, " "),
      date: "2026-01-01",
      description: "",
    });
  }

  // Sort by date descending
  return posts.sort((a, b) => (a.date > b.date ? -1 : 1));
}

export function getPostSlugs(): string[] {
  return fs
    .readdirSync(CONTENT_DIR)
    .filter((f) => f.endsWith(".mdx"))
    .map((f) => f.replace(/\.mdx$/, ""));
}
```

`app/blog/[slug]/page.tsx` — the dynamic page:

```tsx
import { getPostSlugs } from "@/lib/posts";

type PageProps = {
  params: Promise<{ slug: string }>;
};

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  const { default: Post, metadata } = await import(`@/content/${slug}.mdx`);

  return (
    <div>
      {/* Post header */}
      <header className="mb-8 pb-8 border-b">
        <h1 className="text-4xl font-bold mb-3">{metadata?.title || slug}</h1>
        {metadata?.date && (
          <time className="text-gray-500 text-sm">
            {new Date(metadata.date).toLocaleDateString("en-GB", {
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </time>
        )}
        {metadata?.tags && (
          <div className="flex gap-2 mt-3">
            {metadata.tags.map((tag: string) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </header>

      {/* MDX content */}
      <Post />
    </div>
  );
}

// Tell Next.js which slugs to pre-render at build time
export function generateStaticParams() {
  return getPostSlugs().map((slug) => ({ slug }));
}

// 404 for unknown slugs
export const dynamicParams = false;
```

> **How this works:**
> 1. `generateStaticParams()` returns all valid slugs at build time
> 2. Next.js pre-renders a page for each slug
> 3. `await import(\`@/content/${slug}.mdx\`)` loads the MDX file as a React component
> 4. The exported `metadata` object is available alongside the component
> 5. `dynamicParams = false` means unknown slugs return 404 (important for static export)



---

## PART 4: Responsive Design and GitHub Pages Deployment

## 15.16 Responsive layout patterns

### Mobile-first breakpoints

Tailwind uses mobile-first breakpoints. Write styles for mobile, then override for larger screens:

```tsx
<div className="
  px-4            /* mobile: small padding */
  md:px-8         /* tablet: more padding */
  lg:px-0         /* desktop: no padding (container handles it) */
  max-w-4xl mx-auto
">
```

### Common blog responsive patterns

```tsx
{/* Hero: stack on mobile, side-by-side on desktop */}
<section className="flex flex-col md:flex-row gap-8 items-center">
  <div className="flex-1">
    <h1>Title</h1>
    <p>Description</p>
  </div>
  <div className="w-full md:w-80">
    <img src="/hero.png" alt="hero" />
  </div>
</section>

{/* Post grid: 1 col → 2 col → 3 col */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {posts.map(post => <PostCard key={post.slug} post={post} />)}
</div>

{/* Sidebar: below content on mobile, beside on desktop */}
<div className="flex flex-col lg:flex-row gap-8">
  <main className="flex-1">{children}</main>
  <aside className="lg:w-64 order-first lg:order-last">
    {/* TOC, related posts, etc. */}
  </aside>
</div>
```

### Typography responsive scaling

```tsx
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
  Blog Post Title
</h1>
<p className="text-base md:text-lg leading-relaxed">
  Body text that scales up slightly on larger screens.
</p>
```

## 15.17 Dark mode support

Add dark mode to your blog with Tailwind's `dark:` variant:

```tsx
// app/layout.tsx
<html lang="en" className="dark"> {/* or toggle via JS */}
  <body className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
```

Update components:

```tsx
// PostCard with dark mode
<article className="
  border rounded-lg p-6
  hover:shadow-md dark:hover:shadow-gray-800
  bg-white dark:bg-gray-800
  border-gray-200 dark:border-gray-700
">
```

Update `mdx-components.tsx`:

```tsx
code: ({ children }) => (
  <code className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm font-mono">
    {children}
  </code>
),
blockquote: ({ children }) => (
  <blockquote className="border-l-4 border-blue-500 dark:border-blue-400 pl-4 italic text-gray-600 dark:text-gray-400">
    {children}
  </blockquote>
),
```

## 15.18 Deploy to GitHub Pages

### Step 1: Update `next.config.mjs`

```js
const nextConfig = {
  output: "export",
  // For username.github.io repos, basePath is empty ("")
  // For project repos (username.github.io/repo-name), set:
  basePath: process.env.NODE_ENV === "production" ? "/your-repo-name" : "",
  images: { unoptimized: true },
  trailingSlash: true, // GitHub Pages needs this for clean URLs
};
```

> **`trailingSlash: true`** — changes `/blog/hello` to `/blog/hello/index.html`. Without this, refreshing a page on GitHub Pages returns 404 because there's no server to rewrite URLs.

### Step 2: Create GitHub Actions workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - run: npm ci
      - run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./out

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Step 3: Enable GitHub Pages in repo settings

1. Go to your repo → Settings → Pages
2. Source: **GitHub Actions** (not "Deploy from a branch")
3. Push to `main` — the action runs automatically

### Step 4: Add a `.nojekyll` file

Create an empty `.nojekyll` file in your `public/` directory. This tells GitHub Pages not to process your files with Jekyll (which would ignore folders starting with `_`, like `_next`):

```bash
touch public/.nojekyll
```

### Step 5: Update `package.json` scripts

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  }
}
```

`next build` with `output: "export"` automatically produces the `out/` directory.

## 15.19 Handling asset paths on GitHub Pages

When using `basePath`, all internal links and images automatically use the prefix. But for images in MDX content, use Next.js `<Image>` or relative paths:

```mdx
{/* This works — basePath is automatically applied */}
![My diagram](/images/diagram.png)

{/* Or use the Next.js Image component (registered in mdx-components) */}
<Image src="/images/diagram.png" alt="diagram" width={600} height={400} />
```

For links between posts:

```mdx
{/* Use relative links — they work with any basePath */}
Check out my [other post](../other-post)

{/* Or absolute (basePath is applied automatically by Next.js Link) */}
<Link href="/blog/other-post">Other post</Link>
```

## 15.20 Complete project structure (final)

```
your-blog/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── app/
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx                  ← Blog index
│   └── blog/
│       └── [slug]/
│           ├── layout.tsx        ← Post reading layout (max-width, sidebar)
│           └── page.tsx          ← Dynamic MDX loader
├── components/
│   ├── Header.tsx
│   ├── PostCard.tsx
│   └── mdx/
│       ├── Callout.tsx
│       ├── CodeBlock.tsx
│       └── InteractiveDemo.tsx
├── content/
│   ├── hello-world.mdx
│   ├── building-with-d3.mdx
│   └── deploy-guide.mdx
├── lib/
│   └── posts.ts                  ← File system utilities
├── public/
│   ├── .nojekyll
│   └── images/
├── mdx-components.tsx
├── next.config.mjs
├── package.json
└── tsconfig.json
```

---

## 15.21 UX best practices for blog layouts

| Principle | Implementation |
|-----------|---------------|
| **Readable line length** | `max-w-3xl` or `max-w-prose` (65ch) on article content |
| **Scannable headings** | Use clear hierarchy (h1 → h2 → h3), add `id` via rehype-slug |
| **Visual breathing room** | Generous margins between sections (`mt-8`, `mb-6`) |
| **Mobile-first** | Single column by default, expand to multi-column on `md:` / `lg:` |
| **Fast navigation** | Sticky header, table of contents sidebar on desktop |
| **Accessible** | Semantic HTML (article, nav, header, main, aside, footer) |
| **Feedback on interaction** | Hover states on links/cards, focus rings on buttons |
| **Progressive disclosure** | Tags/metadata visible but secondary; content dominates |
| **Print-friendly** | `prose` handles this; avoid fixed-width containers |

## Summary

✅ You set up `@next/mdx` with remark/rehype plugins
✅ You understand the project architecture (content/ → dynamic routes)
✅ You can embed React components in markdown (Callout, BarChart, InteractiveDemo)
✅ You built responsive UI layouts (header, card grid, post reading layout, sidebar)
✅ You know the `prose` shortcut AND the custom component approach
✅ You configured static export with `output: "export"`
✅ You deployed to GitHub Pages with GitHub Actions
✅ You handled basePath, trailingSlash, and .nojekyll

## Key takeaways

**MDX = Markdown's simplicity + React's power.** Write prose in markdown, drop in components when you need interactivity.

**Layout UX is about constraints:** `max-w-3xl` for reading, `max-w-4xl` for index pages, `max-w-6xl` when you have a sidebar. These widths exist because human eyes can't track lines that are too wide.

**GitHub Pages deployment is just `output: "export"` + a GitHub Action.** The static export produces plain HTML/CSS/JS — any static host works.

---

→ [Back to Chapter 14: Shiki Syntax Highlighting](./14-SHIKI-SYNTAX-HIGHLIGHTING.md)
