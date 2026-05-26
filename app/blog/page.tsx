import Link from "next/link";
import { getAllSeries } from "@/lib/markdown";

export default function BlogIndex() {
  const series = getAllSeries();
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="mb-8 text-3xl font-bold">Blog</h1>
      <div className="space-y-4">
        {series.map((s) => (
          <Link
            key={s.slug}
            href={`/blog/${s.slug}/${s.chapters[0].replace(".md", "")}`}
            className="block rounded-lg border p-5 hover:border-teal-400"
          >
            <h2 className="font-semibold">{s.slug.replace(/-/g, " ")}</h2>
            <p className="text-sm text-gray-500">{s.chapters.length} chapters</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
