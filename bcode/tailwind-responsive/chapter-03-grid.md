# Chapter 3: Grid Systems

[← Chapter 2: Flexbox](chapter-02-flexbox.md) | [Chapter 4: Responsive Typography →](chapter-04-typography.md)

---

## The Breakage

LaunchPad's dashboard has stat cards. On desktop, they should be in a 4-column grid. On tablet, 2 columns. On mobile, stacked. The current code uses flexbox with fixed widths:

```html
<div class="flex flex-wrap">
  <div class="w-[300px] m-2">Card 1</div>
  <div class="w-[300px] m-2">Card 2</div>
  <div class="w-[300px] m-2">Card 3</div>
  <div class="w-[300px] m-2">Card 4</div>
</div>
```

At 768px, three cards fit on one row and the fourth wraps alone — looking unbalanced. At 640px, two cards fit with awkward gaps. The layout never looks intentional.

Jake: "I want exactly 2 columns on tablet and exactly 4 on desktop. Not 'whatever fits.'"

## CSS Grid: Precise Column Control

Grid gives you explicit control over columns and rows:

```html
<!-- Exactly the columns you want at each breakpoint -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 1</div>
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 2</div>
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 3</div>
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 4</div>
</div>
```

- Mobile: 1 column (stacked)
- sm (640px+): 2 columns (2×2 grid)
- lg (1024px+): 4 columns (single row)

No guessing. No "whatever fits." Exactly what you specified.

## Grid vs Flexbox: When to Use Which

| Use Grid when... | Use Flexbox when... |
|---|---|
| You know the column count | Items should wrap naturally |
| Layout is 2-dimensional (rows AND columns) | Layout is 1-dimensional (row OR column) |
| Items should align to a grid | Items have varying sizes |
| You want equal-width columns | You want items to grow/shrink |

In practice: **Grid for page layout and card grids. Flexbox for component internals and navigation.**

## Grid Utilities in Tailwind

```html
<!-- Column count -->
<div class="grid grid-cols-3">     <!-- 3 equal columns -->
<div class="grid grid-cols-12">    <!-- 12-column system -->

<!-- Gap (spacing between cells) -->
<div class="grid gap-4">           <!-- 1rem gap all around -->
<div class="grid gap-x-4 gap-y-2"> <!-- Different horizontal/vertical gaps -->

<!-- Column span -->
<div class="col-span-2">          <!-- This item spans 2 columns -->
<div class="col-span-full">       <!-- Spans all columns -->

<!-- Row span -->
<div class="row-span-2">          <!-- Spans 2 rows -->
```

## The Dashboard Stats Grid

```html
<section class="p-4 sm:p-6 lg:p-8">
  <h2 class="text-xl font-bold mb-4">Overview</h2>

  <!-- Stats: 1 → 2 → 4 columns -->
  <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
    <div class="bg-white rounded-lg p-5 shadow-sm border">
      <p class="text-sm font-medium text-gray-500">Revenue</p>
      <p class="text-2xl font-bold mt-1">$48,200</p>
      <p class="text-sm text-green-600 mt-2">↑ 12% from last month</p>
    </div>
    <div class="bg-white rounded-lg p-5 shadow-sm border">
      <p class="text-sm font-medium text-gray-500">Users</p>
      <p class="text-2xl font-bold mt-1">2,420</p>
      <p class="text-sm text-green-600 mt-2">↑ 8% from last month</p>
    </div>
    <div class="bg-white rounded-lg p-5 shadow-sm border">
      <p class="text-sm font-medium text-gray-500">Orders</p>
      <p class="text-2xl font-bold mt-1">1,210</p>
      <p class="text-sm text-red-600 mt-2">↓ 3% from last month</p>
    </div>
    <div class="bg-white rounded-lg p-5 shadow-sm border">
      <p class="text-sm font-medium text-gray-500">Conversion</p>
      <p class="text-2xl font-bold mt-1">3.2%</p>
      <p class="text-sm text-gray-500 mt-2">No change</p>
    </div>
  </div>

  <!-- Mixed layout: chart (wide) + sidebar (narrow) -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
    <div class="lg:col-span-2 bg-white rounded-lg p-5 shadow-sm border">
      <h3 class="font-semibold mb-4">Revenue Chart</h3>
      <div class="h-64 bg-gray-50 rounded flex items-center justify-center">
        [Chart placeholder]
      </div>
    </div>
    <div class="bg-white rounded-lg p-5 shadow-sm border">
      <h3 class="font-semibold mb-4">Recent Activity</h3>
      <div class="space-y-3">
        <p class="text-sm">New order #1234</p>
        <p class="text-sm">User signed up</p>
        <p class="text-sm">Payment received</p>
      </div>
    </div>
  </div>
</section>
```

The chart takes 2/3 of the width (`col-span-2` in a 3-column grid), and the activity feed takes 1/3. On mobile, they stack.

## Auto-Fit: Responsive Without Breakpoints

For grids where you want "as many columns as fit":

```html
<!-- Cards that auto-fit: minimum 250px, fill available space -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 1</div>
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 2</div>
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 3</div>
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 4</div>
  <div class="bg-white p-4 rounded-lg shadow-sm">Card 5</div>
</div>
```

This creates columns that are at least 250px wide. As the screen grows, more columns appear. As it shrinks, columns drop off. No breakpoints needed.

Alternatively, with Tailwind's built-in utilities:

```html
<!-- Simpler approach: explicit breakpoints (more predictable) -->
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4">
  <!-- Cards -->
</div>
```

## Column Spanning

```html
<!-- 12-column grid with spanning -->
<div class="grid grid-cols-12 gap-4">
  <div class="col-span-12 md:col-span-8">Main content (8/12)</div>
  <div class="col-span-12 md:col-span-4">Sidebar (4/12)</div>

  <div class="col-span-12 sm:col-span-6 lg:col-span-3">Quarter 1</div>
  <div class="col-span-12 sm:col-span-6 lg:col-span-3">Quarter 2</div>
  <div class="col-span-12 sm:col-span-6 lg:col-span-3">Quarter 3</div>
  <div class="col-span-12 sm:col-span-6 lg:col-span-3">Quarter 4</div>
</div>
```

The 12-column grid is familiar from Bootstrap. In Tailwind, you build it explicitly with `grid-cols-12` and `col-span-*`.

## Common Grid Patterns

### Feature Grid (Marketing Pages)

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
  <div class="text-center p-6">
    <div class="text-4xl mb-4">🚀</div>
    <h3 class="font-bold text-lg mb-2">Fast</h3>
    <p class="text-gray-600">Blazing fast performance out of the box.</p>
  </div>
  <!-- More features... -->
</div>
```

### Image Gallery

```html
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
  <img src="1.jpg" alt="" class="w-full h-48 object-cover rounded">
  <img src="2.jpg" alt="" class="w-full h-48 object-cover rounded">
  <!-- More images... -->
</div>
```

### Dashboard with Mixed Sizes

```html
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
  <!-- Full-width item -->
  <div class="md:col-span-2 xl:col-span-3 bg-white p-4 rounded-lg">
    Banner / Alert
  </div>
  <!-- Regular items -->
  <div class="bg-white p-4 rounded-lg">Widget 1</div>
  <div class="bg-white p-4 rounded-lg">Widget 2</div>
  <div class="bg-white p-4 rounded-lg">Widget 3</div>
</div>
```

## What You Learned

- **`grid`** — enables CSS Grid on a container
- **`grid-cols-*`** — set explicit column count (responsive with breakpoints)
- **`col-span-*`** — make items span multiple columns
- **`gap-*`** — spacing between grid cells
- **`auto-fit` + `minmax`** — responsive columns without breakpoints
- **Grid vs Flexbox** — Grid for 2D layouts, Flexbox for 1D
- **12-column system** — `grid-cols-12` + `col-span-*` for Bootstrap-style layouts

The grid layout is solid. But the text looks wrong — too small on mobile, too large on ultrawide. We need responsive typography.

---

[← Chapter 2: Flexbox](chapter-02-flexbox.md) | [Chapter 4: Responsive Typography →](chapter-04-typography.md)
