# Chapter 15: Model-Based RL

[← Chapter 14: Reward Shaping](chapter-14-reward-shaping.md)

---

## The Problem

Your PPO agent with reward shaping reaches 91% win rate against the scripted AI. Jonas is happy. But there's a catch: it took 50,000 episodes to get there. Each episode is a full game (~300 turns). That's 15 million environment steps.

Jonas: "The game designers change the rules every sprint. New units, new abilities, new maps. Every time they change something, we retrain from scratch. 50,000 games takes 8 hours on our GPU cluster."

You: "The agent learns everything through trial and error. It doesn't build a mental model of how the world works. If it understood that 'moving right from (3,5) leads to (3,6)', it could plan ahead without actually taking the step. It could simulate thousands of games in its head."

Jonas: "Like how a chess player thinks ahead?"

You: "Exactly. Model-based RL: learn a model of the environment, then use it to plan."

## Model-Free vs Model-Based

**Model-free** (everything so far): Learn a policy or value function directly from experience. No understanding of how the world works.

**Model-based**: Learn a model of the world (transitions and rewards), then use it to plan or generate synthetic experience.

```python
# Model-free: act → observe → learn from real experience
real_next_state, real_reward = env.step(action)
agent.learn(state, action, real_reward, real_next_state)

# Model-based: act → observe → learn model → plan using model
real_next_state, real_reward = env.step(action)
model.learn(state, action, real_next_state, real_reward)

# Generate synthetic experience (no real environment needed!)
for _ in range(planning_steps):
    sim_state = sample_state()
    sim_action = sample_action()
    sim_next, sim_reward = model.predict(sim_state, sim_action)
    agent.learn(sim_state, sim_action, sim_reward, sim_next)
```

## Dyna-Q: The Simplest Model-Based Method

**Dyna** (Sutton, 1991) combines real experience with simulated experience:

1. Take a real step in the environment
2. Update Q from the real experience
3. Update the model from the real experience
4. Repeat N times: sample a previously-seen state-action, simulate with the model, update Q

```python
class DynaQAgent:
    def __init__(self, n_states, n_actions, alpha=0.1, gamma=0.9, 
                 epsilon=0.1, planning_steps=50):
        self.Q = np.zeros((n_states, n_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.planning_steps = planning_steps
        
        # The learned model
        self.model = {}  # (state, action) → (next_state, reward)
        self.visited = []  # Track visited state-action pairs
    
    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.Q.shape[1])
        return np.argmax(self.Q[state])
    
    def learn(self, state, action, reward, next_state, done):
        """Direct RL: learn from real experience."""
        if done:
            td_target = reward
        else:
            td_target = reward + self.gamma * np.max(self.Q[next_state])
        
        self.Q[state, action] += self.alpha * (td_target - self.Q[state, action])
        
        # Update model
        self.model[(state, action)] = (next_state, reward, done)
        if (state, action) not in self.visited:
            self.visited.append((state, action))
        
        # Planning: simulate with the model
        self._plan()
    
    def _plan(self):
        """Use the model to generate synthetic experience."""
        for _ in range(self.planning_steps):
            # Sample a previously-seen state-action pair
            s, a = self.visited[np.random.randint(len(self.visited))]
            
            # Simulate using the model
            next_s, r, done = self.model[(s, a)]
            
            # Q-learning update on simulated experience
            if done:
                td_target = r
            else:
                td_target = r + self.gamma * np.max(self.Q[next_s])
            
            self.Q[s, a] += self.alpha * (td_target - self.Q[s, a])
```

### Dyna-Q Results

```python
def compare_planning_steps(env, steps_list=[0, 5, 50]):
    """Show how planning steps accelerate learning."""
    plt.figure(figsize=(10, 5))
    
    for n_planning in steps_list:
        agent = DynaQAgent(n_states=env.n_states, n_actions=4, 
                          planning_steps=n_planning)
        episode_steps = train_agent(env, agent, episodes=100)
        
        plt.plot(episode_steps, label=f'{n_planning} planning steps')
    
    plt.xlabel('Episode')
    plt.ylabel('Steps to Goal')
    plt.title('Effect of Planning Steps in Dyna-Q')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
```

With 0 planning steps: pure Q-learning, slow convergence.
With 5 planning steps: 5× faster learning.
With 50 planning steps: 50× faster learning (each real step generates 50 learning updates).

The model amplifies real experience. One real interaction becomes 50 learning opportunities.

## Learning the World Model with Neural Networks

For complex environments, we can't store a table of transitions. We learn a neural network model:

```python
class WorldModel(nn.Module):
    """Neural network that predicts next state and reward."""
    
    def __init__(self, state_dim, action_dim, hidden_dim=128):
        super().__init__()
        
        self.dynamics = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        # Predict next state
        self.next_state_head = nn.Linear(hidden_dim, state_dim)
        
        # Predict reward
        self.reward_head = nn.Linear(hidden_dim, 1)
        
        # Predict done
        self.done_head = nn.Sequential(
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
    
    def forward(self, state, action):
        """Predict (next_state, reward, done) from (state, action)."""
        x = torch.cat([state, action], dim=-1)
        features = self.dynamics(x)
        
        next_state = self.next_state_head(features)
        reward = self.reward_head(features)
        done = self.done_head(features)
        
        return next_state, reward, done

class WorldModelTrainer:
    def __init__(self, state_dim, action_dim, lr=1e-3):
        self.model = WorldModel(state_dim, action_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.buffer = deque(maxlen=100000)
    
    def store(self, state, action, next_state, reward, done):
        self.buffer.append((state, action, next_state, reward, done))
    
    def train(self, batch_size=256, n_batches=10):
        """Train the world model on collected experience."""
        if len(self.buffer) < batch_size:
            return
        
        for _ in range(n_batches):
            batch = random.sample(self.buffer, batch_size)
            states, actions, next_states, rewards, dones = zip(*batch)
            
            states = torch.FloatTensor(np.array(states))
            actions = torch.FloatTensor(np.array(actions))
            next_states = torch.FloatTensor(np.array(next_states))
            rewards = torch.FloatTensor(rewards).unsqueeze(1)
            dones = torch.FloatTensor(dones).unsqueeze(1)
            
            pred_next, pred_reward, pred_done = self.model(states, actions)
            
            state_loss = nn.MSELoss()(pred_next, next_states)
            reward_loss = nn.MSELoss()(pred_reward, rewards)
            done_loss = nn.BCELoss()(pred_done, dones)
            
            loss = state_loss + reward_loss + done_loss
            
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        
        return loss.item()
```

## Model-Based Policy Optimization (MBPO)

The state-of-the-art approach: use the learned model to generate short rollouts, then train the policy on this synthetic data.

```python
class MBPOAgent:
    """
    Model-Based Policy Optimization:
    1. Collect real data
    2. Train world model on real data
    3. Generate synthetic rollouts from the model
    4. Train policy (PPO/SAC) on synthetic data
    """
    
    def __init__(self, state_dim, action_dim, n_actions):
        self.world_model = WorldModelTrainer(state_dim, action_dim)
        self.policy = PPOAgent(state_dim, n_actions)
        self.real_buffer = deque(maxlen=100000)
        self.model_buffer = deque(maxlen=400000)
    
    def collect_real_data(self, env, n_steps=1000):
        """Interact with real environment."""
        state = env.reset()
        
        for _ in range(n_steps):
            action = self.policy.choose_action(state)
            next_state, reward, done = env.step(action)
            
            self.real_buffer.append((state, action, next_state, reward, done))
            self.world_model.store(state, action, next_state, reward, done)
            
            if done:
                state = env.reset()
            else:
                state = next_state
    
    def train_model(self):
        """Train world model on real data."""
        self.world_model.train(batch_size=256, n_batches=50)
    
    def generate_synthetic_data(self, n_rollouts=400, rollout_length=5):
        """Generate synthetic experience using the learned model."""
        for _ in range(n_rollouts):
            # Start from a real state
            real_transition = random.choice(self.real_buffer)
            state = real_transition[0]
            
            for step in range(rollout_length):
                action = self.policy.choose_action(state)
                
                # Simulate with model
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                action_tensor = torch.FloatTensor(self._encode_action(action)).unsqueeze(0)
                
                with torch.no_grad():
                    next_state, reward, done = self.world_model.model(state_tensor, action_tensor)
                
                next_state = next_state.squeeze().numpy()
                reward = reward.item()
                done = done.item() > 0.5
                
                self.model_buffer.append((state, action, next_state, reward, done))
                
                if done:
                    break
                state = next_state
    
    def train_policy(self):
        """Train policy on mix of real and synthetic data."""
        # Use synthetic data for policy updates
        # This is where PPO/SAC training happens
        pass
    
    def train(self, env, total_steps=50000, model_train_freq=250):
        """Full MBPO training loop."""
        steps = 0
        
        while steps < total_steps:
            # 1. Collect real data
            self.collect_real_data(env, n_steps=model_train_freq)
            steps += model_train_freq
            
            # 2. Train world model
            self.train_model()
            
            # 3. Generate synthetic data
            self.generate_synthetic_data()
            
            # 4. Train policy on synthetic data
            self.train_policy()
```

MBPO achieves the same performance as model-free methods with 10-100× fewer real environment interactions.

## The Model Error Problem

Learned models are imperfect. Errors compound over long rollouts:

```
Step 1: model error = 0.01 (small)
Step 5: model error = 0.05 (accumulating)
Step 20: model error = 0.50 (useless predictions)
```

This is why MBPO uses **short rollouts** (1-5 steps) from the model. Long rollouts drift into unrealistic states.

```python
def adaptive_rollout_length(model_error, min_length=1, max_length=20):
    """
    Increase rollout length as model improves.
    Short rollouts when model is inaccurate, longer when it's good.
    """
    # model_error: average prediction error on held-out data
    if model_error > 0.1:
        return min_length
    elif model_error > 0.01:
        return 5
    else:
        return max_length
```

## Ensemble Models for Uncertainty

A single model doesn't know when it's wrong. An **ensemble** of models provides uncertainty estimates:

```python
class EnsembleWorldModel:
    """Multiple models — disagreement = uncertainty."""
    
    def __init__(self, state_dim, action_dim, n_models=5):
        self.models = [WorldModel(state_dim, action_dim) for _ in range(n_models)]
        self.optimizers = [optim.Adam(m.parameters(), lr=1e-3) for m in self.models]
    
    def predict(self, state, action):
        """Predict with all models. Return mean and uncertainty."""
        predictions = []
        for model in self.models:
            with torch.no_grad():
                next_s, reward, done = model(state, action)
                predictions.append(next_s)
        
        predictions = torch.stack(predictions)
        mean = predictions.mean(dim=0)
        uncertainty = predictions.std(dim=0).mean()  # Disagreement
        
        return mean, uncertainty
    
    def should_trust_prediction(self, state, action, threshold=0.1):
        """Only use model predictions when models agree."""
        _, uncertainty = self.predict(state, action)
        return uncertainty.item() < threshold
```

When models disagree, the prediction is unreliable — fall back to real experience. When they agree, the prediction is trustworthy — use it for planning.

## Planning with the Model: Monte Carlo Tree Search

For turn-based games like GridWorld Tactics, we can use the model for lookahead planning:

```python
class MCTSPlanner:
    """
    Monte Carlo Tree Search using the learned world model.
    Look ahead N steps to find the best action.
    """
    
    def __init__(self, world_model, policy, n_simulations=100, depth=10, gamma=0.99):
        self.model = world_model
        self.policy = policy
        self.n_simulations = n_simulations
        self.depth = depth
        self.gamma = gamma
    
    def plan(self, state, n_actions):
        """Find the best action by simulating futures."""
        action_values = np.zeros(n_actions)
        action_counts = np.zeros(n_actions)
        
        for _ in range(self.n_simulations):
            # Try each action and simulate forward
            action = self._select_action(action_values, action_counts)
            value = self._simulate(state, action)
            
            action_counts[action] += 1
            action_values[action] += (value - action_values[action]) / action_counts[action]
        
        return np.argmax(action_values)
    
    def _simulate(self, state, first_action):
        """Simulate a trajectory using the world model."""
        total_return = 0
        discount = 1.0
        
        current_state = state
        action = first_action
        
        for step in range(self.depth):
            # Use model to predict next state
            state_tensor = torch.FloatTensor(current_state).unsqueeze(0)
            action_tensor = self._encode(action)
            
            with torch.no_grad():
                next_state, reward, done = self.model(state_tensor, action_tensor)
            
            total_return += discount * reward.item()
            discount *= self.gamma
            
            if done.item() > 0.5:
                break
            
            current_state = next_state.squeeze().numpy()
            action = self.policy.choose_action(current_state)
        
        return total_return
    
    def _select_action(self, values, counts):
        """UCB selection for action choice."""
        total = counts.sum()
        if total == 0:
            return np.random.randint(len(values))
        
        ucb = values + 2 * np.sqrt(np.log(total + 1) / (counts + 1))
        return np.argmax(ucb)
```

## The Full Pipeline for GridWorld Tactics

```python
def train_final_agent():
    """
    The complete training pipeline:
    1. PPO for the policy (stable optimization)
    2. World model for sample efficiency
    3. Reward shaping for learning speed
    4. MCTS for deployment (planning at test time)
    """
    env = GridWorldTactics()
    
    # Phase 1: Collect initial data with random policy
    initial_data = collect_random_data(env, n_episodes=100)
    
    # Phase 2: Train world model
    world_model = EnsembleWorldModel(state_dim=20, action_dim=8)
    world_model.train(initial_data)
    
    # Phase 3: Train policy with MBPO + reward shaping
    shaped_env = PBRSEnvironment(env, gridworld_tactics_potential)
    agent = MBPOAgent(state_dim=20, action_dim=8, n_actions=8)
    agent.train(shaped_env, total_steps=50000)
    
    # Phase 4: Deploy with MCTS planning
    planner = MCTSPlanner(world_model, agent.policy, n_simulations=200)
    
    return agent, planner
```

## Final Results

| Method | Episodes to 90% Win Rate | Real Env Steps |
|---|---|---|
| Q-learning (tabular) | N/A (can't handle state space) | N/A |
| DQN | 30,000 | 9,000,000 |
| PPO (model-free) | 50,000 | 15,000,000 |
| PPO + reward shaping | 15,000 | 4,500,000 |
| MBPO + shaping | 5,000 | 1,500,000 |
| MBPO + shaping + MCTS | 3,000 | 900,000 |

Model-based methods achieve the same performance with 10× fewer real interactions.

## Jonas's Final Review

Jonas watches the final agent play against the scripted AI:

"It's flanking. It's retreating wounded units. It's capturing objectives in priority order. It's... it's actually good. Better than the scripted AI we spent 8 months writing."

Mira: "And when I change the map?"

You: "The world model adapts in a few hundred episodes. The policy fine-tunes on the new synthetic data. We don't retrain from scratch."

Jonas: "Ship it."

## The Complete RL Toolkit

Looking back at the journey:

| Problem | Solution | Chapter |
|---|---|---|
| No learning signal | Reward design, discounting | 1 |
| Gets stuck on first good action | Exploration (ε-greedy, UCB) | 2 |
| No formal framework | MDP formalization | 3 |
| Know the model, want optimal policy | Dynamic programming | 4 |
| Don't know model, can wait for episode end | Monte Carlo methods | 5 |
| Can't wait for episode end | TD learning | 6 |
| Need action values, off-policy | Q-learning | 7 |
| Need safety during training | SARSA | 8 |
| State space too large for table | Function approximation | 9 |
| Need nonlinear approximation | Deep Q-Networks | 10 |
| Need continuous actions | Policy gradients | 11 |
| Policy gradient variance too high | Actor-Critic (A2C) | 12 |
| Policy updates too unstable | PPO | 13 |
| Rewards too sparse | Reward shaping, curiosity, HER | 14 |
| Too many real interactions needed | Model-based RL, Dyna, MBPO | 15 |

## What You Learned

- **Model-based RL** — learn a model of the world; use it to plan and generate synthetic data
- **Dyna-Q** — augment real experience with simulated experience from a learned model
- **World models** — neural networks that predict next state and reward
- **MBPO** — short model rollouts + policy optimization; 10-100× more sample efficient
- **Model error** — predictions degrade over long rollouts; use short rollouts
- **Ensemble models** — multiple models provide uncertainty estimates
- **MCTS** — use the model for lookahead planning at deployment time
- **The tradeoff** — model-based is more sample efficient but adds model learning complexity

## Where to Go Next

This course covered the foundations. The field continues:

- **Multi-agent RL** — multiple agents learning simultaneously (self-play, cooperation)
- **Offline RL** — learn from fixed datasets without environment interaction
- **Hierarchical RL** — learn at multiple levels of abstraction (options, goals)
- **Meta-RL** — learn to learn; adapt to new tasks in few episodes
- **RLHF** — reinforcement learning from human feedback (how LLMs are aligned)
- **Safe RL** — constrained optimization; guarantee safety during training
- **Sim-to-real** — train in simulation, deploy in the real world

The fundamentals don't change. States, actions, rewards, policies, values, Bellman equations — these are the building blocks of every method, no matter how advanced.

You started with a random agent that wandered into traps 47% of the time. You end with an agent that plans ahead, adapts to new environments, and beats hand-crafted AI that took 8 months to build.

That's reinforcement learning.

---

[← Chapter 14: Reward Shaping](chapter-14-reward-shaping.md)
