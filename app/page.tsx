import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto">
          <header className="text-center mb-16">
            <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            </h1>
            <p className="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
              Exploring the intersection of code and creativity through interactive experiences and generative art.
            </p>
          </header>

          <section className="mb-16">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-8 text-center">
              Projects
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <Link href="/nature-of-code" className="group">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-transform hover:scale-105">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                    Nature of Code
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Interactive p5.js sketches exploring physics, algorithms, and natural phenomena.
                  </p>
                  <span className="text-blue-600 dark:text-blue-400 font-medium group-hover:underline">
                    View Sketches →
                  </span>
                </div>
              </Link>
              
              <Link href="/gallery" className="group">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-transform hover:scale-105">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                    Photo Gallery
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    A collection of photos displayed in an interactive grid layout.
                  </p>
                  <span className="text-blue-600 dark:text-blue-400 font-medium group-hover:underline">
                    View Gallery →
                  </span>
                </div>
              </Link>
              
              <Link href="/opendata" className="group">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-transform hover:scale-105">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                    Open Data
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Interactive data visualization with charts, tables, and statistics.
                  </p>
                  <span className="text-blue-600 dark:text-blue-400 font-medium group-hover:underline">
                    View Data →
                  </span>
                </div>
              </Link>
            </div>
          </section>

          <section className="text-center">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-8">
              Get In Touch
            </h2>
            <div className="flex justify-center space-x-6">
              <a href="mailto:contact@example.com" className="text-blue-600 dark:text-blue-400 hover:underline">
                Email
              </a>
              <a href="https://github.com" className="text-blue-600 dark:text-blue-400 hover:underline">
                GitHub
              </a>
              <a href="https://linkedin.com" className="text-blue-600 dark:text-blue-400 hover:underline">
                LinkedIn
              </a>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
