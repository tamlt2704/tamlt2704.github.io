# Chapter 6: The Leaked Secret — "Why Is My API Key on Google?"

[← Chapter 5: CI Checks](chapter-05-ci-checks.md) | [Chapter 7: The Rollback →](chapter-07-releases.md)

---

## The Disaster

You add a Formspree endpoint to your contact form:

```tsx
const FORMSPREE_URL = "https://formspree.io/f/xpznqkdl"

async function handleSubmit(data: FormData) {
  await fetch(FORMSPREE_URL, { method: 'POST', body: data })
}
```

You commit it. Push it. It works. Two weeks later, you get 500 spam submissions per day. Someone found your endpoint by searching GitHub.

That was a form endpoint — annoying but survivable. Now imagine it was an AWS access key. Or a database password. Or a Stripe secret key.

Git remembers everything. Even if you delete the line in the next commit, the secret is in the history. Forever. Anyone who clones your repo can find it with:

```bash
git log -p | grep "API_KEY"
```

## The Rule

**Never commit secrets. Ever. Not even once. Not even in a private repo.**

If it's a key, token, password, or endpoint you don't want public — it goes in environment variables, not in code.

## Environment Variables: The Right Way

### Local Development: `.env.local`

```bash
# .env.local — NEVER committed (already in .gitignore)
NEXT_PUBLIC_FORMSPREE_URL=https://formspree.io/f/xpznqkdl
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

Next.js loads `.env.local` automatically. Variables prefixed with `NEXT_PUBLIC_` are available in the browser. Without the prefix, they're server-only.

Use them in code:

```tsx
const FORMSPREE_URL = process.env.NEXT_PUBLIC_FORMSPREE_URL!

async function handleSubmit(data: FormData) {
  await fetch(FORMSPREE_URL, { method: 'POST', body: data })
}
```

No hardcoded values. The code works locally because `.env.local` provides the values. But what about CI?

### GitHub Actions: Repository Secrets

Go to repo → Settings → Secrets and variables → Actions → New repository secret.

| Name | Value |
|---|---|
| `FORMSPREE_URL` | `https://formspree.io/f/xpznqkdl` |

Use it in your workflow:

```yaml
      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_FORMSPREE_URL: ${{ secrets.FORMSPREE_URL }}
```

`${{ secrets.FORMSPREE_URL }}` injects the secret at runtime. It never appears in logs — GitHub masks it automatically. If your workflow tries to `echo` it, you'll see `***`.

### The `.env.example` Pattern

You can't commit `.env.local`. But Future You (or anyone cloning the repo) needs to know what variables are required. Create a template:

```bash
# .env.example — committed, no real values
NEXT_PUBLIC_FORMSPREE_URL=your_formspree_url_here
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

Commit `.env.example`. Add instructions to your README:

```markdown
## Setup
1. Copy `.env.example` to `.env.local`
2. Fill in your values
```

## The `.gitignore` Audit

Check your `.gitignore` has these:

```
# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.env*.local
```

If you already committed a secret, removing it from the file isn't enough. It's in Git history. You need to:

1. **Rotate the secret** — generate a new key, revoke the old one
2. **Clean history** (optional) — use `git filter-branch` or [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

Rotating is mandatory. Cleaning history is nice-to-have. Assume the old key is compromised.

## GitHub's Secret Scanning

GitHub automatically scans public repos for known secret patterns (AWS keys, Stripe keys, etc.) and alerts you. For private repos, you can enable it:

Settings → Code security and analysis → Secret scanning → Enable

It won't catch everything (like a Formspree URL), but it catches the dangerous ones.

## Updated Deploy Workflow

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
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_FORMSPREE_URL: ${{ secrets.FORMSPREE_URL }}
          NEXT_PUBLIC_SITE_URL: ${{ vars.SITE_URL }}

      - uses: actions/upload-pages-artifact@v3
        with:
          path: out

      - uses: actions/deploy-pages@v4
```

Notice two different syntaxes:
- `${{ secrets.FORMSPREE_URL }}` — encrypted, masked in logs, for sensitive values
- `${{ vars.SITE_URL }}` — plain text variables, for non-sensitive config

Set variables in Settings → Secrets and variables → Actions → Variables tab.

## Secrets vs Variables

| | Secrets | Variables |
|---|---|---|
| Encrypted | Yes | No |
| Masked in logs | Yes | No |
| Use for | API keys, tokens, passwords | URLs, feature flags, config |
| Syntax | `${{ secrets.NAME }}` | `${{ vars.NAME }}` |

## What You Learned

- Never commit secrets — use environment variables
- `.env.local` for local dev, repository secrets for CI
- `${{ secrets.NAME }}` injects secrets into workflows
- `.env.example` documents required variables without exposing values
- GitHub's secret scanning catches known key patterns
- If you leak a secret, rotate it immediately — deleting the commit isn't enough

Your secrets are safe. Your deploys are automated. But what happens when a deploy goes wrong and you need to go back to the previous version? Right now, you can't — there's no concept of "versions."

Next chapter: tags, releases, and the ability to roll back.

---

[← Chapter 5: CI Checks](chapter-05-ci-checks.md) | [Chapter 7: The Rollback →](chapter-07-releases.md)
