# Chapter 9: Sound — "It Needs Pew Pew"

[← Chapter 8: Camera](chapter-08-camera.md) | [Chapter 10: Levels →](chapter-10-levels.md)

---

## The Crisis

The game is silent. Bullets fire without a sound. Explosions are visual only. Mika found free sound effects on [freesound.org](https://freesound.org) and a chiptune track on [opengameart.org](https://opengameart.org). "Make it sound like a game."

## Sound Components

Sound in Defold is simple: add a Sound component to a game object, reference an audio file, play it with a message.

Supported formats:
- **.ogg** (Vorbis) — for music and long sounds
- **.wav** — for short sound effects

## Adding Sound Effects

### Laser Shot

1. Add `laser.wav` to your project (e.g., `/sounds/laser.wav`)
2. Open `main.collection` → select `player` game object
3. Right-click → Add Component → Sound
4. Properties:
   - **Id**: `laser_sound`
   - **Sound**: `/sounds/laser.wav`
   - **Gain**: `0.5` (50% volume — lasers shouldn't be deafening)

Play it when firing:

```lua
-- player.script (in the fire function)
function fire(self)
    local pos = go.get_position()
    local bullet_pos = vmath.vector3(pos.x, pos.y + 32, 0.6)
    factory.create("#bullet_factory", bullet_pos)

    -- Play laser sound
    msg.post("#laser_sound", "play_sound")
end
```

### Explosion

Add to the explosion game object (`explosion.go`):
1. Add Component → Sound
   - **Id**: `boom_sound`
   - **Sound**: `/sounds/explosion.ogg`
   - **Gain**: `0.7`

```lua
-- explosion.script (updated)
function init(self)
    -- Play explosion sound immediately
    msg.post("#boom_sound", "play_sound")
end
```

### Player Hit

Add to the player:
1. Add Component → Sound
   - **Id**: `hit_sound`
   - **Sound**: `/sounds/hit.wav`
   - **Gain**: `0.6`

```lua
-- In player.script on_message, when hit:
msg.post("#hit_sound", "play_sound")
```

## Background Music

Music is just a longer sound with looping:

1. In `main.collection`, add Game Object → name it `music`
2. Add Component → Sound
   - **Id**: `bgm`
   - **Sound**: `/sounds/space_theme.ogg`
   - **Looping**: checked ✓
   - **Gain**: `0.3` (background music should be quiet)

```lua
-- music.script
function init(self)
    msg.post("#bgm", "play_sound")
end
```

## Sound Properties

```lua
-- Play with options
msg.post("#laser_sound", "play_sound", {
    gain = 0.8,    -- volume (0-1)
    delay = 0,     -- seconds before playing
    speed = 1.2,   -- pitch (1 = normal, 2 = octave up)
})

-- Stop a sound
msg.post("#bgm", "stop_sound")

-- Set gain (volume) dynamically
msg.post("#bgm", "set_gain", { gain = 0.1 })
```

## Sound Groups (Mixing)

Defold supports sound groups for volume control:

In `game.project`:
```ini
[sound]
gain = 1.0
```

You can define groups in the Sound component properties:
- **Group**: `sfx` or `music`

Then control group volume:
```lua
sound.set_group_gain(hash("music"), 0.5)  -- music at 50%
sound.set_group_gain(hash("sfx"), 1.0)    -- effects at 100%
```

This lets players adjust music and SFX independently.

## Preventing Sound Spam

If the player fires 6 times per second, you get 6 overlapping laser sounds. Limit concurrent plays:

```lua
-- player.script
local MAX_CONCURRENT_SOUNDS = 3

function init(self)
    self.active_sounds = 0
end

function fire(self)
    -- ... spawn bullet ...

    if self.active_sounds < MAX_CONCURRENT_SOUNDS then
        self.active_sounds = self.active_sounds + 1
        msg.post("#laser_sound", "play_sound")
    end
end

function on_message(self, message_id, message, sender)
    if message_id == hash("sound_done") then
        self.active_sounds = math.max(0, self.active_sounds - 1)
    end
end
```

The `sound_done` message is sent automatically when a non-looping sound finishes playing.

## Audio Ducking

When an explosion happens, briefly lower the music volume for impact:

```lua
-- explosion.script
function init(self)
    msg.post("#boom_sound", "play_sound")
    -- Duck music
    sound.set_group_gain(hash("music"), 0.1)
    -- Restore after 0.3 seconds
    timer.delay(0.3, false, function()
        sound.set_group_gain(hash("music"), 0.3)
    end)
end
```

## Positional Audio (Bonus)

For stereo panning based on position:

```lua
-- Pan based on X position (left/right)
local pos = go.get_position()
local pan = (pos.x / 960) * 2 - 1  -- -1 (left) to 1 (right)
-- Defold doesn't have built-in panning, but you can use gain on L/R channels
-- or use a sound library that supports it
```

## Verify

1. `Ctrl+B` → background music plays and loops
2. Fire → laser "pew" sound
3. Asteroid explodes → explosion boom + music ducks briefly
4. Player hit → impact sound + screen shake
5. Rapid firing → sounds don't stack excessively
6. Music volume is lower than effects

Mika puts on headphones. Lasers pew. Explosions boom. Music pulses. "It's a game now. A real game. But we need a boss fight. And multiple levels."

Levels. Chapter 10.

The jam clock reads 28:00:00.

---

[← Chapter 8: Camera](chapter-08-camera.md) | [Chapter 10: Levels →](chapter-10-levels.md)
