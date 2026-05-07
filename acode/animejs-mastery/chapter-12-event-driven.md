# Chapter 12: Button Hover — Event-Driven Animation

[← Chapter 11: Scroll Animation](chapter-11-scroll-animation.md) | [Chapter 13: SVG Morphing →](chapter-13-svg-morphing.md)

---

## The Brief

Mika's interaction spec:

> "The 'Explore Collection' button: on hover, it scales up slightly, the background shifts to gold, and a subtle glow appears. On click, it pulses inward (like being pressed) then springs back. On mobile, the tap feedback should be faster."

Every interactive element needs motion feedback. Hover, click, focus, drag — each event can trigger an animation that communicates state.

---

## Hover: mouseenter + mouseleave

```javascript
const button = document.querySelector('.cta-button');

button.addEventListener('mouseenter', () => {
  anime({
    targets: button,
    scale: 1.05,
    duration: 300,
    easing: 'easeOutCubic',
  });
});

button.addEventListener('mouseleave', () => {
  anime({
    targets: button,
    scale: 1,
    duration: 300,
    easing: 'easeOutCubic',
  });
});
```

Simple scale on hover. But there's a problem — if the user hovers and leaves quickly, animations can stack and fight each other.

---

## The Stacking Problem

Rapid hover/leave creates competing animations:

```
mouseenter → scale to 1.05 (300ms)
mouseleave (at 100ms) → scale to 1 (300ms)
mouseenter (at 150ms) → scale to 1.05 (300ms)
// Three animations fighting over the same property!
```

Solution: remove previous animations before starting new ones:

```javascript
let currentAnimation = null;

button.addEventListener('mouseenter', () => {
  if (currentAnimation) currentAnimation.pause();
  currentAnimation = anime({
    targets: button,
    scale: 1.05,
    duration: 300,
    easing: 'easeOutCubic',
  });
});

button.addEventListener('mouseleave', () => {
  if (currentAnimation) currentAnimation.pause();
  currentAnimation = anime({
    targets: button,
    scale: 1,
    duration: 300,
    easing: 'easeOutCubic',
  });
});
```

Pausing the previous animation before starting a new one prevents conflicts. The new animation picks up from wherever the element currently is.

---

## The Complete Button Interaction

```html
<button class="cta-button">
  <span class="btn-text">Explore Collection</span>
  <span class="btn-glow"></span>
</button>
```

```css
.cta-button {
  position: relative;
  padding: 16px 40px;
  background: transparent;
  border: 1px solid #c8a864;
  color: #c8a864;
  font-size: 0.875rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  cursor: pointer;
  overflow: hidden;
}

.btn-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(200, 168, 100, 0.15), transparent 70%);
  opacity: 0;
  pointer-events: none;
}
```

```javascript
const btn = document.querySelector('.cta-button');
const glow = btn.querySelector('.btn-glow');
let hoverAnim = null;

// Hover in
btn.addEventListener('mouseenter', () => {
  if (hoverAnim) hoverAnim.pause();
  hoverAnim = anime.timeline({ easing: 'easeOutCubic' })
    .add({
      targets: btn,
      scale: 1.03,
      borderColor: '#e0c878',
      duration: 300,
    }, 0)
    .add({
      targets: glow,
      opacity: [0, 1],
      scale: [0.8, 1],
      duration: 400,
    }, 0);
});

// Hover out
btn.addEventListener('mouseleave', () => {
  if (hoverAnim) hoverAnim.pause();
  hoverAnim = anime.timeline({ easing: 'easeOutCubic' })
    .add({
      targets: btn,
      scale: 1,
      borderColor: '#c8a864',
      duration: 300,
    }, 0)
    .add({
      targets: glow,
      opacity: 0,
      duration: 200,
    }, 0);
});

// Click
btn.addEventListener('mousedown', () => {
  anime({
    targets: btn,
    scale: 0.97,
    duration: 100,
    easing: 'easeInQuad',
  });
});

btn.addEventListener('mouseup', () => {
  anime({
    targets: btn,
    scale: 1.03,  // Back to hover state
    duration: 400,
    easing: 'easeOutElastic(1, 0.5)',  // Spring back
  });
});
```

Three states: rest (scale 1), hover (scale 1.03 + glow), pressed (scale 0.97). The spring on release gives satisfying feedback.

---

## Ripple Effect

A Material Design-style ripple on click:

```javascript
btn.addEventListener('click', (e) => {
  // Create ripple element
  const ripple = document.createElement('span');
  ripple.classList.add('ripple');

  // Position at click point
  const rect = btn.getBoundingClientRect();
  ripple.style.left = `${e.clientX - rect.left}px`;
  ripple.style.top = `${e.clientY - rect.top}px`;

  btn.appendChild(ripple);

  // Animate
  anime({
    targets: ripple,
    scale: [0, 4],
    opacity: [0.4, 0],
    duration: 600,
    easing: 'easeOutQuad',
    complete: () => ripple.remove(),
  });
});
```

```css
.ripple {
  position: absolute;
  width: 50px;
  height: 50px;
  background: rgba(200, 168, 100, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(0);
  pointer-events: none;
}
```

The ripple spawns at the click position, expands, fades, and removes itself. Clean.

---

## Card Hover Interactions

Product cards with lift + shadow on hover:

```javascript
document.querySelectorAll('.product-card').forEach(card => {
  let anim = null;

  card.addEventListener('mouseenter', () => {
    if (anim) anim.pause();
    anim = anime({
      targets: card,
      translateY: -8,
      scale: 1.02,
      boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
      duration: 300,
      easing: 'easeOutCubic',
    });
  });

  card.addEventListener('mouseleave', () => {
    if (anim) anim.pause();
    anim = anime({
      targets: card,
      translateY: 0,
      scale: 1,
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      duration: 300,
      easing: 'easeOutCubic',
    });
  });
});
```

Cards lift off the page on hover. The shadow deepens to reinforce the elevation metaphor.

---

## Focus States (Accessibility)

Don't forget keyboard users:

```javascript
btn.addEventListener('focus', () => {
  anime({
    targets: btn,
    boxShadow: '0 0 0 3px rgba(200, 168, 100, 0.4)',
    duration: 200,
    easing: 'easeOutQuad',
  });
});

btn.addEventListener('blur', () => {
  anime({
    targets: btn,
    boxShadow: '0 0 0 0px rgba(200, 168, 100, 0)',
    duration: 200,
    easing: 'easeOutQuad',
  });
});
```

A focus ring that animates in — visible for keyboard navigation, smooth like everything else.

---

## Chaining Event Animations

A notification that slides in, waits, then slides out:

```javascript
function showNotification(message) {
  const notification = document.querySelector('.notification');
  notification.textContent = message;

  // Slide in
  anime.timeline({ easing: 'cubicBezier(0.16, 1, 0.3, 1)' })
    .add({
      targets: notification,
      translateX: [300, 0],
      opacity: [0, 1],
      duration: 500,
    })
    .add({
      targets: notification,
      translateX: [0, 300],
      opacity: [1, 0],
      duration: 400,
      easing: 'easeInCubic',
    }, '+=3000');  // Wait 3 seconds then exit
}
```

Enter → pause → exit. One timeline handles the full lifecycle.

---

## Debouncing Rapid Events

For events that fire rapidly (resize, input), debounce:

```javascript
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// Animate search results as user types
const searchInput = document.querySelector('.search-input');
const results = document.querySelector('.search-results');

searchInput.addEventListener('input', debounce(() => {
  // Fetch results...
  // Then animate them in
  anime({
    targets: '.search-result',
    opacity: [0, 1],
    translateY: [10, 0],
    delay: anime.stagger(50),
    duration: 300,
    easing: 'easeOutCubic',
  });
}, 300));
```

---

## Touch Events (Mobile)

Mobile needs faster feedback — no 300ms hover delay:

```javascript
// Detect touch device
const isTouch = 'ontouchstart' in window;

if (isTouch) {
  btn.addEventListener('touchstart', () => {
    anime({
      targets: btn,
      scale: 0.97,
      duration: 80,  // Faster than mouse
      easing: 'easeInQuad',
    });
  });

  btn.addEventListener('touchend', () => {
    anime({
      targets: btn,
      scale: 1,
      duration: 300,
      easing: 'easeOutElastic(1, 0.6)',
    });
  });
} else {
  // Mouse events (from earlier)
}
```

Touch feedback should be near-instant (80ms) to feel responsive. The spring on release can be longer — it plays after the finger lifts.

---

## Animation Cleanup

When elements are removed or components unmount, clean up:

```javascript
class AnimatedButton {
  constructor(el) {
    this.el = el;
    this.animations = [];
    this.bindEvents();
  }

  bindEvents() {
    this.handleEnter = () => this.onEnter();
    this.handleLeave = () => this.onLeave();
    this.el.addEventListener('mouseenter', this.handleEnter);
    this.el.addEventListener('mouseleave', this.handleLeave);
  }

  onEnter() {
    this.killAll();
    this.animations.push(anime({
      targets: this.el,
      scale: 1.03,
      duration: 300,
      easing: 'easeOutCubic',
    }));
  }

  onLeave() {
    this.killAll();
    this.animations.push(anime({
      targets: this.el,
      scale: 1,
      duration: 300,
      easing: 'easeOutCubic',
    }));
  }

  killAll() {
    this.animations.forEach(a => a.pause());
    this.animations = [];
  }

  destroy() {
    this.killAll();
    this.el.removeEventListener('mouseenter', this.handleEnter);
    this.el.removeEventListener('mouseleave', this.handleLeave);
  }
}
```

Always provide a `destroy()` method for cleanup. Especially important in SPAs where elements come and go.

---

## What You Learned

- **mouseenter/mouseleave** — hover animations
- **Animation stacking** — pause previous before starting new
- **Multi-property hover** — scale + glow + border in timeline
- **Click feedback** — press down (scale 0.97) + spring release
- **Ripple effect** — spawn, expand, fade, remove
- **Card interactions** — lift + shadow elevation
- **Focus states** — animated focus rings for accessibility
- **Chaining** — enter → wait → exit in one timeline
- **Debouncing** — prevent animation spam on rapid events
- **Touch** — faster feedback for mobile
- **Cleanup** — pause animations, remove listeners on destroy

Every interaction has motion feedback. Hover lifts. Click presses. Focus glows. The site feels responsive and alive.

Next: the hamburger menu icon that morphs into an X. SVG path morphing.

---

[← Chapter 11: Scroll Animation](chapter-11-scroll-animation.md) | [Chapter 13: SVG Morphing →](chapter-13-svg-morphing.md)
