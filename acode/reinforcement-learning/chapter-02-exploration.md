# Chapter 2: Exploration vs Exploitation

[← Chapter 1: The Reward Signal](chapter-01-reward-signal.md) | [Chapter 3: Markov Decision Processes →](chapter-03-mdp.md)

---

## The Problem

Your agent now understands rewards. You give it a simple rule: "remember which action gave the best reward last time, and do that again."

```python
class GreedyAgent:
    def __init__(self, n_actions=4):
        self.action_values = np.zeros(n_actions)
        self.action_counts = np.zeros(n_actions)
    
    def choose_action(self, state):
        return np.argmax(self.action_values)
    
    def learn(self, state, action, reward, next_state, done):
        self.action_counts[action] += 1
        # Running average of rewards per action
        n = self.action_counts[action]
        self.action_values[action] += (reward - self.action_values[action]) / n
```

You run it. The agent tries "up" first, gets 0 reward (empty square), and decides "up" is the best action it's ever seen. It goes up forever. It never tries right, never discovers the goal.

QA Tanya: "It's stuck in the top-left corner. Just... vibrating."

The agent is **exploiting** — repeating the best-known action. But it never **explored** — it never tried enough alternatives to find something better.

This is the exploration-exploitation dilemma. Exploit too much, you miss better options. Explore too much, you waste time on bad actions you already know are bad.

## The Multi-Armed Bandit

Before we solve this in GridWorld, let's isolate the problem. Strip away movement, states, and grids. Just actions and rewards.

A **multi-armed bandit** is a row of slot machines. Each machine pays out with a different (unknown) average. You have N pulls. Maximize total payout.

```python
class MultiArmedBandit:
    def __init__(self, n_arms=5):
        # True reward probabilities (unknown to the agent)
        self.true_values = np.random.randn(n_arms)
        self.n_arms = n_arms
    
    def pull(self, arm):
        """Pull an arm. Returns reward drawn from N(true_value, 1)."""
        return np.random.randn() + self.true_values[arm]
    
    def optimal_arm(self):
        return np.argmax(self.true_values)
```

Each arm has a true average payout. The agent doesn't know these values — it has to estimate them by pulling arms and observing rewards.

## Strategy 1: Pure Greedy (Exploit Only)

```python
def run_greedy(bandit, steps=1000):
    estimates = np.zeros(bandit.n_arms)
    counts = np.zeros(bandit.n_arms)
    rewards = []
    
    for step in range(steps):
        # Always pick the arm with highest estimated value
        arm = np.argmax(estimates)
        reward = bandit.pull(arm)
        
        # Update estimate (incremental mean)
        counts[arm] += 1
        estimates[arm] += (reward - estimates[arm]) / counts[arm]
        rewards.append(reward)
    
    return rewards
```

Problem: The agent pulls each arm once (or just the first arm), gets noisy rewards, and locks onto whichever arm happened to give the highest first pull. With probability ~80%, it locks onto a suboptimal arm and never recovers.

```
True values:   [0.2, 1.5, -0.3, 0.8, 0.1]
First pulls:   [0.9, 0.3, -1.1, 0.4, 0.7]  ← noisy!
Greedy picks:  arm 0 forever (first pull was lucky)
Optimal arm:   arm 1 (true value 1.5)
```

## Strategy 2: Pure Random (Explore Only)

```python
def run_random(bandit, steps=1000):
    rewards = []
    for step in range(steps):
        arm = np.random.randint(bandit.n_arms)
        reward = bandit.pull(arm)
        rewards.append(reward)
    return rewards
```

The agent tries everything equally. It never gets stuck. But it also never focuses on the best arm. Average reward converges to the mean of all arms — much worse than the best arm.

## Strategy 3: Epsilon-Greedy (The Balance)

```python
def run_epsilon_greedy(bandit, steps=1000, epsilon=0.1):
    estimates = np.zeros(bandit.n_arms)
    counts = np.zeros(bandit.n_arms)
    rewards = []
    
    for step in range(steps):
        if np.random.random() < epsilon:
            # Explore: pick a random arm
            arm = np.random.randint(bandit.n_arms)
        else:
            # Exploit: pick the best-known arm
            arm = np.argmax(estimates)
        
        reward = bandit.pull(arm)
        counts[arm] += 1
        estimates[arm] += (reward - estimates[arm]) / counts[arm]
        rewards.append(reward)
    
    return rewards
```

With probability ε, explore randomly. With probability 1-ε, exploit the best-known action.

This is **epsilon-greedy** — the simplest exploration strategy that actually works.

### Choosing Epsilon

| ε | Behavior |
|---|---|
| 0.0 | Pure greedy — no exploration |
| 0.01 | Mostly exploit, rare exploration |
| 0.1 | Explore 10% of the time — good default |
| 0.3 | Heavy exploration — good early, wasteful later |
| 1.0 | Pure random — no exploitation |

```python
def compare_strategies(n_runs=200, steps=1000):
    results = {'greedy': [], 'random': [], 'eps_0.01': [], 'eps_0.1': [], 'eps_0.3': []}
    
    for run in range(n_runs):
        bandit = MultiArmedBandit(n_arms=10)
        
        results['greedy'].append(run_greedy(bandit, steps))
        results['random'].append(run_random(bandit, steps))
        results['eps_0.01'].append(run_epsilon_greedy(bandit, steps, epsilon=0.01))
        results['eps_0.1'].append(run_epsilon_greedy(bandit, steps, epsilon=0.1))
        results['eps_0.3'].append(run_epsilon_greedy(bandit, steps, epsilon=0.3))
    
    # Plot average reward over time for each strategy
    plt.figure(figsize=(10, 5))
    for name, runs in results.items():
        avg = np.mean(runs, axis=0)
        plt.plot(avg, label=name)
    plt.xlabel('Step')
    plt.ylabel('Average Reward')
    plt.title('Exploration Strategies on 10-Armed Bandit')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

Typical result:
- **Greedy** starts fast but plateaus low (stuck on suboptimal arm)
- **Random** is flat and mediocre
- **ε=0.1** climbs steadily and reaches near-optimal performance
- **ε=0.01** climbs slower but eventually overtakes ε=0.1 (less wasted exploration)
- **ε=0.3** learns fast initially but wastes too much time exploring later

## Strategy 4: Decaying Epsilon

Why not start with high exploration and reduce it over time?

```python
def run_decaying_epsilon(bandit, steps=1000, epsilon_start=1.0, epsilon_end=0.01, decay=0.995):
    estimates = np.zeros(bandit.n_arms)
    counts = np.zeros(bandit.n_arms)
    rewards = []
    epsilon = epsilon_start
    
    for step in range(steps):
        if np.random.random() < epsilon:
            arm = np.random.randint(bandit.n_arms)
        else:
            arm = np.argmax(estimates)
        
        reward = bandit.pull(arm)
        counts[arm] += 1
        estimates[arm] += (reward - estimates[arm]) / counts[arm]
        rewards.append(reward)
        
        # Decay epsilon
        epsilon = max(epsilon_end, epsilon * decay)
    
    return rewards
```

This gives you the best of both worlds: heavy exploration early (when you know nothing) and heavy exploitation later (when you've found the best arm).

## Strategy 5: Upper Confidence Bound (UCB)

Epsilon-greedy explores randomly — it's equally likely to re-try a well-known bad arm as an unknown arm. That's wasteful.

**UCB** explores *intelligently* — it prefers arms that are uncertain (haven't been tried much):

```python
def run_ucb(bandit, steps=1000, c=2.0):
    estimates = np.zeros(bandit.n_arms)
    counts = np.zeros(bandit.n_arms)
    rewards = []
    
    # Pull each arm once first
    for arm in range(bandit.n_arms):
        reward = bandit.pull(arm)
        counts[arm] = 1
        estimates[arm] = reward
        rewards.append(reward)
    
    for step in range(bandit.n_arms, steps):
        # UCB formula: estimated value + exploration bonus
        ucb_values = estimates + c * np.sqrt(np.log(step) / counts)
        arm = np.argmax(ucb_values)
        
        reward = bandit.pull(arm)
        counts[arm] += 1
        estimates[arm] += (reward - estimates[arm]) / counts[arm]
        rewards.append(reward)
    
    return rewards
```

The exploration bonus `c * sqrt(ln(t) / N(a))` is large when:
- The arm hasn't been pulled much (N(a) is small)
- Many total steps have passed (ln(t) is large)

This means: "If I haven't tried this arm in a while, maybe I should check if it's better than I think."

UCB typically outperforms epsilon-greedy because it never wastes exploration on arms it already knows are bad.

## Strategy 6: Optimistic Initialization

A clever trick: initialize all estimates high.

```python
def run_optimistic(bandit, steps=1000, initial_value=5.0):
    estimates = np.full(bandit.n_arms, initial_value)  # Start optimistic
    counts = np.zeros(bandit.n_arms)
    rewards = []
    
    for step in range(steps):
        arm = np.argmax(estimates)  # Pure greedy!
        reward = bandit.pull(arm)
        
        counts[arm] += 1
        estimates[arm] += (reward - estimates[arm]) / counts[arm]
        rewards.append(reward)
    
    return rewards
```

Every arm starts with an estimate of 5.0 (much higher than any true value). The agent greedily picks the highest estimate, gets a real reward (much lower than 5.0), and the estimate drops. Now another arm has the highest estimate. The agent naturally cycles through all arms until estimates converge to true values.

No epsilon needed. Exploration emerges from optimism.

Downside: only works at the start. If the environment changes later, the agent won't re-explore.

## Back to GridWorld: Epsilon-Greedy Agent

Let's apply epsilon-greedy to our grid world. But there's a complication: in the bandit problem, there's one state. In GridWorld, there are 16 states. The agent needs to learn which action is best *in each state*.

```python
class EpsilonGreedyGridAgent:
    def __init__(self, n_states=16, n_actions=4, epsilon=0.1, alpha=0.1):
        self.epsilon = epsilon
        self.alpha = alpha
        # Q-table: estimated value of each action in each state
        self.q_table = np.zeros((n_states, n_actions))
        self.episode_returns = []
    
    def state_to_index(self, state):
        """Convert (row, col) to a single index."""
        return state[0] * 4 + state[1]
    
    def choose_action(self, state):
        s = self.state_to_index(state)
        if np.random.random() < self.epsilon:
            return np.random.randint(4)  # Explore
        else:
            return np.argmax(self.q_table[s])  # Exploit
    
    def learn(self, state, action, reward, next_state, done):
        s = self.state_to_index(state)
        # Simple update: move estimate toward observed reward
        # (This is a simplified version — proper Q-learning comes in Ch 7)
        target = reward
        if not done:
            ns = self.state_to_index(next_state)
            target += 0.9 * np.max(self.q_table[ns])  # Look ahead
        
        self.q_table[s, action] += self.alpha * (target - self.q_table[s, action])
```

```python
def train_epsilon_greedy(episodes=500, epsilon=0.1):
    env = GridWorld()
    agent = EpsilonGreedyGridAgent(epsilon=epsilon)
    
    for ep in range(episodes):
        state = env.reset()
        episode_reward = 0
        
        for step in range(100):
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            
            # Add time penalty
            if not done:
                reward = -0.04
            
            agent.learn(state, action, reward, next_state, done)
            state = next_state
            episode_reward += reward
            
            if done:
                break
        
        agent.episode_returns.append(episode_reward)
    
    return agent

agent = train_epsilon_greedy()
print(f"Final 50-episode average: {np.mean(agent.episode_returns[-50:]):.3f}")
```

Result: The agent learns to reach the goal ~85% of the time after 500 episodes. Massive improvement over the random baseline (18%).

But it still fails 15% of the time — because ε=0.1 means it takes a random (possibly fatal) action 10% of the time, even after it's learned the optimal path.

## The Exploration-Exploitation Tradeoff Visualized

```python
def visualize_exploration(agent, env):
    """Show the learned policy as arrows on the grid."""
    action_symbols = ['↑', '↓', '←', '→']
    
    print("Learned Policy:")
    for r in range(4):
        row_str = ""
        for c in range(4):
            if (r, c) == env.goal:
                row_str += " G "
            elif (r, c) in env.traps:
                row_str += " X "
            else:
                s = r * 4 + c
                best_action = np.argmax(agent.q_table[s])
                row_str += f" {action_symbols[best_action]} "
        print(row_str)

visualize_exploration(agent, GridWorld())
```

Output:
```
Learned Policy:
 →  →  →  G 
 ↑  X  ↑  ↑ 
 ↑  →  ↑  X 
 ↑  →  →  ↑ 
```

The agent has learned to navigate around traps and reach the goal. The arrows show the greedy policy — what the agent would do without exploration.

## Jonas Checks In

Jonas: "So it's learning. 85% success. But it still randomly walks into traps?"

You: "That's the epsilon. It explores 10% of the time, even after it knows the optimal path. We could decay epsilon to zero, but then it can't adapt if the environment changes."

Jonas: "Can it plan ahead? Like, know that going right leads to a trap two steps away?"

You: "Right now it's learning action values through trial and error. It doesn't have a model of the world — it doesn't know what happens before it tries. For that, we need to formalize what 'states' and 'transitions' mean. That's the Markov Decision Process."

## What You Learned

- **Exploration-exploitation dilemma** — try new things vs repeat what works
- **Pure greedy** — locks onto suboptimal actions, never recovers
- **Epsilon-greedy** — explore randomly ε% of the time; simple and effective
- **Decaying epsilon** — explore more early, exploit more later
- **UCB** — explore uncertain actions preferentially; smarter than random exploration
- **Optimistic initialization** — high initial estimates force natural exploration
- **Q-table** — stores estimated value of each action in each state
- **Result** — epsilon-greedy agent reaches 85% success vs 18% random baseline

The agent can learn from rewards and balance exploration with exploitation. But we've been informal about what "states" and "transitions" mean. The agent doesn't know the rules of the world — it just bumps into things and remembers what happened.

To build better algorithms, we need a formal framework for sequential decision-making.

---

[← Chapter 1: The Reward Signal](chapter-01-reward-signal.md) | [Chapter 3: Markov Decision Processes →](chapter-03-mdp.md)
