# Chapter 08: The Step Engine — Connecting Code to Visualisation

## What you'll learn

- How to pre-compute all algorithm steps
- How to represent a "step" as data
- How to sync the code highlight with the visualisation state
- How to build Bubble Sort end-to-end

This is the most important chapter. Everything before was setup — this is where the visualiser becomes real.

## 8.1 The core idea

An algorithm visualiser is NOT running the algorithm live. It's replaying pre-computed steps.

**Why pre-compute?** Because:
- Users want to go backwards (you can't un-execute code)
- Users want to jump to any step
- You need to know the total step count upfront (for the progress bar)
- Animation timing would be unpredictable if you ran real code

So the workflow is:

```
Input array → Run algorithm → Generate step list → User navigates steps
             (happens once)                        (happens on every click)
```

Each step contains EVERYTHING needed to render that moment in time:
- Which line of code is highlighted
- What the array looks like right now
- Which elements are being compared/swapped
- A human-readable description

## 8.2 Define the Step type

Create `app/algorithms/lib/types.ts`:

```ts
export type AlgorithmStep = {
  // Code
  codeLine: number;        // which line to highlight (0-indexed)
  description: string;     // what's happening in plain English

  // Visualisation state
  array: number[];         // current state of the array
  comparing: number[];     // indices being compared (highlighted yellow)
  swapping: [number, number] | null;  // indices being swapped (highlighted red)
  sorted: number[];        // indices that are in their final position (highlighted green)
};
```

> **Why include the full array in every step?** Because the user can jump to any step. If we only stored "diffs" (what changed), we'd need to replay from the beginning to reach step 47. By storing the full state, every step is self-contained — O(1) access.
>
> **The trade-off:** More memory. For bubble sort on a 10-element array, you get ~90 steps × 10 numbers = ~900 integers. Trivial. For merge sort on 1000 elements, it could grow large. For our educational context (small arrays), full state is the right choice.
>
> **Alternative: diff-based.** Store only changes (`{type: "swap", i: 2, j: 5}`). Faster to generate, smaller storage. But then Prev requires replaying from start, or maintaining an undo stack. More complex for no real benefit at our scale.

## 8.3 Generate Bubble Sort steps

Create `app/algorithms/lib/bubbleSort.ts`:

```ts
import { AlgorithmStep } from "./types";

export const BUBBLE_SORT_CODE_JAVA = [
  "public void bubbleSort(int[] arr) {",
  "  int n = arr.length;",
  "  for (int i = 0; i < n - 1; i++) {",
  "    for (int j = 0; j < n - i - 1; j++) {",
  "      if (arr[j] > arr[j + 1]) {",
  "        // Swap arr[j] and arr[j+1]",
  "        int temp = arr[j];",
  "        arr[j] = arr[j + 1];",
  "        arr[j + 1] = temp;",
  "      }",
  "    }",
  "  }",
  "}",
];

export const BUBBLE_SORT_CODE_PYTHON = [
  "def bubble_sort(arr):",
  "    n = len(arr)",
  "    for i in range(n - 1):",
  "        for j in range(n - i - 1):",
  "            if arr[j] > arr[j + 1]:",
  "                # Swap arr[j] and arr[j+1]",
  "                arr[j], arr[j + 1] = arr[j + 1], arr[j]",
  "",
  "",
  "",
  "",
  "",
  "",
];

export function generateBubbleSortSteps(input: number[]): AlgorithmStep[] {
  const steps: AlgorithmStep[] = [];
  const arr = [...input]; // don't mutate the original
  const n = arr.length;
  const sorted: number[] = [];

  // Initial state
  steps.push({
    codeLine: 0,
    description: "Start bubble sort — we'll repeatedly compare adjacent elements",
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: [],
  });

  steps.push({
    codeLine: 1,
    description: `Array has ${n} elements`,
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: [],
  });

  for (let i = 0; i < n - 1; i++) {
    steps.push({
      codeLine: 2,
      description: `Pass ${i + 1}: bubble the largest unsorted element to position ${n - 1 - i}`,
      array: [...arr],
      comparing: [],
      swapping: null,
      sorted: [...sorted],
    });

    for (let j = 0; j < n - i - 1; j++) {
      // Compare step
      steps.push({
        codeLine: 4,
        description: `Compare arr[${j}]=${arr[j]} with arr[${j + 1}]=${arr[j + 1]}`,
        array: [...arr],
        comparing: [j, j + 1],
        swapping: null,
        sorted: [...sorted],
      });

      if (arr[j] > arr[j + 1]) {
        // Swap step
        steps.push({
          codeLine: 6,
          description: `${arr[j]} > ${arr[j + 1]} — swap them!`,
          array: [...arr],
          comparing: [],
          swapping: [j, j + 1],
          sorted: [...sorted],
        });

        // Perform the swap
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];

        // Show result after swap
        steps.push({
          codeLine: 8,
          description: `Swapped → arr[${j}]=${arr[j]}, arr[${j + 1}]=${arr[j + 1]}`,
          array: [...arr],
          comparing: [],
          swapping: null,
          sorted: [...sorted],
        });
      } else {
        steps.push({
          codeLine: 9,
          description: `${arr[j]} ≤ ${arr[j + 1]} — no swap needed`,
          array: [...arr],
          comparing: [],
          swapping: null,
          sorted: [...sorted],
        });
      }
    }

    // After each pass, the last element is in its final position
    sorted.push(n - 1 - i);
  }

  // Final element is also sorted
  sorted.push(0);

  steps.push({
    codeLine: 12,
    description: "Array is fully sorted!",
    array: [...arr],
    comparing: [],
    swapping: null,
    sorted: [...sorted],
  });

  return steps;
}
```

## 8.4 Understanding the step generation

The key insight: **we run the actual algorithm, but we RECORD what happens at each interesting moment.**

```
Real bubble sort:              Our version:
compare → swap → compare...    compare → RECORD → swap → RECORD → compare → RECORD...
```

Each `steps.push(...)` captures a snapshot. The algorithm runs to completion in milliseconds — the user replays it at their own pace.

> **Design decision: How many steps per operation?**
>
> We could record EVERY line execution (dozens of steps for the loop counters). Or we could only record the "interesting" moments (comparisons and swaps). We chose a middle ground:
> - Comparisons (so the user sees what's being compared)
> - Swaps (the actual work)
> - Pass boundaries (so the user understands the outer structure)
>
> Too many steps = tedious. Too few = confusing. Adjust based on your audience.

## 8.5 Wire the step engine into the page

Update `app/algorithms/page.tsx`:

```tsx
"use client";

import { useState, useEffect, useMemo } from "react";
import CodePanel from "./components/CodePanel";
import VisualisationPanel from "./components/VisualisationPanel";
import Controls from "./components/Controls";
import RoughBarChart from "./components/RoughBarChart";
import {
  generateBubbleSortSteps,
  BUBBLE_SORT_CODE_JAVA,
} from "./lib/bubbleSort";

const INITIAL_ARRAY = [38, 27, 43, 3, 9, 82, 10];

export default function AlgorithmsPage() {
  const steps = useMemo(
    () => generateBubbleSortSteps(INITIAL_ARRAY),
    []
  );

  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const step = steps[currentStep];

  function handleNext() {
    setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
  }

  function handlePrev() {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }

  function handleReset() {
    setCurrentStep(0);
    setIsPlaying(false);
  }

  function handlePlay() {
    setIsPlaying((prev) => !prev);
  }

  useEffect(() => {
    if (!isPlaying) return;

    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= steps.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 800);

    return () => clearInterval(timer);
  }, [isPlaying, steps.length]);

  return (
    <div className="flex flex-col h-screen p-4 gap-4">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Bubble Sort</h1>
          <p className="text-gray-600">{step.description}</p>
        </div>
        <div className="text-sm text-gray-500">
          Step {currentStep + 1} / {steps.length}
        </div>
      </header>

      <div className="flex flex-1 gap-4 min-h-0">
        <CodePanel
          code={BUBBLE_SORT_CODE_JAVA}
          currentLine={step.codeLine}
          language="java"
        />
        <VisualisationPanel>
          <RoughBarChart
            data={step.array}
            highlightIndices={[...step.comparing, ...step.sorted]}
          />
        </VisualisationPanel>
      </div>

      <Controls
        onPrev={handlePrev}
        onNext={handleNext}
        onPlay={handlePlay}
        onReset={handleReset}
        isPlaying={isPlaying}
      />
    </div>
  );
}
```

## 8.6 Understanding `useMemo`

```tsx
const steps = useMemo(
  () => generateBubbleSortSteps(INITIAL_ARRAY),
  []
);
```

`useMemo` caches the result of an expensive computation. The step generation runs ONCE (on first render) and the result is reused on every subsequent render.

Without `useMemo`, every time you click "Next" (causing a re-render), the entire bubble sort would re-run. With `useMemo`, it only runs when dependencies change (`[]` = never re-run).

> **When to use `useMemo`:** When a computation is expensive AND its inputs don't change between renders. Our step generation is O(n²) — not "expensive" for small arrays, but there's no reason to repeat it.
>
> **When NOT to use it:** Simple calculations like `const total = a + b`. The overhead of memoisation costs more than just recomputing.

## 8.7 Try it out

Visit `/algorithms` and:
1. Click "Next" — see the code highlight move AND the bars update
2. The description tells you what's happening
3. Yellow bars = being compared
4. Click "Play" — auto-advances every 800ms
5. Click "Prev" — goes back to the previous state
6. Click "Reset" — back to the beginning

**This is the complete feedback loop:** code ↔ visualisation ↔ description, all driven by a single `currentStep` number.

## 8.8 The architecture so far

```
generateBubbleSortSteps(input)
        ↓
[step0, step1, step2, ..., stepN]   ← pre-computed, immutable
        ↓
currentStep (state) ← controls (Prev/Next/Play/Reset)
        ↓
steps[currentStep]
        ↓
┌───────────┼───────────────┐
↓           ↓               ↓
CodePanel   RoughBarChart   Description
(codeLine)  (array, highlights)
```

Everything derives from ONE source of truth: `currentStep`. Change that number, and the entire UI updates. This is the power of React's declarative model.

## Summary

✅ You built the step engine — pre-computing all algorithm states  
✅ You defined the `AlgorithmStep` type — the contract between algorithm and UI  
✅ You implemented Bubble Sort step generation  
✅ You connected code highlighting to visualisation state  
✅ You have a fully working Bubble Sort visualiser  

## Key takeaway

**Pre-compute everything, navigate by index.** This is the fundamental architecture of any algorithm visualiser. The algorithm runs once to generate steps. The UI is just a controlled "slideshow" through those steps. This makes Prev/Next/Jump trivial — they're just index changes.

---

→ [Chapter 09: More Sorting Algorithms](./09-MORE-SORTING-ALGORITHMS.md)
