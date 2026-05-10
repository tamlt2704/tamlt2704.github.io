# Chapter 4: Collision! — Making Things Hit Each Other

[← Chapter 3: Input](chapter-03-input.md) | [Chapter 5: Sprite Sheets →](chapter-05-animation.md)

---

## The Problem

Bullets fly across the screen. Enemies bounce around. But nothing interacts. A bullet passes through an enemy like a ghost. The player walks through walls that don't exist yet. There are no consequences to anything.

Kai sends a message: "I drew explosion sprites. When do things actually die?"

You need collision detection — the system that answers "are these two things overlapping?"

## Rect Collision: The Simple Case

Every entity has a bounding rectangle. Pygame's `Rect` class has built-in collision:

```python
player_rect = pygame.Rect(100, 100, 32, 32)
enemy_rect = pygame.Rect(120, 110, 32, 32)

if player_rect.colliderect(enemy_rect):
    print("Hit!")
```

`colliderect` returns True if two rectangles overlap. It's an axis-aligned bounding box (AABB) test — fast, simple, and wrong for anything that isn't a rectangle.

### Checking Bullets Against Enemies

```python
def check_bullet_hits(bullets, enemies):
    """Check all bullets against all enemies. Remove both on hit."""
    bullets_to_remove = []
    enemies_to_remove = []

    for bullet in bullets:
        bullet_rect = pygame.Rect(
            int(bullet["pos"].x - 4),
            int(bullet["pos"].y - 4),
            8, 8
        )
        for enemy in enemies:
            enemy_rect = pygame.Rect(
                int(enemy.pos.x), int(enemy.pos.y),
                enemy.size, enemy.size
            )
            if bullet_rect.colliderect(enemy_rect):
                bullets_to_remove.append(bullet)
                enemies_to_remove.append(enemy)
                break  # Bullet can only hit one enemy

    for b in bullets_to_remove:
        if b in bullets:
            bullets.remove(b)
    for e in enemies_to_remove:
        if e in enemies:
            enemies.remove(e)
```

This works. But it's O(n × m) — every bullet checked against every enemy. With 100 bullets and 50 enemies, that's 5,000 checks per frame. Fine for now. We'll optimize in Chapter 12.

## Pygame Sprite Groups

Pygame has a built-in system for managing collections of sprites and checking collisions between groups:

```python
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, velocity):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 100))
        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        self.pos = pygame.math.Vector2(pos)
        self.velocity = velocity

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Kill if off-screen
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((28, 28))
        self.image.fill((255, 60, 60))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.hp = 3
        self.velocity = pygame.math.Vector2(
            random.uniform(-1, 1), random.uniform(-1, 1)
        ).normalize() * random.uniform(80, 150)

    def update(self, dt):
        self.pos += self.velocity * dt
        if self.pos.x <= 0 or self.pos.x >= SCREEN_WIDTH - 28:
            self.velocity.x *= -1
        if self.pos.y <= 0 or self.pos.y >= SCREEN_HEIGHT - 28:
            self.velocity.y *= -1
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - 28))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT - 28))
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()


# Create groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# Spawn enemies
for _ in range(10):
    enemy_group.add(Enemy(random.randint(50, 750), random.randint(50, 550)))
```

### Group Collision

```python
# Check all bullets against all enemies
hits = pygame.sprite.groupcollide(bullet_group, enemy_group, True, False)
# True = kill bullet on hit
# False = don't kill enemy (we handle HP manually)

for bullet, enemies_hit in hits.items():
    for enemy in enemies_hit:
        enemy.take_damage(1)
```

`groupcollide` returns a dictionary: `{bullet: [enemies_it_hit]}`. The boolean arguments control whether to auto-kill sprites in each group.

### Player vs. Enemy Collision

```python
# Check if player collides with any enemy
hit_enemies = pygame.sprite.spritecollide(player_sprite, enemy_group, False)
if hit_enemies:
    player.take_damage(1)
```

## Circle Collision

Rectangles are fast but imprecise. A bullet is round. An enemy might be round. Use circle collision for better accuracy:

```python
def circle_collide(pos1, radius1, pos2, radius2):
    """Check if two circles overlap."""
    distance_sq = (pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2
    radius_sum = radius1 + radius2
    return distance_sq <= radius_sum ** 2
```

Note: we compare squared distances to avoid the expensive `sqrt` call. If `distance² ≤ (r1 + r2)²`, the circles overlap.

With Pygame's sprite system, you can pass a custom collision function:

```python
def circle_collision(sprite1, sprite2):
    """Custom collision using circle overlap."""
    pos1 = pygame.math.Vector2(sprite1.rect.center)
    pos2 = pygame.math.Vector2(sprite2.rect.center)
    r1 = sprite1.radius
    r2 = sprite2.radius
    return pos1.distance_squared_to(pos2) <= (r1 + r2) ** 2

hits = pygame.sprite.groupcollide(
    bullet_group, enemy_group, True, False,
    collided=circle_collision
)
```

## Collision Response

Detection tells you *if* things collide. Response tells you *what happens*:

### Bullet hits enemy → damage + destroy bullet

```python
for bullet, enemies_hit in hits.items():
    for enemy in enemies_hit:
        enemy.take_damage(1)
    # Bullet already killed by groupcollide(dokill1=True)
```

### Player hits enemy → knockback + invincibility frames

```python
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # ...
        self.hp = 5
        self.invincible_timer = 0.0
        self.knockback_velocity = pygame.math.Vector2(0, 0)

    def take_damage(self, amount, source_pos):
        if self.invincible_timer > 0:
            return  # Can't be hit during i-frames

        self.hp -= amount
        self.invincible_timer = 1.0  # 1 second of invincibility

        # Knockback away from damage source
        knockback_dir = (self.pos - source_pos)
        if knockback_dir.length() > 0:
            knockback_dir = knockback_dir.normalize()
        self.knockback_velocity = knockback_dir * 400

    def update(self, dt):
        # Invincibility countdown
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        # Apply and decay knockback
        if self.knockback_velocity.length() > 10:
            self.pos += self.knockback_velocity * dt
            self.knockback_velocity *= 0.9  # Friction
        else:
            self.knockback_velocity = pygame.math.Vector2(0, 0)

        # Normal movement...
```

### Visual feedback during invincibility

```python
def draw(self, surface):
    if self.invincible_timer > 0:
        # Blink: visible every other 100ms
        if int(self.invincible_timer * 10) % 2 == 0:
            return  # Skip drawing this frame (blink effect)
    # Normal draw...
```

## Spatial Hashing (Preview)

When you have 500 bullets and 200 enemies, checking every pair is 100,000 tests per frame. Spatial hashing divides the screen into a grid and only checks entities in the same cell:

```python
class SpatialHash:
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.grid = {}

    def clear(self):
        self.grid.clear()

    def _key(self, pos):
        return (int(pos.x // self.cell_size), int(pos.y // self.cell_size))

    def insert(self, entity):
        key = self._key(entity.pos)
        if key not in self.grid:
            self.grid[key] = []
        self.grid[key].append(entity)

    def query(self, pos, radius):
        """Get all entities near a position."""
        results = []
        cx, cy = int(pos.x // self.cell_size), int(pos.y // self.cell_size)
        # Check surrounding cells
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                key = (cx + dx, cy + dy)
                if key in self.grid:
                    results.extend(self.grid[key])
        return results
```

Instead of 100,000 checks, you do ~500 (each bullet only checks entities in nearby cells). We'll implement this properly in Chapter 12 when performance matters.

## The Complete Chapter 4 Code

```python
import pygame
import sys
import random

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Void Runners")
clock = pygame.time.Clock()
FPS = 60
pygame.mouse.set_visible(False)

BG_COLOR = (15, 15, 25)
PLAYER_SPEED = 300
BULLET_SPEED = 600
FIRE_RATE = 8


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 255, 180), (0, 0, 32, 32))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.radius = 14
        self.hp = 5
        self.invincible_timer = 0.0

    def update(self, dt, direction):
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * PLAYER_SPEED * dt
        self.pos.x = max(16, min(self.pos.x, SCREEN_WIDTH - 16))
        self.pos.y = max(16, min(self.pos.y, SCREEN_HEIGHT - 16))
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if self.invincible_timer > 0:
            self.invincible_timer -= dt

    def take_damage(self):
        if self.invincible_timer > 0:
            return
        self.hp -= 1
        self.invincible_timer = 1.5

    def draw(self, surface):
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0:
            return
        surface.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, velocity):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 100), (4, 4), 4)
        self.rect = self.image.get_rect(center=(int(pos.x), int(pos.y)))
        self.pos = pygame.math.Vector2(pos)
        self.velocity = velocity
        self.radius = 4

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if not pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 60, 60), (0, 0, 28, 28))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.radius = 12
        self.hp = 3
        self.velocity = pygame.math.Vector2(
            random.uniform(-1, 1), random.uniform(-1, 1)
        ).normalize() * random.uniform(80, 150)

    def update(self, dt):
        self.pos += self.velocity * dt
        if self.pos.x <= 0 or self.pos.x >= SCREEN_WIDTH - 28:
            self.velocity.x *= -1
        if self.pos.y <= 0 or self.pos.y >= SCREEN_HEIGHT - 28:
            self.velocity.y *= -1
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - 28))
        self.pos.y = max(0, min(self.pos.y, SCREEN_HEIGHT - 28))
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))


# --- Setup ---
player = Player()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

for _ in range(8):
    enemy_group.add(Enemy(random.randint(50, 750), random.randint(50, 550)))

fire_cooldown = 0.0
score = 0
font = pygame.font.Font(None, 36)

running = True
while running:
    dt = min(clock.tick(FPS) / 1000.0, 0.05)
    fire_cooldown = max(0, fire_cooldown - dt)

    # --- Input ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()
    mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
    mouse_held = pygame.mouse.get_pressed()

    direction = pygame.math.Vector2(0, 0)
    if keys[pygame.K_w]:
        direction.y = -1
    if keys[pygame.K_s]:
        direction.y = 1
    if keys[pygame.K_a]:
        direction.x = -1
    if keys[pygame.K_d]:
        direction.x = 1

    # --- Shoot ---
    if mouse_held[0] and fire_cooldown <= 0:
        aim = mouse_pos - player.pos
        if aim.length() > 0:
            aim = aim.normalize()
            bullet_group.add(Bullet(player.pos, aim * BULLET_SPEED))
            fire_cooldown = 1.0 / FIRE_RATE

    # --- Update ---
    player.update(dt, direction)
    bullet_group.update(dt)
    enemy_group.update(dt)

    # --- Collision: bullets vs enemies ---
    hits = pygame.sprite.groupcollide(bullet_group, enemy_group, True, False)
    for bullet, enemies_hit in hits.items():
        for enemy in enemies_hit:
            enemy.hp -= 1
            if enemy.hp <= 0:
                enemy.kill()
                score += 100

    # --- Collision: player vs enemies ---
    if player.invincible_timer <= 0:
        enemy_hits = pygame.sprite.spritecollide(player, enemy_group, False)
        if enemy_hits:
            player.take_damage()

    # --- Respawn enemies ---
    while len(enemy_group) < 8:
        enemy_group.add(Enemy(random.randint(50, 750), random.randint(50, 550)))

    # --- Draw ---
    screen.fill(BG_COLOR)
    player.draw(screen)
    bullet_group.draw(screen)
    enemy_group.draw(screen)

    # HUD
    hp_text = font.render(f"HP: {player.hp}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 10))
    screen.blit(score_text, (10, 40))

    # Crosshair
    mx, my = int(mouse_pos.x), int(mouse_pos.y)
    pygame.draw.line(screen, (255, 255, 255), (mx - 8, my), (mx + 8, my), 1)
    pygame.draw.line(screen, (255, 255, 255), (mx, my - 8), (mx, my + 8), 1)

    pygame.display.flip()

pygame.quit()
sys.exit()
```

Run this. Move with WASD, aim with mouse, hold click to shoot. Enemies take 3 hits to kill. They respawn. You have HP. You blink when hit. There's a score.

It's a game.

## What You Learned

- **Rect collision** — `colliderect()` for AABB overlap detection
- **Sprite groups** — `groupcollide()` and `spritecollide()` for batch checks
- **Circle collision** — distance² vs. radius sum² (no sqrt needed)
- **Collision response** — damage, knockback, invincibility frames
- **Visual feedback** — blinking during i-frames
- **Spatial hashing** — preview of optimization for many entities
- **The game loop** — it's a real game now: move, shoot, hit, score

The game works. Things collide. Enemies die. The player takes damage.

But everything is colored rectangles. Kai has been sending sprite sheets for weeks. Time to make it look like an actual game.

---

[← Chapter 3: Input](chapter-03-input.md) | [Chapter 5: Sprite Sheets →](chapter-05-animation.md)
