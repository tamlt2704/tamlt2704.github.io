# Chapter 6: Sound & Music — Making It Feel Alive

[← Chapter 5: Sprite Sheets](chapter-05-animation.md) | [Chapter 7: Tile Maps →](chapter-07-tilemaps.md)

---

## The Problem

Rena's playtest: "I shot an enemy and nothing happened. I mean, it died — the HP went down — but I didn't *feel* it. There's no feedback. No impact sound. No music. It's like playing on mute."

She's right. Audio is 50% of game feel. A punch without a sound effect feels like waving your hand. An explosion without a boom is just a visual. Music sets the emotional tone — tension, triumph, dread.

Void Runners is silent. Time to fix that.

## Pygame Mixer Basics

```python
# Initialize mixer (do this before pygame.init() for best results)
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
```

The `pre_init` call configures the audio system:
- **frequency**: 44100 Hz (CD quality)
- **size**: -16 (16-bit signed samples)
- **channels**: 2 (stereo)
- **buffer**: 512 (lower = less latency, higher = fewer glitches)

## Sound Effects

```python
# Load a sound
shoot_sound = pygame.mixer.Sound("assets/audio/shoot.wav")
hit_sound = pygame.mixer.Sound("assets/audio/hit.wav")
explosion_sound = pygame.mixer.Sound("assets/audio/explosion.wav")

# Play it
shoot_sound.play()
```

That's it. Load once, play whenever. The sound plays asynchronously — it doesn't block the game loop.

### Volume Control

```python
# Per-sound volume (0.0 to 1.0)
shoot_sound.set_volume(0.3)
hit_sound.set_volume(0.5)
explosion_sound.set_volume(0.7)

# Master volume
pygame.mixer.set_num_channels(16)  # Allow 16 simultaneous sounds
```

### Preventing Sound Spam

If you fire 8 bullets per second, playing the shoot sound 8 times per second creates a wall of noise. Limit it:

```python
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.cooldowns = {}

    def load(self, name, path, volume=1.0, min_interval=0.0):
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        self.sounds[name] = sound
        self.cooldowns[name] = {"interval": min_interval, "timer": 0.0}

    def update(self, dt):
        for name in self.cooldowns:
            if self.cooldowns[name]["timer"] > 0:
                self.cooldowns[name]["timer"] -= dt

    def play(self, name):
        if name not in self.sounds:
            return
        cd = self.cooldowns[name]
        if cd["timer"] <= 0:
            self.sounds[name].play()
            cd["timer"] = cd["interval"]


sfx = SoundManager()
sfx.load("shoot", "assets/audio/shoot.wav", volume=0.3, min_interval=0.08)
sfx.load("hit", "assets/audio/hit.wav", volume=0.5, min_interval=0.05)
sfx.load("explosion", "assets/audio/explosion.wav", volume=0.7)
sfx.load("player_hurt", "assets/audio/hurt.wav", volume=0.6)

# In game loop:
sfx.update(dt)

# When shooting:
sfx.play("shoot")
```

Now the shoot sound plays at most every 80ms, even if you fire faster.

## Music

Music uses a separate system from sound effects — it streams from disk instead of loading into memory:

```python
# Load and play music
pygame.mixer.music.load("assets/audio/level_theme.ogg")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(loops=-1)  # -1 = loop forever

# Fade in
pygame.mixer.music.play(loops=-1, fade_ms=2000)

# Fade out
pygame.mixer.music.fadeout(1000)  # 1 second fade

# Pause/unpause
pygame.mixer.music.pause()
pygame.mixer.music.unpause()
```

### Music Transitions

When changing levels or entering a boss fight:

```python
def change_music(new_track, fade_out=1000, fade_in=2000):
    """Cross-fade to a new music track."""
    pygame.mixer.music.fadeout(fade_out)
    # Queue the next track (plays after fadeout)
    pygame.mixer.music.queue(new_track)
    # Note: queue doesn't support fade_in, so we use an event
    pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
```

A simpler approach with a timer:

```python
class MusicManager:
    def __init__(self):
        self.current_track = None
        self.next_track = None
        self.transitioning = False
        self.fade_timer = 0.0

    def play(self, track_path, fade_in=2000):
        if track_path == self.current_track:
            return
        if self.current_track:
            pygame.mixer.music.fadeout(1000)
            self.next_track = track_path
            self.transitioning = True
            self.fade_timer = 1.0
        else:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(loops=-1, fade_ms=fade_in)
            self.current_track = track_path

    def update(self, dt):
        if self.transitioning:
            self.fade_timer -= dt
            if self.fade_timer <= 0:
                pygame.mixer.music.load(self.next_track)
                pygame.mixer.music.play(loops=-1, fade_ms=2000)
                self.current_track = self.next_track
                self.next_track = None
                self.transitioning = False
```

## Audio File Formats

| Format | Use For | Why |
|---|---|---|
| WAV | Sound effects | Uncompressed, zero decode latency |
| OGG | Music, long sounds | Compressed, streams from disk |
| MP3 | Music (alternative) | Compressed, wider compatibility |

Sound effects should be WAV — they need to play instantly with no decode delay. Music should be OGG/MP3 — the files are large and streaming is fine since music doesn't need frame-perfect timing.

## Positional Audio (Simple)

Make sounds louder when the source is near the player, quieter when far:

```python
def play_positional(sound, source_pos, listener_pos, max_distance=500):
    """Play a sound with volume based on distance."""
    distance = source_pos.distance_to(listener_pos)
    if distance > max_distance:
        return  # Too far, don't play

    # Linear falloff
    volume = 1.0 - (distance / max_distance)
    volume = max(0.0, min(1.0, volume))

    # Pan left/right based on relative position
    channel = sound.play()
    if channel:
        channel.set_volume(volume, volume)  # Left, right volumes

        # Simple stereo panning
        dx = source_pos.x - listener_pos.x
        pan = dx / max_distance  # -1 (left) to 1 (right)
        left_vol = volume * min(1.0, 1.0 - pan)
        right_vol = volume * min(1.0, 1.0 + pan)
        channel.set_volume(left_vol, right_vol)
```

Now explosions far from the player are quiet, and you can hear which direction they're coming from.

## Generating Placeholder Sounds

No audio files yet? Generate simple ones programmatically:

```python
import numpy as np

def generate_beep(frequency=440, duration=0.1, volume=0.3):
    """Generate a simple sine wave beep."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t) * volume * 32767
    # Fade out to avoid clicks
    fade = np.linspace(1, 0, n_samples // 4)
    wave[-len(fade):] *= fade
    # Convert to 16-bit stereo
    stereo = np.column_stack([wave, wave]).astype(np.int16)
    sound = pygame.sndarray.make_sound(stereo)
    return sound

shoot_sound = generate_beep(880, 0.05, 0.2)
hit_sound = generate_beep(220, 0.1, 0.4)
explosion_sound = generate_beep(110, 0.3, 0.5)
```

Replace with real audio files when available. The system doesn't care where the Sound objects come from.

## Integrating Audio Into the Game

```python
# When player shoots:
if mouse_held[0] and fire_cooldown <= 0:
    aim = (mouse_pos - player.pos).normalize()
    bullet_group.add(Bullet(player.pos, aim * BULLET_SPEED))
    fire_cooldown = 1.0 / FIRE_RATE
    sfx.play("shoot")  # ← Audio feedback

# When bullet hits enemy:
for bullet, enemies_hit in hits.items():
    for enemy in enemies_hit:
        enemy.hp -= 1
        sfx.play("hit")  # ← Audio feedback
        if enemy.hp <= 0:
            enemy.kill()
            sfx.play("explosion")  # ← Audio feedback
            score += 100

# When player takes damage:
if enemy_hits and player.invincible_timer <= 0:
    player.take_damage()
    sfx.play("player_hurt")  # ← Audio feedback
```

Every action has audio feedback. The game feels responsive. Rena can tell when she's hitting things without looking at the HP numbers.

## What You Learned

- **Mixer initialization** — `pre_init` for low-latency audio
- **Sound effects** — load WAV, play on events, control volume
- **Sound cooldowns** — prevent audio spam from rapid-fire
- **Music streaming** — OGG/MP3, looping, fade in/out
- **Music transitions** — cross-fade between tracks
- **Positional audio** — volume falloff and stereo panning by distance
- **Placeholder generation** — numpy sine waves for prototyping

The game has sound. Shots pop. Hits crunch. Music loops. It feels alive.

But the levels are still a single empty room. Enemies spawn randomly in a void. There's no world to explore. Time to build actual levels with tile maps.

---

[← Chapter 5: Sprite Sheets](chapter-05-animation.md) | [Chapter 7: Tile Maps →](chapter-07-tilemaps.md)
