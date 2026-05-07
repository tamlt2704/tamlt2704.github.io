# Chapter 3: Responsive Navbar — Mobile-First Navigation

[← Chapter 2: Layout](chapter-02-layout.md) | [Chapter 4: Typography →](chapter-04-typography.md)

---

## The Task

Sora: "On desktop, the navbar shows all links. On mobile, it collapses into a hamburger menu. When you tap the hamburger, a panel slides in from the left. Standard stuff — but make it smooth."

---

## The Desktop Navbar

Start with what we need on large screens:

```tsx
function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 lg:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-8">
            <span className="text-xl font-bold text-gray-900">Pixelflow</span>

            {/* Desktop nav links — hidden on mobile */}
            <nav className="hidden md:flex items-center gap-1">
              <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-900 bg-gray-100">
                Dashboard
              </a>
              <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50">
                Analytics
              </a>
              <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50">
                Team
              </a>
              <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50">
                Settings
              </a>
            </nav>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            <button className="p-2 rounded-md text-gray-500 hover:text-gray-900 hover:bg-gray-100">
              🔔
            </button>
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-medium">
              S
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
```

Key patterns:
- `sticky top-0 z-50` → stays at top when scrolling, above other content
- `hidden md:flex` → nav links hidden on mobile, flex on tablet+
- `hover:text-gray-900 hover:bg-gray-50` → hover states (more in Chapter 6)

---

## Adding the Hamburger Button

The hamburger only shows on mobile:

```tsx
function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 lg:px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            {/* Hamburger — visible on mobile only */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden p-2 rounded-md text-gray-500 hover:text-gray-900 hover:bg-gray-100"
              aria-label="Toggle menu"
              aria-expanded={isOpen}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>

            <span className="text-xl font-bold text-gray-900">Pixelflow</span>

            {/* Desktop nav */}
            <nav className="hidden md:flex items-center gap-1">
              {/* ... links ... */}
            </nav>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {/* ... */}
          </div>
        </div>
      </div>

      {/* Mobile menu panel */}
      {isOpen && (
        <MobileMenu onClose={() => setIsOpen(false)} />
      )}
    </header>
  );
}
```

`md:hidden` → the hamburger disappears on tablet and above (where the full nav shows).

---

## The Mobile Menu

A slide-in panel with backdrop:

```tsx
function MobileMenu({ onClose }) {
  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 md:hidden"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Panel */}
      <div className="fixed inset-y-0 left-0 w-72 bg-white z-50 shadow-xl md:hidden">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <span className="text-lg font-bold text-gray-900">Pixelflow</span>
          <button
            onClick={onClose}
            className="p-2 rounded-md text-gray-500 hover:text-gray-900 hover:bg-gray-100"
            aria-label="Close menu"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav className="p-4 flex flex-col gap-1">
          <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-900 bg-gray-100">
            Dashboard
          </a>
          <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50">
            Analytics
          </a>
          <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50">
            Team
          </a>
          <a href="#" className="px-3 py-2 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-50">
            Settings
          </a>
        </nav>
      </div>
    </>
  );
}
```

Breaking down the positioning:
- `fixed inset-0` → covers entire viewport (backdrop)
- `fixed inset-y-0 left-0` → full height, pinned to left (panel)
- `bg-black/50` → black with 50% opacity (the `/50` is opacity shorthand)
- `w-72` → 288px wide panel
- `z-40` / `z-50` → backdrop behind panel, panel above backdrop

---

## Sizing & Positioning Utilities

```
────────────────────────────────────────────────
 Class              │ CSS
────────────────────────────────────────────────
 fixed              │ position: fixed
 absolute           │ position: absolute
 relative           │ position: relative
 sticky             │ position: sticky
 inset-0            │ top/right/bottom/left: 0
 inset-y-0          │ top: 0; bottom: 0
 inset-x-0          │ left: 0; right: 0
 top-0              │ top: 0
 left-0             │ left: 0
 z-10/20/30/40/50   │ z-index values
────────────────────────────────────────────────
```

---

## Opacity Shorthand

Tailwind lets you add opacity to any color with a slash:

```html
<div class="bg-black/50">     <!-- rgba(0,0,0,0.5) -->
<div class="bg-blue-500/75">  <!-- blue-500 at 75% opacity -->
<div class="text-white/90">   <!-- white text at 90% opacity -->
<div class="border-gray-900/10"> <!-- very subtle border -->
```

---

## Accessibility Matters

Dev: "Does the hamburger menu need all those aria attributes?"

You: "Yes. Screen readers need to know:
1. What the button does (`aria-label`)
2. Whether the menu is open (`aria-expanded`)
3. That the backdrop isn't content (`aria-hidden`)"

Sora: "Accessibility isn't optional. It's part of the design."

Minimum for interactive elements:
- Buttons need labels (text content or `aria-label`)
- Toggle buttons need `aria-expanded`
- Decorative elements need `aria-hidden="true"`
- Focus must be visible (Tailwind handles this with `focus:ring`)

---

## The Responsive Pattern

The full responsive navbar pattern:

```
Mobile (< 768px):
┌─────────────────────────────────┐
│ ☰  Pixelflow            🔔  👤 │
└─────────────────────────────────┘
  ↓ tap hamburger
┌────────────┐────────────────────┐
│ Pixelflow ✕│░░░░░░░░░░░░░░░░░░░│
│            │░░░ backdrop ░░░░░░░│
│ Dashboard  │░░░░░░░░░░░░░░░░░░░│
│ Analytics  │░░░░░░░░░░░░░░░░░░░│
│ Team       │░░░░░░░░░░░░░░░░░░░│
│ Settings   │░░░░░░░░░░░░░░░░░░░│
│            │░░░░░░░░░░░░░░░░░░░│
└────────────┘────────────────────┘

Desktop (≥ 768px):
┌──────────────────────────────────────────────────┐
│ Pixelflow   Dashboard  Analytics  Team    🔔  👤 │
└──────────────────────────────────────────────────┘
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Classes
────────────────────────────────┼──────────────────────────────────────
Sticky header                   │ sticky top-0 z-50
Show on mobile only             │ md:hidden
Show on desktop only            │ hidden md:flex (or md:block)
Full-screen overlay             │ fixed inset-0 bg-black/50
Side panel                      │ fixed inset-y-0 left-0 w-72
Opacity on colors               │ bg-{color}/{opacity}
Avatar circle                   │ w-8 h-8 rounded-full
Icon button                     │ p-2 rounded-md hover:bg-gray-100
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "Navigation works. Now I need the content pages styled. Blog posts, documentation, settings pages — lots of text. The typography needs to be clean and readable. And we need a consistent type scale."

Typography, prose styling, and content layout.

---

[← Chapter 2: Layout](chapter-02-layout.md) | [Chapter 4: Typography →](chapter-04-typography.md)
