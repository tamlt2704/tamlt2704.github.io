# Chapter 7: Dark Mode — Light and Dark, Seamlessly

[← Chapter 6: States & Transitions](chapter-06-states-transitions.md) | [Chapter 8: Animations →](chapter-08-animations.md)

---

## The Task

Sora: "Dark mode isn't optional anymore. Every user expects it. The dashboard needs to look great in both. And it should respect system preference by default, with a manual toggle override."

---

## How Dark Mode Works

Tailwind's `dark:` variant applies styles when dark mode is active:

```html
<div class="bg-white dark:bg-gray-900">
  <h1 class="text-gray-900 dark:text-white">Title</h1>
  <p class="text-gray-600 dark:text-gray-300">Body text</p>
</div>
```

Read it as: "white background normally, gray-900 background in dark mode."

---

## Dark Mode Strategies

Tailwind v4 uses the `prefers-color-scheme` media query by default. To use class-based toggling (for a manual switch), add to your CSS:

```css
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));
```

Now dark mode activates when a parent element has the `dark` class:

```html
<!-- Add "dark" class to html or body to enable dark mode -->
<html class="dark">
  <body class="bg-white dark:bg-gray-950">
    ...
  </body>
</html>
```

---

## The Toggle Logic

```tsx
import { useState, useEffect } from 'react';

function useTheme() {
  const [theme, setTheme] = useState(() => {
    // Check localStorage first, then system preference
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme');
      if (stored) return stored;
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggle = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return { theme, toggle };
}
```

The toggle button:

```tsx
function ThemeToggle() {
  const { theme, toggle } = useTheme();

  return (
    <button
      onClick={toggle}
      className="p-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800 transition-colors"
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}
```

---

## The Dark Mode Color System

Sora's mapping:

```
────────────────────────────────────────────────────────────
 Element          │ Light              │ Dark
────────────────────────────────────────────────────────────
 Page background  │ bg-gray-50         │ dark:bg-gray-950
 Card background  │ bg-white           │ dark:bg-gray-900
 Card border      │ border-gray-200    │ dark:border-gray-800
 Primary text     │ text-gray-900      │ dark:text-white
 Secondary text   │ text-gray-600      │ dark:text-gray-400
 Muted text       │ text-gray-400      │ dark:text-gray-500
 Input background │ bg-white           │ dark:bg-gray-800
 Input border     │ border-gray-300    │ dark:border-gray-700
 Hover background │ hover:bg-gray-50   │ dark:hover:bg-gray-800
 Dividers         │ divide-gray-200    │ dark:divide-gray-800
────────────────────────────────────────────────────────────
```

The pattern: in dark mode, backgrounds go dark (800-950), text goes light (white, gray-300), borders go subtle (700-800).

---

## Converting the Metric Card

Before (light only):

```tsx
<div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
  <p className="text-sm text-gray-500 font-medium">{title}</p>
  <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
</div>
```

After (light + dark):

```tsx
<div className="bg-white dark:bg-gray-900 rounded-lg p-6 shadow-sm border border-gray-100 dark:border-gray-800">
  <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">{title}</p>
  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{value}</p>
</div>
```

---

## Using CSS Variables for Semantic Colors

Instead of adding `dark:` to every element, use CSS variables for a cleaner approach:

```css
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --color-surface: #ffffff;
  --color-surface-raised: #f9fafb;
  --color-on-surface: #111827;
  --color-on-surface-muted: #6b7280;
  --color-border: #e5e7eb;
  --color-border-subtle: #f3f4f6;
}

.dark {
  --color-surface: #030712;
  --color-surface-raised: #111827;
  --color-on-surface: #f9fafb;
  --color-on-surface-muted: #9ca3af;
  --color-border: #1f2937;
  --color-border-subtle: #1f2937;
}
```

Now use semantic names — no `dark:` prefix needed:

```html
<div class="bg-surface border-border rounded-lg p-6">
  <p class="text-on-surface-muted text-sm">{title}</p>
  <p class="text-on-surface text-3xl font-bold">{value}</p>
</div>
```

The component doesn't know about dark mode. The CSS variables handle it.

---

## The Full Dashboard in Dark Mode

```tsx
function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 lg:px-6">
          <div className="flex items-center justify-between h-16">
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              Pixelflow
            </span>
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-sm font-medium">
                S
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Sidebar */}
      <div className="flex">
        <aside className="hidden lg:block w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 min-h-[calc(100vh-4rem)]">
          <nav className="p-4 flex flex-col gap-1">
            <NavItem active>Dashboard</NavItem>
            <NavItem>Analytics</NavItem>
            <NavItem>Team</NavItem>
          </nav>
        </aside>

        <main className="flex-1 p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

function NavItem({ children, active }) {
  return (
    <a
      href="#"
      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
        active
          ? "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white"
          : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
      }`}
    >
      {children}
    </a>
  );
}
```

---

## Dark Mode for Images & Media

```html
<!-- Invert diagrams/logos that are dark-on-light -->
<img src="logo.svg" class="dark:invert" />

<!-- Different images for light/dark -->
<img src="chart-light.png" class="dark:hidden" />
<img src="chart-dark.png" class="hidden dark:block" />

<!-- Reduce brightness of photos in dark mode -->
<img src="photo.jpg" class="dark:brightness-90" />
```

---

## Preventing Flash of Wrong Theme

The theme toggle uses localStorage, but there's a flash of light mode on page load. Fix with a script in `<head>`:

```html
<head>
  <script>
    // Runs before page renders — prevents flash
    if (localStorage.theme === 'dark' ||
        (!localStorage.theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    }
  </script>
</head>
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Classes
────────────────────────────────┼──────────────────────────────────────
Dark background                 │ bg-white dark:bg-gray-900
Dark text                       │ text-gray-900 dark:text-white
Dark border                     │ border-gray-200 dark:border-gray-800
Dark hover                      │ hover:bg-gray-50 dark:hover:bg-gray-800
Dark + state combo              │ dark:hover:bg-gray-700
Invert for dark                 │ dark:invert
Hide in dark                    │ dark:hidden
Show in dark                    │ hidden dark:block
Semantic variables              │ Define in @theme + override in .dark
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "Dark mode is in. Now I need things to move. Loading spinners, skeleton screens, hover animations that feel alive. The dashboard should feel responsive to every interaction."

Animations, keyframes, and micro-interactions.

---

[← Chapter 6: States & Transitions](chapter-06-states-transitions.md) | [Chapter 8: Animations →](chapter-08-animations.md)
