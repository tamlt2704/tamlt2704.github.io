# Chapter 12: Design Tokens & Custom Theme

[← Chapter 11: Component Patterns](chapter-11-component-patterns.md) | [Chapter 13: Plugins →](chapter-13-plugins.md)

---

## The Task

Sora: "I want the design system locked down. Custom fonts, a spacing scale that matches our 8px grid exactly, brand colors with semantic names, custom breakpoints for our target devices. Everything in one place."

---

## The @theme Directive (Tailwind v4)

In Tailwind v4, customization lives in your CSS using `@theme`:

```css
@import "tailwindcss";

@theme {
  /* ── Fonts ─────────────────────────────── */
  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;
  --font-display: "Cal Sans", "Inter", sans-serif;

  /* ── Colors: Brand ─────────────────────── */
  --color-brand-50: #eef2ff;
  --color-brand-100: #e0e7ff;
  --color-brand-200: #c7d2fe;
  --color-brand-300: #a5b4fc;
  --color-brand-400: #818cf8;
  --color-brand-500: #6366f1;
  --color-brand-600: #4f46e5;
  --color-brand-700: #4338ca;
  --color-brand-800: #3730a3;
  --color-brand-900: #312e81;
  --color-brand-950: #1e1b4b;

  /* ── Colors: Accent ────────────────────── */
  --color-accent-50: #fffbeb;
  --color-accent-500: #f59e0b;
  --color-accent-600: #d97706;

  /* ── Colors: Semantic ──────────────────── */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  /* ── Spacing (8px grid) ────────────────── */
  --spacing-0: 0px;
  --spacing-0.5: 2px;
  --spacing-1: 4px;
  --spacing-1.5: 6px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;
  --spacing-16: 64px;
  --spacing-20: 80px;
  --spacing-24: 96px;

  /* ── Border Radius ─────────────────────── */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-full: 9999px;

  /* ── Shadows ───────────────────────────── */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);

  /* ── Breakpoints ───────────────────────── */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;

  /* ── Animations ────────────────────────── */
  --animate-fade-in: fade-in 0.3s ease-out;
  --animate-slide-up: slide-up 0.3s ease-out;
  --animate-scale-in: scale-in 0.2s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

Everything defined in `@theme` becomes available as utilities:
- `--color-brand-500` → `bg-brand-500`, `text-brand-500`, `border-brand-500`
- `--font-display` → `font-display`
- `--spacing-8` → `p-8`, `m-8`, `gap-8`, `w-8`, `h-8`
- `--radius-lg` → `rounded-lg`
- `--animate-fade-in` → `animate-fade-in`

---

## Custom Fonts

Load fonts in your HTML or CSS, then reference them in `@theme`:

```html
<!-- In your HTML head -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Use in markup:

```html
<h1 class="font-display text-4xl font-bold">Display Heading</h1>
<p class="font-sans text-base">Body text in Inter</p>
<code class="font-mono text-sm">Code in JetBrains Mono</code>
```

---

## Semantic Color Tokens with Dark Mode

Define semantic tokens that change with theme:

```css
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

@theme {
  /* Semantic surface colors */
  --color-surface: var(--surface);
  --color-surface-raised: var(--surface-raised);
  --color-surface-overlay: var(--surface-overlay);
  --color-on-surface: var(--on-surface);
  --color-on-surface-muted: var(--on-surface-muted);
  --color-border-default: var(--border-default);
  --color-border-subtle: var(--border-subtle);
}

:root {
  --surface: #ffffff;
  --surface-raised: #f9fafb;
  --surface-overlay: #ffffff;
  --on-surface: #111827;
  --on-surface-muted: #6b7280;
  --border-default: #e5e7eb;
  --border-subtle: #f3f4f6;
}

.dark {
  --surface: #0a0a0a;
  --surface-raised: #171717;
  --surface-overlay: #1f1f1f;
  --on-surface: #fafafa;
  --on-surface-muted: #a3a3a3;
  --border-default: #262626;
  --border-subtle: #1a1a1a;
}
```

Now components don't need `dark:` prefixes:

```html
<div class="bg-surface border-border-default rounded-lg p-6">
  <h2 class="text-on-surface text-lg font-semibold">Title</h2>
  <p class="text-on-surface-muted text-sm">Description</p>
</div>
```

Same markup works in both themes. The CSS variables handle the switch.

---

## Extending vs Overriding

In `@theme`, you're defining the complete set of values for a namespace. To add to Tailwind's defaults without removing them, use `--color-*` naming that doesn't conflict:

```css
@theme {
  /* These ADD to the existing color palette */
  --color-brand-500: #6366f1;
  --color-brand-600: #4f46e5;

  /* Tailwind's built-in colors (blue, red, green, etc.) still work */
}
```

To completely replace a namespace (like spacing), define all values you want:

```css
@theme {
  /* This replaces the default spacing scale */
  --spacing-*: initial; /* Clear defaults */
  --spacing-0: 0px;
  --spacing-1: 4px;
  --spacing-2: 8px;
  /* ... only these values will be available */
}
```

---

## Container Queries

For components that respond to their container size (not viewport):

```html
<!-- Mark the container -->
<div class="@container">
  <!-- Respond to container width -->
  <div class="@sm:flex @sm:gap-4 @lg:grid @lg:grid-cols-3">
    <MetricCard />
    <MetricCard />
    <MetricCard />
  </div>
</div>
```

Container query breakpoints:

```
────────────────────────────────────────────────
 Prefix   │ Min container width
────────────────────────────────────────────────
 @xs:     │ 320px
 @sm:     │ 384px
 @md:     │ 448px
 @lg:     │ 512px
 @xl:     │ 576px
 @2xl:    │ 672px
────────────────────────────────────────────────
```

This is powerful for reusable components that might live in a sidebar (narrow) or main content (wide).

---

## The Complete Design System File

Sora's final design system in one CSS file:

```css
/* src/styles/design-system.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";

@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;
  --font-display: "Cal Sans", sans-serif;

  --color-brand-50: #eef2ff;
  --color-brand-100: #e0e7ff;
  --color-brand-200: #c7d2fe;
  --color-brand-300: #a5b4fc;
  --color-brand-400: #818cf8;
  --color-brand-500: #6366f1;
  --color-brand-600: #4f46e5;
  --color-brand-700: #4338ca;
  --color-brand-800: #3730a3;
  --color-brand-900: #312e81;
  --color-brand-950: #1e1b4b;

  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  --animate-fade-in: fade-in 0.3s ease-out;
  --animate-slide-up: slide-up 0.3s ease-out;
  --animate-scale-in: scale-in 0.2s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

One file. Every design decision documented. Every developer uses the same tokens.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Token Type                      │ CSS Variable Pattern
────────────────────────────────┼──────────────────────────────────────
Colors                          │ --color-{name}-{shade}
Fonts                           │ --font-{name}
Spacing                         │ --spacing-{n}
Border radius                   │ --radius-{size}
Shadows                         │ --shadow-{size}
Breakpoints                     │ --breakpoint-{name}
Animations                      │ --animate-{name}
Clear defaults                  │ --{namespace}-*: initial
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "What if I need something Tailwind doesn't have? A custom `text-shadow` utility. A `scrollbar-hide` class. A `glass` variant for frosted glass effects. Can we extend Tailwind itself?"

Custom plugins — writing your own utilities and variants.

---

[← Chapter 11: Component Patterns](chapter-11-component-patterns.md) | [Chapter 13: Plugins →](chapter-13-plugins.md)
