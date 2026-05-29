# Chapter 3: Q-Learning (Tabular)

[← MDPs](./chapter-02-mdp.md) | [Next: Deep Q-Networks →](./chapter-04-dqn.md)

---

## Q-Learning Algorithm

Model-free, off-policy algorithm. Learns `Q^*(s,a)` without knowing transition probabilities.

**Update rule:**

`Q(s,a) \leftarrow Q(s,a) + \alpha\left[r + \gamma \max_{a'} Q(s',a') - Q(s,a)\right]`

- `\alpha`: Learning rate
- `\gamma`: Discount factor
- The term in brackets is the **TD error**

## Implementation

```python
import numpy as np
import gymnasium as gym

def q_learning(env_name, episodes=10000, alpha=0.1, gamma=0.99,
               epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.995):
    env = gym.make(env_name)
    n_states = env.observation_space.n
    n_actions = env.action_space.n
    Q = np.zeros((n_states, n_actions))

    epsilon = epsilon_start
    rewards_history = []

    for ep in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False

        while not done:
            # Epsilon-greedy action selection
            if np.random.random() < epsilon:
                action = env.action_space.sample()
            else:
                action = np.argmax(Q[state])

            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            # Q-learning update
            td_target = reward + gamma * np.max(Q[next_state]) * (1 - terminated)
            Q[state, action] += alpha * (td_target - Q[state, action])

            state = next_state
            total_reward += reward

        epsilon = max(epsilon_end, epsilon * epsilon_decay)
        rewards_history.append(total_reward)

    env.close()
    return Q, rewards_history

# Train on Taxi environment
Q, rewards = q_learning('Taxi-v3', episodes=5000)
print(f"Last 100 episodes avg reward: {np.mean(rewards[-100:]):.2f}")
```

## Testing the Learned Policy

```python
env = gym.make('Taxi-v3')
total = 0
for _ in range(100):
    state, _ = env.reset()
    done = False
    while not done:
        action = np.argmax(Q[state])
        state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        total += reward

print(f"Average reward (greedy): {total/100:.2f}")
```

## SARSA (On-Policy Alternative)

`Q(s,a) \leftarrow Q(s,a) + \alpha\left[r + \gamma Q(s',a') - Q(s,a)\right]`

Difference: Uses the _actual_ next action `a'` (from policy) instead of `\max_{a'}`.

```python
# SARSA update (inside loop):
next_action = epsilon_greedy(Q[next_state], epsilon)
Q[state, action] += alpha * (
    reward + gamma * Q[next_state, next_action] * (1 - terminated)
    - Q[state, action]
)
```

## Q-Learning vs SARSA

| Aspect      | Q-Learning      | SARSA                |
| ----------- | --------------- | -------------------- |
| Type        | Off-policy      | On-policy            |
| Update uses | max Q(s',a')    | Q(s', actual a')     |
| Behavior    | More aggressive | Safer, avoids cliffs |

---

[← MDPs](./chapter-02-mdp.md) | [Next: Deep Q-Networks →](./chapter-04-dqn.md)
