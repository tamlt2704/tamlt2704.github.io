"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
    { href: "/", label: "Home" },
    { href: "/blog", label: "Blog" },
    { href: "/about", label: "About" },
];

export default function Navbar() {
    const pathname = usePathname();

    return (
        <nav style={{ borderBottom: "1px solid #ddd", padding: "12px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", background: "white" }}>
            <Link href="/" style={{ fontWeight: 700, fontSize: "18px", color: "black", textDecoration: "none" }}>
                tamlt2704
            </Link>
            <div style={{ display: "flex", gap: "24px" }}>
                {links.map((link) => (
                    <Link
                        key={link.href}
                        href={link.href}
                        style={{
                            color: "black",
                            textDecoration: pathname === link.href ? "underline" : "none",
                            fontSize: "14px",
                        }}
                    >
                        {link.label}
                    </Link>
                ))}
            </div>
        </nav>
    );
}
