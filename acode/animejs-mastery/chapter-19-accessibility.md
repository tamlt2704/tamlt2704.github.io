# Chapter 19: Accessibility — Motion Makes Me Dizzy

[← Chapter 18: Design Handoff](chapter-18-design-handoff.md) | [Chapter 20: The Final Presentation →](chapter-20-animation-system.md)

---

## The Problem

During QA, the accessibility consultant flags the site:

> "The parallax scrolling triggers my vestibular disorder. The auto-playing animations are distracting for users with ADHD. The counting numbers are unreadable by screen readers during animation. The site fails WCAG 2.1 Success Criterion 2.3.3 (Animation from Interactions)."

Theo: "We can't remove the animations — they're the product. But we need to make the site usable for everyone. What are our options?"

---

## WCAG Requirements for Animation

### 2.3.3 Animation from Interactions (AAA)

> Motion animation triggered by interaction can be disabled, unless the animation is essential to the functionality or the information being conveyed.

### 2.2.2 Pause, Stop, Hide (A)

> For any auto-updating information that starts automatically and is presented in parallel with other content, there is a mechanism to pause, stop, or hide it.

### What This Means in Practice

1. Respect `prefers-reduced-motion`
2. Provide a manual toggle for users who haven't set the OS preference
3. Auto-playing animations must be pausable
4. Animation must not be the only way to convey information

---

## The Three-Tier Approach

```
Tier 1: Full Motion (default)
├── All animations play
├── Scroll-driven effects active
├── Spring physics, motion paths
└── For users who haven't indicated a preference

Tier 2: Reduced Motion (prefers-reduced-motion: reduce)
├── No parallax or scroll-driven animation
├── Simple fades only (opacity transitions)
├── No movement (translateX/Y disabled)
├── Shorter durations (max 200ms)
└── For users with vestibular disorders

Tier 3: No Motion (manual toggle)
├── All animations disabled
├── Instant state changes
├── Static content only
└── For users who need zero motion
```

---

## Implementing the Motion Preference System

```javascript
class MotionPreference {
  constructor() {
    this.level = this.detect();
    this.listeners = [];
    this.watchSystemPreference();
  }

  detect() {
    // Check manual override first (stored in localStorage)
    const manual = localStorage.getItem('motion-preference');
    if (manual) return manual;  // 'full', 'reduced', 'none'

    // Fall back to system preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return 'reduced';
    }

    return 'full';
  }

  set(level) {
    this.level = level;
    localStorage.setItem('motion-preference', level);
    this.notify();
  }

  watchSystemPreference() {
    window.matchMedia('(prefers-reduced-motion: reduce)')
      .addEventListener('change', (e) => {
        // Only update if no manual override
        if (!localStorage.getItem('motion-preference')) {
          this.level = e.matches ? 'reduced' : 'full';
          this.notify();
        }
      });
  }

  onChange(callback) {
    this.listeners.push(callback);
  }

  notify() {
    this.listeners.forEach(cb => cb(this.level));
  }

  get isFull() { return this.level === 'full'; }
  get isReduced() { return this.level === 'reduced'; }
  get isNone() { return this.level === 'none'; }
}

const motion = new MotionPreference();
```

---

## The Motion Toggle UI

```html
<div class="motion-toggle" role="group" aria-label="Animation preference">
  <button
    class="motion-option"
    data-level="full"
    aria-pressed="true"
  >Full Motion</button>
  <button
    class="motion-option"
    data-level="reduced"
    aria-pressed="false"
  >Reduced</button>
  <button
    class="motion-option"
    data-level="none"
    aria-pressed="false"
  >No Motion</button>
</div>
```

```javascript
document.querySelectorAll('.motion-option').forEach(btn => {
  btn.addEventListener('click', () => {
    const level = btn.dataset.level;
    motion.set(level);

    // Update aria-pressed
    document.querySelectorAll('.motion-option').forEach(b => {
      b.setAttribute('aria-pressed', b.dataset.level === level);
    });
  });
});
```

Place this in the site footer or settings panel. Users can override regardless of their OS setting.

---

## Adaptive Animation Function

Replace all `anime()` calls with a motion-aware wrapper:

```javascript
function animate(config) {
  if (motion.isNone) {
    // Tier 3: instant state change
    applyFinalState(config);
    if (config.complete) config.complete();
    return null;
  }

  if (motion.isReduced) {
    // Tier 2: simple fade, no movement
    return anime({
      targets: config.targets,
      opacity: config.opacity || [0, 1],
      duration: Math.min(config.duration || 200, 200),
      easing: 'linear',
      complete: config.complete,
    });
  }

  // Tier 1: full animation
  return anime(config);
}

function applyFinalState(config) {
  const targets = typeof config.targets === 'string'
    ? document.querySelectorAll(config.targets)
    : [config.targets].flat();

  targets.forEach(el => {
    if (!el) return;
    el.style.opacity = '1';
    el.style.transform = 'none';
  });
}
```

Now every animation call automatically adapts:

```javascript
// This single call works for all three tiers
animate({
  targets: '.hero-title',
  opacity: [0, 1],
  translateY: [30, 0],
  duration: 800,
  easing: 'easeOutCubic',
});
// Full: fades + slides over 800ms
// Reduced: fades only over 200ms
// None: instantly visible
```

---

## Screen Reader Considerations

### Animated Numbers

Screen readers can't track rapidly changing text:

```javascript
// ❌ Screen reader announces every intermediate value
anime({
  targets: counter,
  value: 300,
  round: 1,
  update: () => {
    el.textContent = counter.value;  // "1" "2" "3" ... "300"
  },
});

// ✅ Use aria-live with debouncing
el.setAttribute('aria-live', 'off');  // Silence during animation

anime({
  targets: counter,
  value: 300,
  round: 1,
  update: () => {
    el.textContent = counter.value.toLocaleString();
  },
  begin: () => {
    el.setAttribute('aria-live', 'off');
  },
  complete: () => {
    el.setAttribute('aria-live', 'polite');
    // Now screen reader announces the final value
  },
});
```

Or provide the final value in a visually hidden element:

```html
<div class="spec-card">
  <span class="spec-value" aria-hidden="true">0</span>
  <span class="sr-only">300 meters water resistance</span>
</div>
```

The animated number is decorative (`aria-hidden`). The real content is in the screen-reader-only span.

---

## Focus Management During Animation

Don't move focus during animations. Don't animate elements that have focus:

```javascript
// ❌ Animating a focused element can disorient keyboard users
anime({
  targets: document.activeElement,
  translateX: 200,
  duration: 500,
});

// ✅ Skip animation on focused elements
function animateElement(el, config) {
  if (el === document.activeElement) {
    applyFinalState({ targets: el, ...config });
    return;
  }
  return anime({ targets: el, ...config });
}
```

---

## Pause Auto-Playing Animations

The loading dots and bezel light loop forever. Provide a pause mechanism:

```javascript
const autoPlayAnimations = [];

// Register auto-playing animations
const loadingAnim = anime({
  targets: '.loading-dot',
  scale: [1, 1.5],
  loop: true,
  direction: 'alternate',
  duration: 500,
});
autoPlayAnimations.push(loadingAnim);

// Global pause button
document.querySelector('.pause-animations').addEventListener('click', () => {
  autoPlayAnimations.forEach(anim => anim.pause());
});

// Or pause when page is not visible (saves battery too)
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    autoPlayAnimations.forEach(anim => anim.pause());
  } else if (motion.isFull) {
    autoPlayAnimations.forEach(anim => anim.play());
  }
});
```

---

## Avoiding Seizure Triggers

WCAG 2.3.1: No content flashes more than 3 times per second.

```javascript
// ❌ Dangerous: rapid flashing
anime({
  targets: '.alert',
  opacity: [0, 1],
  duration: 100,  // 10 flashes per second!
  loop: true,
  direction: 'alternate',
});

// ✅ Safe: gentle pulse
anime({
  targets: '.alert',
  opacity: [0.7, 1],  // Subtle range
  duration: 1000,      // Slow cycle
  loop: true,
  direction: 'alternate',
  easing: 'easeInOutSine',
});
```

Rules:
- No flashing faster than 3Hz (333ms minimum cycle)
- Keep opacity range narrow for pulsing (0.7–1, not 0–1)
- Avoid large areas of flashing content

---

## Reduced Motion: What to Keep

Not all animation should be removed. Some motion aids comprehension:

```
KEEP (even in reduced motion):
├── Loading indicators (but simplify)
├── Progress feedback
├── State change indicators (checkbox → checked)
└── Scroll position indicators

REMOVE:
├── Parallax
├── Scroll-driven animation
├── Decorative entrances
├── Motion paths
├── Spring physics
└── Auto-playing decorative loops
```

```javascript
function animateStateChange(el, newState) {
  if (motion.isNone) {
    el.classList.toggle('active', newState);
    return;
  }

  // Even reduced motion gets a brief opacity transition
  // because it communicates state change
  anime({
    targets: el,
    opacity: newState ? 1 : 0.5,
    duration: motion.isReduced ? 150 : 300,
    easing: 'linear',
  });
}
```

---

## Testing Accessibility

### Manual Testing Checklist

- [ ] Enable "Reduce motion" in OS settings → verify site is usable
- [ ] Tab through the page → no focus traps during animation
- [ ] Screen reader (VoiceOver/NVDA) → animated content is announced correctly
- [ ] Pause all auto-playing animations → verify pause mechanism works
- [ ] No content flashes more than 3 times per second
- [ ] Motion toggle works and persists across page loads
- [ ] All animated content has a non-animated fallback

### Automated Testing

```javascript
// Test that reduced motion disables movement
test('respects reduced motion', () => {
  // Mock matchMedia
  window.matchMedia = jest.fn().mockReturnValue({
    matches: true,  // prefers-reduced-motion: reduce
    addEventListener: jest.fn(),
  });

  const motion = new MotionPreference();
  expect(motion.isReduced).toBe(true);

  // Verify no translateY in reduced mode
  const result = animate({
    targets: '.hero',
    translateY: [30, 0],
    opacity: [0, 1],
  });

  // In reduced mode, only opacity should animate
  // translateY should be skipped
});
```

---

## What You Learned

- **prefers-reduced-motion** — OS-level preference, always respect it
- **Three tiers** — full, reduced, none
- **Manual toggle** — let users override regardless of OS setting
- **Adaptive wrapper** — one function handles all tiers
- **Screen readers** — aria-live off during animation, announce final state
- **Focus management** — don't animate focused elements
- **Auto-play pause** — mechanism to stop looping animations
- **Seizure safety** — no flashing faster than 3Hz
- **What to keep** — state indicators even in reduced motion
- **Testing** — manual + automated verification

The site is now accessible. Full motion for those who want it. Reduced for those who need it. None for those who require it. Everyone gets the content. The animation is enhancement, not requirement.

One chapter left: the client presentation. Putting it all together into a cohesive animation system.

---

[← Chapter 18: Design Handoff](chapter-18-design-handoff.md) | [Chapter 20: The Final Presentation →](chapter-20-animation-system.md)
