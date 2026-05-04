"""
Docker 101 — Episode 04: Networking
Containers as houses, networks as roads. Port mapping, bridge networks.

Render: manim -pqh ep04_networking.py NetworkingScene
"""
from manim import *
from helpers import *


class NetworkingScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.the_problem()
        self.bridge_network()
        self.port_mapping()
        self.custom_network()
        self.recap()

    # ── The Problem (35s) ────────────────────────
    def the_problem(self):
        title = section_title("The Problem: Containers Are Isolated")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        web = container_box("web", CONTAINER_GREEN, 2, 1.2)
        web.move_to(LEFT * 3)
        api = container_box("api", DOCKER_BLUE, 2, 1.2)
        api.move_to(ORIGIN)
        db = container_box("postgres", CONTAINER_YELLOW, 2, 1.2)
        db.move_to(RIGHT * 3)

        self.play(FadeIn(web), FadeIn(api), FadeIn(db), run_time=0.5)

        # X marks — can't talk
        for pair in [(web, api), (api, db)]:
            mid = (pair[0].get_center() + pair[1].get_center()) / 2
            x_mark = Text("✗", font=FONT, font_size=24, color=CONTAINER_RED)
            x_mark.move_to(mid + UP * 0.3)
            self.play(FadeIn(x_mark), run_time=0.2)

        note = Text("By default, containers can't see each other",
                     font=FONT, font_size=15, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Bridge Network (50s) ─────────────────────
    def bridge_network(self):
        title = section_title("Bridge Network")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Network "road"
        road = RoundedRectangle(width=9, height=0.5, corner_radius=0.1,
                                 fill_color="#0a2a1a", fill_opacity=1,
                                 stroke_color=NETWORK_TEAL, stroke_width=1.5)
        road.move_to(DOWN * 0.5)
        road_label = Text("bridge network (my-network)", font=FONT,
                          font_size=12, color=NETWORK_TEAL)
        road_label.next_to(road, DOWN, buff=0.15)

        self.play(FadeIn(road), FadeIn(road_label), run_time=0.3)

        # Containers connected to the network
        containers = []
        names = ["web", "api", "db"]
        colors = [CONTAINER_GREEN, DOCKER_BLUE, CONTAINER_YELLOW]
        for i, (name, color) in enumerate(zip(names, colors)):
            cont = container_box(name, color, 2, 1)
            cont.move_to([i * 3 - 3, 1.2, 0])
            containers.append(cont)

            # Connection line to road
            pipe = Line(cont[0].get_bottom(), road.get_top() + RIGHT * (i * 3 - 3),
                        color=NETWORK_TEAL, stroke_width=1.5)
            self.play(FadeIn(cont), Create(pipe), run_time=0.3)

        # Data flowing
        for i in range(2):
            arrow = Arrow(containers[i].get_right() + RIGHT * 0.1,
                          containers[i + 1].get_left() + LEFT * 0.1,
                          color=NETWORK_TEAL, buff=0.3, stroke_width=2)
            self.play(GrowArrow(arrow), run_time=0.3)

        note = Text("Containers on the same network can talk by name: http://api:8080",
                     font=FONT, font_size=13, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Port Mapping (50s) ───────────────────────
    def port_mapping(self):
        title = section_title("Port Mapping: -p host:container")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmd = cmd_text("docker run -p 8080:80 nginx")
        cmd.scale(0.75).move_to(UP * 1.5)
        self.play(Write(cmd), run_time=0.5)

        # Outside world
        world = RoundedRectangle(width=2.5, height=1.5, corner_radius=0.1,
                                  fill_color=DARK_CELL, fill_opacity=1,
                                  stroke_color=GREY_DIM, stroke_width=1)
        world.move_to(LEFT * 4 + DOWN * 0.5)
        world_label = Text("Browser\nlocalhost:8080", font=FONT, font_size=12,
                           color=WHITE)
        world_label.move_to(world.get_center())

        # Host
        host_box = Rectangle(width=5, height=3, fill_color="#111",
                             fill_opacity=1, stroke_color=BORDER, stroke_width=1)
        host_box.move_to(RIGHT * 1.5 + DOWN * 0.5)
        host_label = Text("Host Machine", font=FONT, font_size=11, color=GREY_DIM)
        host_label.move_to(host_box.get_top() + DOWN * 0.2)

        # Container inside host
        cont = container_box("nginx\n:80", CONTAINER_GREEN, 2.5, 1.2)
        cont.move_to(RIGHT * 1.5 + DOWN * 0.8)

        self.play(FadeIn(world), FadeIn(world_label), FadeIn(host_box),
                  FadeIn(host_label), FadeIn(cont), run_time=0.5)

        # Port mapping arrow
        arrow = Arrow(world.get_right(), cont[0].get_left(),
                      color=CONTAINER_GREEN, buff=0.2)
        port_label = Text("8080 → 80", font=FONT, font_size=12, color=CONTAINER_GREEN)
        port_label.next_to(arrow, UP, buff=0.1)
        self.play(GrowArrow(arrow), FadeIn(port_label), run_time=0.5)

        note = Text("Host port 8080 maps to container port 80",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Custom Network (35s) ─────────────────────
    def custom_network(self):
        title = section_title("Creating a Network")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmds = VGroup(
            cmd_text("docker network create my-net"),
            cmd_text("docker run --network my-net --name web nginx"),
            cmd_text("docker run --network my-net --name api node"),
        )
        cmds.scale(0.6).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        cmds.move_to(UP * 0.5)

        for c in cmds:
            self.play(Write(c), run_time=0.4)
            self.wait(0.3)

        note = Text("web can reach api at http://api:3000 (by container name)",
                     font=FONT, font_size=14, color=NETWORK_TEAL)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text("• Containers are isolated by default",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Bridge network connects containers",
                 font=FONT, font_size=15, color=WHITE),
            Text("• -p 8080:80 maps host port to container port",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Containers on same network talk by name",
                 font=FONT, font_size=15, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
