# Level 4: Specialisations — Pick Your Path

At this level, you go deep into one (or two) areas. You can't master everything — pick what excites you.

---

## Path A: Data Visualisation

**This matches your interest** — algorithms, gov.data dashboards, interactive charts.

### The Progression

```
Recharts (where you are)
    ↓ want more control
D3.js (build any chart from scratch)
    ↓ need speed for big data
Canvas API (10k+ data points, no DOM)
    ↓ want 3D
WebGL / Three.js (3D visualisations)
    ↓ want maps
Mapbox / Deck.gl (geographic data)
```

### D3.js — The Data Visualisation Powerhouse

D3 doesn't give you charts — it gives you tools to build any visualisation:

| D3 Concept | What it does |
|-----------|-------------|
| **Scales** | Map data values → pixel positions (`d3.scaleLinear`) |
| **Axes** | Generate axis labels and tick marks |
| **Shapes** | SVG path generators (lines, arcs, areas) |
| **Selections** | Select and manipulate DOM elements |
| **Transitions** | Animate between states |
| **Layouts** | Algorithms for tree, force, pie, histogram layouts |

```tsx
// D3 scale: map data (0-100) to pixels (0-500)
const x = d3.scaleLinear()
  .domain([0, 100])     // data range
  .range([0, 500])      // pixel range

x(50)  // → 250 (halfway)
x(0)   // → 0
x(100) // → 500
```

**D3 + React approach:**
- Use D3 for maths (scales, layouts, data processing)
- Use React for rendering (SVG elements as JSX)
- Don't let D3 touch the DOM — React owns the DOM

```tsx
import * as d3 from "d3"

function BarChart({ data }: { data: { label: string; value: number }[] }) {
  const width = 600
  const height = 300

  const x = d3.scaleBand()
    .domain(data.map(d => d.label))
    .range([0, width])
    .padding(0.2)

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value) ?? 0])
    .range([height, 0])

  return (
    <svg width={width} height={height}>
      {data.map(d => (
        <rect
          key={d.label}
          x={x(d.label)}
          y={y(d.value)}
          width={x.bandwidth()}
          height={height - y(d.value)}
          fill="hsl(var(--primary))"
        />
      ))}
    </svg>
  )
}
```

### Canvas API — When SVG Gets Slow

SVG creates a DOM node per element. 10,000 bars = 10,000 nodes = browser lag.

Canvas draws pixels directly — one `<canvas>` element, unlimited shapes:

```tsx
"use client"

import { useRef, useEffect } from "react"

function CanvasChart({ data }: { data: number[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const barWidth = canvas.width / data.length

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    data.forEach((value, i) => {
      const barHeight = (value / 100) * canvas.height
      ctx.fillStyle = "hsl(220, 70%, 50%)"
      ctx.fillRect(
        i * barWidth,
        canvas.height - barHeight,
        barWidth - 1,
        barHeight
      )
    })
  }, [data])

  return <canvas ref={canvasRef} width={800} height={400} />
}
```

**SVG vs Canvas:**

| | SVG | Canvas |
|-|-----|--------|
| Best for | < 1000 elements, interactivity needed | > 1000 elements, animation-heavy |
| Interaction | Native (click/hover on elements) | Manual (calculate what was clicked) |
| Accessibility | Elements can have ARIA | Just an image — needs alt text |
| Resolution | Scales perfectly (vector) | Can be blurry on zoom |
| Tooling with React | JSX elements | `useRef` + imperative drawing |

### Storytelling with Data

The difference between a dashboard and a data story:

| Dashboard | Data Story |
|-----------|-----------|
| Shows all data at once | Guides you through one insight at a time |
| User explores freely | Author controls the narrative |
| Static layout | Scroll-driven reveals |
| "Here's the data" | "Here's what this data means" |

**Scrollytelling pattern:**

```
[Text: "In 2020, spending was stable"]
    ↓ scroll
[Chart animates to show 2020 data]
    ↓ scroll
[Text: "Then COVID hit"]
    ↓ scroll
[Chart animates — spike appears]
    ↓ scroll
[Text: "Education spending doubled"]
    ↓ scroll
[Chart highlights education bar]
```

Libraries: `react-scrollama`, `@scrollama/react`, or Intersection Observer + Framer Motion.

### Resources for Path A

| Resource | What | Free? |
|----------|------|-------|
| [Observable](https://observablehq.com) | Interactive notebooks, D3 examples | ✅ |
| [D3 in Depth](https://d3indepth.com) | D3 concepts explained clearly | ✅ |
| [Fullstack D3 (Amelia Wattenberger)](https://fullstack-d3.com) | D3 + React book | 💰 |
| [Information is Beautiful](https://informationisbeautiful.net) | Inspiration gallery | ✅ |
| [The Pudding](https://pudding.cool) | World-class scrollytelling examples | ✅ |
| [Shirley Wu](https://sxywu.com) | Beautiful D3 + React examples | ✅ |

---

## Path B: Interactive / Creative

### The Progression

```
Framer Motion (where you are)
    ↓ want scroll-driven
GSAP + ScrollTrigger
    ↓ want 3D
Three.js / React Three Fiber
    ↓ want custom effects
Shaders (GLSL)
    ↓ want generative art
Canvas + algorithms + randomness
```

### Three.js + React Three Fiber

3D in the browser, using React:

```bash
npm install three @react-three/fiber @react-three/drei
```

```tsx
import { Canvas } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"

function Scene() {
  return (
    <Canvas>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <mesh rotation={[0, Math.PI / 4, 0]}>
        <boxGeometry args={[2, 2, 2]} />
        <meshStandardMaterial color="hotpink" />
      </mesh>
      <OrbitControls />  {/* drag to rotate */}
    </Canvas>
  )
}
```

**Use cases:**
- 3D algorithm visualisations (graph traversal in 3D space)
- Product configurators (rotate, customise)
- Data landscapes (3D scatter plots, terrain)
- Portfolio/creative sites

### GSAP + ScrollTrigger

Professional-grade scroll-driven animations:

```bash
npm install gsap
```

```tsx
import { useEffect, useRef } from "react"
import gsap from "gsap"
import { ScrollTrigger } from "gsap/ScrollTrigger"

gsap.registerPlugin(ScrollTrigger)

function AnimatedSection() {
  const ref = useRef(null)

  useEffect(() => {
    gsap.fromTo(ref.current,
      { opacity: 0, y: 100 },
      {
        opacity: 1,
        y: 0,
        scrollTrigger: {
          trigger: ref.current,
          start: "top 80%",   // when top of element hits 80% of viewport
          end: "top 20%",
          scrub: true,         // ties animation to scroll position
        },
      }
    )
  }, [])

  return <div ref={ref}>I animate as you scroll</div>
}
```

### Generative Art

Use algorithms + randomness to create visual art:

```tsx
function generateArt(ctx: CanvasRenderingContext2D, width: number, height: number) {
  for (let i = 0; i < 500; i++) {
    const x = Math.random() * width
    const y = Math.random() * height
    const radius = Math.random() * 20
    const hue = Math.random() * 360

    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fillStyle = `hsl(${hue}, 70%, 60%)`
    ctx.globalAlpha = 0.6
    ctx.fill()
  }
}
```

Combine with algorithms: Perlin noise, L-systems, particle systems, Voronoi diagrams.

### Resources for Path B

| Resource | What | Free? |
|----------|------|-------|
| [Three.js Journey](https://threejs-journey.com) | Best Three.js course | 💰 |
| [The Coding Train](https://thecodingtrain.com) | Creative coding (p5.js, algorithms) | ✅ |
| [Codrops](https://tympanus.net/codrops/) | Creative web experiments | ✅ |
| [GSAP docs](https://gsap.com/docs/) | ScrollTrigger, timeline examples | ✅ |
| [Shadertoy](https://shadertoy.com) | Shader examples and inspiration | ✅ |

---

## Path C: Application Development

### The Progression

```
React + Next.js (where you are)
    ↓ complex interactions
State machines (XState)
    ↓ real-time
WebSockets
    ↓ rich editing
TipTap / Lexical (rich text)
    ↓ complex layouts
Drag and drop (dnd-kit)
    ↓ offline
PWA + Service Workers
```

### State Machines (XState)

When your app has complex states with strict transitions:

```
Game: idle → playing → paused → finished
             ↓                    ↓
           game-over            restart → idle
```

```bash
npm install xstate @xstate/react
```

```tsx
import { createMachine } from "xstate"
import { useMachine } from "@xstate/react"

const gameMachine = createMachine({
  id: "game",
  initial: "idle",
  states: {
    idle: { on: { START: "playing" } },
    playing: {
      on: {
        PAUSE: "paused",
        GAME_OVER: "finished",
      },
    },
    paused: { on: { RESUME: "playing" } },
    finished: { on: { RESTART: "idle" } },
  },
})

function Game() {
  const [state, send] = useMachine(gameMachine)

  if (state.matches("idle")) return <button onClick={() => send("START")}>Play</button>
  if (state.matches("playing")) return <button onClick={() => send("PAUSE")}>Pause</button>
  // ...
}
```

**When state machines > useState:**
- More than 3-4 states with specific allowed transitions
- Invalid states are possible (e.g. "paused" while "idle")
- The logic is getting hard to follow with if/else chains

### Real-Time (WebSockets)

Live data, chat, collaboration:

```tsx
"use client"

import { useEffect, useState } from "react"

function LiveChat() {
  const [messages, setMessages] = useState<string[]>([])

  useEffect(() => {
    const ws = new WebSocket("wss://your-server.com/chat")

    ws.onmessage = (event) => {
      setMessages(prev => [...prev, event.data])
    }

    return () => ws.close()  // cleanup
  }, [])

  return (
    <ul>
      {messages.map((msg, i) => <li key={i}>{msg}</li>)}
    </ul>
  )
}
```

### Drag and Drop (dnd-kit)

```bash
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

Build: Kanban boards, sortable lists, file upload zones, dashboard layout editors.

### Resources for Path C

| Resource | What | Free? |
|----------|------|-------|
| [XState docs](https://stately.ai/docs) | State machines for UI | ✅ |
| [dnd-kit docs](https://dndkit.com) | Drag and drop | ✅ |
| [TipTap docs](https://tiptap.dev) | Rich text editor | ✅ |
| [Socket.io docs](https://socket.io) | WebSocket library | ✅ |
| [PWA course (web.dev)](https://web.dev/learn/pwa) | Offline-first apps | ✅ |

---

## Path D: Infrastructure / Full-Stack Leaning

### The Progression

```
Static site (where you are)
    ↓ need a database
Supabase / PlanetScale (DB as a service)
    ↓ need auth
NextAuth / Clerk
    ↓ need deployment
Vercel / Cloudflare
    ↓ need CI/CD
GitHub Actions
    ↓ need monitoring
Sentry + Analytics
```

### Supabase — Database + Auth in Minutes

```bash
npm install @supabase/supabase-js
```

Supabase gives you: PostgreSQL database, authentication, real-time subscriptions, file storage — all with a JS client.

```tsx
import { createClient } from "@supabase/supabase-js"

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
)

// Read data
const { data } = await supabase.from("posts").select("*")

// Insert data
await supabase.from("posts").insert({ title: "Hello", body: "World" })

// Auth
await supabase.auth.signInWithOAuth({ provider: "github" })
```

### GitHub Actions for Frontend

You already have the deploy workflow. More useful workflows:

```yaml
# Run tests on every PR
name: CI
on: pull_request
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npm run build
      - run: npm test
```

### Sentry — Error Monitoring

See errors from real users in production:

```bash
npx @sentry/wizard@latest -i nextjs
```

When a user hits a bug, you get: the error, stack trace, browser info, and what they were doing.

### Resources for Path D

| Resource | What | Free? |
|----------|------|-------|
| [Supabase docs](https://supabase.com/docs) | DB + Auth | ✅ (free tier) |
| [Vercel docs](https://vercel.com/docs) | Deployment platform | ✅ (free tier) |
| [GitHub Actions docs](https://docs.github.com/en/actions) | CI/CD | ✅ |
| [Sentry docs](https://docs.sentry.io) | Error monitoring | ✅ (free tier) |
| [Cloudflare Workers](https://developers.cloudflare.com/workers/) | Edge computing | ✅ (free tier) |

---

## How to Pick Your Path

| If you enjoy... | Choose |
|----------------|--------|
| Making data beautiful and understandable | Path A |
| Creative coding, visual effects, "wow" moments | Path B |
| Building complex interactive apps (tools, editors) | Path C |
| Understanding the full stack, deployment, DevOps | Path D |

**You can combine paths.** Data visualisation (A) + creative coding (B) is a powerful combo for your algorithm blog. Application dev (C) + infrastructure (D) makes you a full-stack developer.

---

## How to Know You've Reached Level 4

- [ ] You can build things most developers can't
- [ ] People come to you with questions in your specialisation
- [ ] You can evaluate trade-offs between approaches in your domain
- [ ] You've read source code of libraries in your space (D3, Three.js, etc.)
- [ ] You can teach your specialisation to others (your blog!)
- [ ] You've contributed to or built tools in your area
