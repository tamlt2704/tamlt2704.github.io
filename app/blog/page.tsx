import Link from "next/link";
import { getAllSeries } from "@/lib/markdown";

const CARD_COLORS = [
  "from-teal-500/20 to-teal-600/5 border-teal-500/30 hover:border-teal-400",
  "from-purple-500/20 to-purple-600/5 border-purple-500/30 hover:border-purple-400",
  "from-amber-500/20 to-amber-600/5 border-amber-500/30 hover:border-amber-400",
  "from-rose-500/20 to-rose-600/5 border-rose-500/30 hover:border-rose-400",
  "from-blue-500/20 to-blue-600/5 border-blue-500/30 hover:border-blue-400",
  "from-emerald-500/20 to-emerald-600/5 border-emerald-500/30 hover:border-emerald-400",
];

export default function BlogIndex() {
  const series = getAllSeries();
  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="mb-10 text-4xl font-bold">Blog</h1>
      <div className="grid gap-5 sm:grid-cols-2">
        {series.map((s, i) => (
          <Link
            key={s.slug}
            href={`/blog/${s.slug}/${s.chapters[0].replace(".md", "")}`}
            className={`group rounded-xl border bg-gradient-to-br p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg ${CARD_COLORS[i % CARD_COLORS.length]}`}
          >
            <h2 className="text-lg font-semibold capitalize">{s.slug.replace(/-/g, " ")}</h2>
            <p className="mt-2 text-sm opacity-60">
              {s.chapters.length} {s.chapters.length === 1 ? "chapter" : "chapters"}
            </p>
          </Link>
        ))}
      </div>
    </main>
  );
}
