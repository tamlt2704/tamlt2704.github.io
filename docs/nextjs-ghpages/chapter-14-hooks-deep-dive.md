# Chapter 14: Hooks Deep Dive

[← Chapter 13: React Mental Model](chapter-13-react-mental-model.md) | [Chapter 15: TypeScript for This Project →](chapter-15-typescript.md)

---

## The Hooks You'll Use Every Day

React has ~15 hooks. You'll use 4 of them 95% of the time. Let's master those through our blog components.

## useState: Managing Data That Changes

You've used this in every interactive component. Let's understand it deeply.

```javascript
const [value, setValue] = useState(initialValue);
```

**The initial value only matters on first render:**

```javascript
// This reads localStorage ONCE, not on every render
const [theme, setTheme] = useState(() => {
  return localStorage.getItem("theme") || "light";
});
```

The function form (`() => ...`) is called a "lazy initializer." Use it when the initial value is expensive to compute.

**State updates can be based on previous state:**

```javascript
// BAD — if called twice quickly, both read the same `count`
setCount(count + 1);
setCount(count + 1);  // still only +1 total

// GOOD — updater function always gets the latest value
setCount(prev => prev + 1);
setCount(prev => prev + 1);  // +2 total
```

Use the updater form when the new value depends on the old value.

**State updates are batched:**

```javascript
function handleClick() {
  setLoading(true);
  setError(null);
  setData(newData);
  // React batches these — only ONE re-render happens, not three
}
```

React is smart. Multiple `setState` calls in the same event handler = one re-render.

### Real example: our ThemeToggle

```javascript
function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    // Sync with actual DOM state on mount
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggle = () => {
    setDark(prev => !prev);  // updater form — always correct
    document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", !dark ? "dark" : "light");
  };

  return <button onClick={toggle}>{dark ? "☀️" : "🌙"}</button>;
}
```

## useEffect: Side Effects After Render

"Side effects" = anything outside React's render cycle: DOM manipulation, API calls, timers, subscriptions.

```javascript
useEffect(() => {
  // This runs AFTER the component renders
  
  return () => {
    // This runs BEFORE the next effect, or when component unmounts (cleanup)
  };
}, [dependencies]);  // Only re-run when these values change
```

**The dependency array controls when it runs:**

```javascript
// Runs after EVERY render (rarely what you want)
useEffect(() => { ... });

// Runs ONCE after first render (mount)
useEffect(() => { ... }, []);

// Runs when `query` changes
useEffect(() => { ... }, [query]);

// Runs when `query` OR `page` changes
useEffect(() => { ... }, [query, page]);
```

### Real example: MutationObserver in MarkdownCode

```javascript
function MarkdownCode({ children, className }) {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Side effect: observe DOM changes
    const check = () => setIsDark(
      document.documentElement.classList.contains("dark")
    );
    check();  // initial check

    const observer = new MutationObserver(check);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    // Cleanup: disconnect when component unmounts
    return () => observer.disconnect();
  }, []);  // empty deps = run once on mount

  return (
    <SyntaxHighlighter style={isDark ? oneDark : oneLight}>
      {children}
    </SyntaxHighlighter>
  );
}
```

### Real example: Reading progress bar

```javascript
function ReadingProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const update = () => {
      const scrolled = window.scrollY;
      const total = document.body.scrollHeight - window.innerHeight;
      setProgress(total > 0 ? (scrolled / total) * 100 : 0);
    };

    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
    //       ↑ cleanup — remove listener when component unmounts
  }, []);

  return <div style={{ width: `${progress}%` }} className="h-0.5 bg-teal-500" />;
}
```

### Common useEffect mistakes:

```javascript
// BUG: missing dependency
const [query, setQuery] = useState("");
useEffect(() => {
  fetch(`/api/search?q=${query}`);  // uses `query` but doesn't list it
}, []);  // never re-runs when query changes!

// FIX: include all used values in deps
useEffect(() => {
  fetch(`/api/search?q=${query}`);
}, [query]);  // re-runs when query changes
```

Rule: if you use a value inside the effect, it goes in the dependency array.

## useRef: Escape Hatch to the DOM

`useRef` gives you a mutable container that persists across renders without causing re-renders:

```javascript
const ref = useRef(initialValue);
// ref.current = the value (mutable, doesn't trigger re-render)
```

**Use case 1: Access a DOM element**

```javascript
function CodePlayground({ initialCode }) {
  const textareaRef = useRef(null);

  const focusEditor = () => {
    textareaRef.current?.focus();  // directly access the DOM node
  };

  return (
    <textarea ref={textareaRef} defaultValue={initialCode} />
  );
}
```

**Use case 2: Store a value that shouldn't trigger re-renders**

```javascript
function StepVisualizer({ steps }) {
  const [current, setCurrent] = useState(0);
  const touchStartRef = useRef(0);  // doesn't need to trigger re-render

  const handleTouchStart = (e) => {
    touchStartRef.current = e.touches[0].clientX;
  };

  const handleTouchEnd = (e) => {
    const diff = touchStartRef.current - e.changedTouches[0].clientX;
    if (diff > 50) setCurrent(c => Math.min(steps.length - 1, c + 1));
    if (diff < -50) setCurrent(c => Math.max(0, c - 1));
  };

  return <div onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>...</div>;
}
```

**Use case 3: Track previous value**

```javascript
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;  // returns the value from LAST render
}

// Usage:
const prevCount = usePrevious(count);
// On first render: undefined
// After count changes from 5 to 6: prevCount = 5
```

## Custom Hooks: Reusable Logic

A custom hook is just a function that uses other hooks. Name it `use___`:

```javascript
// Extract the dark mode logic into a reusable hook
function useDarkMode() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const check = () => setDark(document.documentElement.classList.contains("dark"));
    check();
    const observer = new MutationObserver(check);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  return { dark, toggle };
}

// Now any component can use it:
function ThemeToggle() {
  const { dark, toggle } = useDarkMode();
  return <button onClick={toggle}>{dark ? "☀️" : "🌙"}</button>;
}

function CodeBlock({ code }) {
  const { dark } = useDarkMode();
  return <SyntaxHighlighter style={dark ? oneDark : oneLight}>{code}</SyntaxHighlighter>;
}
```

### More custom hooks for our project:

```javascript
// Track scroll position
function useScrollProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const update = () => {
      const total = document.body.scrollHeight - window.innerHeight;
      setProgress(total > 0 ? (window.scrollY / total) * 100 : 0);
    };
    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, []);
  return progress;
}

// Detect mobile
function useIsMobile(breakpoint = 768) {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < breakpoint);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, [breakpoint]);
  return isMobile;
}

// Intersection observer (for lazy loading)
function useInView(ref, options = {}) {
  const [inView, setInView] = useState(false);
  useEffect(() => {
    if (!ref.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => setInView(entry.isIntersecting),
      options
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref, options]);
  return inView;
}
```

## The Hook Decision Tree

```
Need to store data that affects the UI?
  → useState

Need to run code after render (DOM, API, timer)?
  → useEffect

Need a DOM reference or mutable value that doesn't re-render?
  → useRef

Need to share state across many components?
  → useContext (or a state library)

Need to extract reusable stateful logic?
  → Custom hook (useXxx)
```

---

## Key Takeaways

1. `useState` — data that changes and triggers re-renders
2. `useEffect` — side effects after render, with cleanup
3. `useRef` — mutable values that don't trigger re-renders
4. Custom hooks — extract and reuse stateful logic
5. Dependency arrays control when effects re-run
6. Always include used values in dependency arrays
7. Use updater form (`prev => ...`) when new state depends on old

## What's Next

Chapter 15 adds TypeScript — not as a burden, but as a tool that catches bugs before they reach the browser. We'll type our components, hooks, and the markdown pipeline so the editor helps instead of hinders.
