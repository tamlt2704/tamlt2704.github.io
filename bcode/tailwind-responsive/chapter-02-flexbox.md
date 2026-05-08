# Chapter 2: Flexbox Layouts

[← Chapter 1: Mobile First](chapter-01-mobile-first.md) | [Chapter 3: Grid Systems →](chapter-03-grid.md)

---

## The Breakage

The LaunchPad dashboard has a sidebar + content layout. On desktop it looks fine. On tablet (768px), the sidebar and content fight for space:

```html
<!-- Current: sidebar always visible, always 256px -->
<div class="flex">
  <aside class="w-64">Sidebar</aside>
  <main class="w-full">Content</main>
</div>
```

At 768px, the sidebar takes 256px, leaving only 512px for content. Cards overflow. Text wraps awkwardly. The layout feels cramped.

Jake (designer): "On tablet, the sidebar should collapse. On mobile, it should disappear entirely."

## Flexbox in Tailwind: The Basics

Flexbox arranges items in a row or column with flexible sizing:

```html
<!-- Row (default): items side by side -->
<div class="flex">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

<!-- Column: items stacked -->
<div class="flex flex-col">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

### Key Flex Utilities

| Utility | What it does |
|---|---|
| `flex` | Enable flexbox |
| `flex-row` / `flex-col` | Direction (row is default) |
| `flex-wrap` | Allow items to wrap to next line |
| `flex-1` | Grow to fill available space |
| `flex-none` | Don't grow or shrink |
| `flex-shrink-0` | Never shrink below natural size |
| `gap-4` | Space between items (1rem) |

## The Sidebar Pattern: Responsive Flex

```html
<div class="flex flex-col lg:flex-row min-h-screen">
  <!-- Sidebar: full width on mobile (top bar), fixed width on desktop -->
  <aside class="w-full lg:w-64 flex-none bg-white border-b lg:border-b-0 lg:border-r">
    <div class="flex lg:flex-col p-4 gap-4 overflow-x-auto lg:overflow-x-visible">
      <a href="#" class="whitespace-nowrap lg:whitespace-normal">Dashboard</a>
      <a href="#" class="whitespace-nowrap lg:whitespace-normal">Projects</a>
      <a href="#" class="whitespace-nowrap lg:whitespace-normal">Team</a>
      <a href="#" class="whitespace-nowrap lg:whitespace-normal">Settings</a>
    </div>
  </aside>

  <!-- Content: takes remaining space -->
  <main class="flex-1 p-4 lg:p-8">
    <h1 class="text-xl font-bold">Dashboard</h1>
    <!-- ... -->
  </main>
</div>
```

What happens at each breakpoint:
- **Mobile**: `flex-col` → sidebar on top as horizontal nav, content below
- **Desktop (lg+)**: `flex-row` → sidebar on left, content fills remaining space

## flex-1 vs flex-none vs flex-auto

```html
<div class="flex gap-4">
  <div class="flex-none w-16">Fixed</div>   <!-- Never grows/shrinks: 64px -->
  <div class="flex-1">Fills space</div>      <!-- Grows to fill remaining -->
  <div class="flex-none w-16">Fixed</div>   <!-- Never grows/shrinks: 64px -->
</div>
```

- `flex-none` = `flex: none` → fixed size, ignores available space
- `flex-1` = `flex: 1 1 0%` → grows and shrinks equally, starts at 0 width
- `flex-auto` = `flex: 1 1 auto` → grows and shrinks, starts at content width

## Responsive Direction: Stack on Mobile, Row on Desktop

```html
<!-- User profile card -->
<div class="flex flex-col sm:flex-row items-center gap-4 p-4 bg-white rounded-lg">
  <img src="avatar.jpg" alt="User" class="w-16 h-16 rounded-full flex-none">
  <div class="flex-1 text-center sm:text-left">
    <h3 class="font-semibold">Jane Smith</h3>
    <p class="text-sm text-gray-500">Product Manager</p>
  </div>
  <button class="px-4 py-2 bg-blue-500 text-white rounded flex-none">
    Message
  </button>
</div>
```

- **Mobile**: column layout — avatar, text, button stacked vertically, centered
- **sm+**: row layout — avatar left, text middle (grows), button right

## Wrapping: When Items Don't Fit

```html
<!-- Tag list that wraps -->
<div class="flex flex-wrap gap-2">
  <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">React</span>
  <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">Node.js</span>
  <span class="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">TypeScript</span>
  <span class="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm">Tailwind</span>
  <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">Docker</span>
</div>
```

Without `flex-wrap`, items overflow the container. With it, they wrap to the next line when space runs out. Works at every screen size without breakpoints.

## Alignment: justify and items

```html
<!-- Horizontal alignment (main axis) -->
<div class="flex justify-between">  <!-- Space between items -->
<div class="flex justify-center">   <!-- Center items -->
<div class="flex justify-end">      <!-- Push to end -->

<!-- Vertical alignment (cross axis) -->
<div class="flex items-center">     <!-- Vertically center -->
<div class="flex items-start">      <!-- Align to top -->
<div class="flex items-stretch">    <!-- Stretch to fill height (default) -->
```

### Common Pattern: Space Between with Centering

```html
<!-- Header: logo left, nav right, vertically centered -->
<header class="flex items-center justify-between p-4">
  <div class="font-bold text-xl">LaunchPad</div>
  <nav class="flex gap-4">
    <a href="#">Docs</a>
    <a href="#">Pricing</a>
    <a href="#">Login</a>
  </nav>
</header>
```

## The Complete Responsive Layout

```html
<body class="min-h-screen bg-gray-50">
  <!-- Top bar: always visible -->
  <header class="flex items-center justify-between p-4 bg-white border-b">
    <div class="flex items-center gap-3">
      <!-- Hamburger: visible on mobile only -->
      <button class="lg:hidden p-1" aria-label="Menu">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
      <h1 class="font-bold text-lg">LaunchPad</h1>
    </div>
    <div class="flex items-center gap-3">
      <span class="hidden sm:inline text-sm text-gray-500">jane@company.com</span>
      <img src="avatar.jpg" alt="Profile" class="w-8 h-8 rounded-full">
    </div>
  </header>

  <!-- Body: sidebar + content -->
  <div class="flex">
    <!-- Sidebar: hidden mobile, visible desktop -->
    <aside class="hidden lg:flex flex-col w-64 bg-white border-r min-h-[calc(100vh-64px)] p-4">
      <nav class="flex flex-col gap-1">
        <a href="#" class="px-3 py-2 rounded bg-blue-50 text-blue-700 font-medium">Dashboard</a>
        <a href="#" class="px-3 py-2 rounded hover:bg-gray-100">Projects</a>
        <a href="#" class="px-3 py-2 rounded hover:bg-gray-100">Team</a>
        <a href="#" class="px-3 py-2 rounded hover:bg-gray-100">Reports</a>
      </nav>
    </aside>

    <!-- Main content: fills remaining space -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8">
      <!-- Page header with action -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
        <h2 class="text-2xl font-bold">Projects</h2>
        <button class="px-4 py-2 bg-blue-600 text-white rounded-lg w-full sm:w-auto">
          New Project
        </button>
      </div>

      <!-- Content goes here -->
      <div class="space-y-4">
        <!-- Project rows -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-white rounded-lg shadow-sm gap-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-blue-100 rounded flex items-center justify-center flex-none">
              📁
            </div>
            <div>
              <p class="font-medium">Website Redesign</p>
              <p class="text-sm text-gray-500">Updated 2 hours ago</p>
            </div>
          </div>
          <div class="flex items-center gap-2 sm:flex-none">
            <span class="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">Active</span>
            <span class="text-sm text-gray-500">3 members</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</body>
```

## Debugging Flex Layouts

When flex layouts break, check these in order:

1. **Is `flex` applied to the parent?** (not the children)
2. **Is `flex-1` on the right child?** (the one that should grow)
3. **Is `flex-none` on fixed-width items?** (prevents unwanted shrinking)
4. **Is `min-w-0` needed?** (flex items have `min-width: auto` by default, which can prevent shrinking below content width)

```html
<!-- Common fix: text overflow in flex items -->
<div class="flex gap-4">
  <div class="flex-1 min-w-0">  <!-- min-w-0 allows text to truncate -->
    <p class="truncate">Very long text that should truncate instead of overflowing...</p>
  </div>
  <div class="flex-none">Button</div>
</div>
```

## What You Learned

- **`flex`** — enables flexbox on a container
- **`flex-col` / `flex-row`** — stack vs side-by-side (responsive with `lg:flex-row`)
- **`flex-1`** — grow to fill space; **`flex-none`** — stay fixed
- **`flex-wrap`** — allow items to wrap when they don't fit
- **`justify-*`** — horizontal alignment; **`items-*`** — vertical alignment
- **`gap-*`** — spacing between flex items (replaces margin hacks)
- **`min-w-0`** — fix for text overflow in flex items

The sidebar and content no longer fight. But the dashboard cards need a proper grid — not just flex wrapping. CSS Grid gives us precise control over columns and rows.

---

[← Chapter 1: Mobile First](chapter-01-mobile-first.md) | [Chapter 3: Grid Systems →](chapter-03-grid.md)
