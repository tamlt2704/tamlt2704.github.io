# Chapter 3: Beautiful Code Blocks

[← Chapter 2: Markdown Pipeline](/blog/nextjs-ghpages/chapter-02-markdown-pipeline) | [Chapter 4: Interactive Quiz →](/blog/nextjs-ghpages/chapter-04-interactive-quiz)

---

## What We're Fixing

Right now your code blocks look like this:

```
┌─────────────────────────────────────────────┐
│ BEFORE: plain <pre> tag                     │
├─────────────────────────────────────────────┤
│                                             │
│  def binary_search(arr, target):            │
│      lo, hi = 0, len(arr) - 1              │
│      while lo <= hi:                        │
│          mid = (lo + hi) // 2              │
│          if arr[mid] == target:            │
│              return mid                     │
│                                             │
│  (all white text, gray background, no       │
│   structure visible at a glance)            │
│                                             │
└─────────────────────────────────────────────┘

                    ↓ after this chapter ↓

┌─────────────────────────────────────────────┐
│ AFTER: syntax highlighted                   │
├─────────────────────────────────────────────┤
│                                             │
│  def binary_search(arr, target):  ← purple  │
│      lo, hi = 0, len(arr) - 1    ← white   │
│      while lo <= hi:              ← purple  │
│          mid = (lo + hi) // 2     ← white   │
│          if arr[mid] == target:   ← purple  │
│              return mid           ← purple  │
│                                             │
│  (keywords colored, strings green,          │
│   comments gray — brain parses structure    │
│   before reading words)                     │
│                                             │
└─────────────────────────────────────────────┘
```

Three things make this work:

1. **MarkdownCode** — intercepts `<code>` tags and applies color
2. **MarkdownPre** — prevents double-wrapping from Tailwind's prose styles
3. **Components map** — tells MDX to use our components instead of defaults

---

## Install the Highlighter

```bash
npm install react-syntax-highlighter @types/react-syntax-highlighter
```

---

## Concept: What Is Prism?

Prism is a syntax highlighting engine. It reads your code string, breaks it into **tokens** (keywords, strings, comments, operators), and assigns each token a CSS class. A **theme** maps those classes to colors.

We use `react-syntax-highlighter` which wraps Prism in a React component. The `oneDark` theme gives you VS Code's familiar dark palette.

---

## Concept: Why 'use client'?

Next.js renders components on the server by default. But `react-syntax-highlighter` uses browser DOM APIs to measure and render highlighted code. Adding `"use client"` tells Next.js: "ship this component's JavaScript to the browser."

Without it, you get a server-side error about missing DOM globals.

---

## Step 1: Create the MarkdownCode Component

This component receives every `<code>` tag from MDX. It checks: does this code block have a language? If yes → full syntax highlighting. If no → it's inline code, render with a subtle pink style.

```bash
mkdir -p app/blog/components
```

````tsx
// 📁 app/blog/components/MarkdownCode.tsx — create this file

"use client"; // Prism needs browser DOM APIs

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Props {
  children: React.ReactNode;
  className?: string; // MDX sets "language-python" for ```python blocks
}
````

Save. This is just the imports and types — the logic comes next.

---

## Step 2: Handle Inline Code

When you write `` `variable` `` in markdown (no language), MDX renders `<code>variable</code>` with no className. We detect that and render a simple styled span.

```tsx
// 📁 app/blog/components/MarkdownCode.tsx — add the component body

export function MarkdownCode({ children, className }: Props) {
  // "language-python" → "python", no class → null
  const match = /language-(\w+)/.exec(className || "");

  if (!match) {
    // Inline code: `like this` — pink highlight, no Prism
    return (
      <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-sm text-pink-600">
        {children}
      </code>
    );
  }
```

---

## Step 3: Handle Fenced Code Blocks

When MDX sees ` ```python `, it passes `className="language-python"` to our component. We extract the language and feed it to SyntaxHighlighter.

```tsx
// 📁 app/blog/components/MarkdownCode.tsx — continue inside the function

  const lang = match[1]; // "python", "javascript", "bash", etc.
  // Remove trailing newline — Prism adds an extra blank line otherwise
  const code = String(children).replace(/\n$/, "");

  return (
    <SyntaxHighlighter
      language={lang}
      style={oneDark}
      customStyle={{
        margin: "1rem 0",
        borderRadius: "0.5rem",
        fontSize: "0.85rem",
        lineHeight: 1.6,
      }}
    >
      {code}
    </SyntaxHighlighter>
  );
}
```

---

## Concept: What Is MarkdownPre?

MDX renders fenced code blocks as `<pre><code>...</code></pre>`. Tailwind's `prose` class adds its own padding, background, and border-radius to `<pre>` tags. That conflicts with SyntaxHighlighter's styling — you get double padding, mismatched backgrounds.

The fix: replace `<pre>` with a React fragment (`<>...</>`). The fragment renders nothing — it just passes children through. SyntaxHighlighter handles all the styling.

```
MDX output:  <pre><code className="language-python">...</code></pre>
                │                    │
                ↓                    ↓
Our override:  <MarkdownPre>       <MarkdownCode>
                │                    │
                ↓                    ↓
Renders as:    <> (nothing)         <SyntaxHighlighter> (colored code)
```

---

## Step 4: Add the MarkdownPre Wrapper

```tsx
// 📁 app/blog/components/MarkdownCode.tsx — add at the bottom of the file

// Replaces <pre> with a fragment to prevent Tailwind prose double-styling
export function MarkdownPre({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
```

Save. The component file is complete.

---

## Concept: What Is a Components Map?

MDX converts markdown to React. By default, `# Hello` becomes `<h1>Hello</h1>` and ` ```python ` becomes `<pre><code>...</code></pre>`.

A **components map** is an object that says: "when you'd normally render `<code>`, use my `MarkdownCode` instead." It's a lookup table from HTML tag names to custom React components:

```
{
  code: MarkdownCode,   // every <code> → our highlighted version
  pre: MarkdownPre,     // every <pre>  → transparent fragment
}
```

You pass this map to `MDXRemote`. Every markdown file in your blog gets the override — zero per-file configuration.

---

## Step 5: Register in the MDX Components Map

```tsx
// 📁 app/blog/[...slug]/page.tsx — update the MDXRemote call

import { MarkdownCode, MarkdownPre } from "@/app/blog/components/MarkdownCode";

// Inside your component's return, update MDXRemote:
<MDXRemote
  source={content}
  components={{
    code: MarkdownCode, // intercept all <code> tags
    pre: MarkdownPre, // strip default <pre> styling
  }}
  options={{
    mdxOptions: { remarkPlugins: [remarkGfm], format: "md" },
  }}
/>;
```

Save. Refresh. You see every fenced code block in your posts rendered with VS Code's dark theme — keywords in purple, strings in green, comments in gray. Inline code like `variable` appears in pink with a light background.

---

## Step 6: Add Tailwind Typography

The `@tailwindcss/typography` plugin gives you a single `prose` class that styles all markdown output — headings, paragraphs, lists, blockquotes, tables — with professional typographic defaults.

```bash
npm install @tailwindcss/typography
```

```css
/* 📁 app/globals.css — add these two lines at the top */

@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

Save. Now wrap your MDX output:

```tsx
// 📁 app/blog/[...slug]/page.tsx — wrap MDXRemote in prose

<div className="prose prose-lg max-w-none prose-headings:text-gray-900 prose-a:text-teal-600">
  <MDXRemote ... />
</div>
```

Save. Refresh. You see your markdown rendered like a professionally typeset article — proper heading hierarchy, comfortable line height, indented lists, styled blockquotes. All from one CSS class.

---

## The Full Flow

````
You write:     ```python\ndef hello(): ...\n```

MDX parses:    <pre><code className="language-python">def hello(): ...</code></pre>

Components     pre  → MarkdownPre  → renders <> (nothing)
map routes:    code → MarkdownCode → renders <SyntaxHighlighter>

Browser shows: colored, rounded, dark-themed code block
````

---

## Commit Your Progress

```bash
git add app/blog/components/MarkdownCode.tsx app/blog/[...slug]/page.tsx app/globals.css
git commit -m "feat: add syntax highlighting and typography styles"
```

---

## What's Next

Static content looks great now. But a blog that just _shows_ code isn't much better than a textbook. In Chapter 4, we'll build our first interactive component — a Quiz that lives inside markdown and gives readers immediate feedback.

The blog starts teaching back.
