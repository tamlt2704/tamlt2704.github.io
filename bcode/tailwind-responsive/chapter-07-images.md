# Chapter 7: Responsive Images

[← Chapter 6: Navigation](chapter-06-navigation.md) | [Chapter 8: Cards →](chapter-08-cards.md)

---

## The Breakage

LaunchPad's marketing page has a hero image. Jake designed it at 1440×600px. The implementation:

```html
<div class="relative">
  <img src="/hero-dashboard.png" alt="Dashboard preview" class="w-full">
  <div class="absolute top-1/2 left-12 -translate-y-1/2">
    <h1 class="text-5xl font-bold text-white">Ship Faster</h1>
    <p class="text-xl text-white/80 mt-4">The dashboard that grows with you.</p>
  </div>
</div>
```

Problems:
- On mobile, the image squishes to 375×156px — the text overlay is unreadable
- On ultrawide, the image stretches to 3840×1600px — pixelated and distorted
- The aspect ratio changes at every width, pushing content below unpredictably

Diana: "The hero looks like it's being tortured on my phone."

## Object-Fit: Control How Images Fill Space

```html
<!-- Fixed height container with image that covers without distortion -->
<div class="relative h-64 sm:h-80 lg:h-[500px]">
  <img
    src="/hero-dashboard.png"
    alt="Dashboard preview"
    class="w-full h-full object-cover"
  >
  <div class="absolute inset-0 bg-black/40 flex items-center justify-center">
    <div class="text-center px-4">
      <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">Ship Faster</h1>
      <p class="text-base sm:text-lg text-white/80 mt-3">The dashboard that grows with you.</p>
    </div>
  </div>
</div>
```

Key classes:
- `object-cover` — image fills container, cropping excess (no distortion)
- `object-contain` — image fits inside container, may have letterboxing
- `object-center` — crop from center (default)
- `object-top` — crop from top (good for portraits)

## Aspect Ratio

Lock the image to a consistent ratio regardless of width:

```html
<!-- 16:9 hero that scales proportionally -->
<div class="relative aspect-video overflow-hidden rounded-lg">
  <img
    src="/hero-dashboard.png"
    alt="Dashboard preview"
    class="w-full h-full object-cover"
  >
</div>

<!-- Square thumbnails -->
<div class="grid grid-cols-3 gap-2">
  <div class="aspect-square overflow-hidden rounded-lg">
    <img src="/thumb-1.jpg" alt="" class="w-full h-full object-cover">
  </div>
  <div class="aspect-square overflow-hidden rounded-lg">
    <img src="/thumb-2.jpg" alt="" class="w-full h-full object-cover">
  </div>
  <div class="aspect-square overflow-hidden rounded-lg">
    <img src="/thumb-3.jpg" alt="" class="w-full h-full object-cover">
  </div>
</div>
```

Tailwind aspect ratio utilities:
- `aspect-video` — 16:9
- `aspect-square` — 1:1
- `aspect-[4/3]` — custom ratio

## Responsive Images with srcset

Serve different image sizes based on viewport:

```html
<img
  srcset="
    /hero-400.webp 400w,
    /hero-800.webp 800w,
    /hero-1200.webp 1200w,
    /hero-1920.webp 1920w
  "
  sizes="(max-width: 640px) 100vw,
         (max-width: 1024px) 80vw,
         1200px"
  src="/hero-1200.webp"
  alt="Dashboard preview"
  class="w-full h-64 sm:h-80 lg:h-[500px] object-cover rounded-lg"
  loading="lazy"
>
```

- `srcset` — tells the browser which sizes are available
- `sizes` — tells the browser how wide the image will display
- `loading="lazy"` — defer offscreen images (native lazy loading)

## Background Images with Tailwind

```html
<!-- Full-bleed hero with background image -->
<section class="relative bg-cover bg-center bg-no-repeat h-72 sm:h-96 lg:h-[600px]"
         style="background-image: url('/hero-dashboard.png')">
  <div class="absolute inset-0 bg-gradient-to-r from-black/60 to-transparent"></div>
  <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center">
    <div class="max-w-lg">
      <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">Ship Faster</h1>
      <p class="mt-4 text-base sm:text-lg text-white/80">The dashboard that grows with you.</p>
      <button class="mt-6 px-6 py-3 bg-white text-gray-900 font-semibold rounded-lg hover:bg-gray-100">
        Get Started
      </button>
    </div>
  </div>
</section>
```

## User Avatars (Common Pattern)

```html
<!-- Responsive avatar sizes -->
<img
  src="/avatar.jpg"
  alt="User avatar"
  class="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 rounded-full object-cover ring-2 ring-white"
>
```

## What You Learned

- **`object-cover`** — fill container without distortion (crops excess)
- **`object-contain`** — fit inside container (may letterbox)
- **`aspect-video` / `aspect-square`** — lock aspect ratio regardless of width
- **`aspect-[4/3]`** — custom aspect ratios with arbitrary values
- **`srcset` + `sizes`** — serve appropriately sized images per viewport
- **`loading="lazy"`** — native lazy loading for offscreen images
- **`bg-cover bg-center`** — responsive background images
- **Responsive height** — `h-64 sm:h-80 lg:h-[500px]` for hero sections

Images are under control. Next problem: the card grid on the features page looks wrong at literally every screen size.

---

[← Chapter 6: Navigation](chapter-06-navigation.md) | [Chapter 8: Cards →](chapter-08-cards.md)
