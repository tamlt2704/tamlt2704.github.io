# Chapter 15: Responsive — Different on Mobile

[← Chapter 14: Spring Physics](chapter-14-spring-physics.md) | [Chapter 16: Performance →](chapter-16-performance.md)

---

## The Brief

The client tests the site on their iPad. Three problems:

1. The watch assembly animation is too complex for mobile — it janks
2. The hover interactions don't exist on touch devices
3. Their designer has vestibular issues — the motion makes them dizzy

Theo: "The site needs to work everywhere. Full animation on desktop. Simplified on tablet. Minimal on mobile. And anyone who prefers reduced motion gets instant state changes — no animation at all."

---

## prefers-reduced-motion

The most important responsive animation feature. Users who experience motion sickness or have vestibular disorders can set this OS preference:

```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

if (prefersReducedMotion.matches) {
  // No animation — instant state changes
  document.querySelectorAll('[data-animate]').forEach(el => {
    el.style.opacity = '1';
    el.style.transform = 'none';
  });
} else {
  // Full animations
  animateHero();
  animateSpecs();
  animateScrollReveals();
}
```

### Listening for Changes

Users can toggle this preference while the page is open:

```javascript
prefersReducedMotion.addEventListener('change', (e) => {
  if (e.matches) {
    // User just enabled reduced motion — stop all animations
    anime.remove('*');  // Remove all running animations
    resetAllElements();
  } else {
    // User disabled reduced motion — start animations
    initAnimations();
  }
});
```

---

## The Animation Wrapper

Create a utility that respects the preference:

```javascript
function safeAnimate(config) {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (prefersReduced) {
    // Apply final state immediately, no animation
    const targets = typeof config.targets === 'string'
      ? document.querySelectorAll(config.targets)
      : [config.targets].flat();

    targets.forEach(el => {
      if (config.opacity) el.style.opacity = Array.isArray(config.opacity) ? config.opacity[1] : config.opacity;
      if (config.translateY) el.style.transform = 'translateY(0)';
      if (config.translateX) el.style.transform = 'translateX(0)';
      if (config.scale) el.style.transform = 'scale(1)';
    });

    // Still fire complete callback
    if (config.complete) config.complete();
    return null;
  }

  return anime(config);
}

// Usage — same API, but respects preference
safeAnimate({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [30, 0],
  duration: 800,
  easing: 'easeOutCubic',
});
```

---

## Responsive Breakpoints

Different animation parameters for different screen sizes:

```javascript
function getAnimationConfig() {
  const width = window.innerWidth;

  if (width < 768) {
    // Mobile: simpler, shorter
    return {
      heroDistance: 15,      // Less movement
      heroDuration: 500,    // Faster
      staggerDelay: 50,     // Tighter stagger
      enableParallax: false,
      enableMotionPath: false,
    };
  } else if (width < 1024) {
    // Tablet: moderate
    return {
      heroDistance: 25,
      heroDuration: 700,
      staggerDelay: 70,
      enableParallax: true,
      enableMotionPath: false,
    };
  } else {
    // Desktop: full experience
    return {
      heroDistance: 30,
      heroDuration: 800,
      staggerDelay: 80,
      enableParallax: true,
      enableMotionPath: true,
    };
  }
}

const config = getAnimationConfig();

anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [config.heroDistance, 0],
  duration: config.heroDuration,
  easing: 'easeOutCubic',
});
```

Mobile gets shorter distances and faster durations. Less movement = less jank on weaker hardware.

---

## Disabling Complex Animations on Mobile

The watch assembly with motion paths is too heavy for mobile. Replace it:

```javascript
const config = getAnimationConfig();

if (config.enableMotionPath) {
  // Desktop: full assembly with motion path
  playWatchAssembly();
} else {
  // Mobile: simple fade-in of the complete watch
  anime({
    targets: '.watch-complete',
    opacity: [0, 1],
    scale: [0.95, 1],
    duration: 600,
    easing: 'easeOutCubic',
  });
}
```

Mobile users see the watch fade in as a complete image. Desktop users see the full assembly sequence. Same content, appropriate motion.

---

## Handling Resize

When the viewport changes (rotation, resize), animations may need to recalculate:

```javascript
let currentConfig = getAnimationConfig();
let resizeTimer;

window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    const newConfig = getAnimationConfig();

    // Only reinitialize if breakpoint changed
    if (newConfig.enableMotionPath !== currentConfig.enableMotionPath) {
      destroyAnimations();
      currentConfig = newConfig;
      initAnimations(currentConfig);
    }
  }, 250);  // Debounce
});
```

Don't reinitialize on every pixel change — only when crossing a breakpoint that affects animation behavior.

---

## Touch vs Mouse

Replace hover animations with appropriate touch alternatives:

```javascript
const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

function setupCardInteractions() {
  document.querySelectorAll('.product-card').forEach(card => {
    if (isTouch) {
      // Touch: tap to expand, no hover
      card.addEventListener('click', () => {
        anime({
          targets: card,
          scale: [1, 1.02, 1],
          duration: 400,
          easing: 'easeOutCubic',
        });
      });
    } else {
      // Mouse: hover to lift
      card.addEventListener('mouseenter', () => {
        anime({ targets: card, translateY: -8, scale: 1.02, duration: 300, easing: 'easeOutCubic' });
      });
      card.addEventListener('mouseleave', () => {
        anime({ targets: card, translateY: 0, scale: 1, duration: 300, easing: 'easeOutCubic' });
      });
    }
  });
}
```

---

## CSS Fallbacks

For critical animations, provide CSS fallbacks that work without JavaScript:

```css
/* Base state: visible (works without JS) */
.hero-title {
  opacity: 1;
  transform: translateY(0);
}

/* When JS is available, hide for animation */
.js-loaded .hero-title {
  opacity: 0;
  transform: translateY(30px);
}

/* Reduced motion: no transform, just instant display */
@media (prefers-reduced-motion: reduce) {
  .js-loaded .hero-title {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
```

```javascript
// Mark that JS is loaded
document.documentElement.classList.add('js-loaded');

// Then animate
anime({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [30, 0],
  duration: 800,
  easing: 'easeOutCubic',
});
```

Three layers:
1. No JS → content visible (CSS default)
2. JS + reduced motion → content visible (CSS override)
3. JS + full motion → animated entrance

---

## Animation Budget

Theo's rule for mobile: "You get 3 animations per viewport. Choose wisely."

```javascript
function getAnimationBudget() {
  const width = window.innerWidth;
  if (width < 768) return 3;   // Mobile: 3 animations visible at once
  if (width < 1024) return 5;  // Tablet: 5
  return Infinity;              // Desktop: unlimited
}

class BudgetedScrollReveal {
  constructor() {
    this.budget = getAnimationBudget();
    this.activeCount = 0;
  }

  reveal(el, config) {
    if (this.activeCount >= this.budget) {
      // Over budget: instant reveal, no animation
      el.style.opacity = '1';
      el.style.transform = 'none';
      return;
    }

    this.activeCount++;
    anime({
      targets: el,
      ...config,
      complete: () => {
        this.activeCount--;
      },
    });
  }
}
```

On mobile, only 3 elements animate simultaneously. Others appear instantly. This prevents the GPU from being overwhelmed.

---

## Testing Responsive Animation

A debug panel for development:

```javascript
function createAnimationDebugPanel() {
  const panel = document.createElement('div');
  panel.innerHTML = `
    <div style="position:fixed;bottom:10px;right:10px;background:#1a1a1a;padding:12px;border-radius:8px;font-size:12px;color:#fff;z-index:9999;">
      <label><input type="checkbox" id="debug-reduced-motion"> Simulate reduced motion</label><br>
      <label><input type="range" id="debug-width" min="320" max="1920" value="${window.innerWidth}"> Width: <span id="debug-width-val">${window.innerWidth}</span></label><br>
      <button id="debug-replay">Replay animations</button>
    </div>
  `;
  document.body.appendChild(panel);

  document.getElementById('debug-reduced-motion').addEventListener('change', (e) => {
    window.__forceReducedMotion = e.target.checked;
    // Reinitialize
  });
}

if (location.hostname === 'localhost') {
  createAnimationDebugPanel();
}
```

---

## What You Learned

- **prefers-reduced-motion** — respect user's motion preference
- **Instant fallback** — apply final state without animation
- **Change listener** — respond to preference toggle in real-time
- **Breakpoint configs** — different params for mobile/tablet/desktop
- **Disable complex animations** — motion path off on mobile
- **Touch vs mouse** — appropriate interaction patterns per device
- **CSS fallbacks** — three-layer progressive enhancement
- **Animation budget** — limit concurrent animations on weak devices
- **Resize handling** — debounced breakpoint detection
- **Debug tools** — simulate preferences during development

The site works everywhere. Full experience on desktop. Simplified on mobile. Respectful for users with motion sensitivity. Progressive enhancement, not graceful degradation.

Part 3 is complete. You can move things, coordinate things, and respond to things. Now: ship things. Performance, framework integration, design handoff, and the final presentation.

---

[← Chapter 14: Spring Physics](chapter-14-spring-physics.md) | [Chapter 16: Performance →](chapter-16-performance.md)
