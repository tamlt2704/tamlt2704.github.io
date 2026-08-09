# Chapter 22: Algorithms, LeetCode Patterns, and System Design

## What you'll learn

- Core data structures and when to use them
- Essential algorithms: sorting, searching, recursion, dynamic programming
- Big-O complexity analysis (how to reason about performance)
- LeetCode problem patterns (not memorizing solutions — recognizing shapes)
- System design fundamentals (scaling, databases, caching, message queues)
- System design interview framework

---

## PART 1: Core Data Structures & Algorithms

## 22.1 Data structures — choosing the right container

| Structure | Access | Search | Insert | Delete | Use when |
|-----------|--------|--------|--------|--------|----------|
| **Array** | O(1) | O(n) | O(n) | O(n) | Fixed-size, index access, iteration |
| **LinkedList** | O(n) | O(n) | O(1)* | O(1)* | Frequent insert/delete at known position |
| **HashMap** | — | O(1) avg | O(1) avg | O(1) avg | Key→value lookup, counting, deduplication |
| **HashSet** | — | O(1) avg | O(1) avg | O(1) avg | Membership testing, uniqueness |
| **Stack** | O(1) top | O(n) | O(1) push | O(1) pop | LIFO: undo, parsing, DFS |
| **Queue** | O(1) front | O(n) | O(1) enqueue | O(1) dequeue | FIFO: BFS, scheduling, buffering |
| **Heap/PriorityQueue** | O(1) min/max | O(n) | O(log n) | O(log n) | Top-K, shortest path, scheduling |
| **Binary Search Tree** | O(log n)* | O(log n)* | O(log n)* | O(log n)* | Sorted data, range queries |
| **Trie** | — | O(m) | O(m) | O(m) | Prefix search, autocomplete (m=word length) |
| **Graph** (adj list) | — | O(V+E) | O(1) | O(E) | Relationships, networks, paths |

*Under ideal conditions (balanced tree, known position)

## 22.2 Big-O — how to think about performance

Big-O describes how runtime grows as input size (n) increases:

```
O(1)       → Constant    (HashMap lookup)         ████
O(log n)   → Logarithmic (Binary search)          ████████
O(n)       → Linear      (Array scan)             ████████████████
O(n log n) → Linearithmic (Merge sort)            ████████████████████████
O(n²)      → Quadratic   (Nested loops)           ████████████████████████████████████████
O(2ⁿ)      → Exponential (Brute-force subsets)    💀 DON'T
```

**Practical limits (1 second):**
- O(n): n ≤ 10⁸ (100 million)
- O(n log n): n ≤ 10⁶ (1 million)
- O(n²): n ≤ 10⁴ (10 thousand)
- O(2ⁿ): n ≤ 20

**How to calculate Big-O from code:**

```java
// O(n) — single loop
for (int i = 0; i < n; i++) { ... }

// O(n²) — nested loops (both depend on n)
for (int i = 0; i < n; i++)
  for (int j = 0; j < n; j++) { ... }

// O(n log n) — halving something n times
for (int i = 0; i < n; i++)      // O(n)
  binarySearch(arr, target);      // O(log n) each

// O(log n) — halving the search space
while (left <= right) {
  mid = (left + right) / 2;
  // go left or right
}
```

## 22.3 Sorting algorithms

| Algorithm | Time (avg) | Time (worst) | Space | Stable? | Key idea |
|-----------|-----------|-------------|-------|---------|----------|
| Bubble Sort | O(n²) | O(n²) | O(1) | Yes | Swap adjacent if wrong order |
| Selection Sort | O(n²) | O(n²) | O(1) | No | Find min, put it at front |
| Insertion Sort | O(n²) | O(n²) | O(1) | Yes | Insert each element into sorted portion |
| Merge Sort | O(n log n) | O(n log n) | O(n) | Yes | Divide, sort halves, merge |
| Quick Sort | O(n log n) | O(n²) | O(log n) | No | Partition around pivot |
| Heap Sort | O(n log n) | O(n log n) | O(1) | No | Build heap, extract max repeatedly |

**When to use which:**
- **Nearly sorted data** → Insertion Sort (O(n) best case)
- **General purpose** → Merge Sort (guaranteed O(n log n), stable)
- **In-place needed** → Quick Sort (O(log n) space, fastest in practice)
- **Top-K elements** → Heap (don't fully sort — just extract K)

## 22.4 Searching

**Linear Search** — O(n): check every element

```java
for (int i = 0; i < arr.length; i++)
  if (arr[i] == target) return i;
return -1;
```

**Binary Search** — O(log n): requires sorted array, halves search space each step

```java
int binarySearch(int[] arr, int target) {
  int left = 0, right = arr.length - 1;
  while (left <= right) {
    int mid = left + (right - left) / 2;  // avoid overflow
    if (arr[mid] == target) return mid;
    else if (arr[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return -1;  // not found
}
```

> **Binary search applies beyond arrays:** Any monotonic function (sorted property). "What's the minimum capacity to ship packages in D days?" — binary search on the answer.

## 22.5 Recursion and backtracking

**Recursion** = function calls itself with a smaller input until a base case.

```java
// Factorial: n! = n × (n-1)!
int factorial(int n) {
  if (n <= 1) return 1;          // base case
  return n * factorial(n - 1);   // recursive case
}
```

**The recursion template:**
1. Define the base case (when to stop)
2. Define the recursive case (reduce problem, call yourself)
3. Trust the recursion (don't trace every call — assume it works for smaller inputs)

**Backtracking** = try a choice, recurse, undo if it doesn't work:

```java
// Generate all permutations
void permute(int[] nums, List<Integer> current, boolean[] used, List<List<Integer>> results) {
  if (current.size() == nums.length) {
    results.add(new ArrayList<>(current));  // base case: found a permutation
    return;
  }
  for (int i = 0; i < nums.length; i++) {
    if (used[i]) continue;
    used[i] = true;                   // choose
    current.add(nums[i]);
    permute(nums, current, used, results);  // explore
    current.remove(current.size() - 1);     // un-choose (backtrack)
    used[i] = false;
  }
}
```

## 22.6 Dynamic programming (DP)

DP = recursion + memoization. It applies when:
1. **Overlapping subproblems** — same subproblem is solved multiple times
2. **Optimal substructure** — optimal solution uses optimal sub-solutions

**Two approaches:**

```java
// Top-down (memoization) — recursive + cache
int fib(int n, int[] memo) {
  if (n <= 1) return n;
  if (memo[n] != 0) return memo[n];  // already computed
  memo[n] = fib(n - 1, memo) + fib(n - 2, memo);
  return memo[n];
}

// Bottom-up (tabulation) — iterative, fill table from base cases
int fib(int n) {
  int[] dp = new int[n + 1];
  dp[0] = 0; dp[1] = 1;
  for (int i = 2; i <= n; i++)
    dp[i] = dp[i - 1] + dp[i - 2];
  return dp[n];
}
```

**DP recipe:**
1. Define state: what changes between subproblems? (`dp[i]` = answer for input size i)
2. Define transition: how to compute `dp[i]` from smaller subproblems?
3. Define base case: what are the trivial answers?
4. Determine order: fill table so dependencies are ready

## 22.7 Graph algorithms

**Representations:**

```java
// Adjacency list (most common — sparse graphs)
Map<String, List<String>> graph = new HashMap<>();
graph.put("A", List.of("B", "C"));
graph.put("B", List.of("A", "D"));

// Adjacency matrix (dense graphs, fast edge lookup)
int[][] matrix = new int[n][n]; // matrix[i][j] = 1 if edge exists
```

**BFS** — explore level by level (shortest path in unweighted graphs):

```java
void bfs(Map<String, List<String>> graph, String start) {
  Queue<String> queue = new LinkedList<>();
  Set<String> visited = new HashSet<>();
  queue.add(start);
  visited.add(start);

  while (!queue.isEmpty()) {
    String node = queue.poll();
    process(node);
    for (String neighbor : graph.get(node)) {
      if (!visited.contains(neighbor)) {
        visited.add(neighbor);
        queue.add(neighbor);
      }
    }
  }
}
```

**DFS** — explore as deep as possible (cycle detection, topological sort):

```java
void dfs(Map<String, List<String>> graph, String node, Set<String> visited) {
  visited.add(node);
  process(node);
  for (String neighbor : graph.get(node)) {
    if (!visited.contains(neighbor)) {
      dfs(graph, neighbor, visited);
    }
  }
}
```

| Algorithm | Purpose | Complexity |
|-----------|---------|-----------|
| BFS | Shortest path (unweighted) | O(V + E) |
| DFS | Traverse all, detect cycles | O(V + E) |
| Dijkstra | Shortest path (weighted, non-negative) | O((V+E) log V) |
| Topological Sort | Dependency ordering (DAG) | O(V + E) |
| Union-Find | Connected components, cycle detection | O(α(n)) ≈ O(1) |



---

## PART 2: LeetCode Patterns

The key to LeetCode is **pattern recognition** — not memorizing solutions. There are ~15 patterns that cover 90% of problems. Learn to recognize which pattern a problem uses.

## 22.8 Pattern 1: Two Pointers

**Recognise when:** Sorted array/string, find pair/triplet, remove duplicates, palindrome check.

```java
// Find two numbers that sum to target (sorted array)
int[] twoSum(int[] arr, int target) {
  int left = 0, right = arr.length - 1;
  while (left < right) {
    int sum = arr[left] + arr[right];
    if (sum == target) return new int[]{left, right};
    else if (sum < target) left++;
    else right--;
  }
  return new int[]{-1, -1};
}
```

**Problems:** Two Sum II, 3Sum, Container With Most Water, Trapping Rain Water, Remove Duplicates, Valid Palindrome

## 22.9 Pattern 2: Sliding Window

**Recognise when:** Subarray/substring of size K, "longest/shortest" substring with a condition.

```java
// Longest substring without repeating characters
int lengthOfLongestSubstring(String s) {
  Set<Character> window = new HashSet<>();
  int left = 0, maxLen = 0;

  for (int right = 0; right < s.length(); right++) {
    while (window.contains(s.charAt(right))) {
      window.remove(s.charAt(left));
      left++;
    }
    window.add(s.charAt(right));
    maxLen = Math.max(maxLen, right - left + 1);
  }
  return maxLen;
}
```

**Template:**
1. Expand right pointer to include new element
2. Shrink left pointer until window is valid
3. Track the best answer at each step

**Problems:** Maximum Subarray Sum of Size K, Longest Substring Without Repeating, Minimum Window Substring, Fruits Into Baskets

## 22.10 Pattern 3: Binary Search (beyond arrays)

**Recognise when:** Sorted array, "minimum/maximum that satisfies condition", monotonic function.

```java
// Find minimum capacity to ship packages in D days
int shipWithinDays(int[] weights, int days) {
  int left = Arrays.stream(weights).max().getAsInt(); // min possible
  int right = Arrays.stream(weights).sum();            // max possible

  while (left < right) {
    int mid = left + (right - left) / 2;
    if (canShipInDays(weights, mid, days)) {
      right = mid;         // try smaller capacity
    } else {
      left = mid + 1;      // need more capacity
    }
  }
  return left;
}

boolean canShipInDays(int[] weights, int capacity, int days) {
  int currentLoad = 0, daysNeeded = 1;
  for (int w : weights) {
    if (currentLoad + w > capacity) {
      daysNeeded++;
      currentLoad = 0;
    }
    currentLoad += w;
  }
  return daysNeeded <= days;
}
```

**Key insight:** If you can write a function `isValid(x)` that is monotonic (false...false...true...true), you can binary search on the answer.

**Problems:** Search in Rotated Array, Find Peak Element, Koko Eating Bananas, Split Array Largest Sum

## 22.11 Pattern 4: HashMap / Counting

**Recognise when:** Frequency counting, "have we seen this before?", anagrams, two sum (unsorted).

```java
// Two Sum (unsorted) — O(n)
int[] twoSum(int[] nums, int target) {
  Map<Integer, Integer> seen = new HashMap<>();  // value → index
  for (int i = 0; i < nums.length; i++) {
    int complement = target - nums[i];
    if (seen.containsKey(complement)) {
      return new int[]{seen.get(complement), i};
    }
    seen.put(nums[i], i);
  }
  return new int[]{-1, -1};
}
```

**Problems:** Two Sum, Group Anagrams, Top K Frequent Elements, Longest Consecutive Sequence, Subarray Sum Equals K

## 22.12 Pattern 5: Stack

**Recognise when:** Matching brackets, next greater/smaller element, monotonic stack, calculator.

```java
// Next Greater Element — monotonic decreasing stack
int[] nextGreaterElement(int[] nums) {
  int[] result = new int[nums.length];
  Arrays.fill(result, -1);
  Deque<Integer> stack = new ArrayDeque<>();  // stores indices

  for (int i = 0; i < nums.length; i++) {
    while (!stack.isEmpty() && nums[i] > nums[stack.peek()]) {
      result[stack.pop()] = nums[i];
    }
    stack.push(i);
  }
  return result;
}
```

**Problems:** Valid Parentheses, Daily Temperatures, Largest Rectangle in Histogram, Min Stack, Evaluate RPN

## 22.13 Pattern 6: BFS / DFS on Graphs

**Recognise when:** Grid traversal, "number of islands", shortest path, connected components, level-order.

```java
// Number of Islands — DFS flood fill
int numIslands(char[][] grid) {
  int count = 0;
  for (int r = 0; r < grid.length; r++) {
    for (int c = 0; c < grid[0].length; c++) {
      if (grid[r][c] == '1') {
        count++;
        dfs(grid, r, c);  // mark entire island as visited
      }
    }
  }
  return count;
}

void dfs(char[][] grid, int r, int c) {
  if (r < 0 || r >= grid.length || c < 0 || c >= grid[0].length) return;
  if (grid[r][c] != '1') return;
  grid[r][c] = '0';  // mark visited
  dfs(grid, r + 1, c);
  dfs(grid, r - 1, c);
  dfs(grid, r, c + 1);
  dfs(grid, r, c - 1);
}
```

**BFS for shortest path:**
```java
// Shortest path in grid (BFS guarantees shortest in unweighted)
int shortestPath(int[][] grid) {
  Queue<int[]> queue = new LinkedList<>();
  queue.add(new int[]{0, 0, 0}); // row, col, distance
  boolean[][] visited = new boolean[m][n];
  visited[0][0] = true;

  int[][] dirs = {{0,1},{0,-1},{1,0},{-1,0}};
  while (!queue.isEmpty()) {
    int[] curr = queue.poll();
    if (curr[0] == m-1 && curr[1] == n-1) return curr[2];
    for (int[] d : dirs) {
      int nr = curr[0]+d[0], nc = curr[1]+d[1];
      if (nr >= 0 && nr < m && nc >= 0 && nc < n && !visited[nr][nc] && grid[nr][nc] == 0) {
        visited[nr][nc] = true;
        queue.add(new int[]{nr, nc, curr[2]+1});
      }
    }
  }
  return -1;
}
```

**Problems:** Number of Islands, Rotting Oranges, Word Ladder, Clone Graph, Course Schedule

## 22.14 Pattern 7: Tree Traversal

**Recognise when:** Binary tree problems, "maximum depth", "path sum", "serialize tree".

```java
// Maximum depth — recursive DFS
int maxDepth(TreeNode root) {
  if (root == null) return 0;
  return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}

// Level-order traversal — BFS
List<List<Integer>> levelOrder(TreeNode root) {
  List<List<Integer>> result = new ArrayList<>();
  if (root == null) return result;
  Queue<TreeNode> queue = new LinkedList<>();
  queue.add(root);

  while (!queue.isEmpty()) {
    int size = queue.size();
    List<Integer> level = new ArrayList<>();
    for (int i = 0; i < size; i++) {
      TreeNode node = queue.poll();
      level.add(node.val);
      if (node.left != null) queue.add(node.left);
      if (node.right != null) queue.add(node.right);
    }
    result.add(level);
  }
  return result;
}
```

**Problems:** Max Depth, Same Tree, Invert Tree, Path Sum, Lowest Common Ancestor, Serialize/Deserialize

## 22.15 Pattern 8: Dynamic Programming

**Recognise when:** "Count ways", "minimum cost", "can you reach?", overlapping subproblems.

```java
// Climbing stairs: how many ways to reach step n (take 1 or 2 steps)?
int climbStairs(int n) {
  if (n <= 2) return n;
  int prev2 = 1, prev1 = 2;
  for (int i = 3; i <= n; i++) {
    int curr = prev1 + prev2;
    prev2 = prev1;
    prev1 = curr;
  }
  return prev1;
}

// 0/1 Knapsack
int knapsack(int[] weights, int[] values, int capacity) {
  int n = weights.length;
  int[][] dp = new int[n + 1][capacity + 1];

  for (int i = 1; i <= n; i++) {
    for (int w = 0; w <= capacity; w++) {
      dp[i][w] = dp[i-1][w]; // don't take item i
      if (weights[i-1] <= w) {
        dp[i][w] = Math.max(dp[i][w], dp[i-1][w - weights[i-1]] + values[i-1]);
      }
    }
  }
  return dp[n][capacity];
}
```

**DP categories:**
- 1D: Climbing Stairs, House Robber, Coin Change
- 2D: Edit Distance, Longest Common Subsequence, Unique Paths
- Knapsack: Subset Sum, Partition Equal Subset, Target Sum
- Interval: Burst Balloons, Matrix Chain Multiplication

## 22.16 Pattern 9: Heap / Priority Queue

**Recognise when:** "Top K", "K-th largest", merge K sorted things, scheduling.

```java
// Kth Largest Element — min-heap of size K
int findKthLargest(int[] nums, int k) {
  PriorityQueue<Integer> minHeap = new PriorityQueue<>();
  for (int num : nums) {
    minHeap.add(num);
    if (minHeap.size() > k) minHeap.poll(); // remove smallest
  }
  return minHeap.peek(); // kth largest is the smallest in the heap
}
```

**Problems:** Kth Largest Element, Merge K Sorted Lists, Top K Frequent, Meeting Rooms II, Find Median

## 22.17 Pattern 10: Intervals

**Recognise when:** Merge intervals, insert interval, "minimum meeting rooms".

```java
// Merge overlapping intervals
int[][] merge(int[][] intervals) {
  Arrays.sort(intervals, (a, b) -> a[0] - b[0]); // sort by start
  List<int[]> merged = new ArrayList<>();
  merged.add(intervals[0]);

  for (int i = 1; i < intervals.length; i++) {
    int[] last = merged.get(merged.size() - 1);
    if (intervals[i][0] <= last[1]) {
      last[1] = Math.max(last[1], intervals[i][1]); // merge
    } else {
      merged.add(intervals[i]); // no overlap
    }
  }
  return merged.toArray(new int[0][]);
}
```

**Problems:** Merge Intervals, Insert Interval, Non-Overlapping Intervals, Meeting Rooms

## 22.18 More patterns (quick reference)

| Pattern | Key technique | Example problem |
|---------|---------------|-----------------|
| Prefix Sum | Precompute cumulative sums | Subarray Sum Equals K |
| Trie | Prefix tree for strings | Implement Trie, Word Search II |
| Union-Find | Disjoint sets, connected components | Number of Provinces, Redundant Connection |
| Topological Sort | Dependency ordering | Course Schedule, Alien Dictionary |
| Bit Manipulation | XOR, AND, bit counting | Single Number, Counting Bits |
| Greedy | Local optimal → global optimal | Jump Game, Task Scheduler |

## 22.19 LeetCode study plan

**Week 1-2: Easy (build confidence)**
- Two Sum, Valid Parentheses, Merge Two Sorted Lists
- Best Time to Buy and Sell Stock, Valid Palindrome
- Max Depth of Binary Tree, Climbing Stairs

**Week 3-4: Medium (core patterns)**
- 3Sum, Longest Substring Without Repeating
- Binary Tree Level Order, Number of Islands
- Coin Change, Product of Array Except Self

**Week 5-6: Medium-Hard (advanced patterns)**
- Word Break, Course Schedule, Merge Intervals
- Top K Frequent Elements, LRU Cache
- Lowest Common Ancestor, Serialize Binary Tree

**Week 7-8: Hard (stretch goals)**
- Trapping Rain Water, Sliding Window Maximum
- Word Ladder, Edit Distance
- Median of Two Sorted Arrays, Merge K Sorted Lists



---

## PART 3: System Design

## 22.20 Why system design matters

Algorithms solve problems at the code level. System design solves problems at the architecture level:
- How do you serve 10 million users?
- Where does data live?
- What happens when a server crashes?
- How do you handle 100,000 requests per second?

## 22.21 The system design interview framework

Always follow this structure (45 minutes):

```
[5 min]  1. CLARIFY REQUIREMENTS
              ├─ Functional: What does it DO?
              ├─ Non-functional: Scale, latency, availability
              └─ Constraints: Budget, team size, timeline

[5 min]  2. ESTIMATE SCALE
              ├─ Users (DAU, MAU)
              ├─ Read/Write ratio
              ├─ Data volume
              └─ Bandwidth / QPS

[10 min] 3. HIGH-LEVEL DESIGN
              ├─ Core components (boxes + arrows)
              ├─ API design (endpoints)
              └─ Data flow

[15 min] 4. DETAILED DESIGN
              ├─ Database schema + choice
              ├─ Caching strategy
              ├─ Scaling approach
              └─ Key algorithms/data structures

[5 min]  5. ADDRESS BOTTLENECKS
              ├─ Single points of failure
              ├─ How to scale
              └─ Monitoring/alerting

[5 min]  6. WRAP-UP
              └─ Tradeoffs made, future improvements
```

## 22.22 Core building blocks

### Load Balancer

Distributes requests across multiple servers:

```
Clients → [Load Balancer] → Server 1
                           → Server 2
                           → Server 3
```

Algorithms: Round-robin, Least connections, IP hash, Weighted

### Web Servers (Horizontal Scaling)

```
Stateless servers (can add/remove anytime):
- All state in database/cache, not in server memory
- Any server can handle any request
- Scale by adding more servers behind load balancer
```

### Database

| Type | Best for | Examples |
|------|----------|---------|
| Relational (SQL) | Structured data, joins, ACID transactions | PostgreSQL, MySQL |
| Document (NoSQL) | Flexible schema, hierarchical data | MongoDB, DynamoDB |
| Key-Value | Simple lookups, caching, sessions | Redis, Memcached |
| Wide-Column | Time-series, analytics, massive scale | Cassandra, HBase |
| Graph | Relationships, social networks | Neo4j |

**Choosing SQL vs NoSQL:**
- Need transactions/joins? → SQL
- Need flexible schema? → NoSQL
- Need massive write throughput? → NoSQL (Cassandra)
- Need complex queries? → SQL
- Need horizontal scaling? → NoSQL (easier, but SQL can too with sharding)

### Caching

```
Client → Cache HIT → Return cached data (fast)
       → Cache MISS → Database → Store in cache → Return data
```

**Strategies:**
| Strategy | How it works | Use when |
|----------|-------------|----------|
| Cache-Aside | App checks cache first, fills on miss | General purpose |
| Write-Through | Write to cache AND DB simultaneously | Strong consistency needed |
| Write-Behind | Write to cache, async write to DB | High write throughput |
| Read-Through | Cache auto-loads from DB on miss | Simple, automatic |

**What to cache:**
- Database query results (user profiles, product pages)
- Computed results (recommendations, feed rankings)
- Session data
- API responses

**TTL (Time-To-Live):** Set expiry on cached data. Balance: too short = cache miss, too long = stale data.

### Message Queue

```
Producer → [Queue] → Consumer
                   → Consumer
                   → Consumer
```

Decouples producers from consumers. Use when:
- Work is slow (email sending, image processing, video encoding)
- You need to handle bursts (absorb spikes, process at steady rate)
- You need reliable delivery (retry failed messages)

Examples: RabbitMQ, Apache Kafka, AWS SQS

### CDN (Content Delivery Network)

```
User (Sydney) → CDN Edge (Sydney) → Origin Server (US)
                [cache HIT = fast]   [only on cache MISS]
```

Serves static content (images, CSS, JS, videos) from servers close to users. Reduces latency from ~200ms to ~20ms.

## 22.23 Database scaling

### Replication

```
         ┌─────────────┐
Writes → │   Primary   │
         └──────┬──────┘
                │ replicate
        ┌───────┼───────┐
        ▼       ▼       ▼
    [Replica] [Replica] [Replica]  ← Reads distributed here
```

- **Primary** handles all writes
- **Replicas** handle reads (most apps are read-heavy: 90% reads, 10% writes)
- Eventual consistency (replicas may lag by milliseconds)

### Sharding (Horizontal Partitioning)

Split data across multiple databases:

```
Users A-M → Shard 1
Users N-Z → Shard 2
```

Sharding strategies:
- **Hash-based:** `shard = hash(userId) % numShards` — even distribution
- **Range-based:** `A-M → Shard1, N-Z → Shard2` — simple but can be uneven
- **Geographic:** users in EU → EU shard, US → US shard

## 22.24 Common system design questions

### URL Shortener (Easy)

```
Requirements:
- Shorten long URLs to short codes (e.g., bit.ly/abc123)
- Redirect short URL to original
- Analytics (click count)

High-level:
- API: POST /shorten {url} → {shortCode}
       GET /{shortCode} → 301 Redirect

- Generate short code: Base62 encoding of auto-increment ID
- Storage: Key-Value store (shortCode → originalURL)
- Cache: Popular URLs cached in Redis
- Scale: Read-heavy → cache + replicas
```

### Chat System (Medium)

```
Requirements:
- 1:1 and group messaging
- Online status
- Message history
- Real-time delivery

Key decisions:
- WebSocket for real-time push (not HTTP polling)
- Message store: Cassandra (write-heavy, time-series)
- Online status: Redis (TTL-based heartbeat)
- Message delivery: Queue per user (offline messages stored, delivered on reconnect)

Scale:
- WebSocket servers behind load balancer (sticky sessions)
- Fan-out: send message to all group members via message queue
- Read-heavy history: cache recent messages per conversation
```

### News Feed (Hard)

```
Requirements:
- User posts content
- Followers see posts in their feed
- Sorted by recency (or relevance)
- Handle celebrities (millions of followers)

Two approaches:
1. Fan-out on WRITE (push model):
   - When user posts, immediately write to all followers' feeds
   - Fast reads (feed is pre-computed)
   - Slow writes for celebrities (millions of writes per post)

2. Fan-out on READ (pull model):
   - When user opens feed, query all followed users' posts
   - Fast writes (just store the post)
   - Slow reads (query many users, merge, sort)

3. Hybrid (Facebook/Twitter approach):
   - Regular users: fan-out on write (pre-compute followers' feeds)
   - Celebrities: fan-out on read (too expensive to push to millions)
   - Merge at read time
```

### Rate Limiter (Medium)

```
Requirements:
- Limit requests per user per time window
- Return 429 Too Many Requests when exceeded

Algorithms:
1. Fixed Window: Count requests in fixed time windows (e.g., 100 req/min)
2. Sliding Window Log: Store timestamp of each request, count in rolling window
3. Token Bucket: Tokens added at fixed rate, each request costs 1 token
4. Sliding Window Counter: Weighted average of current and previous window

Implementation:
- Redis: INCR key with TTL (fixed window)
- Or Redis sorted set: timestamps as scores (sliding window)
- Distributed: each server checks shared Redis counter
```

## 22.25 System design estimation cheat sheet

```
READ LATENCY:
  L1 cache:           0.5 ns
  RAM:                100 ns
  SSD read:           100 μs
  Network (same DC):  500 μs
  HDD seek:           10 ms
  Network (cross-continent): 150 ms

THROUGHPUT:
  SSD sequential read: 500 MB/s
  Network (1 Gbps):    125 MB/s
  HDD sequential read: 100 MB/s

SCALE NUMBERS:
  Seconds per day:     86,400 (~100K)
  Seconds per month:   2.6M
  QPS from DAU:        DAU × (avg requests per user) / 86400
  Example: 10M DAU × 10 requests = 100M/day ≈ 1,200 QPS average, 2,400 QPS peak (2x)

STORAGE:
  1 char:              1 byte (ASCII) or 2-4 bytes (UTF-8)
  1 tweet (280 char):  ~1 KB (with metadata)
  1 image:             200 KB – 2 MB
  1 video (1 min):     50-100 MB
  1 billion tweets:    ~1 TB
```

## 22.26 Tradeoffs to discuss

Every design interview expects you to discuss tradeoffs:

| Tradeoff | Option A | Option B |
|----------|----------|----------|
| Consistency vs Availability | Strong consistency (bank transactions) | Eventual consistency (social feed) |
| SQL vs NoSQL | ACID, joins, complex queries | Scale, flexibility, speed |
| Cache vs Fresh data | Fast but potentially stale | Always correct but slower |
| Push vs Pull | Real-time, bandwidth cost | On-demand, latency on first load |
| Monolith vs Microservices | Simple, fast to build | Scalable, complex to operate |
| Normalize vs Denormalize | Less storage, no duplicates | Faster reads, redundant data |



---

## Summary

### Part 1: Algorithms ✅
- Data structures: array, hashmap, stack, queue, heap, tree, graph — and when to use each
- Big-O: how to calculate and what's practical for each complexity class
- Sorting: bubble, merge, quick — and why merge sort is the safe default
- Searching: linear O(n) vs binary O(log n) — binary search works on any monotonic function
- Recursion: base case + recursive case + trust the recursion
- DP: overlapping subproblems + optimal substructure → memoize or tabulate
- Graphs: BFS (shortest path) vs DFS (explore all) + when to use each

### Part 2: LeetCode ✅
- 10 core patterns: Two Pointers, Sliding Window, Binary Search, HashMap, Stack, BFS/DFS, Trees, DP, Heap, Intervals
- Each pattern has a template — recognise the pattern, apply the template, adapt to specifics
- Study plan: 8 weeks from Easy to Hard, building pattern recognition progressively

### Part 3: System Design ✅
- Interview framework: Requirements → Estimation → High-level → Detailed → Bottlenecks → Wrap-up
- Building blocks: Load Balancer, Databases (SQL/NoSQL), Cache, Message Queue, CDN
- Scaling: Replication (read), Sharding (write), Caching (latency)
- Common designs: URL Shortener, Chat System, News Feed, Rate Limiter
- Estimation: know your numbers (QPS from DAU, storage per entity, latency ranges)
- Tradeoffs: consistency vs availability, push vs pull, normalise vs denormalise

## Key takeaways

**Algorithms:** Don't memorize — understand the WHY. Why does binary search need sorted input? Why does BFS give shortest path? Once you understand the invariant, you can derive the algorithm.

**LeetCode:** Pattern recognition > brute grinding. 150 well-chosen problems (covering all patterns) beats 500 random problems. After solving a problem, identify WHICH pattern it used and add it to your mental catalogue.

**System Design:** It's about communication, not the "right answer." Show your thinking: state assumptions, calculate numbers, discuss tradeoffs, acknowledge what you're simplifying. The interviewer wants to see HOW you think about large-scale systems, not a perfect architecture diagram.

**The connection:** Algorithms are the building blocks INSIDE system design. A rate limiter uses a HashMap + sliding window. A news feed ranking uses a priority queue. URL shortening uses base conversion. The skills compound.

---

→ [Back to Chapter 21: Authentication](./21-AUTH-NEXTJS-SPRING-JWT.md)
