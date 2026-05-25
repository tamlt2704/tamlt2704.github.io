# Chapter 1: Live in Ten Minutes

[← Chapter 0: Overview](/blog/nextjs-ghpages/chapter-00-overview) | [Chapter 2: The Markdown Pipeline →](/blog/nextjs-ghpages/chapter-02-markdown-pipeline)

---

## The Goal

By the end of this chapter, you'll have a Next.js site live at `https://yourusername.github.io`. It'll show one page with one sentence. That's enough — the pipeline is what matters.

## Option A: Start with a Dev Container (Recommended)

If you set up the devcontainer from Chapter 0, you can start coding immediately in the cloud. Create a new repo on GitHub, add the `.devcontainer/devcontainer.json`, open a Codespace, and you're ready.

But the devcontainer needs a project to work with. Let's create one.

## Option B: Local Setup

If you're working locally, make sure you have Node.js 20+ installed:

```bash
# Check your Node version — needs to be 20 or higher
node --version
# v20.x.x or v22.x.x
```

## Create the Project (Pinned Versions)

We pin every dependency to an exact version. This prevents "it worked yesterday but broke today" situations where a minor update introduces breaking changes.

```bash
# Create a new Next.js project with TypeScript, Tailwind, App Router, and React Compiler
# We pin to version 16.1.6 — the same version used throughout this series
# --typescript: adds TypeScript support (type checking)
# --tailwind: adds Tailwind CSS (utility-first styling)
# --app: uses the App Router (modern Next.js routing)
# --no-src-dir: puts app/ at the root (simpler structure for a blog)
# --react-compiler: enables the React Compiler (automatic memoization)
npx create-next-app@16.1.6 . --typescript --tailwind --app --no-src-dir --eslint --react-compiler --force
```

Say **yes** to the import alias (`@/*`).

**Why `.` instead of `my-blog`?** Using `.` scaffolds into the current folder instead of creating a subfolder. This means your existing `.husky/`, `.prettierrc`, `eslint`, and `lint-staged` configs are automatically picked up — no duplication, no conflicts.

**Why `--force`?** `create-next-app` refuses to scaffold into a folder that already has files (like `.husky/`, `package.json`, `.prettierrc`). The `--force` flag tells it to proceed anyway and merge — your existing configs are preserved.

**What is the React Compiler?** Before React 19, you had to manually tell React "don't re-render this unless these values change" using `useMemo`, `useCallback`, and `React.memo`. It was easy to forget, easy to get wrong, and added noise to every component.

The React Compiler is a build-time tool that analyzes your code and adds that memoization automatically. You write plain components. The compiler figures out what to optimize. No manual `useMemo` needed.

| Without React Compiler                        | With React Compiler                         |
| --------------------------------------------- | ------------------------------------------- |
| Manual `useMemo`, `useCallback`, `React.memo` | Write plain functions — compiler handles it |
| Easy to forget, causes unnecessary re-renders | Automatic, consistent, always correct       |
| Adds noise to every component                 | Clean, readable components                  |

The `--react-compiler` flag installs `babel-plugin-react-compiler` and enables it in `next.config.ts` via `experimental.reactCompiler: true` automatically — no manual setup needed.

Now let's pin the versions. Open `package.json` and replace the dependency versions with exact numbers (no `^` prefix — that allows auto-upgrades):

```jsonc
{
  "dependencies": {
    // Core framework — pinned to exact versions used in this series
    "next": "16.1.6",
    "react": "19.2.3",
    "react-dom": "19.2.3",

    // Markdown rendering — converts .md files to React components
    "next-mdx-remote": "6.0.0",
    "gray-matter": "4.0.3", // Parses YAML frontmatter from markdown
    "remark-gfm": "4.0.1", // GitHub-flavored markdown (tables, task lists)

    // Syntax highlighting — colors code blocks by language
    "react-syntax-highlighter": "16.1.1",
    "@types/react-syntax-highlighter": "15.5.13",
  },
  "devDependencies": {
    // TypeScript — type checking at build time
    "typescript": "5.7.0",
    "@types/node": "20.17.0",
    "@types/react": "19.0.0",
    "@types/react-dom": "19.0.0",

    // Tailwind CSS v4 — utility-first styling
    "tailwindcss": "4.0.0",
    "@tailwindcss/postcss": "4.0.0",
    "@tailwindcss/typography": "0.5.19", // Beautiful prose styling

    // Code quality
    "eslint": "9.17.0",
    "eslint-config-next": "16.1.6",
    "prettier": "3.4.2",
    "prettier-plugin-tailwindcss": "0.6.9", // Auto-sorts Tailwind classes

    // React Compiler — automatically memoizes components at build time
    "babel-plugin-react-compiler": "19.1.0",
  },
}
```

Install everything:

```bash
npm install    # Downloads all packages listed in package.json
```

> **Why pin versions?** The `^` prefix (e.g. `"^15.1.0"`) means "any compatible version up to 16.0.0." That sounds safe, but libraries sometimes introduce bugs in minor releases. Pinning to exact versions means your project builds the same way today, tomorrow, and next year. Update manually when you're ready.

## Install the Markdown Plugins

These aren't included by `create-next-app` — we need them for our blog pipeline:

```bash
# next-mdx-remote: renders markdown as React components (supports custom components in .md)
# gray-matter: extracts YAML metadata from the top of markdown files
# remark-gfm: adds GitHub-flavored markdown support (tables, strikethrough, checkboxes)
npm install next-mdx-remote@6.0.0 gray-matter@4.0.3 remark-gfm@4.0.1

# react-syntax-highlighter: applies color themes to code blocks
npm install react-syntax-highlighter@16.1.1
npm install -D @types/react-syntax-highlighter@15.5.13

# Tailwind typography plugin: makes prose (paragraphs, headings, lists) look professional
npm install -D @tailwindcss/typography@0.5.19

# Prettier + Tailwind class sorting
npm install -D prettier@3.4.2 prettier-plugin-tailwindcss@0.6.9
```

## Configure for Static Export

GitHub Pages serves static files — it can't run a Node.js server. We need to tell Next.js to output plain HTML/CSS/JS instead of expecting a server.

Open `next.config.ts`:

```typescript
import type { NextConfig } from "next";

// NextConfig is a TypeScript type that defines all valid configuration options
// Your editor will autocomplete and validate these settings
const nextConfig: NextConfig = {
  // "export" mode: `next build` generates a static `out/` folder
  // Instead of a server that renders pages on request, ALL pages are pre-built as HTML files
  output: "export",

  // GitHub Pages can't run Next.js's image optimization server
  // This tells Next.js to use standard <img> tags instead
  images: {
    unoptimized: true,
  },

  // Enables the React Compiler — automatically optimizes components at build time
  // Added automatically by --react-compiler flag in create-next-app
  experimental: {
    reactCompiler: true,
  },
};

export default nextConfig;
```

**What changes with `output: "export"`:**

| Without (default)                                     | With `output: "export"`                       |
| ----------------------------------------------------- | --------------------------------------------- |
| Needs a Node.js server to run                         | Just static files — any web host works        |
| Pages rendered on each request                        | Pages pre-built at build time                 |
| Can use server-side features (API routes, middleware) | Only static/client features                   |
| Deploy to Vercel, Railway, etc.                       | Deploy to GitHub Pages, Netlify, S3, anywhere |

## Your First Page

Replace `app/page.tsx` with something simple. In Next.js App Router, every `page.tsx` file inside the `app/` folder becomes a route. This one is at the root, so it's your homepage (`/`):

```tsx
// app/page.tsx
// This is a React Server Component — it runs at build time, not in the browser.
// The function name doesn't matter, but it must be the default export.
export default function Home() {
  return (
    // Tailwind classes: max-w-2xl = max width 672px, mx-auto = center horizontally
    // px-6 = padding left/right 24px, py-20 = padding top/bottom 80px
    <main className="mx-auto max-w-2xl px-6 py-20">
      <h1 className="text-3xl font-bold text-gray-900">My Blog</h1>
      <p className="mt-4 text-gray-600">This site teaches back.</p>
    </main>
  );
}
```

If you're new to Tailwind: instead of writing CSS in a separate file, you apply small utility classes directly. `text-3xl` = font-size 30px. `font-bold` = font-weight 700. `mt-4` = margin-top 16px. It feels weird at first, then you never go back.

Test locally:

```bash
npm run dev
```

Open `http://localhost:3000`. You see your page. Good.

Now build the static version:

```bash
npm run build
```

Look at the `out/` folder that appeared. That's your entire site — plain HTML, CSS, and JS files. No server needed. That's what GitHub Pages will serve.

## Update Your Blog Title

`create-next-app` sets a default title of "Create Next App". Update it now in `app/layout.tsx`:

```tsx
export const metadata: Metadata = {
  title: "Your Blog Name", // Shown in browser tabs and search results
  description: "Your blog description",
};
```

This is the global title. Individual pages can override it with their own `generateMetadata` export — covered in Chapter 7.

```bash
git add app/layout.tsx
git commit -m "chore: update blog title and description"
```

## Push to GitHub

Create a repository on GitHub. Name it `yourusername.github.io` for a user site, or anything else for a project site.

These git commands initialize your project and push it to GitHub:

```bash
git init                    # Create a new git repository in this folder
git add .                   # Stage all files for commit
git commit -m "chore: initial project setup"  # Save the current state
git remote add origin https://github.com/yourusername/yourusername.github.io.git  # Link to GitHub
git push -u origin main     # Push code to GitHub (-u sets up tracking for future pushes)
```

## The Deploy Workflow

GitHub Actions is a CI/CD system built into GitHub. You define a workflow in a YAML file, and GitHub runs it automatically when certain events happen (like pushing code).

Create `.github/workflows/deploy.yml`:

```bash
mkdir -p .github/workflows && touch .github/workflows/deploy.yml
```

```yaml
# This file tells GitHub: "every time I push to main, build my site and deploy it"
name: Deploy to GitHub Pages

# Trigger: run this workflow whenever code is pushed to the main branch
on:
  push:
    branches: [main]

# Permission: allow the workflow to push to the gh-pages branch
permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest # Use a fresh Linux machine (free, provided by GitHub)
    steps:
      - uses: actions/checkout@v4 # Step 1: Download your code
      - uses: actions/setup-node@v4 # Step 2: Install Node.js
        with:
          node-version: 20
      - run: npm install # Step 3: Install dependencies (next, react, etc.)
      - run: npm run build # Step 4: Build static HTML into out/ folder
      - run: touch out/.nojekyll # Step 5: Tell GitHub Pages "don't use Jekyll"
      - uses: peaceiris/actions-gh-pages@v3 # Step 6: Push out/ folder to gh-pages branch
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }} # Auto-provided by GitHub, no setup needed
          publish_dir: ./out # Which folder to deploy
```

**Line-by-line breakdown:**

| Line                            | What it does                                                 |
| ------------------------------- | ------------------------------------------------------------ |
| `on: push: branches: [main]`    | Only runs when you push to `main` (not other branches)       |
| `permissions: contents: write`  | Allows the action to create/update the `gh-pages` branch     |
| `runs-on: ubuntu-latest`        | GitHub gives you a free Linux VM for ~6 minutes              |
| `actions/checkout@v4`           | Clones your repo into the VM                                 |
| `actions/setup-node@v4`         | Installs Node.js 20 on the VM                                |
| `npm run build`                 | Runs `next build` which generates static files in `out/`     |
| `touch out/.nojekyll`           | Creates an empty file that prevents Jekyll processing        |
| `peaceiris/actions-gh-pages@v3` | A community action that pushes a folder to `gh-pages` branch |
| `${{ secrets.GITHUB_TOKEN }}`   | A token GitHub auto-generates — you don't need to create it  |

Commit and push:

```bash
git add .
git commit -m "feat: add GitHub Actions deploy workflow"
git push
```

## Enable GitHub Pages

Go to your repo → Settings → Pages → Source: **Deploy from a branch** → Branch: `gh-pages` / `/ (root)` → Save.

Wait 2 minutes. Visit `https://yourusername.github.io`.

Your page is live.

## What Just Happened

```
You write code
    ↓ git push
GitHub Actions runs
    ↓ npm run build
Static HTML generated in out/
    ↓ pushed to gh-pages branch
GitHub Pages serves it
    ↓
The world sees your site
```

Every future push triggers this automatically. Write → push → live. No deploy commands, no servers, no bills.

## The `.nojekyll` File

Without it, GitHub Pages assumes your site is a Jekyll project and ignores files starting with `_`. Next.js generates `_next/` for its assets. The `.nojekyll` file says "serve everything as-is."

One empty file. Critical.

---

## Commit Your Progress

```bash
git add .
git commit -m "feat: scaffold Next.js project with static export"
git push
```

## What's Next

We have a live site with one page. Boring. In Chapter 2, we'll build the markdown pipeline — drop a `.md` file in a folder and it automatically becomes a blog post with syntax highlighting, navigation, and beautiful typography.

The content drives the site. Not the other way around.
