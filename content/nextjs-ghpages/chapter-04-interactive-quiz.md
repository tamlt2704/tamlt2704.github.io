# Chapter 4: Your First Interactive Component

[← Chapter 3: Beautiful Code](/blog/nextjs-ghpages/chapter-03-beautiful-code) | [Chapter 5: Code Playground →](/blog/nextjs-ghpages/chapter-05-code-playground)

---

## What We're Building

A quiz that lives inside your markdown. The reader clicks an answer, gets instant feedback:

```
┌─────────────────────────────────────────────────┐
│  What is the time complexity of binary search?  │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ A. O(n)                                 │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │ B. O(log n)                        ← ✓  │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │ C. O(n log n)                           │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │ D. O(1)                                 │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ ✅ Correct!                              │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

Three steps: build the component, register it with MDX, use it in markdown.

---

## Concept: Why "use client"?

Next.js renders pages on the server by default. Server components can't respond to clicks or track state — they produce static HTML.

When a component needs interactivity (clicks, typing, animations), you mark it with `"use client"`. This tells Next.js: "Ship this component's JavaScript to the browser so it can respond to user actions."

Our Quiz needs clicks → it must be a client component.

---

## Concept: What useState Does

`useState` gives a component memory that survives re-renders.

```
const [selected, setSelected] = useState(null)
         │              │                    │
         │              │                    └── initial value
         │              └── function to update it
         └── current value (read this to display)
```

When you call `setSelected(2)`, React re-renders the component with `selected` now equal to `2`. The UI updates automatically.

---

## Step 1: Create the Quiz Component

```tsx
// 📁 app/blog/components/Quiz.tsx — create this file

"use client"; // Enables interactivity (clicks, state)

import { useState } from "react";

interface QuizProps {
  question: string;
  options: string[]; // ["O(n)", "O(log n)", ...]
  answer: number; // Index of correct answer (0-based)
  explanation?: string;
}
```

This is the top of the file: the directive, the import, and the type definition. The `interface` tells TypeScript exactly what props the component accepts — it catches mistakes before runtime.

Now the component body with state:

```tsx
// 📁 app/blog/components/Quiz.tsx — add below the interface

export function Quiz({ question, options, answer, explanation }: QuizProps) {
  // Track which option was clicked (null = not yet answered)
  const [selected, setSelected] = useState<number | null>(null);
  // Lock the quiz after answering so they can't re-click
  const [revealed, setRevealed] = useState(false);

  const handleSelect = (index: number) => {
    if (revealed) return; // Already answered, ignore
    setSelected(index);
    setRevealed(true);
  };
```

Two pieces of state, one handler. That's the entire logic.

Now the render — the question and option buttons:

```tsx
// 📁 app/blog/components/Quiz.tsx — return statement inside Quiz

  return (
    <div className="my-8 rounded-lg border border-gray-200 bg-gray-50 p-6">
      <p className="mb-4 font-semibold text-gray-900">{question}</p>
      <div className="space-y-2">
        {options.map((option, i) => {
          let style = "border-gray-200 bg-white hover:border-teal-400";
          if (revealed && i === answer)
            style = "border-green-500 bg-green-50";
          else if (revealed && i === selected)
            style = "border-red-400 bg-red-50";
          else if (revealed)
            style = "border-gray-200 bg-white opacity-60";
```

Each button gets a different style after the answer is revealed: green for correct, red for wrong pick, faded for the rest.

The button itself and the result message:

```tsx
// 📁 app/blog/components/Quiz.tsx — continue inside the .map()

          return (
            <button
              key={i}
              onClick={() => handleSelect(i)}
              disabled={revealed}
              className={`w-full rounded-md border px-4 py-3 text-left text-sm transition ${style}`}
            >
              <span className="mr-3 font-mono text-gray-400">
                {String.fromCharCode(65 + i)}.
              </span>
              {option}
            </button>
          );
        })}
      </div>
```

`String.fromCharCode(65 + i)` converts 0→"A", 1→"B", 2→"C", 3→"D".

Finally, the result feedback:

```tsx
// 📁 app/blog/components/Quiz.tsx — after the buttons div, before closing </div>

      {revealed && (
        <div className={`mt-4 rounded p-3 text-sm ${
          selected === answer
            ? "bg-green-100 text-green-800"
            : "bg-red-100 text-red-800"
        }`}>
          {selected === answer
            ? "Correct!"
            : `Not quite. The answer is ${String.fromCharCode(65 + answer)}.`}
          {explanation && <p className="mt-1 text-gray-700">{explanation}</p>}
        </div>
      )}
    </div>
  );
}
```

Save. Refresh. Nothing visible yet — we haven't wired it to MDX.

---

## Concept: How MDX Passes Props as Strings

In markdown, you write:

```markdown
<Quiz options='["O(n)", "O(log n)"]' answer="1" />
```

MDX passes `options` as a **string** `'["O(n)", "O(log n)"]'` and `answer` as a **string** `"1"`.

But our component expects `options: string[]` and `answer: number`. We need to parse them. Let's add a wrapper that handles this conversion.

---

## Step 2: Add a Wrapper That Parses String Props

```tsx
// 📁 app/blog/components/QuizMDX.tsx — create this file

"use client";

import { Quiz } from "./Quiz";

// MDX passes all props as strings — this wrapper parses them
export function QuizMDX(props: {
  question: string;
  options: string;
  answer: string;
  explanation?: string;
}) {
  return (
    <Quiz
      question={props.question}
      options={JSON.parse(props.options)} // string → array
      answer={Number(props.answer)} // string → number
      explanation={props.explanation}
    />
  );
}
```

Save. Refresh. Still nothing visible — next step wires it in.

---

## Step 3: Register in MDX Components Map

```tsx
// 📁 app/blog/[...slug]/page.tsx — add import at top

import { QuizMDX } from "@/app/blog/components/QuizMDX";
```

```tsx
// 📁 app/blog/[...slug]/page.tsx — add Quiz to components object

<MDXRemote
  source={content}
  components={{
    code: MarkdownCode,
    pre: MarkdownPre,
    Quiz: QuizMDX, // ← maps <Quiz> in markdown to our component
  }}
  options={{
    mdxOptions: {
      remarkPlugins: [remarkGfm],
      format: "md",
    },
  }}
/>
```

One import, one line in the map. When MDX sees `<Quiz .../>` in markdown, it renders `QuizMDX` with those props.

Save. Refresh. No visible change yet — we need to actually use it in a post.

---

## Step 4: Use It in Markdown

```markdown
<!-- 📁 content/any-post.md — add a quiz anywhere in your post -->

## Quick Check

<Quiz
  question="What is the time complexity of binary search?"
  options='["O(n)", "O(log n)", "O(n log n)", "O(1)"]'
  answer="1"
  explanation="log₂(1024) = 10. Binary search halves the search space each step."
/>
```

Note: `answer="1"` means index 1 (the second option, "O(log n)"). Zero-based.

Save. Refresh. You see a styled quiz card with four clickable options. Click "B. O(log n)" — it turns green and shows "Correct!". Click any other — it turns red and reveals the right answer.

---

## How It All Connects

```
Markdown file          MDX engine              Browser
─────────────          ──────────              ───────
<Quiz                  Looks up "Quiz"         QuizMDX parses
  question="..."  →    in components map   →    string props →  Quiz renders
  options='[...]'      finds QuizMDX            with state       interactive UI
  answer="1"
/>
```

The markdown stays readable. The component handles all interactivity. They compose naturally.

---

## Commit

```bash
git add app/blog/components/Quiz.tsx app/blog/components/QuizMDX.tsx
git commit -m "feat: add interactive Quiz component for MDX"
```

---

## What's Next

A quiz tests recall. But what about experimentation? In Chapter 5, we'll build a **Code Playground** — an editable code block where readers can modify code and see results instantly.
