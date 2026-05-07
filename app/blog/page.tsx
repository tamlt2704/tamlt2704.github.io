import Navbar from "@/app/components/Navbar";
import NewsletterSignup from "@/app/components/NewsletterSignup";
import Link from "next/link";

interface BlogPost {
    slug: string;
    title: string;
    description: string;
    date: string;
    series: string;
    tags: string[];
}

const posts: BlogPost[] = [
    {
        slug: "jobengine-mobile-00-setup",
        title: "React Native from Scratch: Setting Up Your Mobile Workbench",
        description: "Expo, simulators, Android Studio, Xcode — everything you need to start building a React Native app from zero.",
        date: "2026-05-01",
        series: "Job Engine Mobile",
        tags: ["react-native", "expo", "setup"],
    },
    {
        slug: "jobengine-mobile-01-first-screen",
        title: "First Screen: Navigation & Core Components",
        description: "React Native isn't React DOM. Learn the mental shift from div/h1/button to View/Text/Pressable, and set up type-safe navigation.",
        date: "2026-05-02",
        series: "Job Engine Mobile",
        tags: ["react-native", "react-navigation", "typescript"],
    },
    {
        slug: "jobengine-mobile-02-native-styling",
        title: "Native Styling: Building a Job List That Feels Native",
        description: "StyleSheet, FlatList, platform-specific shadows, pull-to-refresh, and safe areas — making your app feel like it belongs on the device.",
        date: "2026-05-03",
        series: "Job Engine Mobile",
        tags: ["react-native", "stylesheet", "flatlist"],
    },
    {
        slug: "jobengine-mobile-03-data-fetching",
        title: "Data Fetching: Talking to the Backend",
        description: "TanStack Query on mobile — caching, retry logic, background refetch, and handling the app lifecycle.",
        date: "2026-05-04",
        series: "Job Engine Mobile",
        tags: ["react-native", "tanstack-query", "api"],
    },
    {
        slug: "jobengine-mobile-04-realtime-push",
        title: "Real-time & Push Notifications: Never Miss a Job",
        description: "SSE for foreground updates, push notifications for background — two systems that keep users informed without polling.",
        date: "2026-05-05",
        series: "Job Engine Mobile",
        tags: ["react-native", "sse", "push-notifications", "firebase"],
    },
    {
        slug: "jobengine-mobile-05-performance",
        title: "Performance: Silky Smooth at 10,000 Jobs",
        description: "React.memo, FlatList tuning, Hermes engine, infinite scroll — making a list of 10,000 items scroll at 60fps.",
        date: "2026-05-06",
        series: "Job Engine Mobile",
        tags: ["react-native", "performance", "hermes", "flatlist"],
    },
    {
        slug: "jobengine-mobile-06-gestures-animations",
        title: "Gestures & Animations: Swipe, Drag, Delight",
        description: "React Native Gesture Handler + Reanimated 3 — swipe-to-cancel, long press menus, and 60fps animations on the UI thread.",
        date: "2026-05-07",
        series: "Job Engine Mobile",
        tags: ["react-native", "reanimated", "gestures", "animations"],
    },
    {
        slug: "jobengine-mobile-07-offline-persistence",
        title: "Offline & Persistence: Works Without WiFi",
        description: "MMKV storage, offline mutation queues, optimistic updates, and sync-on-reconnect — the app works in elevators.",
        date: "2026-05-08",
        series: "Job Engine Mobile",
        tags: ["react-native", "offline", "mmkv", "persistence"],
    },
    {
        slug: "jobengine-mobile-08-authentication",
        title: "Authentication: Secure Storage & Biometrics",
        description: "Keychain, Face ID, JWT refresh, role-based UI, deep links, and session timeout — production-grade mobile auth.",
        date: "2026-05-09",
        series: "Job Engine Mobile",
        tags: ["react-native", "authentication", "biometrics", "jwt"],
    },
    {
        slug: "jobengine-mobile-09-dag-visualization",
        title: "DAG Visualization: The Pipeline on Your Palm",
        description: "Rendering a directed acyclic graph with SVG, pan/zoom gestures, and a mobile-optimized vertical fallback.",
        date: "2026-05-10",
        series: "Job Engine Mobile",
        tags: ["react-native", "svg", "dag", "visualization"],
    },
    {
        slug: "jobengine-mobile-10-responsive-screens",
        title: "Multiple Screens: Phone, Tablet, Foldable",
        description: "Adaptive navigation, master-detail layouts, responsive grids, and foldable device support — one app, every screen size.",
        date: "2026-05-11",
        series: "Job Engine Mobile",
        tags: ["react-native", "responsive", "tablet", "foldable"],
    },
    {
        slug: "jobengine-mobile-11-charts-analytics",
        title: "Charts & Analytics: Visualize the Data",
        description: "Line charts, pie charts, bar charts, KPI cards — building an analytics dashboard the CEO can understand in 10 seconds.",
        date: "2026-05-12",
        series: "Job Engine Mobile",
        tags: ["react-native", "charts", "analytics", "data-visualization"],
    },
    {
        slug: "jobengine-mobile-12-production-release",
        title: "Production Release: Ship It to the App Store",
        description: "EAS Build, code signing, OTA updates, Sentry crash reporting, and CI/CD — from simulator to App Store.",
        date: "2026-05-13",
        series: "Job Engine Mobile",
        tags: ["react-native", "eas", "deployment", "ci-cd"],
    },
];

export default function BlogPage() {
    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900">
            <Navbar />
            <div className="max-w-3xl mx-auto px-4 py-12">
                <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "#111", marginBottom: "8px" }}>
                    Blog
                </h1>
                <p style={{ color: "#666", fontSize: "15px", marginBottom: "40px" }}>
                    Tutorials and deep dives on building real software.
                </p>

                {/* Series Header */}
                <div style={{ marginBottom: "32px", padding: "16px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                    <h2 style={{ fontSize: "18px", fontWeight: "600", color: "#1e293b", marginBottom: "4px" }}>
                        📱 Job Engine Mobile — React Native Series
                    </h2>
                    <p style={{ color: "#64748b", fontSize: "14px", margin: 0 }}>
                        Build a production mobile app from zero to App Store. 13 chapters covering navigation, data fetching, push notifications, offline support, authentication, charts, and deployment.
                    </p>
                </div>

                {/* Post List */}
                <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                    {posts.map((post, index) => (
                        <Link
                            key={post.slug}
                            href={`/blog/${post.slug}`}
                            style={{ textDecoration: "none" }}
                        >
                            <article style={{ padding: "16px", borderRadius: "8px", border: "1px solid #e5e7eb", transition: "border-color 0.2s" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                                    <span style={{ fontSize: "12px", color: "#6b7280", fontFamily: "monospace" }}>
                                        Ch {index}
                                    </span>
                                    <span style={{ fontSize: "12px", color: "#9ca3af" }}>•</span>
                                    <span style={{ fontSize: "12px", color: "#6b7280" }}>
                                        {post.date}
                                    </span>
                                </div>
                                <h3 style={{ fontSize: "16px", fontWeight: "600", color: "#111827", marginBottom: "4px" }}>
                                    {post.title}
                                </h3>
                                <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
                                    {post.description}
                                </p>
                                <div style={{ display: "flex", gap: "6px", marginTop: "8px", flexWrap: "wrap" }}>
                                    {post.tags.map((tag) => (
                                        <span
                                            key={tag}
                                            style={{ fontSize: "11px", color: "#3b82f6", background: "#eff6ff", padding: "2px 6px", borderRadius: "4px" }}
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </article>
                        </Link>
                    ))}
                </div>

                {/* Newsletter CTA */}
                <div style={{ marginTop: "48px" }}>
                    <NewsletterSignup />
                </div>
            </div>
        </div>
    );
}
