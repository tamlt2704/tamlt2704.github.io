# Chapter 2: Movement — "It Just Sits There"

[← Chapter 1: First Sprite](chapter-01-first-sprite.md) | [Chapter 3: Shooting →](chapter-03-shooting.md)

---

## The Crisis

The ship is on screen. It doesn't move. Mika is drawing asteroids. "When I'm done, those need to fall from the top. And the ship needs to dodge them. You have 2 hours."

Time to write Lua.

## Your First Script

1. Right-click in Assets → New → Script
2. Name it `player.script`
3. Open it

You see a template:

```lua
function init(self)
end

function final(self)
end

function update(self, dt)
end

function on_message(self, message_id, message, sender)
end

function on_input(self, action_id, action)
end

function on_reload(self)
end
```

These are **lifecycle functions**. The engine calls them automatically:

| Function | When | Web equivalent |
|---|---|---|
| `init(self)` | Object created | `constructor()` / `useEffect([], ...)` |
| `update(self, dt)` | Every frame (~60/sec) | `requestAnimationFrame` |
| `on_input(self, action_id, action)` | Key/mouse/touch event | `addEventListener("keydown")` |
| `on_message(self, ...)` | Message received | Custom event / `postMessage` |
| `final(self)` | Object destroyed | `componentWillUnmount` |

## Lua Crash Course (5 Minutes)

```lua
-- Variables (local = scoped, no local = global, AVOID globals)
local speed = 200
local name = "player"
local alive = true

-- Tables (= objects + arrays combined)
local pos = { x = 100, y = 200 }
print(pos.x)  -- 100

-- Arrays are 1-indexed (yes, really)
local items = { "sword", "shield", "potion" }
print(items[1])  -- "sword" (NOT items[0])

-- Functions
local function add(a, b)
    return a + b
end

-- if/else
if speed > 100 then
    print("fast")
elseif speed > 50 then
    print("medium")
else
    print("slow")
end

-- for loop
for i = 1, 10 do
    print(i)
end

-- No classes. Use tables + metatables (or just tables).
-- self is passed explicitly to functions.
```

Key differences from JavaScript:
- `~=` instead of `!=`
- `..` for string concatenation (not `+`)
- `nil` instead of `null`/`undefined`
- Arrays start at 1
- No `===` — just `==`
- `and`/`or`/`not` instead of `&&`/`||`/`!`

## Input Bindings

Before the script can read keyboard input, you need to map keys to actions.

Open `input/game.input_binding`:

| Input | Action |
|---|---|
| KEY_LEFT | `move_left` |
| KEY_RIGHT | `move_right` |
| KEY_UP | `move_up` |
| KEY_DOWN | `move_down` |
| KEY_SPACE | `shoot` |
| MOUSE_BUTTON_1 | `shoot` |

In the editor: double-click `game.input_binding` → add Key Triggers → set the key and action name.

## The Player Script

```lua
-- player.script

-- Constants
local SPEED = 400  -- pixels per second
local BOUNDS_X = { min = 32, max = 928 }  -- keep ship on screen
local BOUNDS_Y = { min = 32, max = 508 }

function init(self)
    -- Tell the engine we want input events
    msg.post(".", "acquire_input_focus")

    -- Movement state
    self.input = vmath.vector3(0, 0, 0)
end

function update(self, dt)
    -- Move based on input
    if vmath.length(self.input) > 0 then
        -- Normalize so diagonal isn't faster
        local direction = vmath.normalize(self.input)
        local movement = direction * SPEED * dt

        -- Apply movement
        local pos = go.get_position()
        pos = pos + movement

        -- Clamp to screen bounds
        pos.x = math.max(BOUNDS_X.min, math.min(BOUNDS_X.max, pos.x))
        pos.y = math.max(BOUNDS_Y.min, math.min(BOUNDS_Y.max, pos.y))

        go.set_position(pos)
    end

    -- Reset input each frame
    self.input = vmath.vector3(0, 0, 0)
end

function on_input(self, action_id, action)
    -- Build input vector from held keys
    if action_id == hash("move_left") then
        self.input.x = self.input.x - 1
    elseif action_id == hash("move_right") then
        self.input.x = self.input.x + 1
    elseif action_id == hash("move_up") then
        self.input.y = self.input.y + 1
    elseif action_id == hash("move_down") then
        self.input.y = self.input.y - 1
    end
end
```

## Attach the Script

1. Open `main.collection`
2. Select the `player` game object
3. Right-click → Add Component File → select `player.script`

Now the player game object has two components:
- `sprite` — how it looks
- `player.script` — how it behaves

## Key Concepts Explained

### `self` — The Script Instance

`self` is a table that belongs to this specific script instance. Store state here:

```lua
function init(self)
    self.health = 100
    self.speed = 400
    self.alive = true
end
```

It's like `this` in JavaScript, but passed explicitly.

### `dt` — Delta Time

`dt` is the time (in seconds) since the last frame. Usually ~0.016 (1/60th of a second).

**Always multiply movement by `dt`**. Otherwise your game runs at different speeds on different devices:

```lua
-- ❌ Wrong: moves 5 pixels per frame (speed depends on FPS)
pos.x = pos.x + 5

-- ✅ Right: moves 300 pixels per second (consistent regardless of FPS)
pos.x = pos.x + 300 * dt
```

### `go.get_position()` / `go.set_position()`

`go` is the **game object** module. It controls the current game object:

```lua
go.get_position()       -- get current position (vector3)
go.set_position(pos)    -- set position
go.get_rotation()       -- get rotation (quaternion)
go.set_scale(2)         -- double the size
go.delete()             -- destroy this game object
```

### `hash()` — String Interning

Defold uses hashed strings for performance. Instead of comparing strings every frame:

```lua
-- Internally, hash("move_left") becomes a number (fast comparison)
if action_id == hash("move_left") then
```

You'll see `hash()` everywhere. It's Defold's way of avoiding string allocations in the hot loop.

### `vmath.vector3` — Math Vectors

Defold has built-in vector math:

```lua
local v = vmath.vector3(1, 2, 0)  -- x, y, z
local len = vmath.length(v)        -- magnitude
local norm = vmath.normalize(v)    -- unit vector
local sum = v + vmath.vector3(3, 4, 0)  -- vector addition
```

## Build & Run

`Ctrl+B`. Arrow keys move the ship. It stays within screen bounds. Diagonal movement is normalized (not faster than cardinal).

## Touch/Mouse Input (Bonus)

For mobile, add touch support:

```lua
function on_input(self, action_id, action)
    -- Existing keyboard input...

    -- Touch/mouse: move toward the touch point
    if action_id == hash("touch") and action.pressed then
        local target = vmath.vector3(action.x, action.y, 0)
        local pos = go.get_position()
        local direction = vmath.normalize(target - pos)
        self.input = direction
    end
end
```

Add `MOUSE_BUTTON_1` → `touch` in your input bindings.

## Verify

1. `Ctrl+B` → ship appears
2. Arrow keys → ship moves smoothly in all directions
3. Diagonal movement is same speed as cardinal
4. Ship can't leave the screen
5. Movement is frame-rate independent (smooth on any machine)

Mika looks at the screen. The ship glides across the starfield. "Nice. Now it needs to shoot."

The jam clock reads 68:15:00.

---

[← Chapter 1: First Sprite](chapter-01-first-sprite.md) | [Chapter 3: Shooting →](chapter-03-shooting.md)
