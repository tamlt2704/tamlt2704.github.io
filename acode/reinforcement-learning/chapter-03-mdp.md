# Chapter 3: Markov Decision Processes

[← Chapter 2: Exploration](chapter-02-exploration.md) | [Chapter 4: Dynamic Programming →](chapter-04-dynamic-programming.md)

---

## The Problem

Your epsilon-greedy agent works on the 4×4 grid. Jonas wants to scale it up. Mira designs a new level: 8×8 grid, more traps, moving enemies, and a fog of war that hides distant squares.

You try your agent on the new grid. It takes 50,000 episodes to learn a decent policy. On the 4×4 grid it took 500.

Jonas: "Why is it so slow?"

You: "It's learning everything from scratch through trial and error. It doesn't know that moving right from (3,2) leads to (3,3). It has to discover every transition by trying it. If we could give it a model of the world — the rules of movement — it could plan ahead without needing thousands of episodes."

Jonas: "So give it the rules."

You: "First I need to formalize what 'rules of the world' even means. That's a Markov Decision Process."

## What Is an MDP?

A **Markov Decision Process** is a mathematical framework for sequential decision-making. It has five components:

| Component | Symbol | Meaning |
|---|---|---|
| States | S | All possible situations the agent can be in |
| Actions | A | All possible things the agent can do |
| Transition function | P(s'|s,a) | Probability of reaching state s' from state s after action a |
| Reward function | R(s,a,s') | Reward received for transitioning from s to s' via action a |
| Discount factor | γ | How much future rewards are worth |

Together: MDP = (S, A, P, R, γ)

### Our GridWorld as an MDP

```python
class GridWorldMDP:
    """GridWorld expressed as a formal MDP."""
    
    def __init__(self, size=4):
        self.size = size
        self.n_states = size * size  # 16 states
        self.n_actions = 4           # up, down, left, right
        self.gamma = 0.9
        
        # Terminal states
        self.goal = 3          # state index for (0,3)
        self.traps = [5, 11]   # state indices for (1,1) and (2,3)
        self.terminal_states = [self.goal] + self.traps
        
        # Build transition and reward matrices
        self.P = self._build_transitions()
        self.R = self._build_rewards()
    
    def _state_to_rc(self, s):
        return s // self.size, s % self.size
    
    def _rc_to_state(self, r, c):
        return r * self.size + c
    
    def _build_transitions(self):
        """P[s][a] = list of (probability, next_state) tuples."""
        P = {}
        for s in range(self.n_states):
            P[s] = {}
            for a in range(self.n_actions):
                P[s][a] = self._get_transitions(s, a)
        return P
    
    def _get_transitions(self, s, a):
        """Deterministic transitions for now."""
        if s in self.terminal_states:
            return [(1.0, s)]  # Terminal states loop to themselves
        
        r, c = self._state_to_rc(s)
        
        if a == 0:    # up
            nr, nc = max(0, r-1), c
        elif a == 1:  # down
            nr, nc = min(self.size-1, r+1), c
        elif a == 2:  # left
            nr, nc = r, max(0, c-1)
        elif a == 3:  # right
            nr, nc = r, min(self.size-1, c+1)
        
        next_state = self._rc_to_state(nr, nc)
        return [(1.0, next_state)]  # Deterministic: 100% chance
    
    def _build_rewards(self):
        """R[s][a] = expected reward for taking action a in state s."""
        R = np.zeros((self.n_states, self.n_actions))
        
        for s in range(self.n_states):
            if s in self.terminal_states:
                continue
            for a in range(self.n_actions):
                for prob, next_s in self.P[s][a]:
                    if next_s == self.goal:
                        R[s, a] += prob * 1.0
                    elif next_s in self.traps:
                        R[s, a] += prob * (-1.0)
                    else:
                        R[s, a] += prob * (-0.04)
        return R
```

## The Markov Property

The "Markov" in MDP means: **the future depends only on the current state, not on how you got there.**

```
P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, ..., s_0, a_0) = P(s_{t+1} | s_t, a_t)
```

The history doesn't matter. Only the present state matters for predicting the future.

Is this realistic? For our grid world, yes — the agent's position is all you need to know. It doesn't matter whether it arrived from the left or from below.

When is it *not* Markov? When the state doesn't capture everything relevant:
- A game where the enemy's behavior depends on what happened 10 turns ago
- A stock market where price depends on trends, not just current price
- Any situation with hidden information

When the Markov property doesn't hold, you either:
1. Expand the state to include the relevant history (e.g., last N positions)
2. Use memory-based architectures (LSTMs, transformers) — much later

For now, our environments are Markov.

## Deterministic vs Stochastic Transitions

Our grid world is **deterministic** — action "right" always moves right. Real environments are often **stochastic**:

```python
def _get_stochastic_transitions(self, s, a, slip_prob=0.1):
    """
    With probability (1 - slip_prob), move in intended direction.
    With probability slip_prob, slip to a perpendicular direction.
    """
    if s in self.terminal_states:
        return [(1.0, s)]
    
    # Intended direction
    intended = self._move(s, a)
    
    # Perpendicular directions (slip)
    if a in [0, 1]:  # up/down → might slip left/right
        slip_actions = [2, 3]
    else:            # left/right → might slip up/down
        slip_actions = [0, 1]
    
    transitions = [(1 - slip_prob, intended)]
    for slip_a in slip_actions:
        slip_state = self._move(s, slip_a)
        transitions.append((slip_prob / 2, slip_state))
    
    return transitions
```

With 10% slip probability, the agent might slide sideways when trying to move forward. This makes planning harder — you can't guarantee outcomes. The agent must account for uncertainty.

The classic "Frozen Lake" environment in Gymnasium uses this: the ice is slippery, so you don't always go where you intend.

## Policies

A **policy** π maps states to actions. It's the agent's complete strategy.

```python
# Deterministic policy: one action per state
policy = {
    0: 'right', 1: 'right', 2: 'right', 3: 'stay',
    4: 'up',    5: 'stay',  6: 'up',    7: 'up',
    8: 'up',    9: 'right', 10: 'up',   11: 'stay',
    12: 'up',   13: 'right', 14: 'right', 15: 'up'
}

# Stochastic policy: probability distribution over actions per state
stochastic_policy = {
    0: [0.1, 0.1, 0.1, 0.7],  # 70% right, 10% each other
    # ...
}
```

The **optimal policy** π* is the policy that maximizes expected return from every state. Finding it is the goal of RL.

## Value Functions

How good is a state? How good is an action in a state? Value functions answer these questions.

### State-Value Function V^π(s)

"If I'm in state s and follow policy π, what's my expected return?"

```
V^π(s) = E[G_t | S_t = s, π]
       = E[r_{t+1} + γ·r_{t+2} + γ²·r_{t+3} + ... | S_t = s, π]
```

### Action-Value Function Q^π(s, a)

"If I'm in state s, take action a, then follow policy π, what's my expected return?"

```
Q^π(s, a) = E[G_t | S_t = s, A_t = a, π]
```

The relationship: V^π(s) = Q^π(s, π(s)) for deterministic policies.

### Computing V for a Simple Policy

```python
def evaluate_policy_simulation(mdp, policy, episodes=10000, max_steps=100):
    """Estimate V(s) by running the policy many times."""
    state_returns = {s: [] for s in range(mdp.n_states)}
    
    for ep in range(episodes):
        # Random start state (not terminal)
        s = np.random.choice([i for i in range(mdp.n_states) 
                              if i not in mdp.terminal_states])
        start_state = s
        rewards = []
        
        for step in range(max_steps):
            if s in mdp.terminal_states:
                break
            a = policy[s]
            # Sample next state from transitions
            probs = [p for p, _ in mdp.P[s][a]]
            states = [ns for _, ns in mdp.P[s][a]]
            s = np.random.choice(states, p=probs)
            rewards.append(mdp.R[start_state, a] if step == 0 
                          else mdp.R[s, a] if s not in mdp.terminal_states else 0)
        
        # Compute discounted return
        G = 0
        for r in reversed(rewards):
            G = r + mdp.gamma * G
        state_returns[start_state].append(G)
    
    # Average returns per state
    V = np.zeros(mdp.n_states)
    for s in range(mdp.n_states):
        if state_returns[s]:
            V[s] = np.mean(state_returns[s])
    return V
```

This works but it's slow — we need thousands of episodes to get good estimates. In Chapter 4, we'll compute V exactly using the structure of the MDP.

## The Bellman Equation

The key insight: value functions have a recursive structure.

The value of a state = immediate reward + discounted value of the next state:

```
V^π(s) = Σ_a π(a|s) · Σ_s' P(s'|s,a) · [R(s,a,s') + γ · V^π(s')]
```

In English: "The value of being here = what I expect to get now + γ × the value of where I end up."

For our deterministic grid world with a deterministic policy:

```
V^π(s) = R(s, π(s)) + γ · V^π(next_state)
```

This is the **Bellman equation** — the foundation of almost every RL algorithm.

```python
def bellman_equation_example():
    """Show the Bellman equation for one state."""
    # State 12 (bottom-left, the start)
    # Policy says: go right → state 13
    # Reward for moving: -0.04
    # V(13) = let's say 0.5 (we'd compute this too)
    
    gamma = 0.9
    reward = -0.04
    V_next = 0.5
    
    V_12 = reward + gamma * V_next
    print(f"V(12) = {reward} + {gamma} × {V_next} = {V_12}")
    # V(12) = -0.04 + 0.9 × 0.5 = 0.41
```

The Bellman equation turns the problem of computing values (which requires simulating entire episodes) into a system of equations (one per state) that can be solved directly.

## The Bellman Optimality Equation

For the *optimal* policy:

```
V*(s) = max_a Σ_s' P(s'|s,a) · [R(s,a,s') + γ · V*(s')]
```

"The optimal value of a state = the best action's immediate reward + γ × the optimal value of where that action leads."

And for Q*:

```
Q*(s,a) = Σ_s' P(s'|s,a) · [R(s,a,s') + γ · max_a' Q*(s',a')]
```

If we can solve these equations, we have the optimal policy: just pick the action that maximizes Q*(s,a) in each state.

## Why This Matters

The MDP framework gives us:

1. **A formal language** — states, actions, transitions, rewards, policies, values
2. **The Bellman equation** — a recursive relationship that algorithms can exploit
3. **A clear goal** — find the policy that maximizes expected return from every state
4. **A separation** — the environment (MDP) vs the agent (policy)

With this framework, we can now ask: "If we know the MDP (all transitions and rewards), can we compute the optimal policy directly?"

The answer is yes. That's dynamic programming.

## Mira's Concern

Mira: "Wait — you're saying the agent needs to know all the transition probabilities? We're still designing the game. The rules change every week."

You: "That's the thing. Dynamic programming needs a perfect model. It's useful for understanding the theory and for environments where we know the rules. But for the real game — where rules change and the state space is huge — we'll need model-free methods. Those come in Chapters 5-8."

Mira: "So why learn dynamic programming at all?"

You: "Because it shows us what the optimal solution looks like. It's the ceiling. And the ideas — bootstrapping, iterating on value estimates — show up in every algorithm after it."

## What You Learned

- **MDP** — the formal framework: (States, Actions, Transitions, Rewards, γ)
- **Markov property** — the future depends only on the present state
- **Stochastic transitions** — actions don't always lead where you expect
- **Policy** — a mapping from states to actions (the agent's strategy)
- **Value functions** — V(s) for states, Q(s,a) for state-action pairs
- **Bellman equation** — V(s) = R + γ·V(next) — the recursive structure of value
- **Bellman optimality equation** — the version for the best possible policy
- **Model-based vs model-free** — knowing transitions enables planning; not knowing them requires learning

The MDP is defined. The Bellman equation gives us a recursive structure. If we know the full MDP, we can solve for the optimal policy without any trial-and-error learning at all.

That's dynamic programming — computing optimal policies from perfect knowledge.

---

[← Chapter 2: Exploration](chapter-02-exploration.md) | [Chapter 4: Dynamic Programming →](chapter-04-dynamic-programming.md)
