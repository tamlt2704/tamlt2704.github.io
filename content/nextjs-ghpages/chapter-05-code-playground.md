# Chapter 5: The Code Playground

[← Chapter 4: Interactive Quiz](/blog/nextjs-ghpages/chapter-04-interactive-quiz) | [Chapter 6: Visualizer →](/blog/nextjs-ghpages/chapter-06-visualizer)

---

## What We're Building

```
┌─────────────────────────────────────────────┐
│  [javascript]                               │
│                                             │
│  function greet(name) {                     │  ← editable textarea
│    console.log("Hello, " + name);           │
│  }                                          │
│  greet("World");                            │
│                                             │
├─────────────────────────────────────────────┤
│  [▶ Run]  [Reset]                           │  ← controls bar
├─────────────────────────────────────────────┤
│  Hello, World                               │  ← output area
└─────────────────────────────────────────────┘
```

The reader edits code, clicks Run, sees output. No terminal. No context switch.

---

## Concept: How `new Function` Works

JavaScript's `new Function` constructor creates a function from a string at runtime:

```js
const fn = new Function("console", "console.log('hi')");
fn(fakeConsole); // calls: function(console) { console.log('hi') }
```

The first arguments are parameter names. The last argument is the function body. This lets us:

1. Execute arbitrary user code
2. Inject a **fake console** that captures `log()` calls into an array
3. Keep execution scoped (safer than raw `eval`)

---

## Concept: What Is Pyodide?

Pyodide is CPython compiled to WebAssembly. It runs **real Python** in the browser — no server needed.

- Size: ~5MB (loaded lazily, only when user clicks Run)
- After first load: cached by the browser, subsequent runs are instant
- We redirect `sys.stdout` to a `StringIO` buffer to capture `print()` output

---

## Concept: Why Base64 Encoding for MDX

In MDX, component props use JSX syntax with curly braces `{}`. But code snippets also contain curly braces — this breaks JSX parsing:

```mdx
<!-- ❌ BROKEN — curly braces in code conflict with JSX -->

<CodePlayground initialCode={`function() { return {} }`} />
```

The fix: encode the code as **base64** and pass it via a `code` prop. The component decodes it at render time.

**How to encode with Node.js:**

```js
Buffer.from('function greet() {\n  console.log("hi");\n}').toString("base64");
// → "ZnVuY3Rpb24gZ3JlZXQoKSB7CiAgY29uc29sZS5sb2coImhpIik7Cn0="
```

In your MDX file, use the encoded string:

```mdx
<CodePlayground
  language="javascript"
  code="ZnVuY3Rpb24gZ3JlZXQoKSB7CiAgY29uc29sZS5sb2coImhpIik7Cn0="
/>
```

The component decodes it with `atob(code)` before displaying in the editor.

---

## Step 1: Create the Component File

```tsx
// 📁 app/blog/components/CodePlayground.tsx — create the file with client directive and imports
"use client"; // Needs browser APIs: textarea, Function constructor, atob

import { useState, useRef } from "react";

interface Props {
  language?: string; // "javascript" or "python"
  code: string; // base64-encoded initial code (avoids JSX curly brace conflicts)
  height?: string; // CSS height for the textarea
}
```

Save. No visible change yet — we're building the component piece by piece.

---

## Step 2: Component State and Decode

```tsx
// 📁 app/blog/components/CodePlayground.tsx — add the component function with state
export function CodePlayground({
  language = "javascript",
  code,
  height = "200px",
}: Props) {
  // Decode base64 prop back to readable code
  const initialCode = typeof window !== "undefined" ? atob(code) : "";
  const [editorCode, setEditorCode] = useState(initialCode);
  const [output, setOutput] = useState("");
  const [running, setRunning] = useState(false);
```

---

## Step 3: JavaScript Execution Logic

```tsx
// 📁 app/blog/components/CodePlayground.tsx — add runCode function inside the component
const runCode = async () => {
  setRunning(true);
  setOutput("");
  try {
    if (language === "javascript" || language === "js") {
      const logs: string[] = [];
      // Fake console captures all log() calls into our array
      const fakeConsole = { log: (...args: any[]) => logs.push(args.join(" ")) };
      const fn = new Function("console", editorCode);
      fn(fakeConsole);
      setOutput(logs.join("\n") || "(no output)");
    }
  } catch (err: any) {
    setOutput(`Error: ${err.message}`);
  }
  setRunning(false);
};
```

---

## Step 4: Python Execution Logic

```tsx
// 📁 app/blog/components/CodePlayground.tsx — add Python branch inside the try block
      } else if (language === "python") {
        // Load Pyodide lazily — only on first Run click
        const pyodide = await loadPyodide();
        // Redirect stdout so we can capture print() output
        pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
`);
        pyodide.runPython(editorCode);
        const stdout = pyodide.runPython("sys.stdout.getvalue()");
        setOutput(stdout || "(no output)");
      }
```

---

## Step 5: The JSX (Editor + Controls + Output)

```tsx
// 📁 app/blog/components/CodePlayground.tsx — return the UI
  return (
    <div className="my-6 overflow-hidden rounded-lg border border-gray-300">
      <div className="relative">
        <textarea
          value={editorCode}
          onChange={(e) => setEditorCode(e.target.value)}
          spellCheck={false}
          className="w-full resize-none bg-gray-900 p-4 font-mono text-sm text-gray-100"
          style={{ height }}
        />
        <span className="absolute top-2 right-2 rounded bg-gray-800 px-2 py-0.5 text-xs text-gray-500">
          {language}
        </span>
      </div>
```

---

## Step 6: Controls and Output Area

```tsx
// 📁 app/blog/components/CodePlayground.tsx — controls bar and output display
      <div className="flex items-center gap-2 border-t bg-gray-100 px-4 py-2">
        <button onClick={runCode} disabled={running}
          className="rounded bg-teal-600 px-3 py-1 text-sm text-white hover:bg-teal-700 disabled:opacity-50">
          {running ? "Running..." : "▶ Run"}
        </button>
        <button onClick={() => setEditorCode(initialCode)}
          className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900">
          Reset
        </button>
      </div>
      {output && (
        <pre className="border-t bg-gray-50 px-4 py-3 font-mono text-sm whitespace-pre-wrap">
          {output}
        </pre>
      )}
    </div>
  );
}
```

---

## Step 7: Lazy Pyodide Loader

```tsx
// 📁 app/blog/components/CodePlayground.tsx — add outside the component, at file bottom
let pyodideInstance: any = null;

async function loadPyodide() {
  if (pyodideInstance) return pyodideInstance;
  // Load from CDN only on first use — 5MB cached by browser after
  const { loadPyodide: load } = await import("pyodide" as any);
  pyodideInstance = await load({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/",
  });
  return pyodideInstance;
}
```

Save. The component is complete.

---

## Step 8: Register in the Components Map

```tsx
// 📁 app/blog/[...slug]/page.tsx — add CodePlayground to the MDXRemote components map
import { CodePlayground } from "@/app/blog/components/CodePlayground";

// Inside your MDXRemote call, add to the components object:
components={{
  code: MarkdownCode,
  pre: MarkdownPre,
  a: ({ href, ...props }) => <a href={href?.replace(/\.md$/, "")} {...props} />,
  Quiz,
  CodePlayground, // ← new: enables <CodePlayground /> in MDX files
}}
```

Save. Now MDX files can use `<CodePlayground />`.

---

## Step 9: Use in MDX — JavaScript Example

First, encode your code snippet:

```bash
node -e "console.log(Buffer.from('function binarySearch(arr, target) {\n  let lo = 0, hi = arr.length - 1;\n  while (lo <= hi) {\n    const mid = Math.floor((lo + hi) / 2);\n    if (arr[mid] === target) return mid;\n    if (arr[mid] < target) lo = mid + 1;\n    else hi = mid - 1;\n  }\n  return -1;\n}\nconsole.log(binarySearch([1,3,5,7,9,11], 7));').toString('base64'))"
```

Then use the output in your MDX:

```mdx
<CodePlayground
  language="javascript"
  code="ZnVuY3Rpb24gYmluYXJ5U2VhcmNoKGFyciwgdGFyZ2V0KSB7CiAgbGV0IGxvID0gMCwgaGkgPSBhcnIubGVuZ3RoIC0gMTsKICB3aGlsZSAobG8gPD0gaGkpIHsKICAgIGNvbnN0IG1pZCA9IE1hdGguZmxvb3IoKGxvICsgaGkpIC8gMik7CiAgICBpZiAoYXJyW21pZF0gPT09IHRhcmdldCkgcmV0dXJuIG1pZDsKICAgIGlmIChhcnJbbWlkXSA8IHRhcmdldCkgbG8gPSBtaWQgKyAxOwogICAgZWxzZSBoaSA9IG1pZCAtIDE7CiAgfQogIHJldHVybiAtMTsKfQpjb25zb2xlLmxvZyhiaW5hcnlTZWFyY2goWzEsMyw1LDcsOSwxMV0sIDcpKTs="
/>
```

Save. Refresh. You see an editable code editor with a binary search function. Click Run — output shows `3`.

---

## Step 10: Use in MDX — Python Example

Encode your Python code:

```bash
node -e "console.log(Buffer.from('def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nfor i in range(10):\n    print(f\"fib({i}) = {fibonacci(i)}\")').toString('base64'))"
```

Use in MDX:

```mdx
<CodePlayground
  language="python"
  code="ZGVmIGZpYm9uYWNjaShuKToKICAgIGlmIG4gPD0gMToKICAgICAgICByZXR1cm4gbgogICAgcmV0dXJuIGZpYm9uYWNjaShuLTEpICsgZmlib25hY2NpKG4tMikKCmZvciBpIGluIHJhbmdlKDEwKToKICAgIHByaW50KGYiZmliKHtpfSkgPSB7Zmlib25hY2NpKGkpfSIp"
/>
```

Save. Refresh. You see a Python editor. First Run takes 2-3 seconds (loading Pyodide WASM). After that, instant. Output shows `fib(0) = 0` through `fib(9) = 34`.

---

## Design Decisions

**Why a textarea instead of Monaco/CodeMirror?**
A `<textarea>` is 0 KB of JavaScript. Monaco is 2MB. For a blog where readers tweak 5-10 lines, monospace textarea is enough.

**Why no backend?**
GitHub Pages is static. Pyodide solves Python. JavaScript runs natively. No server cost.

**Why lazy-load Pyodide?**
5MB is too much on page load. JavaScript-only pages stay fast. Python cost is paid once, then cached.

**Why base64 instead of template literals?**
MDX parses JSX. Curly braces in code (`{}`) break the parser. Base64 eliminates all special characters — the prop is just a plain string.

---

## Commit

```bash
git add app/blog/components/CodePlayground.tsx
git commit -m "feat: add CodePlayground component for JS and Python"
```

---

## What's Next

Quizzes test knowledge. Playgrounds enable experimentation. But some concepts need _visualization_ — watching an algorithm step through data, seeing a tree rebalance. Chapter 6: the Visualizer component.
