"""edge-tts wrapper: generate audio files and measure durations."""
import asyncio, os, json
from pathlib import Path
import edge_tts
from mutagen.mp3 import MP3
from common.styles import ZH_VOICE, EN_VOICE


async def _generate_one(text: str, voice: str, path: str):
    comm = edge_tts.Communicate(text, voice)
    await comm.save(path)


def generate_audio(text: str, path: str, lang: str = "zh") -> float:
    """Generate TTS audio file. Returns duration in seconds."""
    voice = ZH_VOICE if lang == "zh" else EN_VOICE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    asyncio.run(_generate_one(text, voice, path))
    return get_duration(path)


def get_duration(path: str) -> float:
    """Get audio duration in seconds."""
    return MP3(path).info.length


def generate_episode_audio(clips: list[dict], audio_dir: str) -> dict:
    """Generate all audio clips for an episode.

    clips: [{"id": "greet_01", "text": "你好", "lang": "zh"}, ...]
    Returns: {"greet_01": {"path": "...", "duration": 1.23}, ...}
    """
    os.makedirs(audio_dir, exist_ok=True)
    manifest = {}
    for clip in clips:
        cid = clip["id"]
        path = os.path.join(audio_dir, f"{cid}.mp3")
        if os.path.exists(path):
            dur = get_duration(path)
        else:
            dur = generate_audio(clip["text"], path, clip.get("lang", "zh"))
        manifest[cid] = {"path": os.path.abspath(path), "duration": dur}
    # Save manifest for Manim to read
    mpath = os.path.join(audio_dir, "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest
