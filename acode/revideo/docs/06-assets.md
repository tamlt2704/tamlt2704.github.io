# Import Assets

[← Easing Functions](05-easing-functions.md) | [Layout →](07-layout.md)

---

## Images

```tsx
import { Img } from '@revideo/2d';

// Add an image
view.add(<Img src="public/photo.png" width={400} />);

// With ref for animation
const img = createRef<Img>();
view.add(<Img ref={img} src="public/logo.svg" width={300} opacity={0} />);
yield* img().opacity(1, 0.5);
yield* img().scale(1.2, 0.3);
```

Place image files in the `public/` directory of your project.

**Manim equivalent:** `ImageMobject("photo.png")`

### SVG

SVGs are loaded the same way as images:

```tsx
<Img src="public/icon.svg" width={200} />
```

## Video

```tsx
import { Video } from '@revideo/2d';

const video = createRef<Video>();
view.add(<Video ref={video} src="public/clip.mp4" width={800} />);

// Play the video
yield* video().play();

// Or seek to a specific time
video().seek(5); // jump to 5 seconds
```

## Audio

```tsx
import { Audio } from '@revideo/2d';

view.add(<Audio src="public/music.mp3" />);
```

Audio plays automatically when the scene starts. You can control timing by adding it at a specific point in your generator.

**Manim equivalent:**

```python
# Manim
self.add_sound("music.mp3")
```

---

[← Easing Functions](05-easing-functions.md) | [Layout →](07-layout.md)
