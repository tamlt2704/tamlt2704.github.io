# Chapter 5: Policy Gradient (REINFORCE)

[← DQN](./chapter-04-dqn.md) | [Next: Actor-Critic & Applications →](./chapter-06-advanced.md)

---

## Why Policy Gradient?

Instead of learning Q-values, directly optimize the policy `\pi_\theta(a|s)`.

**Advantages over DQN:**

- Naturally handles continuous action spaces
- Can learn stochastic policies
- More stable convergence in some settings

## Mathematical Foundation

**Objective:** Maximize expected return:

`J(\theta) = \mathbb{E}_{\pi_\theta}\left[\sum_t \gamma^t r_t\right]`

**Policy Gradient Theorem:**

`\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\left[\sum_t \nabla_\theta \log\pi_\theta(a_t|s_t) \cdot G_t\right]`

Where `G_t = \sum_{k=t}^{T} \gamma^{k-t} r_k` is the return from timestep `t`.

## REINFORCE Implementation

```python
import torch
import torch.nn as nn
import numpy as np
import gymnasium as gym

class PolicyNetwork(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128), nn.ReLU(),
            nn.Linear(128, action_dim), nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.net(x)

class REINFORCE:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99):
        self.gamma = gamma
        self.policy = PolicyNetwork(state_dim, action_dim)
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=lr)

    def act(self, state):
        probs = self.policy(torch.FloatTensor(state))
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        return action.item(), dist.log_prob(action)

    def update(self, log_probs, rewards):
        # Compute discounted returns
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)
        returns = torch.FloatTensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)  # baseline

        # Policy gradient loss
        loss = 0
        for log_prob, G in zip(log_probs, returns):
            loss -= log_prob * G

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
```

## Training

```python
env = gym.make('CartPole-v1')
agent = REINFORCE(state_dim=4, action_dim=2)

for ep in range(1000):
    state, _ = env.reset()
    log_probs, rewards = [], []
    done = False

    while not done:
        action, log_prob = agent.act(state)
        state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        log_probs.append(log_prob)
        rewards.append(reward)

    agent.update(log_probs, rewards)

    if ep % 100 == 0:
        print(f"Episode {ep}, Reward: {sum(rewards):.0f}")
```

## Variance Reduction

REINFORCE has high variance. Common fixes:

- **Baseline subtraction**: `G_t - b(s_t)` where `b` is a learned value function
- **Reward normalization**: Zero-mean, unit-variance returns
- **Advantage**: `A(s,a) = Q(s,a) - V(s)` → leads to Actor-Critic

---

[← DQN](./chapter-04-dqn.md) | [Next: Actor-Critic & Applications →](./chapter-06-advanced.md)
