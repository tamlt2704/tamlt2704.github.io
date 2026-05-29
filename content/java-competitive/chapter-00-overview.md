# Java for Competitive Programming: Performance Guide

[next: Fast I/O](chapter-01-fast-io.md)

## Why This Guide

Java is a viable language for competitive programming — used successfully in ICPC, Codeforces, LeetCode, and AtCoder. But to compete with C++ solutions, you need to know the performance tricks that eliminate Java's constant-factor overhead.

This guide focuses on **speed**: both algorithmic complexity and the constant factors that make the difference between AC and TLE.

## Why Java?

**Advantages:**

- Strong standard library (Collections, BigInteger, regex)
- No segfaults or undefined behavior
- BigInteger for arbitrary precision (no Python needed)
- Garbage collection means no memory leaks
- Consistent behavior across platforms
- 64-bit long is native (no `long long` needed)

**Challenges:**

- 2-3x slower than C++ in raw speed (JVM overhead, bounds checking)
- Higher memory usage (object headers, boxing)
- Slower I/O with default Scanner
- Auto-boxing traps (Integer vs int)
- Codeforces gives Java 2x-3x time limit, but not always enough

## Chapters

1. [Fast I/O](chapter-01-fast-io.md) — BufferedReader, StringTokenizer, custom FastReader
2. [Data Structures](chapter-02-data-structures.md) — Choosing the right collection for speed
3. [Algorithms](chapter-03-algorithms.md) — Binary search, sorting, two pointers
4. [Math](chapter-04-math.md) — Modular arithmetic, primes, combinatorics
5. [Graphs](chapter-05-graphs.md) — BFS, Dijkstra, Union-Find, segment trees
6. [Strings](chapter-06-strings.md) — StringBuilder, hashing, KMP, Trie
7. [JVM Optimization](chapter-07-optimization.md) — Avoid boxing, bit tricks, memory
8. [Contest Templates](chapter-08-templates.md) — Copy-paste ready code

## Quick Comparison: Java vs C++

| Aspect     | Java                                      | C++                       |
| ---------- | ----------------------------------------- | ------------------------- |
| Speed      | ~2-3x slower                              | Baseline                  |
| Memory     | ~2-4x more                                | Baseline                  |
| I/O        | Slow by default, fast with BufferedReader | Fast with scanf/cin+sync  |
| BigInteger | Built-in                                  | Need \_\_int128 or custom |
| Overflow   | No UB, predictable wrap                   | UB on signed overflow     |
| Arrays     | Bounds-checked                            | No bounds check           |
| Time limit | Often 2x-3x on CF                         | Baseline                  |

## The Golden Rules

1. **Always use fast I/O** — Scanner alone can cause TLE
2. **Use primitive arrays** — `int[]` not `Integer[]`
3. **Avoid object creation in loops** — GC pressure kills performance
4. **Use ArrayDeque** — Never Stack or LinkedList
5. **Pre-allocate everything** — Know your bounds, allocate once
