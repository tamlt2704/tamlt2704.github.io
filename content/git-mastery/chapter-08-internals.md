# Chapter 8: Git Internals

[prev: Advanced](chapter-07-advanced.md) | [Overview](chapter-00-overview.md)

## Everything Is an Object

Git is a content-addressable filesystem. Everything is stored as objects identified by SHA-1 hashes. There are four types:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  commit  │────→│   tree   │────→│   blob   │
└──────────┘     └──────────┘     └──────────┘
     │                │
     │                └──→ tree (subdirectory)
     │                       └──→ blob
     ▼
  parent commit
```

## Blob (Binary Large Object)

Stores file content. No filename, no metadata — just the raw content.

```bash
# See what's stored
echo "Hello" | git hash-object --stdin
# ce013625030ba8dba906f756967f9e9ca394464a

# Store it
echo "Hello" | git hash-object --stdin -w

# Read it back
git cat-file -p ce0136
# Hello

git cat-file -t ce0136
# blob
```

Two files with identical content share the same blob object.

## Tree

Stores directory structure — maps filenames to blobs (or other trees for subdirectories):

```bash
git cat-file -p main^{tree}
```

Output:

```
100644 blob ce013625...   hello.txt
100644 blob a1b2c3d4...   readme.md
040000 tree f4e5d6c7...   src
```

Mode values:

- `100644` — normal file
- `100755` — executable
- `040000` — subdirectory (tree)
- `120000` — symlink

## Commit

Points to a tree (snapshot) plus metadata:

```bash
git cat-file -p HEAD
```

Output:

```
tree 8f94139338f9404f26296befa88755fc2598c289
parent a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
author Alice <alice@example.com> 1622505600 +0000
committer Alice <alice@example.com> 1622505600 +0000

Add user authentication
```

A commit contains:

- Pointer to a tree (the snapshot)
- Pointer to parent commit(s) (zero for root, one for normal, two+ for merge)
- Author and committer info
- Commit message

## Tag (Annotated)

A named pointer to a commit with metadata:

```bash
git tag -a v1.0 -m "Release 1.0"
git cat-file -p v1.0
```

Output:

```
object a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
type commit
tag v1.0
tagger Alice <alice@example.com> 1622505600 +0000

Release 1.0
```

Lightweight tags are just refs (no object created).

## SHA-1 Hashing

Every object's ID is the SHA-1 hash of its content prefixed with type and size:

```bash
# How Git computes a blob hash:
echo -n "blob 6\0Hello\n" | sha1sum
# ce013625030ba8dba906f756967f9e9ca394464a
```

Properties:

- Same content always produces the same hash
- Different content produces different hashes (collision-resistant)
- You can verify integrity by recomputing the hash

## How Branches Work

A branch is just a file containing a commit SHA:

```bash
cat .git/refs/heads/main
# a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0

cat .git/HEAD
# ref: refs/heads/main
```

Creating a branch = writing a 41-byte file. Switching branches = updating HEAD. That's why branching is instant.

```
.git/
├── HEAD                    (points to current branch)
├── refs/
│   ├── heads/
│   │   ├── main           (SHA of latest commit on main)
│   │   └── feature        (SHA of latest commit on feature)
│   └── tags/
│       └── v1.0           (SHA of tag object)
└── objects/
    ├── ce/
    │   └── 013625...      (blob)
    ├── 8f/
    │   └── 941393...      (tree)
    └── a1/
        └── b2c3d4...      (commit)
```

## How Merge Works Internally

### Fast-Forward

Just moves the branch pointer forward. No new objects created.

### Three-Way Merge

1. Git finds the merge base (common ancestor)
2. Compares merge base → ours and merge base → theirs
3. If changes don't overlap: auto-merge
4. If changes overlap: conflict (human resolves)
5. Creates a new tree object with merged content
6. Creates a merge commit pointing to that tree with two parents

```bash
# Find merge base
git merge-base main feature
# Shows the common ancestor commit
```

## Packfiles

Git initially stores objects as loose files. Over time (or on push/gc), it packs them:

```bash
# See object storage stats
git count-objects -v
```

Output:

```
count: 43
size: 168
in-pack: 1234
packs: 1
size-pack: 892
```

Packfiles use delta compression — storing only differences between similar objects. This is why Git repos are small despite storing full snapshots.

```bash
# Manually trigger packing
git gc

# Verify pack integrity
git verify-pack -v .git/objects/pack/pack-*.idx | head -20
```

## Garbage Collection

Unreachable objects (orphaned by reset, rebase, etc.) are cleaned up:

```bash
git gc                     # run garbage collection
git gc --aggressive        # more thorough (slower)
git prune                  # remove unreachable objects
git fsck                   # check integrity, find dangling objects
```

Objects are kept for a grace period (default 2 weeks) before pruning. This is why `git reflog` can recover "lost" commits.

```bash
# See dangling objects
git fsck --unreachable

# Expire reflog entries older than 30 days
git reflog expire --expire=30.days --all
git gc
```

## Exercises

1. Create a file, add and commit it. Use `git cat-file -p` to inspect the commit, tree, and blob objects.

2. Create two files with identical content. Verify they share the same blob with `git ls-tree HEAD`.

3. Inspect `.git/refs/heads/` to see branch files. Create a branch manually by writing a SHA to a new file there.

4. Run `git count-objects -v` before and after `git gc` to see packing in action.

5. Use `git fsck` to find dangling objects after a `git reset --hard`.
