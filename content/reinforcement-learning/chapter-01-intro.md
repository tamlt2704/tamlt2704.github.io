# Chapter 1: What is Reinforcement Learning?

[← Overview](./chapter-00-overview.md) | [Next: MDPs →](./chapter-02-mdp.md)

---

## The RL Framework

An **agent** interacts with an **environment** by taking **actions** and receiving **rewards**.

```
Agent → Action → Environment → (Next State, Reward) → Agent → ...
```

**Goal:** Learn a policy `\pi(a|s)` that maximizes cumulative reward.

## Key Concepts

- **State** (`s`): Current situation
- **Action** (`a`): What the agent does
- **Reward** (`r`): Immediate feedback signal
- **Episode**: Sequence from start to terminal state
- **Return**: `G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k+1}` (discounted cumulative reward)
- **Discount factor** (`\gamma \in [0,1]`): How much to value future rewards

## RL vs Supervised Learning

| Aspect   | Supervised     | RL                     |
| -------- | -------------- | ---------------------- |
| Feedback | Correct labels | Scalar reward          |
| Data     | i.i.d. dataset | Sequential, correlated |
| Goal     | Minimize loss  | Maximize return        |

## First Gymnasium Environment

```python
import gymnasium as gym

env = gym.make('CartPole-v1')
state, info = env.reset(seed=42)

total_reward = 0
done = False

while not done:
    action = env.action_space.sample()  # Random policy
    state, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    done = terminated or truncated

print(f"Random agent reward: {total_reward}")
env.close()
```

## Understanding CartPole

- **State**: [cart_position, cart_velocity, pole_angle, pole_angular_velocity]
- **Actions**: 0 (push left), 1 (push right)
- **Reward**: +1 for each timestep the pole stays upright
- **Termination**: Pole angle > 12° or cart leaves bounds

## Exploration vs Exploitation

The fundamental RL dilemma:

- **Exploit**: Use current best knowledge
- **Explore**: Try new actions to discover better strategies

**ε-greedy**: With probability ε take random action, otherwise take best known action.

```python
import numpy as np

def epsilon_greedy(q_values, epsilon=0.1):
    if np.random.random() < epsilon:
        return np.random.randint(len(q_values))
    return np.argmax(q_values)
```

---

[← Overview](./chapter-00-overview.md) | [Next: MDPs →](./chapter-02-mdp.md)
