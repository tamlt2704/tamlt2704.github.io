# Chapter 13: Custom Plugins — Extending Tailwind

[← Chapter 12: Design Tokens](chapter-12-design-tokens.md) | [Chapter 14: Performance →](chapter-14-performance.md)

---

## The Task

Sora: "I need three things Tailwind doesn't have: text shadows for the hero section, a way to hide scrollbars on the horizontal scroll container, and a frosted glass effect for the modal backdrop. Can you make those?"

You: "Plugins. We can add any CSS as a Tailwind utility."

---

## Plugin Basics (Tailwind v4)

In Tailwind v4, simple custom utilities can be added directly in CSS:

```css
@import "tailwindcss";

/* Custom utility via @utility */
@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}

@utility text-shadow-sm {
  text-shadow: 0 1px 2px rgb(0 0 0 / 0.1);
}

@utility text-shadow-md {
  text-shadow: 0 2px 4px rgb(0 0 0 / 0.15);
}

@utility text-shadow-lg {
  text-shadow: 0 4px 8px rgb(0 0 0 / 0.2);
}

@utility text-shadow-none {
  text-shadow: none;
}

@utility glass {
  background: rgb(255 255 255 / 0.1);
  backdrop-filter: blur(12px) saturate(150%);
  border: 1px solid rgb(255 255 255 / 0.2);
}
```

Now use them like any built-in utility:

```html
<h1 class="text-shadow-lg text-white">Hero Title</h1>
<div class="overflow-x-auto scrollbar-hide">Horizontal scroll</div>
<div class="glass rounded-xl p-6">Frosted glass card</div>
```

---

## JavaScript Plugins (Advanced)

For more complex plugins with variants, dynamic values, or configuration, write a JS plugin:

```js
// plugins/text-shadow.js
import plugin from 'tailwindcss/plugin';

export default plugin(function ({ matchUtilities, theme }) {
  matchUtilities(
    {
      'text-shadow': (value) => ({
        textShadow: value,
      }),
    },
    {
      values: {
        sm: '0 1px 2px rgb(0 0 0 / 0.1)',
        DEFAULT: '0 2px 4px rgb(0 0 0 / 0.1)',
        md: '0 2px 4px rgb(0 0 0 / 0.15)',
        lg: '0 4px 8px rgb(0 0 0 / 0.2)',
        xl: '0 8px 16px rgb(0 0 0 / 0.25)',
        none: 'none',
      },
    }
  );
});
```

Register it in your CSS:

```css
@import "tailwindcss";
@plugin "./plugins/text-shadow.js";
```

`matchUtilities` gives you:
- Arbitrary value support: `text-shadow-[0_4px_8px_red]`
- All values available as classes: `text-shadow-sm`, `text-shadow-lg`
- Works with variants: `hover:text-shadow-lg`, `dark:text-shadow-none`

---

## Adding Custom Variants

Create variants that respond to custom conditions:

```js
// plugins/variants.js
import plugin from 'tailwindcss/plugin';

export default plugin(function ({ addVariant }) {
  // Matches when a parent has data-theme="dark"
  addVariant('theme-dark', '[data-theme="dark"] &');

  // Matches when the element has aria-selected
  addVariant('selected', '&[aria-selected="true"]');

  // Matches when a parent dialog is open
  addVariant('dialog-open', 'dialog[open] &');

  // Matches based on group data attribute
  addVariant('group-active', ':merge(.group)[data-active] &');
});
```

Usage:

```html
<div data-theme="dark">
  <p class="text-gray-900 theme-dark:text-white">Adapts to data-theme</p>
</div>

<button aria-selected="true" class="selected:bg-brand-100 selected:text-brand-700">
  Tab
</button>
```

---

## Real Plugin: Animated Gradient Border

A plugin for the animated gradient borders Sora wants on premium cards:

```css
@utility gradient-border {
  position: relative;
  background: var(--tw-gradient-from, #6366f1);
  background-clip: padding-box;
  border: 2px solid transparent;
  border-radius: 12px;

  &::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 14px;
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899, #6366f1);
    background-size: 300% 300%;
    animation: gradient-rotate 4s ease infinite;
    z-index: -1;
  }
}

@keyframes gradient-rotate {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

```html
<div class="gradient-border bg-white dark:bg-gray-900 p-6">
  Premium card with animated gradient border
</div>
```

---

## Plugin: Responsive Container

A plugin that adds a centered, max-width container with responsive padding:

```css
@utility container-responsive {
  width: 100%;
  max-width: 1280px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;

  @media (min-width: 640px) {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  @media (min-width: 1024px) {
    padding-left: 2rem;
    padding-right: 2rem;
  }
}
```

---

## Official Plugins Worth Knowing

```
────────────────────────────────────────────────────────────
 Plugin                      │ What It Adds
────────────────────────────────────────────────────────────
 @tailwindcss/typography     │ prose class for rich content
 @tailwindcss/forms          │ Better default form styles
 @tailwindcss/container-queries │ @container support
────────────────────────────────────────────────────────────
```

Install and register:

```bash
npm install -D @tailwindcss/typography @tailwindcss/forms @tailwindcss/container-queries
```

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
@plugin "@tailwindcss/container-queries";
```

---

## The Forms Plugin

`@tailwindcss/forms` resets form elements to a clean baseline:

```html
<!-- Without plugin: browser-default ugly checkbox -->
<!-- With plugin: clean, styled checkbox that respects your colors -->
<input type="checkbox" class="rounded border-gray-300 text-brand-600 focus:ring-brand-500" />

<!-- Without plugin: browser-default select -->
<!-- With plugin: clean select with custom arrow -->
<select class="rounded-lg border-gray-300 focus:border-brand-500 focus:ring-brand-500">
  <option>Option 1</option>
</select>
```

It doesn't add new classes — it resets the defaults so native form elements look good with minimal Tailwind classes.

---

## When to Write a Plugin vs Use @utility

```
────────────────────────────────────────────────────────────
 Need                           │ Use
────────────────────────────────────────────────────────────
 Simple static utility          │ @utility in CSS
 Utility with multiple values   │ JS plugin with matchUtilities
 Custom variant/modifier        │ JS plugin with addVariant
 Complex with pseudo-elements   │ @utility with & selectors
 Shared across projects         │ JS plugin (publishable to npm)
────────────────────────────────────────────────────────────
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Syntax
────────────────────────────────┼──────────────────────────────────────
Simple custom utility           │ @utility name { ... }
Utility with pseudo-elements    │ @utility name { &::before { ... } }
Register JS plugin              │ @plugin "./path/to/plugin.js"
Register npm plugin             │ @plugin "@tailwindcss/typography"
JS: add static utilities        │ addUtilities({ '.name': { ... } })
JS: add dynamic utilities       │ matchUtilities({ name: (v) => ({}) })
JS: add variant                 │ addVariant('name', 'selector &')
JS: add components              │ addComponents({ '.name': { ... } })
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "The design system is complete. Now — how big is our CSS bundle? Are we shipping unused styles? What about performance in production?"

Production optimization, purging, and performance.

---

[← Chapter 12: Design Tokens](chapter-12-design-tokens.md) | [Chapter 14: Performance →](chapter-14-performance.md)
