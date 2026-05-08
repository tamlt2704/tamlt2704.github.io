# Chapter 9: Responsive Tables

[← Chapter 8: Cards](chapter-08-cards.md) | [Chapter 10: Forms →](chapter-10-forms.md)

---

## The Breakage

The analytics page has a user activity table with 8 columns: Name, Email, Plan, Status, Projects, Storage, Last Active, Actions. On desktop it's fine. On mobile:

```html
<table class="w-full">
  <thead>
    <tr>
      <th class="p-3 text-left">Name</th>
      <th class="p-3 text-left">Email</th>
      <th class="p-3 text-left">Plan</th>
      <th class="p-3 text-left">Status</th>
      <th class="p-3 text-left">Projects</th>
      <th class="p-3 text-left">Storage</th>
      <th class="p-3 text-left">Last Active</th>
      <th class="p-3 text-left">Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="p-3">Alice Johnson</td>
      <td class="p-3">alice@example.com</td>
      <td class="p-3">Pro</td>
      <td class="p-3">Active</td>
      <td class="p-3">12</td>
      <td class="p-3">4.2 GB</td>
      <td class="p-3">2 hours ago</td>
      <td class="p-3"><button>Edit</button></td>
    </tr>
  </tbody>
</table>
```

The table is 900px+ wide. On a 375px phone, users scroll right for ages. They can't see the Name and Actions columns at the same time. Diana: "I have to scroll sideways to find the delete button. This is 2024."

## Strategy 1: Horizontal Scroll with Sticky Column

The simplest fix — let it scroll but pin the important column:

```html
<div class="overflow-x-auto rounded-lg border">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th class="sticky left-0 bg-gray-50 px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
          Name
        </th>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan</th>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Active</th>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200 bg-white">
      <tr>
        <td class="sticky left-0 bg-white px-4 py-3 text-sm font-medium text-gray-900 whitespace-nowrap">
          Alice Johnson
        </td>
        <td class="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">alice@example.com</td>
        <td class="px-4 py-3 text-sm text-gray-500">Pro</td>
        <td class="px-4 py-3 text-sm">
          <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">Active</span>
        </td>
        <td class="px-4 py-3 text-sm text-gray-500">2h ago</td>
        <td class="px-4 py-3 text-sm">
          <button class="text-blue-600 hover:text-blue-800">Edit</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

Key: `overflow-x-auto` on the wrapper + `sticky left-0` on the Name column.

## Strategy 2: Stacked Cards on Mobile

Transform the table into cards on small screens:

```html
<!-- Desktop: table. Mobile: stacked cards -->
<div class="overflow-x-auto rounded-lg border hidden sm:block">
  <table class="min-w-full divide-y divide-gray-200">
    <!-- Standard table for sm+ -->
    <thead class="bg-gray-50">
      <tr>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan</th>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
        <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200">
      <tr>
        <td class="px-4 py-3 text-sm font-medium">Alice Johnson</td>
        <td class="px-4 py-3 text-sm">Pro</td>
        <td class="px-4 py-3 text-sm"><span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Active</span></td>
        <td class="px-4 py-3 text-sm"><button class="text-blue-600">Edit</button></td>
      </tr>
    </tbody>
  </table>
</div>

<!-- Mobile: card layout -->
<div class="sm:hidden space-y-3">
  <div class="bg-white rounded-lg border p-4">
    <div class="flex items-center justify-between mb-2">
      <span class="font-medium text-gray-900">Alice Johnson</span>
      <span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Active</span>
    </div>
    <div class="text-sm text-gray-500 space-y-1">
      <p><span class="font-medium text-gray-700">Plan:</span> Pro</p>
      <p><span class="font-medium text-gray-700">Projects:</span> 12</p>
      <p><span class="font-medium text-gray-700">Last active:</span> 2h ago</p>
    </div>
    <div class="mt-3 pt-3 border-t flex gap-3">
      <button class="text-sm text-blue-600 font-medium">Edit</button>
      <button class="text-sm text-red-600 font-medium">Delete</button>
    </div>
  </div>
</div>
```

Pattern: `hidden sm:block` for the table, `sm:hidden` for the card version.

## Strategy 3: Hide Less Important Columns

Show fewer columns on smaller screens:

```html
<table class="min-w-full divide-y divide-gray-200">
  <thead class="bg-gray-50">
    <tr>
      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Email</th>
      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden lg:table-cell">Storage</th>
      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Last Active</th>
      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
    </tr>
  </thead>
  <tbody class="divide-y divide-gray-200">
    <tr>
      <td class="px-4 py-3 text-sm font-medium">Alice Johnson</td>
      <td class="px-4 py-3 text-sm hidden md:table-cell">alice@example.com</td>
      <td class="px-4 py-3 text-sm"><span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Active</span></td>
      <td class="px-4 py-3 text-sm hidden lg:table-cell">4.2 GB</td>
      <td class="px-4 py-3 text-sm hidden sm:table-cell">2h ago</td>
      <td class="px-4 py-3 text-sm"><button class="text-blue-600">Edit</button></td>
    </tr>
  </tbody>
</table>
```

Use `hidden md:table-cell` — not `hidden md:block` (tables need `table-cell` display).

## What You Learned

- **`overflow-x-auto`** — horizontal scroll wrapper for wide tables
- **`sticky left-0`** — pin important columns while scrolling
- **Stacked cards** — `hidden sm:block` table + `sm:hidden` cards for mobile
- **`hidden md:table-cell`** — progressively show columns at wider breakpoints
- **`min-w-full`** — table takes at least full container width
- **`whitespace-nowrap`** — prevent cell content from wrapping awkwardly
- **`divide-y`** — clean row separators without manual borders

Tables are tamed. But the settings form? Input fields overflow their container on mobile and labels sit awkwardly beside tiny inputs.

---

[← Chapter 8: Cards](chapter-08-cards.md) | [Chapter 10: Forms →](chapter-10-forms.md)
