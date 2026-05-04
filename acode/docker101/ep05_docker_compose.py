"""
Docker 101 — Episode 05: Docker Compose
Orchestra conductor — multiple services in one file.

Render: manim -pqh ep05_docker_compose.py DockerCompose
"""
from manim import *
from helpers import *


class DockerCompose(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.the_problem()
        self.the_compose_file()
        self.services_starting()
        self.depends_on()
        self.compose_commands()
        self.recap()

    # ── The Problem (35s) ────────────────────────
    def the_problem(self):
        title = section_title("The Problem: Too Many Commands")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmds = VGroup(
            cmd_text("docker network create app-net"),
            cmd_text("docker run -d --name db --network app-net -v pgdata:/data postgres"),
            cmd_text("docker run -d --name redis --network app-net redis"),
            cmd_text("docker run -d --name api --network app-net -p 8080:8080 myapi"),
            cmd_text("docker run -d --name web --network app-net -p 3000:80 nginx"),
        )
        cmds.scale(0.42).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        cmds.move_to(DOWN * 0.3)

        for c in cmds:
            self.play(FadeIn(c), run_time=0.2)

        note = Text("5 commands. Every time. In the right order. Hope you don't typo.",
                     font=FONT, font_size=14, color=CONTAINER_RED)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── The Compose File (60s) ───────────────────
    def the_compose_file(self):
        title = section_title("docker-compose.yml")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show YAML structure
        yaml_lines = [
            ("services:", WHITE, 0),
            ("  web:", CONTAINER_GREEN, 1),
            ("    image: nginx", GREY_DIM, 2),
            ("    ports: ['3000:80']", GREY_DIM, 2),
            ("  api:", DOCKER_BLUE, 1),
            ("    build: ./api", GREY_DIM, 2),
            ("    ports: ['8080:8080']", GREY_DIM, 2),
            ("  db:", CONTAINER_YELLOW, 1),
            ("    image: postgres", GREY_DIM, 2),
            ("    volumes: ['pgdata:/data']", GREY_DIM, 2),
            ("  redis:", CONTAINER_RED, 1),
            ("    image: redis", GREY_DIM, 2),
        ]

        code_group = VGroup()
        for text, color, indent in yaml_lines:
            t = Text(text, font=FONT, font_size=14, color=color)
            code_group.add(t)
        code_group.arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        code_group.to_edge(LEFT, buff=0.8).shift(DOWN * 0.3)

        code_bg = RoundedRectangle(
            width=code_group.width + 0.6, height=code_group.height + 0.5,
            corner_radius=0.1, fill_color="#111", fill_opacity=1,
            stroke_color=BORDER, stroke_width=1)
        code_bg.move_to(code_group.get_center())

        self.play(FadeIn(code_bg), run_time=0.2)
        for line in code_group:
            self.play(FadeIn(line), run_time=0.12)

        # Visual: 4 containers
        services = VGroup()
        s_data = [("web", CONTAINER_GREEN), ("api", DOCKER_BLUE),
                  ("db", CONTAINER_YELLOW), ("redis", CONTAINER_RED)]
        for i, (name, color) in enumerate(s_data):
            c = container_box(name, color, 1.5, 0.8)
            c.move_to([RIGHT * 4 + UP * (1.2 - i * 0.9)])
            services.add(c)

        self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.3) for s in services],
                  lag_ratio=0.15), run_time=0.8)

        note = Text("One file defines everything. One command runs it all.",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Services Starting (40s) ──────────────────
    def services_starting(self):
        title = section_title("docker compose up")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmd = cmd_text("docker compose up -d")
        cmd.move_to(UP * 1.8)
        self.play(Write(cmd), run_time=0.5)

        # Services start one by one
        s_data = [("db", CONTAINER_YELLOW, "postgres:16"),
                  ("redis", CONTAINER_RED, "redis:7"),
                  ("api", DOCKER_BLUE, "build: ./api"),
                  ("web", CONTAINER_GREEN, "nginx")]

        containers = []
        for i, (name, color, detail) in enumerate(s_data):
            cont = container_box(name, color, 2.5, 0.8)
            cont.move_to([0, 0.8 - i * 1, 0])

            status = Text("● starting...", font=FONT, font_size=10, color=CONTAINER_YELLOW)
            status.next_to(cont, RIGHT, buff=0.3)

            self.play(FadeIn(cont, shift=UP * 0.2), FadeIn(status), run_time=0.3)

            # Change to running
            running = Text("● running", font=FONT, font_size=10, color=CONTAINER_GREEN)
            running.next_to(cont, RIGHT, buff=0.3)
            self.play(Transform(status, running), run_time=0.2)
            containers.append(cont)

        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── depends_on (35s) ─────────────────────────
    def depends_on(self):
        title = section_title("depends_on: Start Order")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Show dependency chain
        db = container_box("db", CONTAINER_YELLOW, 1.8, 0.8)
        db.move_to(LEFT * 3 + DOWN * 0.3)
        api = container_box("api", DOCKER_BLUE, 1.8, 0.8)
        api.move_to(ORIGIN + DOWN * 0.3)
        web = container_box("web", CONTAINER_GREEN, 1.8, 0.8)
        web.move_to(RIGHT * 3 + DOWN * 0.3)

        self.play(FadeIn(db), run_time=0.3)

        a1 = Arrow(db[0].get_right(), api[0].get_left(), color=NETWORK_TEAL, buff=0.15)
        l1 = Text("depends_on", font=FONT, font_size=9, color=NETWORK_TEAL)
        l1.next_to(a1, UP, buff=0.05)
        self.play(GrowArrow(a1), FadeIn(l1), FadeIn(api), run_time=0.4)

        a2 = Arrow(api[0].get_right(), web[0].get_left(), color=NETWORK_TEAL, buff=0.15)
        l2 = Text("depends_on", font=FONT, font_size=9, color=NETWORK_TEAL)
        l2.next_to(a2, UP, buff=0.05)
        self.play(GrowArrow(a2), FadeIn(l2), FadeIn(web), run_time=0.4)

        order = Text("Start order: db → api → web", font=FONT,
                      font_size=16, color=GREY_DIM)
        order.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(order), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Commands (30s) ───────────────────────────
    def compose_commands(self):
        title = section_title("Compose Commands")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmds = VGroup(
            VGroup(cmd_text("docker compose up -d"),
                   Text("  Start all services", font=FONT, font_size=13, color=GREY_DIM)
                   ).arrange(DOWN, aligned_edge=LEFT, buff=0.03),
            VGroup(cmd_text("docker compose down"),
                   Text("  Stop and remove all", font=FONT, font_size=13, color=GREY_DIM)
                   ).arrange(DOWN, aligned_edge=LEFT, buff=0.03),
            VGroup(cmd_text("docker compose logs -f"),
                   Text("  Follow logs from all services", font=FONT, font_size=13, color=GREY_DIM)
                   ).arrange(DOWN, aligned_edge=LEFT, buff=0.03),
            VGroup(cmd_text("docker compose ps"),
                   Text("  List running services", font=FONT, font_size=13, color=GREY_DIM)
                   ).arrange(DOWN, aligned_edge=LEFT, buff=0.03),
        )
        cmds.scale(0.8).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        cmds.move_to(DOWN * 0.3)

        for c in cmds:
            self.play(FadeIn(c, shift=RIGHT * 0.3), run_time=0.3)
            self.wait(0.3)

        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text("• docker-compose.yml defines all services",
                 font=FONT, font_size=15, color=WHITE),
            Text("• docker compose up -d starts everything",
                 font=FONT, font_size=15, color=WHITE),
            Text("• depends_on controls start order",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Networks and volumes auto-created",
                 font=FONT, font_size=15, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
