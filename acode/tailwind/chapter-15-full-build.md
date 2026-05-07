# Chapter 15: The Full Build — Pixelflow Dashboard

[← Chapter 14: Performance](chapter-14-performance.md)

---

## The Task

Sora: "Ship it. The complete dashboard. Everything we've built — responsive layout, dark mode, animations, the component system. One page. Production-ready."

---

## The Final Architecture

```
src/
├── components/
│   ├── ui/
│   │   ├── button.tsx          (Ch 6, 10)
│   │   ├── card.tsx            (Ch 1, 11)
│   │   ├── input.tsx           (Ch 9)
│   │   ├── badge.tsx           (Ch 5, 10)
│   │   ├── avatar.tsx          (Ch 11)
│   │   ├── spinner.tsx         (Ch 8)
│   │   └── toggle.tsx          (Ch 9)
│   ├── layout/
│   │   ├── dashboard-layout.tsx (Ch 2, 3, 7)
│   │   ├── navbar.tsx          (Ch 3)
│   │   ├── sidebar.tsx         (Ch 2)
│   │   └── page-header.tsx     (Ch 4)
│   └── features/
│       ├── metric-card.tsx     (Ch 1)
│       ├── activity-feed.tsx   (Ch 6)
│       ├── team-list.tsx       (Ch 6)
│       └── chart-placeholder.tsx
├── lib/
│   └── utils.ts                (Ch 10)
├── hooks/
│   └── use-theme.ts            (Ch 7)
├── styles/
│   └── index.css               (Ch 5, 12, 13)
└── pages/
    └── dashboard.tsx           (this chapter)
```

---

## The Design System CSS

```css
/* src/styles/index.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";

@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;

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

  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;

  --animate-fade-in: fade-in 0.3s ease-out;
  --animate-slide-up: slide-up 0.3s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@utility scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}
```

---

## The Complete Dashboard Page

```tsx
// src/pages/dashboard.tsx
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { PageHeader } from '@/components/layout/page-header';
import { MetricCard } from '@/components/features/metric-card';
import { ActivityFeed } from '@/components/features/activity-feed';
import { TeamList } from '@/components/features/team-list';

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6 animate-fade-in">
        <PageHeader
          title="Dashboard"
          description="Welcome back. Here's what's happening with your projects."
        />

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <MetricCard
            title="Total Revenue"
            value="$45,231"
            change="+20.1%"
            trend="up"
            description="from last month"
          />
          <MetricCard
            title="Active Users"
            value="2,350"
            change="+12.5%"
            trend="up"
            description="from last month"
          />
          <MetricCard
            title="Churn Rate"
            value="1.2%"
            change="-0.4%"
            trend="up"
            description="from last month"
          />
        </div>

        {/* Chart Section */}
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Revenue Over Time
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                Monthly recurring revenue for the past 12 months
              </p>
            </div>
            <div className="flex gap-2">
              <button className="px-3 py-1.5 text-xs font-medium rounded-md bg-brand-50 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
                12M
              </button>
              <button className="px-3 py-1.5 text-xs font-medium rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                6M
              </button>
              <button className="px-3 py-1.5 text-xs font-medium rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                30D
              </button>
            </div>
          </div>
          <div className="h-64 flex items-end gap-2 px-2">
            {/* Simplified bar chart */}
            {[40, 55, 45, 60, 75, 65, 80, 70, 85, 90, 78, 95].map((height, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div
                  className="w-full bg-brand-500/80 dark:bg-brand-400/80 rounded-t-sm hover:bg-brand-600 dark:hover:bg-brand-300 transition-colors cursor-pointer"
                  style={{ height: `${height}%` }}
                />
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  {['J','F','M','A','M','J','J','A','S','O','N','D'][i]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Activity Feed — takes 3 columns */}
          <div className="lg:col-span-3 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recent Activity
            </h2>
            <ActivityFeed />
          </div>

          {/* Team — takes 2 columns */}
          <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Team Members
            </h2>
            <TeamList />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
```

---

## The Layout Component

```tsx
// src/components/layout/dashboard-layout.tsx
import { useState } from 'react';
import { Navbar } from './navbar';
import { Sidebar } from './sidebar';

export function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
      <Navbar onMenuClick={() => setSidebarOpen(true)} />

      <div className="flex">
        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <>
            <div
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
            <div className="fixed inset-y-0 left-0 w-72 bg-white dark:bg-gray-900 z-50 lg:hidden shadow-xl animate-slide-in">
              <Sidebar onClose={() => setSidebarOpen(false)} />
            </div>
          </>
        )}

        {/* Desktop sidebar */}
        <aside className="hidden lg:block w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 min-h-[calc(100vh-4rem)] sticky top-16">
          <Sidebar />
        </aside>

        {/* Main content */}
        <main className="flex-1 p-4 lg:p-6 max-w-7xl">
          {children}
        </main>
      </div>
    </div>
  );
}
```

---

## The Metric Card (Final Version)

```tsx
// src/components/features/metric-card.tsx
import { cn } from '@/lib/utils';

export function MetricCard({ title, value, change, trend, description, className }) {
  return (
    <div className={cn(
      "bg-white dark:bg-gray-900 rounded-lg p-6 border border-gray-200 dark:border-gray-800",
      "hover:shadow-md hover:-translate-y-0.5 transition-all duration-200",
      className
    )}>
      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
        {title}
      </p>
      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2 tracking-tight">
        {value}
      </p>
      <div className="mt-2 flex items-center gap-1.5">
        <span className={cn(
          "inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium",
          trend === "up"
            ? "bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-400"
            : "bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-400"
        )}>
          {trend === "up" ? "↑" : "↓"} {change}
        </span>
        {description && (
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {description}
          </span>
        )}
      </div>
    </div>
  );
}
```

---

## The Activity Feed

```tsx
// src/components/features/activity-feed.tsx
const activities = [
  { user: "Sora", action: "updated the design system", time: "2m ago", avatar: "S" },
  { user: "Dev", action: "pushed 3 commits to main", time: "15m ago", avatar: "D" },
  { user: "Kai", action: "deployed to production", time: "1h ago", avatar: "K" },
  { user: "You", action: "merged PR #142", time: "2h ago", avatar: "Y" },
  { user: "Sora", action: "created new Figma frames", time: "3h ago", avatar: "S" },
];

export function ActivityFeed() {
  return (
    <div className="space-y-4">
      {activities.map((activity, i) => (
        <div
          key={i}
          className="group flex items-start gap-3 p-2 -mx-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900 flex items-center justify-center text-brand-700 dark:text-brand-300 text-xs font-medium flex-shrink-0">
            {activity.avatar}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-gray-900 dark:text-white">
              <span className="font-medium">{activity.user}</span>
              {" "}{activity.action}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              {activity.time}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## The Team List

```tsx
// src/components/features/team-list.tsx
const members = [
  { name: "Sora", role: "Design Lead", status: "online" },
  { name: "Dev", role: "Junior Engineer", status: "online" },
  { name: "Kai", role: "Backend Engineer", status: "away" },
  { name: "You", role: "Frontend Engineer", status: "online" },
];

export function TeamList() {
  return (
    <div className="space-y-3">
      {members.map((member) => (
        <div
          key={member.name}
          className="group flex items-center gap-3 p-2 -mx-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors cursor-pointer"
        >
          <div className="relative">
            <div className="w-9 h-9 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-sm font-medium text-gray-600 dark:text-gray-300">
              {member.name[0]}
            </div>
            <span className={cn(
              "absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-gray-900",
              member.status === "online" ? "bg-green-500" : "bg-amber-400"
            )} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {member.name}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {member.role}
            </p>
          </div>
          <span className="text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity text-sm">
            →
          </span>
        </div>
      ))}
    </div>
  );
}
```

---

## Everything You Learned

```
────────────────────────────────────────────────────────────
 Chapter │ Concept                    │ Used In Dashboard
────────────────────────────────────────────────────────────
 01      │ Utility classes            │ Every element
 02      │ Flexbox, Grid, responsive  │ Layout, card grid
 03      │ Responsive navbar          │ Header, mobile menu
 04      │ Typography                 │ Headings, body text
 05      │ Colors, gradients          │ Brand colors, badges
 06      │ States, transitions        │ Hover effects, focus
 07      │ Dark mode                  │ Full dark theme
 08      │ Animations                 │ Fade-in, hover lift
 09      │ Forms                      │ (Settings page)
 10      │ Dynamic classes            │ cn(), conditional styles
 11      │ Component patterns         │ Card, Button, Layout
 12      │ Design tokens              │ @theme configuration
 13      │ Plugins                    │ scrollbar-hide
 14      │ Performance                │ Optimized bundle
────────────────────────────────────────────────────────────
```

---

## Sora's Final Review

Sora opens the dashboard on her phone. Rotates to landscape. Switches to dark mode. Resizes the browser from 320px to 2560px.

> "It's responsive. It's fast. It's accessible. The dark mode is clean. The animations are subtle. The code is maintainable."

She pauses.

> "Ship it."

---

## Where to Go From Here

- **[Tailwind CSS Docs](https://tailwindcss.com/docs)** — the official reference
- **[Tailwind UI](https://tailwindui.com)** — premium component library by the Tailwind team
- **[shadcn/ui](https://ui.shadcn.com)** — open-source components built with Tailwind + Radix
- **[Headless UI](https://headlessui.com)** — unstyled, accessible components (pair with Tailwind)
- **[Heroicons](https://heroicons.com)** — SVG icons by the Tailwind team

---

## The Rules

What you'll tell the next developer who joins:

1. **Mobile-first.** Write base styles for mobile, add breakpoints going up.
2. **Utility-first.** Write classes in markup. Extract components, not CSS classes.
3. **Complete strings.** Never construct class names dynamically.
4. **Semantic tokens.** Use CSS variables for colors that change with theme.
5. **`cn()` everything.** Always accept and merge a `className` prop.
6. **Respect motion.** Add `motion-reduce:` alternatives.
7. **Contrast matters.** 4.5:1 minimum for text. No exceptions.
8. **Ship small.** Tailwind only generates what you use. Trust it.

---

[← Chapter 14: Performance](chapter-14-performance.md)
