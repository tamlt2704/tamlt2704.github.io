# Chapter 3: Shooting — "I Need Bullets"

[← Chapter 2: Movement](chapter-02-movement.md) | [Chapter 4: Collisions →](chapter-04-collisions.md)

---

## The Crisis

The ship moves. Mika's asteroids are almost done. "The ship needs to shoot. Bullets go up. Asteroids come down. They collide. Things explode." She says this like it's obvious.

You need to create bullets at runtime. In web dev, you'd `document.createElement("div")`. In Defold, you use a **Factory**.

## Factories: Runtime Object Spawning

A Factory is a component that creates game objects on demand. You define a "template" (a `.go` file), and the factory stamps out copies.

```
Web analogy:
  const bullet = document.createElement("div")
  document.body.appendChild(bullet)

Defold:
  factory.create("#bullet_factory")
```

## Step 1: Create the Bullet Game Object

1. Right-click in Assets → New → Game Object
2. Name it `bullet.go`
3. Open it → Add Component → Sprite
4. Set Image: `main.atlas`, Default Animation: `bullet`
5. Add Component → Script (we'll create `bullet.script`)

The bullet game object is a **template** — it doesn't exist in the scene yet. The factory will spawn copies of it.

## Step 2: The Bullet Script

```lua
-- bullet.script

local SPEED = 800  -- pixels per second (fast!)
local MAX_Y = 600  -- destroy when off screen

function update(self, dt)
    local pos = go.get_position()
    pos.y = pos.y + SPEED * dt
    go.set_position(pos)

    -- Self-destruct when off screen
    if pos.y > MAX_Y then
        go.delete()
    end
end
```

That's it. The bullet moves up every frame and deletes itself when it leaves the screen. No garbage collection worries — `go.delete()` is immediate and clean.

## Step 3: Add a Factory to the Player

1. Open `main.collection`
2. Select the `player` game object
3. Right-click → Add Component → Factory
4. In Properties:
   - **Id**: `bullet_factory`
   - **Prototype**: `/main/bullet.go`

Now the player has three components:
- `sprite` — the ship image
- `player.script` — movement logic
- `bullet_factory` — spawns bullets

## Step 4: Fire on Input

Update `player.script`:

```lua
-- player.script (updated)

local SPEED = 400
local FIRE_RATE = 0.15  -- seconds between shots (6.6 shots/sec)
local BOUNDS_X = { min = 32, max = 928 }
local BOUNDS_Y = { min = 32, max = 508 }

function init(self)
    msg.post(".", "acquire_input_focus")
    self.input = vmath.vector3(0, 0, 0)
    self.shooting = false
    self.fire_cooldown = 0
end

function update(self, dt)
    -- Movement (same as before)
    if vmath.length(self.input) > 0 then
        local direction = vmath.normalize(self.input)
        local movement = direction * SPEED * dt
        local pos = go.get_position()
        pos = pos + movement
        pos.x = math.max(BOUNDS_X.min, math.min(BOUNDS_X.max, pos.x))
        pos.y = math.max(BOUNDS_Y.min, math.min(BOUNDS_Y.max, pos.y))
        go.set_position(pos)
    end

    -- Shooting
    self.fire_cooldown = self.fire_cooldown - dt
    if self.shooting and self.fire_cooldown <= 0 then
        self:fire()
        self.fire_cooldown = FIRE_RATE
    end

    self.input = vmath.vector3(0, 0, 0)
end

function fire(self)
    local pos = go.get_position()
    -- Spawn bullet slightly above the ship
    local bullet_pos = vmath.vector3(pos.x, pos.y + 32, 0.6)
    factory.create("#bullet_factory", bullet_pos)
end

function on_input(self, action_id, action)
    if action_id == hash("move_left") then
        self.input.x = self.input.x - 1
    elseif action_id == hash("move_right") then
        self.input.x = self.input.x + 1
    elseif action_id == hash("move_up") then
        self.input.y = self.input.y + 1
    elseif action_id == hash("move_down") then
        self.input.y = self.input.y - 1
    end

    -- Shoot while space/mouse is held
    if action_id == hash("shoot") then
        if action.pressed then
            self.shooting = true
        elseif action.released then
            self.shooting = false
        end
    end
end
```

## How `factory.create()` Works

```lua
factory.create(factory_url, position, rotation, properties, scale)
```

- **factory_url** — `"#bullet_factory"` (the `#` means "component on this game object")
- **position** — where to spawn (vector3)
- **rotation** — optional (quaternion)
- **properties** — optional table of script properties to override
- **scale** — optional (vector3 or number)

Returns the ID of the created game object. You can store it if you need to track bullets.

## URL Addressing

The `#` in `"#bullet_factory"` is Defold's addressing system:

```lua
"#bullet_factory"           -- component on THIS game object
"player#sprite"             -- sprite component on "player" game object
"/main/player#sprite"       -- full absolute path
```

It's like CSS selectors but for game objects:

| Defold URL | Meaning |
|---|---|
| `"."` | This game object |
| `"#component"` | Component on this game object |
| `"other_object"` | Another game object in the same collection |
| `"/collection/object"` | Absolute path |

## Fire Rate & Cooldown

Without a cooldown, holding space would spawn a bullet every frame (60 bullets/second). The cooldown timer prevents this:

```lua
self.fire_cooldown = self.fire_cooldown - dt  -- count down
if self.shooting and self.fire_cooldown <= 0 then
    self:fire()
    self.fire_cooldown = FIRE_RATE  -- reset timer
end
```

This is a common game dev pattern — timers using `dt` subtraction.

## Bullet Cleanup

Bullets delete themselves when off-screen (`go.delete()`). This is important — without cleanup, you'd have thousands of invisible bullets consuming memory.

In web dev, you'd remove DOM elements. In Defold, `go.delete()` removes the game object and all its components from the engine immediately.

## Verify

1. `Ctrl+B` → ship appears
2. Hold space → bullets stream upward from the ship
3. Bullets disappear when they leave the screen
4. Fire rate is limited (not 60 bullets/frame)
5. You can move AND shoot simultaneously
6. Check Console — no errors, no warnings

Mika watches bullets stream across the starfield. "Beautiful. Now the asteroids need to die when bullets hit them."

Collisions. Chapter 4.

The jam clock reads 66:00:00.

---

[← Chapter 2: Movement](chapter-02-movement.md) | [Chapter 4: Collisions →](chapter-04-collisions.md)
