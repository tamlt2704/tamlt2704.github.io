# Chapter 6 — Sound & Music

## Sound System Overview

- **4 channels** (0–3) can play simultaneously
- **64 sound slots** (0–63) to define sounds
- **8 music slots** (0–7) for sequenced tracks
- Sounds use simple waveforms: square, triangle, pulse, noise

## Defining Sounds in Code

```python
import pyxel

pyxel.init(160, 120)

# Define sound 0: a short "coin pickup" blip
pyxel.sounds[0].set(
    notes="c3e3g3c4",     # notes to play
    tones="pppp",          # p=pulse, s=square, t=triangle, n=noise
    volumes="6420",        # volume per note (0-7)
    effects="nnnn",        # n=none, s=slide, v=vibrato, f=fadeout
    speed=7                # playback speed (lower = faster)
)

# Define sound 1: explosion
pyxel.sounds[1].set(
    notes="f1c1f0c0",
    tones="nnnn",          # noise waveform
    volumes="7531",
    effects="ffff",        # fadeout
    speed=10
)

# Define sound 2: jump
pyxel.sounds[2].set(
    notes="c2g2c3",
    tones="ppp",
    volumes="765",
    effects="nnn",
    speed=5
)
```

## Playing Sounds

```python
# Play sound 0 on channel 0
pyxel.play(0, 0)

# Play sound 1 on channel 1 (both play simultaneously)
pyxel.play(1, 1)

# Play sound on any available channel
pyxel.play(0, 0)  # channel 0
```

## Sound Parameters

**Notes:** `c0` to `b4` (C octave 0 to B octave 4), or `r` for rest

```
c  c#  d  d#  e  f  f#  g  g#  a  a#  b
```

**Tones:**
- `p` — pulse (classic chiptune)
- `s` — square
- `t` — triangle (bass-like)
- `n` — noise (percussion, explosions)

**Volumes:** `0` to `7` per note

**Effects:**
- `n` — none
- `s` — slide (portamento to next note)
- `v` — vibrato
- `f` — fadeout

**Speed:** 1–255 (lower = faster playback)

## Using the Sound Editor

```bash
pyxel edit assets.pyxres
```

The Sound tab lets you visually compose sounds by clicking notes on a piano roll.

## Music (Sequencing Sounds)

Music chains multiple sounds together across channels:

```python
# Music slot 0: play sounds 0,1,2,3 in sequence on channel 0
# and sounds 4,5,6,7 on channel 1 simultaneously
pyxel.musics[0].set(
    ch0=[0, 1, 2, 3],    # sound indices for channel 0
    ch1=[4, 5, 6, 7],    # sound indices for channel 1
    ch2=[],               # channel 2 unused
    ch3=[]                # channel 3 unused
)

# Play music 0, looping
pyxel.playm(0, loop=True)

# Stop music
pyxel.stop()  # stops all channels
```

## Practical Example

```python
import pyxel

pyxel.init(160, 120, title="Sound Demo")

# Coin sound
pyxel.sounds[0].set("e3g3c4", "ppp", "642", "nnn", 5)
# Jump sound
pyxel.sounds[1].set("c2e2g2", "ttt", "765", "nns", 4)
# Hit sound
pyxel.sounds[2].set("c1", "n", "7", "f", 15)

def update():
    if pyxel.btnp(pyxel.KEY_1):
        pyxel.play(0, 0)  # coin
    if pyxel.btnp(pyxel.KEY_2):
        pyxel.play(1, 1)  # jump
    if pyxel.btnp(pyxel.KEY_3):
        pyxel.play(2, 2)  # hit
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    pyxel.text(30, 50, "1: Coin  2: Jump  3: Hit", 7)
    pyxel.text(50, 70, "Q: Quit", 13)

pyxel.run(update, draw)
```

## Tips

- Keep sounds short (4–8 notes) for effects
- Use longer sequences for background music
- Channel 3 is often reserved for SFX so music doesn't get interrupted
- Load sounds from `.pyxres` file for complex compositions

## Exercise

Add sounds to the coin collection game from Chapter 5:
- Play a "ding" when collecting a coin
- Play a "buzz" when hitting a wall
- Add simple background music loop

## Next

Chapter 7: Building levels with tilemaps.
