# Chapter 6: Lottie — After Effects to Web

[prev: Framer Motion](./chapter-05-framer-motion.md) | [next: Advanced Techniques](./chapter-07-techniques.md)

Lottie renders After Effects animations on the web in real-time. Designers create complex animations in After Effects, export them as JSON with the Bodymovin plugin, and developers play them back with the Lottie player. The result: designer-quality animations with tiny file sizes and full interactivity.

## How Lottie Works

1. Designer creates animation in Adobe After Effects
2. Export with Bodymovin plugin (AE extension) to JSON
3. Developer loads JSON with lottie-web player
4. Lottie renders as SVG (or Canvas/HTML) at runtime

The JSON describes shapes, keyframes, and easing — Lottie reconstructs the animation frame by frame.

## Setup — lottie-web

```html
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5/build/player/lottie.min.js"></script>
```

Or with npm:

```typescript
npm install lottie-web
```

```typescript
import lottie from "lottie-web";
```

## Basic Playback

```html
<div id="lottie-container" style="width: 300px; height: 300px;"></div>

<script src="https://cdn.jsdelivr.net/npm/lottie-web@5/build/player/lottie.min.js"></script>
<script>
  const anim = lottie.loadAnimation({
    container: document.getElementById("lottie-container"),
    renderer: "svg", // 'svg', 'canvas', or 'html'
    loop: true,
    autoplay: true,
    path: "animation.json", // URL to your Lottie JSON
  });
</script>
```

Visually: Whatever the designer created in After Effects plays back smoothly — could be a character walking, a logo animating, or an abstract motion graphic.

### Loading from JSON Data Directly

```typescript
import lottie from "lottie-web";
import animationData from "./animation.json";

const anim = lottie.loadAnimation({
  container: document.getElementById("lottie-container"),
  renderer: "svg",
  loop: true,
  autoplay: true,
  animationData: animationData, // inline JSON instead of path
});
```

## Controlling Playback

```typescript
const anim = lottie.loadAnimation({
  container: document.getElementById("container"),
  renderer: "svg",
  loop: false,
  autoplay: false,
  path: "animation.json",
});

// Play / Pause / Stop
anim.play();
anim.pause();
anim.stop();

// Speed (1 = normal, 2 = double, 0.5 = half)
anim.setSpeed(2);

// Direction (1 = forward, -1 = reverse)
anim.setDirection(-1);

// Go to specific frame
anim.goToAndStop(30, true); // frame 30, isFrame=true
anim.goToAndPlay(1.5, false); // 1.5 seconds, isFrame=false

// Play a segment (frames 20 to 50)
anim.playSegments([20, 50], true); // true = force from frame 20

// Loop specific segment
anim.playSegments(
  [
    [0, 30],
    [30, 60],
  ],
  false,
);
```

## Events

```typescript
anim.addEventListener("complete", () => {
  console.log("Animation finished");
});

anim.addEventListener("loopComplete", () => {
  console.log("Loop iteration done");
});

anim.addEventListener("enterFrame", (e) => {
  // Fires every frame — use for syncing UI
  console.log("Current frame:", e.currentTime);
});

anim.addEventListener("DOMLoaded", () => {
  console.log("Animation DOM ready");
});
```

## React Integration — react-lottie

```typescript
npm install react-lottie
```

```typescript
import Lottie from 'react-lottie';
import animationData from './success-check.json';

function SuccessAnimation() {
  const options = {
    loop: false,
    autoplay: true,
    animationData: animationData,
    rendererSettings: {
      preserveAspectRatio: 'xMidYMid slice'
    }
  };

  return <Lottie options={options} height={200} width={200} />;
}
```

### Controlled Lottie in React

```typescript
import Lottie from 'react-lottie';
import { useState } from 'react';
import animationData from './toggle.json';

function ControlledAnimation() {
  const [isStopped, setIsStopped] = useState(true);
  const [direction, setDirection] = useState(1);

  const options = {
    loop: false,
    autoplay: false,
    animationData: animationData
  };

  return (
    <div>
      <Lottie
        options={options}
        height={200}
        width={200}
        isStopped={isStopped}
        direction={direction}
      />
      <button onClick={() => { setIsStopped(false); setDirection(1); }}>Play</button>
      <button onClick={() => setDirection(-1)}>Reverse</button>
      <button onClick={() => setIsStopped(true)}>Stop</button>
    </div>
  );
}
```

### Modern Alternative: lottie-react

```typescript
npm install lottie-react
```

```typescript
import Lottie from 'lottie-react';
import animationData from './animation.json';
import { useRef } from 'react';

function ModernLottie() {
  const lottieRef = useRef(null);

  return (
    <div>
      <Lottie
        lottieRef={lottieRef}
        animationData={animationData}
        loop={true}
        style={{ width: 300, height: 300 }}
        onComplete={() => console.log('done')}
      />
      <button onClick={() => lottieRef.current?.setSpeed(2)}>2x Speed</button>
    </div>
  );
}
```

## Interactive Lottie — On Hover

```typescript
import lottie from "lottie-web";

const container = document.getElementById("hover-anim");

const anim = lottie.loadAnimation({
  container,
  renderer: "svg",
  loop: false,
  autoplay: false,
  path: "hover-icon.json",
});

container.addEventListener("mouseenter", () => {
  anim.setDirection(1);
  anim.play();
});

container.addEventListener("mouseleave", () => {
  anim.setDirection(-1);
  anim.play();
});
```

Visually: An icon that animates forward on hover (e.g., a mail icon opening) and reverses on mouse leave (envelope closes again).

## Interactive Lottie — On Scroll

```typescript
import lottie from "lottie-web";

const anim = lottie.loadAnimation({
  container: document.getElementById("scroll-anim"),
  renderer: "svg",
  loop: false,
  autoplay: false,
  path: "progress.json",
});

// Map scroll position to animation frame
window.addEventListener("scroll", () => {
  const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight);
  const frame = Math.floor(scrollPercent * anim.totalFrames);
  anim.goToAndStop(frame, true);
});
```

Visually: An animation that progresses as you scroll — at the top of the page it's at frame 0, at the bottom it's at the final frame. Could be a rocket launching, a progress bar filling, or a story unfolding.

## Interactive Lottie — Click Segments

```typescript
const anim = lottie.loadAnimation({
  container: document.getElementById("like-btn"),
  renderer: "svg",
  loop: false,
  autoplay: false,
  path: "like-button.json",
});

let liked = false;

document.getElementById("like-btn").addEventListener("click", () => {
  if (!liked) {
    anim.playSegments([0, 60], true); // Play "like" segment
  } else {
    anim.playSegments([60, 120], true); // Play "unlike" segment
  }
  liked = !liked;
});
```

Visually: A heart/like button. First click plays the "like" animation (heart fills with particles). Second click plays the "unlike" animation (heart empties).

## LottieFiles Marketplace

[LottieFiles](https://lottiefiles.com) is the largest marketplace for free and premium Lottie animations. You can:

- Browse thousands of ready-made animations
- Preview and customize colors before downloading
- Use the LottieFiles player (lighter than lottie-web)
- Edit animations with their online editor

### Using LottieFiles Player

```html
<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>

<lottie-player
  src="https://assets2.lottiefiles.com/packages/lf20_example.json"
  background="transparent"
  speed="1"
  style="width: 300px; height: 300px;"
  loop
  autoplay
>
</lottie-player>
```

The web component approach — no JavaScript setup needed.

### DotLottie Format

The newer `.lottie` format (dotLottie) compresses JSON + assets into a single file:

```html
<script
  src="https://unpkg.com/@dotlottie/player-component@latest/dist/dotlottie-player.mjs"
  type="module"
></script>

<dotlottie-player src="animation.lottie" autoplay loop style="width: 300px; height: 300px;">
</dotlottie-player>
```

## Creating Lottie Animations

### With After Effects + Bodymovin

1. Design animation in After Effects
2. Install Bodymovin extension (Window > Extensions > Bodymovin)
3. Select composition, choose export settings
4. Render to JSON

Supported AE features: shapes, fills, strokes, transforms, masks, trim paths, repeaters, text. Not supported: expressions, 3D layers, effects (blur, glow), video/audio.

### With Rive (Alternative)

[Rive](https://rive.app) is a modern alternative to After Effects for creating interactive animations:

```typescript
npm install @rive-app/react-canvas
```

```typescript
import { useRive } from '@rive-app/react-canvas';

function RiveAnimation() {
  const { RiveComponent } = useRive({
    src: 'animation.riv',
    stateMachines: 'State Machine 1',
    autoplay: true
  });

  return <RiveComponent style={{ width: 400, height: 400 }} />;
}
```

Rive advantages: state machines for interactivity, smaller file sizes, real-time editor, direct web export (no After Effects needed).

### With Haiku (now Animator by Haiku)

A code-aware animation tool that exports to Lottie, GIF, video, or code. Designers work visually, developers get clean output.

## Optimization Tips

- Keep animations under 30KB JSON for fast loading
- Use shapes over images (images bloat the JSON)
- Reduce keyframes — fewer keyframes = smaller file
- Simplify paths — fewer points per shape
- Use the LottieFiles optimizer to compress
- Lazy-load animations below the fold

```typescript
// Lazy load with Intersection Observer
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      lottie.loadAnimation({
        container: entry.target,
        renderer: "svg",
        loop: true,
        autoplay: true,
        path: entry.target.dataset.src,
      });
      observer.unobserve(entry.target);
    }
  });
});

document.querySelectorAll("[data-lottie]").forEach((el) => observer.observe(el));
```

## Complete Example: Onboarding Flow

```typescript
import lottie from "lottie-web";

const steps = ["welcome.json", "features.json", "getstarted.json"];
let currentStep = 0;
let anim: any = null;

function loadStep(index: number) {
  const container = document.getElementById("onboarding");
  if (anim) anim.destroy();

  anim = lottie.loadAnimation({
    container: container!,
    renderer: "svg",
    loop: true,
    autoplay: true,
    path: steps[index],
  });
}

document.getElementById("next-btn")?.addEventListener("click", () => {
  currentStep = Math.min(currentStep + 1, steps.length - 1);
  loadStep(currentStep);
});

document.getElementById("prev-btn")?.addEventListener("click", () => {
  currentStep = Math.max(currentStep - 1, 0);
  loadStep(currentStep);
});

loadStep(0);
```

Visually: A multi-step onboarding screen where each step has a different Lottie animation. Clicking "Next" destroys the current animation and loads the next one. Each step could show: a waving character, feature highlights with animated icons, and a rocket launching for "Get Started."

## Key Takeaways

- Lottie bridges the designer-developer gap — designers animate in After Effects, developers play back on web
- `lottie-web` renders as SVG for crisp, scalable animations
- Control playback with `play()`, `pause()`, `goToAndStop()`, `playSegments()`
- Make animations interactive with hover, click, and scroll triggers
- LottieFiles marketplace has thousands of ready-to-use animations
- Rive is a modern alternative with built-in state machines
- Keep JSON files small — use shapes, minimize keyframes, compress with LottieFiles optimizer
- Use Intersection Observer to lazy-load animations for performance
