# Chapter 4: Deep Q-Networks (DQN)

[← Q-Learning](./chapter-03-qlearning.md) | [Next: Policy Gradient →](./chapter-05-policy-gradient.md)

---

## Why Deep Q-Networks?

Tabular Q-learning fails with large/continuous state spaces. DQN approximates `Q(s,a)` with a neural network.

**Key innovations:**

1. **Experience Replay** — store transitions, sample random mini-batches (breaks correlation)
2. **Target Network** — separate network for stable TD targets

**Loss:**

`L = \mathbb{E}\left[\left(r + \gamma \max_{a'} Q_{target}(s',a') - Q(s,a)\right)^2\right]`

## Implementation

```python
import torch
import torch.nn as nn
import numpy as np
import gymnasium as gym
from collections import deque
import random

class QNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, action_dim)
        )

    def forward(self, x):
        return self.net(x)

class DQNAgent:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99,
                 buffer_size=10000, batch_size=64):
        self.action_dim = action_dim
        self.gamma = gamma
        self.batch_size = batch_size

        self.q_net = QNetwork(state_dim, action_dim)
        self.target_net = QNetwork(state_dim, action_dim)
        self.target_net.load_state_dict(self.q_net.state_dict())

        self.optimizer = torch.optim.Adam(self.q_net.parameters(), lr=lr)
        self.buffer = deque(maxlen=buffer_size)

    def act(self, state, epsilon):
        if random.random() < epsilon:
            return random.randrange(self.action_dim)
        with torch.no_grad():
            q = self.q_net(torch.FloatTensor(state))
            return q.argmax().item()

    def store(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def train_step(self):
        if len(self.buffer) < self.batch_size:
            return
        batch = random.sample(self.buffer, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones)

        q_values = self.q_net(states).gather(1, actions.unsqueeze(1)).squeeze()
        with torch.no_grad():
            next_q = self.target_net(next_states).max(1)[0]
            targets = rewards + self.gamma * next_q * (1 - dones)

        loss = nn.MSELoss()(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target(self):
        self.target_net.load_state_dict(self.q_net.state_dict())
```

## Training Loop

```python
env = gym.make('CartPole-v1')
agent = DQNAgent(state_dim=4, action_dim=2)

epsilon = 1.0
for ep in range(500):
    state, _ = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = agent.act(state, epsilon)
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        agent.store(state, action, reward, next_state, float(terminated))
        agent.train_step()
        state = next_state
        total_reward += reward

    epsilon = max(0.01, epsilon * 0.995)
    if ep % 10 == 0:
        agent.update_target()
    if ep % 50 == 0:
        print(f"Episode {ep}, Reward: {total_reward:.0f}, ε: {epsilon:.3f}")
```

---

[← Q-Learning](./chapter-03-qlearning.md) | [Next: Policy Gradient →](./chapter-05-policy-gradient.md)
