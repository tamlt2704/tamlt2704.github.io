# Chapter 2: The Markdown Pipeline

[← Chapter 1: First Deploy](/blog/nextjs-ghpages/chapter-01-first-deploy) | [Chapter 3: Beautiful Code →](/blog/nextjs-ghpages/chapter-03-beautiful-code)

---

## The Problem

You have 50 markdown files about algorithms. 20 about Docker. 15 about game development. You don't want to create a React component for each one. You want to drop a `.md` file in a folder and have it appear as a page — automatically.

## The Folder Structure

Here's the plan:

```
my-blog/
  content/
    algorithms/
      chapter-00-overview.md
      chapter-01-linear-search.md
      chapter-02-binary-search.md
    docker101/
      chapter-00-containers.md
      chapter-01-images.md
  app/
    blog/
      [...slug]/
        page.tsx          ← one file renders ALL markdown
  lib/
    markdown.ts           ← reads folders, finds files
```

One React page. Unlimited content. The folder name becomes the series. The file name becomes the chapter.

## Install Dependencies

```bash
npm install next-mdx-remote gray-matter remark-gfm
```

- `next-mdx-remote` — renders markdown as React components (server-side)
- `gray-matter` — parses YAML frontmatter from markdown files
- `remark-gfm` — adds GitHub Flavored Markdown (tables, strikethrough, task lists)

## The Content Reader

This file scans your `content/` folder and provides functions to list series and read chapters. It runs at build time (server-side only) — readers never see this code.

Create `lib/markdown.ts`:

```bash
mkdir -p lib && touch lib/markdown.ts
```

```typescript
import fs from "fs"; // Node.js file system module — reads files and folders
import path from "path"; // Builds file paths that work on any OS (Windows, Mac, Linux)

const CONTENT_DIR = "content";

/**
 * Get all series (folders) with their chapters.
 * Returns: [{ name: "algorithms", slug: "algorithms", chapters: ["chapter-00.md", ...] }]
 */
export function getAllSeries() {
  // process.cwd() = the root of your project (where package.json lives)
  const base = path.join(process.cwd(), CONTENT_DIR);

  // If the content folder doesn't exist yet, return empty (no crash)
  if (!fs.existsSync(base)) return [];

  return fs
    .readdirSync(base, { withFileTypes: true }) // List everything in content/
    .filter((d) => d.isDirectory()) // Keep only folders (not files)
    .map((d) => ({
      // Transform each folder into an object
      name: d.name, // "algorithms"
      slug: d.name, // Used in URLs: /blog/algorithms/...
      chapters: fs
        .readdirSync(path.join(base, d.name)) // List files inside the folder
        .filter((f) => f.endsWith(".md")) // Keep only markdown files
        .sort(), // Alphabetical order (chapter-00, chapter-01, ...)
    }));
}

/**
 * Read a single markdown file's content as a string.
 * Returns null if the file doesn't exist.
 */
export function getChapterContent(series: string, file: string) {
  const filePath = path.join(process.cwd(), CONTENT_DIR, series, file);
  if (!fs.existsSync(filePath)) return null;
  return fs.readFileSync(filePath, "utf-8"); // Read the entire file as text
}

/**
 * Get the list of chapter filenames in a series, sorted.
 * Used for prev/next navigation.
 */
export function getSeriesChapters(series: string) {
  const dir = path.join(process.cwd(), CONTENT_DIR, series);
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md") && f !== "README.md") // exclude README
    .sort();
}
```

**Why `fs` and not `fetch`?** This code runs at build time on your machine (or in GitHub Actions). It reads files directly from disk — no HTTP requests, no API, no latency. The result gets baked into static HTML.

This is the entire content layer. No database. No API. Just `fs.readFileSync`.

```bash
git add lib/markdown.ts
git commit -m "feat: add markdown content reader"
```

## The Catch-All Route

This is the most important file in the project. One component renders _every_ markdown file as a page. The `[...slug]` in the folder name means "match any URL path with any number of segments."

Create `app/blog/[...slug]/page.tsx`:

```bash
mkdir -p "app/blog/[...slug]" && touch "app/blog/[...slug]/page.tsx"
```

```tsx
import { notFound } from "next/navigation"; // Shows a 404 page
import fs from "fs";
import path from "path";
import matter from "gray-matter"; // Parses YAML frontmatter from markdown
import { MDXRemote } from "next-mdx-remote/rsc"; // Renders markdown as React components
import remarkGfm from "remark-gfm"; // Adds GitHub-flavored markdown (tables, etc.)
import { MarkdownCode, MarkdownPre } from "@/app/blog/components/MarkdownCode";
import { getSeriesChapters } from "@/lib/markdown";

// Next.js passes URL segments as params.
// For /blog/algorithms/chapter-01 → slug = ["algorithms", "chapter-01"]
interface Props {
  params: Promise<{ slug: string[] }>;
}

/**
 * generateStaticParams tells Next.js which pages to pre-build.
 * At build time, it scans all .md files and returns their URL paths.
 * Without this, Next.js wouldn't know what pages exist (since they're dynamic).
 */
export async function generateStaticParams() {
  const base = path.join(process.cwd(), "content");
  if (!fs.existsSync(base)) return [];

  const params: { slug: string[] }[] = [];
  const folders = fs.readdirSync(base, { withFileTypes: true }).filter((d) => d.isDirectory());

  for (const folder of folders) {
    const files = fs
      .readdirSync(path.join(base, folder.name))
      .filter((f) => f.endsWith(".md") && f !== "README.md"); // exclude README
    for (const file of files) {
      // Each file becomes a URL: /blog/{folder}/{filename-without-.md}
      params.push({ slug: [folder.name, file.replace(/\.md$/, "")] });
    }
  }
  return params; // must return or generateStaticParams returns undefined
}

/**
 * The page component. Runs once per markdown file at build time.
 * Reads the file, renders it as HTML, wraps it in layout.
 */
export default async function BlogPage({ params }: Props) {
  const { slug } = await params;
  if (slug.length < 2) return notFound(); // Need at least series + chapter

  // Destructure: /blog/algorithms/chapter-01 → series="algorithms", fileSlug="chapter-01"
  const [series, fileSlug] = slug;
  const filePath = path.join(process.cwd(), "content", series, `${fileSlug}.md`);

  if (!fs.existsSync(filePath)) return notFound(); // File doesn't exist → 404

  // Read the markdown file and separate frontmatter (metadata) from content
  const raw = fs.readFileSync(filePath, "utf-8");
  const { content } = matter(raw); // content = the markdown text without frontmatter

  // Build prev/next navigation links
  const chapters = getSeriesChapters(series);
  const currentFile = `${fileSlug}.md`;
  const idx = chapters.indexOf(currentFile);
  const prev = idx > 0 ? chapters[idx - 1] : null;
  const next = idx < chapters.length - 1 ? chapters[idx + 1] : null;

  return (
    <article className="mx-auto max-w-3xl px-6 py-12">
      {/* prose = Tailwind typography plugin, styles all HTML elements beautifully */}
      <div className="prose prose-lg max-w-none">
        <MDXRemote
          source={content}
          components={{
            code: MarkdownCode, // syntax highlighting for code blocks
            pre: MarkdownPre, // prevents double-wrapping by Tailwind prose
            // strip .md from links so chapter links work as Next.js routes
            a: ({ href, ...props }) => <a href={href?.replace(/\.md$/, "")} {...props} />,
          }}
          options={{
            mdxOptions: {
              remarkPlugins: [remarkGfm], // Enable tables, strikethrough, task lists
              format: "mdx", // mdx mode enables JSX components like <Quiz /> inside markdown
            },
          }}
        />
      </div>

      {/* Prev / Next */}
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

**What each `components` entry does:**

| Key    | What it replaces                           | Why                                                            |
| ------ | ------------------------------------------ | -------------------------------------------------------------- |
| `code` | `` `inline` `` and ` ```fenced``` ` blocks | Adds syntax highlighting via `react-syntax-highlighter`        |
| `pre`  | `<pre>` wrapper around code blocks         | Prevents Tailwind prose from double-styling the block          |
| `a`    | Every `[link](url)` in markdown            | Strips `.md` extension so chapter links work as Next.js routes |

## How It Works

The `[...slug]` catch-all route matches any URL under `/blog/`:

```
/blog/algorithms/chapter-01-linear-search
       ↓
slug = ["algorithms", "chapter-01-linear-search"]
       ↓
reads: content/algorithms/chapter-01-linear-search.md
       ↓
renders as HTML with MDXRemote
```

`generateStaticParams()` runs at build time, enumerates every `.md` file, and pre-renders all pages. The result is pure static HTML — no server needed.

```bash
git add app/blog
git commit -m "feat: add catch-all blog route with prev/next navigation"
```

## Test It

Create `content/hello/chapter-00-test.md`:

`````markdown
# Hello World

This is my first blog post.

It supports **bold**, _italic_, and `inline code`.

## A Code Block

````python
print("Hello from the blog!")
```⁠

## A Table

| Feature | Status |
|---------|--------|
| Markdown | ✅ |
| Code blocks | ✅ |
| Tables | ✅ |
````
`````

````

Run `npm run dev`, visit `http://localhost:3000/blog/hello/chapter-00-test`.

Your markdown is a web page. No React component written. Just a file in a folder.

## The Mental Model

```
content/
  {series}/
    {chapter}.md
         ↓
/blog/{series}/{chapter}
         ↓
Static HTML at build time
```

Add a folder → new series appears. Add a file → new chapter appears. Delete a file → page disappears. The filesystem _is_ your CMS.

---

## Commit Your Progress

```bash
git add .
git commit -m "feat: add markdown pipeline with catch-all route"
```

## What's Next

The page works but looks plain. Code blocks are unstyled monospace. In Chapter 3, we'll add syntax highlighting with `react-syntax-highlighter` and Tailwind's typography plugin to make everything look professional with zero effort.
````
