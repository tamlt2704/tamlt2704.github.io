export default function Navbar() {
    return (
        <nav className="border-b">
            <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
                <a href="/" className="text-xl font-bold"> Blog </a>
                <div className="flex gap-6"> 
                    <a href="/about" className="hover:text-blue-600"> About </a>
                    <a href="/blog" className="hover:text-blue-600"> Blog </a>
                </div>
            </div>
        </nav>
    )
}