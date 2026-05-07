# Chapter 20: The Client Presentation — Animation System

[← Chapter 19: Accessibility](chapter-19-accessibility.md) | [Chapter 0: Overview →](chapter-00-overview.md)

---

## The Moment

Two weeks. From "what's Anime.js?" to a complete animation system for a luxury watchmaker's site. The client presentation is in one hour.

Theo gathers the team:

> "Walk me through what we're presenting. Not the code — the system. How does the motion work as a whole? What are the rules? What's the language?"

---

## The Animation System

A design system has typography, color, and spacing tokens. An animation system has motion tokens:

```javascript
// motion-system.js — The Lumina Animation System

// ─── EASING TOKENS ───────────────────────────────────────────
export const EASING = {
  // Brand: mechanical precision
  mechanical: 'cubicBezier(0.4, 0, 0.2, 1)',

  // Entrances: controlled reveal
  enter: 'cubicBezier(0.16, 1, 0.3, 1)',

  // Exits: gathering momentum
  exit: 'cubicBezier(0.4, 0, 1, 1)',

  // Subtle: barely perceptible
  subtle: 'easeOutSine',

  // Linear: for opacity only
  linear: 'linear',
};

// ─── DURATION TOKENS ─────────────────────────────────────────
export const DURATION = {
  instant: 100,     // Micro-feedback
  fast: 200,        // State changes
  normal: 400,      // Standard transitions
  slow: 800,        // Entrances
  dramatic: 1200,   // Hero elements
};

// ─── DISTANCE TOKENS ─────────────────────────────────────────
export const DISTANCE = {
  subtle: 10,       // Barely moves
  normal: 20,       // Standard entrance
  far: 40,          // Dramatic entrance
  hero: 60,         // Hero elements only
};

// ─── STAGGER TOKENS ──────────────────────────────────────────
export const STAGGER = {
  tight: 50,        // Fast cascade
  normal: 80,       // Standard cascade
  relaxed: 120,     // Deliberate cascade
  dramatic: 200,    // One-by-one reveal
};

// ─── SPRING TOKENS ───────────────────────────────────────────
export const SPRING = {
  // Heavy, precise (brand default)
  mechanical: 'spring(2, 200, 20, 0)',

  // Snappy feedback
  button: 'spring(1, 300, 25, 0)',

  // Controlled open
  panel: 'spring(1, 150, 18, 0)',
};
```

---

## Naming Conventions

Every animation has a name that describes its purpose, not its implementation:

```javascript
// ❌ Named by implementation
function fadeInSlideUp() { ... }
function scaleAndRotate() { ... }

// ✅ Named by purpose
function revealHero() { ... }
function assembleWatch() { ... }
function cascadeNavigation() { ... }
function countSpecs() { ... }
function traceBezel() { ... }
```

The name tells you what it does for the user, not what CSS properties change.

---

## The Animation Registry

All page animations registered in one place:

```javascript
// animations/index.js
import { revealHero } from './hero';
import { assembleWatch } from './watch';
import { cascadeNavigation } from './navigation';
import { countSpecs } from './specs';
import { revealSections } from './scroll-reveals';
import { traceBezel } from './bezel';

export class AnimationOrchestrator {
  constructor(motionPreference) {
    this.motion = motionPreference;
    this.animations = new Map();
    this.scrollReveals = null;
  }

  init() {
    if (this.motion.isNone) {
      this.showAllContent();
      return;
    }

    // Page load sequence
    this.animations.set('hero', revealHero(this.motion));
    this.animations.set('navigation', cascadeNavigation(this.motion));

    // Scroll-triggered
    this.scrollReveals = revealSections(this.motion);

    // Interactive
    if (this.motion.isFull) {
      this.animations.set('bezel', traceBezel());
    }
  }

  async playIntro() {
    if (this.motion.isNone) return;

    const hero = this.animations.get('hero');
    const nav = this.animations.get('navigation');

    // Hero first, then nav overlaps
    hero.play();
    await new Promise(resolve => setTimeout(resolve, 600));
    nav.play();
  }

  showAllContent() {
    document.querySelectorAll('[data-animate]').forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
  }

  destroy() {
    this.animations.forEach(anim => {
      if (anim && anim.pause) anim.pause();
    });
    if (this.scrollReveals) this.scrollReveals.destroy();
  }
}
```

---

## The Complete Page Flow

```
Page Load
│
├── 0ms: Hero title fades in + slides up
├── 300ms: Hero subtitle follows
├── 600ms: Navigation cascades in
├── 800ms: Watch assembly begins (if in viewport)
│   ├── Dial fades + scales
│   ├── Hour hand rotates (overlaps)
│   ├── Minute hand rotates (overlaps)
│   ├── Strap unfolds
│   └── Brand text appears
└── Bezel light begins tracing (infinite loop)

Scroll
│
├── Specs section enters → numbers count up + rings fill
├── Heritage section enters → timeline items cascade
├── Craftsmanship section → images alternate left/right
├── Collection grid → cards ripple from center
└── CTA section → dramatic entrance

Interaction
│
├── Button hover → scale + glow
├── Button click → press + spring release + ripple
├── Card hover → lift + shadow
├── Menu toggle → hamburger morphs to X
└── Favorites → drag + spring reorder
```

---

## The Presentation Script

Theo's talking points for the client:

### 1. First Impression (0–2 seconds)

> "When the page loads, the brand name appears with precision — no bounce, no overshoot. Mechanical. Like a watch movement clicking into place. The navigation follows in a controlled cascade."

### 2. The Hero Moment (2–4 seconds)

> "The watch assembles itself. Dial, hands, strap — each piece arrives with the same mechanical precision. The overlapping timing creates momentum without chaos. It feels engineered."

### 3. Scroll Discovery

> "As you scroll, content reveals itself. Numbers count up to their values — water resistance, power reserve. The progress rings fill. Nothing animates until you reach it. Respectful of your attention."

### 4. Interaction Quality

> "Every button, every card responds to touch. Not with generic CSS transitions — with springs that have weight. The hamburger menu doesn't swap icons — it morphs. Every detail is considered."

### 5. Accessibility

> "For users who prefer reduced motion, the site simplifies to gentle fades. For those who need no motion at all, content appears instantly. The animation is enhancement, never barrier."

---

## Code Organization

```
src/
├── animations/
│   ├── system.js          # Tokens (easing, duration, distance)
│   ├── orchestrator.js    # Page-level coordination
│   ├── hero.js            # Hero section animations
│   ├── watch.js           # Watch assembly timeline
│   ├── navigation.js      # Nav cascade
│   ├── specs.js           # Number counting + rings
│   ├── scroll-reveals.js  # IntersectionObserver system
│   ├── interactions.js    # Hover, click, focus
│   ├── menu-morph.js      # Hamburger → X
│   └── bezel.js           # Motion path trace
├── hooks/
│   ├── useAnime.js        # Basic animation hook
│   ├── useTimeline.js     # Timeline hook
│   ├── useScrollReveal.js # Scroll trigger hook
│   └── useMotion.js       # Motion preference hook
└── utils/
    ├── motion-preference.js  # Preference detection + storage
    └── performance.js        # FPS monitoring, capability detection
```

Each file has a single responsibility. The orchestrator coordinates. The hooks integrate with React. The utils handle cross-cutting concerns.

---

## Principles: The Lumina Motion Language

Document these for the team:

### 1. Precision Over Personality

> Every animation uses the mechanical easing curve. No bounce. No elastic. The brand is Swiss precision.

### 2. Hierarchy Through Timing

> Important elements animate first. Supporting elements follow. The sequence communicates what matters.

### 3. Overlap Creates Momentum

> Sequential animations feel slow. Overlapping animations feel dynamic. Use `-=200` to `-=400` offsets.

### 4. Opacity is Linear

> Human perception of transparency is non-linear. Always use `easing: 'linear'` for opacity. Let the movement carry the personality.

### 5. Less on Mobile

> Reduce distance, reduce duration, reduce complexity. Mobile users are often in motion themselves — competing animation is noise.

### 6. Respect the User

> `prefers-reduced-motion` is not optional. It's a requirement. The site works without animation.

### 7. Animation is Communication

> If you can't explain why something moves, it shouldn't move. Every animation answers: "why is this moving?"

---

## The Client's Reaction

The presentation ends. The client — a Swiss watchmaker who has spent 40 years obsessing over precision — watches the site one more time on their iPad.

A long pause.

> "The hour hand. When it rotates into position — it decelerates like our actual caliber 3255 movement. How did you know?"

Theo smiles. You smile. Mika smiles.

> "The site feels like our watches. Precise. Intentional. Every movement has purpose."

They sign off. The site ships.

---

## What You Built

| Feature | Technique | Chapter |
|---|---|---|
| Hero entrance | Basic animation, easing | 1, 2 |
| Per-property timing | Property parameters | 3 |
| Nav cascade | Stagger | 4 |
| Loading dots | Loop, alternate, autoplay | 5 |
| Watch assembly | Timeline, offsets | 6 |
| Counting numbers | Value animation, round | 7 |
| Progress rings | SVG stroke-dashoffset | 8 |
| Bezel light trace | Motion path | 9 |
| Presentation scrubber | Controls, seek | 10 |
| Scroll reveals | IntersectionObserver | 11 |
| Button interactions | Event-driven, ripple | 12 |
| Menu morph | SVG path morphing | 13 |
| Drag reorder | Spring physics | 14 |
| Mobile adaptation | Responsive, reduced motion | 15 |
| iPad performance | GPU compositing | 16 |
| React integration | Refs, hooks, cleanup | 17 |
| Comp matching | Timing sheets, comparison | 18 |
| Accessibility | Three-tier motion system | 19 |
| Animation system | Tokens, naming, orchestration | 20 |

---

## What's Next

The Lumina project is done. But the skills transfer:

- **E-commerce**: product image reveals, cart animations, checkout progress
- **SaaS dashboards**: chart animations, data transitions, notification toasts
- **Marketing sites**: scroll storytelling, parallax, hero sequences
- **Mobile apps**: page transitions, gesture feedback, loading states
- **Games**: UI animations, score counters, achievement reveals

14KB. No dependencies. The entire web animation toolkit in one library.

---

## The Final Rule

Theo's parting wisdom:

> "The best animation is the one you don't notice. It doesn't draw attention to itself — it draws attention to the content. When someone says 'that site feels premium,' they're not talking about the animation. They're talking about the experience the animation created."

> "Make it move. Make it mean something. Make it invisible."

---

[← Chapter 19: Accessibility](chapter-19-accessibility.md) | [Chapter 0: Overview →](chapter-00-overview.md)
