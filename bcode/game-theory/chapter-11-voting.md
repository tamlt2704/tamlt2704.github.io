# Chapter 11: Voting & Social Choice — The Impossibility of Fairness

[← Chapter 10: Evolutionary Game Theory](chapter-10-evolutionary.md) | [Chapter 12: Cooperative Games →](chapter-12-cooperative.md)

---

## The Problem

The engineering team needs to choose a framework for the new platform rewrite. Three options:

- **React** — the safe choice, everyone knows it
- **Svelte** — lighter, faster, but less ecosystem
- **HTMX** — radical simplicity, but risky for complex UIs

Priya says: "Let's just vote." Eight engineers submit their preference rankings. You tally the results.

And then something strange happens. Depending on *which voting method* you use, a different framework wins.

Kai: "That can't be right. Just count the votes."

You: "Which votes? Counted how? That's the whole problem."

## The Preference Profile

```python
import numpy as np
from itertools import permutations

# 8 engineers, ranked preferences (1st, 2nd, 3rd)
# Candidates: R = React, S = Svelte, H = HTMX

preferences = {
    "Alice":   ["Svelte", "HTMX", "React"],
    "Bob":     ["React", "Svelte", "HTMX"],
    "Carlos":  ["HTMX", "Svelte", "React"],
    "Diana":   ["Svelte", "React", "HTMX"],
    "Eve":     ["React", "HTMX", "Svelte"],
    "Frank":   ["HTMX", "React", "Svelte"],
    "Grace":   ["Svelte", "HTMX", "React"],
    "Hiro":    ["React", "HTMX", "Svelte"],
}

candidates = ["React", "Svelte", "HTMX"]

print("=== Preference Profile ===\n")
print(f"{'Engineer':<10} {'1st':<10} {'2nd':<10} {'3rd':<10}")
print("-" * 40)
for name, prefs in preferences.items():
    print(f"{name:<10} {prefs[0]:<10} {prefs[1]:<10} {prefs[2]:<10}")
```

```
=== Preference Profile ===

Engineer   1st        2nd        3rd       
----------------------------------------
Alice      Svelte     HTMX       React     
Bob        React      Svelte     HTMX      
Carlos     HTMX       Svelte     React     
Diana      Svelte     React      HTMX      
Eve        React      HTMX       Svelte    
Frank      HTMX       React      Svelte    
Grace      Svelte     HTMX       React     
Hiro       React      HTMX       Svelte    
```

## Method 1: Plurality (First Past the Post)

```python
def plurality(preferences, candidates):
    """Count first-place votes only. Most first-place votes wins."""
    scores = {c: 0 for c in candidates}
    for prefs in preferences.values():
        scores[prefs[0]] += 1
    
    winner = max(scores, key=scores.get)
    return winner, scores

winner, scores = plurality(preferences, candidates)
print("=== Plurality Voting ===")
print(f"First-place votes: {scores}")
print(f"Winner: {winner}")
```

```
=== Plurality Voting ===
First-place votes: {'React': 3, 'Svelte': 3, 'HTMX': 2}
Winner: React (tie-broken alphabetically)
```

## Method 2: Borda Count

```python
def borda_count(preferences, candidates):
    """
    Assign points based on ranking position.
    With 3 candidates: 1st = 2 points, 2nd = 1 point, 3rd = 0 points.
    """
    n = len(candidates)
    scores = {c: 0 for c in candidates}
    
    for prefs in preferences.values():
        for rank, candidate in enumerate(prefs):
            scores[candidate] += (n - 1 - rank)  # 2, 1, 0
    
    winner = max(scores, key=scores.get)
    return winner, scores

winner, scores = borda_count(preferences, candidates)
print("=== Borda Count ===")
print(f"Scores (2 pts for 1st, 1 for 2nd, 0 for 3rd): {scores}")
print(f"Winner: {winner}")
```

```
=== Borda Count ===
Scores (2 pts for 1st, 1 for 2nd, 0 for 3rd): {'React': 7, 'Svelte': 8, 'HTMX': 9}
Winner: HTMX
```

Wait — HTMX wins? It had the *fewest* first-place votes!

## Method 3: Condorcet (Pairwise Majority)

```python
def condorcet(preferences, candidates):
    """
    A Condorcet winner beats every other candidate in pairwise comparison.
    """
    n_voters = len(preferences)
    pairwise = {}
    
    for i, c1 in enumerate(candidates):
        for j, c2 in enumerate(candidates):
            if i >= j:
                continue
            # How many voters prefer c1 over c2?
            c1_wins = 0
            for prefs in preferences.values():
                if prefs.index(c1) < prefs.index(c2):
                    c1_wins += 1
            c2_wins = n_voters - c1_wins
            pairwise[(c1, c2)] = (c1_wins, c2_wins)
    
    print("=== Condorcet (Pairwise) ===")
    print("Head-to-head results:")
    for (c1, c2), (w1, w2) in pairwise.items():
        winner_label = c1 if w1 > w2 else c2 if w2 > w1 else "Tie"
        print(f"  {c1} vs {c2}: {w1}-{w2} → {winner_label} wins")
    
    # Check for Condorcet winner (beats all others)
    for candidate in candidates:
        beats_all = True
        for other in candidates:
            if other == candidate:
                continue
            pair = (candidate, other) if (candidate, other) in pairwise else (other, candidate)
            if pair[0] == candidate:
                if pairwise[pair][0] <= pairwise[pair][1]:
                    beats_all = False
            else:
                if pairwise[pair][1] <= pairwise[pair][0]:
                    beats_all = False
        if beats_all:
            print(f"\nCondorcet winner: {candidate}")
            return candidate
    
    print("\nNo Condorcet winner exists! (Cycle)")
    return None

condorcet_winner = condorcet(preferences, candidates)
```

```
=== Condorcet (Pairwise) ===
Head-to-head results:
  React vs Svelte: 4-4 → Tie
  React vs HTMX: 4-4 → Tie
  Svelte vs HTMX: 5-3 → Svelte wins

Condorcet winner: Svelte
```

## The Disagreement

```python
def compare_methods(preferences, candidates):
    """Run all methods and show the disagreement."""
    print("=" * 50)
    print("VOTING METHOD COMPARISON")
    print("=" * 50)
    
    p_winner, p_scores = plurality(preferences, candidates)
    b_winner, b_scores = borda_count(preferences, candidates)
    c_winner = condorcet(preferences, candidates)
    
    print(f"\n{'Method':<20} {'Winner':<10}")
    print("-" * 30)
    print(f"{'Plurality':<20} {'React (tied)':<10}")
    print(f"{'Borda Count':<20} {'HTMX':<10}")
    print(f"{'Condorcet':<20} {'Svelte':<10}")
    print(f"\nThree methods, three different winners.")
    print(f"Which one is 'right'? None of them. All of them.")

compare_methods(preferences, candidates)
```

```
==================================================
VOTING METHOD COMPARISON
==================================================

Method               Winner    
------------------------------
Plurality            React (tied)
Borda Count          HTMX      
Condorcet            Svelte    

Three methods, three different winners.
Which one is 'right'? None of them. All of them.
```

## Arrow's Impossibility Theorem

Kenneth Arrow proved in 1951 that **no voting system** with 3+ candidates can simultaneously satisfy all of these reasonable fairness criteria:

```python
def arrows_theorem_demo():
    """
    Arrow's fairness criteria:
    
    1. Unrestricted Domain: Any preference ordering is allowed
    2. Pareto Efficiency: If everyone prefers A to B, society should too
    3. Independence of Irrelevant Alternatives (IIA): 
       The social ranking of A vs B depends only on individual rankings of A vs B
    4. Non-Dictatorship: No single voter determines the outcome
    
    Arrow's Theorem: No voting system satisfies all four simultaneously
    (for 3+ candidates with ranked preferences).
    """
    print("=== Arrow's Impossibility Theorem ===\n")
    print("Fairness criteria:")
    print("  1. Unrestricted Domain — any preferences allowed")
    print("  2. Pareto Efficiency — unanimous preferences respected")
    print("  3. IIA — removing a loser shouldn't change the winner")
    print("  4. Non-Dictatorship — no single voter is decisive\n")
    
    # Demonstrate IIA violation in plurality
    print("--- IIA Violation in Plurality ---\n")
    
    # Original election
    prefs_original = {
        "V1": ["React", "Svelte", "HTMX"],
        "V2": ["React", "Svelte", "HTMX"],
        "V3": ["Svelte", "HTMX", "React"],
        "V4": ["Svelte", "HTMX", "React"],
        "V5": ["HTMX", "React", "Svelte"],
    }
    
    w1, s1 = plurality(prefs_original, candidates)
    print(f"Original: {s1} → Winner: React/Svelte tie\n")
    
    # Remove HTMX (an "irrelevant" alternative that didn't win)
    prefs_no_htmx = {}
    for voter, prefs in prefs_original.items():
        prefs_no_htmx[voter] = [p for p in prefs if p != "HTMX"]
    
    reduced_candidates = ["React", "Svelte"]
    w2, s2 = plurality(prefs_no_htmx, reduced_candidates)
    print(f"Remove HTMX: {s2} → Winner: {w2}")
    print(f"\nRemoving a LOSER (HTMX) changed the winner!")
    print(f"This violates Independence of Irrelevant Alternatives.")

arrows_theorem_demo()
```

```
=== Arrow's Impossibility Theorem ===

Fairness criteria:
  1. Unrestricted Domain — any preferences allowed
  2. Pareto Efficiency — unanimous preferences respected
  3. IIA — removing a loser shouldn't change the winner
  4. Non-Dictatorship — no single voter is decisive

--- IIA Violation in Plurality ---

Original: {'React': 2, 'Svelte': 2, 'HTMX': 1} → Winner: React/Svelte tie

Remove HTMX: {'React': 2, 'Svelte': 3} → Winner: Svelte

Removing a LOSER (HTMX) changed the winner!
This violates Independence of Irrelevant Alternatives.
```

## Strategic Voting

If you know the voting method, you can vote *strategically* — misrepresenting your preferences to get a better outcome.

```python
def strategic_voting_demo():
    """
    Show how a voter can manipulate the outcome by lying about preferences.
    """
    print("=== Strategic Voting ===\n")
    
    # Borda count with honest preferences
    honest_prefs = {
        "V1": ["React", "Svelte", "HTMX"],
        "V2": ["React", "Svelte", "HTMX"],
        "V3": ["Svelte", "HTMX", "React"],
        "V4": ["Svelte", "HTMX", "React"],
        "V5": ["HTMX", "Svelte", "React"],
        "V6": ["HTMX", "React", "Svelte"],
        "V7": ["HTMX", "React", "Svelte"],
    }
    
    w_honest, s_honest = borda_count(honest_prefs, candidates)
    print(f"Honest Borda scores: {s_honest}")
    print(f"Honest winner: {w_honest}\n")
    
    # V1 and V2 prefer React. They can strategically rank HTMX last
    # to hurt the actual winner. But what if they tank Svelte instead?
    strategic_prefs = honest_prefs.copy()
    # V1 lies: puts HTMX last (already true) and Svelte last
    strategic_prefs["V1"] = ["React", "HTMX", "Svelte"]  # Demote Svelte
    strategic_prefs["V2"] = ["React", "HTMX", "Svelte"]  # Demote Svelte
    
    w_strat, s_strat = borda_count(strategic_prefs, candidates)
    print(f"After V1, V2 strategically demote Svelte:")
    print(f"Strategic Borda scores: {s_strat}")
    print(f"Strategic winner: {w_strat}\n")
    
    # Gibbard-Satterthwaite theorem
    print("--- Gibbard-Satterthwaite Theorem ---")
    print("Any non-dictatorial voting system with 3+ candidates")
    print("is susceptible to strategic manipulation.")
    print("\nNo system is strategy-proof (except dictatorship).")

strategic_voting_demo()
```

```
=== Strategic Voting ===

Honest Borda scores: {'React': 5, 'Svelte': 7, 'HTMX': 9}
Honest winner: HTMX

After V1, V2 strategically demote Svelte:
Strategic Borda scores: {'React': 5, 'Svelte': 5, 'HTMX': 11}
Strategic winner: HTMX

--- Gibbard-Satterthwaite Theorem ---
Any non-dictatorial voting system with 3+ candidates
is susceptible to strategic manipulation.

No system is strategy-proof (except dictatorship).
```

## What Priya Actually Did

```python
def priyas_solution():
    """
    Priya's pragmatic approach: use the method that matches the decision type.
    """
    print("=== Priya's Decision Framework ===\n")
    
    decisions = {
        "Binary choice (A vs B)": {
            "method": "Simple majority",
            "why": "With 2 options, all methods agree. No paradoxes.",
        },
        "Multiple options, need consensus": {
            "method": "Condorcet (pairwise)",
            "why": "Picks the option that beats all others head-to-head. Respects majority in every matchup.",
        },
        "Multiple options, need broad support": {
            "method": "Borda count",
            "why": "Rewards being everyone's 2nd choice. Avoids polarizing winners.",
        },
        "Quick decision, low stakes": {
            "method": "Plurality + runoff",
            "why": "Fast. If no majority, top-2 runoff eliminates spoiler effect.",
        },
        "High stakes, reversible": {
            "method": "Try the top choice for 2 sprints, then re-vote",
            "why": "Reduces the cost of being wrong. Information > perfection.",
        },
    }
    
    for decision, data in decisions.items():
        print(f"📋 {decision}")
        print(f"   Method: {data['method']}")
        print(f"   Why: {data['why']}\n")

priyas_solution()
```

Priya chose Borda count for the framework decision. Svelte won — nobody's first choice, but everyone's acceptable choice. Six months later, the team is happy with it.

"The 'best' voting system depends on what you're optimizing for," you tell Mara. "There is no universal answer. Arrow proved that mathematically."

Mara: "So democracy is broken?"

You: "Democracy is a set of tradeoffs. The important thing is choosing your tradeoffs consciously."

## What You Learned

- **Plurality** — count first-place votes; simple but ignores depth of preferences
- **Borda count** — assign points by rank; rewards broad acceptability
- **Condorcet method** — pairwise majority; finds the candidate who beats all others
- **Arrow's impossibility theorem** — no system satisfies all fairness criteria simultaneously
- **Gibbard-Satterthwaite** — all non-dictatorial systems are manipulable
- **Strategic voting** — voters can benefit by misrepresenting preferences
- **Practical wisdom** — match the voting method to the decision context

Next: three teams built a product together. Revenue is $1M. How much does each team deserve? The Shapley value has a surprisingly elegant answer.

---

[← Chapter 10: Evolutionary Game Theory](chapter-10-evolutionary.md) | [Chapter 12: Cooperative Games →](chapter-12-cooperative.md)
