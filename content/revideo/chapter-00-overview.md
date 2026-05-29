# Revideo: Create Videos with Code

[next: Setup](chapter-01-setup.md)

Revideo is a TypeScript framework for creating programmatic videos and animations. It is a fork of Motion Canvas, optimized for video production workflows. You write scenes as generator functions, animate properties with signals, and render the result to mp4.

## Chapters

1. [Setup](chapter-01-setup.md) - Installation, project structure, editor UI
2. [Scenes & Nodes](chapter-02-scenes.md) - Scene generators, node types, properties
3. [Animations](chapter-03-animations.md) - Tweening, easing, parallel/sequential timing
4. [Signals & Reactivity](chapter-04-signals.md) - Reactive values, computed signals
5. [Layout & Text](chapter-05-layout.md) - Flexbox layout, text, code highlighting
6. [Advanced Motion](chapter-06-motion.md) - Paths, springs, camera, scene transitions
7. [Media](chapter-07-media.md) - Images, video, audio, SVG, Lottie
8. [Projects](chapter-08-projects.md) - Complete example videos

## What is Revideo?

Revideo lets you define animations in TypeScript using generator functions. Each `yield*` pauses execution until an animation completes, giving you precise frame-level control over timing.

```typescript
import {makeScene2D, Rect} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const rect = <Rect width={100} height={100} fill="#e13238" />;
  view.add(rect);

  // yield* waits for the animation to finish
  yield* rect.x(300, 1);
  yield* rect.rotation(360, 0.5);
});
```

## Revideo vs Manim

|           | Revideo                           | Manim                        |
| --------- | --------------------------------- | ---------------------------- |
| Language  | TypeScript                        | Python                       |
| Rendering | Browser-based, real-time preview  | Offline rendering            |
| Paradigm  | Signals + generators              | Imperative animation methods |
| Ecosystem | npm, web technologies             | Python scientific stack      |
| Best for  | Web-style graphics, UI animations | Mathematical visualizations  |

## Revideo vs After Effects

|                 | Revideo                       | After Effects                    |
| --------------- | ----------------------------- | -------------------------------- |
| Interface       | Code editor + preview         | Visual timeline                  |
| Reproducibility | Git-friendly, deterministic   | Binary project files             |
| Automation      | Fully scriptable, CI/CD       | Limited scripting (ExtendScript) |
| Cost            | Free, open source             | Subscription                     |
| Learning curve  | Requires TypeScript knowledge | Visual, but complex UI           |

## Use Cases

- **Explainer videos** - Animate diagrams, flowcharts, and concepts step by step
- **Data visualization** - Bar chart races, animated graphs, real-time data
- **Code tutorials** - Typing effects, syntax highlighting, line-by-line walkthroughs
- **YouTube intros/outros** - Branded motion graphics
- **Presentation slides** - Animated slides rendered as video
- **Social media content** - Short animated clips with consistent branding
