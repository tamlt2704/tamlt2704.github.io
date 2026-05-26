"use client";

import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Props {
  language?: string;
  height?: string;
  code?: string; // base64-encoded code
  children?: React.ReactNode;
  initialCode?: string;
}

export function CodePlayground({
  language = "javascript",
  height = "200px",
  code,
  children,
  initialCode,
}: Props) {
  const getStartCode = () => {
    let s = "";
    if (code) {
      try {
        s = atob(code);
      } catch {
        s = code;
      }
    } else if (initialCode) {
      s = initialCode;
    } else if (typeof children === "string") {
      s = children;
    }
    return s.trim();
  };

  const [currentCode, setCurrentCode] = useState(getStartCode);
  const [output, setOutput] = useState("");
  const [running, setRunning] = useState(false);
  const [editing, setEditing] = useState(false);

  const runCode = async () => {
    setRunning(true);
    setOutput("");

    try {
      if (language === "javascript" || language === "js") {
        const logs: string[] = [];
        const fakeConsole = { log: (...args: unknown[]) => logs.push(args.join(" ")) };
        const fn = new Function("console", currentCode);
        fn(fakeConsole);
        setOutput(logs.join("\n") || "(no output)");
      } else if (language === "python") {
        const pyodide = await loadPyodide();
        pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
`);
        pyodide.runPython(currentCode);
        const stdout = pyodide.runPython("sys.stdout.getvalue()");
        setOutput(stdout || "(no output)");
      }
    } catch (err: unknown) {
      setOutput(`Error: ${err instanceof Error ? err.message : String(err)}`);
    }

    setRunning(false);
  };

  return (
    <div className="not-prose my-6 overflow-hidden rounded-lg border border-gray-300">
      <div className="relative" style={{ minHeight: height }}>
        {editing ? (
          <textarea
            value={currentCode}
            onChange={(e) => setCurrentCode(e.target.value)}
            onBlur={() => setEditing(false)}
            autoFocus
            spellCheck={false}
            className="w-full resize-none bg-gray-900 p-4 font-mono text-sm text-gray-100 focus:outline-none"
            style={{ height, tabSize: 2 }}
          />
        ) : (
          <div onClick={() => setEditing(true)} className="cursor-text">
            <SyntaxHighlighter
              language={language === "js" ? "javascript" : language}
              style={oneDark}
              customStyle={{ margin: 0, borderRadius: 0, minHeight: height, fontSize: "0.85rem" }}
            >
              {currentCode}
            </SyntaxHighlighter>
          </div>
        )}
        <span className="absolute top-2 right-2 rounded bg-gray-800 px-2 py-0.5 text-xs text-gray-500">
          {language}
        </span>
      </div>

      <div className="flex items-center gap-2 border-t bg-gray-100 px-4 py-2">
        <button
          onClick={runCode}
          disabled={running}
          className="rounded bg-teal-600 px-3 py-1 text-sm text-white hover:bg-teal-700 disabled:opacity-50"
        >
          {running ? "Running..." : "▶ Run"}
        </button>
        <button
          onClick={() => setCurrentCode(getStartCode())}
          className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
        >
          Reset
        </button>
        <span className="ml-auto text-xs text-gray-400">
          {editing ? "editing" : "click to edit"}
        </span>
      </div>

      {output && (
        <pre className="border-t bg-gray-50 px-4 py-3 font-mono text-sm whitespace-pre-wrap text-gray-800">
          {output}
        </pre>
      )}
    </div>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let pyodideInstance: any = null;
async function loadPyodide() {
  if (pyodideInstance) return pyodideInstance;
  // Load Pyodide from CDN via script tag (avoids Next.js bundler issues)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  if (!(window as any).loadPyodide) {
    await new Promise<void>((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js";
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Failed to load Pyodide"));
      document.head.appendChild(script);
    });
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  pyodideInstance = await (window as any).loadPyodide();
  return pyodideInstance;
}
