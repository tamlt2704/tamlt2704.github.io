# Chapter 11: Performance — "It Stutters on My Phone"

[← Chapter 10: Levels](chapter-10-levels.md) | [Chapter 12: Ship It →](chapter-12-ship-it.md)

---

## The Crisis

You test on Mika's old Android phone. The game runs at 40fps. Explosions drop it to 25. The boss fight is a slideshow.

Defold is fast — games ship under 2MB, the engine is native C++. But you can still tank performance with bad patterns. The jam deadline is in 16 hours. Time to profile and fix.

## The Profiler

Defold has a built-in profiler. Enable it:

In `game.project`:
```ini
[profiler]
track_cpu = 1
```

Or toggle at runtime:
```lua
profiler.enable_ui(true)
```

The profiler overlay shows:
- **FPS** — frames per second (target: 60)
- **Frame time** — milliseconds per frame (target: < 16.6ms)
- **Draw calls** — number of GPU draw commands
- **Instances** — active game objects

## Problem 1: Too Many Draw Calls

Each sprite with a different texture = 1 draw call. If you have 50 asteroids using 3 different atlas textures, that's potentially 50 draw calls.

**Fix: One atlas for everything.**

All game sprites should be in a single atlas. The GPU draws them all in one batch:

```
❌ Bad: 5 atlases (player.atlas, enemy.atlas, effects.atlas, bg.atlas, ui.atlas)
   = 5+ draw calls minimum, more with interleaving

✓ Good: 1 atlas (game.atlas) with all sprites
   = 1-2 draw calls for the entire game
```

Check your draw calls in the profiler. For a 2D game, you should have < 10.

## Problem 2: Too Many Game Objects

50 asteroids + 30 bullets + 20 explosions = 100 active game objects. Each one has a transform, components, and runs scripts every frame.

**Fix: Object pooling.**

Instead of `factory.create()` / `go.delete()` (which allocates/deallocates memory), reuse objects:

```lua
-- pool.lua (module)
local M = {}

M.pools = {}

function M.get(pool_name, factory_url, position)
    local pool = M.pools[pool_name]
    if pool and #pool > 0 then
        -- Reuse an existing object
        local id = table.remove(pool)
        go.set_position(position, id)
        msg.post(id, "activate")  -- custom message to re-enable
        return id
    else
        -- Pool empty — create new
        return factory.create(factory_url, position)
    end
end

function M.release(pool_name, id)
    if not M.pools[pool_name] then
        M.pools[pool_name] = {}
    end
    -- "Hide" the object instead of deleting
    go.set_position(vmath.vector3(-1000, -1000, 0), id)
    msg.post(id, "deactivate")  -- custom message to disable
    table.insert(M.pools[pool_name], id)
end

return M
```

Usage in bullet script:
```lua
local pool = require("pool")

-- Instead of go.delete():
function deactivate(self)
    msg.post("#collision_object", "disable")
    msg.post("#sprite", "disable")
end

-- In spawner, instead of factory.create():
local bullet_id = pool.get("bullets", "#bullet_factory", spawn_pos)
```

## Problem 3: Expensive Update Loops

Every script's `update()` runs every frame. If 50 asteroids each do math every frame:

```lua
-- ❌ Expensive: runs 50 × 60 = 3000 times per second
function update(self, dt)
    local pos = go.get_position()
    pos.y = pos.y - self.speed * dt
    go.set_position(pos)
end
```

**Fix: Use `go.animate()` for simple movement.**

```lua
-- ✓ Cheap: engine handles the animation natively (no Lua per frame)
function init(self)
    local duration = 540 / self.speed  -- time to cross screen
    go.animate(".", "position.y", go.PLAYBACK_ONCE_FORWARD, -50, go.EASING_LINEAR, duration)
end

function update(self, dt)
    -- Empty! No per-frame Lua needed for movement.
end
```

`go.animate()` runs in C++, not Lua. It's significantly faster for simple linear/eased movement.

## Problem 4: Garbage Collection Spikes

Lua has a garbage collector. Creating tables every frame causes GC pauses:

```lua
-- ❌ Creates a new vector3 every frame (garbage)
function update(self, dt)
    local movement = vmath.vector3(0, -self.speed * dt, 0)
    go.set_position(go.get_position() + movement)
end

-- ✓ Reuse a pre-allocated vector
function init(self)
    self.movement = vmath.vector3(0, 0, 0)
end

function update(self, dt)
    self.movement.y = -self.speed * dt
    go.set_position(go.get_position() + self.movement)
end
```

Also avoid creating tables in hot loops:
```lua
-- ❌ New table every frame
msg.post("#sound", "play_sound", { gain = 0.5 })

-- ✓ Reuse
local SOUND_PARAMS = { gain = 0.5 }
msg.post("#sound", "play_sound", SOUND_PARAMS)
```

## Problem 5: Too Many Collision Checks

Physics checks every collision object against every other one (filtered by group/mask). 50 asteroids × 30 bullets = 1500 potential checks per frame.

**Fix: Disable collisions on off-screen objects.**

```lua
function update(self, dt)
    local pos = go.get_position()
    -- Only enable collision when on screen
    if pos.y < 600 and pos.y > -50 then
        msg.post("#collision_object", "enable")
    else
        msg.post("#collision_object", "disable")
    end
end
```

## Problem 6: Texture Memory

Large textures eat GPU memory. A 2048×2048 atlas uses 16MB of VRAM.

**Fix:**
- Use the smallest atlas size that fits your sprites
- Enable texture compression in `game.project`:

```ini
[graphics]
texture_profiles = /builtins/graphics/default.texture_profiles
```

Create a custom texture profile that compresses for mobile:
- **PVRTC** for iOS
- **ETC2** for Android
- **WebP** for HTML5

## The Performance Checklist

| Issue | Fix | Impact |
|---|---|---|
| Many draw calls | Single atlas | High |
| Object creation/deletion | Object pooling | High |
| Per-frame Lua movement | `go.animate()` | Medium |
| GC spikes | Reuse tables/vectors | Medium |
| Too many collision checks | Disable off-screen | Medium |
| Large textures | Compression profiles | Medium (mobile) |
| Complex scripts on many objects | Simplify update loops | Medium |

## Measuring the Fix

Before optimization (Mika's phone):
```
FPS: 38-45
Draw calls: 47
Game objects: 120
Frame time: 24ms
```

After optimization:
```
FPS: 58-60
Draw calls: 3
Game objects: 45 (pooled)
Frame time: 8ms
```

## Verify

1. Enable profiler → check FPS stays at 60
2. Boss fight with many bullets → no frame drops
3. 50 asteroids on screen → smooth scrolling
4. Explosions don't cause GC spikes
5. Test on a low-end device → still playable

Mika's phone runs at 60fps. The boss fight is smooth. Explosions pop without stuttering.

"It works. Ship it. We have 8 hours left."

Ship it. Chapter 12.

The jam clock reads 08:00:00.

---

[← Chapter 10: Levels](chapter-10-levels.md) | [Chapter 12: Ship It →](chapter-12-ship-it.md)
