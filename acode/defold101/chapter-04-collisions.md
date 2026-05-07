# Chapter 4: Collisions — "Things Need to Hit Each Other"

[← Chapter 3: Shooting](chapter-03-shooting.md) | [Chapter 5: Animation →](chapter-05-animation.md)

---

## The Crisis

Bullets fly up. Asteroids fall down (well, they will once you spawn them). But nothing *happens* when they overlap. The bullet passes through the asteroid like a ghost. Mika is not impressed.

"They need to collide. Asteroid explodes. Score goes up. Ship dies if an asteroid hits it."

Defold uses a physics engine (Box2D) for collisions. But you don't need realistic physics — you just need to know when two things overlap.

## Collision Objects: The Invisible Hitbox

A **Collision Object** is a component you add to a game object. It defines:
- **Shape** — the hitbox (circle, box, capsule)
- **Type** — kinematic (you control movement) or dynamic (physics controls it)
- **Group** — what team this object is on ("player", "enemy", "bullet")
- **Mask** — which groups it collides with

```
Web analogy:
  Collision Object ≈ getBoundingClientRect() + intersection check
  But the engine does it for you, every frame, for all objects.
```

## Step 1: Add Collision to the Player

1. Open `main.collection` → select `player`
2. Right-click → Add Component → Collision Object
3. Properties:
   - **Type**: `Kinematic` (we control movement, not physics)
   - **Group**: `player`
   - **Mask**: `enemy` (we collide with enemies)
4. Right-click the Collision Object → Add Shape → Circle
   - Radius: `20` (slightly smaller than the 64px sprite for forgiving hitbox)

## Step 2: Add Collision to the Bullet

Open `bullet.go`:
1. Add Component → Collision Object
2. Properties:
   - **Type**: `Kinematic`
   - **Group**: `bullet`
   - **Mask**: `enemy`
3. Add Shape → Box
   - Width: `4`, Height: `12`

## Step 3: Create the Asteroid

1. New → Game Object → `asteroid.go`
2. Add Sprite → `main.atlas` → `asteroid_01`
3. Add Script → `asteroid.script`
4. Add Collision Object:
   - **Type**: `Kinematic`
   - **Group**: `enemy`
   - **Mask**: `player, bullet` (collides with both)
5. Add Shape → Circle → Radius: `20`

```lua
-- asteroid.script

local SPEED_MIN = 100
local SPEED_MAX = 250

function init(self)
    -- Random downward speed
    self.speed = math.random(SPEED_MIN, SPEED_MAX)
    -- Slight horizontal drift
    self.drift = math.random(-30, 30)
end

function update(self, dt)
    local pos = go.get_position()
    pos.y = pos.y - self.speed * dt
    pos.x = pos.x + self.drift * dt
    go.set_position(pos)

    -- Self-destruct below screen
    if pos.y < -50 then
        go.delete()
    end
end

function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        -- Hit by something! Check what.
        if message.group == hash("bullet") then
            -- Destroyed by bullet
            -- TODO: spawn explosion, add score
            go.delete()
        end
    end
end
```

## Step 4: Spawn Asteroids

Add a spawner to the scene. Create `spawner.script`:

```lua
-- spawner.script

local SPAWN_INTERVAL = 0.8  -- seconds between spawns
local SPAWN_Y = 580         -- above screen

function init(self)
    self.timer = 0
end

function update(self, dt)
    self.timer = self.timer + dt
    if self.timer >= SPAWN_INTERVAL then
        self.timer = self.timer - SPAWN_INTERVAL
        self:spawn_asteroid()
    end
end

function spawn_asteroid(self)
    local x = math.random(50, 910)
    local pos = vmath.vector3(x, SPAWN_Y, 0.4)
    factory.create("#asteroid_factory", pos)
end
```

In `main.collection`:
1. Add Game Object → name it `spawner`
2. Add Component File → `spawner.script`
3. Add Component → Factory → Prototype: `asteroid.go`, Id: `asteroid_factory`

## How Collisions Work

The physics engine checks overlaps every frame. When two collision objects overlap AND their group/mask match:

```
Player (group: "player", mask: "enemy")
Asteroid (group: "enemy", mask: "player, bullet")

Player's mask includes "enemy" ✓
Asteroid's mask includes "player" ✓
→ COLLISION! Both receive messages.
```

Both objects get an `on_message` with `message_id == hash("collision_response")`:

```lua
function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        print("I was hit by: " .. tostring(message.group))
        print("The other object: " .. tostring(message.other_id))
    end
end
```

The `message` table contains:
- `message.other_id` — the game object that hit us
- `message.other_position` — its position
- `message.group` — its collision group

## Step 5: Bullet Hits Asteroid

Update `bullet.script` to self-destruct on hit:

```lua
-- bullet.script (updated)

local SPEED = 800

function update(self, dt)
    local pos = go.get_position()
    pos.y = pos.y + SPEED * dt
    go.set_position(pos)

    if pos.y > 600 then
        go.delete()
    end
end

function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        -- Bullet hit something — destroy self
        go.delete()
    end
end
```

## Step 6: Player Gets Hit

Update `player.script` — add to `on_message`:

```lua
function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        if message.group == hash("enemy") then
            -- Player hit by asteroid!
            print("GAME OVER")
            -- TODO: death animation, restart
        end
    end
end
```

## Collision Groups & Masks Cheat Sheet

| Object | Group | Mask | Collides with |
|---|---|---|---|
| Player | `player` | `enemy` | Asteroids |
| Bullet | `bullet` | `enemy` | Asteroids |
| Asteroid | `enemy` | `player, bullet` | Player and Bullets |

The rule: A collision happens when **A's mask contains B's group** AND **B's mask contains A's group**.

Bullets don't collide with the player (player's mask doesn't include "bullet"). Asteroids don't collide with each other (asteroid's mask doesn't include "enemy").

## Kinematic vs Dynamic vs Trigger

| Type | Behavior | Use case |
|---|---|---|
| **Kinematic** | You move it with code. No gravity. | Player, bullets, enemies |
| **Dynamic** | Physics moves it. Has gravity, mass. | Ragdolls, falling debris |
| **Trigger** | Detects overlap but no physical response | Pickups, zones, checkpoints |

For our game, everything is **Kinematic** — we control all movement ourselves.

## Verify

1. `Ctrl+B` → asteroids fall from the top
2. Shoot an asteroid → both bullet and asteroid disappear
3. Let an asteroid hit the ship → "GAME OVER" prints in Console
4. Bullets pass through each other (no bullet-bullet collision)
5. Asteroids pass through each other (no enemy-enemy collision)

Mika watches an asteroid explode. Well, disappear. "It needs an explosion animation. And the asteroid should break apart."

Animation. Chapter 5.

The jam clock reads 62:30:00.

---

[← Chapter 3: Shooting](chapter-03-shooting.md) | [Chapter 5: Animation →](chapter-05-animation.md)
