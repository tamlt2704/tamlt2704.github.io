# Chapter 8: Dark Mode That Doesn't Flash

[← Chapter 7: Finishing Touches](/blog/nextjs-ghpages/chapter-07-finishing-touches) | [Chapter 9: Streaming on Static →](/blog/nextjs-ghpages/chapter-09-streaming)

---

## The Problem

It's 11 PM. Your reader opens your blog. White background. Retinas scorched. They close the tab.

Dark mode isn't a luxury — it's table stakes. But implementing it wrong gives you the dreaded "white flash" on page load: the page renders light, then JavaScript kicks in and switches to dark. Jarring.

We need dark mode that:

1. Respects the system preference by default
2. Lets users toggle manually
3. Persists their choice across visits
4. Never flashes the wrong theme

## The Strategy

The trick: apply the theme **before React hydrates**. That means a tiny inline script in `<head>` that reads localStorage and sets a class on `<html>` — before any CSS paints.

## Step 1: Tailwind Dark Mode

Tailwind supports dark mode via a class on `<html>`:

```css
/* app/globals.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";

@custom-variant dark (&:where(.dark, .dark *));
```

Now any `dark:` prefix works when `<html class="dark">` is set:

```tsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
```

## Step 2: The Anti-Flash Script

The problem: React hydrates _after_ the browser paints. If the user prefers dark mode, they'll see a white flash before JavaScript adds the `dark` class. The fix: inject a tiny script in `<head>` that runs _before_ any CSS paints.

Create `app/theme-script.tsx`:

```tsx
/**
 * This component outputs a <script> tag that runs BEFORE the page renders.
 * It checks localStorage and system preference, then adds "dark" class to <html>.
 * Because it's in <head>, it executes before any CSS is applied — no flash.
 */
export function ThemeScript() {
  // This string becomes inline JavaScript in the HTML <head>
  const script = `
    (function() {
      try {
        // Check if user previously chose a theme
        var stored = localStorage.getItem('theme');
        // Check if their OS/browser prefers dark mode
        var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        // Use stored preference, or fall back to system preference
        var dark = stored === 'dark' || (!stored && prefersDark);
        // Add the class BEFORE any CSS renders — prevents white flash
        if (dark) document.documentElement.classList.add('dark');
      } catch(e) {}  // Silently fail if localStorage is blocked (private browsing)
    })();
  `;
  // dangerouslySetInnerHTML injects raw HTML — needed for inline scripts
  // It's "dangerous" because it bypasses React's XSS protection, but here we control the content
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
```

**Why not just use `useEffect`?** Because `useEffect` runs _after_ the component renders. By then, the browser has already painted the white background. This inline script runs synchronously in `<head>`, before any paint happens.

Add it to `app/layout.tsx`:

```tsx
import { ThemeScript } from "./theme-script";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body className="bg-white text-gray-900 transition-colors dark:bg-gray-900 dark:text-gray-100">
        {children}
      </body>
    </html>
  );
}
```

The script runs **synchronously** before the browser paints. No flash.

`suppressHydrationWarning` tells React not to complain about the class mismatch between server render (no class) and client (has `dark` class).

## Step 3: The Toggle Button

Create `app/components/ThemeToggle.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  return (
    <button
      onClick={toggle}
      className="rounded-md p-2 transition hover:bg-gray-100 dark:hover:bg-gray-800"
      aria-label="Toggle theme"
    >
      {dark ? "☀️" : "🌙"}
    </button>
  );
}
```

Drop it in your navbar. One click toggles. Choice persists in localStorage.

## Step 4: Dark Prose Styles

Update your article wrapper:

```tsx
<div className="prose prose-lg dark:prose-invert max-w-none">
  <MDXRemote ... />
</div>
```

`dark:prose-invert` flips all typography colors for dark mode. Headings, paragraphs, links, blockquotes — all handled.

## Step 5: Dark Code Blocks

Your `MarkdownCode.tsx` already uses `oneDark` (a dark theme). For light mode, swap themes:

```tsx
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";

export function MarkdownCode({ children, className }: Props) {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const check = () => setIsDark(document.documentElement.classList.contains("dark"));
    check();
    const observer = new MutationObserver(check);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

  // ... rest of component
  return (
    <SyntaxHighlighter
      language={lang}
      style={isDark ? oneDark : oneLight}
      // ...
    >
      {code}
    </SyntaxHighlighter>
  );
}
```

A `MutationObserver` watches the `<html>` class. When it changes, code blocks re-render with the matching theme. Instant, no page reload.

## Step 6: Dark Interactive Components

Update Quiz, CodePlayground, StepVisualizer with dark variants:

```tsx
// Quiz.tsx — just add dark: classes
<div className="my-8 p-6 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
  <p className="font-semibold text-gray-900 dark:text-gray-100">{question}</p>
  ...
</div>

// CodePlayground.tsx
<textarea className="bg-gray-900 text-gray-100" /> {/* already dark */}
<div className="bg-gray-100 dark:bg-gray-800 border-t dark:border-gray-700">
  ...
</div>
```

Since the editor is always dark (code looks better that way), only the controls and output need dark variants.

## The Result

- First visit: system preference applied instantly (no flash)
- Toggle: instant switch, persisted
- Code blocks: theme-aware
- Interactive components: dark-ready
- Zero external libraries

---

## What's Next

Dark mode is visual polish. Chapter 9 tackles something more ambitious: can we get streaming-like behavior on a static site? Progressive content loading, skeleton states, and the illusion of server-side streaming — all from GitHub Pages.
