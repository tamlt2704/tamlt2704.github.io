# Media

[prev: Advanced Motion](chapter-06-motion.md) | [next: Projects](chapter-08-projects.md)

## Images

```typescript
import {makeScene2D, Img} from '@revideo/2d';

export default makeScene2D(function* (view) {
  const img = <Img src="/images/photo.png" width={400} opacity={0} />;
  view.add(img);

  yield* img.opacity(1, 0.5);
  yield* img.scale(1.2, 1);
  yield* img.rotation(10, 0.5);
});
```

## Video Clips

```typescript
import {makeScene2D, Video} from '@revideo/2d';
import {waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  const video = <Video src="/clips/demo.mp4" width={800} />;
  view.add(video);

  // Start playback
  video.play();

  yield* waitFor(3);

  // Pause and seek
  video.pause();
  yield* video.opacity(0.5, 0.3);

  video.seek(5);
  video.play();
  yield* video.opacity(1, 0.3);

  yield* waitFor(2);
});
```

## Audio Sync

```typescript
import {makeScene2D, Circle} from '@revideo/2d';
import {waitFor, usePlayback} from '@revideo/core';

export default makeScene2D(function* (view) {
  const playback = usePlayback();

  const circle = <Circle size={100} fill="#e13238" />;
  view.add(circle);

  // Sync animation to audio beats (manual timing)
  const beats = [0.5, 1.0, 1.5, 2.0, 2.5];

  for (const beat of beats) {
    yield* waitFor(beat - playback.time);
    yield* circle.scale(1.3, 0.1);
    yield* circle.scale(1, 0.1);
  }
});
```

## SVG Import

```typescript
import {makeScene2D, Img} from '@revideo/2d';

export default makeScene2D(function* (view) {
  // SVGs can be loaded as images
  const icon = <Img src="/icons/arrow.svg" width={200} opacity={0} />;
  view.add(icon);

  yield* icon.opacity(1, 0.5);
  yield* icon.x(200, 0.8);
  yield* icon.rotation(90, 0.5);
});
```

## Screen Recordings

```typescript
import {makeScene2D, Video, Rect} from '@revideo/2d';
import {waitFor} from '@revideo/core';

export default makeScene2D(function* (view) {
  // Frame around the recording
  const frame = (
    <Rect width={820} height={470} stroke="#333" lineWidth={4} radius={12}>
      <Video src="/recordings/screen.mp4" width={800} height={450} />
    </Rect>
  );
  view.add(frame);

  frame.opacity(0);
  yield* frame.opacity(1, 0.5);

  // Play the recording
  const video = frame.children()[0] as any;
  video.play();

  yield* waitFor(5);

  yield* frame.scale(0.8, 0.5);
  yield* frame.opacity(0, 0.3);
});
```
