# Chapter 9: Particles & Effects — Making Hits Feel Powerful

[← Chapter 8: Enemies](chapter-08-enemies.md) | [Chapter 10: UI & Menus →](chapter-10-ui.md)

---

## The Problem

Rena's latest feedback: "I killed an enemy and it just... vanished. No explosion. No sparks. Nothing. It doesn't feel like I did anything powerful."

She's describing the absence of **game juice** — the visual and audio feedback that makes actions feel impactful. A bullet hitting an enemy should produce sparks, a flash, screen shake. An explosion should scatter debris. A dash should leave a trail.

Without juice, a mechanically perfect game feels flat. With juice, even simple mechanics feel incredible.

## Particle Systems

A particle is a tiny visual element with a position, velocity, lifetime, and appearance. A particle system spawns many particles at once and updates them each frame:

```python
class Particle:
    def __init__(self, pos, velocity, color, size, lifetime):
        self.pos = pygame.math.Vector2(pos)
        self.velocity = pygame.math.Vector2(velocity)
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    @property
    def alpha(self):
        """Fade out over lifetime."""
        return self.lifetime / self.max_lifetime

    @property
    def alive(self):
        return self.lifetime > 0

    def update(self, dt):
        self.pos += self.velocity * dt
        self.velocity *= 0.95  # Friction
        self.lifetime -= dt
        self.size = max(0, self.size - dt * 3)  # Shrink over time

    def draw(self, surface, camera_offset=(0, 0)):
        if not self.alive:
            return
        x = int(self.pos.x - camera_offset[0])
        y = int(self.pos.y - camera_offset[1])
        alpha = int(255 * self.alpha)
        color = (*self.color[:3], alpha)

        # For simple particles, just draw a circle
        if self.size > 1:
            pygame.draw.circle(surface, self.color, (x, y), int(self.size))


class ParticleSystem:
    def __init__(self, max_particles=500):
        self.particles = []
        self.max_particles = max_particles

    def emit(self, pos, count, color, speed_range, size_range, lifetime_range, spread=360):
        """Spawn particles in a burst."""
        import math
        for _ in range(count):
            angle = random.uniform(0, math.radians(spread))
            speed = random.uniform(*speed_range)
            velocity = pygame.math.Vector2(
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
            # Rotate to random direction
            velocity.rotate_ip(random.uniform(0, 360))

            size = random.uniform(*size_range)
            lifetime = random.uniform(*lifetime_range)

            # Color variation
            r = min(255, max(0, color[0] + random.randint(-20, 20)))
            g = min(255, max(0, color[1] + random.randint(-20, 20)))
            b = min(255, max(0, color[2] + random.randint(-20, 20)))

            self.particles.append(Particle(pos, velocity, (r, g, b), size, lifetime))

        # Cap particle count
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface, camera_offset=(0, 0)):
        for particle in self.particles:
            particle.draw(surface, camera_offset)
```

## Effect Presets

```python
particles = ParticleSystem()

def emit_hit_sparks(pos):
    """Small yellow sparks when bullet hits."""
    particles.emit(pos, count=8, color=(255, 220, 50),
                   speed_range=(100, 300), size_range=(2, 4),
                   lifetime_range=(0.1, 0.3))

def emit_explosion(pos):
    """Big explosion when enemy dies."""
    # Fire core
    particles.emit(pos, count=20, color=(255, 100, 0),
                   speed_range=(50, 200), size_range=(4, 8),
                   lifetime_range=(0.2, 0.5))
    # Smoke
    particles.emit(pos, count=10, color=(80, 80, 80),
                   speed_range=(20, 80), size_range=(6, 12),
                   lifetime_range=(0.3, 0.8))

def emit_dash_trail(pos):
    """Trail behind player during dash."""
    particles.emit(pos, count=3, color=(0, 255, 180),
                   speed_range=(10, 40), size_range=(3, 6),
                   lifetime_range=(0.1, 0.3))

def emit_blood(pos, direction):
    """Directional blood splatter."""
    for _ in range(6):
        angle = random.uniform(-0.5, 0.5)  # Narrow cone
        speed = random.uniform(100, 250)
        vel = direction.rotate(math.degrees(angle)) * speed
        particles.particles.append(
            Particle(pos, vel, (200, 0, 0), random.uniform(2, 5), random.uniform(0.2, 0.5))
        )
```

## Screen Shake

The most impactful juice technique. When something big happens, shake the camera:

```python
class ScreenShake:
    def __init__(self):
        self.trauma = 0.0  # 0 to 1
        self.decay = 3.0   # How fast trauma decays

    def add_trauma(self, amount):
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt):
        self.trauma = max(0, self.trauma - self.decay * dt)

    def get_offset(self):
        """Get random offset based on current trauma."""
        if self.trauma <= 0:
            return (0, 0)
        # Shake intensity = trauma squared (feels more natural)
        intensity = self.trauma ** 2
        max_offset = 12 * intensity
        ox = random.uniform(-max_offset, max_offset)
        oy = random.uniform(-max_offset, max_offset)
        return (int(ox), int(oy))


shake = ScreenShake()

# When enemy dies:
shake.add_trauma(0.3)

# When player takes damage:
shake.add_trauma(0.5)

# In draw phase:
shake.update(dt)
shake_offset = shake.get_offset()
# Apply offset to everything drawn:
# screen.blit(game_surface, shake_offset)
```

The trick: render everything to a separate surface, then blit that surface to the screen with the shake offset. This shakes the entire view uniformly.

```python
game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Draw everything to game_surface
game_surface.fill(BG_COLOR)
tilemap.draw(game_surface, camera.offset)
# ... draw entities ...

# Apply shake when blitting to screen
screen.blit(game_surface, shake.get_offset())
pygame.display.flip()
```

## Hitstop (Frame Freeze)

When a powerful hit lands, freeze the game for 2-3 frames. It emphasizes the impact:

```python
class Hitstop:
    def __init__(self):
        self.timer = 0.0

    def trigger(self, duration=0.05):
        """Freeze for duration seconds (2-3 frames at 60fps)."""
        self.timer = duration

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt
            return True  # Game is frozen
        return False


hitstop = Hitstop()

# When a big hit lands:
hitstop.trigger(0.04)  # ~2 frames

# In game loop:
frozen = hitstop.update(dt)
if not frozen:
    # Normal update (movement, AI, physics)
    player.update(dt, direction)
    enemy_group.update(dt)
    bullet_group.update(dt)
# Always draw (so the freeze frame is visible)
```

## Flash Effects

### White flash on hit

```python
class FlashEffect:
    def __init__(self):
        self.timer = 0.0
        self.color = (255, 255, 255)

    def trigger(self, duration=0.05, color=(255, 255, 255)):
        self.timer = duration
        self.color = color

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt

    def draw(self, surface, rect):
        if self.timer > 0:
            flash_surface = pygame.Surface(rect.size)
            flash_surface.fill(self.color)
            flash_surface.set_alpha(180)
            surface.blit(flash_surface, rect)
```

### Full-screen flash

```python
def draw_screen_flash(surface, alpha):
    """Brief white flash over entire screen."""
    if alpha > 0:
        flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash.fill((255, 255, 255))
        flash.set_alpha(int(alpha))
        surface.blit(flash, (0, 0))
```

## Putting It All Together

When a bullet hits an enemy:

```python
# In collision handling:
for bullet, enemies_hit in hits.items():
    for enemy in enemies_hit:
        enemy.hp -= 1
        # JUICE:
        emit_hit_sparks(bullet.pos)           # Sparks
        shake.add_trauma(0.1)                  # Small shake
        enemy.flash.trigger(0.05)              # White flash on enemy
        sfx.play("hit")                        # Sound

        if enemy.hp <= 0:
            emit_explosion(enemy.pos)          # Big explosion
            shake.add_trauma(0.3)              # Big shake
            hitstop.trigger(0.04)              # Frame freeze
            sfx.play("explosion")              # Boom
            enemy.kill()
            score += 100
```

One collision triggers five feedback systems. Each one is subtle alone. Together, they make killing an enemy feel *powerful*.

## What You Learned

- **Particle systems** — spawn, update, draw, cull dead particles
- **Effect presets** — sparks, explosions, trails, blood
- **Screen shake** — trauma-based, squared intensity, random offset
- **Hitstop** — freeze frames on impact for emphasis
- **Flash effects** — per-entity and full-screen white flash
- **Juice stacking** — multiple feedback systems per event

The game feels incredible now. Hits land with weight. Explosions scatter particles. The screen shakes on big moments. It's visceral.

But there's no way to start the game, pause it, or see your health clearly. No title screen. No game over. Time to build UI.

---

[← Chapter 8: Enemies](chapter-08-enemies.md) | [Chapter 10: UI & Menus →](chapter-10-ui.md)
