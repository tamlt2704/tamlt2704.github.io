# Chapter 3: Algorithm Implementations

[prev: Data Structures](chapter-02-data-structures.md) | [next: Math](chapter-04-math.md)

## Binary Search

### Arrays.binarySearch — O(log n)

```java
int[] arr = {1, 3, 5, 7, 9};
int idx = Arrays.binarySearch(arr, 5);  // returns 2
int idx2 = Arrays.binarySearch(arr, 4); // returns -(insertion point) - 1 = -3
```

To emulate C++ `lower_bound` (first element >= target):

```java
int pos = Arrays.binarySearch(arr, target);
if (pos < 0) pos = -(pos + 1);
```

### Custom Binary Search

```java
// Find smallest x in [lo, hi] where check(x) is true
static int lowerBound(int lo, int hi) {
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (check(mid)) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}

// Find largest x in [lo, hi] where check(x) is true
static int upperBound(int lo, int hi) {
    while (lo < hi) {
        int mid = lo + (hi - lo + 1) / 2;
        if (check(mid)) lo = mid;
        else hi = mid - 1;
    }
    return lo;
}

// Binary search on doubles
static double bsDouble(double lo, double hi) {
    for (int iter = 0; iter < 100; iter++) {
        double mid = (lo + hi) / 2;
        if (check(mid)) hi = mid;
        else lo = mid;
    }
    return lo;
}
```

## Sorting

### Primitive Arrays — O(n log n)

`Arrays.sort(int[])` uses **dual-pivot quicksort**. Fast in practice but O(n^2) worst case.

```java
int[] arr = {5, 2, 8, 1, 9};
Arrays.sort(arr);
Arrays.sort(arr, 1, 4); // sort indices [1, 4)
```

**Codeforces anti-hack:** Adversarial inputs trigger O(n^2). Shuffle first:

```java
static void shuffle(int[] arr) {
    Random rng = new Random();
    for (int i = arr.length - 1; i > 0; i--) {
        int j = rng.nextInt(i + 1);
        int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    }
}
shuffle(arr);
Arrays.sort(arr);
```

### Object Arrays — O(n log n) guaranteed

`Arrays.sort(Object[])` uses **TimSort** (stable, O(n log n) worst case).

```java
int[][] intervals = {{1,3}, {2,5}, {0,7}};
Arrays.sort(intervals, (a, b) -> a[0] - b[0]);

// Safe comparator (avoids overflow)
Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
```

**Warning:** `(a, b) -> a - b` overflows if a and b have different signs. Use `Integer.compare` for safety.

## Two Pointers — O(n)

```java
// Two sum on sorted array
static int[] twoSum(int[] arr, int target) {
    int lo = 0, hi = arr.length - 1;
    while (lo < hi) {
        int sum = arr[lo] + arr[hi];
        if (sum == target) return new int[]{lo, hi};
        else if (sum < target) lo++;
        else hi--;
    }
    return new int[]{-1, -1};
}
```

## Sliding Window — O(n)

```java
// Smallest subarray with sum >= target
static int minLenSubarray(int[] arr, int target) {
    int left = 0, ans = Integer.MAX_VALUE;
    long sum = 0;
    for (int right = 0; right < arr.length; right++) {
        sum += arr[right];
        while (sum >= target) {
            ans = Math.min(ans, right - left + 1);
            sum -= arr[left++];
        }
    }
    return ans == Integer.MAX_VALUE ? -1 : ans;
}
```

### Sliding Window Maximum — O(n) with Monotonic Deque

```java
static int[] maxSlidingWindow(int[] arr, int k) {
    int n = arr.length;
    int[] res = new int[n - k + 1];
    Deque<Integer> dq = new ArrayDeque<>();
    for (int i = 0; i < n; i++) {
        while (!dq.isEmpty() && dq.peekFirst() <= i - k) dq.pollFirst();
        while (!dq.isEmpty() && arr[dq.peekLast()] <= arr[i]) dq.pollLast();
        dq.offerLast(i);
        if (i >= k - 1) res[i - k + 1] = arr[dq.peekFirst()];
    }
    return res;
}
```

## Prefix Sums — O(1) Range Queries After O(n) Build

```java
// 1D prefix sum
long[] pre = new long[n + 1];
for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + arr[i];
// Sum of arr[l..r] = pre[r+1] - pre[l]

// 2D prefix sum
int[][] pre = new int[n + 1][m + 1];
for (int i = 0; i < n; i++)
    for (int j = 0; j < m; j++)
        pre[i+1][j+1] = pre[i][j+1] + pre[i+1][j] - pre[i][j] + grid[i][j];
```

## Relevant Problems

- **LeetCode 34** — Find First and Last Position (binary search)
- **Codeforces 1324D** — Pair of Topics (two pointers + sort)
- **LeetCode 239** — Sliding Window Maximum (monotonic deque)
- **LeetCode 209** — Minimum Size Subarray Sum (variable sliding window)
- **AtCoder ABC 172D** — Prefix sums with arithmetic
