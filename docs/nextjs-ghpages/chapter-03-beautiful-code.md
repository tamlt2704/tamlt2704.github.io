# Chapter 3: Beautiful Code Blocks

[← Chapter 2: Markdown Pipeline](chapter-02-markdown-pipeline.md) | [Chapter 4: Interactive Quiz →](chapter-04-interactive-quiz.md)

---

## The Problem

Your code blocks render as plain `<pre>` tags. White text on gray. No language detection. No color. Your readers' eyes glaze over.

Compare:

**Before:** A wall of monospace text.
**After:** Python keywords in purple, strings in green, comments in gray. The reader's brain parses the structure before reading the words.

## Install the Highlighter

```bash
npm install react-syntax-highlighter @types/react-syntax-highlighter
```

## The Custom Code Component

When MDX renders a markdown code block, it creates `<pre><code>` elements. We intercept the `<code>` element and replace it with a syntax-highlighted version. This component handles both inline code (`` `like this` ``) and fenced code blocks (` ```python ... ``` `).

Create `app/blog/components/MarkdownCode.tsx`:

````tsx
"use client"; // Needs browser — SyntaxHighlighter uses DOM APIs

// Prism is a syntax highlighting engine. It tokenizes code and applies colors.
// oneDark is VS Code's dark theme — familiar to most developers.
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Props {
  children: React.ReactNode; // The code text inside the <code> tag
  className?: string; // MDX sets this to "language-python" for ```python blocks
}

export function MarkdownCode({ children, className }: Props) {
  // Extract language from className. Example: "language-python" → "python"
  // If no language specified (inline code), match will be null
  const match = /language-(\w+)/.exec(className || "");
  const lang = match ? match[1] : "";
  // Convert children to string and remove trailing newline (Prism adds extra line otherwise)
  const code = String(children).replace(/\n$/, "");

  if (!match) {
    // No language = inline code like `variable`
    // Render with a subtle pink highlight (common convention in docs)
    return (
      <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-sm text-pink-600">
        {children}
      </code>
    );
  }

  // Fenced code block with a language — apply full syntax highlighting
  return (
    <SyntaxHighlighter
      language={lang} // "python", "javascript", "bash", etc.
      style={oneDark} // Color theme (object mapping token types to colors)
      customStyle={{
        margin: "1rem 0", // Space above and below the block
        borderRadius: "0.5rem", // Rounded corners
        fontSize: "0.85rem", // Slightly smaller than body text
        lineHeight: 1.6, // Comfortable reading spacing
      }}
    >
      {code}
    </SyntaxHighlighter>
  );
}

// MarkdownPre prevents double-wrapping.
// Without this, Tailwind's prose styles add their own <pre> styling on top of ours.
// By replacing <pre> with a fragment (<>), we let SyntaxHighlighter handle all styling.
export function MarkdownPre({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
````

**The flow when MDX encounters a code block:**

````
Markdown: ```python\nprint("hi")\n```
    ↓ MDX parser
JSX: <pre><code className="language-python">print("hi")</code></pre>
    ↓ Our components override
<MarkdownPre> → renders nothing (fragment)
  <MarkdownCode className="language-python"> → renders SyntaxHighlighter
    ↓
Colored, styled code block in the browser
````

1. MDX passes every code block through our `code` component
2. Fenced blocks get `className="language-python"` — we extract the language
3. `SyntaxHighlighter` applies the `oneDark` theme (VS Code's dark theme)
4. Inline code gets a subtle pink highlight instead

The `MarkdownPre` wrapper prevents Tailwind's prose styles from double-wrapping the code block.

## Wire It Into the Renderer

Update `app/blog/[...slug]/page.tsx`:

```tsx
import { MarkdownCode, MarkdownPre } from "@/app/blog/components/MarkdownCode";

// In the MDXRemote component:
<MDXRemote
  source={content}
  components={{
    code: MarkdownCode,
    pre: MarkdownPre,
  }}
  options={{
    mdxOptions: {
      remarkPlugins: [remarkGfm],
      format: "md",
    },
  }}
/>;
```

That's it. Every code block in every markdown file now gets syntax highlighting. You didn't touch a single content file.

## Add Tailwind Typography

Install the plugin:

```bash
npm install @tailwindcss/typography
```

Add to your `tailwind.config.ts` (or `app/globals.css` with Tailwind v4):

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

Now wrap your content in `prose` classes:

```tsx
<div className="prose prose-lg max-w-none prose-headings:text-gray-900 prose-a:text-teal-600">
  <MDXRemote ... />
</div>
```

The `prose` class handles:

- Heading sizes and spacing
- Paragraph line height
- List indentation
- Blockquote styling
- Link colors
- Table borders

All from one class. Your markdown looks like a professionally typeset article.

## The Result

Write this in any `.md` file:

````markdown
## Binary Search

The key insight: if the array is sorted, you can eliminate half the remaining elements with each comparison.

````python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```⁠

Time complexity: `O(log n)` — each step halves the search space.
````
````

It renders with:

- A styled heading
- Proper paragraph spacing
- Syntax-highlighted Python with the `oneDark` theme
- Inline code (`O(log n)`) in pink with a gray background

Zero configuration per file. Write markdown, get beauty.

---

## Commit Your Progress

```bash
git add .
git commit -m "feat: add syntax highlighting and typography styles"
```

## What's Next

Static content looks great now. But a blog that just _shows_ code isn't much better than a textbook. In Chapter 4, we'll build our first interactive component — a Quiz that lives inside markdown and gives readers immediate feedback.

The blog starts teaching back.
