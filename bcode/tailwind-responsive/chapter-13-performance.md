# Chapter 13: Performance

[← Chapter 12: Container Queries](chapter-12-container-queries.md) | [Chapter 14: Design System →](chapter-14-design-system.md)

---

## The Breakage

The QA team runs a Lighthouse audit on LaunchPad's dashboard:

```
Performance: 72
First Contentful Paint: 2.1s
Largest Contentful Paint: 3.8s
Total CSS size: 487KB (uncompressed)
```

Diana: "Why is our CSS file half a megabyte? We're a dashboard, not Facebook."

The problem: during development, someone included the full Tailwind development build. Every possible utility — all colors, all spacing values, all variants — shipped to production. Users download 487KB of CSS, but the app only uses ~15KB worth of classes.

## How Tailwind JIT Works

Tailwind 3.x uses Just-In-Time (JIT) compilation by default. It scans your source files and generates **only the CSS you actually use**:

```js
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{html,js,jsx,ts,tsx}',
    './public/index.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

The `content` array tells Tailwind where to look for class names. If a class isn't found in those files, it won't be in the output CSS.

## The Content Configuration

This is the most critical setting. Get it wrong and either:
- Classes are missing (content paths too narrow)
- Bundle is huge (content paths too broad, or dev build shipped)

```js
// tailwind.config.js
module.exports = {
  content: [
    // App source files
    './src/**/*.{js,jsx,ts,tsx}',
    './src/**/*.html',

    // Component libraries
    './node_modules/@your-org/ui-kit/dist/**/*.js',

    // Template files
    './templates/**/*.hbs',

    // DON'T include node_modules broadly!
    // ❌ './node_modules/**/*.js'  ← scans everything, breaks JIT
  ],
}
```

### Common Mistakes

```js
// ❌ Wrong: missing file extensions
content: ['./src/**/*']

// ❌ Wrong: missing component directory
content: ['./src/pages/**/*.tsx']  // misses src/components/

// ❌ Wrong: dynamic class names won't be detected
const color = 'red';
className={`text-${color}-500`}  // Tailwind can't find this!

// ✅ Right: use complete class names
className={color === 'red' ? 'text-red-500' : 'text-blue-500'}
```

## Safelist: Keep Classes That Can't Be Detected

For dynamic classes that Tailwind's scanner can't find:

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  safelist: [
    // Specific classes
    'bg-red-500',
    'bg-green-500',
    'bg-blue-500',

    // Pattern-based
    {
      pattern: /bg-(red|green|blue|yellow)-(100|500|700)/,
      variants: ['hover', 'dark'],
    },
  ],
}
```

Use sparingly — every safelisted class adds to bundle size.

## Production Build

```bash
# Development (includes all utilities for fast iteration)
npx tailwindcss -i ./src/input.css -o ./dist/output.css

# Production (minified, only used classes)
npx tailwindcss -i ./src/input.css -o ./dist/output.css --minify
```

Result after proper configuration:

```
Before: 487KB (full dev build)
After:  14KB  (only used classes, minified)
Gzipped: 4KB
```

## Tree-Shaking Unused Plugins

If you installed plugins but don't use all their features:

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {},
  },
  // Only include plugins you actually use
  plugins: [
    require('@tailwindcss/typography'),
    // Don't include @tailwindcss/forms if you style inputs manually
    // Don't include @tailwindcss/aspect-ratio if you use native aspect-ratio
  ],
}
```

## Layer Organization

Use `@layer` to control where custom CSS lands (affects purging):

```css
/* src/input.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom base styles — purged if unused */
@layer base {
  html {
    @apply scroll-smooth;
  }
}

/* Reusable component classes — purged if unused */
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700
           font-medium text-sm transition-colors;
  }
}

/* Custom utilities — purged if unused */
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

Classes defined in `@layer` are tree-shaken just like Tailwind's built-in utilities.

## Performance Checklist

```bash
# 1. Verify content paths cover all source files
npx tailwindcss --content './src/**/*.tsx' -o /dev/null 2>&1 | head

# 2. Check output size
npx tailwindcss -i ./src/input.css -o ./dist/output.css --minify
ls -la ./dist/output.css

# 3. Find unused CSS (optional, with PurgeCSS)
npx purgecss --css ./dist/output.css --content './src/**/*.tsx' --output ./dist/purged.css
```

## What You Learned

- **`content` array** — tells Tailwind where to scan for class names (most important setting)
- **JIT mode** — generates only CSS for classes found in your source files
- **`--minify`** — production flag for compressed output
- **`safelist`** — keep dynamically-generated classes that the scanner can't detect
- **Complete class names** — never concatenate class strings (`text-${color}-500` won't work)
- **`@layer`** — organize custom CSS so it's tree-shaken properly
- **487KB → 14KB** — proper content configuration dramatically reduces bundle size

The bundle is lean. But there's one last problem: every page in the dashboard uses slightly different spacing, colors, and component styles. There's no consistency.

---

[← Chapter 12: Container Queries](chapter-12-container-queries.md) | [Chapter 14: Design System →](chapter-14-design-system.md)
