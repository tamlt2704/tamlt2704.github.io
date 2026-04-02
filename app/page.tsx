import Navbar from "@/app/components/Navbar";
import Link from "next/link";

const playLinks = [
    { href: "/play/hanzi", label: "✍️ Hanzi Writer" },
    { href: "/play/math", label: "🔢 Math" },
    { href: "/play/numberbond", label: "🔗 Number Bonds" },
    { href: "/play/chinese", label: "🗣 Chinese Starters" },
    { href: "/play/solarsystem", label: "☀️ Solar System" },
    { href: "/play/daynight", label: "🌍 Day & Night Map" },
    { href: "/play/projectile", label: "🚀 Projectile Launcher" },
    { href: "/play/balance", label: "⚖️ Balance Scale" },
    { href: "/play/circuits", label: "⚡ Simple Circuits" },
    { href: "/play/pendulum", label: "🕐 Pendulum" },
    { href: "/play/fractions", label: "🍕 Fraction Pizza" },
    { href: "/play/timestable", label: "☄️ Times Table Shooter" },
    { href: "/play/shapes", label: "🔷 Shape Builder" },
    { href: "/play/turtle", label: "🐢 Turtle Graphics" },
    { href: "/play/pattern", label: "🧩 Pattern Machine" },
    { href: "/play/wordbuilder", label: "🔤 Word Builder" },
    { href: "/play/sentences", label: "📝 Sentence Scramble" },
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
