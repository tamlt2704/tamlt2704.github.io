"""LeetCode teaching scenes — step through algorithms with IDE + visualization."""

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from src.ide import IDE, OutputPanel
from src.helpers import make_split_layout, step_through


class BinarySearch(VoiceoverScene):
    """Teach binary search with pointer visualization."""

    def construct(self):
        self.set_speech_service(GTTSService())

        code = '''def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1'''

        ide = IDE(code=code, title="binary_search.py")
        output = OutputPanel(title="Array")
        make_split_layout(ide, output)

        with self.voiceover("Binary search finds a target in a sorted array in log n time."):
            self.play(FadeIn(ide), FadeIn(output))

        with self.voiceover("We maintain two pointers, lo and hi."):
            ide.highlight_lines(self, 2, 2)

        with self.voiceover("Each iteration we compute the midpoint."):
            ide.highlight_lines(self, 4, 4, color=BLUE)

        # Show array with pointers
        with self.voiceover("Given the sorted array 1, 3, 5, 7, 9, searching for 7:"):
            output.show_array(self, [1, 3, 5, 7, 9])

        with self.voiceover("We eliminate half the array each step. Found at index 3."):
            output.show_text(self, "→ index 3", color=GREEN)

        self.wait(2)
