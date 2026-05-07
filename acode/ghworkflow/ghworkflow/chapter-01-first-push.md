# Chapter 1: Your First Push — "It Works on My Machine"

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: The Overwrite →](chapter-02-branches.md)

---

## The Setup

It's Saturday night. You've been building SideProject for a week — a Next.js static site. The code lives in a folder on your desktop. No version control. No backups. Just vibes.

You decide to put it on GitHub. How hard can it be?

## Create the Repo

Go to [github.com/new](https://github.com/new).

- Repository name: `sideproject`
- Visibility: Public (free GitHub Pages hosting)
- Don't initialize with README — you already have code

GitHub shows you this:

```
…or push an existing repository from the command line

git remote add origin https://github.com/YOUR_USERNAME/sideproject.git
git branch -M main
git push -u origin main
```

But wait. You don't have a Git repo yet. Let's fix that.

## Initialize Git

```bash
cd ~/Desktop/sideproject
git init
```

That's it. Git creates a hidden `.git/` folder that tracks everything. Your project is now a repository — a folder with memory.

```
sideproject/
├── .git/          ← Git's brain. Don't touch this.
├── src/
├── public/
├── package.json
├── next.config.ts
└── node_modules/  ← 300MB of JavaScript. Do NOT commit this.
```

## The First Mistake: Committing `node_modules`

You're excited. You add everything:

```bash
git add .
```

You just staged 47,000 files. 300MB of `node_modules`. Every dependency, every sub-dependency, every README in every package. Your push will take 20 minutes and your repo will be a bloated mess.

Past You doesn't know about `.gitignore`. Future You will curse this moment.

### The Fix: `.gitignore`

Create `.gitignore` in the project root:

```
# Dependencies
node_modules/

# Build output
.next/
out/

# Environment
.env
.env.local
.env*.local

# OS junk
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
```

Rules are simple:
- One pattern per line
- `folder/` ignores the entire folder
- `*.ext` ignores all files with that extension
- `!important.env` negates a rule (force-include)

Now reset and re-add:

```bash
git reset    # unstage everything
git add .    # re-add (now respects .gitignore)
git status   # verify — no node_modules
```

`git status` is your sanity check. Run it before every commit. It shows what's staged (green), modified (red), and untracked.

## Your First Commit

```bash
git commit -m "Initial commit: Next.js static site setup"
```

A commit is a snapshot. A save point. A moment in time you can always return to. The `-m` flag is the message — a note to Future You explaining what this snapshot contains.

```
[main (root-commit) a1b2c3d] Initial commit: Next.js static site setup
 12 files changed, 847 insertions(+)
```

That hash (`a1b2c3d`) is the commit's fingerprint. Unique across the entire universe. Git uses it to identify this exact snapshot forever.

### What Makes a Good Commit Message

Bad:
```
git commit -m "stuff"
git commit -m "fix"
git commit -m "asdfgh"
```

Good:
```
git commit -m "Add static export config for GitHub Pages"
git commit -m "Fix image paths for production build"
git commit -m "Add Chakra UI and configure provider"
```

Future You is reading these at 2am trying to find which commit broke the site. Be kind to Future You.

## Connect to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/sideproject.git
```

`origin` is just a nickname for the GitHub URL. Convention, not magic. You could call it `banana` and it would work the same.

```bash
git remote -v
# origin  https://github.com/YOUR_USERNAME/sideproject.git (fetch)
# origin  https://github.com/YOUR_USERNAME/sideproject.git (push)
```

## Push

```bash
git branch -M main
git push -u origin main
```

- `branch -M main` — rename your default branch to `main`
- `push -u origin main` — push to GitHub and set `origin/main` as the upstream (so future `git push` works without arguments)

```
Enumerating objects: 15, done.
Counting objects: 100% (15/15), done.
Writing objects: 100% (15/15), 4.21 KiB | 4.21 MiB/s, done.
Total 15 (delta 0), reused 0 (delta 0)
To https://github.com/YOUR_USERNAME/sideproject.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

Refresh GitHub. Your code is there. You feel invincible.

## The Disaster: Pushing Broken Code

It's 11pm. You're adding a new component. You make a typo in `page.tsx`:

```tsx
export default function Home() {
  return (
    <div>
      <h1>Welcome to SideProject</h
    </div>  // ← unclosed tag
  )
}
```

You don't notice. You commit and push:

```bash
git add .
git commit -m "Add homepage content"
git push
```

You go to bed. The next morning, you run `npm run deploy`. The build fails. Your site is down. The last working version? Gone — you pushed directly to `main` and there's no safety net.

You check the error:

```
./src/app/page.tsx
Error: Unexpected token. Expected jsx identifier
```

One typo. One push. Site down.

### The Lesson

Pushing directly to `main` is like editing a Google Doc with no undo. Every push is live. Every mistake is permanent (well, not really — Git remembers everything, but reverting is painful).

We'll fix this in Chapter 2 with branches, and in Chapter 4 with automated builds that catch errors before they reach `main`.

## The Quick Fix: Amend

For now, fix the typo and amend the commit:

```bash
# Fix the typo in page.tsx, then:
git add src/app/page.tsx
git commit --amend -m "Add homepage content"
git push --force
```

`--amend` rewrites the last commit instead of creating a new one. `--force` overwrites the remote. This is fine when you're solo. In a team, force-pushing is a war crime.

## The Mental Model

```
Your Laptop                          GitHub
┌──────────────────┐                ┌──────────────────┐
│  Working Dir     │                │  Remote (origin)  │
│  (your files)    │                │                    │
│       │          │                │  main branch       │
│       ▼          │                │  ┌──┬──┬──┐       │
│  Staging Area    │   git push     │  │c1│c2│c3│       │
│  (git add)       │ ──────────►    │  └──┴──┴──┘       │
│       │          │                │                    │
│       ▼          │   git pull     │                    │
│  Local Repo      │ ◄──────────    │                    │
│  (.git/)         │                │                    │
└──────────────────┘                └──────────────────┘
```

Three places your code lives:
1. **Working directory** — the files you see and edit
2. **Staging area** — the "shopping cart" before a commit (`git add`)
3. **Repository** — the permanent history (local `.git/` and remote on GitHub)

`git add` moves changes to staging. `git commit` saves staging to the local repo. `git push` syncs local repo to GitHub.

## The Commands You'll Use Every Day

```bash
git status              # What changed?
git add .               # Stage everything
git add file.tsx        # Stage one file
git commit -m "msg"     # Save snapshot
git push                # Upload to GitHub
git pull                # Download from GitHub
git log --oneline       # Show commit history
git diff                # Show unstaged changes
```

That's 8 commands. You'll use them hundreds of times. Everything else is situational.

## What You Learned

- `git init` creates a repo
- `.gitignore` keeps junk out of your repo
- `git add` → `git commit` → `git push` is the daily loop
- Commit messages are for Future You
- Pushing directly to `main` has no safety net
- `--amend` and `--force` fix mistakes (solo only)

Your code is on GitHub. Your site deployed once. Then you broke it with a typo because there's nothing between your keyboard and production.

Next chapter: you'll overwrite your own work because you don't know what a branch is.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: The Overwrite →](chapter-02-branches.md)
