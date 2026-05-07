# Chapter 18: Animation State Machine — Knowing What to Play When

[← Chapter 17: Renderer](chapter-17-renderer.md) | [Chapter 19: Runtime Effects →](chapter-19-runtime-effects.md)

---

## The Problem

You wire animations to input. Press right → walk. Press jump → jump. Press attack → attack. It works... until you press attack while jumping. The attack plays mid-air, then jump resumes, then landing, then idle — but for one frame walk flashes because you're still holding right. Chaos.

Riku draws a diagram:

> "You need a **state machine**. Every input directly triggers an animation — that creates conflicts. A state machine defines which states exist, which transitions are allowed, and which states have priority."

---

## The Principle: States, Transitions, Priority

```
STATES:      idle, walk, run, jump, fall, attack, hit, death
TRANSITIONS: idle→walk (move), walk→jump (jump pressed), NOT death→idle
PRIORITY:    death > hit > attack > jump/fall > run > walk > idle
             (higher priority interrupts lower)
```

---

## Step-by-Step: The State Machine

### Step 1: Define States

```typescript
enum AnimState { Idle='idle', Walk='walk', Run='run', Jump='jump',
                 Fall='fall', Attack='attack', Hit='hit', Death='death' }

interface StateConfig {
  animation: string;
  loop: boolean;
  priority: number;
  canTransitionTo: AnimState[];
}

const STATE_CONFIG: Record<AnimState, StateConfig> = {
  [AnimState.Idle]:   { animation:'idle',   loop:true,  priority:0,
    canTransitionTo:[AnimState.Walk,AnimState.Run,AnimState.Jump,AnimState.Attack,AnimState.Hit,AnimState.Death] },
  [AnimState.Walk]:   { animation:'walk',   loop:true,  priority:1,
    canTransitionTo:[AnimState.Idle,AnimState.Run,AnimState.Jump,AnimState.Attack,AnimState.Hit,AnimState.Death] },
  [AnimState.Run]:    { animation:'run',    loop:true,  priority:2,
    canTransitionTo:[AnimState.Idle,AnimState.Walk,AnimState.Jump,AnimState.Attack,AnimState.Hit,AnimState.Death] },
  [AnimState.Jump]:   { animation:'jump',   loop:false, priority:3,
    canTransitionTo:[AnimState.Fall,AnimState.Attack,AnimState.Hit,AnimState.Death] },
  [AnimState.Fall]:   { animation:'fall',   loop:false, priority:3,
    canTransitionTo:[AnimState.Idle,AnimState.Walk,AnimState.Run,AnimState.Hit,AnimState.Death] },
  [AnimState.Attack]: { animation:'attack', loop:false, priority:4,
    canTransitionTo:[AnimState.Idle,AnimState.Walk,AnimState.Run,AnimState.Hit,AnimState.Death] },
  [AnimState.Hit]:    { animation:'hit',    loop:false, priority:5,
    canTransitionTo:[AnimState.Idle,AnimState.Walk,AnimState.Run,AnimState.Death] },
  [AnimState.Death]:  { animation:'death',  loop:false, priority:6,
    canTransitionTo:[] },
};
```

### Step 2: The State Machine Class

```typescript
class AnimationStateMachine {
  private currentState: AnimState = AnimState.Idle;
  private animator: SpriteAnimator;
  private queuedState: AnimState | null = null;

  constructor(animator: SpriteAnimator) {
    this.animator = animator;
    this.enterState(AnimState.Idle);
  }

  get state(): AnimState { return this.currentState; }

  transition(newState: AnimState): boolean {
    if (newState === this.currentState) return false;
    const current = STATE_CONFIG[this.currentState];
    const next = STATE_CONFIG[newState];

    if (!current.canTransitionTo.includes(newState)) return false;

    // Non-looping animations only interrupted by higher priority
    if (!current.loop && !this.animator.isFinished()) {
      if (next.priority <= current.priority) {
        this.queuedState = newState;
        return false;
      }
    }
    this.enterState(newState);
    return true;
  }

  private enterState(state: AnimState): void {
    this.currentState = state;
    this.queuedState = null;
    const config = STATE_CONFIG[state];
    this.animator.play(config.animation, config.loop);
  }

  update(deltaTime: number): void {
    this.animator.update(deltaTime);
    if (!STATE_CONFIG[this.currentState].loop && this.animator.isFinished()) {
      this.enterState(this.queuedState ?? AnimState.Idle);
    }
  }
}
```

### Step 3: Connect to Game Logic

```typescript
class Player {
  private sm: AnimationStateMachine;
  private vx = 0; private vy = 0;
  private grounded = true; private running = false;

  updateAnimationState(input: InputState): void {
    if (input.attack) { this.sm.transition(AnimState.Attack); return; }
    if (!this.grounded && this.vy < 0) { this.sm.transition(AnimState.Jump); return; }
    if (!this.grounded && this.vy >= 0) { this.sm.transition(AnimState.Fall); return; }
    if (Math.abs(this.vx) > 0) {
      this.sm.transition(this.running ? AnimState.Run : AnimState.Walk); return;
    }
    this.sm.transition(AnimState.Idle);
  }

  takeDamage(): void { this.sm.transition(AnimState.Hit); }
  die(): void { this.sm.transition(AnimState.Death); }
}
```

Check conditions in priority order (highest first). The state machine rejects invalid transitions automatically.

---

## The Transition Diagram

```
                ┌──────────┐
       ┌────────│  DEATH   │  (final — no exit)
       │        └──────────┘
       │             ↑
       │        ┌──────────┐
       ├────────│   HIT    │──→ IDLE (on finish)
       │        └──────────┘
       │             ↑
       │        ┌──────────┐
       ├────────│  ATTACK  │──→ IDLE (on finish)
       │        └──────────┘
       │             ↑
  ┌────┴────┐  ┌──────────┐
  │  JUMP   │─→│   FALL   │──→ IDLE (on land)
  └─────────┘  └──────────┘
       ↑             ↑
  ┌─────────┐  ┌──────────┐
  │   RUN   │←→│   WALK   │
  └─────────┘  └──────────┘
       ↑             ↑
       └──────┬──────┘
        ┌──────────┐
        │   IDLE   │  (default)
        └──────────┘
```

---

## The Mistake You'll Make

You attack while running. Attack finishes. Ember snaps to idle — even though you're still holding the run button.

Riku traces your logic:

> "When a non-looping animation finishes, you default to idle. But you should re-evaluate the CURRENT input. After attack finishes, ask: 'is the player still holding right?' Then go to run, not idle."

### The Fix: Re-evaluate Every Frame

```typescript
// Call updateAnimationState every frame.
// The state machine rejects invalid transitions via priority,
// so calling it constantly is safe.
update(deltaTime: number, input: InputState): void {
  this.processMovement(input);
  this.updateAnimationState(input);
  this.sm.update(deltaTime);
}
```

When attack is playing (priority 4), `transition(Run)` (priority 2) is rejected. When attack finishes and resets to idle, the next frame's `transition(Run)` succeeds.

---

## Quick Reference

| Concept | Implementation |
|---|---|
| States | Enum of all possible animations |
| Transitions | Whitelist of allowed state changes |
| Priority | Higher number = harder to interrupt |
| Looping | idle, walk, run (play forever) |
| One-shot | jump, attack, hit, death (play once) |
| On finish | Return to idle or re-evaluate input |
| External events | Hit/Death bypass normal priority |

| Priority | States |
|---|---|
| 0 | Idle |
| 1 | Walk |
| 2 | Run |
| 3 | Jump, Fall |
| 4 | Attack |
| 5 | Hit |
| 6 | Death |

---

## Exercise: Implement the State Machine

1. Add `AnimationStateMachine` to your renderer from Chapter 17
2. Define all states with priority, transitions, and loop settings
3. Connect to keyboard: arrows=walk/run, space=jump, Z=attack, X=hit
4. Test: walk→jump→fall→land, attack while walking, hit while attacking, mash all buttons

**Success criteria**: No matter what the player presses, Ember is always in a valid animation state.

---

[← Chapter 17: Renderer](chapter-17-renderer.md) | [Chapter 19: Runtime Effects →](chapter-19-runtime-effects.md)
