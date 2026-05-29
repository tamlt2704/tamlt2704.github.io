# Chapter 2: Branching

[prev: Basics](chapter-01-basics.md) | [next: Remotes](chapter-03-remote.md)

## What Is a Branch?

A branch is simply a pointer to a commit. Creating a branch is instant — Git just writes a 41-byte file containing the SHA-1 hash of the commit it points to.

## HEAD Explained

HEAD is a pointer to the branch you're currently on. It tells Git which branch to advance when you make a new commit.

```
HEAD → main → commit C
```

When you switch branches, HEAD moves:

```
HEAD → feature → commit D
```

**Detached HEAD**: When HEAD points directly to a commit (not a branch), you're in "detached HEAD" state. Commits made here can be lost if you switch away without creating a branch.

## Creating Branches

```bash
git branch feature           # create branch (stay on current)
git switch -c feature        # create and switch (modern, Git 2.23+)
git checkout -b feature      # create and switch (old way)
```

## Switching Branches

```bash
git switch feature           # modern way
git checkout feature         # old way
```

## Listing Branches

```bash
git branch                   # local branches
git branch -r                # remote branches
git branch -a                # all branches
git branch -v                # with last commit info
```

Output:

```
* main
  feature
  bugfix/login
```

## Merging

### Fast-Forward Merge

When the target branch has no new commits since the branch point, Git just moves the pointer forward:

```
Before:
main:    A --- B
                \
feature:         C --- D

After (git switch main && git merge feature):
main:    A --- B --- C --- D
```

```bash
git switch main
git merge feature
```

Output:

```
Updating b1c2d3e..f4a5b6c
Fast-forward
 feature.txt | 1 +
 1 file changed, 1 insertion(+)
```

### Three-Way Merge

When both branches have diverged, Git creates a merge commit with two parents:

```
Before:
main:    A --- B --- E
                \
feature:         C --- D

After (git switch main && git merge feature):
main:    A --- B --- E --- M
                \         /
feature:         C --- D
```

Output:

```
Merge made by the 'ort' strategy.
 feature.txt | 1 +
 1 file changed, 1 insertion(+)
```

### No-Fast-Forward Merge

Force a merge commit even when fast-forward is possible:

```bash
git merge --no-ff feature
```

This preserves the fact that work happened on a branch.

## Deleting Branches

```bash
git branch -d feature        # delete (only if merged)
git branch -D feature        # force delete (even if unmerged)
```

## Visualizing Branch History

```bash
git log --oneline --graph --all
```

Output:

```
*   e5f6a7b (HEAD -> main) Merge branch 'feature'
|\
| * c3d4e5f (feature) Add feature
| * a1b2c3d Start feature work
|/
* 9f8e7d6 Initial commit
```

## Renaming Branches

```bash
git branch -m old-name new-name
git branch -m new-name             # rename current branch
```

## Exercises

1. Create a branch `feature`, add commits, merge back to `main` with fast-forward. Verify with `git log --oneline --graph`.

2. Create diverged branches and observe the three-way merge commit.

3. Use `git merge --no-ff` and compare the log to a fast-forward merge.

4. Enter detached HEAD by checking out a commit hash. Make a commit, then recover it by creating a branch.

5. Create three branches, merge them all back, and visualize with `git log --oneline --graph --all`.
