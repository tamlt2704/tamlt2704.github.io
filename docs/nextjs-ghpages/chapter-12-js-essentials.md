# Chapter 12: JavaScript You Actually Need

[← Chapter 11: Performance](chapter-11-performance.md) | [Chapter 13: React Mental Model →](chapter-13-react-mental-model.md)

---

## Why This Chapter Exists

You've been copying code from previous chapters. It works. But when something breaks, you stare at it. What does `...` do? Why is there a `=>` everywhere? What's `?.` doing?

This chapter covers the JavaScript you'll encounter daily in this project — not a textbook, but the patterns that appear in every file you've written so far.

## Destructuring: Unpacking Data

You've seen this in every component:

```javascript
// Instead of:
function Quiz(props) {
  const question = props.question;
  const options = props.options;
  const answer = props.answer;
}

// You write:
function Quiz({ question, options, answer }) {
  // question, options, answer are ready to use
}
```

It works with arrays too — that's what `useState` returns:

```javascript
const [count, setCount] = useState(0);
//     ↑ first item    ↑ second item
```

Nested destructuring (from our markdown pipeline):

```javascript
const { content, data } = matter(raw);
// Pulls `content` and `data` out of the object returned by matter()
```

## Spread & Rest: The Three Dots

**Spread** — expands an array or object:

```javascript
// Copy an array with modifications
const chapters = ["ch1", "ch2", "ch3"];
const withNew = [...chapters, "ch4"];  // ["ch1", "ch2", "ch3", "ch4"]

// Copy an object with overrides
const defaults = { theme: "light", fontSize: 14 };
const userPrefs = { ...defaults, theme: "dark" };  // { theme: "dark", fontSize: 14 }
```

You used this in the Quiz component — spreading styles:

```javascript
const style = { ...baseStyle, ...(isActive ? activeStyle : {}) };
```

**Rest** — collects remaining items:

```javascript
function Button({ children, className, ...rest }) {
  // `rest` contains all other props (onClick, disabled, etc.)
  return <button className={className} {...rest}>{children}</button>;
}
```

This pattern is everywhere in React — forward unknown props to the underlying element.

## Arrow Functions & Implicit Return

```javascript
// Multi-line: needs braces + return
const processChapter = (raw) => {
  const { content, data } = matter(raw);
  return { content, meta: data };
};

// Single expression: implicit return (no braces, no return keyword)
const double = (x) => x * 2;
const getSlug = (file) => file.replace(".md", "");

// Returning an object? Wrap in parentheses:
const makePost = (title) => ({ title, date: Date.now() });
```

In our project, you see implicit returns in `.map()` and `.filter()`:

```javascript
const chapters = files
  .filter((f) => f.endsWith(".md"))   // keep only .md files
  .map((f) => f.replace(".md", ""));  // strip extension
```

## Template Literals: String Building

```javascript
// Old way (concatenation):
const url = "/blog/" + series + "/" + slug;

// Modern way (template literal):
const url = `/blog/${series}/${slug}`;
```

Backticks (`` ` ``) allow `${}` expressions inside strings. You've used these for:

```javascript
// Dynamic class names
className={`px-3 py-2 ${isActive ? "bg-teal-50" : "text-gray-600"}`}

// Dynamic paths
const filePath = path.join(process.cwd(), `content/${series}/${fileSlug}.md`);
```

## Optional Chaining: Safe Property Access

```javascript
// Without optional chaining — crashes if user is null
const name = user.profile.name;

// With optional chaining — returns undefined instead of crashing
const name = user?.profile?.name;
```

In our project:

```javascript
// The first heading might not exist
const title = content.split("\n").find((l) => l.startsWith("# "))?.replace("# ", "") || fileSlug;
//                                                                  ↑ safe — returns undefined if find() returns nothing
```

## Nullish Coalescing: Default Values

```javascript
// || treats 0, "", false as "empty" (often wrong)
const count = value || 10;  // if value is 0, this gives 10 (bug!)

// ?? only treats null/undefined as "empty" (usually correct)
const count = value ?? 10;  // if value is 0, this gives 0 (correct)
```

In practice:

```javascript
const fontSize = props.fontSize ?? 14;  // only default if truly not provided
```

## Array Methods: The Functional Toolkit

These replace `for` loops in modern JavaScript:

```javascript
const files = ["chapter-00.md", "README.md", "chapter-01.md", "notes.txt"];

// .filter() — keep items that pass a test
const chapters = files.filter(f => f.startsWith("chapter-"));
// ["chapter-00.md", "chapter-01.md"]

// .map() — transform each item
const slugs = chapters.map(f => f.replace(".md", ""));
// ["chapter-00", "chapter-01"]

// .find() — get the first match
const readme = files.find(f => f === "README.md");
// "README.md"

// .some() — does any item pass?
const hasMarkdown = files.some(f => f.endsWith(".md"));
// true

// .sort() — order items
const sorted = chapters.sort();
// ["chapter-00.md", "chapter-01.md"]

// Chain them:
const result = files
  .filter(f => f.endsWith(".md"))
  .filter(f => f.startsWith("chapter-"))
  .map(f => f.replace(".md", ""))
  .sort();
```

Our `lib/markdown.ts` is built entirely on these methods.

## Async/Await: Waiting for Things

Some operations take time (reading files, fetching data). `async/await` makes them readable:

```javascript
// Without async/await (callback hell):
fetch("/api/posts")
  .then(response => response.json())
  .then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error(error);
  });

// With async/await (reads like synchronous code):
async function getPosts() {
  try {
    const response = await fetch("/api/posts");
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}
```

In our CodePlayground, loading Pyodide:

```javascript
const runCode = async () => {
  setRunning(true);
  try {
    const pyodide = await loadPyodide();  // wait for WASM to load
    pyodide.runPython(code);
  } catch (err) {
    setOutput(`Error: ${err.message}`);
  }
  setRunning(false);
};
```

## Modules: Import & Export

Every file in our project is a module:

```javascript
// Named exports (can have many per file)
export function getAllSeries() { ... }
export function getChapter() { ... }

// Import named exports
import { getAllSeries, getChapter } from "@/lib/markdown";

// Default export (one per file)
export default function BlogPage() { ... }

// Import default
import BlogPage from "./page";
```

The `@/` prefix is a path alias (configured in `tsconfig.json`) that means "project root." So `@/lib/markdown` = `<root>/lib/markdown.ts`.

## Ternary Operator: Inline Decisions

```javascript
// if/else for a value:
const label = isActive ? "Active" : "Inactive";

// In JSX (you can't use if/else inside JSX):
<span className={isActive ? "text-green-500" : "text-gray-400"}>
  {isActive ? "Online" : "Offline"}
</span>
```

Nested ternaries get ugly — use early returns instead:

```javascript
// BAD
const status = loading ? "Loading..." : error ? "Error!" : data ? "Done" : "Idle";

// GOOD
function getStatus() {
  if (loading) return "Loading...";
  if (error) return "Error!";
  if (data) return "Done";
  return "Idle";
}
```

---

## Quick Reference

| Pattern | Example | Used For |
|---------|---------|----------|
| Destructuring | `{ name, age } = obj` | Extracting props, state |
| Spread | `{ ...obj, key: val }` | Copying with changes |
| Arrow + implicit return | `x => x * 2` | Callbacks, transforms |
| Template literal | `` `Hello ${name}` `` | Dynamic strings |
| Optional chaining | `obj?.prop?.sub` | Safe nested access |
| `??` | `val ?? default` | Null/undefined fallback |
| `.map()` / `.filter()` | `arr.map(fn)` | Transform/filter arrays |
| `async/await` | `const data = await fetch(url)` | Async operations |
| Ternary | `cond ? a : b` | Inline conditionals in JSX |

Every one of these appears in the code you've already written. Now you know *why*.

---

## What's Next

You know the JavaScript. Chapter 13 builds the React mental model — how components render, why state triggers re-renders, and the rules that make hooks work. All explained through the components we've already built.
