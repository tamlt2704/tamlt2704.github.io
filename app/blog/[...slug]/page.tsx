import { notFound } from "next/navigation";
import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { MDXRemote } from "next-mdx-remote/rsc"; // Renders markdown string as React components (server-side, runs at build time)
import remarkGfm from "remark-gfm";
import { getSeriesChapters } from "@/lib/markdown";
import { MarkdownCode, MarkdownPre } from "@/app/blog/components/MarkdownCode";
import { Quiz } from "@/app/blog/components/Quiz";
import { CodePlayground } from "@/app/blog/components/CodePlayground";

// Next.js passes URL segments as params.
// For /blog/algorithms/chapter-01 → slug = ["algorithms", "chapter-01"]
interface Props {
  params: Promise<{ slug: string[] }>;
}

/**
 * generateStaticParams tells Next.js which pages to pre-build.
 * At build time, it scans all .md files and returns their URL paths.
 * Without this, Next.js wouldn't know what pages exist (since they're dynamic).
 */
export async function generateStaticParams() {
  const base = path.join(process.cwd(), "content");
  if (!fs.existsSync(base)) return [];

  const params: { slug: string[] }[] = [];
  const folders = fs.readdirSync(base, { withFileTypes: true }).filter((d) => d.isDirectory());

  for (const folder of folders) {
    const files = fs
      .readdirSync(path.join(base, folder.name))
      .filter((f) => f.endsWith(".md") && f !== "README.md");
    for (const file of files) {
      params.push({ slug: [folder.name, file.replace(/\.md$/, "")] });
    }
  }
  return params;
}

export default async function BlogPage({ params }: Props) {
  const { slug } = await params;
  if (slug.length < 2) return notFound();

  // Destructure: /blog/algorithms/chapter-01 → series="algorithms", fileSlug="chapter-01"
  const [series, fileSlug] = slug;
  const filePath = path.join(process.cwd(), "content", series, `${fileSlug}.md`);

  if (!fs.existsSync(filePath)) return notFound();

  const raw = fs.readFileSync(filePath, "utf8");
  const { content } = matter(raw); // content = the markdown text without frontmatter

  // build next/prev navigation links
  const chapters = getSeriesChapters(series);
  const currentFile = `${fileSlug}.md`;
  const idx = chapters.indexOf(currentFile);
  const prev = idx > 0 ? chapters[idx - 1] : null;
  const next = idx < chapters.length - 1 ? chapters[idx + 1] : null;

  return (
    <article className="mx-auto max-w-3xl px-6 py-12">
      {/* prose = Tailwind typography plugin, styles all HTML elements beautifully */}
      <div className="prose prose-lg max-w-none">
        <MDXRemote
          source={content}
          components={{
            code: MarkdownCode,
            pre: MarkdownPre,
            // Strip .md from links so relative chapter links work as Next.js routes
            a: ({ href, ...props }) => <a href={href?.replace(/\.md$/, "")} {...props} />,
            Quiz,
            CodePlayground,
          }}
          options={{
            mdxOptions: {
              remarkPlugins: [remarkGfm], // Enable tables, strikethrough, task lists
              format: "mdx", // Treat input as MDX to support JSX components like <Quiz />
            },
          }}
        />
      </div>
      {/* Prev / Next */}
      <nav className="mt-12 flex justify-between border-t pt-6 text-sm">
        {prev && (
          <a
            href={`/blog/${series}/${prev.replace(".md", "")}`}
            className="text-teal-600 hover:underline"
          >
            ← Previous
          </a>
        )}
        {next && (
          <a
            href={`/blog/${series}/${next.replace(".md", "")}`}
            className="ml-auto text-teal-600 hover:underline"
          >
            Next →
          </a>
        )}
      </nav>
    </article>
  );
}
