# Chapter 10: Audio

Ursina plays audio with a single line. Support for WAV, OGG, and MP3 formats. Audio can loop, adjust volume, and even attach to entities for spatial sound.

```python
from ursina import *

app = Ursina()

# Background music (loops, lower volume)
# music = Audio('background_music.mp3', loop=True, volume=0.3, autoplay=True)

# Sound effect (plays once on demand)
# jump_sound = Audio('jump.wav', autoplay=False)

# Spatial audio (volume based on distance to listener)
# spatial_sfx = Audio('hum.ogg', loop=True, autoplay=True)
# spatial_sfx.position = Vec3(5, 0, 0)  # sound comes from the right

# Demo with built-in functionality
player = Entity(model='cube', color=color.orange, position=(0, 0.5, 0))
ground = Entity(model='plane', texture='grass', scale=20)

info = Text(text='Press SPACE to play sound\nPress M to toggle music',
            position=(-0.5, 0.4))

def input(key):
    if key == 'space':
        # Play a one-shot sound effect
        Audio('sine', volume=0.5)  # built-in test tone
    if key == 'm':
        pass  # music.playing = not music.playing

EditorCamera()
app.run()
```

## Key Points

- **Audio(file, autoplay=True)**: plays immediately when created
- **Audio(file, loop=True)**: loops continuously — perfect for music
- **volume**: 0.0 (silent) to 1.0 (full volume)
- **autoplay=False**: load the sound but don't play until you call `audio.play()`
- **Spatial audio**: set `audio.position` to a Vec3 — volume fades with distance
- Place audio files in your project folder (same directory as your script)

## What You Learned

- How to play background music with looping
- How to trigger one-shot sound effects
- How to control volume and playback
- How spatial audio works with entity positions
- Supported audio formats: WAV, OGG, MP3

---

[← Chapter 9: UI](chapter-09-ui.md) | [Next → Chapter 11: Terrain & Sky](chapter-11-terrain.md)
