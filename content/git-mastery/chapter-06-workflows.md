# Chapter 6: Team Workflows

[prev: Undoing Things](chapter-05-undoing.md) | [next: Advanced](chapter-07-advanced.md)

## Git Flow

A structured workflow with long-lived branches:

```
main ─────────────────────────────────────── (production)
  \                                    /
   develop ──────────────────────────── (integration)
     \          /        \          /
      feature-A          feature-B
```

Branches:

- `main` — production-ready code, tagged with versions
- `develop` — integration branch for features
- `feature/*` — new features, branch from develop
- `release/*` — prepare a release, branch from develop
- `hotfix/*` — urgent fixes, branch from main

```bash
# Start a feature
git switch develop
git switch -c feature/user-auth

# Finish a feature
git switch develop
git merge --no-ff feature/user-auth
git branch -d feature/user-auth

# Start a release
git switch develop
git switch -c release/1.2.0
# ... bump version, fix bugs ...
git switch main
git merge --no-ff release/1.2.0
git tag v1.2.0
git switch develop
git merge --no-ff release/1.2.0

# Hotfix
git switch main
git switch -c hotfix/critical-bug
# ... fix ...
git switch main
git merge --no-ff hotfix/critical-bug
git tag v1.2.1
git switch develop
git merge --no-ff hotfix/critical-bug
```

Best for: teams with scheduled releases, multiple versions in production.

## GitHub Flow

Simpler: one main branch, short-lived feature branches, deploy from main.

```
main ─── A ─── B ─── C ─── D ─── E
              \         /
               feature-X
```

```bash
# 1. Create a branch
git switch -c feature-x

# 2. Make commits
git add .
git commit -m "Implement feature X"

# 3. Push and open PR
git push -u origin feature-x
# Open Pull Request on GitHub

# 4. Review, discuss, iterate

# 5. Merge (usually via GitHub UI)
# 6. Deploy from main
# 7. Delete branch
git switch main
git pull
git branch -d feature-x
```

Best for: continuous deployment, web apps, small teams.

## Trunk-Based Development

Everyone commits to main (trunk) directly or via very short-lived branches (< 1 day).

```
main ─── A ─── B ─── C ─── D ─── E ─── F
              \   /
               X        (lived < 1 day)
```

Key practices:

- Feature flags to hide incomplete work
- Small, frequent commits
- CI runs on every push to main
- No long-lived branches

```bash
# Short-lived branch (optional)
git switch -c quick-fix
git commit -am "Fix button alignment"
git switch main
git merge quick-fix
git branch -d quick-fix
git push
```

Best for: experienced teams, CI/CD pipelines, high deployment frequency.

## Pull Requests

A pull request (PR) / merge request (MR) is a request to merge your branch into another:

- Provides a place for code review
- Runs CI checks before merge
- Documents why changes were made
- Can require approvals before merge

PR best practices:

- Keep PRs small and focused (< 400 lines)
- Write a clear description of what and why
- Link to related issues
- Respond to review comments promptly

## Code Review

What to look for:

- Correctness and edge cases
- Readability and naming
- Test coverage
- Security implications
- Performance concerns

```bash
# Fetch and check out a PR locally
git fetch origin pull/123/head:pr-123
git switch pr-123
```

## Protected Branches

Configure on GitHub/GitLab to enforce rules on important branches:

- Require pull request reviews before merging
- Require status checks (CI) to pass
- Require linear history (no merge commits)
- Restrict who can push
- Require signed commits

## CODEOWNERS

A file that defines who must review changes to specific paths:

```
# .github/CODEOWNERS

# Default owners for everything
* @team-lead

# Frontend team owns UI code
/src/components/ @frontend-team
*.css @frontend-team

# Backend team owns API
/src/api/ @backend-team
/src/models/ @backend-team

# DevOps owns infrastructure
/infra/ @devops-team
Dockerfile @devops-team
```

When a PR touches files matching a pattern, those owners are automatically requested as reviewers.

## Exercises

1. Set up a Git Flow structure: create `develop` from `main`, create a feature branch, merge it back with `--no-ff`.

2. Simulate GitHub Flow: create a feature branch, push it, imagine a PR review, merge to main.

3. Practice trunk-based: make 5 small commits directly to main, each under 10 lines changed.

4. Create a CODEOWNERS file for a project with frontend, backend, and infrastructure directories.

5. Compare `git log --oneline --graph` output between Git Flow (many merge commits) and trunk-based (linear history).
