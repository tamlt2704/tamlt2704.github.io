# Chapter 8: Responsive Card Layouts

[← Chapter 7: Images](chapter-07-images.md) | [Chapter 9: Tables →](chapter-09-tables.md)

---

## The Breakage

The pricing page has three plan cards. Jake designed them side-by-side at 1440px. The implementation:

```html
<div class="flex gap-6 p-8">
  <div class="w-1/3 bg-white rounded-xl p-6 shadow">
    <h3 class="text-xl font-bold">Starter</h3>
    <p class="text-3xl font-bold mt-4">$9<span class="text-sm">/mo</span></p>
    <ul class="mt-6 space-y-2 text-sm">
      <li>5 projects</li>
      <li>1 GB storage</li>
      <li>Email support</li>
    </ul>
    <button class="mt-6 w-full py-2 bg-gray-900 text-white rounded-lg">Choose</button>
  </div>
  <!-- Two more cards... -->
</div>
```

At 768px, each card is 768/3 = 256px minus gaps — text wraps awkwardly, buttons get cramped. At 375px, cards are 125px wide each. Completely unusable.

QA team: "Cards look wrong at every breakpoint. Not just mobile — tablet too."

## The Fix: Responsive Grid Cards

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4 sm:p-6 lg:p-8">
  <!-- Starter -->
  <div class="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md transition-shadow">
    <h3 class="text-lg font-bold text-gray-900">Starter</h3>
    <p class="mt-4">
      <span class="text-4xl font-bold">$9</span>
      <span class="text-gray-500">/month</span>
    </p>
    <ul class="mt-6 space-y-3 text-sm text-gray-600">
      <li class="flex items-center gap-2">
        <svg class="w-4 h-4 text-green-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
        </svg>
        5 projects
      </li>
      <li class="flex items-center gap-2">
        <svg class="w-4 h-4 text-green-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
        </svg>
        1 GB storage
      </li>
      <li class="flex items-center gap-2">
        <svg class="w-4 h-4 text-green-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
        </svg>
        Email support
      </li>
    </ul>
    <button class="mt-8 w-full py-2.5 bg-gray-900 text-white text-sm font-semibold rounded-lg hover:bg-gray-800">
      Choose Starter
    </button>
  </div>

  <!-- Pro (featured) -->
  <div class="bg-gray-900 text-white rounded-xl p-6 shadow-lg ring-2 ring-gray-900 relative">
    <span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold px-3 py-1 rounded-full">
      Most Popular
    </span>
    <h3 class="text-lg font-bold">Pro</h3>
    <p class="mt-4">
      <span class="text-4xl font-bold">$29</span>
      <span class="text-gray-300">/month</span>
    </p>
    <ul class="mt-6 space-y-3 text-sm text-gray-300">
      <li class="flex items-center gap-2">✓ Unlimited projects</li>
      <li class="flex items-center gap-2">✓ 50 GB storage</li>
      <li class="flex items-center gap-2">✓ Priority support</li>
      <li class="flex items-center gap-2">✓ Custom domains</li>
    </ul>
    <button class="mt-8 w-full py-2.5 bg-white text-gray-900 text-sm font-semibold rounded-lg hover:bg-gray-100">
      Choose Pro
    </button>
  </div>

  <!-- Enterprise -->
  <div class="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md transition-shadow md:col-span-2 lg:col-span-1">
    <h3 class="text-lg font-bold text-gray-900">Enterprise</h3>
    <p class="mt-4">
      <span class="text-4xl font-bold">$99</span>
      <span class="text-gray-500">/month</span>
    </p>
    <ul class="mt-6 space-y-3 text-sm text-gray-600">
      <li class="flex items-center gap-2">✓ Everything in Pro</li>
      <li class="flex items-center gap-2">✓ SSO & SAML</li>
      <li class="flex items-center gap-2">✓ Dedicated support</li>
      <li class="flex items-center gap-2">✓ SLA guarantee</li>
    </ul>
    <button class="mt-8 w-full py-2.5 bg-gray-900 text-white text-sm font-semibold rounded-lg hover:bg-gray-800">
      Contact Sales
    </button>
  </div>
</div>
```

Notice `md:col-span-2 lg:col-span-1` on the Enterprise card — at `md` (2-column grid), it spans full width so it doesn't sit alone. At `lg` (3 columns), it takes its normal single column.

## Min-Width Trick: Cards That Never Get Too Narrow

```html
<!-- Cards with a minimum width — auto-wrap when they'd get too small -->
<div class="grid grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-6 p-4">
  <div class="bg-white rounded-lg p-5 shadow-sm border">
    <h3 class="font-semibold">Project Alpha</h3>
    <p class="text-sm text-gray-500 mt-2">Last updated 2h ago</p>
    <div class="mt-4 flex items-center gap-2">
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="bg-blue-500 h-2 rounded-full w-3/4"></div>
      </div>
      <span class="text-xs text-gray-500 shrink-0">75%</span>
    </div>
  </div>
  <!-- More cards... -->
</div>
```

Each card is at least 280px. The grid automatically adjusts column count based on available space.

## Equal-Height Cards with Flexbox

Cards with varying content lengths look uneven. Fix with flex:

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- Each card uses flex-col to push button to bottom -->
  <div class="flex flex-col bg-white rounded-lg p-5 shadow-sm border">
    <h3 class="font-semibold">Short Title</h3>
    <p class="text-sm text-gray-600 mt-2 flex-1">Brief description.</p>
    <button class="mt-4 w-full py-2 bg-gray-900 text-white text-sm rounded-lg">View</button>
  </div>
  <div class="flex flex-col bg-white rounded-lg p-5 shadow-sm border">
    <h3 class="font-semibold">Much Longer Title Here</h3>
    <p class="text-sm text-gray-600 mt-2 flex-1">
      This card has a much longer description that takes up more vertical space
      and would normally push the button down unevenly.
    </p>
    <button class="mt-4 w-full py-2 bg-gray-900 text-white text-sm rounded-lg">View</button>
  </div>
</div>
```

`flex-1` on the description makes it grow to fill available space, pushing buttons to the same vertical position.

## What You Learned

- **`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`** — responsive column count for card grids
- **`col-span-2 lg:col-span-1`** — handle odd card counts at intermediate breakpoints
- **`minmax(280px, 1fr)`** — cards never shrink below a readable width
- **`auto-fill` vs `auto-fit`** — auto-fill leaves empty tracks, auto-fit collapses them
- **`flex flex-col` + `flex-1`** — equal-height cards with bottom-aligned buttons
- **`hover:shadow-md transition-shadow`** — subtle interaction feedback

The cards are solid. But the data table on the analytics page? It has 8 columns and scrolls horizontally forever on mobile.

---

[← Chapter 7: Images](chapter-07-images.md) | [Chapter 9: Tables →](chapter-09-tables.md)
