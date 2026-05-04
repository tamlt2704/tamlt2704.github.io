# Chapter 10: It Doesn't Work on My Phone — Mobile & Responsive

[← Chapter 9: Performance](chapter-09-performance.md) | [Chapter 11: GraphQL →](chapter-11-graphql.md)

---

## The Problem

Karen opens the dashboard on her phone during a meeting. The job cards overflow. The stats bar is unreadable. The DAG graph is microscopic. "It doesn't work on my phone."

It works. It just wasn't designed for a 375px screen.

## What You'll Build

- **Responsive layout** — Tailwind breakpoints (`sm:`, `md:`, `lg:`) for every component
- **Mobile navigation** — hamburger menu, bottom tab bar, swipe gestures
- **Touch-friendly actions** — larger tap targets, swipe-to-cancel on job cards
- **Responsive DAG** — simplified pipeline view on mobile (vertical list instead of graph)
- **PWA basics** — `manifest.json`, service worker, "Add to Home Screen"
- **Viewport meta** — proper mobile scaling

## Key Concepts

- **Tailwind responsive prefixes** — `md:grid-cols-2 lg:grid-cols-3`
- **Mobile-first design** — start with the smallest screen, add complexity for larger ones
- **Touch events** — `onTouchStart`, `onTouchEnd`, swipe detection
- **Media queries** — `useMediaQuery` hook for conditional rendering
- **PWA** — Progressive Web App basics, offline capability
- **Testing on mobile** — Chrome DevTools device emulation, real device testing

---

[← Chapter 9: Performance](chapter-09-performance.md) | [Chapter 11: GraphQL →](chapter-11-graphql.md)
