# Chapter 7: Q-Learning

[← Chapter 6: Temporal Difference Learning](chapter-06-td-learning.md) | [Chapter 8: SARSA →](chapter-08-sarsa.md)

---

## The Problem

TD(0) estimates V(s) — how good each state is. But to pick actions, you need Q(s,a) — how good each action is in each state.

With V(s), choosing the best action requires knowing the transition model:
```python
best_action = argmax_a [R(s,a) + gamma * V(next_state(s,a))]
#                                        ^^^^^^^^^^^^^^^^
#                                        Need to know where action leads!
```

With Q(s,a), you just pick the highest Q value:
```python
best_action = argmax_a Q[s, a]  # No model needed!
```

Q-learning estimates Q* (the optimal action-value function) directly, using TD updates. It's the first algorithm that learns the optimal policy without needing a model and without waiting for episodes to end.

## The Q-Learning Update

```
Q(s, a) ← Q(s, a) + α · [r + γ · max_a' Q(s', a') - Q(s, a)]
```

In English: "Update Q(s,a) toward the reward I got plus the best possible value from the next state."

The key: `max_a' Q(s', a')` — Q-learning always uses the *best* next action for the target, regardless of what action the agent actually takes next. This makes it **off-policy** — it learns about the optimal policy while following an exploratory policy.

```python
class QLearningAgent:
    def __init__(self, n_states=16, n_actions=4, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.Q = np.zeros((n_states, n_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.episode_returns = []
    
    def choose_action(self, state):
        """Epsilon-greedy action selection."""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.Q.shape[1])
        return np.argmax(self.Q[state])
    
    def learn(self, state, action, reward, next_state, done):
        """Q-learning update: use max Q(s', a') as target."""
        if done:
            td_target = reward
        else:
            td_target = reward + self.gamma * np.max(self.Q[next_state])
        
        td_error = td_target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error
```

## Training the Q-Learning Agent

```python
def train_q_learning(episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
    env = GridWorld()
    agent = QLearningAgent(n_states=16, n_actions=4, 
                           alpha=alpha, gamma=gamma, epsilon=epsilon)
    
    for ep in range(episodes):
        state = env.reset()
        state_idx = state[0] * 4 + state[1]
        episode_reward = 0
        
        for step in range(100):
            action = agent.choose_action(state_idx)
            next_state, reward, done = env.step(action)
            next_idx = next_state[0] * 4 + next_state[1]
            
            if not done:
                reward = -0.04  # Time penalty
            
            agent.learn(state_idx, action, reward, next_idx, done)
            
            state_idx = next_idx
            episode_reward += reward
            
            if done:
                break
        
        agent.episode_returns.append(episode_reward)
    
    return agent

agent = train_q_learning(episodes=500)
print(f"Last 50 episodes avg reward: {np.mean(agent.episode_returns[-50:]):.3f}")
```

Result: ~0.75 average reward in the last 50 episodes. The agent consistently finds the goal while avoiding traps.

## Why Off-Policy Matters

Q-learning is off-policy: the **behavior policy** (ε-greedy, explores) differs from the **target policy** (greedy, exploits).

```python
# During training:
action = epsilon_greedy(Q, state)     # Behavior: explores
# But the update uses:
target = reward + gamma * max(Q[s'])  # Target: assumes optimal future actions
```

This separation is powerful:
1. The agent explores (tries random actions to discover the environment)
2. But it learns about the optimal policy (what it *should* do)
3. The Q-table converges to Q* regardless of how much the agent explores

Compare with on-policy methods (SARSA, Chapter 8): they learn about the policy they're actually following, exploration and all.

## Visualizing Q-Values

```python
def visualize_q_values(agent, env_size=4):
    """Show Q-values as a heatmap for each action."""
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    action_names = ['Up', 'Down', 'Left', 'Right']
    
    for a, ax in enumerate(axes):
        q_grid = agent.Q[:, a].reshape(env_size, env_size)
        im = ax.imshow(q_grid, cmap='RdYlGn', vmin=-1, vmax=1)
        ax.set_title(f'Q(s, {action_names[a]})')
        
        for r in range(env_size):
            for c in range(env_size):
                ax.text(c, r, f'{q_grid[r, c]:.2f}', ha='center', va='center')
        
        ax.set_xticks(range(env_size))
        ax.set_yticks(range(env_size))
    
    plt.colorbar(im, ax=axes, shrink=0.8)
    plt.suptitle('Q-Values by Action')
    plt.tight_layout()
    plt.show()

visualize_q_values(agent)
```

The Q-table reveals the agent's complete knowledge: for every state, it knows the expected value of every action. The policy is simply: pick the action with the highest Q-value.

## Convergence Guarantees

Q-learning converges to Q* (the optimal action-value function) under two conditions:

1. **Every state-action pair is visited infinitely often** — ε-greedy ensures this (as long as ε > 0)
2. **The learning rate decreases appropriately** — technically needs Σα = ∞ and Σα² < ∞

In practice, a fixed α = 0.1 works well for small problems. For larger problems, decaying α helps stability.

```python
def decaying_alpha(episode, alpha_start=0.5, alpha_end=0.01, decay=0.999):
    """Decay learning rate over time."""
    return max(alpha_end, alpha_start * (decay ** episode))
```

## Q-Learning on Larger Grids

Let's test on an 8×8 grid with more traps:

```python
class LargerGridWorld:
    def __init__(self, size=8):
        self.size = size
        self.n_states = size * size
        self.n_actions = 4
        
        self.goal = (0, size-1)
        self.traps = [(1, 3), (2, 5), (3, 1), (4, 6), (5, 2), (6, 4)]
        self.start = (size-1, 0)
        self.agent_pos = self.start
    
    # ... (same step/reset logic as before)

def train_larger_grid(episodes=5000):
    env = LargerGridWorld(size=8)
    agent = QLearningAgent(n_states=64, n_actions=4, 
                           alpha=0.1, gamma=0.95, epsilon=0.1)
    
    for ep in range(episodes):
        state = env.reset()
        state_idx = state[0] * 8 + state[1]
        
        for step in range(200):
            action = agent.choose_action(state_idx)
            next_state, reward, done = env.step(action)
            next_idx = next_state[0] * 8 + next_state[1]
            
            if not done:
                reward = -0.01
            
            agent.learn(state_idx, action, reward, next_idx, done)
            state_idx = next_idx
            
            if done:
                break
        
        agent.episode_returns.append(step)
    
    return agent
```

On the 8×8 grid, Q-learning takes ~2000 episodes to find a good policy. The Q-table has 64 × 4 = 256 entries — still manageable.

But what about a 100×100 grid? That's 10,000 states × 4 actions = 40,000 Q-values. Still feasible.

What about continuous states (position = any real number)? Or states with multiple features (position, velocity, health, ammo)? The Q-table approach breaks down. That's Chapter 9-10.

## The Maximization Bias Problem

Q-learning has a subtle flaw. The `max` operation introduces an upward bias:

```python
td_target = reward + gamma * np.max(Q[next_state])
#                            ^^^^^^
#                            This overestimates!
```

If Q-values are noisy (early in training), `max` picks the noisiest high value. It's like asking "what's the best restaurant?" when all your ratings are random — you'll pick whichever got lucky.

**Double Q-learning** fixes this by maintaining two Q-tables:

```python
class DoubleQLearningAgent:
    def __init__(self, n_states=16, n_actions=4, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.Q1 = np.zeros((n_states, n_actions))
        self.Q2 = np.zeros((n_states, n_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
    
    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.Q1.shape[1])
        # Use sum of both Q-tables for action selection
        return np.argmax(self.Q1[state] + self.Q2[state])
    
    def learn(self, state, action, reward, next_state, done):
        if np.random.random() < 0.5:
            # Update Q1 using Q2 for evaluation
            if done:
                target = reward
            else:
                best_action = np.argmax(self.Q1[next_state])  # Q1 picks action
                target = reward + self.gamma * self.Q2[next_state, best_action]  # Q2 evaluates
            self.Q1[state, action] += self.alpha * (target - self.Q1[state, action])
        else:
            # Update Q2 using Q1 for evaluation
            if done:
                target = reward
            else:
                best_action = np.argmax(self.Q2[next_state])
                target = reward + self.gamma * self.Q1[next_state, best_action]
            self.Q2[state, action] += self.alpha * (target - self.Q2[state, action])
```

One Q-table selects the best action; the other evaluates it. This decouples selection from evaluation and eliminates the upward bias.

## Jonas Checks In

Jonas: "Q-learning finds the optimal policy. Why do we need anything else?"

You: "Two reasons. First, Q-learning can be aggressive — it assumes optimal future behavior, which can be dangerous in risky environments. If there's a cliff next to the optimal path, Q-learning will walk right along the edge because it assumes it'll never slip. SARSA is more cautious."

Jonas: "And the second reason?"

You: "The Q-table. It works for 16 states, 64 states, even 10,000 states. But GridWorld Tactics has continuous positions, multiple units, health bars, resources... the state space is effectively infinite. We can't have a table entry for every possible state. We need function approximation — neural networks that generalize across similar states."

Jonas: "When do we get to neural networks?"

You: "Chapter 10. First we need to understand SARSA (the cautious alternative) and why tables break down."

## What You Learned

- **Q-learning** — TD update for Q(s,a) using max Q(s', a') as target
- **Off-policy** — learns optimal policy while following exploratory policy
- **The update** — Q(s,a) ← Q(s,a) + α·[r + γ·max Q(s',a') - Q(s,a)]
- **Convergence** — guaranteed to find Q* with sufficient exploration and appropriate α
- **Maximization bias** — max operator overestimates noisy Q-values
- **Double Q-learning** — two Q-tables to decouple action selection from evaluation
- **Limitation** — Q-table size grows linearly with state space; breaks for large/continuous states

Q-learning is the workhorse of tabular RL. But its aggressive optimism (always assuming optimal future behavior) can be dangerous. The next chapter introduces SARSA — a more cautious learner that accounts for its own exploration mistakes.

---

[← Chapter 6: Temporal Difference Learning](chapter-06-td-learning.md) | [Chapter 8: SARSA →](chapter-08-sarsa.md)
