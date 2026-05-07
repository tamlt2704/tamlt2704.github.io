# Chapter 13: PPO

[← Chapter 12: Actor-Critic](chapter-12-actor-critic.md) | [Chapter 14: Reward Shaping →](chapter-14-reward-shaping.md)

---

## The Problem

Your A2C agent on GridWorld Tactics hits 85% win rate after 2,000 episodes. Then at episode 2,100, a series of unlucky episodes produces a large gradient. The policy update overshoots. Win rate crashes to 30%. It takes another 1,000 episodes to recover — if it recovers at all.

Jonas: "This is unacceptable. We can't have the AI get worse during training. The designers need to evaluate it at any point."

You: "The problem is unconstrained policy updates. A2C can change the policy by any amount in one step. If the gradient is noisy (and it always is), large updates are destructive. We need to limit how much the policy changes per update."

This is **Proximal Policy Optimization (PPO)** — the most widely used deep RL algorithm today. It's what trains ChatGPT (RLHF), robotic controllers, and game AI.

## The Core Idea: Trust Regions

Don't let the new policy stray too far from the old policy. If the update is too large, clip it.

Define the probability ratio:

```
r(θ) = π_new(a|s) / π_old(a|s)
```

- r = 1.0: new policy same as old
- r = 1.5: new policy 50% more likely to take this action
- r = 0.5: new policy 50% less likely to take this action

PPO clips this ratio to stay within [1-ε, 1+ε]:

```
L_CLIP = min(r(θ) · A, clip(r(θ), 1-ε, 1+ε) · A)
```

With ε = 0.2, the policy can change by at most 20% per update. This prevents catastrophic collapse.

## PPO Implementation

```python
class PPOAgent:
    def __init__(self, state_dim, n_actions, hidden_dim=64, lr=3e-4,
                 gamma=0.99, gae_lambda=0.95, clip_epsilon=0.2,
                 entropy_coef=0.01, value_coef=0.5, n_epochs=4, batch_size=64):
        
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.n_epochs = n_epochs
        self.batch_size = batch_size
        
        self.model = ActorCritic(state_dim, n_actions, hidden_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        
        # Rollout storage
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.values = []
        self.dones = []
    
    def choose_action(self, state):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            probs, value = self.model(state_tensor)
        
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        
        self.states.append(state)
        self.actions.append(action.item())
        self.log_probs.append(dist.log_prob(action).item())
        self.values.append(value.item())
        
        return action.item()
    
    def store(self, reward, done):
        self.rewards.append(reward)
        self.dones.append(done)
    
    def compute_gae(self, next_value):
        """
        Generalized Advantage Estimation (GAE).
        Smoothly interpolates between 1-step TD and MC advantage.
        """
        advantages = []
        gae = 0
        
        values = self.values + [next_value]
        
        for t in reversed(range(len(self.rewards))):
            delta = self.rewards[t] + self.gamma * values[t+1] * (1 - self.dones[t]) - values[t]
            gae = delta + self.gamma * self.gae_lambda * (1 - self.dones[t]) * gae
            advantages.insert(0, gae)
        
        returns = [adv + val for adv, val in zip(advantages, self.values)]
        return advantages, returns
    
    def update(self, next_value):
        """PPO update: multiple epochs over the collected data."""
        advantages, returns = self.compute_gae(next_value)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(self.states))
        actions = torch.LongTensor(self.actions)
        old_log_probs = torch.FloatTensor(self.log_probs)
        advantages = torch.FloatTensor(advantages)
        returns = torch.FloatTensor(returns)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Multiple epochs of updates on the same data
        for epoch in range(self.n_epochs):
            # Mini-batch updates
            indices = np.arange(len(self.states))
            np.random.shuffle(indices)
            
            for start in range(0, len(self.states), self.batch_size):
                end = start + self.batch_size
                batch_idx = indices[start:end]
                
                batch_states = states[batch_idx]
                batch_actions = actions[batch_idx]
                batch_old_log_probs = old_log_probs[batch_idx]
                batch_advantages = advantages[batch_idx]
                batch_returns = returns[batch_idx]
                
                # Get current policy predictions
                probs, values = self.model(batch_states)
                dist = torch.distributions.Categorical(probs)
                new_log_probs = dist.log_prob(batch_actions)
                entropy = dist.entropy()
                
                # PPO clipped objective
                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 
                                    1 + self.clip_epsilon) * batch_advantages
                actor_loss = -torch.min(surr1, surr2).mean()
                
                # Value loss
                value_loss = (batch_returns - values.squeeze()).pow(2).mean()
                
                # Entropy bonus
                entropy_loss = -entropy.mean()
                
                # Total loss
                loss = (actor_loss + self.value_coef * value_loss + 
                       self.entropy_coef * entropy_loss)
                
                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.model.parameters(), 0.5)
                self.optimizer.step()
        
        # Clear rollout storage
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.values = []
        self.dones = []
```

## Generalized Advantage Estimation (GAE)

GAE is to advantage estimation what TD(λ) is to value estimation. It smoothly interpolates between:
- λ=0: 1-step TD advantage (low variance, high bias)
- λ=1: Monte Carlo advantage (high variance, low bias)

```
A_GAE = δ_t + (γλ)δ_{t+1} + (γλ)²δ_{t+2} + ...
```

where δ_t = r_t + γV(s_{t+1}) - V(s_t) is the TD error.

Typical λ = 0.95 gives a good balance.

## Training PPO

```python
def train_ppo(env_name='CartPole-v1', total_steps=100000, rollout_length=2048):
    env = gym.make(env_name)
    state_dim = env.observation_space.shape[0]
    n_actions = env.action_space.n
    
    agent = PPOAgent(state_dim, n_actions)
    episode_rewards = []
    current_reward = 0
    
    obs, _ = env.reset()
    
    for step in range(total_steps):
        action = agent.choose_action(obs)
        next_obs, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        
        agent.store(reward, done)
        current_reward += reward
        
        if done:
            episode_rewards.append(current_reward)
            current_reward = 0
            obs, _ = env.reset()
        else:
            obs = next_obs
        
        # Update every rollout_length steps
        if (step + 1) % rollout_length == 0:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(obs).unsqueeze(0)
                _, next_value = agent.model(state_tensor)
                next_value = next_value.item()
            
            agent.update(next_value)
            
            if episode_rewards:
                avg = np.mean(episode_rewards[-20:])
                print(f"Step {step+1}, Avg Reward: {avg:.1f}")
    
    env.close()
    return episode_rewards
```

## Why PPO Works So Well

### 1. Clipping Prevents Catastrophe
```python
ratio = new_prob / old_prob
clipped_ratio = clip(ratio, 1-ε, 1+ε)
loss = min(ratio * advantage, clipped_ratio * advantage)
```

If the advantage is positive (good action), the ratio is clipped at 1+ε — the policy can't increase the probability too much.

If the advantage is negative (bad action), the ratio is clipped at 1-ε — the policy can't decrease the probability too much.

### 2. Multiple Epochs = Data Efficiency
A2C uses each sample once. PPO reuses the same rollout for 4-10 gradient updates. This is much more sample-efficient.

### 3. GAE = Good Advantage Estimates
GAE with λ=0.95 gives low-variance advantage estimates that are still responsive to individual actions.

### 4. Simple to Implement and Tune
Compared to TRPO (Trust Region Policy Optimization), PPO achieves similar performance with a much simpler implementation. No second-order optimization, no conjugate gradients.

## PPO Hyperparameters

| Parameter | Typical Value | Effect |
|---|---|---|
| clip_epsilon | 0.1 - 0.3 | How much policy can change per update |
| n_epochs | 3 - 10 | How many times to reuse each rollout |
| rollout_length | 128 - 2048 | Steps collected before each update |
| batch_size | 32 - 512 | Mini-batch size for gradient updates |
| GAE λ | 0.9 - 0.99 | Bias-variance tradeoff for advantages |
| Learning rate | 1e-4 to 3e-4 | Step size for gradient updates |
| Entropy coef | 0.0 - 0.05 | Exploration encouragement |

The defaults (ε=0.2, epochs=4, λ=0.95, lr=3e-4) work well across many environments.

## PPO on GridWorld Tactics

```python
def train_gridworld_tactics_ppo():
    """PPO on the full game environment."""
    # State: position, health, ammo, nearby enemies, terrain
    state_dim = 20
    # Actions: move directions, attack, defend, use_item
    n_actions = 8
    
    agent = PPOAgent(
        state_dim=state_dim,
        n_actions=n_actions,
        hidden_dim=128,
        lr=3e-4,
        clip_epsilon=0.2,
        n_epochs=4,
        batch_size=128
    )
    
    # PPO handles the complex environment stably
    # No catastrophic collapse, steady improvement
    # Reaches 90%+ win rate against scripted AI in ~5000 episodes
```

## Stability Comparison

```python
def compare_stability(env_name='CartPole-v1', runs=10):
    """Show PPO's stability vs A2C."""
    ppo_results = []
    a2c_results = []
    
    for run in range(runs):
        ppo_results.append(train_ppo(env_name, total_steps=50000))
        a2c_results.append(train_a2c(env_name, episodes=500))
    
    # PPO: all runs converge to similar performance
    # A2C: some runs converge, some collapse
    
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    for result in a2c_results:
        plt.plot(result, alpha=0.3, color='blue')
    plt.title('A2C (10 runs) — unstable')
    plt.ylabel('Reward')
    
    plt.subplot(1, 2, 2)
    for result in ppo_results:
        plt.plot(result, alpha=0.3, color='green')
    plt.title('PPO (10 runs) — stable')
    plt.ylabel('Reward')
    
    plt.tight_layout()
    plt.show()
```

PPO's learning curves are remarkably consistent across runs. A2C's curves are all over the place — some great, some terrible.

## Jonas's Verdict

Jonas watches the PPO agent play GridWorld Tactics:

"It flanks. It retreats when outnumbered. It captures objectives in priority order. And it never suddenly forgets how to play."

You: "PPO gives us stable, monotonic improvement. The clipping ensures we never take a step so large that we destroy what we've learned."

Jonas: "Ship it?"

You: "Almost. There's one more problem. The reward signal is too sparse on the harder levels. The agent needs 50 correct decisions in a row to win, and it gets no feedback until the end. It can't learn from such sparse signal."

Jonas: "So we need better rewards?"

You: "We need reward shaping — giving the agent intermediate signals that guide it toward the goal without distorting what it ultimately optimizes."

## What You Learned

- **PPO** — clips the policy ratio to prevent destructive updates
- **Clipped objective** — min(r·A, clip(r, 1-ε, 1+ε)·A); limits policy change
- **GAE** — generalized advantage estimation; smooth bias-variance tradeoff
- **Multiple epochs** — reuse rollout data for better sample efficiency
- **Stability** — PPO rarely collapses; consistent across random seeds
- **Simplicity** — much simpler than TRPO with similar performance
- **The standard** — PPO is the default choice for most deep RL applications today

PPO gives us stable, efficient policy optimization. But it still needs a good reward signal to learn from. When rewards are sparse (only at episode end), even PPO struggles.

The next chapter tackles the reward design problem: how to guide learning when the natural reward is too rare.

---

[← Chapter 12: Actor-Critic](chapter-12-actor-critic.md) | [Chapter 14: Reward Shaping →](chapter-14-reward-shaping.md)
