"""
Docker 101 — Episode 01: Images & Containers
Image = blueprint (layers). Container = running instance. Pull, run, ps.

Render: manim -pqh ep01_images_containers.py ImagesContainers
"""
from manim import *
from helpers import *


class ImagesContainers(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.what_is_an_image()
        self.image_layers()
        self.image_to_container()
        self.multiple_containers()
        self.docker_commands()
        self.recap()

    # ── What is an Image? (40s) ──────────────────
    def what_is_an_image(self):
        title = section_title("What is a Docker Image?")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Blueprint analogy
        blueprint = RoundedRectangle(width=4, height=3, corner_radius=0.15,
                                      fill_color="#1a1a2e", fill_opacity=1,
                                      stroke_color=IMAGE_PURPLE, stroke_width=2)
        blueprint.move_to(LEFT * 2.5)
        bp_label = Text("Image\n(Blueprint)", font=FONT, font_size=16,
                        color=IMAGE_PURPLE)
        bp_label.move_to(blueprint.get_center() + UP * 0.5)

        contents = VGroup(
            Text("• Ubuntu 22.04", font=FONT, font_size=11, color=WHITE),
            Text("• Python 3.11", font=FONT, font_size=11, color=WHITE),
            Text("• Flask", font=FONT, font_size=11, color=WHITE),
            Text("• Your app code", font=FONT, font_size=11, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        contents.move_to(blueprint.get_center() + DOWN * 0.4)

        self.play(FadeIn(blueprint), FadeIn(bp_label), run_time=0.5)
        self.play(FadeIn(contents), run_time=0.5)

        note = Text("An image is a read-only template with everything your app needs",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Image Layers (50s) ───────────────────────
    def image_layers(self):
        title = section_title("Images are Made of Layers")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        layers_data = [
            "Ubuntu 22.04 (base)",
            "apt install python3",
            "pip install flask",
            "COPY app.py /app/",
            "CMD python app.py",
        ]
        layers = image_layers(layers_data, width=5, layer_height=0.5)
        layers.shift(DOWN * 0.3)

        # Build layers one by one (bottom to top)
        for i, layer in enumerate(layers):
            self.play(FadeIn(layer, shift=UP * 0.2), run_time=0.4)
            self.wait(0.3)

        # Show that layers are cached
        cache_note = Text("Each layer is cached — rebuild only what changed",
                          font=FONT, font_size=14, color=CONTAINER_GREEN)
        cache_note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(cache_note), run_time=0.3)

        # Highlight top layer as "changed"
        self.play(layers[-1][0].animate.set_fill(CONTAINER_YELLOW, opacity=0.9),
                  run_time=0.3)
        changed = Text("← only this rebuilds", font=FONT, font_size=12,
                       color=CONTAINER_YELLOW)
        changed.next_to(layers[-1], RIGHT, buff=0.3)
        self.play(FadeIn(changed), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Image → Container (50s) ──────────────────
    def image_to_container(self):
        title = section_title("Image → Container")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Image (left)
        img = RoundedRectangle(width=2.5, height=2, corner_radius=0.1,
                                fill_color="#1a1a2e", fill_opacity=1,
                                stroke_color=IMAGE_PURPLE, stroke_width=2)
        img.move_to(LEFT * 4)
        img_label = Text("Image\n(read-only)", font=FONT, font_size=13,
                         color=IMAGE_PURPLE)
        img_label.move_to(img.get_center())
        self.play(FadeIn(img), FadeIn(img_label), run_time=0.3)

        # docker run command
        cmd = cmd_text("docker run myapp")
        cmd.move_to(UP * 2.5)
        self.play(Write(cmd), run_time=0.5)

        # Arrow
        arrow = Arrow(LEFT * 2.5, RIGHT * 0.5, color=DOCKER_BLUE)
        run_label = Text("docker run", font=FONT, font_size=12, color=DOCKER_BLUE)
        run_label.next_to(arrow, UP, buff=0.1)
        self.play(GrowArrow(arrow), FadeIn(run_label), run_time=0.5)

        # Container appears (right)
        cont = container_box("myapp", CONTAINER_GREEN, 2.5, 2)
        cont.move_to(RIGHT * 3)

        # Running indicator
        running = Text("● RUNNING", font=FONT, font_size=11, color=CONTAINER_GREEN)
        running.next_to(cont, UP, buff=0.15)

        self.play(FadeIn(cont, shift=RIGHT * 0.3), FadeIn(running), run_time=0.5)

        # Writable layer on top
        rw_layer = Rectangle(width=2.3, height=0.3, fill_color=CONTAINER_GREEN,
                             fill_opacity=0.3, stroke_color=CONTAINER_GREEN,
                             stroke_width=1)
        rw_layer.move_to(cont[0].get_top() + DOWN * 0.2)
        rw_label = Text("writable layer", font=FONT, font_size=9, color=CONTAINER_GREEN)
        rw_label.move_to(rw_layer.get_center())
        self.play(FadeIn(rw_layer), FadeIn(rw_label), run_time=0.3)

        note = Text("Container = Image + writable layer + running process",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Multiple Containers from One Image (40s) ─
    def multiple_containers(self):
        title = section_title("One Image → Many Containers")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Image in center-left
        img = RoundedRectangle(width=2, height=1.5, corner_radius=0.1,
                                fill_color="#1a1a2e", fill_opacity=1,
                                stroke_color=IMAGE_PURPLE, stroke_width=2)
        img.move_to(LEFT * 4 + DOWN * 0.3)
        img_label = Text("nginx\nimage", font=FONT, font_size=12, color=IMAGE_PURPLE)
        img_label.move_to(img.get_center())
        self.play(FadeIn(img), FadeIn(img_label), run_time=0.3)

        # Spawn 3 containers
        colors = [CONTAINER_GREEN, DOCKER_BLUE, CONTAINER_YELLOW]
        names = ["web-1", "web-2", "web-3"]
        containers = []

        for i in range(3):
            arrow = Arrow(img.get_right() + RIGHT * 0.1,
                          RIGHT * (0.5 + i * 0) + UP * (1 - i * 1.2) + LEFT * 0.5,
                          color=colors[i], buff=0.3, stroke_width=2)
            cont = container_box(names[i], colors[i], 2, 0.8)
            cont.move_to(RIGHT * 2 + UP * (1 - i * 1.2))
            containers.append(cont)

            self.play(GrowArrow(arrow), FadeIn(cont, shift=RIGHT * 0.2),
                      run_time=0.4)

        note = Text("Same image, 3 independent containers — each with its own state",
                     font=FONT, font_size=13, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Docker Commands (50s) ────────────────────
    def docker_commands(self):
        title = section_title("Essential Commands")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        commands = [
            ("docker pull nginx", "Download an image from Docker Hub"),
            ("docker run nginx", "Create + start a container"),
            ("docker ps", "List running containers"),
            ("docker stop <id>", "Stop a running container"),
            ("docker rm <id>", "Remove a stopped container"),
            ("docker images", "List downloaded images"),
        ]

        items = VGroup()
        for cmd_str, desc in commands:
            cmd_t = Text(f"$ {cmd_str}", font=FONT, font_size=15, color=CONTAINER_GREEN)
            desc_t = Text(f"  {desc}", font=FONT, font_size=13, color=GREY_DIM)
            row = VGroup(cmd_t, desc_t).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
            items.add(row)

        items.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        items.move_to(ORIGIN + DOWN * 0.3)

        for item in items:
            self.play(FadeIn(item, shift=RIGHT * 0.3), run_time=0.3)
            self.wait(0.3)

        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text("• Image = read-only template (layers)",
                 font=FONT, font_size=16, color=WHITE),
            Text("• Container = running instance of an image",
                 font=FONT, font_size=16, color=WHITE),
            Text("• One image → many containers",
                 font=FONT, font_size=16, color=WHITE),
            Text("• Layers are cached (fast rebuilds)",
                 font=FONT, font_size=16, color=WHITE),
            Text("• docker pull / run / ps / stop / rm",
                 font=FONT, font_size=16, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
