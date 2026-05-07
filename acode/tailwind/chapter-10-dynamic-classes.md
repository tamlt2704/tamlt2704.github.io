# Chapter 10: Dynamic Classes — Managing Complexity

[← Chapter 9: Forms](chapter-09-forms.md) | [Chapter 11: Component Patterns →](chapter-11-component-patterns.md)

---

## The Task

Dev: "I have the same button styles in 14 files. The card styles in 9 files. If Sora changes the border radius from `rounded-lg` to `rounded-xl`, I have to find-and-replace everywhere. There has to be a better way."

You: "There is. Let me show you three approaches, from simple to powerful."

---

## Approach 1: Template Literals (Simple)

For basic conditional classes:

```tsx
function Badge({ variant, children }) {
  const colors = {
    success: "bg-green-50 text-green-700 border-green-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    error: "bg-red-50 text-red-700 border-red-200",
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors[variant]}`}>
      {children}
    </span>
  );
}
```

Works fine for 2-3 variants. Gets messy fast with more combinations.

---

## Approach 2: clsx / cn (Conditional Merging)

Install `clsx` for conditional class joining:

```bash
npm install clsx
```

```tsx
import clsx from 'clsx';

function NavItem({ active, children }) {
  return (
    <a
      className={clsx(
        "px-3 py-2 rounded-md text-sm font-medium transition-colors",
        active
          ? "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white"
          : "text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800"
      )}
    >
      {children}
    </a>
  );
}
```

`clsx` handles:
- Conditional classes: `clsx("base", condition && "extra")`
- Object syntax: `clsx({ "bg-red-500": hasError, "bg-green-500": isValid })`
- Arrays: `clsx(["base", variant === "primary" && "bg-blue-500"])`
- Falsy values are ignored: `clsx("base", undefined, null, false, "extra")` → `"base extra"`

---

## The `cn` Helper (clsx + tailwind-merge)

When you combine classes conditionally, conflicts can happen:

```tsx
// Problem: both p-4 and p-6 are in the final string
clsx("p-4", someCondition && "p-6")
// → "p-4 p-6" (which one wins? depends on CSS order — unreliable)
```

`tailwind-merge` resolves conflicts by keeping the last one:

```bash
npm install clsx tailwind-merge
```

Create a utility:

```tsx
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

Now:

```tsx
import { cn } from '@/lib/utils';

cn("p-4", "p-6")           // → "p-6" (last wins)
cn("text-red-500", "text-blue-500") // → "text-blue-500"
cn("rounded-lg", condition && "rounded-xl") // → resolves correctly
```

This is the standard pattern used by shadcn/ui and most Tailwind component libraries.

---

## Approach 3: CVA (Class Variance Authority)

For components with multiple variants and sizes, CVA provides structure:

```bash
npm install class-variance-authority
```

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  // Base classes (always applied)
  "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        primary: "bg-brand-600 text-white hover:bg-brand-700 focus-visible:ring-brand-500",
        secondary: "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 focus-visible:ring-gray-500",
        danger: "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
        ghost: "text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-500",
        link: "text-brand-600 hover:text-brand-700 underline-offset-4 hover:underline",
      },
      size: {
        sm: "px-3 py-1.5 text-xs gap-1.5",
        md: "px-4 py-2 text-sm gap-2",
        lg: "px-6 py-3 text-base gap-2",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

// TypeScript gets the variant types for free
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & {
    children: React.ReactNode;
  };

function Button({ variant, size, className, children, ...props }: ButtonProps) {
  return (
    <button className={cn(buttonVariants({ variant, size }), className)} {...props}>
      {children}
    </button>
  );
}
```

Usage:

```tsx
<Button>Default (primary, md)</Button>
<Button variant="secondary" size="lg">Large Secondary</Button>
<Button variant="danger" size="sm">Delete</Button>
<Button variant="ghost" size="icon">✕</Button>
<Button className="w-full">Full Width Override</Button>
```

The `className` prop + `cn()` lets consumers override styles when needed.

---

## CVA for the Card Component

```tsx
const cardVariants = cva(
  "rounded-lg border transition-all",
  {
    variants: {
      variant: {
        default: "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800",
        elevated: "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 shadow-md",
        interactive: "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer",
        outlined: "bg-transparent border-gray-300 dark:border-gray-700",
      },
      padding: {
        none: "",
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
      },
    },
    defaultVariants: {
      variant: "default",
      padding: "md",
    },
  }
);

function Card({ variant, padding, className, children, ...props }) {
  return (
    <div className={cn(cardVariants({ variant, padding }), className)} {...props}>
      {children}
    </div>
  );
}
```

---

## When to Use What

Dev: "So which approach do I use?"

```
────────────────────────────────────────────────────────────
 Situation                       │ Use
────────────────────────────────────────────────────────────
 Simple true/false toggle        │ Template literal or clsx
 2-3 conditional classes         │ clsx
 Need to override/merge classes  │ cn (clsx + tailwind-merge)
 Component with variants + sizes │ CVA
 One-off styling                 │ Just write the classes
────────────────────────────────────────────────────────────
```

Kai: "Can I just use CVA for everything?"

You: "You can, but it's overkill for a component with no variants. If it's just a card with one look, write the classes directly. CVA shines when you have a matrix of options."

---

## Important: Don't Construct Class Names Dynamically

```tsx
// ❌ BAD — Tailwind can't detect these classes
const color = "blue";
<div className={`bg-${color}-500 text-${color}-100`} />

// ✓ GOOD — Use complete class names
const colors = {
  blue: "bg-blue-500 text-blue-100",
  red: "bg-red-500 text-red-100",
  green: "bg-green-500 text-green-100",
};
<div className={colors[color]} />
```

Tailwind scans your source files for complete class names. If it never sees `bg-blue-500` as a complete string, it won't generate the CSS. Always use full, static class names.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Tool                            │ Install
────────────────────────────────┼──────────────────────────────────────
clsx                            │ npm install clsx
tailwind-merge                  │ npm install tailwind-merge
class-variance-authority        │ npm install class-variance-authority
────────────────────────────────┴──────────────────────────────────────

────────────────────────────────┬──────────────────────────────────────
Pattern                         │ Code
────────────────────────────────┼──────────────────────────────────────
Conditional class               │ clsx("base", active && "bg-blue-500")
Object syntax                   │ clsx({ "bg-red-500": hasError })
Merge conflicts                 │ cn("p-4", "p-6") → "p-6"
CVA variants                    │ cva("base", { variants: {...} })
Allow className override        │ cn(variants({ ... }), className)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Sora: "Now that we have a system for variants, let's talk about when to extract components vs when to use `@apply`. I keep seeing both approaches and I want a clear rule."

Component extraction patterns and the `@apply` debate.

---

[← Chapter 9: Forms](chapter-09-forms.md) | [Chapter 11: Component Patterns →](chapter-11-component-patterns.md)
