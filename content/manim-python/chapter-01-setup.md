# Chapter 1: Setup

[prev: Overview](chapter-00-overview.md) | [next: Shapes](chapter-02-shapes.md)

## Installation

```bash
pip install manim
```

### Dependencies

- **ffmpeg** (required) - for video rendering
- **LaTeX** (optional) - for math typesetting with MathTex/Tex. Install TeX Live or MiKTeX.

On Windows:

```bash
choco install ffmpeg miktex
```

On macOS:

```bash
brew install ffmpeg mactex
```

On Ubuntu:

```bash
sudo apt install ffmpeg texlive-full
```

## Your First Scene

```python
from manim import *

class CircleAppearing(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        self.play(Create(circle))
        self.wait()
```

```bash
manim -pql scene.py CircleAppearing
```

## Running Manim

The basic command structure:

```bash
manim [flags] file.py ClassName
```

- `-p` — preview (open the file after rendering)
- `-ql` — low quality (480p, 15fps)
- `-qm` — medium quality (720p, 30fps)
- `-qh` — high quality (1080p, 60fps)
- `-qk` — 4K quality (2160p, 60fps)

## Output Formats

By default manim outputs `.mp4`. You can change this:

```bash
# GIF output
manim -pql --format=gif scene.py CircleAppearing

# PNG of last frame
manim -pql -s scene.py CircleAppearing
```

Output files are saved to `./media/videos/`.

## Quality Comparison

```python
from manim import *

class QualityDemo(Scene):
    def construct(self):
        text = Text("Try different quality flags!")
        circle = Circle(color=GREEN, fill_opacity=0.5)
        self.play(Write(text))
        self.play(text.animate.shift(UP * 2))
        self.play(Create(circle))
        self.wait()
```

```bash
# Low quality - fast rendering, good for development
manim -pql scene.py QualityDemo

# High quality - slow rendering, good for final output
manim -pqh scene.py QualityDemo
```

## Project Structure

A typical manim project:

```
my_project/
├── scene.py          # your scenes
├── media/            # auto-generated output
│   └── videos/
│       └── scene/
│           ├── 480p15/
│           ├── 720p30/
│           └── 1080p60/
```
