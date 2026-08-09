# Chapter 54: Professional Game Development — Java Server + TypeScript Client

## What you'll learn

- Game architecture: Entity-Component-System (ECS), game loop, state management
- Java game server: real-time multiplayer with WebSocket, tick-based simulation
- TypeScript game client: Canvas/WebGL rendering, input handling, prediction
- Networking: client-side prediction, server reconciliation, lag compensation
- Build: a multiplayer arena game (real-time PvP with authoritative server)
- Performance: fixed timestep, interpolation, spatial hashing, object pooling
- Deployment: scaling game servers with matchmaking

---

## PART 1: Architecture

## 54.1 Why Java server + TypeScript client?

```
┌────────────────────────┐         ┌────────────────────────┐
│   JAVA SERVER          │         │   TYPESCRIPT CLIENT    │
│                        │  WebSocket  │                        │
│  • Authoritative game  │◄──────────►│  • Rendering (Canvas)  │
│    state (truth)       │         │  • Input handling      │
│  • Physics simulation  │         │  • Client prediction   │
│  • Anti-cheat (server  │         │  • Interpolation       │
│    validates all moves)│         │  • UI / HUD            │
│  • Matchmaking         │         │  • Sound effects       │
│  • Persistence (stats) │         │                        │
│                        │         │  Runs in browser       │
│  Runs on server (JVM)  │         │  (or Electron/Tauri)   │
└────────────────────────┘         └────────────────────────┘

WHY THIS SPLIT:
• Java: high-performance, concurrent, battle-tested for servers (Minecraft, RuneScape)
• TypeScript: runs in every browser, excellent tooling, type safety
• WebSocket: real-time bidirectional communication (low latency)
• Authoritative server: prevents cheating (client never decides game state)
```

## 54.2 Entity-Component-System (ECS)

The industry-standard architecture for games (used by Unity, Unreal under the hood):

```
ENTITIES: just an ID (number). No data, no behaviour.
  entity_1 = 1001
  entity_2 = 1002
  entity_3 = 1003

COMPONENTS: pure data attached to entities (no logic).
  Position { x: 100, y: 200 }
  Velocity { vx: 5, vy: -3 }
  Health { current: 80, max: 100 }
  Sprite { texture: "player.png", width: 32, height: 32 }
  Collider { radius: 16, type: "circle" }
  PlayerInput { up: false, down: false, left: true, right: false }

SYSTEMS: logic that operates on entities with specific components.
  MovementSystem: queries all entities with (Position + Velocity)
                  → updates position based on velocity
  RenderSystem:   queries all entities with (Position + Sprite)
                  → draws them on screen
  CombatSystem:   queries all entities with (Health + Collider)
                  → applies damage on collision
  InputSystem:    queries all entities with (PlayerInput + Velocity)
                  → converts input into velocity

WHY ECS:
• Cache-friendly (components stored contiguously in memory)
• Composable (add Collider to anything → it collides)
• Testable (systems are pure functions of component data)
• Scalable (10,000 entities with same code as 10)
```

## 54.3 The game loop (fixed timestep)

```java
// Server game loop (Java)
public class GameLoop implements Runnable {
    private static final double TICK_RATE = 60.0; // 60 ticks per second
    private static final double TICK_DURATION = 1.0 / TICK_RATE; // ~16.67ms
    private static final long TICK_DURATION_NS = (long)(TICK_DURATION * 1_000_000_000);

    private volatile boolean running = true;
    private final GameWorld world;

    @Override
    public void run() {
        long previousTime = System.nanoTime();
        long accumulator = 0;
        long tick = 0;

        while (running) {
            long currentTime = System.nanoTime();
            long frameTime = currentTime - previousTime;
            previousTime = currentTime;
            accumulator += frameTime;

            // Process at fixed rate (deterministic)
            while (accumulator >= TICK_DURATION_NS) {
                world.processInput();      // read player inputs
                world.update(TICK_DURATION); // physics, AI, game logic
                world.broadcastState();    // send state to clients
                accumulator -= TICK_DURATION_NS;
                tick++;
            }

            // Sleep to avoid busy-waiting
            long sleepTime = TICK_DURATION_NS - (System.nanoTime() - currentTime);
            if (sleepTime > 0) {
                try { Thread.sleep(sleepTime / 1_000_000, (int)(sleepTime % 1_000_000)); }
                catch (InterruptedException e) { Thread.currentThread().interrupt(); }
            }
        }
    }
}
```

```typescript
// Client game loop (TypeScript)
class GameLoop {
  private lastTime = 0;
  private readonly FIXED_DT = 1 / 60;
  private accumulator = 0;

  start() {
    requestAnimationFrame(this.frame.bind(this));
  }

  private frame(timestamp: number) {
    const dt = Math.min((timestamp - this.lastTime) / 1000, 0.1);
    this.lastTime = timestamp;
    this.accumulator += dt;

    // Fixed update (physics, prediction)
    while (this.accumulator >= this.FIXED_DT) {
      this.fixedUpdate(this.FIXED_DT);
      this.accumulator -= this.FIXED_DT;
    }

    // Render (variable rate — interpolate between states)
    const alpha = this.accumulator / this.FIXED_DT;
    this.render(alpha);

    requestAnimationFrame(this.frame.bind(this));
  }

  private fixedUpdate(dt: number) { /* physics, input processing */ }
  private render(alpha: number) { /* draw with interpolation */ }
}
```

---

## PART 2: Java Game Server

## 54.4 Project setup (Spring Boot + WebSocket)

```kotlin
// build.gradle.kts
plugins {
    java
    id("org.springframework.boot") version "3.3.0"
    id("io.spring.dependency-management") version "1.1.5"
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-websocket")
    implementation("com.fasterxml.jackson.core:jackson-databind")
    implementation("org.springframework.boot:spring-boot-starter-web")
}
```

## 54.5 ECS implementation (Java)

```java
// Entity — just an ID
public class Entity {
    private static int nextId = 0;
    public final int id = nextId++;
    private final Map<Class<?>, Object> components = new HashMap<>();

    public <T> void add(T component) {
        components.put(component.getClass(), component);
    }

    @SuppressWarnings("unchecked")
    public <T> T get(Class<T> type) {
        return (T) components.get(type);
    }

    public <T> boolean has(Class<T> type) {
        return components.containsKey(type);
    }

    public <T> void remove(Class<T> type) {
        components.remove(type);
    }
}

// Components (pure data)
public record Position(double x, double y) {}
public record Velocity(double vx, double vy) {}
public record Health(int current, int max) {}
public record Collider(double radius, ColliderType type) {}
public record PlayerInput(boolean up, boolean down, boolean left, boolean right, boolean fire) {}
public record Projectile(int ownerId, double speed, double angle, long spawnTick) {}
public record PlayerInfo(String name, int score, String sessionId) {}

// Mutable versions (for systems that modify state)
public class MutablePosition {
    public double x, y;
    public MutablePosition(double x, double y) { this.x = x; this.y = y; }
}

public class MutableVelocity {
    public double vx, vy;
    public MutableVelocity(double vx, double vy) { this.vx = vx; this.vy = vy; }
}

public class MutableHealth {
    public int current;
    public final int max;
    public MutableHealth(int max) { this.current = max; this.max = max; }
    public boolean isDead() { return current <= 0; }
    public void damage(int amount) { current = Math.max(0, current - amount); }
}
```

## 54.6 Game world and systems

```java
public class GameWorld {
    private final List<Entity> entities = new CopyOnWriteArrayList<>();
    private final Map<String, Entity> playerEntities = new ConcurrentHashMap<>(); // sessionId → entity
    private long currentTick = 0;

    // Constants
    private static final double PLAYER_SPEED = 300.0; // pixels/sec
    private static final double PROJECTILE_SPEED = 600.0;
    private static final double ARENA_WIDTH = 1200;
    private static final double ARENA_HEIGHT = 800;
    private static final int PROJECTILE_DAMAGE = 20;

    public void update(double dt) {
        currentTick++;
        inputSystem(dt);
        movementSystem(dt);
        projectileSystem(dt);
        collisionSystem();
        cleanupSystem();
    }

    // --- SYSTEMS ---

    private void inputSystem(double dt) {
        for (Entity e : entities) {
            if (!e.has(PlayerInput.class) || !e.has(MutableVelocity.class)) continue;
            PlayerInput input = e.get(PlayerInput.class);
            MutableVelocity vel = e.get(MutableVelocity.class);

            vel.vx = 0; vel.vy = 0;
            if (input.up()) vel.vy = -PLAYER_SPEED;
            if (input.down()) vel.vy = PLAYER_SPEED;
            if (input.left()) vel.vx = -PLAYER_SPEED;
            if (input.right()) vel.vx = PLAYER_SPEED;

            // Normalise diagonal movement
            double len = Math.sqrt(vel.vx * vel.vx + vel.vy * vel.vy);
            if (len > PLAYER_SPEED) {
                vel.vx = vel.vx / len * PLAYER_SPEED;
                vel.vy = vel.vy / len * PLAYER_SPEED;
            }
        }
    }

    private void movementSystem(double dt) {
        for (Entity e : entities) {
            if (!e.has(MutablePosition.class) || !e.has(MutableVelocity.class)) continue;
            MutablePosition pos = e.get(MutablePosition.class);
            MutableVelocity vel = e.get(MutableVelocity.class);

            pos.x += vel.vx * dt;
            pos.y += vel.vy * dt;

            // Clamp to arena bounds
            pos.x = Math.max(0, Math.min(ARENA_WIDTH, pos.x));
            pos.y = Math.max(0, Math.min(ARENA_HEIGHT, pos.y));
        }
    }

    private void collisionSystem() {
        List<Entity> collidables = entities.stream()
            .filter(e -> e.has(MutablePosition.class) && e.has(Collider.class))
            .toList();

        for (int i = 0; i < collidables.size(); i++) {
            for (int j = i + 1; j < collidables.size(); j++) {
                Entity a = collidables.get(i);
                Entity b = collidables.get(j);
                if (checkCollision(a, b)) {
                    resolveCollision(a, b);
                }
            }
        }
    }

    private boolean checkCollision(Entity a, Entity b) {
        MutablePosition pa = a.get(MutablePosition.class);
        MutablePosition pb = b.get(MutablePosition.class);
        Collider ca = a.get(Collider.class);
        Collider cb = b.get(Collider.class);

        double dx = pa.x - pb.x;
        double dy = pa.y - pb.y;
        double dist = Math.sqrt(dx * dx + dy * dy);
        return dist < ca.radius() + cb.radius();
    }

    private void resolveCollision(Entity a, Entity b) {
        // Projectile hits player
        if (a.has(Projectile.class) && b.has(MutableHealth.class)) {
            Projectile proj = a.get(Projectile.class);
            if (proj.ownerId() != b.id) { // can't hit yourself
                b.get(MutableHealth.class).damage(PROJECTILE_DAMAGE);
                entities.remove(a); // destroy projectile
            }
        }
        // Reverse check
        if (b.has(Projectile.class) && a.has(MutableHealth.class)) {
            Projectile proj = b.get(Projectile.class);
            if (proj.ownerId() != a.id) {
                a.get(MutableHealth.class).damage(PROJECTILE_DAMAGE);
                entities.remove(b);
            }
        }
    }

    // --- PLAYER MANAGEMENT ---

    public Entity spawnPlayer(String sessionId, String name) {
        Entity player = new Entity();
        player.add(new MutablePosition(ARENA_WIDTH / 2, ARENA_HEIGHT / 2));
        player.add(new MutableVelocity(0, 0));
        player.add(new MutableHealth(100));
        player.add(new Collider(16, ColliderType.CIRCLE));
        player.add(new PlayerInput(false, false, false, false, false));
        player.add(new PlayerInfo(name, 0, sessionId));
        entities.add(player);
        playerEntities.put(sessionId, player);
        return player;
    }

    public void handleInput(String sessionId, PlayerInput input) {
        Entity player = playerEntities.get(sessionId);
        if (player != null) {
            player.add(input); // replace input component
        }
    }

    public GameState getState() {
        // Serialize current world state for clients
        return new GameState(currentTick, entities.stream()
            .map(this::entityToSnapshot)
            .toList());
    }
}
```

## 54.7 WebSocket handler

```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(gameWebSocketHandler(), "/game")
                .setAllowedOrigins("*");
    }

    @Bean
    public GameWebSocketHandler gameWebSocketHandler() {
        return new GameWebSocketHandler();
    }
}

@Component
public class GameWebSocketHandler extends TextWebSocketHandler {
    private final GameWorld world;
    private final ObjectMapper mapper = new ObjectMapper();
    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.put(session.getId(), session);
        world.spawnPlayer(session.getId(), "Player-" + session.getId().substring(0, 4));
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) {
        try {
            ClientMessage msg = mapper.readValue(message.getPayload(), ClientMessage.class);
            switch (msg.type()) {
                case "input" -> world.handleInput(session.getId(), msg.input());
                case "fire" -> world.handleFire(session.getId(), msg.angle());
            }
        } catch (Exception e) {
            // log error
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        sessions.remove(session.getId());
        world.removePlayer(session.getId());
    }

    // Called by game loop every tick
    public void broadcastState(GameState state) {
        String json = mapper.writeValueAsString(state);
        TextMessage message = new TextMessage(json);
        sessions.values().parallelStream().forEach(session -> {
            try { session.sendMessage(message); }
            catch (Exception e) { /* handle disconnect */ }
        });
    }
}
```



---

## PART 3: TypeScript Game Client

## 54.8 Client architecture

```typescript
// src/game/Game.ts
import { Renderer } from "./Renderer";
import { InputHandler } from "./InputHandler";
import { NetworkClient } from "./NetworkClient";
import { GameState, EntitySnapshot } from "./types";

export class Game {
  private renderer: Renderer;
  private input: InputHandler;
  private network: NetworkClient;
  private state: GameState | null = null;
  private previousState: GameState | null = null;
  private lastTime = 0;

  constructor(canvas: HTMLCanvasElement) {
    this.renderer = new Renderer(canvas);
    this.input = new InputHandler();
    this.network = new NetworkClient("ws://localhost:8080/game");

    this.network.onState((state) => {
      this.previousState = this.state;
      this.state = state;
    });
  }

  start() {
    this.input.bind();
    this.network.connect();
    requestAnimationFrame(this.loop.bind(this));
  }

  private loop(timestamp: number) {
    const dt = (timestamp - this.lastTime) / 1000;
    this.lastTime = timestamp;

    // Send input to server every frame
    this.network.sendInput(this.input.getState());

    // Render with interpolation
    if (this.state && this.previousState) {
      const alpha = Math.min(this.network.getInterpolationAlpha(), 1);
      this.renderer.render(this.previousState, this.state, alpha);
    }

    requestAnimationFrame(this.loop.bind(this));
  }

  destroy() {
    this.input.unbind();
    this.network.disconnect();
  }
}
```

## 54.9 Renderer (Canvas 2D)

```typescript
// src/game/Renderer.ts
import { GameState, EntitySnapshot } from "./types";

export class Renderer {
  private ctx: CanvasRenderingContext2D;
  private width: number;
  private height: number;

  constructor(canvas: HTMLCanvasElement) {
    this.ctx = canvas.getContext("2d")!;
    this.width = canvas.width;
    this.height = canvas.height;
  }

  render(prevState: GameState, currentState: GameState, alpha: number) {
    const ctx = this.ctx;

    // Clear
    ctx.fillStyle = "#0f172a";
    ctx.fillRect(0, 0, this.width, this.height);

    // Draw grid (background)
    this.drawGrid();

    // Draw entities with interpolation
    for (const entity of currentState.entities) {
      const prev = prevState.entities.find(e => e.id === entity.id);
      if (prev) {
        // Interpolate between previous and current position
        const x = this.lerp(prev.x, entity.x, alpha);
        const y = this.lerp(prev.y, entity.y, alpha);
        this.drawEntity(entity, x, y);
      } else {
        // New entity — draw at current position
        this.drawEntity(entity, entity.x, entity.y);
      }
    }

    // Draw HUD
    this.drawHUD(currentState);
  }

  private drawEntity(entity: EntitySnapshot, x: number, y: number) {
    const ctx = this.ctx;

    switch (entity.type) {
      case "player":
        // Body
        ctx.beginPath();
        ctx.arc(x, y, entity.radius, 0, Math.PI * 2);
        ctx.fillStyle = entity.isLocalPlayer ? "#3b82f6" : "#ef4444";
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Health bar
        const barWidth = 40;
        const healthPercent = entity.health / entity.maxHealth;
        ctx.fillStyle = "#1e293b";
        ctx.fillRect(x - barWidth / 2, y - entity.radius - 12, barWidth, 6);
        ctx.fillStyle = healthPercent > 0.5 ? "#22c55e" : healthPercent > 0.25 ? "#f59e0b" : "#ef4444";
        ctx.fillRect(x - barWidth / 2, y - entity.radius - 12, barWidth * healthPercent, 6);

        // Name
        ctx.fillStyle = "#ffffff";
        ctx.font = "11px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(entity.name, x, y - entity.radius - 16);
        break;

      case "projectile":
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = "#fbbf24";
        ctx.fill();
        // Trail effect
        ctx.beginPath();
        ctx.arc(x - entity.vx * 0.02, y - entity.vy * 0.02, 3, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(251, 191, 36, 0.4)";
        ctx.fill();
        break;
    }
  }

  private drawGrid() {
    const ctx = this.ctx;
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < this.width; x += 50) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, this.height); ctx.stroke();
    }
    for (let y = 0; y < this.height; y += 50) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(this.width, y); ctx.stroke();
    }
  }

  private drawHUD(state: GameState) {
    const ctx = this.ctx;
    // Score
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 16px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText(`Score: ${state.localPlayer?.score ?? 0}`, 10, 25);
    ctx.fillText(`Players: ${state.entities.filter(e => e.type === "player").length}`, 10, 50);
    ctx.fillText(`Tick: ${state.tick}`, 10, 75);
  }

  private lerp(a: number, b: number, t: number): number {
    return a + (b - a) * t;
  }
}
```

## 54.10 Input handler

```typescript
// src/game/InputHandler.ts
export interface InputState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  fire: boolean;
  mouseX: number;
  mouseY: number;
}

export class InputHandler {
  private keys = new Set<string>();
  private mouseDown = false;
  private mouseX = 0;
  private mouseY = 0;

  bind() {
    window.addEventListener("keydown", this.onKeyDown);
    window.addEventListener("keyup", this.onKeyUp);
    window.addEventListener("mousedown", this.onMouseDown);
    window.addEventListener("mouseup", this.onMouseUp);
    window.addEventListener("mousemove", this.onMouseMove);
  }

  unbind() {
    window.removeEventListener("keydown", this.onKeyDown);
    window.removeEventListener("keyup", this.onKeyUp);
    window.removeEventListener("mousedown", this.onMouseDown);
    window.removeEventListener("mouseup", this.onMouseUp);
    window.removeEventListener("mousemove", this.onMouseMove);
  }

  getState(): InputState {
    return {
      up: this.keys.has("KeyW") || this.keys.has("ArrowUp"),
      down: this.keys.has("KeyS") || this.keys.has("ArrowDown"),
      left: this.keys.has("KeyA") || this.keys.has("ArrowLeft"),
      right: this.keys.has("KeyD") || this.keys.has("ArrowRight"),
      fire: this.mouseDown,
      mouseX: this.mouseX,
      mouseY: this.mouseY,
    };
  }

  private onKeyDown = (e: KeyboardEvent) => { this.keys.add(e.code); };
  private onKeyUp = (e: KeyboardEvent) => { this.keys.delete(e.code); };
  private onMouseDown = () => { this.mouseDown = true; };
  private onMouseUp = () => { this.mouseDown = false; };
  private onMouseMove = (e: MouseEvent) => { this.mouseX = e.clientX; this.mouseY = e.clientY; };
}
```

## 54.11 Network client

```typescript
// src/game/NetworkClient.ts
import { GameState, InputState } from "./types";

export class NetworkClient {
  private ws: WebSocket | null = null;
  private stateCallback: ((state: GameState) => void) | null = null;
  private lastServerTick = 0;
  private lastReceiveTime = 0;
  private tickRate = 60; // server sends 60 updates/sec

  constructor(private url: string) {}

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onmessage = (event) => {
      const state: GameState = JSON.parse(event.data);
      this.lastServerTick = state.tick;
      this.lastReceiveTime = performance.now();
      this.stateCallback?.(state);
    };
    this.ws.onclose = () => { setTimeout(() => this.connect(), 2000); }; // auto-reconnect
  }

  disconnect() {
    this.ws?.close();
  }

  onState(callback: (state: GameState) => void) {
    this.stateCallback = callback;
  }

  sendInput(input: InputState) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "input", ...input }));
    }
  }

  sendFire(angle: number) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "fire", angle }));
    }
  }

  // How far between the two most recent server states we are
  // Used for interpolation (smooth rendering between tick updates)
  getInterpolationAlpha(): number {
    const timeSinceLastUpdate = performance.now() - this.lastReceiveTime;
    const tickDuration = 1000 / this.tickRate;
    return timeSinceLastUpdate / tickDuration;
  }
}
```

---

## PART 4: Multiplayer Networking Patterns

## 54.12 The networking problem

```
SERVER (truth)         NETWORK (50-150ms latency)         CLIENT (display)
  Tick 100 ────────────── 80ms delay ──────────────────── shows Tick 100
  Tick 101                                                 (80ms behind reality!)
  Tick 102
  Tick 103
  Tick 104 ────────────── arrives ───────────────────────── shows Tick 104
                                                            (jumped from 100→104!)

WITHOUT INTERPOLATION: jerky movement (jumps every 80ms)
WITH INTERPOLATION: smooth movement (blend between received states)
```

## 54.13 Client-side prediction

```typescript
// The client doesn't wait for the server to confirm movement.
// It PREDICTS where the player will be based on input.

class ClientPrediction {
  private pendingInputs: Array<{ tick: number; input: InputState }> = [];

  applyInput(input: InputState, localPlayer: EntitySnapshot, dt: number) {
    // Move the local player IMMEDIATELY (don't wait for server)
    if (input.up) localPlayer.y -= PLAYER_SPEED * dt;
    if (input.down) localPlayer.y += PLAYER_SPEED * dt;
    if (input.left) localPlayer.x -= PLAYER_SPEED * dt;
    if (input.right) localPlayer.x += PLAYER_SPEED * dt;

    // Save this input (for reconciliation)
    this.pendingInputs.push({ tick: currentTick, input });
  }

  reconcile(serverState: EntitySnapshot, lastProcessedTick: number) {
    // Server tells us: "at tick 50, you were at position X,Y"
    // Discard all inputs the server already processed
    this.pendingInputs = this.pendingInputs.filter(i => i.tick > lastProcessedTick);

    // Re-apply unprocessed inputs on top of server state
    let x = serverState.x;
    let y = serverState.y;
    for (const { input } of this.pendingInputs) {
      if (input.up) y -= PLAYER_SPEED * FIXED_DT;
      if (input.down) y += PLAYER_SPEED * FIXED_DT;
      if (input.left) x -= PLAYER_SPEED * FIXED_DT;
      if (input.right) x += PLAYER_SPEED * FIXED_DT;
    }

    // Update local player to reconciled position
    localPlayer.x = x;
    localPlayer.y = y;
  }
}
```

**Why prediction + reconciliation:**
- Without prediction: press W → wait 80ms → player moves (feels sluggish)
- With prediction: press W → player moves instantly → server confirms later
- If server disagrees (e.g., you were blocked by a wall): reconcile smoothly

## 54.14 Entity interpolation (other players)

```typescript
// For OTHER players (not the local one), interpolate between server states.
// You render them slightly in the past (one tick behind) for smooth display.

class EntityInterpolation {
  private stateBuffer: Array<{ tick: number; entities: EntitySnapshot[] }> = [];

  addState(state: GameState) {
    this.stateBuffer.push({ tick: state.tick, entities: state.entities });
    // Keep last 2 seconds of states
    if (this.stateBuffer.length > 120) this.stateBuffer.shift();
  }

  getInterpolated(renderTick: number): EntitySnapshot[] {
    // Find the two states that bracket renderTick
    let before = this.stateBuffer[0];
    let after = this.stateBuffer[1];

    for (let i = 0; i < this.stateBuffer.length - 1; i++) {
      if (this.stateBuffer[i].tick <= renderTick && this.stateBuffer[i + 1].tick >= renderTick) {
        before = this.stateBuffer[i];
        after = this.stateBuffer[i + 1];
        break;
      }
    }

    // Interpolate between before and after
    const t = (renderTick - before.tick) / (after.tick - before.tick);
    return before.entities.map((entity) => {
      const afterEntity = after.entities.find(e => e.id === entity.id);
      if (!afterEntity) return entity;
      return {
        ...entity,
        x: entity.x + (afterEntity.x - entity.x) * t,
        y: entity.y + (afterEntity.y - entity.y) * t,
      };
    });
  }
}
```

---

## PART 5: Performance & Scaling

## 54.15 Server performance

```java
// Spatial hashing: O(n²) collision → O(n) per entity
public class SpatialHash {
    private final int cellSize;
    private final Map<Long, List<Entity>> grid = new HashMap<>();

    public void clear() { grid.clear(); }

    public void insert(Entity e) {
        long key = hash(e.get(MutablePosition.class));
        grid.computeIfAbsent(key, k -> new ArrayList<>()).add(e);
    }

    public List<Entity> getNearby(Entity e) {
        MutablePosition pos = e.get(MutablePosition.class);
        List<Entity> nearby = new ArrayList<>();
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                long key = hash(pos.x + dx * cellSize, pos.y + dy * cellSize);
                List<Entity> cell = grid.get(key);
                if (cell != null) nearby.addAll(cell);
            }
        }
        return nearby;
    }

    private long hash(MutablePosition p) { return hash(p.x, p.y); }
    private long hash(double x, double y) {
        int cx = (int)(x / cellSize);
        int cy = (int)(y / cellSize);
        return ((long)cx << 32) | (cy & 0xFFFFFFFFL);
    }
}

// Object pooling: avoid GC pauses
public class ProjectilePool {
    private final Queue<Entity> pool = new ConcurrentLinkedQueue<>();

    public Entity acquire() {
        Entity e = pool.poll();
        if (e == null) e = new Entity(); // only allocate if pool empty
        return e;
    }

    public void release(Entity e) {
        // Reset components, return to pool
        pool.offer(e);
    }
}
```

## 54.16 Matchmaking and scaling

```
ARCHITECTURE FOR 10,000+ CONCURRENT PLAYERS:

┌────────────┐     ┌──────────────────────┐     ┌───────────────┐
│  Clients   │────►│   Load Balancer      │────►│  Matchmaker   │
│  (browser) │     │   (WebSocket-aware)  │     │  (pairs       │
└────────────┘     └──────────────────────┘     │   players)    │
                                                 └───────┬───────┘
                                                         │ assigns to
                         ┌───────────────────────────────┼───────────────┐
                         ▼                               ▼               ▼
                   ┌──────────┐                   ┌──────────┐    ┌──────────┐
                   │ Game Srv │                   │ Game Srv │    │ Game Srv │
                   │ (Room 1) │                   │ (Room 2) │    │ (Room 3) │
                   │ 8 players│                   │ 8 players│    │ 8 players│
                   └──────────┘                   └──────────┘    └──────────┘

EACH GAME SERVER: handles 1 "room" of 2-16 players
MATCHMAKER: groups players by skill/region, assigns to a game server
SCALING: spin up more game server instances as needed (Kubernetes)
STATE: each room is independent (no shared state between servers)
```

---

## Summary

✅ Architecture: ECS (Entity-Component-System) — data-oriented, scalable, composable
✅ Java server: authoritative game loop (60 ticks/sec), WebSocket, anti-cheat by design
✅ TypeScript client: Canvas 2D rendering, input handling, interpolation
✅ Networking: client-side prediction (instant feedback), server reconciliation, entity interpolation (smooth others)
✅ Performance: spatial hashing (O(n) collisions), object pooling (no GC), fixed timestep
✅ Scaling: matchmaker → game server per room → Kubernetes auto-scale

## Key takeaways

**Authoritative server is non-negotiable for multiplayer.** The server is the truth. Clients can predict locally (for responsiveness), but the server validates everything. This prevents cheating by design — the client can lie about its input, but the server only applies what's physically possible.

**ECS scales where OOP doesn't.** A Player class with inheritance (Player → Character → Entity) becomes a tangled mess at 50+ entity types. ECS lets you compose behaviours: slap a `Collider` + `Health` on anything → it can be damaged. No inheritance hierarchy needed.

**Client prediction + interpolation = smooth gameplay at any latency.** Your own character responds instantly (prediction). Other players move smoothly (interpolation). The server is the referee — corrections happen invisibly in the background (reconciliation).

---

→ [Back to Chapter 53: Piano for Kids](./53-PIANO-FOR-KIDS.md)
