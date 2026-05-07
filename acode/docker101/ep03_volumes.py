"""
Docker 101 — Episode 03: Volumes
Container dies → data gone. Volumes = persistent storage.

Render: manim -pqh ep03_volumes.py VolumesScene
"""
from manim import *
from helpers import *


class VolumesScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.the_problem()
        self.what_is_a_volume()
        self.named_volumes()
        self.bind_mounts()
        self.recap()

    # ── The Problem (40s) ────────────────────────
    def the_problem(self):
        title = section_title("The Problem: Data Disappears")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Container with data inside
        cont = container_box("postgres", DOCKER_BLUE, 3, 1.8)
        cont.move_to(LEFT * 0.5)

        data = VGroup(
            Text("users.db", font=FONT, font_size=12, color=CONTAINER_GREEN),
            Text("orders.db", font=FONT, font_size=12, color=CONTAINER_GREEN),
            Text("config.json", font=FONT, font_size=12, color=CONTAINER_GREEN),
        ).arrange(DOWN, buff=0.08)
        data.move_to(cont.get_center() + DOWN * 0.3)

        self.play(FadeIn(cont), FadeIn(data), run_time=0.5)
        self.wait(1)

        # docker rm
        cmd = cmd_text("docker rm postgres")
        cmd.to_edge(UP, buff=1.5)
        self.play(Write(cmd), run_time=0.3)

        # Container explodes
        self.play(cont.animate.set_opacity(0.2), data.animate.set_opacity(0.2),
                  run_time=0.3)
        boom = Text("💥 Container removed", font=FONT, font_size=18, color=CONTAINER_RED)
        boom.next_to(cont, RIGHT, buff=0.5)
        self.play(FadeIn(boom), run_time=0.3)

        gone = Text("Data is GONE. Forever.", font=FONT, font_size=18, color=CONTAINER_RED)
        gone.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(gone), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── What is a Volume? (50s) ──────────────────
    def what_is_a_volume(self):
        title = section_title("Volumes: Data That Survives")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Container
        cont = container_box("postgres", DOCKER_BLUE, 2.5, 1.5)
        cont.move_to(UP * 0.5)

        # Volume (external storage)
        vol = RoundedRectangle(width=2.5, height=1, corner_radius=0.1,
                                fill_color="#2a1a00", fill_opacity=1,
                                stroke_color=VOLUME_ORANGE, stroke_width=2)
        vol.move_to(DOWN * 1.8)
        vol_label = Text("Volume\n(pgdata)", font=FONT, font_size=13, color=VOLUME_ORANGE)
        vol_label.move_to(vol.get_center())

        # Connection
        pipe = DashedLine(cont[0].get_bottom(), vol.get_top(),
                          color=VOLUME_ORANGE, dash_length=0.1)
        mount_label = Text("/var/lib/postgresql/data", font=FONT,
                           font_size=10, color=GREY_DIM)
        mount_label.next_to(pipe, RIGHT, buff=0.1)

        self.play(FadeIn(cont), run_time=0.3)
        self.play(FadeIn(vol), FadeIn(vol_label), run_time=0.3)
        self.play(Create(pipe), FadeIn(mount_label), run_time=0.5)

        # Container dies, volume stays
        self.wait(1)
        self.play(FadeOut(cont), run_time=0.3)

        survives = Text("Container gone. Volume survives. ✓", font=FONT,
                        font_size=16, color=CONTAINER_GREEN)
        survives.move_to(UP * 0.5)
        self.play(FadeIn(survives), run_time=0.3)

        # New container connects to same volume
        cont2 = container_box("postgres-2", CONTAINER_GREEN, 2.5, 1.5)
        cont2.move_to(UP * 0.5)
        self.play(FadeOut(survives), FadeIn(cont2), run_time=0.3)

        reconnect = Text("New container → same data ✓", font=FONT,
                         font_size=14, color=CONTAINER_GREEN)
        reconnect.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(reconnect), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Named Volumes (40s) ──────────────────────
    def named_volumes(self):
        title = section_title("Named Volumes")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmd = cmd_text("docker run -v pgdata:/var/lib/postgresql/data postgres")
        cmd.scale(0.7).move_to(UP * 1.5)
        self.play(Write(cmd), run_time=0.5)

        # Break down the -v flag
        parts = VGroup(
            Text("-v", font=FONT, font_size=18, color=DOCKER_BLUE),
            Text("pgdata", font=FONT, font_size=18, color=VOLUME_ORANGE),
            Text(":", font=FONT, font_size=18, color=WHITE),
            Text("/var/lib/postgresql/data", font=FONT, font_size=16, color=GREY_DIM),
        ).arrange(RIGHT, buff=0.1)
        parts.move_to(UP * 0.3)

        label1 = Text("volume name", font=FONT, font_size=11, color=VOLUME_ORANGE)
        label1.next_to(parts[1], DOWN, buff=0.15)
        label2 = Text("path inside container", font=FONT, font_size=11, color=GREY_DIM)
        label2.next_to(parts[3], DOWN, buff=0.15)

        self.play(FadeIn(parts), run_time=0.3)
        self.play(FadeIn(label1), FadeIn(label2), run_time=0.3)

        note = Text("Docker manages the volume — stored in /var/lib/docker/volumes/",
                     font=FONT, font_size=13, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Bind Mounts (40s) ────────────────────────
    def bind_mounts(self):
        title = section_title("Bind Mounts (for Development)")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmd = cmd_text("docker run -v $(pwd):/app myapp")
        cmd.scale(0.75).move_to(UP * 1.5)
        self.play(Write(cmd), run_time=0.5)

        # Host folder
        host = RoundedRectangle(width=2.5, height=1.5, corner_radius=0.1,
                                 fill_color=DARK_CELL, fill_opacity=1,
                                 stroke_color=CONTAINER_GREEN, stroke_width=2)
        host.move_to(LEFT * 3 + DOWN * 0.5)
        host_label = Text("Your Laptop\n./src/", font=FONT, font_size=12,
                          color=CONTAINER_GREEN)
        host_label.move_to(host.get_center())

        # Container
        cont = container_box("myapp", DOCKER_BLUE, 2.5, 1.5)
        cont.move_to(RIGHT * 3 + DOWN * 0.5)

        # Two-way arrow
        arrow = DoubleArrow(host.get_right() + RIGHT * 0.1,
                            cont[0].get_left() + LEFT * 0.1,
                            color=VOLUME_ORANGE, buff=0.2)
        sync = Text("live sync", font=FONT, font_size=11, color=VOLUME_ORANGE)
        sync.next_to(arrow, UP, buff=0.1)

        self.play(FadeIn(host), FadeIn(host_label), FadeIn(cont), run_time=0.3)
        self.play(GrowArrow(arrow), FadeIn(sync), run_time=0.5)

        note = Text("Edit code on your laptop → changes appear in container instantly",
                     font=FONT, font_size=13, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text("• Container data is ephemeral (dies with container)",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Volumes persist data outside the container",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Named volume: -v name:/path (Docker manages)",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Bind mount: -v ./src:/app (live sync for dev)",
                 font=FONT, font_size=15, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
