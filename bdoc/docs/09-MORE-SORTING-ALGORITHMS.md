# Chapter 09: More Sorting Algorithms

## What you'll learn

- How to add Selection Sort (minimal code change)
- How to add Merge Sort (introduces the concept of auxiliary space visualisation)
- How to build an algorithm selector

## 9.1 The pattern

Every new algorithm follows the same pattern:

1. Define the code (Java + Python versions)
2. Write a `generate___Steps(input)` function that produces `AlgorithmStep[]`
3. Plug it into the existing UI

The UI, controls, and BarChart component don't change at all. Only the step generation differs. This is the payoff of good architecture — adding algorithms is cheap.

## 9.2 Selection Sort

Create `app/algorithms/lib/selectionSort.ts`:

```ts
import { AlgorithmStep } from "./types";

export const SELECTION_SORT_CODE_JAVA = [
  "public void selectionSort(int[] arr) {",
  "  int n = arr.length;",
  "  for (int i = 0; i < n - 1; i++) {",
  "    int minIdx = i;",
  "    for (int j = i + 1; j < n; j++) {",
  "      if (arr[j] < arr[minIdx]) {",
  "        minIdx = j;",
  "      }",
  "    }",
  "    // Swap arr[i] and arr[minIdx]",
  "    int temp = arr[i];",
  "    arr[i] = arr[minIdx];",
  "    arr[minIdx] = temp;",
  "  }",
  "}",
];

export const SELECTION_SORT_CODE_PYTHON = [
  "def selection_sort(arr):",
  "    n = len(arr)",
  "    for i in range(n - 1):",
  "        min_idx = i",
  "        for j in range(i + 1, n):",
  "            if arr[j] < arr[min_idx]:",
  "                min_idx = j",
  "",
  "",
  "        # Swap arr[i] and arr[min_idx]",
  "        arr[i], arr[min_idx] = arr[min_idx], arr[i]",
  "",
  "",
  "",
  "",
];

export function generateSelectionSortSteps(input: number[]): AlgorithmStep[] {
  const steps: AlgorithmStep[] = [];
  const arr = [...input];
  const n = arr.length;
  const sorted: number[] = [];

  steps.push({
    codeLine: 0,
    description: "Start selection sort — find the minimum element and place it at the front",
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: [],
  });

  for (let i = 0; i < n - 1; i++) {
    let minIdx = i;

    steps.push({
      codeLine: 3,
      description: `Pass ${i + 1}: find the minimum in positions ${i} to ${n - 1}. Current minimum: arr[${minIdx}]=${arr[minIdx]}`,
      array: [...arr],
      comparing: [minIdx],
      swapping: null,
      sorted: [...sorted],
    });

    for (let j = i + 1; j < n; j++) {
      steps.push({
        codeLine: 5,
        description: `Compare arr[${j}]=${arr[j]} with current min arr[${minIdx}]=${arr[minIdx]}`,
        array: [...arr],
        comparing: [j, minIdx],
        swapping: null,
        sorted: [...sorted],
      });

      if (arr[j] < arr[minIdx]) {
        minIdx = j;
        steps.push({
          codeLine: 6,
          description: `Found new minimum! arr[${j}]=${arr[j]} < ${arr[minIdx === j ? i : minIdx]}. minIdx = ${j}`,
          array: [...arr],
          comparing: [minIdx],
          swapping: null,
          sorted: [...sorted],
        });
      }
    }

    if (minIdx !== i) {
      steps.push({
        codeLine: 10,
        description: `Swap arr[${i}]=${arr[i]} with arr[${minIdx}]=${arr[minIdx]} (place minimum at position ${i})`,
        array: [...arr],
        comparing: [],
        swapping: [i, minIdx],
        sorted: [...sorted],
      });

      [arr[i], arr[minIdx]] = [arr[minIdx], arr[i]];

      steps.push({
        codeLine: 12,
        description: `After swap: position ${i} now has ${arr[i]} (its final value)`,
        array: [...arr],
        comparing: [],
        swapping: null,
        sorted: [...sorted, i],
      });
    } else {
      steps.push({
        codeLine: 9,
        description: `arr[${i}]=${arr[i]} is already the minimum — no swap needed`,
        array: [...arr],
        comparing: [],
        swapping: null,
        sorted: [...sorted, i],
      });
    }

    sorted.push(i);
  }

  sorted.push(n - 1);
  steps.push({
    codeLine: 14,
    description: "Array is fully sorted!",
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: [...sorted],
  });

  return steps;
}
```

**Notice how similar the structure is to Bubble Sort.** Same type, same pattern — just different algorithm logic inside.

## 9.3 Merge Sort (more complex)

Merge sort is different because it uses auxiliary space (temporary arrays during merging). Our visualisation needs to show this.

Extend the step type to handle this. Update `app/algorithms/lib/types.ts`:

```ts
export type AlgorithmStep = {
  codeLine: number;
  description: string;
  array: number[];
  comparing: number[];
  swapping: [number, number] | null;
  sorted: number[];
  // New: for merge sort
  auxiliaryArrays?: { label: string; data: number[] }[];
  activeRange?: [number, number]; // which portion of the array is currently being processed
};
```

Create `app/algorithms/lib/mergeSort.ts`:

```ts
import { AlgorithmStep } from "./types";

export const MERGE_SORT_CODE_JAVA = [
  "public void mergeSort(int[] arr, int left, int right) {",
  "  if (left < right) {",
  "    int mid = (left + right) / 2;",
  "    mergeSort(arr, left, mid);",
  "    mergeSort(arr, mid + 1, right);",
  "    merge(arr, left, mid, right);",
  "  }",
  "}",
  "",
  "void merge(int[] arr, int l, int m, int r) {",
  "  int[] left = Arrays.copyOfRange(arr, l, m + 1);",
  "  int[] right = Arrays.copyOfRange(arr, m + 1, r + 1);",
  "  int i = 0, j = 0, k = l;",
  "  while (i < left.length && j < right.length) {",
  "    if (left[i] <= right[j]) {",
  "      arr[k++] = left[i++];",
  "    } else {",
  "      arr[k++] = right[j++];",
  "    }",
  "  }",
  "  // Copy remaining elements",
  "  while (i < left.length) arr[k++] = left[i++];",
  "  while (j < right.length) arr[k++] = right[j++];",
  "}",
];

export function generateMergeSortSteps(input: number[]): AlgorithmStep[] {
  const steps: AlgorithmStep[] = [];
  const arr = [...input];
  const sorted: number[] = [];

  steps.push({
    codeLine: 0,
    description: "Start merge sort — divide the array in half, sort each half, then merge",
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: [],
  });

  function mergeSortHelper(left: number, right: number) {
    if (left >= right) return;

    const mid = Math.floor((left + right) / 2);

    steps.push({
      codeLine: 2,
      description: `Divide: split arr[${left}..${right}] at mid=${mid}`,
      array: [...arr],
      comparing: [],
      swapping: null,
      sorted: [...sorted],
      activeRange: [left, right],
    });

    mergeSortHelper(left, mid);
    mergeSortHelper(mid + 1, right);

    // Merge phase
    const leftArr = arr.slice(left, mid + 1);
    const rightArr = arr.slice(mid + 1, right + 1);

    steps.push({
      codeLine: 5,
      description: `Merge: combining [${leftArr}] and [${rightArr}]`,
      array: [...arr],
      comparing: [],
      swapping: null,
      sorted: [...sorted],
      auxiliaryArrays: [
        { label: "Left", data: leftArr },
        { label: "Right", data: rightArr },
      ],
      activeRange: [left, right],
    });

    let i = 0, j = 0, k = left;

    while (i < leftArr.length && j < rightArr.length) {
      steps.push({
        codeLine: 14,
        description: `Compare left[${i}]=${leftArr[i]} with right[${j}]=${rightArr[j]}`,
        array: [...arr],
        comparing: [k],
        swapping: null,
        sorted: [...sorted],
        activeRange: [left, right],
      });

      if (leftArr[i] <= rightArr[j]) {
        arr[k] = leftArr[i];
        i++;
      } else {
        arr[k] = rightArr[j];
        j++;
      }
      k++;

      steps.push({
        codeLine: 15,
        description: `Placed ${arr[k - 1]} at position ${k - 1}`,
        array: [...arr],
        comparing: [],
        swapping: null,
        sorted: [...sorted],
        activeRange: [left, right],
      });
    }

    while (i < leftArr.length) {
      arr[k] = leftArr[i];
      i++;
      k++;
    }
    while (j < rightArr.length) {
      arr[k] = rightArr[j];
      j++;
      k++;
    }

    steps.push({
      codeLine: 22,
      description: `Merged result: [${arr.slice(left, right + 1)}]`,
      array: [...arr],
      comparing: [],
      swapping: null,
      sorted: [...sorted],
      activeRange: [left, right],
    });
  }

  mergeSortHelper(0, arr.length - 1);

  // Mark all as sorted
  for (let i = 0; i < arr.length; i++) sorted.push(i);

  steps.push({
    codeLine: 7,
    description: "Array is fully sorted!",
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: [...sorted],
  });

  return steps;
}
```

## 9.4 Build an algorithm selector

Update `page.tsx` to allow switching algorithms:

```tsx
type Algorithm = "bubble" | "selection" | "merge";

const ALGORITHMS: Record<Algorithm, { name: string; description: string }> = {
  bubble: { name: "Bubble Sort", description: "Repeatedly swap adjacent elements if they are in the wrong order" },
  selection: { name: "Selection Sort", description: "Find the minimum element and place it at the front" },
  merge: { name: "Merge Sort", description: "Divide in half, sort each half, merge them together" },
};
```

```tsx
const [algorithm, setAlgorithm] = useState<Algorithm>("bubble");

const steps = useMemo(() => {
  switch (algorithm) {
    case "bubble": return generateBubbleSortSteps(INITIAL_ARRAY);
    case "selection": return generateSelectionSortSteps(INITIAL_ARRAY);
    case "merge": return generateMergeSortSteps(INITIAL_ARRAY);
  }
}, [algorithm]);

const code = useMemo(() => {
  switch (algorithm) {
    case "bubble": return BUBBLE_SORT_CODE_JAVA;
    case "selection": return SELECTION_SORT_CODE_JAVA;
    case "merge": return MERGE_SORT_CODE_JAVA;
  }
}, [algorithm]);
```

Add a selector in the header:

```tsx
<select
  value={algorithm}
  onChange={(e) => {
    setAlgorithm(e.target.value as Algorithm);
    setCurrentStep(0);
    setIsPlaying(false);
  }}
  className="px-3 py-1.5 border rounded text-sm"
>
  {Object.entries(ALGORITHMS).map(([key, { name }]) => (
    <option key={key} value={key}>{name}</option>
  ))}
</select>
```

When you change the algorithm, the steps regenerate, the step counter resets, and the UI updates. No other changes needed.

## 9.5 Why this architecture works

Adding a new algorithm requires ONLY:
1. A new file in `lib/` with the code + step generator
2. A new entry in the `ALGORITHMS` object
3. A new case in the switch statement

The entire UI layer (CodePanel, BarChart, Controls) is **algorithm-agnostic**. It only knows about `AlgorithmStep` — it doesn't know or care whether it's bubble sort, merge sort, or quicksort.

> **This is the Open/Closed Principle in action:** The system is open for extension (new algorithms) but closed for modification (existing code doesn't change). If you've studied design patterns in Java, this is the same idea — program to an interface (`AlgorithmStep`), not an implementation.

## Summary

✅ You added Selection Sort and Merge Sort  
✅ You built an algorithm selector dropdown  
✅ You see the pattern: all algorithms share the same UI through the `AlgorithmStep` interface  
✅ You extended the step type for merge sort's auxiliary arrays  

## Key takeaway

**The `AlgorithmStep` type is your contract.** As long as a step generator produces this shape of data, the UI handles it. This is the same principle as interfaces in Java or protocols in Python — define the shape, let implementations vary.

---

→ [Chapter 10: Graph Visualisation — BFS and DFS](./10-GRAPH-VISUALISATION.md)
