# Responsive UI with Tailwind — From Mobile to 4K

A narrative-driven course on building responsive interfaces with Tailwind CSS. You're a frontend engineer at **LaunchPad**, a SaaS dashboard startup. The CEO just checked the app on her phone and said "this is unusable." You have two weeks to make every screen work from 320px to 3840px.

## Episodes

| # | Title | The Breakage | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, mobile-first philosophy, the cast |
| 01 | [Mobile First](chapter-01-mobile-first.md) | Desktop layout crammed onto phone | Mobile-first workflow, breakpoints, sm/md/lg/xl/2xl |
| 02 | [Flexbox Layouts](chapter-02-flexbox.md) | Sidebar overlaps content on tablet | flex, flex-wrap, gap, justify, items, grow/shrink |
| 03 | [Grid Systems](chapter-03-grid.md) | Dashboard cards stack wrong | grid, grid-cols, col-span, auto-fit, responsive grids |
| 04 | [Responsive Typography](chapter-04-typography.md) | Text too small on mobile, too large on 4K | text-sm/lg/xl, clamp(), fluid type, prose |
| 05 | [Responsive Spacing](chapter-05-spacing.md) | Padding crushes content on small screens | Responsive p/m, space-y, container, max-w |
| 06 | [Navigation Patterns](chapter-06-navigation.md) | Navbar items overflow on mobile | Hamburger menu, responsive nav, hidden/block |
| 07 | [Responsive Images](chapter-07-images.md) | Hero image breaks layout | object-fit, aspect-ratio, srcset with Tailwind |
| 08 | [Cards and Lists](chapter-08-cards.md) | Card grid looks wrong at every size | Responsive card layouts, min-width tricks |
| 09 | [Tables on Mobile](chapter-09-tables.md) | Data table scrolls horizontally forever | Responsive tables, stacked layout, overflow |
| 10 | [Forms That Fit](chapter-10-forms.md) | Form fields overflow on mobile | Responsive form layouts, input sizing, label stacking |
| 11 | [Dark Mode](chapter-11-dark-mode.md) | Users demand dark mode | dark: variant, system preference, toggle |
| 12 | [Container Queries](chapter-12-container-queries.md) | Component looks wrong in sidebar vs main | @container, container queries with Tailwind |
| 13 | [Performance](chapter-13-performance.md) | CSS bundle is 500KB | Purging, JIT, content configuration, tree-shaking |
| 14 | [Design System](chapter-14-design-system.md) | Every page uses different spacing/colors | Custom theme, extend, plugins, component extraction |

## Prerequisites

- Node.js 18+
- Tailwind CSS 3.4+ (or 4.x)
- Any framework (examples use plain HTML, adaptable to React/Vue/Svelte)

## Philosophy

Every responsive technique is introduced because something looks broken on a real device. You'll see the broken screenshot first, then learn the Tailwind utilities that fix it. The broken layout comes first. The responsive fix follows.
