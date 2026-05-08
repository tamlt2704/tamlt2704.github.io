# Chapter 14: Design System

[← Chapter 13: Performance](chapter-13-performance.md) | [Course Overview →](chapter-00-overview.md)

---

## The Breakage

Jake reviews the dashboard and notices:

- The settings page uses `blue-600` for buttons, the billing page uses `blue-500`
- Card padding is `p-4` on one page, `p-5` on another, `p-6` on a third
- Some headings are `text-xl font-bold`, others are `text-lg font-semibold`
- Border radius varies between `rounded-lg`, `rounded-xl`, and `rounded-md`

Diana: "Why does every page look like it was built by a different person?"

It was. Three engineers, no shared system. Every component is a one-off with slightly different Tailwind classes.

## Custom Theme: Extend the Config

Define your design tokens in `tailwind.config.js`:

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',  // Primary action
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        surface: {
          DEFAULT: '#ffffff',
          muted: '#f9fafb',
          raised: '#f3f4f6',
          dark: '#111827',
          'dark-muted': '#1f2937',
          'dark-raised': '#374151',
        },
      },
      spacing: {
        'card': '1.25rem',       // Standard card padding
        'section': '2rem',       // Section spacing
        'page': '3rem',          // Page-level spacing
      },
      borderRadius: {
        'card': '0.75rem',       // All cards use this
        'button': '0.5rem',      // All buttons use this
        'input': '0.5rem',       // All inputs use this
      },
      fontSize: {
        'heading-1': ['2.25rem', { lineHeight: '2.5rem', fontWeight: '700' }],
        'heading-2': ['1.5rem', { lineHeight: '2rem', fontWeight: '600' }],
        'heading-3': ['1.25rem', { lineHeight: '1.75rem', fontWeight: '600' }],
        'body': ['0.9375rem', { lineHeight: '1.5rem' }],
        'caption': ['0.8125rem', { lineHeight: '1.25rem' }],
      },
    },
  },
}
```

Now the team uses semantic names:

```html
<!-- Before: magic numbers everywhere -->
<div class="bg-white rounded-xl p-5">
  <h2 class="text-xl font-semibold">...</h2>
</div>

<!-- After: design tokens -->
<div class="bg-surface rounded-card p-card">
  <h2 class="text-heading-2">...</h2>
</div>
```

## Component Extraction with @apply

For patterns repeated across many files, extract component classes:

```css
/* src/input.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2
           text-sm font-medium rounded-button
           transition-colors duration-150
           focus:outline-none focus:ring-2 focus:ring-offset-2;
  }

  .btn-primary {
    @apply btn bg-brand-600 text-white
           hover:bg-brand-700 focus:ring-brand-500;
  }

  .btn-secondary {
    @apply btn bg-white text-gray-700 border border-gray-300
           hover:bg-gray-50 focus:ring-brand-500;
  }

  .card {
    @apply bg-surface dark:bg-surface-dark
           rounded-card p-card
           border border-gray-200 dark:border-gray-700
           shadow-sm;
  }

  .input {
    @apply w-full border border-gray-300 dark:border-gray-600
           rounded-input px-3 py-2 text-body
           bg-white dark:bg-surface-dark-muted
           text-gray-900 dark:text-gray-100
           focus:ring-2 focus:ring-brand-500 focus:border-brand-500;
  }
}
```

Usage becomes clean and consistent:

```html
<div class="card">
  <h2 class="text-heading-2 mb-4">Project Settings</h2>
  <form class="space-y-4">
    <input type="text" class="input" placeholder="Project name">
    <div class="flex gap-3">
      <button class="btn-primary">Save</button>
      <button class="btn-secondary">Cancel</button>
    </div>
  </form>
</div>
```

## Tailwind Plugins for Custom Utilities

For more complex patterns, write a plugin:

```js
// tailwind.config.js
const plugin = require('tailwindcss/plugin');

module.exports = {
  // ...
  plugins: [
    plugin(function({ addComponents, theme }) {
      addComponents({
        '.stat-card': {
          backgroundColor: theme('colors.surface.DEFAULT'),
          borderRadius: theme('borderRadius.card'),
          padding: theme('spacing.card'),
          border: `1px solid ${theme('colors.gray.200')}`,
          '@media (prefers-color-scheme: dark)': {
            backgroundColor: theme('colors.surface.dark'),
            borderColor: theme('colors.gray.700'),
          },
        },
        '.page-container': {
          maxWidth: theme('maxWidth.7xl'),
          marginLeft: 'auto',
          marginRight: 'auto',
          paddingLeft: theme('spacing.4'),
          paddingRight: theme('spacing.4'),
          '@screen sm': {
            paddingLeft: theme('spacing.6'),
            paddingRight: theme('spacing.6'),
          },
          '@screen lg': {
            paddingLeft: theme('spacing.8'),
            paddingRight: theme('spacing.8'),
          },
        },
      });
    }),
  ],
}
```

## The Complete Design System in Action

```html
<div class="min-h-screen bg-surface-muted dark:bg-surface-dark">
  <!-- Header -->
  <header class="bg-surface dark:bg-surface-dark-muted border-b border-gray-200 dark:border-gray-800">
    <div class="page-container flex items-center justify-between h-16">
      <span class="text-heading-3 text-gray-900 dark:text-white">LaunchPad</span>
      <button class="btn-primary">New Project</button>
    </div>
  </header>

  <!-- Content -->
  <main class="page-container py-section">
    <h1 class="text-heading-1 text-gray-900 dark:text-white mb-section">Dashboard</h1>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-section">
      <div class="stat-card">
        <p class="text-caption text-gray-500 dark:text-gray-400">Revenue</p>
        <p class="text-heading-1 mt-1">$48,200</p>
      </div>
      <div class="stat-card">
        <p class="text-caption text-gray-500 dark:text-gray-400">Users</p>
        <p class="text-heading-1 mt-1">2,420</p>
      </div>
      <div class="stat-card">
        <p class="text-caption text-gray-500 dark:text-gray-400">Orders</p>
        <p class="text-heading-1 mt-1">1,210</p>
      </div>
      <div class="stat-card">
        <p class="text-caption text-gray-500 dark:text-gray-400">Conversion</p>
        <p class="text-heading-1 mt-1">3.2%</p>
      </div>
    </div>

    <div class="card">
      <h2 class="text-heading-2 mb-4">Recent Activity</h2>
      <div class="space-y-3">
        <p class="text-body text-gray-600 dark:text-gray-400">New user signed up</p>
        <p class="text-body text-gray-600 dark:text-gray-400">Order #1234 completed</p>
        <p class="text-body text-gray-600 dark:text-gray-400">Payment received</p>
      </div>
    </div>
  </main>
</div>
```

Every engineer uses the same tokens. Every page looks intentional.

## What You Learned

- **`theme.extend.colors`** — define brand colors as design tokens
- **Custom spacing/radius/fontSize** — semantic names (`card`, `section`, `heading-1`)
- **`@layer components` + `@apply`** — extract repeated patterns into reusable classes
- **Tailwind plugins** — `addComponents()` for complex, theme-aware patterns
- **Semantic naming** — `bg-surface` instead of `bg-white` (easier dark mode, easier refactoring)
- **Consistency** — one source of truth for spacing, colors, typography, and radii

---

## Course Complete 🎉

You've taken LaunchPad's dashboard from a desktop-only disaster to a responsive, performant, dark-mode-ready application with a consistent design system.

The responsive checklist passes on all 47 of QA's devices. Diana can read everything on her phone. Jake's designs translate cleanly to every breakpoint. The CSS bundle is 14KB instead of 487KB.

**The key principles:**
1. Mobile-first — build for small screens, enhance for large
2. Tailwind breakpoints — `sm:`, `md:`, `lg:`, `xl:`, `2xl:` apply upward
3. Container queries — components adapt to their context, not the viewport
4. Design tokens — consistency through shared configuration
5. Performance — ship only the CSS you use

---

[← Chapter 13: Performance](chapter-13-performance.md) | [Course Overview →](chapter-00-overview.md)
