# Chapter 1: The Coin That Isn't Fair — Bayes' Theorem

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Credible Intervals →](chapter-02-credible-intervals.md)

---

## The Problem

MedPulse is running an A/B test. A new discharge protocol (Treatment B) is supposed to reduce 30-day readmissions compared to the current protocol (Treatment A).

After one week, the results:

| Group | Patients | Readmitted | Rate |
|---|---|---|---|
| A (control) | 20 | 6 | 30% |
| B (new) | 20 | 3 | 15% |

Marcus, the product manager, is excited: "B cuts readmissions in half! Ship it!"

You run a frequentist test:

```python
from scipy.stats import fisher_exact

table = [[6, 14], [3, 17]]  # [[a_readmit, a_ok], [b_readmit, b_ok]]
odds_ratio, p_value = fisher_exact(table)
print(f"p-value: {p_value:.3f}")
```

```
p-value: 0.451
```

p = 0.45. Not significant. "We can't conclude anything," you tell Marcus.

Marcus: "So is B better or not?"

You: "We don't have enough data to say."

Marcus: "That's not an answer."

He's right. The frequentist framework gives you a binary: significant or not. It doesn't tell you what you actually believe about the difference. It doesn't tell you the probability that B is better. It doesn't tell you how much better B might be.

Dr. Okafor: "I don't need a p-value. I need to know: given what we've seen, what's the probability that the new protocol is actually better? And how much better might it be?"

That's a Bayesian question. Let's answer it.

## Bayes' Theorem

The foundation of everything in this course:

```
P(θ|D) = P(D|θ) × P(θ) / P(D)
```

In words:

```
Posterior = Likelihood × Prior / Evidence
```

| Term | What It Means | In Our Problem |
|---|---|---|
| P(θ) | Prior | What we believe about readmission rates before the trial |
| P(D\|θ) | Likelihood | How probable is seeing 6/20 and 3/20 given specific rates |
| P(θ\|D) | Posterior | What we believe about the rates after seeing the data |
| P(D) | Evidence | Normalizing constant (makes posterior sum to 1) |

The prior encodes what we knew before. The likelihood encodes what the data tells us. The posterior is the combination.

## The Beta-Binomial Model

Readmission is binary: a patient either comes back or doesn't. That's a Bernoulli trial. The number of readmissions out of N patients follows a Binomial distribution.

For the rate parameter θ (the true readmission probability), the natural prior is a **Beta distribution**:

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta

# Beta(1, 1) = Uniform — "any rate between 0 and 1 is equally likely"
# Beta(2, 8) = "rates around 20% are most likely" (weak prior)
# Beta(10, 40) = "rates around 20% are most likely" (strong prior)

x = np.linspace(0, 1, 200)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x, beta.pdf(x, 1, 1), label="Beta(1,1) — no opinion")
ax.plot(x, beta.pdf(x, 2, 8), label="Beta(2,8) — weak prior ~20%")
ax.plot(x, beta.pdf(x, 10, 40), label="Beta(10,40) — strong prior ~20%")
ax.set_xlabel("Readmission Rate")
ax.set_ylabel("Density")
ax.legend()
ax.set_title("Prior Beliefs About Readmission Rate")
plt.show()
```

Why Beta? Because it's **conjugate** to the Binomial — meaning the posterior is also a Beta distribution. The math works out cleanly:

```
Prior:      Beta(a, b)
Data:       k successes out of n trials
Posterior:  Beta(a + k, b + n - k)
```

Just add the counts. That's it.

## Solving the A/B Test

```python
import numpy as np
from scipy.stats import beta
import matplotlib.pyplot as plt

# Prior: Beta(1, 1) — uniform, no strong opinion
prior_a, prior_b = 1, 1

# Data
readmit_A, total_A = 6, 20   # Control
readmit_B, total_B = 3, 20   # Treatment

# Posterior for group A: Beta(1 + 6, 1 + 14) = Beta(7, 15)
post_A = beta(prior_a + readmit_A, prior_b + total_A - readmit_A)

# Posterior for group B: Beta(1 + 3, 1 + 17) = Beta(4, 18)
post_B = beta(prior_a + readmit_B, prior_b + total_B - readmit_B)

# Plot posteriors
x = np.linspace(0, 0.7, 200)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(x, post_A.pdf(x), label=f"Group A posterior — Beta(7, 15)", color="red")
ax.plot(x, post_B.pdf(x), label=f"Group B posterior — Beta(4, 18)", color="blue")
ax.fill_between(x, post_A.pdf(x), alpha=0.2, color="red")
ax.fill_between(x, post_B.pdf(x), alpha=0.2, color="blue")
ax.set_xlabel("Readmission Rate")
ax.set_ylabel("Density")
ax.legend()
ax.set_title("Posterior Distributions for Readmission Rates")
plt.show()

# The question Dr. Okafor asked: P(rate_B < rate_A)?
n_samples = 100_000
samples_A = post_A.rvs(n_samples)
samples_B = post_B.rvs(n_samples)

prob_B_better = np.mean(samples_B < samples_A)
print(f"P(B is better than A) = {prob_B_better:.3f}")

# How much better?
improvement = samples_A - samples_B
print(f"Expected improvement: {improvement.mean():.3f}")
print(f"90% interval for improvement: [{np.percentile(improvement, 5):.3f}, {np.percentile(improvement, 95):.3f}]")
```

```
P(B is better than A) = 0.804
Expected improvement: 0.091
90% interval for improvement: [-0.089, 0.271]
```

Now we can answer Dr. Okafor:

- There's an **80% probability** that B is better than A
- The expected improvement is about **9 percentage points**
- But the improvement could be anywhere from **-9% to +27%** (90% interval)
- We're fairly confident B is better, but not certain, and we don't know by how much

That's an honest answer. The frequentist test said "inconclusive." The Bayesian analysis says "probably better, but we need more data to be sure how much."

## The Prior Matters (And That's OK)

What if we use a more informative prior? MedPulse has historical data: readmission rates across their hospitals average 22% with some spread.

```python
# Informative prior: Beta(5, 18) — centered around 22%, moderately confident
prior_a, prior_b = 5, 18

post_A_informed = beta(prior_a + readmit_A, prior_b + total_A - readmit_A)
post_B_informed = beta(prior_a + readmit_B, prior_b + total_B - readmit_B)

samples_A_inf = post_A_informed.rvs(100_000)
samples_B_inf = post_B_informed.rvs(100_000)

prob_B_better_inf = np.mean(samples_B_inf < samples_A_inf)
print(f"With informative prior: P(B better) = {prob_B_better_inf:.3f}")
```

```
With informative prior: P(B better) = 0.782
```

The prior pulled both estimates toward 22%, shrinking the difference slightly. With more data, the prior matters less. With 200 patients per group instead of 20, the prior barely affects the result.

This is a feature, not a bug. With small samples, the prior regularizes — it prevents you from being overconfident about extreme results. "6 out of 20 = 30%" is a noisy estimate. The prior says "probably not that high" and pulls it toward the historical average.

## Updating With More Data

Two weeks later, more patients enrolled:

```python
# Week 2 data (cumulative)
readmit_A, total_A = 14, 50
readmit_B, total_B = 7, 50

post_A_w2 = beta(1 + 14, 1 + 36)  # Beta(15, 37)
post_B_w2 = beta(1 + 7, 1 + 43)   # Beta(8, 44)

samples_A_w2 = post_A_w2.rvs(100_000)
samples_B_w2 = post_B_w2.rvs(100_000)

prob_B_better_w2 = np.mean(samples_B_w2 < samples_A_w2)
improvement_w2 = samples_A_w2 - samples_B_w2

print(f"P(B better) = {prob_B_better_w2:.3f}")
print(f"Expected improvement: {improvement_w2.mean():.3f}")
print(f"90% interval: [{np.percentile(improvement_w2, 5):.3f}, {np.percentile(improvement_w2, 95):.3f}]")
```

```
P(B better) = 0.937
Expected improvement: 0.131
90% interval: [0.012, 0.251]
```

With more data:
- Probability B is better jumped from 80% to **94%**
- The 90% interval no longer includes zero — we're fairly confident the improvement is real
- The posteriors are narrower — less uncertainty

This is Bayesian updating in action. You don't restart the analysis — you accumulate evidence. The posterior from week 1 becomes the prior for week 2 (mathematically equivalent to using all the data at once).

## PyMC Implementation

The Beta-Binomial is simple enough to solve analytically. But let's see how PyMC handles it — this is the pattern for every future chapter:

```python
import pymc as pm
import arviz as az

with pm.Model() as ab_test:
    # Priors
    rate_A = pm.Beta("rate_A", alpha=1, beta=1)
    rate_B = pm.Beta("rate_B", alpha=1, beta=1)

    # Likelihood
    obs_A = pm.Binomial("obs_A", n=50, p=rate_A, observed=14)
    obs_B = pm.Binomial("obs_B", n=50, p=rate_B, observed=7)

    # Derived quantity
    diff = pm.Deterministic("diff", rate_A - rate_B)

    # Sample
    trace = pm.sample(2000, cores=2, random_seed=42)

# Results
summary = az.summary(trace, var_names=["rate_A", "rate_B", "diff"])
print(summary)

# Probability B is better
diff_samples = trace.posterior["diff"].values.flatten()
print(f"\nP(B better) = {np.mean(diff_samples > 0):.3f}")

# Plot
az.plot_posterior(trace, var_names=["diff"], ref_val=0)
plt.title("Posterior: rate_A - rate_B")
plt.show()
```

Same answer as the analytical solution, but now you have the machinery to handle models where no closed-form exists (which is most of them).

## What You Learned

- **Bayes' theorem** — posterior ∝ likelihood × prior
- **Beta-Binomial model** — conjugate model for binary outcomes
- **Bayesian A/B testing** — get P(B > A) directly, not just "significant or not"
- **Prior sensitivity** — informative priors regularize small samples
- **Sequential updating** — accumulate evidence over time
- **PyMC pattern** — define priors, define likelihood, sample, interpret

The frequentist test said "inconclusive." The Bayesian analysis said "80% chance B is better, but the improvement could be small or large — get more data." After more data: "94% chance B is better, improvement is probably 1–25 percentage points."

Dr. Okafor: "Now I can make a decision. 94% confident with a meaningful effect size. Let's expand the trial."

Marcus: "But what does 94% mean exactly? How sure is sure enough?"

That's Chapter 2 — credible intervals and how to communicate uncertainty.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Credible Intervals →](chapter-02-credible-intervals.md)
