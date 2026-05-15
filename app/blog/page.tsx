"use client";

import Navbar from "@/app/components/Navbar";
import NewsletterSignup from "@/app/components/NewsletterSignup";
import { useState } from "react";

const REPO = "https://github.com/tamlt2704/tamlt2704.github.io/blob/main";

interface Series {
    title: string;
    description: string;
    chapters: number;
    path: string;
    tags: string[];
    accent: string;
}

const series: Series[] = [
    {
        title: "Pymunk + Manim",
        description: "Physics animations in Python. Balls bounce, pendulums swing, gears turn.",
        chapters: 13,
        path: "bcode/pymunk-manim",
        tags: ["python", "physics", "animation"],
        accent: "border-l-teal-500",
    },
    {
        title: "Emacs LLM",
        description: "Build a local Q&A model from scratch. Trained on the Emacs manual, runs on CPU.",
        chapters: 15,
        path: "bcode/emacs-llm",
        tags: ["python", "pytorch", "llm", "rag"],
        accent: "border-l-purple-500",
    },
    {
        title: "Python Dark Arts",
        description: "Advanced metaprogramming. Decorators, descriptors, metaclasses — write less, do more.",
        chapters: 16,
        path: "bcode/python-dark-arts",
        tags: ["python", "metaprogramming"],
        accent: "border-l-rose-500",
    },
    {
        title: "Ursina Mastery",
        description: "3D games in Python the easy way. Textures, lighting, collisions, audio.",
        chapters: 16,
        path: "bcode/ursina-mastery",
        tags: ["python", "3d", "gamedev"],
        accent: "border-l-amber-500",
    },
    {
        title: "Pygame Mastery",
        description: "From blank window to shipped game. Movement, collisions, particles, polish.",
        chapters: 16,
        path: "bcode/pygame-mastery",
        tags: ["python", "2d", "gamedev"],
        accent: "border-l-green-500",
    },
    {
        title: "OOP Python",
        description: "From scripts to systems. Refactor chaos into clean architecture.",
        chapters: 16,
        path: "bcode/oop-python",
        tags: ["python", "oop", "design"],
        accent: "border-l-pink-500",
    },
    {
        title: "Java Virtual Threads",
        description: "Concurrency without the pain. From thread pool wall to million-thread servers.",
        chapters: 13,
        path: "bcode/java-virtual-threads",
        tags: ["java", "concurrency"],
        accent: "border-l-blue-500",
    },
    {
        title: "Java GC",
        description: "From GC pauses to GC mastery. Tame the garbage collector.",
        chapters: 13,
        path: "bcode/java-gc",
        tags: ["java", "performance"],
        accent: "border-l-orange-500",
    },
    {
        title: "Java Time",
        description: "Dates, zones, and durations done right. Never get bitten by DST again.",
        chapters: 13,
        path: "bcode/java-time",
        tags: ["java", "datetime"],
        accent: "border-l-sky-500",
    },
    {
        title: "Probabilistic Programming",
        description: "Thinking in distributions. Bayesian inference with PyMC.",
        chapters: 16,
        path: "bcode/probabilistic",
        tags: ["python", "statistics", "bayesian"],
        accent: "border-l-cyan-500",
    },
    {
        title: "n8n Mastery",
        description: "Workflow automation that actually works. From first webhook to production.",
        chapters: 16,
        path: "bcode/n8n-mastery",
        tags: ["automation", "n8n", "workflows"],
        accent: "border-l-indigo-500",
    },
    {
        title: "Game Theory",
        description: "Strategic thinking in code. Nash equilibria, auctions, mechanism design.",
        chapters: 16,
        path: "bcode/game-theory",
        tags: ["python", "economics", "strategy"],
        accent: "border-l-red-500",
    },
];

export default function BlogPage() {
    const [showNewsletter, setShowNewsletter] = useState(false);

    return (
        <div className="min-h-screen bg-white">
            <Navbar />
            <main className="max-w-3xl mx-auto px-6 py-16">
                <h1 className="text-3xl font-bold text-gray-900">Blog</h1>
                <p className="mt-2 text-gray-500">
                    Series-based tutorials on building real things.
                </p>

                <div className="mt-12 flex flex-col gap-5">
                    {series.map((s) => (
                        <a
                            key={s.path}
                            href={`${REPO}/${s.path}/README.md`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="group block"
                        >
                            <article className={`border-l-4 ${s.accent} bg-white border border-gray-100 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow duration-200`}>
                                <h2 className="text-lg font-semibold text-gray-900 group-hover:text-teal-600 transition-colors">
                                    {s.title}
                                    <span className="ml-2 text-xs font-normal text-gray-400">
                                        · {s.chapters} chapters
                                    </span>
                                </h2>
                                <p className="mt-2 text-sm text-gray-600 leading-relaxed">
                                    {s.description}
                                </p>
                                <div className="mt-3 flex gap-2 flex-wrap">
                                    {s.tags.map((tag) => (
                                        <span key={tag} className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </article>
                        </a>
                    ))}
                </div>

                <div className="mt-16">
                    {!showNewsletter ? (
                        <button
                            onClick={() => setShowNewsletter(true)}
                            className="text-sm text-gray-400 hover:text-teal-600 transition-colors"
                        >
                            Subscribe to updates →
                        </button>
                    ) : (
                        <div className="relative">
                            <button
                                onClick={() => setShowNewsletter(false)}
                                className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 text-lg"
                            >
                                ×
                            </button>
                            <NewsletterSignup />
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
