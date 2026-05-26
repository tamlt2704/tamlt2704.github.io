# Chapter 5: The Code Playground

[← Chapter 4: Interactive Quiz](/blog/nextjs-ghpages/chapter-04-interactive-quiz) | [Chapter 6: Visualizer →](/blog/nextjs-ghpages/chapter-06-visualizer)

---

## The Limitation

Your reader sees a code block. They think "what if I change the input?" They copy the code, open a terminal, paste it, run it. Context switch. Flow broken.

What if the code block itself was editable? What if there was a "Run" button right there?

## The Approach

For a static site (no backend), we have two options for running code:

1. **JavaScript/TypeScript** — runs natively in the browser
2. **Python** — use Pyodide (Python compiled to WebAssembly)

We'll build a playground that handles both. JavaScript runs instantly. Python loads Pyodide on first use.

## The Component

This component has three parts: an editable textarea (the "editor"), a Run button, and an output area. For JavaScript, it executes code using `new Function()`. For Python, it loads Pyodide (a WebAssembly Python runtime) on demand.

Create `app/blog/components/CodePlayground.tsx`:

```bash
touch app/blog/components/CodePlayground.tsx
```

```tsx
"use client"; // Interactive — needs browser APIs (textarea, Function constructor)

import { useState, useRef } from "react";
// useState: track code text, output, and running state
// useRef: get a reference to the textarea DOM element (for focus management)

interface Props {
  language?: string; // "javascript" or "python"
  initialCode: string; // The starting code shown in the editor
  height?: string; // CSS height of the textarea (default "200px")
}

export function CodePlayground({
  language = "javascript", // Default to JS if not specified
  initialCode,
  height = "200px",
}: Props) {
  const [code, setCode] = useState(initialCode.trim()); // Current editor content
  const [output, setOutput] = useState(""); // Execution result
  const [running, setRunning] = useState(false); // Show "Running..." state
  const textareaRef = useRef<HTMLTextAreaElement>(null); // DOM reference for focus

  const runCode = async () => {
    setRunning(true);
    setOutput(""); // Clear previous output

    try {
      if (language === "javascript" || language === "js") {
        // JavaScript execution strategy:
        // 1. Create a fake console that captures log() calls into an array
        // 2. Wrap the user's code in a new Function (like eval, but scoped)
        // 3. Pass our fake console as the "console" variable
        const logs: string[] = [];
        const fakeConsole = { log: (...args: any[]) => logs.push(args.join(" ")) };
        const fn = new Function("console", code); // Creates: function(console) { <user code> }
        fn(fakeConsole); // Execute with our fake console
        setOutput(logs.join("\n") || "(no output)");
      } else if (language === "python") {
        // Python execution strategy:
        // Pyodide is CPython compiled to WebAssembly — real Python in the browser
        // It's ~5MB, so we load it lazily (only when user clicks Run)
        const pyodide = await loadPyodide();
        // Redirect Python's stdout to a StringIO buffer so we can capture print() output
        pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
`);
        pyodide.runPython(code); // Execute the user's Python code
        const stdout = pyodide.runPython("sys.stdout.getvalue()"); // Read captured output
        setOutput(stdout || "(no output)");
      }
    } catch (err: any) {
      // Show the error message (syntax errors, runtime errors, etc.)
      setOutput(`Error: ${err.message}`);
    }

    setRunning(false);
  };

  return (
    <div className="my-6 overflow-hidden rounded-lg border border-gray-300">
      {/* Editor */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          spellCheck={false}
          className="w-full resize-none bg-gray-900 p-4 font-mono text-sm text-gray-100 focus:outline-none"
          style={{ height, tabSize: 4 }}
        />
        <span className="absolute top-2 right-2 rounded bg-gray-800 px-2 py-0.5 text-xs text-gray-500">
          {language}
        </span>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2 border-t bg-gray-100 px-4 py-2">
        <button
          onClick={runCode}
          disabled={running}
          className="rounded bg-teal-600 px-3 py-1 text-sm text-white hover:bg-teal-700 disabled:opacity-50"
        >
          {running ? "Running..." : "▶ Run"}
        </button>
        <button
          onClick={() => setCode(initialCode.trim())}
          className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
        >
          Reset
        </button>
      </div>

      {/* Output */}
      {output && (
        <pre className="border-t bg-gray-50 px-4 py-3 font-mono text-sm whitespace-pre-wrap text-gray-800">
          {output}
        </pre>
      )}
    </div>
  );
}

// Lazy Pyodide loader
let pyodideInstance: any = null;
async function loadPyodide() {
  if (pyodideInstance) return pyodideInstance;
  // @ts-ignore
  const { loadPyodide: load } = await import("pyodide");
  pyodideInstance = await load({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/",
  });
  return pyodideInstance;
}
```

## Register It

The `components` map tells MDXRemote: "when you encounter this HTML tag or JSX component name, render this React component instead."

| Key    | What it replaces                           | Why                                                     |
| ------ | ------------------------------------------ | ------------------------------------------------------- |
| `code` | `` `inline` `` and ` ```fenced``` ` blocks | Adds syntax highlighting via `react-syntax-highlighter` |
| `pre`  | `<pre>` wrapper around code blocks         | Prevents Tailwind prose from double-styling the block   |
| `a`    | Every `[link](url)` in markdown            | Strips `.md` extension so chapter links work as routes  |
| `Quiz` | `<Quiz />` in markdown                     | Renders the interactive multiple-choice component       |

```tsx
import { MarkdownCode, MarkdownPre } from "@/app/blog/components/MarkdownCode";
import { Quiz } from "@/app/blog/components/Quiz";

<MDXRemote
  source={content}
  components={{
    code: MarkdownCode, // syntax highlighting
    pre: MarkdownPre, // prevents double-wrapping by Tailwind prose
    a: ({ href, ...props }) => <a href={href?.replace(/\.md$/, "")} {...props} />, // strips .md from chapter links
    Quiz, // interactive multiple-choice component
  }}
  options={{
    mdxOptions: {
      remarkPlugins: [remarkGfm],
      format: "md",
    },
  }}
/>;
```

## Use It in Markdown

MDX's JSX parser conflicts with curly braces `{}` in code strings. The reliable solution: base64-encode your code and pass it via the `code` prop. The component decodes it client-side with `atob()`.

**Step 1: Encode your code**

In your terminal (PowerShell):

```powershell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("function binarySearch(arr, target) {`nlet lo = 0, hi = arr.length - 1;`nwhile (lo <= hi) {`nconst mid = Math.floor((lo + hi) / 2);`nif (arr[mid] === target) return mid;`nif (arr[mid] < target) lo = mid + 1;`nelse hi = mid - 1;`n}`nreturn -1;`n}`n`nconsole.log(binarySearch([1, 3, 5, 7, 9, 11], 7));"))
```

Or in bash/Node:

```bash
echo -n 'your code here' | base64
```

```javascript
// Node.js one-liner
Buffer.from(
  `function binarySearch(arr, target) {
  let lo = 0, hi = arr.length - 1;
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (arr[mid] === target) return mid;
    if (arr[mid] < target) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}

console.log(binarySearch([1, 3, 5, 7, 9, 11], 7));`,
).toString("base64");
```

**Step 2: Use the base64 string in markdown**

```markdown
<CodePlayground language="javascript" code="ZnVuY3Rpb24gYmluYXJ5U2VhcmNoKGFyciwgdGFyZ2V0KSB7CiAgbGV0IGxvID0gMCwgaGkgPSBhcnIubGVuZ3RoIC0gMTsKICB3aGlsZSAobG8gPD0gaGkpIHsKICAgIGNvbnN0IG1pZCA9IE1hdGguZmxvb3IoKGxvICsgaGkpIC8gMik7CiAgICBpZiAoYXJyW21pZF0gPT09IHRhcmdldCkgcmV0dXJuIG1pZDsKICAgIGlmIChhcnJbbWlkXSA8IHRhcmdldCkgbG8gPSBtaWQgKyAxOwogICAgZWxzZSBoaSA9IG1pZCAtIDE7CiAgfQogIHJldHVybiAtMTsKfQoKY29uc29sZS5sb2coYmluYXJ5U2VhcmNoKFsxLCAzLCA1LCA3LCA5LCAxMV0sIDcpKTs=" />
```

The reader sees an editable code block with syntax highlighting. They change `7` to `11`. Click Run. See the result. No context switch. No terminal. Learning by doing, right in the article.

## Python Playground

For Python content, Pyodide loads on first click (~5MB, cached after):

```markdown
<CodePlayground language="python" code="ZGVmIGZpYm9uYWNjaShuKToKICAgIGlmIG4gPD0gMToKICAgICAgICByZXR1cm4gbgogICAgcmV0dXJuIGZpYm9uYWNjaShuLTEpICsgZmlib25hY2NpKG4tMikKCmZvciBpIGluIHJhbmdlKDEwKToKICAgIHByaW50KGYnZmliKHtpfSkgPSB7Zmlib25hY2NpKGkpfScp" />
```

First run takes 2-3 seconds (loading WASM). After that, instant.

## Design Decisions

**Why a textarea instead of Monaco/CodeMirror?**

Simplicity. A `<textarea>` is 0 KB of JavaScript. Monaco is 2MB. For a blog where people tweak 5-10 lines, a textarea with monospace font is enough. If you want syntax highlighting in the editor later, swap in CodeMirror — the interface stays the same.

**Why not a backend?**

GitHub Pages is static. No server means no execution environment. Pyodide solves this for Python. JavaScript runs natively. For other languages, you'd need an external API (like Judge0) — but that adds latency and cost.

**Why lazy-load Pyodide?**

5MB is too much to load on page load. Loading on first "Run" click means JavaScript-only pages stay fast. The reader who needs Python pays the cost once.

```bash
git add app/blog/components/CodePlayground.tsx
git commit -m "feat: add CodePlayground component"
```

---

## Commit Your Progress

```bash
git add .
git commit -m "feat: add CodePlayground component for JS and Python"
```

## What's Next

Quizzes test knowledge. Playgrounds enable experimentation. But some concepts need _visualization_ — watching an algorithm step through data, seeing the tree rebalance, watching the sort happen. Chapter 6: the Visualizer component.
