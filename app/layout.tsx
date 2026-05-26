import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tam's blog",
  description: "Learn by doing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <nav className="sticky top-0 z-50 border-b border-gray-800 bg-gray-900/80 px-6 py-4 backdrop-blur-md">
          <div className="mx-auto flex max-w-5xl items-center justify-between">
            <Link href="/" className="text-lg font-bold text-white">
              Tam&apos;s Blog
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
        {children}
      </body>
    </html>
  );
}
