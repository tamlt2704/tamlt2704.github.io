# Chapter 5: Monte Carlo Methods

[← Chapter 4: Dynamic Programming](chapter-04-dynamic-programming.md) | [Chapter 6: Temporal Difference Learning →](chapter-06-td-learning.md)

---

## The Problem

Dynamic programming gave us the optimal policy for the 4×4 grid — but it required knowing every transition probability. Now Mira changes the game: enemies move unpredictably, terrain effects are random, and the fog of war hides parts of the map.

You don't have a model anymore. You can't call `mdp.P[s][a]` because you don't know the transition probabilities. All you can do is play episodes and observe what happens.

Jonas: "So we're back to trial and error?"

You: "Yes, but structured trial and error. We play complete episodes, record the rewards, and compute returns. Then we average the returns for each state to estimate value functions. No model needed."

This is **Monte Carlo** (MC) learning — estimating values from sampled episodes.

## The Core Idea

1. Run an episode following some policy
2. Record the sequence: S₀, A₀, R₁, S₁, A₁, R₂, ..., Sₜ
3. For each state visited, compute the return (discounted sum of future rewards)
4. Average the returns across many episodes

```python
def monte_carlo_prediction(env, policy, episodes=5000, gamma=0.9):
    """
    Estimate V^π using Monte Carlo: average returns from episodes.
    """
    returns = {s: [] for s in range(env.n_states)}
    V = np.zeros(env.n_states)
    
    for ep in range(episodes):
        # Generate an episode
        episode = generate_episode(env, policy)
        
        # Compute returns for each state visited
        G = 0
        for t in reversed(range(len(episode))):
            state, action, reward = episode[t]
            G = reward + gamma * G
            
            # First-visit MC: only count the first time we visit each state
            states_before = [episode[i][0] for i in range(t)]
            if state not in states_before:
                returns[state].append(G)
                V[state] = np.mean(returns[state])
    
    return V

def generate_episode(env, policy, max_steps=100):
    """Run one episode, return list of (state, action, reward) tuples."""
    episode = []
    state = env.reset()
    
    for step in range(max_steps):
        action = policy[state]
        next_state, reward, done = env.step(state, action)
        episode.append((state, action, reward))
        
        if done:
            break
        state = next_state
    
    return episode
```

## First-Visit vs Every-Visit MC

A state might be visited multiple times in one episode (the agent loops back). Two variants:

**First-visit MC**: Only use the return from the *first* time a state is visited in each episode.

**Every-visit MC**: Use the return from *every* visit to a state.

```python
def first_visit_mc(env, policy, episodes=5000, gamma=0.9):
    """First-visit: count each state only once per episode."""
    returns = {s: [] for s in range(env.n_states)}
    
    for ep in range(episodes):
        episode = generate_episode(env, policy)
        visited = set()
        G = 0
        
        for t in reversed(range(len(episode))):
            state, action, reward = episode[t]
            G = reward + gamma * G
            
            if state not in visited:
                visited.add(state)
                returns[state].append(G)
    
    V = {s: np.mean(returns[s]) if returns[s] else 0 for s in range(env.n_states)}
    return V

def every_visit_mc(env, policy, episodes=5000, gamma=0.9):
    """Every-visit: count all visits to each state."""
    returns = {s: [] for s in range(env.n_states)}
    
    for ep in range(episodes):
        episode = generate_episode(env, policy)
        G = 0
        
        for t in reversed(range(len(episode))):
            state, action, reward = episode[t]
            G = reward + gamma * G
            returns[state].append(G)
    
    V = {s: np.mean(returns[s]) if returns[s] else 0 for s in range(env.n_states)}
    return V
```

Both converge to the true V^π. First-visit has nicer theoretical properties (unbiased). Every-visit uses more data per episode (lower variance in practice).

## MC Control: Learning the Optimal Policy

Prediction (estimating V) is useful, but we want **control** — finding the optimal policy.

Problem: V(s) alone isn't enough to improve the policy. To pick the best action, we need Q(s,a) — the value of each action in each state.

```python
def mc_control_epsilon_greedy(env, episodes=10000, gamma=0.9, epsilon=0.1):
    """
    Monte Carlo control with epsilon-greedy exploration.
    Learns Q(s,a) and improves the policy simultaneously.
    """
    Q = np.zeros((env.n_states, env.n_actions))
    returns = {(s, a): [] for s in range(env.n_states) for a in range(env.n_actions)}
    
    for ep in range(episodes):
        # Generate episode using epsilon-greedy policy derived from Q
        episode = generate_episode_epsilon_greedy(env, Q, epsilon)
        
        # Update Q values
        visited = set()
        G = 0
        
        for t in reversed(range(len(episode))):
            state, action, reward = episode[t]
            G = reward + gamma * G
            
            if (state, action) not in visited:
                visited.add((state, action))
                returns[(state, action)].append(G)
                Q[state, action] = np.mean(returns[(state, action)])
    
    # Extract greedy policy
    policy = {s: np.argmax(Q[s]) for s in range(env.n_states)}
    return Q, policy

def generate_episode_epsilon_greedy(env, Q, epsilon, max_steps=100):
    """Generate episode using epsilon-greedy policy from Q."""
    episode = []
    state = env.reset()
    
    for step in range(max_steps):
        # Epsilon-greedy action selection
        if np.random.random() < epsilon:
            action = np.random.randint(env.n_actions)
        else:
            action = np.argmax(Q[state])
        
        next_state, reward, done = env.step(state, action)
        episode.append((state, action, reward))
        
        if done:
            break
        state = next_state
    
    return episode
```

## The Exploration Problem in MC

MC control has a subtle issue: if the policy is deterministic, some state-action pairs might never be visited. You can't estimate Q(s,a) if you never try action a in state s.

Solutions:

### 1. Exploring Starts

Force every episode to start with a random state-action pair:

```python
def mc_exploring_starts(env, episodes=10000, gamma=0.9):
    """MC control with exploring starts — random initial state and action."""
    Q = np.zeros((env.n_states, env.n_actions))
    returns = {(s, a): [] for s in range(env.n_states) for a in range(env.n_actions)}
    
    for ep in range(episodes):
        # Random start state and action
        start_state = np.random.choice([s for s in range(env.n_states) 
                                        if s not in env.terminal_states])
        start_action = np.random.randint(env.n_actions)
        
        # Generate episode from this start
        episode = generate_episode_from(env, Q, start_state, start_action)
        
        # Update Q
        visited = set()
        G = 0
        for t in reversed(range(len(episode))):
            state, action, reward = episode[t]
            G = reward + gamma * G
            if (state, action) not in visited:
                visited.add((state, action))
                returns[(state, action)].append(G)
                Q[state, action] = np.mean(returns[(state, action)])
    
    policy = {s: np.argmax(Q[s]) for s in range(env.n_states)}
    return Q, policy
```

Problem: In real environments, you can't always choose where to start. You can't teleport a game character to an arbitrary position.

### 2. Epsilon-Greedy (On-Policy)

Keep exploring throughout the episode with ε-greedy. This guarantees all state-action pairs are visited eventually. The downside: the learned policy is ε-greedy, not fully greedy. It always has some randomness.

### 3. Off-Policy Learning (Importance Sampling)

Use one policy to explore (behavior policy) and learn about a different policy (target policy):

```python
def mc_off_policy(env, episodes=10000, gamma=0.9):
    """
    Off-policy MC: explore with random policy, learn greedy policy.
    Uses importance sampling to correct for the policy mismatch.
    """
    Q = np.zeros((env.n_states, env.n_actions))
    C = np.zeros((env.n_states, env.n_actions))  # Cumulative weights
    target_policy = {s: np.argmax(Q[s]) for s in range(env.n_states)}
    
    for ep in range(episodes):
        # Behavior policy: random (explores everything)
        episode = generate_random_episode(env)
        
        G = 0
        W = 1.0  # Importance sampling weight
        
        for t in reversed(range(len(episode))):
            state, action, reward = episode[t]
            G = reward + gamma * G
            
            C[state, action] += W
            Q[state, action] += (W / C[state, action]) * (G - Q[state, action])
            
            # Update target policy
            target_policy[state] = np.argmax(Q[state])
            
            # If behavior policy took a different action than target, weight = 0
            if action != target_policy[state]:
                break
            
            # Importance sampling ratio
            # target_policy is deterministic (prob=1 for best action)
            # behavior_policy is uniform (prob=1/n_actions)
            W *= env.n_actions  # = 1.0 / (1/n_actions)
    
    return Q, target_policy
```

Off-policy MC is powerful in theory but has high variance in practice — the importance sampling weights can explode.

## MC vs DP: The Tradeoff

| | Dynamic Programming | Monte Carlo |
|---|---|---|
| Model required? | Yes (full MDP) | No (just episodes) |
| Bootstrapping? | Yes (uses V estimates) | No (uses actual returns) |
| Bias | None (exact computation) | None (unbiased estimates) |
| Variance | None | High (returns are noisy) |
| Convergence | Guaranteed (finite) | Guaranteed (asymptotic) |
| Works online? | No (needs full sweep) | Yes (update after each episode) |

## The Waiting Problem

QA Tanya runs the MC agent on a longer episode: "It played for 200 steps, hit the goal, and... nothing happened. It didn't learn anything until the episode ended."

That's the fundamental limitation of Monte Carlo: **you must wait until the episode ends to compute returns and update values.**

For short episodes (our 4×4 grid, ~6 steps), this is fine. For long episodes (a full game of GridWorld Tactics, ~500 turns), the agent plays an entire game before learning anything from it.

What if we could learn *during* the episode? Update values after every single step?

That's temporal difference learning.

## What You Learned

- **Monte Carlo** — estimate values by averaging returns from complete episodes
- **No model needed** — just play and observe; don't need transition probabilities
- **First-visit vs every-visit** — count states once or multiple times per episode
- **MC control** — learn Q(s,a) to improve the policy
- **Exploration problem** — need to visit all state-action pairs (exploring starts, ε-greedy, off-policy)
- **Off-policy MC** — learn about one policy while following another (importance sampling)
- **The limitation** — must wait until episode ends to learn; high variance from noisy returns

MC methods free us from needing a model. But waiting until the end of an episode is wasteful. The next chapter introduces learning after every single step.

---

[← Chapter 4: Dynamic Programming](chapter-04-dynamic-programming.md) | [Chapter 6: Temporal Difference Learning →](chapter-06-td-learning.md)
