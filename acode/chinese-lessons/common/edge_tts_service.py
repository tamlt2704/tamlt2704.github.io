"""Custom manim-voiceover SpeechService using edge-tts."""
import asyncio
from pathlib import Path
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService
import edge_tts


class EdgeTTSService(SpeechService):
    """SpeechService using Microsoft Edge TTS (via edge-tts package)."""

    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural", **kwargs):
        SpeechService.__init__(self, **kwargs)
        self.voice = voice

    def generate_from_text(
        self, text: str, cache_dir: str = None, path: str = None, **kwargs
    ) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "edge_tts",
            "voice": kwargs.get("voice", self.voice),
        }

        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        if path is None:
            audio_path = self.get_audio_basename(input_data) + ".mp3"
        else:
            audio_path = path

        voice = kwargs.get("voice", self.voice)
        output_file = str(Path(cache_dir) / audio_path)

        asyncio.run(self._generate(input_text, voice, output_file))

        return {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }

    @staticmethod
    async def _generate(text: str, voice: str, path: str):
        comm = edge_tts.Communicate(text, voice)
        await comm.save(path)
