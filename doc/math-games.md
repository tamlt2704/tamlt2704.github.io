# Building Math Games for Kids — Step by Step

---

## What We're Building

Simple, fun math games that run in the browser. No backend needed — perfect for GitHub Pages.

```
┌────────────────────────────────────────┐
│  🧮 Math Games                         │
├────────────────────────────────────────┤
│                                        │
│     What is 7 + 3 ?                    │
│                                        │
│     [  8  ] [  10  ] [  9  ] [  11  ] │
│                                        │
│     ✅ Correct!       Score: 5/7       │
│                                        │
│     ████████████░░░ Level 2            │
│                                        │
└────────────────────────────────────────┘
```

---

## Game Ideas

| Game | Concept | Age |
|------|---------|-----|
| **Addition Quiz** | Pick the right answer from 4 choices | 5-7 |
| **Speed Math** | Answer as many as you can in 60 seconds | 7-10 |
| **Missing Number** | `__ + 3 = 8`, fill in the blank | 6-8 |
| **Times Table** | Multiplication drill with levels | 7-10 |
| **Number Order** | Drag numbers into ascending/descending order | 5-7 |
| **Math Bubbles** | Pop the bubble with the correct answer (timed) | 6-9 |

---

## Step 1: Game State Pattern

Every math game follows this pattern:

```tsx
"use client"

import { useState } from "react"

export default function MathGame() {
  const [score, setScore] = useState(0)
  const [total, setTotal] = useState(0)
  const [gameState, setGameState] = useState<"ready" | "playing" | "finished">("ready")

  // 1. Generate a question
  // 2. Show options
  // 3. Check answer
  // 4. Update score
  // 5. Next question or finish

  return (...)
}
```

**Three game states:**

| State | What the user sees |
|-------|-------------------|
| `ready` | Start screen with instructions |
| `playing` | The actual game — questions + answers |
| `finished` | Score summary, play again button |

---

## Step 2: Addition Quiz (Complete Example)

Create `app/games/addition/page.tsx`:

```tsx
"use client"

import { useState, useCallback } from "react"
import { motion } from "motion/react"

interface Question {
  a: number
  b: number
  answer: number
  options: number[]
}

function generateQuestion(max: number): Question {
  const a = Math.floor(Math.random() * max) + 1
  const b = Math.floor(Math.random() * max) + 1
  const answer = a + b

  // Generate 3 wrong answers near the correct one
  const options = new Set<number>([answer])
  while (options.size < 4) {
    const wrong = answer + Math.floor(Math.random() * 5) - 2
    if (wrong !== answer && wrong > 0) options.add(wrong)
  }

  // Shuffle options
  return {
    a,
    b,
    answer,
    options: [...options].sort(() => Math.random() - 0.5),
  }
}

export default function AdditionGame() {
  const [score, setScore] = useState(0)
  const [round, setRound] = useState(0)
  const [totalRounds] = useState(10)
  const [question, setQuestion] = useState<Question>(() => generateQuestion(10))
  const [feedback, setFeedback] = useState<"correct" | "wrong" | null>(null)
  const [gameState, setGameState] = useState<"ready" | "playing" | "finished">("ready")

  const nextQuestion = useCallback(() => {
    if (round + 1 >= totalRounds) {
      setGameState("finished")
    } else {
      setRound((r) => r + 1)
      setQuestion(generateQuestion(10))
      setFeedback(null)
    }
  }, [round, totalRounds])

  function handleAnswer(choice: number) {
    if (feedback !== null) return // prevent double-click

    if (choice === question.answer) {
      setScore((s) => s + 1)
      setFeedback("correct")
    } else {
      setFeedback("wrong")
    }

    setTimeout(nextQuestion, 1000)
  }

  function startGame() {
    setScore(0)
    setRound(0)
    setQuestion(generateQuestion(10))
    setFeedback(null)
    setGameState("playing")
  }

  // ─── Ready Screen ───
  if (gameState === "ready") {
    return (
      <div className="flex flex-col items-center justify-center gap-6 px-4 py-20">
        <h1 className="text-4xl font-bold text-foreground">🧮 Addition Quiz</h1>
        <p className="text-lg text-muted-foreground">Answer 10 addition questions</p>
        <button
          onClick={startGame}
          className="rounded-lg bg-primary px-8 py-4 text-xl font-bold text-primary-foreground hover:opacity-90"
        >
          Start!
        </button>
      </div>
    )
  }

  // ─── Finished Screen ───
  if (gameState === "finished") {
    const percent = Math.round((score / totalRounds) * 100)
    const emoji = percent >= 80 ? "🌟" : percent >= 50 ? "👍" : "💪"

    return (
      <div className="flex flex-col items-center justify-center gap-6 px-4 py-20">
        <span className="text-6xl">{emoji}</span>
        <h2 className="text-3xl font-bold text-foreground">Game Over!</h2>
        <p className="text-xl text-muted-foreground">
          You scored <span className="font-bold text-foreground">{score}/{totalRounds}</span>
        </p>
        <div className="w-64 rounded-full bg-muted">
          <div
            className="h-4 rounded-full bg-primary transition-all"
            style={{ width: `${percent}%` }}
          />
        </div>
        <button
          onClick={startGame}
          className="rounded-lg bg-primary px-8 py-4 text-xl font-bold text-primary-foreground hover:opacity-90"
        >
          Play Again
        </button>
      </div>
    )
  }

  // ─── Playing Screen ───
  return (
    <div className="flex flex-col items-center justify-center gap-8 px-4 py-20">
      {/* Progress */}
      <div className="flex w-full max-w-md items-center justify-between text-sm text-muted-foreground">
        <span>Question {round + 1}/{totalRounds}</span>
        <span>Score: {score}</span>
      </div>
      <div className="h-2 w-full max-w-md rounded-full bg-muted">
        <div
          className="h-2 rounded-full bg-primary transition-all"
          style={{ width: `${((round + 1) / totalRounds) * 100}%` }}
        />
      </div>

      {/* Question */}
      <motion.div
        key={round}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <p className="text-4xl font-bold text-foreground">
          {question.a} + {question.b} = ?
        </p>
      </motion.div>

      {/* Options */}
      <div className="grid grid-cols-2 gap-4">
        {question.options.map((option) => (
          <motion.button
            key={option}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => handleAnswer(option)}
            className={`rounded-lg border-2 px-8 py-4 text-2xl font-bold transition-colors ${
              feedback === null
                ? "border-border bg-card text-foreground hover:border-primary"
                : option === question.answer
                  ? "border-green-500 bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300"
                  : "border-border bg-card text-muted-foreground opacity-50"
            }`}
          >
            {option}
          </motion.button>
        ))}
      </div>

      {/* Feedback */}
      {feedback && (
        <motion.p
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`text-2xl font-bold ${
            feedback === "correct" ? "text-green-500" : "text-red-500"
          }`}
        >
          {feedback === "correct" ? "✅ Correct!" : `❌ It was ${question.answer}`}
        </motion.p>
      )}
    </div>
  )
}
```

---

## Step 3: Understanding the Key Parts

### Generating Wrong Answers

```tsx
const wrong = answer + Math.floor(Math.random() * 5) - 2
```

Wrong answers are close to the real answer (±2). This makes the game harder — kids can't just pick the biggest number.

### Preventing Double-Click

```tsx
if (feedback !== null) return
```

Once an answer is selected, ignore further clicks until the next question loads.

### Feedback Delay

```tsx
setTimeout(nextQuestion, 1000)
```

Show "Correct!" or "Wrong!" for 1 second before moving on. Gives kids time to see the result.

### Progress Bar

```tsx
style={{ width: `${((round + 1) / totalRounds) * 100}%` }}
```

Visual progress — kids see how far they've come. Motivating.

---

## Step 4: Speed Math (Timer-Based)

A different game type — answer as many as you can before time runs out.

```tsx
"use client"

import { useState, useEffect, useRef } from "react"

export default function SpeedMath() {
  const [score, setScore] = useState(0)
  const [timeLeft, setTimeLeft] = useState(60)
  const [question, setQuestion] = useState(() => generateQuestion(10))
  const [input, setInput] = useState("")
  const [gameState, setGameState] = useState<"ready" | "playing" | "finished">("ready")
  const inputRef = useRef<HTMLInputElement>(null)

  // Countdown timer
  useEffect(() => {
    if (gameState !== "playing") return
    if (timeLeft <= 0) {
      setGameState("finished")
      return
    }

    const timer = setTimeout(() => setTimeLeft((t) => t - 1), 1000)
    return () => clearTimeout(timer)
  }, [timeLeft, gameState])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const answer = parseInt(input)

    if (answer === question.a + question.b) {
      setScore((s) => s + 1)
    }

    setInput("")
    setQuestion(generateQuestion(10))
    inputRef.current?.focus()
  }

  function startGame() {
    setScore(0)
    setTimeLeft(60)
    setInput("")
    setQuestion(generateQuestion(10))
    setGameState("playing")
    setTimeout(() => inputRef.current?.focus(), 100)
  }

  if (gameState === "ready") {
    return (
      <div className="flex flex-col items-center gap-6 py-20">
        <h1 className="text-4xl font-bold">⚡ Speed Math</h1>
        <p className="text-muted-foreground">How many can you solve in 60 seconds?</p>
        <button onClick={startGame} className="rounded-lg bg-primary px-8 py-4 text-xl font-bold text-primary-foreground">
          Go!
        </button>
      </div>
    )
  }

  if (gameState === "finished") {
    return (
      <div className="flex flex-col items-center gap-6 py-20">
        <h2 className="text-3xl font-bold">⏱️ Time's Up!</h2>
        <p className="text-xl text-muted-foreground">You solved <span className="font-bold text-foreground">{score}</span> questions</p>
        <button onClick={startGame} className="rounded-lg bg-primary px-8 py-4 text-xl font-bold text-primary-foreground">
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-8 py-20">
      {/* Timer */}
      <div className="text-5xl font-bold text-foreground">
        {timeLeft}s
      </div>

      {/* Question */}
      <p className="text-3xl font-bold text-foreground">
        {question.a} + {question.b} = ?
      </p>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          ref={inputRef}
          type="number"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-24 rounded-lg border border-border bg-card px-4 py-3 text-center text-2xl font-bold text-foreground"
          autoFocus
        />
        <button type="submit" className="rounded-lg bg-primary px-6 py-3 text-xl font-bold text-primary-foreground">
          →
        </button>
      </form>

      {/* Score */}
      <p className="text-muted-foreground">Score: {score}</p>
    </div>
  )
}
```

---

## Step 5: Difficulty Levels

Make games progressively harder:

```tsx
interface Level {
  name: string
  max: number       // largest number in questions
  operations: string[]
}

const levels: Level[] = [
  { name: "Easy", max: 10, operations: ["+"] },
  { name: "Medium", max: 20, operations: ["+", "-"] },
  { name: "Hard", max: 50, operations: ["+", "-", "×"] },
  { name: "Expert", max: 100, operations: ["+", "-", "×", "÷"] },
]
```

Generate questions based on level:

```tsx
function generateQuestion(level: Level): Question {
  const op = level.operations[Math.floor(Math.random() * level.operations.length)]
  let a = Math.floor(Math.random() * level.max) + 1
  let b = Math.floor(Math.random() * level.max) + 1
  let answer: number

  switch (op) {
    case "+":
      answer = a + b
      break
    case "-":
      // Ensure positive result for kids
      if (b > a) [a, b] = [b, a]
      answer = a - b
      break
    case "×":
      // Keep multiplication tables reasonable
      a = Math.floor(Math.random() * 12) + 1
      b = Math.floor(Math.random() * 12) + 1
      answer = a * b
      break
    case "÷":
      // Ensure clean division (no decimals)
      answer = Math.floor(Math.random() * 12) + 1
      b = Math.floor(Math.random() * 12) + 1
      a = answer * b  // work backwards so it divides evenly
      break
    default:
      answer = a + b
  }

  return { a, b, op, answer, options: generateOptions(answer) }
}
```

**Key design choice:** For subtraction, ensure `a > b` (no negative answers). For division, generate the answer first and work backwards (no decimals).

---

## Step 6: Kid-Friendly UX

### Large Touch Targets

```tsx
// Buttons should be at least 48px tall for small fingers
className="min-h-[48px] min-w-[48px] px-6 py-4 text-xl"
```

### Big, Clear Text

```tsx
// Question text should be very large
className="text-4xl font-bold"

// Options also large
className="text-2xl font-bold"
```

### Positive Reinforcement

```tsx
const encouragements = ["Great job! 🌟", "Amazing! 🎉", "You're a star! ⭐", "Fantastic! 🚀"]
const consolations = ["Almost! 💪", "Keep trying! 🙌", "So close! 👏"]

// Pick random feedback
const msg = feedback === "correct"
  ? encouragements[Math.floor(Math.random() * encouragements.length)]
  : consolations[Math.floor(Math.random() * consolations.length)]
```

### Sound Effects (Optional)

```tsx
function playSound(type: "correct" | "wrong") {
  const audio = new Audio(type === "correct" ? "/sounds/correct.mp3" : "/sounds/wrong.mp3")
  audio.volume = 0.5
  audio.play()
}
```

Put short `.mp3` files in `public/sounds/`.

### No Pressure on Wrong Answers

- Show the correct answer when wrong (learning opportunity)
- Don't use red flashing or scary sounds
- Keep the tone encouraging

---

## Step 7: Animations (Framer Motion)

Make it feel alive for kids:

```tsx
// Question slides in
<motion.div
  key={round}
  initial={{ opacity: 0, x: 50 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: -50 }}
>

// Correct answer bounces
<motion.span
  initial={{ scale: 0 }}
  animate={{ scale: [0, 1.3, 1] }}
  transition={{ duration: 0.4 }}
>
  ✅ Correct!
</motion.span>

// Score pops when updated
<motion.span
  key={score}
  initial={{ scale: 1.5 }}
  animate={{ scale: 1 }}
>
  Score: {score}
</motion.span>

// Buttons wiggle on hover
<motion.button whileHover={{ rotate: [-1, 1, -1, 0] }}>
```

---

## Step 8: Games Index Page

Create `app/games/page.tsx`:

```tsx
import Link from "next/link"

const games = [
  {
    slug: "addition",
    title: "Addition Quiz",
    emoji: "➕",
    description: "Pick the right answer from 4 choices",
    age: "5-7",
    color: "bg-blue-100 dark:bg-blue-950",
  },
  {
    slug: "speed-math",
    title: "Speed Math",
    emoji: "⚡",
    description: "How many can you solve in 60 seconds?",
    age: "7-10",
    color: "bg-yellow-100 dark:bg-yellow-950",
  },
  {
    slug: "times-tables",
    title: "Times Tables",
    emoji: "✖️",
    description: "Practice your multiplication",
    age: "7-10",
    color: "bg-green-100 dark:bg-green-950",
  },
  {
    slug: "missing-number",
    title: "Missing Number",
    emoji: "❓",
    description: "Find the missing number in the equation",
    age: "6-8",
    color: "bg-purple-100 dark:bg-purple-950",
  },
]

export default function GamesPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="mb-2 text-3xl font-bold text-foreground">🧮 Math Games</h1>
      <p className="mb-8 text-muted-foreground">Pick a game and start practising!</p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {games.map((game) => (
          <Link
            key={game.slug}
            href={`/games/${game.slug}`}
            className={`group rounded-xl border border-border p-6 transition-all hover:shadow-lg ${game.color}`}
          >
            <span className="text-4xl">{game.emoji}</span>
            <h2 className="mt-3 text-xl font-bold text-foreground group-hover:text-primary">
              {game.title}
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">{game.description}</p>
            <span className="mt-2 inline-block rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
              Ages {game.age}
            </span>
          </Link>
        ))}
      </div>
    </div>
  )
}
```

---

## Step 9: Storing High Scores (localStorage)

No server needed — save to the browser:

```tsx
function saveHighScore(game: string, score: number) {
  const key = `highscore-${game}`
  const current = parseInt(localStorage.getItem(key) ?? "0")
  if (score > current) {
    localStorage.setItem(key, score.toString())
  }
}

function getHighScore(game: string): number {
  if (typeof window === "undefined") return 0
  return parseInt(localStorage.getItem(`highscore-${game}`) ?? "0")
}
```

Show it on the finished screen:

```tsx
const highScore = getHighScore("addition")
const isNewRecord = score > highScore

{isNewRecord && (
  <p className="text-lg font-bold text-yellow-500">🏆 New High Score!</p>
)}
<p className="text-sm text-muted-foreground">Best: {Math.max(score, highScore)}</p>
```

---

## Project Structure

```
app/
├── games/
│   ├── page.tsx                ← Games index
│   ├── addition/
│   │   └── page.tsx            ← Addition quiz
│   ├── speed-math/
│   │   └── page.tsx            ← Speed math
│   ├── times-tables/
│   │   └── page.tsx            ← Times tables
│   └── missing-number/
│       └── page.tsx            ← Missing number
public/
└── sounds/
    ├── correct.mp3
    └── wrong.mp3
```

---

## UX Checklist for Kids' Games

| ✓ | Principle |
|---|-----------|
| □ | Big buttons (48px+ height) — easy to tap |
| □ | Large text (2xl-4xl) — easy to read |
| □ | High contrast colors — accessible |
| □ | Positive feedback always — never punish wrong answers |
| □ | Show correct answer on miss — it's a learning tool |
| □ | Clear progress indicator — "3 of 10" or progress bar |
| □ | No time pressure for young kids (optional timer for older) |
| □ | Satisfying animations on correct answer |
| □ | Emoji and color — make it feel playful, not like homework |
| □ | Works on tablet — most kids use iPad |
| □ | No login required — just play immediately |
| □ | Difficulty adapts or is selectable |
