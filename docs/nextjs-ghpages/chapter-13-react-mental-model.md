# Chapter 13: The React Mental Model

[← Chapter 12: JS Essentials](chapter-12-js-essentials.md) | [Chapter 14: Hooks Deep Dive →](chapter-14-hooks-deep-dive.md)

---

## The One Equation

```
UI = f(state)
```

Your component is a function. State is the input. UI is the output. When state changes, the function runs again. React updates the screen. That's it.

Let's prove it with our Quiz component:

```javascript
function Quiz({ question, options, answer }) {
  const [selected, setSelected] = useState(null);    // state
  const [revealed, setRevealed] = useState(false);   // state

  // This function runs every time state changes:
  return (
    <div>
      <p>{question}</p>
      {options.map((option, i) => (
        <button onClick={() => { setSelected(i); setRevealed(true); }}>
          {option}
        </button>
      ))}
      {revealed && <p>{selected === answer ? "Correct!" : "Wrong"}</p>}
    </div>
  );
}
```

Timeline:
1. First render: `selected = null`, `revealed = false` → shows question + buttons
2. User clicks option B → `setSelected(1)`, `setRevealed(true)`
3. React calls `Quiz` again with new state → shows question + buttons + result
4. React diffs old output vs new output → adds the result `<p>` to the DOM

You never said "insert a paragraph element." You said "if revealed, show this." React figured out the DOM operation.

## Components: Functions, Not Templates

A component is a function that:
- Receives **props** (data from parent)
- May have **state** (data it manages internally)
- Returns **JSX** (description of what to render)

```javascript
//        props ↓
function Button({ label, onClick, variant = "primary" }) {
  //     state ↓
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    await onClick();
    setLoading(false);
  };

  //     JSX ↓
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={handleClick}
      disabled={loading}
    >
      {loading ? "..." : label}
    </button>
  );
}
```

## Props Flow Down, Events Flow Up

```
       App
      /   \
  Sidebar  Content
             |
          Article
             |
           Quiz ← state lives here
```

**Props:** Parent passes data down to children.
**Events:** Children notify parents via callback functions.

```javascript
// Parent passes data DOWN via props
function Article({ content, quizData }) {
  return (
    <div>
      <Markdown source={content} />
      <Quiz {...quizData} onComplete={handleComplete} />
    </div>
  );
}

// Child notifies parent UP via callback
function Quiz({ question, options, answer, onComplete }) {
  const handleSelect = (i) => {
    if (i === answer) {
      onComplete();  // tells parent "quiz completed"
    }
  };
  // ...
}
```

## Re-renders: When and Why

A component re-renders when:
1. **Its state changes** (`setState` called)
2. **Its parent re-renders** (new props might be different)
3. **Its context changes** (shared state updated)

```javascript
function Parent() {
  const [count, setCount] = useState(0);
  
  // Every time count changes, Parent re-renders
  // Which means Child also re-renders (even if its props didn't change)
  return (
    <div>
      <p>{count}</p>
      <button onClick={() => setCount(count + 1)}>+</button>
      <Child name="Ada" />  {/* re-renders even though name didn't change */}
    </div>
  );
}
```

This is usually fine. React is fast. Don't optimize until you measure a problem.

## The Rules of Hooks

Hooks (`useState`, `useEffect`, etc.) have two rules:

**1. Only call at the top level** — never inside if/else, loops, or nested functions:

```javascript
// BAD — conditional hook
function Quiz({ question }) {
  if (!question) return null;
  const [selected, setSelected] = useState(null);  // BREAKS
}

// GOOD — hook before early return
function Quiz({ question }) {
  const [selected, setSelected] = useState(null);
  if (!question) return null;  // early return AFTER hooks
}
```

**2. Only call in React functions** — components or custom hooks, not regular functions:

```javascript
// BAD — hook in regular function
function getCount() {
  const [count, setCount] = useState(0);  // BREAKS
}

// GOOD — hook in component
function Counter() {
  const [count, setCount] = useState(0);  // fine
}

// GOOD — hook in custom hook
function useCounter() {
  const [count, setCount] = useState(0);  // fine
  return { count, increment: () => setCount(c => c + 1) };
}
```

Why? React tracks hooks by their *order* in the component. If you put a hook inside an `if`, the order changes between renders, and React loses track.

## State is Immutable (Treat It That Way)

Never mutate state directly:

```javascript
// BAD — mutating state
const [todos, setTodos] = useState([{ text: "Learn React", done: false }]);
todos[0].done = true;  // WRONG — React won't know it changed
setTodos(todos);       // WRONG — same reference, React skips re-render

// GOOD — create new state
setTodos(todos.map(todo =>
  todo.text === "Learn React" ? { ...todo, done: true } : todo
));
```

The spread operator (`...`) creates a new object/array. React sees a new reference and re-renders.

## Server Components vs Client Components

In Next.js App Router (what we're using):

```javascript
// Server Component (default) — runs at BUILD TIME
// Can read files, access databases, no useState/useEffect
export default async function BlogPage() {
  const content = fs.readFileSync(filePath, "utf-8");  // runs on server
  return <article>{content}</article>;
}

// Client Component — runs in the BROWSER
// Can use hooks, events, browser APIs
"use client";
export function Quiz({ question, options, answer }) {
  const [selected, setSelected] = useState(null);  // needs browser
  return <button onClick={() => setSelected(0)}>...</button>;
}
```

The `"use client"` directive at the top marks a component as client-side. Everything else is server by default.

In our project:
- `app/blog/[...slug]/page.tsx` — **server** (reads markdown files at build time)
- `app/blog/components/Quiz.tsx` — **client** (needs useState for interactivity)
- `app/blog/components/MarkdownCode.tsx` — **client** (needs browser for syntax highlighting)

## The Component Tree in Our Project

```
RootLayout (server)
  ├── ThemeScript (server — inline script)
  ├── Navbar (server or client)
  └── BlogPage (server — reads .md files)
        └── MDXRemote (server — renders markdown)
              ├── MarkdownCode (client — syntax highlighting)
              ├── Quiz (client — interactive)
              ├── CodePlayground (client — interactive)
              └── StepVisualizer (client — interactive)
```

Server components handle the static structure. Client components handle interactivity. They compose naturally.

## Thinking in Components

When you look at a UI, break it into components by asking:

1. **What changes independently?** → separate component with its own state
2. **What repeats?** → component that takes different props
3. **What can be reused?** → generic component (Button, Card, Modal)

Our blog:
- `Quiz` — self-contained state (selected answer)
- `CodePlayground` — self-contained state (code text, output)
- `MarkdownCode` — stateless, just renders props differently based on language
- `ThemeToggle` — global state (dark/light affects everything)

---

## Key Takeaways

1. `UI = f(state)` — components are functions from data to UI
2. Props flow down, events flow up
3. State changes trigger re-renders
4. Hooks must be called at the top level, in order
5. Never mutate state — create new objects/arrays
6. Server components read data, client components handle interaction
7. Break UI into components by what changes independently

## What's Next

Chapter 14 goes deep on hooks — `useState` patterns, `useEffect` for side effects, `useRef` for DOM access, and custom hooks for reusable logic. All demonstrated through improvements to our blog components.
