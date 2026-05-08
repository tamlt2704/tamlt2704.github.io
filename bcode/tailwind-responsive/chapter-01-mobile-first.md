# Chapter 1: Mobile First

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Flexbox Layouts →](chapter-02-flexbox.md)

---

## The Breakage

Diana sends a screenshot from her iPhone. The LaunchPad dashboard:

- Sidebar takes up 300px (half the screen)
- Main content is squished into the remaining space
- Cards are 400px wide and overflow off-screen
- Text is 16px — fine on desktop, but the layout makes it unreadable

The CSS:

```html
<div class="flex">
  <aside class="w-[300px]">...</aside>
  <main class="flex-1">
    <div class="grid grid-cols-3 gap-6">
      <div class="w-[400px]">Card 1</div>
      <div class="w-[400px]">Card 2</div>
      <div class="w-[400px]">Card 3</div>
    </div>
  </main>
</div>
```

Fixed widths everywhere. Three-column grid on all screens. This was designed for 1440px and nothing else.

## The Mobile-First Mindset

Mobile-first doesn't mean "mobile only." It means:

1. **Start with the smallest screen** — what's the simplest layout that works?
2. **Add complexity as space allows** — more columns, sidebars, larger text

In Tailwind, this is built into the breakpoint system:

```html
<!-- Unprefixed = applies to ALL screens (mobile base) -->
<!-- Prefixed = applies at that breakpoint AND ABOVE -->

<div class="text-sm md:text-base lg:text-lg">
  <!-- Mobile: small text -->
  <!-- Tablet (768px+): normal text -->
  <!-- Laptop (1024px+): large text -->
</div>
```

Think of it as progressive enhancement: start simple, add features for bigger screens.

## Fixing the Dashboard: Step by Step

### Step 1: Hide the Sidebar on Mobile

On a 375px screen, a sidebar is useless. Hide it and show it on larger screens:

```html
<div class="flex">
  <!-- Hidden on mobile, visible on lg+ -->
  <aside class="hidden lg:block lg:w-64">
    <nav>...</nav>
  </aside>

  <main class="flex-1 p-4">
    ...
  </main>
</div>
```

- Mobile: sidebar is `hidden`, main content gets full width
- Laptop (1024px+): sidebar appears at 256px (`w-64`)

### Step 2: Responsive Grid

Cards should stack on mobile, 2 columns on tablet, 3 on desktop:

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="bg-white rounded-lg p-4 shadow">Card 1</div>
  <div class="bg-white rounded-lg p-4 shadow">Card 2</div>
  <div class="bg-white rounded-lg p-4 shadow">Card 3</div>
</div>
```

- Mobile (< 640px): 1 column — cards stack vertically
- Small (640px+): 2 columns
- Large (1024px+): 3 columns

No fixed widths. Cards fill their grid cell.

### Step 3: Remove Fixed Widths

Replace every `w-[400px]` with responsive utilities:

```html
<!-- BEFORE: fixed width, breaks on mobile -->
<div class="w-[400px]">...</div>

<!-- AFTER: full width, constrained on larger screens -->
<div class="w-full max-w-md">...</div>
```

`w-full` = 100% of parent. `max-w-md` = never wider than 448px. Works at every screen size.

## The Complete Responsive Dashboard Shell

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com"></script>
  <title>LaunchPad</title>
</head>
<body class="bg-gray-100 min-h-screen">

  <!-- Mobile header (visible on mobile, hidden on lg+) -->
  <header class="lg:hidden bg-white border-b p-4 flex items-center justify-between">
    <h1 class="text-lg font-semibold">LaunchPad</h1>
    <button class="p-2" aria-label="Open menu">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
    </button>
  </header>

  <div class="flex">
    <!-- Sidebar: hidden on mobile, visible on lg+ -->
    <aside class="hidden lg:flex lg:flex-col lg:w-64 bg-white border-r min-h-screen p-4">
      <h1 class="text-xl font-bold mb-8">LaunchPad</h1>
      <nav class="space-y-2">
        <a href="#" class="block px-3 py-2 rounded bg-blue-50 text-blue-700">Dashboard</a>
        <a href="#" class="block px-3 py-2 rounded hover:bg-gray-50">Projects</a>
        <a href="#" class="block px-3 py-2 rounded hover:bg-gray-50">Team</a>
        <a href="#" class="block px-3 py-2 rounded hover:bg-gray-50">Settings</a>
      </nav>
    </aside>

    <!-- Main content -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8">
      <h2 class="text-xl sm:text-2xl font-bold mb-6">Dashboard</h2>

      <!-- Stats cards: 1 col → 2 col → 4 col -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-lg p-4 shadow-sm">
          <p class="text-sm text-gray-500">Total Projects</p>
          <p class="text-2xl font-bold">24</p>
        </div>
        <div class="bg-white rounded-lg p-4 shadow-sm">
          <p class="text-sm text-gray-500">Active Tasks</p>
          <p class="text-2xl font-bold">142</p>
        </div>
        <div class="bg-white rounded-lg p-4 shadow-sm">
          <p class="text-sm text-gray-500">Team Members</p>
          <p class="text-2xl font-bold">8</p>
        </div>
        <div class="bg-white rounded-lg p-4 shadow-sm">
          <p class="text-sm text-gray-500">Completion</p>
          <p class="text-2xl font-bold">67%</p>
        </div>
      </div>

      <!-- Project list: responsive table/cards -->
      <div class="bg-white rounded-lg shadow-sm p-4">
        <h3 class="font-semibold mb-4">Recent Projects</h3>
        <div class="space-y-3">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 bg-gray-50 rounded">
            <div>
              <p class="font-medium">Website Redesign</p>
              <p class="text-sm text-gray-500">Due: Jan 15</p>
            </div>
            <span class="mt-2 sm:mt-0 inline-block px-2 py-1 text-xs bg-green-100 text-green-700 rounded w-fit">
              On Track
            </span>
          </div>
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 bg-gray-50 rounded">
            <div>
              <p class="font-medium">API Migration</p>
              <p class="text-sm text-gray-500">Due: Feb 1</p>
            </div>
            <span class="mt-2 sm:mt-0 inline-block px-2 py-1 text-xs bg-yellow-100 text-yellow-700 rounded w-fit">
              At Risk
            </span>
          </div>
        </div>
      </div>
    </main>
  </div>

</body>
</html>
```

## The Viewport Meta Tag

This line is critical:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

Without it, mobile browsers render the page at desktop width (typically 980px) and zoom out. With it, the browser uses the actual device width. **Every responsive page needs this.**

## Testing Your Breakpoints

Open Chrome DevTools (`F12`), click the device toggle (`Ctrl+Shift+M`), and test at:

| Width | What you're testing |
|---|---|
| 320px | Smallest phones (iPhone SE) |
| 375px | Standard phones (iPhone 14) |
| 768px | Tablets (iPad portrait) |
| 1024px | Laptops |
| 1440px | Desktop monitors |
| 1920px | Large desktops |

Drag the width slider and watch your layout adapt. If anything breaks, you've found your next fix.

## Common Mistakes

### 1. Using max-width breakpoints (desktop-first)

```html
<!-- WRONG: desktop-first thinking -->
<div class="grid-cols-3 max-md:grid-cols-1">

<!-- RIGHT: mobile-first -->
<div class="grid-cols-1 md:grid-cols-3">
```

Tailwind is mobile-first by default. Fight the urge to start with the desktop layout.

### 2. Forgetting that unprefixed = all screens

```html
<!-- This hides on ALL screens, including desktop -->
<div class="hidden md:block">
```

`hidden` applies everywhere. `md:block` overrides it at 768px+. This is correct — but make sure you intended it.

### 3. Using px values instead of Tailwind spacing

```html
<!-- FRAGILE: fixed pixels -->
<div class="ml-[300px]">

<!-- RESPONSIVE: Tailwind utilities -->
<div class="ml-0 lg:ml-64">
```

## What You Learned

- **Mobile-first** — design for small screens first, enhance for larger
- **Breakpoint prefixes** — `sm:`, `md:`, `lg:`, `xl:`, `2xl:` apply at that width and above
- **Unprefixed = base** — applies to all screens (your mobile layout)
- **Hide/show pattern** — `hidden lg:block` for sidebar
- **Responsive grid** — `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`
- **Viewport meta tag** — required for mobile rendering
- **No fixed widths** — use `w-full`, `max-w-*`, and responsive utilities

The dashboard no longer breaks on Diana's phone. But the sidebar and content still fight for space on tablets. We need better flex layouts.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Flexbox Layouts →](chapter-02-flexbox.md)
