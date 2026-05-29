# Chapter 1: Git Basics

[Overview](chapter-00-overview.md) | [next: Branching](chapter-02-branching.md)

## The Three Areas

Git manages your files across three areas:

```
Working Directory    →    Staging Area (Index)    →    Repository (.git)
                git add                      git commit
```

- **Working Directory**: Files you see and edit on disk
- **Staging Area**: A snapshot of what will go into the next commit
- **Repository**: The full history of committed snapshots

## Initializing a Repository

```bash
git init my-project
cd my-project
```

Output:

```
Initialized empty Git repository in /home/user/my-project/.git/
```

## Cloning an Existing Repository

```bash
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git my-folder
```

## Checking Status

```bash
git status
```

Output after creating a file:

```
On branch main
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        hello.txt

nothing added to commit but untracked files present
```

## Staging Files

```bash
git add hello.txt          # stage a specific file
git add .                  # stage all changes in current directory
git add -p                 # interactively stage hunks
```

## Committing

```bash
git commit -m "Add hello.txt"
git commit                 # opens editor for longer message
git commit -am "msg"       # stage tracked files + commit in one step
```

Output:

```
[main (root-commit) a1b2c3d] Add hello.txt
 1 file changed, 1 insertion(+)
 create mode 100644 hello.txt
```

## Viewing History

```bash
git log                    # full log
git log --oneline          # compact one-line format
git log --oneline --graph  # with branch visualization
git log -5                 # last 5 commits
git log --author="Alice"   # filter by author
git log -- path/to/file    # history of a specific file
```

## Viewing Differences

```bash
git diff                   # working dir vs staging
git diff --staged          # staging vs last commit
git diff HEAD              # working dir vs last commit
git diff abc123 def456     # between two commits
git diff main feature      # between two branches
```

Example output:

```
diff --git a/hello.txt b/hello.txt
index ce01362..a042389 100644
--- a/hello.txt
+++ b/hello.txt
@@ -1 +1,2 @@
 Hello
+World
```

## .gitignore

Create a `.gitignore` file to exclude files from tracking:

```
# Compiled output
*.class
*.o
build/
dist/

# Dependencies
node_modules/
vendor/

# IDE files
.idea/
.vscode/
*.swp

# OS files
.DS_Store
Thumbs.db

# Environment
.env
.env.local
```

Rules:

- `#` for comments
- `*` matches anything except `/`
- `**` matches directories recursively
- `!` negates a pattern
- Trailing `/` matches only directories

```bash
git status --ignored       # check what's being ignored
git add -f secret.txt      # force-add an ignored file
git config --global core.excludesfile ~/.gitignore_global
```

## Exercises

1. Create a new repository, add three files, and make two commits. Use `git log --oneline` to verify.

2. Modify a file, use `git diff` to see changes, stage it, then use `git diff --staged`.

3. Create a `.gitignore` that excludes `*.log` and `tmp/`. Verify with `git status`.

4. Use `git log --oneline --graph --all` on a repository with multiple branches.

5. Practice `git add -p` to stage only part of a file's changes.
