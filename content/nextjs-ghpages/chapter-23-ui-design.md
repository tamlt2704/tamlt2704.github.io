# Chapter 23: Building a Beautiful UI

[← Chapter 22: Gated Resources](/blog/nextjs-ghpages/chapter-22-gated-resources)

---

## The Difference

Two blogs with identical content. One looks like a default template. The other feels crafted — the navbar is clean, the course cards invite clicks, the typography breathes. Readers trust the second one more. They stay longer.

Good design isn't decoration. It's communication. Let's build a UI that communicates "this is worth your time."

## The Navbar

A navbar needs to do three things: show where you are, let you navigate, and stay out of the way.

Create `app/components/Navbar.tsx`:

```tsx
import Link from "next/link";
import { ThemeToggle } from "./ThemeToggle";
import { AuthButton } from "./AuthButton";
import { LangSwitcher } from "./LangSwitcher";

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md dark:border-gray-800 dark:bg-gray-950/80">
      <nav className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        {/* Left: Logo + site name */}
        <Link href="/" className="group flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-teal-400 to-teal-600">
            <span className="text-xs font-bold text-white">A</span>
          </div>
          <span className="hidden font-semibold text-gray-900 transition group-hover:text-teal-600 sm:inline dark:text-white">
            ACode
          </span>
        </Link>

        {/* Center: Main navigation */}
        <div className="hidden items-center gap-6 md:flex">
          <NavLink href="/blog">Courses</NavLink>
          <NavLink href="/resources">Resources</NavLink>
          <NavLink href="/about">About</NavLink>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <LangSwitcher />
          <ThemeToggle />
          <AuthButton />
        </div>
      </nav>
    </header>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="text-sm text-gray-600 transition hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
    >
      {children}
    </Link>
  );
}
```

### Design decisions:

- **`sticky top-0`** — stays visible on scroll without taking space
- **`backdrop-blur-md` + semi-transparent bg** — content shows through subtly, feels modern
- **`h-14`** — compact, doesn't waste mobile screen space
- **Hidden on mobile** — center nav hides below `md:`, use a hamburger or bottom nav instead
- **Logo as gradient square** — distinctive, works at any size, no image to load

### Mobile Navigation

Add a hamburger menu for mobile:

```tsx
"use client";

import { useState } from "react";
import Link from "next/link";

export function MobileMenu() {
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        onClick={() => setOpen(!open)}
        className="p-2 text-gray-600 dark:text-gray-400"
        aria-label="Menu"
      >
        {open ? (
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        )}
      </button>

      {open && (
        <div className="absolute top-14 right-0 left-0 space-y-3 border-b border-gray-200 bg-white p-4 dark:border-gray-800 dark:bg-gray-950">
          <MobileLink href="/blog" onClick={() => setOpen(false)}>
            Courses
          </MobileLink>
          <MobileLink href="/resources" onClick={() => setOpen(false)}>
            Resources
          </MobileLink>
          <MobileLink href="/about" onClick={() => setOpen(false)}>
            About
          </MobileLink>
        </div>
      )}
    </div>
  );
}

function MobileLink({
  href,
  children,
  onClick,
}: {
  href: string;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className="block py-2 text-base text-gray-700 hover:text-teal-600 dark:text-gray-300"
    >
      {children}
    </Link>
  );
}
```

## Course Cards

The landing page shows all available courses as cards. Each card needs: title, description, chapter count, and a visual hook.

Create `app/components/CourseCard.tsx`:

```tsx
import Link from "next/link";

interface Props {
  title: string;
  description: string;
  chapters: number;
  href: string;
  icon: string; // emoji or icon
  color: string; // accent color class like "from-teal-400 to-teal-600"
  tags?: string[];
}

export function CourseCard({ title, description, chapters, href, icon, color, tags }: Props) {
  return (
    <Link href={href} className="group block">
      <div className="relative overflow-hidden rounded-xl border border-gray-200 bg-white p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-gray-300 hover:shadow-lg dark:border-gray-800 dark:bg-gray-900 dark:hover:border-gray-700">
        {/* Gradient accent bar */}
        <div className={`absolute top-0 right-0 left-0 h-1 bg-gradient-to-r ${color}`} />

        {/* Icon */}
        <div className="mb-3 text-3xl">{icon}</div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 transition group-hover:text-teal-600 dark:text-white dark:group-hover:text-teal-400">
          {title}
        </h3>

        {/* Description */}
        <p className="mt-2 line-clamp-2 text-sm text-gray-600 dark:text-gray-400">{description}</p>

        {/* Footer: tags + chapter count */}
        <div className="mt-4 flex items-center justify-between">
          <div className="flex gap-1.5">
            {tags?.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-400"
              >
                {tag}
              </span>
            ))}
          </div>
          <span className="text-xs text-gray-400">{chapters} chapters</span>
        </div>
      </div>
    </Link>
  );
}
```

### Design decisions:

- **`hover:-translate-y-0.5` + `hover:shadow-lg`** — card lifts on hover, feels interactive
- **Gradient accent bar** — each course has a unique color, visual variety
- **`line-clamp-2`** — description never overflows, consistent card height
- **Tags** — quick scan of what the course covers
- **Group hover** — title changes color when hovering anywhere on the card

## The Course Grid

```tsx
// app/page.tsx or app/blog/page.tsx
import { CourseCard } from "@/app/components/CourseCard";

const COURSES = [
  {
    title: "Next.js GitHub Pages",
    description: "Build a free interactive blog with markdown, quizzes, and code playgrounds.",
    chapters: 23,
    href: "/blog/en/nextjs-ghpages/chapter-00-overview",
    icon: "🚀",
    color: "from-teal-400 to-cyan-500",
    tags: ["Next.js", "React", "Tailwind"],
  },
  {
    title: "Algorithms & Data Structures",
    description: "From linear search to dynamic programming. Real problems, real code.",
    chapters: 15,
    href: "/blog/en/algorithms/chapter-00-overview",
    icon: "🧮",
    color: "from-purple-400 to-pink-500",
    tags: ["Python", "Interviews", "CS"],
  },
  {
    title: "Docker 101",
    description: "Containers, images, compose, and production deployment.",
    chapters: 10,
    href: "/blog/en/docker101/docker-101-guide",
    icon: "🐳",
    color: "from-blue-400 to-indigo-500",
    tags: ["DevOps", "Docker", "Linux"],
  },
  // ... more courses
];

export default function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
      {/* Hero */}
      <section className="mb-16 text-center">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl dark:text-white">
          Learn by Building
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
          Free programming courses with interactive quizzes, code playgrounds, and step-by-step
          visualizations. No signup required.
        </p>
      </section>

      {/* Course grid */}
      <section>
        <h2 className="mb-6 text-sm font-semibold tracking-wide text-gray-500 uppercase dark:text-gray-400">
          Courses
        </h2>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {COURSES.map((course) => (
            <CourseCard key={course.href} {...course} />
          ))}
        </div>
      </section>
    </main>
  );
}
```

### The grid:

- **1 column** on mobile (< 640px)
- **2 columns** on tablet (640–1023px)
- **3 columns** on desktop (1024px+)
- **`gap-5`** — breathing room between cards

## Component Styling Patterns

### The Card Pattern (reusable)

```tsx
function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={`rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900 ${className}`}
    >
      {children}
    </div>
  );
}
```

Use it everywhere:

```tsx
<Card>Quiz content</Card>
<Card className="hover:shadow-lg transition">Clickable card</Card>
<Card className="border-teal-200 bg-teal-50 dark:bg-teal-900/20">Highlighted card</Card>
```

### The Badge Pattern

```tsx
function Badge({
  children,
  variant = "default",
}: {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning";
}) {
  const styles = {
    default: "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400",
    success: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400",
    warning: "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400",
  };

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[variant]}`}
    >
      {children}
    </span>
  );
}
```

### The Button Pattern

```tsx
interface ButtonProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  onClick?: () => void;
  disabled?: boolean;
}

function Button({ children, variant = "primary", size = "md", onClick, disabled }: ButtonProps) {
  const base =
    "inline-flex items-center justify-center font-medium rounded-lg transition disabled:opacity-50";

  const variants = {
    primary: "bg-teal-600 text-white hover:bg-teal-700 shadow-sm",
    secondary:
      "border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800",
    ghost:
      "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-6 py-3 text-base",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${sizes[size]}`}
    >
      {children}
    </button>
  );
}
```

## The Footer

```tsx
export function Footer() {
  return (
    <footer className="mt-20 border-t border-gray-200 dark:border-gray-800">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="grid gap-8 sm:grid-cols-3">
          {/* Brand */}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">ACode</h3>
            <p className="mt-2 text-sm text-gray-500">
              Free interactive programming courses. Learn by building real things.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-sm font-semibold text-gray-500 uppercase">Courses</h4>
            <ul className="mt-3 space-y-2">
              <li>
                <FooterLink href="/blog/en/nextjs-ghpages">Next.js Blog</FooterLink>
              </li>
              <li>
                <FooterLink href="/blog/en/algorithms">Algorithms</FooterLink>
              </li>
              <li>
                <FooterLink href="/blog/en/docker101">Docker</FooterLink>
              </li>
            </ul>
          </div>

          {/* Social */}
          <div>
            <h4 className="text-sm font-semibold text-gray-500 uppercase">Connect</h4>
            <ul className="mt-3 space-y-2">
              <li>
                <FooterLink href="https://github.com/yourusername">GitHub</FooterLink>
              </li>
              <li>
                <FooterLink href="https://twitter.com/yourhandle">Twitter</FooterLink>
              </li>
              <li>
                <FooterLink href="https://buymeacoffee.com/yourusername">
                  Buy Me a Coffee
                </FooterLink>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 border-t border-gray-200 pt-6 text-center text-xs text-gray-400 dark:border-gray-800">
          © {new Date().getFullYear()} Your Name. Content is free. Code is MIT.
        </div>
      </div>
    </footer>
  );
}

function FooterLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      className="text-sm text-gray-600 transition hover:text-teal-600 dark:text-gray-400"
    >
      {children}
    </a>
  );
}
```

## Color System

Keep it simple — one accent color, neutral grays, semantic colors:

```css
/* Your color palette (already built into Tailwind) */
/* Primary accent: teal-600 */
/* Text: gray-900 (light) / white (dark) */
/* Muted text: gray-600 (light) / gray-400 (dark) */
/* Borders: gray-200 (light) / gray-800 (dark) */
/* Backgrounds: white (light) / gray-950 (dark) */
/* Success: green-600 */
/* Warning: yellow-600 */
/* Error: red-600 */
```

One accent color (teal) used consistently = professional. Rainbow colors = amateur.

## Typography Scale

```css
/* Consistent sizing */
text-xs    → 12px  (badges, metadata)
text-sm    → 14px  (body text, buttons)
text-base  → 16px  (default body)
text-lg    → 18px  (card titles)
text-xl    → 20px  (section headings)
text-2xl   → 24px  (page headings)
text-4xl   → 36px  (hero heading)
```

Rule: never use more than 3-4 sizes on one page. Consistency > variety.

## Spacing System

Tailwind's spacing scale is your friend:

```
gap-1  (4px)  → between inline elements
gap-2  (8px)  → between related items
gap-4  (16px) → between sections
gap-6  (24px) → between major blocks
gap-8  (32px) → between page sections
py-12  (48px) → page top/bottom padding
py-16  (64px) → hero sections
```

Rule: use multiples of 4. Everything aligns to a grid. Looks intentional.

## The Complete Page Layout

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body className="flex min-h-screen flex-col bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
```

`flex flex-col` + `flex-1` on main = footer always at the bottom, even on short pages.

---

## Design Principles for Developer Blogs

1. **Whitespace is content** — let things breathe, don't cram
2. **One accent color** — teal for links, buttons, highlights. That's it.
3. **Consistent borders** — `border-gray-200 dark:border-gray-800` everywhere
4. **Subtle interactions** — hover lifts, color transitions, not bouncing animations
5. **Mobile first** — design for 375px, then expand for desktop
6. **Dark mode isn't inverted** — it's a separate palette, not `filter: invert()`
7. **Typography does the work** — good font sizes + line height > fancy layouts

---

## What's Next

You have a complete, beautiful, interactive learning platform. The only thing left is content. Write more courses. Ship them. The platform handles the rest.
