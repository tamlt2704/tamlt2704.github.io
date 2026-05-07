# Chapter 7: The Rollback — "Go Back to Yesterday"

[← Chapter 6: Secrets](chapter-06-secrets.md) | [Chapter 8: The Cleanup →](chapter-08-advanced-workflows.md)

---

## The Disaster

Saturday night. You merge a PR that redesigns the homepage. The deploy succeeds. The site is live. You share the link on social media.

Sunday morning. Someone DMs you: "Your site is blank on mobile." You check. The new CSS breaks on screens under 768px. White page. Nothing renders.

You need to roll back to the previous version. But which commit was that? You scroll through `git log`:

```
a1b2c3d Redesign homepage layout
f4e5d6c Update footer links
b7a8c9d Add dark mode toggle
...
```

Which one was the last known-good deploy? You don't know. You never marked it.

## Tags: Bookmarks in History

A tag is a label on a specific commit. "This commit was version 1.0.0." "This commit was the last working deploy."

```bash
git tag v1.0.0
git push origin v1.0.0
```

That's it. Commit `a1b2c3d` is now tagged `v1.0.0`. You can always get back to it:

```bash
git checkout v1.0.0    # go to that exact state
```

### Annotated Tags (Better)

```bash
git tag -a v1.0.0 -m "First stable release with dark mode and contact form"
git push origin v1.0.0
```

`-a` creates an annotated tag — it stores the tagger, date, and message. Use annotated tags for releases. Use lightweight tags (`git tag name`) for temporary bookmarks.

```bash
git tag                    # list all tags
git show v1.0.0            # show tag details
git tag -d v1.0.0          # delete local tag
git push origin :v1.0.0    # delete remote tag
```

## Semantic Versioning

```
v1.2.3
│ │ │
│ │ └── PATCH: bug fixes, no new features
│ └──── MINOR: new features, backward compatible
└────── MAJOR: breaking changes
```

For a solo project, keep it simple:
- `v0.x.x` — still building, anything can change
- `v1.0.0` — first "real" release
- Bump PATCH for fixes, MINOR for features

Don't overthink it. The point is having markers you can roll back to.

## GitHub Releases

A release is a tag with a description and optional file attachments. It's the human-friendly version of a tag.

### Create a Release Manually

1. Go to repo → Releases → "Create a new release"
2. Choose tag: `v1.0.0` (or create a new one)
3. Title: `v1.0.0 — Dark Mode & Contact Form`
4. Description: what changed since the last release
5. Click "Publish release"

### Auto-Generate Release Notes

Click "Generate release notes." GitHub creates a changelog from merged PRs since the last tag:

```markdown
## What's Changed
* Add dark mode toggle by @you in #3
* Add contact form with validation by @you in #5
* Fix image paths for production by @you in #7

**Full Changelog**: https://github.com/you/sideproject/compare/v0.1.0...v1.0.0
```

This is why squash-merging PRs with good titles matters — they become your changelog.

## Automated Releases with GitHub Actions

Create a workflow that tags and releases when you're ready:

```yaml
# .github/workflows/release.yml
name: Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version tag (e.g., v1.2.0)'
        required: true

jobs:
  release:
    runs-on: ubuntu-latest
    
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create tag
        run: |
          git tag ${{ github.event.inputs.version }}
          git push origin ${{ github.event.inputs.version }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.event.inputs.version }}
          generate_release_notes: true
```

`workflow_dispatch` adds a "Run workflow" button in the Actions tab. You type the version, click run, and it creates the tag + release with auto-generated notes.

`fetch-depth: 0` clones the full history so the tag has the right context.

## Rolling Back

The homepage is broken on mobile. You need to roll back. Now you have tags.

### Option 1: Revert the PR

The safest approach. Find the merge commit and revert it:

```bash
git revert <merge-commit-hash> -m 1
git push
```

This creates a new commit that undoes the changes. History is preserved. The deploy workflow runs and deploys the reverted version.

### Option 2: Redeploy a Tag

If you want to deploy a specific tagged version:

```yaml
# .github/workflows/deploy.yml — add manual trigger
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      ref:
        description: 'Git ref to deploy (tag, branch, or SHA)'
        default: 'main'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.ref || github.ref }}
      # ... rest of deploy steps
```

Now you can go to Actions → Deploy → Run workflow → type `v1.0.0` → deploy that exact version.

```
Actions tab → Deploy to GitHub Pages → Run workflow
  ┌─────────────────────────────┐
  │ Git ref to deploy: v1.0.0   │
  │ [Run workflow]               │
  └─────────────────────────────┘
```

30 seconds later, the site is back to `v1.0.0`. The mobile bug is gone. You fix the CSS on a branch, merge it, and tag `v1.1.0`.

## The Release Workflow

```
feature branch → PR → CI ✅ → merge → auto deploy
                                         │
                    when ready:  tag v1.2.0 → GitHub Release
                                         │
                    if broken:   revert or redeploy v1.1.0
```

You don't tag every merge. You tag milestones — when a set of features is stable and you want a checkpoint.

## What You Learned

- Tags are bookmarks on commits — `git tag v1.0.0`
- Semantic versioning: MAJOR.MINOR.PATCH
- GitHub Releases = tags + changelogs + download links
- `workflow_dispatch` adds manual trigger buttons
- Rollback by reverting the merge commit or redeploying a tag
- Tag milestones, not every commit

You can roll back now. You have versions. But your workflow files are getting messy — duplicated steps, no caching strategy, hardcoded values everywhere.

Next chapter: cleaning up your workflows like a pro.

---

[← Chapter 6: Secrets](chapter-06-secrets.md) | [Chapter 8: The Cleanup →](chapter-08-advanced-workflows.md)
