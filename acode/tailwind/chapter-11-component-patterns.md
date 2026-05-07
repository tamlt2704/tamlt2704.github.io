# Chapter 11: Component Patterns — Extraction & @apply

[← Chapter 10: Dynamic Classes](chapter-10-dynamic-classes.md) | [Chapter 12: Design Tokens →](chapter-12-design-tokens.md)

---

## The Task

Dev: "I have the same card styles in 9 places. Should I make a CSS class with `@apply`? Or a React component? Or both? When do I extract?"

You: "Let me give you the rule."

---

## The Extraction Rule

```
────────────────────────────────────────────────────────────
 Situation                        │ Solution
────────────────────────────────────────────────────────────
 Same styles, same structure      │ Extract a component
 Same styles, different elements  │ @apply (rare) or cn() helper
 Same styles, used once           │ Don't extract. Leave it.
 Multi-file reuse                 │ Always a component
────────────────────────────────────────────────────────────
```

The priority order:
1. **Component** (React/Vue/Svelte) — first choice, always
2. **`cn()` utility** — for shared class strings without structure
3. **`@apply`** — last resort, for things you can't componentize

---

## When Components Win

If the styles AND the structure repeat together, make a component:

```tsx
// ✓ Component — styles + structure together
function MetricCard({ title, value, change, trend }) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg p-6 border border-gray-200 dark:border-gray-800">
      <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">{title}</p>
      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{value}</p>
      <p className={cn("text-sm font-medium mt-2", trend === "up" ? "text-green-600" : "text-red-600")}>
        {trend === "up" ? "↑" : "↓"} {change}
      </p>
    </div>
  );
}
```

You get:
- Single source of truth for styles AND markup
- Props for customization
- TypeScript types for safety
- Easy to find and update

---

## When @apply Makes Sense

`@apply` extracts utility classes into a CSS class. Use it when:
1. You can't use a component (third-party HTML, CMS content, email templates)
2. You need a base style for native elements in prose content

```css
/* Good use of @apply: styling CMS/markdown content */
.prose-custom h2 {
  @apply text-2xl font-bold text-gray-900 dark:text-white mt-8 mb-4;
}

.prose-custom a {
  @apply text-brand-600 hover:text-brand-700 underline underline-offset-2;
}

.prose-custom code {
  @apply bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm;
}
```

```css
/* Good use: base form styles you can't componentize */
.form-input {
  @apply w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-colors;
}
```

---

## When @apply is Wrong

```css
/* ❌ BAD — just make a Button component */
.btn-primary {
  @apply inline-flex items-center justify-center px-4 py-2 bg-brand-600 text-white font-medium rounded-lg hover:bg-brand-700 transition-colors;
}

/* ❌ BAD — just make a Card component */
.card {
  @apply bg-white dark:bg-gray-900 rounded-lg p-6 border border-gray-200 dark:border-gray-800;
}
```

Why it's bad:
- You lose the component's structure (what's inside the card?)
- You can't pass props
- You're back to inventing class names (the thing Tailwind avoids)
- You split styles from markup (the thing Tailwind avoids)

Dev: "But the Tailwind docs say to use @apply for repeated utilities..."

You: "The docs also say 'if you're using a framework with components, you almost never need @apply.' Components are the answer 95% of the time."

---

## Composable Component Patterns

### Compound Components

For complex UI with multiple parts:

```tsx
function Card({ className, children, ...props }) {
  return (
    <div className={cn("bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800", className)} {...props}>
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ className, children }) {
  return (
    <div className={cn("px-6 py-4 border-b border-gray-200 dark:border-gray-800", className)}>
      {children}
    </div>
  );
};

Card.Body = function CardBody({ className, children }) {
  return (
    <div className={cn("px-6 py-4", className)}>
      {children}
    </div>
  );
};

Card.Footer = function CardFooter({ className, children }) {
  return (
    <div className={cn("px-6 py-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 rounded-b-lg", className)}>
      {children}
    </div>
  );
};
```

Usage:

```tsx
<Card>
  <Card.Header>
    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Team Members</h2>
  </Card.Header>
  <Card.Body>
    <MemberList />
  </Card.Body>
  <Card.Footer>
    <Button variant="ghost" size="sm">View All</Button>
  </Card.Footer>
</Card>
```

### The className Prop Pattern

Always accept a `className` prop and merge it with `cn()`:

```tsx
function Avatar({ src, alt, size = "md", className }) {
  const sizes = {
    sm: "w-6 h-6",
    md: "w-8 h-8",
    lg: "w-10 h-10",
    xl: "w-12 h-12",
  };

  return (
    <img
      src={src}
      alt={alt}
      className={cn("rounded-full object-cover", sizes[size], className)}
    />
  );
}

// Consumer can override/extend:
<Avatar src="..." alt="..." className="ring-2 ring-white" />
```

---

## Slot Pattern for Flexible Layouts

```tsx
function PageLayout({ title, description, actions, children }) {
  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{title}</h1>
          {description && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{description}</p>
          )}
        </div>
        {actions && <div className="flex gap-3">{actions}</div>}
      </div>
      {children}
    </div>
  );
}

// Usage:
<PageLayout
  title="Team Members"
  description="Manage who has access to this project."
  actions={
    <>
      <Button variant="secondary">Export</Button>
      <Button>Invite Member</Button>
    </>
  }
>
  <MemberTable />
</PageLayout>
```

---

## Organizing Components

Sora's file structure:

```
src/
├── components/
│   ├── ui/              ← Primitive, reusable (Button, Card, Input, Badge)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── badge.tsx
│   ├── layout/          ← Layout shells (Navbar, Sidebar, PageLayout)
│   │   ├── navbar.tsx
│   │   ├── sidebar.tsx
│   │   └── page-layout.tsx
│   └── features/        ← Feature-specific (MetricCard, MemberList, Chart)
│       ├── metric-card.tsx
│       ├── member-list.tsx
│       └── activity-feed.tsx
├── lib/
│   └── utils.ts         ← cn() helper
└── styles/
    └── index.css        ← Tailwind imports, @theme, @apply (minimal)
```

Rules:
- `ui/` components are generic — no business logic, no data fetching
- `features/` components are specific — they know about your domain
- `layout/` components define page structure

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Question                        │ Answer
────────────────────────────────┼──────────────────────────────────────
Repeated styles + structure?    │ Make a component
Repeated styles, no structure?  │ cn() helper or shared constant
Can't use components?           │ @apply in CSS
One-off styling?                │ Write classes directly
Allow consumer overrides?       │ Accept className prop + cn()
Complex multi-part component?   │ Compound component pattern
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "The component system is clean. But I want to go deeper on the design tokens. Custom spacing scale, custom breakpoints, brand fonts. The full config."

Tailwind configuration, custom themes, and design tokens.

---

[← Chapter 10: Dynamic Classes](chapter-10-dynamic-classes.md) | [Chapter 12: Design Tokens →](chapter-12-design-tokens.md)
