import Link from "next/link";

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 border-b border-gray-800 bg-gray-900/80 px-6 py-4 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between">
        <Link href="/" className="text-lg font-bold text-white">
          {/*Tam&apos;s Blog*/}
        </Link>
        <div className="flex gap-6 text-sm">
          <Link href="/" className="text-gray-400 transition hover:text-white">
            Home
          </Link>
          <Link href="/blog" className="text-gray-400 transition hover:text-white">
            Blog
          </Link>
        </div>
      </div>
    </nav>
  );
}
