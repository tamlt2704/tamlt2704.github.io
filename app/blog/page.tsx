import Link from "next/link";
import { getAllSeries } from "@/lib/markdown";

export default function BlogIndex() {
  const series = getAllSeries();
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="mb-8 text-3xl font-bold text-white">Blog</h1>
      <div className="space-y-4">
        {series.map((s) => (
          <Link
            key={s.slug}
            href={`/blog/${s.slug}/${s.chapters[0].replace(".md", "")}`}
            className="block rounded-lg border-gray-800 bg-gray-900 p-5 transition hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10"
          >
            <h2 className="font-semibold text-white">{s.slug.replace(/-/g, " ")}</h2>
            <p className="mt-1 text-sm text-gray-500">{s.chapters.length} chapters</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
