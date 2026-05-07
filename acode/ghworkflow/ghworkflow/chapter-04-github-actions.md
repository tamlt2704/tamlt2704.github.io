# Chapter 4: The Robot — "I Forgot to Deploy Again"

[← Chapter 3: Pull Requests](chapter-03-pull-requests.md) | [Chapter 5: The Broken Build →](chapter-05-ci-checks.md)

---

## The Disaster

Friday. You merge a PR with a beautiful new landing page. You close your laptop. You go out. Saturday morning, someone shares your site link. The landing page isn't there. The old version is still live.

You forgot to run `npm run deploy`.

This is the third time this month. You merge code, feel accomplished, and forget the last step. The code is on `main` but the site is stale.

You need a robot. A robot that deploys every time you merge to `main`. A robot that never forgets, never sleeps, and never goes out on Friday night.

That robot is **GitHub Actions**.

## What Is GitHub Actions?

GitHub Actions is a CI/CD system built into GitHub. You write a YAML file that says "when X happens, do Y." GitHub runs it on their servers. Free for public repos (2,000 minutes/month for private).

```
Trigger (when)  →  Job (what)  →  Steps (how)
   push to main      build         npm install
                     deploy        npm run build
                                   deploy to Pages
```

## Your First Workflow

Create the file:

```bash
mkdir -p .github/workflows
```

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      pages: write
      id-token: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: out

      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

That's it. 35 lines. Let's break it down.

## Anatomy of a Workflow

### The Trigger

```yaml
on:
  push:
    branches: [main]
```

"Run this workflow when someone pushes to `main`." Since you're merging PRs, every merge is a push to `main`. The robot wakes up automatically.

Other triggers you'll use:

```yaml
on:
  push:
    branches: [main]           # push to main
  pull_request:
    branches: [main]           # PR opened/updated against main
  schedule:
    - cron: '0 0 * * 1'       # every Monday at midnight
  workflow_dispatch:            # manual trigger button
```

### The Job

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
```

A job runs on a fresh virtual machine. `ubuntu-latest` is a Linux VM with common tools pre-installed. Every run starts clean — no leftover state from previous runs.

### The Steps

Each step is one command or action:

```yaml
steps:
  - name: Checkout code              # 1. Get your code
    uses: actions/checkout@v4

  - name: Setup Node.js              # 2. Install Node
    uses: actions/setup-node@v4
    with:
      node-version: '20'
      cache: 'npm'                   # cache node_modules

  - name: Install dependencies       # 3. npm install
    run: npm ci

  - name: Build                      # 4. next build → out/
    run: npm run build
```

Two types of steps:
- `uses:` — runs a pre-built action from the marketplace (like a plugin)
- `run:` — runs a shell command

`npm ci` instead of `npm install` — it's faster, stricter, and uses the exact versions from `package-lock.json`. Always use `ci` in CI.

### Permissions

```yaml
permissions:
  contents: read       # read your code
  pages: write         # deploy to GitHub Pages
  id-token: write      # authenticate with Pages
```

Least privilege. The robot can read your code and write to Pages. Nothing else.

## Enable GitHub Pages

Before the workflow works, enable Pages:

1. Go to repo → Settings → Pages
2. Source: **GitHub Actions** (not "Deploy from a branch")
3. Save

That's it. The workflow handles the rest.

## Push and Watch

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Actions deploy workflow"
git push
```

Go to your repo → Actions tab. You'll see the workflow running:

```
Deploy to GitHub Pages
  ✓ Checkout code          (2s)
  ✓ Setup Node.js          (5s)
  ✓ Install dependencies   (12s)
  ✓ Build                  (8s)
  ✓ Upload artifact        (3s)
  ✓ Deploy to GitHub Pages (15s)
  
  ✅ Completed in 45s
```

Your site is live. Automatically. Every time you merge to `main`.

You never run `npm run deploy` again.

## The Workflow File Explained

```
.github/
└── workflows/
    └── deploy.yml     ← GitHub reads this automatically
```

GitHub scans `.github/workflows/` for YAML files. Any file there is a workflow. You can have multiple:

```
.github/workflows/
├── deploy.yml         # deploy on push to main
├── ci.yml             # run tests on PRs (Chapter 5)
└── release.yml        # create releases (Chapter 7)
```

## The Alternative: `gh-pages` Branch Deploy

The README mentions `gh-pages -d out`. That's the old way — push static files to a `gh-pages` branch. It works, but the GitHub Actions approach is better because:

| `gh-pages` package | GitHub Actions |
|---|---|
| Runs on your laptop | Runs on GitHub's servers |
| You must remember to run it | Automatic on merge |
| Needs `npm install gh-pages` | No extra dependencies |
| Pushes to a branch | Uses Pages API directly |
| No build logs on GitHub | Full logs in Actions tab |

If you already have the `gh-pages` setup from the README, you can keep it as a manual fallback:

```json
{
  "scripts": {
    "deploy:manual": "next build && touch out/.nojekyll && gh-pages -d out -t true"
  }
}
```

But let the robot handle the day-to-day.

## Debugging a Failed Workflow

Your workflow will fail. Here's how to debug:

### Read the Logs

Click the failed run → click the failed step → read the red text.

```
Error: Process completed with exit code 1.
  npm ERR! Missing script: "build"
```

The error is almost always in the last red line. Read it before panicking.

### Common Failures

| Error | Cause | Fix |
|---|---|---|
| `Missing script: "build"` | No `build` script in `package.json` | Add `"build": "next build"` |
| `Module not found` | Missing dependency | Check `package.json`, run `npm ci` |
| `Permission denied` | Pages not enabled or wrong permissions | Settings → Pages → Source: GitHub Actions |
| `Node.js version` | Wrong version | Match `node-version` to your local version |

### Run Locally First

Before pushing a workflow change, test the build locally:

```bash
npm ci
npm run build
ls out/    # verify output exists
```

If it works locally but fails in CI, the difference is usually: environment variables, Node version, or missing files in `.gitignore`.

## What You Learned

- GitHub Actions runs workflows on GitHub's servers
- `.github/workflows/*.yml` files define workflows
- `on: push: branches: [main]` triggers on merge
- Steps use `actions/*` (plugins) or `run:` (shell commands)
- `npm ci` is the CI version of `npm install`
- GitHub Pages can deploy from Actions (not just branches)
- The Actions tab shows logs for every run

You have a robot. It deploys on every merge. But it deploys even when the build is broken — it just fails silently. You don't notice until someone tells you the site is down.

Next chapter: making the robot check your work before deploying.

---

[← Chapter 3: Pull Requests](chapter-03-pull-requests.md) | [Chapter 5: The Broken Build →](chapter-05-ci-checks.md)
