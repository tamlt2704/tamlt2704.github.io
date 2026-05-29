# Chapter 7: Advanced Git

[prev: Team Workflows](chapter-06-workflows.md) | [next: Internals](chapter-08-internals.md)

## Cherry-Pick

Apply a specific commit from another branch:

```bash
git cherry-pick abc1234            # apply one commit
git cherry-pick abc1234 def5678    # apply multiple
git cherry-pick abc1234..def5678   # apply a range
git cherry-pick -n abc1234         # apply without committing
```

```
Before:
main:    A --- B
feature:       C --- D --- E

After cherry-pick D onto main:
main:    A --- B --- D'
feature:       C --- D --- E
```

Use cases: backporting a fix to a release branch, pulling one commit without merging the whole branch.

## Stash

Temporarily save uncommitted changes:

```bash
git stash                      # stash tracked changes
git stash -u                   # include untracked files
git stash save "WIP: feature"  # with a message
git stash list                 # list all stashes
git stash pop                  # apply most recent + remove from list
git stash apply                # apply but keep in list
git stash apply stash@{2}     # apply a specific stash
git stash drop stash@{0}      # delete a stash
git stash clear                # delete all stashes
git stash show -p              # show stash diff
```

Output of `git stash list`:

```
stash@{0}: WIP on feature: a1b2c3d Add login
stash@{1}: WIP on main: f4e5d6c Update readme
```

## Bisect

Binary search through commits to find which one introduced a bug:

```bash
git bisect start
git bisect bad                 # current commit is broken
git bisect good v1.0           # this tag/commit was working

# Git checks out a middle commit. Test it, then:
git bisect good                # this commit is fine
# or
git bisect bad                 # this commit has the bug

# Repeat until Git finds the culprit:
# abc1234 is the first bad commit

git bisect reset               # return to original HEAD
```

Automate with a test script:

```bash
git bisect start HEAD v1.0
git bisect run ./test.sh
# test.sh should exit 0 for good, 1 for bad
```

## Worktrees

Check out multiple branches simultaneously in separate directories:

```bash
git worktree add ../hotfix hotfix-branch
git worktree add ../feature feature-branch
git worktree list
git worktree remove ../hotfix
```

Output of `git worktree list`:

```
/home/user/project         a1b2c3d [main]
/home/user/hotfix          f4e5d6c [hotfix-branch]
```

Use cases: working on a hotfix while keeping your feature branch intact, running tests on another branch without switching.

## Submodules

Include another Git repository inside yours:

```bash
git submodule add https://github.com/lib/library.git vendor/library
git submodule init
git submodule update
git submodule update --init --recursive   # clone + init in one step
```

After cloning a repo with submodules:

```bash
git clone --recurse-submodules https://github.com/user/project.git
# or after cloning:
git submodule update --init --recursive
```

Update submodule to latest:

```bash
cd vendor/library
git pull origin main
cd ../..
git add vendor/library
git commit -m "Update library submodule"
```

Drawbacks: complex workflow, easy to forget updating, confusing for new contributors.

## Subtrees

Alternative to submodules — merges external repo into your tree:

```bash
# Add a subtree
git subtree add --prefix=vendor/lib https://github.com/lib/library.git main --squash

# Pull updates
git subtree pull --prefix=vendor/lib https://github.com/lib/library.git main --squash

# Push changes back upstream
git subtree push --prefix=vendor/lib https://github.com/lib/library.git main
```

Advantages over submodules: simpler for contributors (no init step), code is directly in the repo.

## Sparse Checkout

Check out only specific directories from a large repo:

```bash
git clone --no-checkout https://github.com/large/monorepo.git
cd monorepo
git sparse-checkout init --cone
git sparse-checkout set src/my-service docs
git checkout main
```

Only `src/my-service/` and `docs/` are on disk. Everything else is tracked but not checked out.

```bash
git sparse-checkout list       # show current patterns
git sparse-checkout add tests  # add another directory
git sparse-checkout disable    # check out everything again
```

## Git Hooks

Scripts that run automatically at certain points in the Git workflow. Located in `.git/hooks/`.

### pre-commit

Runs before a commit is created. Exit non-zero to abort:

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run linter
npm run lint
if [ $? -ne 0 ]; then
  echo "Lint failed. Fix errors before committing."
  exit 1
fi

# Check for debug statements
if grep -r "console.log" --include="*.ts" src/; then
  echo "Remove console.log statements before committing."
  exit 1
fi
```

### commit-msg

Validate or modify the commit message:

```bash
#!/bin/sh
# .git/hooks/commit-msg

# Enforce conventional commits format
commit_msg=$(cat "$1")
pattern="^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,72}"

if ! echo "$commit_msg" | grep -qE "$pattern"; then
  echo "Invalid commit message format."
  echo "Use: type(scope): description"
  echo "Types: feat, fix, docs, style, refactor, test, chore"
  exit 1
fi
```

### Sharing Hooks

Hooks in `.git/hooks/` aren't tracked. To share with the team:

```bash
# Store hooks in a tracked directory
mkdir .githooks
# Add hook scripts there

# Configure Git to use that directory
git config core.hooksPath .githooks
```

Or use a tool like Husky (Node.js) or pre-commit (Python).

## Exercises

1. Create two branches with different commits. Cherry-pick one specific commit from one branch to the other.

2. Make changes, stash them, switch branches, do other work, switch back, and pop the stash.

3. Create 10 commits where one introduces a "bug" (a specific string). Use `git bisect` to find it.

4. Set up a worktree for a second branch and verify both are accessible simultaneously.

5. Create a pre-commit hook that rejects commits containing "TODO" in staged files.
