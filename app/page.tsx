import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-[80vh] items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="px-6 text-center">
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
    </main>
  );
}
