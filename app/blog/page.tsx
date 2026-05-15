"use client";

import Navbar from "@/app/components/Navbar";
import { useState } from "react";

const REPO = "https://github.com/tamlt2704/tamlt2704.github.io/blob/main";

interface Series {
    title: string;
    description: string;
    path: string;
    tags: string[];
}

const series: Series[] = [
    // acode
    { title: "Algorithms", description: "From linear search to production systems at a logistics startup.", path: "acode/algorithms", tags: ["python", "algorithms"] },
    { title: "Anime.js Mastery", description: "Luxury-grade motion. 14KB. No dependencies.", path: "acode/animejs-mastery", tags: ["javascript", "animation"] },
    { title: "Defold 101", description: "Game jam survival. 72 hours. Ship or die.", path: "acode/defold101", tags: ["gamedev", "lua"] },
    { title: "Docker 101", description: "Visual Docker explanations animated with Manim.", path: "acode/docker101", tags: ["devops", "docker", "manim"] },
    { title: "Emacs Rocks", description: "Short episodes. One trick each. Instantly useful.", path: "acode/emacs101", tags: ["emacs"] },
    { title: "FastAPI", description: "Build APIs fast with Python's modern framework.", path: "acode/fastapi", tags: ["python", "api"] },
    { title: "Firebase Mastery", description: "Three co-founders. No backend. Six weeks to demo day.", path: "acode/firebase-mastery", tags: ["firebase", "serverless"] },
    { title: "GitHub Workflows", description: "CI/CD from first push to advanced workflows.", path: "acode/ghworkflow", tags: ["devops", "github"] },
    { title: "Google OR-Tools", description: "Operations research and optimization.", path: "acode/google-or", tags: ["python", "optimization"] },
    { title: "Gradle Mastery", description: "Multi-module builds that don't fight you.", path: "acode/gradle-mastery", tags: ["java", "build"] },
    { title: "Intro to Manim", description: "Step-by-step Manim scripts. Render, watch, learn.", path: "acode/intro-to-manim", tags: ["python", "manim", "animation"] },
    { title: "Isometric JS", description: "Build an isometric city builder from scratch with Canvas.", path: "acode/isometric-js", tags: ["javascript", "gamedev"] },
    { title: "Job Engine", description: "The intern's tale. Build a job engine that works.", path: "acode/jobengine", tags: ["java", "spring"] },
    { title: "Kafka Mastery", description: "12,000 trucks. GPS every 5 seconds. Replace polling.", path: "acode/kafka-mastery", tags: ["java", "kafka", "streaming"] },
    { title: "LangChain Mastery", description: "AI legal research assistant, built disaster by disaster.", path: "acode/langchain-mastery", tags: ["python", "llm", "ai"] },
    { title: "LeetCode", description: "112 problems with Python stubs and test cases.", path: "acode/leetcode", tags: ["python", "algorithms"] },
    { title: "Matplotlib 101", description: "Karen needs a chart. You have data. Build it.", path: "acode/matplotlib101", tags: ["python", "dataviz"] },
    { title: "Modern Java", description: "Upgrade from Java 11 to 21. Kill the instanceof chains.", path: "acode/modernjava", tags: ["java"] },
    { title: "Monetization Playbook", description: "Building income streams from technical content.", path: "acode/monetization-playbook", tags: ["business"] },
    { title: "OpenCV Mastery", description: "Teach a machine to see. Automated parking system.", path: "acode/opencv-mastery", tags: ["python", "cv", "ai"] },
    { title: "Org Mode", description: "Plain text that does everything. Grep your life.", path: "acode/org-mode", tags: ["emacs", "productivity"] },
    { title: "Pandas 101", description: "Animated video series. One concept per video.", path: "acode/pandas101", tags: ["python", "data", "manim"] },
    { title: "Pixi React", description: "Pixel art games with React. 48-hour game jam.", path: "acode/pixi-react", tags: ["react", "gamedev"] },
    { title: "Playwright", description: "Production-grade E2E tests from scratch.", path: "acode/playwright", tags: ["testing", "typescript"] },
    { title: "PostgreSQL Mastery", description: "Your database is on fire. The DBA quit. Fix it.", path: "acode/postgres-mastery", tags: ["database", "postgres"] },
    { title: "Procedural Assets", description: "Generate infinite game assets from algorithms.", path: "acode/procgen-assets", tags: ["python", "gamedev", "procedural"] },
    { title: "PydanticAI", description: "Type-safe AI agents. Rewrite chaos into production.", path: "acode/pydantic-ai", tags: ["python", "ai"] },
    { title: "Pytest Mastery", description: "Tests that catch bugs. Fintech invoicing platform.", path: "acode/pytest-mastery", tags: ["python", "testing"] },
    { title: "Python Mastery", description: "Advanced Python techniques and patterns.", path: "acode/python-mastery", tags: ["python"] },
    { title: "Redis 101", description: "From first key to production cluster.", path: "acode/redis101", tags: ["database", "redis"] },
    { title: "Reinforcement Learning", description: "From random agents to model-based planning.", path: "acode/reinforcement-learning", tags: ["python", "ai", "rl"] },
    { title: "sklearn Story", description: "Machine learning with scikit-learn.", path: "acode/sklearn-story", tags: ["python", "ai", "ml"] },
    { title: "Spring AI", description: "AI integration with Spring Boot.", path: "acode/spring-ai", tags: ["java", "spring", "ai"] },
    { title: "Spring Integration", description: "Enterprise integration patterns with Spring.", path: "acode/spring-integration", tags: ["java", "spring"] },
    { title: "Spring Security", description: "Secure your Spring applications.", path: "acode/spring-security", tags: ["java", "spring", "security"] },
    { title: "Spring Batch", description: "Batch processing with Spring.", path: "acode/springbatch", tags: ["java", "spring"] },
    { title: "Sprite Animation", description: "Draw and animate pixel art sprites from scratch.", path: "acode/sprite-animation", tags: ["gamedev", "art"] },
    { title: "SQL Mastery", description: "Master SQL queries and database design.", path: "acode/sql-mastery", tags: ["database", "sql"] },
    { title: "Stripe Mastery", description: "From first charge to subscription empire.", path: "acode/stripe-mastery", tags: ["payments", "api"] },
    { title: "SVG Animation", description: "From static spinners to production motion design.", path: "acode/svg-animation", tags: ["javascript", "animation"] },
    { title: "System Design", description: "File-sharing startup went viral. Scale or die.", path: "acode/system-design", tags: ["architecture"] },
    { title: "Tailwind CSS", description: "Rewrite 4,000 lines of CSS chaos.", path: "acode/tailwind", tags: ["css", "frontend"] },
    { title: "Three.js Guide", description: "Build 3D experiences for the web.", path: "acode/threejsguide", tags: ["javascript", "3d"] },
    { title: "tmux", description: "One terminal. Infinite workspaces.", path: "acode/tmux", tags: ["devops", "terminal"] },
    { title: "TypeScript Story", description: "TypeScript patterns and advanced types.", path: "acode/typescript-story", tags: ["typescript"] },
    { title: "uv Mastery", description: "Modern Python package management.", path: "acode/uv-mastery", tags: ["python", "tooling"] },
    // bcode
    { title: "Algebra Quest", description: "Fantasy world where every puzzle runs on algebra.", path: "bcode/algebra-quest", tags: ["kids", "math"] },
    { title: "Chemistry Fun", description: "From atoms to explosions. Kitchen experiments.", path: "bcode/chemistry-fun", tags: ["kids", "science"] },
    { title: "Emacs Lisp", description: "Bend your editor to your will.", path: "bcode/emacs-lisp", tags: ["emacs", "lisp"] },
    { title: "Emacs LLM", description: "Build a local Q&A model from scratch on CPU.", path: "bcode/emacs-llm", tags: ["python", "llm", "ai"] },
    { title: "FlowCraft", description: "Visual integration platform. React Flow + Spring.", path: "bcode/flowcraft", tags: ["react", "java", "spring"] },
    { title: "Game Theory", description: "Nash equilibria, auctions, mechanism design.", path: "bcode/game-theory", tags: ["python", "strategy"] },
    { title: "Godot for Parents", description: "Make games with your kids on Saturday mornings.", path: "bcode/godot-for-parents", tags: ["gamedev", "kids"] },
    { title: "Home Automation", description: "Your house, your rules. Everything runs locally.", path: "bcode/home-automation", tags: ["iot", "automation"] },
    { title: "Java Collections", description: "From ArrayList to ConcurrentSkipListMap.", path: "bcode/java-collections", tags: ["java"] },
    { title: "Java Concurrency", description: "From threads to virtual threads. 2M events/sec.", path: "bcode/java-concurrency", tags: ["java", "concurrency"] },
    { title: "Java Design Patterns", description: "Gang of Four patterns in modern Java.", path: "bcode/java-design-patterns", tags: ["java", "patterns"] },
    { title: "Java GC", description: "From GC pauses to GC mastery.", path: "bcode/java-gc", tags: ["java", "performance"] },
    { title: "Java Time", description: "Dates, zones, durations. Never bitten by DST again.", path: "bcode/java-time", tags: ["java"] },
    { title: "Java Virtual Threads", description: "Million-thread concurrency. One incident at a time.", path: "bcode/java-virtual-threads", tags: ["java", "concurrency"] },
    { title: "LLM From Scratch", description: "Build a language model with your own hands.", path: "bcode/llm-from-scratch", tags: ["python", "ai", "llm"] },
    { title: "Manim IDE", description: "Teach programming visually with animated IDE.", path: "bcode/manim-ide", tags: ["python", "manim", "animation"] },
    { title: "MongoDB Mastery", description: "Documents to production clusters.", path: "bcode/mongodb-mastery", tags: ["database", "mongodb"] },
    { title: "n8n Mastery", description: "Workflow automation that actually works.", path: "bcode/n8n-mastery", tags: ["automation", "n8n"] },
    { title: "OOP Python", description: "From scripts to systems. Clean architecture.", path: "bcode/oop-python", tags: ["python", "oop"] },
    { title: "Personal Finance", description: "Automate your money with Python.", path: "bcode/personal-finance-code", tags: ["python", "finance"] },
    { title: "Physics Fun", description: "Falling apples to orbiting planets. Simulations.", path: "bcode/physics-fun", tags: ["kids", "physics", "python"] },
    { title: "Pixel8", description: "Retro pixel art games drawn with code only.", path: "bcode/pixel8", tags: ["gamedev", "python"] },
    { title: "Probabilistic Programming", description: "Thinking in distributions. Bayesian inference.", path: "bcode/probabilistic", tags: ["python", "statistics"] },
    { title: "Prolog", description: "Logic programming. Automated compliance checker.", path: "bcode/prolog", tags: ["prolog", "logic"] },
    { title: "Pygame Mastery", description: "From blank window to shipped game.", path: "bcode/pygame-mastery", tags: ["python", "gamedev"] },
    { title: "Pymunk + Manim", description: "Physics animations. Balls bounce, gears turn.", path: "bcode/pymunk-manim", tags: ["python", "manim", "physics"] },
    { title: "Python Dark Arts", description: "Decorators, descriptors, metaclasses.", path: "bcode/python-dark-arts", tags: ["python", "metaprogramming"] },
    { title: "PyTorch Mastery", description: "From tensors to production models.", path: "bcode/pytorch-mastery", tags: ["python", "ai", "pytorch"] },
    { title: "Pyxel Mastery", description: "Retro pixel art games in Python for the web.", path: "bcode/pyxel-mastery", tags: ["python", "gamedev"] },
    { title: "React Flow", description: "From nodes to production visual editors.", path: "bcode/reactflow", tags: ["react", "frontend"] },
    { title: "Side Income for Devs", description: "Ship products in stolen hours. 5-10h/week.", path: "bcode/side-income-dev", tags: ["business"] },
    { title: "Spring Tips", description: "The stuff they don't teach in tutorials.", path: "bcode/spring-tips", tags: ["java", "spring"] },
    { title: "SQLite", description: "The embedded database. Offline-first apps.", path: "bcode/sqlite", tags: ["database", "sqlite"] },
    { title: "Stock Strategy", description: "From data to decisions. Personal trading dashboard.", path: "bcode/stock-strategy", tags: ["python", "finance"] },
    { title: "System Design Interviews", description: "From blank whiteboard to offer.", path: "bcode/system-design-interviews", tags: ["architecture", "interviews"] },
    { title: "Tailwind Responsive", description: "From mobile to 4K. Every screen works.", path: "bcode/tailwind-responsive", tags: ["css", "frontend"] },
    { title: "Teach Kids to Code", description: "30-minute activities. No lectures, just building.", path: "bcode/teach-kids-code", tags: ["kids", "python"] },
    { title: "Ursina Mastery", description: "3D games in Python the easy way.", path: "bcode/ursina-mastery", tags: ["python", "3d", "gamedev"] },
];

export default function BlogPage() {
    const [filter, setFilter] = useState<string | null>(null);

    const allTags = [...new Set(series.flatMap((s) => s.tags))].sort();
    const filtered = filter ? series.filter((s) => s.tags.includes(filter)) : series;

    return (
        <div className="min-h-screen bg-white">
            <Navbar />
            <div className="max-w-6xl mx-auto px-6 py-10 flex gap-10">
                {/* Main content */}
                <main className="flex-1 min-w-0">
                    <p className="text-sm text-gray-400 mb-4">
                        {filter ? `#${filter} · ` : ""}{filtered.length} series
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {filtered.map((s) => (
                            <a
                                key={s.path}
                                href={`${REPO}/${s.path}/README.md`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="group block"
                            >
                                <article className="h-full rounded-lg p-4 bg-gray-50 border border-gray-200 hover:shadow-md hover:border-gray-300 transition-all duration-150">
                                    <h2 className="text-sm font-semibold text-gray-900 group-hover:text-teal-600">
                                        {s.title}
                                    </h2>
                                    <p className="mt-1.5 text-xs text-gray-500 leading-relaxed">
                                        {s.description}
                                    </p>
                                    <div className="mt-2.5 flex gap-1 flex-wrap">
                                        {s.tags.map((tag) => (
                                            <span
                                                key={tag}
                                                className="text-[10px] text-teal-700 bg-teal-50 px-1.5 py-0.5 rounded"
                                            >
                                                #{tag}
                                            </span>
                                        ))}
                                    </div>
                                </article>
                            </a>
                        ))}
                    </div>
                </main>

                {/* Categories sidebar */}
                <aside className="hidden lg:block w-44 shrink-0">
                    <div className="sticky top-20">
                        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Categories</p>
                        <ul className="flex flex-col gap-1">
                            <li>
                                <button
                                    type="button"
                                    onClick={() => setFilter(null)}
                                    className={!filter
                                        ? "text-xs font-medium text-gray-900"
                                        : "text-xs text-gray-500 hover:text-gray-800"
                                    }
                                >
                                    All ({series.length})
                                </button>
                            </li>
                            {allTags.map((tag) => {
                                const count = series.filter((s) => s.tags.includes(tag)).length;
                                return (
                                    <li key={tag}>
                                        <button
                                            type="button"
                                            onClick={() => setFilter(tag === filter ? null : tag)}
                                            className={filter === tag
                                                ? "text-xs font-medium text-teal-700"
                                                : "text-xs text-gray-500 hover:text-gray-800"
                                            }
                                        >
                                            {tag} ({count})
                                        </button>
                                    </li>
                                );
                            })}
                        </ul>
                    </div>
                </aside>
            </div>
        </div>
    );
}
