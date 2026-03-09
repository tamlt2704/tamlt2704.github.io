import Image from "next/image";
import Navbar from "@/app/components/Navbar.txs";

export default function Home() {
  return (
    <div className="min-h-screen bg-white dark:bg-zinc-900">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-16">
        {/* Your blog content here */}
      </main>
    </div>
  );
}
