# Chapter 7: GUI — "I Need a Menu and HUD"

[← Chapter 6: Messages](chapter-06-messages.md) | [Chapter 8: Camera →](chapter-08-camera.md)

---

## The Crisis

The score exists in a variable. The lives exist in a variable. But the player can't see them. Mika wants: "Score in the top-right. Lives as hearts in the top-left. A start menu. A game over screen with a retry button."

Defold has a separate GUI system — it doesn't use game objects. GUI nodes live in their own coordinate space, always on top, unaffected by the camera.

Think of it like a fixed-position HTML overlay on top of a canvas game.

## GUI vs Game Objects

| | Game Objects | GUI Nodes |
|---|---|---|
| Coordinate space | World (moves with camera) | Screen (fixed position) |
| Rendering | Part of the game scene | Always on top |
| Scripting | `.script` files | `.gui_script` files |
| Use case | Game entities | HUD, menus, buttons |
| Input | `on_input` in scripts | `on_input` in gui_scripts |

## Create the HUD

1. Right-click Assets → New → GUI → name it `hud.gui`
2. Open it — you see a blank canvas representing the screen

### Add Score Text

1. Right-click in Outline → Add → Text Node
2. Properties:
   - **Id**: `score_text`
   - **Text**: `Score: 0`
   - **Font**: `builtins/fonts/default.font`
   - **Position**: X: 860, Y: 520 (top-right area)
   - **Pivot**: `PIVOT_E` (right-aligned)
   - **Color**: white

### Add Lives Display

1. Add → Text Node
2. Properties:
   - **Id**: `lives_text`
   - **Text**: `♥♥♥`
   - **Position**: X: 100, Y: 520 (top-left)
   - **Pivot**: `PIVOT_W` (left-aligned)
   - **Color**: red (#ff4444)

### Add Game Over Panel

1. Add → Box Node (background)
   - **Id**: `gameover_panel`
   - **Size**: 400 × 200
   - **Position**: center of screen (480, 270)
   - **Color**: dark semi-transparent
   - **Visible**: unchecked (hidden by default)

2. Add → Text Node (child of panel)
   - **Id**: `gameover_text`
   - **Text**: `GAME OVER`
   - **Parent**: `gameover_panel`

3. Add → Text Node (child of panel)
   - **Id**: `final_score_text`
   - **Text**: `Score: 0`
   - **Parent**: `gameover_panel`

4. Add → Box Node (retry button)
   - **Id**: `retry_button`
   - **Parent**: `gameover_panel`
   - **Size**: 120 × 40
   - **Color**: blue

5. Add → Text Node (button label)
   - **Id**: `retry_label`
   - **Text**: `RETRY`
   - **Parent**: `retry_button`

## The GUI Script

Create `hud.gui_script`:

```lua
-- hud.gui_script

function init(self)
    -- Hide game over panel initially
    local panel = gui.get_node("gameover_panel")
    gui.set_enabled(panel, false)

    -- Acquire input for button clicks
    msg.post(".", "acquire_input_focus")
end

function on_message(self, message_id, message, sender)
    if message_id == hash("update_score") then
        local node = gui.get_node("score_text")
        gui.set_text(node, "Score: " .. message.score)

    elseif message_id == hash("update_lives") then
        local node = gui.get_node("lives_text")
        local hearts = string.rep("♥", message.lives)
        gui.set_text(node, hearts)

    elseif message_id == hash("show_game_over") then
        local panel = gui.get_node("gameover_panel")
        gui.set_enabled(panel, true)

        local score_node = gui.get_node("final_score_text")
        gui.set_text(score_node, "Score: " .. message.score)

        -- Animate panel appearing (scale from 0 to 1)
        gui.set_scale(panel, vmath.vector3(0, 0, 0))
        gui.animate(panel, "scale", vmath.vector3(1, 1, 1), gui.EASING_OUTBACK, 0.3)
    end
end

function on_input(self, action_id, action)
    if action_id == hash("touch") and action.pressed then
        -- Check if retry button was clicked
        local retry = gui.get_node("retry_button")
        if gui.pick_node(retry, action.x, action.y) then
            -- Hide game over panel
            local panel = gui.get_node("gameover_panel")
            gui.set_enabled(panel, false)
            -- Tell game manager to restart
            msg.post("/game_manager", "restart")
        end
    end
end
```

## Attach GUI to the Collection

In `main.collection`:
1. Add Game Object → name it `gui`
2. Right-click → Add Component File → select `hud.gui`

The GUI component's URL becomes `/gui#hud` — which is what the game manager messages.

## GUI Node API

```lua
-- Get a reference to a node
local node = gui.get_node("score_text")

-- Text
gui.set_text(node, "Hello")
gui.get_text(node)

-- Visibility
gui.set_enabled(node, true/false)

-- Position, scale, color
gui.set_position(node, vmath.vector3(100, 200, 0))
gui.set_scale(node, vmath.vector3(2, 2, 1))
gui.set_color(node, vmath.vector4(1, 0, 0, 1))  -- red

-- Animation (tweening)
gui.animate(node, "position.x", 500, gui.EASING_OUTQUAD, 0.5)
gui.animate(node, "color.w", 0, gui.EASING_LINEAR, 1.0)  -- fade out

-- Hit testing (for buttons)
if gui.pick_node(node, action.x, action.y) then
    -- Clicked!
end
```

## Score Pop Animation

When the score increases, make it pop:

```lua
elseif message_id == hash("update_score") then
    local node = gui.get_node("score_text")
    gui.set_text(node, "Score: " .. message.score)

    -- Pop animation
    gui.set_scale(node, vmath.vector3(1.3, 1.3, 1))
    gui.animate(node, "scale", vmath.vector3(1, 1, 1), gui.EASING_OUTBACK, 0.2)
```

## Start Menu (Bonus)

Create a separate `menu.gui` with:
- Title text: "SPACE SURVIVOR"
- "TAP TO START" text (pulsing animation)
- Credits text

```lua
-- menu.gui_script
function init(self)
    msg.post(".", "acquire_input_focus")

    -- Pulse the "tap to start" text
    local tap_node = gui.get_node("tap_text")
    gui.animate(tap_node, "color.w", 0.3, gui.EASING_INOUTSINE, 0.8, 0, nil, gui.PLAYBACK_LOOP_PINGPONG)
end

function on_input(self, action_id, action)
    if action_id == hash("touch") and action.pressed then
        -- Start the game
        msg.post("/game_manager", "start_game")
        -- Hide menu
        gui.set_enabled(gui.get_node("menu_root"), false)
    end
end
```

## Verify

1. `Ctrl+B` → HUD shows "Score: 0" top-right, "♥♥♥" top-left
2. Shoot asteroids → score updates with pop animation
3. Get hit → one heart disappears
4. Lose all lives → Game Over panel slides in with score
5. Tap Retry → game resets, panel hides, score/lives reset
6. GUI stays fixed even if we add camera movement later

Mika: "The game world needs to be bigger than the screen. I want a scrolling starfield with parallax layers."

Camera. Chapter 8.

The jam clock reads 44:00:00.

---

[← Chapter 6: Messages](chapter-06-messages.md) | [Chapter 8: Camera →](chapter-08-camera.md)
