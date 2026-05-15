"""Java teaching scene — show Java code with IDE component."""

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from src.ide import IDE, OutputPanel
from src.helpers import make_split_layout


class JavaForLoop(VoiceoverScene):
    """Teach Java for-loop with visual IDE."""

    def construct(self):
        self.set_speech_service(GTTSService())

        code = '''public class Main {
    public static void main(String[] args) {
        int[] nums = {3, 1, 4, 1, 5};
        int sum = 0;
        for (int n : nums) {
            sum += n;
        }
        System.out.println(sum);
    }
}'''

        ide = IDE(code=code, language="java", title="Main.java")
        output = OutputPanel(title="Console")
        make_split_layout(ide, output)

        with self.voiceover("Let's look at a Java enhanced for loop."):
            self.play(FadeIn(ide), FadeIn(output))

        with self.voiceover("We declare an integer array with 5 elements."):
            ide.highlight_lines(self, 3, 3)

        with self.voiceover("The for-each loop iterates over every element."):
            ide.highlight_lines(self, 5, 7, color=BLUE)

        with self.voiceover("The sum is 14."):
            output.show_text(self, "14", color=GREEN)

        self.wait(2)
