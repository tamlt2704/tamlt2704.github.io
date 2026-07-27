# Adding shadcn/ui to This Project

## Prerequisites

This project already has:

- Next.js 16 (App Router)
- Tailwind CSS v4
- TypeScript

## Step 1: Run the shadcn init command

```bash
npx shadcn@latest init
```

You'll be prompted with questions:

| Prompt                                               | Recommended Answer                     |
| ---------------------------------------------------- | -------------------------------------- |
| Which style would you like to use?                   | `new-york` (cleaner look) or `default` |
| Which color would you like to use as the base color? | `neutral` (or pick your preference)    |
| Would you like to use CSS variables for theming?     | `yes`                                  |

This will:

- Create a `components.json` config file
- Create `lib/utils.ts` with the `cn()` helper (merges Tailwind classes)
- Update your `globals.css` with CSS variables for theming
- Install `tailwind-merge` and `clsx` as dependencies

## Step 2: Add Components

Add components one at a time as you need them:

```bash
# Examples
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
```

Components are installed to `components/ui/` by default (configurable in `components.json`).

## Step 3: Use a Component

```tsx
import { Button } from "@/components/ui/button"

export default function MyPage() {
  return (
    <div>
      <Button variant="outline">Click me</Button>
    </div>
  )
}
```

## Useful Commands

```bash
# List all available components
npx shadcn@latest add

# Add multiple components at once
npx shadcn@latest add button card input label

# Check what's installed
cat components.json
```

## Project Structure After Setup

```
javizhome/
├── app/
│   ├── globals.css        ← updated with CSS variables
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   └── ui/                ← shadcn components live here
│       ├── button.tsx
│       ├── card.tsx
│       └── ...
├── lib/
│   └── utils.ts           ← cn() helper
├── components.json        ← shadcn config
└── ...
```

## Key Concepts

### Why shadcn/ui?

- **Not a dependency** — components are copied into your project, not installed as a package
- **Full control** — you own the code and can modify it freely
- **Built on Radix UI** — accessible, unstyled primitives under the hood
- **Tailwind-native** — styled with Tailwind classes, easy to customize

### The `cn()` Helper

Located in `lib/utils.ts`, this merges Tailwind classes without conflicts:

```ts
import { cn } from "@/lib/utils"

<div className={cn("px-4 py-2", isActive && "bg-blue-500")} />
```

### Customizing Components

Since components are in your codebase, just edit them directly:

```tsx
// components/ui/button.tsx — change default styles, add variants, etc.
```

### Theming

CSS variables in `globals.css` control the theme. Change them to restyle everything at once:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 0 0% 3.9%;
  --primary: 0 0% 9%;
  /* ... */
}
```

## Common Patterns

### Form with validation (pair with react-hook-form + zod)

```bash
npx shadcn@latest add form input label
npm install react-hook-form @hookform/resolvers zod
```

### Dialog/Modal

```bash
npx shadcn@latest add dialog button
```

### Data table

```bash
npx shadcn@latest add table
npm install @tanstack/react-table
```

## Troubleshooting

### Path alias not working

Ensure `tsconfig.json` has the `@/*` path alias:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### Tailwind v4 compatibility

shadcn/ui supports Tailwind v4. If you hit issues during init, make sure you're using the latest `shadcn` CLI:

```bash
npx shadcn@latest init
```

### Import errors after adding a component

Run `npm install` — some components pull in additional dependencies (like `@radix-ui/react-dialog`).
