# Chapter 10: Responsive Forms

[← Chapter 9: Tables](chapter-09-tables.md) | [Chapter 11: Dark Mode →](chapter-11-dark-mode.md)

---

## The Breakage

The account settings page has a form with side-by-side labels and inputs. Jake's Figma shows a clean two-column layout:

```html
<form class="p-8">
  <div class="flex items-center gap-4 mb-6">
    <label class="w-48 text-right text-sm font-medium">Full Name</label>
    <input type="text" class="w-96 border rounded-lg px-4 py-2">
  </div>
  <div class="flex items-center gap-4 mb-6">
    <label class="w-48 text-right text-sm font-medium">Email Address</label>
    <input type="email" class="w-96 border rounded-lg px-4 py-2">
  </div>
  <div class="flex items-center gap-4 mb-6">
    <label class="w-48 text-right text-sm font-medium">Company Name</label>
    <input type="text" class="w-96 border rounded-lg px-4 py-2">
  </div>
</form>
```

On a 375px phone: the label takes 192px, the input tries to be 384px. Total: 576px. The input overflows the screen by 200px. Users can't even see what they're typing.

QA team: "Form is completely broken on mobile. Can't submit settings."

## The Fix: Stacked on Mobile, Side-by-Side on Desktop

```html
<form class="max-w-2xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
  <h2 class="text-xl sm:text-2xl font-bold mb-6 sm:mb-8">Account Settings</h2>

  <div class="space-y-5 sm:space-y-6">
    <!-- Each field: stacked on mobile, inline on md+ -->
    <div class="grid grid-cols-1 md:grid-cols-[200px_1fr] md:items-center gap-1.5 md:gap-4">
      <label for="name" class="text-sm font-medium text-gray-700">Full Name</label>
      <input
        type="text" id="name"
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
               focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        placeholder="Jane Smith"
      >
    </div>

    <div class="grid grid-cols-1 md:grid-cols-[200px_1fr] md:items-center gap-1.5 md:gap-4">
      <label for="email" class="text-sm font-medium text-gray-700">Email Address</label>
      <input
        type="email" id="email"
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
               focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        placeholder="jane@launchpad.io"
      >
    </div>

    <div class="grid grid-cols-1 md:grid-cols-[200px_1fr] md:items-start gap-1.5 md:gap-4">
      <label for="bio" class="text-sm font-medium text-gray-700 md:pt-2">Bio</label>
      <textarea
        id="bio" rows="4"
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
               focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y"
        placeholder="Tell us about yourself..."
      ></textarea>
    </div>
  </div>

  <!-- Actions -->
  <div class="mt-8 flex flex-col sm:flex-row sm:justify-end gap-3">
    <button type="button" class="px-4 py-2 text-sm font-medium text-gray-700 border rounded-lg hover:bg-gray-50 order-2 sm:order-1">
      Cancel
    </button>
    <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 order-1 sm:order-2">
      Save Changes
    </button>
  </div>
</form>
```

Key patterns:
- `grid-cols-1 md:grid-cols-[200px_1fr]` — stacked on mobile, label+input on desktop
- `w-full` on inputs — they fill available space, never overflow
- `flex-col sm:flex-row` on buttons — stacked on mobile, inline on desktop
- `order-*` — primary action first on mobile (thumb-friendly)

## Multi-Column Form Fields

```html
<!-- Two inputs side by side on larger screens -->
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
  <div>
    <label for="first" class="block text-sm font-medium text-gray-700 mb-1.5">First Name</label>
    <input type="text" id="first" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
  </div>
  <div>
    <label for="last" class="block text-sm font-medium text-gray-700 mb-1.5">Last Name</label>
    <input type="text" id="last" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
  </div>
</div>

<!-- Three columns for address -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr] gap-4">
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1.5">City</label>
    <input type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
  </div>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1.5">State</label>
    <select class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
      <option>CA</option>
      <option>NY</option>
    </select>
  </div>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-1.5">ZIP</label>
    <input type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
  </div>
</div>
```

## Touch-Friendly Inputs

Mobile inputs need larger tap targets:

```html
<!-- Minimum 44px touch target (py-3 = 12px top + 12px bottom + ~20px text = 44px) -->
<input
  type="text"
  class="w-full border border-gray-300 rounded-lg px-4 py-3 text-base
         focus:ring-2 focus:ring-blue-500 focus:border-blue-500
         sm:px-3 sm:py-2 sm:text-sm"
>

<!-- Checkbox with adequate tap area -->
<label class="flex items-center gap-3 py-2 cursor-pointer">
  <input type="checkbox" class="w-5 h-5 sm:w-4 sm:h-4 rounded border-gray-300 text-blue-600">
  <span class="text-sm text-gray-700">Send me email notifications</span>
</label>
```

Use `text-base` on mobile inputs to prevent iOS zoom (Safari zooms inputs smaller than 16px).

## What You Learned

- **`grid-cols-1 md:grid-cols-[200px_1fr]`** — stacked labels on mobile, inline on desktop
- **`w-full`** — inputs fill container width, never overflow
- **`flex-col sm:flex-row`** — stack buttons on mobile, inline on desktop
- **`order-*`** — reorder elements for mobile UX (primary action first)
- **`text-base` on mobile inputs** — prevents iOS Safari auto-zoom
- **`py-3` minimum** — 44px touch targets for mobile accessibility
- **`sm:grid-cols-2`** — multi-column fields when space allows

Forms are usable on every device. But users are complaining about something else entirely — they want dark mode.

---

[← Chapter 9: Tables](chapter-09-tables.md) | [Chapter 11: Dark Mode →](chapter-11-dark-mode.md)
