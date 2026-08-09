# Chapter 04: Displaying Code with Syntax Highlighting

## What you'll learn

- How to implement basic syntax highlighting
- Tokenisation — breaking code into meaningful pieces
- Why we build it ourselves first (then upgrade later)

## 4.1 The problem with our current CodePanel

Right now, all code text is white. Real IDEs colour keywords (`for`, `if`, `int`) differently from strings, comments, and variables. This makes code much easier to read — especially for learners.

## 4.2 How syntax highlighting works (the concept)

Syntax highlighting is a two-step process:

1. **Tokenise** — break the text into tokens: keywords, strings, numbers, comments, operators, identifiers
2. **Colour** — assign a CSS class to each token type, then style those classes

```
"if (arr[j] > arr[j+1])"
        ↓ tokenise
[
  { type: "keyword", value: "if" },
  { type: "punctuation", value: " (" },
  { type: "identifier", value: "arr" },
  { type: "punctuation", value: "[" },
  { type: "identifier", value: "j" },
  ...
]
        ↓ render with colours
<span class="keyword">if</span> <span class="punct">(</span>...
```

> **Why build our own first?** Libraries like Prism.js or Shiki handle this perfectly. But they're black boxes — you install, configure, and hope it works. By building a simple version, you'll understand what they do internally. Then when you switch to a library (Chapter 12), you'll know how to debug issues.
>
> **Alternative: Skip straight to a library.** If you don't care about understanding tokenisation, jump to section 4.6 where we install a library. The hand-built version in 4.3–4.5 is for learning.

## 4.3 Build a simple tokeniser

Create `app/algorithms/lib/tokenise.ts`:

```ts
export type Token = {
  type: "keyword" | "string" | "number" | "comment" | "operator" | "punctuation" | "identifier" | "whitespace";
  value: string;
};

const JAVA_KEYWORDS = new Set([
  "public", "private", "protected", "static", "void", "int", "boolean",
  "char", "double", "float", "long", "short", "byte", "class", "interface",
  "extends", "implements", "new", "return", "if", "else", "for", "while",
  "do", "switch", "case", "break", "continue", "try", "catch", "finally",
  "throw", "throws", "import", "package", "this", "super", "null", "true", "false",
]);

const PYTHON_KEYWORDS = new Set([
  "def", "class", "if", "elif", "else", "for", "while", "return", "import",
  "from", "as", "try", "except", "finally", "raise", "with", "pass", "break",
  "continue", "and", "or", "not", "in", "is", "None", "True", "False",
  "self", "lambda", "yield", "global", "nonlocal",
]);

export function tokenise(line: string, language: "java" | "python"): Token[] {
  const keywords = language === "java" ? JAVA_KEYWORDS : PYTHON_KEYWORDS;
  const tokens: Token[] = [];
  let i = 0;

  while (i < line.length) {
    // Whitespace
    if (line[i] === " " || line[i] === "\t") {
      let start = i;
      while (i < line.length && (line[i] === " " || line[i] === "\t")) i++;
      tokens.push({ type: "whitespace", value: line.slice(start, i) });
      continue;
    }

    // Single-line comment
    if (line.slice(i, i + 2) === "//" || (language === "python" && line[i] === "#")) {
      tokens.push({ type: "comment", value: line.slice(i) });
      break; // rest of line is comment
    }

    // String (double or single quotes)
    if (line[i] === '"' || line[i] === "'") {
      const quote = line[i];
      let j = i + 1;
      while (j < line.length && line[j] !== quote) {
        if (line[j] === "\\") j++; // skip escaped char
        j++;
      }
      tokens.push({ type: "string", value: line.slice(i, j + 1) });
      i = j + 1;
      continue;
    }

    // Number
    if (/[0-9]/.test(line[i])) {
      let start = i;
      while (i < line.length && /[0-9.]/.test(line[i])) i++;
      tokens.push({ type: "number", value: line.slice(start, i) });
      continue;
    }

    // Identifier or keyword
    if (/[a-zA-Z_]/.test(line[i])) {
      let start = i;
      while (i < line.length && /[a-zA-Z0-9_]/.test(line[i])) i++;
      const word = line.slice(start, i);
      tokens.push({
        type: keywords.has(word) ? "keyword" : "identifier",
        value: word,
      });
      continue;
    }

    // Operators
    if ("=<>!+-*/%&|^~".includes(line[i])) {
      tokens.push({ type: "operator", value: line[i] });
      i++;
      continue;
    }

    // Punctuation (brackets, semicolons, etc.)
    tokens.push({ type: "punctuation", value: line[i] });
    i++;
  }

  return tokens;
}
```

**How this works — step by step:**

The function scans the string character by character. At each position, it checks: "What kind of token starts here?" The first match wins:

1. Whitespace? Consume all consecutive spaces.
2. Comment start (`//` or `#`)? Consume the rest of the line.
3. Quote? Scan until the matching closing quote.
4. Digit? Scan until a non-digit.
5. Letter? Scan the full word, then check if it's a keyword.
6. Operator character? Single token.
7. Anything else? Punctuation.

This is a simple **lexer** — the same concept used in compilers. Real lexers are more sophisticated (handling multi-line comments, regex literals, Unicode), but this covers 90% of what we need.

## 4.4 Update CodePanel to use tokens

Update `app/algorithms/components/CodePanel.tsx`:

```tsx
import { tokenise, Token } from "../lib/tokenise";

type CodePanelProps = {
  code: string[];
  currentLine: number;
  language: "java" | "python";
};

const TOKEN_COLOURS: Record<Token["type"], string> = {
  keyword: "text-purple-400",
  string: "text-green-400",
  number: "text-orange-400",
  comment: "text-gray-500 italic",
  operator: "text-cyan-300",
  punctuation: "text-gray-400",
  identifier: "text-gray-100",
  whitespace: "",
};

export default function CodePanel({ code, currentLine, language }: CodePanelProps) {
  return (
    <div className="flex-1 overflow-auto bg-gray-900 p-4 rounded-lg">
      <pre className="text-sm font-mono leading-relaxed">
        {code.map((line, index) => {
          const tokens = tokenise(line, language);
          return (
            <div
              key={index}
              className={`px-2 py-0.5 rounded ${
                index === currentLine
                  ? "bg-yellow-500/20 border-l-2 border-yellow-400"
                  : "border-l-2 border-transparent"
              }`}
            >
              <span className="text-gray-500 mr-4 select-none text-xs">
                {String(index + 1).padStart(2, " ")}
              </span>
              {tokens.map((token, tokenIdx) => (
                <span key={tokenIdx} className={TOKEN_COLOURS[token.type]}>
                  {token.value}
                </span>
              ))}
            </div>
          );
        })}
      </pre>
    </div>
  );
}
```

Don't forget to update `page.tsx` to pass the `language` prop:

```tsx
<CodePanel code={SAMPLE_CODE} currentLine={currentLine} language="java" />
```

**Now your code panel has colours!** Keywords are purple, strings are green, numbers are orange.

## 4.5 Understanding the colour mapping

```tsx
const TOKEN_COLOURS: Record<Token["type"], string> = { ... };
```

`Record<K, V>` is a TypeScript utility type meaning "an object where keys are of type K and values are of type V". This ensures we have a colour for every token type — TypeScript will error if we forget one.

> **Why a lookup object instead of `if/else`?** Performance doesn't matter here (it's fast either way), but readability does. A flat mapping is easier to scan and modify than a chain of conditions. You can change the purple to blue in one place.
>
> **Colour scheme:** These colours follow the "dark theme" convention from VS Code's default theme. Feel free to adjust them.

## 4.6 Alternative: Using a library (Shiki)

Our hand-built tokeniser works for simple code but misses edge cases (multi-line strings, generics, annotations). For production, use a proper library.

The two main options:

| Library | Pros | Cons |
|---------|------|------|
| **Shiki** | Uses VS Code's grammar files — perfect highlighting for 200+ languages. Server-side friendly. | Larger bundle, async loading |
| **Prism.js** | Lightweight, client-side, many plugins | Less accurate for some languages, manual theme setup |

We'll stick with our hand-built tokeniser for this tutorial because it gives us full control over the highlighting AND the line-level interaction (which line is active). You can swap in Shiki later if you want production-grade highlighting.

## 4.7 Adding a description tooltip

One nice addition: showing what each line DOES when it's highlighted. Add to the code data:

```tsx
const SAMPLE_CODE_WITH_DESCRIPTIONS = [
  { code: "public void bubbleSort(int[] arr) {", desc: "Function that sorts an array in-place" },
  { code: "  for (int i = 0; i < arr.length - 1; i++) {", desc: "Outer loop: one pass per element" },
  { code: "    for (int j = 0; j < arr.length - i - 1; j++) {", desc: "Inner loop: compare adjacent pairs" },
  { code: "      if (arr[j] > arr[j + 1]) {", desc: "Is left element bigger than right?" },
  { code: "        int temp = arr[j];", desc: "Save the left value" },
  { code: "        arr[j] = arr[j + 1];", desc: "Move right value to left position" },
  { code: "        arr[j + 1] = temp;", desc: "Put saved value in right position" },
  { code: "      }", desc: "" },
  { code: "    }", desc: "" },
  { code: "  }", desc: "" },
  { code: "}", desc: "" },
];
```

We'll use this in Chapter 08 when we build the step engine. For now, keep it in mind — the data structure will evolve as we add more information per step.

## Summary

✅ You built a tokeniser from scratch  
✅ You understand how syntax highlighting works (tokenise → classify → colour)  
✅ Your code panel now shows coloured syntax  
✅ You know the alternatives (Shiki, Prism.js) and when to use them  

## Key takeaway

**Syntax highlighting is just pattern matching + CSS.** Break text into tokens, classify each token, assign colours. Libraries automate this with grammar files (like regex on steroids), but the concept is the same.

---

→ [Chapter 05: D3 Fundamentals — Your First Bar Chart](./05-D3-FUNDAMENTALS.md)
