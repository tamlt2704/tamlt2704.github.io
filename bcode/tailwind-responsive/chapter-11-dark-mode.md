# Chapter 11: Dark Mode

[← Chapter 10: Forms](chapter-10-forms.md) | [Chapter 12: Container Queries →](chapter-12-container-queries.md)

---

## The Breakage

It's not a layout bug this time. It's a feature request — from 73% of users in the latest survey:

"Please add dark mode. I use the dashboard at night and the white background is blinding."

Diana: "Our competitors all have dark mode. Ship it this sprint."

The current dashboard is hardcoded light:

```html
<div class="bg-white text-gray-900">
  <header class="bg-gray-50 border-b border-gray-200">
    <h1 class="text-xl font-bold text-gray-900">Dashboard</h1>
  </header>
  <main class="bg-gray-100 p-6">
    <div class="bg-white rounded-lg shadow p-4">
      <h2 class="text-lg font-semibold text-gray-800">Revenue</h2>
      <p class="text-gray-600">$48,200 this month</p>
    </div>
  </main>
</div>
```

Every color is explicit. There's no way to flip them without touching every single class.

## Tailwind's Dark Variant

Add `dark:` prefix to any utility. Tailwind applies it when dark mode is active:

```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
  <header class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <h1 class="text-xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
  </header>
  <main class="bg-gray-100 dark:bg-gray-950 p-6">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-4">
      <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100">Revenue</h2>
      <p class="text-gray-600 dark:text-gray-400">$48,200 this month</p>
    </div>
  </main>
</div>
```

## Dark Mode Strategies

### Strategy 1: System Preference (Default)

In `tailwind.config.js`:

```js
// Default behavior — uses prefers-color-scheme media query
module.exports = {
  darkMode: 'media',
  // ...
}
```

Dark mode activates automatically based on the user's OS setting. No toggle needed.

### Strategy 2: Manual Toggle (Class-Based)

```js
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  // ...
}
```

Add/remove `dark` class on `<html>`:

```html
<html class="dark">
  <body class="bg-white dark:bg-gray-900">
    <!-- Dark mode is active -->
  </body>
</html>
```

Toggle with JavaScript:

```html
<button id="theme-toggle" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
  <!-- Sun icon (shown in dark mode) -->
  <svg class="w-5 h-5 hidden dark:block text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0z"/>
  </svg>
  <!-- Moon icon (shown in light mode) -->
  <svg class="w-5 h-5 block dark:hidden text-gray-600" fill="currentColor" viewBox="0 0 20 20">
    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
  </svg>
</button>

<script>
  const toggle = document.getElementById('theme-toggle');
  toggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    const isDark = document.documentElement.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  });

  // Load saved preference
  if (localStorage.theme === 'dark' ||
      (!localStorage.theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
  }
</script>
```

### Strategy 3: Selector (Tailwind 3.4+)

```js
// tailwind.config.js
module.exports = {
  darkMode: ['selector', '[data-theme="dark"]'],
  // ...
}
```

Allows any selector — useful for frameworks that manage themes differently.

## A Complete Dark Mode Component

```html
<div class="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-200">
  <!-- Navigation -->
  <nav class="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-4 py-3">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <span class="text-lg font-bold text-gray-900 dark:text-white">LaunchPad</span>
      <button id="theme-toggle" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
        🌙 / ☀️
      </button>
    </div>
  </nav>

  <!-- Content -->
  <main class="max-w-7xl mx-auto px-4 py-8">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-5 shadow-sm
                  border border-gray-200 dark:border-gray-700">
        <h3 class="font-semibold text-gray-900 dark:text-white">Revenue</h3>
        <p class="text-2xl font-bold mt-2 text-gray-900 dark:text-white">$48,200</p>
        <p class="text-sm text-green-600 dark:text-green-400 mt-1">↑ 12%</p>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg p-5 shadow-sm
                  border border-gray-200 dark:border-gray-700">
        <h3 class="font-semibold text-gray-900 dark:text-white">Users</h3>
        <p class="text-2xl font-bold mt-2 text-gray-900 dark:text-white">2,420</p>
        <p class="text-sm text-green-600 dark:text-green-400 mt-1">↑ 8%</p>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg p-5 shadow-sm
                  border border-gray-200 dark:border-gray-700">
        <h3 class="font-semibold text-gray-900 dark:text-white">Conversion</h3>
        <p class="text-2xl font-bold mt-2 text-gray-900 dark:text-white">3.2%</p>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">No change</p>
      </div>
    </div>
  </main>
</div>
```

## Dark Mode Color Mapping

| Light | Dark | Use |
|---|---|---|
| `bg-white` | `dark:bg-gray-900` | Page/card background |
| `bg-gray-50` | `dark:bg-gray-950` | Subtle background |
| `bg-gray-100` | `dark:bg-gray-800` | Elevated surface |
| `text-gray-900` | `dark:text-white` | Primary text |
| `text-gray-600` | `dark:text-gray-400` | Secondary text |
| `border-gray-200` | `dark:border-gray-700` | Borders |
| `shadow-sm` | `dark:shadow-gray-900/50` | Shadows |

## What You Learned

- **`dark:` variant** — prefix any utility to apply in dark mode
- **`darkMode: 'media'`** — automatic based on OS preference
- **`darkMode: 'class'`** — manual toggle via `dark` class on `<html>`
- **`darkMode: ['selector', '...']`** — custom selector (Tailwind 3.4+)
- **`localStorage`** — persist user's theme preference
- **`hidden dark:block`** — swap icons/content between modes
- **`transition-colors`** — smooth color transitions when toggling

Dark mode is live. But there's a subtler responsive problem: the same stat card component looks great in the main content area but terrible when placed in the narrow sidebar.

---

[← Chapter 10: Forms](chapter-10-forms.md) | [Chapter 12: Container Queries →](chapter-12-container-queries.md)
