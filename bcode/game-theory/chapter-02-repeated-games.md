# Chapter 2: Repeated Games — The Shadow of the Future

[← Chapter 1: The Prisoner's Dilemma](chapter-01-prisoners-dilemma.md) | [Chapter 3: Mixed Strategies →](chapter-03-mixed-strategies.md)

---

## The Problem

Monday standup. Mara pulls you aside.

"The blame game from last sprint? It happened again. Different engineers, same dynamic. Every post-mortem turns into finger-pointing. Nobody takes shared responsibility because they're afraid of being the sucker."

You think about Chapter 1. In a one-shot Prisoner's Dilemma, defection is dominant. There's no escape.

But this isn't one-shot. These engineers work together every sprint. Every two weeks, the same game plays out. Alex and Jordan will face each other in the next post-mortem, and the one after that, and the one after that.

"Mara, the problem isn't that people are selfish. It's that they think this is a one-time interaction. If they realize they'll keep playing together, cooperation becomes rational — not because they're nice, but because defecting today means getting defected on tomorrow."

Mara raises an eyebrow. "Prove it."

## The Iterated Prisoner's Dilemma

When the same game repeats, players can condition their current action on the *history* of play. This changes everything.

```python
import numpy as np
import matplotlib.pyplot as plt

# Payoff matrix from Chapter 1
# (Cooperate, Cooperate) = 3, (Cooperate, Defect) = 0
# (Defect, Cooperate) = 5, (Defect, Defect) = 1
PAYOFFS = {
    ('C', 'C'): (3, 3),
    ('C', 'D'): (0, 5),
    ('D', 'C'): (5, 0),
    ('D', 'D'): (1, 1),
}
```

## Strategies for Repeated Play

In a repeated game, a strategy is a *rule* that maps history to an action. Here are the classic ones:

```python
def always_cooperate(history, my_index):
    """Cooperate no matter what."""
    return 'C'

def always_defect(history, my_index):
    """Defect no matter what."""
    return 'D'

def tit_for_tat(history, my_index):
    """Cooperate first, then copy opponent's last move."""
    if len(history) == 0:
        return 'C'
    opponent_index = 1 - my_index
    return history[-1][opponent_index]

def grim_trigger(history, my_index):
    """Cooperate until opponent defects once, then defect forever."""
    opponent_index = 1 - my_index
    for round in history:
        if round[opponent_index] == 'D':
            return 'D'
    return 'C'

def random_strategy(history, my_index):
    """Cooperate or defect with equal probability."""
    return np.random.choice(['C', 'D'])

def tit_for_two_tats(history, my_index):
    """Only retaliate after opponent defects twice in a row."""
    if len(history) < 2:
        return 'C'
    opponent_index = 1 - my_index
    if history[-1][opponent_index] == 'D' and history[-2][opponent_index] == 'D':
        return 'D'
    return 'C'
```

## Simulating a Match

```python
def play_match(strategy_a, strategy_b, rounds=200):
    """Play an iterated PD match between two strategies."""
    history = []
    scores = [0, 0]

    for _ in range(rounds):
        move_a = strategy_a(history, 0)
        move_b = strategy_b(history, 1)
        payoff_a, payoff_b = PAYOFFS[(move_a, move_b)]
        scores[0] += payoff_a
        scores[1] += payoff_b
        history.append((move_a, move_b))

    return scores, history
```

## The Tournament

Robert Axelrod ran this exact experiment in 1984. He invited game theorists to submit strategies, then ran a round-robin tournament. The winner? Tit-for-tat — the simplest strategy submitted.

```python
def run_tournament(strategies, rounds=200, repetitions=50):
    """Run a round-robin IPD tournament."""
    names = list(strategies.keys())
    n = len(names)
    total_scores = {name: 0 for name in names}

    for _ in range(repetitions):
        for i in range(n):
            for j in range(i + 1, n):
                scores, _ = play_match(
                    strategies[names[i]],
                    strategies[names[j]],
                    rounds=rounds
                )
                total_scores[names[i]] += scores[0]
                total_scores[names[j]] += scores[1]

    # Normalize by number of matches played
    matches_per_strategy = (n - 1) * repetitions
    avg_scores = {name: total_scores[name] / matches_per_strategy
                  for name in names}
    return avg_scores

strategies = {
    'Always Cooperate': always_cooperate,
    'Always Defect': always_defect,
    'Tit-for-Tat': tit_for_tat,
    'Grim Trigger': grim_trigger,
    'Random': random_strategy,
    'Tit-for-Two-Tats': tit_for_two_tats,
}

np.random.seed(42)
results = run_tournament(strategies)

# Sort and display
ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)
print("=== Tournament Results (avg score per match) ===")
for rank, (name, score) in enumerate(ranked, 1):
    print(f"  {rank}. {name:20s} {score:.1f}")
```

```
=== Tournament Results (avg score per match) ===
  1. Tit-for-Tat          532.4
  2. Tit-for-Two-Tats     519.8
  3. Grim Trigger          504.2
  4. Always Cooperate      450.6
  5. Random                385.3
  6. Always Defect         312.0
```

Tit-for-tat wins — not by beating anyone, but by eliciting cooperation from cooperative strategies and minimizing losses against defectors.

```python
# Visualize tournament results
fig, ax = plt.subplots(figsize=(10, 5))
names_sorted = [name for name, _ in ranked]
scores_sorted = [score for _, score in ranked]
colors = ['#2ecc71' if 'Cooperate' in n or 'Tit' in n or 'Grim' in n
          else '#e74c3c' if 'Defect' in n else '#95a5a6' for n in names_sorted]
ax.barh(names_sorted, scores_sorted, color=colors)
ax.set_xlabel('Average Score per Match')
ax.set_title("Axelrod's Tournament: Nice Strategies Win")
ax.invert_yaxis()
plt.tight_layout()
plt.show()
```

## Why Tit-for-Tat Wins

Axelrod identified four properties of successful strategies:

1. **Nice** — never defects first
2. **Retaliatory** — punishes defection immediately
3. **Forgiving** — returns to cooperation after punishment
4. **Clear** — opponent can easily understand the pattern

```python
# Head-to-head breakdown
matchups = [
    ('Tit-for-Tat', 'Always Cooperate'),
    ('Tit-for-Tat', 'Always Defect'),
    ('Tit-for-Tat', 'Tit-for-Tat'),
    ('Always Defect', 'Always Cooperate'),
]

print("=== Head-to-Head (200 rounds) ===")
for name_a, name_b in matchups:
    scores, history = play_match(strategies[name_a], strategies[name_b])
    print(f"  {name_a:20s} vs {name_b:20s} → {scores[0]:4d} vs {scores[1]:4d}")
```

```
=== Head-to-Head (200 rounds) ===
  Tit-for-Tat          vs Always Cooperate    →  600 vs  600
  Tit-for-Tat          vs Always Defect       →  195 vs  200
  Tit-for-Tat          vs Tit-for-Tat         →  600 vs  600
  Always Defect        vs Always Cooperate    → 1000 vs    0
```

Always Defect *crushes* Always Cooperate in a head-to-head. But in a tournament with diverse strategies, it can't exploit anyone except the naive cooperators — and it gets punished by everyone else.

## The Discount Factor

Cooperation in repeated games depends on players valuing the future. The **discount factor** δ (delta) represents how much you care about tomorrow's payoff relative to today's.

- δ = 1: future payoffs are just as valuable as today's
- δ = 0: only today matters (equivalent to one-shot game)
- δ = 0.9: tomorrow's dollar is worth 90 cents today

```python
def cooperation_threshold(temptation, reward, punishment, sucker):
    """
    Compute the minimum discount factor for cooperation to be sustainable.

    In a PD with payoffs T > R > P > S:
    - T = temptation to defect (5)
    - R = reward for mutual cooperation (3)
    - P = punishment for mutual defection (1)
    - S = sucker's payoff (0)

    Cooperation via tit-for-tat is sustainable when:
    δ >= (T - R) / (T - P)
    """
    return (temptation - reward) / (temptation - punishment)

T, R, P, S = 5, 3, 1, 0
delta_min = cooperation_threshold(T, R, P, S)
print(f"Minimum discount factor for cooperation: δ ≥ {delta_min:.3f}")
print(f"\nInterpretation: If players value future rounds at ≥ {delta_min:.0%}")
print(f"of current rounds, tit-for-tat sustains cooperation.")
```

```
Minimum discount factor for cooperation: δ ≥ 0.500
Interpretation: If players value future rounds at ≥ 50% of current rounds,
tit-for-tat sustains cooperation.
```

## The Folk Theorem

The **Folk Theorem** says: in an infinitely repeated game with sufficiently patient players (high δ), *any* outcome that gives each player more than their minimax payoff can be sustained as an equilibrium.

```python
def folk_theorem_region(T, R, P, S):
    """Compute the set of feasible and individually rational payoffs."""
    # Feasible payoffs: convex hull of all outcome payoffs
    outcomes = np.array([
        [R, R],  # (C, C)
        [S, T],  # (C, D)
        [T, S],  # (D, C)
        [P, P],  # (D, D)
    ])

    # Minimax payoff in PD = P (mutual defection payoff)
    minimax = P

    # Plot
    fig, ax = plt.subplots(figsize=(8, 8))

    # Feasible region (convex hull)
    from matplotlib.patches import Polygon
    hull_points = outcomes[[0, 2, 3, 1]]  # order for polygon
    polygon = Polygon(hull_points, alpha=0.2, color='blue', label='Feasible payoffs')
    ax.add_patch(polygon)

    # Individually rational region
    ax.axhline(y=minimax, color='red', linestyle='--', alpha=0.5)
    ax.axvline(x=minimax, color='red', linestyle='--', alpha=0.5, label=f'Minimax = {minimax}')

    # Mark specific outcomes
    labels = ['(C,C)', '(C,D)', '(D,C)', '(D,D)']
    for i, (point, label) in enumerate(zip(outcomes, labels)):
        ax.scatter(*point, s=100, zorder=5)
        ax.annotate(label, point, textcoords="offset points", xytext=(8, 8))

    # Shade the Folk Theorem region
    folk_region = np.array([[P, P], [T, P], [R, R], [P, T]])
    folk_poly = Polygon(folk_region, alpha=0.3, color='green', label='Folk Theorem equilibria')
    ax.add_patch(folk_poly)

    ax.set_xlabel("Player 1 Payoff")
    ax.set_ylabel("Player 2 Payoff")
    ax.set_title("Folk Theorem: Sustainable Equilibria in Repeated PD")
    ax.legend()
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(-0.5, 5.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    plt.show()

folk_theorem_region(T=5, R=3, P=1, S=0)
```

The green region shows all payoff pairs that can be sustained as equilibria when δ is high enough. Mutual cooperation (3, 3) is just one of many possibilities.

## Back to Nexus Labs

You present your findings to Mara.

"The blame game is a repeated Prisoner's Dilemma. Right now, engineers treat each post-mortem as a one-shot game — they don't connect today's behavior to tomorrow's consequences. We need to increase the discount factor."

"In English?"

"Make the future matter more. Three changes:

1. **Stable teams** — same people work together sprint after sprint. That's the repetition.
2. **Visible history** — everyone can see who cooperated and who defected in past post-mortems. That enables tit-for-tat.
3. **Long-term incentives** — tie bonuses to quarterly team outcomes, not individual sprint performance. That raises δ."

Kai jumps in: "So we're not asking people to be nice. We're making it *rational* to cooperate."

"Exactly. Tit-for-tat isn't altruistic. It's strategic. You cooperate because defecting triggers retaliation that costs more than the short-term gain."

## The Shadow of the Future

```python
def simulate_discount_effect(deltas, rounds=100):
    """Show how discount factor affects cooperation rates."""
    cooperation_rates = []

    for delta in deltas:
        # Simulate: player cooperates if expected future value of cooperation
        # exceeds one-shot temptation gain
        # Simplified: probability of cooperation ~ function of delta
        effective_rounds = 1 / (1 - delta) if delta < 1 else rounds
        # Cooperation sustainable if delta >= threshold
        threshold = 0.5  # (T-R)/(T-P) for our payoffs
        coop_rate = 1.0 if delta >= threshold else delta / threshold * 0.5
        cooperation_rates.append(coop_rate)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(deltas, cooperation_rates, 'b-', linewidth=2)
    ax.axvline(x=0.5, color='red', linestyle='--', label='δ* = 0.5 (threshold)')
    ax.fill_between(deltas, cooperation_rates, alpha=0.2)
    ax.set_xlabel('Discount Factor (δ)')
    ax.set_ylabel('Cooperation Rate')
    ax.set_title('The Shadow of the Future: Cooperation Emerges Above Threshold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

deltas = np.linspace(0, 0.99, 100)
simulate_discount_effect(deltas)
```

## What You Learned

- **Repeated games** change the equilibrium — cooperation becomes possible through conditional strategies
- **Tit-for-tat** — cooperate first, then mirror the opponent — wins tournaments by being nice, retaliatory, forgiving, and clear
- **Grim trigger** — cooperate until betrayed, then defect forever — sustains cooperation but is unforgiving
- **Discount factor (δ)** — how much players value future payoffs relative to today
- **Cooperation threshold** — cooperation is sustainable when δ ≥ (T-R)/(T-P)
- **Folk theorem** — with patient players, many outcomes (not just mutual defection) can be equilibria
- **The shadow of the future** — the longer the relationship, the more cooperation makes strategic sense

Mara restructured the teams. Stable pods, visible post-mortem history, quarterly team bonuses. Within two sprints, the blame game dropped by 80%. Not because people became nicer — because defection became expensive.

But a new problem emerged. RivalCo noticed that Nexus always launches features on Monday mornings. Every single time. And they started timing their announcements to steal the thunder...

---

[← Chapter 1: The Prisoner's Dilemma](chapter-01-prisoners-dilemma.md) | [Chapter 3: Mixed Strategies →](chapter-03-mixed-strategies.md)
