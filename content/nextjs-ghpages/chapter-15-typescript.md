# Chapter 15: TypeScript for This Project

[← Chapter 14: Hooks Deep Dive](/blog/nextjs-ghpages/chapter-14-hooks-deep-dive) | [Chapter 16: Supabase Setup →](/blog/nextjs-ghpages/chapter-16-supabase-setup)

---

## Why TypeScript

You rename a prop from `question` to `prompt` in your Quiz component. The component works. But three markdown files still pass `question`. No error. No warning. The quiz silently shows `undefined`.

TypeScript catches this at build time:

```
Error: Property 'question' does not exist on type 'QuizProps'.
Did you mean 'prompt'?
```

TypeScript isn't about ceremony. It's about catching bugs before your readers see them.

## The Basics in 5 Minutes

```typescript
// Primitive types
const name: string = "Ada";
const age: number = 36;
const active: boolean = true;

// Arrays
const tags: string[] = ["react", "nextjs"];
const scores: number[] = [95, 87, 92];

// Objects (interfaces)
interface User {
  name: string;
  age: number;
  email?: string; // optional — might be undefined
}

const user: User = { name: "Ada", age: 36 };
```

Most of the time, TypeScript _infers_ types — you don't write them:

```typescript
const name = "Ada"; // TypeScript knows this is string
const nums = [1, 2, 3]; // TypeScript knows this is number[]
const doubled = nums.map((n) => n * 2); // TypeScript knows n is number
```

You only add types when TypeScript can't figure it out, or when you want to enforce a contract.

## Typing React Components

### Props interface

```typescript
interface QuizProps {
  question: string;
  options: string[];
  answer: number;
  explanation?: string; // optional
}

function Quiz({ question, options, answer, explanation }: QuizProps) {
  // TypeScript knows all prop types here
  // If you typo `questoin`, it's an error immediately
}
```

### Children prop

```typescript
interface LayoutProps {
  children: React.ReactNode;  // anything renderable
}

function Layout({ children }: LayoutProps) {
  return <div className="max-w-3xl mx-auto">{children}</div>;
}
```

### Event handlers

```typescript
function SearchInput() {
  const [query, setQuery] = useState("");  // TypeScript infers string

  // e is automatically typed as React.ChangeEvent<HTMLInputElement>
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  // Or let TypeScript infer it inline:
  return <input onChange={(e) => setQuery(e.target.value)} />;
}
```

### useState with complex types

```typescript
interface Step {
  data: number[];
  highlights: number[];
  label: string;
}

// TypeScript needs help when initial value doesn't reveal the full type
const [selected, setSelected] = useState<number | null>(null);
const [steps, setSteps] = useState<Step[]>([]);
```

## Typing Our Blog Components

### Quiz.tsx

```typescript
interface QuizProps {
  question: string;
  options: string[];
  answer: number;
  explanation?: string;
}

export function Quiz({ question, options, answer, explanation }: QuizProps) {
  const [selected, setSelected] = useState<number | null>(null);
  const [revealed, setRevealed] = useState(false);

  const handleSelect = (index: number) => {
    // index is typed
    if (revealed) return;
    setSelected(index);
    setRevealed(true);
  };

  // ...
}
```

### CodePlayground.tsx

```typescript
interface CodePlaygroundProps {
  language?: "javascript" | "python" | "typescript"; // union type — only these values allowed
  initialCode: string;
  height?: string;
}

export function CodePlayground({
  language = "javascript",
  initialCode,
  height = "200px",
}: CodePlaygroundProps) {
  const [code, setCode] = useState(initialCode.trim());
  const [output, setOutput] = useState("");
  const [running, setRunning] = useState(false);
  // ...
}
```

The `language` prop only accepts specific strings. Pass `"ruby"` and TypeScript errors at build time.

### StepVisualizer.tsx

```typescript
interface Step {
  data: number[];
  highlights: number[];
  label: string;
}

interface StepVisualizerProps {
  steps: Step[];
  title?: string;
}

export function StepVisualizer({ steps, title }: StepVisualizerProps) {
  const [current, setCurrent] = useState(0);
  const step: Step = steps[current]; // TypeScript knows the shape
  // ...
}
```

## Typing the Markdown Pipeline

### lib/markdown.ts

```typescript
import fs from "fs";
import path from "path";

interface SeriesInfo {
  name: string;
  slug: string;
  chapters: string[];
}

export function getAllSeries(): SeriesInfo[] {
  const base = path.join(process.cwd(), "content");
  if (!fs.existsSync(base)) return [];

  return fs
    .readdirSync(base, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map(
      (d): SeriesInfo => ({
        name: d.name,
        slug: d.name,
        chapters: fs
          .readdirSync(path.join(base, d.name))
          .filter((f) => f.endsWith(".md"))
          .sort(),
      }),
    );
}

export function getChapterContent(series: string, file: string): string | null {
  const filePath = path.join(process.cwd(), "content", series, file);
  if (!fs.existsSync(filePath)) return null;
  return fs.readFileSync(filePath, "utf-8");
}
```

Now if you call `getAllSeries()`, TypeScript knows the return type. Autocomplete shows `.name`, `.slug`, `.chapters`.

## Typing Custom Hooks

```typescript
interface UseDarkModeReturn {
  dark: boolean;
  toggle: () => void;
}

function useDarkMode(): UseDarkModeReturn {
  const [dark, setDark] = useState(false);
  // ...
  return { dark, toggle };
}

// Usage — TypeScript knows the shape:
const { dark, toggle } = useDarkMode();
//      ↑ boolean  ↑ () => void
```

## Generics: When Types Are Flexible

Sometimes a function works with _any_ type:

```typescript
// A hook that persists any value to localStorage
function useLocalStorage<T>(key: string, initial: T): [T, (val: T) => void] {
  const [value, setValue] = useState<T>(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initial;
  });

  const set = (val: T) => {
    setValue(val);
    localStorage.setItem(key, JSON.stringify(val));
  };

  return [value, set];
}

// Usage — TypeScript infers T from the initial value:
const [theme, setTheme] = useLocalStorage("theme", "light");
//     ↑ string                                      ↑ string → T = string

const [prefs, setPrefs] = useLocalStorage("prefs", { fontSize: 14, compact: false });
//     ↑ { fontSize: number; compact: boolean }
```

## The TypeScript Escape Hatches

When TypeScript is wrong or you're prototyping:

```typescript
// `as` assertion — "trust me, I know the type"
const element = document.getElementById("root") as HTMLDivElement;

// `any` — disable type checking (use sparingly)
const data: any = JSON.parse(response);

// `unknown` — safer than any, forces you to check before using
const data: unknown = JSON.parse(response);
if (typeof data === "string") {
  console.log(data.toUpperCase()); // TypeScript knows it's string here
}
```

Rule: avoid `any`. Use `unknown` + type guards when you genuinely don't know the type.

## Practical Tips

**Let TypeScript infer when possible:**

```typescript
// Unnecessary — TypeScript already knows
const name: string = "Ada";
const nums: number[] = [1, 2, 3];

// Just write:
const name = "Ada";
const nums = [1, 2, 3];
```

**Type props interfaces, not return types:**

```typescript
// Type the input (props), let TypeScript infer the output (JSX)
function Quiz({ question, options, answer }: QuizProps) {
  return <div>...</div>;  // return type inferred as JSX.Element
}
```

**Use `interface` for objects, `type` for unions:**

```typescript
interface QuizProps {
  question: string;
  options: string[];
}
type Theme = "light" | "dark";
type Status = "idle" | "loading" | "error" | "success";
```

---

## Key Takeaways

1. TypeScript catches bugs at build time, not runtime
2. Type props with `interface`, let TypeScript infer the rest
3. `useState<Type>` when initial value doesn't reveal the full type
4. Union types (`"a" | "b"`) restrict values to specific options
5. Generics (`<T>`) make reusable typed functions/hooks
6. Avoid `any` — use `unknown` with type guards instead
7. Don't over-type — inference handles most cases

---

## Series Complete

You now have everything to build and maintain an interactive learning platform:

| Chapters 1–7 | Build the platform |
| Chapter 8 | Dark/light theme |
| Chapter 9 | Progressive loading |
| Chapter 10 | Responsive layout |
| Chapter 11 | Performance |
| Chapter 12 | JavaScript patterns |
| Chapter 13 | React mental model |
| Chapter 14 | Hooks mastery |
| Chapter 15 | TypeScript safety |

You're not just building a blog — you're becoming a frontend developer by building something real. Every concept was introduced because you needed it, not because a curriculum said so.

Keep writing content. Keep adding components. The platform grows with you.
