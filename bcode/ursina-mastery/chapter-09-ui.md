# Chapter 9: UI

Ursina includes UI elements that render in screen space. Text, buttons, health bars, and sliders work out of the box with minimal setup. Positions use normalized screen coordinates.

```python
from ursina import *

app = Ursina()

# Score display (top-left)
score = 0
score_text = Text(text=f'Score: {score}', position=(-0.85, 0.45), scale=2)

# Health bar
health_bar = HealthBar(max_value=100, value=100, bar_color=color.red,
                       position=(-0.85, 0.4))

# Button
def on_play():
    print('Game started!')

play_btn = Button(text='Play', scale=(0.2, 0.08), position=(0, -0.3),
                  color=color.azure, on_click=on_play)

# Slider
volume_slider = Slider(min=0, max=100, default=50, step=1,
                       position=(0, -0.15), text='Volume')

def input(key):
    global score
    if key == 'space':
        score += 10
        score_text.text = f'Score: {score}'
        health_bar.value -= 10

EditorCamera()
app.run()
```

## Key Points

- **Text()**: screen-space text — position `(-0.5, 0.5)` is top-left, `(0.5, -0.5)` is bottom-right
- **Button()**: clickable UI element with `on_click` callback
- **HealthBar()**: visual bar with `value` and `max_value` — updates automatically
- **Slider()**: draggable slider with min/max/step
- UI elements are always on top of the 3D scene
- Update text content by reassigning `.text`

## What You Learned

- How to display text on screen with positioning
- How to create clickable buttons with callbacks
- How to use HealthBar for visual status indicators
- How to add sliders for adjustable values
- The screen coordinate system for UI placement

---

[← Chapter 8: Animation](chapter-08-animation.md) | [Next → Chapter 10: Audio](chapter-10-audio.md)
