# Chapter 1: Finding a Package — Linear Search

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Binary Search →](chapter-02-binary-search.md)

---

## The Problem

A customer calls: "Where's my package? Tracking number RM-58291."

The support agent types the tracking number into the internal tool. The tool searches the database. 15 seconds pass. The customer is still on hold.

You check the code:

```python
def find_package(packages, tracking_number):
    for package in packages:
        if package["tracking"] == tracking_number:
            return package
    return None
```

One loop. Check every package. Return when found. This is **linear search** — the simplest search algorithm that exists.

With 1,000 packages, it takes 0.001 seconds. Fine.
With 100,000 packages (RouteMaster's current volume), it takes 0.15 seconds. Noticeable.
With 500,000 packages (next quarter's projection), it'll take 0.8 seconds. Unacceptable for a support agent on a live call.

Priya: "Why does package lookup get slower every month?"

Because linear search checks every element until it finds the target. More elements = more checks = more time. That's O(n) — time grows linearly with input size.

## How Linear Search Works

```python
def linear_search(items, target):
    """
    Check each element one by one.
    Returns the index if found, -1 if not.
    """
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1
```

That's it. Start at the beginning. Check each element. Stop when you find it or reach the end.

### Step-by-Step

Searching for `42` in `[17, 3, 42, 8, 91, 55]`:

```
Step 1: items[0] = 17  → not 42, continue
Step 2: items[1] = 3   → not 42, continue
Step 3: items[2] = 42  → FOUND! Return index 2
```

3 comparisons. Lucky — it was near the front.

Searching for `99` in `[17, 3, 42, 8, 91, 55]`:

```
Step 1: items[0] = 17  → not 99, continue
Step 2: items[1] = 3   → not 99, continue
Step 3: items[2] = 42  → not 99, continue
Step 4: items[3] = 8   → not 99, continue
Step 5: items[4] = 91  → not 99, continue
Step 6: items[5] = 55  → not 99, continue
         → END OF LIST. Not found. Return -1
```

6 comparisons. Checked everything. Worst case.

## Complexity Analysis

| Case | Comparisons | When |
|---|---|---|
| Best case | 1 | Target is the first element |
| Average case | n/2 | Target is somewhere in the middle |
| Worst case | n | Target is last or not present |

Big-O uses worst case: **O(n)**.

If you have 100,000 packages and the one you're looking for is last (or doesn't exist), you make 100,000 comparisons.

## Benchmarking: Seeing O(n) in Action

```python
import time
import random

def generate_packages(n):
    """Generate n packages with random tracking numbers."""
    return [{"tracking": f"RM-{i:06d}", "status": "in_transit", "address": f"{i} Main St"}
            for i in range(n)]

def benchmark_linear_search(sizes):
    """Measure search time at different input sizes."""
    for n in sizes:
        packages = generate_packages(n)
        # Worst case: search for something that doesn't exist
        target = "RM-999999"

        start = time.time()
        for _ in range(100):  # Run 100 searches for stable timing
            find_package(packages, target)
        elapsed = (time.time() - start) / 100

        print(f"n={n:>10,} → {elapsed*1000:.3f}ms per search")

benchmark_linear_search([1_000, 10_000, 50_000, 100_000, 500_000])
```

Output:
```
n=     1,000 → 0.089ms per search
n=    10,000 → 0.891ms per search
n=    50,000 → 4.456ms per search
n=   100,000 → 8.912ms per search
n=   500,000 → 44.560ms per search
```

10x more packages → 10x slower. That's linear growth. The graph is a straight line.

## RouteMaster's Package Lookup

The real implementation with the full package structure:

```python
class Package:
    def __init__(self, tracking, sender, recipient, weight, priority, status):
        self.tracking = tracking
        self.sender = sender
        self.recipient = recipient
        self.weight = weight
        self.priority = priority
        self.status = status

    def __repr__(self):
        return f"Package({self.tracking}, {self.status})"


class PackageRegistry:
    def __init__(self):
        self.packages = []

    def add(self, package):
        self.packages.append(package)

    def find_by_tracking(self, tracking_number):
        """Linear search — O(n)."""
        for package in self.packages:
            if package.tracking == tracking_number:
                return package
        return None

    def find_by_status(self, status):
        """Find ALL packages with a given status — must check everything."""
        results = []
        for package in self.packages:
            if package.status == status:
                results.append(package)
        return results

    def find_by_recipient(self, recipient_name):
        """Find all packages for a recipient."""
        results = []
        for package in self.packages:
            if package.recipient == recipient_name:
                results.append(package)
        return results
```

Three different searches. All linear. All O(n). All get slower as RouteMaster grows.

## When Linear Search Is Fine

Linear search isn't always bad. It's the right choice when:

### 1. Small input (n < 100)

```python
# Searching 20 delivery zones — linear search is fine
zones = ["North", "South", "East", "West", "Central", ...]
if "Central" in zones:  # Python's `in` is linear search
    assign_driver()
```

For 20 elements, the overhead of a fancier algorithm costs more than just scanning.

### 2. Unsorted data with no structure

If the data has no order and you can't preprocess it, linear search is your only option.

### 3. You only search once

If you search a list once and throw it away, sorting it first (O(n log n)) is more expensive than just scanning (O(n)).

### 4. You need ALL matches

`find_by_status("delivered")` must check every package — there's no shortcut to finding all matches in an unsorted list.

## When Linear Search Breaks

### The Support Tool

100,000 packages. Support agents make 500 lookups per hour. Each lookup: 9ms.

Total time spent waiting: 500 × 9ms = 4.5 seconds per hour. Annoying but survivable.

At 500,000 packages (Q4 projection): 500 × 45ms = 22.5 seconds per hour. Still tolerable.

### The Dispatch System

The dispatch system runs `find_by_tracking` inside a loop — for every package being dispatched:

```python
def assign_routes(dispatch_list, all_packages):
    """Assign packages to drivers. Called every morning."""
    for tracking_number in dispatch_list:
        package = find_package(all_packages, tracking_number)  # O(n) per call
        if package:
            assign_to_nearest_driver(package)
```

50,000 packages dispatched. Each lookup scans 100,000 records. That's 50,000 × 100,000 = 5 billion comparisons. **O(n × m)** where n is dispatch list size and m is total packages.

This is why the morning route planning takes 45 minutes.

## Optimization: Early Termination

If you know there's exactly one match (like a unique tracking number), return immediately when found:

```python
def find_package(packages, tracking_number):
    for package in packages:
        if package.tracking == tracking_number:
            return package  # Stop here — don't check the rest
    return None
```

This doesn't change the worst case (O(n) if it's last or missing), but improves the average case. If packages are uniformly distributed, you'll check n/2 elements on average instead of n.

## Optimization: Sentinel Search

A micro-optimization that eliminates the bounds check:

```python
def sentinel_search(items, target):
    """
    Place the target at the end so we always find it.
    Eliminates the 'i < len(items)' check in the loop.
    """
    n = len(items)
    if n == 0:
        return -1

    last = items[n - 1]
    items[n - 1] = target  # Place sentinel

    i = 0
    while items[i] != target:
        i += 1

    items[n - 1] = last  # Restore original

    if i < n - 1 or last == target:
        return i
    return -1
```

Still O(n), but ~30% faster in practice because the inner loop has one comparison instead of two. Rarely worth the complexity in Python, but matters in C/assembly for very hot loops.

## Optimization: Move-to-Front

If some packages are looked up more often (hot packages in transit vs delivered ones):

```python
def find_with_move_to_front(packages, tracking_number):
    """
    Move found items to the front.
    Frequently accessed items migrate to the beginning over time.
    """
    for i, package in enumerate(packages):
        if package.tracking == tracking_number:
            if i > 0:
                # Move to front
                packages.insert(0, packages.pop(i))
            return packages[0]
    return None
```

Hot packages get found in O(1) after a few accesses. Cold packages sink to the back. Self-organizing list.

## The Verdict

Linear search works for RouteMaster's support tool (100K packages, occasional lookups). It does NOT work for the dispatch system (50K lookups × 100K packages).

Priya looks at your benchmark results. "So what's faster?"

You: "If the packages were sorted by tracking number, I could use binary search. Instead of checking all 100,000, I'd check about 17."

Priya: "17?"

You: "log₂(100,000) ≈ 17."

Priya: "Sort them. Now."

## What You Learned

- **Linear search** — check every element, O(n)
- **Best/average/worst case** — 1, n/2, n comparisons
- **When it's fine** — small inputs, unsorted data, single searches, finding all matches
- **When it breaks** — large inputs with repeated lookups
- **Optimizations** — early termination, sentinel, move-to-front
- **The real cost** — linear search inside a loop becomes O(n × m)

The support tool is acceptable. The dispatch system is not. You need something fundamentally faster — not a constant-factor improvement, but a different complexity class entirely.

That's Chapter 2.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Binary Search →](chapter-02-binary-search.md)
