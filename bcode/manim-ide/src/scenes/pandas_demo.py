"""Pandas teaching scene — show DataFrame operations with IDE + table output."""

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from src.ide import IDE, OutputPanel
from src.helpers import make_split_layout


class PandasGroupBy(VoiceoverScene):
    """Teach pandas groupby with visual IDE and table output."""

    def construct(self):
        self.set_speech_service(GTTSService())

        code = '''import pandas as pd

df = pd.DataFrame({
    "city": ["NY","LA","NY","LA"],
    "sales": [100, 200, 150, 300]
})

result = df.groupby("city").sum()
print(result)'''

        ide = IDE(code=code, title="analysis.py")
        output = OutputPanel(title="Terminal")
        make_split_layout(ide, output)

        with self.voiceover("Let's learn pandas groupby."):
            self.play(FadeIn(ide), FadeIn(output))

        with self.voiceover("We create a DataFrame with city and sales columns."):
            ide.highlight_lines(self, 3, 6)

        with self.voiceover("Groupby city and sum the sales."):
            ide.highlight_lines(self, 8, 8, color=BLUE)

        with self.voiceover("New York totals 250, Los Angeles totals 500."):
            output.show_text(self, "city\nLA    500\nNY    250", color=GREEN)

        self.wait(2)
