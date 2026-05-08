# Chapter 6: Responsive Navigation

[← Chapter 5: Spacing](chapter-05-spacing.md) | [Chapter 7: Images →](chapter-07-images.md)

---

## The Breakage

LaunchPad's navbar has 7 items. On desktop, they sit in a neat horizontal row. On mobile:

```html
<nav class="flex items-center justify-between p-4 bg-white shadow">
  <div class="text-xl font-bold">LaunchPad</div>
  <div class="flex gap-6">
    <a href="#">Dashboard</a>
    <a href="#">Projects</a>
    <a href="#">Team</a>
    <a href="#">Reports</a>
    <a href="#">Settings</a>
    <a href="#">Billing</a>
    <a href="#">Help</a>
  </div>
</nav>
```

On a 375px screen, the links overflow past the viewport edge. Users have to scroll horizontally to find "Settings" and "Help." Diana's screenshot shows the nav cut off mid-word: "Setti..."

QA team: "Navigation is inaccessible on 12 of our 47 test devices."

## The Hamburger Pattern

Hide nav items on mobile, show them when a menu button is tapped:

```html
<nav class="bg-white shadow">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      <!-- Logo -->
      <div class="text-xl font-bold text-gray-900">LaunchPad</div>

      <!-- Desktop nav (hidden on mobile) -->
      <div class="hidden md:flex items-center gap-6">
        <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Dashboard</a>
        <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Projects</a>
        <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Team</a>
        <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Reports</a>
        <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Settings</a>
        <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Billing</a>
        <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Help</a>
      </div>

      <!-- Mobile menu button (hidden on desktop) -->
      <button class="md:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100"
              aria-label="Open menu" aria-expanded="false">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>
  </div>

  <!-- Mobile menu panel (toggle with JS) -->
  <div class="md:hidden hidden" id="mobile-menu">
    <div class="px-4 py-3 space-y-2 border-t">
      <a href="#" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100">Dashboard</a>
      <a href="#" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100">Projects</a>
      <a href="#" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100">Team</a>
      <a href="#" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100">Reports</a>
      <a href="#" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100">Settings</a>
      <a href="#" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100">Billing</a>
      <a href="#" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100">Help</a>
    </div>
  </div>
</nav>
```

The toggle JavaScript:

```html
<script>
  const btn = document.querySelector('[aria-label="Open menu"]');
  const menu = document.getElementById('mobile-menu');
  btn.addEventListener('click', () => {
    const expanded = menu.classList.toggle('hidden');
    btn.setAttribute('aria-expanded', !expanded);
  });
</script>
```

Key classes:
- `hidden md:flex` — hidden on mobile, flex on md+
- `md:hidden` — visible on mobile, hidden on md+
- `block` — stacks links vertically in mobile menu

## Slide-In Sidebar Nav (Alternative)

For apps with many nav items, a slide-in panel works better:

```html
<!-- Overlay -->
<div class="fixed inset-0 bg-black/50 z-40 md:hidden hidden" id="nav-overlay"></div>

<!-- Slide-in panel -->
<aside class="fixed inset-y-0 left-0 w-64 bg-white shadow-xl z-50 transform -translate-x-full
              transition-transform duration-200 ease-in-out md:hidden" id="nav-panel">
  <div class="p-4 border-b flex items-center justify-between">
    <span class="text-lg font-bold">Menu</span>
    <button class="p-2 rounded-md hover:bg-gray-100" aria-label="Close menu">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
  <nav class="p-4 space-y-1">
    <a href="#" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">Dashboard</a>
    <a href="#" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">Projects</a>
    <a href="#" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">Team</a>
    <a href="#" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">Reports</a>
    <a href="#" class="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">Settings</a>
  </nav>
</aside>
```

Open it by removing `-translate-x-full` → `translate-x-0`.

## Responsive Nav with Priority+ Pattern

Show as many items as fit, put the rest in a "More" dropdown:

```html
<nav class="flex items-center gap-1 px-4 h-16 bg-white shadow overflow-hidden">
  <a href="#" class="shrink-0 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md">Dashboard</a>
  <a href="#" class="shrink-0 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md">Projects</a>
  <a href="#" class="shrink-0 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md hidden sm:block">Team</a>
  <a href="#" class="shrink-0 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md hidden md:block">Reports</a>
  <a href="#" class="shrink-0 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md hidden lg:block">Settings</a>

  <!-- "More" button for hidden items -->
  <button class="lg:hidden ml-auto px-3 py-2 text-sm font-medium text-gray-500">
    More ▾
  </button>
</nav>
```

## What You Learned

- **`hidden md:flex`** — hide on mobile, show on desktop
- **`md:hidden`** — show on mobile, hide on desktop
- **Hamburger menu** — button + toggleable panel for mobile nav
- **`aria-label` / `aria-expanded`** — accessibility for toggle buttons
- **Slide-in panel** — `transform -translate-x-full` + transition for drawer nav
- **Priority+ pattern** — show important items first, overflow into "More"
- **`block` vs `flex`** — vertical stacking for mobile menu items

Navigation works on every screen now. But the hero image on the landing page? It's stretching, squishing, and breaking the layout on different aspect ratios.

---

[← Chapter 5: Spacing](chapter-05-spacing.md) | [Chapter 7: Images →](chapter-07-images.md)
