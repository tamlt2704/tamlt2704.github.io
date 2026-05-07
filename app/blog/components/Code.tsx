"use client";

interface CodeProps {
    children: string;
    lang?: string;
    title?: string;
}

export function Code({ children, lang, title }: CodeProps) {
    return (
        <div style={{ margin: "16px 0", borderRadius: "8px", overflow: "hidden", border: "1px solid #e5e7eb" }}>
            {title && (
                <div style={{ background: "#f3f4f6", padding: "6px 12px", fontSize: "12px", color: "#6b7280", borderBottom: "1px solid #e5e7eb", fontFamily: "monospace" }}>
                    {title}
                </div>
            )}
            <pre style={{ background: "#1f2937", padding: "16px", margin: 0, overflow: "auto", fontSize: "13px", lineHeight: 1.6 }}>
                <code style={{ color: "#e5e7eb", fontFamily: "var(--font-geist-mono), monospace" }}>
                    {children}
                </code>
            </pre>
        </div>
    );
}

export function InlineCode({ children }: { children: string }) {
    return (
        <code style={{ background: "#f3f4f6", padding: "2px 6px", borderRadius: "4px", fontSize: "13px", fontFamily: "var(--font-geist-mono), monospace", color: "#e11d48" }}>
            {children}
        </code>
    );
}

interface SectionProps {
    title: string;
    children: React.ReactNode;
}

export function Section({ title, children }: SectionProps) {
    return (
        <section style={{ marginTop: "32px" }}>
            <h2 style={{ fontSize: "20px", fontWeight: "bold", color: "#111827", marginBottom: "12px" }}>
                {title}
            </h2>
            {children}
        </section>
    );
}

export function SubSection({ title, children }: SectionProps) {
    return (
        <section style={{ marginTop: "24px" }}>
            <h3 style={{ fontSize: "16px", fontWeight: "600", color: "#1f2937", marginBottom: "8px" }}>
                {title}
            </h3>
            {children}
        </section>
    );
}

export function Paragraph({ children }: { children: React.ReactNode }) {
    return <p style={{ marginBottom: "16px" }}>{children}</p>;
}

export function Note({ children }: { children: React.ReactNode }) {
    return (
        <div style={{ background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: "8px", padding: "12px 16px", margin: "16px 0", fontSize: "14px", color: "#1e40af" }}>
            {children}
        </div>
    );
}
