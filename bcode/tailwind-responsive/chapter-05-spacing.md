# Chapter 5: Responsive Spacing

[← Chapter 4: Typography](chapter-04-typography.md) | [Chapter 6: Navigation →](chapter-06-navigation.md)

---

## The Breakage

Jake's Figma has generous 48px padding on every section. You implement it faithfully:

```html
<section class="p-12">
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-8">
    <div class="p-8 bg-white rounded-lg shadow">
      <h3 class="text-xl font-bold mb-6">Active Projects</h3>
      <p class="text-gray-600">You have 12 active projects...</p>
    </div>
    <div class="p-8 bg-white rounded-lg shadow">
      <h3 class="text-xl font-bold mb-6">Team Members</h3>
      <p class="text-gray-600">8 team members online...</p>
    </div>
  </div>
</section>
```

On a 375px phone: `p-12` = 48px padding on each side. That leaves 375 - 96 = 279px for content. The cards have `p-8` (32px) inside, leaving barely 200px for actual text. Everything feels crushed.

Diana: "There's more padding than content on my phone."

## Responsive Padding and Margin

Scale spacing with breakpoints — tight on mobile, generous on desktop:

```html
<section class="p-4 sm:p-6 lg:p-8 xl:p-12">
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
    <div class="p-4 sm:p-6 lg:p-8 bg-white rounded-lg shadow">
      <h3 class="text-xl font-bold mb-3 sm:mb-4 lg:mb-6">Active Projects</h3>
      <p class="text-gray-600">You have 12 active projects...</p>
    </div>
    <div class="p-4 sm:p-6 lg:p-8 bg-white rounded-lg shadow">
      <h3 class="text-xl font-bold mb-3 sm:mb-4 lg:mb-6">Team Members</h3>
      <p class="text-gray-600">8 team members online...</p>
    </div>
  </div>
</section>
```

Now on a 375px phone: `p-4` = 16px per side → 343px for content. Much better.

## The Container Utility

Tailwind's `container` centers content and caps width at each breakpoint:

```html
<!-- Auto-centers with max-width at each breakpoint -->
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <h1 class="text-2xl font-bold">Dashboard</h1>
  <!-- Content stays readable, never stretches to full ultrawide width -->
</div>
```

Default container widths match breakpoints:
- sm: max-width 640px
- md: max-width 768px
- lg: max-width 1024px
- xl: max-width 1280px
- 2xl: max-width 1536px

## Max-Width for Content Control

Sometimes you want a narrower content area regardless of screen size:

```html
<!-- Narrow content column (great for settings pages, forms) -->
<div class="max-w-2xl mx-auto px-4 sm:px-6">
  <h1 class="text-2xl font-bold mb-6">Account Settings</h1>
  <form class="space-y-6">
    <!-- Form fields -->
  </form>
</div>

<!-- Wide but not full-bleed (dashboards) -->
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Dashboard widgets -->
  </div>
</div>
```

## Space-Y for Vertical Rhythm

Instead of adding `mb-*` to every child, use `space-y-*` on the parent:

```html
<!-- Before: manual margins everywhere -->
<div>
  <div class="mb-4">Item 1</div>
  <div class="mb-4">Item 2</div>
  <div class="mb-4">Item 3</div>  <!-- Last item has unnecessary margin -->
</div>

<!-- After: space-y handles it -->
<div class="space-y-4 sm:space-y-6">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

`space-y-*` adds margin-top to every child except the first. Responsive variants let you increase spacing on larger screens.

## A Complete Responsive Page Layout

```html
<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="bg-white border-b px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <h1 class="text-lg sm:text-xl font-bold">LaunchPad</h1>
      <nav class="hidden sm:flex gap-4 text-sm">
        <a href="#" class="text-gray-600 hover:text-gray-900">Projects</a>
        <a href="#" class="text-gray-600 hover:text-gray-900">Team</a>
      </nav>
    </div>
  </header>

  <!-- Main content -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12">
    <div class="space-y-6 sm:space-y-8 lg:space-y-12">
      <!-- Section 1 -->
      <section class="bg-white rounded-lg p-4 sm:p-6 shadow-sm">
        <h2 class="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Overview</h2>
        <p class="text-gray-600">Your dashboard content here.</p>
      </section>

      <!-- Section 2 -->
      <section class="bg-white rounded-lg p-4 sm:p-6 shadow-sm">
        <h2 class="text-lg sm:text-xl font-semibold mb-3 sm:mb-4">Activity</h2>
        <p class="text-gray-600">Recent activity feed.</p>
      </section>
    </div>
  </main>
</div>
```

## The Spacing Scale Cheat Sheet

| Class | Value | Use case |
|---|---|---|
| `p-2` / `m-2` | 8px | Tight: badges, tags |
| `p-4` / `m-4` | 16px | Default: cards on mobile |
| `p-6` / `m-6` | 24px | Comfortable: cards on tablet |
| `p-8` / `m-8` | 32px | Generous: sections on desktop |
| `p-12` / `m-12` | 48px | Spacious: hero sections |
| `gap-4` | 16px | Grid/flex gaps on mobile |
| `gap-6` | 24px | Grid/flex gaps on tablet+ |

## What You Learned

- **Responsive padding/margin** — `p-4 sm:p-6 lg:p-8` scales spacing with screen size
- **`container mx-auto`** — centers content with max-width at each breakpoint
- **`max-w-*`** — caps content width (`max-w-2xl` for forms, `max-w-7xl` for dashboards)
- **`space-y-*`** — vertical spacing between children without manual margins
- **`px-4 sm:px-6 lg:px-8`** — the standard responsive horizontal padding pattern
- **Spacing ratio** — mobile spacing should be roughly 50-60% of desktop spacing

The spacing is breathing now. But the navigation bar? On mobile, all seven nav items try to fit in one row and overflow off-screen.

---

[← Chapter 4: Typography](chapter-04-typography.md) | [Chapter 6: Navigation →](chapter-06-navigation.md)
