# Chapter 4: Dynamic Programming

[← Chapter 3: Markov Decision Processes](chapter-03-mdp.md) | [Chapter 5: Monte Carlo Methods →](chapter-05-monte-carlo.md)

---

## The Problem

You have the full MDP — every transition probability, every reward. Jonas asks: "If we know the rules of the game perfectly, can we just compute the best strategy directly? No trial and error?"

Yes. That's dynamic programming (DP). It exploits the Bellman equation to compute optimal policies without ever running an episode.

But there's a catch: you need the complete model. Every state, every transition, every reward must be known. For our 4×4 grid, that's trivial. For a real game with millions of states? Impossible.

DP is the theoretical foundation. It shows us what "optimal" looks like. Every practical algorithm in later chapters approximates what DP computes exactly.

## Policy Evaluation: How Good Is This Policy?

Given a policy π, compute V^π(s) for all states.

The Bellman equation for policy π:

```
V^π(s) = Σ_a π(a|s) · Σ_s' P(s'|s,a) · [R(s,a,s') + γ · V^π(s')]
```

For a deterministic policy (one action per state):

```
V^π(s) = R(s, π(s)) + γ · V^π(next_state(s, π(s)))
```

This is a system of linear equations — one per state. We can solve it iteratively:

```python
def policy_evaluation(mdp, policy, theta=1e-6, max_iterations=1000):
    """
    Compute V^π for a given policy.
    Iteratively apply the Bellman equation until convergence.
    """
    V = np.zeros(mdp.n_states)
    
    for iteration in range(max_iterations):
        delta = 0
        
        for s in range(mdp.n_states):
            if s in mdp.terminal_states:
                continue
            
            v = V[s]
            a = policy[s]
            
            # Bellman equation
            new_v = 0
            for prob, next_s in mdp.P[s][a]:
                reward = mdp.R[s, a]
                new_v += prob * (reward + mdp.gamma * V[next_s])
            
            V[s] = new_v
            delta = max(delta, abs(v - V[s]))
        
        if delta < theta:
            print(f"Policy evaluation converged in {iteration+1} iterations")
            return V
    
    print(f"Policy evaluation did not converge in {max_iterations} iterations")
    return V
```

### Example: Evaluate the "Always Go Right" Policy

```python
mdp = GridWorldMDP()
always_right = {s: 3 for s in range(16)}  # Action 3 = right

V = policy_evaluation(mdp, always_right)

# Display as grid
print("V^π for 'always go right' policy:")
for r in range(4):
    row_str = ""
    for c in range(4):
        s = r * 4 + c
        row_str += f" {V[s]:6.3f} "
    print(row_str)
```

Output:
```
Policy evaluation converged in 47 iterations
V^π for 'always go right' policy:
  0.656   0.729   0.810   0.000 
 -0.124   0.000  -0.068  -0.076 
 -0.164  -0.145  -0.128   0.000 
 -0.200  -0.177  -0.157  -0.139 
```

States near the goal (top-right) have high values. States near traps have negative values. Terminal states have value 0 (episode ends there).

The "always right" policy is decent for the top row but terrible for the bottom — it pushes agents into the right-side trap.

## Policy Improvement: Make the Policy Better

Given V^π, can we find a better policy? Yes — be greedy with respect to V:

```python
def policy_improvement(mdp, V):
    """
    Given value function V, compute the greedy policy.
    For each state, pick the action that maximizes expected value.
    """
    new_policy = {}
    
    for s in range(mdp.n_states):
        if s in mdp.terminal_states:
            new_policy[s] = 0  # Doesn't matter
            continue
        
        action_values = np.zeros(mdp.n_actions)
        for a in range(mdp.n_actions):
            for prob, next_s in mdp.P[s][a]:
                action_values[a] += prob * (mdp.R[s, a] + mdp.gamma * V[next_s])
        
        new_policy[s] = np.argmax(action_values)
    
    return new_policy
```

**Policy improvement theorem**: The greedy policy with respect to V^π is at least as good as π. If it's strictly better in any state, the overall policy is strictly better.

## Policy Iteration: Evaluate → Improve → Repeat

Alternate between evaluation and improvement until the policy stops changing:

```python
def policy_iteration(mdp):
    """
    Find the optimal policy by alternating evaluation and improvement.
    """
    # Start with a random policy
    policy = {s: np.random.randint(mdp.n_actions) for s in range(mdp.n_states)}
    
    iteration = 0
    while True:
        # Evaluate current policy
        V = policy_evaluation(mdp, policy)
        
        # Improve policy
        new_policy = policy_improvement(mdp, V)
        
        # Check if policy changed
        if new_policy == policy:
            print(f"Policy iteration converged in {iteration+1} iterations")
            return policy, V
        
        policy = new_policy
        iteration += 1

optimal_policy, optimal_V = policy_iteration(GridWorldMDP())
```

Output:
```
Policy iteration converged in 3 iterations
```

Three iterations. That's it. Policy iteration is remarkably fast — it typically converges in very few iterations, even for large state spaces.

### The Optimal Policy

```python
action_symbols = ['↑', '↓', '←', '→']
print("Optimal Policy:")
for r in range(4):
    row_str = ""
    for c in range(4):
        s = r * 4 + c
        if s == 3:
            row_str += " G "
        elif s in [5, 11]:
            row_str += " X "
        else:
            row_str += f" {action_symbols[optimal_policy[s]]} "
    print(row_str)

print("\nOptimal Values:")
for r in range(4):
    row_str = ""
    for c in range(4):
        s = r * 4 + c
        row_str += f" {optimal_V[s]:6.3f} "
    print(row_str)
```

```
Optimal Policy:
 →  →  →  G 
 ↑  X  ↑  ← 
 ↑  →  ↑  X 
 ↑  →  →  ↑ 

Optimal Values:
  0.810   0.900   1.000   0.000 
  0.729   0.000   0.810   0.000 
  0.656   0.729   0.729   0.000 
  0.590   0.656   0.656   0.590 
```

The optimal policy navigates around both traps and reaches the goal efficiently from every state.

## Value Iteration: Skip the Full Evaluation

Policy iteration evaluates the policy fully (until convergence) at each step. That's expensive. **Value iteration** combines evaluation and improvement into a single update:

```python
def value_iteration(mdp, theta=1e-6, max_iterations=1000):
    """
    Find optimal V* directly by iterating the Bellman optimality equation.
    """
    V = np.zeros(mdp.n_states)
    
    for iteration in range(max_iterations):
        delta = 0
        
        for s in range(mdp.n_states):
            if s in mdp.terminal_states:
                continue
            
            v = V[s]
            
            # Bellman optimality equation: take the max over actions
            action_values = np.zeros(mdp.n_actions)
            for a in range(mdp.n_actions):
                for prob, next_s in mdp.P[s][a]:
                    action_values[a] += prob * (mdp.R[s, a] + mdp.gamma * V[next_s])
            
            V[s] = np.max(action_values)
            delta = max(delta, abs(v - V[s]))
        
        if delta < theta:
            print(f"Value iteration converged in {iteration+1} iterations")
            break
    
    # Extract policy from optimal values
    policy = policy_improvement(mdp, V)
    return policy, V

optimal_policy_vi, optimal_V_vi = value_iteration(GridWorldMDP())
```

```
Value iteration converged in 28 iterations
```

Value iteration takes more iterations than policy iteration (28 vs 3) but each iteration is much cheaper (no inner evaluation loop). For large state spaces, value iteration is usually preferred.

## Comparing the Two Approaches

| | Policy Iteration | Value Iteration |
|---|---|---|
| Outer iterations | Few (2-5 typically) | Many (tens to hundreds) |
| Per iteration cost | High (full policy evaluation) | Low (single sweep) |
| Total computation | Often less for small MDPs | Often less for large MDPs |
| Convergence | Exact in finite steps | Asymptotic (approaches optimal) |

Both find the same optimal policy. The choice is computational convenience.

## The Limitation: You Need the Model

```python
# This is what DP requires:
for prob, next_s in mdp.P[s][a]:  # Must know ALL transitions
    action_values[a] += prob * (mdp.R[s, a] + mdp.gamma * V[next_s])
```

DP needs `P(s'|s,a)` — the complete transition model. For our 4×4 grid with 16 states and 4 actions, that's a table with 16 × 4 = 64 entries. Manageable.

For GridWorld Tactics on a 20×20 grid with multiple units, fog of war, and enemy AI? The state space explodes:
- 400 positions × multiple units × health levels × resource counts × enemy positions × fog state
- Easily millions or billions of states
- Transition probabilities depend on enemy AI (unknown)

DP is impossible here. We need methods that learn from experience without knowing the model.

## Jonas Checks In

Jonas: "So DP gives us the perfect answer but only works when we know everything about the environment."

You: "Exactly. It's the gold standard — if we can compute it, we know the optimal policy. But for the real game, we can't. The state space is too large and we don't know the enemy's behavior."

Jonas: "So what do we do?"

You: "We go back to learning from experience. But now we have the theory — Bellman equations, value functions, policy improvement. The next algorithms use these same ideas but learn from episodes instead of computing from a model."

Jonas: "What's the simplest version of that?"

You: "Monte Carlo methods. Run episodes, observe returns, average them. No model needed."

## What You Learned

- **Policy evaluation** — compute V^π by iterating the Bellman equation
- **Policy improvement** — make a policy greedy with respect to its value function
- **Policy iteration** — alternate evaluation and improvement until convergence (2-5 iterations)
- **Value iteration** — combine evaluation and improvement into one update (simpler, more iterations)
- **Both find the optimal policy** — they're equivalent in the limit
- **The limitation** — DP requires the complete model (all transitions and rewards known)
- **Why it matters** — DP ideas (bootstrapping, Bellman updates) appear in every RL algorithm

DP shows us the destination. The next chapters show us how to get there without a map.

---

[← Chapter 3: Markov Decision Processes](chapter-03-mdp.md) | [Chapter 5: Monte Carlo Methods →](chapter-05-monte-carlo.md)
