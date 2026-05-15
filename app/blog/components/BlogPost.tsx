"use client";

import Navbar from "@/app/components/Navbar";
import Link from "next/link";

interface BlogPostProps {
    title: string;
    date: string;
    series: string;
    chapter: number;
    prevSlug?: string;
    prevTitle?: string;
    nextSlug?: string;
    nextTitle?: string;
    children: React.ReactNode;
}

export default function BlogPost({
    title,
    date,
    series,
    chapter,
    prevSlug,
    prevTitle,
    nextSlug,
    nextTitle,
    children,
}: BlogPostProps) {
    return (
        <div className="min-h-screen bg-white dark:bg-zinc-900">
            <Navbar />
            <article className="max-w-3xl mx-auto px-6 sm:px-10 lg:px-16 py-12">
                {/* Breadcrumb */}
                <div style={{ marginBottom: "24px", fontSize: "13px" }}>
                    <Link href="/blog" style={{ color: "#0d9488", textDecoration: "none" }}>
                        ← Blog
                    </Link>
                    <span style={{ color: "#9ca3af", margin: "0 8px" }}>/</span>
                    <span style={{ color: "#6b7280" }}>{series}</span>
                    <span style={{ color: "#9ca3af", margin: "0 8px" }}>/</span>
                    <span style={{ color: "#6b7280" }}>Chapter {chapter}</span>
                </div>

                {/* Title */}
                <h1 style={{ fontSize: "28px", fontWeight: "bold", color: "#111827", marginBottom: "8px", lineHeight: 1.3 }}>
                    {title}
                </h1>
                <div style={{ fontSize: "13px", color: "#6b7280", marginBottom: "32px" }}>
                    {date} • {series}
                </div>

                {/* Content */}
                <div className="blog-content" style={{ fontSize: "15px", lineHeight: 1.8, color: "#374151" }}>
                    {children}
                </div>

                {/* Navigation */}
                <nav style={{ marginTop: "48px", paddingTop: "24px", borderTop: "1px solid #e5e7eb", display: "flex", justifyContent: "space-between" }}>
                    {prevSlug ? (
                        <Link href={`/blog/${prevSlug}`} style={{ color: "#0d9488", textDecoration: "none", fontSize: "14px" }}>
                            ← {prevTitle}
                        </Link>
                    ) : <span />}
                    {nextSlug ? (
                        <Link href={`/blog/${nextSlug}`} style={{ color: "#0d9488", textDecoration: "none", fontSize: "14px" }}>
                            {nextTitle} →
                        </Link>
                    ) : <span />}
                </nav>
            </article>
        </div>
    );
}
