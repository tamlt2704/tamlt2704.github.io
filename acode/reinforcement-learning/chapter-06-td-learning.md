# Chapter 6: Temporal Difference Learning

[← Chapter 5: Monte Carlo Methods](chapter-05-monte-carlo.md) | [Chapter 7: Q-Learning →](chapter-07-q-learning.md)

---

## The Problem

Your Monte Carlo agent learns, but it's painfully slow on longer episodes. Mira's new level has 50+ steps per episode. The agent plays the entire game, then updates. If it made a terrible move on step 3, it doesn't learn from that mistake until step 50.

Jonas: "Can't it learn as it goes? Like, realize immediately that walking into a trap was bad?"

You: "That's exactly what temporal difference learning does. It updates after every single step, using a mix of observed reward and estimated future value."

## The Key Insight: Bootstrapping

Monte Carlo waits for the actual return G:
```
V(s) ← V(s) + α · (G - V(s))
```

But G isn't known until the episode ends. What if we *estimate* G using our current value function?

After one step, we observe reward r and land in state s'. We can estimate:
```
G ≈ r + γ · V(s')
```

This is the **TD target** — the observed reward plus the discounted estimated value of the next state.

The update becomes:
```
V(s) ← V(s) + α · (r + γ·V(s') - V(s))
```

The term `r + γ·V(s') - V(s)` is the **TD error** (δ) — the difference between what we expected and what we got.

## TD(0): The Simplest TD Method

```python
def td_zero_prediction(env, policy, episodes=1000, alpha=0.1, gamma=0.9):
    """
    TD(0): Update V after every step using bootstrapped estimate.
    """
    V = np.zeros(env.n_states)
    
    for ep in range(episodes):
        state = env.reset()
        
        while True:
            action = policy[state]
            next_state, reward, done = env.step(state, action)
            
            # TD update — happens EVERY STEP
            if done:
                td_target = reward  # No next state value (episode over)
            else:
                td_target = reward + gamma * V[next_state]
            
            td_error = td_target - V[state]
            V[state] += alpha * td_error
            
            if done:
                break
            state = next_state
    
    return V
```

Compare with MC:
- MC: play entire episode → compute returns → update all visited states
- TD(0): take one step → update immediately → continue

## Why TD Works: The Intuition

Imagine you're driving to work. Your usual commute is 30 minutes.

**Monte Carlo approach**: Drive all the way to work. If it took 45 minutes, update your estimate. You learn nothing until you arrive.

**TD approach**: After 5 minutes, you hit unexpected traffic. You estimate: "5 minutes so far + probably 35 more = 40 minutes total." You immediately update your estimate of this route. You don't need to finish the drive to know it's going badly.

TD uses partial information (what happened so far + what you expect) to update immediately.

## TD vs MC: A Direct Comparison

```python
def compare_td_mc(env, policy, true_V, episodes=500, runs=100):
    """Compare TD(0) and MC learning speed."""
    td_errors = np.zeros((runs, episodes))
    mc_errors = np.zeros((runs, episodes))
    
    for run in range(runs):
        V_td = np.zeros(env.n_states)
        V_mc = np.zeros(env.n_states)
        
        for ep in range(episodes):
            # --- TD(0) ---
            state = env.reset()
            while True:
                action = policy[state]
                next_state, reward, done = env.step(state, action)
                
                td_target = reward + (0 if done else 0.9 * V_td[next_state])
                V_td[state] += 0.1 * (td_target - V_td[state])
                
                if done:
                    break
                state = next_state
            
            # --- MC (first-visit) ---
            episode = generate_episode(env, policy)
            G = 0
            visited = set()
            for t in reversed(range(len(episode))):
                s, a, r = episode[t]
                G = r + 0.9 * G
                if s not in visited:
                    visited.add(s)
                    V_mc[s] += 0.1 * (G - V_mc[s])
            
            # Track RMS error
            td_errors[run, ep] = np.sqrt(np.mean((V_td - true_V) ** 2))
            mc_errors[run, ep] = np.sqrt(np.mean((V_mc - true_V) ** 2))
    
    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(np.mean(td_errors, axis=0), label='TD(0)')
    plt.plot(np.mean(mc_errors, axis=0), label='MC')
    plt.xlabel('Episodes')
    plt.ylabel('RMS Error')
    plt.title('TD(0) vs MC: Learning Speed')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

Typical result: TD(0) converges faster than MC, especially in the early episodes. TD makes better use of each step of experience.

## The Bias-Variance Tradeoff

| | MC | TD(0) |
|---|---|---|
| Target | G (actual return) | r + γ·V(s') (estimate) |
| Bias | Unbiased | Biased (V(s') might be wrong) |
| Variance | High (G is noisy) | Low (single step + estimate) |
| Convergence | To true V^π | To true V^π (with appropriate α) |

TD is biased because it uses V(s') — which might be wrong early in training. But it has lower variance because it doesn't depend on the entire sequence of future rewards.

In practice, the lower variance wins. TD learns faster.

## TD Error as a Learning Signal

The TD error δ = r + γ·V(s') - V(s) tells you something important:

- **δ > 0**: "This was better than expected." The transition gave more value than predicted.
- **δ < 0**: "This was worse than expected." The transition gave less value than predicted.
- **δ = 0**: "This was exactly as expected." No surprise, no learning.

```python
def track_td_errors(env, policy, episodes=200, alpha=0.1, gamma=0.9):
    """Track TD errors over training to see learning progress."""
    V = np.zeros(env.n_states)
    all_td_errors = []
    
    for ep in range(episodes):
        state = env.reset()
        episode_errors = []
        
        while True:
            action = policy[state]
            next_state, reward, done = env.step(state, action)
            
            td_target = reward + (0 if done else gamma * V[next_state])
            td_error = td_target - V[state]
            V[state] += alpha * td_error
            
            episode_errors.append(abs(td_error))
            
            if done:
                break
            state = next_state
        
        all_td_errors.append(np.mean(episode_errors))
    
    return all_td_errors
```

As the agent learns, TD errors shrink toward zero — the agent's predictions become accurate.

## The Learning Rate α

The learning rate controls how much each update changes V:

```python
V[s] += alpha * td_error
```

| α | Behavior |
|---|---|
| 0.01 | Very slow learning, stable |
| 0.1 | Good default, balances speed and stability |
| 0.5 | Fast but noisy |
| 1.0 | Fully replace old estimate with new target |

Too high: values oscillate wildly. Too low: takes forever to converge.

```python
def compare_learning_rates(env, policy, true_V, alphas=[0.01, 0.05, 0.1, 0.3]):
    """Show effect of different learning rates."""
    plt.figure(figsize=(10, 5))
    
    for alpha in alphas:
        V = np.zeros(env.n_states)
        errors = []
        
        for ep in range(500):
            state = env.reset()
            while True:
                action = policy[state]
                next_state, reward, done = env.step(state, action)
                td_target = reward + (0 if done else 0.9 * V[next_state])
                V[state] += alpha * (td_target - V[state])
                if done:
                    break
                state = next_state
            errors.append(np.sqrt(np.mean((V - true_V) ** 2)))
        
        plt.plot(errors, label=f'α={alpha}')
    
    plt.xlabel('Episodes')
    plt.ylabel('RMS Error')
    plt.title('Effect of Learning Rate')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

## TD for Control: SARSA Preview

TD(0) estimates V^π — the value of states under a fixed policy. But we want to learn the *optimal* policy. For that, we need to estimate Q(s,a) and improve the policy.

Two approaches:
- **SARSA** (on-policy): Learn Q for the policy you're following (Chapter 8)
- **Q-learning** (off-policy): Learn Q for the optimal policy regardless of what you're doing (Chapter 7)

Both use TD updates on Q instead of V:

```python
# TD update for Q (preview)
Q[s, a] += alpha * (reward + gamma * Q[s', a'] - Q[s, a])  # SARSA
Q[s, a] += alpha * (reward + gamma * max(Q[s']) - Q[s, a])  # Q-learning
```

The difference: SARSA uses the *actual* next action a'. Q-learning uses the *best* next action. This distinction has profound consequences — Chapter 7 and 8 explore them.

## Eligibility Traces: TD(λ) — A Bridge Between MC and TD

TD(0) looks one step ahead. MC looks all the way to the end. What about looking N steps ahead?

**N-step TD**:
```
G_t^(n) = r_t + γ·r_{t+1} + γ²·r_{t+2} + ... + γⁿ·V(s_{t+n})
```

- n=1: TD(0) — one step of real reward, then bootstrap
- n=∞: MC — all real rewards, no bootstrapping

**TD(λ)** averages over all n-step returns, weighted by λ:

```python
def td_lambda(env, policy, episodes=1000, alpha=0.1, gamma=0.9, lam=0.8):
    """
    TD(λ) with eligibility traces.
    λ=0 → TD(0), λ=1 → MC-like behavior.
    """
    V = np.zeros(env.n_states)
    
    for ep in range(episodes):
        state = env.reset()
        # Eligibility trace: how "responsible" each state is for current error
        E = np.zeros(env.n_states)
        
        while True:
            action = policy[state]
            next_state, reward, done = env.step(state, action)
            
            td_target = reward + (0 if done else gamma * V[next_state])
            td_error = td_target - V[state]
            
            # Increment trace for current state
            E[state] += 1
            
            # Update ALL states proportional to their eligibility
            V += alpha * td_error * E
            
            # Decay traces
            E *= gamma * lam
            
            if done:
                break
            state = next_state
    
    return V
```

The eligibility trace E(s) tracks how recently and frequently each state was visited. When a TD error occurs, all recently-visited states get updated — not just the current one. This propagates information backward through the episode much faster.

| λ | Behavior |
|---|---|
| 0 | Pure TD(0) — only update current state |
| 0.5 | Moderate trace — update recent states |
| 0.9 | Long trace — update many past states |
| 1.0 | Equivalent to MC (with appropriate α) |

## QA Tanya's Test

Tanya runs the TD agent on a tricky level where the trap is right next to the goal:

```
┌───┬───┬───┬───┐
│ . │ . │ X │ G │
├───┼───┼───┼───┤
│ . │ . │ . │ . │
├───┼───┼───┼───┤
│ . │ . │ . │ . │
├───┼───┼───┼───┤
│ A │ . │ . │ . │
└───┴───┴───┴───┘
```

The TD agent learns quickly that the state next to the trap has low value — even though the goal is just one step further. It learns to approach the goal from below (row 1, col 3) rather than from the left (row 0, col 2 → trap).

Tanya: "It figured out the safe path in 100 episodes. The MC agent took 800."

TD's step-by-step updates propagate danger signals faster. When the agent hits the trap, the TD error immediately lowers the value of the adjacent state. MC would need to complete many more episodes to average out the returns.

## What You Learned

- **TD(0)** — update V after every step using r + γ·V(s') as the target
- **Bootstrapping** — using estimated values (V(s')) instead of waiting for actual returns
- **TD error** — δ = r + γ·V(s') - V(s); the surprise signal that drives learning
- **Bias-variance tradeoff** — TD is biased but low variance; MC is unbiased but high variance
- **Learning rate α** — controls update speed; 0.1 is a good default
- **TD(λ)** — eligibility traces bridge TD(0) and MC; λ controls the tradeoff
- **TD learns faster** — step-by-step updates propagate information more efficiently

TD gives us the speed of learning after every step. But we're still only estimating state values V(s). To find the optimal policy, we need action values Q(s,a).

The next chapter introduces Q-learning — the algorithm that learns the optimal policy directly, even while exploring.

---

[← Chapter 5: Monte Carlo Methods](chapter-05-monte-carlo.md) | [Chapter 7: Q-Learning →](chapter-07-q-learning.md)
