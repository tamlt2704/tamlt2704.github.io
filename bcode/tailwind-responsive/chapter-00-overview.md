# Chapter 0: Before You Start

[Chapter 1: Mobile First →](chapter-01-mobile-first.md)

---

## The Story

You're a frontend engineer at **LaunchPad**, a SaaS startup building a project management dashboard. The app looks great on your 27" monitor. Then the CEO, **Diana**, checks it on her iPhone during a flight:

"I can't read anything. The sidebar covers the whole screen. The table scrolls sideways forever. The buttons are microscopic. Fix this before the investor demo on Friday."

You open Chrome DevTools, toggle the device toolbar, and select "iPhone 14." The dashboard is a disaster. Cards overlap. Text overflows. The navigation is unusable.

The problem: the entire UI was built for desktop. Every width is hardcoded. Every layout assumes 1440px. Responsive design was "we'll do it later." Later is now.

Over 14 chapters, you'll make LaunchPad's dashboard work beautifully from 320px phones to 3840px ultrawide monitors — using Tailwind CSS utilities and a mobile-first approach.

## What Is Mobile-First?

Mobile-first means: **design for the smallest screen first, then add complexity for larger screens.**

In Tailwind, unprefixed utilities apply to all screen sizes. Breakpoint prefixes (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`) apply at that width *and above*:

```html
<!-- This means: -->
<!-- All screens: 1 column -->
<!-- sm (640px+): 2 columns -->
<!-- lg (1024px+): 3 columns -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
```

You're not "hiding things on mobile." You're building the mobile layout first, then enhancing for larger screens.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Frontend Engineer | "It works on my monitor" (not anymore) |
| **Diana** | CEO | Tests everything on her phone. Always. |
| **Jake** | Designer | Hands you Figma files with only desktop mockups |
| **QA Team** | Testers | Own 47 different devices. Find every breakage. |

## Prerequisites

### Node.js 18+

```bash
node --version
# v18.x.x or higher
```

### Tailwind CSS 3.4+

```bash
npm install -D tailwindcss
npx tailwindcss init
```

Or use the Tailwind CDN for quick experiments:

```html
<script src="https://cdn.tailwindcss.com"></script>
```

### Browser DevTools

Chrome/Firefox DevTools with the responsive design mode is your primary testing tool:
- Chrome: `Ctrl+Shift+M` (toggle device toolbar)
- Firefox: `Ctrl+Shift+M` (responsive design mode)

### Tailwind Breakpoints

| Prefix | Min-width | Typical device |
|---|---|---|
| (none) | 0px | All screens (mobile base) |
| `sm:` | 640px | Large phones, landscape |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Laptops |
| `xl:` | 1280px | Desktops |
| `2xl:` | 1536px | Large desktops |

These are *minimum* widths. `md:flex` means "apply flex at 768px and above." Below 768px, it doesn't apply.

## The Responsive Checklist

Every component you build should pass this checklist:

- [ ] Readable at 320px (smallest phone)
- [ ] Usable at 375px (iPhone SE)
- [ ] Good at 768px (iPad portrait)
- [ ] Great at 1024px (laptop)
- [ ] Excellent at 1440px (desktop)
- [ ] Not broken at 3840px (ultrawide)

We'll use this checklist in every chapter.

## The Roadmap

| Ch | The Broken Thing | The Fix |
|---|---|---|
| 1 | Desktop layout on phone | Mobile-first workflow |
| 2 | Sidebar overlaps content | Flexbox responsive patterns |
| 3 | Cards stack wrong | CSS Grid with Tailwind |
| 4 | Text too small/large | Responsive typography |
| 5 | Padding crushes content | Responsive spacing |
| 6 | Nav overflows | Responsive navigation |
| 7 | Hero image breaks | Responsive images |
| 8 | Card grid looks wrong | Responsive card patterns |
| 9 | Table scrolls forever | Responsive tables |
| 10 | Form fields overflow | Responsive forms |
| 11 | Users want dark mode | Dark mode variant |
| 12 | Component in sidebar vs main | Container queries |
| 13 | CSS bundle is 500KB | Performance optimization |
| 14 | Inconsistent spacing/colors | Design system extraction |

Let's fix the first screen.

---

[Chapter 1: Mobile First →](chapter-01-mobile-first.md)
