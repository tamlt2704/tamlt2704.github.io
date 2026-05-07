"""
Intro to Manim — 06: Import Assets
Covers: ImageMobject, SVGMobject, sounds.
Source: https://docs.devtaoism.com/docs/html/contents/_6_assets.html

Render: manim -pql 06_assets.py AssetsScene
"""
from manim import *


class AssetsScene(Scene):
    def construct(self):
        self.camera.background_color = "#0d0d0d"

        title = Text("06: Import Assets", font_size=28, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # ── Images ───────────────────────────────
        section = Text("Images & SVG", font_size=22, color=BLUE)
        section.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(section))

        code = Code(
            code=(
                '# Raster image (PNG, JPG)\n'
                'img = ImageMobject("photo.png")\n'
                'img.scale(0.5)\n'
                'img.to_edge(LEFT)\n\n'
                '# SVG (vector)\n'
                'svg = SVGMobject("icon.svg")\n'
                'svg.set_color(WHITE)\n'
                'svg.to_edge(RIGHT)'
            ),
            language="python", font_size=14,
            background="rectangle", style="monokai",
            insert_line_no=False, background_stroke_color="#333",
        )
        code.scale(0.75).move_to(DOWN * 0.5)
        self.play(FadeIn(code))

        note = Text("Place files in same directory or use full path",
                     font_size=14, color=GREY)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

        # ── Sounds ───────────────────────────────
        title2 = Text("Sounds", font_size=22, color=BLUE)
        title2.to_edge(UP)
        self.play(Write(title2))

        code2 = Code(
            code=(
                '# Add sound at current time\n'
                'self.add_sound("click.mp3")\n\n'
                '# Add sound with time offset\n'
                'self.add_sound("music.mp3", time_offset=0.5)'
            ),
            language="python", font_size=14,
            background="rectangle", style="monokai",
            insert_line_no=False, background_stroke_color="#333",
        )
        code2.scale(0.75)
        self.play(FadeIn(code2))

        note2 = Text("Sounds only work in rendered video, not in preview",
                      font_size=14, color=GREY)
        note2.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note2))
        self.wait(2)
