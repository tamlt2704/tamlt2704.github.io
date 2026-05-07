# Chapter 0: Before You Start

[Chapter 1: The Reward Signal →](chapter-01-reward-signal.md)

---

## The Story

You're a machine learning engineer at **AutoPilot Games**, a small studio that builds AI opponents for strategy and simulation games. The company has shipped three titles with scripted AI — if-else trees hundreds of lines deep, hand-tuned by designers who've since left.

The new game, **GridWorld Tactics**, is a turn-based strategy game on a grid. Units move, attack, capture objectives, and retreat. The scripted AI took 8 months to write for the last game. The designers refuse to do it again.

Your lead, **Jonas**, pulls you into a meeting room:

"We need AI that learns to play. Not scripted. Not hard-coded. Something that figures out tactics on its own — flanking, retreating, resource management. The designers will define the reward structure, but the agent has to discover the strategy. You have 12 weeks."

You nod. You took a machine learning class. You've trained neural networks. How hard can it be?

Over the next 15 chapters, you'll build reinforcement learning agents from scratch. Every algorithm solves a real problem — teaching an agent to navigate, to plan ahead, to balance exploration with exploitation, to handle continuous actions, to learn from sparse rewards. And every naive approach will fail in a way that teaches you why the textbook algorithm exists.

The agent will get stuck in corners. The reward signal will be so sparse the agent learns nothing for 10,000 episodes. The Q-table will explode in size. The policy gradient will have variance so high it unlearns good behavior. The neural network will catastrophically forget everything it learned yesterday.

Each failure teaches you something about how agents learn that no tutorial could.

By the end, you'll have working implementations of bandits, Q-learning, SARSA, deep Q-networks, policy gradients, actor-critic methods, and model-based planning — and you'll understand *when* and *why* to reach for each one.

## How to Read This

Every chapter is the same loop:

1. The current agent fails at something — it's too slow, too random, or too forgetful
2. You diagnose the failure — what's the agent missing?
3. You learn the algorithm that addresses it
4. You implement it, step by step
5. You watch it work — and discover where it breaks next

No algorithm shows up before you need it. You won't hear about deep Q-networks until the Q-table approach collapses under a large state space. You won't touch actor-critic until pure policy gradients are too noisy to converge.

The broken agent comes first. The fix follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | ML Engineer | "I've trained classifiers. RL can't be that different." |
| **Jonas** | Tech Lead | Pragmatic. "Does it beat the scripted AI? Ship it." |
| **Mira** | Game Designer | Defines what "good play" means. Frustrated when agents exploit loopholes. |
| **The Agent** | Your creation | Starts dumb. Gets clever. Sometimes too clever. |
| **The Scripted AI** | The baseline | 8 months of hand-tuned if-else. Predictable but competent. |
| **QA Tanya** | Quality Assurance | "Your agent just stood in a corner for 400 turns." |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | Agent does nothing useful | Reward signals, returns, discounting |
| 2 | Agent always picks the same action | Exploration vs exploitation, epsilon-greedy, bandits |
| 3 | Agent can't plan one step ahead | Markov Decision Processes, states, transitions |
| 4 | Agent needs the perfect model to plan | Dynamic programming, value iteration, policy iteration |
| 5 | Agent doesn't have a model of the world | Monte Carlo methods, learning from episodes |
| 6 | Agent waits until the end to learn | Temporal difference learning, TD(0), bootstrapping |
| 7 | Agent needs to pick actions, not just evaluate states | Q-learning, off-policy learning |
| 8 | Agent forgets when it explores | SARSA, on-policy learning, the cliff walk |
| 9 | State space is too large for a table | Function approximation, feature engineering |
| 10 | Features aren't enough | Deep Q-Networks, experience replay, target networks |
| 11 | Agent can't handle continuous actions | Policy gradients, REINFORCE |
| 12 | Policy gradient variance is too high | Actor-critic, advantage functions, A2C |
| 13 | Agent forgets old skills when learning new ones | PPO, trust regions, clipping |
| 14 | Rewards are too sparse to learn from | Reward shaping, curiosity, hindsight experience replay |
| 15 | Agent needs to plan ahead efficiently | Model-based RL, Dyna, world models |

## Prerequisites

Three things: Python 3, NumPy, and patience for watching agents fail.

### Python 3.10+

All algorithms are implemented in Python with minimal dependencies. The focus is on understanding, not framework magic.

```bash
python3 --version
# Python 3.10.x or higher
```

### Dependencies

```bash
pip install numpy matplotlib gymnasium
```

| Package | Why |
|---|---|
| `numpy` | Matrix math, random sampling |
| `matplotlib` | Plotting learning curves, visualizing policies |
| `gymnasium` | Standard RL environments (GridWorld, CartPole, etc.) |

We'll build core algorithms from scratch. Gymnasium provides environments to test them in — not the algorithms themselves.

### Optional (Later Chapters)

```bash
pip install torch  # Chapters 10-15 (deep RL)
```

PyTorch is used for neural network function approximation starting in Chapter 10. The first 9 chapters are pure NumPy.

### Quick Check

```python
import numpy as np
import gymnasium as gym

env = gym.make("FrozenLake-v1")
print(f"States: {env.observation_space.n}")
print(f"Actions: {env.action_space.n}")
```

If that prints `States: 16` and `Actions: 4`, you're ready.

## The Key Idea

Supervised learning: you have labeled data. The model learns input → output mappings from examples.

Reinforcement learning: you have no labels. The agent takes actions in an environment, receives rewards, and figures out what works through trial and error.

The difference is fundamental:

| | Supervised Learning | Reinforcement Learning |
|---|---|---|
| Feedback | Correct answer for every input | A number (reward) after each action |
| Timing | Immediate | Often delayed — you won't know if a move was good until 50 turns later |
| Data | Fixed dataset | Agent generates its own data by acting |
| Goal | Minimize prediction error | Maximize cumulative reward |
| Exploration | Not needed — data is given | Critical — must try things to discover what works |

In supervised learning, you know the right answer. In RL, you discover it.

That's what makes it hard. That's what makes it interesting.

## Notation

You'll see these symbols throughout:

| Symbol | Meaning |
|---|---|
| s | State (where the agent is) |
| a | Action (what the agent does) |
| r | Reward (what the agent gets) |
| γ (gamma) | Discount factor (how much future rewards matter) |
| π (pi) | Policy (the agent's strategy: state → action) |
| V(s) | Value function (how good is this state?) |
| Q(s, a) | Action-value function (how good is this action in this state?) |
| α (alpha) | Learning rate (how fast the agent updates beliefs) |
| ε (epsilon) | Exploration rate (how often the agent tries random actions) |

Don't memorize these. They'll become second nature as you use them.

## The Environment: GridWorld Tactics (Simplified)

We'll start with tiny grids and build up. Chapter 1 uses a 4×4 grid:

```
┌───┬───┬───┬───┐
│ . │ . │ . │ G │
├───┼───┼───┼───┤
│ . │ X │ . │ . │
├───┼───┼───┼───┤
│ . │ . │ . │ X │
├───┼───┼───┼───┤
│ A │ . │ . │ . │
└───┴───┴───┴───┘

A = Agent (start)
G = Goal (+1 reward)
X = Trap (-1 reward)
. = Empty (0 reward)
```

The agent can move up, down, left, right. It wants to reach G without hitting X. Simple enough to debug by hand. Complex enough to demonstrate every core concept.

By Chapter 15, the agent will handle multi-unit tactics on a 20×20 grid with fog of war, resource nodes, and opponent agents. But we start here.

Let's give the agent its first reward.

---

[Chapter 1: The Reward Signal →](chapter-01-reward-signal.md)
