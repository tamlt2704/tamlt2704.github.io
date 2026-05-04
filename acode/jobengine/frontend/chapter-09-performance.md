# Chapter 9: It's Slow — Performance

[← Chapter 8: Authentication](chapter-08-auth.md) | [Chapter 10: Mobile →](chapter-10-mobile.md)

---

## The Problem

ShopZilla processes 10,000 jobs per day. The dashboard tries to render all 10,000 in a grid. The browser freezes. The TV shows a white screen for 8 seconds. Captain Deadline: "It's broken."

It's not broken. It's slow. Which is worse.

## What You'll Build

- **Pagination** — show 50 jobs per page, load more on scroll or button click
- **Virtualized list** — only render the ~20 visible rows, not all 10,000 (`@tanstack/react-virtual`)
- **Search with debounce** — don't fire a request on every keystroke, wait 300ms
- **`React.memo`** — prevent re-rendering job cards that didn't change
- **`useMemo` / `useCallback`** — memoize expensive computations and callbacks
- **Lazy loading** — `React.lazy()` + `Suspense` for the DAG page (heavy library, load on demand)
- **Bundle analysis** — `vite-plugin-visualizer` to find what's making the bundle big

## Key Concepts

- **Virtualization** — rendering only visible items in a long list
- **Debouncing** — delaying execution until input stops changing
- **Memoization** — `React.memo`, `useMemo`, `useCallback` and when they actually help
- **Code splitting** — `React.lazy` + dynamic `import()` for route-based splitting
- **Profiling** — React DevTools Profiler, Chrome Performance tab
- **Bundle size** — tree shaking, analyzing what ships to the browser

---

[← Chapter 8: Authentication](chapter-08-auth.md) | [Chapter 10: Mobile →](chapter-10-mobile.md)
