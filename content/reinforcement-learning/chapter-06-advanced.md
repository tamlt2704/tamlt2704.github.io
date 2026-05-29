# Chapter 6: Actor-Critic & Real Applications

[← Policy Gradient](./chapter-05-policy-gradient.md) | [Back to Overview →](./chapter-00-overview.md)

---

## Actor-Critic

Combines policy gradient (actor) with value function (critic) for lower variance.

- **Actor**: Policy `\pi_\theta(a|s)` — decides actions
- **Critic**: Value `V_\phi(s)` — evaluates states

**Advantage:** `A(s,a) = r + \gamma V(s') - V(s)` (TD error as advantage estimate)

## A2C Implementation

```python
import torch
import torch.nn as nn
import numpy as np
import gymnasium as gym

class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.shared = nn.Sequential(nn.Linear(state_dim, 128), nn.ReLU())
        self.actor = nn.Sequential(nn.Linear(128, action_dim), nn.Softmax(dim=-1))
        self.critic = nn.Linear(128, 1)

    def forward(self, x):
        features = self.shared(x)
        return self.actor(features), self.critic(features)

class A2CAgent:
    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99):
        self.gamma = gamma
        self.model = ActorCritic(state_dim, action_dim)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

    def act(self, state):
        probs, value = self.model(torch.FloatTensor(state))
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        return action.item(), dist.log_prob(action), value

    def update(self, log_probs, values, rewards, dones):
        returns = []
        G = 0
        for r, d in zip(reversed(rewards), reversed(dones)):
            G = r + self.gamma * G * (1 - d)
            returns.insert(0, G)
        returns = torch.FloatTensor(returns)

        values = torch.cat(values).squeeze()
        log_probs = torch.stack(log_probs)
        advantage = returns - values.detach()

        actor_loss = -(log_probs * advantage).mean()
        critic_loss = nn.MSELoss()(values, returns)
        loss = actor_loss + 0.5 * critic_loss

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
```

## Training A2C

```python
env = gym.make('CartPole-v1')
agent = A2CAgent(state_dim=4, action_dim=2)

for ep in range(1000):
    state, _ = env.reset()
    log_probs, values, rewards, dones = [], [], [], []
    done = False

    while not done:
        action, log_prob, value = agent.act(state)
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        log_probs.append(log_prob)
        values.append(value)
        rewards.append(reward)
        dones.append(float(terminated))
        state = next_state

    agent.update(log_probs, values, rewards, dones)
    if ep % 100 == 0:
        print(f"Episode {ep}, Reward: {sum(rewards):.0f}")
```

## PPO (Proximal Policy Optimization)

PPO clips the policy ratio to prevent destructive updates:

`L^{CLIP} = \mathbb{E}\left[\min\left(r_t(\theta)A_t,\; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)A_t\right)\right]`

Where `r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}`

PPO is the default choice for most modern RL applications due to stability and performance.

## Real-World Applications

| Domain             | Example                  | Algorithm           |
| ------------------ | ------------------------ | ------------------- |
| Games              | AlphaGo, Atari, Dota 2   | MCTS + RL, DQN, PPO |
| Robotics           | Manipulation, locomotion | PPO, SAC            |
| NLP                | RLHF (ChatGPT alignment) | PPO                 |
| Finance            | Portfolio optimization   | A2C, DQN            |
| Autonomous driving | Lane keeping, decisions  | PPO, model-based    |

## Algorithm Selection Guide

| Scenario                            | Recommended      |
| ----------------------------------- | ---------------- |
| Discrete actions, small state space | Q-Learning       |
| Discrete actions, large state space | DQN              |
| Continuous actions                  | PPO, SAC         |
| Sample efficiency matters           | SAC, model-based |
| Stability matters                   | PPO              |

## Next Steps

- Implement PPO with GAE (Generalized Advantage Estimation)
- Try Stable-Baselines3: `pip install stable-baselines3`
- Explore multi-agent RL and hierarchical RL

```python
# Quick start with Stable-Baselines3
from stable_baselines3 import PPO

model = PPO('MlpPolicy', 'CartPole-v1', verbose=1)
model.learn(total_timesteps=50000)
```

---

[← Policy Gradient](./chapter-05-policy-gradient.md) | [Back to Overview →](./chapter-00-overview.md)
