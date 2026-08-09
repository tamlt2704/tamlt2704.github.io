# Chapter 02: Your First Component

## What you'll learn

- What a React component is (and why it matters)
- How to split a page into smaller pieces
- How props pass data between components
- How to build the two-panel layout

## 2.1 What is a component?

In Java, you organise code into classes. In Python, into functions and modules. In React, you organise your UI into **components**.

A component is a function that returns a piece of UI:

```tsx
function Greeting() {
  return <h1>Hello, World</h1>;
}
```

That's it. A function that returns JSX (the HTML-like syntax). You can use it like an HTML tag:

```tsx
<Greeting />
```

**Why components matter:**

Our algorithm visualiser has distinct parts — a code panel, a visualisation panel, control buttons. If we write everything in one giant file, it becomes unreadable fast. Components let us build each piece independently, test it independently, and reuse it across different algorithms.

> **The mental model:** Think of components like Java classes that render UI. Each one has its own data (state), receives input (props), and produces output (rendered HTML). The difference: they're functions, not classes.

## 2.2 Create the layout structure

We want this layout:

```
┌──────────────────────────────────────────────┐
│  Header (algorithm name, description)        │
├────────────────────┬─────────────────────────┤
│                    │                         │
│  Code Panel        │  Visualisation Panel    │
│  (left half)       │  (right half)           │
│                    │                         │
├────────────────────┴─────────────────────────┤
│  Controls (Prev, Next, Play, Reset)          │
└──────────────────────────────────────────────┘
```

Let's build this step by step. First, create a folder for our components:

```
app/algorithms/
├── page.tsx
└── components/
    ├── CodePanel.tsx
    ├── VisualisationPanel.tsx
    └── Controls.tsx
```

## 2.3 The CodePanel component

Create `app/algorithms/components/CodePanel.tsx`:

```tsx
type CodePanelProps = {
  code: string[];
  currentLine: number;
};

export default function CodePanel({ code, currentLine }: CodePanelProps) {
  return (
    <div className="flex-1 overflow-auto bg-gray-900 p-4 rounded-lg">
      <pre className="text-sm font-mono">
        {code.map((line, index) => (
          <div
            key={index}
            className={`px-2 py-0.5 ${
              index === currentLine
                ? "bg-yellow-500/20 border-l-2 border-yellow-400"
                : ""
            }`}
          >
            <span className="text-gray-500 mr-4 select-none">
              {String(index + 1).padStart(2, " ")}
            </span>
            <span className="text-gray-100">{line}</span>
          </div>
        ))}
      </pre>
    </div>
  );
}
```

**Let's break this down — every part:**

### The type definition

```tsx
type CodePanelProps = {
  code: string[];        // An array of strings — each string is one line of code
  currentLine: number;   // Which line to highlight (0-indexed)
};
```

This is TypeScript. It says: "When someone uses `<CodePanel />`, they MUST provide `code` (an array of strings) and `currentLine` (a number)." If they forget, TypeScript shows an error immediately — before you even run the app.

> **Why not just use `any`?** You could, but you'd lose all safety. Imagine passing `currentLine="hello"` by accident — without types, it silently breaks at runtime. With types, your editor underlines it in red immediately.

### The props destructuring

```tsx
export default function CodePanel({ code, currentLine }: CodePanelProps) {
```

This is equivalent to:

```tsx
export default function CodePanel(props: CodePanelProps) {
  const code = props.code;
  const currentLine = props.currentLine;
```

Destructuring is just shorthand. Both work — destructuring is the convention in React.

### The rendering

```tsx
{code.map((line, index) => (
  <div key={index} ...>
```

`code.map(...)` is how you render a list in React. It's like a for-each loop:

```java
// Java equivalent:
for (int i = 0; i < code.length; i++) {
    render(code[i], i);
}
```

The `key={index}` tells React how to track items in the list. Without it, React re-renders everything when the list changes (slow). With it, React only updates what actually changed.

> **Why `key`?** React doesn't re-render the entire page every time something changes. It compares the new UI with the old UI and only updates the differences. The `key` helps it match old items with new items. For static lists, using the index is fine. For lists that reorder, you'd use a unique ID.

### The conditional styling

```tsx
className={`px-2 py-0.5 ${
  index === currentLine
    ? "bg-yellow-500/20 border-l-2 border-yellow-400"
    : ""
}`}
```

This is a ternary expression inside a template literal. If this line is the current line, add highlighting classes. Otherwise, add nothing.

**Alternative approach — CSS classes:**

```tsx
// You could also do this with a helper:
function lineClass(index: number, currentLine: number) {
  if (index === currentLine) return "px-2 py-0.5 bg-yellow-500/20 border-l-2 border-yellow-400";
  return "px-2 py-0.5";
}
```

Both work. Inline ternary is shorter for simple cases.

## 2.4 The VisualisationPanel component

Create `app/algorithms/components/VisualisationPanel.tsx`:

```tsx
type VisualisationPanelProps = {
  children?: React.ReactNode;
};

export default function VisualisationPanel({ children }: VisualisationPanelProps) {
  return (
    <div className="flex-1 flex items-center justify-center bg-white border rounded-lg min-h-[400px]">
      {children || (
        <p className="text-gray-400">Visualisation will appear here</p>
      )}
    </div>
  );
}
```

**New concept: `children`**

`children` is a special prop. It means "whatever you put BETWEEN the opening and closing tags":

```tsx
<VisualisationPanel>
  <svg>...</svg>          ← This becomes `children`
</VisualisationPanel>
```

It's like a slot — the parent decides what goes inside. We'll fill it with our D3 visualisation later.

> **Why not pass the SVG as a prop?** You could: `<VisualisationPanel content={<svg>...</svg>} />`. But `children` is the React convention for wrapping content. It reads more naturally — like HTML nesting.

## 2.5 The Controls component

Create `app/algorithms/components/Controls.tsx`:

```tsx
type ControlsProps = {
  onPrev: () => void;
  onNext: () => void;
  onPlay: () => void;
  onReset: () => void;
  isPlaying: boolean;
};

export default function Controls({
  onPrev,
  onNext,
  onPlay,
  onReset,
  isPlaying,
}: ControlsProps) {
  const buttonBase =
    "px-4 py-2 rounded font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";

  return (
    <div className="flex gap-3 justify-center py-4">
      <button
        onClick={onPrev}
        className={`${buttonBase} bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-400`}
      >
        ◀ Prev
      </button>
      <button
        onClick={onNext}
        className={`${buttonBase} bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-400`}
      >
        Next ▶
      </button>
      <button
        onClick={onPlay}
        className={`${buttonBase} ${
          isPlaying
            ? "bg-red-600 hover:bg-red-700 text-white focus:ring-red-400"
            : "bg-green-600 hover:bg-green-700 text-white focus:ring-green-400"
        }`}
      >
        {isPlaying ? "⏸ Pause" : "▶ Play"}
      </button>
      <button
        onClick={onReset}
        className={`${buttonBase} bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-400`}
      >
        ↺ Reset
      </button>
    </div>
  );
}
```

**New concept: function props**

```tsx
onPrev: () => void;   // A function that takes no arguments and returns nothing
```

This means: "Give me a function to call when the user clicks Prev." The component doesn't know what happens — it just calls the function. The parent decides the behaviour.

> **Why pass functions as props?** Separation of concerns. The Controls component handles UI (buttons, styling, click events). The parent handles logic (what "next step" means). This makes Controls reusable — you could use it for any algorithm without changing the component.
>
> **Alternative:** You could put the logic inside Controls itself. But then you'd need a different Controls component for each algorithm. By passing functions, one Controls works for bubble sort, merge sort, BFS — anything.

## 2.6 Wire it all together

Update `app/algorithms/page.tsx`:

```tsx
"use client";

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
  return (
    <div className="flex flex-col h-screen p-4 gap-4">
      {/* Header */}
      <header>
        <h1 className="text-2xl font-bold">Bubble Sort</h1>
        <p className="text-gray-600">
          Repeatedly swap adjacent elements if they are in the wrong order.
        </p>
      </header>

      {/* Main content: code + visualisation */}
      <div className="flex flex-1 gap-4 min-h-0">
        <CodePanel code={SAMPLE_CODE} currentLine={3} />
        <VisualisationPanel />
      </div>

      {/* Controls */}
      <Controls
        onPrev={() => console.log("prev")}
        onNext={() => console.log("next")}
        onPlay={() => console.log("play")}
        onReset={() => console.log("reset")}
        isPlaying={false}
      />
    </div>
  );
}
```

Visit `/algorithms`. You should see:
- Two panels side by side
- Code on the left with line 4 highlighted (index 3)
- A placeholder on the right
- Working buttons at the bottom (check the console — `F12` → Console tab)

## 2.7 Why `"use client"`?

You've seen this at the top of `page.tsx`:

```tsx
"use client";
```

**The short answer:** It tells Next.js "this component runs in the browser, not on the server."

**The longer answer:** Next.js can render pages on the server (faster initial load, better SEO). But server-rendered code can't use browser APIs (clicks, animations, D3, window, document). When your component needs interactivity, you mark it `"use client"`.

**Rule of thumb:**
- Static content (text, images, layouts) → no `"use client"` needed
- Interactive content (buttons, animations, user input) → needs `"use client"`

Our algorithm visualiser is entirely interactive, so the page needs it.

> **Alternative approach:** You could keep the page as a server component and only mark the interactive parts as client components. This is an optimisation for later — for now, one `"use client"` at the page level is simpler to understand.

## Summary

✅ You created three components: CodePanel, VisualisationPanel, Controls  
✅ You learned about props (data flowing from parent to child)  
✅ You learned about `children` (content slot)  
✅ You learned about function props (passing behaviour)  
✅ You built the two-panel layout  
✅ You understand `"use client"`  

## Key takeaway

**Components are functions that return UI. Props are their inputs. Build small, focused components and compose them — just like composing functions or classes.**

---

→ [Chapter 03: State and Interactivity](./03-STATE-AND-INTERACTIVITY.md)
