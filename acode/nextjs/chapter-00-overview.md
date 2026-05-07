# Next.js Mastery: A Full-Stack Survival Story

You just joined **TrailBlazer** — a startup building a hiking trail review platform. Think AllTrails meets Yelp. Users browse trails, leave reviews, upload photos, and check weather conditions.

Day one, the CTO — **Raj** — pulls you aside.

> "Our old site is a static HTML mess. No SEO. No dynamic content. Google can't find us. Users can't log in. The marketing team is manually updating trail pages. We're rebuilding everything in Next.js. You start now."

He hands you a sticky note:

> Build a full-stack app. Server-rendered pages. Dynamic routes. Auth. Forms. Image optimization. Deploy to production. You have two weeks.

You open your laptop. The cursor blinks.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Frontend/Full-Stack Dev | "I know React. How hard can this be?" |
| **Raj** | CTO | Draws architecture diagrams. Asks "but what about SEO?" |
| **Mika** | Designer | Hands you Figma links. Cares about page transitions and CLS. |
| **Owen** | Backend Engineer | Built the REST API. Hates N+1 queries. |
| **Priya** | VP of Marketing | "If Google can't see it, it doesn't exist." |
| **The Lighthouse Score** | The judge | Cold, impartial, unforgiving. |

---

## The App: TrailBlazer

| Page | Description | Challenge |
|---|---|---|
| Home | Featured trails, hero section | Static generation, fast load |
| Trail Detail | Photos, reviews, weather widget | Dynamic SSR, SEO per trail |
| Search | Filtered list with URL params | Streaming, suspense |
| User Profile | Reviews, saved trails | Auth-protected, client state |
| Write Review | Form with photo upload | Server actions, validation |
| Admin | Moderate reviews, analytics | Middleware, role-based access |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Raj assigns a feature
   │
   ▼
  🤔 You learn the Next.js concept needed
   │
   ▼
  ⌨️  You build it
   │
   ▼
  💥 Something breaks or performs badly
   │
   ▼
  🧠 You understand WHY and fix it
   │
   ▼
  📋 Next feature
```

No concept shows up before you need it. You won't hear about middleware until you need auth guards. You won't touch streaming until a page is too slow. You won't learn about ISR until the marketing team complains about stale content.

---

## The Roadmap

### Part 1: Foundations — "Make It Work"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 01 │ Project setup, first page              │ App Router, file-based routing, layout
────┼────────────────────────────────────────┼──────────────────────────────────────
 02 │ Trail listing & detail pages           │ Server Components, dynamic routes, params
────┼────────────────────────────────────────┼──────────────────────────────────────
 03 │ Fetching data from Owen's API          │ async components, caching, revalidation
────┼────────────────────────────────────────┼──────────────────────────────────────
 04 │ Styling with Tailwind + dark mode      │ CSS Modules, globals, next/font
────┼────────────────────────────────────────┼──────────────────────────────────────
 05 │ Navigation, links, loading states      │ Link, loading.tsx, error.tsx, not-found
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 2: Real Features — "Make It Useful"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 06 │ SEO, meta tags, Open Graph             │ generateMetadata, sitemap, robots.txt
────┼────────────────────────────────────────┼──────────────────────────────────────
 07 │ Client Components & interactivity      │ "use client", hooks, hydration
────┼────────────────────────────────────────┼──────────────────────────────────────
 08 │ Forms & Server Actions                 │ "use server", useActionState, validation
────┼────────────────────────────────────────┼──────────────────────────────────────
 09 │ Authentication & protected routes      │ Middleware, cookies, sessions
────┼────────────────────────────────────────┼──────────────────────────────────────
 10 │ Image optimization & uploads           │ next/image, blur placeholders, sizing
────┴────────────────────────────────────────┴──────────────────────────────────────
```

### Part 3: Production — "Make It Fast & Ship It"

```
────┬────────────────────────────────────────┬──────────────────────────────────────
 Ch │ The Feature                            │ What You Learn
────┼────────────────────────────────────────┼──────────────────────────────────────
 11 │ Static generation & ISR                │ generateStaticParams, revalidate, on-demand
────┼────────────────────────────────────────┼──────────────────────────────────────
 12 │ Streaming & Suspense                   │ loading.tsx, Suspense boundaries, parallel
────┼────────────────────────────────────────┼──────────────────────────────────────
 13 │ API Routes & Route Handlers            │ GET/POST handlers, webhooks, CORS
────┼────────────────────────────────────────┼──────────────────────────────────────
 14 │ Performance & Core Web Vitals          │ Bundle analysis, lazy loading, Lighthouse
────┼────────────────────────────────────────┼──────────────────────────────────────
 15 │ Deployment & production hardening      │ Vercel, Docker, env vars, monitoring
────┴────────────────────────────────────────┴──────────────────────────────────────
```

---

## Prerequisites

- **Node.js 20+**
- **Basic React** (components, hooks, JSX)
- **A terminal**
- **VS Code** (recommended — great Next.js support)

---

## The API

Owen already built the backend. REST API at `http://localhost:4000`:

```
GET    /api/trails              → list trails (search, filter, paginate)
GET    /api/trails/:slug        → single trail detail
GET    /api/trails/:slug/reviews → reviews for a trail
POST   /api/trails/:slug/reviews → submit a review (auth required)
GET    /api/users/me            → current user profile
POST   /api/auth/login          → returns JWT + sets cookie
POST   /api/auth/register       → create account
POST   /api/upload              → upload a photo (returns URL)
```

We'll consume this API from Next.js — sometimes on the server, sometimes on the client. Knowing when to do which is half the battle.

---

[Next: Chapter 1 — Your First Page →](chapter-01-first-page.md)
