# Chapter 5: The Broken Build — "The Tests Pass... Right?"

[← Chapter 4: GitHub Actions](chapter-04-github-actions.md) | [Chapter 6: The Leaked Secret →](chapter-06-secrets.md)

---

## The Disaster

Monday. You open a PR. It looks good. You merge it. The deploy workflow runs. It fails at the build step:

```
./src/app/page.tsx
Type error: Property 'title' does not exist on type 'Post'.
```

You broke the build. The deploy failed. Your site is still showing last week's version. You didn't notice for two days because you never checked the Actions tab.

The problem: your deploy workflow only runs AFTER merging to `main`. By the time it fails, the broken code is already on `main`. You need a workflow that runs BEFORE merging — on the PR itself.

## Two Workflows, Two Jobs

```
PR opened/updated → CI workflow (build + test) → ✅ or ❌
                                                    │
Merge to main → Deploy workflow → 🚀               │
                                                    │
Branch protection: "CI must pass before merge" ◄────┘
```

The deploy workflow from Chapter 4 stays. You add a second workflow that runs on PRs.

## The CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npm run lint

      - name: Build
        run: npm run build
```

This runs on every PR against `main`. Three checks:

1. **Type check** — catches type errors without building
2. **Lint** — catches style issues, unused imports, etc.
3. **Build** — catches everything else

If any step fails, the whole job fails. The PR shows a red ❌.

## Required Status Checks

The CI workflow is useless if you can merge anyway. Make it mandatory.

Go to Settings → Branches → Edit `main` rule:

- [x] **Require status checks to pass before merging**
- Search for `build` (the job name from `ci.yml`)
- Select it

Now your PR shows:

```
🔴 build — Required
   Some checks haven't completed yet

   ⏳ CI / build — In progress
```

You can't click "Merge" until it's green:

```
🟢 build — Required
   All checks have passed

   ✅ CI / build — Passed
```

The Green Lock from Chapter 3 just got teeth.

## Adding Tests

Type checking and linting catch syntax issues. Tests catch logic bugs.

Add a test script to `package.json`:

```json
{
  "scripts": {
    "test": "jest",
    "build": "next build",
    "lint": "next lint"
  }
}
```

Install Jest (if not already):

```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

Write a simple test:

```tsx
// src/__tests__/utils.test.ts
import { formatDate } from '../utils/format'

describe('formatDate', () => {
  it('formats ISO date to readable string', () => {
    expect(formatDate('2024-01-15')).toBe('January 15, 2024')
  })

  it('returns "Invalid date" for garbage input', () => {
    expect(formatDate('not-a-date')).toBe('Invalid date')
  })
})
```

Add the test step to CI:

```yaml
      - name: Test
        run: npm test -- --ci --coverage
```

`--ci` makes Jest fail on missing snapshots instead of creating them. `--coverage` generates a coverage report.

The full CI workflow now:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm test -- --ci --coverage

      - name: Build
        run: npm run build
```

Four gates. All must pass. One failure blocks the merge.

## Status Badges

Add a badge to your README so you can see CI status at a glance:

```markdown
![CI](https://github.com/YOUR_USERNAME/sideproject/actions/workflows/ci.yml/badge.svg)
```

This renders as a green "passing" or red "failing" badge. You'll see it every time you open the repo.

## The PR Experience Now

```
feature/new-page → PR → CI runs automatically
                         │
                         ├── ✅ Type check
                         ├── ✅ Lint
                         ├── ✅ Tests (4 passed)
                         ├── ✅ Build
                         │
                         └── 🟢 Ready to merge
                                    │
                              Merge to main
                                    │
                              Deploy workflow → 🚀 Live
```

If any check fails:

```
feature/broken → PR → CI runs
                       │
                       ├── ✅ Type check
                       ├── ❌ Lint (unused import)
                       │
                       └── 🔴 Blocked — fix and push again
```

You push a fix to the same branch. CI re-runs. Green. Merge.

## Caching: Don't Reinstall Every Time

`npm ci` downloads all dependencies every run. For a Next.js project, that's 200+ packages. The `cache: 'npm'` in `setup-node` helps, but you can go further:

```yaml
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
```

This caches the npm global cache based on `package-lock.json`. If the lock file hasn't changed, dependencies are restored from cache instead of downloaded. Cuts install time from ~15s to ~3s.

## What You Learned

- CI workflows run on PRs, deploy workflows run on merge
- Required status checks block merging until CI passes
- Type check → Lint → Test → Build is the standard gate order
- `npm ci` + cache makes CI fast
- Status badges show build health at a glance
- The PR is now: branch → push → CI → review → merge → deploy

Your robot checks your work before deploying. But there's something it can't check — secrets. Next chapter: you commit an API key and learn about environment variables the hard way.

---

[← Chapter 4: GitHub Actions](chapter-04-github-actions.md) | [Chapter 6: The Leaked Secret →](chapter-06-secrets.md)
