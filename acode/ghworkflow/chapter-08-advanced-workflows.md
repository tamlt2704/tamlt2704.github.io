# Chapter 8: The Cleanup — "My Workflow File Is a Mess"

[← Chapter 7: Releases](chapter-07-releases.md) | [Chapter 9: The Playbook →](chapter-09-playbook.md)

---

## The Disaster

You have three workflow files. They all do `checkout → setup node → npm ci`. You update the Node version in one file and forget the others. CI runs on Node 20, deploy runs on Node 18. The build passes in CI but fails in deploy because of a Node 20 feature.

Your workflows have copy-paste duplication. Time to clean up.

## Reusable Workflows

Extract the common setup into a reusable workflow:

```yaml
# .github/workflows/setup.yml
name: Setup

on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '20'

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: 'npm'

      - run: npm ci
```

`workflow_call` means "this workflow can be called by other workflows." It's a function.

Use it in CI:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  setup:
    uses: ./.github/workflows/setup.yml

  check:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm run lint
      - run: npm test -- --ci
      - run: npm run build
```

Change the Node version in one place. All workflows use it.

Actually — for a solo developer, reusable workflows add complexity. A simpler approach: just keep your workflows consistent and use a comment at the top:

```yaml
# NOTE: Keep node-version in sync across all workflow files
# Current: 20
```

Pragmatism over architecture. You're solo. Don't over-engineer.

## Composite Actions

If you want DRY without the complexity of reusable workflows, use a composite action:

```yaml
# .github/actions/setup-project/action.yml
name: Setup Project
description: Checkout, install Node, install deps

inputs:
  node-version:
    default: '20'

runs:
  using: composite
  steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'

    - run: npm ci
      shell: bash
```

Use it in any workflow:

```yaml
steps:
  - uses: ./.github/actions/setup-project
  - run: npm run build
```

One line replaces three steps. Change the Node version in `action.yml`, all workflows update.

## Caching: Beyond npm

The `cache: 'npm'` in `setup-node` caches the npm download cache. But `npm ci` still installs (links) packages every time. For bigger projects, cache `node_modules` directly:

```yaml
      - name: Cache node_modules
        uses: actions/cache@v4
        with:
          path: node_modules
          key: node-modules-${{ hashFiles('package-lock.json') }}

      - name: Install (if cache miss)
        if: steps.cache.outputs.cache-hit != 'true'
        run: npm ci
```

Give the cache step an `id` to reference its output:

```yaml
      - name: Cache node_modules
        id: cache
        uses: actions/cache@v4
        with:
          path: node_modules
          key: node-modules-${{ hashFiles('package-lock.json') }}
```

If `package-lock.json` hasn't changed, skip `npm ci` entirely. Install time: 0 seconds.

For Next.js, also cache the build cache:

```yaml
      - name: Cache Next.js build
        uses: actions/cache@v4
        with:
          path: .next/cache
          key: nextjs-${{ hashFiles('package-lock.json') }}-${{ hashFiles('**/*.tsx', '**/*.ts') }}
          restore-keys: nextjs-${{ hashFiles('package-lock.json') }}-
```

## Concurrency: Don't Stack Deploys

You merge two PRs in quick succession. Two deploy workflows start. They race. The second one might deploy before the first one finishes, or they might conflict.

```yaml
# .github/workflows/deploy.yml
concurrency:
  group: deploy
  cancel-in-progress: true
```

`cancel-in-progress: true` — if a new deploy starts, cancel the old one. You always want the latest version.

For CI on PRs, use the PR number as the group:

```yaml
# .github/workflows/ci.yml
concurrency:
  group: ci-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

Push a fix to your PR branch? The old CI run cancels, the new one starts. No wasted minutes.

## Conditional Steps

Skip steps based on conditions:

```yaml
      - name: Deploy
        if: github.ref == 'refs/heads/main'
        run: echo "Deploying..."

      - name: Test
        if: github.event_name == 'pull_request'
        run: npm test
```

Useful for a single workflow that handles both PRs and pushes. But for solo work, separate files are clearer.

## Timeouts

A stuck workflow burns your free minutes. Set timeouts:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
```

If the job takes longer than 10 minutes, it's killed. Default is 360 minutes (6 hours). That's a lot of wasted minutes if something hangs.

## The Final Workflow Files

After cleanup:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm run lint
      - run: npm test -- --ci
      - run: npm run build
```

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      ref:
        description: 'Git ref to deploy'
        default: 'main'

concurrency:
  group: deploy
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    permissions:
      contents: read
      pages: write
      id-token: write

    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.ref || github.ref }}

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_FORMSPREE_URL: ${{ secrets.FORMSPREE_URL }}

      - uses: actions/upload-pages-artifact@v3
        with:
          path: out

      - uses: actions/deploy-pages@v4
```

Two files. Clean. No duplication that matters. Timeouts. Concurrency control.

## What You Learned

- Composite actions extract common steps into reusable blocks
- Cache `node_modules` and `.next/cache` for faster builds
- `concurrency` prevents stacking deploys and wasting CI minutes
- `timeout-minutes` kills stuck jobs
- Don't over-engineer — you're solo, keep it simple

One chapter left. The complete playbook — everything wired together.

---

[← Chapter 7: Releases](chapter-07-releases.md) | [Chapter 9: The Playbook →](chapter-09-playbook.md)
