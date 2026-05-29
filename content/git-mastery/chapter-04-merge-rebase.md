# Chapter 4: Merge vs Rebase

[prev: Remotes](chapter-03-remote.md) | [next: Undoing Things](chapter-05-undoing.md)

## When to Use Each

**Merge** — preserves history as it happened. Creates a merge commit. Best for:

- Integrating shared branches (main, develop)
- When you want to see when branches converged
- Public/shared branches

**Rebase** — rewrites history to be linear. Best for:

- Cleaning up local feature branch before merging
- Keeping a linear, readable history
- Private branches not yet shared

**Golden rule**: Never rebase commits that have been pushed and shared with others.

## Rebase

Replays your commits on top of another branch:

```bash
git switch feature
git rebase main
```

```
Before:
main:    A --- B --- C
                \
feature:         D --- E

After rebase:
main:    A --- B --- C
                      \
feature:               D' --- E'
```

D' and E' are new commits (different SHA) with the same changes. Then fast-forward:

```bash
git switch main
git merge feature    # fast-forward
```

## Interactive Rebase

The most powerful tool for cleaning up history:

```bash
git rebase -i HEAD~4       # last 4 commits
git rebase -i main         # all commits since diverging from main
```

Editor opens:

```
pick a1b2c3d Add user model
pick b2c3d4e Fix typo in model
pick c3d4e5f Add user controller
pick d4e5f6a Fix import

# p, pick = use commit as is
# r, reword = edit the commit message
# e, edit = stop for amending
# s, squash = meld into previous commit
# f, fixup = squash but discard message
# d, drop = remove commit
```

### Squash: Combine Commits

```
pick a1b2c3d Add user model
squash b2c3d4e Fix typo in model
pick c3d4e5f Add user controller
squash d4e5f6a Fix import
```

Result: 2 clean commits instead of 4.

### Fixup: Squash Without Message

```
pick a1b2c3d Add user model
fixup b2c3d4e Fix typo in model
```

Auto-fixup workflow:

```bash
git commit --fixup=a1b2c3d
git rebase -i --autosquash main
```

### Reword: Edit Commit Message

```
reword a1b2c3d Add user model
pick c3d4e5f Add user controller
```

### Edit: Pause and Amend

```
edit a1b2c3d Add user model
```

Git stops at that commit:

```bash
git add .
git commit --amend
git rebase --continue
```

## Merge Conflicts Resolution

### Step-by-Step

1. Start the merge:

```bash
git merge feature
```

Output:

```
CONFLICT (content): Merge conflict in file.txt
Automatic merge failed; fix conflicts and then commit the result.
```

2. See conflicted files:

```bash
git status
```

3. Open the file:

```
<<<<<<< HEAD
This is the main branch version
=======
This is the feature branch version
>>>>>>> feature
```

4. Edit — remove markers, keep what you want:

```
This is the merged version
```

5. Complete:

```bash
git add file.txt
git commit              # for merge
# or
git rebase --continue   # for rebase
```

### Useful Commands During Conflicts

```bash
git diff                        # show remaining conflicts
git checkout --ours file.txt    # take our version
git checkout --theirs file.txt  # take their version
git merge --abort               # cancel merge
git rebase --abort              # cancel rebase
```

## Rerere (Reuse Recorded Resolution)

Git remembers how you resolved a conflict and auto-applies it next time:

```bash
git config --global rerere.enabled true
```

```bash
git rerere status          # files rerere is tracking
git rerere diff            # what rerere would do
git rerere forget file.txt # forget a resolution
```

Especially useful when rebasing frequently against a moving target.

## Exercises

1. Create a branch with 5 commits, use `git rebase -i` to squash them into 2.

2. Create a merge conflict intentionally, resolve it step by step.

3. Enable rerere, resolve a conflict, recreate it, and observe auto-resolution.

4. Practice `git commit --fixup` and `git rebase -i --autosquash`.

5. Rebase a feature branch onto updated main, then fast-forward merge. Compare log to a three-way merge.
