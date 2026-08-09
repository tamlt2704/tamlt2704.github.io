# Chapter 14: Shiki — Production-Grade Syntax Highlighting

## What you'll learn

- What Shiki is and why it produces perfect highlighting
- How to install and configure Shiki in a Next.js project
- How to use `codeToTokens` for per-line control (needed for our step engine)
- How to keep the active-line highlight working with Shiki tokens
- How to lazy-load the highlighter so it doesn't block page render
- How to add new languages

## 14.1 Why upgrade from our hand-built tokeniser?

Our `tokenise.ts` (Chapter 04) handles keywords, strings, numbers, and comments. But it breaks on:

- Generic types: `List<String>` — the `<` is tokenised as an operator
- Annotations: `@Override` — treated as punctuation + identifier
- Multi-line strings: Java text blocks, Python triple-quotes
- Method references: `arr::sort` — the `::` isn't handled
- Regex literals (JavaScript)
- Type parameters, lambdas, nested generics

Shiki uses the **exact same grammar files as VS Code** (TextMate grammars). If VS Code highlights it correctly, Shiki will too.

> **How does it work internally?** Shiki loads `.tmLanguage.json` files — these are state machines that define how to tokenise every language. Each grammar has hundreds of regex rules with nested scopes. It's the same technology that's powered VS Code, Sublime Text, and Atom.
>
> **Why not Prism.js?** Prism uses hand-written regex per language — simpler but less accurate. Shiki is more correct at the cost of a larger async load. For an algorithm visualiser where accuracy matters (students read this code), Shiki is the better choice.

## 14.2 Install Shiki

```bash
npm install shiki
```

That's it. No peer dependencies, no CSS files to import. Shiki embeds everything (themes and grammars) and loads them on demand.

Check your `package.json`:

```json
{
  "dependencies": {
    "shiki": "^3.0.0"
  }
}
```

## 14.3 Core concepts

Shiki has two main APIs:

| API | Returns | Use when |
|-----|---------|----------|
| `codeToHtml()` | HTML string with inline `<span style="color:...">` | You want a self-contained highlighted block |
| `codeToTokens()` | Array of tokens per line, each with a colour | You need per-line or per-token control |

For our project, we need `codeToTokens()` because we highlight the **current line** based on algorithm step state.

## 14.4 Create a highlighter singleton

The highlighter is expensive to create (loads grammar + theme files). Create it once, reuse everywhere.

Create `app/algorithms/lib/highlighter.ts`:

```ts
import { createHighlighter, type Highlighter } from "shiki";

let highlighterPromise: Promise<Highlighter> | null = null;

/**
 * Returns a shared Shiki highlighter instance.
 * The first call triggers async loading; subsequent calls return the same promise.
 */
export function getHighlighter(): Promise<Highlighter> {
  if (!highlighterPromise) {
    highlighterPromise = createHighlighter({
      themes: ["github-dark"],
      langs: ["java", "python"],
    });
  }
  return highlighterPromise;
}
```

> **Why a singleton?** `createHighlighter()` fetches and parses grammar files — takes ~100-200ms. If you called it on every render, the page would stutter. A singleton means the cost is paid once.
>
> **Adding languages later:** Call `highlighter.loadLanguage('javascript')` at runtime. You don't need to list every language upfront.

## 14.5 Understanding `codeToTokens`

```ts
const highlighter = await getHighlighter();

const result = highlighter.codeToTokens(
  `public void sort(int[] arr) {\n  return;\n}`,
  { lang: "java", theme: "github-dark" }
);
```

The result shape:

```ts
{
  tokens: [
    // Line 0: "public void sort(int[] arr) {"
    [
      { content: "public", color: "#ff7b72" },
      { content: " ", color: "#e6edf3" },
      { content: "void", color: "#ff7b72" },
      { content: " ", color: "#e6edf3" },
      { content: "sort", color: "#d2a8ff" },
      { content: "(", color: "#e6edf3" },
      { content: "int", color: "#ff7b72" },
      { content: "[]", color: "#e6edf3" },
      { content: " ", color: "#e6edf3" },
      { content: "arr", color: "#e6edf3" },
      { content: ")", color: "#e6edf3" },
      { content: " {", color: "#e6edf3" },
    ],
    // Line 1: "  return;"
    [
      { content: "  ", color: "#e6edf3" },
      { content: "return", color: "#ff7b72" },
      { content: ";", color: "#e6edf3" },
    ],
    // Line 2: "}"
    [
      { content: "}", color: "#e6edf3" },
    ],
  ],
  // ... theme metadata
}
```

Each line is an array of tokens. Each token has `content` (the text) and `color` (hex colour from the theme). You render each token as a `<span>` with that colour.

## 14.6 Build the new CodePanel

Replace `app/algorithms/components/CodePanel.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { getHighlighter } from "../lib/highlighter";

type ShikiToken = {
  content: string;
  color: string;
};

type CodePanelProps = {
  code: string[];
  currentLine: number;
  language: "java" | "python";
};

export default function CodePanel({ code, currentLine, language }: CodePanelProps) {
  const [tokenLines, setTokenLines] = useState<ShikiToken[][] | null>(null);

  useEffect(() => {
    let cancelled = false;

    getHighlighter().then((highlighter) => {
      if (cancelled) return;

      const result = highlighter.codeToTokens(code.join("\n"), {
        lang: language,
        theme: "github-dark",
      });

      setTokenLines(
        result.tokens.map((line) =>
          line.map((token) => ({
            content: token.content,
            color: token.color || "#e6edf3",
          }))
        )
      );
    });

    return () => {
      cancelled = true;
    };
  }, [code, language]);

  return (
    <div className="flex-1 overflow-auto bg-gray-900 p-4 rounded-lg">
      <pre className="text-sm font-mono leading-relaxed">
        {code.map((line, index) => (
          <div
            key={index}
            className={`px-2 py-0.5 rounded ${
              index === currentLine
                ? "bg-yellow-500/20 border-l-2 border-yellow-400"
                : "border-l-2 border-transparent"
            }`}
          >
            {/* Line number */}
            <span className="text-gray-500 mr-4 select-none text-xs">
              {String(index + 1).padStart(2, " ")}
            </span>

            {/* Highlighted tokens (or fallback to plain text while loading) */}
            {tokenLines?.[index]
              ? tokenLines[index].map((token, tokenIdx) => (
                  <span key={tokenIdx} style={{ color: token.color }}>
                    {token.content}
                  </span>
                ))
              : <span className="text-gray-100">{line}</span>
            }
          </div>
        ))}
      </pre>
    </div>
  );
}
```

### What changed from the old CodePanel:

| Before (hand-built) | After (Shiki) |
|---------------------|---------------|
| `import { tokenise } from "../lib/tokenise"` | `import { getHighlighter } from "../lib/highlighter"` |
| `tokenise(line, language)` per line, synchronous | `codeToTokens(allCode)` once, async |
| Tailwind classes for colours (`text-purple-400`) | Inline `style={{ color }}` from theme |
| Limited to Java/Python keywords | 200+ languages, perfect accuracy |

### What stays the same:

- Line numbers on the left
- Active line highlight (yellow background + left border)
- The component props interface (`code`, `currentLine`, `language`)
- The overall layout structure

## 14.7 The loading pattern

Notice the fallback:

```tsx
{tokenLines?.[index]
  ? tokenLines[index].map(...)   // ← Shiki tokens (coloured)
  : <span className="text-gray-100">{line}</span>  // ← plain text (white)
}
```

On first render, `tokenLines` is `null` — the highlighter hasn't loaded yet. The user sees plain white text for ~100-200ms. Then Shiki finishes, state updates, and colours appear.

This is imperceptible in practice. But if you want instant highlighting, you can:

1. **Pre-highlight at build time** (server component or `getStaticProps`)
2. **Pre-highlight in the step generator** and store tokens alongside the code

> **Why not use `React.use()` (Suspense)?** You could wrap `getHighlighter()` in a Suspense boundary. But our component is `"use client"` (needs `useState` for steps), and mixing async server data with client interactivity adds complexity. The `useEffect` pattern is simpler here.

## 14.8 Adding more languages

When you add a new algorithm language (say JavaScript or C++):

```ts
// Option A: Add at creation time (in highlighter.ts)
highlighterPromise = createHighlighter({
  themes: ["github-dark"],
  langs: ["java", "python", "javascript", "cpp"],
});

// Option B: Load on demand (anywhere)
const highlighter = await getHighlighter();
await highlighter.loadLanguage("javascript");
```

Option B is better for bundle size — you only load grammars you actually use.

Update the `CodePanelProps` type:

```ts
type CodePanelProps = {
  code: string[];
  currentLine: number;
  language: "java" | "python" | "javascript" | "cpp";
};
```

## 14.9 Switching themes

Shiki includes many themes. Popular dark themes:

| Theme | Style |
|-------|-------|
| `github-dark` | GitHub's dark mode (what we use) |
| `one-dark-pro` | Atom's One Dark |
| `dracula` | Purple-heavy dark theme |
| `tokyo-night` | Blue-ish dark theme |
| `vitesse-dark` | Minimal, muted colours |

To switch:

```ts
// In highlighter.ts — load the theme
highlighterPromise = createHighlighter({
  themes: ["github-dark", "one-dark-pro"],
  langs: ["java", "python"],
});

// In CodePanel — use it
const result = highlighter.codeToTokens(code.join("\n"), {
  lang: language,
  theme: "one-dark-pro",  // ← change here
});
```

To support user-selectable themes, pass the theme name as a prop and include multiple themes at creation time.

## 14.10 Dual themes (light + dark mode)

If your app supports light/dark mode:

```ts
const result = highlighter.codeToTokens(code.join("\n"), {
  lang: language,
  themes: {
    light: "github-light",
    dark: "github-dark",
  },
});

// Each token now has: token.htmlStyle (CSS variables for both themes)
```

Then use CSS variables that swap based on your theme class:

```tsx
<span style={token.htmlStyle}>{token.content}</span>
```

This is more advanced — stick with a single dark theme until you need it.

## 14.11 Performance considerations

| Concern | Solution |
|---------|----------|
| First load is slow (~200ms) | Singleton pattern — pay once, reuse forever |
| Re-tokenising on every step | Only re-tokenise when `code` or `language` changes, NOT on `currentLine` change |
| Large code blocks (100+ lines) | `codeToTokens` handles this fine — it's fast after first load |
| Bundle size | Shiki lazy-loads grammars/themes — only what you use is downloaded |
| Memory | One highlighter instance uses ~5MB. Negligible for a desktop browser. |

The key optimisation is in the `useEffect` dependency array:

```tsx
useEffect(() => {
  // Only runs when code or language changes
  // Does NOT run when currentLine changes (that's just CSS)
}, [code, language]);
```

Stepping through algorithm states changes `currentLine` (60 times per sorting run). The tokens stay the same — only the yellow highlight moves. No re-tokenisation needed.

## 14.12 Cleaning up the old tokeniser

Once Shiki is working, you can remove:

- `app/algorithms/lib/tokenise.ts` — no longer needed
- The `TOKEN_COLOURS` mapping — Shiki provides colours from the theme
- The `Token` type export — replaced by Shiki's token format

Or keep `tokenise.ts` as a fallback for environments where Shiki can't load (tests, SSR without await).

## 14.13 Full working example

Here's everything together — copy-paste ready:

**`app/algorithms/lib/highlighter.ts`**:

```ts
import { createHighlighter, type Highlighter } from "shiki";

let highlighterPromise: Promise<Highlighter> | null = null;

export function getHighlighter(): Promise<Highlighter> {
  if (!highlighterPromise) {
    highlighterPromise = createHighlighter({
      themes: ["github-dark"],
      langs: ["java", "python"],
    });
  }
  return highlighterPromise;
}
```

**`app/algorithms/components/CodePanel.tsx`**:

```tsx
"use client";

import { useEffect, useState } from "react";
import { getHighlighter } from "../lib/highlighter";

type ShikiToken = {
  content: string;
  color: string;
};

type CodePanelProps = {
  code: string[];
  currentLine: number;
  language: "java" | "python";
};

export default function CodePanel({ code, currentLine, language }: CodePanelProps) {
  const [tokenLines, setTokenLines] = useState<ShikiToken[][] | null>(null);

  useEffect(() => {
    let cancelled = false;

    getHighlighter().then((highlighter) => {
      if (cancelled) return;

      const result = highlighter.codeToTokens(code.join("\n"), {
        lang: language,
        theme: "github-dark",
      });

      setTokenLines(
        result.tokens.map((line) =>
          line.map((token) => ({
            content: token.content,
            color: token.color || "#e6edf3",
          }))
        )
      );
    });

    return () => {
      cancelled = true;
    };
  }, [code, language]);

  return (
    <div className="flex-1 overflow-auto bg-gray-900 p-4 rounded-lg">
      <pre className="text-sm font-mono leading-relaxed">
        {code.map((line, index) => (
          <div
            key={index}
            className={`px-2 py-0.5 rounded ${
              index === currentLine
                ? "bg-yellow-500/20 border-l-2 border-yellow-400"
                : "border-l-2 border-transparent"
            }`}
          >
            <span className="text-gray-500 mr-4 select-none text-xs">
              {String(index + 1).padStart(2, " ")}
            </span>
            {tokenLines?.[index]
              ? tokenLines[index].map((token, tokenIdx) => (
                  <span key={tokenIdx} style={{ color: token.color }}>
                    {token.content}
                  </span>
                ))
              : <span className="text-gray-100">{line}</span>
            }
          </div>
        ))}
      </pre>
    </div>
  );
}
```

## 14.14 Testing it works

1. Run `npm run dev`
2. Visit `/algorithms`
3. You should see the bubble sort Java code with:
   - Keywords (`public`, `void`, `for`, `if`) in red/orange
   - Types (`int`) in red
   - Method names in purple
   - Strings in light blue
   - The active line highlighted in yellow

Compare with VS Code — the colours should match (since they use the same grammar files).

## Summary

✅ You installed Shiki and created a singleton highlighter
✅ You understand `codeToTokens()` — the per-line token API
✅ You replaced the hand-built tokeniser with production-grade highlighting
✅ You kept the active-line feature working (it's just CSS, independent of tokens)
✅ You know how to add languages, switch themes, and handle the async load
✅ You understand the performance model (tokenise once, highlight line is free)

## Key takeaway

**Shiki gives you VS Code-quality highlighting with one function call.** The trick for interactive use (like our step engine) is `codeToTokens()` — it gives you raw tokens instead of HTML, so you keep full control over rendering. Tokenise when the code changes, not when the step changes.

---

→ [Back to Chapter 04: Displaying Code](./04-DISPLAYING-CODE.md)
