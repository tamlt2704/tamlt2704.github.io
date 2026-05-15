import { notFound } from "next/navigation";
import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { MDXRemote } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import Navbar from "@/app/components/Navbar";
import Link from "next/link";
import { getSeriesChapters } from "@/lib/markdown";
import { MarkdownCode, MarkdownPre } from "@/app/blog/components/MarkdownCode";

interface Props {
    params: Promise<{ slug: string[] }>;
}

export async function generateStaticParams() {
    const params: { slug: string[] }[] = [];
    const dirs = (process.env.CONTENT_DIRS || "acode,bcode").split(",").map(d => d.trim());

    for (const dir of dirs) {
        const base = path.join(process.cwd(), dir);
        if (!fs.existsSync(base)) continue;

        const folders = fs.readdirSync(base, { withFileTypes: true })
            .filter((d) => d.isDirectory());

        for (const folder of folders) {
            const folderPath = path.join(base, folder.name);
            let files: string[];
            try {
                files = fs.readdirSync(folderPath)
                    .filter((f) => f.endsWith(".md"));
            } catch {
                continue;
            }

            for (const file of files) {
                const fileSlug = file.replace(".md", "");
                params.push({ slug: [dir, folder.name, fileSlug] });
            }
        }
    }
    return params;
}

export default async function MarkdownPage({ params }: Props) {
    const { slug } = await params;
    // slug = ["bcode", "pymunk-manim", "chapter-00-setup"]
    if (slug.length < 3) return notFound();

    const [dir, series, fileSlug] = slug;
    const filePath = path.join(process.cwd(), dir, series, `${fileSlug}.md`);

    if (!fs.existsSync(filePath)) return notFound();

    const raw = fs.readFileSync(filePath, "utf-8");
    const { content, data } = matter(raw);

    // Get prev/next chapters
    const seriesDir = `${dir}/${series}`;
    const chapters = getSeriesChapters(seriesDir);
    const currentFile = `${fileSlug}.md`;
    const currentIndex = chapters.indexOf(currentFile);
    const prevChapter = currentIndex > 0 ? chapters[currentIndex - 1] : null;
    const nextChapter = currentIndex < chapters.length - 1 ? chapters[currentIndex + 1] : null;

    const title = content.split("\n").find((l) => l.startsWith("# "))?.replace("# ", "") || fileSlug;
    const seriesTitle = series.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

    return (
        <div className="min-h-screen bg-white">
            <Navbar />
            <article className="max-w-3xl mx-auto px-6 py-12">
                {/* Breadcrumb */}
                <div className="text-sm text-gray-500 mb-6">
                    <Link href="/blog" className="text-teal-600 hover:underline">Blog</Link>
                    <span className="mx-2">/</span>
                    <span>{seriesTitle}</span>
                    <span className="mx-2">/</span>
                    <span>{fileSlug}</span>
                </div>

                {/* Markdown content */}
                <div className="prose prose-gray prose-lg max-w-none prose-headings:text-gray-900 prose-a:text-teal-600">
                    <MDXRemote
                        source={content}
                        components={{
                            code: MarkdownCode,
                            pre: MarkdownPre,
                        }}
                        options={{
                            mdxOptions: {
                                remarkPlugins: [remarkGfm],
                                format: "md",
                            },
                        }}
                    />
                </div>

                {/* Prev / Next navigation */}
                <nav className="mt-12 pt-6 border-t border-gray-200 flex justify-between">
                    {prevChapter ? (
                        <Link
                            href={`/blog/${dir}/${series}/${prevChapter.replace(".md", "")}`}
                            className="text-sm text-teal-600 hover:underline"
                        >
                            ← {prevChapter.replace(".md", "").replace("chapter-", "Ch ")}
                        </Link>
                    ) : <span />}
                    {nextChapter ? (
                        <Link
                            href={`/blog/${dir}/${series}/${nextChapter.replace(".md", "")}`}
                            className="text-sm text-teal-600 hover:underline"
                        >
                            {nextChapter.replace(".md", "").replace("chapter-", "Ch ")} →
                        </Link>
                    ) : <span />}
                </nav>
            </article>
        </div>
    );
}
