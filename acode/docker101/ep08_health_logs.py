"""
Docker 101 — Episode 08: Health Checks & Logs
Heartbeat monitor on containers. Log streams. Restart policies.

Render: manim -pqh ep08_health_logs.py HealthLogsScene
"""
from manim import *
from helpers import *


class HealthLogsScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.health_checks()
        self.logs()
        self.restart_policies()
        self.recap()

    def health_checks(self):
        title = section_title("Health Checks")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cont = container_box("api", DOCKER_BLUE, 3, 1.5)
        cont.move_to(LEFT * 1)

        # Heartbeat line
        heart_points = []
        for i in range(20):
            x = i * 0.3 + 1.5
            y = 0.3 * (1 if i % 4 == 1 else (-0.5 if i % 4 == 3 else 0))
            heart_points.append([x, y, 0])

        heartbeat = VMobject(color=CONTAINER_GREEN, stroke_width=2)
        heartbeat.set_points_smoothly(heart_points)

        self.play(FadeIn(cont), run_time=0.3)
        self.play(Create(heartbeat), run_time=1.5)

        # Dockerfile HEALTHCHECK
        code = VGroup(
            Text("HEALTHCHECK --interval=30s \\", font=FONT, font_size=13, color=DOCKER_BLUE),
            Text("  CMD curl -f http://localhost:8080/health", font=FONT, font_size=13, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        code.to_edge(DOWN, buff=1)
        self.play(FadeIn(code), run_time=0.3)

        # Status indicators
        statuses = VGroup(
            Text("healthy ✓", font=FONT, font_size=14, color=CONTAINER_GREEN),
            Text("unhealthy ✗", font=FONT, font_size=14, color=CONTAINER_RED),
            Text("starting ◌", font=FONT, font_size=14, color=CONTAINER_YELLOW),
        ).arrange(RIGHT, buff=0.8)
        statuses.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(statuses), run_time=0.3)
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def logs(self):
        title = section_title("docker logs")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        cmd = cmd_text("docker logs -f api")
        cmd.move_to(UP * 1.5)
        self.play(Write(cmd), run_time=0.3)

        # Streaming log output
        terminal = Rectangle(width=9, height=3, fill_color="#0d0d0d",
                             fill_opacity=1, stroke_color=BORDER, stroke_width=1)
        terminal.shift(DOWN * 0.5)
        self.play(FadeIn(terminal), run_time=0.2)

        log_lines = [
            ("[INFO]  Server started on :8080", CONTAINER_GREEN),
            ("[INFO]  GET /health → 200 (2ms)", GREY_DIM),
            ("[INFO]  POST /jobs → 201 (15ms)", GREY_DIM),
            ("[WARN]  Slow query: 450ms", CONTAINER_YELLOW),
            ("[ERROR] Connection refused: redis:6379", CONTAINER_RED),
            ("[INFO]  Retry 1/3...", GREY_DIM),
            ("[INFO]  Redis connected ✓", CONTAINER_GREEN),
        ]

        for i, (text, color) in enumerate(log_lines):
            t = Text(text, font=FONT, font_size=12, color=color)
            t.move_to(terminal.get_top() + DOWN * (0.3 + i * 0.35))
            t.align_to(terminal, LEFT).shift(RIGHT * 0.2)
            self.play(FadeIn(t, shift=UP * 0.1), run_time=0.15)

        note = Text("-f = follow (live stream, like tail -f)",
                     font=FONT, font_size=14, color=GREY_DIM)
        note.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def restart_policies(self):
        title = section_title("Restart Policies")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        policies = [
            ("no", "Never restart (default)"),
            ("on-failure", "Restart only if exit code ≠ 0"),
            ("always", "Always restart (even manual stop)"),
            ("unless-stopped", "Always, except if manually stopped"),
        ]

        items = VGroup()
        for policy, desc in policies:
            p = Text(f"--restart={policy}", font=FONT, font_size=14, color=DOCKER_BLUE)
            d = Text(f"  {desc}", font=FONT, font_size=12, color=GREY_DIM)
            row = VGroup(p, d).arrange(RIGHT, buff=0.1)
            items.add(row)
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        items.move_to(DOWN * 0.3)

        self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.3) for i in items],
                  lag_ratio=0.2), run_time=1)

        # Demo: container crashes and restarts
        cont = container_box("api", DOCKER_BLUE, 1.5, 0.6)
        cont.move_to(RIGHT * 4 + UP * 0.5)
        self.play(FadeIn(cont), run_time=0.2)

        for _ in range(2):
            crash = Text("💥", font_size=20)
            crash.move_to(cont.get_center())
            self.play(FadeIn(crash), cont.animate.set_opacity(0.2), run_time=0.2)
            self.play(FadeOut(crash), cont.animate.set_opacity(1), run_time=0.2)

        restart_label = Text("auto-restart ✓", font=FONT, font_size=10, color=CONTAINER_GREEN)
        restart_label.next_to(cont, DOWN, buff=0.1)
        self.play(FadeIn(restart_label), run_time=0.2)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text("• HEALTHCHECK monitors container health",
                 font=FONT, font_size=15, color=WHITE),
            Text("• docker logs -f streams live output",
                 font=FONT, font_size=15, color=WHITE),
            Text("• Restart policies auto-recover crashes",
                 font=FONT, font_size=15, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
