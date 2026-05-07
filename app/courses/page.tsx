import Navbar from "@/app/components/Navbar";
import Link from "next/link";

interface Course {
    slug: string;
    title: string;
    description: string;
    chapters: number;
    price: string;
    status: "available" | "coming-soon";
    tags: string[];
}

const courses: Course[] = [
    {
        slug: "react-native-production",
        title: "React Native: Zero to App Store",
        description:
            "Build a production mobile app from scratch. Covers navigation, data fetching, push notifications, offline support, authentication, charts, and deployment with EAS.",
        chapters: 13,
        price: "$49",
        status: "available",
        tags: ["react-native", "expo", "typescript", "mobile"],
    },
    {
        slug: "nextjs-content-platform",
        title: "Build a Content Platform with Next.js",
        description:
            "Create a blog, course platform, and newsletter system using Next.js App Router, MDX, Stripe payments, and email automation.",
        chapters: 10,
        price: "$39",
        status: "coming-soon",
        tags: ["next.js", "mdx", "stripe", "email"],
    },
    {
        slug: "algorithms-visual",
        title: "Algorithms & Data Structures — Visually",
        description:
            "Learn algorithms through interactive visualizations. Binary search, sorting, trees, graphs, dynamic programming — all animated.",
        chapters: 15,
        price: "$59",
        status: "coming-soon",
        tags: ["algorithms", "data-structures", "visualization"],
    },
];

export default function CoursesPage() {
    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900">
            <Navbar />
            <div className="max-w-4xl mx-auto px-4 py-12">
                <h1
                    style={{
                        fontSize: "32px",
                        fontWeight: "bold",
                        color: "#111",
                        marginBottom: "8px",
                    }}
                >
                    Courses
                </h1>
                <p
                    style={{
                        color: "#666",
                        fontSize: "16px",
                        marginBottom: "48px",
                        maxWidth: "600px",
                    }}
                >
                    Structured, project-based courses that take you from zero to
                    production. Each course includes source code, exercises, and
                    lifetime updates.
                </p>

                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
                        gap: "24px",
                    }}
                >
                    {courses.map((course) => (
                        <article
                            key={course.slug}
                            style={{
                                border: "1px solid #e5e7eb",
                                borderRadius: "12px",
                                padding: "24px",
                                display: "flex",
                                flexDirection: "column",
                                justifyContent: "space-between",
                                opacity: course.status === "coming-soon" ? 0.7 : 1,
                            }}
                        >
                            <div>
                                <div
                                    style={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        marginBottom: "12px",
                                    }}
                                >
                                    <span
                                        style={{
                                            fontSize: "12px",
                                            fontWeight: "600",
                                            color:
                                                course.status === "available"
                                                    ? "#16a34a"
                                                    : "#f59e0b",
                                            background:
                                                course.status === "available"
                                                    ? "#f0fdf4"
                                                    : "#fffbeb",
                                            padding: "4px 8px",
                                            borderRadius: "4px",
                                        }}
                                    >
                                        {course.status === "available"
                                            ? "Available"
                                            : "Coming Soon"}
                                    </span>
                                    <span
                                        style={{
                                            fontSize: "20px",
                                            fontWeight: "bold",
                                            color: "#111",
                                        }}
                                    >
                                        {course.price}
                                    </span>
                                </div>
                                <h2
                                    style={{
                                        fontSize: "18px",
                                        fontWeight: "600",
                                        color: "#111",
                                        marginBottom: "8px",
                                    }}
                                >
                                    {course.title}
                                </h2>
                                <p
                                    style={{
                                        fontSize: "14px",
                                        color: "#6b7280",
                                        lineHeight: 1.6,
                                        marginBottom: "12px",
                                    }}
                                >
                                    {course.description}
                                </p>
                                <p
                                    style={{
                                        fontSize: "13px",
                                        color: "#9ca3af",
                                        marginBottom: "16px",
                                    }}
                                >
                                    {course.chapters} chapters • Source code included
                                </p>
                                <div
                                    style={{
                                        display: "flex",
                                        gap: "6px",
                                        flexWrap: "wrap",
                                    }}
                                >
                                    {course.tags.map((tag) => (
                                        <span
                                            key={tag}
                                            style={{
                                                fontSize: "11px",
                                                color: "#3b82f6",
                                                background: "#eff6ff",
                                                padding: "2px 6px",
                                                borderRadius: "4px",
                                            }}
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            <div style={{ marginTop: "20px" }}>
                                {course.status === "available" ? (
                                    <Link
                                        href={`/courses/${course.slug}`}
                                        style={{
                                            display: "block",
                                            textAlign: "center",
                                            background: "#111",
                                            color: "white",
                                            padding: "10px 16px",
                                            borderRadius: "8px",
                                            fontSize: "14px",
                                            fontWeight: "500",
                                            textDecoration: "none",
                                        }}
                                    >
                                        Get the Course →
                                    </Link>
                                ) : (
                                    <button
                                        disabled
                                        style={{
                                            display: "block",
                                            width: "100%",
                                            textAlign: "center",
                                            background: "#f3f4f6",
                                            color: "#9ca3af",
                                            padding: "10px 16px",
                                            borderRadius: "8px",
                                            fontSize: "14px",
                                            fontWeight: "500",
                                            border: "none",
                                            cursor: "not-allowed",
                                        }}
                                    >
                                        Notify Me
                                    </button>
                                )}
                            </div>
                        </article>
                    ))}
                </div>

                {/* FAQ Section */}
                <section style={{ marginTop: "64px" }}>
                    <h2
                        style={{
                            fontSize: "22px",
                            fontWeight: "bold",
                            color: "#111",
                            marginBottom: "24px",
                        }}
                    >
                        FAQ
                    </h2>
                    <div
                        style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "16px",
                        }}
                    >
                        {[
                            {
                                q: "What do I get?",
                                a: "Full source code, step-by-step chapters, exercises, and lifetime access to updates. No subscriptions.",
                            },
                            {
                                q: "What level are these for?",
                                a: "Intermediate developers who know the basics but want to build real, production-quality projects.",
                            },
                            {
                                q: "Can I get a refund?",
                                a: "Yes, 30-day money-back guarantee. No questions asked.",
                            },
                            {
                                q: "Do I need prior experience with the specific tech?",
                                a: "No. Each course starts from zero in that technology. You just need general programming experience.",
                            },
                        ].map((faq) => (
                            <div
                                key={faq.q}
                                style={{
                                    padding: "16px",
                                    background: "#f8fafc",
                                    borderRadius: "8px",
                                }}
                            >
                                <p
                                    style={{
                                        fontWeight: "600",
                                        fontSize: "14px",
                                        color: "#111",
                                        marginBottom: "4px",
                                    }}
                                >
                                    {faq.q}
                                </p>
                                <p
                                    style={{
                                        fontSize: "14px",
                                        color: "#6b7280",
                                        margin: 0,
                                    }}
                                >
                                    {faq.a}
                                </p>
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
}
