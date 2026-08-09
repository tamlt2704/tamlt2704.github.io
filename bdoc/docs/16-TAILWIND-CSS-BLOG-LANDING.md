# Chapter 16: Tailwind CSS — Build a Blog Landing Page from Scratch

## What you'll learn

- Tailwind's utility-first philosophy (why it works, how to think in it)
- The box model and spacing system
- Flexbox and Grid layout with Tailwind
- Responsive design (mobile-first breakpoints)
- Building real components: hero, cards, navigation, footer
- Typography, colours, and visual hierarchy
- Hover states, transitions, and micro-interactions
- Dark mode
- Common patterns and when to extract components vs use utilities

---

## PART 1: How Tailwind Thinks

## 16.1 Utility-first — the mental model

Traditional CSS:

```css
.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  background: white;
}
```

Tailwind:

```html
<div class="p-6 rounded-lg shadow-sm bg-white">
```

Every visual property becomes a class. You compose styles by stacking classes. No CSS files to maintain, no naming conventions to argue about.

> **"But it's ugly!"** Yes, the HTML has more classes. The tradeoff: you NEVER leave your component file. No jumping between `.tsx` and `.css`. No dead CSS accumulating. No specificity battles. After a week, you'll read `p-6 rounded-lg shadow-sm` as fluently as you read CSS properties.

## 16.2 The spacing scale

Tailwind uses a consistent spacing scale. Every number maps to a `rem` value:

| Class | Value | Pixels (at 16px base) |
|-------|-------|-----------------------|
| `p-0` | 0 | 0px |
| `p-1` | 0.25rem | 4px |
| `p-2` | 0.5rem | 8px |
| `p-3` | 0.75rem | 12px |
| `p-4` | 1rem | 16px |
| `p-6` | 1.5rem | 24px |
| `p-8` | 2rem | 32px |
| `p-12` | 3rem | 48px |
| `p-16` | 4rem | 64px |
| `p-24` | 6rem | 96px |

This applies to `p` (padding), `m` (margin), `gap`, `w` (width), `h` (height), `top`, `left`, etc.

**Directional variants:**
- `p-4` — all sides
- `px-4` — left + right (x-axis)
- `py-4` — top + bottom (y-axis)
- `pt-4` — top only
- `pb-4` — bottom only
- `pl-4` — left only
- `pr-4` — right only

## 16.3 The box model in Tailwind

```
┌─────────────────────────────────────┐
│           margin (m-4)              │
│  ┌───────────────────────────────┐  │
│  │        border (border)        │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │     padding (p-6)       │  │  │
│  │  │  ┌───────────────────┐  │  │  │
│  │  │  │    CONTENT        │  │  │  │
│  │  │  │    (w-64 h-32)    │  │  │  │
│  │  │  └───────────────────┘  │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

Key classes:
```
w-full        → width: 100%
h-screen      → height: 100vh
min-h-screen  → min-height: 100vh
max-w-4xl     → max-width: 56rem (896px)
border        → border: 1px solid
rounded-lg    → border-radius: 0.5rem
shadow-md     → box-shadow (medium)
```

## 16.4 Flexbox — the everyday layout

90% of your layouts use flexbox:

```tsx
{/* Horizontal row with spacing */}
<div className="flex gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

{/* Vertical column */}
<div className="flex flex-col gap-4">
  <div>Top</div>
  <div>Middle</div>
  <div>Bottom</div>
</div>

{/* Space between (push items to edges) */}
<div className="flex justify-between items-center">
  <span>Left</span>
  <span>Right</span>
</div>

{/* Center everything */}
<div className="flex items-center justify-center h-screen">
  <p>Perfectly centered</p>
</div>
```

**Flex cheat sheet:**

| Class | CSS | What it does |
|-------|-----|-------------|
| `flex` | `display: flex` | Enable flexbox |
| `flex-col` | `flex-direction: column` | Stack vertically |
| `flex-1` | `flex: 1 1 0%` | Grow to fill space |
| `gap-4` | `gap: 1rem` | Space between children |
| `items-center` | `align-items: center` | Vertical centering |
| `justify-between` | `justify-content: space-between` | Push to edges |
| `justify-center` | `justify-content: center` | Horizontal centering |
| `flex-wrap` | `flex-wrap: wrap` | Allow wrapping |
| `shrink-0` | `flex-shrink: 0` | Don't shrink |

## 16.5 CSS Grid — for 2D layouts

When you need rows AND columns:

```tsx
{/* Equal columns */}
<div className="grid grid-cols-3 gap-6">
  <div>Col 1</div>
  <div>Col 2</div>
  <div>Col 3</div>
</div>

{/* Responsive columns */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {posts.map(post => <PostCard key={post.slug} post={post} />)}
</div>

{/* Unequal columns (sidebar + content) */}
<div className="grid grid-cols-[250px_1fr] gap-8">
  <aside>Sidebar</aside>
  <main>Content</main>
</div>
```

## 16.6 Responsive design — mobile-first

Tailwind breakpoints are **min-width** (mobile-first):

| Prefix | Min-width | Typical device |
|--------|-----------|----------------|
| (none) | 0px | Mobile (default) |
| `sm:` | 640px | Large phone / small tablet |
| `md:` | 768px | Tablet |
| `lg:` | 1024px | Laptop |
| `xl:` | 1280px | Desktop |
| `2xl:` | 1536px | Large desktop |

**Read it as:** "from this breakpoint and up, apply this style."

```tsx
<div className="
  text-sm          /* mobile: small text */
  md:text-base     /* tablet+: normal text */
  lg:text-lg       /* laptop+: larger text */
">
```

```tsx
<div className="
  flex flex-col    /* mobile: stack vertically */
  md:flex-row      /* tablet+: side by side */
  gap-4
  md:gap-8         /* more gap on larger screens */
">
```



---

## PART 2: Building the Landing Page

## 16.7 The complete landing page structure

We'll build this layout:

```
┌──────────────────────────────────────────────────────┐
│  HEADER: Logo + Nav links              [Dark toggle] │
├──────────────────────────────────────────────────────┤
│                                                      │
│              HERO SECTION                             │
│     Big headline + subtitle + CTA button             │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│         FEATURED POSTS (3-column grid)               │
│     [Card 1]    [Card 2]    [Card 3]                 │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│       FEATURES/ABOUT SECTION (alternating)           │
│     [Image]  [Text]                                  │
│     [Text]   [Image]                                 │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│           NEWSLETTER CTA                             │
│     Email input + subscribe button                   │
│                                                      │
├──────────────────────────────────────────────────────┤
│  FOOTER: Links + copyright                           │
└──────────────────────────────────────────────────────┘
```

## 16.8 Header / Navigation

```tsx
export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="/" className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors">
            ✦ DevBlog
          </a>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-8">
            <a href="/blog" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
              Blog
            </a>
            <a href="/projects" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
              Projects
            </a>
            <a href="/about" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
              About
            </a>
            <a
              href="https://github.com"
              className="text-sm px-4 py-2 bg-gray-900 text-white rounded-full hover:bg-gray-700 transition-colors"
            >
              GitHub →
            </a>
          </nav>

          {/* Mobile menu button */}
          <button className="md:hidden p-2 text-gray-600 hover:text-gray-900">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
```

**What each class does:**

| Classes | Purpose |
|---------|---------|
| `fixed top-0 left-0 right-0 z-50` | Sticks to top, always visible above content |
| `bg-white/80 backdrop-blur-md` | Semi-transparent with glass blur effect |
| `border-b border-gray-100` | Subtle bottom border (separates from content) |
| `max-w-6xl mx-auto px-4 sm:px-6` | Content constrained, centered, responsive padding |
| `flex items-center justify-between h-16` | Row layout, vertically centered, fixed height |
| `hidden md:flex` | Hidden on mobile, visible on tablet+ |
| `rounded-full` | Pill-shaped button |
| `transition-colors` | Smooth colour change on hover |

## 16.9 Hero Section

```tsx
export default function Hero() {
  return (
    <section className="pt-32 pb-20 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto text-center">
        {/* Eyebrow / tag */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-sm font-medium mb-6">
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
          Now with interactive visualisations
        </div>

        {/* Main headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 tracking-tight mb-6">
          Learn algorithms through{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
            visual storytelling
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed">
          Interactive tutorials that show you how sorting, searching, and graph
          algorithms work — step by step, with code and visualisations side by side.
        </p>

        {/* CTA buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/blog"
            className="px-8 py-3 bg-gray-900 text-white rounded-full font-medium hover:bg-gray-700 transition-colors shadow-lg shadow-gray-900/20"
          >
            Start Reading →
          </a>
          <a
            href="/algorithms"
            className="px-8 py-3 border border-gray-300 text-gray-700 rounded-full font-medium hover:border-gray-400 hover:bg-gray-50 transition-colors"
          >
            Try the Visualiser
          </a>
        </div>
      </div>
    </section>
  );
}
```

**Techniques used:**

- **Gradient text**: `text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600` — makes text show through a gradient background
- **Shadow with colour**: `shadow-lg shadow-gray-900/20` — coloured shadow (not just grey)
- **Eyebrow tag**: small pill above the headline to call out something new
- **`tracking-tight`**: tighter letter-spacing for large headlines (looks more professional)
- **`max-w-2xl mx-auto`** on subtitle: limits line width for readability even within a wider container
- **Stack on mobile, row on desktop**: `flex-col sm:flex-row` for CTA buttons

## 16.10 Featured Posts Grid

```tsx
type Post = {
  slug: string;
  title: string;
  description: string;
  date: string;
  tags: string[];
  readTime: string;
};

function PostCard({ post }: { post: Post }) {
  return (
    <a
      href={`/blog/${post.slug}`}
      className="group block"
    >
      <article className="h-full p-6 rounded-2xl border border-gray-200 bg-white hover:border-gray-300 hover:shadow-lg transition-all duration-200">
        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-600 font-medium"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
          {post.title}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-600 leading-relaxed mb-4 line-clamp-2">
          {post.description}
        </p>

        {/* Meta */}
        <div className="flex items-center justify-between text-xs text-gray-400 mt-auto pt-4 border-t border-gray-100">
          <time>{post.date}</time>
          <span>{post.readTime}</span>
        </div>
      </article>
    </a>
  );
}

export default function FeaturedPosts({ posts }: { posts: Post[] }) {
  return (
    <section className="py-20 px-4 sm:px-6 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <div className="flex items-end justify-between mb-10">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Latest Posts</h2>
            <p className="text-gray-600">Fresh tutorials and deep dives</p>
          </div>
          <a href="/blog" className="text-sm text-blue-600 hover:text-blue-800 font-medium hidden sm:block">
            View all →
          </a>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post) => (
            <PostCard key={post.slug} post={post} />
          ))}
        </div>
      </div>
    </section>
  );
}
```

**Key patterns:**

- **`group` + `group-hover:`** — hover on the card changes the title colour (parent hover affects child)
- **`line-clamp-2`** — truncates description to 2 lines with ellipsis
- **`rounded-2xl`** — larger border radius (more modern look)
- **`transition-all duration-200`** — smooth animation for border, shadow, and colour changes
- **`h-full` + `mt-auto`** — makes all cards equal height with meta pushed to bottom
- **`bg-gray-50`** on section — subtle background change to visually separate sections

## 16.11 Feature Section — alternating image + text

```tsx
type Feature = {
  title: string;
  description: string;
  image: string;
};

function FeatureRow({ feature, reversed }: { feature: Feature; reversed: boolean }) {
  return (
    <div className={`flex flex-col ${reversed ? "md:flex-row-reverse" : "md:flex-row"} gap-8 md:gap-16 items-center`}>
      {/* Image */}
      <div className="flex-1 w-full">
        <div className="aspect-video rounded-2xl bg-gray-100 overflow-hidden border border-gray-200">
          <img
            src={feature.image}
            alt={feature.title}
            className="w-full h-full object-cover"
          />
        </div>
      </div>

      {/* Text */}
      <div className="flex-1">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          {feature.title}
        </h3>
        <p className="text-gray-600 leading-relaxed mb-6">
          {feature.description}
        </p>
        <a href="#" className="inline-flex items-center gap-2 text-blue-600 font-medium hover:text-blue-800 transition-colors">
          Learn more
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </a>
      </div>
    </div>
  );
}

export default function Features({ features }: { features: Feature[] }) {
  return (
    <section className="py-20 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto space-y-20">
        {features.map((feature, index) => (
          <FeatureRow key={index} feature={feature} reversed={index % 2 === 1} />
        ))}
      </div>
    </section>
  );
}
```

**Patterns:**
- **`flex-row-reverse`** — flips the order without changing HTML structure (alternating layout)
- **`aspect-video`** — maintains 16:9 ratio regardless of content
- **`space-y-20`** — vertical spacing between feature rows (large gap for visual breathing)
- **`object-cover`** — image fills container without distortion



---

## PART 3: More Components + Visual Design System

## 16.12 Newsletter CTA section

```tsx
export default function NewsletterCTA() {
  return (
    <section className="py-20 px-4 sm:px-6">
      <div className="max-w-2xl mx-auto text-center">
        {/* Background card */}
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-gray-900 to-gray-800 text-white">
          <h2 className="text-2xl sm:text-3xl font-bold mb-3">
            Stay up to date
          </h2>
          <p className="text-gray-300 mb-8 max-w-md mx-auto">
            Get notified when I publish new tutorials. No spam, unsubscribe anytime.
          </p>

          {/* Form */}
          <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              placeholder="you@example.com"
              className="flex-1 px-4 py-3 rounded-full bg-white/10 border border-white/20 text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-blue-600 text-white rounded-full font-medium hover:bg-blue-500 transition-colors shrink-0"
            >
              Subscribe
            </button>
          </form>

          <p className="text-xs text-gray-400 mt-4">
            Join 2,000+ developers. Free forever.
          </p>
        </div>
      </div>
    </section>
  );
}
```

**Techniques:**
- **`bg-gradient-to-br from-gray-900 to-gray-800`** — subtle gradient background (more depth than flat colour)
- **`rounded-3xl`** — very large border radius (modern card style)
- **`bg-white/10 border-white/20`** — semi-transparent input field that blends with dark background
- **`focus:ring-2 focus:ring-blue-500`** — visible focus indicator (accessibility)
- **`placeholder:text-gray-400`** — lighter placeholder text
- **`shrink-0`** on button — prevents button from shrinking when input grows

## 16.13 Footer

```tsx
export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="sm:col-span-2 lg:col-span-1">
            <span className="text-lg font-bold text-gray-900">✦ DevBlog</span>
            <p className="text-sm text-gray-600 mt-2 max-w-xs">
              Interactive tutorials on algorithms, web dev, and computer science.
            </p>
          </div>

          {/* Links column 1 */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Content</h4>
            <ul className="space-y-2">
              <li><a href="/blog" className="text-sm text-gray-600 hover:text-gray-900">Blog</a></li>
              <li><a href="/algorithms" className="text-sm text-gray-600 hover:text-gray-900">Visualiser</a></li>
              <li><a href="/projects" className="text-sm text-gray-600 hover:text-gray-900">Projects</a></li>
            </ul>
          </div>

          {/* Links column 2 */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Connect</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-sm text-gray-600 hover:text-gray-900">GitHub</a></li>
              <li><a href="#" className="text-sm text-gray-600 hover:text-gray-900">Twitter</a></li>
              <li><a href="#" className="text-sm text-gray-600 hover:text-gray-900">LinkedIn</a></li>
            </ul>
          </div>

          {/* Links column 3 */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Legal</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-sm text-gray-600 hover:text-gray-900">Privacy</a></li>
              <li><a href="#" className="text-sm text-gray-600 hover:text-gray-900">Terms</a></li>
              <li><a href="#" className="text-sm text-gray-600 hover:text-gray-900">RSS</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-gray-100 text-sm text-gray-500 text-center">
          © 2026 DevBlog. Built with Next.js, MDX, and Tailwind CSS.
        </div>
      </div>
    </footer>
  );
}
```

## 16.14 Colour system — choosing a palette

Tailwind provides a full colour scale per colour (50–950). For a blog, use:

**Primary palette:**
```
Text:        gray-900 (headings), gray-600 (body), gray-400 (meta)
Background:  white, gray-50 (alternating sections)
Accent:      blue-600 (links, CTAs), blue-50 (tag backgrounds)
Borders:     gray-100 (subtle), gray-200 (visible), gray-300 (strong)
```

**Visual hierarchy through colour:**
```tsx
<h1 className="text-gray-900">Most important</h1>      {/* darkest */}
<p className="text-gray-600">Supporting text</p>        {/* medium */}
<time className="text-gray-400">Least important</time>  {/* lightest */}
<a className="text-blue-600">Action/link</a>            {/* colour = interactive */}
```

**Rule of thumb:** Use ONE accent colour (blue). Everything else is grey. Multiple colours = visual noise.

## 16.15 Typography scale

| Element | Classes | Looks like |
|---------|---------|------------|
| Page title | `text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight` | Huge, bold, tight |
| Section heading | `text-3xl font-bold` | Large, bold |
| Card title | `text-lg font-semibold` | Medium, semi-bold |
| Body text | `text-base text-gray-600 leading-relaxed` | Normal, grey, spaced |
| Small meta | `text-sm text-gray-500` | Small, light |
| Tiny labels | `text-xs text-gray-400 font-medium uppercase tracking-wide` | Tiny, all-caps, spaced |

**`leading-*`** (line-height):
- `leading-tight` (1.25) — headlines
- `leading-normal` (1.5) — short text
- `leading-relaxed` (1.625) — body paragraphs (easier to read)
- `leading-loose` (2) — very spacious

**`tracking-*`** (letter-spacing):
- `tracking-tight` (-0.025em) — large headlines (looks tighter/bolder)
- `tracking-normal` (0) — default
- `tracking-wide` (0.025em) — uppercase labels (improves readability of caps)

## 16.16 Dark mode

Tailwind's `dark:` variant applies when the `dark` class is on `<html>`:

```tsx
// Toggle approach:
<html className="dark">  {/* or remove for light */}
```

Adapting components:

```tsx
{/* Header */}
<header className="bg-white/80 dark:bg-gray-900/80 border-b border-gray-100 dark:border-gray-800">

{/* Hero text */}
<h1 className="text-gray-900 dark:text-white">
<p className="text-gray-600 dark:text-gray-300">

{/* Cards */}
<article className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
  <h3 className="text-gray-900 dark:text-white">
  <p className="text-gray-600 dark:text-gray-400">

{/* Backgrounds */}
<section className="bg-gray-50 dark:bg-gray-900">

{/* Input fields */}
<input className="bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white">
```

**Pattern:** For every light colour, add a `dark:` equivalent. Usually:
- Light backgrounds → dark backgrounds (gray-800/900)
- Dark text → light text (white/gray-100)
- Light borders → darker borders (gray-700/800)
- Accent colours stay the same (blue-600 works on both)

## 16.17 Hover states and micro-interactions

```tsx
{/* Card lift on hover */}
<div className="hover:shadow-lg hover:-translate-y-1 transition-all duration-200">

{/* Button press effect */}
<button className="hover:bg-blue-700 active:scale-95 transition-all">

{/* Link with underline animation */}
<a className="relative after:absolute after:bottom-0 after:left-0 after:w-0 after:h-0.5 after:bg-blue-600 hover:after:w-full after:transition-all">

{/* Icon rotation on hover */}
<span className="inline-block transition-transform group-hover:rotate-12">→</span>

{/* Opacity reveal */}
<div className="opacity-0 group-hover:opacity-100 transition-opacity">
  Hidden until parent is hovered
</div>
```

**Transition classes:**
- `transition-colors` — only colour changes animate (fastest)
- `transition-all` — everything animates (heavier but catches everything)
- `duration-150` / `duration-200` / `duration-300` — animation speed
- `ease-in-out` — smooth acceleration/deceleration



---

## PART 4: Putting It All Together

## 16.18 The complete landing page

```tsx
// app/page.tsx
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import FeaturedPosts from "@/components/FeaturedPosts";
import Features from "@/components/Features";
import NewsletterCTA from "@/components/NewsletterCTA";
import Footer from "@/components/Footer";

const POSTS = [
  {
    slug: "bubble-sort-visualised",
    title: "Bubble Sort — Visualised Step by Step",
    description: "Watch bubble sort in action with animated D3 bar charts and line-by-line code highlighting.",
    date: "2 Aug 2026",
    tags: ["algorithms", "d3"],
    readTime: "8 min read",
  },
  {
    slug: "nextjs-mdx-blog",
    title: "Build a Blog with Next.js and MDX",
    description: "How to set up MDX, embed React components in markdown, and deploy to GitHub Pages.",
    date: "5 Aug 2026",
    tags: ["nextjs", "mdx"],
    readTime: "12 min read",
  },
  {
    slug: "tailwind-from-scratch",
    title: "Tailwind CSS — From Zero to Landing Page",
    description: "Learn Tailwind by building a real landing page with responsive layout, dark mode, and animations.",
    date: "8 Aug 2026",
    tags: ["css", "tailwind"],
    readTime: "15 min read",
  },
];

const FEATURES = [
  {
    title: "Step-by-step visualisation",
    description: "Every algorithm is broken into discrete steps. See exactly what happens on each iteration — which elements are compared, which are swapped, and why.",
    image: "/images/feature-steps.png",
  },
  {
    title: "Code and visuals side by side",
    description: "The current line of code is highlighted as the visualisation updates. Connect the abstract code to the concrete action.",
    image: "/images/feature-code.png",
  },
  {
    title: "Multiple languages",
    description: "Switch between Java, Python, and JavaScript implementations. Same algorithm, different syntax — see what's universal.",
    image: "/images/feature-languages.png",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Hero />
        <FeaturedPosts posts={POSTS} />
        <Features features={FEATURES} />
        <NewsletterCTA />
      </main>
      <Footer />
    </div>
  );
}
```

## 16.19 Common Tailwind patterns — quick reference

### Centering

```tsx
{/* Center a content block horizontally */}
<div className="max-w-4xl mx-auto px-4">

{/* Center flex children vertically + horizontally */}
<div className="flex items-center justify-center h-screen">

{/* Center text */}
<div className="text-center">

{/* Center an element within a relative parent */}
<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
```

### Truncation

```tsx
{/* Single line truncate */}
<p className="truncate">Very long text that gets cut off...</p>

{/* Multi-line clamp */}
<p className="line-clamp-2">Text clamped to 2 lines with ellipsis...</p>
<p className="line-clamp-3">Three lines maximum...</p>
```

### Aspect ratios

```tsx
<div className="aspect-square">  {/* 1:1 */}
<div className="aspect-video">   {/* 16:9 */}
<div className="aspect-[4/3]">   {/* custom 4:3 */}
```

### Dividers

```tsx
{/* Horizontal line */}
<hr className="border-t border-gray-200 my-8" />

{/* Vertical divider in a flex row */}
<div className="w-px h-6 bg-gray-200" />

{/* Section separator with background change */}
<section className="bg-gray-50">  {/* different bg = visual separation */}
```

### Badges and pills

```tsx
{/* Simple badge */}
<span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">
  Published
</span>

{/* Status dot + text */}
<span className="inline-flex items-center gap-1.5 text-xs">
  <span className="w-2 h-2 rounded-full bg-green-500" />
  Active
</span>
```

### Overlapping elements (avatars)

```tsx
<div className="flex -space-x-2">
  <img className="w-8 h-8 rounded-full ring-2 ring-white" src="/avatar1.jpg" />
  <img className="w-8 h-8 rounded-full ring-2 ring-white" src="/avatar2.jpg" />
  <img className="w-8 h-8 rounded-full ring-2 ring-white" src="/avatar3.jpg" />
</div>
```

### Skeleton loading

```tsx
<div className="animate-pulse space-y-4">
  <div className="h-4 bg-gray-200 rounded w-3/4" />
  <div className="h-4 bg-gray-200 rounded w-full" />
  <div className="h-4 bg-gray-200 rounded w-5/6" />
</div>
```

## 16.20 When to extract a component vs inline utilities

**Inline utilities (keep classes in JSX) when:**
- The element is used once
- It's simple (< 10 classes)
- You're iterating quickly

**Extract to a component when:**
- You use the same pattern 3+ times
- The class list exceeds ~15 classes
- It has props that change the appearance
- It represents a meaningful concept (PostCard, Callout, Badge)

```tsx
// ❌ Don't create .css classes for this:
.card { @apply p-6 rounded-lg shadow-sm bg-white border; }

// ✅ Do create a React component:
function Card({ children }: { children: React.ReactNode }) {
  return (
    <div className="p-6 rounded-lg shadow-sm bg-white border">
      {children}
    </div>
  );
}
```

> **Why not `@apply`?** It defeats the purpose of utility-first. You're back to naming things and maintaining CSS. Components are the abstraction layer in React — use them instead of CSS classes.

## 16.21 Performance tips

- **No purging needed in Tailwind v4** — it only generates the CSS for classes you actually use
- **`transition-colors` > `transition-all`** — fewer properties to animate = smoother
- **Avoid `shadow-lg` on many elements** — large shadows are expensive to render; reserve for hover states
- **`will-change-transform`** — add this to elements you animate frequently (cards on hover)
- **Use `loading="lazy"` on images** — native lazy loading, no library needed

## Summary

✅ You understand utility-first: stack classes, no custom CSS
✅ You know the spacing scale (p-4 = 1rem = 16px)
✅ You can build any layout with flex and grid
✅ You understand mobile-first responsive design (sm:, md:, lg:)
✅ You built a complete landing page: header, hero, cards, features, CTA, footer
✅ You know the colour system: gray for text/borders, one accent colour for actions
✅ You understand typography hierarchy: size + weight + colour = importance
✅ You can add dark mode with `dark:` variants
✅ You know when to use transitions and hover states
✅ You know when to extract components vs keep utilities inline

## Key takeaways

**Think in constraints.** Tailwind's spacing scale (4, 6, 8, 12, 16, 24) forces consistency. You can't accidentally use 17px somewhere — the scale keeps everything harmonious.

**Visual hierarchy = size + weight + colour.** Large + bold + dark = important. Small + normal + grey = secondary. Colour = interactive.

**Mobile-first means write the simple version, then add complexity.** Start with a single column, add `md:grid-cols-2` for tablet, `lg:grid-cols-3` for desktop.

**Spacing creates visual groups.** Items close together feel related. Large gaps separate sections. `gap-4` inside a group, `py-20` between sections.

---

→ [Back to Chapter 15: Next.js MDX Blog](./15-NEXTJS-MDX-BLOG.md)
