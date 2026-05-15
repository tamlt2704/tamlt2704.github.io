# Chapter 12 — Complete Game: Space Shooter

## What We're Building

A vertical scrolling space shooter with:
- Player ship with movement and shooting
- Enemies that spawn and move down
- Collision detection (bullets hit enemies, enemies hit player)
- Score, lives, game over
- Particles for explosions
- Sound effects
- State machine (title → play → game over)

## Full Code

```python
import pyxel
import random
import math

# =============================================================================
# Constants
# =============================================================================

WIDTH = 160
HEIGHT = 120
PLAYER_SPEED = 2
BULLET_SPEED = 4
ENEMY_SPEED = 1
SPAWN_RATE = 30  # frames between enemy spawns

# States
TITLE = 0
PLAYING = 1
GAMEOVER = 2

# =============================================================================
# Entities
# =============================================================================

class Player:
    def __init__(self):
        self.x = WIDTH // 2 - 4
        self.y = HEIGHT - 16
        self.w = 8
        self.h = 8
        self.lives = 3
        self.invincible = 0  # frames of invincibility after hit

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x = max(0, self.x - PLAYER_SPEED)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x = min(WIDTH - self.w, self.x + PLAYER_SPEED)
        if pyxel.btn(pyxel.KEY_UP):
            self.y = max(0, self.y - PLAYER_SPEED)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y = min(HEIGHT - self.h, self.y + PLAYER_SPEED)

        if self.invincible > 0:
            self.invincible -= 1

    def draw(self):
        # Blink when invincible
        if self.invincible > 0 and pyxel.frame_count % 4 < 2:
            return
        pyxel.rect(self.x, self.y, self.w, self.h, 11)
        pyxel.pset(self.x + 3, self.y - 1, 10)  # nose
        pyxel.pset(self.x + 4, self.y - 1, 10)

    def hit(self):
        if self.invincible == 0:
            self.lives -= 1
            self.invincible = 60  # 2 seconds
            return True
        return False


class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 2
        self.h = 4
        self.alive = True

    def update(self):
        self.y -= BULLET_SPEED
        if self.y < -4:
            self.alive = False

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 10)


class Enemy:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 8)
        self.y = -8
        self.w = 8
        self.h = 8
        self.alive = True
        self.speed = ENEMY_SPEED + random.uniform(0, 0.5)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT + 8:
            self.alive = False

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 8)
        pyxel.pset(self.x + 2, self.y + 6, 9)
        pyxel.pset(self.x + 5, self.y + 6, 9)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = random.randint(8, 20)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def is_dead(self):
        return self.life <= 0

    def draw(self):
        pyxel.pset(int(self.x), int(self.y), self.color)


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.color = random.choice([1, 5, 6, 7])

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self):
        pyxel.pset(int(self.x), int(self.y), self.color)

# =============================================================================
# Game
# =============================================================================

class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Space Shooter", fps=30)
        self.setup_sounds()
        self.stars = [Star() for _ in range(30)]
        self.reset()
        self.state = TITLE
        pyxel.run(self.update, self.draw)

    def setup_sounds(self):
        # Shoot sound
        pyxel.sounds[0].set("c3c4", "pp", "64", "nn", 5)
        # Explosion sound
        pyxel.sounds[1].set("f1c1f0", "nnn", "753", "fff", 8)
        # Player hit
        pyxel.sounds[2].set("c1c0", "nn", "75", "ff", 12)
        # Score sound
        pyxel.sounds[3].set("e3g3c4", "ppp", "642", "nnn", 4)

    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.score = 0
        self.spawn_timer = 0
        self.difficulty = 0

    # =========================================================================
    # Update
    # =========================================================================

    def update(self):
        # Stars always animate
        for star in self.stars:
            star.update()

        if self.state == TITLE:
            self.update_title()
        elif self.state == PLAYING:
            self.update_playing()
        elif self.state == GAMEOVER:
            self.update_gameover()

    def update_title(self):
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.reset()
            self.state = PLAYING

    def update_playing(self):
        self.player.update()

        # Shooting
        if pyxel.btnp(pyxel.KEY_SPACE):
            bx = self.player.x + self.player.w // 2 - 1
            by = self.player.y - 4
            self.bullets.append(Bullet(bx, by))
            pyxel.play(0, 0)

        # Update bullets
        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.alive]

        # Spawn enemies
        self.spawn_timer += 1
        spawn_rate = max(10, SPAWN_RATE - self.difficulty)
        if self.spawn_timer >= spawn_rate:
            self.enemies.append(Enemy())
            self.spawn_timer = 0

        # Update enemies
        for e in self.enemies:
            e.update()
        self.enemies = [e for e in self.enemies if e.alive]

        # Increase difficulty over time
        self.difficulty = self.score // 5

        # Bullet-enemy collisions
        for b in self.bullets:
            for e in self.enemies:
                if self.collides(b, e):
                    b.alive = False
                    e.alive = False
                    self.score += 1
                    self.spawn_explosion(e.x + 4, e.y + 4, 8)
                    pyxel.play(1, 1)

        # Enemy-player collisions
        for e in self.enemies:
            if e.alive and self.collides(self.player, e):
                if self.player.hit():
                    e.alive = False
                    self.spawn_explosion(e.x + 4, e.y + 4, 12)
                    pyxel.play(2, 2)
                    if self.player.lives <= 0:
                        self.state = GAMEOVER

        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]

    def update_gameover(self):
        # Keep particles animating
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.state = TITLE

    # =========================================================================
    # Helpers
    # =========================================================================

    def collides(self, a, b):
        return (a.x < b.x + b.w and a.x + a.w > b.x and
                a.y < b.y + b.h and a.y + a.h > b.y)

    def spawn_explosion(self, x, y, count):
        for _ in range(count):
            color = random.choice([8, 9, 10, 2])
            self.particles.append(Particle(x, y, color))

    # =========================================================================
    # Draw
    # =========================================================================

    def draw(self):
        pyxel.cls(0)

        # Stars (always)
        for star in self.stars:
            star.draw()

        if self.state == TITLE:
            self.draw_title()
        elif self.state == PLAYING:
            self.draw_playing()
        elif self.state == GAMEOVER:
            self.draw_gameover()

    def draw_title(self):
        pyxel.text(40, 35, "SPACE SHOOTER", 7)
        if pyxel.frame_count % 60 < 40:
            pyxel.text(38, 60, "Press SPACE", 13)
        pyxel.text(30, 90, "Arrows:Move  Space:Shoot", 5)

    def draw_playing(self):
        self.player.draw()
        for b in self.bullets:
            b.draw()
        for e in self.enemies:
            e.draw()
        for p in self.particles:
            p.draw()

        # HUD
        pyxel.text(5, 5, f"Score:{self.score}", 7)
        pyxel.text(120, 5, f"Lives:{self.player.lives}", 8)

    def draw_gameover(self):
        for p in self.particles:
            p.draw()
        pyxel.text(48, 40, "GAME OVER", 8)
        pyxel.text(45, 55, f"Score: {self.score}", 7)
        if pyxel.frame_count % 60 < 40:
            pyxel.text(35, 80, "SPACE to continue", 13)


# Run
Game()
```

## How to Run

```bash
python space_shooter.py
```

## How to Export

```bash
# Save the code as my_game/main.py
pyxel package my_game main.py
pyxel app2html main.pyxapp
# Open main.html in browser
```

## What This Demonstrates

- Game loop (update/draw separation)
- Input handling
- Entity management (player, bullets, enemies)
- AABB collision detection
- Particle effects
- Sound effects
- State machine (title/play/gameover)
- Difficulty scaling
- Parallax stars background
- Invincibility frames

## Extending Ideas

- Add power-ups (spread shot, shield, speed boost)
- Different enemy types (zigzag, shooting back)
- Boss fights every N points
- High score persistence (write to file in native, localStorage on web)
- Add sprite art instead of colored rectangles
- Add music track for gameplay

## Congratulations!

You now know enough Pyxel to build and publish pixel art games. The key concepts transfer to any game framework:
- Game loop
- Entity management
- Collision detection
- State machines
- Juice (particles, sound, screen shake)

Happy building!
