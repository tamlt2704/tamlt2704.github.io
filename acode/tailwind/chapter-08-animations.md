# Chapter 8: Animations & Micro-Interactions

[← Chapter 7: Dark Mode](chapter-07-dark-mode.md) | [Chapter 9: Forms →](chapter-09-forms.md)

---

## The Task

Sora: "The dashboard feels dead. I need loading spinners, skeleton screens, smooth entrances, and hover effects that make it feel alive. Nothing flashy — just enough motion to feel responsive."

---

## Built-in Animations

Tailwind ships four animations out of the box:

```html
<!-- Spin (loading spinners) -->
<svg class="animate-spin h-5 w-5 text-brand-600">...</svg>

<!-- Ping (notification dot) -->
<span class="animate-ping absolute h-3 w-3 rounded-full bg-red-400"></span>

<!-- Pulse (skeleton loading) -->
<div class="animate-pulse bg-gray-200 dark:bg-gray-700 h-4 rounded"></div>

<!-- Bounce (attention) -->
<span class="animate-bounce">↓</span>
```

---

## Loading Spinner

```tsx
function Spinner({ size = "md" }) {
  const sizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-8 w-8",
  };

  return (
    <svg
      className={`animate-spin ${sizes[size]} text-brand-600`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12" cy="12" r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}

// Button with loading state
function LoadingButton({ loading, children, ...props }) {
  return (
    <button
      className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors"
      disabled={loading}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}
```

---

## Skeleton Screens

Instead of a spinner, show the shape of content that's loading:

```tsx
function MetricCardSkeleton() {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg p-6 border border-gray-100 dark:border-gray-800">
      <div className="animate-pulse space-y-3">
        <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-8 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <MetricCardSkeleton />
      <MetricCardSkeleton />
      <MetricCardSkeleton />
    </div>
  );
}
```

`animate-pulse` fades opacity between 100% and 50%, creating a breathing effect.

---

## Transforms

Tailwind supports CSS transforms as utilities:

```html
<!-- Scale -->
<div class="hover:scale-105 transition-transform">Grows on hover</div>
<div class="hover:scale-95 transition-transform">Shrinks on hover (press effect)</div>

<!-- Translate (move) -->
<div class="hover:-translate-y-1 transition-transform">Lifts up on hover</div>
<div class="hover:translate-x-1 transition-transform">Shifts right</div>

<!-- Rotate -->
<div class="hover:rotate-3 transition-transform">Slight tilt</div>
<svg class="hover:rotate-180 transition-transform duration-300">Arrow that flips</svg>
```

---

## The Lift-on-Hover Card

A subtle but effective pattern:

```tsx
function ProjectCard({ name, description, members }) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg p-6 border border-gray-200 dark:border-gray-800 hover:shadow-lg hover:-translate-y-1 transition-all duration-200 cursor-pointer">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{name}</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{description}</p>
      <div className="mt-4 flex -space-x-2">
        {members.map((m, i) => (
          <img
            key={i}
            src={m.avatar}
            alt={m.name}
            className="w-8 h-8 rounded-full border-2 border-white dark:border-gray-900"
          />
        ))}
      </div>
    </div>
  );
}
```

Key: `hover:shadow-lg hover:-translate-y-1 transition-all duration-200` — the card lifts and gains shadow simultaneously.

---

## Notification Dot with Ping

```tsx
function NotificationBell({ hasNotifications }) {
  return (
    <button className="relative p-2 rounded-lg text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>

      {hasNotifications && (
        <span className="absolute top-1.5 right-1.5 flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500" />
        </span>
      )}
    </button>
  );
}
```

The ping animation: an expanding, fading circle behind a solid dot.

---

## Custom Keyframe Animations

For animations beyond the built-in four, define custom keyframes:

```css
@import "tailwindcss";

@theme {
  --animate-fade-in: fade-in 0.3s ease-out;
  --animate-slide-up: slide-up 0.3s ease-out;
  --animate-slide-down: slide-down 0.2s ease-out;
  --animate-scale-in: scale-in 0.2s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slide-down {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
```

Use them:

```html
<div class="animate-fade-in">Fades in</div>
<div class="animate-slide-up">Slides up into view</div>
<div class="animate-scale-in">Scales in (good for modals)</div>
```

---

## Dropdown Menu with Animation

```tsx
function Dropdown({ isOpen, children }) {
  if (!isOpen) return null;

  return (
    <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 animate-scale-in origin-top-right">
      {children}
    </div>
  );
}

function DropdownItem({ children, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
    >
      {children}
    </button>
  );
}
```

`origin-top-right` sets the transform origin — the scale animation expands from the top-right corner (where the trigger button is).

---

## Accordion / Collapsible

```tsx
function Accordion({ title, children }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-gray-200 dark:border-gray-800">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between py-4 text-left text-sm font-medium text-gray-900 dark:text-white hover:text-brand-600 transition-colors"
      >
        {title}
        <svg
          className={`w-5 h-5 text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <div className={`overflow-hidden transition-all duration-200 ${isOpen ? 'max-h-96 pb-4' : 'max-h-0'}`}>
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {children}
        </div>
      </div>
    </div>
  );
}
```

The trick: `max-h-0` → `max-h-96` with `transition-all` creates a smooth expand/collapse.

---

## Reduced Motion

Some users have motion sensitivity. Respect their preference:

```html
<!-- Disable animation for users who prefer reduced motion -->
<div class="animate-bounce motion-reduce:animate-none">
  Bounces normally, static for reduced-motion users
</div>

<!-- Alternative: only animate for users who are OK with it -->
<div class="motion-safe:animate-pulse">
  Only pulses if user hasn't set prefers-reduced-motion
</div>
```

Sora: "Always add `motion-reduce:` alternatives. It's not optional."

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Classes
────────────────────────────────┼──────────────────────────────────────
Loading spinner                 │ animate-spin
Skeleton loading                │ animate-pulse bg-gray-200 rounded
Notification ping               │ animate-ping
Lift on hover                   │ hover:-translate-y-1 hover:shadow-lg transition-all
Press effect                    │ active:scale-95 transition-transform
Rotate icon                     │ rotate-180 transition-transform
Expand/collapse                 │ max-h-0 → max-h-96 overflow-hidden transition-all
Transform origin                │ origin-top-right
Respect motion preference       │ motion-reduce:animate-none
Custom animation                │ Define @keyframes + --animate-* in @theme
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "The dashboard feels alive. Now I need the settings page — forms everywhere. Text inputs, selects, checkboxes, toggles, validation states. Make them look consistent and accessible."

Forms and input styling.

---

[← Chapter 7: Dark Mode](chapter-07-dark-mode.md) | [Chapter 9: Forms →](chapter-09-forms.md)
