# Chapter 2: The Overwrite — "Where Did My Code Go?"

[← Chapter 1: Your First Push](chapter-01-first-push.md) | [Chapter 3: The Self-Review →](chapter-03-pull-requests.md)

---

## The Disaster

Tuesday night. You're building two features at the same time:
1. A dark mode toggle
2. A contact form

You start dark mode. Halfway through, you get an idea for the contact form. You switch to working on that. You make changes to `layout.tsx` for the form. Then you remember dark mode also needs changes to `layout.tsx`.

You've been editing the same file for two different features. Your changes are tangled. You can't ship the contact form without shipping the half-finished dark mode. You can't undo the form changes without losing the dark mode work.

You `git stash` one, work on the other, pop the stash, get a merge conflict, panic, and run:

```bash
git checkout -- .   # nuclear option: discard all changes
```

Three hours of work. Gone.

Past You didn't use branches. Future You is furious.

## What's a Branch?

A branch is a parallel timeline. You split off from `main`, make changes in isolation, and merge back when you're done. If you mess up, `main` is untouched.

```
main:        c1 ── c2 ── c3 ─────────── c6 (merge)
                          \             /
feature/dark-mode:         c4 ── c5 ──┘
```

`main` stays clean. Your feature lives in its own lane. When it's ready, you merge it back. If it's garbage, you delete the branch. No harm done.

## Create a Branch

```bash
git checkout -b feature/dark-mode
```

That's it. You're now on a new branch called `feature/dark-mode`. Every commit you make goes here, not `main`.

```bash
git branch
#   main
# * feature/dark-mode    ← you are here
```

The `*` shows your current branch. Think of it as "which timeline am I in?"

### Naming Conventions

```
feature/dark-mode       # new feature
fix/broken-image-path   # bug fix
chore/update-deps       # maintenance
docs/add-readme         # documentation
```

The prefix tells Future You what the branch is for at a glance. No prefix? You'll have 20 branches named `test`, `test2`, `final`, `final-final`.

## The Solo Branch Strategy

Teams use complex branching models (GitFlow, trunk-based). You're solo. Keep it simple:

```
main (protected, always deployable)
  │
  ├── feature/dark-mode
  ├── fix/image-paths
  └── chore/update-next
```

Rules:
1. **Never commit directly to `main`** — always branch off
2. **One branch per feature/fix** — don't mix concerns
3. **Merge via pull request** — even for yourself (Chapter 3)
4. **Delete after merge** — keep it clean

That's the whole strategy.

## Build the Feature

You're on `feature/dark-mode`. Make your changes:

```tsx
// src/app/layout.tsx — add theme provider
import { ThemeProvider } from './providers'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  )
}
```

Commit as you go:

```bash
git add .
git commit -m "Add ThemeProvider to root layout"

# ... more work ...

git add .
git commit -m "Add dark mode toggle component"

# ... more work ...

git add .
git commit -m "Persist theme preference in localStorage"
```

Three commits. All on `feature/dark-mode`. `main` is untouched.

## Push the Branch

```bash
git push -u origin feature/dark-mode
```

Now the branch exists on GitHub too. The `-u` sets upstream so future pushes are just `git push`.

Go to your repo on GitHub. You'll see:

```
🔀 feature/dark-mode had recent pushes — Compare & pull request
```

We'll use that button in Chapter 3.

## Switch Between Branches

Here's where branches save you. Remember the contact form idea?

```bash
git checkout main                    # go back to main
git checkout -b feature/contact-form # new branch from main
```

Now you're working on the contact form. `layout.tsx` is clean — no dark mode changes. Two features, two branches, zero conflicts.

```bash
git checkout feature/dark-mode    # switch to dark mode
git checkout feature/contact-form # switch to contact form
git checkout main                 # switch to main
```

Each branch is a snapshot. Switching is instant. Your files literally change on disk when you switch branches. It's not magic — Git swaps the working directory contents.

```
main                    feature/dark-mode       feature/contact-form
┌──────────────┐       ┌──────────────┐        ┌──────────────┐
│ layout.tsx   │       │ layout.tsx   │        │ layout.tsx   │
│ (original)   │       │ (+ theme)    │        │ (+ form)     │
│              │       │ toggle.tsx   │        │ contact.tsx  │
│              │       │ providers.tsx│        │              │
└──────────────┘       └──────────────┘        └──────────────┘
```

Three versions of your project, coexisting peacefully.

## Merge: Bringing It Home

Dark mode is done. Time to merge it into `main`.

### Option A: Merge on GitHub (Recommended)

Create a pull request (Chapter 3 covers this in detail). Click "Merge". Done.

### Option B: Merge Locally

```bash
git checkout main                  # switch to main
git merge feature/dark-mode        # merge the branch
git push                           # push to GitHub
```

```
Updating a1b2c3d..d4e5f6g
Fast-forward
 src/app/layout.tsx    | 5 ++++-
 src/app/toggle.tsx    | 22 ++++++++++++++++++++++
 src/app/providers.tsx | 15 +++++++++++++++
 3 files changed, 41 insertions(+), 1 deletion(-)
```

"Fast-forward" means `main` had no new commits since you branched. Git just moves the pointer forward. No merge commit needed.

### Clean Up

```bash
git branch -d feature/dark-mode              # delete local branch
git push origin --delete feature/dark-mode   # delete remote branch
```

Don't hoard branches. Merged branches are dead branches. Delete them.

```bash
git branch
# * main
#   feature/contact-form    ← still working on this
```

## The Conflict: When Two Branches Touch the Same Line

You finish the contact form. You merge it. But wait — both dark mode and the contact form modified `layout.tsx`. Git doesn't know which version to keep.

```
<<<<<<< HEAD
        <ThemeProvider>{children}</ThemeProvider>
=======
        <ContactBanner />{children}
>>>>>>> feature/contact-form
```

This is a merge conflict. Git is saying: "Both branches changed this line. You decide."

### The Fix

Edit the file to combine both changes:

```tsx
<ThemeProvider>
  <ContactBanner />
  {children}
</ThemeProvider>
```

Then:

```bash
git add src/app/layout.tsx
git commit -m "Merge contact form — resolve layout conflict"
```

Conflicts are normal. They happen when two branches edit the same line. The fix is always: open the file, pick the right version, commit.

### Preventing Conflicts

1. **Keep branches short-lived** — merge within a day or two
2. **Pull `main` into your branch regularly** — `git merge main` while on your feature branch
3. **Don't edit the same files in parallel** — easier said than done

```bash
# While on feature/contact-form:
git merge main    # bring in latest main changes
# Fix any conflicts now, while they're small
```

## The Stash: "Hold My Beer"

You're mid-feature on `feature/contact-form`. Uncommitted changes everywhere. You need to switch to `main` to check something. Git won't let you switch with dirty files.

```bash
git stash                    # save uncommitted changes
git checkout main            # now you can switch
# ... check something ...
git checkout feature/contact-form
git stash pop                # restore your changes
```

`stash` is a clipboard for uncommitted work. Use it for quick context switches. Don't use it as a long-term storage — that's what branches are for.

```bash
git stash list               # see all stashes
git stash drop               # delete the top stash
git stash clear              # delete all stashes
```

## The Log: "What Did I Do Last Week?"

```bash
git log --oneline
# d4e5f6g Merge contact form — resolve layout conflict
# c3d4e5f Add contact form page
# b2c3d4e Persist theme preference in localStorage
# a1b2c3d Add dark mode toggle component
# 9z8y7x6 Initial commit: Next.js static site setup

git log --oneline --graph --all
# *   d4e5f6g (HEAD -> main) Merge contact form
# |\
# | * c3d4e5f (feature/contact-form) Add contact form page
# |/
# * b2c3d4e Persist theme preference
# * a1b2c3d Add dark mode toggle
# * 9z8y7x6 Initial commit
```

The `--graph` flag draws the branch history. You can see where branches split and merge. This is your project's timeline.

## The Undo Toolkit

| Situation | Command |
|---|---|
| Unstage a file | `git reset HEAD file.tsx` |
| Discard changes to a file | `git checkout -- file.tsx` |
| Undo last commit (keep changes) | `git reset --soft HEAD~1` |
| Undo last commit (discard changes) | `git reset --hard HEAD~1` |
| Revert a pushed commit | `git revert <hash>` |
| Go back to a specific commit | `git checkout <hash>` |

`reset --soft` is your best friend. It undoes the commit but keeps your changes staged. Perfect for "I committed too early."

`revert` is the safe undo for pushed commits. It creates a new commit that undoes the old one. History is preserved.

`reset --hard` is the nuclear option. Changes are gone. Use with caution.

## What You Learned

- Branches are parallel timelines — one per feature
- `git checkout -b name` creates and switches to a branch
- The solo strategy: `main` is sacred, everything else is a branch
- Merge conflicts happen when two branches edit the same line
- `git stash` is a clipboard for uncommitted work
- `git log --oneline --graph` shows your project's timeline
- Delete branches after merging — don't hoard

You're no longer overwriting your own work. But you're still merging without reviewing. You're the developer AND the reviewer — and right now, you're skipping the review.

Next chapter: pull requests for one. Yes, you're going to review your own code. It sounds weird. It catches bugs.

---

[← Chapter 1: Your First Push](chapter-01-first-push.md) | [Chapter 3: The Self-Review →](chapter-03-pull-requests.md)
