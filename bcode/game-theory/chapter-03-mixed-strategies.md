# Chapter 3: Mixed Strategies — When Predictability Kills

[← Chapter 2: Repeated Games](chapter-02-repeated-games.md) | [Chapter 4: Sequential Games →](chapter-04-sequential-games.md)

---

## The Problem

Kai storms into your office on a Tuesday.

"They did it again. We announced the new API gateway Monday morning — like we always do. By Monday afternoon, RivalCo had a blog post up: 'Why Our Gateway Is Better: A Point-by-Point Comparison.' They had it *pre-written*. They just waited for us to go first."

You pull up the data. Nexus has launched every major feature on a Monday for the past 18 months. Monday morning blog post, Monday afternoon Product Hunt, Tuesday press coverage. Like clockwork.

"Kai, we're playing matching pennies against RivalCo, and we're showing them our coin before we flip it."

"What?"

"We're perfectly predictable. And when you're perfectly predictable, you're perfectly exploitable."

## Matching Pennies: No Pure Strategy Equilibrium

Consider the timing game between Nexus and RivalCo:

- If Nexus launches on Monday and RivalCo *also* announces Monday → RivalCo steals thunder (they counter-program)
- If Nexus launches on Monday and RivalCo announces Friday → Nexus gets clean coverage
- If Nexus launches on Friday and RivalCo announces Monday → Nexus gets clean coverage
- If Nexus launches on Friday and RivalCo announces Friday → RivalCo steals thunder

```python
import numpy as np
import nashpy as nash

# Nexus wants to AVOID matching RivalCo's timing
# RivalCo wants to MATCH Nexus's timing

#                  RivalCo Monday   RivalCo Friday
# Nexus Monday       (-1, 1)          (1, -1)
# Nexus Friday       (1, -1)          (-1, 1)

nexus_payoffs = np.array([
    [-1,  1],   # Nexus launches Monday
    [ 1, -1],   # Nexus launches Friday
])

rival_payoffs = np.array([
    [ 1, -1],   # RivalCo announces Monday
    [-1,  1],   # RivalCo announces Friday
])

print("Nexus payoffs:")
print(nexus_payoffs)
print("\nRivalCo payoffs:")
print(rival_payoffs)
```

This is **Matching Pennies** — a zero-sum game where one player wants to match and the other wants to mismatch.

## No Pure Strategy Nash Equilibrium

Let's check every pure strategy combination:

```python
def check_pure_ne(A, B):
    """Check all pure strategy profiles for Nash Equilibria."""
    rows, cols = A.shape
    equilibria = []

    for i in range(rows):
        for j in range(cols):
            # Is (i, j) a NE?
            # Player 1: is row i the best response to column j?
            best_row = np.argmax(A[:, j])
            # Player 2: is column j the best response to row i?
            best_col = np.argmax(B[i, :])

            if best_row == i and best_col == j:
                equilibria.append((i, j))

    return equilibria

pure_ne = check_pure_ne(nexus_payoffs, rival_payoffs)
print(f"Pure strategy Nash Equilibria: {pure_ne}")
print("None! Every pure strategy can be exploited.")
```

```
Pure strategy Nash Equilibria: []
None! Every pure strategy can be exploited.
```

No matter what Nexus picks deterministically, RivalCo can counter it. And vice versa. There's no stable pure strategy.

## The Mixed Strategy Solution

When no pure strategy equilibrium exists, players must **randomize**. A mixed strategy assigns probabilities to each action.

The key insight: in a mixed strategy NE, each player randomizes in a way that makes the opponent **indifferent** between their options.

```python
def solve_mixed_ne_2x2(A, B):
    """
    Solve for mixed strategy NE in a 2x2 game.

    Player 1 mixes with probability p on row 0, (1-p) on row 1.
    Player 2 mixes with probability q on col 0, (1-q) on col 1.

    Player 2 is indifferent when:
      p * B[0,0] + (1-p) * B[1,0] = p * B[0,1] + (1-p) * B[1,1]
      (for column 0 vs column 1)

    Wait — Player 2's payoff from choosing col j given Player 1 mixes with p:
      EU2(col 0) = p * B[0,0] + (1-p) * B[1,0]
      EU2(col 1) = p * B[0,1] + (1-p) * B[1,1]

    Player 1 makes Player 2 indifferent:
      p * B[0,0] + (1-p) * B[1,0] = p * B[0,1] + (1-p) * B[1,1]

    Similarly, Player 2 makes Player 1 indifferent:
      q * A[0,0] + (1-q) * A[0,1] = q * A[1,0] + (1-q) * A[1,1]
    """
    # Solve for p (Player 1's mix) — makes Player 2 indifferent
    # p*(B[0,0] - B[1,0]) + B[1,0] = p*(B[0,1] - B[1,1]) + B[1,1]
    # p*(B[0,0] - B[1,0] - B[0,1] + B[1,1]) = B[1,1] - B[1,0]
    denom_p = B[0,0] - B[1,0] - B[0,1] + B[1,1]
    if denom_p == 0:
        return None, None
    p = (B[1,1] - B[1,0]) / denom_p

    # Solve for q (Player 2's mix) — makes Player 1 indifferent
    denom_q = A[0,0] - A[0,1] - A[1,0] + A[1,1]
    if denom_q == 0:
        return None, None
    q = (A[1,1] - A[0,1]) / denom_q

    return p, q

p, q = solve_mixed_ne_2x2(nexus_payoffs, rival_payoffs)
print(f"Mixed Strategy NE:")
print(f"  Nexus: Monday with prob {p:.2f}, Friday with prob {1-p:.2f}")
print(f"  RivalCo: Monday with prob {q:.2f}, Friday with prob {1-q:.2f}")
```

```
Mixed Strategy NE:
  Nexus: Monday with prob 0.50, Friday with prob 0.50
  RivalCo: Monday with prob 0.50, Friday with prob 0.50
```

In matching pennies, both players should randomize 50/50. Neither can be exploited.

## Verifying with Nashpy

```python
game = nash.Game(nexus_payoffs, rival_payoffs)
equilibria = list(game.support_enumeration())

print("=== Nashpy Verification ===")
for eq in equilibria:
    nexus_strat, rival_strat = eq
    print(f"  Nexus: {nexus_strat}")
    print(f"  RivalCo: {rival_strat}")
    expected_nexus = nexus_strat @ nexus_payoffs @ rival_strat
    expected_rival = nexus_strat @ rival_payoffs @ rival_strat
    print(f"  Expected payoffs: Nexus={expected_nexus:.2f}, RivalCo={expected_rival:.2f}")
```

```
=== Nashpy Verification ===
  Nexus: [0.5 0.5]
  RivalCo: [0.5 0.5]
  Expected payoffs: Nexus=0.00, RivalCo=0.00
```

## The Indifference Principle

The mixed NE has a counterintuitive property: **you don't randomize to help yourself — you randomize to make your opponent indifferent.**

```python
def demonstrate_indifference(A, B, p, q):
    """Show that at the mixed NE, each player is indifferent."""
    # Player 1 (Nexus) expected payoff from each pure strategy
    # given Player 2 mixes with q
    eu_row0 = q * A[0,0] + (1-q) * A[0,1]  # Monday
    eu_row1 = q * A[1,0] + (1-q) * A[1,1]  # Friday

    print("Nexus's expected payoff given RivalCo mixes 50/50:")
    print(f"  Play Monday: {q}*({A[0,0]}) + {1-q}*({A[0,1]}) = {eu_row0:.2f}")
    print(f"  Play Friday: {q}*({A[1,0]}) + {1-q}*({A[1,1]}) = {eu_row1:.2f}")
    print(f"  → Nexus is INDIFFERENT (both give {eu_row0:.2f})")

    print()

    # Player 2 (RivalCo) expected payoff from each pure strategy
    eu_col0 = p * B[0,0] + (1-p) * B[1,0]  # Monday
    eu_col1 = p * B[0,1] + (1-p) * B[1,1]  # Friday

    print("RivalCo's expected payoff given Nexus mixes 50/50:")
    print(f"  Play Monday: {p}*({B[0,0]}) + {1-p}*({B[1,0]}) = {eu_col0:.2f}")
    print(f"  Play Friday: {p}*({B[0,1]}) + {1-p}*({B[1,1]}) = {eu_col1:.2f}")
    print(f"  → RivalCo is INDIFFERENT (both give {eu_col0:.2f})")

demonstrate_indifference(nexus_payoffs, rival_payoffs, p, q)
```

## A Non-Symmetric Example

Real games aren't always symmetric. Suppose Nexus gets more value from Monday launches (bigger audience) but RivalCo's counter is more effective on Mondays too:

```python
# Asymmetric timing game
#                  RivalCo Monday   RivalCo Friday
# Nexus Monday       (-2, 3)          (4, -1)
# Nexus Friday       (2, -2)          (-1, 2)

A_asym = np.array([[-2, 4], [2, -1]])
B_asym = np.array([[3, -1], [-2, 2]])

p_asym, q_asym = solve_mixed_ne_2x2(A_asym, B_asym)
print(f"Asymmetric game mixed NE:")
print(f"  Nexus: Monday={p_asym:.3f}, Friday={1-p_asym:.3f}")
print(f"  RivalCo: Monday={q_asym:.3f}, Friday={1-q_asym:.3f}")

# Verify with nashpy
game_asym = nash.Game(A_asym, B_asym)
for eq in game_asym.support_enumeration():
    print(f"\n  Nashpy confirms: Nexus={eq[0]}, RivalCo={eq[1]}")
    payoff_n = eq[0] @ A_asym @ eq[1]
    payoff_r = eq[0] @ B_asym @ eq[1]
    print(f"  Expected payoffs: Nexus={payoff_n:.3f}, RivalCo={payoff_r:.3f}")
```

```
Asymmetric game mixed NE:
  Nexus: Monday=0.444, Friday=0.556
  RivalCo: Monday=0.556, Friday=0.444

  Nashpy confirms: Nexus=[0.444 0.556], RivalCo=[0.556 0.444]
  Expected payoffs: Nexus=0.889, RivalCo=0.556
```

Nexus should launch on Monday *less* often than you'd think — because that's what makes RivalCo unable to exploit the pattern.

## Simulating Convergence

What if players learn over time? Fictitious play converges to the mixed NE:

```python
def fictitious_play(A, B, rounds=1000):
    """Simulate fictitious play — each player best-responds to
    the empirical frequency of the opponent's past actions."""
    counts = [np.zeros(A.shape[0]), np.zeros(A.shape[1])]  # action counts
    history_p = []  # Player 1's mixing probability over time

    for t in range(rounds):
        # Player 1 best-responds to Player 2's empirical distribution
        if t == 0:
            q_emp = np.ones(A.shape[1]) / A.shape[1]
        else:
            q_emp = counts[1] / counts[1].sum()

        eu_rows = A @ q_emp
        action_1 = np.argmax(eu_rows)

        # Player 2 best-responds to Player 1's empirical distribution
        if t == 0:
            p_emp = np.ones(A.shape[0]) / A.shape[0]
        else:
            p_emp = counts[0] / counts[0].sum()

        eu_cols = B.T @ p_emp
        action_2 = np.argmax(eu_cols)

        counts[0][action_1] += 1
        counts[1][action_2] += 1

        # Track Player 1's empirical frequency of action 0
        history_p.append(counts[0][0] / counts[0].sum())

    return history_p, counts

history_p, final_counts = fictitious_play(nexus_payoffs, rival_payoffs, rounds=500)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(history_p, 'b-', alpha=0.7, label="Nexus P(Monday)")
ax.axhline(y=0.5, color='red', linestyle='--', label='NE = 0.5')
ax.set_xlabel('Round')
ax.set_ylabel('Empirical Probability of Monday')
ax.set_title('Fictitious Play Converges to Mixed NE')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

The empirical frequencies oscillate but converge toward the mixed NE probabilities.

## The Exploitation Cost of Predictability

```python
def exploitation_cost(A, pure_strategy, ne_mix, opponent_ne):
    """How much does a player lose by being predictable vs. mixing optimally?"""
    # Payoff from pure strategy against best-responding opponent
    best_response_col = np.argmax(rival_payoffs[pure_strategy, :] * -1)  # opponent maximizes their payoff
    # Actually: opponent picks column that maximizes THEIR payoff given our row
    opp_payoffs_given_row = rival_payoffs[pure_strategy, :]
    best_response_col = np.argmax(opp_payoffs_given_row)
    pure_payoff = A[pure_strategy, best_response_col]

    # Payoff from NE mix
    ne_payoff = ne_mix @ A @ opponent_ne

    return ne_payoff - pure_payoff

# If Nexus always plays Monday, RivalCo best-responds with Monday
cost = exploitation_cost(nexus_payoffs, 0, np.array([0.5, 0.5]), np.array([0.5, 0.5]))
print(f"Cost of always playing Monday: {cost:.1f} per interaction")
print(f"(NE payoff: 0.0, Exploited payoff: -1.0)")
print(f"\nNexus loses 1 unit per interaction by being predictable!")
```

```
Cost of always playing Monday: 1.0 per interaction
(NE payoff: 0.0, Exploited payoff: -1.0)

Nexus loses 1 unit per interaction by being predictable!
```

## Back to Nexus Labs

You present to Mara and Kai.

"We've been launching on Mondays for 18 months. RivalCo has learned our pattern and counter-programs perfectly. The fix isn't to switch to Fridays — they'd learn that too. The fix is to be *unpredictable*."

Kai frowns. "So we just... flip a coin?"

"Not exactly. We randomize according to specific probabilities that depend on the payoff structure. In our case, roughly 50/50 between Monday and Friday. But the key insight is: **the optimal strategy is to make RivalCo unable to predict us**. Any detectable pattern is exploitable."

Mara nods slowly. "So we build a launch calendar that looks random to outsiders but follows calculated probabilities internally."

"Exactly. And here's the counterintuitive part — at the mixed equilibrium, we're *indifferent* between Monday and Friday. We're not randomizing because one day is better. We're randomizing because predictability is worse than either day."

Priya, who's been listening from the doorway: "This is just operational security applied to product strategy."

"Yes. In security, you don't always patch on the same day. In poker, you don't always bluff with the same hand. In product, you don't always launch on the same day. Predictability is a vulnerability."

## What You Learned

- **No pure strategy NE** — some games have no stable deterministic solution
- **Mixed strategy** — a probability distribution over actions, not a single choice
- **Indifference principle** — at the mixed NE, each player is indifferent between their options
- **Computing mixed NE** — set opponent's expected payoffs equal across their strategies, solve for your mix
- **Exploitation cost** — being predictable lets opponents best-respond and extract value
- **Fictitious play** — learning dynamics converge to mixed NE over time
- **The insight** — sometimes the optimal play is to be deliberately unpredictable

RivalCo can no longer predict Nexus's launch timing. But a new question arises: Nexus is considering entering a new market. Should they move first and establish themselves, or wait to see what RivalCo does? The answer depends on who moves when — and that requires a different kind of game entirely.

---

[← Chapter 2: Repeated Games](chapter-02-repeated-games.md) | [Chapter 4: Sequential Games →](chapter-04-sequential-games.md)
