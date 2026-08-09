# Chapter 12: Polish and Deploy

## What you'll learn

- Speed control for playback
- Keyboard shortcuts
- Responsive design (works on smaller screens)
- Deploying to GitHub Pages

## 12.1 Speed control

Replace the fixed `1000ms` interval with a configurable speed. Add state:

```tsx
const [speed, setSpeed] = useState(800); // milliseconds between steps
```

Update the `useEffect` timer:

```tsx
useEffect(() => {
  if (!isPlaying) return;

  const timer = setInterval(() => {
    setCurrentStep((prev) => {
      if (prev >= steps.length - 1) {
        setIsPlaying(false);
        return prev;
      }
      return prev + 1;
    });
  }, speed); // ← use the speed state

  return () => clearInterval(timer);
}, [isPlaying, steps.length, speed]); // ← add speed to dependencies
```

Add a speed slider to the Controls area:

```tsx
<div className="flex items-center gap-2 text-sm text-gray-600">
  <span>Speed:</span>
  <input
    type="range"
    min={100}
    max={2000}
    step={100}
    value={speed}
    onChange={(e) => setSpeed(Number(e.target.value))}
    className="w-24"
  />
  <span>{speed}ms</span>
</div>
```

> **Why a range slider instead of preset buttons (0.5x, 1x, 2x)?** The slider gives fine-grained control. Learners who "get it" can speed up. Learners who need more time can slow down. Preset buttons force choices that may not match the user's pace.
>
> **Note the UX:** Lower slider value = faster. This can feel backwards. Consider labelling it "Fast ← → Slow" or inverting the visual. We keep it simple here.

## 12.2 Keyboard shortcuts

Users shouldn't need to click buttons. Arrow keys are natural for stepping:

```tsx
useEffect(() => {
  function handleKeyDown(e: KeyboardEvent) {
    switch (e.key) {
      case "ArrowRight":
      case "n":
        e.preventDefault();
        handleNext();
        break;
      case "ArrowLeft":
      case "p":
        e.preventDefault();
        handlePrev();
        break;
      case " ": // spacebar
        e.preventDefault();
        handlePlay();
        break;
      case "r":
        e.preventDefault();
        handleReset();
        break;
    }
  }

  window.addEventListener("keydown", handleKeyDown);
  return () => window.removeEventListener("keydown", handleKeyDown);
}, []); // Empty deps — handlers use updater pattern, so they're always current
```

Add a hint below the controls:

```tsx
<p className="text-xs text-gray-400 text-center mt-1">
  Keyboard: ← Prev | → Next | Space Play/Pause | R Reset
</p>
```

> **Why `e.preventDefault()`?** Without it, spacebar scrolls the page, and arrow keys might scroll or focus-shift. We want them to control the visualiser exclusively when on this page.
>
> **Accessibility note:** Keyboard shortcuts should not conflict with screen reader shortcuts. The arrow keys and spacebar are safe in most contexts. If you add more shortcuts, consider a "focus required" model — shortcuts only work when the visualiser panel is focused.

## 12.3 Progress bar

A visual indicator of how far through the algorithm you are:

```tsx
<div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
  <div
    className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
    style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
  />
</div>
```

You can also make it clickable — allow jumping to any step:

```tsx
<div
  className="w-full bg-gray-200 rounded-full h-2 mt-2 cursor-pointer"
  onClick={(e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const ratio = (e.clientX - rect.left) / rect.width;
    const targetStep = Math.round(ratio * (steps.length - 1));
    setCurrentStep(targetStep);
  }}
>
  <div
    className="bg-blue-600 h-2 rounded-full transition-all duration-200"
    style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
  />
</div>
```

## 12.4 Responsive design

On mobile or narrow screens, the side-by-side layout breaks. Stack the panels vertically:

```tsx
{/* Replace flex with responsive classes */}
<div className="flex flex-col lg:flex-row flex-1 gap-4 min-h-0">
  <CodePanel ... />
  <VisualisationPanel>...</VisualisationPanel>
</div>
```

Tailwind classes:
- `flex-col` — stack vertically by default (mobile)
- `lg:flex-row` — side by side on large screens (≥1024px)

Also make the SVG responsive:

```tsx
// In BarChart/GraphChart, derive width from container:
const containerRef = useRef<HTMLDivElement>(null);
const [dimensions, setDimensions] = useState({ width: 500, height: 300 });

useEffect(() => {
  if (!containerRef.current) return;
  const observer = new ResizeObserver((entries) => {
    const { width, height } = entries[0].contentRect;
    setDimensions({ width, height: Math.min(height, 400) });
  });
  observer.observe(containerRef.current);
  return () => observer.disconnect();
}, []);
```

> **What is ResizeObserver?** A browser API that fires a callback when an element's size changes. Unlike `window.resize`, it watches a specific element — works even when the window size doesn't change but a panel resizes (e.g., opening a sidebar).
>
> **Alternative: just set percentage widths.** SVG with `viewBox` can scale automatically. Use `viewBox="0 0 500 300"` and `width="100%"`. D3 still uses the viewBox coordinate system internally. This is simpler than ResizeObserver for basic cases.

## 12.5 Deploying to GitHub Pages

Your repo is `javizstudio.github.io` — a GitHub Pages site. Next.js needs configuration for static export.

### Step 1: Configure Next.js for static export

Update `next.config.ts`:

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",       // Generate static HTML files
  images: {
    unoptimized: true,    // GitHub Pages doesn't support Next.js image optimization
  },
};

export default nextConfig;
```

### Step 2: Build

```bash
npm run build
```

This generates an `out/` folder with static HTML, CSS, and JS files.

### Step 3: Deploy

If your repo is set up as a GitHub Pages site (Settings → Pages → Deploy from branch):

```bash
# The out/ folder IS your site
# Option 1: Push to a gh-pages branch
git add out/ -f
git commit -m "Deploy static site"
git subtree push --prefix out origin gh-pages

# Option 2: Use GitHub Actions (recommended)
# Create .github/workflows/deploy.yml
```

A simple GitHub Actions workflow:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: out
      - uses: actions/deploy-pages@v4
```

> **Why static export?** GitHub Pages serves static files. Next.js normally requires a Node.js server (for API routes, server-side rendering). `output: "export"` generates plain HTML — no server needed. You lose server features but gain free, zero-maintenance hosting.
>
> **Alternative hosting:** Vercel (free tier, supports full Next.js features including server components and API routes), Netlify (similar), Cloudflare Pages (similar). If you want server features later, deploy to Vercel.

## 12.6 Final touches checklist

- [ ] Page title and meta description (`metadata` in `layout.tsx`)
- [ ] Favicon (replace `app/favicon.ico`)
- [ ] Loading state while steps generate (for complex algorithms)
- [ ] Error boundary (graceful error handling)
- [ ] `aria-label` on buttons for screen readers
- [ ] Colour-blind safe palette (don't rely only on colour — add shapes/patterns)
- [ ] Print styles (optional — nice for students who want to print)

## 12.7 Where to go from here

You've built a complete algorithm visualiser. Ideas for extending:

| Feature | Complexity | Chapter to revisit |
|---------|-----------|-------------------|
| Binary search visualisation | Low | Ch 8 (step engine) |
| Quicksort | Medium | Ch 9 (more sorts) |
| Dijkstra's algorithm | Medium | Ch 10 (graphs) |
| User-input arrays | Low | Ch 3 (state) |
| Step-back with animation | Medium | Ch 6 (transitions) |
| Share specific steps via URL | Low | Ch 11 (persistence) |
| Dark/light mode toggle | Low | Ch 2 (components) |
| Code editor (let users modify code) | High | New concept (Monaco editor) |

## Summary

✅ Speed control with slider  
✅ Keyboard shortcuts for quick navigation  
✅ Responsive layout (mobile + desktop)  
✅ Progress bar with click-to-jump  
✅ Static export and GitHub Pages deployment  

## Key takeaway

**Polish is what separates a "project" from a "product."** The algorithm logic was done in Chapter 8. Chapters 9–12 are about making it usable, accessible, and deployable. In real-world development, this "last 20%" takes 80% of the time — but it's what makes people actually use your tool.

---

🎉 **Tutorial complete!** You've built a full algorithm visualiser from scratch — from understanding React components to deploying a production site. You now know:

- How React components, state, and effects work
- How D3 binds data to visual elements
- How Rough.js adds a hand-drawn aesthetic
- How to design a step engine that decouples algorithms from UI
- How to support multiple languages and algorithms

The architecture scales: adding new algorithms means writing one new file. The UI handles the rest.

→ Back to [Introduction](./00-INTRODUCTION.md)
