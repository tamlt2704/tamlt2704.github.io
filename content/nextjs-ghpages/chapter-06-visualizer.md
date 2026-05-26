# Chapter 6: The Step Visualizer

[← Chapter 5: Code Playground](/blog/nextjs-ghpages/chapter-05-code-playground) | [Chapter 7: Finishing Touches →](/blog/nextjs-ghpages/chapter-07-finishing-touches)

---

## What We're Building

```
┌─────────────────────────────────────────────────┐
│  Binary Search for 7                            │
│                                                 │
│   ┌───┐ ┌───┐ ┌───┐ ┌═══┐ ┌───┐ ┌───┐ ┌───┐  │
│   │ 1 │ │ 3 │ │ 5 │ ║ 7 ║ │ 9 │ │11 │ │13 │  │
│   └───┘ └───┘ └───┘ └═══┘ └───┘ └───┘ └───┘  │
│                       ▲▲▲                       │
│              highlighted element                │
│                                                 │
│   "Check mid=3: arr[3]=7. Found!"              │
│                                                 │
│   [⏮ Start] [← Prev]  2 / 4  [Next →] [End ⏭] │
└─────────────────────────────────────────────────┘
```

The reader clicks Prev/Next to step through an algorithm. Each step shows the array with highlighted elements and a label explaining what happened.

---

## What Is a "Step"?

A step is a snapshot of data at one moment in an algorithm's execution:

- **data** — the array values (e.g. `[1, 3, 5, 7, 9]`)
- **highlights** — which indices are "active" (being compared, swapped, found)
- **label** — a human-readable description ("Compare 5 and 3. Swap!")

The component holds a list of steps and lets the user navigate between them.

---

## Why a JSON String for MDX Props?

MDX cannot handle JSX expressions containing objects inside markdown files. This fails:

```
<StepVisualizer steps={[{ data: [1,2,3], highlights: [0], label: "hi" }]} />
```

MDX's parser chokes on the curly braces and object syntax. The workaround: pass steps as a **JSON string** wrapped in single quotes. The component parses it internally:

```
typeof steps === 'string' ? JSON.parse(steps) : steps
```

This means in your markdown you write:

```
<StepVisualizer steps='[{"data":[1,2,3],"highlights":[0],"label":"hi"}]' />
```

Single quotes around the JSON. The component handles the rest.

---

## Step 1: Create the Component File

```bash
touch app/blog/components/StepVisualizer.tsx
```

---

## Step 2: Define the Interface and Props

```tsx
// 📁 app/blog/components/StepVisualizer.tsx — define types
"use client"; // Interactive — needs useState for navigation

import { useState } from "react";

// Each step = one snapshot of the algorithm
interface Step {
  data: number[];
  highlights: number[];
  label: string;
}

interface Props {
  steps: string | Step[]; // JSON string from MDX, or array directly
  title?: string;
}
```

Save. No visual change yet — we need the component body.

---

## Step 3: Parse Steps and Set Up State

```tsx
// 📁 app/blog/components/StepVisualizer.tsx — component body
export function StepVisualizer({ steps, title }: Props) {
  // Parse JSON string from MDX, or use array directly
  const parsed: Step[] =
    typeof steps === "string" ? JSON.parse(steps) : steps;

  // Track which step the user is viewing
  const [current, setCurrent] = useState(0);
  const step = parsed[current];
```

---

## Step 4: Render the Array Boxes

```tsx
  // 📁 app/blog/components/StepVisualizer.tsx — array display
  return (
    <div className="my-8 rounded-lg border border-gray-200 bg-white p-5">
      {title && <p className="mb-3 text-sm font-semibold">{title}</p>}

      {/* Each number = a box. Highlighted = teal + scaled up */}
      <div className="mb-4 flex justify-center gap-1">
        {step.data.map((val, i) => (
          <div
            key={i}
            className={`flex h-10 w-10 items-center justify-center rounded border font-mono text-sm transition-all ${
              step.highlights.includes(i)
                ? "scale-110 border-teal-500 bg-teal-100"
                : "border-gray-200 bg-gray-50"
            }`}
          >
            {val}
          </div>
        ))}
      </div>
```

---

## Step 5: Add the Label and Navigation Buttons

```tsx
      // 📁 app/blog/components/StepVisualizer.tsx — label + nav
      {/* Description of what happened this step */}
      <p className="mb-4 text-center text-sm text-gray-600">
        {step.label}
      </p>

      {/* Prev/Next navigation */}
      <div className="flex items-center justify-center gap-3">
        <button
          onClick={() => setCurrent(Math.max(0, current - 1))}
          disabled={current === 0}
          className="rounded border px-3 py-1 text-sm disabled:opacity-30"
        >
          ← Prev
        </button>
        <span className="text-xs text-gray-400">
          {current + 1} / {parsed.length}
        </span>
        <button
          onClick={() => setCurrent(Math.min(parsed.length - 1, current + 1))}
          disabled={current === parsed.length - 1}
          className="rounded border px-3 py-1 text-sm disabled:opacity-30"
        >
          Next →
        </button>
      </div>
    </div>
  );
}
```

Save. The component is complete but not yet usable in markdown.

---

## Step 6: Register in MDX

Add `StepVisualizer` to the components map so MDX knows about it.

```tsx
// 📁 app/blog/[series]/[slug]/page.tsx — add to imports
import { StepVisualizer } from "@/app/blog/components/StepVisualizer";
```

```tsx
// 📁 app/blog/[series]/[slug]/page.tsx — add to components map
<MDXRemote
  source={content}
  components={{
    code: MarkdownCode,
    pre: MarkdownPre,
    a: ({ href, ...props }) => <a href={href?.replace(/\.md$/, "")} {...props} />,
    Quiz,
    CodePlayground,
    StepVisualizer, // ← new
  }}
  options={{
    mdxOptions: { remarkPlugins: [remarkGfm], format: "md" },
  }}
/>
```

Save. Refresh. No visible change yet — we haven't used it in any markdown file.

---

## Step 7: Use It in Markdown

Now use the component in a `.md` file. Remember: **JSON string in single quotes**.

```markdown
## Binary Search: Step by Step

<StepVisualizer
  title="Binary Search for 11"
  steps='[
    {"data":[1,3,5,7,9,11,13],"highlights":[0,1,2,3,4,5,6],"label":"Full array. lo=0, hi=6"},
    {"data":[1,3,5,7,9,11,13],"highlights":[3],"label":"Check mid=3: arr[3]=7 < 11. Go right."},
    {"data":[1,3,5,7,9,11,13],"highlights":[4,5,6],"label":"Search right half. lo=4, hi=6"},
    {"data":[1,3,5,7,9,11,13],"highlights":[5],"label":"Check mid=5: arr[5]=11. Found!"}
  ]'
/>
```

Save. Refresh. You see a row of numbered boxes with Prev/Next buttons. Click Next — the highlights move and the label updates. You're watching binary search eliminate half the array each step.

---

## How It All Connects

```
Markdown file                    MDX rendering
─────────────                    ─────────────
<StepVisualizer                  components map finds
  steps='[{"data":...}]'  ──►   StepVisualizer component
/>                               │
                                 ▼
                          JSON.parse(steps)
                                 │
                                 ▼
                          useState(0) tracks current step
                          Prev/Next buttons update state
                          Array boxes re-render with highlights
```

---

## Combining All Three Components

One chapter can use StepVisualizer, CodePlayground, and Quiz together:

```markdown
## Bubble Sort

<StepVisualizer
  title="Bubble Sort: [5, 3, 8, 1, 2]"
  steps='[
    {"data":[5,3,8,1,2],"highlights":[0,1],"label":"Compare 5 and 3. Swap!"},
    {"data":[3,5,8,1,2],"highlights":[1,2],"label":"Compare 5 and 8. No swap."},
    {"data":[3,5,8,1,2],"highlights":[2,3],"label":"Compare 8 and 1. Swap!"},
    {"data":[3,5,1,8,2],"highlights":[3,4],"label":"Compare 8 and 2. Swap!"},
    {"data":[3,5,1,2,8],"highlights":[4],"label":"Pass 1 done. 8 is in place."}
  ]'
/>
```

Save. Refresh. You see the bubble sort animation — each click shows one comparison or swap.

---

## Commit

```bash
git add app/blog/components/StepVisualizer.tsx
git commit -m "feat: add StepVisualizer component"
```

---

## What's Next

Chapter 7 ties it all together — navigation between chapters, SEO metadata, and the final deploy. Your interactive learning platform goes live.
