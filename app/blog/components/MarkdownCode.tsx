"use client"; // Needs browser — SyntaxHighlighter uses DOM APIs

// Prism is a syntax highlighting engine. It tokenizes code and applies colors.
// oneDark is VS Code's dark theme — familiar to most developers.
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Props {
  children: React.ReactNode;
  className?: string; // MDX sets this to "language-python" for ```python blocks
}

export function MarkdownCode({ children, className }: Props) {
  // Extract language from className. Example: "language-python" → "python"
  const match = /language-(\w+)/.exec(className || "");
  const lang = match ? match[1] : "";
  const code = String(children).replace(/\n$/, "");

  if (!match) {
    // Inline code like `variable` — subtle pink highlight
    return (
      <code className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-sm text-pink-600">
        {children}
      </code>
    );
  }

  return (
    <SyntaxHighlighter
      language={lang}
      style={oneDark}
      customStyle={{
        margin: "1rem 0",
        borderRadius: "0.5rem",
        fontSize: "0.85rem",
        lineHeight: 1.6,
      }}
    >
      {code}
    </SyntaxHighlighter>
  );
}

// Prevents Tailwind prose styles from double-wrapping the code block
export function MarkdownPre({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
