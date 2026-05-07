# Chapter 1: The Reward Signal

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Exploration →](chapter-02-exploration.md)

---

## The Problem

You build your first agent. It exists in a 4×4 grid. It can move up, down, left, right. There's a goal square worth +1 and trap squares worth -1.

You write the simplest possible agent:

```python
import random

def random_agent(env):
    """Pick a random action every step."""
    return random.choice(env.available_actions())
```

You run it for 1,000 episodes. Average reward: -0.3. The agent stumbles into traps more often than it finds the goal. It has no memory, no strategy, no learning.

QA Tanya watches the replay: "It's just... wandering. For 400 turns. Then it falls in a hole."

Jonas: "Okay, so it needs to learn. What does it learn *from*?"

The answer: **rewards**. The reward signal is the only feedback an RL agent gets. It's the entire teaching mechanism. Get the reward wrong, and the agent learns the wrong thing — or nothing at all.

## The Environment

First, let's build the grid world:

```python
import numpy as np

class GridWorld:
    def __init__(self, size=4):
        self.size = size
        self.grid = np.zeros((size, size))
        
        # Place goal and traps
        self.goal = (0, 3)
        self.traps = [(1, 1), (2, 3)]
        
        self.grid[self.goal] = 1      # +1 reward
        for trap in self.traps:
            self.grid[trap] = -1      # -1 reward
        
        self.start = (3, 0)
        self.agent_pos = self.start
    
    def reset(self):
        """Reset agent to start position. Return initial state."""
        self.agent_pos = self.start
        return self.agent_pos
    
    def step(self, action):
        """
        Take an action. Returns (new_state, reward, done).
        Actions: 0=up, 1=down, 2=left, 3=right
        """
        row, col = self.agent_pos
        
        if action == 0:    # up
            row = max(0, row - 1)
        elif action == 1:  # down
            row = min(self.size - 1, row + 1)
        elif action == 2:  # left
            col = max(0, col - 1)
        elif action == 3:  # right
            col = min(self.size - 1, col + 1)
        
        self.agent_pos = (row, col)
        reward = self.grid[self.agent_pos]
        done = self.agent_pos == self.goal or self.agent_pos in self.traps
        
        return self.agent_pos, reward, done
    
    def available_actions(self):
        return [0, 1, 2, 3]
    
    def render(self):
        """Print the grid with agent position."""
        symbols = {0: '.', 1: 'G', -1: 'X'}
        for r in range(self.size):
            row_str = ""
            for c in range(self.size):
                if (r, c) == self.agent_pos:
                    row_str += " A "
                else:
                    row_str += f" {symbols[self.grid[r, c]]} "
            print(row_str)
        print()
```

## The Random Agent (Baseline)

```python
def run_random_agent(episodes=1000, max_steps=100):
    env = GridWorld()
    total_rewards = []
    
    for ep in range(episodes):
        state = env.reset()
        episode_reward = 0
        
        for step in range(max_steps):
            action = random.choice(env.available_actions())
            state, reward, done = env.step(action)
            episode_reward += reward
            
            if done:
                break
        
        total_rewards.append(episode_reward)
    
    avg = np.mean(total_rewards)
    print(f"Random agent — {episodes} episodes")
    print(f"  Average reward: {avg:.3f}")
    print(f"  Reached goal:   {total_rewards.count(1.0) / episodes * 100:.1f}%")
    print(f"  Hit trap:       {total_rewards.count(-1.0) / episodes * 100:.1f}%")
    print(f"  Timed out:      {total_rewards.count(0.0) / episodes * 100:.1f}%")
    
    return total_rewards

run_random_agent()
```

Output:
```
Random agent — 1000 episodes
  Average reward: -0.287
  Reached goal:   18.2%
  Hit trap:       47.1%
  Timed out:      34.7%
```

The agent reaches the goal 18% of the time by pure luck. It hits traps almost half the time. A third of the time it wanders until the step limit.

This is the baseline. Everything we build must beat this.

## What Is a Reward?

A reward is a single number the environment gives the agent after each action. That's it. One number.

```python
state, reward, done = env.step(action)
#              ^^^^^^
#              This is the entire teaching signal
```

The agent's goal: **maximize the total reward it accumulates over time.**

Not the immediate reward. The *total*. This distinction matters enormously.

## The Return: Total Reward Over an Episode

The **return** (G) is the sum of all rewards in an episode:

```
G = r₁ + r₂ + r₃ + ... + rₜ
```

For our grid world, most steps give 0 reward. The episode ends with either +1 (goal) or -1 (trap). So the return is just the final reward... for now.

But what if we add a small penalty for each step?

```python
def step_with_time_penalty(self, action):
    """Each step costs -0.04. Encourages finding the goal quickly."""
    state, reward, done = self.step(action)
    if not done:
        reward = -0.04  # Time penalty
    return state, reward, done
```

Now the return is:

```
G = -0.04 + -0.04 + -0.04 + ... + final_reward
```

An agent that reaches the goal in 6 steps: G = 5 × (-0.04) + 1.0 = 0.80
An agent that reaches the goal in 20 steps: G = 19 × (-0.04) + 1.0 = 0.24
An agent that wanders for 100 steps and times out: G = 100 × (-0.04) = -4.0

The time penalty teaches urgency. Without it, the agent has no reason to prefer a short path over a long one.

## Discounting: Future Rewards Are Worth Less

Here's a subtlety. Should the agent value a reward now the same as a reward 50 steps from now?

Imagine two paths:
- Path A: Get +1 reward in 3 steps
- Path B: Get +1 reward in 30 steps

Both have the same final reward. But Path A is better — it's faster, more certain, and leaves time for more rewards.

**Discounting** formalizes this intuition. We multiply future rewards by γ (gamma), a number between 0 and 1:

```
G = r₁ + γ·r₂ + γ²·r₃ + γ³·r₄ + ...
```

With γ = 0.9:
- Reward now: worth 1.0
- Reward in 1 step: worth 0.9
- Reward in 5 steps: worth 0.9⁵ = 0.59
- Reward in 10 steps: worth 0.9¹⁰ = 0.35
- Reward in 50 steps: worth 0.9⁵⁰ = 0.005 (almost nothing)

```python
def compute_return(rewards, gamma=0.9):
    """Compute discounted return from a list of rewards."""
    G = 0
    for reward in reversed(rewards):
        G = reward + gamma * G
    return G
```

### Why Discount?

Three reasons:

1. **Uncertainty** — the further into the future, the less certain the reward actually arrives
2. **Preference for sooner** — all else equal, sooner is better
3. **Mathematical convergence** — without discounting, infinite episodes have infinite returns (can't compare them)

### Gamma Controls the Horizon

| γ | Behavior |
|---|---|
| 0.0 | Completely myopic — only cares about immediate reward |
| 0.5 | Short-sighted — rewards beyond ~5 steps are negligible |
| 0.9 | Balanced — plans ~10-20 steps ahead |
| 0.99 | Far-sighted — considers rewards 100+ steps out |
| 1.0 | No discounting — all future rewards equally important |

```python
def show_discount_horizon(gamma):
    """Show how many steps ahead the agent effectively 'sees'."""
    threshold = 0.01  # Reward worth less than 1% is negligible
    steps = 0
    value = 1.0
    while value > threshold:
        value *= gamma
        steps += 1
    print(f"γ={gamma}: effective horizon ≈ {steps} steps")

show_discount_horizon(0.5)   # γ=0.5: effective horizon ≈ 7 steps
show_discount_horizon(0.9)   # γ=0.9: effective horizon ≈ 44 steps
show_discount_horizon(0.99)  # γ=0.99: effective horizon ≈ 459 steps
```

For GridWorld Tactics, γ = 0.9 is a good starting point. The grid is small enough that the goal is reachable in ~6 steps from the start.

## Reward Design: The Hard Part

Mira (game designer) asks: "What reward should I give for capturing an objective?"

This question is deceptively hard. The reward function defines what the agent optimizes. Get it wrong, and the agent optimizes the wrong thing — perfectly.

### Reward Design Pitfall 1: Sparse Rewards

```python
# Only reward at the very end
def sparse_reward(state, done, won):
    if done and won:
        return 1.0
    return 0.0
```

Problem: The agent gets 0 reward for thousands of steps, then suddenly +1 or nothing. It has no signal to learn from. It's like grading a student only with a final exam and no homework, quizzes, or feedback.

On our 4×4 grid, sparse rewards work because the goal is close. On a 20×20 grid with obstacles? The agent will never stumble into the goal by random exploration.

### Reward Design Pitfall 2: Dense but Misleading

```python
# Reward for getting closer to the goal (Manhattan distance)
def distance_reward(state, goal):
    dist = abs(state[0] - goal[0]) + abs(state[1] - goal[1])
    return -dist * 0.1
```

Problem: The agent learns to minimize distance to the goal — but what if there's a wall in the way? It'll press against the wall forever, getting the best distance reward it can, never learning to go around.

### Reward Design Pitfall 3: Reward Hacking

Mira defines: "+0.1 for each enemy unit damaged."

The agent discovers it can damage an enemy, let it heal, damage it again — farming reward infinitely without ever winning the game.

This is **reward hacking** — the agent finds a way to maximize reward that doesn't align with what you actually wanted.

### Good Reward Design Principles

1. **Reward the outcome, not the path** — reward winning, not the steps that lead to winning
2. **Keep it simple** — fewer reward components = fewer ways to exploit
3. **Test with a random agent** — if a random agent gets positive reward, your rewards are too easy to exploit
4. **Add shaping carefully** — intermediate rewards help learning but can distort behavior

For our grid world, we'll use:

```python
def reward_function(state, done):
    if state == goal:
        return 1.0       # Reached the goal
    elif state in traps:
        return -1.0      # Fell in a trap
    else:
        return -0.04     # Time penalty (encourages efficiency)
```

Simple. Clear. Hard to exploit.

## Putting It Together: The Learning Loop

Every RL algorithm follows this loop:

```python
def rl_loop(env, agent, episodes=1000, gamma=0.9):
    """The fundamental RL training loop."""
    for episode in range(episodes):
        state = env.reset()
        done = False
        rewards = []
        
        while not done:
            # 1. Agent picks an action based on current state
            action = agent.choose_action(state)
            
            # 2. Environment responds with new state and reward
            next_state, reward, done = env.step(action)
            
            # 3. Agent learns from this experience
            agent.learn(state, action, reward, next_state, done)
            
            # 4. Move to next state
            state = next_state
            rewards.append(reward)
        
        # Compute return for this episode
        G = compute_return(rewards, gamma)
        agent.episode_returns.append(G)
```

The three key methods every agent must implement:
- `choose_action(state)` — the policy (how to pick actions)
- `learn(state, action, reward, next_state, done)` — the update rule (how to improve)
- Some way to track performance over time

Right now, our random agent has a trivial `choose_action` and no `learn` at all. The next 14 chapters fill in those methods with increasingly sophisticated algorithms.

## Measuring Progress: The Learning Curve

```python
import matplotlib.pyplot as plt

def plot_learning_curve(returns, window=50, title="Learning Curve"):
    """Plot episode returns with a moving average."""
    avg = np.convolve(returns, np.ones(window)/window, mode='valid')
    
    plt.figure(figsize=(10, 4))
    plt.plot(returns, alpha=0.3, color='blue', label='Episode return')
    plt.plot(range(window-1, len(returns)), avg, color='red', label=f'{window}-episode average')
    plt.xlabel('Episode')
    plt.ylabel('Return')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

A good learning curve goes up over time. A flat line means the agent isn't learning. A line that goes up then crashes means the agent is unstable.

The random agent's learning curve is flat — it never improves because it never learns.

## Jonas Checks In

Jonas: "So the random agent is the baseline. What's the first real algorithm?"

You: "The agent needs to learn which actions are good. But first it needs to *try* different actions. Right now it explores randomly — but once it starts learning, it'll want to exploit what it knows. The tension between trying new things and using what works is the core problem."

Jonas: "Exploration vs exploitation."

You: "Exactly. Chapter 2."

## What You Learned

- **Reward** — a single number after each action; the only teaching signal
- **Return (G)** — total (discounted) reward over an episode
- **Discounting (γ)** — future rewards are worth less; controls planning horizon
- **Reward design** — sparse rewards give no signal; dense rewards can mislead; reward hacking is real
- **The RL loop** — observe state → choose action → receive reward → learn → repeat
- **Learning curves** — the primary tool for measuring whether an agent is improving
- **Baseline** — random agent gets ~18% success on our 4×4 grid

The agent has a reward signal. It knows what "good" means. But it has no strategy for discovering good behavior. It needs to balance trying new things with repeating what worked.

That's the exploration problem.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Exploration →](chapter-02-exploration.md)
