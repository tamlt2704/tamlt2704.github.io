# Chapter 9: Function Approximation

[← Chapter 8: SARSA](chapter-08-sarsa.md) | [Chapter 10: Deep Q-Networks →](chapter-10-dqn.md)

---

## The Problem

Mira's latest level: a 50×50 grid where units have health (0-100), ammo (0-20), and facing direction (4 options). The state space:

```
50 × 50 × 101 × 21 × 4 = 21,210,000 states
```

With 4 actions, the Q-table needs 84,840,000 entries. Most will never be visited. And this is still a simplified version — the real game has multiple units, fog of war, and enemy positions.

Jonas: "The Q-table is 85 million entries. That's not going to work."

You: "We need function approximation. Instead of storing a value for every state, we learn a function that *generalizes* — it estimates values for states it's never seen based on similar states it has seen."

## From Tables to Functions

Q-table: look up Q(s,a) in a giant table. Every state is independent.

Function approximation: compute Q(s,a) from features of the state. Similar states get similar values.

```python
# Table approach (Chapter 7)
Q[state_index, action]  # Exact lookup, no generalization

# Function approximation
Q(state_features, action) = w · φ(s, a)  # Generalize across similar states
```

## Feature Engineering

The first step: represent states as feature vectors instead of indices.

```python
def extract_features(state, action, grid_size=50):
    """
    Convert (row, col, health, ammo, facing) + action into a feature vector.
    """
    row, col, health, ammo, facing = state
    
    features = [
        row / grid_size,              # Normalized position
        col / grid_size,
        health / 100,                 # Normalized health
        ammo / 20,                    # Normalized ammo
        # Distance to goal
        abs(row - goal[0]) / grid_size,
        abs(col - goal[1]) / grid_size,
        # Is the action moving toward the goal?
        1.0 if action_moves_toward_goal(state, action) else 0.0,
        # Is there a trap adjacent?
        1.0 if trap_adjacent(state) else 0.0,
        # One-hot encoding of facing direction
        float(facing == 0),
        float(facing == 1),
        float(facing == 2),
        float(facing == 3),
    ]
    
    return np.array(features)
```

Good features capture what matters for decision-making. Bad features add noise.

## Linear Function Approximation

The simplest function approximator: a linear combination of features.

```
Q(s, a) = w^T · φ(s, a) = w₁·f₁ + w₂·f₂ + ... + wₙ·fₙ
```

```python
class LinearQAgent:
    def __init__(self, n_features, n_actions=4, alpha=0.01, gamma=0.9, epsilon=0.1):
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        # One weight vector per action
        self.weights = np.zeros((n_actions, n_features))
    
    def get_q_value(self, features, action):
        """Q(s,a) = dot product of weights and features."""
        return np.dot(self.weights[action], features)
    
    def get_all_q_values(self, features):
        """Get Q-values for all actions."""
        return np.array([self.get_q_value(features, a) for a in range(self.n_actions)])
    
    def choose_action(self, features):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.n_actions)
        q_values = self.get_all_q_values(features)
        return np.argmax(q_values)
    
    def learn(self, features, action, reward, next_features, done):
        """Semi-gradient TD update for linear Q."""
        current_q = self.get_q_value(features, action)
        
        if done:
            td_target = reward
        else:
            next_q_values = self.get_all_q_values(next_features)
            td_target = reward + self.gamma * np.max(next_q_values)
        
        td_error = td_target - current_q
        
        # Gradient of linear Q w.r.t. weights = features
        self.weights[action] += self.alpha * td_error * features
```

### Why Linear Works

The update `w += α · δ · φ(s,a)` is gradient descent on the squared TD error:

```
Loss = (td_target - Q(s,a))²
∂Loss/∂w = -2 · (td_target - Q(s,a)) · ∂Q/∂w
         = -2 · td_error · features    (for linear Q)
```

We move the weights in the direction that reduces the prediction error.

### The Power of Generalization

With a table, learning that state (25, 30, 80, 15, 0) is good tells you nothing about state (25, 31, 80, 15, 0). They're completely independent entries.

With linear approximation, if the feature "distance to goal" has a large negative weight, then *all* states far from the goal get low values — even states never visited. The agent generalizes from experience.

## Training on CartPole

Let's test on a classic continuous-state environment: CartPole.

```python
import gymnasium as gym

def cartpole_features(observation):
    """
    CartPole state: [cart_position, cart_velocity, pole_angle, pole_angular_velocity]
    Create polynomial features for better approximation.
    """
    x, x_dot, theta, theta_dot = observation
    
    features = np.array([
        1.0,            # Bias
        x,              # Cart position
        x_dot,          # Cart velocity
        theta,          # Pole angle
        theta_dot,      # Pole angular velocity
        x * theta,      # Interaction: position × angle
        x_dot * theta_dot,  # Interaction: velocities
        theta ** 2,     # Squared angle (penalize large angles)
        x ** 2,         # Squared position
    ])
    
    return features

def train_cartpole_linear(episodes=2000):
    env = gym.make('CartPole-v1')
    n_features = 9  # From our feature function
    agent = LinearQAgent(n_features=n_features, n_actions=2, 
                         alpha=0.001, gamma=0.99, epsilon=0.1)
    
    episode_lengths = []
    
    for ep in range(episodes):
        obs, _ = env.reset()
        features = cartpole_features(obs)
        total_steps = 0
        
        for step in range(500):
            action = agent.choose_action(features)
            next_obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            next_features = cartpole_features(next_obs)
            
            agent.learn(features, action, reward, next_features, done)
            features = next_features
            total_steps += 1
            
            if done:
                break
        
        episode_lengths.append(total_steps)
        
        # Decay epsilon
        agent.epsilon = max(0.01, agent.epsilon * 0.995)
    
    env.close()
    return episode_lengths

lengths = train_cartpole_linear()
print(f"Last 100 episodes avg: {np.mean(lengths[-100:]):.0f} steps")
```

With good features, linear approximation can solve CartPole (~200+ steps average). But it struggles with more complex environments where the value function isn't linear in any obvious features.

## Tile Coding: Better Features Automatically

Manually designing features is tedious and domain-specific. **Tile coding** creates features automatically by discretizing the continuous space with overlapping grids:

```python
class TileCoding:
    def __init__(self, n_tilings=8, tiles_per_dim=8, state_bounds=None):
        """
        Create overlapping tilings of the state space.
        Each tiling is offset slightly, creating a rich feature representation.
        """
        self.n_tilings = n_tilings
        self.tiles_per_dim = tiles_per_dim
        self.state_bounds = state_bounds  # [(low, high), ...] per dimension
        self.n_tiles = n_tilings * (tiles_per_dim ** len(state_bounds))
    
    def get_features(self, state):
        """Return active tile indices for this state."""
        features = np.zeros(self.n_tiles)
        
        for tiling in range(self.n_tilings):
            # Offset each tiling slightly
            offset = tiling / self.n_tilings
            
            tile_indices = []
            for dim, (low, high) in enumerate(self.state_bounds):
                # Scale state to [0, tiles_per_dim]
                scaled = (state[dim] - low) / (high - low) * self.tiles_per_dim
                scaled += offset  # Apply offset
                tile_idx = int(np.clip(scaled, 0, self.tiles_per_dim - 1))
                tile_indices.append(tile_idx)
            
            # Convert multi-dim index to flat index
            flat_idx = tiling * (self.tiles_per_dim ** len(self.state_bounds))
            for i, idx in enumerate(tile_indices):
                flat_idx += idx * (self.tiles_per_dim ** i)
            
            features[flat_idx] = 1.0
        
        return features
```

Tile coding gives you:
- Automatic feature generation (no manual engineering)
- Guaranteed generalization (nearby states share tiles)
- Linear complexity (fast to compute)
- Works well with linear function approximation

## The Deadly Triad

Function approximation introduces instability. Three things together can cause divergence:

1. **Function approximation** (generalizing across states)
2. **Bootstrapping** (using estimated values in the target)
3. **Off-policy learning** (learning about a different policy than you follow)

Any two are fine. All three together can diverge — Q-values explode to infinity.

```python
# This can diverge:
# - Function approximation: linear Q
# - Bootstrapping: TD target uses Q(s')
# - Off-policy: Q-learning uses max Q(s')

td_target = reward + gamma * max(Q(next_features))  # All three present!
```

Solutions:
- Use on-policy methods (SARSA) — removes off-policy
- Use Monte Carlo returns — removes bootstrapping
- Use a table — removes function approximation
- Use careful architectures (target networks, experience replay) — Chapter 10

## Convergence Properties

| Method | Table | Linear FA | Nonlinear FA |
|---|---|---|---|
| MC (on-policy) | ✓ Converges | ✓ Converges | ~ May converge |
| TD (on-policy) | ✓ Converges | ✓ Converges | ✗ May diverge |
| Q-learning (off-policy) | ✓ Converges | ✗ May diverge | ✗ May diverge |

Linear function approximation with on-policy TD (SARSA) is guaranteed to converge. Q-learning with function approximation is not — but in practice, with careful tuning, it often works. Deep Q-Networks (Chapter 10) add tricks to make it stable.

## The Limitation of Linear

```python
# Linear Q can only represent:
Q(s, a) = w₁·f₁ + w₂·f₂ + ... + wₙ·fₙ

# It CANNOT represent:
# - "If health > 50 AND near goal, go right"
# - "If enemy is flanking AND ammo is low, retreat"
# - Complex nonlinear decision boundaries
```

For GridWorld Tactics, the value function is highly nonlinear. Whether to attack depends on a complex combination of health, ammo, enemy position, terrain, and more. No set of hand-crafted features can capture all these interactions.

We need a universal function approximator — something that can learn arbitrary nonlinear functions from data.

We need neural networks.

## What You Learned

- **Function approximation** — replace Q-table with a parameterized function
- **Feature engineering** — represent states as vectors; good features enable generalization
- **Linear Q** — Q(s,a) = w·φ(s,a); simple, fast, guaranteed convergence (on-policy)
- **Generalization** — learning about one state transfers to similar states
- **Tile coding** — automatic feature generation via overlapping discretizations
- **The deadly triad** — FA + bootstrapping + off-policy can diverge
- **Limitation** — linear methods can't represent complex nonlinear value functions

The Q-table era is over. Function approximation lets us handle large and continuous state spaces. But linear functions aren't expressive enough for complex games.

The next chapter replaces the linear function with a neural network — and introduces the tricks needed to make it stable.

---

[← Chapter 8: SARSA](chapter-08-sarsa.md) | [Chapter 10: Deep Q-Networks →](chapter-10-dqn.md)
