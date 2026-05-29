# Chapter 5: Undoing Things

[prev: Merge vs Rebase](chapter-04-merge-rebase.md) | [next: Team Workflows](chapter-06-workflows.md)

## When to Use What

| Situation                         | Command                        |
| --------------------------------- | ------------------------------ |
| Fix last commit message           | `git commit --amend`           |
| Add forgotten file to last commit | `git commit --amend --no-edit` |
| Unstage a file                    | `git restore --staged file`    |
| Discard working dir changes       | `git restore file`             |
| Undo commit, keep staged          | `git reset --soft HEAD~1`      |
| Undo commit, keep unstaged        | `git reset --mixed HEAD~1`     |
| Undo commit, discard all          | `git reset --hard HEAD~1`      |
| Undo a public commit safely       | `git revert <commit>`          |
| Remove untracked files            | `git clean -f`                 |
| Recover lost commit               | `git reflog`                   |

## Amend

Fix the most recent commit:

```bash
git commit --amend -m "Better message"

git add forgotten-file.txt
git commit --amend --no-edit
```

Warning: amend rewrites the commit (new SHA). Don't amend pushed/shared commits.

## Reset

Moves the branch pointer backward. Three modes:

```
                    --soft     --mixed (default)    --hard
Repository:         undone     undone               undone
Staging area:       kept       undone               undone
Working directory:  kept       kept                 undone
```

```bash
git reset --soft HEAD~1    # undo commit, changes stay staged
git reset --mixed HEAD~1   # undo commit, changes unstaged
git reset --hard HEAD~1    # undo commit, changes GONE
git reset HEAD file.txt    # unstage a single file
```

Visualized:

```
Before (HEAD at C):
A --- B --- C (main, HEAD)

After git reset --soft HEAD~1:
A --- B (main, HEAD)     [C's changes staged]

After git reset --hard HEAD~1:
A --- B (main, HEAD)     [C's changes gone]
```

## Revert

Creates a new commit that undoes a previous commit. Safe for shared history:

```bash
git revert abc1234         # revert a specific commit
git revert HEAD            # revert the last commit
git revert HEAD~3..HEAD    # revert last 3 commits
git revert -n abc1234      # revert without auto-committing
```

Revert vs Reset:

- `revert` adds history (safe for shared branches)
- `reset` removes history (only for local branches)

## Restore (Git 2.23+)

Modern replacement for `git checkout -- file`:

```bash
git restore file.txt                  # discard working dir changes
git restore --staged file.txt         # unstage
git restore --source=HEAD~2 file.txt  # restore from 2 commits ago
git restore --staged --worktree file.txt  # unstage AND discard
```

## Checkout File (Legacy)

```bash
git checkout -- file.txt              # discard changes
git checkout abc1234 -- file.txt      # restore from commit
```

## Clean

Remove untracked files:

```bash
git clean -n               # dry run (preview)
git clean -f               # delete untracked files
git clean -fd              # delete files AND directories
git clean -fx              # delete untracked + ignored files
git clean -i               # interactive mode
```

Always run `-n` first.

## Recovering Lost Commits with Reflog

The reflog records every HEAD movement. Even after `reset --hard`, commits exist for ~30 days.

```bash
git reflog
```

Output:

```
a1b2c3d HEAD@{0}: reset: moving to HEAD~1
f4e5d6c HEAD@{1}: commit: Add important feature
b7a8c9d HEAD@{2}: commit: Update readme
```

Recover:

```bash
git branch recovered f4e5d6c
# or
git reset --hard f4e5d6c
```

Reflog is local only — not shared with remotes.

## Exercises

1. Make a commit, use `git commit --amend` to change its message. Verify with `git log`.

2. Make 3 commits, use `git reset --soft HEAD~3` to squash them into one.

3. Make a commit on main, revert it. Verify the revert commit in `git log`.

4. Create untracked files, preview with `git clean -n`, remove with `git clean -f`.

5. Use `git reset --hard` to "lose" a commit, recover it via `git reflog`.
