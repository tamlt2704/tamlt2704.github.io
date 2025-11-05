import Link from "next/link";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  return (
    <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-gray-900 dark:text-white">
            Tam's blog
          </Link>
          <div className="flex items-center space-x-6">
            <Link href="/" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
              Home
            </Link>
            <Link href="/nature-of-code" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
              Nature of Code
            </Link>
            <Link href="/gallery" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
              Gallery
            </Link>
            <Link href="/opendata" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
              Open Data
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  );
}