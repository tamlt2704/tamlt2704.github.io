"""
Docker 101 — Episode 09: Docker in Production
Single container → scaling → orchestration. The big picture.

Render: manim -pqh ep09_production.py ProductionScene
"""
from manim import *
from helpers import *


class ProductionScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.single_container()
        self.scaling_up()
        self.load_balancer()
        self.orchestration()
        self.the_full_picture()
        self.recap()

    def single_container(self):
        title = section_title("Stage 1: One Container")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        server = RoundedRectangle(width=4, height=3, corner_radius=0.15,
                                   fill_color="#111", fill_opacity=1,
                                   stroke_color=BORDER, stroke_width=1)
        server.shift(DOWN * 0.3)
        server_label = Text("Server", font=FONT, font_size=12, color=GREY_DIM)
        server_label.next_to(server, UP, buff=0.1)

        cont = container_box("api", CONTAINER_GREEN, 2.5, 1)
        cont.move_to(server.get_center())

        self.play(FadeIn(server), FadeIn(server_label), FadeIn(cont), run_time=0.5)

        note = Text("Works for small traffic. But what if 10,000 users hit it?",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def scaling_up(self):
        title = section_title("Stage 2: Scale Up (More Containers)")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmd = cmd_text("docker compose up --scale api=3")
        cmd.scale(0.7).move_to(UP * 1.5)
        self.play(Write(cmd), run_time=0.5)

        containers = VGroup()
        for i in range(3):
            c = container_box(f"api-{i+1}", CONTAINER_GREEN, 2, 0.8)
            c.move_to([i * 2.5 - 2.5, 0, 0])
            containers.add(c)

        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in containers],
                  lag_ratio=0.2), run_time=0.8)

        note = Text("3 copies of the same container. But who routes traffic?",
                     font=FONT, font_size=14, color=CONTAINER_YELLOW)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def load_balancer(self):
        title = section_title("Stage 3: Load Balancer")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Users
        users = VGroup()
        for i in range(3):
            u = Text("👤", font_size=24)
            u.move_to(LEFT * 5 + UP * (0.8 - i * 0.8))
            users.add(u)
        self.play(FadeIn(users), run_time=0.3)

        # Load balancer
        lb = RoundedRectangle(width=2, height=2, corner_radius=0.1,
                               fill_color=DARK_CELL, fill_opacity=1,
                               stroke_color=DOCKER_BLUE, stroke_width=2)
        lb.move_to(LEFT * 1.5)
        lb_label = Text("nginx\n(LB)", font=FONT, font_size=12, color=DOCKER_BLUE)
        lb_label.move_to(lb.get_center())
        self.play(FadeIn(lb), FadeIn(lb_label), run_time=0.3)

        # Arrows from users to LB
        for u in users:
            a = Arrow(u.get_right(), lb.get_left(), color=GREY_DIM,
                      buff=0.15, stroke_width=1.5)
            self.play(GrowArrow(a), run_time=0.15)

        # Containers
        containers = VGroup()
        for i in range(3):
            c = container_box(f"api-{i+1}", CONTAINER_GREEN, 1.8, 0.7)
            c.move_to([RIGHT * 2.5, UP * (0.8 - i * 0.8), 0])
            containers.add(c)

            a = Arrow(lb.get_right(), c[0].get_left(), color=CONTAINER_GREEN,
                      buff=0.15, stroke_width=1.5)
            self.play(FadeIn(c), GrowArrow(a), run_time=0.2)

        note = Text("Load balancer distributes requests across containers",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def orchestration(self):
        title = section_title("Stage 4: Orchestration")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Multiple servers
        servers = VGroup()
        for i in range(3):
            server = RoundedRectangle(width=3, height=2.5, corner_radius=0.1,
                                       fill_color="#111", fill_opacity=1,
                                       stroke_color=BORDER, stroke_width=1)
            server.move_to([i * 3.3 - 3.3, -0.3, 0])
            s_label = Text(f"Server {i+1}", font=FONT, font_size=10, color=GREY_DIM)
            s_label.next_to(server, UP, buff=0.08)

            # 2 containers per server
            for j in range(2):
                c = container_box(f"api", CONTAINER_GREEN, 1.2, 0.5)
                c.scale(0.8).move_to(server.get_center() + UP * (0.3 - j * 0.7))
                server.add(c)

            servers.add(VGroup(server, s_label))

        self.play(LaggedStart(*[FadeIn(s) for s in servers], lag_ratio=0.2),
                  run_time=1)

        # Orchestrator label
        orch = Text("Kubernetes / Docker Swarm", font=FONT, font_size=16,
                     color=DOCKER_BLUE)
        orch.to_edge(DOWN, buff=0.8)
        orch_desc = Text("Manages containers across multiple servers automatically",
                         font=FONT, font_size=13, color=GREY_DIM)
        orch_desc.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(orch), FadeIn(orch_desc), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def the_full_picture(self):
        title = section_title("The Journey")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        stages = VGroup(
            Text("1 container", font=FONT, font_size=16, color=GREY_DIM),
            Text("→", font=FONT, font_size=16, color=GREY_DIM),
            Text("3 containers", font=FONT, font_size=16, color=CONTAINER_GREEN),
            Text("→", font=FONT, font_size=16, color=GREY_DIM),
            Text("+ load balancer", font=FONT, font_size=16, color=DOCKER_BLUE),
            Text("→", font=FONT, font_size=16, color=GREY_DIM),
            Text("orchestration", font=FONT, font_size=16, color=CONTAINER_YELLOW),
        ).arrange(RIGHT, buff=0.2)
        stages.move_to(ORIGIN)
        self.play(LaggedStart(*[FadeIn(s) for s in stages], lag_ratio=0.15),
                  run_time=1.5)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("The Docker 101 Journey:", font=FONT, font_size=24, color=DOCKER_BLUE),
            Text("Ep 0: What is Docker (containers vs VMs)", font=FONT, font_size=14, color=WHITE),
            Text("Ep 1: Images & Containers (pull, run, ps)", font=FONT, font_size=14, color=WHITE),
            Text("Ep 2: Dockerfile (FROM, COPY, RUN, CMD)", font=FONT, font_size=14, color=WHITE),
            Text("Ep 3: Volumes (persistent data)", font=FONT, font_size=14, color=WHITE),
            Text("Ep 4: Networking (bridge, ports)", font=FONT, font_size=14, color=WHITE),
            Text("Ep 5: Docker Compose (multi-service)", font=FONT, font_size=14, color=WHITE),
            Text("Ep 6: Multi-stage Builds (slim images)", font=FONT, font_size=14, color=WHITE),
            Text("Ep 7: Registry (push, pull, tags)", font=FONT, font_size=14, color=WHITE),
            Text("Ep 8: Health Checks & Logs", font=FONT, font_size=14, color=WHITE),
            Text("Ep 9: Production (scaling, orchestration)", font=FONT, font_size=14, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.1), run_time=2)
        self.wait(4)
