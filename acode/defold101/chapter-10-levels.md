# Chapter 10: Levels — "We Need a Boss Fight"

[← Chapter 9: Sound](chapter-09-sound.md) | [Chapter 11: Performance →](chapter-11-performance.md)

---

## The Crisis

The game is one endless wave of asteroids. Mika drew a boss — a giant alien ship with three attack patterns. "I want: Level 1 (asteroids), Level 2 (asteroids + small enemies), Boss Fight. Then it loops harder."

You need to load and unload entire scenes at runtime. In web dev, this is like routing — showing different pages. In Defold, it's **Collection Proxies**.

## Collection Proxies: Loading Scenes at Runtime

A Collection Proxy is a component that can load/unload an entire collection (scene) at runtime. Think of it as lazy-loaded routes:

```
Web:     React Router → lazy(() => import("./BossLevel"))
Defold:  Collection Proxy → loads "boss.collection" on demand
```

## Restructuring the Project

Current structure (everything in one collection):
```
main.collection
├── player
├── spawner
├── camera
├── game_manager
└── gui
```

New structure (separated into loadable levels):
```
main.collection (always loaded — the "shell")
├── game_manager
├── gui
└── level_proxy (Collection Proxy → loads level collections)

level1.collection (asteroids only)
├── player
├── spawner
├── camera
├── background

level2.collection (asteroids + enemies)
├── player
├── enemy_spawner
├── camera
├── background

boss.collection (boss fight)
├── player
├── boss
├── camera
├── arena_background
```

## Step 1: Create Level Collections

1. New → Collection → `level1.collection`
2. Move the player, spawner, camera, and background into it
3. New → Collection → `boss.collection`
4. Add a boss game object with its own script

## Step 2: Add Collection Proxy to Main

In `main.collection`:
1. Select `game_manager` game object
2. Add Component → Collection Proxy
3. Properties:
   - **Id**: `level_proxy`
   - **Collection**: `/main/level1.collection`

## Step 3: Loading and Unloading

```lua
-- game_manager.script (updated)

function init(self)
    self.current_level = 1
    self.score = 0
    self.lives = 3

    -- Load the first level
    msg.post("#level_proxy", "load")
end

function on_message(self, message_id, message, sender)
    if message_id == hash("proxy_loaded") then
        -- Collection is loaded into memory — now initialize it
        msg.post(sender, "init")
        msg.post(sender, "enable")

    elseif message_id == hash("level_complete") then
        -- Unload current level
        msg.post("#level_proxy", "disable")
        msg.post("#level_proxy", "final")
        msg.post("#level_proxy", "unload")

    elseif message_id == hash("proxy_unloaded") then
        -- Load next level
        self.current_level = self.current_level + 1
        local next_collection = self:get_level_collection()
        -- Change the proxy's collection reference
        go.set("#level_proxy", "collection", next_collection)
        msg.post("#level_proxy", "load")

    elseif message_id == hash("add_score") then
        self.score = self.score + message.points
        msg.post("/gui#hud", "update_score", { score = self.score })
    end
end

function get_level_collection(self)
    if self.current_level == 1 then
        return "/main/level1.collectionc"
    elseif self.current_level == 2 then
        return "/main/level2.collectionc"
    elseif self.current_level == 3 then
        return "/main/boss.collectionc"
    else
        -- Loop back with increased difficulty
        self.current_level = 1
        return "/main/level1.collectionc"
    end
end
```

Note the `c` suffix — at runtime, collections are compiled to `.collectionc`.

## The Proxy Lifecycle

```
load → proxy_loaded → init → enable → [game runs] → disable → final → unload → proxy_unloaded
```

| Step | What happens |
|---|---|
| `load` | Loads the collection into memory (async) |
| `proxy_loaded` | Message sent when loading is complete |
| `init` | Calls `init()` on all scripts in the collection |
| `enable` | Makes everything visible and active |
| `disable` | Hides everything, stops updates |
| `final` | Calls `final()` on all scripts |
| `unload` | Frees memory |

## The Boss Fight

```lua
-- boss.script

local PHASE_1_HP = 100
local PHASE_2_HP = 50

function init(self)
    self.hp = PHASE_1_HP + PHASE_2_HP
    self.phase = 1
    self.attack_timer = 0
    self.pattern_index = 1

    -- Enter from top of screen
    go.animate(".", "position.y", go.PLAYBACK_ONCE_FORWARD, 420, go.EASING_OUTQUAD, 1.5)
end

function update(self, dt)
    self.attack_timer = self.attack_timer + dt

    if self.phase == 1 then
        self:phase1_behavior(dt)
    else
        self:phase2_behavior(dt)
    end
end

function phase1_behavior(self, dt)
    -- Sway left and right
    local pos = go.get_position()
    pos.x = 480 + math.sin(self.attack_timer * 2) * 200
    go.set_position(pos)

    -- Fire bullets downward every 0.5 seconds
    if self.attack_timer % 0.5 < dt then
        factory.create("#boss_bullet_factory", go.get_position())
    end
end

function phase2_behavior(self, dt)
    -- Faster, more aggressive
    local pos = go.get_position()
    pos.x = 480 + math.sin(self.attack_timer * 4) * 300
    go.set_position(pos)

    -- Spread shot every 0.3 seconds
    if self.attack_timer % 0.3 < dt then
        local base_pos = go.get_position()
        for angle = -30, 30, 15 do
            local rad = math.rad(angle - 90)
            local dir = vmath.vector3(math.cos(rad), math.sin(rad), 0)
            factory.create("#boss_bullet_factory", base_pos, nil, { direction = dir })
        end
    end
end

function on_message(self, message_id, message, sender)
    if message_id == hash("collision_response") then
        if message.group == hash("bullet") then
            self.hp = self.hp - 10

            -- Flash white
            go.set("#sprite", "tint", vmath.vector4(3, 3, 3, 1))
            timer.delay(0.05, false, function()
                go.set("#sprite", "tint", vmath.vector4(1, 1, 1, 1))
            end)

            -- Phase transition
            if self.hp <= PHASE_2_HP and self.phase == 1 then
                self.phase = 2
                self.attack_timer = 0
                -- Visual change
                msg.post("#sprite", "play_animation", { id = hash("boss_angry") })
                msg.post("/camera", "shake", { duration = 0.5, intensity = 10 })
            end

            -- Death
            if self.hp <= 0 then
                msg.post("/game_manager", "add_score", { points = 5000 })
                msg.post("/game_manager", "level_complete")
                -- Epic explosion
                for i = 1, 8 do
                    timer.delay(i * 0.1, false, function()
                        local offset = vmath.vector3(math.random(-40, 40), math.random(-40, 40), 0)
                        msg.post("/spawner", "spawn_explosion", { pos = go.get_position() + offset })
                    end)
                end
                timer.delay(1.0, false, function() go.delete() end)
            end
        end
    end
end
```

## Level Completion Trigger

In `level1.collection`, the spawner tracks when enough asteroids have been destroyed:

```lua
-- spawner.script (add level completion)
function on_message(self, message_id, message, sender)
    if message_id == hash("asteroid_destroyed") then
        self.destroyed_count = self.destroyed_count + 1
        if self.destroyed_count >= 30 then
            -- Level complete!
            msg.post("/game_manager", "level_complete")
        end
    end
end
```

## Game State Machine

The game manager becomes a state machine:

```lua
-- States: MENU → PLAYING → BOSS → GAME_OVER → MENU
function on_message(self, message_id, message, sender)
    if message_id == hash("start_game") then
        self.state = "PLAYING"
        msg.post("#level_proxy", "load")

    elseif message_id == hash("level_complete") and self.state == "PLAYING" then
        -- Transition to next level
        self.state = "TRANSITIONING"
        -- Show "Level Complete!" for 2 seconds
        msg.post("/gui#hud", "show_level_complete", { level = self.current_level })
        timer.delay(2.0, false, function()
            msg.post("#level_proxy", "disable")
            msg.post("#level_proxy", "final")
            msg.post("#level_proxy", "unload")
        end)
    end
end
```

## Verify

1. Game starts → Level 1 loads (asteroids)
2. Destroy 30 asteroids → "Level Complete!" → Level 2 loads
3. Level 2 has faster asteroids + small enemies
4. Complete Level 2 → Boss appears with entrance animation
5. Boss Phase 1: sways and shoots downward
6. Reduce HP to 50% → Phase 2: faster, spread shots, angry sprite
7. Kill boss → epic multi-explosion → "Level Complete!"
8. Game loops back to Level 1 with increased difficulty

Mika watches the boss explode in a cascade of fireballs. "SHIP IT. But wait — it stutters on my phone."

Performance. Chapter 11.

The jam clock reads 16:00:00.

---

[← Chapter 9: Sound](chapter-09-sound.md) | [Chapter 11: Performance →](chapter-11-performance.md)
