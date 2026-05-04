"""
Docker 101 — Episode 06: Multi-stage Builds
Fat image → diet → slim image. Build tools stay behind.

Render: manim -pqh ep06_multistage.py MultistageScene
"""
from manim import *
from helpers import *


class MultistageScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.the_problem()
        self.the_solution()
        self.the_dockerfile()
        self.size_comparison()
        self.recap()

    def the_problem(self):
        title = section_title("The Problem: Fat Images")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        layers = image_layers([
            "Ubuntu 22.04 (80 MB)",
            "gcc, make, cmake (400 MB)",
            "npm install (300 MB)",
            "npm run build (5 MB)",
            "Your app (2 MB)",
        ], width=5, layer_height=0.5)
        layers.shift(DOWN * 0.3)
        self.play(FadeIn(layers), run_time=0.5)

        total = Text("Total: ~787 MB 😱", font=FONT, font_size=20, color=CONTAINER_RED)
        total.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(total), run_time=0.3)

        note = Text("You ship 785 MB of build tools you don't need at runtime",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def the_solution(self):
        title = section_title("Multi-stage: Build, Then Copy")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Stage 1: Build
        build_box = RoundedRectangle(width=4, height=2.5, corner_radius=0.1,
                                      fill_color=DARK_CELL, fill_opacity=1,
                                      stroke_color=CONTAINER_YELLOW, stroke_width=2)
        build_box.move_to(LEFT * 3 + DOWN * 0.3)
        build_label = Text("Stage 1: BUILD", font=FONT, font_size=14, color=CONTAINER_YELLOW)
        build_label.next_to(build_box, UP, buff=0.1)
        build_contents = VGroup(
            Text("Ubuntu + gcc + npm", font=FONT, font_size=11, color=GREY_DIM),
            Text("npm install", font=FONT, font_size=11, color=GREY_DIM),
            Text("npm run build", font=FONT, font_size=11, color=GREY_DIM),
            Text("→ dist/ (5 MB)", font=FONT, font_size=11, color=CONTAINER_GREEN),
        ).arrange(DOWN, buff=0.08)
        build_contents.move_to(build_box.get_center())

        self.play(FadeIn(build_box), FadeIn(build_label), FadeIn(build_contents),
                  run_time=0.5)

        # Arrow: only copy the output
        arrow = Arrow(build_box.get_right(), RIGHT * 0.5, color=CONTAINER_GREEN, buff=0.2)
        copy_label = Text("COPY --from=build\n/app/dist → /app/",
                          font=FONT, font_size=10, color=CONTAINER_GREEN)
        copy_label.next_to(arrow, UP, buff=0.1)
        self.play(GrowArrow(arrow), FadeIn(copy_label), run_time=0.5)

        # Stage 2: Runtime
        run_box = RoundedRectangle(width=3, height=1.5, corner_radius=0.1,
                                    fill_color=DARK_CELL, fill_opacity=1,
                                    stroke_color=CONTAINER_GREEN, stroke_width=2)
        run_box.move_to(RIGHT * 3.5 + DOWN * 0.3)
        run_label = Text("Stage 2: RUN", font=FONT, font_size=14, color=CONTAINER_GREEN)
        run_label.next_to(run_box, UP, buff=0.1)
        run_contents = VGroup(
            Text("Alpine (5 MB)", font=FONT, font_size=11, color=GREY_DIM),
            Text("nginx", font=FONT, font_size=11, color=GREY_DIM),
            Text("dist/ (5 MB)", font=FONT, font_size=11, color=CONTAINER_GREEN),
        ).arrange(DOWN, buff=0.08)
        run_contents.move_to(run_box.get_center())

        self.play(FadeIn(run_box), FadeIn(run_label), FadeIn(run_contents),
                  run_time=0.5)

        total = Text("Final image: ~25 MB ✓", font=FONT, font_size=18, color=CONTAINER_GREEN)
        total.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(total), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def the_dockerfile(self):
        title = section_title("The Multi-stage Dockerfile")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        lines = [
            ("# Stage 1: Build", GREY_DIM),
            ("FROM node:22 AS build", DOCKER_BLUE),
            ("WORKDIR /app", WHITE),
            ("COPY package*.json ./", WHITE),
            ("RUN npm ci", WHITE),
            ("COPY . .", WHITE),
            ("RUN npm run build", CONTAINER_YELLOW),
            ("", WHITE),
            ("# Stage 2: Runtime", GREY_DIM),
            ("FROM nginx:alpine", CONTAINER_GREEN),
            ("COPY --from=build /app/dist /usr/share/nginx/html", CONTAINER_GREEN),
        ]

        code = VGroup()
        for text, color in lines:
            t = Text(text, font=FONT, font_size=13, color=color)
            code.add(t)
        code.arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        code.move_to(DOWN * 0.3)

        for line in code:
            self.play(FadeIn(line), run_time=0.15)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def size_comparison(self):
        title = section_title("Size Comparison")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Fat bar
        fat = Rectangle(width=7, height=0.6, fill_color=CONTAINER_RED,
                        fill_opacity=0.8, stroke_width=0)
        fat.move_to(UP * 0.5)
        fat_label = Text("Single stage: 787 MB", font=FONT, font_size=14, color=WHITE)
        fat_label.move_to(fat.get_center())

        # Slim bar
        slim = Rectangle(width=0.25, height=0.6, fill_color=CONTAINER_GREEN,
                         fill_opacity=0.8, stroke_width=0)
        slim.align_to(fat, LEFT).shift(DOWN * 1)
        slim_label = Text("Multi-stage: 25 MB", font=FONT, font_size=14, color=WHITE)
        slim_label.next_to(slim, RIGHT, buff=0.2)

        self.play(GrowFromEdge(fat, LEFT), FadeIn(fat_label), run_time=0.5)
        self.play(GrowFromEdge(slim, LEFT), FadeIn(slim_label), run_time=0.5)

        reduction = Text("97% smaller 🎉", font=FONT, font_size=22, color=CONTAINER_GREEN)
        reduction.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(reduction), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text("• Single-stage images include build tools (huge)",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Multi-stage: build in one stage, copy output to another",
                 font=FONT, font_size=15, color=WHITE),
            Text("• COPY --from=build copies between stages",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Final image: only runtime + your app",
                 font=FONT, font_size=15, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
