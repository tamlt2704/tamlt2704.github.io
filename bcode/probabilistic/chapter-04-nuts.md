# Chapter 4: A Better Sampler — HMC and NUTS

[← Chapter 3: MCMC](chapter-03-mcmc.md) | [Chapter 5: Bayesian Regression →](chapter-05-linear-regression.md)

---

## The Problem

The Metropolis-Hastings sampler from Chapter 3 took 20,000 iterations to produce 3,000 effective samples. For a 4-parameter model. Dr. Okafor's real model has 30 parameters (patient demographics, lab values, comorbidities). At this rate, it would take hours.

Priya: "I ran your sampler overnight. It produced 500 effective samples. The trace plot looks like a drunk person walking. This isn't production-ready."

The problem with random walks: in high dimensions, most random directions are perpendicular to where you want to go. The sampler wastes 99% of its steps going sideways.

## Hamiltonian Monte Carlo (HMC)

HMC borrows from physics. Instead of a random walk, imagine the parameter space as a landscape where the posterior density is the elevation. Drop a ball on this landscape. It rolls toward high-density regions naturally.

The physics analogy:
- **Position** = parameter values (where we are)
- **Momentum** = velocity (how fast we're moving)
- **Potential energy** = negative log posterior (high density = low energy)
- **Kinetic energy** = momentum² / 2

The ball follows Hamilton's equations — it explores the posterior efficiently because physics conserves energy. It can't get stuck in local modes (it has momentum to carry it through valleys).

```python
def hmc_step(current_q, log_prob_grad, step_size, n_leapfrog):
    """
    One HMC step.
    current_q: current position (parameter values)
    log_prob_grad: function returning (log_prob, gradient)
    step_size: leapfrog step size (epsilon)
    n_leapfrog: number of leapfrog steps (L)
    """
    q = current_q.copy()
    # Random momentum
    p = np.random.normal(size=len(q))
    current_p = p.copy()

    # Leapfrog integration
    log_prob, grad = log_prob_grad(q)
    p += 0.5 * step_size * grad  # Half step for momentum

    for i in range(n_leapfrog - 1):
        q += step_size * p  # Full step for position
        log_prob, grad = log_prob_grad(q)
        p += step_size * grad  # Full step for momentum

    q += step_size * p  # Final position step
    log_prob_new, grad = log_prob_grad(q)
    p += 0.5 * step_size * grad  # Final half step for momentum

    # Metropolis acceptance (corrects for numerical integration error)
    current_log_prob, _ = log_prob_grad(current_q)
    current_H = -current_log_prob + 0.5 * np.sum(current_p ** 2)
    proposed_H = -log_prob_new + 0.5 * np.sum(p ** 2)

    if np.log(np.random.uniform()) < current_H - proposed_H:
        return q, True  # Accept
    else:
        return current_q, False  # Reject
```

### Why HMC Is Better

| | Metropolis-Hastings | HMC |
|---|---|---|
| Movement | Random walk | Guided by gradient |
| Acceptance rate | ~23% optimal (high-D) | ~65-80% |
| Correlation | High (small steps) | Low (long trajectories) |
| ESS per iteration | Low | High |
| Scales with dimensions | Poorly (√D steps needed) | Well (D^(1/4) steps) |
| Requires | Only density evaluation | Density + gradient |

## NUTS: No-U-Turn Sampler

HMC has two tuning parameters: step size (ε) and number of leapfrog steps (L). Choose wrong and it fails:
- L too small → doesn't explore enough (like Metropolis)
- L too large → wastes computation, U-turns back to start

**NUTS** (No-U-Turn Sampler) automatically determines L by detecting when the trajectory starts turning back. It builds a binary tree of leapfrog steps and stops when the trajectory makes a U-turn.

You don't need to implement NUTS — PyMC does it for you. But understanding what it does helps you diagnose problems.

## PyMC: NUTS in Practice

```python
import pymc as pm
import arviz as az
import numpy as np

# Same data from Chapter 3
with pm.Model() as logistic_model:
    # Priors
    intercept = pm.Normal("intercept", mu=0, sigma=10)
    beta_age = pm.Normal("beta_age", mu=0, sigma=2)
    beta_visits = pm.Normal("beta_visits", mu=0, sigma=2)
    beta_los = pm.Normal("beta_los", mu=0, sigma=2)

    # Linear predictor
    logit_p = intercept + beta_age * age_std + beta_visits * visits_std + beta_los * los_std

    # Likelihood
    y = pm.Bernoulli("y", logit_p=logit_p, observed=readmitted)

    # Sample with NUTS (default)
    trace = pm.sample(2000, tune=1000, cores=2, random_seed=42)

# Summary
print(az.summary(trace, hdi_prob=0.90))
```

```
           mean    sd  hdi_5%  hdi_95%  ess_bulk  ess_tail  r_hat
intercept -0.41  0.17  -0.70   -0.12    3842      3156      1.00
beta_age   0.30  0.16   0.03    0.56    4012      3298      1.00
beta_visits 0.81  0.17   0.53    1.09    3756      3012      1.00
beta_los  -0.20  0.15  -0.45    0.05    3987      3245      1.00
```

2000 samples, ~4000 ESS. That's 200% efficiency (ESS > n_samples because NUTS uses multiple gradient evaluations per sample). Compare to Metropolis: 20,000 samples, 3000 ESS (15% efficiency).

## Diagnostics

### R-hat (Convergence)

R-hat compares variance within chains to variance between chains. If chains haven't converged to the same distribution, R-hat > 1.

```python
# R-hat should be < 1.01 for all parameters
rhat = az.rhat(trace)
print(rhat)
```

R-hat > 1.01 → chains haven't converged. Run longer or fix the model.

### Divergences

NUTS reports "divergent transitions" — places where the numerical integration failed. Divergences indicate the posterior has sharp features the sampler can't navigate.

```python
# Check for divergences
divergences = trace.sample_stats["diverging"].sum().values
print(f"Divergent transitions: {divergences}")
```

Divergences > 0 → the posterior might not be well-sampled. Common fixes:
- Reparameterize the model
- Use more informative priors
- Increase `target_accept` (smaller step size)

```python
# If divergences occur:
trace = pm.sample(2000, tune=1000, target_accept=0.95)  # Default is 0.8
```

### Trace Plots

```python
az.plot_trace(trace)
plt.tight_layout()
plt.show()
```

Good: "hairy caterpillar" traces, smooth histograms, chains overlap.
Bad: trends, multimodality, chains in different places.

### Effective Sample Size

```python
az.plot_ess(trace, kind="evolution")
plt.show()
```

ESS should grow linearly with iterations. If it plateaus, the sampler is stuck.

## Tuning Phase

PyMC's `tune=1000` means: spend 1000 iterations adjusting the step size before collecting samples. During tuning:
- Step size adapts to achieve ~80% acceptance rate
- Mass matrix adapts to account for parameter correlations
- These samples are discarded (not part of the posterior)

Never use tuning samples for inference. They're the sampler learning to walk.

## When NUTS Struggles

1. **Multimodal posteriors**: NUTS can't jump between disconnected modes
2. **Funnel geometries**: hierarchical models with varying scales
3. **Discrete parameters**: NUTS needs gradients (continuous only)
4. **Very high dimensions**: >1000 parameters gets slow

For these cases, you need specialized techniques (reparameterization, marginalization, variational inference). We'll encounter some in later chapters.

## What You Learned

- **HMC** — uses gradients to guide sampling, not random walks
- **Leapfrog integration** — simulates Hamiltonian dynamics
- **NUTS** — automatically tunes trajectory length (no-U-turn)
- **PyMC sampling** — `pm.sample()` uses NUTS by default
- **R-hat** — convergence diagnostic, should be < 1.01
- **Divergences** — numerical integration failures, need fixing
- **ESS** — effective sample size, measures sampling efficiency
- **Tuning** — adaptive phase before collecting samples

NUTS is the workhorse of modern Bayesian inference. It's what PyMC, Stan, and NumPyro use by default. It handles 10-1000 parameters efficiently with minimal tuning.

Now that you have a reliable sampler, let's use it for something useful: regression with full uncertainty on predictions.

---

[← Chapter 3: MCMC](chapter-03-mcmc.md) | [Chapter 5: Bayesian Regression →](chapter-05-linear-regression.md)
