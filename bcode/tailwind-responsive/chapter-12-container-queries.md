# Chapter 12: Container Queries

[← Chapter 11: Dark Mode](chapter-11-dark-mode.md) | [Chapter 13: Performance →](chapter-13-performance.md)

---

## The Breakage

LaunchPad has a reusable `<StatCard>` component. It looks great in the main content area (800px wide). But when you drop the same component into the 300px sidebar:

```html
<!-- Main area: looks fine -->
<div class="w-full lg:w-2/3">
  <div class="flex items-center gap-4 p-6 bg-white rounded-lg">
    <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">📊</div>
    <div>
      <p class="text-sm text-gray-500">Revenue</p>
      <p class="text-2xl font-bold">$48,200</p>
    </div>
    <p class="ml-auto text-sm text-green-600">↑ 12%</p>
  </div>
</div>

<!-- Sidebar: same component, now cramped and broken -->
<aside class="w-full lg:w-1/3">
  <div class="flex items-center gap-4 p-6 bg-white rounded-lg">
    <!-- Icon, text, and badge all fight for 300px of space -->
    <!-- Text truncates, badge wraps below -->
  </div>
</aside>
```

The problem: **media queries respond to the viewport width, not the component's container width.** The viewport is 1440px (desktop), so `lg:` styles apply — but the sidebar is only 300px wide. The component doesn't know it's in a narrow space.

## Container Queries: Respond to Parent Width

Container queries let a component adapt based on its container's size, not the viewport:

```html
<!-- Mark the parent as a container -->
<div class="@container">
  <!-- Child responds to container width, not viewport -->
  <div class="flex flex-col @sm:flex-row items-start @sm:items-center gap-3 @sm:gap-4 p-4 @sm:p-6 bg-white rounded-lg">
    <div class="w-10 h-10 @sm:w-12 @sm:h-12 bg-blue-100 rounded-lg flex items-center justify-center shrink-0">
      📊
    </div>
    <div>
      <p class="text-xs @sm:text-sm text-gray-500">Revenue</p>
      <p class="text-xl @sm:text-2xl font-bold">$48,200</p>
    </div>
    <p class="@sm:ml-auto text-xs @sm:text-sm text-green-600 font-medium">↑ 12%</p>
  </div>
</div>
```

- `@container` — marks an element as a query container
- `@sm:` — applies when the container is ≥320px wide
- `@md:` — applies when the container is ≥448px wide
- `@lg:` — applies when the container is ≥512px wide

## Container Query Breakpoints

| Prefix | Min container width |
|---|---|
| `@xs` | 256px (16rem) |
| `@sm` | 320px (20rem) |
| `@md` | 448px (28rem) |
| `@lg` | 512px (32rem) |
| `@xl` | 576px (36rem) |
| `@2xl` | 672px (42rem) |

## Named Containers

When you have nested containers, name them to target specific ancestors:

```html
<!-- Named container -->
<div class="@container/main">
  <div class="@container/sidebar">
    <!-- Responds to the sidebar container -->
    <div class="@sm/sidebar:flex-row flex-col flex gap-4">
      <!-- ... -->
    </div>
  </div>
</div>
```

## Real Example: Dashboard Widget

The same widget component works in any context:

```html
<!-- In main content (wide) -->
<div class="lg:col-span-2">
  <div class="@container">
    <div class="bg-white rounded-lg border p-4 @md:p-6">
      <div class="flex flex-col @md:flex-row @md:items-center @md:justify-between gap-4">
        <div>
          <h3 class="font-semibold text-gray-900">Active Users</h3>
          <p class="text-3xl @lg:text-4xl font-bold mt-1">2,420</p>
        </div>
        <div class="flex gap-2 @md:gap-4">
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500">Today</p>
            <p class="text-lg font-bold">342</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center">
            <p class="text-xs text-gray-500">This Week</p>
            <p class="text-lg font-bold">1,205</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 text-center hidden @lg:block">
            <p class="text-xs text-gray-500">This Month</p>
            <p class="text-lg font-bold">2,420</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Same component in sidebar (narrow) — automatically adapts -->
<aside class="lg:col-span-1">
  <div class="@container">
    <!-- Same inner HTML — stacks vertically, hides "This Month" stat -->
  </div>
</aside>
```

## Container Queries vs Media Queries

| Feature | Media Queries (`sm:`, `lg:`) | Container Queries (`@sm:`, `@lg:`) |
|---|---|---|
| Responds to | Viewport width | Parent container width |
| Use for | Page layout | Reusable components |
| Nesting | Doesn't matter | Container must be marked |
| Browser support | Universal | Modern browsers (2023+) |

**Rule of thumb:** Use media queries for page-level layout. Use container queries for components that appear in different contexts.

## What You Learned

- **`@container`** — marks an element as a container query context
- **`@sm:`, `@md:`, `@lg:`** — apply styles based on container width
- **Named containers** — `@container/name` + `@sm/name:` for nested contexts
- **Component-level responsiveness** — same component adapts to sidebar vs main
- **`hidden @lg:block`** — show/hide based on container width
- **Media vs container queries** — viewport layout vs component adaptation

The components are truly responsive now — they adapt to wherever they're placed. But there's a performance problem: the CSS bundle is 500KB and growing.

---

[← Chapter 11: Dark Mode](chapter-11-dark-mode.md) | [Chapter 13: Performance →](chapter-13-performance.md)
