# Chapter 10: Deep Q-Networks

[← Chapter 9: Function Approximation](chapter-09-function-approximation.md) | [Chapter 11: Policy Gradients →](chapter-11-policy-gradients.md)

---

## The Problem

Linear function approximation can't capture the complex value landscape of GridWorld Tactics. The relationship between state features and optimal actions is deeply nonlinear — whether to attack depends on dozens of interacting factors.

You try a neural network as the Q-function approximator. It diverges within 100 episodes. Q-values explode to ±10,000. The agent oscillates wildly.

Jonas: "I thought neural networks could learn anything."

You: "They can — but naively combining neural networks with Q-learning is unstable. The deadly triad strikes. We need two tricks to stabilize it: experience replay and target networks."

This is the **Deep Q-Network (DQN)** — the algorithm that played Atari games at superhuman level in 2015.

## Why Naive Deep Q-Learning Fails

Three problems:

### 1. Correlated Samples
In online learning, consecutive samples are highly correlated (state 5 → state 6 → state 7). Neural networks trained on correlated data overfit to recent experience and forget earlier lessons.

### 2. Moving Target
The TD target `r + γ · max Q(s', a')` uses the same network we're updating. Every update changes the target. It's like a dog chasing its own tail.

### 3. Catastrophic Forgetting
The network overwrites old knowledge when learning new things. It masters one part of the grid, then forgets it while learning another part.

## The DQN Solution

Two key innovations:

### Experience Replay
Store transitions in a buffer. Sample random mini-batches for training. This breaks correlation and reuses data efficiently.

### Target Network
Keep a separate, slowly-updated copy of the network for computing targets. This stabilizes the target and prevents oscillation.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (np.array(states), np.array(actions), np.array(rewards),
                np.array(next_states), np.array(dones))
    
    def __len__(self):
        return len(self.buffer)
```

## The DQN Architecture

```python
class QNetwork(nn.Module):
    def __init__(self, state_dim, n_actions, hidden_dim=64):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_actions)
        )
    
    def forward(self, state):
        """Input: state features. Output: Q-value for each action."""
        return self.network(state)

class DQNAgent:
    def __init__(self, state_dim, n_actions, hidden_dim=64, lr=1e-3,
                 gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995,
                 buffer_size=10000, batch_size=64, target_update_freq=100):
        
        self.n_actions = n_actions
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.step_count = 0
        
        # Two networks: online (learning) and target (stable)
        self.q_network = QNetwork(state_dim, n_actions, hidden_dim)
        self.target_network = QNetwork(state_dim, n_actions, hidden_dim)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        self.replay_buffer = ReplayBuffer(buffer_size)
    
    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            return q_values.argmax(dim=1).item()
    
    def store_transition(self, state, action, reward, next_state, done):
        self.replay_buffer.push(state, action, reward, next_state, done)
    
    def learn(self):
        """Sample from replay buffer and update Q-network."""
        if len(self.replay_buffer) < self.batch_size:
            return
        
        # Sample random batch (breaks correlation!)
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)
        
        # Current Q-values
        current_q = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Target Q-values (from target network — stable!)
        with torch.no_grad():
            next_q = self.target_network(next_states).max(dim=1)[0]
            td_target = rewards + self.gamma * next_q * (1 - dones)
        
        # Loss and update
        loss = nn.MSELoss()(current_q, td_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network periodically
        self.step_count += 1
        if self.step_count % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()
```

## Training Loop

```python
def train_dqn(env_name='CartPole-v1', episodes=500):
    env = gym.make(env_name)
    state_dim = env.observation_space.shape[0]
    n_actions = env.action_space.n
    
    agent = DQNAgent(state_dim, n_actions)
    episode_rewards = []
    
    for ep in range(episodes):
        obs, _ = env.reset()
        episode_reward = 0
        
        for step in range(500):
            action = agent.choose_action(obs)
            next_obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            agent.store_transition(obs, action, reward, next_obs, float(done))
            agent.learn()
            
            obs = next_obs
            episode_reward += reward
            
            if done:
                break
        
        episode_rewards.append(episode_reward)
        
        if (ep + 1) % 50 == 0:
            avg = np.mean(episode_rewards[-50:])
            print(f"Episode {ep+1}, Avg Reward: {avg:.1f}, Epsilon: {agent.epsilon:.3f}")
    
    env.close()
    return episode_rewards

rewards = train_dqn()
```

Typical output:
```
Episode 50,  Avg Reward: 23.4, Epsilon: 0.779
Episode 100, Avg Reward: 45.2, Epsilon: 0.607
Episode 150, Avg Reward: 112.8, Epsilon: 0.473
Episode 200, Avg Reward: 198.3, Epsilon: 0.369
Episode 250, Avg Reward: 312.5, Epsilon: 0.287
Episode 300, Avg Reward: 456.2, Epsilon: 0.224
```

The agent solves CartPole (500 steps) within ~300 episodes.

## How Experience Replay Helps

```python
# Without replay: train on consecutive transitions
# s1→s2, s2→s3, s3→s4, s4→s5 (highly correlated!)

# With replay: train on random samples from history
# s847→s848, s12→s13, s503→s504, s291→s292 (uncorrelated!)
```

Benefits:
1. **Breaks correlation** — random sampling decorrelates training data
2. **Data efficiency** — each transition is used many times (not just once)
3. **Stability** — the network sees a diverse mix of experiences

## How the Target Network Helps

```python
# Without target network:
target = reward + gamma * Q_network(next_state).max()  # Target changes every update!

# With target network:
target = reward + gamma * Q_target(next_state).max()   # Target is stable for N steps
```

The target network is a frozen copy of the Q-network. It's updated every N steps (hard update) or slowly blended (soft update):

```python
# Hard update (every N steps)
target_network.load_state_dict(q_network.state_dict())

# Soft update (every step, τ = 0.005)
for target_param, param in zip(target_network.parameters(), q_network.parameters()):
    target_param.data.copy_(tau * param.data + (1 - tau) * target_param.data)
```

## Double DQN

Remember the maximization bias from Chapter 7? It's worse with neural networks. **Double DQN** fixes it:

```python
def double_dqn_target(self, next_states, rewards, dones):
    """
    Double DQN: online network selects action, target network evaluates it.
    """
    with torch.no_grad():
        # Online network picks the best action
        best_actions = self.q_network(next_states).argmax(dim=1)
        
        # Target network evaluates that action
        next_q = self.target_network(next_states).gather(1, best_actions.unsqueeze(1)).squeeze(1)
        
        td_target = rewards + self.gamma * next_q * (1 - dones)
    
    return td_target
```

This decouples action selection (online network) from action evaluation (target network), reducing overestimation.

## Dueling DQN

Some states are inherently good or bad regardless of action. **Dueling DQN** separates the value function into:
- V(s): how good is this state?
- A(s,a): how much better is this action than average?

```python
class DuelingQNetwork(nn.Module):
    def __init__(self, state_dim, n_actions, hidden_dim=64):
        super().__init__()
        
        self.feature = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Value stream: V(s)
        self.value_stream = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Advantage stream: A(s, a)
        self.advantage_stream = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_actions)
        )
    
    def forward(self, state):
        features = self.feature(state)
        value = self.value_stream(features)
        advantage = self.advantage_stream(features)
        
        # Q(s,a) = V(s) + A(s,a) - mean(A(s,:))
        q_values = value + advantage - advantage.mean(dim=1, keepdim=True)
        return q_values
```

Dueling DQN learns faster because it can quickly identify bad states (low V) without needing to evaluate every action.

## Prioritized Experience Replay

Not all transitions are equally useful. Transitions with high TD error (surprising outcomes) are more informative:

```python
class PrioritizedReplayBuffer:
    def __init__(self, capacity=10000, alpha=0.6):
        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        self.alpha = alpha  # How much prioritization to use
    
    def push(self, state, action, reward, next_state, done, td_error=1.0):
        self.buffer.append((state, action, reward, next_state, done))
        self.priorities.append(abs(td_error) + 1e-6)  # Small constant to avoid zero priority
    
    def sample(self, batch_size, beta=0.4):
        priorities = np.array(self.priorities) ** self.alpha
        probs = priorities / priorities.sum()
        
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        
        # Importance sampling weights (correct for bias)
        weights = (len(self.buffer) * probs[indices]) ** (-beta)
        weights /= weights.max()
        
        batch = [self.buffer[i] for i in indices]
        return batch, indices, weights
    
    def update_priorities(self, indices, td_errors):
        for idx, td_error in zip(indices, td_errors):
            self.priorities[idx] = abs(td_error) + 1e-6
```

Prioritized replay focuses learning on the most surprising (and therefore most informative) transitions.

## DQN on GridWorld Tactics

```python
def train_gridworld_tactics_dqn():
    """DQN on a more complex grid environment."""
    # State: [row, col, health, ammo, enemy_row, enemy_col, enemy_health]
    state_dim = 7
    n_actions = 5  # up, down, left, right, attack
    
    agent = DQNAgent(
        state_dim=state_dim,
        n_actions=n_actions,
        hidden_dim=128,
        lr=5e-4,
        gamma=0.99,
        buffer_size=50000,
        batch_size=128,
        target_update_freq=200
    )
    
    # Training would go here...
    # The key insight: DQN handles the 7-dimensional continuous state
    # without needing a table with millions of entries
```

## Hyperparameter Guide

| Parameter | Typical Range | Effect |
|---|---|---|
| Learning rate | 1e-4 to 1e-3 | Too high → unstable; too low → slow |
| Buffer size | 10K to 1M | Larger → more diverse samples |
| Batch size | 32 to 256 | Larger → more stable gradients |
| Target update freq | 100 to 10000 | More frequent → less stable |
| Epsilon decay | 0.99 to 0.9999 | Faster → less exploration |
| Hidden layers | 2-3 layers, 64-256 units | Larger → more capacity |
| Gamma | 0.95 to 0.999 | Higher → longer planning horizon |

## QA Tanya's Report

Tanya: "The DQN agent beats the scripted AI on the 20×20 grid. It flanks, it retreats when low on health, it prioritizes objectives. But..."

Jonas: "But?"

Tanya: "It can only do discrete actions. Move up, move down, attack. The game designers want smooth movement — any angle, any speed. DQN can't handle continuous actions."

You: "Right. DQN outputs Q-values for each discrete action. If actions are continuous (move at angle 37° with speed 0.7), we can't enumerate all possibilities. We need a different approach — one that directly outputs actions instead of evaluating them."

Jonas: "Policy gradients?"

You: "Policy gradients."

## What You Learned

- **DQN** — neural network as Q-function approximator with two stabilization tricks
- **Experience replay** — store and randomly sample transitions; breaks correlation
- **Target network** — frozen copy for stable TD targets; updated periodically
- **Double DQN** — separate action selection from evaluation to reduce overestimation
- **Dueling DQN** — separate V(s) and A(s,a) streams for faster learning
- **Prioritized replay** — focus on surprising transitions for efficient learning
- **The result** — DQN handles continuous/high-dimensional states that tables cannot
- **The limitation** — only works for discrete actions; can't handle continuous action spaces

DQN conquered discrete-action problems with complex states. But many real problems have continuous actions — steering angles, force magnitudes, resource allocations. For those, we need to learn the policy directly.

---

[← Chapter 9: Function Approximation](chapter-09-function-approximation.md) | [Chapter 11: Policy Gradients →](chapter-11-policy-gradients.md)
