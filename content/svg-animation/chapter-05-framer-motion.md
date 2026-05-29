# Chapter 5: Framer Motion — React SVG Animations

[prev: GSAP](./chapter-04-gsap.md) | [next: Lottie](./chapter-06-lottie.md)

Framer Motion is the animation library for React. Its declarative API makes SVG animations feel native to React's component model — animate on mount, on state change, on gesture, or on layout shift. If you're building a React app, Framer Motion is the natural choice for SVG animation.

## Setup

```typescript
npm install framer-motion
```

```typescript
import { motion } from "framer-motion";
```

## motion.svg Elements

Wrap any SVG element with `motion.` prefix to make it animatable.

```typescript
import { motion } from 'framer-motion';

function PulsingCircle() {
  return (
    <svg width="200" height="200" viewBox="0 0 200 200">
      <motion.circle
        cx={100}
        cy={100}
        r={50}
        fill="#e74c3c"
        animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      />
    </svg>
  );
}
```

Visually: A red circle that pulses — growing and fading, then shrinking back — looping forever.

## The animate Prop

Direct animation values on mount:

```typescript
function AnimatedRect() {
  return (
    <svg width="300" height="100" viewBox="0 0 300 100">
      <motion.rect
        x={20}
        y={30}
        width={40}
        height={40}
        rx={5}
        fill="#3498db"
        initial={{ x: 20, opacity: 0 }}
        animate={{ x: 240, opacity: 1 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
      />
    </svg>
  );
}
```

Visually: A blue rounded square that slides in from the left while fading in.

## Variants — Orchestrated Animations

Variants define named animation states and enable parent-child orchestration.

```typescript
import { motion } from 'framer-motion';

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.15 }
  }
};

const barVariants = {
  hidden: { height: 0, y: 0 },
  visible: (height: number) => ({
    height,
    y: -height,
    transition: { duration: 0.8, ease: "backOut" }
  })
};

function BarChart() {
  const data = [120, 180, 90, 200, 150];
  const colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6"];

  return (
    <svg width="300" height="250" viewBox="0 0 300 250">
      <motion.g variants={containerVariants} initial="hidden" animate="visible">
        {data.map((h, i) => (
          <motion.rect
            key={i}
            x={30 + i * 55}
            y={220}
            width={40}
            rx={4}
            fill={colors[i]}
            variants={barVariants}
            custom={h}
          />
        ))}
      </motion.g>
    </svg>
  );
}
```

Visually: Five colored bars grow upward one after another (staggered by 0.15s) with a bouncy overshoot — a chart animating in on page load.

## whileHover and whileTap

Gesture-driven animations:

```typescript
function InteractiveIcon() {
  return (
    <svg width="100" height="100" viewBox="0 0 24 24">
      <motion.path
        d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
        fill="#ccc"
        whileHover={{ fill: "#e74c3c", scale: 1.2 }}
        whileTap={{ scale: 0.9 }}
        transition={{ type: "spring", stiffness: 300 }}
        style={{ originX: "50%", originY: "50%" }}
      />
    </svg>
  );
}
```

Visually: A grey heart that turns red and grows on hover, shrinks slightly on click, with springy physics.

## SVG Path Animations — Line Drawing

```typescript
import { motion } from 'framer-motion';

function DrawingPath() {
  return (
    <svg width="300" height="200" viewBox="0 0 300 200">
      {/* Visible path that draws itself */}
      <motion.path
        d="M 20,100 C 20,20 140,20 150,100 C 160,180 280,180 280,100"
        fill="none"
        stroke="#e74c3c"
        strokeWidth={4}
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 2.5, ease: "easeInOut" }}
      />
    </svg>
  );
}
```

Visually: An S-curve that draws itself from start to end over 2.5 seconds. Framer Motion's `pathLength` prop handles the stroke-dasharray math automatically.

### Multi-Path Sequential Drawing

```typescript
import { motion } from 'framer-motion';

const pathVariants = {
  hidden: { pathLength: 0, opacity: 0 },
  visible: (i: number) => ({
    pathLength: 1,
    opacity: 1,
    transition: { pathLength: { duration: 1.5, delay: i * 0.5 }, opacity: { duration: 0.01, delay: i * 0.5 } }
  })
};

function LogoReveal() {
  const paths = [
    "M 20,50 L 80,50 L 50,100 Z",
    "M 90,50 C 90,20 150,20 150,50 C 150,80 90,80 90,50",
    "M 160,100 L 160,20 L 220,20 L 220,60 L 180,60"
  ];

  return (
    <svg width="250" height="120" viewBox="0 0 250 120">
      {paths.map((d, i) => (
        <motion.path
          key={i}
          d={d}
          fill="none"
          stroke="#3498db"
          strokeWidth={3}
          strokeLinecap="round"
          strokeLinejoin="round"
          variants={pathVariants}
          initial="hidden"
          animate="visible"
          custom={i}
        />
      ))}
    </svg>
  );
}
```

Visually: Three shapes draw themselves sequentially — a triangle, then a circle, then an angular shape — like a logo being sketched.

## AnimatePresence — Exit Animations

Animate elements when they're removed from the DOM:

```typescript
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

function ToggleShape() {
  const [isCircle, setIsCircle] = useState(true);

  return (
    <div>
      <button onClick={() => setIsCircle(!isCircle)}>Toggle</button>
      <svg width="200" height="200" viewBox="0 0 200 200">
        <AnimatePresence mode="wait">
          {isCircle ? (
            <motion.circle
              key="circle"
              cx={100} cy={100} r={60}
              fill="#3498db"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: "spring", stiffness: 200 }}
            />
          ) : (
            <motion.rect
              key="rect"
              x={40} y={40} width={120} height={120} rx={10}
              fill="#e74c3c"
              initial={{ scale: 0, opacity: 0, rotate: -180 }}
              animate={{ scale: 1, opacity: 1, rotate: 0 }}
              exit={{ scale: 0, opacity: 0, rotate: 180 }}
              transition={{ type: "spring", stiffness: 200 }}
            />
          )}
        </AnimatePresence>
      </svg>
    </div>
  );
}
```

Visually: Clicking the button swaps between a blue circle and a red rounded square. The outgoing shape shrinks and fades, the incoming shape grows in with a spring bounce and rotation.

## useMotionValue and useTransform

For performance-critical animations that bypass React re-renders:

```typescript
import { motion, useMotionValue, useTransform } from 'framer-motion';

function DraggableCircle() {
  const x = useMotionValue(0);
  const background = useTransform(x, [-100, 0, 100], ["#e74c3c", "#3498db", "#2ecc71"]);
  const scale = useTransform(x, [-100, 0, 100], [0.8, 1, 1.2]);

  return (
    <svg width="300" height="200" viewBox="0 0 300 200">
      <motion.circle
        cx={150}
        cy={100}
        r={40}
        style={{ x, fill: background, scale }}
        drag="x"
        dragConstraints={{ left: -100, right: 100 }}
      />
    </svg>
  );
}
```

Visually: A circle you can drag left/right. As you drag left it turns red and shrinks; drag right it turns green and grows. The color and size interpolate smoothly based on position.

## Layout Animations

Animate SVG elements when their layout changes:

```typescript
import { motion } from 'framer-motion';
import { useState } from 'react';

function SortableBars() {
  const [sorted, setSorted] = useState(false);
  const data = sorted ? [80, 120, 160, 200, 240] : [200, 80, 160, 240, 120];

  return (
    <div>
      <button onClick={() => setSorted(!sorted)}>Sort</button>
      <svg width="300" height="280" viewBox="0 0 300 280">
        {data.map((h, i) => (
          <motion.rect
            key={h}
            layout
            x={30 + i * 55}
            y={260 - h}
            width={40}
            height={h}
            rx={4}
            fill="#3498db"
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          />
        ))}
      </svg>
    </div>
  );
}
```

Visually: Five bars that smoothly rearrange themselves when you click "Sort" — each bar slides to its new position with spring physics.

## Orchestration with Variants

Complex multi-element choreography:

```typescript
import { motion } from 'framer-motion';

const svgVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.3, delayChildren: 0.2 } }
};

const circleVariants = {
  hidden: { r: 0, opacity: 0 },
  visible: { r: 30, opacity: 1, transition: { type: "spring", stiffness: 200 } }
};

const lineVariants = {
  hidden: { pathLength: 0 },
  visible: { pathLength: 1, transition: { duration: 0.8 } }
};

function NetworkGraph() {
  const nodes = [
    { cx: 100, cy: 80 }, { cx: 200, cy: 50 },
    { cx: 250, cy: 150 }, { cx: 150, cy: 180 }, { cx: 60, cy: 160 }
  ];
  const edges = [
    "M 100,80 L 200,50", "M 200,50 L 250,150",
    "M 250,150 L 150,180", "M 150,180 L 60,160", "M 60,160 L 100,80"
  ];

  return (
    <motion.svg width="320" height="240" viewBox="0 0 320 240"
                variants={svgVariants} initial="hidden" animate="visible">
      {edges.map((d, i) => (
        <motion.path key={`edge-${i}`} d={d} fill="none" stroke="#ccc"
                     strokeWidth={2} variants={lineVariants}/>
      ))}
      {nodes.map((n, i) => (
        <motion.circle key={`node-${i}`} cx={n.cx} cy={n.cy}
                       fill="#3498db" variants={circleVariants}/>
      ))}
    </motion.svg>
  );
}
```

Visually: A network graph that builds itself — lines draw between positions first, then nodes pop in with spring physics, all staggered for a choreographed reveal.

## Complete Example: Animated SVG Icon Button

```typescript
import { motion } from 'framer-motion';
import { useState } from 'react';

function MenuToggle() {
  const [isOpen, setIsOpen] = useState(false);

  const topLine = {
    closed: { d: "M 4,6 L 20,6" },
    open: { d: "M 4,4 L 20,20" }
  };
  const middleLine = {
    closed: { opacity: 1 },
    open: { opacity: 0 }
  };
  const bottomLine = {
    closed: { d: "M 4,18 L 20,18" },
    open: { d: "M 4,20 L 20,4" }
  };

  return (
    <motion.svg
      width="48" height="48" viewBox="0 0 24 24"
      onClick={() => setIsOpen(!isOpen)}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      style={{ cursor: "pointer" }}
    >
      <motion.path
        stroke="#333" strokeWidth={2} strokeLinecap="round"
        variants={topLine} animate={isOpen ? "open" : "closed"}
        transition={{ duration: 0.3 }}
      />
      <motion.path
        d="M 4,12 L 20,12"
        stroke="#333" strokeWidth={2} strokeLinecap="round"
        variants={middleLine} animate={isOpen ? "open" : "closed"}
        transition={{ duration: 0.2 }}
      />
      <motion.path
        stroke="#333" strokeWidth={2} strokeLinecap="round"
        variants={bottomLine} animate={isOpen ? "open" : "closed"}
        transition={{ duration: 0.3 }}
      />
    </motion.svg>
  );
}
```

Visually: A hamburger menu icon (three horizontal lines). Clicking it morphs into an X — top line rotates to form one diagonal, bottom line rotates to form the other, middle line fades out. Clicking again reverses the animation.

## Scroll-Linked SVG Animation

```typescript
import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';

function ScrollDrawing() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });
  const pathLength = useTransform(scrollYProgress, [0, 0.5], [0, 1]);
  const opacity = useTransform(scrollYProgress, [0, 0.2], [0, 1]);

  return (
    <div ref={ref} style={{ height: "100vh", display: "grid", placeItems: "center" }}>
      <svg width="400" height="300" viewBox="0 0 400 300">
        <motion.path
          d="M 50,250 C 50,50 200,50 200,150 C 200,250 350,250 350,50"
          fill="none"
          stroke="#e74c3c"
          strokeWidth={4}
          strokeLinecap="round"
          style={{ pathLength, opacity }}
        />
      </svg>
    </div>
  );
}
```

Visually: An S-curve that draws itself as you scroll — at the top of the viewport it's invisible, halfway through scrolling it's fully drawn. The drawing progress maps directly to scroll position.

## Key Takeaways

- `motion.circle`, `motion.path`, `motion.rect` etc. make any SVG element animatable
- `pathLength` prop handles line drawing without manual dasharray calculations
- Variants enable parent-child orchestration with `staggerChildren`
- `whileHover`/`whileTap` add gesture animations declaratively
- `AnimatePresence` animates elements entering and leaving the DOM
- `useMotionValue`/`useTransform` create performant derived animations
- `useScroll` ties animations to scroll position
- Layout animations handle reordering and position changes automatically
