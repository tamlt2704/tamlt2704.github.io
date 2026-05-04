"""
Emacs 101 (Manim) — Episode 02: "Kill, Yank, and the Kill Ring"
Animated: select text, kill it, yank it back, cycle through kill ring.

Render: manim -pqh ep02_kill_yank.py KillYank
"""
from manim import *
from helpers import *


class KillYank(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.intro()
        self.kill_line()
        self.kill_region()
        self.the_kill_ring()
        self.recap()

    def intro(self):
        title = Text("Emacs 101", font=FONT, font_size=40, color=TEAL)
        sub = Text("Episode 02: Kill, Yank & the Kill Ring",
                    font=FONT, font_size=22, color=DIM)
        sub.next_to(title, DOWN, buff=0.3)
        self.play(Write(title), FadeIn(sub), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(sub))

    # ── C-k: Kill to End of Line (40s) ───────────
    def kill_line(self):
        frame = emacs_frame(title="hello.txt").scale(0.85)
        self.play(FadeIn(frame), run_time=0.3)

        title = Text("C-k → Kill to End of Line", font=FONT, font_size=18, color=YELLOW)
        title.to_edge(UP, buff=0.2)
        self.play(FadeIn(title), run_time=0.2)

        # Editor content
        lines_data = [
            "The quick brown fox",
            "jumps over the lazy dog",
            "Emacs is powerful",
        ]
        start = frame.editor.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.4
        lines = VGroup()
        for i, line in enumerate(lines_data):
            t = Text(line, font=FONT, font_size=13, color=WHITE)
            t.move_to(start + DOWN * i * 0.3)
            t.align_to(start, LEFT)
            lines.add(t)
        self.play(FadeIn(lines), run_time=0.3)

        # Cursor at "brown" on line 1
        cur = cursor_block()
        cur.move_to(lines[0].get_left() + RIGHT * 1.3)
        self.play(FadeIn(cur), run_time=0.2)

        # Show C-k keypress
        kc = key_combo("C-k")
        kc.to_edge(DOWN, buff=0.5)
        desc = Text("Kill from cursor to end of line", font=FONT, font_size=12, color=DIM)
        desc.next_to(kc, DOWN, buff=0.1)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.2)

        # Highlight the killed portion
        killed_text = "brown fox"
        # Create a highlight rectangle over the killed portion
        kill_rect = Rectangle(width=1.3, height=0.22, fill_color=RED,
                              fill_opacity=0.3, stroke_width=0)
        kill_rect.move_to(lines[0].get_right() + LEFT * 0.65)
        self.play(FadeIn(kill_rect), run_time=0.3)
        self.wait(0.3)

        # Text disappears (killed)
        # Replace line 1 with truncated version
        new_line1 = Text("The quick ", font=FONT, font_size=13, color=WHITE)
        new_line1.move_to(start)
        new_line1.align_to(start, LEFT)
        self.play(FadeOut(kill_rect),
                  Transform(lines[0], new_line1), run_time=0.3)

        # Show kill ring entry
        ring_label = Text("Kill ring: [\"brown fox\"]", font=FONT, font_size=12, color=TEAL)
        ring_label.move_to(frame.mini.get_center())
        self.play(FadeIn(ring_label), run_time=0.3)
        self.wait(1)

        # C-y: Yank it back
        self.play(FadeOut(kc), FadeOut(desc), run_time=0.15)
        kc2 = key_combo("C-y")
        kc2.to_edge(DOWN, buff=0.5)
        desc2 = Text("Yank (paste) the last kill", font=FONT, font_size=12, color=DIM)
        desc2.next_to(kc2, DOWN, buff=0.1)
        self.play(FadeIn(kc2), FadeIn(desc2), run_time=0.2)

        # Text reappears
        restored = Text("The quick brown fox", font=FONT, font_size=13, color=WHITE)
        restored.move_to(start)
        restored.align_to(start, LEFT)
        self.play(Transform(lines[0], restored), run_time=0.3)
        self.wait(1)

        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── C-w: Kill Region (40s) ───────────────────
    def kill_region(self):
        frame = emacs_frame(title="code.py").scale(0.85)
        self.play(FadeIn(frame), run_time=0.3)

        title = Text("C-SPC → Set Mark, then C-w → Kill Region",
                      font=FONT, font_size=16, color=YELLOW)
        title.to_edge(UP, buff=0.2)
        self.play(FadeIn(title), run_time=0.2)

        # Editor content
        start = frame.editor.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.4
        code_text = Text("def hello_world():", font=FONT, font_size=13, color=WHITE)
        code_text.move_to(start).align_to(start, LEFT)
        self.play(FadeIn(code_text), run_time=0.2)

        # Step 1: C-SPC at "hello"
        cur = cursor_block()
        cur.move_to(code_text.get_left() + RIGHT * 0.56)
        self.play(FadeIn(cur), run_time=0.2)

        kc1 = key_combo("C-SPC")
        kc1.to_edge(DOWN, buff=0.5)
        desc1 = Text("Set mark (start of selection)", font=FONT, font_size=12, color=DIM)
        desc1.next_to(kc1, DOWN, buff=0.1)
        self.play(FadeIn(kc1), FadeIn(desc1), run_time=0.2)

        mark_dot = Dot(cur.get_center(), color=YELLOW, radius=0.04)
        self.play(FadeIn(mark_dot), run_time=0.2)
        self.wait(0.5)
        self.play(FadeOut(kc1), FadeOut(desc1), run_time=0.15)

        # Step 2: Move cursor to end of "world" (C-f several times)
        kc2 = key_combo("C-f C-f C-f ...")
        kc2.to_edge(DOWN, buff=0.5)
        desc2 = Text("Move forward to select", font=FONT, font_size=12, color=DIM)
        desc2.next_to(kc2, DOWN, buff=0.1)
        self.play(FadeIn(kc2), FadeIn(desc2), run_time=0.2)

        # Show region highlight
        region = Rectangle(width=1.5, height=0.22, fill_color=REGION_COLOR,
                           fill_opacity=0.6, stroke_width=0)
        region.move_to(code_text.get_left() + RIGHT * 1.3)
        self.play(FadeIn(region), cur.animate.shift(RIGHT * 1.5), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(kc2), FadeOut(desc2), run_time=0.15)

        # Step 3: C-w kills the region
        kc3 = key_combo("C-w")
        kc3.to_edge(DOWN, buff=0.5)
        desc3 = Text("Kill region (cut selection)", font=FONT, font_size=12, color=DIM)
        desc3.next_to(kc3, DOWN, buff=0.1)
        self.play(FadeIn(kc3), FadeIn(desc3), run_time=0.2)

        # Region disappears
        self.play(region.animate.set_fill(RED, opacity=0.5), run_time=0.2)
        self.play(FadeOut(region), FadeOut(mark_dot), run_time=0.3)

        # Show M-w alternative
        alt = Text("M-w = copy (don't kill)", font=FONT, font_size=13, color=TEAL)
        alt.move_to(frame.editor.get_center() + DOWN)
        self.play(FadeIn(alt), run_time=0.3)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── The Kill Ring (50s) ──────────────────────
    def the_kill_ring(self):
        title = Text("The Kill Ring — Clipboard History", font=FONT, font_size=20, color=YELLOW)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.4)

        # Visual: a ring of killed text
        ring_items = ['"brown fox"', '"hello_world"', '"lazy dog"', '"Emacs"']
        ring = VGroup()
        for i, item in enumerate(ring_items):
            angle = i * TAU / len(ring_items) - PI / 2
            r = 1.5
            box = RoundedRectangle(width=1.8, height=0.4, corner_radius=0.06,
                                    fill_color=EMACS_BG, fill_opacity=1,
                                    stroke_color=TEAL, stroke_width=1)
            label = Text(item, font=FONT, font_size=11, color=WHITE)
            label.move_to(box.get_center())
            group = VGroup(box, label)
            group.move_to([r * np.cos(angle), r * np.sin(angle) - 0.5, 0])
            ring.add(group)

        # Ring circle
        ring_circle = Circle(radius=1.5, color=DIM, stroke_width=0.5,
                             stroke_opacity=0.3)
        ring_circle.shift(DOWN * 0.5)

        self.play(FadeIn(ring_circle), run_time=0.2)
        self.play(LaggedStart(*[FadeIn(r) for r in ring], lag_ratio=0.15), run_time=0.6)

        # Pointer at top (most recent)
        pointer = Arrow(UP * 0.3 + DOWN * 0.5, ring[0].get_center(),
                        color=YELLOW, buff=0.15, stroke_width=2)
        ptr_label = Text("C-y pastes this", font=FONT, font_size=11, color=YELLOW)
        ptr_label.next_to(pointer, UP, buff=0.1)
        self.play(GrowArrow(pointer), FadeIn(ptr_label), run_time=0.3)
        self.wait(1)

        # M-y cycles
        kc = key_combo("M-y")
        kc.to_edge(DOWN, buff=0.5)
        desc = Text("M-y → cycle to next item in ring", font=FONT, font_size=12, color=DIM)
        desc.next_to(kc, DOWN, buff=0.1)
        self.play(FadeIn(kc), FadeIn(desc), run_time=0.2)

        # Rotate the ring
        for _ in range(3):
            self.play(Rotate(ring, TAU / len(ring_items), about_point=DOWN * 0.5),
                      run_time=0.5)
            self.wait(0.3)

        note = Text("Every kill is remembered. Nothing is lost.",
                     font=FONT, font_size=14, color=TEAL)
        note.to_edge(DOWN, buff=0.2)
        self.play(FadeIn(note), run_time=0.3)
        self.wait(2)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ── Recap (15s) ──────────────────────────────
    def recap(self):
        recap = VGroup(
            Text("Episode 02 Recap:", font=FONT, font_size=24, color=TEAL),
            Text("• C-k → kill to end of line", font=FONT, font_size=15, color=WHITE),
            Text("• C-SPC → set mark (start selection)", font=FONT, font_size=15, color=WHITE),
            Text("• C-w → kill region (cut)", font=FONT, font_size=15, color=WHITE),
            Text("• M-w → copy region (don't cut)", font=FONT, font_size=15, color=WHITE),
            Text("• C-y → yank (paste most recent)", font=FONT, font_size=15, color=WHITE),
            Text("• M-y → cycle through kill ring", font=FONT, font_size=15, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        recap.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.3)
                  for l in recap], lag_ratio=0.12), run_time=1.2)
        self.wait(3)
