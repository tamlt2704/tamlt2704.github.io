# Chapter 2: The Markdown Pipeline

[← Chapter 1: First Deploy](/blog/nextjs-ghpages/chapter-01-first-deploy) | [Chapter 3: Beautiful Code →](/blog/nextjs-ghpages/chapter-03-beautiful-code)

---

## The Big Picture

You have 50 markdown files. You don't want 50 React components. You want to drop a `.md` file in a folder and have it appear as a page — automatically.

Here's the pipeline we're building:

```
┌─────────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│  .md file   │────▶│  fs.read │────▶│gray-matter │────▶│MDXRemote │────▶│HTML page │
│  on disk    │     │  (Node)  │     │  (parse)   │     │ (render) │     │ (static) │
└─────────────┘     └──────────┘     └───────────┘     └──────────┘     └──────────┘
       │                                                                       │
       │              BUILD TIME (your machine / GitHub Actions)                │
       └───────────────────────────────────────────────────────────────────────┘
```

One React page. Unlimited content. The filesystem _is_ your CMS.

---

## Step 1: Content Folder Structure

Before writing code, create the folder layout:

```
my-blog/
  content/
    algorithms/
      chapter-00-overview.md
      chapter-01-linear-search.md
    docker101/
      chapter-00-containers.md
  app/
    blog/
      [...slug]/
        page.tsx        ← one file renders ALL markdown
  lib/
    markdown.ts         ← reads folders, finds files
```

The folder name becomes the series. The filename becomes the chapter URL.

---

## Step 2: Install Dependencies

### What is MDX?

MDX is markdown that can contain React components. `next-mdx-remote` renders MDX on the server at build time — the browser receives plain HTML, no JavaScript needed.

### What does gray-matter do?

Markdown files often start with YAML metadata (title, date, tags). `gray-matter` splits that metadata from the content so you can use both separately.

### Install:

```bash
npm install next-mdx-remote gray-matter remark-gfm
```

---

## Step 3: The Markdown Reader Utility

This utility reads your `content/` folder at build time. It uses Node.js `fs` — no database, no API, no latency.

```typescript
// 📁 lib/markdown.ts — create the content reader

import fs from "fs";
import path from "path";

// All markdown lives here, relative to project root
const CONTENT_DIR = "content";
```

Save. No visible change yet — this is a utility file.

Now add the function that lists all series and their chapters:

```typescript
// 📁 lib/markdown.ts — add below the imports

export function getAllSeries() {
  const base = path.join(process.cwd(), CONTENT_DIR);
  if (!fs.existsSync(base)) return [];

  return fs
    .readdirSync(base, { withFileTypes: true })
    .filter((d) => d.isDirectory()) // only folders
    .map((d) => ({
      name: d.name,
      slug: d.name, // used in URLs
      chapters: fs
        .readdirSync(path.join(base, d.name))
        .filter((f) => f.endsWith(".md"))
        .sort(), // alphabetical = chapter order
    }));
}
```

Next, add the function that reads a single chapter file:

```typescript
// 📁 lib/markdown.ts — read one markdown file

export function getChapterContent(series: string, file: string) {
  const filePath = path.join(process.cwd(), CONTENT_DIR, series, file);
  if (!fs.existsSync(filePath)) return null;
  return fs.readFileSync(filePath, "utf-8");
}
```

Finally, add the function for listing chapters (used for prev/next navigation):

```typescript
// 📁 lib/markdown.ts — list chapters in a series

export function getSeriesChapters(series: string) {
  const dir = path.join(process.cwd(), CONTENT_DIR, series);
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md") && f !== "README.md")
    .sort();
}
```

Save. No visible change — this runs only at build time.

**Why `fs` and not `fetch`?** This code runs on your machine (or in GitHub Actions). It reads files directly from disk. The result gets baked into static HTML.

---

## Step 4: The Dynamic Route

### What is `[...slug]`?

Next.js uses folder names with brackets for dynamic routes. `[...slug]` is a "catch-all" — it matches any number of URL segments:

```
/blog/algorithms/chapter-01  →  slug = ["algorithms", "chapter-01"]
/blog/docker101/chapter-00   →  slug = ["docker101", "chapter-00"]
```

### What does generateStaticParams do?

At build time, Next.js doesn't know what pages exist (they're just `.md` files). `generateStaticParams` scans your content folder and returns every valid URL. Next.js then pre-renders each one as static HTML.

Create the route file:

```bash
mkdir -p "app/blog/[...slug]"
```

```tsx
// 📁 app/blog/[...slug]/page.tsx — imports and types

import { notFound } from "next/navigation";
import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { MDXRemote } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import { getSeriesChapters } from "@/lib/markdown";

interface Props {
  params: Promise<{ slug: string[] }>;
}
```

Now add `generateStaticParams` — this tells Next.js which pages to build:

```tsx
// 📁 app/blog/[...slug]/page.tsx — tell Next.js what pages exist

export async function generateStaticParams() {
  const base = path.join(process.cwd(), "content");
  if (!fs.existsSync(base)) return [];

  const params: { slug: string[] }[] = [];
  const folders = fs.readdirSync(base, { withFileTypes: true }).filter((d) => d.isDirectory());

  for (const folder of folders) {
    const files = fs
      .readdirSync(path.join(base, folder.name))
      .filter((f) => f.endsWith(".md") && f !== "README.md");
    for (const file of files) {
      // /blog/algorithms/chapter-01 → slug: ["algorithms", "chapter-01"]
      params.push({ slug: [folder.name, file.replace(/\.md$/, "")] });
    }
  }
  return params;
}
```

Now the page component — it reads the file and renders it:

```tsx
// 📁 app/blog/[...slug]/page.tsx — the page component

export default async function BlogPage({ params }: Props) {
  const { slug } = await params;
  if (slug.length < 2) return notFound();

  const [series, fileSlug] = slug;
  const filePath = path.join(
    process.cwd(), "content", series, `${fileSlug}.md`
  );
  if (!fs.existsSync(filePath)) return notFound();

  // Separate YAML frontmatter from markdown content
  const raw = fs.readFileSync(filePath, "utf-8");
  const { content } = matter(raw);
```

Continue with the render and navigation:

```tsx
  // 📁 app/blog/[...slug]/page.tsx — render MDX + navigation

  // Build prev/next links from chapter list
  const chapters = getSeriesChapters(series);
  const currentFile = `${fileSlug}.md`;
  const idx = chapters.indexOf(currentFile);
  const prev = idx > 0 ? chapters[idx - 1] : null;
  const next = idx < chapters.length - 1 ? chapters[idx + 1] : null;

  return (
    <article className="mx-auto max-w-3xl px-6 py-12">
      <div className="prose prose-lg max-w-none">
        <MDXRemote
          source={content}
          options={{
            mdxOptions: { remarkPlugins: [remarkGfm], format: "mdx" },
          }}
        />
      </div>
```

Finally, the prev/next navigation at the bottom:

```tsx
      {/* 📁 app/blog/[...slug]/page.tsx — prev/next nav */}

      <nav className="mt-12 flex justify-between border-t pt-6 text-sm">
        {prev && (
          <a
            href={`/blog/${series}/${prev.replace(".md", "")}`}
            className="text-teal-600 hover:underline"
          >
            ← Previous
          </a>
        )}
        {next && (
          <a
            href={`/blog/${series}/${next.replace(".md", "")}`}
            className="ml-auto text-teal-600 hover:underline"
          >
            Next →
          </a>
        )}
      </nav>
    </article>
  );
}
```

Save. Now we need a test file to see it work.

---

## Step 5: Test It

Create a sample markdown file:

```markdown
<!-- 📁 content/hello/chapter-00-test.md — test content -->

# Hello World

This is my first blog post. It supports **bold**, _italic_, and `code`.

## A Table

| Feature     | Status |
| ----------- | ------ |
| Markdown    | ✅     |
| Code blocks | ✅     |
| Tables      | ✅     |
```

Save. Refresh. You see your markdown rendered as a styled web page at `http://localhost:3000/blog/hello/chapter-00-test`.

---

## Step 6: Prev/Next Navigation

Add a second file to test navigation:

```markdown
<!-- 📁 content/hello/chapter-01-second.md — second chapter -->

# Second Chapter

Click "← Previous" below to go back to chapter-00.
```

Save. Refresh. You see "← Previous" and "Next →" links at the bottom of each chapter, connecting them in alphabetical order.

---

## The Mental Model

```
content/
  {series}/
    {chapter}.md         ← add file here
         │
         ▼
/blog/{series}/{chapter} ← page appears here
         │
         ▼
Static HTML at build     ← no server needed
```

Add a folder → new series. Add a file → new chapter. Delete a file → page disappears.

---

## Commit

```bash
git add .
git commit -m "feat: add markdown pipeline with catch-all route"
```

---

## What's Next

The page works but code blocks are unstyled monospace. In Chapter 3, we add syntax highlighting with `react-syntax-highlighter` and Tailwind typography to make everything look professional.

[← Chapter 1: First Deploy](/blog/nextjs-ghpages/chapter-01-first-deploy) | [Chapter 3: Beautiful Code →](/blog/nextjs-ghpages/chapter-03-beautiful-code)
