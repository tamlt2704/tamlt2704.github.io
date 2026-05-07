import Navbar from "@/app/components/Navbar";
import NewsletterSignup from "@/app/components/NewsletterSignup";

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900">
            <Navbar />
            <div className="max-w-3xl mx-auto px-6 py-12">
                <h1
                    style={{
                        fontSize: "28px",
                        fontWeight: "bold",
                        color: "#111",
                        marginBottom: "24px",
                    }}
                >
                    About
                </h1>

                <div style={{ fontSize: "15px", lineHeight: 1.8, color: "#374151" }}>
                    <p style={{ marginBottom: "16px" }}>
                        I&apos;m a software engineer who builds things and writes about the process.
                        This site is where I publish tutorials, courses, and interactive tools
                        covering mobile development, web platforms, algorithms, and systems design.
                    </p>
                    <p style={{ marginBottom: "16px" }}>
                        I believe the best way to learn is to build real projects — not toy examples.
                        Every tutorial on this site is extracted from production work.
                    </p>
                    <p style={{ marginBottom: "32px" }}>
                        When I&apos;m not coding, I&apos;m probably studying Chinese, building educational
                        games for my kids, or optimizing something that doesn&apos;t need optimizing.
                    </p>
                </div>

                {/* What I Do */}
                <section style={{ marginBottom: "48px" }}>
                    <h2
                        style={{
                            fontSize: "20px",
                            fontWeight: "600",
                            color: "#111",
                            marginBottom: "16px",
                        }}
                    >
                        What I Do
                    </h2>
                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
                            gap: "12px",
                        }}
                    >
                        {[
                            { emoji: "📱", label: "Mobile Apps", detail: "React Native / Expo" },
                            { emoji: "🌐", label: "Web Platforms", detail: "Next.js / TypeScript" },
                            { emoji: "☁️", label: "Cloud & DevOps", detail: "AWS / Docker / K8s" },
                            { emoji: "📊", label: "Data & Algorithms", detail: "Python / Visualization" },
                        ].map((item) => (
                            <div
                                key={item.label}
                                style={{
                                    padding: "16px",
                                    background: "#f8fafc",
                                    borderRadius: "8px",
                                    border: "1px solid #e2e8f0",
                                }}
                            >
                                <span style={{ fontSize: "24px" }}>{item.emoji}</span>
                                <p
                                    style={{
                                        fontWeight: "600",
                                        fontSize: "14px",
                                        color: "#111",
                                        marginTop: "8px",
                                        marginBottom: "2px",
                                    }}
                                >
                                    {item.label}
                                </p>
                                <p style={{ fontSize: "13px", color: "#6b7280", margin: 0 }}>
                                    {item.detail}
                                </p>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Work With Me */}
                <section style={{ marginBottom: "48px" }}>
                    <h2
                        style={{
                            fontSize: "20px",
                            fontWeight: "600",
                            color: "#111",
                            marginBottom: "16px",
                        }}
                    >
                        Work With Me
                    </h2>
                    <div
                        style={{
                            padding: "24px",
                            background: "#f8fafc",
                            borderRadius: "12px",
                            border: "1px solid #e2e8f0",
                        }}
                    >
                        <p
                            style={{
                                fontSize: "15px",
                                color: "#374151",
                                marginBottom: "16px",
                                lineHeight: 1.6,
                            }}
                        >
                            I take on select consulting and freelance projects. Areas I can help with:
                        </p>
                        <ul
                            style={{
                                fontSize: "14px",
                                color: "#374151",
                                lineHeight: 2,
                                paddingLeft: "20px",
                                marginBottom: "16px",
                            }}
                        >
                            <li>React Native app development (greenfield or rescue)</li>
                            <li>Next.js platform architecture and performance</li>
                            <li>Technical content and documentation</li>
                            <li>Code review and architecture consulting</li>
                            <li>Team training workshops</li>
                        </ul>
                        <a
                            href="mailto:tamlt2704@gmail.com"
                            style={{
                                display: "inline-block",
                                background: "#111",
                                color: "white",
                                padding: "10px 20px",
                                borderRadius: "8px",
                                fontSize: "14px",
                                fontWeight: "500",
                                textDecoration: "none",
                            }}
                        >
                            Get in Touch →
                        </a>
                    </div>
                </section>

                {/* Newsletter */}
                <section>
                    <NewsletterSignup />
                </section>
            </div>
        </div>
    );
}
