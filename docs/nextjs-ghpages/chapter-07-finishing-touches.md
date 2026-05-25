# Chapter 7: Finishing Touches

[← Chapter 6: Visualizer](chapter-06-visualizer.md)

---

## What We Have

A Next.js site that:
- Reads markdown from folders
- Renders with syntax highlighting
- Supports interactive components (Quiz, CodePlayground, StepVisualizer)
- Deploys to GitHub Pages on every push

What's missing: a landing page, series navigation, and SEO.

## The Blog Index Page

Create `app/blog/page.tsx` — lists all series:

```tsx
import Link from "next/link";
import { getAllSeries } from "@/lib/markdown";

export default function BlogIndex() {
  const series = getAllSeries();

  return (
    <main className="max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Blog</h1>

      <div className="space-y-6">
        {series.map((s) => (
          <Link
            key={s.slug}
            href={`/blog/${s.slug}/${s.chapters[0].replace(".md", "")}`}
            className="block p-5 rounded-lg border border-gray-200 hover:border-teal-400 transition"
          >
            <h2 className="text-lg font-semibold text-gray-900">
              {s.name.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {s.chapters.length} chapters
            </p>
          </Link>
        ))}
      </div>
    </main>
  );
}
```

Visit `/blog` — every folder in `content/` appears as a clickable card.

## Chapter Sidebar

For longer series, add a sidebar showing all chapters. Update `app/blog/[...slug]/page.tsx`:

```tsx
// Inside the return, before <article>:
<aside className="hidden lg:block fixed left-8 top-24 w-56">
  <p className="text-xs font-semibold text-gray-400 uppercase mb-3">
    {series.replace(/-/g, " ")}
  </p>
  <nav className="space-y-1">
    {chapters.map((ch) => {
      const slug = ch.replace(".md", "");
      const isActive = slug === fileSlug;
      const label = slug.replace("chapter-", "").replace(/-/g, " ");
      return (
        <a
          key={ch}
          href={`/blog/${series}/${slug}`}
          className={`block text-sm px-3 py-1.5 rounded ${
            isActive
              ? "bg-teal-50 text-teal-700 font-medium"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          {label}
        </a>
      );
    })}
  </nav>
</aside>
```

On desktop, readers see where they are in the series and can jump to any chapter.

## SEO: Page Titles and Metadata

Add `generateMetadata` to your catch-all route:

```tsx
import type { Metadata } from "next";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const [series, fileSlug] = slug;
  const title = fileSlug
    .replace("chapter-", "Ch ")
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
  const seriesTitle = series.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  return {
    title: `${title} — ${seriesTitle}`,
    description: `Learn ${seriesTitle} step by step.`,
  };
}
```

Each page gets a unique `<title>` tag. Google indexes them properly.

## The Complete Components Map

Here's your final `components` object — every interactive element available in markdown:

```tsx
import { MarkdownCode, MarkdownPre } from "@/app/blog/components/MarkdownCode";
import { Quiz } from "@/app/blog/components/Quiz";
import { CodePlayground } from "@/app/blog/components/CodePlayground";
import { StepVisualizer } from "@/app/blog/components/StepVisualizer";

const components = {
  code: MarkdownCode,
  pre: MarkdownPre,
  Quiz,
  CodePlayground,
  StepVisualizer,
};
```

Add more anytime. Create the component, add one line here, use it in any markdown file.

## Final Project Structure

```
my-blog/
├── app/
│   ├── blog/
│   │   ├── [...slug]/page.tsx    ← renders all markdown
│   │   ├── page.tsx              ← blog index
│   │   └── components/
│   │       ├── MarkdownCode.tsx  ← syntax highlighting
│   │       ├── Quiz.tsx          ← multiple choice
│   │       ├── CodePlayground.tsx← editable + runnable code
│   │       └── StepVisualizer.tsx← algorithm step-through
│   ├── page.tsx                  ← home page
│   └── globals.css
├── content/
│   ├── algorithms/
│   │   ├── chapter-00-overview.md
│   │   ├── chapter-01-linear-search.md
│   │   └── ...
│   └── docker101/
│       └── ...
├── lib/
│   └── markdown.ts               ← content reader
├── next.config.ts                 ← static export
├── .github/workflows/deploy.yml   ← auto-deploy
└── package.json
```

## The Workflow

Your daily workflow as a content creator:

1. Write a `.md` file in `content/{series}/`
2. Use `<Quiz>`, `<CodePlayground>`, `<StepVisualizer>` wherever it helps
3. `git push`
4. Site updates in 2 minutes

No build commands. No deploy scripts. No CMS login. Write → push → live.

## What You Built

From zero to a fully interactive learning platform:

- **Chapter 1:** Static site on GitHub Pages
- **Chapter 2:** Markdown → pages pipeline
- **Chapter 3:** Beautiful syntax highlighting
- **Chapter 4:** Quizzes for instant feedback
- **Chapter 5:** Code playgrounds for experimentation
- **Chapter 6:** Step visualizers for understanding
- **Chapter 7:** Navigation, SEO, polish

Total cost: $0/month.
Total JavaScript frameworks: 1.
Total lines of infrastructure code: ~30 (the deploy workflow).

The blog teaches back. Ship it.
