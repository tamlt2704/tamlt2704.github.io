# Chapter 8: Camera — "The Level Is Bigger Than the Screen"

[← Chapter 7: GUI](chapter-07-gui.md) | [Chapter 9: Sound →](chapter-09-sound.md)

---

## The Crisis

Mika drew a vertical scrolling starfield — three parallax layers (distant stars, mid nebula, close asteroids). The game world is 960×5400 (10 screens tall). The camera needs to scroll upward as the player advances.

"I want the background to feel deep. Far stars move slow. Close debris moves fast. Like a real space game."

## The Camera Component

Defold has a built-in camera component, but for 2D games, the community library **Orthographic** is standard:

Add to `game.project` dependencies:
```
https://github.com/britzl/defold-orthographic/archive/master.zip
```

Project → Fetch Libraries.

Or use the built-in camera — simpler for our needs:

1. In `main.collection`, add Game Object → name it `camera`
2. Add Component → Camera
3. Properties:
   - **Fov** (field of view): `45` (for orthographic, this controls zoom)
   - **Near Z**: `-1`
   - **Far Z**: `1`
   - **Projection**: `Fixed` (orthographic, no perspective)

4. Add Script → `camera.script`

```lua
-- camera.script

local SCROLL_SPEED = 50  -- pixels per second upward

function init(self)
    -- Activate this camera
    msg.post("#camera", "acquire_camera_focus")
    -- Start position
    self.y_offset = 0
end

function update(self, dt)
    -- Auto-scroll upward
    self.y_offset = self.y_offset + SCROLL_SPEED * dt

    -- Camera follows player horizontally, scrolls vertically
    local player_pos = go.get_position("/player")
    local cam_x = player_pos.x
    local cam_y = 270 + self.y_offset  -- 270 = half screen height

    go.set_position(vmath.vector3(cam_x, cam_y, 0))
end
```

## Parallax Scrolling

Three background layers at different scroll speeds:

```lua
-- parallax.script (attach to a "parallax_manager" game object)

function init(self)
    self.layers = {
        { id = "/bg_far", speed = 0.2 },    -- distant stars (slow)
        { id = "/bg_mid", speed = 0.5 },    -- nebula (medium)
        { id = "/bg_near", speed = 0.9 },   -- close debris (fast)
    }
end

function update(self, dt)
    local cam_pos = go.get_position("/camera")

    for _, layer in ipairs(self.layers) do
        local pos = go.get_position(layer.id)
        -- Each layer moves at a fraction of camera speed
        pos.y = cam_pos.y * layer.speed
        -- Tile the background (wrap around)
        pos.y = pos.y % 540  -- screen height
        go.set_position(pos, layer.id)
    end
end
```

For infinite scrolling, duplicate each background layer and offset by one screen height. When one scrolls off-screen, reposition it ahead.

## Simpler Approach: Repeating Background

For our jam game, a simpler infinite scroll:

```lua
-- scrolling_bg.script (attach to background game object)

local SCROLL_SPEED = 80  -- pixels per second

function init(self)
    self.offset = 0
end

function update(self, dt)
    self.offset = self.offset + SCROLL_SPEED * dt

    -- Wrap when one full screen has scrolled
    if self.offset >= 540 then
        self.offset = self.offset - 540
    end

    -- Move background down (creates illusion of moving up)
    local pos = go.get_position()
    pos.y = 270 - self.offset
    go.set_position(pos)
end
```

Duplicate the background sprite and offset it by 540px above. Both scroll together, creating a seamless loop.

## World Coordinates vs Screen Coordinates

With a camera, there are now two coordinate systems:

| | World Coordinates | Screen Coordinates |
|---|---|---|
| Used by | Game objects, physics | GUI, input (mouse/touch) |
| Origin | Bottom-left of the world | Bottom-left of the screen |
| Affected by camera | Yes (moves with camera) | No (always fixed) |

When the player taps the screen, `action.x` and `action.y` are in **screen coordinates**. To convert to world coordinates:

```lua
-- Convert screen position to world position
local screen_pos = vmath.vector3(action.x, action.y, 0)
local world_pos = camera.screen_to_world(camera_id, screen_pos)
```

With the orthographic library:
```lua
local world_pos = camera.screen_to_world("/camera#camera", vmath.vector3(action.x, action.y, 0))
```

## Camera Shake

When the player gets hit, shake the camera for impact:

```lua
-- camera.script (add shake function)

function on_message(self, message_id, message, sender)
    if message_id == hash("shake") then
        self.shake_duration = message.duration or 0.3
        self.shake_intensity = message.intensity or 5
    end
end

function update(self, dt)
    -- ... existing scroll code ...

    -- Apply shake
    local shake_offset = vmath.vector3(0, 0, 0)
    if self.shake_duration and self.shake_duration > 0 then
        self.shake_duration = self.shake_duration - dt
        shake_offset.x = math.random(-self.shake_intensity, self.shake_intensity)
        shake_offset.y = math.random(-self.shake_intensity, self.shake_intensity)
    end

    go.set_position(vmath.vector3(cam_x, cam_y, 0) + shake_offset)
end
```

Trigger from player hit:
```lua
msg.post("/camera", "shake", { duration = 0.2, intensity = 8 })
```

## Camera Bounds

Keep the camera from showing empty space beyond the level:

```lua
-- Clamp camera to level bounds
local LEVEL_WIDTH = 960
local LEVEL_HEIGHT = 5400
local HALF_SCREEN_W = 480
local HALF_SCREEN_H = 270

cam_x = math.max(HALF_SCREEN_W, math.min(LEVEL_WIDTH - HALF_SCREEN_W, cam_x))
cam_y = math.max(HALF_SCREEN_H, math.min(LEVEL_HEIGHT - HALF_SCREEN_H, cam_y))
```

## Verify

1. `Ctrl+B` → background scrolls continuously
2. Stars in the back move slowly, debris in front moves fast (parallax)
3. Player moves → camera follows horizontally
4. Get hit → screen shakes briefly
5. GUI (score, lives) stays fixed regardless of camera movement
6. Background loops seamlessly (no visible seam)

Mika watches the parallax layers drift past. "It feels like space now. Add some engine sounds and laser pew-pews."

Sound. Chapter 9.

The jam clock reads 36:00:00.

---

[← Chapter 7: GUI](chapter-07-gui.md) | [Chapter 9: Sound →](chapter-09-sound.md)
