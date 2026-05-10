# Chapter 1: The Prisoner's Dilemma — Why Rational Players Lose

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Repeated Games →](chapter-02-repeated-games.md)

---

## The Problem

Friday afternoon. A production outage took down Nexus Labs' API for 2 hours. The post-mortem reveals two contributing factors: a deployment by **Alex** (backend) that didn't handle a new edge case, and a config change by **Jordan** (infra) that exposed the edge case.

Mara wants accountability. She meets with each engineer separately:

"Tell me what happened. If you take responsibility, I'll note it as a learning moment. If the other person was primarily at fault and you can explain why, I'll focus the follow-up on them."

Alex thinks: "If I blame Jordan and Jordan stays quiet, I look good. If we both stay quiet, it's a shared learning. If I stay quiet and Jordan blames me, I'm the scapegoat."

Jordan thinks the exact same thing.

This is the **Prisoner's Dilemma** — the most famous game in all of game theory.

## The Payoff Matrix

Let's formalize it. Each player has two strategies: **Cooperate** (stay quiet, share responsibility) or **Defect** (blame the other person).

```python
import numpy as np

# Payoffs: (Alex's outcome, Jordan's outcome)
# Scale: 3 = best, 0 = worst

#                    Jordan
#                 Cooperate    Defect
# Alex Cooperate   (3, 3)      (0, 5)
# Alex Defect      (5, 0)      (1, 1)

alex_payoffs = np.array([
    [3, 0],   # Alex cooperates: gets 3 if Jordan cooperates, 0 if Jordan defects
    [5, 1],   # Alex defects: gets 5 if Jordan cooperates, 1 if Jordan defects
])

jordan_payoffs = np.array([
    [3, 5],   # Jordan cooperates: gets 3 if Alex cooperates, 5 if Alex defects... wait
    [0, 1],
])

# Actually, Jordan's payoffs mirror Alex's (symmetric game):
jordan_payoffs = alex_payoffs.T
```

Reading the matrix:
- **(Cooperate, Cooperate) = (3, 3)**: Both share responsibility. Mild consequence. Best collective outcome.
- **(Defect, Cooperate) = (5, 0)**: Defector looks great, cooperator is scapegoated.
- **(Cooperate, Defect) = (0, 5)**: Cooperator is scapegoated, defector looks great.
- **(Defect, Defect) = (1, 1)**: Both blame each other. Mara is annoyed at both. Worst collective outcome.

## Dominant Strategy

A strategy is **dominant** if it's the best choice regardless of what the other player does.

```python
def find_dominant_strategy(payoff_matrix):
    """Check if a player has a dominant strategy."""
    n_strategies = payoff_matrix.shape[0]
    for i in range(n_strategies):
        dominates_all = True
        for j in range(n_strategies):
            if i == j:
                continue
            # Strategy i dominates j if it's better in EVERY column
            if not all(payoff_matrix[i] >= payoff_matrix[j]):
                dominates_all = False
            # Must be strictly better in at least one column
            if not any(payoff_matrix[i] > payoff_matrix[j]):
                dominates_all = False
        if dominates_all:
            return i
    return None

dominant = find_dominant_strategy(alex_payoffs)
print(f"Alex's dominant strategy: {'Defect' if dominant == 1 else 'Cooperate' if dominant == 0 else 'None'}")
```

```
Alex's dominant strategy: Defect
```

For Alex:
- If Jordan cooperates: Defect (5) > Cooperate (3)
- If Jordan defects: Defect (1) > Cooperate (0)

Defect is better **no matter what Jordan does**. The same logic applies to Jordan. Both have a dominant strategy to defect.

## Nash Equilibrium

A **Nash Equilibrium** is a strategy profile where no player can improve their payoff by unilaterally changing their strategy.

```python
import nashpy as nash

game = nash.Game(alex_payoffs, jordan_payoffs)
equilibria = list(game.support_enumeration())

for eq in equilibria:
    alex_strategy, jordan_strategy = eq
    print(f"Alex: {alex_strategy}, Jordan: {jordan_strategy}")
    # Compute payoffs at equilibrium
    alex_payoff = alex_strategy @ alex_payoffs @ jordan_strategy
    jordan_payoff = alex_strategy @ jordan_payoffs @ jordan_strategy
    print(f"Payoffs: Alex={alex_payoff:.1f}, Jordan={jordan_payoff:.1f}")
```

```
Alex: [0. 1.], Jordan: [0. 1.]
Payoffs: Alex=1.0, Jordan=1.0
```

The Nash Equilibrium is (Defect, Defect) with payoffs (1, 1). Both players get their second-worst outcome.

## The Tragedy

The equilibrium is (Defect, Defect) = (1, 1). But (Cooperate, Cooperate) = (3, 3) is better for **both** players. Rational individual behavior leads to a collectively worse outcome.

This is the core insight of the Prisoner's Dilemma: **individual rationality ≠ collective rationality**.

```python
import matplotlib.pyplot as plt

# Visualize the dilemma
outcomes = {
    'Both Cooperate': (3, 3),
    'Alex Defects': (5, 0),
    'Jordan Defects': (0, 5),
    'Both Defect': (1, 1),
}

fig, ax = plt.subplots(figsize=(8, 6))
for label, (x, y) in outcomes.items():
    ax.scatter(x, y, s=200, zorder=5)
    ax.annotate(label, (x, y), textcoords="offset points", xytext=(10, 10))

ax.set_xlabel("Alex's Payoff")
ax.set_ylabel("Jordan's Payoff")
ax.set_title("Prisoner's Dilemma: Nash Equilibrium vs. Pareto Optimal")
ax.axhline(y=1, color='red', linestyle='--', alpha=0.3, label='NE payoff')
ax.axvline(x=1, color='red', linestyle='--', alpha=0.3)
ax.legend()
plt.show()
```

## Real-World Prisoner's Dilemmas

The structure appears everywhere:

### Price Wars

```
                    RivalCo
                 High Price    Low Price
Nexus High Price   (10, 10)     (2, 12)
Nexus Low Price    (12, 2)      (5, 5)
```

Both cutting prices is the equilibrium. Both keeping prices high is better for both. But each firm individually benefits from undercutting.

### Open Source

```
                    RivalCo
                 Keep Closed    Open Source
Nexus Keep Closed   (8, 8)       (3, 10)
Nexus Open Source   (10, 3)      (5, 5)
```

Open-sourcing attracts developers (short-term gain) but commoditizes the market (long-term loss for both).

### Arms Races (Feature Bloat)

```
                    RivalCo
                 Focus         Feature Bloat
Nexus Focus        (8, 8)       (4, 9)
Nexus Feature Bloat (9, 4)      (5, 5)
```

Both adding features nobody needs because the other might.

## Implementing a General Payoff Matrix Solver

```python
def analyze_2x2_game(A, B, row_labels=None, col_labels=None):
    """Analyze a 2x2 game completely."""
    if row_labels is None:
        row_labels = ["Strategy 0", "Strategy 1"]
    if col_labels is None:
        col_labels = ["Strategy 0", "Strategy 1"]

    print("=== Game Analysis ===\n")

    # Print payoff matrix
    print(f"{'':>15} {col_labels[0]:>12} {col_labels[1]:>12}")
    for i, label in enumerate(row_labels):
        row = f"{label:>15}"
        for j in range(2):
            row += f"  ({A[i,j]:>2}, {B[i,j]:>2})"
        print(row)

    # Check for dominant strategies
    print("\n--- Dominant Strategies ---")
    for player, matrix, name in [(0, A, "Row"), (1, B.T, "Column")]:
        dom = find_dominant_strategy(matrix)
        if dom is not None:
            labels = row_labels if player == 0 else col_labels
            print(f"  {name} player: {labels[dom]} is dominant")
        else:
            print(f"  {name} player: no dominant strategy")

    # Find Nash Equilibria
    print("\n--- Nash Equilibria ---")
    game = nash.Game(A, B)
    for eq in game.support_enumeration():
        row_strat, col_strat = eq
        payoff_row = row_strat @ A @ col_strat
        payoff_col = row_strat @ B @ col_strat
        print(f"  Row: {row_strat}, Col: {col_strat}")
        print(f"  Payoffs: ({payoff_row:.2f}, {payoff_col:.2f})")

    # Check Pareto optimality
    print("\n--- Pareto Analysis ---")
    outcomes = [(A[i,j], B[i,j], row_labels[i], col_labels[j])
                for i in range(2) for j in range(2)]
    for a_pay, b_pay, r, c in outcomes:
        dominated = any(
            (a2 >= a_pay and b2 >= b_pay and (a2 > a_pay or b2 > b_pay))
            for a2, b2, _, _ in outcomes
        )
        status = "Pareto dominated" if dominated else "Pareto optimal"
        print(f"  ({r}, {c}) = ({a_pay}, {b_pay}) — {status}")


# Analyze the Prisoner's Dilemma
analyze_2x2_game(
    alex_payoffs, jordan_payoffs,
    row_labels=["Cooperate", "Defect"],
    col_labels=["Cooperate", "Defect"]
)
```

```
=== Game Analysis ===

                   Cooperate      Defect
      Cooperate  ( 3,  3)  ( 0,  5)
         Defect  ( 5,  0)  ( 1,  1)

--- Dominant Strategies ---
  Row player: Defect is dominant
  Column player: Defect is dominant

--- Nash Equilibria ---
  Row: [0. 1.], Col: [0. 1.]
  Payoffs: (1.00, 1.00)

--- Pareto Analysis ---
  (Cooperate, Cooperate) = (3, 3) — Pareto optimal
  (Cooperate, Defect) = (0, 5) — Pareto optimal
  (Defect, Cooperate) = (5, 0) — Pareto optimal
  (Defect, Defect) = (1, 1) — Pareto dominated
```

The Nash Equilibrium (Defect, Defect) is the only Pareto-dominated outcome. The one thing rational players converge on is the one outcome that's unambiguously bad.

## Can We Escape?

The one-shot Prisoner's Dilemma has no escape. Defect is dominant. Period.

But real life isn't one-shot. Alex and Jordan work together every sprint. They'll face this situation again. And again. And again.

When the game repeats, cooperation becomes possible — not through altruism, but through **strategy**. "I'll cooperate today because if I defect, you'll defect tomorrow, and we'll both be stuck at (1, 1) forever."

That's Chapter 2.

## What You Learned

- **Payoff matrix** — represents all outcomes for all strategy combinations
- **Dominant strategy** — best choice regardless of opponent's action
- **Nash Equilibrium** — no player can unilaterally improve by switching
- **Pareto optimality** — no outcome makes everyone better off
- **The dilemma** — individual rationality leads to collective irrationality
- **Ubiquity** — price wars, arms races, open-source decisions are all PDs

Alex and Jordan both defected. Both got written up. Both are resentful. Next sprint, the same dynamic will play out — unless someone changes the game.

Mara: "This keeps happening. Every post-mortem turns into a blame game. How do I fix the incentives?"

You: "If it only happens once, you can't. But if it happens repeatedly..."

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Repeated Games →](chapter-02-repeated-games.md)
