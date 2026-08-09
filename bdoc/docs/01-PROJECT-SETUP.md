# Chapter 01: Project Setup

## What you'll learn

- How a Next.js project is organised
- What `package.json` does
- How to install D3.js and Rough.js
- How to verify everything works

## 1.1 Understanding the project structure

Open the project folder. Here's what matters:

```
javizstudio.github.io/
├── app/                 ← All your pages live here
│   ├── layout.tsx       ← The "wrapper" around every page (fonts, body tag)
│   ├── page.tsx         ← The home page (what you see at localhost:3000)
│   └── globals.css      ← Global styles (Tailwind imports)
├── public/              ← Static files (images, SVGs)
├── docs/                ← This tutorial
├── package.json         ← Your project's dependency list
├── tsconfig.json        ← TypeScript configuration
└── next.config.ts       ← Next.js settings
```

**Key concept: the `app/` folder IS your website.**

Every folder inside `app/` becomes a URL route. A file named `page.tsx` inside a folder becomes the content of that route:

```
app/page.tsx          → localhost:3000/
app/algorithms/page.tsx → localhost:3000/algorithms
app/about/page.tsx    → localhost:3000/about
```

This is called **file-based routing**. You don't configure routes anywhere — you just create folders and files.

> **Why this matters:** In Java (Spring Boot) or Python (Flask/Django), you write route annotations or URL patterns in a separate file. Next.js eliminates that — the file structure IS the routing. Less configuration, fewer places for things to go wrong.

## 1.2 What is `package.json`?

Think of it as your project's `pom.xml` (Maven) or `requirements.txt` (pip). It lists:
- What libraries your project depends on
- What scripts you can run (`npm run dev`, `npm run build`)

Your current dependencies:

```json
{
  "dependencies": {
    "d3": "^7.9.0",          ← Already installed!
    "next": "16.2.11",       ← The framework
    "react": "19.2.4",       ← UI library (Next.js uses React)
    "react-dom": "19.2.4"   ← React's browser renderer
  }
}
```

D3 is already here. We just need Rough.js and type definitions.

## 1.3 Install remaining dependencies

Open your terminal in the project root and run:

```bash
npm install roughjs
npm install --save-dev @types/d3
```

**What these do:**

| Package | Purpose | Why `--save-dev`? |
|---------|---------|-------------------|
| `roughjs` | Hand-drawn style SVG rendering | No — it runs in the browser, so it's a regular dependency |
| `@types/d3` | TypeScript type definitions for D3 | Yes — only needed during development, not in the final website |

> **`--save-dev` explained:** Some packages are only useful while you're writing code (type checkers, linters, test frameworks). They don't ship to your users. `--save-dev` puts them in `devDependencies` instead of `dependencies`. The final website bundle won't include them — it stays smaller.

After running those commands, your `package.json` should now include:

```json
{
  "dependencies": {
    "d3": "^7.9.0",
    "next": "16.2.11",
    "react": "19.2.4",
    "react-dom": "19.2.4",
    "roughjs": "^4.6.6"
  },
  "devDependencies": {
    "@types/d3": "^7.x.x",
    ...
  }
}
```

## 1.4 Start the dev server

```bash
npm run dev
```

Open `http://localhost:3000` in your browser. You should see the default Next.js page. That's the content of `app/page.tsx`.

**Leave this running.** Next.js has hot-reload — when you save a file, the browser updates automatically. No manual refresh needed.

## 1.5 Create the algorithms page

Create a new folder and file:

```
app/
└── algorithms/
    └── page.tsx
```

Put this inside `app/algorithms/page.tsx`:

```tsx
export default function AlgorithmsPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Algorithm Visualiser</h1>
      <p className="mt-2 text-gray-600">Coming soon...</p>
    </div>
  );
}
```

Now visit `http://localhost:3000/algorithms`. You should see your heading.

**What just happened:**

1. You created `app/algorithms/page.tsx`
2. Next.js automatically created a route at `/algorithms`
3. The function `AlgorithmsPage` returns JSX (HTML-like syntax inside JavaScript)
4. The `className` attribute is React's version of HTML's `class` (because `class` is a reserved word in JavaScript)
5. The Tailwind classes (`p-8`, `text-2xl`, etc.) style the elements without a CSS file

## 1.6 Verify D3 and Rough.js work

Let's quickly check that our libraries load. Update `app/algorithms/page.tsx`:

```tsx
"use client";

import * as d3 from "d3";
import { useEffect, useRef } from "react";

export default function AlgorithmsPage() {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg
      .append("rect")
      .attr("x", 10)
      .attr("y", 10)
      .attr("width", 100)
      .attr("height", 60)
      .attr("fill", "steelblue");
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Algorithm Visualiser</h1>
      <svg ref={svgRef} width={200} height={100} className="mt-4 border" />
    </div>
  );
}
```

Visit `/algorithms`. You should see a blue rectangle. If you do — D3 is working.

**Don't worry about understanding all of this yet.** We'll break down every concept (`"use client"`, `useRef`, `useEffect`, `d3.select`) in the next chapters. For now, you've confirmed the tools work.

## 1.7 What we haven't done yet (and why)

| Skipped for now | Why |
|----------------|-----|
| Rough.js test | We'll introduce it in Chapter 07, after you understand D3 basics |
| Code highlighting library | Chapter 04 — we'll build it ourselves first to understand how it works |
| State management | Chapter 03 — one concept at a time |

## Summary

✅ You know how the project is structured  
✅ You installed D3.js (already there), Rough.js, and @types/d3  
✅ You created a new page at `/algorithms`  
✅ You verified D3 renders inside your page  

## Key takeaway

**In Next.js, folders = routes. Files named `page.tsx` = page content.** That's the most important structural concept. Everything else (styling, data, interactivity) builds on top of this.

---

→ [Chapter 02: Your First Component](./02-YOUR-FIRST-COMPONENT.md)
