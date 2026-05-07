# Chapter 19: Framework Integration — SVG in React and Vue

[← Ch 18: Optimization](chapter-18-optimization.md) | [Ch 20: Landing Page →](chapter-20-landing-page.md)

---

## Zara's Request

> "40+ animated SVGs scattered across the codebase. Some GSAP, some CSS, some inline styles. No consistency. Wrap them in reusable components — props for size, color, animation state."

Dani: "They need to respect motion preferences, clean up on unmount, and not re-trigger on every re-render."

---

## Inline SVG in React

```jsx
function OrbitlyLogo({ size = 24, color = 'currentColor' }) {
  return (
    <svg viewBox="0 0 100 100" width={size} height={size} role="img" aria-label="Orbitly logo">
      <path d="M 50 15 C 70 15 85 30 85 50 C 85 70 70 85 50 85 C 30 85 15 70 15 50 C 15 30 30 15 50 15"
            fill="none" stroke={color} strokeWidth="3" strokeLinecap="round"/>
      <circle cx="85" cy="50" r="5" fill={color}/>
    </svg>
  );
}
```

JSX differences: `stroke-width` → `strokeWidth`, `stroke-linecap` → `strokeLinecap`, `class` → `className`.

## GSAP in useEffect

```jsx
import { useEffect, useRef } from 'react';
import gsap from 'gsap';

function AnimatedCheckmark({ isComplete, size = 48 }) {
  const circleRef = useRef(null);
  const checkRef = useRef(null);
  const tlRef = useRef(null);

  useEffect(() => {
    const circumference = 2 * Math.PI * 20;
    gsap.set(circleRef.current, { strokeDasharray: circumference, strokeDashoffset: circumference });
    gsap.set(checkRef.current, { strokeDasharray: 30, strokeDashoffset: 30 });

    tlRef.current = gsap.timeline({ paused: true })
      .to(circleRef.current, { strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut' })
      .to(checkRef.current, { strokeDashoffset: 0, duration: 0.3, ease: 'power2.out' }, '-=0.1');

    return () => tlRef.current?.kill(); // Cleanup on unmount
  }, []);

  useEffect(() => {
    isComplete ? tlRef.current?.play() : tlRef.current?.reverse();
  }, [isComplete]);

  return (
    <svg viewBox="0 0 50 50" width={size} height={size}
         role="img" aria-label={isComplete ? 'Complete' : 'Incomplete'}>
      <circle ref={circleRef} cx="25" cy="25" r="20"
              fill="none" stroke="#10b981" strokeWidth="2" transform="rotate(-90 25 25)"/>
      <path ref={checkRef} d="M 15 25 L 22 32 L 35 19"
            fill="none" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round"/>
    </svg>
  );
}
```

---

## Framer Motion

```jsx
import { motion } from 'framer-motion';

function AnimatedIcon({ isActive }) {
  return (
    <svg viewBox="0 0 24 24" width="24" height="24">
      <motion.circle cx="12" cy="12" r="10" fill="none" stroke="#6366f1" strokeWidth="2"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: isActive ? 1 : 0 }}
        transition={{ duration: 0.6, ease: 'easeInOut' }}/>
    </svg>
  );
}
```

Framer Motion props: `pathLength` (0–1), `pathOffset`, `opacity`, `scale`, `rotate`, `x`, `y`, `fill`, `stroke`.

---

## Respecting Reduced Motion

```jsx
function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReduced(mq.matches);
    const handler = (e) => setReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);
  return reduced;
}

function AnimatedElement({ children }) {
  const ref = useRef(null);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    if (reducedMotion) { gsap.set(ref.current, { opacity: 1 }); return; }
    const anim = gsap.from(ref.current, { opacity: 0, y: 30, duration: 0.6 });
    return () => anim.kill();
  }, [reducedMotion]);

  return <div ref={ref}>{children}</div>;
}
```

---

## Cleanup Pattern

```jsx
function ParticleBackground() {
  const svgRef = useRef(null);
  const animsRef = useRef([]);

  useEffect(() => {
    svgRef.current.querySelectorAll('.particle').forEach((p, i) => {
      animsRef.current.push(gsap.to(p, {
        y: -200, opacity: 0, duration: 3 + Math.random() * 4,
        delay: Math.random() * 2, repeat: -1
      }));
    });
    return () => { animsRef.current.forEach(a => a.kill()); animsRef.current = []; };
  }, []);

  return (
    <svg ref={svgRef} viewBox="0 0 400 300" aria-hidden="true">
      {Array.from({ length: 20 }, (_, i) => (
        <circle key={i} className="particle" cx={Math.random()*400} cy={300}
                r={1+Math.random()*2} fill="#6366f1" opacity="0.3"/>
      ))}
    </svg>
  );
}
```

---

## Vue Integration

```vue
<template>
  <svg viewBox="0 0 100 100" :width="size" :height="size">
    <circle ref="circleEl" cx="50" cy="50" r="40" fill="none" :stroke="color" stroke-width="3"
            :stroke-dasharray="circumference" :stroke-dashoffset="offset"/>
  </svg>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import gsap from 'gsap';
const props = defineProps({ progress: Number, size: { default: 48 }, color: { default: '#6366f1' } });
const circumference = 2 * Math.PI * 40;
const offset = computed(() => circumference * (1 - props.progress / 100));
const circleEl = ref(null);
let anim = null;
onMounted(() => { anim = gsap.from(circleEl.value, { strokeDashoffset: circumference, duration: 1.5 }); });
onUnmounted(() => { anim?.kill(); });
</script>
```

---

## Common Mistakes

**Not killing on unmount** — GSAP continues after unmount, causing memory leaks.

**Re-triggering on every render** — use `useRef` for timeline instances.

**Using dangerouslySetInnerHTML** — inline SVG in JSX is safer and gives ref access.

---

## Exercise

Build Orbitly's animated icon library:
1. `<AnimatedIcon>` component: `name`, `size`, `color`, `animate` props
2. Three icons: checkmark (draw), spinner (rotate), bell (shake)
3. Respects `prefers-reduced-motion`
4. Cleans up on unmount
5. `trigger` prop: `'mount'`, `'hover'`, or `'manual'`

---

## Quick Reference

| Pattern | Purpose |
|---------|---------|
| `useRef` + `useEffect` | GSAP lifecycle |
| `motion.*` | Framer Motion declarative |
| `useReducedMotion()` | Accessibility hook |
| Return in useEffect | Kill on unmount |
| Store timeline in ref | Avoid re-creation |

| Lifecycle | Solution |
|-----------|----------|
| Animate on mount | `useEffect([], ...)` |
| Animate on prop | `useEffect([prop], ...)` |
| Cleanup | Return `() => anim.kill()` |
| Avoid re-trigger | `useRef` for timeline |

---

[← Ch 18: Optimization](chapter-18-optimization.md) | [Ch 20: Landing Page →](chapter-20-landing-page.md)
