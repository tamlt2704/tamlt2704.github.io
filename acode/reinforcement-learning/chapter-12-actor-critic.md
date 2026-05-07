# Chapter 12: Actor-Critic

[← Chapter 11: Policy Gradients](chapter-11-policy-gradients.md) | [Chapter 13: PPO →](chapter-13-ppo.md)

---

## The Problem

REINFORCE works but it's painfully slow. After 5,000 episodes on the 20×20 grid, the agent barely outperforms random. The variance is killing it — one lucky episode sends the gradient in one direction, the next unlucky episode yanks it back.

Jonas: "It's been training for 3 hours and it's still terrible. DQN solved CartPole in 20 minutes."

You: "REINFORCE uses Monte Carlo returns — it waits until the episode ends, then uses the noisy total return to update. What if we used a value function to estimate returns, like TD does? Lower variance, faster learning."

Jonas: "So combine policy gradients with a value function?"

You: "Exactly. Two networks: an **actor** (the policy) and a **critic** (the value function). The critic tells the actor how good its actions are. The actor adjusts accordingly."

## The Actor-Critic Architecture

```
State → Actor (policy network) → Action
State → Critic (value network) → V(s) (how good is this state?)
```

The actor decides what to do. The critic evaluates how good the situation is. The actor improves based on the critic's feedback.

```python
class ActorCritic(nn.Module):
    def __init__(self, state_dim, n_actions, hidden_dim=64):
        super().__init__()
        
        # Shared feature extraction
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Actor head: outputs action probabilities
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_actions),
            nn.Softmax(dim=-1)
        )
        
        # Critic head: outputs state value V(s)
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(self, state):
        features = self.shared(state)
        action_probs = self.actor(features)
        state_value = self.critic(features)
        return action_probs, state_value
```

## The Advantage Function

The key insight: instead of using the raw return G, use the **advantage**:

```
A(s, a) = Q(s, a) - V(s)
```

"How much better is this action compared to the average action in this state?"

- A > 0: This action is better than average → increase its probability
- A < 0: This action is worse than average → decrease its probability
- A = 0: This action is exactly average → no change

We estimate the advantage using TD error:

```
A ≈ r + γ·V(s') - V(s) = δ (TD error)
```

The TD error is a one-step estimate of the advantage. It's biased but has much lower variance than Monte Carlo returns.

## A2C: Advantage Actor-Critic

```python
class A2CAgent:
    def __init__(self, state_dim, n_actions, lr=3e-4, gamma=0.99, 
                 entropy_coef=0.01, value_coef=0.5):
        self.gamma = gamma
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        
        self.model = ActorCritic(state_dim, n_actions)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
    
    def choose_action(self, state):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        probs, value = self.model(state_tensor)
        
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        
        return action.item(), dist.log_prob(action), value, dist.entropy()
    
    def learn(self, log_prob, value, reward, next_value, done, entropy):
        """Update after EVERY STEP (not after episode!)."""
        # TD target
        if done:
            td_target = torch.FloatTensor([reward])
        else:
            td_target = reward + self.gamma * next_value.detach()
        
        # Advantage (TD error)
        advantage = td_target - value
        
        # Actor loss: policy gradient with advantage
        actor_loss = -(log_prob * advantage.detach())
        
        # Critic loss: MSE between predicted and target value
        critic_loss = advantage.pow(2)
        
        # Entropy bonus: encourage exploration
        entropy_loss = -entropy
        
        # Total loss
        loss = actor_loss + self.value_coef * critic_loss + self.entropy_coef * entropy_loss
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
```

## Training A2C

```python
def train_a2c(env_name='CartPole-v1', episodes=1000):
    env = gym.make(env_name)
    state_dim = env.observation_space.shape[0]
    n_actions = env.action_space.n
    
    agent = A2CAgent(state_dim, n_actions)
    episode_rewards = []
    
    for ep in range(episodes):
        obs, _ = env.reset()
        episode_reward = 0
        
        for step in range(500):
            action, log_prob, value, entropy = agent.choose_action(obs)
            next_obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            # Get next state value for TD target
            if not done:
                with torch.no_grad():
                    next_state_tensor = torch.FloatTensor(next_obs).unsqueeze(0)
                    _, next_value = agent.model(next_state_tensor)
            else:
                next_value = torch.zeros(1)
            
            # Learn after EVERY step
            agent.learn(log_prob, value, reward, next_value, done, entropy)
            
            obs = next_obs
            episode_reward += reward
            
            if done:
                break
        
        episode_rewards.append(episode_reward)
        
        if (ep + 1) % 100 == 0:
            avg = np.mean(episode_rewards[-100:])
            print(f"Episode {ep+1}, Avg Reward: {avg:.1f}")
    
    env.close()
    return episode_rewards
```

Key difference from REINFORCE: A2C updates **every step**, not after the episode. This is possible because the critic provides an immediate estimate of how good the action was.

## The Three Losses

A2C optimizes three objectives simultaneously:

### 1. Actor Loss (Policy Gradient)
```python
actor_loss = -log_prob * advantage.detach()
```
Push the policy toward actions with positive advantage.

### 2. Critic Loss (Value Prediction)
```python
critic_loss = (td_target - value) ** 2
```
Make the critic's predictions more accurate.

### 3. Entropy Bonus
```python
entropy_loss = -entropy
```
Prevent the policy from becoming too deterministic too early. Encourage exploration.

The entropy bonus is crucial — without it, the policy often collapses to always choosing one action, getting stuck in a local optimum.

## N-Step A2C

Instead of 1-step TD, use N steps of real rewards before bootstrapping:

```python
class NStepA2C:
    def __init__(self, state_dim, n_actions, n_steps=5, lr=3e-4, gamma=0.99):
        self.n_steps = n_steps
        self.gamma = gamma
        self.model = ActorCritic(state_dim, n_actions)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
    
    def compute_n_step_return(self, rewards, next_value, dones):
        """Compute n-step return: r1 + γr2 + γ²r3 + ... + γⁿV(s_n)."""
        returns = []
        R = next_value
        
        for step in reversed(range(len(rewards))):
            R = rewards[step] + self.gamma * R * (1 - dones[step])
            returns.insert(0, R)
        
        return returns
    
    def update(self, states, actions, rewards, next_state, dones):
        """Update using n-step returns."""
        states_tensor = torch.FloatTensor(np.array(states))
        actions_tensor = torch.LongTensor(actions)
        
        probs, values = self.model(states_tensor)
        values = values.squeeze()
        
        # N-step return
        with torch.no_grad():
            next_tensor = torch.FloatTensor(next_state).unsqueeze(0)
            _, next_value = self.model(next_tensor)
            next_value = next_value.item()
        
        returns = self.compute_n_step_return(rewards, next_value, dones)
        returns = torch.FloatTensor(returns)
        
        # Advantages
        advantages = returns - values.detach()
        
        # Actor loss
        dist = torch.distributions.Categorical(probs)
        log_probs = dist.log_prob(actions_tensor)
        actor_loss = -(log_probs * advantages).mean()
        
        # Critic loss
        critic_loss = (returns - values).pow(2).mean()
        
        # Entropy
        entropy = dist.entropy().mean()
        
        loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy
        
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.model.parameters(), 0.5)  # Gradient clipping
        self.optimizer.step()
```

N-step returns (typically n=5) balance bias and variance better than 1-step TD.

## Continuous Actions with Actor-Critic

```python
class ContinuousActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        super().__init__()
        
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Actor: Gaussian policy
        self.mean = nn.Linear(hidden_dim, action_dim)
        self.log_std = nn.Parameter(torch.zeros(action_dim))
        
        # Critic
        self.value = nn.Linear(hidden_dim, 1)
    
    def forward(self, state):
        features = self.shared(state)
        mean = self.mean(features)
        std = self.log_std.exp()
        value = self.value(features)
        return mean, std, value
    
    def get_action(self, state):
        mean, std, value = self.forward(state)
        dist = torch.distributions.Normal(mean, std)
        action = dist.sample()
        log_prob = dist.log_prob(action).sum(dim=-1)
        return action, log_prob, value
```

## Comparing Methods on GridWorld Tactics

```python
def benchmark_comparison():
    """Compare REINFORCE, A2C, and DQN on the same environment."""
    results = {}
    
    # REINFORCE: slow, high variance
    results['REINFORCE'] = train_reinforce(episodes=2000)
    
    # A2C: faster, lower variance
    results['A2C'] = train_a2c(episodes=2000)
    
    # DQN: fast but discrete only
    results['DQN'] = train_dqn(episodes=2000)
    
    plt.figure(figsize=(10, 5))
    for name, rewards in results.items():
        smoothed = np.convolve(rewards, np.ones(50)/50, mode='valid')
        plt.plot(smoothed, label=name)
    plt.xlabel('Episode')
    plt.ylabel('Reward (50-ep avg)')
    plt.title('Algorithm Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

Typical ranking:
1. **DQN** — fastest for discrete actions (experience replay helps)
2. **A2C** — good balance of speed and flexibility
3. **REINFORCE** — slowest due to high variance

## The Stability Problem

A2C is better than REINFORCE, but it's still fragile:

- Large policy updates can destroy good behavior
- The critic's errors propagate to the actor
- Performance can collapse suddenly after many good episodes

QA Tanya: "It was doing great at episode 800 — 90% win rate. Then at episode 850 it forgot everything and dropped to 20%. What happened?"

This is **catastrophic policy collapse**. A bad gradient update pushes the policy far from the good region, and it can't recover.

The fix: constrain how much the policy can change in one update. That's PPO.

## What You Learned

- **Actor-Critic** — two networks: actor (policy) and critic (value function)
- **Advantage** — A = Q(s,a) - V(s) ≈ r + γV(s') - V(s); how much better than average
- **A2C** — advantage actor-critic; updates every step using TD error as advantage
- **Three losses** — actor (policy gradient), critic (value prediction), entropy (exploration)
- **N-step returns** — balance bias/variance by using N real rewards before bootstrapping
- **Continuous actions** — Gaussian policy with learned mean and std
- **Gradient clipping** — prevent exploding gradients from destabilizing training
- **The problem** — large updates can catastrophically destroy learned behavior

Actor-critic gives us step-by-step learning with lower variance than REINFORCE. But it's still unstable — one bad update can undo thousands of episodes of learning.

The next chapter introduces PPO — the algorithm that constrains policy updates to prevent catastrophic collapse.

---

[← Chapter 11: Policy Gradients](chapter-11-policy-gradients.md) | [Chapter 13: PPO →](chapter-13-ppo.md)
