# Chapter 6: States & Transitions — Making Things Interactive

[← Chapter 5: Colors & Theming](chapter-05-colors-theming.md) | [Chapter 7: Dark Mode →](chapter-07-dark-mode.md)

---

## The Task

Sora: "Every interactive element needs feedback. Buttons change on hover. Inputs glow on focus. Disabled things look disabled. And transitions — nothing should just snap from one state to another."

---

## State Variants

Tailwind uses prefixes to style different states:

```html
<button class="bg-brand-600 hover:bg-brand-700 active:bg-brand-800">
  Hover me
</button>
```

The most common state variants:

```
────────────────────────────────────────────────
 Prefix        │ When It Applies
────────────────────────────────────────────────
 hover:        │ Mouse is over the element
 focus:        │ Element has keyboard focus
 focus-visible:│ Focus via keyboard (not click)
 active:       │ Being clicked/pressed
 disabled:     │ Element is disabled
 first:        │ First child
 last:         │ Last child
 odd:          │ Odd children (tables)
 even:         │ Even children (tables)
 group-hover:  │ Parent with "group" class is hovered
 peer-focus:   │ Sibling with "peer" class is focused
────────────────────────────────────────────────
```

---

## Building a Button System

```tsx
function Button({ variant = "primary", size = "md", disabled, children, ...props }) {
  const base = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none";

  const variants = {
    primary: "bg-brand-600 text-white hover:bg-brand-700 active:bg-brand-800 focus-visible:ring-brand-500",
    secondary: "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 active:bg-gray-100 focus-visible:ring-gray-500",
    danger: "bg-red-600 text-white hover:bg-red-700 active:bg-red-800 focus-visible:ring-red-500",
    ghost: "text-gray-700 hover:bg-gray-100 active:bg-gray-200 focus-visible:ring-gray-500",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm gap-1.5",
    md: "px-4 py-2 text-sm gap-2",
    lg: "px-6 py-3 text-base gap-2",
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
```

Key patterns:
- `transition-colors` → smooth color changes (150ms default)
- `focus-visible:ring-2 focus-visible:ring-offset-2` → keyboard focus ring
- `disabled:opacity-50 disabled:pointer-events-none` → disabled state
- `active:bg-brand-800` → pressed state (slightly darker)

---

## Focus Rings

Focus rings are critical for accessibility. Users navigating with keyboard need to see what's focused.

```html
<!-- Focus ring (always shows on focus) -->
<button class="focus:ring-2 focus:ring-blue-500">
  Always shows ring
</button>

<!-- Focus-visible ring (only shows on keyboard focus) -->
<button class="focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">
  Only shows ring on keyboard navigation
</button>

<!-- Ring offset creates space between element and ring -->
<button class="focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2">
  ┌─ ring-offset-2 (2px gap) ─┐
  │  ┌─ ring-2 (2px ring) ─┐  │
  │  │  [ Button ]          │  │
  │  └──────────────────────┘  │
  └────────────────────────────┘
</button>
```

Use `focus-visible:` instead of `focus:` for buttons and links. It only shows the ring when the user is navigating with keyboard, not when clicking with mouse.

---

## Transitions

```html
<!-- Transition specific properties -->
<div class="transition-colors duration-150">Color changes smoothly</div>
<div class="transition-opacity duration-200">Opacity changes smoothly</div>
<div class="transition-transform duration-300">Transform changes smoothly</div>
<div class="transition-all duration-200">Everything changes smoothly</div>

<!-- Duration -->
<div class="duration-75">75ms (snappy)</div>
<div class="duration-150">150ms (default, good for colors)</div>
<div class="duration-200">200ms (good for most things)</div>
<div class="duration-300">300ms (good for transforms)</div>
<div class="duration-500">500ms (slow, for large movements)</div>

<!-- Easing -->
<div class="ease-in">Starts slow, ends fast</div>
<div class="ease-out">Starts fast, ends slow (most natural)</div>
<div class="ease-in-out">Slow start and end</div>
```

Sora's rule: "Colors and opacity: 150ms. Transforms and layout: 200-300ms. Never more than 500ms."

---

## Group Hover

Style a child when a parent is hovered:

```tsx
function TeamMemberCard({ name, role, avatar }) {
  return (
    <div className="group flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
      <img
        src={avatar}
        alt={name}
        className="w-10 h-10 rounded-full ring-2 ring-transparent group-hover:ring-brand-500 transition-all"
      />
      <div>
        <p className="text-sm font-medium text-gray-900 group-hover:text-brand-600 transition-colors">
          {name}
        </p>
        <p className="text-xs text-gray-500">{role}</p>
      </div>
      <span className="ml-auto text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
        →
      </span>
    </div>
  );
}
```

How it works:
1. Parent gets `group` class
2. Children use `group-hover:` prefix
3. When parent is hovered, all `group-hover:` styles activate

---

## Peer States

Style an element based on a sibling's state:

```tsx
function FloatingLabelInput({ label, id, ...props }) {
  return (
    <div className="relative">
      <input
        id={id}
        className="peer w-full px-4 py-3 border border-gray-300 rounded-lg text-base placeholder-transparent focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all"
        placeholder={label}
        {...props}
      />
      <label
        htmlFor={id}
        className="absolute left-3 -top-2.5 px-1 bg-white text-xs text-gray-500 transition-all peer-placeholder-shown:top-3.5 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-xs peer-focus:text-brand-600"
      >
        {label}
      </label>
    </div>
  );
}
```

How it works:
1. Input gets `peer` class
2. Label uses `peer-placeholder-shown:` and `peer-focus:` prefixes
3. Label moves based on input state

---

## Interactive Table Rows

```tsx
function DataTable({ rows }) {
  return (
    <table className="w-full">
      <thead>
        <tr className="border-b border-gray-200">
          <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase tracking-wide">
            Name
          </th>
          <th className="text-left py-3 px-4 text-xs font-medium text-gray-500 uppercase tracking-wide">
            Status
          </th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-100">
        {rows.map((row) => (
          <tr
            key={row.id}
            className="hover:bg-gray-50 transition-colors cursor-pointer"
          >
            <td className="py-3 px-4 text-sm text-gray-900">{row.name}</td>
            <td className="py-3 px-4">
              <StatusBadge status={row.status} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

## Combining States

States can be stacked:

```html
<!-- Dark mode + hover -->
<button class="bg-white hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700">

<!-- Responsive + state -->
<div class="p-4 lg:p-6 hover:shadow-md lg:hover:shadow-lg">

<!-- Group + focus-within -->
<div class="group focus-within:ring-2 focus-within:ring-brand-500">
  <input class="..." />
</div>

<!-- First/last child -->
<div class="first:rounded-t-lg last:rounded-b-lg">
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Classes
────────────────────────────────┼──────────────────────────────────────
Hover color change              │ hover:bg-X transition-colors
Keyboard focus ring             │ focus-visible:ring-2 focus-visible:ring-X
Disabled state                  │ disabled:opacity-50 disabled:pointer-events-none
Active (pressed)                │ active:bg-X
Smooth transition               │ transition-{property} duration-{ms}
Group hover (parent→child)      │ group + group-hover:X
Peer state (sibling→sibling)    │ peer + peer-focus:X
Focus within container          │ focus-within:ring-2
Striped table rows              │ odd:bg-gray-50 even:bg-white
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "Looks alive now. But we need dark mode. The whole dashboard. Toggle between light and dark. And it should respect the user's system preference by default."

Dark mode — Tailwind's `dark:` variant.

---

[← Chapter 5: Colors & Theming](chapter-05-colors-theming.md) | [Chapter 7: Dark Mode →](chapter-07-dark-mode.md)
