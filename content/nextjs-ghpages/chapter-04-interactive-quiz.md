# Chapter 4: Your First Interactive Component

[← Chapter 3: Beautiful Code](/blog/nextjs-ghpages/chapter-03-beautiful-code) | [Chapter 5: Code Playground →](/blog/nextjs-ghpages/chapter-05-code-playground)

---

## The Moment It Gets Interesting

Your blog has beautiful markdown rendering. Syntax highlighting. Typography. But the reader is still passive — scrolling, reading, maybe copying a code snippet. There's no feedback loop. No "did I actually understand that?"

What if, after explaining binary search, you could write this in your markdown:

```markdown
## Quick Check

<Quiz
question="What is the time complexity of binary search?"
options={["O(n)", "O(log n)", "O(n log n)", "O(1)"]}
answer={1}
/>
```

And the reader sees a multiple-choice question. They click an answer. Green flash for correct. Red shake for wrong. Instant feedback, right where the concept was explained.

That's what we're building.

## The Quiz Component

The Quiz component needs to be a **client component** (runs in the browser) because it uses `useState` for interactivity. Server components can't handle clicks or state changes.

Create `app/blog/components/Quiz.tsx`:

```bash
touch app/blog/components/Quiz.tsx
```

```tsx
"use client"; // This directive marks it as a client component (runs in browser, not at build time)

import { useState } from "react"; // React hook for managing state that changes over time

// TypeScript interface: defines what props this component accepts
// This acts as documentation AND catches errors if you pass wrong data
interface QuizProps {
  question: string; // The question text
  options: string[]; // Array of answer choices, e.g. ["O(n)", "O(log n)", ...]
  answer: number; // Index of the correct answer (0-based)
  explanation?: string; // Optional explanation shown after answering (? = optional)
}

export function Quiz({ question, options, answer, explanation }: QuizProps) {
  // useState returns [currentValue, setterFunction]
  // selected: which option the user clicked (null = hasn't clicked yet)
  const [selected, setSelected] = useState<number | null>(null);
  // revealed: whether to show the answer (prevents clicking again)
  const [revealed, setRevealed] = useState(false);

  const handleSelect = (index: number) => {
    if (revealed) return; // Already answered — ignore further clicks
    setSelected(index); // Remember which option was clicked
    setRevealed(true); // Lock in the answer, show result
  };

  const isCorrect = selected === answer;

  return (
    // my-8 = vertical margin, p-6 = padding, rounded-lg = rounded corners
    <div className="my-8 rounded-lg border border-gray-200 bg-gray-50 p-6">
      <p className="mb-4 font-semibold text-gray-900">{question}</p>

      {/* space-y-2 = 8px gap between each button */}
      <div className="space-y-2">
        {/* .map() renders one button per option */}
        {options.map((option, i) => {
          // Determine button style based on state
          let style = "border-gray-200 bg-white hover:border-teal-400"; // default
          if (revealed) {
            if (i === answer)
              style = "border-green-500 bg-green-50"; // correct answer: green
            else if (i === selected)
              style = "border-red-400 bg-red-50"; // wrong selection: red
            else style = "border-gray-200 bg-white opacity-60"; // other options: faded
          }

          return (
            <button
              key={i} // React needs unique key for list items
              onClick={() => handleSelect(i)} // When clicked, select this option
              disabled={revealed} // Can't click after answering
              className={`w-full rounded-md border px-4 py-3 text-left text-sm transition ${style}`}
            >
              {/* String.fromCharCode(65) = "A", 66 = "B", etc. */}
              <span className="mr-3 font-mono text-gray-400">{String.fromCharCode(65 + i)}.</span>
              {option}
            </button>
          );
        })}
      </div>

      {/* Only show result after user has answered */}
      {revealed && (
        <div
          className={`mt-4 rounded p-3 text-sm ${isCorrect ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
        >
          {isCorrect ? "Correct!" : `Not quite. The answer is ${String.fromCharCode(65 + answer)}.`}
          {explanation && <p className="mt-1 text-gray-700">{explanation}</p>}
        </div>
      )}
    </div>
  );
}
```

**How the state machine works:**

| State       | `selected` | `revealed` | What user sees                                           |
| ----------- | ---------- | ---------- | -------------------------------------------------------- |
| Initial     | `null`     | `false`    | Question + clickable buttons                             |
| After click | `2` (e.g.) | `true`     | Buttons locked, correct=green, wrong=red, result message |

Two pieces of state, one event handler. That's the entire Quiz logic.

```bash
git add app/blog/components/Quiz.tsx
git commit -m "feat: add Quiz component"
```

## Register It With MDX

Update `app/blog/[...slug]/page.tsx` — add Quiz to the components map:

```tsx
import { Quiz } from "@/app/blog/components/Quiz";

<MDXRemote
  source={content}
  components={{
    code: MarkdownCode,
    pre: MarkdownPre,
    a: ({ href, ...props }) => <a href={href?.replace(/\.md$/, "")} {...props} />,
    Quiz, // ← readers can now use <Quiz /> in markdown
  }}
  options={{
    mdxOptions: {
      remarkPlugins: [remarkGfm],
      format: "md",
    },
  }}
/>;
```

That's the entire wiring. One import, one line in the components object.

```bash
git add app/blog
git commit -m "feat: register Quiz in MDX components map"
```

## Use It in Markdown

Now in any `.md` file:

`````markdown
# Binary Search

Binary search works on sorted arrays. It compares the target to the middle
element and eliminates half the remaining elements each step.

````python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```⁠

<Quiz
  question="If the array has 1024 elements, what's the maximum number of comparisons binary search needs?"
  options={["1024", "512", "10", "32"]}
  answer={2}
  explanation="log₂(1024) = 10. Binary search halves the space each step."
/>
````
`````

````

The reader learns the concept, sees the code, then immediately tests their understanding. The feedback is instant. No scrolling to an answer key.

## How MDX Components Work in Markdown

When `next-mdx-remote` encounters `<Quiz ... />` in a markdown file, it:

1. Recognizes it as a JSX tag (not HTML)
2. Looks up `Quiz` in the `components` map you provided
3. Passes the props (`question`, `options`, `answer`)
4. Renders the React component in place

The markdown file stays readable. The component handles all interactivity. They compose naturally.

## Adding More Components

The pattern is always the same:

1. Create a client component in `app/blog/components/`
2. Add it to the `components` map in your page
3. Use it in any markdown file with JSX syntax

Some ideas:

```markdown
<Callout type="warning">
  Don't forget to handle the empty array case!
</Callout>

<Quiz question="..." options={[...]} answer={0} />

<CodePlayground language="python" initialCode="print('hello')" />

<StepVisualizer steps={[...]} />
```

Each one is a self-contained React component. The markdown is the glue.

---

## Commit Your Progress

```bash
git add .
git commit -m "feat: add Quiz component for interactive markdown"
```

## What's Next

A quiz tests recall. But what about experimentation? In Chapter 5, we'll build a Code Playground — an editable code block where readers can modify the code and see results instantly. The blog becomes a sandbox.
````
