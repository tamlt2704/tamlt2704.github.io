"""
Intro to Manim — 03: Camera & Render Settings
Covers: manim.cfg, CLI flags, config dict, resolution, background color.
Source: https://docs.devtaoism.com/docs/html/contents/_3_camera_options.html

Render: manim -pql 03_camera_render.py CameraRender
"""
from manim import *


class CameraRender(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"

        title = Text("03: Camera & Render Settings", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # CLI flags
        flags = VGroup(
            Text("manim script.py SceneName [flags]", font_size=20, color=BLUE),
            Text("", font_size=8),
            Text("-pql  → preview + low quality (854×480, 15fps)", font_size=16),
            Text("-pqm  → preview + medium (1280×720, 30fps)", font_size=16),
            Text("-pqh  → preview + high (1920×1080, 60fps)", font_size=16),
            Text("-pqk  → preview + 4K (3840×2160, 60fps)", font_size=16),
            Text("-ps   → save last frame as PNG (no video)", font_size=16),
            Text("-o NAME → custom output filename", font_size=16),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        flags.move_to(DOWN * 0.3)

        self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.3) for f in flags],
                  lag_ratio=0.12), run_time=1.5)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

        # Background color
        title2 = Text("Background Color", font_size=24, color=YELLOW)
        title2.to_edge(UP)
        self.play(Write(title2))

        code = Code(
            code='self.camera.background_color = "#1a1a2e"',
            language="python", font_size=16,
            background="rectangle", style="monokai",
            insert_line_no=False, background_stroke_color="#333",
        )
        code.scale(0.8)
        self.play(FadeIn(code))

        note = Text("Set in construct() before any animations",
                     font_size=16, color=GREY)
        note.to_edge(DOWN)
        self.play(FadeIn(note))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

        # Config priority
        title3 = Text("Config Priority", font_size=24, color=YELLOW)
        title3.to_edge(UP)
        self.play(Write(title3))

        priority = VGroup(
            Text("1. CLI flags (highest)", font_size=18, color=RED),
            Text("2. Code: config.xxx = ...", font_size=18, color=ORANGE),
            Text("3. manim.cfg file (lowest)", font_size=18, color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        priority.move_to(ORIGIN)

        arrows = VGroup()
        for i in range(2):
            a = Arrow(priority[i].get_bottom(), priority[i + 1].get_top(),
                      color=GREY, buff=0.05, stroke_width=2)
            arrows.add(a)

        self.play(FadeIn(priority), FadeIn(arrows))
        self.wait(3)
