# Text

[← Layout](07-layout.md) | [Transitions →](09-transitions.md)

---

## Txt Node

```tsx
import { Txt } from '@revideo/2d';

<Txt text="Hello World" fill="white" fontSize={48} fontFamily="monospace" />
```

### Font Properties

| Property | Type | Example |
|---|---|---|
| `text` | string | `"Hello"` |
| `fill` | color | `"white"`, `"#4ec9b0"` |
| `fontSize` | number | `48` |
| `fontFamily` | string | `"Arial"`, `"monospace"` |
| `fontWeight` | number/string | `700`, `"bold"` |
| `fontStyle` | string | `"italic"` |
| `textAlign` | string | `"center"`, `"left"`, `"right"` |
| `lineHeight` | number | `1.5` (multiplier) or `60` (pixels) |

### Animating Text

```tsx
const title = createRef<Txt>();
view.add(<Txt ref={title} text="" fill="white" fontSize={64} />);

// Type-writer effect (manual)
const fullText = "Hello World";
for (let i = 0; i <= fullText.length; i++) {
  title().text(fullText.slice(0, i));
  yield* waitFor(0.05);
}

// Fade in
yield* title().opacity(1, 0.5);

// Change text content (instant)
title().text("New Text");

// Animate color
yield* title().fill('#4ec9b0', 0.5);
```

**Manim equivalent:**

```python
text = Text("Hello World", font_size=48, color=WHITE)
self.play(Write(text))
```

Revideo doesn't have a built-in `Write` animation for text. The typewriter loop above is the closest equivalent. For a "draw" effect on shapes, use `line().end(1, duration)`.

## Code Blocks

For code syntax highlighting, use `Txt` with a monospace font:

```tsx
<Txt
  text={`function hello() {\n  return "world";\n}`}
  fill="#cccccc"
  fontFamily="JetBrains Mono, monospace"
  fontSize={18}
  lineHeight={28}
/>
```

---

[← Layout](07-layout.md) | [Transitions →](09-transitions.md)
