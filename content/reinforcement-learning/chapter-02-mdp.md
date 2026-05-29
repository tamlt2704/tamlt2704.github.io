# Chapter 2: Markov Decision Processes

[← What is RL](./chapter-01-intro.md) | [Next: Q-Learning →](./chapter-03-qlearning.md)

---

## MDP Definition

An MDP is a tuple `(S, A, P, R, \gamma)`:

- `S`: Set of states
- `A`: Set of actions
- `P(s'|s,a)`: Transition probability
- `R(s,a,s')`: Reward function
- `\gamma`: Discount factor

**Markov property**: Future depends only on current state, not history.

## Value Functions

**State-value function** (how good is state `s` under policy `\pi`):

`V^\pi(s) = \mathbb{E}_\pi\left[\sum_{k=0}^{\infty}\gamma^k r_{t+k+1} \mid s_t = s\right]`

**Action-value function** (how good is action `a` in state `s`):

`Q^\pi(s,a) = \mathbb{E}_\pi\left[\sum_{k=0}^{\infty}\gamma^k r_{t+k+1} \mid s_t = s, a_t = a\right]`

## Bellman Equations

The recursive relationship that makes RL tractable:

`V^\pi(s) = \sum_a \pi(a|s) \sum_{s'} P(s'|s,a)\left[R(s,a,s') + \gamma V^\pi(s')\right]`

**Optimal Bellman equation:**

`V^*(s) = \max_a \sum_{s'} P(s'|s,a)\left[R(s,a,s') + \gamma V^*(s')\right]`

## Value Iteration (Dynamic Programming)

```python
import numpy as np

def value_iteration(env_P, n_states, n_actions, gamma=0.99, theta=1e-8):
    """
    env_P: dict where env_P[s][a] = [(prob, next_state, reward, done), ...]
    """
    V = np.zeros(n_states)

    while True:
        delta = 0
        for s in range(n_states):
            v = V[s]
            q_values = np.zeros(n_actions)
            for a in range(n_actions):
                for prob, s_next, reward, done in env_P[s][a]:
                    q_values[a] += prob * (reward + gamma * V[s_next] * (1 - done))
            V[s] = np.max(q_values)
            delta = max(delta, abs(v - V[s]))
        if delta < theta:
            break

    # Extract policy
    policy = np.zeros(n_states, dtype=int)
    for s in range(n_states):
        q_values = np.zeros(n_actions)
        for a in range(n_actions):
            for prob, s_next, reward, done in env_P[s][a]:
                q_values[a] += prob * (reward + gamma * V[s_next] * (1 - done))
        policy[s] = np.argmax(q_values)

    return V, policy
```

## Example: FrozenLake

```python
import gymnasium as gym

env = gym.make('FrozenLake-v1', is_slippery=True)
V, policy = value_iteration(env.unwrapped.P, 16, 4)

# Test learned policy
wins = 0
for _ in range(1000):
    state, _ = env.reset()
    done = False
    while not done:
        action = policy[state]
        state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
    wins += reward

print(f"Win rate: {wins/1000:.2%}")
```

---

[← What is RL](./chapter-01-intro.md) | [Next: Q-Learning →](./chapter-03-qlearning.md)
