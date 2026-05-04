# Chapter 0: Before You Start

[Chapter 1: Your First Push →](chapter-01-first-push.md)

---

## The Story

This is a series about GitHub — but not the kind where you memorize "`git push` uploads code" and move on.

You're a solo developer building **SideProject**, a Next.js app you're deploying to GitHub Pages. You have no team. No code reviewer. No DevOps person. Just you, your laptop, and a growing pile of features that need to ship.

Day one, you create a repo. You push code directly to `main`. It works. Then you break production at 2am because you pushed a typo. Then you lose 3 hours of work because you forgot to commit. Then your deploy fails silently and you don't notice for a week.

Each disaster teaches you a GitHub workflow concept that no tutorial could. You'll fix every mistake, automate every pain point, and ship with confidence.

By the end, you'll have a complete solo developer workflow: branching strategy, pull requests (yes, even for yourself), GitHub Actions CI/CD, automated deploys, release tags, environment secrets, and a `.github/` folder that does half your job for you.

## How to Read This

Every chapter is the same loop:

1. Something breaks — your site is down, your code is lost, your deploy is wrong
2. You figure out what went wrong
3. You learn the GitHub concept that prevents it
4. You set it up
5. It never happens again

No concept shows up before you need it. You won't hear about branch protection until you push broken code to `main`. You won't touch GitHub Actions until you're tired of running `npm run deploy` manually.

The disasters come first. The workflow follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Solo Developer | Builds at night. Deploys on vibes. |
| **Past You** | The Saboteur | Wrote that code 3 weeks ago. Left no comments. |
| **Future You** | The Victim | Will debug Past You's mess at 2am. |
| **GitHub** | The Platform | Remembers everything. Judges nothing. |
| **The Green Lock** | Branch Protection | Won't let you merge garbage. |
| **The Robot** | GitHub Actions | Does exactly what you tell it. Nothing more. |

## The Roadmap

| Ch | The Disaster | What You Learn |
|---|---|---|
| 1 | You push broken code to `main` | Repos, commits, `.gitignore`, first push |
| 2 | You overwrite your own work | Branches, merging, the solo branch strategy |
| 3 | You merge a bug you could've caught | Pull requests for one — reviewing your own code |
| 4 | You forget to deploy after merging | GitHub Actions — your first workflow file |
| 5 | Your build passes but the site is broken | Testing in CI, build checks, status badges |
| 6 | You leak an API key in a commit | Secrets, `.env`, environment variables |
| 7 | You can't roll back a bad deploy | Tags, releases, versioning |
| 8 | Your workflow file is a mess | Reusable workflows, matrix builds, caching |
| 9 | You want to ship like a pro | The complete solo developer playbook |

## Prerequisites

Three things: Git, a GitHub account, and a terminal.

### Git

```bash
# Windows (winget)
winget install Git.Git

# macOS
brew install git

# Linux
sudo apt install git
```

Configure your identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

Verify:

```bash
git --version
```

### GitHub Account

Go to [github.com](https://github.com) and sign up. Free tier is all you need. You get unlimited public repos, unlimited private repos, 2,000 Actions minutes/month, and GitHub Pages hosting.

### Node.js (for the example project)

We'll use a Next.js static site as our running example — the same setup from the README.

```bash
node --version   # need 18+
npm --version
```

### Quick Check

```bash
git --version && node --version && echo "Ready"
```

If Git prints a version and Node prints 18+, you're good.

Let's break some things.

---

[Chapter 1: Your First Push →](chapter-01-first-push.md)
