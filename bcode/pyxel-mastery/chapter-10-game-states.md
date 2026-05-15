# Chapter 10 — Game States & Menus

## State Machine

Most games have states: title screen → playing → game over → title screen.

```python
import pyxel

pyxel.init(160, 120, title="State Machine")

STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2

state = STATE_TITLE
score = 0
px, py = 76, 100

def update():
    global state, score, px, py

    if state == STATE_TITLE:
        if pyxel.btnp(pyxel.KEY_SPACE):
            state = STATE_PLAYING
            score = 0
            px, py = 76, 100

    elif state == STATE_PLAYING:
        if pyxel.btn(pyxel.KEY_LEFT):  px -= 2
        if pyxel.btn(pyxel.KEY_RIGHT): px += 2

        score += 1
        if score > 300:  # "win" condition for demo
            state = STATE_GAMEOVER

    elif state == STATE_GAMEOVER:
        if pyxel.btnp(pyxel.KEY_SPACE):
            state = STATE_TITLE

def draw():
    pyxel.cls(0)

    if state == STATE_TITLE:
        pyxel.text(50, 40, "MY GAME", 7)
        pyxel.text(35, 70, "Press SPACE to start", 13)

    elif state == STATE_PLAYING:
        pyxel.rect(px, py, 8, 8, 11)
        pyxel.text(5, 5, f"Score: {score}", 7)

    elif state == STATE_GAMEOVER:
        pyxel.text(45, 40, "GAME OVER", 8)
        pyxel.text(40, 60, f"Score: {score}", 7)
        pyxel.text(30, 80, "SPACE to restart", 13)

pyxel.run(update, draw)
```

## Class-Based States

Cleaner for larger games:

```python
class State:
    def update(self): pass
    def draw(self): pass

class TitleState(State):
    def update(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            return PlayState()
        return self

    def draw(self):
        pyxel.cls(0)
        pyxel.text(50, 40, "MY GAME", 7)
        if pyxel.frame_count % 60 < 40:
            pyxel.text(35, 70, "Press SPACE", 13)

class PlayState(State):
    def __init__(self):
        self.px = 76
        self.score = 0

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):  self.px -= 2
        if pyxel.btn(pyxel.KEY_RIGHT): self.px += 2
        self.score += 1
        if self.score > 300:
            return GameOverState(self.score)
        return self

    def draw(self):
        pyxel.cls(1)
        pyxel.rect(self.px, 100, 8, 8, 11)
        pyxel.text(5, 5, f"Score: {self.score}", 7)

class GameOverState(State):
    def __init__(self, score):
        self.score = score

    def update(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            return TitleState()
        return self

    def draw(self):
        pyxel.cls(0)
        pyxel.text(45, 40, "GAME OVER", 8)
        pyxel.text(40, 60, f"Score: {self.score}", 7)

# Main
import pyxel
pyxel.init(160, 120)
current_state = TitleState()

def update():
    global current_state
    current_state = current_state.update()

def draw():
    current_state.draw()

pyxel.run(update, draw)
```

## Simple Menu with Selection

```python
class MenuState(State):
    def __init__(self):
        self.options = ["Start Game", "Options", "Quit"]
        self.selected = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected = (self.selected - 1) % len(self.options)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected = (self.selected + 1) % len(self.options)
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.selected == 0:
                return PlayState()
            elif self.selected == 2:
                pyxel.quit()
        return self

    def draw(self):
        pyxel.cls(0)
        pyxel.text(55, 20, "MY GAME", 7)
        for i, option in enumerate(self.options):
            color = 10 if i == self.selected else 13
            prefix = "> " if i == self.selected else "  "
            pyxel.text(50, 50 + i * 12, prefix + option, color)
```

## Transitions

Simple fade to black between states:

```python
class FadeTransition(State):
    def __init__(self, next_state):
        self.next_state = next_state
        self.timer = 0
        self.duration = 30

    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            return self.next_state
        return self

    def draw(self):
        # Draw black rects that grow to cover screen
        progress = self.timer / self.duration
        h = int(60 * progress)
        pyxel.rect(0, 0, 160, h, 0)
        pyxel.rect(0, 120 - h, 160, h, 0)
```

## Pause

```python
class PlayState(State):
    def __init__(self):
        self.paused = False
        # ... game state ...

    def update(self):
        if pyxel.btnp(pyxel.KEY_P):
            self.paused = not self.paused

        if not self.paused:
            # ... normal game logic ...
            pass
        return self

    def draw(self):
        pyxel.cls(1)
        # ... draw game ...
        if self.paused:
            pyxel.rect(40, 45, 80, 30, 0)
            pyxel.text(55, 55, "PAUSED", 7)
```

## Exercise

Build a complete flow:
- Title screen with blinking "Press Start"
- Menu with Start / Quit options
- Game state with a simple mechanic
- Game over with score display
- Smooth transitions between states

## Next

Chapter 11: Exporting your game to the web.
