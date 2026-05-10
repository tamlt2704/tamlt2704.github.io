# Chapter 4: Sequential Games — Thinking Backward

[← Chapter 3: Mixed Strategies](chapter-03-mixed-strategies.md) | [Chapter 5: Commitment & Credibility →](chapter-05-commitment.md)

---

## The Problem

Board meeting. The topic: Nexus's new developer API platform.

Mara presents the opportunity. "The enterprise API management market is growing 30% year-over-year. We can build a platform that competes directly with RivalCo's offering. But there's a timing question."

The Board member leans forward. "What's RivalCo doing?"

"They haven't announced anything yet. But our intel says they're evaluating the same market."

Kai jumps in: "We should launch first. First-mover advantage. Grab the developers before RivalCo can react."

Priya pushes back: "Or we wait. Let them go first, see what mistakes they make, and build something better. Second-mover advantage."

You've been quiet. Both arguments sound reasonable — which means neither is rigorous. This isn't a simultaneous game. One player moves first, the other observes and responds. The analysis requires a completely different tool.

"We need to think backward," you say. "Start from the end and work back to the beginning."

## Extensive Form: Game Trees

Sequential games are represented as **trees**, not matrices. Each node is a decision point, each branch is an action, and each leaf is an outcome.

```python
import numpy as np
import matplotlib.pyplot as plt

class GameNode:
    """A node in an extensive form game tree."""
    def __init__(self, player=None, actions=None, payoffs=None, children=None):
        self.player = player        # Who decides at this node
        self.actions = actions or []  # Available actions
        self.payoffs = payoffs       # Terminal payoffs (leaf nodes only)
        self.children = children or {}  # action -> GameNode

    def is_terminal(self):
        return self.payoffs is not None


def build_market_entry_game():
    """
    Nexus moves first: Enter or Wait
    RivalCo observes, then: Enter or Wait

    Payoffs: (Nexus, RivalCo)
    - Both Enter: market splits, high costs → (2, 2)
    - Nexus Enter, RivalCo Wait: Nexus dominates → (6, 1)
    - Nexus Wait, RivalCo Enter: RivalCo dominates → (1, 6)
    - Both Wait: status quo, no growth → (3, 3)
    """
    # RivalCo's decision after Nexus enters
    rival_after_enter = GameNode(
        player="RivalCo",
        actions=["Enter", "Wait"],
        children={
            "Enter": GameNode(payoffs=(2, 2)),
            "Wait": GameNode(payoffs=(6, 1)),
        }
    )

    # RivalCo's decision after Nexus waits
    rival_after_wait = GameNode(
        player="RivalCo",
        actions=["Enter", "Wait"],
        children={
            "Enter": GameNode(payoffs=(1, 6)),
            "Wait": GameNode(payoffs=(3, 3)),
        }
    )

    # Nexus's initial decision
    root = GameNode(
        player="Nexus",
        actions=["Enter", "Wait"],
        children={
            "Enter": rival_after_enter,
            "Wait": rival_after_wait,
        }
    )

    return root

game_tree = build_market_entry_game()
```

## Backward Induction

The algorithm is simple: start at the terminal nodes, work backward. At each decision node, the player picks the action that maximizes their payoff.

```python
def backward_induction(node):
    """
    Solve a sequential game by backward induction.
    Returns: (optimal_payoffs, strategy_profile)
    """
    if node.is_terminal():
        return node.payoffs, {}

    best_action = None
    best_payoffs = None
    strategy_profile = {}

    for action in node.actions:
        child = node.children[action]
        child_payoffs, child_strategies = backward_induction(child)

        # This player picks the action maximizing THEIR payoff
        player_idx = 0 if node.player == "Nexus" else 1

        if best_payoffs is None or child_payoffs[player_idx] > best_payoffs[player_idx]:
            best_action = action
            best_payoffs = child_payoffs

        strategy_profile.update(child_strategies)

    strategy_profile[node.player + "_at_" + str(id(node))] = best_action

    return best_payoffs, strategy_profile


# Solve step by step
print("=== Backward Induction ===\n")

# Step 1: RivalCo's decision after Nexus enters
print("Step 1: If Nexus enters, RivalCo chooses:")
print(f"  Enter → payoff for RivalCo: 2")
print(f"  Wait  → payoff for RivalCo: 1")
print(f"  → RivalCo enters (2 > 1)\n")

# Step 2: RivalCo's decision after Nexus waits
print("Step 2: If Nexus waits, RivalCo chooses:")
print(f"  Enter → payoff for RivalCo: 6")
print(f"  Wait  → payoff for RivalCo: 3")
print(f"  → RivalCo enters (6 > 3)\n")

# Step 3: Nexus's decision knowing RivalCo's responses
print("Step 3: Nexus anticipates RivalCo's responses:")
print(f"  Enter → RivalCo enters → Nexus gets 2")
print(f"  Wait  → RivalCo enters → Nexus gets 1")
print(f"  → Nexus enters (2 > 1)\n")

print("Subgame Perfect Equilibrium: Nexus enters, RivalCo enters")
print("Outcome: (2, 2)")
```

```
=== Backward Induction ===

Step 1: If Nexus enters, RivalCo chooses:
  Enter → payoff for RivalCo: 2
  Wait  → payoff for RivalCo: 1
  → RivalCo enters (2 > 1)

Step 2: If Nexus waits, RivalCo chooses:
  Enter → payoff for RivalCo: 6
  Wait  → payoff for RivalCo: 3
  → RivalCo enters (6 > 3)

Step 3: Nexus anticipates RivalCo's responses:
  Enter → RivalCo enters → Nexus gets 2
  Wait  → RivalCo enters → Nexus gets 1
  → Nexus enters (2 > 1)

Subgame Perfect Equilibrium: Nexus enters, RivalCo enters
Outcome: (2, 2)
```

## Visualizing the Game Tree

```python
def draw_game_tree(ax):
    """Draw the market entry game tree."""
    # Node positions
    positions = {
        'root': (0.5, 0.9),
        'enter': (0.25, 0.55),
        'wait': (0.75, 0.55),
        'ee': (0.1, 0.15),
        'ew': (0.35, 0.15),
        'we': (0.65, 0.15),
        'ww': (0.9, 0.15),
    }

    # Draw edges
    edges = [
        ('root', 'enter', 'Enter'),
        ('root', 'wait', 'Wait'),
        ('enter', 'ee', 'Enter'),
        ('enter', 'ew', 'Wait'),
        ('wait', 'we', 'Enter'),
        ('wait', 'ww', 'Wait'),
    ]

    for start, end, label in edges:
        x = [positions[start][0], positions[end][0]]
        y = [positions[start][1], positions[end][1]]
        color = 'red' if (start == 'root' and label == 'Enter') or \
                         (start == 'enter' and label == 'Enter') else 'gray'
        linewidth = 3 if color == 'red' else 1
        ax.plot(x, y, color=color, linewidth=linewidth, alpha=0.7)
        mid_x = (x[0] + x[1]) / 2 + (0.03 if label == 'Enter' else -0.03)
        mid_y = (y[0] + y[1]) / 2
        ax.text(mid_x, mid_y, label, fontsize=9, ha='center',
                fontweight='bold' if color == 'red' else 'normal')

    # Draw nodes
    ax.scatter(*positions['root'], s=200, color='blue', zorder=5)
    ax.text(positions['root'][0], positions['root'][1] + 0.05, 'Nexus', ha='center', fontweight='bold')

    for node in ['enter', 'wait']:
        ax.scatter(*positions[node], s=200, color='green', zorder=5)
        ax.text(positions[node][0], positions[node][1] + 0.05, 'RivalCo', ha='center', fontweight='bold')

    # Terminal payoffs
    payoffs = {'ee': '(2, 2)', 'ew': '(6, 1)', 'we': '(1, 6)', 'ww': '(3, 3)'}
    for node, payoff in payoffs.items():
        ax.scatter(*positions[node], s=150, color='orange', zorder=5)
        ax.text(positions[node][0], positions[node][1] - 0.06, payoff, ha='center', fontsize=10)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0, 1.05)
    ax.set_title("Market Entry Game — Backward Induction Path (red)", fontsize=12)
    ax.axis('off')

fig, ax = plt.subplots(figsize=(10, 7))
draw_game_tree(ax)
plt.tight_layout()
plt.show()
```

## Subgame Perfect Equilibrium

A **Subgame Perfect Equilibrium (SPE)** is a strategy profile where every player's strategy is optimal at *every* decision node — not just on the equilibrium path.

```python
def find_all_ne_vs_spe():
    """
    Compare Nash Equilibria of the normal form
    with the Subgame Perfect Equilibrium.
    """
    # Convert to normal form (strategic form)
    # Nexus strategies: Enter, Wait
    # RivalCo strategies: (action if Nexus enters, action if Nexus waits)
    #   EE = Enter after Enter, Enter after Wait
    #   EW = Enter after Enter, Wait after Wait
    #   WE = Wait after Enter, Enter after Wait
    #   WW = Wait after Enter, Wait after Wait

    # Nexus payoffs
    nexus_normal = np.array([
        # RivalCo: EE    EW    WE    WW
        [2, 2, 6, 6],   # Nexus Enter
        [1, 3, 1, 3],   # Nexus Wait
    ])

    # RivalCo payoffs
    rival_normal = np.array([
        # RivalCo: EE    EW    WE    WW
        [2, 2, 1, 1],   # Nexus Enter
        [6, 3, 6, 3],   # Nexus Wait
    ])

    print("Normal Form (Nexus × RivalCo contingent strategies):")
    print(f"{'':>12} {'EE':>6} {'EW':>6} {'WE':>6} {'WW':>6}")
    for i, label in enumerate(['Enter', 'Wait']):
        row = f"{label:>12}"
        for j in range(4):
            row += f" ({nexus_normal[i,j]},{rival_normal[i,j]})"
        print(row)

    print("\n--- Nash Equilibria (normal form) ---")
    # Check each cell
    for i in range(2):
        for j in range(4):
            # Is i best response to j?
            if nexus_normal[i, j] < nexus_normal[1-i, j]:
                continue
            # Is j best response to i?
            if rival_normal[i, j] < max(rival_normal[i, :]):
                # Check if j is actually the best column given row i
                if rival_normal[i, j] < np.max(rival_normal[i, :]):
                    continue
            labels_r = ['EE', 'EW', 'WE', 'WW']
            labels_n = ['Enter', 'Wait']
            print(f"  ({labels_n[i]}, {labels_r[j]}) → ({nexus_normal[i,j]}, {rival_normal[i,j]})")

    print("\n--- Subgame Perfect Equilibrium ---")
    print("  (Enter, EE) → (2, 2)")
    print("  Only EE is sequentially rational for RivalCo")
    print("  (Enter after Enter because 2>1, Enter after Wait because 6>3)")

find_all_ne_vs_spe()
```

The normal form has multiple Nash Equilibria, but only one is subgame perfect. The others rely on non-credible threats ("I'll wait if you enter" — but RivalCo wouldn't actually wait).

## Simultaneous vs. Sequential: Does Order Matter?

```python
def compare_simultaneous_sequential():
    """Show how the same payoffs produce different outcomes
    depending on whether the game is simultaneous or sequential."""

    # Simultaneous game (normal form)
    A = np.array([[2, 6], [1, 3]])  # Nexus payoffs
    B = np.array([[2, 1], [6, 3]])  # RivalCo payoffs

    import nashpy as nash
    game = nash.Game(A, B)
    sim_eq = list(game.support_enumeration())

    print("=== Simultaneous Game ===")
    print("  (Both choose without seeing the other's move)")
    for eq in sim_eq:
        payoff_n = eq[0] @ A @ eq[1]
        payoff_r = eq[0] @ B @ eq[1]
        print(f"  NE: Nexus={eq[0]}, RivalCo={eq[1]}")
        print(f"      Payoffs: ({payoff_n:.1f}, {payoff_r:.1f})")

    print("\n=== Sequential Game (Nexus moves first) ===")
    print("  SPE: Nexus=Enter, RivalCo=Enter")
    print("  Payoffs: (2, 2)")
    print("  Nexus gets 2 (worse than simultaneous mixed NE)")

    print("\n=== Sequential Game (RivalCo moves first) ===")
    # If RivalCo moves first:
    # RivalCo Enter → Nexus Enter (2>1) → (2, 2)
    # RivalCo Wait → Nexus Enter (6>3) → (6, 1)
    # RivalCo picks Enter (2 > 1)
    print("  SPE: RivalCo=Enter, Nexus=Enter")
    print("  Payoffs: (2, 2)")
    print("  Same outcome! (symmetric game)")

compare_simultaneous_sequential()
```

## First-Mover Advantage: When It Exists

First-mover advantage isn't universal. It depends on the game structure.

```python
def first_mover_advantage_example():
    """
    Stackelberg competition: first mover gets advantage.
    Technology standard: first mover sets the standard.
    """
    # Technology standard game
    # Two firms choose Standard A or Standard B
    # Payoffs depend on coordination + first-mover bonus

    print("=== Technology Standard Game ===\n")
    print("If Nexus moves first and picks Standard A:")
    print("  RivalCo prefers to coordinate → picks A too")
    print("  Outcome: (4, 3) — Nexus gets first-mover premium\n")

    print("If Nexus moves first and picks Standard B:")
    print("  RivalCo prefers to coordinate → picks B too")
    print("  Outcome: (3, 4) — wait, RivalCo gets premium on B\n")

    print("So Nexus picks A (their preferred standard).")
    print("SPE: Nexus=A, RivalCo=A, Payoffs=(4, 3)\n")

    # Model it
    # RivalCo after Nexus picks A: A→(4,3), B→(1,1)  → picks A
    # RivalCo after Nexus picks B: A→(1,1), B→(3,4)  → picks B
    # Nexus: A→(4,3) vs B→(3,4) → picks A

    payoffs_sequential = {
        'Nexus first': (4, 3),
        'RivalCo first': (3, 4),
        'Simultaneous (A,A)': (4, 3),
        'Simultaneous (B,B)': (3, 4),
        'Miscoordinate': (1, 1),
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    labels = list(payoffs_sequential.keys())
    nexus_pays = [p[0] for p in payoffs_sequential.values()]
    rival_pays = [p[1] for p in payoffs_sequential.values()]

    x = np.arange(len(labels))
    width = 0.35
    ax.bar(x - width/2, nexus_pays, width, label='Nexus', color='steelblue')
    ax.bar(x + width/2, rival_pays, width, label='RivalCo', color='coral')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha='right')
    ax.set_ylabel('Payoff')
    ax.set_title('First-Mover Advantage in Standard-Setting')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()

first_mover_advantage_example()
```

## A General Backward Induction Solver

```python
def solve_game_tree(node, depth=0):
    """General backward induction solver with trace."""
    indent = "  " * depth

    if node.is_terminal():
        return node.payoffs, []

    best_action = None
    best_payoffs = None
    trace = []

    player_idx = 0 if node.player == "Nexus" else 1

    for action in node.actions:
        child = node.children[action]
        child_payoffs, child_trace = solve_game_tree(child, depth + 1)
        trace.extend(child_trace)

        if best_payoffs is None or child_payoffs[player_idx] > best_payoffs[player_idx]:
            best_action = action
            best_payoffs = child_payoffs

    trace.append(f"{indent}{node.player} chooses '{best_action}' → payoffs {best_payoffs}")
    return best_payoffs, trace

# Solve and show trace
payoffs, trace = solve_game_tree(game_tree)
print("=== Solution Trace (bottom-up) ===")
for line in trace:
    print(line)
print(f"\nFinal outcome: {payoffs}")
```

```
=== Solution Trace (bottom-up) ===
  RivalCo chooses 'Enter' → payoffs (2, 2)
  RivalCo chooses 'Enter' → payoffs (1, 6)
Nexus chooses 'Enter' → payoffs (2, 2)

Final outcome: (2, 2)
```

## Back to Nexus Labs

You present to the Board.

"The question isn't 'should we enter the market.' It's 'what will RivalCo do after we enter.' Backward induction shows that regardless of whether we enter or wait, RivalCo will enter. Given that, we should enter first — we get 2 instead of 1."

The Board member asks: "But (3, 3) — both waiting — is better for us than (2, 2). Can't we just... both wait?"

"That's not an equilibrium. If we wait, RivalCo enters and gets 6. They have no reason to wait with us. The only way to change this outcome is to change the game itself — through commitment."

Mara: "What do you mean, change the game?"

"Right now, our 'enter' decision is reversible. We could enter and then retreat if it gets ugly. But what if we made our entry *irreversible*? What if we burned the bridge behind us? That changes RivalCo's calculation entirely."

Mara looks intrigued. "Tell me more about burning bridges."

"That's next."

## What You Learned

- **Extensive form** — sequential games are represented as trees, not matrices
- **Backward induction** — solve from the end, working backward to the start
- **Subgame perfect equilibrium** — optimal play at every decision node, not just on-path
- **Normal form vs. extensive form** — the same payoffs can produce different outcomes depending on timing
- **First-mover advantage** — exists when moving first lets you force the follower into your preferred outcome
- **Non-credible strategies** — some Nash Equilibria rely on threats that wouldn't actually be carried out
- **The key question** — "What will they do AFTER I move?" not "What should I do?"

Nexus entered the market. RivalCo followed. Both got (2, 2). But Mara isn't satisfied — she wants (6, 1). To get there, Nexus needs to make RivalCo believe that entering would be catastrophic for them. That requires a credible commitment...

---

[← Chapter 3: Mixed Strategies](chapter-03-mixed-strategies.md) | [Chapter 5: Commitment & Credibility →](chapter-05-commitment.md)
