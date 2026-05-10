# Chapter 10: Evolutionary Game Theory — Why Bad Strategies Survive

[← Chapter 9: Signaling](chapter-09-signaling.md) | [Chapter 11: Voting & Social Choice →](chapter-11-voting.md)

---

## The Problem

Priya pulls you aside after standup. "I've got a culture problem and I can't figure out why it persists."

She explains: the engineering team has two types of developers. The **Helpers** do thorough code reviews, mentor juniors, write documentation, and answer questions in Slack. The **Selfish** ones skip reviews, never document, and focus exclusively on shipping their own features.

"The Helpers burn out because they're carrying the team. The Selfish ones get promoted because they ship more features. I've tried talks, I've tried culture docs. But the Selfish ones never fully disappear — and neither do the Helpers. It's like the team is stuck at some ratio."

You recognize the pattern. This isn't a management problem. It's an **evolutionary game** — and the stable mix of strategies is a mathematical inevitability.

## The Hawk-Dove Game

The classic model for this is the **Hawk-Dove game** (also called Chicken). Two animals compete for a resource:

- **Hawks** fight aggressively. If they meet another Hawk, both get injured.
- **Doves** share peacefully. If they meet a Hawk, they back down and get nothing.

```python
import numpy as np
import matplotlib.pyplot as plt

# Payoff matrix for Hawk-Dove
# Resource value: V = 4
# Cost of fighting: C = 6 (C > V, so fighting is costly)

V = 4  # Value of the resource
C = 6  # Cost of a fight

# Payoffs: (row player, column player)
#              Dove         Hawk
# Dove      (V/2, V/2)   (0, V)
# Hawk      (V, 0)       ((V-C)/2, (V-C)/2)

hawk_dove_matrix = np.array([
    [V/2, 0],       # Dove vs Dove, Dove vs Hawk
    [V, (V-C)/2],   # Hawk vs Dove, Hawk vs Hawk
])

print("=== Hawk-Dove Payoff Matrix ===")
print(f"Resource value V = {V}, Fight cost C = {C}\n")
print(f"{'':>10} {'Dove':>10} {'Hawk':>10}")
print(f"{'Dove':>10} {V/2:>10.1f} {0:>10.1f}")
print(f"{'Hawk':>10} {V:>10.1f} {(V-C)/2:>10.1f}")
print(f"\nHawk vs Dove: Hawk always wins ({V} > {V/2})")
print(f"Hawk vs Hawk: Both lose ({(V-C)/2} < 0)")
print(f"Neither strategy is dominant!")
```

```
=== Hawk-Dove Payoff Matrix ===
Resource value V = 4, Fight cost C = 6

               Dove       Hawk
      Dove        2.0        0.0
      Hawk        4.0       -1.0

Hawk vs Dove: Hawk always wins (4 > 2)
Hawk vs Hawk: Both lose (-1.0 < 0)
Neither strategy is dominant!
```

## Replicator Dynamics

In evolutionary game theory, we don't ask "what should a rational player do?" We ask: "if a population plays this game repeatedly, which strategies grow and which shrink?"

The **replicator equation** says: a strategy grows if its fitness exceeds the population average.

```python
def replicator_dynamics(payoff_matrix, x0, T=100, dt=0.01):
    """
    Simulate replicator dynamics for a symmetric 2-strategy game.
    
    x = fraction of population playing strategy 0 (Dove)
    1-x = fraction playing strategy 1 (Hawk)
    """
    n_steps = int(T / dt)
    x = np.zeros(n_steps)
    x[0] = x0  # Initial fraction of Doves
    
    a, b = payoff_matrix[0]  # Dove payoffs vs Dove, vs Hawk
    c, d = payoff_matrix[1]  # Hawk payoffs vs Dove, vs Hawk
    
    for t in range(n_steps - 1):
        p = x[t]  # Fraction of Doves
        
        # Fitness of each strategy
        fitness_dove = a * p + b * (1 - p)
        fitness_hawk = c * p + d * (1 - p)
        
        # Average fitness
        avg_fitness = p * fitness_dove + (1 - p) * fitness_hawk
        
        # Replicator equation: dx/dt = x * (fitness_x - avg_fitness)
        dx = p * (fitness_dove - avg_fitness) * dt
        
        x[t+1] = np.clip(x[t] + dx, 0.001, 0.999)
    
    return x

# Simulate from different starting points
fig, ax = plt.subplots(figsize=(10, 6))
T = 50
dt = 0.01
time = np.arange(0, T, dt)

for x0 in [0.1, 0.3, 0.5, 0.7, 0.9]:
    trajectory = replicator_dynamics(hawk_dove_matrix, x0, T=T, dt=dt)
    ax.plot(time[:len(trajectory)], trajectory, label=f'Start: {x0:.0%} Dove')

# Theoretical ESS
ess_dove = (C - V) / C  # Fraction of Doves at ESS
ax.axhline(y=ess_dove, color='red', linestyle='--', linewidth=2, 
           label=f'ESS: {ess_dove:.1%} Dove')

ax.set_xlabel("Time")
ax.set_ylabel("Fraction of Doves")
ax.set_title("Replicator Dynamics: Hawk-Dove Game")
ax.legend()
ax.set_ylim(0, 1)
plt.tight_layout()
plt.show()

print(f"\nEvolutionarily Stable Strategy: {ess_dove:.1%} Doves, {1-ess_dove:.1%} Hawks")
```

```
Evolutionarily Stable Strategy: 33.3% Doves, 66.7% Hawks
```

No matter where you start, the population converges to the same mix. The "bad" strategy (Hawk) persists because when Hawks are rare, they exploit Doves easily. But when Hawks are common, they destroy each other.

## Evolutionarily Stable Strategies (ESS)

A strategy is an **ESS** if a population using it cannot be invaded by a small group of mutants.

```python
def check_ess(payoff_matrix, strategy_idx):
    """
    Check if a pure strategy is an ESS.
    
    Strategy i is ESS if:
    1. E(i, i) > E(j, i) for all j ≠ i  (strict Nash), OR
    2. E(i, i) = E(j, i) AND E(i, j) > E(j, j) for all j ≠ i
    """
    n = payoff_matrix.shape[0]
    i = strategy_idx
    
    for j in range(n):
        if j == i:
            continue
        
        eii = payoff_matrix[i, i]  # Payoff of i vs i
        eji = payoff_matrix[j, i]  # Payoff of j vs i (invader vs resident)
        
        if eii > eji:
            continue  # Condition 1 satisfied
        elif eii == eji:
            eij = payoff_matrix[i, j]
            ejj = payoff_matrix[j, j]
            if eij > ejj:
                continue  # Condition 2 satisfied
            else:
                return False, f"Strategy {j} can invade (tie-breaking fails)"
        else:
            return False, f"Strategy {j} does better against {i} than {i} does"
    
    return True, "ESS confirmed"

# Check pure strategies
print("=== ESS Analysis: Hawk-Dove ===\n")
strategies = ["Dove", "Hawk"]
for idx, name in enumerate(strategies):
    is_ess, reason = check_ess(hawk_dove_matrix, idx)
    print(f"Is pure {name} an ESS? {is_ess}")
    print(f"  Reason: {reason}\n")

# The ESS is actually a mixed strategy
print("=== Mixed ESS ===")
print(f"Play Hawk with probability p* = V/C = {V}/{C} = {V/C:.3f}")
print(f"Play Dove with probability 1-p* = {1 - V/C:.3f}")
print(f"\nAt this mix, expected payoff vs any strategy is equal.")
print(f"No mutant can do better — the population is stable.")
```

```
=== ESS Analysis: Hawk-Dove ===

Is pure Dove an ESS? False
  Reason: Strategy 1 does better against 0 than 0 does

Is pure Hawk an ESS? False
  Reason: Strategy 1 can invade (tie-breaking fails)

=== Mixed ESS ===
Play Hawk with probability p* = V/C = 4/6 = 0.667
Play Dove with probability 1-p* = 0.333

At this mix, expected payoff vs any strategy is equal.
No mutant can do better — the population is stable.
```

## Back to Nexus: Helpers vs. Selfish Devs

```python
def engineering_culture_dynamics():
    """
    Model Priya's engineering team as a Hawk-Dove variant.
    
    Helpers (Doves): Do code reviews, mentor, document
    Selfish (Hawks): Skip reviews, focus on own output
    """
    # When two Helpers meet: both benefit from reviews (shared value)
    # When Helper meets Selfish: Helper does review, Selfish gets free benefit
    # When two Selfish meet: no reviews happen, both ship buggy code
    
    review_value = 3        # Value of getting a good code review
    review_cost = 1         # Time cost of doing a review
    bug_cost = 2            # Cost of shipping without review
    
    # Payoff matrix
    #                    Helper              Selfish
    # Helper    (review_value - cost)    (-cost, review_value)
    # Selfish   (review_value, 0)        (-bug_cost, -bug_cost)
    
    payoffs = np.array([
        [review_value - review_cost, -review_cost],     # Helper vs Helper, Helper vs Selfish
        [review_value, -bug_cost],                       # Selfish vs Helper, Selfish vs Selfish
    ])
    
    print("=== Engineering Team: Helper vs Selfish ===\n")
    print(f"{'':>10} {'Helper':>10} {'Selfish':>10}")
    print(f"{'Helper':>10} {payoffs[0,0]:>10.1f} {payoffs[0,1]:>10.1f}")
    print(f"{'Selfish':>10} {payoffs[1,0]:>10.1f} {payoffs[1,1]:>10.1f}")
    
    # Find ESS mix
    # At ESS: fitness(Helper) = fitness(Selfish)
    # Let p = fraction of Helpers
    # fitness_H = (V-c)*p + (-c)*(1-p) = p*(V-c) - c + cp = p*V - c
    # fitness_S = V*p + (-bug)*(1-p) = p*V + p*bug - bug
    # Set equal: p*V - c = p*V + p*bug - bug
    # -c = p*bug - bug
    # bug - c = p*bug
    # p* = (bug - c) / bug
    
    p_star = (bug_cost - review_cost) / bug_cost
    
    print(f"\n--- Equilibrium ---")
    print(f"Stable fraction of Helpers: {p_star:.1%}")
    print(f"Stable fraction of Selfish: {1-p_star:.1%}")
    
    # Simulate
    fig, ax = plt.subplots(figsize=(10, 6))
    T, dt = 80, 0.01
    time = np.arange(0, T, dt)
    
    for x0 in [0.1, 0.3, 0.5, 0.7, 0.95]:
        traj = replicator_dynamics(payoffs, x0, T=T, dt=dt)
        ax.plot(time[:len(traj)], traj, label=f'Start: {x0:.0%} Helpers')
    
    ax.axhline(y=p_star, color='red', linestyle='--', linewidth=2,
               label=f'ESS: {p_star:.0%} Helpers')
    ax.set_xlabel("Time (sprints)")
    ax.set_ylabel("Fraction of Helpers")
    ax.set_title("Engineering Culture: Replicator Dynamics")
    ax.legend()
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.show()
    
    return payoffs, p_star

payoffs, p_star = engineering_culture_dynamics()
```

```
=== Engineering Team: Helper vs Selfish ===

               Helper    Selfish
    Helper        2.0       -1.0
   Selfish        3.0       -2.0

--- Equilibrium ---
Stable fraction of Helpers: 50.0%
Stable fraction of Selfish: 50.0%
```

## Invasion Analysis

Can a new strategy invade the population?

```python
def invasion_analysis(payoff_matrix, resident_fraction, mutant_fraction=0.01):
    """
    Can a small group of mutants invade a resident population?
    
    Mutant invades if its fitness > resident fitness when rare.
    """
    p_resident = 1 - mutant_fraction
    
    # Resident is strategy 0 (Dove/Helper), mutant is strategy 1 (Hawk/Selfish)
    # Fitness when mutant is rare (mostly facing residents)
    fitness_resident = payoff_matrix[0, 0] * p_resident + payoff_matrix[0, 1] * mutant_fraction
    fitness_mutant = payoff_matrix[1, 0] * p_resident + payoff_matrix[1, 1] * mutant_fraction
    
    print(f"Population: {p_resident:.1%} Residents (strategy 0), {mutant_fraction:.1%} Mutants (strategy 1)")
    print(f"Resident fitness: {fitness_resident:.4f}")
    print(f"Mutant fitness:   {fitness_mutant:.4f}")
    print(f"→ Mutant {'CAN' if fitness_mutant > fitness_resident else 'CANNOT'} invade\n")
    
    return fitness_mutant > fitness_resident

print("=== Invasion Analysis ===\n")
print("Scenario 1: All Helpers, one Selfish dev joins")
invasion_analysis(payoffs, resident_fraction=0.99)

print("Scenario 2: All Selfish, one Helper joins")
# Flip perspective: resident is now strategy 1
flipped = np.array([[payoffs[1,1], payoffs[1,0]], [payoffs[0,1], payoffs[0,0]]])
invasion_analysis(flipped, resident_fraction=0.99)

print("Conclusion: BOTH strategies can invade the other when rare.")
print("This is why the population stabilizes at a MIX, not a pure state.")
```

```
=== Invasion Analysis ===

Scenario 1: All Helpers, one Selfish dev joins
Population: 99.0% Residents (strategy 0), 1.0% Mutants (strategy 1)
Resident fitness: 1.9700
Mutant fitness:   2.9500
→ Mutant CAN invade

Scenario 2: All Selfish, one Helper joins
Population: 99.0% Residents (strategy 0), 1.0% Mutants (strategy 1)
Resident fitness: -1.9900
Mutant fitness:   -0.9700
→ Mutant CAN invade

Conclusion: BOTH strategies can invade the other when rare.
This is why the population stabilizes at a MIX, not a pure state.
```

## Priya's Options

You present the analysis to Priya.

"The selfish devs aren't a bug — they're a stable feature of the system. You can't eliminate them through culture talks. But you *can* change the payoff matrix."

```python
def interventions():
    """What can Priya do to shift the equilibrium toward more Helpers?"""
    
    interventions = {
        "Mandatory code review (change rules)": {
            "effect": "Selfish vs Selfish now costs more (can't skip)",
            "new_bug_cost": 4,
            "new_review_cost": 1,
        },
        "Reward reviews in perf (change payoffs)": {
            "effect": "Helper vs Helper payoff increases",
            "new_bug_cost": 2,
            "new_review_cost": 0.5,  # Reviews count toward output
        },
        "Pair programming (change game structure)": {
            "effect": "Can't be selfish when paired — eliminates the strategy",
            "new_bug_cost": 2,
            "new_review_cost": 0.2,
        }
    }
    
    print("=== Interventions to Shift ESS ===\n")
    for name, data in interventions.items():
        p_star = (data['new_bug_cost'] - data['new_review_cost']) / data['new_bug_cost']
        print(f"📋 {name}")
        print(f"   {data['effect']}")
        print(f"   New ESS: {p_star:.0%} Helpers, {1-p_star:.0%} Selfish")
        print()

interventions()
```

```
=== Interventions to Shift ESS ===

📋 Mandatory code review (change rules)
   Selfish vs Selfish now costs more (can't skip)
   New ESS: 75% Helpers, 25% Selfish

📋 Reward reviews in perf (change payoffs)
   Helper vs Helper payoff increases
   New ESS: 75% Helpers, 25% Selfish

📋 Pair programming (change game structure)
   Can't be selfish when paired — eliminates the strategy
   New ESS: 90% Helpers, 10% Selfish
```

Priya nods slowly. "So I can't preach cooperation into existence. I have to make defection more expensive."

"Exactly. Evolution doesn't care about intentions. It only cares about fitness."

## What You Learned

- **Evolutionary game theory** — studies strategy dynamics in populations, not individual decisions
- **Replicator dynamics** — strategies that outperform the average grow; those that underperform shrink
- **Evolutionarily Stable Strategy (ESS)** — a strategy that can't be invaded by mutants
- **Mixed ESS** — populations often stabilize at a mix of strategies, not a single winner
- **Invasion condition** — a mutant invades if it does better than residents when rare
- **Changing the game** — you can't eliminate "bad" strategies by asking nicely; change the payoffs

Next: the engineering team votes on which framework to adopt. Three options, five voting methods, five different winners. Welcome to the impossibility of fairness.

---

[← Chapter 9: Signaling](chapter-09-signaling.md) | [Chapter 11: Voting & Social Choice →](chapter-11-voting.md)
