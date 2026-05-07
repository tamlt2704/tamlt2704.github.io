"""
Docker 101 — Episode 07: Docker Hub & Registry
Push/pull images. Tags. Private registries.

Render: manim -pqh ep07_registry.py RegistryScene
"""
from manim import *
from helpers import *


class RegistryScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.what_is_registry()
        self.push_pull()
        self.tags()
        self.recap()

    def what_is_registry(self):
        title = section_title("Docker Hub = App Store for Images")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Warehouse with shelves
        warehouse = RoundedRectangle(width=8, height=3.5, corner_radius=0.15,
                                      fill_color="#111", fill_opacity=1,
                                      stroke_color=DOCKER_BLUE, stroke_width=2)
        warehouse.shift(DOWN * 0.3)
        wh_label = Text("Docker Hub (hub.docker.com)", font=FONT,
                        font_size=14, color=DOCKER_BLUE)
        wh_label.next_to(warehouse, UP, buff=0.15)
        self.play(FadeIn(warehouse), FadeIn(wh_label), run_time=0.3)

        # Image boxes on shelves
        images = ["nginx", "postgres", "redis", "node", "python", "ubuntu"]
        boxes = VGroup()
        for i, name in enumerate(images):
            box = RoundedRectangle(width=1.8, height=0.7, corner_radius=0.08,
                                    fill_color=DARK_CELL, fill_opacity=1,
                                    stroke_color=IMAGE_PURPLE, stroke_width=1)
            lbl = Text(name, font=FONT, font_size=12, color=IMAGE_PURPLE)
            lbl.move_to(box.get_center())
            g = VGroup(box, lbl)
            row, col = divmod(i, 3)
            g.move_to([col * 2.2 - 2.2, 0.5 - row * 1, 0])
            boxes.add(g)

        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in boxes],
                  lag_ratio=0.1), run_time=1)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def push_pull(self):
        title = section_title("Push & Pull")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Your machine
        local = container_box("myapp\n(local)", CONTAINER_GREEN, 2.5, 1.2)
        local.move_to(LEFT * 3.5 + DOWN * 0.3)

        # Docker Hub
        hub = RoundedRectangle(width=3, height=1.5, corner_radius=0.1,
                                fill_color="#111", fill_opacity=1,
                                stroke_color=DOCKER_BLUE, stroke_width=2)
        hub.move_to(RIGHT * 3.5 + DOWN * 0.3)
        hub_label = Text("Docker Hub", font=FONT, font_size=14, color=DOCKER_BLUE)
        hub_label.move_to(hub.get_center())

        self.play(FadeIn(local), FadeIn(hub), FadeIn(hub_label), run_time=0.3)

        # Push arrow
        push = Arrow(local[0].get_right(), hub.get_left(), color=CONTAINER_GREEN, buff=0.2)
        push_label = Text("docker push", font=FONT, font_size=11, color=CONTAINER_GREEN)
        push_label.next_to(push, UP, buff=0.08)
        self.play(GrowArrow(push), FadeIn(push_label), run_time=0.5)
        self.wait(1)

        # Pull arrow
        pull = Arrow(hub.get_left() + DOWN * 0.3, local[0].get_right() + DOWN * 0.3,
                     color=DOCKER_BLUE, buff=0.2)
        pull_label = Text("docker pull", font=FONT, font_size=11, color=DOCKER_BLUE)
        pull_label.next_to(pull, DOWN, buff=0.08)
        self.play(GrowArrow(pull), FadeIn(pull_label), run_time=0.5)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def tags(self):
        title = section_title("Tags = Versions")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        tags_data = [
            ("python:3.11", "Specific version"),
            ("python:3.11-slim", "Smaller variant"),
            ("python:3.11-alpine", "Smallest (~50 MB)"),
            ("python:latest", "Most recent (risky!)"),
        ]
        items = VGroup()
        for tag, desc in tags_data:
            tag_t = Text(tag, font=FONT, font_size=16, color=IMAGE_PURPLE)
            desc_t = Text(f"  {desc}", font=FONT, font_size=13, color=GREY_DIM)
            row = VGroup(tag_t, desc_t).arrange(RIGHT, buff=0.1)
            items.add(row)
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        items.move_to(DOWN * 0.3)

        self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items],
                  lag_ratio=0.2), run_time=1)

        warning = Text("⚠ Always pin versions. Never use :latest in production.",
                       font=FONT, font_size=14, color=CONTAINER_YELLOW)
        warning.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(warning), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text("• Docker Hub = public image registry",
                 font=FONT, font_size=15, color=WHITE),
            Text("• docker push / pull to share images",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Tags = versions (pin them!)",
                 font=FONT, font_size=15, color=WHITE),
            Text("• slim/alpine variants for smaller images",
                 font=FONT, font_size=15, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
