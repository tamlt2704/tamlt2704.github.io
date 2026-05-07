# Chapter 5: Animation — "Mika Sent 200 Frames"

[← Chapter 4: Collisions](chapter-04-collisions.md) | [Chapter 6: Messages →](chapter-06-messages.md)

---

## The Crisis

Mika sends a zip file. Inside: `explosion_01.png` through `explosion_12.png`. Twelve frames of a fireball. "Play these when an asteroid dies. 24fps. Loop once."

She also sends `ship_idle_01.png` through `ship_idle_04.png` — the ship's engine flickering. "This loops forever."

In web dev, you'd use CSS `@keyframes` or a GIF. In Defold, you use **flip-book animations** inside an atlas.

## Animation Groups in the Atlas

Open `main.atlas`. Instead of adding individual images, you create an **Animation Group**:

1. Right-click in Outline → Add Animation Group
2. Name it `explosion`
3. Right-click the group → Add Images → select all 12 explosion frames
4. Properties:
   - **Fps**: `24`
   - **Playback**: `Once Forward` (play once, then stop)

Repeat for the ship idle:
1. Add Animation Group → name it `ship_idle`
2. Add the 4 idle frames
3. Properties:
   - **Fps**: `8`
   - **Playback**: `Loop Forward` (repeat forever)

Your atlas now has:

```
main.atlas
├── ship (static, single frame — for when we need it)
├── ship_idle (animation, 4 frames, loops)
├── space_bg (static)
├── bullet (static)
├── asteroid_01 (static)
├── explosion (animation, 12 frames, plays once)
```

## Playback Modes

| Mode | Behavior |
|---|---|
| `None` | Static image (no animation) |
| `Once Forward` | Play 1→12, then stop on last frame |
| `Once Backward` | Play 12→1, then stop |
| `Once Ping Pong` | Play 1→12→1, then stop |
| `Loop Forward` | Play 1→12, repeat forever |
| `Loop Backward` | Play 12→1, repeat forever |
| `Loop Ping Pong` | Play 1→12→1→12..., forever |

## Playing Animations from Script

Update the player's sprite to use the animated idle:

In `main.collection`, select the player's sprite component:
- Change **Default Animation** from `ship` to `ship_idle`

Done. The ship's engine now flickers automatically.

To change animations at runtime (e.g., switch to a "damaged" animation):

```lua
-- Play a different animation on this sprite
msg.post("#sprite", "play_animation", { id = hash("ship_damaged") })
```

## Explosion Effect

Create `explosion.go`:

1. New → Game Object → `explosion.go`
2. Add Sprite → `main.atlas` → Default Animation: `explosion`
3. Add Script → `explosion.script`

```lua
-- explosion.script

function init(self)
    -- The animation plays automatically (it's the default animation)
    -- We just need to delete ourselves when it finishes
end

function on_message(self, message_id, message, sender)
    if message_id == hash("animation_done") then
        -- Animation finished playing → remove the explosion
        go.delete()
    end
end
```

Wait — how does the script know when the animation ends? The sprite component sends an `animation_done` message to its game object's script when a "Once" animation completes.

## Spawning Explosions on Asteroid Death

Update `asteroid.script`:

```lua
function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        if message.group == hash("bullet") then
            -- Spawn explosion at our position
            local pos = go.get_position()
            factory.create("#explosion_factory", pos)
            -- Delete the asteroid
            go.delete()
        end
    end
end
```

But wait — the asteroid doesn't have an explosion factory. We have two options:

**Option A**: Add the factory to each asteroid (wasteful — every asteroid carries a factory).

**Option B**: Put the factory on a manager object and send it a message (better).

Let's use Option B. Add to the `spawner` game object:
1. Add Component → Factory → Prototype: `explosion.go`, Id: `explosion_factory`

Update `asteroid.script` to message the spawner:

```lua
function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        if message.group == hash("bullet") then
            -- Tell spawner to create explosion at our position
            msg.post("/spawner#spawner", "spawn_explosion", { pos = go.get_position() })
            go.delete()
        end
    end
end
```

Update `spawner.script`:

```lua
function on_message(self, message_id, message, sender)
    if message_id == hash("spawn_explosion") then
        factory.create("#explosion_factory", message.pos)
    end
end
```

## Sprite Flip (Facing Direction)

If the ship moves left, flip the sprite horizontally:

```lua
-- In player.script update()
if self.input.x < 0 then
    sprite.set_hflip("#sprite", true)
elseif self.input.x > 0 then
    sprite.set_hflip("#sprite", false)
end
```

## Tinting and Flashing

Make the player flash red when hit:

```lua
-- Flash red
go.set("#sprite", "tint", vmath.vector4(1, 0.3, 0.3, 1))

-- Reset after 0.1 seconds
timer.delay(0.1, false, function()
    go.set("#sprite", "tint", vmath.vector4(1, 1, 1, 1))
end)
```

`tint` is a vector4 (r, g, b, a). Default is (1, 1, 1, 1) — full white = no tint.

## Property Animation (Tweening)

Defold has built-in tweening with `go.animate()`:

```lua
-- Fade out over 0.5 seconds
go.animate(".", "tint.w", go.PLAYBACK_ONCE_FORWARD, 0, go.EASING_LINEAR, 0.5)

-- Scale up (pop effect) then back down
go.animate(".", "scale", go.PLAYBACK_ONCE_PINGPONG, vmath.vector3(1.3, 1.3, 1), go.EASING_OUTBACK, 0.2)

-- Move to a position over 1 second with easing
go.animate(".", "position.y", go.PLAYBACK_ONCE_FORWARD, 300, go.EASING_OUTQUAD, 1.0)
```

This is like CSS transitions but controlled from code. Available easings: `LINEAR`, `INQUAD`, `OUTQUAD`, `INOUTQUAD`, `OUTBACK`, `OUTBOUNCE`, `OUTELASTIC`, etc.

## Verify

1. `Ctrl+B` → ship engine flickers (idle animation loops)
2. Shoot an asteroid → explosion animation plays at its position
3. Explosion disappears after the animation completes (12 frames at 24fps = 0.5s)
4. No explosion objects accumulate (check with profiler)
5. Ship flashes red briefly when hit by asteroid

Mika watches explosions bloom across the starfield. "Now we need a score counter. And the enemies need to get harder over time. How do objects talk to each other?"

Messages. Chapter 6.

The jam clock reads 58:00:00.

---

[← Chapter 4: Collisions](chapter-04-collisions.md) | [Chapter 6: Messages →](chapter-06-messages.md)
