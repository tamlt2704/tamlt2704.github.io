# Chapter 2: Layout — Flexbox, Grid, and Responsive Design

[← Chapter 1: Utility Basics](chapter-01-utility-basics.md) | [Chapter 3: Responsive Navbar →](chapter-03-responsive-navbar.md)

---

## The Task

Sora: "Three metric cards in a row on desktop. Stack on mobile. Sidebar is 256px, main content fills the rest. The whole thing needs to work from 320px to 2560px."

---

## Flexbox in Tailwind

Flexbox is your go-to for one-dimensional layouts (row or column).

```html
<!-- Row (default) -->
<div class="flex gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

<!-- Column -->
<div class="flex flex-col gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

Key flex utilities:

```
────────────────────────────────────────────────
 Class              │ CSS
────────────────────────────────────────────────
 flex               │ display: flex
 flex-col           │ flex-direction: column
 flex-row           │ flex-direction: row (default)
 flex-wrap          │ flex-wrap: wrap
 gap-{n}            │ gap: {n * 4}px
 items-center       │ align-items: center
 items-start        │ align-items: flex-start
 justify-center     │ justify-content: center
 justify-between    │ justify-content: space-between
 justify-end        │ justify-content: flex-end
 flex-1             │ flex: 1 1 0% (grow to fill)
 flex-none          │ flex: none (don't grow/shrink)
 flex-shrink-0      │ flex-shrink: 0
────────────────────────────────────────────────
```

---

## The Metric Cards Row

```tsx
function MetricCards() {
  return (
    <div className="flex gap-6">
      <MetricCard title="Revenue" value="$12,480" change="+12.5%" trend="up" />
      <MetricCard title="Users" value="1,429" change="+4.2%" trend="up" />
      <MetricCard title="Churn" value="2.4%" change="+0.3%" trend="down" />
    </div>
  );
}
```

But each card needs to take equal width:

```tsx
// Inside MetricCard, add flex-1:
<div className="flex-1 bg-white rounded-lg p-6 shadow-sm border border-gray-100">
```

`flex-1` means "grow to fill available space equally."

---

## CSS Grid in Tailwind

Grid is your go-to for two-dimensional layouts (rows AND columns).

```html
<!-- 3 equal columns -->
<div class="grid grid-cols-3 gap-6">
  <div>Card 1</div>
  <div>Card 2</div>
  <div>Card 3</div>
</div>

<!-- 2 columns, second one wider -->
<div class="grid grid-cols-[256px_1fr] gap-6">
  <aside>Sidebar</aside>
  <main>Content</main>
</div>
```

Key grid utilities:

```
────────────────────────────────────────────────
 Class              │ CSS
────────────────────────────────────────────────
 grid               │ display: grid
 grid-cols-{n}      │ grid-template-columns: repeat(n, 1fr)
 grid-cols-[...]    │ custom column template
 grid-rows-{n}      │ grid-template-rows: repeat(n, 1fr)
 col-span-{n}       │ grid-column: span n
 row-span-{n}       │ grid-row: span n
 gap-{n}            │ gap (both axes)
 gap-x-{n}          │ column-gap
 gap-y-{n}          │ row-gap
────────────────────────────────────────────────
```

---

## The Dashboard Layout

```tsx
function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top navbar */}
      <header className="h-16 bg-white border-b border-gray-200 flex items-center px-6">
        <span className="font-bold text-xl">Pixelflow</span>
      </header>

      {/* Sidebar + Main */}
      <div className="flex">
        <aside className="w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
          {/* Nav items */}
        </aside>
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

Breaking it down:
- `min-h-screen` → minimum height: 100vh (fills viewport)
- `w-64` → width: 256px (64 × 4px)
- `flex-1` → main content fills remaining width
- `min-h-[calc(100vh-4rem)]` → sidebar fills height minus navbar

---

## Responsive Design: Mobile-First

Tailwind is mobile-first. Base classes apply to all screens. Prefixed classes apply at that breakpoint and above.

```
────────────────────────────────────────────────
 Prefix  │ Min-width │ Typical device
────────────────────────────────────────────────
 (none)  │ 0px       │ Mobile (default)
 sm:     │ 640px     │ Large phone / small tablet
 md:     │ 768px     │ Tablet
 lg:     │ 1024px    │ Laptop
 xl:     │ 1280px    │ Desktop
 2xl:    │ 1536px    │ Large desktop
────────────────────────────────────────────────
```

The pattern: **start mobile, add breakpoints going up.**

```html
<!-- Stack on mobile, 2 cols on tablet, 3 cols on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <MetricCard />
  <MetricCard />
  <MetricCard />
</div>
```

Read it as:
- Default (mobile): 1 column
- `md:` (≥768px): 2 columns
- `lg:` (≥1024px): 3 columns

---

## Making the Dashboard Responsive

The sidebar should collapse on mobile:

```tsx
function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 lg:px-6">
        <span className="font-bold text-xl">Pixelflow</span>
      </header>

      <div className="flex">
        {/* Hidden on mobile, visible on lg+ */}
        <aside className="hidden lg:block w-64 bg-white border-r border-gray-200 min-h-[calc(100vh-4rem)]">
          <nav className="p-4 flex flex-col gap-1">
            <a href="#" className="px-3 py-2 rounded-md bg-gray-100 text-gray-900 font-medium text-sm">
              Home
            </a>
            <a href="#" className="px-3 py-2 rounded-md text-gray-600 hover:bg-gray-50 text-sm">
              Analytics
            </a>
            <a href="#" className="px-3 py-2 rounded-md text-gray-600 hover:bg-gray-50 text-sm">
              Team
            </a>
          </nav>
        </aside>

        <main className="flex-1 p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

Key responsive patterns:
- `hidden lg:block` → hidden on mobile, visible on desktop
- `block lg:hidden` → visible on mobile, hidden on desktop
- `p-4 lg:p-6` → less padding on mobile, more on desktop
- `text-2xl lg:text-3xl` → smaller text on mobile

---

## Common Layout Patterns

### Centering

```html
<!-- Center horizontally and vertically -->
<div class="flex items-center justify-center h-screen">
  <p>Centered content</p>
</div>

<!-- Center a max-width container -->
<div class="max-w-4xl mx-auto px-4">
  <p>Centered with max width</p>
</div>
```

### Space Between

```html
<!-- Items pushed to edges -->
<div class="flex items-center justify-between">
  <span>Logo</span>
  <nav>Links</nav>
</div>
```

### Sticky Elements

```html
<!-- Sticky sidebar -->
<aside class="sticky top-0 h-screen overflow-y-auto">
  Nav content
</aside>

<!-- Sticky header -->
<header class="sticky top-0 z-50 bg-white border-b">
  Header content
</header>
```

### Full-Bleed with Contained Content

```html
<section class="bg-gray-900 w-full">
  <div class="max-w-7xl mx-auto px-4 py-16">
    Content stays centered and contained
  </div>
</section>
```

---

## The Dashboard Content Area

Putting it together — the main content with responsive cards and a chart area:

```tsx
function DashboardContent() {
  return (
    <div className="space-y-6">
      {/* Metric cards: 1 col mobile, 2 col tablet, 3 col desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <MetricCard title="Revenue" value="$12,480" change="+12.5%" trend="up" />
        <MetricCard title="Users" value="1,429" change="+4.2%" trend="up" />
        <MetricCard title="Churn" value="2.4%" change="+0.3%" trend="down" />
      </div>

      {/* Chart area: full width */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Revenue Over Time</h2>
        <div className="h-64 bg-gray-50 rounded flex items-center justify-center text-gray-400">
          Chart goes here
        </div>
      </div>

      {/* Bottom section: stack on mobile, side by side on desktop */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          {/* Activity list */}
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Team Members</h2>
          {/* Team list */}
        </div>
      </div>
    </div>
  );
}
```

`space-y-6` adds `margin-top: 24px` to every child except the first. It's the vertical equivalent of `gap` for non-flex/grid containers.

---

## Dev's Question

Dev: "When do I use Flexbox vs Grid?"

You:
- **Flexbox** (`flex`): one direction. Navbar items, button groups, centering, sidebar + content.
- **Grid** (`grid`): two directions. Card grids, dashboard layouts, anything with rows AND columns.

Rule of thumb: if you're thinking "items in a row" → flex. If you're thinking "items in a grid" → grid.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Classes
────────────────────────────────┼──────────────────────────────────────
Row of items                    │ flex gap-{n}
Column of items                 │ flex flex-col gap-{n}
Equal-width columns             │ grid grid-cols-{n} gap-{n}
Sidebar + content               │ flex → w-64 + flex-1
Center everything               │ flex items-center justify-center
Push apart                      │ flex justify-between
Responsive columns              │ grid-cols-1 md:grid-cols-2 lg:grid-cols-3
Hide on mobile                  │ hidden lg:block
Show only on mobile             │ block lg:hidden
Vertical spacing                │ space-y-{n}
Max-width centered              │ max-w-{size} mx-auto
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "The layout works. But on mobile there's no way to access the sidebar navigation. I need a hamburger menu that slides in. And the navbar needs to be responsive too."

Time to build a responsive navbar with a mobile menu.

---

[← Chapter 1: Utility Basics](chapter-01-utility-basics.md) | [Chapter 3: Responsive Navbar →](chapter-03-responsive-navbar.md)
