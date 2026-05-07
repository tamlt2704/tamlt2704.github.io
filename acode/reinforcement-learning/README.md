# Reinforcement Learning

A 15-chapter course that builds RL agents from scratch, progressing from random agents to model-based planning. Every algorithm is motivated by a failure of the previous approach.

## Story

You're an ML engineer at AutoPilot Games, tasked with building AI that learns to play a turn-based strategy game. The scripted AI took 8 months to write. You have 12 weeks to build something that learns on its own.

## Chapters

| Ch | Title | Core Concept |
|---|---|---|
| 0 | [Overview](chapter-00-overview.md) | Setup, prerequisites, roadmap |
| 1 | [The Reward Signal](chapter-01-reward-signal.md) | Rewards, returns, discounting |
| 2 | [Exploration](chapter-02-exploration.md) | ε-greedy, UCB, bandits |
| 3 | [Markov Decision Processes](chapter-03-mdp.md) | States, transitions, Bellman equation |
| 4 | [Dynamic Programming](chapter-04-dynamic-programming.md) | Policy/value iteration |
| 5 | [Monte Carlo Methods](chapter-05-monte-carlo.md) | Learning from complete episodes |
| 6 | [Temporal Difference Learning](chapter-06-td-learning.md) | TD(0), bootstrapping, eligibility traces |
| 7 | [Q-Learning](chapter-07-q-learning.md) | Off-policy TD control |
| 8 | [SARSA](chapter-08-sarsa.md) | On-policy TD control, cliff walk |
| 9 | [Function Approximation](chapter-09-function-approximation.md) | Linear Q, tile coding, deadly triad |
| 10 | [Deep Q-Networks](chapter-10-dqn.md) | Experience replay, target networks |
| 11 | [Policy Gradients](chapter-11-policy-gradients.md) | REINFORCE, continuous actions |
| 12 | [Actor-Critic](chapter-12-actor-critic.md) | A2C, advantage functions |
| 13 | [PPO](chapter-13-ppo.md) | Clipped objectives, trust regions |
| 14 | [Reward Shaping](chapter-14-reward-shaping.md) | PBRS, curiosity, HER |
| 15 | [Model-Based RL](chapter-15-model-based.md) | Dyna, world models, MBPO, MCTS |

## Prerequisites

- Python 3.10+
- NumPy, Matplotlib, Gymnasium
- PyTorch (Chapters 10-15)

```bash
pip install numpy matplotlib gymnasium torch
```

## Progression

- **Chapters 1-4**: Foundations (rewards, MDPs, dynamic programming)
- **Chapters 5-8**: Tabular methods (MC, TD, Q-learning, SARSA)
- **Chapters 9-10**: Function approximation (linear → deep)
- **Chapters 11-13**: Policy optimization (REINFORCE → A2C → PPO)
- **Chapters 14-15**: Advanced topics (reward shaping, model-based)
