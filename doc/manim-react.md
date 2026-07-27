# Manim in React — Baby Steps

Recreate 3Blue1Brown-style math animations in React. Each step introduces **one thing** and stays under ~20 lines.

---

## What Manim Does (and Our React Version)

| Manim feature | What it looks like | React tools |
|--------------|-------------------|-------------|
| `Write(text)` | Text appears character by character | Framer Motion + `delay` per char |
| `Create(code)` | Code appears line by line | Shiki + staggered lines |
| `MathTex(...)` | Beautiful math equations | KaTeX |
| `Circle()`, `Arrow()` | SVG shapes | SVG + Framer Motion |
| `Transform(a, b)` | One thing morphs into another | `shiki-magic-move` / `layout` |
| `self.play(a, b, c)` | Sequenced animations | `useAnimate` async chain |
| `self.wait(1)` | Pause between animations | `await sleep(1000)` |
| `FadeIn` / `FadeOut` | Appear / disappear | `AnimatePresence` |

---

## Install Everything

```bash
npm install motion katex shiki react-shiki shiki-magic-move
```

Also add KaTeX CSS. In your layout or global CSS:

```tsx
import 'katex/dist/katex.min.css'
```

---


## Section 1: Text Appearing (Manim's `Write`)

In Manim, `self.play(Write(text))` makes text appear character by character, like someone is typing it.

---

### Step 1.1: Text That Fades In (Simplest)

One thing: text goes from invisible to visible.

```tsx
"use client"

import { motion } from "motion/react"

export function FadeInText({ text }: { text: string }) {
  return (
    <motion.p
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      className="text-2xl text-foreground"
    >
      {text}
    </motion.p>
  )
}
```

**Why `initial`?** The starting state — before the animation. Without it, the text just appears at full opacity instantly.

**Why `duration: 1`?** How long the fade takes in seconds. Manim's default is usually 1 second too.

---

### Step 1.2: Text Appears Character by Character

One thing: split text into characters, delay each one.

```tsx
"use client"

import { motion } from "motion/react"

export function WriteText({ text }: { text: string }) {
  return (
    <p className="text-2xl text-foreground">
      {text.split("").map((char, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: i * 0.05, duration: 0.1 }}
        >
          {char}
        </motion.span>
      ))}
    </p>
  )
}
```

**Why split into characters?** Each character needs its own animation timing. One `<span>` per character → each can have a different `delay`.

**Why `delay: i * 0.05`?** The first char appears at 0s, second at 0.05s, third at 0.1s, etc. The multiplier (0.05) controls typing speed. Smaller = faster typing.

**Why `duration: 0.1`?** How long each character takes to fade in. Short = snappy appear. Long = gentle fade.

---

### Step 1.3: Write Effect with Cursor

One thing: add a blinking cursor that moves with the text.

```tsx
"use client"

import { motion } from "motion/react"

export function WriteWithCursor({ text }: { text: string }) {
  const totalTime = text.length * 0.05

  return (
    <p className="text-2xl text-foreground">
      {text.split("").map((char, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: i * 0.05, duration: 0.1 }}
        >
          {char}
        </motion.span>
      ))}
      <motion.span
        className="inline-block w-[2px] h-6 bg-primary ml-[1px]"
        animate={{ opacity: [1, 0, 1] }}
        transition={{ repeat: Infinity, duration: 0.8 }}
      />
    </p>
  )
}
```

**Why `animate={{ opacity: [1, 0, 1] }}`?** A keyframe array — blink on, off, on. Combined with `repeat: Infinity`, it blinks forever.

**Why `repeat: Infinity`?** Without it, the animation plays once and stops. `Infinity` means it loops forever — that's what makes a cursor blink.

---

### Step 1.4: Trigger on Demand (Not on Mount)

One thing: text only starts writing when you tell it to.

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export function WriteOnClick({ text }: { text: string }) {
  const [show, setShow] = useState(false)

  return (
    <div>
      {show && (
        <p className="text-2xl text-foreground">
          {text.split("").map((char, i) => (
            <motion.span
              key={i}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.05, duration: 0.1 }}
            >
              {char}
            </motion.span>
          ))}
        </p>
      )}
      <button onClick={() => setShow(true)}
        className="mt-4 rounded bg-primary px-4 py-2 text-primary-foreground">
        Play
      </button>
    </div>
  )
}
```

**Why conditional rendering `{show && ...}`?** `initial` + `animate` fire when the component mounts. By not rendering it until `show` is true, we control when the animation starts.

---


## Section 2: Code Display (Manim's `Create(Code(...))`)

In Manim, code appears line by line with syntax highlighting. We use Shiki for highlighting and Framer Motion for the reveal.

---

### Step 2.1: Static Code Block (No Animation)

One thing: display syntax-highlighted code.

```tsx
"use client"

import { useShikiHighlighter } from 'react-shiki'

export function CodeBlock({ code, lang = "python" }: { code: string; lang?: string }) {
  const highlighter = useShikiHighlighter({ themes: ['github-dark'], langs: [lang] })
  const html = highlighter?.codeToHtml(code, { lang, theme: 'github-dark' }) ?? ''

  return (
    <div
      className="rounded-lg p-4 text-sm"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
```

**Why Shiki?** It uses the same grammar as VS Code — exact same colors and token detection. Prism is simpler but less accurate.

**Why `dangerouslySetInnerHTML`?** Shiki outputs HTML strings (with `<span>` tags for each colored token). React needs this escape hatch to render raw HTML.

---

### Step 2.2: Lines Appear One by One

One thing: split code into lines, stagger their appearance.

```tsx
"use client"

import { motion } from "motion/react"

export function CodeReveal({ code }: { code: string }) {
  const lines = code.split("\n")

  return (
    <pre className="rounded-lg bg-zinc-900 p-4 text-sm font-mono text-zinc-100">
      {lines.map((line, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.4, duration: 0.3 }}
        >
          {line || " "}
        </motion.div>
      ))}
    </pre>
  )
}
```

**Why `delay: i * 0.4`?** Each line waits 0.4s longer than the previous. Line 0 at 0s, line 1 at 0.4s, line 2 at 0.8s. This creates the line-by-line reveal.

**Why `x: -10` → `x: 0`?** Lines slide in from slightly left. Small movement + fade = polished feel. Just `opacity` alone feels flat.

**Why `{line || " "}`?** Empty lines (`""`) collapse in HTML. A space keeps the line height.

---

### Step 2.3: Highlight the Current Line

One thing: one line is highlighted (yellow background), moves down as lines appear.

```tsx
"use client"

import { useState, useEffect } from "react"
import { motion } from "motion/react"

export function CodeWalkthrough({ code }: { code: string }) {
  const lines = code.split("\n")
  const [activeLine, setActiveLine] = useState(0)

  useEffect(() => {
    if (activeLine >= lines.length) return
    const timer = setTimeout(() => setActiveLine(a => a + 1), 800)
    return () => clearTimeout(timer)
  }, [activeLine, lines.length])

  return (
    <pre className="rounded-lg bg-zinc-900 p-4 text-sm font-mono">
      {lines.map((line, i) => (
        <motion.div
          key={i}
          className={i === activeLine ? "bg-yellow-400/20 text-zinc-100" : "text-zinc-400"}
          animate={{ opacity: i <= activeLine ? 1 : 0.2 }}
          transition={{ duration: 0.3 }}
        >
          {line || " "}
        </motion.div>
      ))}
    </pre>
  )
}
```

**Why `activeLine` state?** Tracks which line the "cursor" is on. Lines above it are visible, the current one is highlighted, lines below are dimmed.

**Why `bg-yellow-400/20`?** The `/20` is Tailwind opacity — 20% yellow background. Just enough to see without overwhelming the code.

**Why `opacity: i <= activeLine ? 1 : 0.2`?** Lines that haven't been reached yet are nearly invisible. They "appear" as the active line reaches them.

---

### Step 2.4: Code Morph (One Version → Another)

One thing: code smoothly transforms from version A to version B (like manim's `TransformMatchingShapes`).

```bash
npm install shiki-magic-move
```

```tsx
"use client"

import { ShikiMagicMove } from 'shiki-magic-move/react'
import { useState } from "react"
import { getHighlighter } from 'shiki'

const codeVersions = [
  `def greet():\n    print("hello")`,
  `def greet(name):\n    print(f"hello {name}")`,
  `def greet(name: str) -> None:\n    message = f"hello {name}"\n    print(message)`,
]

export function CodeMorph() {
  const [step, setStep] = useState(0)

  return (
    <div>
      <ShikiMagicMove
        code={codeVersions[step]}
        lang="python"
        theme="github-dark"
      />
      <button onClick={() => setStep(s => (s + 1) % codeVersions.length)}>
        Next Version →
      </button>
    </div>
  )
}
```

**Why `shiki-magic-move`?** It diffs the tokens between two code versions and animates each token to its new position. Deleted tokens fade out, new tokens fade in, moved tokens glide. You get manim's `TransformMatchingShapes` for free.

**Why `(s + 1) % codeVersions.length`?** Cycles through versions: 0 → 1 → 2 → 0 → ... The `%` (modulo) wraps around.

---


## Section 3: LaTeX Math (Manim's `MathTex`)

In Manim, `MathTex(r"\int_0^1 x^2 dx")` renders beautiful math. We use KaTeX — same result, runs in the browser.

---

### Step 3.1: Render One Equation (Static)

One thing: turn LaTeX string into rendered math.

```tsx
import katex from 'katex'
import 'katex/dist/katex.min.css'

export function Math({ tex }: { tex: string }) {
  const html = katex.renderToString(tex, { throwOnError: false })
  return <span dangerouslySetInnerHTML={{ __html: html }} />
}
```

Usage:

```tsx
<Math tex="E = mc^2" />
<Math tex="\int_0^1 x^2 \, dx = \frac{1}{3}" />
<Math tex="\sum_{i=1}^{n} i = \frac{n(n+1)}{2}" />
```

**Why `throwOnError: false`?** If you make a typo in the LaTeX, KaTeX won't crash your app — it shows an error inline instead.

**Why a separate component?** You'll use `<Math>` everywhere. One component, reuse it in every scene.

---

### Step 3.2: Equation That Fades In

One thing: wrap the Math component with Framer Motion.

```tsx
import { motion } from "motion/react"

export function FadeInMath({ tex }: { tex: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
    >
      <Math tex={tex} />
    </motion.div>
  )
}
```

**Why `scale: 0.8` → `1`?** The equation grows slightly as it appears — like it's "coming toward you." Manim does this too. Just opacity alone feels flat.

---

### Step 3.3: Equation Steps (One After Another)

One thing: show a derivation step by step, each equation appearing below the last.

```tsx
"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"

const steps = [
  "x^2 + 5x + 6 = 0",
  "(x + 2)(x + 3) = 0",
  "x = -2 \\quad \\text{or} \\quad x = -3",
]

export function MathDerivation() {
  const [visibleCount, setVisibleCount] = useState(1)

  return (
    <div className="flex flex-col items-center gap-4">
      {steps.slice(0, visibleCount).map((tex, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-xl"
        >
          <Math tex={tex} />
        </motion.div>
      ))}

      <button
        onClick={() => setVisibleCount(c => Math.min(c + 1, steps.length))}
        disabled={visibleCount >= steps.length}
        className="rounded bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
      >
        Next Step →
      </button>
    </div>
  )
}
```

**Why `steps.slice(0, visibleCount)`?** Shows only the first N equations. Each click increases N by 1, revealing the next step. Previous steps stay visible.

**Why `y: 20` → `y: 0`?** Each new equation slides up into position. Combined with fade = smooth entry from below.

---

### Step 3.4: Highlight Part of an Equation

One thing: use KaTeX color commands to emphasize parts.

```tsx
const steps = [
  "x^2 + 5x + 6 = 0",
  "\\colorbox{yellow}{$(x + 2)$}(x + 3) = 0",
  "x = \\textcolor{red}{-2} \\quad \\text{or} \\quad x = \\textcolor{red}{-3}",
]
```

**Why KaTeX color commands?** No extra library needed. `\textcolor{red}{...}` colors text, `\colorbox{yellow}{...}` adds background. This is how Manim highlights equation parts too.

Common KaTeX color commands:

| Command | What it does |
|---------|-------------|
| `\textcolor{red}{x}` | Red text |
| `\colorbox{yellow}{$x$}` | Yellow background |
| `\boxed{x = 5}` | Box around the answer |
| `\underbrace{x+y}_{sum}` | Brace below with label |

---

### Step 3.5: Inline Math with Text

One thing: mix regular text and math in the same sentence.

```tsx
export function MathParagraph() {
  return (
    <p className="text-lg text-foreground">
      The quadratic formula{" "}
      <Math tex="x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}" />{" "}
      gives us the roots of any quadratic equation.
    </p>
  )
}
```

**Why `{" "}`?** React strips whitespace between JSX elements. The `{" "}` forces a space before and after the math. Without it, the equation jams against the text.

---


## Section 4: Shapes (Manim's `Circle`, `Arrow`, `Line`)

In Manim, you create shapes and animate them onto the scene. In React, we use SVG + Framer Motion.

---

### Step 4.1: Draw a Circle

One thing: an SVG circle that animates in.

```tsx
"use client"

import { motion } from "motion/react"

export function AnimatedCircle() {
  return (
    <svg width={200} height={200}>
      <motion.circle
        cx={100} cy={100} r={60}
        fill="none"
        stroke="hsl(var(--primary))"
        strokeWidth={3}
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1.5, ease: "easeInOut" }}
      />
    </svg>
  )
}
```

**Why `pathLength`?** This is the magic prop for "drawing" shapes. `0` = nothing drawn, `1` = fully drawn. Framer Motion animates between them, so the circle appears to draw itself.

**Why `fill="none"`?** We want just the outline (stroke), not a filled disc. This matches manim's `Create(Circle())` which draws the perimeter.

**Why `ease: "easeInOut"`?** Starts slow, speeds up in the middle, slows at the end. Feels natural — like a pen speeding up and slowing down.

---

### Step 4.2: Draw a Line

One thing: a line that draws from point A to point B.

```tsx
export function AnimatedLine() {
  return (
    <svg width={400} height={100}>
      <motion.line
        x1={50} y1={50} x2={350} y2={50}
        stroke="hsl(var(--primary))"
        strokeWidth={2}
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.8 }}
      />
    </svg>
  )
}
```

Same `pathLength` trick — works on any SVG shape (`circle`, `line`, `path`, `rect`).

---

### Step 4.3: Draw an Arrow

One thing: a line with a triangle at the end.

```tsx
export function AnimatedArrow() {
  return (
    <svg width={400} height={100}>
      {/* Arrow marker definition */}
      <defs>
        <marker id="arrowhead" markerWidth={10} markerHeight={7}
          refX={10} refY={3.5} orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="hsl(var(--primary))" />
        </marker>
      </defs>

      <motion.line
        x1={50} y1={50} x2={340} y2={50}
        stroke="hsl(var(--primary))"
        strokeWidth={2}
        markerEnd="url(#arrowhead)"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.8 }}
      />
    </svg>
  )
}
```

**Why `<defs>` + `<marker>`?** SVG's way of defining reusable decorations. The `marker` is a triangle shape, and `markerEnd` attaches it to the end of the line. You define it once, reuse on any line.

**Why `orient="auto"`?** The arrowhead rotates to match the line's direction. Without this, diagonal lines would have a sideways arrowhead.

---

### Step 4.4: Arrow Pointing at Something

One thing: an arrow from a label to a specific position (like manim's annotation arrows).

```tsx
export function AnnotationArrow({ from, to, label }: {
  from: { x: number; y: number }
  to: { x: number; y: number }
  label: string
}) {
  return (
    <svg className="absolute inset-0 pointer-events-none" width="100%" height="100%">
      <defs>
        <marker id="arrow" markerWidth={8} markerHeight={6}
          refX={8} refY={3} orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#facc15" />
        </marker>
      </defs>

      <motion.line
        x1={from.x} y1={from.y} x2={to.x} y2={to.y}
        stroke="#facc15" strokeWidth={2}
        markerEnd="url(#arrow)"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay: 0.5, duration: 0.6 }}
      />

      <motion.text x={from.x} y={from.y - 10}
        fill="#facc15" fontSize={14}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.1 }}
      >
        {label}
      </motion.text>
    </svg>
  )
}
```

**Why `pointer-events-none`?** The SVG overlays your content. Without this, it would block clicks on elements underneath.

**Why `delay: 0.5` on the line, `delay: 1.1` on the text?** The arrow draws first (0.5s to start, 0.6s duration = finishes at 1.1s), then the label appears. Sequencing without a timeline — just math.

---

### Step 4.5: Shape That Fills In (Create → Fill)

One thing: draw the outline first, then fill it with color.

```tsx
export function DrawThenFill() {
  return (
    <svg width={200} height={200}>
      <motion.circle
        cx={100} cy={100} r={60}
        stroke="hsl(var(--primary))"
        strokeWidth={3}
        initial={{ pathLength: 0, fill: "transparent" }}
        animate={{ pathLength: 1, fill: "hsl(var(--primary) / 0.2)" }}
        transition={{
          pathLength: { duration: 1.5 },
          fill: { delay: 1.5, duration: 0.5 },
        }}
      />
    </svg>
  )
}
```

**Why separate transition timings?** `pathLength` takes 1.5s. `fill` starts at 1.5s (after drawing finishes) and takes 0.5s. You can give each property its own timing by using an object in `transition`.

**Why `hsl(var(--primary) / 0.2)`?** 20% opacity fill — tinted but see-through. Same pattern manim uses when filling shapes.

---


## Section 5: Transforms (Manim's `Transform`, `ReplacementTransform`)

In Manim, `Transform(a, b)` morphs one object into another. The key idea: the old thing smoothly becomes the new thing.

---

### Step 5.1: Fade Cross-Dissolve (Simplest Transform)

One thing: old content fades out, new content fades in.

```tsx
"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"

export function CrossDissolve() {
  const [step, setStep] = useState(0)
  const items = ["Hello", "World", "!"]

  return (
    <div>
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
          className="text-4xl font-bold"
        >
          {items[step]}
        </motion.div>
      </AnimatePresence>
      <button onClick={() => setStep(s => (s + 1) % items.length)}>Next</button>
    </div>
  )
}
```

**Why `AnimatePresence`?** Normal React removes elements instantly. `AnimatePresence` gives elements time to play their `exit` animation before being removed from the DOM.

**Why `mode="wait"`?** The old element fully exits (fades out) BEFORE the new one enters (fades in). Without it, they overlap — both visible during the transition.

**Why `key={step}`?** React uses `key` to know when an element is "new." When `step` changes, React sees a different key → removes old → mounts new. `AnimatePresence` intercepts this to animate the removal.

---

### Step 5.2: Slide Transform (Old Slides Out, New Slides In)

One thing: content slides left/right like a slideshow.

```tsx
<AnimatePresence mode="wait">
  <motion.div
    key={step}
    initial={{ opacity: 0, x: 50 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -50 }}
    transition={{ duration: 0.3 }}
  >
    {items[step]}
  </motion.div>
</AnimatePresence>
```

**Why `x: 50` on enter, `x: -50` on exit?** New content enters from the right (+50), old content leaves to the left (-50). Creates the feeling of moving forward through content.

---

### Step 5.3: Math Equation Transform

One thing: one equation morphs into another (like manim's `TransformMatchingTex`).

```tsx
"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"

const equations = [
  "ax^2 + bx + c = 0",
  "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
  "x = \\frac{-5 \\pm \\sqrt{25 - 24}}{2}",
  "x = \\frac{-5 \\pm 1}{2}",
  "x = -2 \\quad \\text{or} \\quad x = -3",
]

export function MathTransform() {
  const [step, setStep] = useState(0)

  return (
    <div className="flex flex-col items-center gap-6">
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 1.1 }}
          transition={{ duration: 0.4 }}
        >
          <Math tex={equations[step]} />
        </motion.div>
      </AnimatePresence>

      <button onClick={() => setStep(s => Math.min(s + 1, equations.length - 1))}>
        Next Step →
      </button>
    </div>
  )
}
```

**Why `scale: 0.9` on enter, `scale: 1.1` on exit?** The old equation slightly grows (zooms out = "moving away"), the new one slightly shrinks in (zooms in = "arriving"). Subtle but gives depth.

**Note:** This isn't a true token morph (where individual symbols slide to new positions). For that, you'd need a custom diffing algorithm. The cross-dissolve with scale is 90% as good and much simpler.

---

### Step 5.4: Layout Transform (Element Moves Position)

One thing: the same element smoothly moves when its position changes.

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export function MovingBox() {
  const [position, setPosition] = useState<"left" | "center" | "right">("left")

  const xMap = { left: 0, center: 150, right: 300 }

  return (
    <div>
      <motion.div
        className="h-16 w-16 rounded-lg bg-primary"
        animate={{ x: xMap[position] }}
        transition={{ type: "spring", stiffness: 200, damping: 20 }}
      />
      <div className="mt-4 flex gap-2">
        <button onClick={() => setPosition("left")}>Left</button>
        <button onClick={() => setPosition("center")}>Center</button>
        <button onClick={() => setPosition("right")}>Right</button>
      </div>
    </div>
  )
}
```

**Why no `AnimatePresence` here?** The element isn't being removed — it's the SAME element moving. Just change `animate` and Motion handles the transition.

**When to use which:**
- Same element, different properties → `animate` (Step 5.4)
- Different elements swapping → `AnimatePresence` + `key` (Steps 5.1–5.3)

---

### Step 5.5: Shape Morph (Circle → Square)

One thing: animate `borderRadius` to morph shapes.

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export function ShapeMorph() {
  const [isCircle, setIsCircle] = useState(true)

  return (
    <motion.div
      className="h-24 w-24 bg-primary cursor-pointer"
      animate={{
        borderRadius: isCircle ? "50%" : "12px",
        rotate: isCircle ? 0 : 45,
      }}
      transition={{ duration: 0.5 }}
      onClick={() => setIsCircle(!isCircle)}
    />
  )
}
```

**Why `borderRadius`?** `50%` makes a square into a circle. `12px` makes it a rounded square. Animating between them = shape morph.

**Why add `rotate: 45`?** Gives the transform more visual interest — the square rotates as it morphs. Remove it for a pure circle↔square morph.

---


## Section 6: Scene Sequencing (Manim's `self.play` + `self.wait`)

In Manim, a scene is a sequence: play animation A, wait 1 second, play animation B. This is the "timeline." Motion doesn't have a built-in timeline, but we can build one.

---

### Step 6.1: Step-Based Scenes (Simplest Timeline)

One thing: a step counter drives what's visible. Already seen this — formalise it.

```tsx
"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "motion/react"

export function Scene() {
  const [step, setStep] = useState(0)

  return (
    <div className="relative h-[300px] w-[500px]">
      {step >= 0 && (
        <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className="text-3xl font-bold">
          The Pythagorean Theorem
        </motion.h1>
      )}
      {step >= 1 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}>
          <Math tex="a^2 + b^2 = c^2" />
        </motion.div>
      )}
      {step >= 2 && (
        <motion.p initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="text-muted-foreground">
          Where c is the hypotenuse.
        </motion.p>
      )}

      <button onClick={() => setStep(s => s + 1)} className="absolute bottom-0">
        Next →
      </button>
    </div>
  )
}
```

**Why `step >= N` not `step === N`?** Elements stay visible once revealed. `>=` means "show from step N onwards." `===` would hide it when you advance past it.

**This is the foundation.** Every manim scene is just: "at step N, show thing X." The rest is polish.

---

### Step 6.2: Auto-Playing Scene (Timed Steps)

One thing: steps advance automatically with delays.

```tsx
"use client"

import { useState, useEffect } from "react"

const TIMINGS = [0, 1000, 2500, 4000]  // ms when each step fires

export function AutoScene() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const timers = TIMINGS.map((ms, i) =>
      setTimeout(() => setStep(i), ms)
    )
    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div>
      {step >= 0 && <FadeIn>Title appears immediately</FadeIn>}
      {step >= 1 && <FadeIn>First point at 1s</FadeIn>}
      {step >= 2 && <FadeIn>Second point at 2.5s</FadeIn>}
      {step >= 3 && <FadeIn>Third point at 4s</FadeIn>}
    </div>
  )
}

function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      {children}
    </motion.div>
  )
}
```

**Why an array of timings?** Each entry says "at this millisecond, fire this step." You can control exact timing without chaining delays. Easy to adjust — just change the numbers.

**Why schedule all timers at once?** They all start from mount time. Timer at 2500ms fires 2.5 seconds after the component appears — regardless of when previous steps fire.

---

### Step 6.3: `useAnimate` for Imperative Sequences

One thing: chain animations in order with `await`.

```tsx
"use client"

import { useAnimate } from "motion/react"

export function ImperativeScene() {
  const [scope, animate] = useAnimate()

  async function play() {
    // Step 1: title appears
    await animate(".title", { opacity: 1 }, { duration: 0.5 })

    // Step 2: wait
    await new Promise(r => setTimeout(r, 500))

    // Step 3: equation appears
    await animate(".equation", { opacity: 1, y: 0 }, { duration: 0.5 })

    // Step 4: underline draws
    await animate(".underline", { scaleX: 1 }, { duration: 0.4 })
  }

  return (
    <div ref={scope}>
      <h1 className="title opacity-0">The Title</h1>
      <div className="equation opacity-0 translate-y-4">
        <Math tex="E = mc^2" />
      </div>
      <div className="underline origin-left scale-x-0 h-[2px] bg-primary" />
      <button onClick={play}>▶ Play</button>
    </div>
  )
}
```

**Why `useAnimate`?** It's Framer Motion's imperative API — you control exactly what happens and when. `await animate(...)` means "wait for this animation to finish, then do the next thing."

**Why CSS classes for initial state (`opacity-0`)?** With `useAnimate`, you don't use `initial` prop. The elements start with their CSS state, and `animate()` drives them to the target.

**Why `ref={scope}`?** `animate(".title", ...)` uses CSS selectors to find elements. The `scope` limits the search to this container — won't accidentally animate elements elsewhere on the page.

---

### Step 6.4: Reusable `wait` Helper

One thing: make pauses cleaner.

```tsx
const wait = (ms: number) => new Promise(r => setTimeout(r, ms))

async function play() {
  await animate(".title", { opacity: 1 }, { duration: 0.5 })
  await wait(500)
  await animate(".equation", { opacity: 1 }, { duration: 0.5 })
  await wait(300)
  await animate(".arrow", { pathLength: 1 }, { duration: 0.8 })
}
```

**Why a helper?** `new Promise(r => setTimeout(r, ms))` is ugly to read. `wait(500)` is exactly like manim's `self.wait(0.5)`.

---

### Step 6.5: Play / Pause / Reset Controls

One thing: control playback like a video.

```tsx
"use client"

import { useState, useRef } from "react"
import { useAnimate } from "motion/react"

export function ControllableScene() {
  const [scope, animate] = useAnimate()
  const [playing, setPlaying] = useState(false)
  const abortRef = useRef<AbortController>()

  async function play() {
    abortRef.current = new AbortController()
    setPlaying(true)

    try {
      await animate(".step1", { opacity: 1 }, { duration: 0.5 })
      await wait(500)
      await animate(".step2", { opacity: 1 }, { duration: 0.5 })
      await wait(500)
      await animate(".step3", { opacity: 1 }, { duration: 0.5 })
    } finally {
      setPlaying(false)
    }
  }

  function reset() {
    animate(".step1, .step2, .step3", { opacity: 0 }, { duration: 0 })
    setPlaying(false)
  }

  return (
    <div ref={scope}>
      <p className="step1 opacity-0">First thing</p>
      <p className="step2 opacity-0">Second thing</p>
      <p className="step3 opacity-0">Third thing</p>
      <div className="flex gap-2 mt-4">
        <button onClick={play} disabled={playing}>▶ Play</button>
        <button onClick={reset}>↺ Reset</button>
      </div>
    </div>
  )
}
```

**Why `duration: 0` on reset?** Instantly snap everything back to hidden — no animation. This is your "rewind to start."

**Why `disabled={playing}`?** Prevents double-clicking play and running two sequences simultaneously.

---


## Section 7: Putting It All Together

Now you have all the pieces. A manim-style scene combines:

- Text appearing (Section 1)
- Code revealing (Section 2)
- Math equations (Section 3)
- Shapes drawing (Section 4)
- Transforms between states (Section 5)
- Timed sequencing (Section 6)

---

### Full Example: Explaining a Function

```tsx
"use client"

import { useAnimate } from "motion/react"
import { motion } from "motion/react"

const wait = (ms: number) => new Promise(r => setTimeout(r, ms))

export function ExplainFunction() {
  const [scope, animate] = useAnimate()

  async function play() {
    // Scene 1: Title writes in
    await animate(".title", { opacity: 1 }, { duration: 0.5 })
    await wait(800)

    // Scene 2: Code appears line by line
    await animate(".code-line-1", { opacity: 1, x: 0 }, { duration: 0.3 })
    await wait(200)
    await animate(".code-line-2", { opacity: 1, x: 0 }, { duration: 0.3 })
    await wait(200)
    await animate(".code-line-3", { opacity: 1, x: 0 }, { duration: 0.3 })
    await wait(600)

    // Scene 3: Arrow points to the return value
    await animate(".arrow", { pathLength: 1 }, { duration: 0.6 })
    await wait(300)

    // Scene 4: Math equation fades in
    await animate(".equation", { opacity: 1, scale: 1 }, { duration: 0.5 })
    await wait(500)

    // Scene 5: Explanation text
    await animate(".explanation", { opacity: 1, y: 0 }, { duration: 0.4 })
  }

  function reset() {
    animate("*", { opacity: 0 }, { duration: 0 })
    animate(".code-line-1, .code-line-2, .code-line-3", { x: -10 }, { duration: 0 })
    animate(".equation", { scale: 0.9 }, { duration: 0 })
    animate(".explanation", { y: 10 }, { duration: 0 })
    animate(".arrow", { pathLength: 0 }, { duration: 0 })
  }

  return (
    <div ref={scope} className="relative p-8">
      <h2 className="title opacity-0 text-2xl font-bold mb-4">
        How factorial works
      </h2>

      <pre className="bg-zinc-900 rounded-lg p-4 font-mono text-sm text-zinc-100 mb-4">
        <div className="code-line-1 opacity-0 -translate-x-2">def fact(n):</div>
        <div className="code-line-2 opacity-0 -translate-x-2">    if n == 0: return 1</div>
        <div className="code-line-3 opacity-0 -translate-x-2">    return n * fact(n-1)</div>
      </pre>

      <div className="equation opacity-0 scale-90 text-xl mb-4">
        <Math tex="n! = n \times (n-1) \times \cdots \times 1" />
      </div>

      <p className="explanation opacity-0 translate-y-2 text-muted-foreground">
        Each call multiplies n by the result of fact(n-1), until it hits the base case.
      </p>

      <div className="flex gap-2 mt-6">
        <button onClick={play} className="rounded bg-primary px-4 py-2 text-primary-foreground">
          ▶ Play
        </button>
        <button onClick={reset} className="rounded bg-secondary px-4 py-2 text-secondary-foreground">
          ↺ Reset
        </button>
      </div>
    </div>
  )
}
```

**The pattern:** Each `await animate(...)` is one "beat" in the scene. `wait()` adds pause between beats. Reset snaps everything back instantly.

---

## Cheat Sheet: Manim → React

| Manim | React |
|-------|-------|
| `self.play(Write(text))` | Char-by-char with `delay: i * 0.05` |
| `self.play(Create(circle))` | `pathLength: 0 → 1` on SVG |
| `self.play(FadeIn(obj))` | `initial={{ opacity: 0 }} animate={{ opacity: 1 }}` |
| `self.play(FadeOut(obj))` | `AnimatePresence` + `exit={{ opacity: 0 }}` |
| `self.play(Transform(a, b))` | `AnimatePresence mode="wait"` + `key` change |
| `self.play(TransformMatchingShapes)` | `shiki-magic-move` for code |
| `self.wait(1)` | `await wait(1000)` |
| `MathTex(r"...")` | `<Math tex="..." />` with KaTeX |
| `Code(...)` | Shiki + line-by-line reveal |
| `Arrow()` | SVG `<line>` + `<marker>` |
| `obj.animate.shift(RIGHT)` | `animate={{ x: 100 }}` |
| `obj.animate.scale(2)` | `animate={{ scale: 2 }}` |
| `obj.animate.set_color(RED)` | `animate={{ color: "red" }}` |

---

## Project Ideas (Ordered by Difficulty)

| # | Project | Sections used |
|---|---------|--------------|
| 1 | **Explain a sorting algorithm** — code + bars + step narration | 2, 6 |
| 2 | **Quadratic formula derivation** — equations transform step by step | 3, 5, 6 |
| 3 | **Pythagorean theorem proof** — shapes + equations + labels | 3, 4, 6 |
| 4 | **Recursion visualiser** — code highlight + call stack growing | 2, 4, 6 |
| 5 | **Big-O explained** — graph drawing + equations + narration | 3, 4, 6 |
| 6 | **Linear algebra basics** — matrices + vector arrows + transforms | 3, 4, 5 |
| 7 | **Full lesson: Binary Search** — code, math, visualisation, narration | 1–6 |

---

## When You Outgrow This

| Need | Tool |
|------|------|
| Scrubbing (drag timeline back/forth) | GSAP timeline |
| Export to video (MP4) | Remotion (React → video) |
| 3D animations | React Three Fiber |
| Actual Manim (Python, full power) | `manim` CLI + render |
| Collaborative editing | Motion Canvas (TypeScript manim-like) |

For interactive web content (blog posts, explainers, teaching tools), the React approach in this tutorial is ideal. For pre-rendered videos, consider [Remotion](https://www.remotion.dev/) or actual Manim.


## Section 8: Rate Functions / Easing (Manim's `rate_func`)

In Manim, `rate_func` controls HOW the animation progresses. Does it start slow? End fast? Bounce? In Framer Motion, this is the `ease` or `type` in `transition`.

---

### Step 8.1: What Easing Does

Same animation, different easing — feels completely different:

```tsx
"use client"

import { motion } from "motion/react"

const easings = ["linear", "easeIn", "easeOut", "easeInOut"] as const

export function EasingDemo() {
  return (
    <div className="flex flex-col gap-4">
      {easings.map((ease) => (
        <div key={ease} className="flex items-center gap-4">
          <span className="w-24 text-xs text-muted-foreground">{ease}</span>
          <motion.div
            className="h-8 w-8 rounded bg-primary"
            animate={{ x: [0, 250, 0] }}
            transition={{ duration: 2, ease, repeat: Infinity }}
          />
        </div>
      ))}
    </div>
  )
}
```

**Why `animate={{ x: [0, 250, 0] }}`?** Keyframes — move right then back. Combined with `repeat: Infinity`, it loops forever so you can compare the easings.

**Why `repeat: Infinity`?** The animation plays once and stops by default. `Infinity` = loops forever. Use a number for specific count: `repeat: 3` = play 4 times total (1 initial + 3 repeats).

---

### Step 8.2: Manim Easing → Framer Motion Easing

| Manim `rate_func` | Framer Motion `ease` | Feels like |
|-------------------|---------------------|-----------|
| `smooth` (default) | `"easeInOut"` | Slow start, fast middle, slow end |
| `linear` | `"linear"` | Constant speed |
| `rush_into` | `"easeIn"` | Slow start, fast finish |
| `rush_from` | `"easeOut"` | Fast start, slow finish |
| `there_and_back` | `x: [0, 250, 0]` keyframes | Goes there and returns |
| `wiggle` | Custom spring with low damping | Bouncy oscillation |

---

### Step 8.3: Spring Physics (Manim Doesn't Have This!)

Framer Motion has something manim doesn't — springs. They feel more natural than easing curves.

```tsx
<motion.div
  animate={{ x: 200 }}
  transition={{ type: "spring", stiffness: 100, damping: 10 }}
/>
```

| Parameter | What it does | Low value | High value |
|-----------|-------------|-----------|-----------|
| `stiffness` | How fast it reaches target | Slow, floaty | Snappy, fast |
| `damping` | How fast bouncing stops | Bounces many times | Barely bounces |
| `mass` | How heavy the object feels | Light, responsive | Heavy, sluggish |

**When to use which:**
- `ease` = predictable, exact timing (good for sequenced scenes)
- `spring` = natural, physics-based (good for UI interactions)

---

### Step 8.4: Custom Cubic Bezier (Fine Control)

One thing: define your own curve — exactly like CSS `cubic-bezier()`.

```tsx
<motion.div
  animate={{ x: 200 }}
  transition={{ duration: 1, ease: [0.17, 0.67, 0.83, 0.67] }}
/>
```

**Why 4 numbers?** They're the control points of a bezier curve. `[0, 0, 1, 1]` = linear. Use [cubic-bezier.com](https://cubic-bezier.com) to design your own visually.

---

### Step 8.5: Different Easing Per Property

One thing: the position moves with spring, but opacity fades linearly.

```tsx
<motion.div
  initial={{ opacity: 0, x: -100 }}
  animate={{ opacity: 1, x: 0 }}
  transition={{
    x: { type: "spring", stiffness: 200, damping: 20 },
    opacity: { duration: 0.3, ease: "linear" },
  }}
/>
```

**Why different easings?** Opacity looks best with a simple fade (linear). Position looks best with a spring (natural). Manim does this with `rate_func` per animation in `self.play()`. We do it with per-property transitions.

---


## Section 9: Updaters (Manim's `add_updater` + `ValueTracker`)

In Manim, updaters are functions that run every frame — keeping things in sync. "The brace always follows the line." "The label always shows the current value." In React, we do this with derived state and `useMotionValue`.

---

### Step 9.1: One Thing Follows Another (Simplest Updater)

One thing: a label always stays next to a moving dot.

```tsx
"use client"

import { motion, useMotionValue, useTransform } from "motion/react"

export function FollowingLabel() {
  const x = useMotionValue(0)
  const labelX = useTransform(x, (v) => v + 30)

  return (
    <div className="relative h-[100px]">
      <motion.div
        className="absolute top-10 h-6 w-6 rounded-full bg-primary cursor-grab"
        drag="x"
        style={{ x }}
        dragConstraints={{ left: 0, right: 300 }}
      />
      <motion.span
        className="absolute top-12 text-sm text-muted-foreground"
        style={{ x: labelX }}
      >
        ← drag me
      </motion.span>
    </div>
  )
}
```

**Why `useMotionValue`?** A special animated value that doesn't trigger re-renders. It updates 60fps silently — React never knows. This is how you get smooth animations without performance issues.

**Why `useTransform(x, fn)`?** Creates a new motion value that's always derived from `x`. When `x` changes, `labelX` = `x + 30` automatically. This IS the updater pattern — "label is always 30px right of the dot."

---

### Step 9.2: Display a Live Value (Manim's `DecimalNumber`)

One thing: show the current numeric value as it changes.

```tsx
"use client"

import { motion, useMotionValue, useTransform, useSpring } from "motion/react"

export function LiveValue() {
  const x = useMotionValue(0)
  const display = useTransform(x, (v) => Math.round(v))

  return (
    <div className="flex flex-col items-center gap-4">
      <motion.div
        className="h-8 w-8 rounded-full bg-primary cursor-grab"
        drag="x"
        style={{ x }}
        dragConstraints={{ left: -150, right: 150 }}
      />
      <motion.span className="text-2xl font-mono">
        {display}
      </motion.span>
    </div>
  )
}
```

**Wait — `{display}` won't work directly.** `useTransform` returns a MotionValue, not a React state. To render it as text, you need `useMotionValueEvent` or a small wrapper:

```tsx
import { useMotionValueEvent } from "motion/react"
import { useState } from "react"

const [displayText, setDisplayText] = useState(0)
useMotionValueEvent(x, "change", (v) => setDisplayText(Math.round(v)))

<span className="text-2xl font-mono">{displayText}</span>
```

**Why two approaches?** `useTransform` is for driving other animations (no re-render). `useMotionValueEvent` is for updating React state (causes re-render). Use the first for visual stuff, the second for text display.

---

### Step 9.3: ValueTracker Pattern (Animate a Number Over Time)

In Manim, `ValueTracker` animates a number from A to B, and updaters react to it. In React:

```tsx
"use client"

import { useSpring, useTransform, motion } from "motion/react"

export function ValueTrackerDemo() {
  const progress = useSpring(0, { stiffness: 50, damping: 20 })
  const x = useTransform(progress, [0, 1], [0, 300])
  const color = useTransform(progress, [0, 0.5, 1], ["#3b82f6", "#facc15", "#22c55e"])

  return (
    <div>
      <motion.div
        className="h-10 w-10 rounded-full"
        style={{ x, backgroundColor: color }}
      />
      <button onClick={() => progress.set(1)}>Animate to end</button>
      <button onClick={() => progress.set(0)}>Reset</button>
    </div>
  )
}
```

**Why `useSpring(0)`?** Creates an animated value starting at 0 — our ValueTracker. Calling `.set(1)` animates it to 1 with spring physics.

**Why `useTransform(progress, [0, 1], [0, 300])`?** Maps the progress (0→1) to a pixel position (0→300). This is like manim's `n2p()` — number to position.

**Why map to color too?** One ValueTracker can drive multiple things simultaneously. As progress goes 0→0.5→1, color goes blue→yellow→green. All in sync, all from one source value.

---

### Step 9.4: Slider-Driven Animation (Interactive ValueTracker)

One thing: a range slider drives the animation — user controls the progress.

```tsx
"use client"

import { useState } from "react"
import { motion } from "motion/react"

export function SliderScene() {
  const [t, setT] = useState(0)

  const x = t * 300
  const radius = 20 + t * 40
  const rotation = t * 360

  return (
    <div className="flex flex-col items-center gap-6">
      <svg width={400} height={100}>
        <motion.circle
          cx={50 + x} cy={50} r={radius}
          fill="hsl(var(--primary))"
          animate={{ rotate: rotation }}
          transition={{ duration: 0 }}
        />
      </svg>

      <input type="range" min={0} max={1} step={0.01}
        value={t}
        onChange={(e) => setT(Number(e.target.value))}
        className="w-64"
      />
      <span className="text-sm text-muted-foreground">t = {t.toFixed(2)}</span>
    </div>
  )
}
```

**Why `transition={{ duration: 0 }}`?** The slider gives instant values — we don't want animation lag. `duration: 0` means "jump to this value immediately."

**Why derive everything from `t`?** One variable drives everything — position, size, rotation. This is the updater concept: `t` is the ValueTracker, everything else is derived. Drag the slider = scrub through the animation.

---


## Section 10: Graphs and Axes (Manim's `Axes` + `plot`)

In Manim, you create axes and plot functions on them. In React, we use SVG with calculated points.

---

### Step 10.1: Draw Axes

One thing: an x-axis and y-axis with tick marks.

```tsx
"use client"

export function Axes({ width = 400, height = 300 }: { width?: number; height?: number }) {
  const cx = width / 2   // center x
  const cy = height / 2  // center y

  return (
    <svg width={width} height={height} className="border rounded-lg bg-card">
      {/* X axis */}
      <line x1={20} y1={cy} x2={width - 20} y2={cy}
        stroke="grey" strokeWidth={1} />
      {/* Y axis */}
      <line x1={cx} y1={20} x2={cx} y2={height - 20}
        stroke="grey" strokeWidth={1} />
      {/* Arrowheads */}
      <polygon points={`${width-20},${cy} ${width-28},${cy-4} ${width-28},${cy+4}`}
        fill="grey" />
      <polygon points={`${cx},20 ${cx-4},28 ${cx+4},28`}
        fill="grey" />
    </svg>
  )
}
```

**Why center at `width/2, height/2`?** SVG coordinates start top-left. We want (0,0) at the center, like manim's coordinate system.

---

### Step 10.2: Plot a Function

One thing: convert `f(x)` into SVG points and draw a path.

```tsx
function plotFunction(
  f: (x: number) => number,
  xMin: number, xMax: number,
  cx: number, cy: number,
  scaleX: number, scaleY: number,
  steps = 100
): string {
  const points: string[] = []
  for (let i = 0; i <= steps; i++) {
    const x = xMin + (xMax - xMin) * (i / steps)
    const px = cx + x * scaleX
    const py = cy - f(x) * scaleY  // SVG y is flipped
    points.push(`${px},${py}`)
  }
  return `M ${points.join(" L ")}`
}
```

**Why `cy - f(x) * scaleY`?** SVG y-axis goes DOWN (0 is top). Math y-axis goes UP. Subtracting flips it so positive y goes up.

**Why return a path string?** SVG `<path d="M ... L ...">` draws a line through all the points. `M` = move to start, `L` = line to next point.

Usage:

```tsx
const d = plotFunction(Math.sin, -Math.PI * 2, Math.PI * 2, 200, 150, 30, 50)

<path d={d} fill="none" stroke="hsl(var(--primary))" strokeWidth={2} />
```

---

### Step 10.3: Animate the Plot Drawing

One thing: the function line draws itself (like manim's `Create`).

```tsx
import { motion } from "motion/react"

<motion.path
  d={d}
  fill="none"
  stroke="hsl(var(--primary))"
  strokeWidth={2}
  initial={{ pathLength: 0 }}
  animate={{ pathLength: 1 }}
  transition={{ duration: 2, ease: "easeInOut" }}
/>
```

Same `pathLength` trick from Section 4 — works on any SVG path, including function plots.

---

### Step 10.4: Animate Along a Curve (Dot Traces the Function)

One thing: a dot moves along f(x) as it draws.

```tsx
"use client"

import { useState, useEffect } from "react"

export function TracingDot() {
  const [t, setT] = useState(0)  // 0 to 1

  useEffect(() => {
    const timer = setInterval(() => {
      setT(prev => {
        if (prev >= 1) return 1
        return prev + 0.005
      })
    }, 16)
    return () => clearInterval(timer)
  }, [])

  const x = -Math.PI * 2 + t * Math.PI * 4  // map t to x range
  const px = 200 + x * 30                    // screen position
  const py = 150 - Math.sin(x) * 50          // screen position (flipped)

  return (
    <svg width={400} height={300}>
      {/* ... axes and path ... */}
      <circle cx={px} cy={py} r={6} fill="#facc15" />
    </svg>
  )
}
```

**Why `t * Math.PI * 4`?** `t` goes from 0 to 1. We map it to the full x-range of our plot (-2π to 2π = 4π total). So `t=0.5` means the dot is at x=0 (middle of the range).

---

## Section 11: Groups (Manim's `VGroup`)

In Manim, `VGroup` lets you animate multiple objects as one. In React, we use parent containers with `variants`.

---

### Step 11.1: Stagger Children (Group Fade-In)

One thing: children appear one after another automatically.

```tsx
"use client"

import { motion } from "motion/react"

const container = {
  animate: {
    transition: { staggerChildren: 0.2 },
  },
}

const child = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
}

export function StaggerGroup() {
  return (
    <motion.div variants={container} initial="initial" animate="animate"
      className="flex gap-3">
      {[1, 2, 3, 4, 5].map((i) => (
        <motion.div key={i} variants={child}
          className="h-12 w-12 rounded-lg bg-primary" />
      ))}
    </motion.div>
  )
}
```

**Why `variants`?** They let parent and children share animation state names (`"initial"`, `"animate"`). The parent controls timing (stagger), children define what happens.

**Why `staggerChildren: 0.2`?** Each child starts 0.2s after the previous. Child 1 at 0s, child 2 at 0.2s, child 3 at 0.4s, etc. This is manim's `.arrange()` + sequential `FadeIn`.

---

### Step 11.2: Animate Group as One (Move All Together)

One thing: move the parent → all children move with it.

```tsx
export function GroupMove() {
  const [moved, setMoved] = useState(false)

  return (
    <motion.div
      animate={{ x: moved ? 200 : 0, rotate: moved ? 15 : 0 }}
      transition={{ type: "spring", stiffness: 200 }}
      className="flex gap-2"
      onClick={() => setMoved(!moved)}
    >
      <div className="h-10 w-10 rounded bg-red-500" />
      <div className="h-10 w-10 rounded bg-blue-500" />
      <div className="h-10 w-10 rounded bg-green-500" />
    </motion.div>
  )
}
```

**Why animate the parent?** Children are inside — they move with it. Same as manim's `VGroup.shift()` or `VGroup.animate.rotate()`. One animation moves the whole group.

---

### Step 11.3: Animate Children Independently Within a Group

One thing: each child does its own animation, parent controls when.

```tsx
const container = {
  initial: {},
  animate: {
    transition: { staggerChildren: 0.15, delayChildren: 0.5 },
  },
}

const item = {
  initial: { scale: 0, rotate: -180 },
  animate: { scale: 1, rotate: 0 },
}

export function IndependentChildren() {
  return (
    <motion.div variants={container} initial="initial" animate="animate"
      className="flex gap-3">
      {["🔴", "🟡", "🟢", "🔵", "🟣"].map((emoji, i) => (
        <motion.div key={i} variants={item}
          transition={{ type: "spring", stiffness: 300 }}
          className="text-3xl">
          {emoji}
        </motion.div>
      ))}
    </motion.div>
  )
}
```

**Why `delayChildren: 0.5`?** Waits 0.5s before any child starts. Useful when the group title appears first, then children stagger in after.

**Why `scale: 0` + `rotate: -180`?** Each child spins in from nothing. Combined with the stagger = cascading spin-in effect. Very manim-like.

---


## Summary: All Manim Concepts Covered

| # | Manim concept | Our React section | Key tool |
|---|--------------|-------------------|----------|
| 1 | `Write(text)` | Section 1: Text | Char-by-char delay |
| 2 | `Create(Code(...))` | Section 2: Code | Shiki + stagger |
| 3 | `MathTex(...)` | Section 3: LaTeX | KaTeX |
| 4 | `Circle`, `Arrow`, `Line` | Section 4: Shapes | SVG + `pathLength` |
| 5 | `Transform`, `FadeTransform` | Section 5: Transforms | `AnimatePresence` |
| 6 | `self.play` + `self.wait` | Section 6: Sequencing | `useAnimate` + async |
| 7 | `rate_func` | Section 8: Easing | `ease` / `spring` / bezier |
| 8 | `add_updater`, `ValueTracker` | Section 9: Updaters | `useMotionValue` + `useTransform` |
| 9 | `Axes` + `plot` | Section 10: Graphs | SVG `<path>` + math |
| 10 | `VGroup` | Section 11: Groups | `variants` + `staggerChildren` |

---

## What's NOT Covered (and Alternatives)

| Manim feature | Why not covered | Alternative |
|--------------|----------------|-------------|
| 3D (`ThreeDAxes`, surfaces) | Needs WebGL | React Three Fiber (separate tutorial) |
| Camera movement | Web doesn't have a camera | CSS transforms on a wrapper div |
| SVG morphing (complex shapes) | Needs path interpolation | `flubber` library or GSAP MorphSVG |
| Video export | Web is interactive, not video | Remotion (React → MP4) |
| Sounds | Out of scope | Web Audio API |
| `Mobject.animate.shift(RIGHT)` | Already covered | `animate={{ x: 100 }}` |
| Layers / z-index | CSS handles this | `z-index` + `relative`/`absolute` |
