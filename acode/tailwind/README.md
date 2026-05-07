# Tailwind CSS — A Frontend Survival Story

You joined Pixelflow. The design lead dropped 47 Figma screens. The old CSS is 4,000 lines of chaos. You're rewriting it in Tailwind. This is that story.

## Episodes

| # | The Design Task | What You Learn |
|---|---|---|
| 00 | [Overview](chapter-00-overview.md) | The story, the cast, the roadmap |
| 01 | [Style a card](chapter-01-utility-basics.md) | Utility classes, spacing, colors, text |
| 02 | [Layout the dashboard](chapter-02-layout.md) | Flexbox, Grid, responsive breakpoints |
| 03 | [Responsive navbar](chapter-03-responsive-navbar.md) | Mobile-first, hamburger menu, positioning |
| 04 | [Typography & content](chapter-04-typography.md) | Font scale, prose plugin, text utilities |
| 05 | [Colors & gradients](chapter-05-colors-theming.md) | Palette, custom colors, gradient text |
| 06 | [Hover, focus, active](chapter-06-states-transitions.md) | State variants, transitions, group-hover |
| 07 | [Dark mode](chapter-07-dark-mode.md) | dark: variant, CSS variables, toggle |
| 08 | [Animations](chapter-08-animations.md) | Spin, pulse, keyframes, transforms |
| 09 | [Forms & inputs](chapter-09-forms.md) | Input styling, validation, toggles |
| 10 | [Dynamic classes](chapter-10-dynamic-classes.md) | clsx, tailwind-merge, CVA |
| 11 | [Component patterns](chapter-11-component-patterns.md) | Extraction rules, @apply, compound components |
| 12 | [Design tokens](chapter-12-design-tokens.md) | @theme, custom fonts, CSS variables |
| 13 | [Custom plugins](chapter-13-plugins.md) | @utility, JS plugins, variants |
| 14 | [Performance](chapter-14-performance.md) | Tree-shaking, bundle size, optimization |
| 15 | [Full build](chapter-15-full-build.md) | Complete dashboard, everything together |

## Prerequisites

- Node.js 18+
- Basic HTML/CSS knowledge
- VS Code with Tailwind CSS IntelliSense

## Quick Start

```bash
npm create vite@latest pixelflow -- --template react
cd pixelflow
npm install -D tailwindcss @tailwindcss/vite
```
