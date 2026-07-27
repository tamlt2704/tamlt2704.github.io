# Frontend Mastery Roadmap

Where you are now → what to learn next → advanced topics.

---

## What You Already Know (From This Project)

| Topic | Status |
|-------|--------|
| React basics (components, props, state) | ✅ |
| Next.js App Router (pages, layouts, routing) | ✅ |
| Tailwind CSS (utility classes, responsive) | ✅ |
| TypeScript basics | ✅ |
| Dark mode / theming | ✅ |
| Component libraries (shadcn/ui) | ✅ |
| Animation (Framer Motion) | ✅ |
| Charts (Recharts) | ✅ |
| MDX (Markdown + components) | ✅ |
| Static export / deployment | ✅ |
| Code quality (Prettier, ESLint, Husky) | ✅ |

You have a solid foundation. Here's what's next.

---

## Level 1: Fill the Gaps (Essentials You'll Need Daily)

### React Deep Dive

| Topic | What it is | Why it matters |
|-------|-----------|----------------|
| `useEffect` cleanup | Return a function to cancel subscriptions/timers | Prevents memory leaks |
| `useRef` | Access DOM elements, persist values without re-render | Focus inputs, timers, animations |
| `useMemo` / `useCallback` | Cache expensive calculations / stable function references | Performance in large lists |
| Custom hooks | Extract reusable logic (you made `useCsvData`) | Clean, DRY code |
| Context API | Share state without prop drilling (you used `ThemeProvider`) | Global state patterns |
| Error boundaries | Catch rendering errors gracefully | App doesn't crash entirely |
| Suspense + lazy loading | Load components on demand | Faster initial page load |

### CSS / Layout Mastery

| Topic | What to learn |
|-------|--------------|
| Flexbox (deep) | `flex-grow`, `flex-shrink`, `flex-basis`, `order` |
| CSS Grid (deep) | `grid-template-areas`, `auto-fit`, `minmax()` |
| Container queries | Style based on parent size (not viewport) |
| CSS animations | `@keyframes`, when to use CSS vs JS animation |
| Scroll-driven animations | Animate on scroll without JS |

### TypeScript (Beyond Basics)

| Topic | Example |
|-------|---------|
| Generics | `function useData<T>(url: string): T[]` |
| Union types + narrowing | `type Status = "loading" \| "error" \| "success"` |
| Utility types | `Partial<T>`, `Pick<T, K>`, `Omit<T, K>`, `Record<K, V>` |
| Interface vs Type | When to use which |
| Type guards | `if ("error" in response)` |
| `as const` | Narrow literal types from arrays/objects |

---

## Level 2: Real-World Skills (What Separates Juniors from Mids)

### State Management

| When | Tool |
|------|------|
| Simple local state | `useState` |
| Shared across few components | Context + `useReducer` |
| Complex global state | Zustand (simplest) or Jotai |
| Server state (API data) | TanStack Query (React Query) |

**Learn TanStack Query** — it handles caching, refetching, loading states, and error handling for API calls. You'll use it on every project with a backend.

### Forms

| Topic | Tool |
|-------|------|
| Form state + validation | `react-hook-form` + `zod` |
| Accessible form components | shadcn `Form`, `Input`, `Select` |
| Multi-step forms | State machine pattern |
| File uploads | Drag-and-drop zone, progress indicators |

### Data Fetching Patterns

| Pattern | When |
|---------|------|
| Client-side fetch (`useEffect`) | User-triggered, real-time data |
| Server Components (Next.js) | Static/rarely-changing data, SEO content |
| TanStack Query | Anything from an API — caching, refetch, optimistic updates |
| Static generation | Blog posts, docs — built at deploy time |
| Incremental Static Regeneration | Data updates every few minutes (not for GitHub Pages) |

### Authentication

| Concept | What to know |
|---------|-------------|
| JWT tokens | How access/refresh tokens work |
| OAuth / OIDC | Login with Google/GitHub |
| Protected routes | Redirect unauthenticated users |
| Middleware | Check auth before rendering a page |
| `next-auth` (Auth.js) | The standard Next.js auth library |

### Testing

| Type | Tool | What it tests |
|------|------|--------------|
| Unit tests | Vitest | Individual functions, hooks |
| Component tests | Testing Library + Vitest | Render a component, check output |
| E2E tests | Playwright | Full browser, click buttons, assert pages |
| Visual regression | Chromatic / Percy | Screenshots don't change unexpectedly |

---

## Level 3: Performance & Architecture (Senior Level)

### Performance

| Topic | What to learn |
|-------|--------------|
| Web Vitals (LCP, CLS, INP) | The metrics Google uses to rank your site |
| Bundle analysis | `next-bundle-analyzer` — find large dependencies |
| Code splitting | Dynamic imports, `next/dynamic`, route-based splitting |
| Image optimization | `next/image`, WebP/AVIF, lazy loading |
| Font optimization | `next/font`, font-display, subset loading |
| Caching strategies | `Cache-Control`, SWR, ISR, CDN edge caching |
| Virtual scrolling | Render 10,000 rows without crashing (TanStack Virtual) |
| Web Workers | Offload heavy computation off the main thread |

### Architecture

| Topic | What to learn |
|-------|--------------|
| Feature-based folder structure | Group by feature, not by type |
| Component design patterns | Compound components, render props, slots |
| Design system thinking | Tokens, variants, composition |
| Monorepo (Turborepo) | Shared UI library across multiple apps |
| Micro-frontends | When (and when not) to split an app |
| Server Components vs Client Components | When to use which (Next.js App Router) |

### Accessibility (a11y)

| Topic | What to learn |
|-------|--------------|
| Semantic HTML | `<nav>`, `<main>`, `<article>`, `<button>` vs `<div>` |
| ARIA attributes | `aria-label`, `aria-expanded`, `role` |
| Keyboard navigation | Tab order, focus traps (modals) |
| Screen reader testing | NVDA (Windows) or VoiceOver (Mac) |
| Color contrast | WCAG AA (4.5:1 ratio for text) |
| Motion preferences | `prefers-reduced-motion` |

---

## Level 4: Specialisations (Pick Your Path)

### Path A: Data Visualisation (Your Interest)

| Topic | What to learn |
|-------|--------------|
| D3.js | Low-level SVG manipulation, scales, axes |
| Canvas API | Fast rendering for 10k+ data points |
| WebGL (Three.js / React Three Fiber) | 3D visualisations |
| Maps (Mapbox, Leaflet) | Geographic visualisation |
| Observable / Notebooks | Exploratory data analysis |
| Storytelling with data | Scrollytelling, annotation, narrative flow |

### Path B: Interactive / Creative

| Topic | What to learn |
|-------|--------------|
| Canvas + WebGL | Games, generative art |
| Three.js / R3F | 3D in the browser |
| Shaders (GLSL) | Custom visual effects |
| Web Audio API | Sound design, music visualisation |
| GSAP + ScrollTrigger | Complex scroll-driven animations |

### Path C: Application Development

| Topic | What to learn |
|-------|--------------|
| Complex state machines | XState — model app logic as state charts |
| Real-time (WebSockets) | Chat, live dashboards, collaboration |
| Offline-first (PWA) | Service workers, IndexedDB |
| Drag and drop | `dnd-kit` — sortable lists, kanban boards |
| Rich text editors | TipTap, Plate, Lexical |
| Internationalisation (i18n) | Multi-language support |

### Path D: Infrastructure / Full-Stack Leaning

| Topic | What to learn |
|-------|--------------|
| Edge functions | Vercel Edge, Cloudflare Workers |
| Database from frontend | Supabase, PlanetScale, Neon |
| CMS integration | Sanity, Contentful, Payload |
| CI/CD for frontend | GitHub Actions, preview deploys |
| Monitoring | Sentry (errors), Vercel Analytics (performance) |
| SEO deep dive | Structured data, Open Graph, sitemaps |

---

## How to Practice

| Method | Why it works |
|--------|-------------|
| **Build projects** | You're already doing this — keep going |
| **Clone sites you admire** | Pick a site, rebuild it. Learn their techniques. |
| **Read source code** | shadcn/ui source is on GitHub — read how they build components |
| **Frontend challenges** | frontendmentor.io, cssbattle.dev |
| **Teach others** | Your blog! Writing forces deep understanding |
| **Contribute to open source** | Fix a bug in a library you use |

---

## Suggested Learning Order (Next 6 Months)

```
Month 1-2: Level 1
  └── React hooks deep dive
  └── TypeScript generics + utility types
  └── CSS Grid mastery
  └── Build: portfolio site with animations

Month 3-4: Level 2
  └── TanStack Query
  └── react-hook-form + zod
  └── Testing (Vitest + Testing Library)
  └── Build: full CRUD app with API

Month 5-6: Level 3 + Specialisation
  └── Performance (Web Vitals, bundle analysis)
  └── Accessibility audit on your own projects
  └── Start your specialisation path
  └── Build: something that impresses you
```

---

## Resources

| Resource | What | Free? |
|----------|------|-------|
| [react.dev](https://react.dev) | Official React docs (excellent) | ✅ |
| [nextjs.org/learn](https://nextjs.org/learn) | Official Next.js tutorial | ✅ |
| [typescript-exercises.github.io](https://typescript-exercises.github.io) | TS practice problems | ✅ |
| [web.dev](https://web.dev) | Google's performance + best practices | ✅ |
| [Josh Comeau's blog](https://joshwcomeau.com) | CSS, React, animations explained beautifully | ✅ |
| [Kent C. Dodds' blog](https://kentcdodds.com) | Testing, React patterns | ✅ |
| [Frontend Masters](https://frontendmasters.com) | Video courses (all levels) | 💰 |
| [ui.dev](https://ui.dev) | React, TypeScript courses | 💰 |
| [Total TypeScript](https://totaltypescript.com) | Advanced TypeScript | 💰 (free workshops) |
