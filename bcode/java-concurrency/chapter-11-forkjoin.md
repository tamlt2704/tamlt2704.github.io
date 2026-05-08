# Chapter 11: Fork/Join Framework

[← Chapter 10: Latches and Barriers](chapter-10-latches-barriers.md) | [Chapter 12: Virtual Threads →](chapter-12-virtual-threads.md)

---

## The Problem

Kai's aggregation algorithm computes percentiles over millions of events. The algorithm is recursive — divide the data, compute partial results, merge:

```java
public class PercentileCalculator {
    public double[] computePercentiles(long[] latencies, double[] percentiles) {
        Arrays.sort(latencies);  // O(n log n) — single-threaded
        double[] results = new double[percentiles.length];
        for (int i = 0; i < percentiles.length; i++) {
            int index = (int) (percentiles[i] * latencies.length);
            results[i] = latencies[index];
        }
        return results;
    }
}
```

With 10 million latency samples, `Arrays.sort()` takes 800ms on one core. We have 8 cores sitting idle.

Kai: "The sort is divide-and-conquer. Merge sort splits the array, sorts halves, merges. Each half is independent. Can we sort both halves in parallel?"

Yes. That's exactly what Fork/Join does.

## The Fork/Join Model

Fork/Join is designed for recursive divide-and-conquer:

```
1. FORK: Split the problem into smaller subproblems
2. Solve subproblems (recursively fork if still too large)
3. JOIN: Combine results from subproblems
```

```java
import java.util.concurrent.RecursiveTask;
import java.util.concurrent.ForkJoinPool;

public class ParallelSum extends RecursiveTask<Long> {
    private final long[] array;
    private final int start, end;
    private static final int THRESHOLD = 10_000;

    public ParallelSum(long[] array, int start, int end) {
        this.array = array;
        this.start = start;
        this.end = end;
    }

    @Override
    protected Long compute() {
        int length = end - start;

        // Base case: small enough to compute directly
        if (length <= THRESHOLD) {
            long sum = 0;
            for (int i = start; i < end; i++) {
                sum += array[i];
            }
            return sum;
        }

        // Recursive case: split in half
        int mid = start + length / 2;
        ParallelSum left = new ParallelSum(array, start, mid);
        ParallelSum right = new ParallelSum(array, mid, end);

        left.fork();           // Submit left half to pool (async)
        long rightResult = right.compute();  // Compute right half in this thread
        long leftResult = left.join();       // Wait for left half

        return leftResult + rightResult;
    }
}

// Usage
ForkJoinPool pool = new ForkJoinPool();  // Default: CPU core count threads
long[] data = new long[10_000_000];
long sum = pool.invoke(new ParallelSum(data, 0, data.length));
```

## RecursiveTask vs RecursiveAction

```java
// RecursiveTask<V>: returns a result
class SumTask extends RecursiveTask<Long> {
    protected Long compute() { return 42L; }
}

// RecursiveAction: no result (side effects only)
class SortTask extends RecursiveAction {
    protected void compute() { /* sorts in place */ }
}
```

## Work Stealing

The magic of `ForkJoinPool`: **work stealing**.

In a regular thread pool, each thread has one shared queue. Under Fork/Join, each thread has its own deque (double-ended queue):

```
Thread 0: [task][task][task][task]  ← busy
Thread 1: [task]                    ← almost done
Thread 2: []                        ← idle, steals from Thread 0's tail
Thread 3: [task][task]              ← working
```

When a thread finishes its work, it steals tasks from the tail of another thread's deque. This keeps all cores busy without centralized scheduling.

Key insight: `fork()` pushes to the current thread's deque. Other idle threads steal from it. This is why Fork/Join outperforms a regular `ExecutorService` for recursive tasks.

## Parallel Merge Sort

```java
public class ParallelMergeSort extends RecursiveAction {
    private final long[] array;
    private final long[] temp;
    private final int start, end;
    private static final int THRESHOLD = 8192;

    public ParallelMergeSort(long[] array, long[] temp, int start, int end) {
        this.array = array;
        this.temp = temp;
        this.start = start;
        this.end = end;
    }

    @Override
    protected void compute() {
        if (end - start <= THRESHOLD) {
            Arrays.sort(array, start, end);  // Small: use sequential sort
            return;
        }

        int mid = (start + end) / 2;

        // Fork left, compute right
        ParallelMergeSort left = new ParallelMergeSort(array, temp, start, mid);
        ParallelMergeSort right = new ParallelMergeSort(array, temp, mid, end);

        left.fork();
        right.compute();
        left.join();

        // Merge sorted halves
        merge(array, temp, start, mid, end);
    }

    private void merge(long[] arr, long[] tmp, int start, int mid, int end) {
        System.arraycopy(arr, start, tmp, start, end - start);
        int i = start, j = mid, k = start;
        while (i < mid && j < end) {
            arr[k++] = tmp[i] <= tmp[j] ? tmp[i++] : tmp[j++];
        }
        while (i < mid) arr[k++] = tmp[i++];
        while (j < end) arr[k++] = tmp[j++];
    }
}

// Usage
long[] data = new long[10_000_000];
long[] temp = new long[data.length];
ForkJoinPool pool = new ForkJoinPool();
pool.invoke(new ParallelMergeSort(data, temp, 0, data.length));
```

Benchmark (10M elements):
```
Arrays.sort (sequential):     820ms
ParallelMergeSort (8 cores):  180ms  — 4.5x speedup
Arrays.parallelSort:          190ms  — JDK's built-in, similar performance
```

## The Common ForkJoinPool

Java provides a shared `ForkJoinPool` used by parallel streams, `CompletableFuture.supplyAsync()`, and `Arrays.parallelSort()`:

```java
// These all use the common pool:
Arrays.parallelSort(data);
list.parallelStream().map(...).collect(...);
CompletableFuture.supplyAsync(() -> compute());

// The common pool has CPU-count threads
ForkJoinPool.commonPool().getParallelism();  // e.g., 7 (on 8-core machine)
```

**Warning**: if you do blocking I/O in the common pool, you starve CPU-bound tasks. Use a separate pool for I/O (see Chapter 7).

## Choosing the Right Threshold

The threshold determines when to stop splitting and compute directly:

```java
// Too small: overhead of forking exceeds benefit
private static final int THRESHOLD = 10;  // BAD: millions of tiny tasks

// Too large: not enough parallelism
private static final int THRESHOLD = 5_000_000;  // BAD: only 2 tasks on 10M elements

// Good rule of thumb: array.length / (parallelism * 4)
// For 10M elements, 8 cores: 10M / 32 ≈ 300K
private static final int THRESHOLD = 100_000;  // Reasonable
```

Benchmark different thresholds for your workload. The sweet spot depends on the cost of the base computation.

## PulseMetrics: Parallel Aggregation

```java
public class ParallelPercentile extends RecursiveTask<long[]> {
    private final long[] latencies;
    private final int start, end;
    private static final int THRESHOLD = 100_000;

    public ParallelPercentile(long[] latencies, int start, int end) {
        this.latencies = latencies;
        this.start = start;
        this.end = end;
    }

    @Override
    protected long[] compute() {
        if (end - start <= THRESHOLD) {
            // Base case: sort this chunk and return
            long[] chunk = Arrays.copyOfRange(latencies, start, end);
            Arrays.sort(chunk);
            return chunk;
        }

        int mid = (start + end) / 2;
        ParallelPercentile left = new ParallelPercentile(latencies, start, mid);
        ParallelPercentile right = new ParallelPercentile(latencies, mid, end);

        left.fork();
        long[] rightSorted = right.compute();
        long[] leftSorted = left.join();

        return mergeSorted(leftSorted, rightSorted);
    }

    private long[] mergeSorted(long[] a, long[] b) {
        long[] result = new long[a.length + b.length];
        int i = 0, j = 0, k = 0;
        while (i < a.length && j < b.length) {
            result[k++] = a[i] <= b[j] ? a[i++] : b[j++];
        }
        while (i < a.length) result[k++] = a[i++];
        while (j < b.length) result[k++] = b[j++];
        return result;
    }
}

// Usage in PulseMetrics
public class LatencyReporter {
    private final ForkJoinPool pool = new ForkJoinPool();

    public LatencyReport computeReport(long[] samples) {
        // Parallel sort via Fork/Join
        long[] sorted = pool.invoke(new ParallelPercentile(samples, 0, samples.length));

        return new LatencyReport(
            sorted[(int)(sorted.length * 0.50)],  // p50
            sorted[(int)(sorted.length * 0.95)],  // p95
            sorted[(int)(sorted.length * 0.99)],  // p99
            sorted[sorted.length - 1]              // max
        );
    }

    public record LatencyReport(long p50, long p95, long p99, long max) {}
}
```

## Parallel Streams: Fork/Join Made Easy

For simple parallel operations, parallel streams use Fork/Join under the hood:

```java
// Sequential
long sum = events.stream()
    .mapToLong(Event::bytes)
    .sum();

// Parallel (uses common ForkJoinPool)
long sum = events.parallelStream()
    .mapToLong(Event::bytes)
    .sum();

// With a custom pool (to avoid polluting the common pool)
ForkJoinPool customPool = new ForkJoinPool(4);
long sum = customPool.submit(() ->
    events.parallelStream()
        .mapToLong(Event::bytes)
        .sum()
).join();
```

When to use parallel streams:
- Large collections (>10K elements)
- CPU-bound operations (no I/O in the pipeline)
- Operations are independent (no shared mutable state)
- The source splits well (ArrayList yes, LinkedList no)

## Common Mistakes

### 1. Forking Both Halves

```java
// WRONG: forks both, then joins both — wastes the current thread
left.fork();
right.fork();       // Current thread does nothing while waiting!
left.join();
right.join();

// RIGHT: fork one, compute the other in this thread
left.fork();
long rightResult = right.compute();  // Use this thread!
long leftResult = left.join();
```

### 2. Blocking I/O in Fork/Join

```java
// WRONG: blocks a ForkJoinPool thread
protected Long compute() {
    return httpClient.get(url).getBody().length();  // Blocks!
}

// Fork/Join is for CPU-bound work. Use ExecutorService for I/O.
```

### 3. Shared Mutable State

```java
// WRONG: race condition in Fork/Join task
private long totalSum = 0;  // Shared!

protected void compute() {
    totalSum += localSum;  // Race condition!
}

// RIGHT: return results, merge in join
protected Long compute() {
    return leftResult + rightResult;  // No shared state
}
```

## What You Learned

- **ForkJoinPool** — thread pool optimized for recursive divide-and-conquer
- **RecursiveTask/RecursiveAction** — tasks that split themselves
- **fork()** — submit subtask to the pool asynchronously
- **join()** — wait for subtask result
- **Work stealing** — idle threads steal from busy threads' queues
- **Threshold** — stop splitting when subproblem is small enough
- **Parallel streams** — Fork/Join made easy for collection processing
- **Fork one, compute the other** — don't waste the current thread

Aggregation is parallel. But PulseMetrics is growing — 100K concurrent WebSocket connections for real-time dashboards. Each connection needs a thread for I/O. 100K platform threads = 100GB of stack memory. We need virtual threads.

---

[← Chapter 10: Latches and Barriers](chapter-10-latches-barriers.md) | [Chapter 12: Virtual Threads →](chapter-12-virtual-threads.md)
