# Chapter 11: Animate on Scroll — Scroll-Driven Animation

[← Chapter 10: Controls](chapter-10-controls.md) | [Chapter 12: Event-Driven Animation →](chapter-12-event-driven.md)

---

## The Brief

The site has five sections below the fold. Each should reveal as the user scrolls:

1. **Specs section** — numbers count up when visible
2. **Heritage section** — timeline of brand history fades in
3. **Craftsmanship section** — images slide in from alternating sides
4. **Collection grid** — cards stagger in
5. **CTA section** — final call-to-action with dramatic entrance

Theo's rule: "Nothing below the fold should animate on page load. It animates when the user reaches it. Anything else is wasted motion."

---

## IntersectionObserver: The Foundation

The browser's `IntersectionObserver` API tells you when an element enters the viewport. Combine it with Anime.js to trigger animations on scroll:

```javascript
function animateOnScroll(selector, animationConfig) {
  const elements = document.querySelectorAll(selector);

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        anime({
          targets: entry.target,
          ...animationConfig,
        });
        observer.unobserve(entry.target);  // Only animate once
      }
    });
  }, {
    threshold: 0.2,  // Trigger when 20% visible
  });

  elements.forEach(el => observer.observe(el));
}

// Usage
animateOnScroll('.spec-card', {
  opacity: [0, 1],
  translateY: [40, 0],
  duration: 800,
  easing: 'cubicBezier(0.16, 1, 0.3, 1)',
});
```

When 20% of a `.spec-card` enters the viewport, it fades in and slides up. Once animated, the observer disconnects — no re-triggering on scroll back up.

---

## Threshold and Root Margin

Fine-tune when the animation triggers:

```javascript
const observer = new IntersectionObserver(callback, {
  threshold: 0.2,           // 0 = any pixel visible, 1 = fully visible
  rootMargin: '0px 0px -100px 0px',  // Trigger 100px before bottom edge
});
```

| Option | Effect |
|---|---|
| `threshold: 0` | Triggers immediately when any pixel enters |
| `threshold: 0.2` | Triggers when 20% is visible |
| `threshold: 1` | Triggers only when fully visible |
| `rootMargin: '-100px'` | Shrinks the trigger zone (element must be 100px inside viewport) |
| `rootMargin: '100px'` | Expands the trigger zone (triggers 100px before entering) |

For the Lumina site, `threshold: 0.2` with `rootMargin: '0px 0px -50px 0px'` means elements trigger when they're 50px inside the viewport and 20% visible. This prevents animations from firing when just a sliver peeks in.

---

## Staggered Scroll Reveals

For groups of elements (like the collection grid), stagger within the observer:

```javascript
function staggerOnScroll(containerSelector, itemSelector, config) {
  const container = document.querySelector(containerSelector);

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        anime({
          targets: entry.target.querySelectorAll(itemSelector),
          opacity: [0, 1],
          translateY: [30, 0],
          delay: anime.stagger(80),
          duration: 600,
          easing: 'cubicBezier(0.16, 1, 0.3, 1)',
          ...config,
        });
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  observer.observe(container);
}

// The grid container triggers, then cards stagger in
staggerOnScroll('.collection-grid', '.product-card', {
  delay: anime.stagger(60, { grid: [3, 4], from: 'center' }),
});
```

The observer watches the container. When it enters, all cards inside stagger in with a grid ripple.

---

## Scroll-Scrubbed Animation

For the watch assembly, Theo wants it tied to scroll position — not triggered once, but continuously controlled by how far the user has scrolled:

```javascript
const assembly = anime.timeline({
  autoplay: false,
  easing: 'cubicBezier(0.4, 0, 0.2, 1)',
});

assembly
  .add({ targets: '.dial', opacity: [0, 1], scale: [0.85, 1], duration: 600 })
  .add({ targets: '.hour-hand', rotate: [0, 210], duration: 1000 }, 400)
  .add({ targets: '.minute-hand', rotate: [0, 60], duration: 800 }, 800)
  .add({ targets: '.strap', scaleY: [0, 1], duration: 500 }, 1200);

// Scrub based on scroll position
function handleScroll() {
  const section = document.querySelector('.watch-section');
  const rect = section.getBoundingClientRect();
  const windowHeight = window.innerHeight;

  // Calculate progress: 0 when section enters, 1 when it leaves
  const start = windowHeight;  // Section top hits viewport bottom
  const end = -section.offsetHeight;  // Section bottom leaves viewport top
  const progress = (start - rect.top) / (start - end);

  // Clamp between 0 and 1
  const clamped = Math.max(0, Math.min(1, progress));

  // Seek the timeline
  assembly.seek(clamped * assembly.duration);
}

window.addEventListener('scroll', handleScroll, { passive: true });
handleScroll();  // Set initial state
```

As the user scrolls through the watch section, the assembly plays forward. Scroll back up and it reverses. The user controls the animation with their scroll wheel.

---

## Scroll Performance

Scroll events fire rapidly (60+ times per second). Keep the handler fast:

```javascript
// ✅ Good: only seek (no DOM reads in the hot path)
let ticking = false;

window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      handleScroll();
      ticking = false;
    });
    ticking = true;
  }
}, { passive: true });

// ✅ Always use { passive: true } for scroll listeners
// It tells the browser you won't call preventDefault()
```

The `requestAnimationFrame` throttle ensures you only calculate once per frame, even if scroll fires more often.

---

## A Reusable Scroll Reveal System

For the Lumina site, create a utility:

```javascript
class ScrollReveal {
  constructor(options = {}) {
    this.threshold = options.threshold || 0.2;
    this.rootMargin = options.rootMargin || '0px 0px -50px 0px';
    this.observer = new IntersectionObserver(
      this.handleIntersect.bind(this),
      { threshold: this.threshold, rootMargin: this.rootMargin }
    );
    this.animations = new Map();
  }

  add(selector, config) {
    document.querySelectorAll(selector).forEach(el => {
      this.animations.set(el, config);
      el.style.opacity = '0';  // Hide initially
      this.observer.observe(el);
    });
    return this;
  }

  handleIntersect(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const config = this.animations.get(entry.target);
        anime({
          targets: entry.target,
          opacity: [0, 1],
          ...config,
        });
        this.observer.unobserve(entry.target);
        this.animations.delete(entry.target);
      }
    });
  }

  destroy() {
    this.observer.disconnect();
    this.animations.clear();
  }
}

// Usage
const reveals = new ScrollReveal({ threshold: 0.2 });

reveals
  .add('.spec-card', {
    translateY: [40, 0],
    delay: anime.stagger(100),
    duration: 800,
    easing: 'cubicBezier(0.16, 1, 0.3, 1)',
  })
  .add('.heritage-item', {
    translateX: [-60, 0],
    delay: anime.stagger(150),
    duration: 900,
    easing: 'cubicBezier(0.16, 1, 0.3, 1)',
  })
  .add('.craft-image', {
    scale: [0.9, 1],
    duration: 1000,
    easing: 'easeOutCubic',
  })
  .add('.cta-section', {
    translateY: [60, 0],
    duration: 1000,
    easing: 'cubicBezier(0.16, 1, 0.3, 1)',
  });
```

One system handles all scroll reveals. Add new sections with one line.

---

## Alternating Directions

The craftsmanship section has images alternating left/right:

```javascript
document.querySelectorAll('.craft-image').forEach((img, i) => {
  const fromLeft = i % 2 === 0;

  reveals.add(img, {
    translateX: [fromLeft ? -60 : 60, 0],
    duration: 900,
    easing: 'cubicBezier(0.16, 1, 0.3, 1)',
  });
});
```

Even-indexed images slide from left, odd from right. Creates visual rhythm as the user scrolls.

---

## Re-triggering Animations

Sometimes you want animations to replay when scrolling back:

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      // Entering: play forward
      anime({
        targets: entry.target,
        opacity: [0, 1],
        translateY: [30, 0],
        duration: 600,
        easing: 'easeOutCubic',
      });
    } else {
      // Leaving: reset (so it can animate again)
      entry.target.style.opacity = '0';
      entry.target.style.transform = 'translateY(30px)';
    }
    // Don't unobserve — keep watching
  });
}, { threshold: 0.2 });
```

For the Lumina site, Theo prefers one-shot reveals: "Animate once. After that, it's just content. Re-triggering feels like a gimmick."

---

## Scroll Progress Indicator

A thin progress bar at the top showing how far down the page the user is:

```javascript
const progressBar = document.querySelector('.scroll-progress');

window.addEventListener('scroll', () => {
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = window.scrollY / scrollHeight;
  progressBar.style.transform = `scaleX(${progress})`;
}, { passive: true });
```

```css
.scroll-progress {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #c8a864;
  transform: scaleX(0);
  transform-origin: left;
  z-index: 1000;
}
```

No Anime.js needed — CSS transform is enough for a simple progress bar. But if you want eased scroll progress (smoothed):

```javascript
const state = { progress: 0 };

window.addEventListener('scroll', () => {
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
  const target = window.scrollY / scrollHeight;

  anime({
    targets: state,
    progress: target,
    duration: 300,
    easing: 'easeOutQuad',
    update: () => {
      progressBar.style.transform = `scaleX(${state.progress})`;
    },
  });
}, { passive: true });
```

The progress bar smoothly catches up to the scroll position instead of jumping.

---

## What You Learned

- **IntersectionObserver** — detect when elements enter the viewport
- **threshold** — how much must be visible to trigger
- **rootMargin** — offset the trigger zone
- **One-shot reveals** — unobserve after animating
- **Staggered reveals** — observe container, stagger children
- **Scroll-scrubbed** — tie animation progress to scroll position
- **Performance** — passive listeners, rAF throttle
- **Reusable system** — ScrollReveal class for the whole site
- **Alternating directions** — visual rhythm with index-based logic
- **Progress indicator** — scroll position visualization

The site comes alive as you scroll. Each section reveals with intention. The watch assembly scrubs with scroll position. Nothing animates until it's seen.

But scroll isn't the only interaction. Buttons need hover states. Cards need click feedback. The hamburger menu needs to respond to taps. That's event-driven animation.

---

[← Chapter 10: Controls](chapter-10-controls.md) | [Chapter 12: Event-Driven Animation →](chapter-12-event-driven.md)
