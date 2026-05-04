"""Base scene using manim-voiceover for native audio-animation sync."""
from manim import *
from manim_voiceover import VoiceoverScene
from common.styles import *
from common.edge_tts_service import EdgeTTSService


class ChineseLessonScene(VoiceoverScene):
    episode_id: str = "ep00"
    episode_title: str = ""
    episode_subtitle: str = ""

    def setup(self):
        super().setup()
        self.camera.background_color = BG_COLOR
        self.set_speech_service(EdgeTTSService(voice=ZH_VOICE))

    def _say(self, text: str, voice: str = None):
        """Return voiceover context manager with optional voice override."""
        kwargs = {}
        if voice:
            kwargs["voice"] = voice
        return self.voiceover(text=text, **kwargs)

    # ── Title card ──

    def show_title(self):
        ep_label = Text(
            self.episode_id.upper().replace("_", " "),
            font=ENGLISH_FONT, font_size=24, color=SUBTITLE_COLOR,
        ).shift(UP * 1.2)
        title = Text(
            self.episode_title, font=CHINESE_FONT,
            font_size=52, color=TITLE_COLOR,
        ).next_to(ep_label, DOWN, buff=0.3)
        sub = Text(
            self.episode_subtitle, font=ENGLISH_FONT,
            font_size=28, color=ENGLISH_COLOR,
        ).next_to(title, DOWN, buff=0.25)
        grp = VGroup(ep_label, title, sub)
        self.play(FadeIn(grp, shift=UP * 0.3), run_time=0.8)
        self.wait(2)
        self.play(FadeOut(grp), run_time=FADE_TIME)
        self.wait(PAUSE_MED)

    # ── Vocabulary card ──

    def show_vocab(self, chinese: str, pinyin: str, english: str):
        zh_text = Text(chinese, font=CHINESE_FONT, font_size=72, color=CHINESE_COLOR)
        py_text = Text(pinyin, font=ENGLISH_FONT, font_size=36, color=PINYIN_COLOR
                       ).next_to(zh_text, UP, buff=0.2)
        en_text = Text(english, font=ENGLISH_FONT, font_size=30, color=ENGLISH_COLOR
                       ).next_to(zh_text, DOWN, buff=0.3)

        # Show Chinese + pinyin, speak Chinese
        self.play(Write(zh_text, run_time=0.6),
                  FadeIn(py_text, shift=DOWN * 0.2, run_time=0.5))
        with self._say(chinese):
            self.wait()
        self.wait(PAUSE_SHORT)

        # Show English, speak English
        self.play(FadeIn(en_text, shift=UP * 0.15), run_time=0.3)
        with self._say(english, voice=EN_VOICE):
            self.wait()
        self.wait(PAUSE_MED)

        # Repeat prompt
        repeat_label = Text("Repeat!", font=ENGLISH_FONT, font_size=22, color=ACCENT2_COLOR
                            ).next_to(en_text, DOWN, buff=0.3)
        highlight = SurroundingRectangle(zh_text, color=ACCENT2_COLOR, buff=0.12, stroke_width=2)
        self.play(FadeIn(repeat_label), Create(highlight), run_time=0.3)
        with self._say(chinese):
            self.wait()
        self.wait(PAUSE_LONG)
        self.play(FadeOut(highlight), FadeOut(repeat_label), run_time=0.2)

        self.play(FadeOut(VGroup(zh_text, py_text, en_text)), run_time=FADE_TIME)
        self.wait(PAUSE_MED)

    # ── Phrase display ──

    def show_phrase(self, chinese: str, pinyin: str, english: str):
        zh_text = Text(chinese, font=CHINESE_FONT, font_size=56, color=CHINESE_COLOR)
        py_text = Text(pinyin, font=ENGLISH_FONT, font_size=28, color=PINYIN_COLOR
                       ).next_to(zh_text, UP, buff=0.15)
        en_text = Text(english, font=ENGLISH_FONT, font_size=26, color=ENGLISH_COLOR
                       ).next_to(zh_text, DOWN, buff=0.25)

        self.play(FadeIn(zh_text, shift=RIGHT * 0.3, run_time=0.5))
        self.play(FadeIn(py_text), run_time=0.3)

        highlight = SurroundingRectangle(zh_text, color=ACCENT_COLOR, buff=0.15, stroke_width=2)
        self.play(Create(highlight), run_time=0.3)
        with self._say(chinese):
            self.wait()
        self.play(FadeOut(highlight), run_time=0.2)
        self.wait(PAUSE_SHORT)

        self.play(FadeIn(en_text, shift=UP * 0.1), run_time=0.3)
        with self._say(english, voice=EN_VOICE):
            self.wait()
        self.wait(PAUSE_MED)

        # Repeat
        repeat_label = Text("Repeat!", font=ENGLISH_FONT, font_size=22, color=ACCENT2_COLOR
                            ).next_to(en_text, DOWN, buff=0.3)
        highlight2 = SurroundingRectangle(zh_text, color=ACCENT2_COLOR, buff=0.12, stroke_width=2)
        self.play(FadeIn(repeat_label), Create(highlight2), run_time=0.3)
        with self._say(chinese):
            self.wait()
        self.wait(PAUSE_LONG)
        self.play(FadeOut(highlight2), FadeOut(repeat_label), run_time=0.2)

        self.play(FadeOut(VGroup(zh_text, py_text, en_text)), run_time=FADE_TIME)
        self.wait(PAUSE_MED)

    # ── Dialogue ──

    def show_dialogue(self, lines: list[dict]):
        prev_group = None
        for line in lines:
            is_a = line["speaker"] == "A"
            color = SPEAKER_A_COLOR if is_a else SPEAKER_B_COLOR
            x_shift = LEFT * 2 if is_a else RIGHT * 2

            dot = Dot(radius=0.15, color=color).shift(UP * 0.8 + x_shift)
            label = Text("A" if is_a else "B", font=ENGLISH_FONT,
                         font_size=20, color=color).move_to(dot)

            zh = Text(line["chinese"], font=CHINESE_FONT, font_size=40, color=CHINESE_COLOR)
            py = Text(line["pinyin"], font=ENGLISH_FONT, font_size=22, color=PINYIN_COLOR
                      ).next_to(zh, UP, buff=0.1)
            en = Text(line["english"], font=ENGLISH_FONT, font_size=22, color=ENGLISH_COLOR
                      ).next_to(zh, DOWN, buff=0.15)
            bubble_content = VGroup(py, zh, en).shift(DOWN * 0.3)
            bubble_rect = SurroundingRectangle(
                bubble_content, color=color, buff=0.2,
                corner_radius=0.15, stroke_width=1.5)
            group = VGroup(dot, label, bubble_rect, bubble_content)

            if prev_group:
                self.play(prev_group.animate.shift(UP * 2.5).set_opacity(0.3), run_time=0.4)

            self.play(FadeIn(group, shift=UP * 0.3), run_time=0.5)
            with self._say(line["chinese"]):
                self.wait()
            self.wait(PAUSE_MED)
            prev_group = group

        self.wait(PAUSE_LONG)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=FADE_TIME)
        self.wait(PAUSE_MED)

    # ── Section header ──

    def show_section(self, title: str, subtitle: str = ""):
        t = Text(title, font=CHINESE_FONT, font_size=40, color=ACCENT_COLOR)
        s = Text(subtitle, font=ENGLISH_FONT, font_size=24, color=ENGLISH_COLOR
                 ).next_to(t, DOWN, buff=0.2) if subtitle else VMobject()
        grp = VGroup(t, s)
        line_obj = Line(LEFT * 3, RIGHT * 3, color=ACCENT_COLOR, stroke_width=1
                        ).next_to(grp, DOWN, buff=0.15)
        self.play(FadeIn(grp, shift=UP * 0.2), GrowFromCenter(line_obj), run_time=0.6)
        self.wait(1.5)
        self.play(FadeOut(grp), FadeOut(line_obj), run_time=FADE_TIME)
        self.wait(PAUSE_MED)

    # ── Review ──

    def show_review(self, items: list[dict]):
        header = Text("复习 Review", font=CHINESE_FONT, font_size=36, color=ACCENT2_COLOR)
        self.play(FadeIn(header, shift=DOWN * 0.2), run_time=0.4)
        self.wait(1.0)
        self.play(header.animate.shift(UP * 3), run_time=0.3)

        for item in items:
            zh = Text(item["chinese"], font=CHINESE_FONT, font_size=60, color=CHINESE_COLOR)
            py = Text(item["pinyin"], font=ENGLISH_FONT, font_size=28, color=PINYIN_COLOR
                      ).next_to(zh, UP, buff=0.15)
            en = Text(item["english"], font=ENGLISH_FONT, font_size=24, color=ENGLISH_COLOR
                      ).next_to(zh, DOWN, buff=0.2)
            grp = VGroup(py, zh, en)
            self.play(FadeIn(grp, scale=1.1), run_time=0.3)
            with self._say(item["chinese"]):
                self.wait()
            self.wait(PAUSE_LONG)
            self.play(FadeOut(grp, scale=0.9), run_time=0.25)
            self.wait(PAUSE_SHORT)

        self.play(FadeOut(header), run_time=0.3)

    # ── End card ──

    def show_end_card(self):
        t = Text("谢谢观看", font=CHINESE_FONT, font_size=48, color=ACCENT_COLOR)
        s = Text("Thanks for watching!", font=ENGLISH_FONT, font_size=28, color=ENGLISH_COLOR
                  ).next_to(t, DOWN, buff=0.3)
        grp = VGroup(t, s)
        self.play(FadeIn(grp, scale=0.8), run_time=0.8)
        self.wait(3)
        self.play(FadeOut(grp), run_time=0.6)
