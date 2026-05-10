# Chapter 0: Before You Start

[Chapter 1: The Prisoner's Dilemma →](chapter-01-prisoners-dilemma.md)

---

## The Story

This is a series about game theory — but not the kind where you memorize "Nash equilibrium is where no player can unilaterally improve" and move on.

You're a strategy analyst at **Nexus Labs**, a mid-size tech company that builds developer tools. The company is profitable but stuck — every strategic decision feels like a coin flip. Should you undercut the competitor's pricing? Should you open-source the core product? Should you hire that engineer the competitor also wants? Should you launch the feature now or wait for them to move first?

Your CEO, **Mara**, is frustrated:

"We keep making decisions that seem smart in isolation but blow up in context. We cut prices, they cut prices, nobody wins. We launched early, they copied us, and now we're both worse off. I need someone who can think about strategy *systematically* — not just gut feelings and spreadsheets."

You nod. You took an economics class. You've heard of game theory. How hard can it be?

Over the next 15 chapters, you'll model Nexus Labs' strategic decisions as formal games. Every model you build solves a real problem — pricing wars, hiring battles, platform adoption, team coordination. And every naive strategy will fail in a way that teaches you why game theory exists.

The price war will spiral to zero. The threat will be called as a bluff. The auction will trigger the winner's curse. The bonus system will be gamed. The voting system will produce a paradox.

Each failure teaches you something about strategic interaction that no MBA case study could.

By the end, you'll have working implementations of Nash equilibria, auction mechanisms, bargaining models, signaling games, evolutionary dynamics, and cooperative solution concepts — and you'll understand *when* and *why* to reach for each one.

## How to Read This

Every chapter is the same loop:

1. A strategic decision goes wrong — someone made a "rational" choice that backfired
2. You identify the game — who are the players? What are their options? What do they want?
3. You model it formally — payoff matrices, game trees, or strategy spaces
4. You find the equilibrium — what rational players would actually do
5. You discover the insight — and often, why the equilibrium is bad for everyone

No concept shows up before you need it. You won't hear about mixed strategies until a competitor perfectly counters every move you make. You won't touch mechanism design until the bonus system gets gamed into absurdity.

The bad decision comes first. The theory follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Strategy Analyst | "There must be a model for this." |
| **Mara** | CEO | Decisive. "Give me the optimal play, not a lecture." |
| **Kai** | Head of Product | Wants to launch everything yesterday. |
| **Priya** | Head of Engineering | "If we open-source it, they'll just fork us." |
| **RivalCo** | The Competitor | Rational, aggressive, well-funded. |
| **The Board** | Investors | "Why did we lose that deal?" |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | Two devs blame each other for a bug | Dominant strategies, Nash equilibrium, payoff matrices |
| 2 | The blame game repeats every sprint | Repeated games, tit-for-tat, cooperation emergence |
| 3 | Competitor always counters our moves | Mixed strategies, randomization, indifference |
| 4 | Should we launch first or wait? | Sequential games, backward induction, game trees |
| 5 | Our threats aren't working | Credible commitment, strategic moves, burning bridges |
| 6 | We're overpaying for ad slots | Auction types, bidding strategies, winner's curse |
| 7 | Engineers game the bonus system | Mechanism design, incentive compatibility |
| 8 | Salary negotiation leaves money on the table | Bargaining theory, Nash solution, BATNA |
| 9 | How to prove quality without revealing secrets | Signaling, screening, separating equilibria |
| 10 | Why do toxic strategies persist? | Evolutionary stability, replicator dynamics |
| 11 | Team can't agree on a framework | Voting paradoxes, Arrow's theorem, social choice |
| 12 | How to split revenue fairly among teams | Shapley value, core, cooperative games |
| 13 | We don't know what the competitor knows | Bayesian games, incomplete information |
| 14 | Nobody adopts our platform first | Coordination, network effects, tipping points |
| 15 | Build the best strategy and compete | Axelrod's tournament, strategy evolution |

## Prerequisites

Two things: Python 3 and a willingness to think about other people's incentives.

### Python 3.10+

```bash
python3 --version
# Python 3.10.x or higher
```

### Dependencies

```bash
pip install numpy matplotlib nashpy
```

| Package | Why |
|---|---|
| `numpy` | Matrix operations, linear algebra for equilibria |
| `matplotlib` | Visualizing payoffs, dynamics, game trees |
| `nashpy` | Computing Nash equilibria for bimatrix games |

We'll build core concepts from scratch. `nashpy` provides verification — you'll implement the algorithms yourself first, then check against the library.

### Quick Check

```python
import nashpy as nash
import numpy as np

# A simple 2x2 game
A = np.array([[3, 0], [5, 1]])  # Row player payoffs
B = np.array([[3, 5], [0, 1]])  # Column player payoffs

game = nash.Game(A, B)
equilibria = list(game.support_enumeration())
print(f"Nash equilibria: {len(equilibria)}")
print(f"First equilibrium: {equilibria[0]}")
```

If that prints equilibria without errors, you're ready.

### Optional: Jupyter

Game theory is visual — payoff matrices, game trees, strategy evolution plots. Notebooks let you see results inline:

```bash
pip install jupyterlab
```

## The Key Idea

A **game** is any situation where:
1. Multiple **players** make decisions
2. Each player's outcome depends on **everyone's** choices (not just their own)
3. Players are **rational** — they try to maximize their own payoff

That's it. Pricing decisions, hiring, negotiations, elections, evolution — all games.

The fundamental question: **What will rational players do?**

Not "what should they do" (that's ethics). Not "what would be best for everyone" (that's social welfare). What *will* they do, given that each player is trying to maximize their own outcome while knowing the others are doing the same?

The answer is often surprising. Rational individual behavior frequently leads to collectively terrible outcomes. That's the central tension of game theory — and the reason it's useful.

## Notation

| Symbol | Meaning |
|---|---|
| N | Set of players {1, 2, ..., n} |
| Sᵢ | Strategy set for player i |
| sᵢ | A specific strategy chosen by player i |
| s₋ᵢ | Strategies chosen by everyone except player i |
| uᵢ(s) | Player i's payoff given strategy profile s |
| σᵢ | Mixed strategy (probability distribution over Sᵢ) |
| BR(s₋ᵢ) | Best response to others' strategies |
| NE | Nash Equilibrium |

Don't memorize these. They'll become natural as you use them.

## The Mental Model

Think of game theory as a lens:

1. **Identify the game**: Who are the players? What can each one do? What do they want?
2. **Model the payoffs**: If player A does X and player B does Y, what happens to each?
3. **Find the equilibrium**: What strategy profile is self-enforcing? (No one wants to deviate.)
4. **Evaluate the outcome**: Is the equilibrium good? Bad? Can we change the game?

Step 4 is where it gets interesting. Often the equilibrium is terrible for everyone (price wars, arms races, tragedy of the commons). The insight isn't just "this is what will happen" — it's "here's how to change the rules so something better happens."

That's mechanism design (Chapter 7). But first, you need to understand why rational players end up in bad equilibria.

Let's watch two developers destroy each other's careers over a bug.

---

[Chapter 1: The Prisoner's Dilemma →](chapter-01-prisoners-dilemma.md)
