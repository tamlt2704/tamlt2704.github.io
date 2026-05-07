# Chapter 8: SARSA

[← Chapter 7: Q-Learning](chapter-07-q-learning.md) | [Chapter 9: Function Approximation →](chapter-09-function-approximation.md)

---

## The Problem

Jonas runs Q-learning on a new level — the Cliff Walk:

```
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │ . │
├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│ S │ C │ C │ C │ C │ C │ C │ C │ C │ C │ C │ G │
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘

S = Start, G = Goal, C = Cliff (reward -100, reset to start)
Each step: reward -1
```

The optimal path goes right along the cliff edge — shortest distance. Q-learning finds this path. But with ε=0.1 exploration, the agent occasionally steps off the cliff. The actual performance during training is terrible — frequent -100 penalties.

QA Tanya: "The Q-learning agent keeps falling off the cliff. It knows the optimal path but it can't stop exploring into danger."

The issue: Q-learning learns the *optimal* policy (walk along the edge) but *follows* an ε-greedy policy (which sometimes steps randomly off the cliff). It doesn't account for its own exploration mistakes.

## SARSA: On-Policy TD Control

**SARSA** (State-Action-Reward-State-Action) is the on-policy alternative to Q-learning. Instead of using `max Q(s', a')`, it uses the actual next action `Q(s', a')`:

```
Q(s, a) ← Q(s, a) + α · [r + γ · Q(s', a') - Q(s, a)]
```

The name comes from the quintuple used in each update: (S, A, R, S', A').

```python
class SARSAAgent:
    def __init__(self, n_states, n_actions=4, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.Q = np.zeros((n_states, n_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.episode_returns = []
    
    def choose_action(self, state):
        """Epsilon-greedy action selection."""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.Q.shape[1])
        return np.argmax(self.Q[state])
    
    def learn(self, state, action, reward, next_state, next_action, done):
        """SARSA update: use actual next action, not max."""
        if done:
            td_target = reward
        else:
            td_target = reward + self.gamma * self.Q[next_state, next_action]
            #                                              ^^^^^^^^^^^
            #                                    Actual next action (not max!)
        
        td_error = td_target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error
```

The critical difference: SARSA uses `Q[s', a']` where a' is the action the agent *actually takes* next (which might be a random exploration action). Q-learning uses `max Q[s']` (the best possible action).

## The Cliff Walk Comparison

```python
class CliffWalk:
    def __init__(self, rows=4, cols=12):
        self.rows = rows
        self.cols = cols
        self.n_states = rows * cols
        self.n_actions = 4  # up, down, left, right
        self.start = (3, 0)
        self.goal = (3, 11)
        self.cliff = [(3, c) for c in range(1, 11)]
    
    def reset(self):
        self.pos = self.start
        return self._state_index()
    
    def _state_index(self):
        return self.pos[0] * self.cols + self.pos[1]
    
    def step(self, action):
        r, c = self.pos
        if action == 0: r = max(0, r - 1)      # up
        elif action == 1: r = min(self.rows-1, r + 1)  # down
        elif action == 2: c = max(0, c - 1)     # left
        elif action == 3: c = min(self.cols-1, c + 1)  # right
        
        self.pos = (r, c)
        
        if self.pos in self.cliff:
            # Fell off cliff! Big penalty, reset to start
            self.pos = self.start
            return self._state_index(), -100, False
        elif self.pos == self.goal:
            return self._state_index(), -1, True
        else:
            return self._state_index(), -1, False

def compare_cliff_walk(episodes=500, runs=50):
    """Compare Q-learning and SARSA on the Cliff Walk."""
    q_rewards = np.zeros((runs, episodes))
    sarsa_rewards = np.zeros((runs, episodes))
    
    for run in range(runs):
        env_q = CliffWalk()
        env_s = CliffWalk()
        q_agent = QLearningAgent(n_states=48, n_actions=4, epsilon=0.1)
        s_agent = SARSAAgent(n_states=48, n_actions=4, epsilon=0.1)
        
        for ep in range(episodes):
            # Q-learning episode
            state = env_q.reset()
            ep_reward = 0
            for _ in range(200):
                action = q_agent.choose_action(state)
                next_state, reward, done = env_q.step(action)
                q_agent.learn(state, action, reward, next_state, done)
                ep_reward += reward
                state = next_state
                if done: break
            q_rewards[run, ep] = ep_reward
            
            # SARSA episode
            state = env_s.reset()
            action = s_agent.choose_action(state)
            ep_reward = 0
            for _ in range(200):
                next_state, reward, done = env_s.step(action)
                next_action = s_agent.choose_action(next_state)
                s_agent.learn(state, action, reward, next_state, next_action, done)
                ep_reward += reward
                state = next_state
                action = next_action
                if done: break
            sarsa_rewards[run, ep] = ep_reward
    
    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(np.mean(q_rewards, axis=0), label='Q-learning', alpha=0.8)
    plt.plot(np.mean(sarsa_rewards, axis=0), label='SARSA', alpha=0.8)
    plt.xlabel('Episodes')
    plt.ylabel('Reward per Episode')
    plt.title('Cliff Walk: Q-learning vs SARSA')
    plt.legend()
    plt.ylim(-100, 0)
    plt.grid(True, alpha=0.3)
    plt.show()

compare_cliff_walk()
```

### The Result

- **Q-learning** learns the optimal path (along the cliff edge) but gets terrible rewards during training because exploration steps off the cliff
- **SARSA** learns a safer path (one row above the cliff) that accounts for its own exploration

```
Q-learning's policy:        SARSA's policy:
. . . . . . . . . . . .    . . . . . . . . . . . .
. . . . . . . . . . . .    . . . . . . . . . . . .
. . . . . . . . . . . .    → → → → → → → → → → → ↓
S C C C C C C C C C C G    S C C C C C C C C C C G
  → → → → → → → → → →       (never goes here)
```

SARSA's path is longer (-15 reward) but it never falls off the cliff. Q-learning's path is shorter (-13 optimal) but the agent frequently gets -100 during training.

## On-Policy vs Off-Policy: The Core Distinction

| | Q-Learning (Off-Policy) | SARSA (On-Policy) |
|---|---|---|
| Update target | max Q(s', a') | Q(s', a') where a' is actual next action |
| Learns about | Optimal policy π* | Current policy (including exploration) |
| Accounts for exploration? | No | Yes |
| Cliff walk behavior | Walks along edge (optimal but risky) | Stays safe (suboptimal but practical) |
| Converges to | Q* (optimal) | Q^π (value of current policy) |

### When to Use Which?

- **Q-learning**: When you'll eventually stop exploring (ε → 0) and want the optimal policy
- **SARSA**: When exploration never stops (fixed ε) and you want the best policy *given* that exploration

In GridWorld Tactics, the deployed agent won't explore (ε = 0). So Q-learning's optimal policy is what we want for deployment. But during training, SARSA gives better online performance.

## Expected SARSA: The Best of Both

What if instead of using the actual next action, we use the *expected* value under the ε-greedy policy?

```python
class ExpectedSARSAAgent:
    def __init__(self, n_states, n_actions=4, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.Q = np.zeros((n_states, n_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
    
    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.Q.shape[1])
        return np.argmax(self.Q[state])
    
    def learn(self, state, action, reward, next_state, done):
        """Expected SARSA: use expected Q under current policy."""
        if done:
            td_target = reward
        else:
            # Expected value under epsilon-greedy policy
            n_actions = self.Q.shape[1]
            best_action = np.argmax(self.Q[next_state])
            
            expected_q = 0
            for a in range(n_actions):
                if a == best_action:
                    prob = 1 - self.epsilon + self.epsilon / n_actions
                else:
                    prob = self.epsilon / n_actions
                expected_q += prob * self.Q[next_state, a]
            
            td_target = reward + self.gamma * expected_q
        
        td_error = td_target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error
```

Expected SARSA:
- Has lower variance than SARSA (no randomness from next action selection)
- Is on-policy like SARSA (accounts for exploration)
- With ε=0, becomes identical to Q-learning
- Generally performs as well or better than both Q-learning and SARSA

## The SARSA Training Loop

Note the structural difference from Q-learning:

```python
def train_sarsa(env, agent, episodes=1000):
    """SARSA needs the next action BEFORE the update."""
    for ep in range(episodes):
        state = env.reset()
        action = agent.choose_action(state)  # Choose first action
        episode_reward = 0
        
        for step in range(200):
            next_state, reward, done = env.step(action)
            next_action = agent.choose_action(next_state)  # Choose next action
            
            # Update uses (S, A, R, S', A')
            agent.learn(state, action, reward, next_state, next_action, done)
            
            episode_reward += reward
            state = next_state
            action = next_action  # Carry forward
            
            if done:
                break
        
        agent.episode_returns.append(episode_reward)
```

Q-learning chooses the action, takes the step, and updates independently. SARSA must choose the next action *before* updating, because the update depends on it.

## N-Step SARSA

Like TD(λ), we can extend SARSA to look multiple steps ahead:

```python
def n_step_sarsa(env, n=3, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
    """N-step SARSA: use n steps of real rewards before bootstrapping."""
    Q = np.zeros((env.n_states, env.n_actions))
    
    for ep in range(episodes):
        states = [env.reset()]
        actions = [epsilon_greedy(Q, states[0], epsilon)]
        rewards = [0]  # R_0 is unused
        T = float('inf')
        t = 0
        
        while True:
            if t < T:
                next_state, reward, done = env.step(actions[t])
                states.append(next_state)
                rewards.append(reward)
                
                if done:
                    T = t + 1
                else:
                    actions.append(epsilon_greedy(Q, next_state, epsilon))
            
            tau = t - n + 1  # State being updated
            
            if tau >= 0:
                # Compute n-step return
                G = sum(gamma**(i-tau-1) * rewards[i] 
                       for i in range(tau+1, min(tau+n, T)+1))
                
                if tau + n < T:
                    G += gamma**n * Q[states[tau+n], actions[tau+n]]
                
                Q[states[tau], actions[tau]] += alpha * (G - Q[states[tau], actions[tau]])
            
            if tau == T - 1:
                break
            t += 1
    
    return Q
```

N-step SARSA bridges the gap between 1-step SARSA (TD) and Monte Carlo (full episode). Typically n=3 to n=5 works well.

## Mira's Feedback

Mira watches both agents play the cliff level:

"The Q-learning agent is technically better — when it doesn't fall off the cliff. But in a real game, players will see the AI fall off cliffs during gameplay. The SARSA agent looks smarter because it never makes catastrophic mistakes."

This is a real design consideration: do you want the theoretically optimal policy (which might look stupid during exploration) or a safe policy that performs well even with some randomness?

For the shipped game, you'd train with Q-learning (to find the optimal policy) then deploy with ε=0 (no exploration). But during development and testing, SARSA gives more representative behavior.

## What You Learned

- **SARSA** — on-policy TD control: Q(s,a) ← Q(s,a) + α·[r + γ·Q(s',a') - Q(s,a)]
- **On-policy** — learns the value of the policy it's following (including exploration)
- **Cliff Walk** — SARSA learns safe paths; Q-learning learns optimal but risky paths
- **Expected SARSA** — uses expected Q under current policy; lower variance than SARSA
- **N-step SARSA** — look multiple steps ahead before bootstrapping
- **When to use SARSA** — when exploration is permanent, when safety matters during training
- **When to use Q-learning** — when you'll deploy without exploration, when you want the true optimum

Both Q-learning and SARSA use tables to store Q-values. For our 4×4 grid (16 states × 4 actions = 64 entries) or even the cliff walk (48 states × 4 actions = 192 entries), this is fine.

But GridWorld Tactics has continuous positions, multiple units, and complex state. The table approach is about to break.

---

[← Chapter 7: Q-Learning](chapter-07-q-learning.md) | [Chapter 9: Function Approximation →](chapter-09-function-approximation.md)
