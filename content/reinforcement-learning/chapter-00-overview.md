# Reinforcement Learning

## Course Overview

Learn RL from tabular methods to deep policy optimization. Each chapter includes working Python code using the Gymnasium library.

## Chapters

| #   | Topic                                                   | Key Concepts                                    |
| --- | ------------------------------------------------------- | ----------------------------------------------- |
| 0   | [Overview](./chapter-00-overview.md)                    | Course structure, setup                         |
| 1   | [What is RL](./chapter-01-intro.md)                     | Agent, environment, reward, episodes            |
| 2   | [Markov Decision Processes](./chapter-02-mdp.md)        | States, actions, transitions, Bellman equation  |
| 3   | [Q-Learning](./chapter-03-qlearning.md)                 | Tabular Q-learning, exploration vs exploitation |
| 4   | [Deep Q-Networks](./chapter-04-dqn.md)                  | Neural network Q-function, experience replay    |
| 5   | [Policy Gradient](./chapter-05-policy-gradient.md)      | REINFORCE, likelihood ratio                     |
| 6   | [Actor-Critic & Applications](./chapter-06-advanced.md) | A2C, PPO, real-world uses                       |

## Setup

```bash
pip install gymnasium numpy torch matplotlib
pip install gymnasium[classic_control]  # CartPole, MountainCar
pip install gymnasium[atari]            # Optional: Atari games
```

## Prerequisites

- Python 3.9+
- Basic probability (expectations, distributions)
- Neural networks basics (for chapters 4–6)

---

[Next: What is RL →](./chapter-01-intro.md)
