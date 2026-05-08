# Chapter 4: Responsive Typography

[← Chapter 3: Grid](chapter-03-grid.md) | [Chapter 5: Responsive Spacing →](chapter-05-spacing.md)

---

## The Breakage

Diana screenshots the dashboard on her iPhone SE: "Why is the heading so tiny I need reading glasses?" Then Jake pulls it up on his 4K monitor: "Why is the body text so huge it looks like a children's book?"

The current code:

```html
<h1 class="text-4xl">Dashboard Overview</h1>
<p class="text-base">Welcome back. Here's what happened while you were away.</p>
<div class="text-sm text-gray-500">Last updated: 2 minutes ago</div>
```

On a 320px phone, `text-4xl` (2.25rem = 36px) dominates the viewport — the heading takes up half the screen. On a 4K display, `text-base` (1rem = 16px) looks like fine print in a sea of whitespace.

The QA team files: "Typography doesn't scale. Looks wrong on every device except 1440px."

## Responsive Text Sizing

The simplest fix: change text size at breakpoints.

```html
<h1 class="text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-bold">
  Dashboard Overview
</h1>
<p class="text-sm sm:text-base lg:text-lg text-gray-600">
  Welcome back. Here's what happened while you were away.
</p>
<span class="text-xs sm:text-sm text-gray-500">
  Last updated: 2 minutes ago
</span>
```

- Mobile: smaller sizes that fit the viewport
- Tablet: medium sizes
- Desktop: larger sizes with more breathing room

## Fluid Typography with clamp()

Breakpoint jumps feel abrupt. Fluid type scales smoothly between a minimum and maximum:

```html
<!-- Fluid heading: min 1.5rem, preferred 4vw, max 3rem -->
<h1 class="font-bold text-[clamp(1.5rem,4vw,3rem)]">
  Dashboard Overview
</h1>

<!-- Fluid body: min 0.875rem, preferred 1.2vw, max 1.125rem -->
<p class="text-[clamp(0.875rem,1.2vw,1.125rem)] text-gray-600">
  Welcome back. Here's what happened while you were away.
</p>
```

`clamp(min, preferred, max)` means:
- Never smaller than `min` (readable on phones)
- Scales with `preferred` (usually a viewport unit)
- Never larger than `max` (controlled on ultrawides)

## A Complete Type Scale

```html
<article class="max-w-prose mx-auto px-4">
  <!-- Page title -->
  <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight">
    Project Status Report
  </h1>

  <!-- Subtitle -->
  <p class="mt-2 text-lg sm:text-xl text-gray-500 font-light">
    Sprint 14 — Week ending March 15
  </p>

  <!-- Section heading -->
  <h2 class="mt-8 text-xl sm:text-2xl font-semibold">
    Key Metrics
  </h2>

  <!-- Body text -->
  <p class="mt-4 text-base sm:text-lg leading-relaxed text-gray-700">
    This sprint we shipped the notification system, fixed 23 bugs,
    and onboarded 340 new users. Conversion rate held steady at 3.2%.
  </p>

  <!-- Small/meta text -->
  <p class="mt-6 text-xs sm:text-sm text-gray-400">
    Report generated automatically. Data may be delayed up to 5 minutes.
  </p>
</article>
```

Key patterns:
- `tracking-tight` on large headings (tightens letter spacing)
- `leading-relaxed` on body text (increases line height for readability)
- `max-w-prose` limits line length to ~65 characters (optimal reading width)

## The Prose Plugin

For long-form content (changelogs, docs, blog posts), Tailwind's Typography plugin handles everything:

```bash
npm install -D @tailwindcss/typography
```

```html
<!-- One class styles all child elements responsively -->
<article class="prose prose-sm sm:prose-base lg:prose-lg mx-auto px-4">
  <h1>Release Notes v2.4</h1>
  <p>We've shipped three major features this quarter...</p>
  <h2>New Dashboard</h2>
  <p>The dashboard now supports <strong>real-time updates</strong>
     and custom widget layouts.</p>
  <ul>
    <li>Drag-and-drop widgets</li>
    <li>Auto-refresh every 30 seconds</li>
    <li>Export to PDF</li>
  </ul>
</article>
```

`prose-sm` → `prose-base` → `prose-lg` scales headings, body, lists, spacing — all at once.

## Truncation and Overflow

Long text on small screens needs containment:

```html
<!-- Single-line truncation -->
<h3 class="text-lg font-semibold truncate">
  This Very Long Project Name That Won't Fit On Mobile Screens
</h3>

<!-- Multi-line clamp (2 lines max) -->
<p class="text-sm text-gray-600 line-clamp-2 sm:line-clamp-3 lg:line-clamp-none">
  A lengthy description that should show 2 lines on mobile,
  3 on tablet, and the full text on desktop where there's room.
</p>
```

## What You Learned

- **Responsive text classes** — `text-sm sm:text-base lg:text-lg` for breakpoint-based scaling
- **`clamp()`** — fluid typography that scales smoothly between min and max
- **`tracking-tight`** — tighten letter spacing on large headings
- **`leading-relaxed`** — increase line height for body readability
- **`max-w-prose`** — limit line length to ~65 characters
- **`prose` plugin** — automatic responsive typography for long-form content
- **`truncate` / `line-clamp-*`** — contain overflow text on small screens

The text is readable now. But Diana notices the cards are crammed together on her phone — the padding is eating all the content space.

---

[← Chapter 3: Grid](chapter-03-grid.md) | [Chapter 5: Responsive Spacing →](chapter-05-spacing.md)
