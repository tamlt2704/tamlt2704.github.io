# Chapter 8: Enemies That Think — AI and Behavior

[← Chapter 7: Tile Maps](chapter-07-tilemaps.md) | [Chapter 9: Particles & Effects →](chapter-09-particles.md)

---

## The Problem

Rena: "The enemies are boring. They just bounce off walls like screensavers. They don't chase me. They don't do anything interesting. I don't feel threatened."

She's right. Bouncing enemies are obstacles, not opponents. For Void Runners to feel like a real action game, enemies need behavior — chasing, patrolling, attacking, retreating.

## Finite State Machines

The simplest AI pattern: each enemy is in one **state**, and transitions between states based on conditions:

```
┌─────────┐  player nearby   ┌─────────┐  in range   ┌──────────┐
│  IDLE   │ ───────────────→ │  CHASE  │ ──────────→ │  ATTACK  │
└─────────┘                  └─────────┘             └──────────┘
     ↑                            │                       │
     │         player far         │    attack done        │
     └────────────────────────────┘←──────────────────────┘
```

```python
class EnemyState:
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    RETREAT = "retreat"


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="grunt"):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 120
        self.hp = 3
        self.state = EnemyState.IDLE
        self.state_timer = 0.0

        # Detection ranges
        self.detect_range = 200   # Start chasing
        self.attack_range = 40    # Start attacking
        self.lose_range = 350     # Stop chasing

        # Attack
        self.attack_cooldown = 0.0
        self.attack_rate = 1.0  # attacks per second

        # Patrol
        self.patrol_points = []
        self.patrol_index = 0

        # Visual
        self.size = 28
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 60, 60), (0, 0, self.size, self.size))
        self.rect = self.image.get_rect(topleft=(int(x), int(y)))

    def update(self, dt, player_pos, tilemap):
        distance_to_player = self.pos.distance_to(player_pos)
        self.state_timer += dt
        self.attack_cooldown = max(0, self.attack_cooldown - dt)

        # State transitions
        if self.state == EnemyState.IDLE:
            self._idle(dt, distance_to_player)
        elif self.state == EnemyState.PATROL:
            self._patrol(dt, distance_to_player)
        elif self.state == EnemyState.CHASE:
            self._chase(dt, player_pos, distance_to_player)
        elif self.state == EnemyState.ATTACK:
            self._attack(dt, player_pos, distance_to_player)
        elif self.state == EnemyState.RETREAT:
            self._retreat(dt, player_pos, distance_to_player)

        # Apply velocity with tilemap collision
        self.pos += self.velocity * dt
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def _set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.state_timer = 0.0

    def _idle(self, dt, distance):
        self.velocity = pygame.math.Vector2(0, 0)
        if distance < self.detect_range:
            self._set_state(EnemyState.CHASE)
        elif self.state_timer > 2.0 and self.patrol_points:
            self._set_state(EnemyState.PATROL)

    def _patrol(self, dt, distance):
        if distance < self.detect_range:
            self._set_state(EnemyState.CHASE)
            return

        if not self.patrol_points:
            self._set_state(EnemyState.IDLE)
            return

        target = self.patrol_points[self.patrol_index]
        direction = target - self.pos
        if direction.length() < 5:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
        elif direction.length() > 0:
            self.velocity = direction.normalize() * self.speed * 0.5

    def _chase(self, dt, player_pos, distance):
        if distance > self.lose_range:
            self._set_state(EnemyState.IDLE)
            return
        if distance < self.attack_range:
            self._set_state(EnemyState.ATTACK)
            return

        direction = player_pos - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed

    def _attack(self, dt, player_pos, distance):
        self.velocity = pygame.math.Vector2(0, 0)

        if distance > self.attack_range * 2:
            self._set_state(EnemyState.CHASE)
            return

        if self.attack_cooldown <= 0:
            self.attack_cooldown = 1.0 / self.attack_rate
            return True  # Signal: attack happened

    def _retreat(self, dt, player_pos, distance):
        if distance > self.detect_range:
            self._set_state(EnemyState.IDLE)
            return

        direction = self.pos - player_pos  # Away from player
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed * 0.8
```

## Enemy Types

Different enemies, different behaviors:

```python
class Grunt(Enemy):
    """Charges straight at the player. Simple but dangerous in groups."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 140
        self.hp = 2
        self.detect_range = 250
        self.attack_range = 30


class Shooter(Enemy):
    """Keeps distance, fires projectiles."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 80
        self.hp = 2
        self.detect_range = 300
        self.attack_range = 150  # Attacks from far away
        self.preferred_distance = 180

    def _chase(self, dt, player_pos, distance):
        if distance > self.lose_range:
            self._set_state(EnemyState.IDLE)
            return
        if distance < self.attack_range:
            self._set_state(EnemyState.ATTACK)
            return
        # Move toward player
        direction = player_pos - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed

    def _attack(self, dt, player_pos, distance):
        # Maintain preferred distance
        if distance < self.preferred_distance * 0.7:
            self._set_state(EnemyState.RETREAT)
            return
        if distance > self.attack_range * 1.2:
            self._set_state(EnemyState.CHASE)
            return

        self.velocity = pygame.math.Vector2(0, 0)
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 1.5
            # Fire projectile toward player
            return ("shoot", player_pos)


class Charger(Enemy):
    """Winds up, then dashes at high speed."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 60
        self.hp = 5
        self.detect_range = 200
        self.charge_speed = 500
        self.charging = False
        self.charge_direction = pygame.math.Vector2(0, 0)
        self.windup_time = 0.8

    def _chase(self, dt, player_pos, distance):
        if distance > self.lose_range:
            self._set_state(EnemyState.IDLE)
            return

        if distance < 150 and self.attack_cooldown <= 0:
            # Start windup
            self.charging = False
            self.charge_direction = (player_pos - self.pos).normalize()
            self._set_state(EnemyState.ATTACK)
            return

        direction = player_pos - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed

    def _attack(self, dt, player_pos, distance):
        if not self.charging:
            # Windup phase — stand still, telegraph the attack
            self.velocity = pygame.math.Vector2(0, 0)
            if self.state_timer > self.windup_time:
                self.charging = True
                self.velocity = self.charge_direction * self.charge_speed
        else:
            # Charging — move fast in locked direction
            if self.state_timer > self.windup_time + 0.5:
                # Charge over
                self.charging = False
                self.attack_cooldown = 2.0
                self._set_state(EnemyState.IDLE)
```

## Simple Pathfinding

Chasing in a straight line fails when walls are in the way. A simple approach: steer around obstacles.

```python
def steer_toward(self, target_pos, tilemap, dt):
    """Move toward target, steering around walls."""
    direction = target_pos - self.pos
    if direction.length() == 0:
        return pygame.math.Vector2(0, 0)

    direction = direction.normalize()

    # Check if direct path is blocked
    check_distance = self.size + 8
    check_pos = self.pos + direction * check_distance
    col, row = tilemap.world_to_grid(check_pos.x, check_pos.y)

    if tilemap.is_wall(col, row):
        # Try perpendicular directions
        perp1 = pygame.math.Vector2(-direction.y, direction.x)
        perp2 = pygame.math.Vector2(direction.y, -direction.x)

        check1 = self.pos + perp1 * check_distance
        check2 = self.pos + perp2 * check_distance

        c1, r1 = tilemap.world_to_grid(check1.x, check1.y)
        c2, r2 = tilemap.world_to_grid(check2.x, check2.y)

        if not tilemap.is_wall(c1, r1):
            direction = perp1
        elif not tilemap.is_wall(c2, r2):
            direction = perp2
        else:
            direction = pygame.math.Vector2(0, 0)  # Stuck

    return direction * self.speed
```

For more complex maps, you'd use A* pathfinding. But for Void Runners' small rooms, wall steering is sufficient and much cheaper.

## Spawning and Waves

Enemies should appear in waves, not all at once:

```python
class WaveSpawner:
    def __init__(self):
        self.wave = 0
        self.enemies_remaining = 0
        self.spawn_timer = 0.0
        self.spawn_interval = 0.5  # seconds between spawns
        self.wave_queue = []

    def start_wave(self, wave_number):
        self.wave = wave_number
        # More enemies each wave
        grunt_count = 3 + wave_number * 2
        shooter_count = max(0, wave_number - 2)
        charger_count = max(0, (wave_number - 4) // 2)

        self.wave_queue = (
            [Grunt] * grunt_count +
            [Shooter] * shooter_count +
            [Charger] * charger_count
        )
        random.shuffle(self.wave_queue)
        self.enemies_remaining = len(self.wave_queue)

    def update(self, dt, enemy_group, spawn_points):
        if not self.wave_queue:
            return

        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            enemy_class = self.wave_queue.pop(0)
            spawn = random.choice(spawn_points)
            enemy_group.add(enemy_class(spawn.x, spawn.y))

    def is_wave_complete(self, enemy_group):
        return len(self.wave_queue) == 0 and len(enemy_group) == 0
```

## What You Learned

- **Finite state machines** — states + transitions = behavior
- **Enemy types** — same FSM pattern, different parameters
- **Detection ranges** — detect, attack, lose thresholds
- **Wall steering** — simple obstacle avoidance without pathfinding
- **Charger pattern** — windup telegraph + fast dash
- **Shooter pattern** — maintain distance, fire projectiles
- **Wave spawning** — escalating difficulty over time

Enemies chase, attack, retreat, and patrol. Different types create different challenges. Waves escalate. The game has tension.

But when a bullet hits an enemy, it just disappears. No impact. No explosion. No screen shake. The hits don't feel powerful. Time to add juice.

---

[← Chapter 7: Tile Maps](chapter-07-tilemaps.md) | [Chapter 9: Particles & Effects →](chapter-09-particles.md)
