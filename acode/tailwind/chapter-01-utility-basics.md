# Chapter 1: Your First Utility Classes — The Card

[← Overview](chapter-00-overview.md) | [Chapter 2: Layout →](chapter-02-layout.md)

---

## The Task

Sora drops a Figma frame in Slack: "Start with the metric card. It's used everywhere. Here's the spec."

The card:
- White background, rounded corners (8px)
- Subtle shadow
- 24px padding
- Title in gray, value in black, large and bold
- A small colored indicator (green = up, red = down)

---

## Setup

```bash
npm create vite@latest pixelflow -- --template react
cd pixelflow
npm install -D tailwindcss @tailwindcss/vite
```

Add the plugin to `vite.config.ts`:

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
```

Import Tailwind in your CSS entry point (`src/index.css`):

```css
@import "tailwindcss";
```

That's it. No config file needed to start. Tailwind v4 auto-detects your content.

---

## The Mental Model

Traditional CSS:

```css
.metric-card {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-card__title {
  color: #6b7280;
  font-size: 14px;
}

.metric-card__value {
  color: #111827;
  font-size: 30px;
  font-weight: 700;
}
```

Tailwind:

```html
<div class="bg-white rounded-lg p-6 shadow-sm">
  <p class="text-gray-500 text-sm">Revenue</p>
  <p class="text-gray-900 text-3xl font-bold">$12,480</p>
</div>
```

Same result. No CSS file. No class name invention. No context switching.

Dev: "But the HTML looks ugly with all those classes."

You: "You read it once and know exactly what it looks like. Try reading `.metric-card__value` and tell me the font size without opening the CSS file."

Dev: "...fair."

---

## Spacing: The 4px Grid

Tailwind uses a spacing scale based on 4px increments:

```
────────────────────────────────────────────────
 Class    │ Value    │ Pixels
────────────────────────────────────────────────
 p-0      │ 0       │ 0px
 p-1      │ 0.25rem │ 4px
 p-2      │ 0.5rem  │ 8px
 p-3      │ 0.75rem │ 12px
 p-4      │ 1rem    │ 16px
 p-5      │ 1.25rem │ 20px
 p-6      │ 1.5rem  │ 24px
 p-8      │ 2rem    │ 32px
 p-10     │ 2.5rem  │ 40px
 p-12     │ 3rem    │ 48px
────────────────────────────────────────────────
```

The same scale works for margin (`m-`), gap (`gap-`), width (`w-`), height (`h-`), and more.

Directional variants:

```html
<div class="p-6">          <!-- all sides: 24px -->
<div class="px-4">         <!-- horizontal (left + right): 16px -->
<div class="py-2">         <!-- vertical (top + bottom): 8px -->
<div class="pt-8">         <!-- top only: 32px -->
<div class="mb-4">         <!-- margin-bottom: 16px -->
<div class="ml-auto">      <!-- margin-left: auto (push right) -->
```

Sora's 8px grid maps perfectly: `p-2` = 8px, `p-4` = 16px, `p-6` = 24px.

---

## Colors: The Palette

Tailwind ships a curated color palette. Each color has shades from 50 (lightest) to 950 (darkest):

```
────────────────────────────────────────────────
 Class           │ What It Styles
────────────────────────────────────────────────
 bg-blue-500     │ background-color
 text-gray-700   │ color (text)
 border-red-300  │ border-color
 ring-green-400  │ outline ring color
────────────────────────────────────────────────
```

The shade scale:

```
50   100  200  300  400  500  600  700  800  900  950
 ░    ░    ▒    ▒    ▓    █    █    ██   ██   ███  ███
light ─────────────────────────────────────────── dark
```

Common patterns:
- **Background**: `bg-white`, `bg-gray-50`, `bg-blue-500`
- **Text**: `text-gray-900` (headings), `text-gray-500` (secondary)
- **Borders**: `border-gray-200` (subtle), `border-red-500` (error)

---

## Typography

```html
<!-- Size -->
<p class="text-xs">12px</p>
<p class="text-sm">14px</p>
<p class="text-base">16px (default)</p>
<p class="text-lg">18px</p>
<p class="text-xl">20px</p>
<p class="text-2xl">24px</p>
<p class="text-3xl">30px</p>

<!-- Weight -->
<p class="font-normal">400</p>
<p class="font-medium">500</p>
<p class="font-semibold">600</p>
<p class="font-bold">700</p>

<!-- Color -->
<p class="text-gray-900">Primary text</p>
<p class="text-gray-500">Secondary text</p>
<p class="text-gray-400">Muted text</p>
```

---

## Borders & Shadows

```html
<!-- Rounded corners -->
<div class="rounded">      <!-- 4px -->
<div class="rounded-md">   <!-- 6px -->
<div class="rounded-lg">   <!-- 8px -->
<div class="rounded-xl">   <!-- 12px -->
<div class="rounded-2xl">  <!-- 16px -->
<div class="rounded-full"> <!-- 9999px (pill/circle) -->

<!-- Shadows -->
<div class="shadow-sm">    <!-- subtle -->
<div class="shadow">       <!-- default -->
<div class="shadow-md">    <!-- medium -->
<div class="shadow-lg">    <!-- large -->
<div class="shadow-xl">    <!-- extra large -->

<!-- Borders -->
<div class="border">                   <!-- 1px solid, default gray -->
<div class="border-2 border-blue-500"> <!-- 2px solid blue -->
```

---

## Building the Metric Card

Now you have everything. Let's build Sora's card:

```tsx
function MetricCard({ title, value, change, trend }) {
  return (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
      <p className="text-sm text-gray-500 font-medium">{title}</p>
      <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
      <div className="mt-2 flex items-center gap-1">
        <span className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
          {trend === 'up' ? '↑' : '↓'}
        </span>
        <span className={`text-sm font-medium ${
          trend === 'up' ? 'text-green-600' : 'text-red-600'
        }`}>
          {change}
        </span>
        <span className="text-sm text-gray-400 ml-1">vs last month</span>
      </div>
    </div>
  );
}
```

Usage:

```tsx
<MetricCard title="Revenue" value="$12,480" change="+12.5%" trend="up" />
<MetricCard title="Churn" value="2.4%" change="+0.3%" trend="down" />
```

---

## The Pattern: Reading Tailwind Classes

Read them left to right, like a sentence:

```
bg-white rounded-lg p-6 shadow-sm border border-gray-100
│        │          │   │         │      │
│        │          │   │         │      └─ border color: gray-100
│        │          │   │         └─ 1px border
│        │          │   └─ small shadow
│        │          └─ padding: 24px all sides
│        └─ border-radius: 8px
└─ background: white
```

You can look at any element and know exactly what it looks like without opening a CSS file.

---

## Arbitrary Values

Sora: "The card needs exactly 18px padding on mobile. Not 16, not 20. Eighteen."

```html
<div class="p-[18px]">
```

Square brackets let you use any value. Use sparingly — if you're using them everywhere, extend the theme instead.

```html
<div class="w-[calc(100%-2rem)]">   <!-- calc works -->
<div class="bg-[#1a1a2e]">          <!-- hex colors -->
<div class="text-[15px]">           <!-- exact sizes -->
<div class="grid-cols-[200px_1fr]"> <!-- grid templates -->
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Category                        │ Pattern
────────────────────────────────┼──────────────────────────────────────
Spacing (padding)               │ p-{n}, px-{n}, py-{n}, pt/pr/pb/pl
Spacing (margin)                │ m-{n}, mx-{n}, my-{n}, mt/mr/mb/ml
Background                      │ bg-{color}-{shade}
Text color                      │ text-{color}-{shade}
Font size                       │ text-{xs|sm|base|lg|xl|2xl|...}
Font weight                     │ font-{normal|medium|semibold|bold}
Border radius                   │ rounded-{none|sm|md|lg|xl|full}
Shadow                          │ shadow-{sm|DEFAULT|md|lg|xl}
Border                          │ border, border-{n}, border-{color}
Width                           │ w-{n}, w-full, w-screen, w-auto
Height                          │ h-{n}, h-full, h-screen
Arbitrary value                 │ property-[exact-value]
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "The card looks great. Now I need three of them in a row. And on mobile they should stack vertically. And the sidebar needs to be 256px wide. And the main content fills the rest."

Layout. Flexbox and Grid — the Tailwind way.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Layout →](chapter-02-layout.md)
