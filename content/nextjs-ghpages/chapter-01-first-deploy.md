# Chapter 1: Live in Ten Minutes

[← Chapter 0: Overview](/blog/nextjs-ghpages/chapter-00-overview) | [Chapter 2: The Markdown Pipeline →](/blog/nextjs-ghpages/chapter-02-markdown-pipeline)

---

## The Goal

By the end of this chapter, you'll have a Next.js site live at `https://yourusername.github.io`. One page, one sentence. The pipeline is what matters.

## What You'll Build

```
┌─────────────────────────────────────────────────────────┐
│  YOUR MACHINE                                           │
│                                                         │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ app/     │───▶│ next build   │───▶│ out/ folder  │  │
│  │ page.tsx │    │ (static      │    │ (HTML, CSS,  │  │
│  └──────────┘    │  export)     │    │  JS files)   │  │
│                  └──────────────┘    └──────┬───────┘  │
│                                             │          │
└─────────────────────────────────────────────┼──────────┘
                                              │ git push
                                              ▼
┌─────────────────────────────────────────────────────────┐
│  GITHUB                                                 │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │ Actions      │───▶│ gh-pages     │───▶│ GitHub   │  │
│  │ (rebuilds    │    │ branch       │    │ Pages    │  │
│  │  on push)    │    │ (static      │    │ (serves  │  │
│  └──────────────┘    │  files)      │    │  site)   │  │
│                      └──────────────┘    └──────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

Every push triggers this pipeline automatically. Write → push → live.

---

## Step 1: Check Your Environment

If you set up the devcontainer from Chapter 0, skip this. Otherwise, verify Node.js locally:

```bash
# Check your Node version — needs to be 20 or higher
node --version
# v20.x.x or v22.x.x
```

---

## Step 2: Create the Project

We pin `create-next-app` to an exact version so everyone following this series gets identical output.

```bash
# Scaffold Next.js into the CURRENT folder (not a subfolder)
# --force: allows scaffolding even if .husky/, .prettierrc exist
npx create-next-app@16.1.6 . \
  --typescript --tailwind --app \
  --no-src-dir --eslint --react-compiler --force
```

Say **yes** to the import alias (`@/*`).

**Why `.` instead of a folder name?** Scaffolds into the current directory — your existing configs (`.husky/`, `.prettierrc`) are preserved, not duplicated.

**Why `--force`?** Without it, `create-next-app` refuses to run in a non-empty folder.

**What is `--react-compiler`?** Before React 19, you manually added `useMemo`/`useCallback` everywhere to prevent re-renders. The React Compiler does this automatically at build time. You write plain components; it optimizes them.

---

## Step 3: Pin Dependency Versions

### Why pin?

The `^` prefix (e.g. `"^15.1.0"`) means "any compatible version up to the next major." Libraries sometimes ship bugs in minor releases. Pinning to exact versions means your build is reproducible — today, tomorrow, next year.

### Core dependencies

```jsonc
// 📁 package.json — replace dependency versions (remove ^ prefixes)
{
  "dependencies": {
    "next": "16.1.6",
    "react": "19.2.3",
    "react-dom": "19.2.3",
  },
}
```

### Markdown dependencies (for the blog pipeline)

```jsonc
// 📁 package.json — add these to "dependencies"
{
  "next-mdx-remote": "6.0.0",
  "gray-matter": "4.0.3",
  "remark-gfm": "4.0.1",
  "react-syntax-highlighter": "16.1.1",
  "@types/react-syntax-highlighter": "15.5.13",
}
```

### Dev dependencies

```jsonc
// 📁 package.json — replace devDependency versions
{
  "devDependencies": {
    "typescript": "5.7.0",
    "@types/node": "20.17.0",
    "@types/react": "19.0.0",
    "@types/react-dom": "19.0.0",
    "tailwindcss": "4.0.0",
    "@tailwindcss/postcss": "4.0.0",
    "@tailwindcss/typography": "0.5.19",
    "eslint": "9.17.0",
    "eslint-config-next": "16.1.6",
    "prettier": "3.4.2",
    "prettier-plugin-tailwindcss": "0.6.9",
    "babel-plugin-react-compiler": "19.1.0",
  },
}
```

Now install everything:

```bash
npm install
```

---

## Step 4: Install Markdown Plugins

These aren't included by `create-next-app` — we need them for the blog pipeline in later chapters:

```bash
# Renders .md files as React components
npm install next-mdx-remote@6.0.0 gray-matter@4.0.3 remark-gfm@4.0.1
```

```bash
# Syntax highlighting for code blocks
npm install react-syntax-highlighter@16.1.1
npm install -D @types/react-syntax-highlighter@15.5.13
```

```bash
# Typography plugin + Prettier with Tailwind class sorting
npm install -D @tailwindcss/typography@0.5.19
npm install -D prettier@3.4.2 prettier-plugin-tailwindcss@0.6.9
```

---

## Step 5: Configure Static Export

### What is static export?

By default, Next.js expects a Node.js server to render pages on each request. GitHub Pages can't run servers — it only serves static files. Setting `output: "export"` tells Next.js: "pre-build every page as plain HTML at build time."

| Default mode                | Static export (`output: "export"`)   |
| --------------------------- | ------------------------------------ |
| Needs a Node.js server      | Just static files — any host works   |
| Pages rendered per request  | Pages pre-built at build time        |
| API routes, middleware work | Only static/client features          |
| Deploy to Vercel, Railway   | Deploy to GitHub Pages, S3, anywhere |

### The config file

```typescript
// 📁 next.config.ts — replace entire file contents
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Generate static HTML in out/ instead of requiring a server
  output: "export",

  // GitHub Pages can't run Next.js's image optimizer
  images: { unoptimized: true },

  // React Compiler: auto-memoizes components at build time
  experimental: { reactCompiler: true },
};

export default nextConfig;
```

Save. Run `npm run build`. You see an `out/` folder appear — that's your entire site as static files.

---

## Step 6: Your First Page

### How routing works in App Router

Every `page.tsx` inside the `app/` folder becomes a URL route:

- `app/page.tsx` → `/` (homepage)
- `app/about/page.tsx` → `/about`
- `app/blog/[slug]/page.tsx` → `/blog/any-post-name`

The function is a React Server Component — it runs at build time, not in the browser.

### Write the homepage

```tsx
// 📁 app/page.tsx — replace entire file contents
export default function Home() {
  return (
    // max-w-2xl = 672px max width, mx-auto = center horizontally
    <main className="mx-auto max-w-2xl px-6 py-20">
      <h1 className="text-3xl font-bold text-gray-900">My Blog</h1>
      <p className="mt-4 text-gray-600">This site teaches back.</p>
    </main>
  );
}
```

If you're new to Tailwind: instead of CSS files, you apply utility classes directly. `text-3xl` = 30px font. `font-bold` = weight 700. `mt-4` = 16px margin-top.

Save. Run `npm run dev`. Open `http://localhost:3000`. You see a centered heading "My Blog" with a subtitle below it.

---

## Step 7: Update the Site Title

`create-next-app` sets a default title of "Create Next App." Fix it now:

```tsx
// 📁 app/layout.tsx — find the metadata export and update it
export const metadata: Metadata = {
  // Shown in browser tabs and search engine results
  title: "Your Blog Name",
  description: "Your blog description",
};
```

Save. Refresh. You see your custom title in the browser tab.

---

## Step 8: Push to GitHub

Create a repository on GitHub named `yourusername.github.io` (for a user site).

```bash
git init
git add .
git commit -m "chore: initial project setup"
```

```bash
# Link your local repo to GitHub and push
git remote add origin https://github.com/YOU/YOU.github.io.git
git push -u origin main
```

---

## Step 9: The Deploy Workflow

### What is GitHub Actions?

A CI/CD system built into GitHub. You define a YAML file describing steps to run. GitHub executes them on a fresh Linux VM every time you push.

### What this workflow does

```
push to main
    ↓
GitHub spins up a Linux VM
    ↓
Installs Node.js + your dependencies
    ↓
Runs `next build` → generates out/ folder
    ↓
Pushes out/ to the gh-pages branch
    ↓
GitHub Pages serves gh-pages as your site
```

### Create the workflow file

```bash
mkdir -p .github/workflows
```

```yaml
# 📁 .github/workflows/deploy.yml — create this file
name: Deploy to GitHub Pages

# Run on every push to main
on:
  push:
    branches: [main]

# Allow pushing to gh-pages branch
permissions:
  contents: write
```

```yaml
# 📁 .github/workflows/deploy.yml — continued (same file)
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm install
      - run: npm run build
      # Prevents GitHub from processing files with Jekyll
      - run: touch out/.nojekyll
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./out
```

### Line-by-line explanation

| Line                            | Why                                                          |
| ------------------------------- | ------------------------------------------------------------ |
| `on: push: branches: [main]`    | Only deploys from main — feature branches don't go live      |
| `permissions: contents: write`  | The action needs to create/update the `gh-pages` branch      |
| `runs-on: ubuntu-latest`        | Free Linux VM from GitHub (~6 min runtime)                   |
| `touch out/.nojekyll`           | Without this, GitHub ignores `_next/` (Next.js asset folder) |
| `peaceiris/actions-gh-pages@v3` | Community action that pushes a folder to a branch            |
| `${{ secrets.GITHUB_TOKEN }}`   | Auto-generated by GitHub — no manual setup needed            |

### Push the workflow

```bash
git add .
git commit -m "feat: add GitHub Actions deploy workflow"
git push
```

Save. Push. You see the Actions tab in GitHub running your workflow (yellow dot → green checkmark).

---

## Step 10: Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `gh-pages` / `/ (root)`
4. Click **Save**

Wait 2 minutes. Visit `https://yourusername.github.io`.

You see your page live on the internet.

---

## The `.nojekyll` File — Why It Matters

GitHub Pages assumes sites are Jekyll projects by default. Jekyll ignores files and folders starting with `_`. Next.js generates all its assets in `_next/`. Without `.nojekyll`, your CSS and JS won't load.

One empty file. Critical.

---

## What Just Happened

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ You write│────▶│ git push │────▶│ Actions  │────▶│ Site is  │
│ code     │     │          │     │ builds   │     │ live     │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

Every future push triggers this automatically. No deploy commands, no servers, no bills.

---

## Commit Your Progress

```bash
git add .
git commit -m "feat: scaffold Next.js project with static export"
git push
```

---

## What's Next

We have a live site with one page. In Chapter 2, we build the markdown pipeline — drop a `.md` file in a folder and it automatically becomes a blog post with syntax highlighting, navigation, and beautiful typography.

The content drives the site. Not the other way around.

[← Chapter 0: Overview](/blog/nextjs-ghpages/chapter-00-overview) | [Chapter 2: The Markdown Pipeline →](/blog/nextjs-ghpages/chapter-02-markdown-pipeline)
