# Chapter 5: Clean Architecture — Hooks, Context & Patterns

[← Chapter 4: Real-time Updates](chapter-04-real-time.md) | [Chapter 6: Job Actions →](chapter-06-actions.md)

---

## The Problem

Your `App.tsx` is 200 lines. State logic, fetch logic, SSE logic, and UI are all tangled together. You add a filter dropdown and the component becomes unreadable. Old Greg reviews your PR: "This is a god component."

## What You'll Build

- Extract all API logic into custom hooks (`useJobs`, `useStats`, `useJobStream`)
- Create a `JobContext` provider so any component can access jobs without prop drilling
- Split the UI into small, focused components: `Layout`, `Header`, `FilterBar`, `JobGrid`
- Introduce the container/presentational pattern: smart components fetch data, dumb components render it

## Key Concepts

- **Custom hooks** — reusable stateful logic (`useFetch`, `useDebounce`, `useLocalStorage`)
- **React Context** — share state across the component tree without passing props through every level
- **Component composition** — `children` prop, slots, compound components
- **Separation of concerns** — data layer vs presentation layer

---

[← Chapter 4: Real-time Updates](chapter-04-real-time.md) | [Chapter 6: Job Actions →](chapter-06-actions.md)
