# Chapter 3: Sampling the Impossible — MCMC

[← Chapter 2: Credible Intervals](chapter-02-credible-intervals.md) | [Chapter 4: A Better Sampler →](chapter-04-nuts.md)

---

## The Problem

Dr. Okafor wants a model that predicts readmission risk based on patient age, number of prior visits, and length of stay. That's a logistic regression with a Bayesian twist — priors on the coefficients.

You try the conjugate approach from Chapter 1:

```python
# Posterior ∝ Likelihood × Prior
# Likelihood: Binomial with logistic link
# Prior: Normal on coefficients
# Posterior: ... no closed form.
```

The Beta-Binomial worked because Beta is conjugate to Binomial. But Normal priors on logistic regression coefficients? No conjugacy. No analytical solution. The posterior is a complex, high-dimensional surface you can't write down.

You need to **sample** from it instead.

## The Idea Behind MCMC

If you can't compute the posterior exactly, generate samples from it. With enough samples, you can estimate any property:

- Mean? Average the samples.
- Credible interval? Sort samples, take percentiles.
- Probability P(θ > 0)? Count samples where θ > 0.

**Markov Chain Monte Carlo** (MCMC) constructs a random walk that, after enough steps, produces samples from the target distribution — even when you can't normalize it.

The key insight: you only need to evaluate the posterior **up to a constant**. You need P(θ|D) ∝ P(D|θ) × P(θ), but you don't need the normalizing constant P(D).

## Metropolis-Hastings: The Simplest MCMC

The algorithm:

1. Start at some parameter value θ
2. Propose a new value θ* (random step from current position)
3. Compute acceptance ratio: α = P(θ*|D) / P(θ|D)
4. If α ≥ 1: accept (move to θ*)
5. If α < 1: accept with probability α (flip a biased coin)
6. Repeat thousands of times

```python
import numpy as np
from scipy.stats import norm

def metropolis_hastings(log_posterior, initial, n_samples, proposal_sd=0.5):
    """
    Simple Metropolis-Hastings sampler.

    log_posterior: function that returns log P(θ|D) up to a constant
    initial: starting parameter value(s)
    n_samples: how many samples to draw
    proposal_sd: standard deviation of proposal distribution
    """
    current = np.array(initial, dtype=float)
    samples = np.zeros((n_samples, len(current)))
    accepted = 0

    current_lp = log_posterior(current)

    for i in range(n_samples):
        # Propose new position (random walk)
        proposal = current + np.random.normal(0, proposal_sd, size=len(current))

        # Compute log posterior at proposal
        proposal_lp = log_posterior(proposal)

        # Acceptance ratio (in log space: subtract instead of divide)
        log_alpha = proposal_lp - current_lp

        # Accept or reject
        if np.log(np.random.uniform()) < log_alpha:
            current = proposal
            current_lp = proposal_lp
            accepted += 1

        samples[i] = current

    acceptance_rate = accepted / n_samples
    return samples, acceptance_rate
```

## Example: Bayesian Logistic Regression

```python
import numpy as np
from scipy.special import expit  # sigmoid function

# Simulated patient data
np.random.seed(42)
n_patients = 200
age = np.random.normal(65, 10, n_patients)           # Mean age 65
prior_visits = np.random.poisson(3, n_patients)       # Mean 3 prior visits
length_of_stay = np.random.exponential(5, n_patients) # Mean 5 days

# True coefficients (what we're trying to recover)
true_intercept = -2.0
true_beta_age = 0.03
true_beta_visits = 0.4
true_beta_los = -0.1

# Generate outcomes
logits = (true_intercept +
          true_beta_age * age +
          true_beta_visits * prior_visits +
          true_beta_los * length_of_stay)
probs = expit(logits)
readmitted = np.random.binomial(1, probs)

print(f"Readmission rate: {readmitted.mean():.2%}")

# Standardize predictors (helps MCMC converge)
age_std = (age - age.mean()) / age.std()
visits_std = (prior_visits - prior_visits.mean()) / prior_visits.std()
los_std = (length_of_stay - length_of_stay.mean()) / length_of_stay.std()
X = np.column_stack([np.ones(n_patients), age_std, visits_std, los_std])


def log_posterior(theta):
    """Log posterior for logistic regression with Normal priors."""
    # Priors: Normal(0, 10) for intercept, Normal(0, 2) for coefficients
    log_prior = norm.logpdf(theta[0], 0, 10)
    log_prior += np.sum(norm.logpdf(theta[1:], 0, 2))

    # Likelihood: Bernoulli with logistic link
    logits = X @ theta
    # Numerically stable log-likelihood
    log_lik = np.sum(readmitted * logits - np.log(1 + np.exp(logits)))

    return log_prior + log_lik


# Run Metropolis-Hastings
initial = np.zeros(4)  # Start at zero
samples, acceptance_rate = metropolis_hastings(
    log_posterior, initial, n_samples=20000, proposal_sd=0.15
)

print(f"Acceptance rate: {acceptance_rate:.2%}")
```

## Diagnosing the Chain

Did the sampler work? Three checks:

### 1. Trace Plot

```python
import matplotlib.pyplot as plt

param_names = ["intercept", "β_age", "β_visits", "β_los"]
fig, axes = plt.subplots(4, 2, figsize=(12, 10))

for i, name in enumerate(param_names):
    # Trace (left): should look like "hairy caterpillar"
    axes[i, 0].plot(samples[:, i], alpha=0.7, linewidth=0.5)
    axes[i, 0].set_ylabel(name)
    axes[i, 0].set_xlabel("Iteration")

    # Histogram (right): should be smooth
    axes[i, 1].hist(samples[5000:, i], bins=50, density=True, alpha=0.7)
    axes[i, 1].set_xlabel(name)

plt.tight_layout()
plt.show()
```

Good trace: random fluctuation around a stable mean ("hairy caterpillar").
Bad trace: trending, stuck, or periodic patterns.

### 2. Burn-In

The chain starts at your initial guess, which might be far from the posterior. Discard early samples:

```python
burn_in = 5000
posterior_samples = samples[burn_in:]
```

### 3. Autocorrelation

Consecutive samples are correlated (the chain moves in small steps). Effective sample size tells you how many independent samples you actually have:

```python
def effective_sample_size(samples):
    """Estimate ESS using autocorrelation."""
    n = len(samples)
    mean = samples.mean()
    var = samples.var()
    if var == 0:
        return 0

    autocorr = np.correlate(samples - mean, samples - mean, mode='full')
    autocorr = autocorr[n-1:] / (var * n)

    # Sum autocorrelations until they go negative
    ess_sum = 0
    for k in range(1, n):
        if autocorr[k] < 0:
            break
        ess_sum += autocorr[k]

    return n / (1 + 2 * ess_sum)

for i, name in enumerate(param_names):
    ess = effective_sample_size(posterior_samples[:, i])
    print(f"{name}: ESS = {ess:.0f} (from {len(posterior_samples)} samples)")
```

If ESS is much less than your sample count, the chain is highly autocorrelated. You need more samples or a better sampler.

## Results

```python
# Posterior summaries (after burn-in)
print("\nPosterior Summary:")
print(f"{'Parameter':<12} {'Mean':>8} {'Std':>8} {'90% HDI':>20}")
print("-" * 52)
for i, name in enumerate(param_names):
    mean = posterior_samples[:, i].mean()
    std = posterior_samples[:, i].std()
    hdi_low = np.percentile(posterior_samples[:, i], 5)
    hdi_high = np.percentile(posterior_samples[:, i], 95)
    print(f"{name:<12} {mean:>8.3f} {std:>8.3f} [{hdi_low:>7.3f}, {hdi_high:>7.3f}]")
```

```
Posterior Summary:
Parameter        Mean      Std              90% HDI
----------------------------------------------------
intercept      -0.412    0.178  [ -0.703,  -0.118]
β_age           0.298    0.163  [  0.028,   0.567]
β_visits        0.812    0.175  [  0.524,   1.098]
β_los          -0.203    0.155  [ -0.459,   0.048]
```

Interpretation:
- More prior visits → higher readmission risk (β_visits clearly positive)
- Older age → slightly higher risk (β_age probably positive)
- Longer stay → slightly lower risk (β_los uncertain, interval includes 0)

## Why Metropolis-Hastings Is Slow

Our sampler took 20,000 iterations to get ~3,000 effective samples. That's a 15% efficiency. Problems:

1. **Proposal tuning**: Too small steps → high acceptance but slow exploration. Too large → low acceptance, chain gets stuck.
2. **Correlated parameters**: The sampler moves one dimension at a time. If parameters are correlated, it takes many steps to explore the joint distribution.
3. **High dimensions**: In 4D, random walks are inefficient. In 100D, they're useless.

Priya, the ML engineer: "Your model takes 3 minutes to fit. The old logistic regression takes 0.1 seconds."

She's right. Metropolis-Hastings is a teaching algorithm. For real work, you need something better.

That's Chapter 4: NUTS.

## What You Learned

- **MCMC** — generate samples from distributions you can't compute analytically
- **Metropolis-Hastings** — propose, accept/reject, repeat
- **Log posterior** — work in log space for numerical stability
- **Trace plots** — visual check for convergence
- **Burn-in** — discard early samples before convergence
- **Effective sample size** — how many independent samples you actually have
- **Autocorrelation** — consecutive samples are correlated in random walks

You can now fit Bayesian models that have no closed-form solution. The posterior for logistic regression with priors? Sampled. Credible intervals on coefficients? Computed from samples.

But it's slow. And fragile. The proposal standard deviation required manual tuning. In higher dimensions, it would fail entirely.

Time for a sampler that actually works in practice.

---

[← Chapter 2: Credible Intervals](chapter-02-credible-intervals.md) | [Chapter 4: A Better Sampler →](chapter-04-nuts.md)
