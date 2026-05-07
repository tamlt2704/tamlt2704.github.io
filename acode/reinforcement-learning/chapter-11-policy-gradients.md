# Chapter 11: Policy Gradients

[← Chapter 10: Deep Q-Networks](chapter-10-dqn.md) | [Chapter 12: Actor-Critic →](chapter-12-actor-critic.md)

---

## The Problem

GridWorld Tactics now has continuous movement: units can move at any angle (0° to 360°) with any speed (0 to 1). The action space is continuous — infinite possible actions.

DQN can't handle this. It outputs Q-values for each discrete action. You could discretize (8 directions × 3 speeds = 24 actions), but that's coarse. Fine discretization (360 directions × 10 speeds = 3,600 actions) makes the Q-network enormous and slow.

Jonas: "We need the agent to output the actual action — an angle and a speed — not evaluate a list of options."

You: "That's a policy gradient method. Instead of learning Q-values and deriving a policy, we learn the policy directly. The network outputs actions, and we adjust it to make good actions more likely."

## The Idea: Learn the Policy Directly

Value-based methods (Q-learning, DQN):
```
State → Q-network → Q-values for each action → pick max
```

Policy gradient methods:
```
State → Policy network → Action (directly)
```

The policy network π_θ(a|s) outputs a probability distribution over actions. For discrete actions, it's a softmax. For continuous actions, it's parameters of a distribution (e.g., mean and std of a Gaussian).

```python
class PolicyNetwork(nn.Module):
    """Policy network for discrete actions."""
    def __init__(self, state_dim, n_actions, hidden_dim=64):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_actions),
            nn.Softmax(dim=-1)
        )
    
    def forward(self, state):
        """Output: probability of each action."""
        return self.network(state)

class ContinuousPolicyNetwork(nn.Module):
    """Policy network for continuous actions (Gaussian policy)."""
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.mean_head = nn.Linear(hidden_dim, action_dim)
        self.log_std_head = nn.Linear(hidden_dim, action_dim)
    
    def forward(self, state):
        """Output: mean and std of Gaussian distribution over actions."""
        features = self.shared(state)
        mean = self.mean_head(features)
        log_std = self.log_std_head(features).clamp(-20, 2)
        std = log_std.exp()
        return mean, std
```

## The Policy Gradient Theorem

How do we improve the policy? We need the gradient of expected return with respect to policy parameters θ:

```
∇_θ J(θ) = E[∇_θ log π_θ(a|s) · G_t]
```

In English: "Increase the probability of actions that led to high returns. Decrease the probability of actions that led to low returns."

This is the **REINFORCE** algorithm (Williams, 1992).

## REINFORCE: The Simplest Policy Gradient

```python
class REINFORCEAgent:
    def __init__(self, state_dim, n_actions, lr=1e-3, gamma=0.99):
        self.gamma = gamma
        self.policy = PolicyNetwork(state_dim, n_actions)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        
        # Store episode data
        self.log_probs = []
        self.rewards = []
    
    def choose_action(self, state):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        probs = self.policy(state_tensor)
        
        # Sample action from the distribution
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        
        # Store log probability for later update
        self.log_probs.append(dist.log_prob(action))
        
        return action.item()
    
    def store_reward(self, reward):
        self.rewards.append(reward)
    
    def learn(self):
        """Update policy after a complete episode."""
        # Compute discounted returns
        returns = []
        G = 0
        for reward in reversed(self.rewards):
            G = reward + self.gamma * G
            returns.insert(0, G)
        
        returns = torch.FloatTensor(returns)
        
        # Normalize returns (reduces variance)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        # Policy gradient loss
        loss = 0
        for log_prob, G in zip(self.log_probs, returns):
            loss -= log_prob * G  # Negative because we want to maximize
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Clear episode data
        self.log_probs = []
        self.rewards = []
        
        return loss.item()
```

## Training REINFORCE

```python
def train_reinforce(env_name='CartPole-v1', episodes=1000):
    env = gym.make(env_name)
    state_dim = env.observation_space.shape[0]
    n_actions = env.action_space.n
    
    agent = REINFORCEAgent(state_dim, n_actions, lr=1e-3)
    episode_rewards = []
    
    for ep in range(episodes):
        obs, _ = env.reset()
        episode_reward = 0
        
        for step in range(500):
            action = agent.choose_action(obs)
            next_obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            agent.store_reward(reward)
            obs = next_obs
            episode_reward += reward
            
            if done:
                break
        
        # Learn from the complete episode
        agent.learn()
        episode_rewards.append(episode_reward)
        
        if (ep + 1) % 100 == 0:
            avg = np.mean(episode_rewards[-100:])
            print(f"Episode {ep+1}, Avg Reward: {avg:.1f}")
    
    env.close()
    return episode_rewards
```

## Why REINFORCE Works (Intuitively)

After an episode with high return:
- `G` is large and positive
- `∇ log π(a|s) · G` pushes the policy to make those actions more likely
- The agent repeats successful behavior

After an episode with low return:
- `G` is small or negative
- The gradient pushes the policy away from those actions
- The agent avoids unsuccessful behavior

It's trial and error at the gradient level: reinforce good episodes, suppress bad ones.

## The Variance Problem

REINFORCE has a critical flaw: **high variance**.

```python
# Episode 1: reward = 100 (great!)  → strongly reinforce all actions
# Episode 2: reward = 98  (also great!) → but G is lower, so reinforce less
# Episode 3: reward = 102 (best yet!) → reinforce most strongly

# The problem: episodes 1 and 2 are both good, but the gradient
# treats episode 2 as "worse" just because it's lower than episode 3.
```

The return G is noisy — it depends on the entire episode, including randomness in the environment. This noise makes the gradient estimates very noisy, causing slow and unstable learning.

### Baseline Subtraction

The fix: subtract a baseline b from the returns:

```
∇_θ J(θ) = E[∇_θ log π_θ(a|s) · (G_t - b)]
```

If b = average return, then:
- Above-average episodes get positive gradient (reinforce)
- Below-average episodes get negative gradient (suppress)

This doesn't change the expected gradient (it's still unbiased) but dramatically reduces variance.

```python
class REINFORCEWithBaseline:
    def __init__(self, state_dim, n_actions, lr_policy=1e-3, lr_baseline=1e-2, gamma=0.99):
        self.gamma = gamma
        self.policy = PolicyNetwork(state_dim, n_actions)
        self.baseline = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
        self.policy_optimizer = optim.Adam(self.policy.parameters(), lr=lr_policy)
        self.baseline_optimizer = optim.Adam(self.baseline.parameters(), lr=lr_baseline)
        
        self.log_probs = []
        self.rewards = []
        self.states = []
    
    def choose_action(self, state):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        probs = self.policy(state_tensor)
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        
        self.log_probs.append(dist.log_prob(action))
        self.states.append(state)
        
        return action.item()
    
    def learn(self):
        # Compute returns
        returns = []
        G = 0
        for reward in reversed(self.rewards):
            G = reward + self.gamma * G
            returns.insert(0, G)
        returns = torch.FloatTensor(returns)
        
        # Baseline predictions
        states_tensor = torch.FloatTensor(np.array(self.states))
        baselines = self.baseline(states_tensor).squeeze()
        
        # Advantage = return - baseline
        advantages = returns - baselines.detach()
        
        # Policy loss
        policy_loss = 0
        for log_prob, advantage in zip(self.log_probs, advantages):
            policy_loss -= log_prob * advantage
        
        # Baseline loss (MSE between predicted and actual returns)
        baseline_loss = nn.MSELoss()(baselines, returns)
        
        # Update both networks
        self.policy_optimizer.zero_grad()
        policy_loss.backward()
        self.policy_optimizer.step()
        
        self.baseline_optimizer.zero_grad()
        baseline_loss.backward()
        self.baseline_optimizer.step()
        
        self.log_probs = []
        self.rewards = []
        self.states = []
```

## Continuous Actions with REINFORCE

For GridWorld Tactics' continuous movement:

```python
class ContinuousREINFORCE:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99):
        self.gamma = gamma
        self.policy = ContinuousPolicyNetwork(state_dim, action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        self.log_probs = []
        self.rewards = []
    
    def choose_action(self, state):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        mean, std = self.policy(state_tensor)
        
        # Sample from Gaussian
        dist = torch.distributions.Normal(mean, std)
        action = dist.sample()
        
        # Log probability of this action
        self.log_probs.append(dist.log_prob(action).sum())
        
        return action.squeeze().detach().numpy()
    
    def learn(self):
        returns = []
        G = 0
        for reward in reversed(self.rewards):
            G = reward + self.gamma * G
            returns.insert(0, G)
        
        returns = torch.FloatTensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        loss = 0
        for log_prob, G in zip(self.log_probs, returns):
            loss -= log_prob * G
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        self.log_probs = []
        self.rewards = []
```

Now the agent outputs continuous values — angle and speed — directly from the policy network. No discretization needed.

## Policy Gradients vs Value-Based Methods

| | Value-Based (DQN) | Policy Gradient (REINFORCE) |
|---|---|---|
| Learns | Q(s,a) → derive policy | π(a|s) directly |
| Action space | Discrete only | Discrete or continuous |
| Stochastic policy? | No (deterministic greedy) | Yes (naturally stochastic) |
| Sample efficiency | Higher (replay buffer) | Lower (on-policy, no replay) |
| Stability | Can diverge (deadly triad) | More stable gradients |
| Variance | Low (bootstrapping) | High (full episode returns) |

## The Remaining Problem: Variance

Even with a baseline, REINFORCE has high variance because:
1. It uses complete episode returns (Monte Carlo)
2. It can only update after an episode ends
3. A single bad action early on penalizes all subsequent actions

What if we could:
- Update during the episode (like TD)?
- Use a learned value function as the baseline?
- Combine the stability of policy gradients with the efficiency of value-based methods?

That's the actor-critic architecture.

## What You Learned

- **Policy gradients** — learn π(a|s) directly instead of Q(s,a)
- **REINFORCE** — ∇J = E[∇log π(a|s) · G]; reinforce good episodes
- **Continuous actions** — Gaussian policy outputs mean and std; sample actions
- **High variance** — full-episode returns are noisy; learning is slow
- **Baseline subtraction** — subtract average return to reduce variance without adding bias
- **Advantage** — G - baseline; positive = better than average, negative = worse
- **Limitation** — must wait for episode end; high variance even with baseline

Policy gradients handle continuous actions and learn stochastic policies. But the variance from Monte Carlo returns makes learning slow and unstable. The next chapter combines a policy network (actor) with a value network (critic) to get the best of both worlds.

---

[← Chapter 10: Deep Q-Networks](chapter-10-dqn.md) | [Chapter 12: Actor-Critic →](chapter-12-actor-critic.md)
