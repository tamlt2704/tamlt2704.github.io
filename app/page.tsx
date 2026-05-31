import Link from "next/link";

const GAMES = [
  { href: "/games/matching", label: "🃏 Memory Match", desc: "Icon matching game with topics" },
  { href: "/games/chinese", label: "🀄 Learn Chinese", desc: "Hanzi, pinyin & stroke practice" },
  { href: "/games/physics", label: "⚛️ Physics Lab", desc: "Matter.js simulations" },
  { href: "/games/food-order", label: "🍽️ Food Order", desc: "Order & cook SG/VN dishes!" },
  { href: "/games/photo-booth", label: "📸 Photo Booth", desc: "Fun frames, stickers & effects!" },
];

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 py-16">
      <div className="text-center">
        <h1 className="bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-5xl font-extrabold text-transparent">
          Learn by Doing
        </h1>
        <p className="mt-4 text-lg text-gray-400">
          Interactive tutorials with quizzes, code playgrounds, and visualizers.
        </p>
        <Link
          href="/blog"
          className="mt-8 inline-block rounded-full bg-teal-500 px-8 py-3 font-medium text-white shadow-lg shadow-teal-500/30 transition hover:bg-teal-400 hover:shadow-teal-400/40"
        >
          Browse Blog →
        </Link>
      </div>

      <div className="mt-16 grid w-full max-w-3xl gap-4 sm:grid-cols-3">
        {GAMES.map((g) => (
          <Link
            key={g.href}
            href={g.href}
            className="rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900 to-gray-950 p-5 text-center transition-all hover:-translate-y-1 hover:border-teal-500/50 hover:shadow-lg hover:shadow-teal-500/10"
          >
            <span className="text-2xl">{g.label.split(" ")[0]}</span>
            <h3 className="mt-2 font-semibold">{g.label.slice(g.label.indexOf(" ") + 1)}</h3>
            <p className="mt-1 text-sm text-gray-400">{g.desc}</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
