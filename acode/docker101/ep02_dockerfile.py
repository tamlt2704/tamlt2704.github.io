"""
Docker 101 — Episode 02: The Dockerfile
Lines of code → layers building on top of each other.

Render: manim -pqh ep02_dockerfile.py DockerfileScene
"""
from manim import *
from helpers import *


class DockerfileScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.what_is_dockerfile()
        self.line_by_line()
        self.build_command()
        self.layer_cache()
        self.best_practices()
        self.recap()

    # ── What is a Dockerfile? (30s) ──────────────
    def what_is_dockerfile(self):
        title = section_title("What is a Dockerfile?")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        analogy = VGroup(
            Text("Recipe", font=FONT, font_size=24, color=CONTAINER_YELLOW),
            Text("→", font=FONT, font_size=24, color=GREY_DIM),
            Text("Cake", font=FONT, font_size=24, color=CONTAINER_GREEN),
        ).arrange(RIGHT, buff=0.5)
        analogy.shift(UP * 0.5)

        analogy2 = VGroup(
            Text("Dockerfile", font=FONT, font_size=24, color=IMAGE_PURPLE),
            Text("→", font=FONT, font_size=24, color=GREY_DIM),
            Text("Image", font=FONT, font_size=24, color=DOCKER_BLUE),
        ).arrange(RIGHT, buff=0.5)
        analogy2.shift(DOWN * 0.5)

        self.play(FadeIn(analogy), run_time=0.5)
        self.wait(0.5)
        self.play(FadeIn(analogy2), run_time=0.5)

        note = Text("A Dockerfile is a text file with instructions to build an image",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Line by Line (80s) ──────────────────────
    def line_by_line(self):
        title = section_title("Dockerfile → Layers")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Dockerfile on the left
        lines = [
            ("FROM", "python:3.11-slim"),
            ("WORKDIR", "/app"),
            ("COPY", "requirements.txt ."),
            ("RUN", "pip install -r requirements.txt"),
            ("COPY", ". ."),
            ("CMD", '["python", "app.py"]'),
        ]

        code_lines = VGroup()
        for i, (keyword, arg) in enumerate(lines):
            kw = Text(keyword, font=FONT, font_size=14, color=DOCKER_BLUE)
            ar = Text(f" {arg}", font=FONT, font_size=14, color=WHITE)
            line = VGroup(kw, ar).arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
            code_lines.add(line)

        code_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        code_lines.to_edge(LEFT, buff=0.5).shift(DOWN * 0.3)

        # File header
        file_label = Text("Dockerfile", font=FONT, font_size=12, color=GREY_DIM)
        file_label.next_to(code_lines, UP, aligned_edge=LEFT, buff=0.2)
        code_bg = RoundedRectangle(
            width=code_lines.width + 0.6, height=code_lines.height + 0.8,
            corner_radius=0.1, fill_color="#111", fill_opacity=1,
            stroke_color=BORDER, stroke_width=1)
        code_bg.move_to(code_lines.get_center() + UP * 0.15)

        self.play(FadeIn(code_bg), FadeIn(file_label), run_time=0.3)

        # Layers on the right (build as each line appears)
        layer_colors = ["#4c1d95", "#5b21b6", "#6d28d9", "#7c3aed", "#9333ea", "#a855f7"]
        layer_labels = [
            "python:3.11-slim",
            "workdir /app",
            "copy requirements.txt",
            "pip install ...",
            "copy app code",
            "cmd: python app.py",
        ]

        layer_group = VGroup()
        layer_y_start = -2

        for i, (line, l_label) in enumerate(zip(code_lines, layer_labels)):
            # Show the Dockerfile line
            self.play(FadeIn(line), run_time=0.3)
            self.wait(0.3)

            # Build the corresponding layer
            rect = Rectangle(width=4, height=0.4, fill_color=layer_colors[i],
                             fill_opacity=0.8, stroke_color=layer_colors[i],
                             stroke_width=1)
            rect.move_to([RIGHT * 3.5, layer_y_start + i * 0.42, 0])
            lbl = Text(l_label, font=FONT, font_size=10, color=WHITE)
            lbl.move_to(rect.get_center())
            layer = VGroup(rect, lbl)
            layer_group.add(layer)

            # Arrow from code line to layer
            self.play(FadeIn(layer, shift=UP * 0.15), run_time=0.3)

        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── docker build (30s) ───────────────────────
    def build_command(self):
        title = section_title("docker build")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmd = cmd_text("docker build -t myapp .")
        cmd.move_to(UP * 1.5)
        self.play(Write(cmd), run_time=0.5)

        # Explain flags
        flags = VGroup(
            Text("-t myapp  → name (tag) the image", font=FONT, font_size=14, color=GREY_DIM),
            Text(".         → build context (current dir)", font=FONT, font_size=14, color=GREY_DIM),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        flags.next_to(cmd, DOWN, buff=0.5)
        self.play(FadeIn(flags), run_time=0.3)

        # Build progress
        progress = VGroup()
        steps = ["Step 1/6: FROM python:3.11-slim",
                 "Step 2/6: WORKDIR /app",
                 "Step 3/6: COPY requirements.txt",
                 "Step 4/6: RUN pip install",
                 "Step 5/6: COPY . .",
                 "Step 6/6: CMD"]
        for i, step in enumerate(steps):
            t = Text(step, font=FONT, font_size=12,
                     color=CONTAINER_GREEN if i < 5 else DOCKER_BLUE)
            progress.add(t)
        progress.arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        progress.move_to(DOWN * 1)

        for step in progress:
            self.play(FadeIn(step), run_time=0.15)

        done = Text("Successfully built myapp ✓", font=FONT, font_size=16,
                     color=CONTAINER_GREEN)
        done.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(done), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Layer Cache (40s) ────────────────────────
    def layer_cache(self):
        title = section_title("Layer Caching — Why Order Matters")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show layers
        labels = ["FROM python", "COPY requirements.txt", "RUN pip install",
                  "COPY app code", "CMD"]
        layers = image_layers(labels, width=5, layer_height=0.45)
        layers.shift(DOWN * 0.3)
        self.play(FadeIn(layers), run_time=0.5)

        # Scenario: you change app.py
        change = Text("You edit app.py →", font=FONT, font_size=14, color=CONTAINER_YELLOW)
        change.to_edge(LEFT, buff=0.3).shift(DOWN * 0.3)
        self.play(FadeIn(change), run_time=0.3)

        # Bottom 3 layers: CACHED
        for i in range(3):
            cached = Text("CACHED ✓", font=FONT, font_size=10, color=CONTAINER_GREEN)
            cached.next_to(layers[i], RIGHT, buff=0.3)
            self.play(FadeIn(cached), run_time=0.15)

        # Top 2 layers: REBUILD
        for i in range(3, 5):
            rebuild = Text("REBUILD", font=FONT, font_size=10, color=CONTAINER_YELLOW)
            rebuild.next_to(layers[i], RIGHT, buff=0.3)
            self.play(layers[i][0].animate.set_fill(CONTAINER_YELLOW, opacity=0.8),
                      FadeIn(rebuild), run_time=0.2)

        note = Text("Put rarely-changing layers first → faster builds",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Best Practices (30s) ─────────────────────
    def best_practices(self):
        title = section_title("Dockerfile Best Practices")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        tips = VGroup(
            Text("✓ Use slim/alpine base images (smaller)", font=FONT,
                 font_size=15, color=CONTAINER_GREEN),
            Text("✓ COPY requirements first, then code (cache)", font=FONT,
                 font_size=15, color=CONTAINER_GREEN),
            Text("✓ Combine RUN commands (fewer layers)", font=FONT,
                 font_size=15, color=CONTAINER_GREEN),
            Text("✗ Don't COPY unnecessary files (use .dockerignore)", font=FONT,
                 font_size=15, color=CONTAINER_RED),
            Text("✗ Don't run as root (use USER)", font=FONT,
                 font_size=15, color=CONTAINER_RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        tips.move_to(DOWN * 0.3)

        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.3) for t in tips],
                  lag_ratio=0.2), run_time=1.5)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text("• Dockerfile = recipe for building an image",
                 font=FONT, font_size=16, color=WHITE),
            Text("• Each instruction creates a layer",
                 font=FONT, font_size=16, color=WHITE),
            Text("• FROM, COPY, RUN, CMD — the core instructions",
                 font=FONT, font_size=16, color=WHITE),
            Text("• Layer caching: order matters for speed",
                 font=FONT, font_size=16, color=WHITE),
            Text("• docker build -t name .",
                 font=FONT, font_size=16, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
