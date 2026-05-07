# Chapter 5: Colors, Gradients & Theming

[← Chapter 4: Typography](chapter-04-typography.md) | [Chapter 6: States & Transitions →](chapter-06-states-transitions.md)

---

## The Task

Sora: "Tailwind's default blue is fine for prototyping, but we need our own brand colors. Pixelflow's primary is indigo-ish, the accent is a warm amber, and we need semantic colors for success/warning/error. Also — gradients on the hero section."

---

## How Tailwind Colors Work

Every color in Tailwind is a scale from 50 (lightest) to 950 (darkest):

```
gray-50   ░░░░░░░░░░  #f9fafb   (backgrounds)
gray-100  ░░░░░░░░░   #f3f4f6   (hover backgrounds)
gray-200  ░░░░░░░░    #e5e7eb   (borders)
gray-300  ░░░░░░░     #d1d5db   (disabled text)
gray-400  ░░░░░░      #9ca3af   (placeholder text)
gray-500  ░░░░░       #6b7280   (secondary text)
gray-600  ░░░░        #4b5563   (body text)
gray-700  ░░░         #374151   (headings)
gray-800  ░░          #1f2937   (dark backgrounds)
gray-900  ░           #111827   (darkest text)
gray-950  █           #030712   (near black)
```

The pattern applies to every color: `red`, `orange`, `amber`, `yellow`, `lime`, `green`, `emerald`, `teal`, `cyan`, `sky`, `blue`, `indigo`, `violet`, `purple`, `fuchsia`, `pink`, `rose`.

---

## Using Colors Everywhere

Colors work with any property prefix:

```html
<!-- Backgrounds -->
<div class="bg-indigo-500">Solid background</div>
<div class="bg-indigo-500/75">75% opacity background</div>

<!-- Text -->
<p class="text-gray-900">Dark text</p>
<p class="text-indigo-600">Brand colored text</p>

<!-- Borders -->
<div class="border border-gray-200">Subtle border</div>
<div class="border-2 border-indigo-500">Strong brand border</div>

<!-- Rings (focus outlines) -->
<button class="ring-2 ring-indigo-500">Focused button</button>

<!-- Shadows (colored) -->
<div class="shadow-lg shadow-indigo-500/25">Colored shadow</div>

<!-- Divide (borders between children) -->
<div class="divide-y divide-gray-200">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

---

## Custom Brand Colors with CSS Variables

Tailwind v4 uses CSS variables natively. Define your brand palette in your CSS:

```css
@import "tailwindcss";

@theme {
  --color-brand-50: #eef2ff;
  --color-brand-100: #e0e7ff;
  --color-brand-200: #c7d2fe;
  --color-brand-300: #a5b4fc;
  --color-brand-400: #818cf8;
  --color-brand-500: #6366f1;
  --color-brand-600: #4f46e5;
  --color-brand-700: #4338ca;
  --color-brand-800: #3730a3;
  --color-brand-900: #312e81;
  --color-brand-950: #1e1b4b;

  --color-accent-50: #fffbeb;
  --color-accent-100: #fef3c7;
  --color-accent-200: #fde68a;
  --color-accent-300: #fcd34d;
  --color-accent-400: #fbbf24;
  --color-accent-500: #f59e0b;
  --color-accent-600: #d97706;
  --color-accent-700: #b45309;
  --color-accent-800: #92400e;
  --color-accent-900: #78350f;
  --color-accent-950: #451a03;

  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}
```

Now use them like any built-in color:

```html
<button class="bg-brand-600 text-white hover:bg-brand-700">
  Primary Action
</button>

<span class="text-accent-500">Highlighted value</span>

<div class="border-l-4 border-success bg-green-50 p-4">
  Success message
</div>
```

---

## Gradients

Tailwind supports linear gradients with direction and color stops:

```html
<!-- Basic gradient -->
<div class="bg-gradient-to-r from-indigo-500 to-purple-500">
  Left to right gradient
</div>

<!-- Three-color gradient -->
<div class="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
  Three stops
</div>

<!-- Directions -->
<div class="bg-gradient-to-t">   <!-- bottom to top -->
<div class="bg-gradient-to-tr">  <!-- to top-right -->
<div class="bg-gradient-to-r">   <!-- left to right -->
<div class="bg-gradient-to-br">  <!-- to bottom-right -->
<div class="bg-gradient-to-b">   <!-- top to bottom -->
<div class="bg-gradient-to-bl">  <!-- to bottom-left -->
<div class="bg-gradient-to-l">   <!-- right to left -->
<div class="bg-gradient-to-tl">  <!-- to top-left -->
```

---

## The Hero Section

Sora's design has a gradient hero with text overlay:

```tsx
function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-brand-600 via-brand-700 to-purple-800">
      {/* Decorative blur circles */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-400/30 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-brand-400/20 rounded-full blur-3xl" />

      {/* Content */}
      <div className="relative max-w-7xl mx-auto px-4 py-24 lg:py-32">
        <h1 className="text-4xl lg:text-6xl font-bold text-white tracking-tight">
          Analytics that
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-200 to-yellow-400">
            {" "}make sense
          </span>
        </h1>
        <p className="mt-6 text-lg text-indigo-100 max-w-2xl">
          Pixelflow gives your team real-time insights without the complexity.
          See what matters, ignore what doesn't.
        </p>
        <div className="mt-8 flex gap-4">
          <button className="px-6 py-3 bg-white text-brand-700 font-semibold rounded-lg hover:bg-gray-100 transition-colors">
            Get Started
          </button>
          <button className="px-6 py-3 bg-white/10 text-white font-semibold rounded-lg border border-white/20 hover:bg-white/20 transition-colors">
            See Demo
          </button>
        </div>
      </div>
    </section>
  );
}
```

Key techniques:
- `bg-gradient-to-br from-brand-600 via-brand-700 to-purple-800` → diagonal gradient
- `bg-purple-400/30 blur-3xl` → decorative blurred circles for depth
- `text-transparent bg-clip-text bg-gradient-to-r` → gradient text effect
- `bg-white/10 border-white/20` → glass-like button with opacity

---

## Gradient Text

The gradient text trick:

```html
<span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
  Gradient Text
</span>
```

How it works:
1. `text-transparent` → makes the text color invisible
2. `bg-clip-text` → clips the background to the text shape
3. `bg-gradient-to-r from-blue-600 to-purple-600` → the gradient shows through

---

## Semantic Color Patterns

Build a consistent system for status colors:

```tsx
function StatusBadge({ status }) {
  const styles = {
    active: "bg-green-50 text-green-700 border-green-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    error: "bg-red-50 text-red-700 border-red-200",
    info: "bg-blue-50 text-blue-700 border-blue-200",
    neutral: "bg-gray-50 text-gray-700 border-gray-200",
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status]}`}>
      {status}
    </span>
  );
}
```

The pattern: light background (50), medium text (700), subtle border (200). Works for every color.

---

## Color Contrast Rules

Sora's accessibility checklist:

```
────────────────────────────────────────────────────────────
 Background    │ Text Color     │ Ratio  │ WCAG
────────────────────────────────────────────────────────────
 white         │ gray-900       │ 17.4:1 │ ✓ AAA
 white         │ gray-700       │ 9.7:1  │ ✓ AAA
 white         │ gray-500       │ 5.0:1  │ ✓ AA
 white         │ gray-400       │ 3.5:1  │ ✗ Fails (decorative only)
 gray-900      │ white          │ 17.4:1 │ ✓ AAA
 brand-600     │ white          │ 4.6:1  │ ✓ AA (large text)
 brand-700     │ white          │ 6.5:1  │ ✓ AA
────────────────────────────────────────────────────────────
```

Rules:
- Body text: minimum 4.5:1 contrast ratio (AA)
- Large text (18px+ bold or 24px+): minimum 3:1
- Use 700+ shades on white backgrounds for body text
- Use 500 for secondary/muted text (passes AA at text-sm+)
- Never use 300 or 400 for meaningful text

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Classes
────────────────────────────────┼──────────────────────────────────────
Brand background                │ bg-brand-600
Brand text                      │ text-brand-600
Opacity on color                │ bg-brand-500/75
Gradient background             │ bg-gradient-to-r from-X to-Y
Three-stop gradient             │ from-X via-Y to-Z
Gradient text                   │ text-transparent bg-clip-text bg-gradient-to-r
Colored shadow                  │ shadow-lg shadow-brand-500/25
Status badge (success)          │ bg-green-50 text-green-700 border-green-200
Decorative blur                 │ absolute bg-X/30 rounded-full blur-3xl
Glass effect                    │ bg-white/10 border-white/20
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "The colors are perfect. But everything feels static. I need hover effects on buttons, focus rings on inputs, active states on nav items. And smooth transitions — nothing should just snap."

States, pseudo-classes, and transitions.

---

[← Chapter 4: Typography](chapter-04-typography.md) | [Chapter 6: States & Transitions →](chapter-06-states-transitions.md)
