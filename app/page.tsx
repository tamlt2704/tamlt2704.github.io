import Navbar from "@/app/components/Navbar";
import Link from "next/link";

const playLinks = [
    { href: "/play/hanzi", label: "✍️ Hanzi Writer" },
    { href: "/play/math", label: "🔢 Math" },
];

export default function Home() {
    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900">
            <Navbar />
            <div className="max-w-5xl mx-auto px-4 py-16 flex gap-12">
                <main className="flex-1">
                    {/* Your blog content here */}
                </main>
                <aside style={{ width: "200px", border: "1px solid #ddd", borderRadius: "4px", padding: "16px", position: "fixed", right: "32px", top: "80px" }}>
                    <p style={{ fontSize: "14px", fontWeight: "bold", color: "#333", marginBottom: "12px", paddingBottom: "8px", borderBottom: "1px solid #ddd" }}>Play</p>
                    <ul style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                        {playLinks.map((link) => (
                            <li key={link.href}>
                                <Link
                                    href={link.href}
                                    style={{ color: "#555", fontSize: "14px", textDecoration: "none" }}
                                >
                                    {link.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </aside>
            </div>
        </div>
    );
}
