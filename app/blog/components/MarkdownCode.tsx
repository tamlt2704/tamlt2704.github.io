"use client";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Props {
    children: React.ReactNode;
    className?: string;
}

/**
 * Custom code block component for MDX rendering.
 * Detects language from className (e.g. "language-python") and applies syntax highlighting.
 */
export function MarkdownCode({ children, className }: Props) {
    const match = /language-(\w+)/.exec(className || "");
    const lang = match ? match[1] : "";
    const code = String(children).replace(/\n$/, "");

    if (!match) {
        // Inline code
        return (
            <code className="text-pink-600 bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">
                {children}
            </code>
        );
    }

    // Fenced code block with language
    return (
        <SyntaxHighlighter
            language={lang}
            style={oneDark}
            customStyle={{
                margin: "1rem 0",
                borderRadius: "0.5rem",
                fontSize: "0.8rem",
                lineHeight: 1.6,
            }}
        >
            {code}
        </SyntaxHighlighter>
    );
}

/**
 * Wrapper for <pre> to prevent double-wrapping by prose styles.
 */
export function MarkdownPre({ children }: { children: React.ReactNode }) {
    return <>{children}</>;
}
