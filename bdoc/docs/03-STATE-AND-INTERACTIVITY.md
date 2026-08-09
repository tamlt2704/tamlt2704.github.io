# Chapter 03: State and Interactivity

## What you'll learn

- What "state" means in React
- How `useState` works
- How buttons trigger state changes
- How the UI automatically updates when state changes

## 3.1 The problem

Right now, `currentLine={3}` is hardcoded. When you click "Next", nothing happens to the UI (we only `console.log`). We need a way to:

1. Store the current line number
2. Change it when buttons are clicked
3. Have the UI update automatically

This is what **state** solves.

## 3.2 State — the core concept

In Java, you'd have a field in a class:

```java
class BubbleSortVisualiser {
    private int currentStep = 0;    // state

    public void next() {
        currentStep++;               // mutation
        render();                    // manual UI update
    }
}
```

In React, state works differently:

```tsx
const [currentStep, setCurrentStep] = useState(0);
//     ↑ value        ↑ setter         ↑ initial value
```

**Critical difference: you never mutate state directly.** You always use the setter:

```tsx
// ❌ WRONG — React won't know anything changed
currentStep = currentStep + 1;

// ✅ CORRECT — React detects the change and re-renders
setCurrentStep(currentStep + 1);
```

> **Why can't you just assign a new value?** React's rendering system watches for `setState` calls. When you call the setter, React knows to re-render the component with the new value. If you just reassign a variable, React has no way to know something changed — the UI stays stale.
>
> **Alternative approach:** Some frameworks (like Vue or Svelte) DO let you assign directly and detect changes automatically (using Proxies or compiler magic). React chose explicit setters for predictability — you always know exactly when a re-render happens.

## 3.3 Add state to the page

Update `app/algorithms/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import CodePanel from "./components/CodePanel";
import VisualisationPanel from "./components/VisualisationPanel";
import Controls from "./components/Controls";

const SAMPLE_CODE = [
  "public void bubbleSort(int[] arr) {",
  "  for (int i = 0; i < arr.length - 1; i++) {",
  "    for (int j = 0; j < arr.length - i - 1; j++) {",
  "      if (arr[j] > arr[j + 1]) {",
  "        int temp = arr[j];",
  "        arr[j] = arr[j + 1];",
  "        arr[j + 1] = temp;",
  "      }",
  "    }",
  "  }",
  "}",
];

export default function AlgorithmsPage() {
  const [currentLine, setCurrentLine] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const totalLines = SAMPLE_CODE.length;

  function handleNext() {
    setCurrentLine((prev) => Math.min(prev + 1, totalLines - 1));
  }

  function handlePrev() {
    setCurrentLine((prev) => Math.max(prev - 1, 0));
  }

  function handleReset() {
    setCurrentLine(0);
    setIsPlaying(false);
  }

  function handlePlay() {
    setIsPlaying((prev) => !prev);
  }

  return (
    <div className="flex flex-col h-screen p-4 gap-4">
      <header>
        <h1 className="text-2xl font-bold">Bubble Sort</h1>
        <p className="text-gray-600">
          Step {currentLine + 1} of {totalLines}
        </p>
      </header>

      <div className="flex flex-1 gap-4 min-h-0">
        <CodePanel code={SAMPLE_CODE} currentLine={currentLine} />
        <VisualisationPanel />
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

**Try it:** Click "Next" — the highlighted line moves down. Click "Prev" — it moves up. "Reset" — back to line 1.

## 3.4 Understanding what happened

Let's trace a single click:

1. User clicks "Next ▶"
2. The `<button onClick={onNext}>` fires → calls `handleNext()`
3. `handleNext` calls `setCurrentLine(prev => Math.min(prev + 1, totalLines - 1))`
4. React sees state changed → re-renders `AlgorithmsPage`
5. The new `currentLine` value flows down as a prop to `<CodePanel />`
6. `CodePanel` re-renders with the new highlighted line

**This is React's data flow:** State changes → component re-renders → new props flow down to children → children re-render.

```
AlgorithmsPage (owns state)
├── CodePanel (receives currentLine as prop)
├── VisualisationPanel (receives nothing yet)
└── Controls (receives handler functions as props)
```

## 3.5 The updater function pattern

Notice this pattern:

```tsx
setCurrentLine((prev) => Math.min(prev + 1, totalLines - 1));
```

Instead of:

```tsx
setCurrentLine(currentLine + 1);
```

**Why use `(prev) => ...` instead of the value directly?**

If you call `setCurrentLine` multiple times quickly (e.g., double-clicking or in rapid succession), React might batch updates. Using the closure value `currentLine` might be stale. The updater function `(prev) => prev + 1` always gets the latest value.

For our use case (clicking one button at a time), both work. But the updater pattern is a good habit — it prevents subtle bugs when things get more complex.

## 3.6 Adding auto-play with `useEffect`

The "Play" button should auto-advance the step every second. This needs a timer — which means we need `useEffect`.

**What is `useEffect`?**

It runs code AFTER the component renders. It's where you put "side effects" — things that happen outside React's rendering (timers, network requests, D3 manipulations).

```tsx
// Mental model:
useEffect(() => {
  // This code runs after every render
  // (or after specific values change — see the dependency array)

  return () => {
    // This cleanup code runs before the next effect or when component unmounts
  };
}, [dependencies]); // Only re-run when these values change
```

Add this to `AlgorithmsPage`, after the handler functions:

```tsx
import { useState, useEffect } from "react";

// ... inside AlgorithmsPage, after handlePlay:

useEffect(() => {
  if (!isPlaying) return;

  const timer = setInterval(() => {
    setCurrentLine((prev) => {
      if (prev >= totalLines - 1) {
        setIsPlaying(false);
        return prev;
      }
      return prev + 1;
    });
  }, 1000);

  return () => clearInterval(timer);
}, [isPlaying, totalLines]);
```

**Breaking it down:**

```tsx
useEffect(() => {        // Run this effect...
  if (!isPlaying) return; // ...only if we're playing

  const timer = setInterval(() => {  // Start a 1-second timer
    setCurrentLine((prev) => {
      if (prev >= totalLines - 1) {  // Reached the end?
        setIsPlaying(false);          // Stop playing
        return prev;                  // Don't advance further
      }
      return prev + 1;               // Advance one line
    });
  }, 1000);

  return () => clearInterval(timer); // CLEANUP: stop the timer
}, [isPlaying, totalLines]);          // Re-run when these change
```

> **Why do we need cleanup?** Without `clearInterval`, old timers keep running when the component re-renders. You'd get multiple timers stacking up, advancing faster and faster. The cleanup function prevents that.
>
> **The dependency array `[isPlaying, totalLines]`:** This tells React "only re-run this effect when `isPlaying` or `totalLines` changes." Without it, the effect runs after EVERY render — creating a new timer each time. With it, it only creates a new timer when play/pause changes.

**Try it:** Click "Play" — lines auto-advance every second. Click "Pause" — stops. Click "Reset" — back to start.

## 3.7 Common mistakes (and why they happen)

| Mistake | What happens | Fix |
|---------|-------------|-----|
| `currentLine++` | TypeScript error — you can't reassign a `const` | Use `setCurrentLine(...)` |
| `setCurrentLine(currentLine + 1)` in a timer | Stale closure — always uses the value when the timer was created | Use `setCurrentLine(prev => prev + 1)` |
| Missing `return () => clearInterval(timer)` | Timer keeps running after component unmounts or re-renders | Always clean up side effects |
| Missing `"use client"` | `useState` doesn't work — error about hooks not being available | Add `"use client"` at the top of the file |
| Empty dependency array `[]` | Effect only runs once — toggling `isPlaying` doesn't start/stop the timer | Include all values the effect reads: `[isPlaying, totalLines]` |

## 3.8 The complete page so far

```tsx
"use client";

import { useState, useEffect } from "react";
import CodePanel from "./components/CodePanel";
import VisualisationPanel from "./components/VisualisationPanel";
import Controls from "./components/Controls";

const SAMPLE_CODE = [
  "public void bubbleSort(int[] arr) {",
  "  for (int i = 0; i < arr.length - 1; i++) {",
  "    for (int j = 0; j < arr.length - i - 1; j++) {",
  "      if (arr[j] > arr[j + 1]) {",
  "        int temp = arr[j];",
  "        arr[j] = arr[j + 1];",
  "        arr[j + 1] = temp;",
  "      }",
  "    }",
  "  }",
  "}",
];

export default function AlgorithmsPage() {
  const [currentLine, setCurrentLine] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const totalLines = SAMPLE_CODE.length;

  function handleNext() {
    setCurrentLine((prev) => Math.min(prev + 1, totalLines - 1));
  }

  function handlePrev() {
    setCurrentLine((prev) => Math.max(prev - 1, 0));
  }

  function handleReset() {
    setCurrentLine(0);
    setIsPlaying(false);
  }

  function handlePlay() {
    setIsPlaying((prev) => !prev);
  }

  useEffect(() => {
    if (!isPlaying) return;

    const timer = setInterval(() => {
      setCurrentLine((prev) => {
        if (prev >= totalLines - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isPlaying, totalLines]);

  return (
    <div className="flex flex-col h-screen p-4 gap-4">
      <header>
        <h1 className="text-2xl font-bold">Bubble Sort</h1>
        <p className="text-gray-600">
          Step {currentLine + 1} of {totalLines}
        </p>
      </header>

      <div className="flex flex-1 gap-4 min-h-0">
        <CodePanel code={SAMPLE_CODE} currentLine={currentLine} />
        <VisualisationPanel />
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

## Summary

✅ You learned `useState` — how React tracks changing values  
✅ You learned the updater pattern `(prev) => ...` for safe state updates  
✅ You learned `useEffect` — how to run side effects (timers, D3, APIs)  
✅ You learned cleanup functions — preventing resource leaks  
✅ You have working Next/Prev/Play/Reset controls  

## Key takeaway

**React re-renders automatically when state changes.** You never manually call "render" — you just update state, and the UI follows. This is the fundamental difference from imperative UI code (jQuery, vanilla DOM manipulation).

---

→ [Chapter 04: Displaying Code with Syntax Highlighting](./04-DISPLAYING-CODE.md)
