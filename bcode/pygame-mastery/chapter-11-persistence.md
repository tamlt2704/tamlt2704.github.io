# Chapter 11: Save & Load — Keeping Progress

[← Chapter 10: UI & Menus](chapter-10-ui.md) | [Chapter 12: Performance →](chapter-12-performance.md)

---

## The Problem

Sam: "I got to wave 12 and had to close the game for dinner. When I came back, it started from wave 1. All my progress is gone."

Games need persistence. High scores, settings (volume, controls), and game state (current wave, unlocks) must survive between sessions.

## JSON: The Simple Approach

For game settings and save data, JSON is perfect — human-readable, easy to debug, built into Python:

```python
import json
import os

SAVE_DIR = os.path.join(os.path.dirname(__file__), "saves")
os.makedirs(SAVE_DIR, exist_ok=True)


def save_data(filename, data):
    """Save a dictionary to a JSON file."""
    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_data(filename, default=None):
    """Load a dictionary from a JSON file. Returns default if not found."""
    filepath = os.path.join(SAVE_DIR, filename)
    if not os.path.exists(filepath):
        return default if default is not None else {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}
```

## Settings System

```python
class Settings:
    DEFAULTS = {
        "master_volume": 0.8,
        "sfx_volume": 0.7,
        "music_volume": 0.4,
        "fullscreen": False,
        "show_fps": False,
        "screen_shake": True,
        "controls": {
            "up": "K_w",
            "down": "K_s",
            "left": "K_a",
            "right": "K_d",
            "dash": "K_LSHIFT",
        }
    }

    def __init__(self):
        self.data = load_data("settings.json", self.DEFAULTS.copy())
        # Fill in any missing keys from defaults
        for key, value in self.DEFAULTS.items():
            if key not in self.data:
                self.data[key] = value

    def get(self, key):
        return self.data.get(key, self.DEFAULTS.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def save(self):
        save_data("settings.json", self.data)


settings = Settings()

# Usage:
pygame.mixer.music.set_volume(settings.get("music_volume"))
```

## High Scores

```python
class HighScores:
    def __init__(self, max_entries=10):
        self.max_entries = max_entries
        self.scores = load_data("highscores.json", {"entries": []})["entries"]

    def add_score(self, score, waves, date=None):
        import datetime
        entry = {
            "score": score,
            "waves": waves,
            "date": date or datetime.datetime.now().isoformat()
        }
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:self.max_entries]
        save_data("highscores.json", {"entries": self.scores})

    def is_high_score(self, score):
        if len(self.scores) < self.max_entries:
            return True
        return score > self.scores[-1]["score"]

    def get_top(self, n=5):
        return self.scores[:n]
```

## Game State Save/Load

For saving mid-game progress (continue from last wave):

```python
class GameState:
    def __init__(self):
        self.wave = 1
        self.score = 0
        self.player_hp = 5
        self.player_max_hp = 5
        self.unlocked_weapons = ["pistol"]
        self.current_weapon = "pistol"

    def to_dict(self):
        return {
            "wave": self.wave,
            "score": self.score,
            "player_hp": self.player_hp,
            "player_max_hp": self.player_max_hp,
            "unlocked_weapons": self.unlocked_weapons,
            "current_weapon": self.current_weapon,
        }

    @classmethod
    def from_dict(cls, data):
        state = cls()
        state.wave = data.get("wave", 1)
        state.score = data.get("score", 0)
        state.player_hp = data.get("player_hp", 5)
        state.player_max_hp = data.get("player_max_hp", 5)
        state.unlocked_weapons = data.get("unlocked_weapons", ["pistol"])
        state.current_weapon = data.get("current_weapon", "pistol")
        return state

    def save(self, slot=0):
        save_data(f"save_slot_{slot}.json", self.to_dict())

    @classmethod
    def load(cls, slot=0):
        data = load_data(f"save_slot_{slot}.json")
        if data:
            return cls.from_dict(data)
        return None

    @classmethod
    def slot_exists(cls, slot=0):
        filepath = os.path.join(SAVE_DIR, f"save_slot_{slot}.json")
        return os.path.exists(filepath)
```

## Save Slots on Title Screen

```python
class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.options = ["New Game"]
        if GameState.slot_exists(0):
            self.options.insert(0, "Continue")
        self.options.append("Quit")
        self.selected = 0

    def _select_option(self):
        option = self.options[self.selected]
        if option == "Continue":
            state = GameState.load(0)
            self.game.change_scene(GameplayScene(self.game, state))
        elif option == "New Game":
            self.game.change_scene(GameplayScene(self.game, GameState()))
        elif option == "Quit":
            self.game.running = False
```

## Auto-Save

Save automatically between waves:

```python
class GameplayScene(Scene):
    def check_wave_complete(self):
        if self.spawner.is_wave_complete(self.enemy_group):
            self.state.wave += 1
            self.state.player_hp = self.player.hp
            self.state.score = self.score
            self.state.save(slot=0)  # Auto-save
            self.spawner.start_wave(self.state.wave)
```

## What NOT to Serialize

Some things can't be saved as JSON:

```python
# WRONG — can't serialize Pygame objects
save_data("game.json", {
    "player_surface": player.image,      # Surface object — not serializable
    "enemy_group": enemy_group,           # Sprite group — not serializable
    "sound": shoot_sound,                 # Sound object — not serializable
})

# RIGHT — save only data, reconstruct objects on load
save_data("game.json", {
    "player_hp": player.hp,
    "player_pos": [player.pos.x, player.pos.y],
    "wave": current_wave,
    "score": score,
    "enemies": [{"type": e.type, "pos": [e.pos.x, e.pos.y], "hp": e.hp} for e in enemies],
})
```

Save state. Reconstruct objects from state on load.

## Corruption Protection

Save files can get corrupted (crash during write, disk full). Write to a temp file first:

```python
import tempfile
import shutil

def safe_save(filename, data):
    """Atomic save — write to temp file, then rename."""
    filepath = os.path.join(SAVE_DIR, filename)
    # Write to temp file in same directory
    fd, tmp_path = tempfile.mkstemp(dir=SAVE_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        # Atomic rename (on most filesystems)
        shutil.move(tmp_path, filepath)
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
```

## What You Learned

- **JSON persistence** — save/load dictionaries to files
- **Settings system** — defaults, get/set, auto-save on change
- **High scores** — sorted list, capped entries
- **Game state** — serialize to dict, reconstruct from dict
- **Save slots** — multiple save files, slot existence check
- **Auto-save** — save between waves automatically
- **Corruption protection** — atomic writes via temp file + rename

Progress persists. Settings stick. High scores motivate replays. Sam can close the game and come back to wave 12.

But at wave 12, there are 30 enemies on screen, 50 bullets flying, and 200 particles. The frame rate drops to 40 FPS. Time to optimize.

---

[← Chapter 10: UI & Menus](chapter-10-ui.md) | [Chapter 12: Performance →](chapter-12-performance.md)
