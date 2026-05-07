# Chapter 14: Reward Shaping

[← Chapter 13: PPO](chapter-13-ppo.md) | [Chapter 15: Model-Based RL →](chapter-15-model-based.md)

---

## The Problem

The final level of GridWorld Tactics: a 20×20 grid with fog of war, multiple objectives, enemy units, and resource management. The only natural reward: +1 for winning the game, -1 for losing. A game lasts 200-500 turns.

You train PPO for 50,000 episodes. The agent learns nothing. Win rate: 50% (same as random against the scripted AI, which also wins 50% by design).

Jonas: "50,000 episodes and it hasn't improved at all?"

You: "The reward is too sparse. The agent needs to make 200 correct decisions in a row to win. The probability of stumbling into a win by random exploration is essentially zero. It never gets the +1 signal, so it never learns."

Mira: "Can't we give it intermediate rewards? Like +0.1 for capturing an objective, +0.05 for damaging an enemy?"

You: "We can — that's reward shaping. But we have to be careful. Bad shaping creates agents that optimize the shaped reward instead of actually winning."

## The Sparse Reward Problem

```python
def sparse_reward(game_state):
    """Only reward at game end."""
    if game_state.won:
        return 1.0
    elif game_state.lost:
        return -1.0
    return 0.0  # 99.9% of steps get zero reward
```

With sparse rewards, the agent gets no gradient signal for hundreds of steps. It's like trying to learn to cook by only being told "good meal" or "bad meal" after eating — with no feedback during preparation.

The agent needs breadcrumbs — intermediate signals that point toward the goal.

## Naive Reward Shaping (And Why It Fails)

### Attempt 1: Reward Everything

```python
def over_shaped_reward(game_state, action):
    reward = 0
    reward += 0.1 * game_state.enemies_damaged
    reward += 0.2 * game_state.objectives_captured
    reward += 0.05 * game_state.distance_moved_toward_enemy
    reward += 0.01 * game_state.ammo_collected
    reward -= 0.1 * game_state.health_lost
    reward -= 0.05 * game_state.turns_idle
    return reward
```

Problem: The agent learns to maximize this shaped reward, not to win. It might:
- Damage enemies without killing them (farming the damage reward)
- Capture objectives but never defend them
- Collect ammo it doesn't need
- Never take risks (avoiding health loss) even when aggression would win

This is reward hacking — the agent finds a policy that maximizes the proxy reward without achieving the true goal.

### Attempt 2: Distance-Based Shaping

```python
def distance_reward(state, goal):
    """Reward for getting closer to the goal."""
    current_dist = manhattan_distance(state.pos, goal)
    return -current_dist * 0.01
```

Problem: The agent presses against walls trying to minimize distance. It never learns to go around obstacles because the detour temporarily increases distance (negative reward).

## Potential-Based Reward Shaping (PBRS)

There's a theoretically sound way to add shaping rewards without changing the optimal policy. Define a **potential function** Φ(s) and add:

```
F(s, s') = γ · Φ(s') - Φ(s)
```

This is the only form of shaping reward guaranteed to preserve the optimal policy.

```python
def potential_based_shaping(state, next_state, gamma=0.99):
    """
    PBRS: the shaped reward is the change in potential.
    Guaranteed not to change the optimal policy!
    """
    phi_s = potential(state)
    phi_s_next = potential(next_state)
    return gamma * phi_s_next - phi_s

def potential(state):
    """
    Potential function: higher for states closer to winning.
    This encodes domain knowledge about what "progress" looks like.
    """
    score = 0
    score += 10 * state.objectives_held / state.total_objectives
    score -= manhattan_distance(state.pos, nearest_objective(state)) * 0.1
    score += state.health / 100 * 2
    score += state.enemy_damage_dealt / state.enemy_total_health * 5
    return score
```

### Why PBRS Works

The shaped reward telescopes over an episode:

```
Σ F(s_t, s_{t+1}) = γΦ(s_1) - Φ(s_0) + γΦ(s_2) - Φ(s_1) + ...
                   ≈ Φ(s_final) - Φ(s_0)  (approximately, with discounting)
```

The total shaping reward depends only on start and end states — it doesn't change which path is optimal. It just makes the reward signal denser, helping the agent learn faster.

```python
class PBRSEnvironment:
    """Wrapper that adds potential-based shaping to any environment."""
    
    def __init__(self, env, potential_fn, gamma=0.99):
        self.env = env
        self.potential_fn = potential_fn
        self.gamma = gamma
        self.prev_potential = None
    
    def reset(self):
        state = self.env.reset()
        self.prev_potential = self.potential_fn(state)
        return state
    
    def step(self, action):
        next_state, reward, done = self.env.step(action)
        
        # Add shaping reward
        current_potential = self.potential_fn(next_state)
        shaping = self.gamma * current_potential - self.prev_potential
        shaped_reward = reward + shaping
        
        self.prev_potential = current_potential
        return next_state, shaped_reward, done
```

## Curiosity-Driven Exploration

What if the agent could generate its own rewards? **Intrinsic motivation** rewards the agent for discovering new things:

```python
class CuriosityModule:
    """
    Reward the agent for encountering states it can't predict.
    Novel states → high prediction error → high intrinsic reward.
    """
    
    def __init__(self, state_dim, action_dim, hidden_dim=64, lr=1e-3):
        # Forward model: predicts next state from (state, action)
        self.forward_model = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, state_dim)
        )
        self.optimizer = optim.Adam(self.forward_model.parameters(), lr=lr)
    
    def compute_intrinsic_reward(self, state, action, next_state):
        """Intrinsic reward = prediction error of the forward model."""
        state_tensor = torch.FloatTensor(state)
        action_tensor = torch.FloatTensor(self._one_hot(action))
        next_state_tensor = torch.FloatTensor(next_state)
        
        # Predict next state
        input_tensor = torch.cat([state_tensor, action_tensor])
        predicted_next = self.forward_model(input_tensor)
        
        # Prediction error = intrinsic reward
        error = (predicted_next - next_state_tensor).pow(2).mean()
        
        # Update forward model
        self.optimizer.zero_grad()
        error.backward()
        self.optimizer.step()
        
        return error.item()
    
    def _one_hot(self, action, n_actions=8):
        vec = np.zeros(n_actions)
        vec[action] = 1.0
        return vec
```

The agent is rewarded for surprise — states it can't predict. This drives exploration into novel areas of the state space, even without external rewards.

### Combining Intrinsic and Extrinsic Rewards

```python
def combined_reward(extrinsic_reward, intrinsic_reward, beta=0.1):
    """
    Total reward = extrinsic (from environment) + β × intrinsic (from curiosity).
    β controls exploration drive.
    """
    return extrinsic_reward + beta * intrinsic_reward
```

As the forward model improves, intrinsic rewards decrease for familiar states. The agent naturally shifts from exploration to exploitation.

## Hindsight Experience Replay (HER)

A radical idea: what if failed episodes could still teach something?

The agent tries to reach goal G but ends up at state S. With HER, we retroactively pretend the goal was S all along — and the agent "succeeded."

```python
class HindsightReplayBuffer:
    """
    Store transitions with the original goal AND with hindsight goals.
    """
    
    def __init__(self, capacity=100000, n_hindsight=4):
        self.buffer = deque(maxlen=capacity)
        self.n_hindsight = n_hindsight
    
    def store_episode(self, episode, goal):
        """
        Store the episode with original goal AND with hindsight goals.
        """
        # Store with original goal
        for state, action, reward, next_state, done in episode:
            self.buffer.append((state, action, reward, next_state, done, goal))
        
        # Store with hindsight goals (states actually achieved)
        for i, (state, action, _, next_state, _) in enumerate(episode):
            # Pick future states from this episode as alternative goals
            future_indices = np.random.choice(
                range(i, len(episode)), 
                min(self.n_hindsight, len(episode) - i),
                replace=False
            )
            
            for idx in future_indices:
                hindsight_goal = episode[idx][3]  # next_state of future step
                
                # Recompute reward with new goal
                new_reward = 1.0 if np.allclose(next_state, hindsight_goal) else -0.01
                new_done = np.allclose(next_state, hindsight_goal)
                
                self.buffer.append((state, action, new_reward, next_state, 
                                   new_done, hindsight_goal))
```

HER is powerful for goal-conditioned tasks: "reach position X", "pick up object Y", "navigate to Z". Even when the agent fails at the intended goal, it learns to reach the states it actually visited — building skills that transfer to the real goal.

## Reward Shaping for GridWorld Tactics

```python
def gridworld_tactics_potential(state):
    """
    Potential function for GridWorld Tactics.
    Encodes domain knowledge about what constitutes progress.
    """
    potential = 0
    
    # Objective control (most important)
    potential += 20 * (state.objectives_held / state.total_objectives)
    
    # Military advantage
    potential += 10 * (state.enemy_units_killed / state.enemy_total_units)
    
    # Resource advantage
    potential += 5 * (state.our_total_health / state.max_total_health)
    
    # Positional advantage (controlling center)
    center = state.grid_size / 2
    dist_to_center = abs(state.avg_unit_pos[0] - center) + abs(state.avg_unit_pos[1] - center)
    potential -= dist_to_center * 0.5
    
    return potential

def train_with_shaping(episodes=10000):
    """Train PPO with potential-based reward shaping."""
    env = GridWorldTactics()
    shaped_env = PBRSEnvironment(env, gridworld_tactics_potential)
    
    agent = PPOAgent(state_dim=20, n_actions=8)
    
    for ep in range(episodes):
        state = shaped_env.reset()
        
        for step in range(500):
            action = agent.choose_action(state)
            next_state, shaped_reward, done = shaped_env.step(action)
            agent.store(shaped_reward, done)
            state = next_state
            if done:
                break
        
        # Update PPO
        agent.update(next_value=0 if done else agent.model(state)[1])
    
    return agent
```

## Results: Sparse vs Shaped

```
Sparse reward only:
  Episode 10000: Win rate 52% (barely above random)
  Episode 50000: Win rate 58% (slow improvement)

With PBRS:
  Episode 10000: Win rate 72% (rapid improvement)
  Episode 50000: Win rate 91% (near-optimal)

With PBRS + Curiosity:
  Episode 10000: Win rate 75%
  Episode 50000: Win rate 93% (explores edge cases better)
```

Reward shaping doesn't change what's optimal — it just makes the signal dense enough for the agent to learn from.

## Mira's Reward Design Checklist

After several iterations, Mira develops a checklist for reward design:

1. **Start with the true objective** — win/lose signal must be present
2. **Add PBRS for learning speed** — potential function encodes progress
3. **Test with a random agent** — if random gets positive shaped reward, it's too easy to exploit
4. **Monitor for reward hacking** — watch for agents that get high reward but don't win
5. **Ablate components** — remove each shaping term and check if performance drops
6. **Reduce shaping over time** — as the agent improves, reduce β toward zero

## What You Learned

- **Sparse reward problem** — agent gets no signal for hundreds of steps; can't learn
- **Naive shaping pitfalls** — over-shaping leads to reward hacking; distance rewards get stuck
- **Potential-based reward shaping (PBRS)** — F = γΦ(s') - Φ(s); preserves optimal policy
- **Curiosity** — intrinsic reward from prediction error; drives exploration of novel states
- **Hindsight Experience Replay** — learn from failures by retroactively changing the goal
- **Practical shaping** — combine true reward + PBRS + curiosity for best results
- **The key insight** — shaping makes learning faster without changing what's optimal

The agent can now learn from dense signals even when the true reward is sparse. But it's still learning everything through trial and error — thousands of episodes of bumping into things.

What if the agent could build a model of the world and plan ahead? Simulate outcomes without actually taking actions? That's model-based RL.

---

[← Chapter 13: PPO](chapter-13-ppo.md) | [Chapter 15: Model-Based RL →](chapter-15-model-based.md)
