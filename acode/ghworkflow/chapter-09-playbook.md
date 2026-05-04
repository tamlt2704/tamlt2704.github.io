# Chapter 9: The Playbook — "Ship Like a Pro"

[← Chapter 8: Advanced Workflows](chapter-08-advanced-workflows.md)

---

## The Full Picture

Nine chapters ago, you were pushing directly to `main` with no safety net. Now:

```
feature branch → push → PR → CI (type + lint + test + build)
                               │
                          review diff (30s self-review)
                               │
                          merge (squash) → auto deploy → live
                               │
                          tag milestone → GitHub Release
                               │
                          if broken → revert or redeploy tag
```

Every step exists because something broke. Every workflow file exists because you forgot something. The disasters came first. The playbook followed.

## The Daily Loop

```bash
# 1. Start work
git checkout main
git pull
git checkout -b feature/thing

# 2. Build
# ... code, commit, code, commit ...
git add .
git commit -m "Add thing"

# 3. Ship
git push -u origin feature/thing
# Open PR on GitHub
# CI runs automatically
# Review the diff (30 seconds)
# Squash and merge
# Deploy runs automatically
# Delete branch

# 4. Verify
# Check Actions tab — green?
# Check live site — working?
```

That's it. Every feature. Every fix. Every day.

## The File Tree

```
sideproject/
├── .github/
│   ├── actions/
│   │   └── setup-project/
│   │       └── action.yml          # (optional) composite action
│   ├── workflows/
│   │   ├── ci.yml                  # runs on PRs
│   │   ├── deploy.yml              # runs on merge to main
│   │   └── release.yml             # manual trigger for releases
│   └── pull_request_template.md    # PR checklist
├── src/
├── public/
├── .env.example                    # documents required env vars
├── .gitignore                      # keeps junk out
├── next.config.ts                  # static export config
├── package.json
└── README.md                       # with status badge
```

## The Cheat Sheet

### Git Commands

| What | Command |
|---|---|
| New branch | `git checkout -b feature/thing` |
| Stage all | `git add .` |
| Commit | `git commit -m "msg"` |
| Push branch | `git push -u origin feature/thing` |
| Switch branch | `git checkout main` |
| Update main | `git pull` |
| Tag a release | `git tag -a v1.0.0 -m "msg"` |
| Push tag | `git push origin v1.0.0` |
| Undo last commit | `git reset --soft HEAD~1` |
| Revert a merge | `git revert <hash> -m 1` |
| Stash changes | `git stash` / `git stash pop` |
| View history | `git log --oneline --graph` |

### GitHub Settings

| Setting | Where | Value |
|---|---|---|
| Branch protection | Settings → Branches | Require PR + status checks |
| Pages source | Settings → Pages | GitHub Actions |
| Secrets | Settings → Secrets → Actions | API keys, tokens |
| Variables | Settings → Variables → Actions | URLs, config |

### Workflow Triggers

```yaml
on:
  push:
    branches: [main]           # merge to main
  pull_request:
    branches: [main]           # PR against main
  workflow_dispatch:            # manual button
    inputs:
      version:
        type: string
  schedule:
    - cron: '0 9 * * 1'       # every Monday 9am UTC
```

## The Concept Map

```
                    GitHub Repository
                    ┌─────────────────────────────────┐
                    │                                   │
                    │  main (protected)                  │
                    │  ├── Branch protection             │
                    │  │   ├── Require PR                │
                    │  │   └── Require CI pass           │
                    │  │                                 │
                    │  ├── Tags: v1.0.0, v1.1.0, ...    │
                    │  └── Releases (auto-generated)     │
                    │                                   │
                    │  .github/workflows/                │
                    │  ├── ci.yml ──► runs on PR         │
                    │  │   └── typecheck, lint, test,    │
                    │  │       build                     │
                    │  ├── deploy.yml ──► runs on merge  │
                    │  │   └── build, upload, deploy     │
                    │  │       to Pages                  │
                    │  └── release.yml ──► manual        │
                    │      └── tag + release notes       │
                    │                                   │
                    │  Secrets: API keys (encrypted)     │
                    │  Variables: config (plain text)    │
                    │                                   │
                    └─────────────────────────────────┘
                                    │
                                    ▼
                            GitHub Pages
                            (your live site)
```

## What Each Chapter Taught You

| Ch | Disaster | Lesson | Key Concept |
|---|---|---|---|
| 1 | Pushed broken code | Git basics, `.gitignore` | Commits are snapshots |
| 2 | Overwrote own work | Branches, merging | Parallel timelines |
| 3 | Merged a TODO | Self-review via PR | The diff is the review |
| 4 | Forgot to deploy | GitHub Actions | Automation on merge |
| 5 | Build broke after merge | CI on PRs | Gate before merge |
| 6 | Leaked an API key | Secrets, `.env` | Never commit secrets |
| 7 | Couldn't roll back | Tags, releases | Bookmarks in history |
| 8 | Duplicated workflow code | Caching, concurrency | Keep it clean |
| 9 | — | Everything together | The playbook |

## The Rules

1. **Never commit to `main` directly** — always branch
2. **Never commit secrets** — use `.env.local` + GitHub Secrets
3. **Always PR** — even for yourself, the diff catches bugs
4. **Let the robot deploy** — never run deploy manually
5. **Tag milestones** — so you can roll back
6. **Keep workflows simple** — you're solo, not a platform team

## You're Done

You started with a folder on your desktop and `git push` on vibes. Now you have:

- A branching strategy that prevents overwrites
- Pull requests that catch bugs before they merge
- CI that blocks broken code from reaching `main`
- Automated deploys that never forget
- Secrets management that keeps your keys safe
- Version tags that let you roll back in 30 seconds
- Clean workflow files that don't waste your free minutes

Six files in `.github/` do half your job. The other half is writing code.

Ship it.

---

[← Chapter 8: Advanced Workflows](chapter-08-advanced-workflows.md)
