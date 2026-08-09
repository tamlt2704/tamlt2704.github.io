# Chapter 24: Deep LeetCode Patterns — Recognise, Template, Solve

## What you'll learn

- 15 patterns that cover 90% of LeetCode problems
- Recognition signals (how to spot which pattern applies)
- Full templates with edge cases handled
- Multiple difficulty levels per pattern (Easy → Hard progressions)
- Common mistakes and how to avoid them

---

## The Pattern Recognition Mindset

Don't read a problem and think "what algorithm?" Instead think:
1. **What's the input?** Array, string, tree, graph, matrix?
2. **What's being asked?** Find, count, optimise, check existence?
3. **What constraints?** Size of n (tells you acceptable complexity), sorted?, values range?
4. **What pattern matches this shape?**

---

## Pattern 1: Two Pointers

### Recognition signals
- Sorted array
- "Find pair/triplet that satisfies condition"
- "Remove duplicates in-place"
- Palindrome problems
- "Container with most water" shape (maximise area between two boundaries)

### Template: Opposite direction

```java
int left = 0, right = arr.length - 1;
while (left < right) {
  // Evaluate current pair
  if (condition met) {
    // record answer
    left++; right--; // or just one
  } else if (need bigger) {
    left++;
  } else {
    right--;
  }
}
```

### Template: Same direction (fast/slow)

```java
int slow = 0;
for (int fast = 0; fast < arr.length; fast++) {
  if (shouldKeep(arr[fast])) {
    arr[slow] = arr[fast];
    slow++;
  }
}
// arr[0..slow-1] is the result
```

### Problem: 3Sum (find all triplets that sum to 0)

```java
List<List<Integer>> threeSum(int[] nums) {
  Arrays.sort(nums);
  List<List<Integer>> result = new ArrayList<>();

  for (int i = 0; i < nums.length - 2; i++) {
    if (i > 0 && nums[i] == nums[i-1]) continue; // skip duplicates

    int left = i + 1, right = nums.length - 1;
    while (left < right) {
      int sum = nums[i] + nums[left] + nums[right];
      if (sum == 0) {
        result.add(List.of(nums[i], nums[left], nums[right]));
        while (left < right && nums[left] == nums[left+1]) left++;   // skip dupes
        while (left < right && nums[right] == nums[right-1]) right--; // skip dupes
        left++; right--;
      } else if (sum < 0) left++;
      else right--;
    }
  }
  return result;
}
```

### Problem: Trapping Rain Water (Hard)

```java
int trap(int[] height) {
  int left = 0, right = height.length - 1;
  int leftMax = 0, rightMax = 0;
  int water = 0;

  while (left < right) {
    if (height[left] < height[right]) {
      leftMax = Math.max(leftMax, height[left]);
      water += leftMax - height[left]; // water above this bar
      left++;
    } else {
      rightMax = Math.max(rightMax, height[right]);
      water += rightMax - height[right];
      right--;
    }
  }
  return water;
}
```

**Why this works:** Water at any position is bounded by the minimum of (max height to its left, max height to its right). By moving the shorter side inward, we guarantee the other side has at least that height.

### Practice problems
| # | Problem | Difficulty | Key insight |
|---|---------|-----------|-------------|
| 1 | Two Sum II | Easy | Opposite pointers on sorted array |
| 11 | Container With Most Water | Medium | Move shorter side inward |
| 15 | 3Sum | Medium | Fix one, two-pointer on rest |
| 42 | Trapping Rain Water | Hard | Track left/right max simultaneously |
| 26 | Remove Duplicates | Easy | Fast/slow same direction |
| 125 | Valid Palindrome | Easy | Opposite pointers, skip non-alnum |

---

## Pattern 2: Sliding Window

### Recognition signals
- "Longest/shortest substring/subarray with condition"
- "At most K distinct characters"
- "Maximum sum subarray of size K"
- Contiguous sequence with a constraint

### Template: Variable-size window

```java
int left = 0, best = 0;
// window state (e.g., HashMap for character count, int for sum)

for (int right = 0; right < s.length(); right++) {
  // 1. EXPAND: add s[right] to window state

  // 2. SHRINK: while window is invalid
  while (windowInvalid()) {
    // remove s[left] from window state
    left++;
  }

  // 3. UPDATE: record the best answer
  best = Math.max(best, right - left + 1);
}
return best;
```

### Template: Fixed-size window

```java
int windowSum = 0;
for (int i = 0; i < k; i++) windowSum += arr[i]; // initial window
int maxSum = windowSum;

for (int i = k; i < arr.length; i++) {
  windowSum += arr[i] - arr[i - k]; // slide: add new, remove old
  maxSum = Math.max(maxSum, windowSum);
}
```

### Problem: Minimum Window Substring (Hard)

```java
String minWindow(String s, String t) {
  Map<Character, Integer> need = new HashMap<>();
  for (char c : t.toCharArray()) need.merge(c, 1, Integer::sum);

  int have = 0, required = need.size();
  Map<Character, Integer> window = new HashMap<>();
  int left = 0, minLen = Integer.MAX_VALUE, minStart = 0;

  for (int right = 0; right < s.length(); right++) {
    // Expand
    char c = s.charAt(right);
    window.merge(c, 1, Integer::sum);
    if (need.containsKey(c) && window.get(c).equals(need.get(c))) have++;

    // Shrink while valid
    while (have == required) {
      // Update answer
      if (right - left + 1 < minLen) {
        minLen = right - left + 1;
        minStart = left;
      }
      // Remove left
      char lc = s.charAt(left);
      window.merge(lc, -1, Integer::sum);
      if (need.containsKey(lc) && window.get(lc) < need.get(lc)) have--;
      left++;
    }
  }

  return minLen == Integer.MAX_VALUE ? "" : s.substring(minStart, minStart + minLen);
}
```

### Practice problems
| # | Problem | Difficulty | Key insight |
|---|---------|-----------|-------------|
| 3 | Longest Substring Without Repeating | Medium | HashSet window, shrink on duplicate |
| 76 | Minimum Window Substring | Hard | Count-based validity check |
| 239 | Sliding Window Maximum | Hard | Monotonic deque |
| 424 | Longest Repeating Character Replacement | Medium | Window invalid when replacements > K |
| 567 | Permutation in String | Medium | Fixed-size window, frequency match |

---

## Pattern 3: Binary Search (Advanced)

### Recognition signals
- "Minimum/maximum value that satisfies condition"
- Answer space is monotonic (all-false then all-true, or vice versa)
- "Can we do it in X?" is answerable in O(n) or better

### Template: Binary search on answer

```java
int left = minPossible, right = maxPossible;
while (left < right) {
  int mid = left + (right - left) / 2;
  if (isValid(mid)) {
    right = mid;       // try smaller (find minimum valid)
  } else {
    left = mid + 1;    // too small, need bigger
  }
}
return left; // smallest valid answer

// For maximum valid: flip the logic
while (left < right) {
  int mid = left + (right - left + 1) / 2; // round UP to avoid infinite loop
  if (isValid(mid)) {
    left = mid;        // try bigger (find maximum valid)
  } else {
    right = mid - 1;   // too big
  }
}
return left; // largest valid answer
```

### Problem: Split Array Largest Sum (Hard)

```java
// Minimise the maximum sum when splitting array into m subarrays
int splitArray(int[] nums, int m) {
  int left = Arrays.stream(nums).max().getAsInt();
  int right = Arrays.stream(nums).sum();

  while (left < right) {
    int mid = left + (right - left) / 2;
    if (canSplit(nums, mid, m)) right = mid;
    else left = mid + 1;
  }
  return left;
}

boolean canSplit(int[] nums, int maxSum, int m) {
  int splits = 1, currentSum = 0;
  for (int num : nums) {
    if (currentSum + num > maxSum) {
      splits++;
      currentSum = num;
      if (splits > m) return false;
    } else {
      currentSum += num;
    }
  }
  return true;
}
```

### Practice problems
| # | Problem | Difficulty | Key insight |
|---|---------|-----------|-------------|
| 875 | Koko Eating Bananas | Medium | Binary search on eating speed |
| 1011 | Capacity to Ship Packages | Medium | Binary search on capacity |
| 410 | Split Array Largest Sum | Hard | Binary search on max sum |
| 4 | Median of Two Sorted Arrays | Hard | Binary search on partition point |
| 33 | Search in Rotated Sorted Array | Medium | Binary search with pivot detection |

---

## Pattern 4: Prefix Sum

### Recognition signals
- "Sum of subarray from i to j"
- "Number of subarrays with sum = K"
- "Range sum queries"

### Template

```java
// Build prefix sum: prefix[i] = sum of arr[0..i-1]
int[] prefix = new int[n + 1];
for (int i = 0; i < n; i++) prefix[i+1] = prefix[i] + arr[i];

// Query sum of arr[i..j] in O(1):
int rangeSum = prefix[j+1] - prefix[i];
```

### Problem: Subarray Sum Equals K

```java
int subarraySum(int[] nums, int k) {
  // prefix[j] - prefix[i] = k means subarray(i, j-1) sums to k
  // So for each j, count how many previous prefix sums equal prefix[j] - k
  Map<Integer, Integer> prefixCount = new HashMap<>();
  prefixCount.put(0, 1); // empty prefix
  int sum = 0, count = 0;

  for (int num : nums) {
    sum += num;
    count += prefixCount.getOrDefault(sum - k, 0);
    prefixCount.merge(sum, 1, Integer::sum);
  }
  return count;
}
```

---

## Pattern 5: Monotonic Stack

### Recognition signals
- "Next greater/smaller element"
- "Largest rectangle in histogram"
- "Stock span" (how many consecutive days was price lower?)

### Template: Next Greater Element

```java
int[] nextGreater(int[] nums) {
  int n = nums.length;
  int[] result = new int[n];
  Arrays.fill(result, -1);
  Deque<Integer> stack = new ArrayDeque<>(); // stores indices

  for (int i = 0; i < n; i++) {
    // Pop all elements smaller than current — current IS their next greater
    while (!stack.isEmpty() && nums[i] > nums[stack.peek()]) {
      result[stack.pop()] = nums[i];
    }
    stack.push(i);
  }
  return result;
}
```

### Problem: Largest Rectangle in Histogram (Hard)

```java
int largestRectangleArea(int[] heights) {
  Deque<Integer> stack = new ArrayDeque<>();
  int maxArea = 0;
  int n = heights.length;

  for (int i = 0; i <= n; i++) {
    int h = (i == n) ? 0 : heights[i];
    while (!stack.isEmpty() && h < heights[stack.peek()]) {
      int height = heights[stack.pop()];
      int width = stack.isEmpty() ? i : i - stack.peek() - 1;
      maxArea = Math.max(maxArea, height * width);
    }
    stack.push(i);
  }
  return maxArea;
}
```

---

## Pattern 6: Backtracking

### Recognition signals
- "Generate all combinations/permutations/subsets"
- "N-Queens", "Sudoku solver"
- "Word search in grid"
- Decision tree with pruning

### Template

```java
void backtrack(State state, List<Result> results) {
  if (isComplete(state)) {
    results.add(copy(state));
    return;
  }

  for (Choice choice : getChoices(state)) {
    if (isValid(choice, state)) {  // pruning
      make(choice, state);         // choose
      backtrack(state, results);   // explore
      undo(choice, state);         // un-choose
    }
  }
}
```

### Problem: Combination Sum (find combinations that sum to target)

```java
List<List<Integer>> combinationSum(int[] candidates, int target) {
  List<List<Integer>> results = new ArrayList<>();
  backtrack(candidates, target, 0, new ArrayList<>(), results);
  return results;
}

void backtrack(int[] nums, int remaining, int start, List<Integer> current, List<List<Integer>> results) {
  if (remaining == 0) {
    results.add(new ArrayList<>(current));
    return;
  }
  if (remaining < 0) return;

  for (int i = start; i < nums.length; i++) {
    current.add(nums[i]);
    backtrack(nums, remaining - nums[i], i, current, results); // i not i+1: reuse allowed
    current.remove(current.size() - 1);
  }
}
```

### Practice problems
| # | Problem | Difficulty | Key insight |
|---|---------|-----------|-------------|
| 78 | Subsets | Medium | Include or exclude each element |
| 46 | Permutations | Medium | Used array, swap-based |
| 39 | Combination Sum | Medium | Start index prevents duplicates |
| 51 | N-Queens | Hard | Column, diagonal, anti-diagonal checks |
| 79 | Word Search | Medium | Grid DFS with visited marking |

---

## Pattern 7: BFS / Graph (Advanced)

### Template: Multi-source BFS

```java
// Start BFS from ALL sources simultaneously (e.g., all rotten oranges)
Queue<int[]> queue = new LinkedList<>();
for (int r = 0; r < m; r++)
  for (int c = 0; c < n; c++)
    if (grid[r][c] == SOURCE) queue.add(new int[]{r, c});

int steps = 0;
while (!queue.isEmpty()) {
  int size = queue.size();
  for (int i = 0; i < size; i++) {
    int[] curr = queue.poll();
    for (int[] dir : DIRS) {
      int nr = curr[0] + dir[0], nc = curr[1] + dir[1];
      if (valid(nr, nc) && grid[nr][nc] == UNVISITED) {
        grid[nr][nc] = VISITED;
        queue.add(new int[]{nr, nc});
      }
    }
  }
  steps++;
}
```

### Template: Topological sort with cycle detection

```java
// Returns empty list if cycle exists (can't take all courses)
List<Integer> topSort(int n, int[][] prerequisites) {
  List<List<Integer>> graph = new ArrayList<>();
  int[] inDegree = new int[n];
  for (int i = 0; i < n; i++) graph.add(new ArrayList<>());
  for (int[] p : prerequisites) {
    graph.get(p[1]).add(p[0]);
    inDegree[p[0]]++;
  }

  Queue<Integer> queue = new LinkedList<>();
  for (int i = 0; i < n; i++)
    if (inDegree[i] == 0) queue.add(i);

  List<Integer> order = new ArrayList<>();
  while (!queue.isEmpty()) {
    int node = queue.poll();
    order.add(node);
    for (int next : graph.get(node))
      if (--inDegree[next] == 0) queue.add(next);
  }
  return order.size() == n ? order : List.of(); // cycle if not all nodes processed
}
```

### Practice problems
| # | Problem | Difficulty | Key insight |
|---|---------|-----------|-------------|
| 994 | Rotting Oranges | Medium | Multi-source BFS |
| 207 | Course Schedule | Medium | Topological sort, cycle = impossible |
| 127 | Word Ladder | Hard | BFS on word graph, transform 1 char |
| 743 | Network Delay Time | Medium | Dijkstra shortest path |
| 261 | Graph Valid Tree | Medium | Union-Find: n-1 edges + connected |

---

## Pattern 8: Dynamic Programming (Advanced)

### Problem: Longest Increasing Subsequence (LIS)

```java
// O(n²) approach
int lengthOfLIS(int[] nums) {
  int[] dp = new int[nums.length]; // dp[i] = LIS ending at i
  Arrays.fill(dp, 1);
  int max = 1;

  for (int i = 1; i < nums.length; i++) {
    for (int j = 0; j < i; j++) {
      if (nums[j] < nums[i]) dp[i] = Math.max(dp[i], dp[j] + 1);
    }
    max = Math.max(max, dp[i]);
  }
  return max;
}

// O(n log n) approach — patience sorting
int lengthOfLIS_fast(int[] nums) {
  List<Integer> tails = new ArrayList<>(); // smallest tail of LIS of each length
  for (int num : nums) {
    int pos = Collections.binarySearch(tails, num);
    if (pos < 0) pos = -(pos + 1);
    if (pos == tails.size()) tails.add(num);
    else tails.set(pos, num);
  }
  return tails.size();
}
```

### Problem: Edit Distance

```java
int minDistance(String word1, String word2) {
  int m = word1.length(), n = word2.length();
  int[][] dp = new int[m + 1][n + 1];

  // Base cases
  for (int i = 0; i <= m; i++) dp[i][0] = i; // delete all
  for (int j = 0; j <= n; j++) dp[0][j] = j; // insert all

  for (int i = 1; i <= m; i++) {
    for (int j = 1; j <= n; j++) {
      if (word1.charAt(i-1) == word2.charAt(j-1)) {
        dp[i][j] = dp[i-1][j-1]; // chars match, no operation
      } else {
        dp[i][j] = 1 + Math.min(
          dp[i-1][j],     // delete from word1
          Math.min(
            dp[i][j-1],   // insert into word1
            dp[i-1][j-1]  // replace
          )
        );
      }
    }
  }
  return dp[m][n];
}
```

### Problem: Word Break

```java
boolean wordBreak(String s, List<String> wordDict) {
  Set<String> dict = new HashSet<>(wordDict);
  boolean[] dp = new boolean[s.length() + 1];
  dp[0] = true; // empty string can be segmented

  for (int i = 1; i <= s.length(); i++) {
    for (int j = 0; j < i; j++) {
      if (dp[j] && dict.contains(s.substring(j, i))) {
        dp[i] = true;
        break;
      }
    }
  }
  return dp[s.length()];
}
```

### Practice problems
| # | Problem | Difficulty | Key insight |
|---|---------|-----------|-------------|
| 300 | Longest Increasing Subsequence | Medium | dp[i] = LIS ending at i; O(n log n) with patience |
| 72 | Edit Distance | Medium | 2D DP: match/insert/delete/replace |
| 139 | Word Break | Medium | dp[i] = can segment s[0..i-1] |
| 322 | Coin Change | Medium | dp[amount] = min coins for amount |
| 1143 | Longest Common Subsequence | Medium | dp[i][j] = LCS of first i and first j chars |
| 518 | Coin Change 2 (count ways) | Medium | Order doesn't matter — outer loop on coins |

---

## Pattern 9: Heap / Priority Queue (Advanced)

### Problem: Merge K Sorted Lists

```java
ListNode mergeKLists(ListNode[] lists) {
  PriorityQueue<ListNode> pq = new PriorityQueue<>((a, b) -> a.val - b.val);

  for (ListNode head : lists)
    if (head != null) pq.add(head);

  ListNode dummy = new ListNode(0), curr = dummy;
  while (!pq.isEmpty()) {
    ListNode smallest = pq.poll();
    curr.next = smallest;
    curr = curr.next;
    if (smallest.next != null) pq.add(smallest.next);
  }
  return dummy.next;
}
// Time: O(N log K) where N = total nodes, K = number of lists
```

### Problem: Find Median from Data Stream

```java
class MedianFinder {
  PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder()); // left half
  PriorityQueue<Integer> minHeap = new PriorityQueue<>(); // right half

  void addNum(int num) {
    maxHeap.add(num);
    minHeap.add(maxHeap.poll()); // ensure maxHeap top ≤ minHeap top

    // Balance: maxHeap can have at most 1 more element
    if (minHeap.size() > maxHeap.size()) {
      maxHeap.add(minHeap.poll());
    }
  }

  double findMedian() {
    if (maxHeap.size() > minHeap.size()) return maxHeap.peek();
    return (maxHeap.peek() + minHeap.peek()) / 2.0;
  }
}
```

---

## Pattern 10: Linked List Tricks

### Fast/slow pointers (cycle detection, middle finding)

```java
// Find middle of linked list
ListNode findMiddle(ListNode head) {
  ListNode slow = head, fast = head;
  while (fast != null && fast.next != null) {
    slow = slow.next;
    fast = fast.next.next;
  }
  return slow; // middle (or first of second half)
}

// Detect cycle (Floyd's algorithm)
boolean hasCycle(ListNode head) {
  ListNode slow = head, fast = head;
  while (fast != null && fast.next != null) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow == fast) return true;
  }
  return false;
}

// Reverse linked list (iterative)
ListNode reverse(ListNode head) {
  ListNode prev = null, curr = head;
  while (curr != null) {
    ListNode next = curr.next;
    curr.next = prev;
    prev = curr;
    curr = next;
  }
  return prev;
}
```

---

## 24.1 The LeetCode solving process

```
1. READ (2 min)
   - Understand input/output
   - Identify constraints (n size → acceptable complexity)
   - Note edge cases

2. PATTERN (2 min)
   - What data structure is the input?
   - What's being optimised?
   - Which pattern fits?

3. PLAN (3 min)
   - Write the approach in comments
   - Identify the key data structure (HashMap? Heap? Stack?)
   - Walk through an example mentally

4. CODE (10 min)
   - Write clean, variable-named code
   - Handle edge cases

5. TEST (3 min)
   - Trace through examples
   - Check edge cases: empty, single element, all same, sorted/reverse sorted
```

## 24.2 Complete study roadmap (by pattern)

| Week | Pattern | Easy | Medium | Hard |
|------|---------|------|--------|------|
| 1 | Two Pointers + Arrays | 1, 26, 27, 125 | 11, 15, 167 | 42 |
| 2 | Sliding Window | 643 | 3, 424, 567 | 76, 239 |
| 3 | HashMap + Prefix Sum | 1, 217, 242 | 49, 560, 128 | — |
| 4 | Stack + Monotonic Stack | 20, 155 | 739, 150, 853 | 84, 85 |
| 5 | Binary Search | 704, 35 | 33, 875, 153 | 4, 410 |
| 6 | Trees + BFS/DFS | 104, 226, 100 | 102, 236, 98 | 124, 297 |
| 7 | Graph + Topo Sort | — | 200, 207, 994 | 127, 269 |
| 8 | DP (1D + 2D) | 70, 746 | 300, 322, 139 | 72, 312 |
| 9 | Heap + Intervals | — | 56, 347, 253 | 23, 295 |
| 10 | Backtracking | — | 39, 46, 78 | 51, 212 |

---

## Summary

✅ You know 10 core patterns with full templates and edge-case handling
✅ You can recognise which pattern a problem uses from its signals
✅ You have worked examples at Easy, Medium, and Hard for each pattern
✅ You understand the solving process (Read → Pattern → Plan → Code → Test)
✅ You have a 10-week study roadmap with specific problem numbers

## Key takeaway

**Pattern recognition is the skill.** After solving 100+ problems across all patterns, you'll read a new problem and immediately think "that's a sliding window" or "that's binary search on the answer." The template handles 80% of the code — you just adapt it to the specific problem.

---

→ [Back to Chapter 23: Deep Algorithms](./23-DEEP-ALGORITHMS.md)
