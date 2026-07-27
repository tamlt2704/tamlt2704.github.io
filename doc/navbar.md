# Building a Navbar — Step by Step

We'll build the navbar piece by piece. Each step adds one concept.

---

## Step 1: Just Links

Start simple — a list of links on the page.

`components/navbar.tsx`:

```tsx
import Link from "next/link"

export function Navbar() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/algorithms">Algorithms</Link>
      <Link href="/blog">Blog</Link>
      <Link href="/about">About</Link>
    </nav>
  )
}
```

Add it to `app/layout.tsx`:

```tsx
import { Navbar } from "@/components/navbar"

// inside the <body>:
;<body>
  <Navbar />
  <main>{children}</main>
</body>
```

**Result:** Four links stacked vertically (block elements by default).

---

## Step 2: Make Links Horizontal

Add `flex` to put them in a row, and `gap` for spacing.

```tsx
<nav className="flex gap-6">
  <Link href="/">Home</Link>
  <Link href="/algorithms">Algorithms</Link>
  <Link href="/blog">Blog</Link>
  <Link href="/about">About</Link>
</nav>
```

**What changed:** `flex` = horizontal row. `gap-6` = space between items.

---

## Step 3: Add a Brand Name

Separate the brand from the links using `items-center`.

```tsx
<nav className="flex items-center gap-6">
  <span className="text-lg font-bold">AlgoViz</span>
  <Link href="/">Home</Link>
  <Link href="/algorithms">Algorithms</Link>
  <Link href="/blog">Blog</Link>
  <Link href="/about">About</Link>
</nav>
```

**What changed:** Brand sits on the left, links follow. `items-center` vertically aligns them.

---

## Step 4: Add Padding

The nav is stuck to the edges. Give it breathing room.

```tsx
<nav className="flex items-center gap-6 px-6 py-4">
```

**What changed:**

- `px-6` = horizontal padding (left and right)
- `py-4` = vertical padding (top and bottom)

---

## Step 5: Add a Bottom Border

Visually separate the navbar from page content.

```tsx
<nav className="flex items-center gap-6 px-6 py-4 border-b">
```

**What changed:** `border-b` = thin grey line at the bottom.

---

## Step 6: Make It Sticky

Keep the navbar visible when scrolling down.

```tsx
<nav className="sticky top-0 flex items-center gap-6 px-6 py-4 border-b bg-white">
```

**What changed:**

- `sticky top-0` = sticks to the top of the viewport on scroll
- `bg-white` = needed so content doesn't show through behind it

---

## Step 7: Push Brand and Links Apart

Put the brand on the left and links on the right (or with space between).

```tsx
<nav className="sticky top-0 flex items-center border-b bg-white px-6 py-4">
  <span className="text-lg font-bold">AlgoViz</span>
  <div className="ml-auto flex gap-6">
    <Link href="/">Home</Link>
    <Link href="/algorithms">Algorithms</Link>
    <Link href="/blog">Blog</Link>
    <Link href="/about">About</Link>
  </div>
</nav>
```

**What changed:** `ml-auto` on the links container pushes it to the right.

---

## Step 8: Style the Links

Make them look like nav items, not blue underlined links.

```tsx
<Link href="/" className="text-sm text-gray-600 transition-colors hover:text-black">
  Home
</Link>
```

Apply to all links:

```tsx
<div className="ml-auto flex gap-6">
  <Link href="/" className="text-sm text-gray-600 transition-colors hover:text-black">
    Home
  </Link>
  <Link href="/algorithms" className="text-sm text-gray-600 transition-colors hover:text-black">
    Algorithms
  </Link>
  <Link href="/blog" className="text-sm text-gray-600 transition-colors hover:text-black">
    Blog
  </Link>
  <Link href="/about" className="text-sm text-gray-600 transition-colors hover:text-black">
    About
  </Link>
</div>
```

**What changed:**

- `text-sm` = smaller font
- `text-gray-600` = muted color
- `hover:text-black` = darker on hover
- `transition-colors` = smooth color change

---

## Step 9: Extract the Links Array

Avoid repeating yourself — define links once.

```tsx
import Link from "next/link"

const links = [
  { href: "/", label: "Home" },
  { href: "/algorithms", label: "Algorithms" },
  { href: "/blog", label: "Blog" },
  { href: "/about", label: "About" },
]

export function Navbar() {
  return (
    <nav className="sticky top-0 flex items-center border-b bg-white px-6 py-4">
      <span className="text-lg font-bold">AlgoViz</span>
      <div className="ml-auto flex gap-6">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="text-sm text-gray-600 transition-colors hover:text-black"
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
```

**What changed:** Links come from an array. Adding a new page = adding one object.

---

## Step 10: Hide Links on Mobile

On small screens, hide the desktop links. We'll add a mobile menu next.

```tsx
<div className="ml-auto hidden gap-6 md:flex">
  {links.map((link) => (
    <Link
      key={link.href}
      href={link.href}
      className="text-sm text-gray-600 transition-colors hover:text-black"
    >
      {link.label}
    </Link>
  ))}
</div>
```

**What changed:** `hidden md:flex` = hidden by default, shown as flex at `md` (768px+).

---

## Step 11: Add a Mobile Menu Button

Show a hamburger icon on small screens. shadcn/ui installs `lucide-react` — a library of clean SVG icons.

```tsx
import { Menu } from "lucide-react"

export function Navbar() {
  return (
    <nav className="sticky top-0 flex items-center border-b bg-white px-6 py-4">
      <span className="text-lg font-bold">AlgoViz</span>

      {/* Desktop links */}
      <div className="ml-auto hidden gap-6 md:flex">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="text-sm text-gray-600 transition-colors hover:text-black"
          >
            {link.label}
          </Link>
        ))}
      </div>

      {/* Mobile menu button */}
      <button className="ml-auto md:hidden" aria-label="Open menu">
        <Menu className="h-5 w-5" />
      </button>
    </nav>
  )
}
```

**What changed:**

- `md:hidden` = hamburger only shows on mobile
- `ml-auto` pushes it to the right on mobile
- `<Menu />` from `lucide-react` — comes with shadcn, no extra install needed

---

## Step 12: Mobile Menu (toggle open/close)

Add `"use client"` and state to toggle a dropdown.

```tsx
"use client"

import { useState } from "react"
import Link from "next/link"
import { Menu, X } from "lucide-react"

const links = [
  { href: "/", label: "Home" },
  { href: "/algorithms", label: "Algorithms" },
  { href: "/blog", label: "Blog" },
  { href: "/about", label: "About" },
]

export function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <nav className="sticky top-0 border-b bg-white">
      <div className="flex items-center px-6 py-4">
        <span className="text-lg font-bold">AlgoViz</span>

        {/* Desktop links */}
        <div className="ml-auto hidden gap-6 md:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-gray-600 transition-colors hover:text-black"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Mobile menu button */}
        <button
          className="ml-auto md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile dropdown — full width below navbar */}
      {open && (
        <div className="flex flex-col gap-3 border-t px-6 py-4 md:hidden">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-gray-600 hover:text-black"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}
```

**What changed:**

- `"use client"` — needed for `useState`
- `useState(false)` — tracks open/close
- `<Menu />` and `<X />` from `lucide-react` — toggles between hamburger and close icon
- When open, links appear stacked below the navbar (full width)
- Clicking a link closes the menu

---

## Step 13: Dropdown Below the Burger Icon

Instead of a full-width panel, make the menu float directly below the burger.

```tsx
"use client"

import { useState } from "react"
import Link from "next/link"
import { Menu, X } from "lucide-react"

const links = [
  { href: "/", label: "Home" },
  { href: "/algorithms", label: "Algorithms" },
  { href: "/blog", label: "Blog" },
  { href: "/about", label: "About" },
]

export function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <nav className="sticky top-0 border-b bg-white">
      <div className="flex items-center px-6 py-4">
        <span className="text-lg font-bold">AlgoViz</span>

        {/* Desktop links */}
        <div className="ml-auto hidden gap-6 md:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-gray-600 transition-colors hover:text-black"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Mobile menu button + dropdown wrapper */}
        <div className="relative ml-auto md:hidden">
          <button onClick={() => setOpen(!open)} aria-label="Toggle menu">
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>

          {/* Dropdown — positioned below the burger */}
          {open && (
            <div className="absolute top-full right-0 mt-2 w-48 rounded-md border bg-white py-2 shadow-lg">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="block px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 hover:text-black"
                  onClick={() => setOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
```

**What changed from Step 12:**

- Wrapped button + dropdown in a `relative` container
- Dropdown uses `absolute right-0 top-full` — floats below the burger, aligned right
- `mt-2` = small gap between burger and menu
- `w-48` = fixed width dropdown
- `rounded-md border shadow-lg` = card-like appearance
- `hover:bg-gray-100` = row highlight on hover

**Key positioning classes:**

| Class      | What it does                                                 |
| ---------- | ------------------------------------------------------------ |
| `relative` | Makes the wrapper the anchor point for the dropdown          |
| `absolute` | Dropdown is positioned relative to the wrapper, not the page |
| `right-0`  | Aligns dropdown's right edge with the burger's right edge    |
| `top-full` | Places it directly below the wrapper                         |
| `mt-2`     | Small gap so it doesn't touch the burger                     |

### Understanding `position` in CSS

Every element has a `position` value. It controls how an element is placed on the page and what it uses as its reference point.

**The 4 values you'll use:**

| Tailwind Class | CSS Value            | What it does                                                                                                                        |
| -------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `static`       | `position: static`   | Default. Element flows normally in the page. Top/left/right/bottom do nothing.                                                      |
| `relative`     | `position: relative` | Element stays in its normal spot, BUT becomes an anchor for any `absolute` children inside it. You can also nudge it with top/left. |
| `absolute`     | `position: absolute` | Element is pulled OUT of the normal flow. It positions itself relative to the nearest `relative` (or `absolute`/`fixed`) parent.    |
| `fixed`        | `position: fixed`    | Like absolute, but relative to the browser window. Stays in place when you scroll.                                                  |

**Why `relative` + `absolute` work together:**

```
┌─────────────────────────────── nav bar ───────────────────────────────┐
│  AlgoViz                                    [relative wrapper]         │
│                                              ┌── button (☰) ──┐       │
│                                              └────────────────┘       │
│                                              ┌── absolute dropdown ─┐ │
│                                              │  Home                │ │
│                                              │  Algorithms          │ │
│                                              │  Blog                │ │
│                                              │  About               │ │
│                                              └──────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

- The `relative` wrapper doesn't move — it sits in its normal position
- The `absolute` dropdown uses that wrapper as its reference point
- `top-full` = place my top edge at the bottom of the wrapper
- `right-0` = align my right edge with the wrapper's right edge

**What happens WITHOUT `relative` on the parent?**

The `absolute` dropdown would look for the next ancestor with a position set. If none exists, it uses the whole page (`<html>`) as the reference — your dropdown flies to the top-right corner of the entire page instead of sitting below the burger.

**Quick experiment to prove it:**

1. Remove `relative` from the wrapper div → dropdown jumps to the page corner
2. Add it back → dropdown snaps back below the burger

**`relative` doesn't visually change anything on its own.** The wrapper looks exactly the same with or without `relative`. Its only job here is to say: "I am the anchor for any `absolute` elements inside me."

### When to use which

| I want to...                                         | Use                                                  |
| ---------------------------------------------------- | ---------------------------------------------------- |
| Pin something to the top of the page (navbar)        | `sticky top-0` or `fixed top-0`                      |
| Float a dropdown below a button                      | `relative` on wrapper + `absolute` on dropdown       |
| Overlay something on top of content (modal backdrop) | `fixed inset-0`                                      |
| Badge/notification dot on an icon                    | `relative` on icon + `absolute top-0 right-0` on dot |
| Tooltip near an element                              | `relative` on trigger + `absolute` on tooltip        |

---

## Summary of Tailwind Classes Used

| Class               | What it does                       |
| ------------------- | ---------------------------------- |
| `flex`              | Horizontal row layout              |
| `gap-6`             | Space between flex items           |
| `items-center`      | Vertically center items            |
| `px-6` / `py-4`     | Padding (horizontal / vertical)    |
| `border-b`          | Bottom border line                 |
| `sticky top-0`      | Stick to top on scroll             |
| `bg-white`          | White background (so sticky works) |
| `ml-auto`           | Push element to the right          |
| `text-sm`           | Smaller text                       |
| `text-gray-600`     | Muted grey color                   |
| `hover:text-black`  | Darker on hover                    |
| `transition-colors` | Smooth color animation             |
| `hidden md:flex`    | Hide on mobile, show on desktop    |
| `md:hidden`         | Show on mobile, hide on desktop    |
| `flex-col`          | Stack items vertically             |

---

## What's Next?

Once you're comfortable with this, you can:

- Add shadcn `Sheet` component for a slide-in mobile menu (instead of the dropdown)
- Add `usePathname()` to highlight the active page
- Add dark mode support
- Browse more icons at https://lucide.dev/icons
