"""
Docker 101 — Episode 00: What is Docker?
The problem Docker solves. Containers vs VMs. The "works on my machine" problem.

Render: manim -pqh ep00_what_is_docker.py WhatIsDocker
"""
from manim import *
from helpers import *


class WhatIsDocker(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.the_problem()
        self.the_old_way()
        self.the_docker_way()
        self.containers_vs_vms()
        self.recap()

    # ── The Problem: "Works on my machine" (50s) ─
    def the_problem(self):
        title = section_title("The Problem")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Developer's laptop
        dev_box = RoundedRectangle(width=3, height=2, corner_radius=0.15,
                                    fill_color=DARK_CELL, fill_opacity=1,
                                    stroke_color=CONTAINER_GREEN, stroke_width=2)
        dev_box.move_to(LEFT * 3.5)
        dev_label = Text("Your Laptop", font=FONT, font_size=14, color=CONTAINER_GREEN)
        dev_label.next_to(dev_box, UP, buff=0.15)

        # App inside
        app = container_box("Python 3.11\n+ Flask\n+ numpy", CONTAINER_GREEN, 2.2, 1.2)
        app.scale(0.7).move_to(dev_box.get_center())

        self.play(FadeIn(dev_box), FadeIn(dev_label), run_time=0.3)
        self.play(FadeIn(app), run_time=0.3)

        check = Text("✓ Works!", font=FONT, font_size=16, color=CONTAINER_GREEN)
        check.next_to(dev_box, DOWN, buff=0.2)
        self.play(FadeIn(check), run_time=0.3)
        self.wait(0.5)

        # Arrow to server
        arrow = Arrow(LEFT * 1.5, RIGHT * 0.5, color=WHITE)
        deploy = Text("deploy", font=FONT, font_size=12, color=GREY_DIM)
        deploy.next_to(arrow, UP, buff=0.1)
        self.play(GrowArrow(arrow), FadeIn(deploy), run_time=0.5)

        # Server
        server_box = RoundedRectangle(width=3, height=2, corner_radius=0.15,
                                       fill_color=DARK_CELL, fill_opacity=1,
                                       stroke_color=CONTAINER_RED, stroke_width=2)
        server_box.move_to(RIGHT * 3.5)
        server_label = Text("Production Server", font=FONT, font_size=14, color=CONTAINER_RED)
        server_label.next_to(server_box, UP, buff=0.15)

        server_app = VGroup(
            Text("Python 3.9 (?)", font=FONT, font_size=12, color=CONTAINER_RED),
            Text("Missing numpy", font=FONT, font_size=12, color=CONTAINER_RED),
            Text("Wrong OS libs", font=FONT, font_size=12, color=CONTAINER_RED),
        ).arrange(DOWN, buff=0.1)
        server_app.move_to(server_box.get_center())

        self.play(FadeIn(server_box), FadeIn(server_label), run_time=0.3)
        self.play(FadeIn(server_app), run_time=0.3)

        fail = Text("✗ CRASHES", font=FONT, font_size=16, color=CONTAINER_RED)
        fail.next_to(server_box, DOWN, buff=0.2)
        self.play(FadeIn(fail), run_time=0.3)
        self.wait(0.5)

        # The famous quote
        quote = Text('"Works on my machine" 🤷', font=FONT, font_size=22, color=CONTAINER_YELLOW)
        quote.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(quote), run_time=0.5)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── The Old Way: VMs (40s) ───────────────────
    def the_old_way(self):
        title = section_title("The Old Way: Virtual Machines")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Host machine
        host = Rectangle(width=10, height=4, fill_color="#111", fill_opacity=1,
                         stroke_color=BORDER, stroke_width=1)
        host.shift(DOWN * 0.5)
        host_label = Text("Host Machine (Hardware + OS)", font=FONT,
                          font_size=12, color=GREY_DIM)
        host_label.move_to(host.get_bottom() + UP * 0.2)

        # Hypervisor layer
        hyper = Rectangle(width=9.5, height=0.4, fill_color="#333",
                          fill_opacity=1, stroke_width=0)
        hyper.move_to(host.get_bottom() + UP * 0.7)
        hyper_label = Text("Hypervisor", font=FONT, font_size=10, color=WHITE)
        hyper_label.move_to(hyper.get_center())

        self.play(FadeIn(host), FadeIn(host_label), FadeIn(hyper), FadeIn(hyper_label),
                  run_time=0.5)

        # 3 VMs — each with full OS
        vms = VGroup()
        vm_colors = [CONTAINER_GREEN, DOCKER_BLUE, CONTAINER_YELLOW]
        vm_names = ["VM 1", "VM 2", "VM 3"]
        for i in range(3):
            vm = VGroup()
            box = RoundedRectangle(width=2.8, height=2.2, corner_radius=0.1,
                                    fill_color=DARK_CELL, fill_opacity=1,
                                    stroke_color=vm_colors[i], stroke_width=1.5)
            # OS layer inside VM
            os_layer = Rectangle(width=2.5, height=0.4, fill_color="#1a1a2e",
                                 fill_opacity=1, stroke_width=0)
            os_label = Text("Guest OS", font=FONT, font_size=9, color=GREY_DIM)
            os_label.move_to(os_layer.get_center())
            os_layer.move_to(box.get_bottom() + UP * 0.35)

            app_label = Text(f"App {i+1}", font=FONT, font_size=14, color=vm_colors[i])
            app_label.move_to(box.get_center() + UP * 0.3)

            name = Text(vm_names[i], font=FONT, font_size=10, color=GREY_DIM)
            name.next_to(box, UP, buff=0.1)

            vm.add(box, os_layer, os_label, app_label, name)
            vm.move_to([i * 3.2 - 3.2, 0.8, 0])
            vms.add(vm)

        self.play(LaggedStart(*[FadeIn(vm) for vm in vms], lag_ratio=0.2),
                  run_time=1)

        # Size labels
        size = Text("Each VM: ~1-10 GB, boots in minutes", font=FONT,
                     font_size=14, color=CONTAINER_RED)
        size.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(size), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── The Docker Way (60s) ─────────────────────
    def the_docker_way(self):
        title = section_title("The Docker Way: Containers")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Host machine
        host = Rectangle(width=10, height=3.5, fill_color="#111", fill_opacity=1,
                         stroke_color=BORDER, stroke_width=1)
        host.shift(DOWN * 0.3)
        host_label = Text("Host Machine (Hardware + OS)", font=FONT,
                          font_size=12, color=GREY_DIM)
        host_label.move_to(host.get_bottom() + UP * 0.2)

        # Docker Engine layer (replaces hypervisor)
        engine = Rectangle(width=9.5, height=0.4, fill_color=DOCKER_BLUE,
                           fill_opacity=0.8, stroke_width=0)
        engine.move_to(host.get_bottom() + UP * 0.7)
        engine_label = Text("Docker Engine", font=FONT, font_size=10, color=WHITE)
        engine_label.move_to(engine.get_center())

        self.play(FadeIn(host), FadeIn(host_label), FadeIn(engine),
                  FadeIn(engine_label), run_time=0.5)

        # 3 containers — NO guest OS
        containers = VGroup()
        c_colors = [CONTAINER_GREEN, DOCKER_BLUE, CONTAINER_YELLOW]
        c_names = ["web", "api", "db"]
        for i in range(3):
            c = container_box(c_names[i], c_colors[i], 2.8, 1.5)
            c.move_to([i * 3.2 - 3.2, 1, 0])
            containers.add(c)

        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in containers],
                  lag_ratio=0.15), run_time=1)

        # No Guest OS label
        no_os = Text("No Guest OS — shares host kernel", font=FONT,
                      font_size=14, color=CONTAINER_GREEN)
        no_os.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(no_os), run_time=0.3)

        size = Text("Each container: ~10-100 MB, starts in seconds", font=FONT,
                     font_size=14, color=CONTAINER_GREEN)
        size.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(size), run_time=0.3)
        self.wait(2)

        # Docker logo
        logo = docker_logo(scale=0.6)
        logo.to_corner(DR, buff=0.5)
        self.play(FadeIn(logo), run_time=0.3)
        self.wait(1)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Containers vs VMs side by side (40s) ─────
    def containers_vs_vms(self):
        title = section_title("Containers vs VMs")
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.5)

        # Comparison table
        headers = ["", "VM", "Container"]
        rows = [
            ["Size", "1-10 GB", "10-100 MB"],
            ["Boot", "Minutes", "Seconds"],
            ["OS", "Full Guest OS", "Shares Host"],
            ["Isolation", "Strong", "Process-level"],
            ["Density", "~10 per host", "~100s per host"],
        ]

        table = VGroup()
        for j, h in enumerate(headers):
            cell = Text(h, font=FONT, font_size=14,
                        color=DOCKER_BLUE if j > 0 else GREY_DIM)
            cell.move_to([j * 2.8 - 2.8, 1.5, 0])
            table.add(cell)

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                color = WHITE
                if j == 2:
                    color = CONTAINER_GREEN
                elif j == 1:
                    color = CONTAINER_YELLOW
                cell = Text(val, font=FONT, font_size=13, color=color)
                cell.move_to([j * 2.8 - 2.8, 0.8 - i * 0.55, 0])
                table.add(cell)

        self.play(FadeIn(table), run_time=0.8)
        self.wait(3)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("What you learned:", font=FONT, font_size=26, color=DOCKER_BLUE),
            Text('• "Works on my machine" → Docker fixes this',
                 font=FONT, font_size=16, color=WHITE),
            Text("• Container = app + dependencies, no guest OS",
                 font=FONT, font_size=16, color=WHITE),
            Text("• Starts in seconds, ~100 MB, 100s per host",
                 font=FONT, font_size=16, color=WHITE),
            Text("• Docker Engine replaces the hypervisor",
                 font=FONT, font_size=16, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.15), run_time=1.2)
        self.wait(3)
