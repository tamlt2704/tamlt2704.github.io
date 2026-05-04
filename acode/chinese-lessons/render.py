"""Build script: render episodes with manim-voiceover (audio baked in)."""
import argparse, subprocess, sys
from pathlib import Path

EPISODES = {
    "ep01": ("episodes/ep01_greetings.py", "EP01Greetings"),
    "ep02": ("episodes/ep02_numbers.py", "EP02Numbers"),
    "ep03": ("episodes/ep03_restaurant.py", "EP03Restaurant"),
    "ep04": ("episodes/ep04_directions.py", "EP04Directions"),
    "ep05": ("episodes/ep05_shopping.py", "EP05Shopping"),
    "ep06": ("episodes/ep06_time.py", "EP06Time"),
    "ep07": ("episodes/ep07_family.py", "EP07Family"),
    "ep08": ("episodes/ep08_weather.py", "EP08Weather"),
    "ep09": ("episodes/ep09_hobbies.py", "EP09Hobbies"),
    "ep10": ("episodes/ep10_emergency.py", "EP10Emergency"),
}

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"


def do_render(ep_id: str, extra_args: list[str] = None):
    mod_path, scene_class = EPISODES[ep_id]
    OUTPUT_DIR.mkdir(exist_ok=True)
    cmd = [
        sys.executable, "-m", "manim", "render",
        "--disable_caching",
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.extend([mod_path, scene_class])
    print(f"[RENDER] {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=str(ROOT))

    # Find output and copy to output/
    video_dir = ROOT / "media" / "videos" / Path(mod_path).stem
    mp4s = sorted(video_dir.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if mp4s:
        import shutil
        dest = OUTPUT_DIR / f"{ep_id}.mp4"
        shutil.copy2(mp4s[0], dest)
        print(f"[OUTPUT] {dest}")


def main():
    parser = argparse.ArgumentParser(description="Chinese Lessons render tool")
    parser.add_argument("episode", nargs="?", help="Episode ID (e.g. ep01)")
    parser.add_argument("--all", action="store_true", help="Render all episodes")
    args, extra = parser.parse_known_args()

    if args.all:
        for ep_id in EPISODES:
            do_render(ep_id, extra)
    elif args.episode:
        if args.episode not in EPISODES:
            print(f"Unknown episode: {args.episode}. Available: {list(EPISODES.keys())}")
            return
        do_render(args.episode, extra)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
