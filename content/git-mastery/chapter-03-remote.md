# Chapter 3: Working with Remotes

[prev: Branching](chapter-02-branching.md) | [next: Merge vs Rebase](chapter-04-merge-rebase.md)

## What Is a Remote?

A remote is a bookmark to another copy of the repository, usually on a server. The default remote after cloning is called `origin`.

## Managing Remotes

```bash
git remote                          # list remote names
git remote -v                       # list with URLs
git remote add origin https://github.com/user/repo.git
git remote add upstream https://github.com/original/repo.git
git remote rename origin old-origin
git remote remove old-origin
git remote set-url origin git@github.com:user/repo.git
```

Output of `git remote -v`:

```
origin  git@github.com:user/repo.git (fetch)
origin  git@github.com:user/repo.git (push)
```

## Fetch

Download commits and branches from a remote without merging:

```bash
git fetch origin               # fetch all branches from origin
git fetch origin main          # fetch only main
git fetch --all                # fetch from all remotes
```

After fetching, remote branches appear as `origin/main`, `origin/feature`, etc. Your local branches are untouched.

## Pull

Fetch + merge in one step:

```bash
git pull                       # fetch + merge current tracking branch
git pull origin main           # fetch origin/main and merge into current
git pull --rebase              # fetch + rebase instead of merge
```

## Push

Upload local commits to a remote:

```bash
git push origin main           # push main to origin
git push                       # push current branch to its upstream
git push -u origin feature     # push and set upstream tracking
git push --force-with-lease    # force push safely
```

## Upstream Tracking

Tracking links a local branch to a remote branch:

```bash
git branch -u origin/main              # set upstream for current branch
git push -u origin feature             # push and set upstream
git branch -vv                         # show tracking info
```

Output of `git branch -vv`:

```
* main    a1b2c3d [origin/main] Latest commit
  feature d4e5f6a [origin/feature: ahead 2] WIP
```

## The Fork Workflow

Used in open-source: you push to your fork, not the original repo.

```
┌─────────────────────────────────────┐
│  upstream (original repo)           │
│  github.com/original/project        │
└──────────────────┬──────────────────┘
                   │ fork (on GitHub)
┌──────────────────▼──────────────────┐
│  origin (your fork)                 │
│  github.com/you/project             │
└──────────────────┬──────────────────┘
                   │ clone
┌──────────────────▼──────────────────┐
│  local machine                      │
└─────────────────────────────────────┘
```

Setup:

```bash
git clone git@github.com:you/project.git
cd project
git remote add upstream https://github.com/original/project.git

# Keep your fork in sync
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

Contributing:

```bash
git switch -c my-fix
# ... make changes ...
git push -u origin my-fix
# Open a Pull Request from your fork to upstream
```

## SSH Keys Setup

Generate a key:

```bash
ssh-keygen -t ed25519 -C "your@email.com"
```

Start the agent and add key:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Copy public key to GitHub/GitLab:

```bash
cat ~/.ssh/id_ed25519.pub
```

Test:

```bash
ssh -T git@github.com
```

Output:

```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

Switch remote to SSH:

```bash
git remote set-url origin git@github.com:user/repo.git
```

## Exercises

1. Clone a repo, run `git remote -v`, add a second remote called `upstream`. Verify.

2. Create a local branch, push with `-u`, verify tracking with `git branch -vv`.

3. Fork a public repo, clone your fork, add upstream, fetch and merge upstream changes.

4. Set up SSH keys and switch a repository from HTTPS to SSH.

5. Use `git fetch` then `git log origin/main..main` to see local-only commits.
