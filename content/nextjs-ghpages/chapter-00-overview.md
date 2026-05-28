# Chapter 0: The Blog That Teaches Back

## Chapters

- [Chapter 0: Overview (this page)](/blog/nextjs-ghpages/chapter-00-overview)
- [Chapter 1: First Deploy](/blog/nextjs-ghpages/chapter-01-first-deploy)
- [Chapter 2: Markdown Pipeline](/blog/nextjs-ghpages/chapter-02-markdown-pipeline)
- [Chapter 3: Beautiful Code](/blog/nextjs-ghpages/chapter-03-beautiful-code)
- [Chapter 4: Interactive Quiz](/blog/nextjs-ghpages/chapter-04-interactive-quiz)
- [Chapter 5: Code Playground](/blog/nextjs-ghpages/chapter-05-code-playground)
- [Chapter 6: Visualizer](/blog/nextjs-ghpages/chapter-06-visualizer)
- [Chapter 7: Finishing Touches](/blog/nextjs-ghpages/chapter-07-finishing-touches)
- [Chapter 8: Dark Mode](/blog/nextjs-ghpages/chapter-08-dark-mode)
- [Chapter 9: Streaming](/blog/nextjs-ghpages/chapter-09-streaming)
- [Chapter 10: Layout & Mobile](/blog/nextjs-ghpages/chapter-10-layout-mobile)
- [Chapter 11: Performance](/blog/nextjs-ghpages/chapter-11-performance)
- [Chapter 12: JS Essentials](/blog/nextjs-ghpages/chapter-12-js-essentials)
- [Chapter 13: React Mental Model](/blog/nextjs-ghpages/chapter-13-react-mental-model)
- [Chapter 14: Hooks Deep Dive](/blog/nextjs-ghpages/chapter-14-hooks-deep-dive)
- [Chapter 15: TypeScript](/blog/nextjs-ghpages/chapter-15-typescript)
- [Chapter 16: Supabase Setup](/blog/nextjs-ghpages/chapter-16-supabase-setup)
- [Chapter 17: View Counts](/blog/nextjs-ghpages/chapter-17-view-counts)
- [Chapter 18: Auth & Progress](/blog/nextjs-ghpages/chapter-18-auth-progress)
- [Chapter 19: Comments](/blog/nextjs-ghpages/chapter-19-comments)
- [Chapter 20: Monetization](/blog/nextjs-ghpages/chapter-20-monetization)
- [Chapter 21: Multi-Language](/blog/nextjs-ghpages/chapter-21-multi-language)
- [Chapter 22: Gated Resources](/blog/nextjs-ghpages/chapter-22-gated-resources)
- [Chapter 23: UI Design](/blog/nextjs-ghpages/chapter-23-ui-design)

---

## The Spark

You've been writing notes. Algorithms, Docker commands, physics simulations — scattered across Notion pages, local markdown files, random Gists. Some are good. Some could help other people. But they just sit there.

Then you see a blog where the code examples _run_. Where readers can drag items to sort them. Where a quiz pops up after an explanation and says "did you actually get that?"

You think: I want that. A blog that doesn't just show — it _teaches_.

## What We're Building

A GitHub Pages site powered by Next.js that:

1. **Reads plain markdown files** from folders — no CMS, no database
2. **Renders them beautifully** with syntax highlighting and navigation
3. **Embeds interactive components** — quizzes, code playgrounds, visualizers — right inside the markdown
4. **Deploys automatically** on every `git push` to `main`
5. **Costs nothing** — GitHub Pages is free

The stack:

| Layer         | Tool                                     | Why                                           |
| ------------- | ---------------------------------------- | --------------------------------------------- |
| Framework     | Next.js 16 (App Router)                  | Static export, React Server Components        |
| Content       | Plain `.md` files in folders             | Version controlled, easy to write             |
| Rendering     | `next-mdx-remote`                        | Renders markdown with custom React components |
| Styling       | Tailwind CSS + `@tailwindcss/typography` | Prose styling out of the box                  |
| Interactivity | Custom React components                  | Quizzes, playgrounds, visualizers             |
| Deploy        | GitHub Actions → `gh-pages` branch       | Push and forget                               |

**What these tools are (if you haven't heard of them):**

- **Next.js** — a React framework that handles routing, building, and optimization. Think of it as "React + batteries included." We use it because it can export a fully static site (no server needed).
- **Tailwind CSS** — instead of writing CSS in separate files, you add small utility classes directly to HTML elements (`class="text-lg font-bold"`). Faster to write, easier to maintain.
- **`next-mdx-remote`** — takes a markdown string and renders it as React components. This is what lets us embed `<Quiz>` inside a `.md` file.
- **GitHub Actions** — GitHub's built-in automation. We write a config file that says "on every push, build the site and deploy it." Free for public repos.
- **GitHub Pages** — free static hosting from GitHub. Your repo's `gh-pages` branch becomes a live website.

## The Journey

| Chapter | What You'll Build                                             |
| ------- | ------------------------------------------------------------- |
| 1       | Empty Next.js project → live on GitHub Pages in 10 minutes    |
| 2       | Markdown pipeline — folders become blog series automatically  |
| 3       | Syntax highlighting and prose styling that looks professional |
| 4       | Your first interactive component: a Quiz inside markdown      |
| 5       | Code Playground — editable, runnable code blocks              |
| 6       | Visualizer — animated step-by-step algorithm walkthroughs     |
| 7       | Navigation, SEO, and the finishing touches                    |

## Prerequisites

- **Basic React** — you know what components, props, and hooks are (even if you're not fluent yet). If you've done a React tutorial, that's enough.
- **Node.js 20+** — the JavaScript runtime that runs Next.js on your machine. Download from [nodejs.org](https://nodejs.org) if you don't have it.
- **A GitHub account** — free. This is where your code lives and where your site gets hosted.
- **Markdown experience** — you've written `# headings`, `**bold**`, and `` `code` `` before. That's all the markdown you need.

That's it. No Next.js experience needed — we'll build understanding as we go.

## Step 1: Create the Project

First, create a new GitHub repository and clone it locally (or open it in a Codespace). Then scaffold the Next.js project into it:

```bash
# Scaffold Next.js into the current directory
# . means "here" — no subfolder created, everything goes into your repo root
# --force allows scaffolding into a folder that already has files (like .git)
npx create-next-app@16.1.6 . --typescript --tailwind --app --no-src-dir --eslint --react-compiler --force
```

Say **yes** to the import alias (`@/*`).

**Why `.` instead of a folder name?** Using `.` puts the project directly in your repo root. This means your tooling configs (`.husky/`, `.prettierrc`, `.vscode/`) live alongside the Next.js files — one repo, one project, no nesting.

**Why `--force`?** `create-next-app` refuses to scaffold into a folder that already has files (like `.git` or existing configs). The `--force` flag tells it to proceed and merge — your existing files are preserved.

**What is the React Compiler?** Before React 19, you had to manually tell React "don't re-render this unless these values change" using `useMemo`, `useCallback`, and `React.memo`. The React Compiler is a build-time tool that analyzes your code and adds that memoization automatically. You write plain components. The compiler figures out what to optimize.

| Without React Compiler                        | With React Compiler                         |
| --------------------------------------------- | ------------------------------------------- |
| Manual `useMemo`, `useCallback`, `React.memo` | Write plain functions — compiler handles it |
| Easy to forget, causes unnecessary re-renders | Automatic, consistent, always correct       |
| Adds noise to every component                 | Clean, readable components                  |

## Step 2: Set Up Your Editor

With the project created, set up VS Code so it catches mistakes and formats code automatically. Five minutes now saves hours later.

### Install VS Code Extensions

Open VS Code → Extensions panel (Ctrl+Shift+X) → search and install each of these:

| Extension                     | Marketplace ID                    | What It Does                                                           |
| ----------------------------- | --------------------------------- | ---------------------------------------------------------------------- |
| **ESLint**                    | `dbaeumer.vscode-eslint`          | Shows JavaScript/TypeScript errors and warnings as you type            |
| **Prettier**                  | `esbenp.prettier-vscode`          | Auto-formats code on save (indentation, quotes, semicolons)            |
| **Tailwind CSS IntelliSense** | `bradlc.vscode-tailwindcss`       | Autocomplete for Tailwind classes + hover preview of CSS               |
| **ES7+ React Snippets**       | `dsznajder.es7-react-js-snippets` | Type `rafce` → generates a full React component skeleton               |
| **Error Lens**                | `usernamehw.errorlens`            | Shows error messages inline next to the code (not just red underlines) |

**Why these specific extensions?** ESLint + Prettier handle code quality and formatting automatically. Tailwind IntelliSense is essential because Tailwind has hundreds of class names — you can't memorize them all. Error Lens makes errors impossible to miss.

### Configure Format on Save

Create `.vscode/settings.json` in your project root:

```bash
mkdir -p .vscode && touch .vscode/settings.json
```

```jsonc
{
  // Use Prettier as the default code formatter (instead of VS Code's built-in)
  "editor.defaultFormatter": "esbenp.prettier-vscode",

  // Automatically format the file every time you press Ctrl+S
  // No more manual formatting — just save and it's clean
  "editor.formatOnSave": true,

  // When you save, also run ESLint's auto-fix
  // This fixes things like: unused imports, missing semicolons, wrong quotes
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
  },

  // Tell VS Code to use the project's TypeScript version (not its built-in one)
  // This ensures you get the same errors locally as in CI/build
  "js/ts.tsdk.path": "node_modules/typescript/lib",

  // Help Tailwind IntelliSense find class names in your JSX
  // Without this, autocomplete only works in plain HTML `class=""` attributes
  "tailwindCSS.experimental.classRegex": [["className\\s*=\\s*['\"]([^'\"]*)['\"]"]],
}
```

**What each setting does in practice:**

| Setting                  | Without it                                     | With it                                           |
| ------------------------ | ---------------------------------------------- | ------------------------------------------------- |
| `formatOnSave`           | You manually run Prettier or code stays messy  | Every save = perfectly formatted                  |
| `fixAll.eslint`          | You see red squiggles but have to fix manually | Auto-fixes on save (removes unused imports, etc.) |
| `js/ts.tsdk.path`        | Might use wrong TS version, different errors   | Matches your project exactly                      |
| `tailwindCSS.classRegex` | No autocomplete for `className="..."` in JSX   | Full Tailwind autocomplete in React               |

## Step 3: Configure Prettier

Prettier is an opinionated code formatter — it rewrites your code to follow consistent style rules. You configure it once, and every file in the project looks the same regardless of who wrote it.

Create `.prettierrc` in your project root:

```bash
touch .prettierrc
```

```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

Install Prettier and the Tailwind sorting plugin:

```bash
npm install -D prettier@3.4.2 prettier-plugin-tailwindcss@0.6.9
```

**What `prettier-plugin-tailwindcss` does:** Without it, Tailwind classes appear in whatever order you typed them. With it, classes are automatically sorted into a logical order (display → position → sizing → spacing → typography → colors). This makes scanning class lists much easier.

## Step 4: ESLint (Already Included)

ESLint is a "linter" — it reads your code and flags potential problems without running it. Think of it as a spell-checker for code. `create-next-app` installs and configures it for you automatically via the `--eslint` flag.

The config lives in `eslint.config.mjs` (you don't need to edit it). The defaults catch:

- **Unused variables** — you declared `const x = 5` but never used `x`
- **Missing React hook dependencies** — your `useEffect` uses a variable but doesn't list it in the dependency array
- **Accessibility issues** — an `<img>` without an `alt` attribute, a button without accessible text
- **Import errors** — importing from a file that doesn't exist

To run ESLint manually (checks all files):

```bash
# Scans all .ts/.tsx files and reports errors
# You rarely need this — VS Code shows errors inline as you type
npm run lint
```

With the VS Code settings above, you'll see errors inline as you type. No need to run it manually.

## Step 5: Pre-Commit Hooks

You don't want broken code, lint errors, or unformatted files in your git history. Git hooks run checks _before_ a commit goes through. If the check fails, the commit is rejected.

**Install Husky + lint-staged:**

Husky manages git hooks (scripts that run at specific git events). lint-staged runs linters only on files you're about to commit (not the whole project — much faster).

```bash
npm install -D husky@9.1.7 lint-staged@15.4.3  # Install as dev dependencies
npx husky init                                   # Creates .husky/ folder with a pre-commit hook file
```

**Edit `.husky/pre-commit`:**

```bash
# && means "only continue if the previous command succeeded"
# If tsc finds type errors, lint-staged never runs and the commit is blocked
npm run precommit:typecheck && npx lint-staged
```

**Add `lint-staged` config to `package.json`:**

Open your existing `package.json` and add these two fields alongside whatever is already there:

```jsonc
{
  "lint-staged": {
    // For TypeScript/React files: fix lint errors, then format
    "*.{ts,tsx}": [
      "eslint --fix", // Auto-fix ESLint issues (unused imports, etc.)
      "prettier --write", // Reformat to match .prettierrc rules
    ],
    // For non-code files: just format (no linting needed)
    "*.{md,json,css}": ["prettier --write"],
    // Run on ALL staged files — blocks commit if a secret is detected
    "*": ["secretlint"],
  },
  "scripts": {
    // tsc = TypeScript compiler, --noEmit = check types but don't output JS files
    "precommit:typecheck": "tsc --noEmit",
  },
}
```

**What happens on every commit:**

```
You run: git commit -m "add quiz component"
    ↓
Husky triggers the pre-commit hook
    ↓
tsc --noEmit checks for type errors across the whole project
    ↓
lint-staged runs ONLY on staged files (fast!)
    ↓
ESLint checks for errors → auto-fixes what it can
Prettier formats the code
Secretlint scans for leaked API keys or tokens
    ↓
If any check finds unfixable errors → commit BLOCKED ❌
If everything passes → commit goes through ✅
```

**Optional: prevent committing secrets**

Secretlint scans your staged files for patterns that look like API keys, tokens, or passwords. If it finds one, the commit is blocked before the secret reaches git history.

```bash
npm install -D secretlint@8.4.0 @secretlint/secretlint-rule-preset-recommend@8.4.0
```

Create `.secretlintrc.json`:

```bash
touch .secretlintrc.json
```

```json
{
  "rules": [
    {
      "id": "@secretlint/secretlint-rule-preset-recommend"
    }
  ]
}
```

**The safety net:**

| Check      | Catches                                 |
| ---------- | --------------------------------------- |
| ESLint     | Unused vars, missing deps, bad patterns |
| Prettier   | Inconsistent formatting                 |
| TypeScript | Type errors, missing props              |
| Secretlint | Leaked API keys, tokens                 |

All of this runs in ~2 seconds (only on staged files). You never push broken code again.

**Optional: enforce commit message format**

commitlint checks your commit message _before_ the commit goes through. If the message doesn't follow the convention, the commit is rejected.

```bash
npm install -D @commitlint/cli@19.8.0 @commitlint/config-conventional@19.8.0
echo '{"extends": ["@commitlint/config-conventional"]}' > .commitlintrc.json
```

Add a `commit-msg` husky hook:

```bash
echo 'npx commitlint --edit $1' > .husky/commit-msg
```

Now every commit message must follow the format `type: description`:

| Type       | When to use                             |
| ---------- | --------------------------------------- |
| `feat`     | Adding a new feature                    |
| `fix`      | Fixing a bug                            |
| `docs`     | Documentation changes only              |
| `chore`    | Maintenance (deps, config, tooling)     |
| `refactor` | Code change that isn't a fix or feature |
| `style`    | Formatting, missing semicolons, etc.    |

```bash
git commit -m "feat: add quiz component"   # ✅ passes
git commit -m "add quiz component"         # ❌ blocked — missing type
git commit -m "ch00"                       # ❌ blocked — missing type
```

## Step 6: Zero-Setup Option — GitHub Codespaces

Don't want to install anything locally? GitHub Codespaces gives you a full VS Code editor in the browser, running on a cloud VM. By adding a config file to your repo, you define exactly what that environment looks like — extensions, settings, even which commands to run on startup.

Add a `.devcontainer/devcontainer.json` to your repo:

```bash
mkdir -p .devcontainer && touch .devcontainer/devcontainer.json
```

```jsonc
{
  // Display name shown in the Codespace creation UI
  "name": "Next.js Blog",

  // Base Docker image — Microsoft provides pre-built images with Node.js installed
  // Pin to Node 22 (LTS) — matches the version we use throughout this series
  "image": "mcr.microsoft.com/devcontainers/javascript-node:22",

  // VS Code-specific customizations (extensions + settings)
  "customizations": {
    "vscode": {
      // Same settings as your local .vscode/settings.json
      "settings": {
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
          "source.fixAll.eslint": "explicit",
        },
      },
      // Extensions to auto-install — uses the extension marketplace IDs
      "extensions": [
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint",
        "bradlc.vscode-tailwindcss",
        "dsznajder.es7-react-js-snippets",
        "usernamehw.errorlens",
      ],
    },
  },

  // Automatically forward port 3000 from the container to your browser
  // So when you run `npm run dev`, you can access it immediately
  "forwardPorts": [3000],
}
```

Now anyone can:

1. Go to your repo on GitHub
2. Press `.` (opens github.dev) or click **Code → Codespaces → New**
3. Wait 30 seconds — full VS Code in the browser, everything configured
4. `npm run dev` → port 3000 forwarded → live preview

No Node install. No extension hunting. No config files to copy. Just open and code.

This also works for **contributors** — anyone who forks your repo gets the same environment. No "works on my machine" problems.

## The Philosophy

Every chapter follows the same pattern:

1. **The problem** — why do we need this?
2. **The simplest solution** — get it working first
3. **The real solution** — make it good
4. **Try it** — interactive exercise to confirm understanding

No filler. No "in this chapter we will learn about..." Just build, explain, build more.

### Commit Often, Commit Well

Every time something works — commit it. Don't batch up a day's work into one commit. Small commits mean:

- **Easy to revert** — broke something? Roll back one commit, not a day of work
- **Readable history** — future you can see exactly when and why each change was made
- **Safer to experiment** — you can try things knowing you can always get back to a working state

At the end of each chapter, you'll see a suggested commit. Use it as a checkpoint — the site works, the tests pass, the code is clean.

Commit message format (enforced by commitlint from Chapter 0):

```bash
git add .
git commit -m "feat: add quiz component to markdown pipeline"
```

| Type       | When to use                             |
| ---------- | --------------------------------------- |
| `feat`     | Adding something new                    |
| `fix`      | Fixing a bug                            |
| `docs`     | Documentation only                      |
| `chore`    | Maintenance (deps, config)              |
| `refactor` | Restructuring without changing behavior |
| `style`    | Formatting, whitespace                  |

Don't overthink the message. A clear `feat: add X` is always better than `update stuff`.

### Writing Rules

- **Never show code without context.** Before every code block, explain _what_ it does and _why_ it's needed. After the block, explain any non-obvious lines.
- **Assume the reader is smart but unfamiliar.** They can learn fast, but they haven't seen this before.
- **Comments inside code are mandatory** for anything non-trivial. If a line would make someone pause, add a comment.
- **No magic.** If something "just works," explain the mechanism. Readers should understand, not memorize.
- **Show the before and after.** When introducing a solution, show what the problem looks like first.

---

Let's start. Chapter 1: your first deploy.
