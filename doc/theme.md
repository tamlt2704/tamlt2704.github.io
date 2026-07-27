# Adding Dark/Light Theme — Step by Step

---

## How It Works (Big Picture)

1. A `class` on `<html>` controls the theme: `<html class="dark">` or `<html class="">`
2. Tailwind's `dark:` prefix applies styles only when that class is present
3. `next-themes` library handles toggling + saving the user's choice to localStorage

---

## Step 1: Install next-themes

```bash
npm install next-themes
```

This is a tiny library (~2KB) that:

- Adds/removes the `dark` class on `<html>`
- Saves the user's choice in localStorage
- Respects their OS preference on first visit
- Prevents a flash of wrong theme on page load

---

## Step 2: Create a Theme Provider

### What is a Provider?

Imagine your app is a building with many rooms (components). Each room might need to know the current theme — the navbar, the page, the footer, a button deep inside a form.

**Without a Provider:** You'd have to pass `theme` as a prop down through every level:

```
Layout → Navbar → Button (needs theme)
Layout → Page → Card → Text (needs theme)
Layout → Footer → Link (needs theme)
```

Every component in the chain has to accept and forward the prop, even if it doesn't use it. This is called "prop drilling" — tedious and fragile.

**With a Provider:** You wrap your app once, and any component anywhere can access the theme directly:

```
ThemeProvider (holds the theme value)
  └── Navbar → just grabs theme ✓
  └── Page → Card → Text → just grabs theme ✓
  └── Footer → just grabs theme ✓
```

It's like a building-wide announcement system. Instead of passing notes room to room, you broadcast and any room can listen.

### How it works in React

React calls this pattern **Context**. A Provider is a component that:

1. **Holds shared state** (e.g. `theme = "dark"`)
2. **Wraps child components** (everything inside it can access that state)
3. **Provides a hook** to read/update the state (e.g. `useTheme()`)

```tsx
// 1. Provider wraps the app (holds the data)
;<ThemeProvider>
  <App />
</ThemeProvider>

// 2. Any component inside grabs the data
function AnyComponent() {
  const { theme, setTheme } = useTheme() // ← reads from the Provider
}
```

### Why it needs "use client"

Providers use React state and effects (`useState`, `useEffect`). These only work in the browser, not on the server. `"use client"` tells Next.js: "this component runs in the browser."

**But child components can still be Server Components.** Only the Provider itself needs `"use client"` — the pages and components inside it don't need it unless they also use hooks.

### Common Providers you'll see in Next.js apps

| Provider                            | What it shares                               |
| ----------------------------------- | -------------------------------------------- |
| `ThemeProvider`                     | Current theme (dark/light) + toggle function |
| `SessionProvider` (next-auth)       | Logged-in user info                          |
| `QueryClientProvider` (react-query) | Cache for API requests                       |
| `Toaster/ToastProvider`             | Toast notification system                    |

They all follow the same pattern: wrap once at the top, use anywhere inside.

### The actual code

Create `components/theme-provider.tsx`:

```tsx
"use client"

import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </NextThemesProvider>
  )
}
```

**Breaking this down:**

| Part                    | What it means                                                |
| ----------------------- | ------------------------------------------------------------ |
| `"use client"`          | This component runs in the browser                           |
| `{ children }`          | Whatever you put inside `<ThemeProvider>...</ThemeProvider>` |
| `NextThemesProvider`    | The actual Provider from the library                         |
| `attribute="class"`     | It will add `class="dark"` to `<html>`                       |
| `defaultTheme="system"` | First visit = follow OS preference                           |
| `enableSystem`          | Reacts to OS dark mode changes live                          |

**Why we make our own wrapper instead of using `NextThemesProvider` directly?**

Because we need `"use client"` on it, and it's cleaner to do that in a separate file than adding it to your `layout.tsx` (which is a Server Component by default).

**What `{ children }` means:**

```tsx
<ThemeProvider>
  <Navbar /> ← these are the "children"
  <main>...</main> ← these too
</ThemeProvider>
```

`children` is a special React prop — it's whatever you put between the opening and closing tags.

---

## Step 3: Wrap Your App with the Provider

Update `app/layout.tsx`:

```tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <Navbar />
          <main>{children}</main>
        </ThemeProvider>
      </body>
    </html>
  )
}
```

**Why `suppressHydrationWarning`?**

`next-themes` adds the `dark` class to `<html>` on the client (after checking localStorage). This causes a tiny mismatch between server HTML and client HTML. `suppressHydrationWarning` tells React that's expected — it's not a bug.

---

## Step 4: Create a Theme Toggle Button

Create `components/theme-toggle.tsx`:

```tsx
"use client"

import { useTheme } from "next-themes"
import { Sun, Moon } from "lucide-react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label="Toggle theme">
      <Sun className="h-5 w-5 dark:hidden" />
      <Moon className="hidden h-5 w-5 dark:block" />
    </button>
  )
}
```

**How the icon swap works:**

- `<Sun>` has `dark:hidden` — visible in light mode, hidden in dark mode
- `<Moon>` has `hidden dark:block` — hidden in light mode, visible in dark mode
- No JavaScript needed for the swap — pure CSS with Tailwind's `dark:` prefix

### Understanding `display` (what `hidden`, `block`, `flex` actually do)

Every HTML element has a `display` value that controls two things:

1. **Is it visible?**
2. **How does it behave in the layout?**

**The main values:**

| Tailwind       | CSS                     | Visible? | Layout behaviour                                                                                    |
| -------------- | ----------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| `hidden`       | `display: none`         | ❌ No    | Gone. Takes no space. Other elements act like it doesn't exist.                                     |
| `block`        | `display: block`        | ✅ Yes   | Takes the full width. Next element goes below it.                                                   |
| `inline`       | `display: inline`       | ✅ Yes   | Only takes the width of its content. Sits next to other inline elements (like words in a sentence). |
| `inline-block` | `display: inline-block` | ✅ Yes   | Like inline, but you can set width/height on it.                                                    |
| `flex`         | `display: flex`         | ✅ Yes   | Children arranged in a row (or column). You get alignment tools.                                    |
| `grid`         | `display: grid`         | ✅ Yes   | Children arranged in a 2D grid (rows + columns).                                                    |

**Visual example:**

```
block elements:
┌──────────────────────────────────┐
│ Block 1 (full width)             │
└──────────────────────────────────┘
┌──────────────────────────────────┐
│ Block 2 (full width)             │
└──────────────────────────────────┘

inline elements:
[Inline 1] [Inline 2] [Inline 3] ← sit side by side

flex container:
┌──────────────────────────────────┐
│ [Child 1] [Child 2] [Child 3]   │ ← flex arranges them in a row
└──────────────────────────────────┘

hidden:
(nothing — the element is gone from the page)
```

**Why `hidden` + `dark:block` works for the icon swap:**

```
Light mode:
  Sun  → display: (default = inline/block) → ✅ visible
  Moon → display: none (hidden)            → ❌ gone

Dark mode:
  Sun  → display: none (dark:hidden)       → ❌ gone
  Moon → display: block (dark:block)       → ✅ visible
```

Both icons exist in the HTML, but only one is displayed at a time. The swap is instant because there's no JavaScript waiting — CSS applies immediately.

**`hidden` vs `invisible`:**

| Tailwind    | CSS                  | What it does                                                 |
| ----------- | -------------------- | ------------------------------------------------------------ |
| `hidden`    | `display: none`      | Element is gone — takes no space                             |
| `invisible` | `visibility: hidden` | Element is invisible but still takes up space (leaves a gap) |

```
hidden:    [A]     [C]        ← B is gone, C moves over
invisible: [A] [      ] [C]   ← B is invisible but still takes space
```

Use `hidden` when you want the element completely removed from layout (like our icon swap). Use `invisible` when you want to reserve the space.

---

## Step 5: Add the Toggle to Your Navbar

In your navbar, add `<ThemeToggle />` next to the other buttons:

```tsx
import { ThemeToggle } from "@/components/theme-toggle"

// Inside the nav bar, in the right-side area:
;<div className="ml-auto flex items-center gap-2">
  <ThemeToggle />
  {/* ... other buttons */}
</div>
```

---

## Step 6: Add Dark Mode Colors

Now use `dark:` prefix on your elements. Start with the basics:

**Navbar:**

```tsx
<nav className="sticky top-0 border-b bg-white dark:bg-gray-950 dark:border-gray-800">
```

**Links:**

```tsx
<Link className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white">
```

**Page background (in `globals.css` or layout):**

```tsx
<body className="bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100">
```

---

## Step 7: Use CSS Variables (Cleaner Approach)

Instead of writing `dark:` on every element, define theme colors once in `globals.css`:

```css
@import "tailwindcss";

:root {
  --background: #ffffff;
  --foreground: #171717;
  --muted: #6b7280;
  --border: #e5e7eb;
}

.dark {
  --background: #0a0a0a;
  --foreground: #ededed;
  --muted: #9ca3af;
  --border: #27272a;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-muted: var(--muted);
  --color-border: var(--border);
}
```

Now use them without `dark:` prefix:

```tsx
<nav className="border-b border-border bg-background">
<Link className="text-muted hover:text-foreground">
<body className="bg-background text-foreground">
```

**Benefit:** Change theme colors in one place. Components don't need to know about dark mode — they just use `bg-background`, `text-foreground`, etc.

---

## Step 8: Handle the Flash Problem

Without extra care, users might see a flash of the wrong theme on page load (light flashes before dark kicks in). `next-themes` handles this with a script it injects, but you can also add:

In `app/layout.tsx`, on the `<html>` tag:

```tsx
<html lang="en" suppressHydrationWarning>
```

And make sure `ThemeProvider` wraps everything inside `<body>` (not outside `<html>`).

---

## Step 9: Three-Way Toggle (Light / Dark / System)

If you want users to choose "follow my OS" as an option:

```tsx
"use client"

import { useTheme } from "next-themes"
import { Sun, Moon, Monitor } from "lucide-react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="flex items-center gap-1 rounded-md border p-1">
      <button
        onClick={() => setTheme("light")}
        className={`rounded p-1 ${theme === "light" ? "bg-gray-200 dark:bg-gray-700" : ""}`}
        aria-label="Light mode"
      >
        <Sun className="h-4 w-4" />
      </button>
      <button
        onClick={() => setTheme("dark")}
        className={`rounded p-1 ${theme === "dark" ? "bg-gray-200 dark:bg-gray-700" : ""}`}
        aria-label="Dark mode"
      >
        <Moon className="h-4 w-4" />
      </button>
      <button
        onClick={() => setTheme("system")}
        className={`rounded p-1 ${theme === "system" ? "bg-gray-200 dark:bg-gray-700" : ""}`}
        aria-label="System theme"
      >
        <Monitor className="h-4 w-4" />
      </button>
    </div>
  )
}
```

---

## Summary of What You Installed/Created

| File                            | Purpose                                         |
| ------------------------------- | ----------------------------------------------- |
| `next-themes` (npm)             | Manages theme state, localStorage, OS detection |
| `components/theme-provider.tsx` | Wraps app with theme context                    |
| `components/theme-toggle.tsx`   | Button to switch themes                         |
| `globals.css`                   | CSS variables for light/dark colors             |

---

## How Tailwind Dark Mode Works

```
User clicks toggle
       ↓
next-themes sets theme in localStorage
       ↓
next-themes adds class="dark" to <html>
       ↓
Tailwind sees .dark on <html>
       ↓
All dark: prefixed styles activate
       ↓
CSS variables under .dark {} take effect
       ↓
Page re-renders with dark colors
```

---

## Common Mistakes

| Mistake                            | Fix                                                                                             |
| ---------------------------------- | ----------------------------------------------------------------------------------------------- |
| Flash of light theme on reload     | Make sure `ThemeProvider` is in layout and `suppressHydrationWarning` is on `<html>`            |
| `dark:` classes not working        | Check Tailwind config uses `class` strategy (default in v4)                                     |
| Toggle doesn't work on first click | `useTheme()` returns `undefined` on first render — add a mounted check (see below)              |
| Colors look wrong                  | Make sure you use `bg-background` / `text-foreground` (not hardcoded `bg-white` / `text-black`) |
| Icons/navbar faint in dark mode    | Replace hardcoded colors with CSS variable classes (see table below)                            |
| 404 page ignores theme             | The default Next.js 404 renders outside your layout — create a custom one (see below)           |

### Use CSS Variable Classes (Not Hardcoded Colors)

| Instead of         | Use                     |
| ------------------ | ----------------------- |
| `bg-white`         | `bg-background`         |
| `text-black`       | `text-foreground`       |
| `text-gray-600`    | `text-muted-foreground` |
| `hover:text-black` | `hover:text-foreground` |
| `border-gray-200`  | `border-border`         |

These read from `globals.css` — `:root` for light, `.dark` for dark. No `dark:` prefix needed.

### Custom 404 Page (So Theme Works)

The default Next.js 404 page doesn't go through your layout's `ThemeProvider`. Create `app/not-found.tsx` so it renders inside your layout:

```tsx
export default function NotFound() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4 py-12">
      <h1 className="text-foreground text-4xl font-bold">404</h1>
      <p className="text-muted-foreground mt-2">Page not found.</p>
    </div>
  )
}
```

Since this file is inside `app/`, it renders within your `RootLayout` — `ThemeProvider` wraps it and CSS variables work.

### Mounted Check (if toggle flickers)

```tsx
"use client"

import { useTheme } from "next-themes"
import { useEffect, useState } from "react"
import { Sun, Moon } from "lucide-react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])

  if (!mounted) return null // avoid hydration mismatch

  return (
    <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
      {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </button>
  )
}
```

**Why?** On the server, `next-themes` doesn't know the theme yet (it's in localStorage). So `theme` is `undefined` on the first render. The mounted check waits until the client knows the real theme before showing the button.
