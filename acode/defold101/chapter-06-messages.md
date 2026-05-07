# Chapter 6: Messages — "Objects Need to Talk"

[← Chapter 5: Animation](chapter-05-animation.md) | [Chapter 7: GUI →](chapter-07-gui.md)

---

## The Crisis

The asteroid dies. The explosion plays. But the score doesn't go up. The spawner doesn't know to increase difficulty. The player doesn't know how many lives are left.

In web dev, you'd use a global state store, or emit events, or call a function directly. In Defold, objects are **decoupled**. They can't call each other's functions. They communicate through **messages**.

This is Defold's most important concept. Master it and everything clicks.

## Message Passing: The Core Idea

```lua
-- Send a message to another object
msg.post(receiver_url, message_id, message_data)
```

- **receiver_url** — who gets the message (a game object or component)
- **message_id** — what kind of message (a string, hashed internally)
- **message_data** — optional table of data

```lua
-- Examples:
msg.post("/spawner", "increase_difficulty", { level = 3 })
msg.post("#sprite", "play_animation", { id = hash("explode") })
msg.post("player", "take_damage", { amount = 25 })
```

It's like `postMessage()` in web workers, or Redux actions, or custom DOM events. Asynchronous. Decoupled. The sender doesn't need to know what the receiver does with it.

## Building a Score System

Create a game manager that tracks score and lives:

1. In `main.collection`, add Game Object → name it `game_manager`
2. Add Script → `game_manager.script`

```lua
-- game_manager.script

function init(self)
    self.score = 0
    self.lives = 3
    self.difficulty = 1
end

function on_message(self, message_id, message, sender)
    if message_id == hash("add_score") then
        self.score = self.score + message.points
        -- Tell the GUI to update
        msg.post("/gui#hud", "update_score", { score = self.score })

        -- Increase difficulty every 500 points
        local new_difficulty = math.floor(self.score / 500) + 1
        if new_difficulty > self.difficulty then
            self.difficulty = new_difficulty
            msg.post("/spawner", "set_difficulty", { level = self.difficulty })
        end

    elseif message_id == hash("player_hit") then
        self.lives = self.lives - 1
        msg.post("/gui#hud", "update_lives", { lives = self.lives })

        if self.lives <= 0 then
            msg.post("/gui#hud", "show_game_over", { score = self.score })
        end

    elseif message_id == hash("restart") then
        self.score = 0
        self.lives = 3
        self.difficulty = 1
        msg.post("/gui#hud", "update_score", { score = 0 })
        msg.post("/gui#hud", "update_lives", { lives = 3 })
        msg.post("/spawner", "set_difficulty", { level = 1 })
    end
end
```

## Sending Score from Asteroid

When an asteroid is destroyed by a bullet, it tells the game manager:

```lua
-- asteroid.script (updated on_message)
function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        if message.group == hash("bullet") then
            -- Notify game manager
            msg.post("/game_manager", "add_score", { points = 100 })
            -- Spawn explosion
            msg.post("/spawner", "spawn_explosion", { pos = go.get_position() })
            go.delete()
        end
    end
end
```

## Player Reports Getting Hit

```lua
-- player.script (updated on_message)
function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        if message.group == hash("enemy") then
            -- Tell game manager
            msg.post("/game_manager", "player_hit")
            -- Flash red
            go.set("#sprite", "tint", vmath.vector4(1, 0.3, 0.3, 1))
            timer.delay(0.1, false, function()
                go.set("#sprite", "tint", vmath.vector4(1, 1, 1, 1))
            end)
            -- Brief invincibility (disable collision for 1 second)
            msg.post("#collision_object", "disable")
            timer.delay(1.0, false, function()
                msg.post("#collision_object", "enable")
            end)
        end
    end
end
```

## Dynamic Difficulty

The spawner adjusts based on messages from the game manager:

```lua
-- spawner.script (updated)

local BASE_INTERVAL = 0.8

function init(self)
    self.timer = 0
    self.spawn_interval = BASE_INTERVAL
end

function update(self, dt)
    self.timer = self.timer + dt
    if self.timer >= self.spawn_interval then
        self.timer = self.timer - self.spawn_interval
        self:spawn_asteroid()
    end
end

function spawn_asteroid(self)
    local x = math.random(50, 910)
    local pos = vmath.vector3(x, 580, 0.4)
    factory.create("#asteroid_factory", pos)
end

function on_message(self, message_id, message, sender)
    if message_id == hash("set_difficulty") then
        -- Faster spawning at higher difficulty
        self.spawn_interval = BASE_INTERVAL / message.level
        print("Difficulty: " .. message.level .. " | Interval: " .. self.spawn_interval)

    elseif message_id == hash("spawn_explosion") then
        factory.create("#explosion_factory", message.pos)
    end
end
```

## Message Flow Diagram

```
Asteroid hit by bullet:

  asteroid.script                    game_manager.script
       │                                    │
       ├── msg.post("add_score") ──────────▶│
       │                                    ├── msg.post("/gui#hud", "update_score")
       │                                    ├── msg.post("/spawner", "set_difficulty")
       │                                    │
       ├── msg.post("spawn_explosion") ────▶│ spawner.script
       │                                    ├── factory.create(explosion)
       │
       └── go.delete()

Player hit by asteroid:

  player.script                     game_manager.script
       │                                    │
       ├── msg.post("player_hit") ─────────▶│
       │                                    ├── msg.post("/gui#hud", "update_lives")
       │                                    ├── (if lives == 0) msg.post("show_game_over")
       │
       ├── flash red
       └── disable collision (1s invincibility)
```

## Messages Are Asynchronous

Messages are delivered at the **end of the current frame**, not immediately. This means:

```lua
msg.post("/game_manager", "add_score", { points = 100 })
-- The game_manager hasn't received this yet!
-- It will process it next frame.
```

This is by design — it prevents infinite loops and makes the order predictable. All messages sent during a frame are delivered together before the next frame starts.

## Built-in Messages

Defold has system messages you can send to built-in components:

```lua
-- Enable/disable a component
msg.post("#sprite", "disable")
msg.post("#sprite", "enable")
msg.post("#collision_object", "disable")

-- Play animation
msg.post("#sprite", "play_animation", { id = hash("explosion") })

-- Acquire/release input
msg.post(".", "acquire_input_focus")
msg.post(".", "release_input_focus")

-- Delete a game object
go.delete()  -- delete self
go.delete("/some_object")  -- delete another object
```

## Broadcasting (One-to-Many)

Need to tell ALL enemies to speed up? You can't broadcast natively, but you can use a pattern:

```lua
-- Option 1: Message a manager that tracks all enemies
msg.post("/enemy_manager", "speed_up_all")

-- Option 2: Use a module (shared Lua table)
-- enemies.lua
local M = {}
M.list = {}
function M.register(id) table.insert(M.list, id) end
function M.broadcast(msg_id, data)
    for _, id in ipairs(M.list) do
        msg.post(id, msg_id, data)
    end
end
return M
```

## Verify

1. Shoot asteroids → score increases (check Console prints)
2. Score reaches 500 → asteroids spawn faster
3. Asteroid hits player → lives decrease, player flashes red
4. Player is invincible for 1 second after being hit
5. Lives reach 0 → "GAME OVER" (in Console for now — GUI in Chapter 7)

The game has a loop: dodge, shoot, score, get harder, die. It's a game. A real game.

Mika: "I can't see the score. I need numbers on screen. And a menu."

GUI. Chapter 7.

The jam clock reads 52:00:00.

---

[← Chapter 5: Animation](chapter-05-animation.md) | [Chapter 7: GUI →](chapter-07-gui.md)
