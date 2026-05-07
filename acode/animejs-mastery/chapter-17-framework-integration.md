# Chapter 17: Integrate with React Components — Framework Integration

[← Chapter 16: Performance](chapter-16-performance.md) | [Chapter 18: Design Handoff →](chapter-18-design-handoff.md)

---

## The Problem

The Lumina site is built with React (Next.js). Your vanilla JS animations work in isolation, but in React:

- DOM elements mount and unmount — you can't query them before they exist
- Re-renders can reset animation state
- Component cleanup must stop running animations (memory leaks)
- Refs replace `document.querySelector`

Theo: "The animations need to live inside components. Not in a separate script file. Each component owns its motion."

---

## The Basic Pattern: useRef + useEffect

```jsx
import { useRef, useEffect } from 'react';
import anime from 'animejs';

function HeroTitle({ text }) {
  const titleRef = useRef(null);

  useEffect(() => {
    const animation = anime({
      targets: titleRef.current,
      opacity: [0, 1],
      translateY: [30, 0],
      duration: 800,
      easing: 'easeOutCubic',
    });

    // Cleanup: stop animation if component unmounts
    return () => animation.pause();
  }, []);  // Empty deps = run once on mount

  return (
    <h1 ref={titleRef} style={{ opacity: 0 }}>
      {text}
    </h1>
  );
}
```

Key points:
1. `useRef` gives you a stable reference to the DOM element
2. `useEffect` runs after the component mounts (DOM exists)
3. Return a cleanup function that pauses the animation
4. Initial style `opacity: 0` prevents flash before animation

---

## Multiple Refs

For animating multiple elements within a component:

```jsx
function SpecCards({ specs }) {
  const containerRef = useRef(null);
  const cardRefs = useRef([]);

  useEffect(() => {
    const animation = anime({
      targets: cardRefs.current,
      opacity: [0, 1],
      translateY: [30, 0],
      delay: anime.stagger(100),
      duration: 600,
      easing: 'cubicBezier(0.16, 1, 0.3, 1)',
    });

    return () => animation.pause();
  }, []);

  return (
    <section ref={containerRef} className="specs">
      {specs.map((spec, i) => (
        <div
          key={spec.id}
          ref={el => cardRefs.current[i] = el}
          className="spec-card"
          style={{ opacity: 0 }}
        >
          <span className="spec-value">{spec.value}</span>
          <span className="spec-label">{spec.label}</span>
        </div>
      ))}
    </section>
  );
}
```

`cardRefs.current` is an array of DOM elements — pass it directly to `targets`.

---

## Custom Hook: useAnime

Extract the pattern into a reusable hook:

```jsx
import { useRef, useEffect, useCallback } from 'react';
import anime from 'animejs';

function useAnime(config, deps = []) {
  const targetRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    if (!targetRef.current) return;

    animationRef.current = anime({
      targets: targetRef.current,
      ...config,
    });

    return () => {
      if (animationRef.current) {
        animationRef.current.pause();
      }
    };
  }, deps);

  const play = useCallback(() => animationRef.current?.play(), []);
  const pause = useCallback(() => animationRef.current?.pause(), []);
  const restart = useCallback(() => animationRef.current?.restart(), []);
  const seek = useCallback((time) => animationRef.current?.seek(time), []);

  return { ref: targetRef, play, pause, restart, seek, animation: animationRef };
}

// Usage
function AnimatedCard({ children }) {
  const { ref } = useAnime({
    opacity: [0, 1],
    translateY: [20, 0],
    duration: 600,
    easing: 'easeOutCubic',
  });

  return <div ref={ref} style={{ opacity: 0 }}>{children}</div>;
}
```

---

## Timeline Hook

For complex sequences:

```jsx
function useTimeline(config = {}) {
  const timelineRef = useRef(null);
  const refs = useRef({});

  useEffect(() => {
    timelineRef.current = anime.timeline({
      autoplay: false,
      ...config,
    });

    return () => {
      if (timelineRef.current) {
        timelineRef.current.pause();
      }
    };
  }, []);

  const addRef = useCallback((name) => {
    if (!refs.current[name]) {
      refs.current[name] = { current: null };
    }
    return (el) => { refs.current[name].current = el; };
  }, []);

  const build = useCallback((builder) => {
    if (timelineRef.current) {
      builder(timelineRef.current, refs.current);
    }
  }, []);

  const play = useCallback(() => timelineRef.current?.play(), []);
  const pause = useCallback(() => timelineRef.current?.pause(), []);
  const seek = useCallback((t) => timelineRef.current?.seek(t), []);

  return { addRef, build, play, pause, seek, timeline: timelineRef };
}

// Usage
function WatchAssembly() {
  const { addRef, build, play } = useTimeline({
    easing: 'cubicBezier(0.4, 0, 0.2, 1)',
  });

  useEffect(() => {
    build((tl, refs) => {
      tl.add({ targets: refs.dial.current, opacity: [0, 1], scale: [0.85, 1], duration: 600 })
        .add({ targets: refs.hourHand.current, rotate: [0, 210], duration: 1000 }, 400)
        .add({ targets: refs.minuteHand.current, rotate: [0, 60], duration: 800 }, 800);
    });
    play();
  }, []);

  return (
    <div className="watch">
      <div ref={addRef('dial')} className="dial" style={{ opacity: 0 }} />
      <div ref={addRef('hourHand')} className="hour-hand" />
      <div ref={addRef('minuteHand')} className="minute-hand" />
    </div>
  );
}
```

---

## Scroll Reveal Hook

Combining IntersectionObserver with React:

```jsx
function useScrollReveal(config = {}) {
  const ref = useRef(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (!ref.current || hasAnimated.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated.current) {
          hasAnimated.current = true;
          anime({
            targets: ref.current,
            opacity: [0, 1],
            translateY: [30, 0],
            duration: 800,
            easing: 'cubicBezier(0.16, 1, 0.3, 1)',
            ...config,
          });
          observer.disconnect();
        }
      },
      { threshold: 0.2 }
    );

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return ref;
}

// Usage
function FeatureSection({ title, description }) {
  const ref = useScrollReveal({ delay: 200 });

  return (
    <section ref={ref} style={{ opacity: 0 }}>
      <h2>{title}</h2>
      <p>{description}</p>
    </section>
  );
}
```

---

## Handling Re-renders

React re-renders can interfere with animations. Protect against this:

```jsx
function Counter({ target }) {
  const displayRef = useRef(null);
  const animationRef = useRef(null);
  const counterRef = useRef({ value: 0 });

  useEffect(() => {
    // Cancel previous animation if target changes
    if (animationRef.current) {
      animationRef.current.pause();
    }

    animationRef.current = anime({
      targets: counterRef.current,
      value: target,
      duration: 2000,
      easing: 'easeOutExpo',
      round: 1,
      update: () => {
        if (displayRef.current) {
          displayRef.current.textContent = counterRef.current.value.toLocaleString();
        }
      },
    });

    return () => animationRef.current?.pause();
  }, [target]);  // Re-run when target changes

  return <span ref={displayRef}>0</span>;
}
```

When `target` prop changes, the previous animation is cancelled and a new one starts from the current value. No jump, smooth transition.

---

## Respecting Reduced Motion in React

```jsx
function useReducedMotion() {
  const [prefersReduced, setPrefersReduced] = useState(
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e) => setPrefersReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  return prefersReduced;
}

// Usage
function AnimatedHero({ title }) {
  const ref = useRef(null);
  const prefersReduced = useReducedMotion();

  useEffect(() => {
    if (prefersReduced) {
      // Instant — no animation
      if (ref.current) ref.current.style.opacity = '1';
      return;
    }

    const anim = anime({
      targets: ref.current,
      opacity: [0, 1],
      translateY: [30, 0],
      duration: 800,
      easing: 'easeOutCubic',
    });

    return () => anim.pause();
  }, [prefersReduced]);

  return <h1 ref={ref} style={{ opacity: prefersReduced ? 1 : 0 }}>{title}</h1>;
}
```

---

## Cleanup Patterns

### Component Unmount

```jsx
useEffect(() => {
  const anim = anime({ targets: ref.current, ... });
  return () => {
    anim.pause();
    // Reset styles if needed
    if (ref.current) {
      ref.current.style.transform = '';
      ref.current.style.opacity = '';
    }
  };
}, []);
```

### Route Changes (Next.js)

```jsx
import { useRouter } from 'next/router';

function PageTransition({ children }) {
  const containerRef = useRef(null);
  const router = useRouter();

  useEffect(() => {
    // Animate in on mount
    anime({
      targets: containerRef.current,
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 500,
      easing: 'easeOutCubic',
    });
  }, [router.pathname]);

  return <div ref={containerRef}>{children}</div>;
}
```

---

## Common React + Anime.js Mistakes

### 1. Querying DOM directly

```jsx
// ❌ Don't use querySelector in React
useEffect(() => {
  anime({ targets: '.hero-title', ... });
}, []);

// ✅ Use refs
useEffect(() => {
  anime({ targets: titleRef.current, ... });
}, []);
```

### 2. Missing cleanup

```jsx
// ❌ Memory leak — animation keeps running after unmount
useEffect(() => {
  anime({ targets: ref.current, loop: true, ... });
}, []);

// ✅ Cleanup stops the animation
useEffect(() => {
  const anim = anime({ targets: ref.current, loop: true, ... });
  return () => anim.pause();
}, []);
```

### 3. Animating during render

```jsx
// ❌ Animation in render body (runs every render!)
function Bad() {
  anime({ targets: '.box', ... });
  return <div className="box" />;
}

// ✅ Animation in useEffect (runs once after mount)
function Good() {
  const ref = useRef(null);
  useEffect(() => {
    anime({ targets: ref.current, ... });
  }, []);
  return <div ref={ref} />;
}
```

---

## What You Learned

- **useRef** — stable DOM references for animation targets
- **useEffect** — run animations after mount, cleanup on unmount
- **Cleanup** — always pause animations in the return function
- **Custom hooks** — useAnime, useTimeline, useScrollReveal
- **Multiple refs** — array of refs for staggered animations
- **Re-render safety** — cancel and restart on prop changes
- **Reduced motion** — useReducedMotion hook
- **No querySelector** — always use refs in React
- **No render-time animation** — always in useEffect

Anime.js works seamlessly with React when you follow the ref + effect + cleanup pattern. Each component owns its animations. Cleanup prevents leaks. Hooks make it reusable.

Next: translating Mika's After Effects comp into code — timing sheets, easing curves, and frame-by-frame matching.

---

[← Chapter 16: Performance](chapter-16-performance.md) | [Chapter 18: Design Handoff →](chapter-18-design-handoff.md)
