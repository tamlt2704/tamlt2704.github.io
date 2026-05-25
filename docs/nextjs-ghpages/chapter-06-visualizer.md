# Chapter 6: The Step Visualizer

[← Chapter 5: Code Playground](chapter-05-code-playground.md) | [Chapter 7: Finishing Touches →](chapter-07-finishing-touches.md)

---

## Why Visualize

Some things click only when you _see_ them move. Binary search eliminating half the array. Bubble sort swapping adjacent elements. A tree rotating to stay balanced.

Text explains the _what_. Code shows the _how_. Visualization shows the _why it works_.

## The Component

A step visualizer shows an array (or any data structure) and lets the reader step forward/backward through an algorithm's execution. It's essentially a slideshow where each "slide" is a snapshot of the data at one point in the algorithm.

Create `app/blog/components/StepVisualizer.tsx`:

```tsx
"use client"; // Interactive — user clicks prev/next buttons

import { useState } from "react";

// Each step is a snapshot: the array state, which indices to highlight, and a description
interface Step {
  data: number[]; // The array values at this point in the algorithm
  highlights: number[]; // Which indices are "active" (being compared, swapped, etc.)
  label: string; // Human-readable description: "Compare 5 and 3. Swap!"
}

interface Props {
  steps: Step[]; // The full sequence of steps (provided by the markdown author)
  title?: string; // Optional heading above the visualizer
}

export function StepVisualizer({ steps, title }: Props) {
  // current = which step we're viewing (0 = first step)
  const [current, setCurrent] = useState(0);
  const step = steps[current]; // The data for the current step

  return (
    <div className="my-8 rounded-lg border border-gray-200 bg-white p-5">
      {title && <p className="mb-3 text-sm font-semibold text-gray-700">{title}</p>}

      {/* Array visualization — each number is a box, highlighted ones are teal + scaled up */}
      <div className="mb-4 flex justify-center gap-1">
        {step.data.map((val, i) => (
          <div
            key={i}
            className={`flex h-10 w-10 items-center justify-center rounded border font-mono text-sm transition-all duration-200 ${
              step.highlights.includes(i)
                ? "scale-110 border-teal-500 bg-teal-100 text-teal-900" // Active: teal + bigger
                : "border-gray-200 bg-gray-50 text-gray-700" // Inactive: gray
            }`}
          >
            {val}
          </div>
        ))}
      </div>

      {/* What happened this step — fixed height so layout doesn't jump */}
      <p className="mb-4 h-5 text-center text-sm text-gray-600">{step.label}</p>

      {/* Navigation controls */}
      <div className="flex items-center justify-center gap-3">
        <button
          onClick={() => setCurrent(0)}
          disabled={current === 0}
          className="px-2 py-1 text-xs text-gray-500 hover:text-gray-900 disabled:opacity-30"
        >
          ⏮ Start
        </button>
        <button
          onClick={() => setCurrent(Math.max(0, current - 1))}
          disabled={current === 0}
          className="rounded border px-3 py-1 text-sm hover:bg-gray-50 disabled:opacity-30"
        >
          ← Prev
        </button>
        <span className="w-16 text-center text-xs text-gray-400">
          {current + 1} / {steps.length}
        </span>
        <button
          onClick={() => setCurrent(Math.min(steps.length - 1, current + 1))}
          disabled={current === steps.length - 1}
          className="rounded border px-3 py-1 text-sm hover:bg-gray-50 disabled:opacity-30"
        >
          Next →
        </button>
        <button
          onClick={() => setCurrent(steps.length - 1)}
          disabled={current === steps.length - 1}
          className="px-2 py-1 text-xs text-gray-500 hover:text-gray-900 disabled:opacity-30"
        >
          End ⏭
        </button>
      </div>
    </div>
  );
}
```

## Use It in Markdown

```markdown
## Binary Search: Step by Step

Watch binary search find `7` in a sorted array:

<StepVisualizer
title="Binary Search for 7"
steps={[
{ data: [1, 3, 5, 7, 9, 11, 13], highlights: [3], label: "Start: check middle (index 3) = 7" },
{ data: [1, 3, 5, 7, 9, 11, 13], highlights: [3], label: "Found! 7 === 7. Return index 3." }
]}
/>
```

A more interesting example — searching for `11`:

```markdown
<StepVisualizer
title="Binary Search for 11"
steps={[
{ data: [1, 3, 5, 7, 9, 11, 13], highlights: [0, 1, 2, 3, 4, 5, 6], label: "Full array. lo=0, hi=6" },
{ data: [1, 3, 5, 7, 9, 11, 13], highlights: [3], label: "Check mid=3: arr[3]=7 < 11. Go right." },
{ data: [1, 3, 5, 7, 9, 11, 13], highlights: [4, 5, 6], label: "Search right half. lo=4, hi=6" },
{ data: [1, 3, 5, 7, 9, 11, 13], highlights: [5], label: "Check mid=5: arr[5]=11 === 11. Found!" }
]}
/>
```

The reader clicks through each step. They see the search space shrink. They see _why_ it's O(log n) — not because you told them, but because they watched it happen.

```bash
git add app/blog/components/StepVisualizer.tsx
git commit -m "feat: add StepVisualizer component"
```

## Register It

```tsx
import { StepVisualizer } from "@/app/blog/components/StepVisualizer";

components={{
  code: MarkdownCode,
  pre: MarkdownPre,
  Quiz,
  CodePlayground,
  StepVisualizer,
}}
```

## Composing All Three

The real power is combining components in a single chapter:

`````markdown
# Bubble Sort

Bubble sort repeatedly swaps adjacent elements that are out of order.

````python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
```⁠

## Watch It Work

<StepVisualizer
  title="Bubble Sort: [5, 3, 8, 1, 2]"
  steps={[
    { data: [5, 3, 8, 1, 2], highlights: [0, 1], label: "Compare 5 and 3. Swap!" },
    { data: [3, 5, 8, 1, 2], highlights: [1, 2], label: "Compare 5 and 8. No swap." },
    { data: [3, 5, 8, 1, 2], highlights: [2, 3], label: "Compare 8 and 1. Swap!" },
    { data: [3, 5, 1, 8, 2], highlights: [3, 4], label: "Compare 8 and 2. Swap!" },
    { data: [3, 5, 1, 2, 8], highlights: [4], label: "Pass 1 done. 8 is in place." }
  ]}
/>

## Try It

<CodePlayground
  language="javascript"
  initialCode={`
function bubbleSort(arr) {
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n - 1 - i; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
      }
    }
  }
  return arr;
}

console.log(bubbleSort([5, 3, 8, 1, 2]));
`}
/>

## Check Understanding

<Quiz
  question="What is the worst-case time complexity of bubble sort?"
  options={["O(n)", "O(n log n)", "O(n²)", "O(log n)"]}
  answer={2}
  explanation="Two nested loops over n elements = n × n = O(n²)"
/>
````
`````

````

One chapter. Three interactive elements. The reader:

1. Reads the explanation
2. Watches the algorithm step by step
3. Experiments with the code
4. Tests their understanding

That's a teaching machine, not a blog post.

---

## Commit Your Progress

```bash
git add .
git commit -m "feat: add StepVisualizer component for algorithm walkthroughs"
```

## What's Next

Chapter 7 ties it all together — navigation between chapters, SEO metadata, a landing page that lists all series, and the final deploy. Your interactive learning platform goes live.
````
