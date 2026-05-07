# Building a House with React Three Fiber & Next.js

> A progressive guide — from an empty lot to a finished house, deployed on GitHub Pages.
>
> Each chapter builds on the last. By the end, you'll have a 3D interactive house scene running live on the web.

---

## The Story

Imagine you just bought an empty plot of land. Right now it's just dirt. Over the next 8 chapters, you'll:

1. **Survey the lot** — set up your tools and see the empty ground
2. **Pour the foundation** — learn shapes and materials
3. **Raise the walls** — position, rotate, and group objects
4. **Wire the electricity** — add lighting
5. **Install doors & windows** — interaction and animation
6. **Bring in furniture** — load 3D models
7. **Landscape the yard** — environment, sky, and polish
8. **Open house** — deploy to GitHub Pages for the world to see

No prior Three.js knowledge needed. You should know React basics and be comfortable with the terminal.

---

## Project Setup

### What We're Installing

| Package | What It Does |
|---|---|
| `next` | React framework — handles routing, building, static export |
| `three` | The 3D engine — does the actual WebGL rendering |
| `@react-three/fiber` | React renderer for Three.js — lets you write 3D scenes as JSX |
| `@react-three/drei` | Helper library — pre-built controls, loaders, effects |

### Create the Project

```bash
npx create-next-app@latest my-3d-house --typescript --app --tailwind --eslint
cd my-3d-house
```

When prompted, accept the defaults. Then install the 3D dependencies:

```bash
npm install three @react-three/fiber @react-three/drei
npm install -D @types/three
```

### Configure for Static Export

Since GitHub Pages only serves static files, tell Next.js to produce a static build.

**`next.config.ts`**
```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'export',
  basePath: process.env.NODE_ENV === 'production' ? '/my-3d-house' : '',
  images: {
    unoptimized: true,
  },
}

export default nextConfig
```

> **Why `basePath`?** GitHub Pages serves your site at `username.github.io/repo-name/`, not at the root. Without this, every asset path breaks in production.

### Project Structure (What We'll Build Toward)

```
src/
├── app/
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Main page — HTML + 3D canvas
├── components/
│   ├── Scene.tsx           # The 3D scene (client component)
│   ├── Ground.tsx          # The ground plane
│   ├── House.tsx           # The house structure
│   ├── Lights.tsx          # All lighting
│   └── Furniture.tsx       # Loaded 3D models
└── public/
    └── models/             # .glb model files
```

You don't need to create all of these now. We'll add them chapter by chapter.

### Verify It Works

```bash
npm run dev
```

Visit `http://localhost:3000`. You should see the default Next.js page. Good — the lot is empty. Let's start building.

---

Next: [Chapter 1 — The Empty Lot](./01-the-empty-lot.md)
