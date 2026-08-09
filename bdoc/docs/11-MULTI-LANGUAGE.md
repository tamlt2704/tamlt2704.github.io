# Chapter 11: Multi-Language Support

## What you'll learn

- How to store code in multiple languages
- How to toggle between Java and Python
- How to align line numbers across languages (the mapping problem)
- How to persist the user's preference

## 11.1 The problem

We already have Java and Python code for each algorithm. But the step generator uses `codeLine` — a single number. Java and Python have different numbers of lines, and the same logical step might be on different line numbers.

Example — the comparison step in bubble sort:

```
Java line 4:   if (arr[j] > arr[j + 1]) {
Python line 4: if arr[j] > arr[j + 1]:
```

In THIS case they happen to be the same line number. But for merge sort:

```
Java line 10:   int[] left = Arrays.copyOfRange(arr, l, m + 1);
Python line 7:  left = arr[l:m+1]
```

Same concept, different line numbers.

## 11.2 Solution: per-language line mapping

Instead of storing one `codeLine`, we store a mapping per language:

```ts
export type AlgorithmStep = {
  // Replace: codeLine: number;
  codeLines: {
    java: number;
    python: number;
  };
  description: string;
  array: number[];
  // ... rest unchanged
};
```

> **Why not just make both languages have the same line count?** We tried this in the early chapters (padding Python with empty lines). It works for simple algorithms but breaks down for:
> - Java's extra closing braces (Python doesn't have them)
> - Java's type declarations (Python infers types)
> - Python's more compact syntax
>
> Padding with empty lines looks awkward and confusing. Better to map explicitly.
>
> **Alternative: use a "logical step ID" instead of line numbers.** Each code line gets a tag like `"compare"`, `"swap_start"`, `"swap_end"`. The CodePanel looks up which physical line has that tag. This is more robust but more complex to set up. The explicit mapping is simpler for our case.

## 11.3 Restructure the code data

Update your algorithm files. Here's the pattern using bubble sort:

```ts
export type CodeData = {
  java: string[];
  python: string[];
};

export const BUBBLE_SORT_CODE: CodeData = {
  java: [
    "public void bubbleSort(int[] arr) {",    // 0
    "  int n = arr.length;",                   // 1
    "  for (int i = 0; i < n - 1; i++) {",    // 2
    "    for (int j = 0; j < n - i - 1; j++) {", // 3
    "      if (arr[j] > arr[j + 1]) {",       // 4
    "        int temp = arr[j];",              // 5
    "        arr[j] = arr[j + 1];",           // 6
    "        arr[j + 1] = temp;",             // 7
    "      }",                                // 8
    "    }",                                  // 9
    "  }",                                    // 10
    "}",                                      // 11
  ],
  python: [
    "def bubble_sort(arr):",                   // 0
    "    n = len(arr)",                        // 1
    "    for i in range(n - 1):",              // 2
    "        for j in range(n - i - 1):",      // 3
    "            if arr[j] > arr[j + 1]:",     // 4
    "                arr[j], arr[j+1] = arr[j+1], arr[j]", // 5
    "",                                        // 6
    "",                                        // 7
    "",                                        // 8
    "",                                        // 9
    "",                                        // 10
    "",                                        // 11
  ],
};
```

For bubble sort, Python's swap is a single line (line 5) vs Java's three lines (5, 6, 7). The step generator needs to account for this:

```ts
// In the step generator, for the swap:
steps.push({
  codeLines: { java: 5, python: 5 }, // "Save to temp" / "Do the swap"
  description: `Swap arr[${j}] and arr[${j+1}]`,
  // ...
});
```

## 11.4 Build a language toggle

Create `app/algorithms/components/LanguageToggle.tsx`:

```tsx
type Language = "java" | "python";

type LanguageToggleProps = {
  language: Language;
  onChange: (lang: Language) => void;
};

export default function LanguageToggle({ language, onChange }: LanguageToggleProps) {
  return (
    <div className="flex rounded-lg overflow-hidden border border-gray-300 text-sm">
      <button
        onClick={() => onChange("java")}
        className={`px-3 py-1.5 font-medium transition-colors ${
          language === "java"
            ? "bg-blue-600 text-white"
            : "bg-white text-gray-700 hover:bg-gray-100"
        }`}
      >
        Java
      </button>
      <button
        onClick={() => onChange("python")}
        className={`px-3 py-1.5 font-medium transition-colors ${
          language === "python"
            ? "bg-blue-600 text-white"
            : "bg-white text-gray-700 hover:bg-gray-100"
        }`}
      >
        Python
      </button>
    </div>
  );
}
```

## 11.5 Wire it into the page

```tsx
import LanguageToggle from "./components/LanguageToggle";

// State:
const [language, setLanguage] = useState<"java" | "python">("java");

// In the header:
<LanguageToggle language={language} onChange={setLanguage} />

// CodePanel now uses the selected language:
<CodePanel
  code={BUBBLE_SORT_CODE[language]}
  currentLine={step.codeLines[language]}
  language={language}
/>
```

Click the toggle — the code switches between Java and Python, and the highlight stays on the correct line for that language.

## 11.6 Persisting the preference

When users refresh the page, their language choice resets. We can save it to `localStorage`:

```tsx
// Initialize from localStorage (with fallback)
const [language, setLanguage] = useState<"java" | "python">(() => {
  if (typeof window === "undefined") return "java"; // SSR guard
  return (localStorage.getItem("preferred-language") as "java" | "python") || "java";
});

// Save on change
function handleLanguageChange(lang: "java" | "python") {
  setLanguage(lang);
  localStorage.setItem("preferred-language", lang);
}
```

> **Why the `typeof window === "undefined"` check?** Next.js can render components on the server (where `window` and `localStorage` don't exist). This guard prevents a crash during server-side rendering. It only matters for the initial render — after that, the component runs in the browser.
>
> **Alternative: use a cookie or URL parameter.** Cookies work across sessions. URL params (`?lang=python`) make links shareable with language preference included. localStorage is simplest for now.

## 11.7 Adding more languages (future-proofing)

The pattern extends naturally:

```ts
type Language = "java" | "python" | "javascript" | "cpp";

export type CodeData = Record<Language, string[]>;

export type AlgorithmStep = {
  codeLines: Record<Language, number>;
  // ...
};
```

Each new language just needs:
1. The code text
2. Line number mapping in the step generator
3. Keywords in the tokeniser

The toggle component already works with any number of buttons.

## Summary

✅ You support multiple programming languages for code display  
✅ You handle line number differences between languages  
✅ You built a toggle component  
✅ You persist the preference to localStorage  

## Key takeaway

**Separate the algorithm logic from its code representation.** The step generator produces steps with language-mapped line numbers. The CodePanel doesn't know which algorithm is running — it just highlights the line it's told to. This separation makes adding new languages trivial.

---

→ [Chapter 12: Polish and Deploy](./12-POLISH-AND-DEPLOY.md)
