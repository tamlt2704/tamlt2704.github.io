# Chapter 2: How Confident Are We? — Credible Intervals

[← Chapter 1: Coin Flip](chapter-01-coin-flip.md) | [Chapter 3: MCMC →](chapter-03-mcmc.md)

---

## The Problem

Marcus, the product manager, stares at your Bayesian A/B test results:

"You said there's a 94% probability that B is better. But what does that mean for my decision? How much better? Could it be barely better? Could it be way better? I need a range, not just a probability."

He's asking for a **credible interval** — the Bayesian equivalent of a confidence interval, but with a much more intuitive interpretation.

## What's a Credible Interval?

A 90% credible interval is a range [a, b] such that there's a 90% probability the parameter lies within it, given the data.

```python
import numpy as np
from scipy.stats import beta

# Posterior for treatment B: Beta(8, 44)
post_B = beta(8, 44)

# 90% credible interval
lower = post_B.ppf(0.05)   # 5th percentile
upper = post_B.ppf(0.95)   # 95th percentile
mean = post_B.mean()

print(f"Readmission rate for B: {mean:.3f}")
print(f"90% credible interval: [{lower:.3f}, {upper:.3f}]")
```

```
Readmission rate for B: 0.154
90% credible interval: [0.076, 0.253]
```

Interpretation: "There's a 90% probability that the true readmission rate for treatment B is between 7.6% and 25.3%."

That's it. No gymnastics about "if we repeated this experiment many times." The interval directly answers: "Where is the parameter probably located?"

## Credible vs. Confidence Intervals

| | Credible Interval (Bayesian) | Confidence Interval (Frequentist) |
|---|---|---|
| Interpretation | "90% probability the parameter is in here" | "If we repeated this 100 times, ~90 intervals would contain the true value" |
| About | This specific interval | The procedure |
| Intuitive? | Yes | No (commonly misinterpreted) |
| Requires prior? | Yes | No |
| Width | Reflects actual uncertainty | Reflects sampling variability |

The frequentist confidence interval does NOT mean "90% chance the parameter is in this range." It means the *method* produces correct intervals 90% of the time. The Bayesian credible interval means exactly what people think confidence intervals mean.

## Highest Density Interval (HDI)

The equal-tailed interval (5th to 95th percentile) isn't always the best choice. For skewed distributions, the **Highest Density Interval** (HDI) is narrower:

```python
import arviz as az

# HDI: the narrowest interval containing 90% of the posterior mass
samples = post_B.rvs(100_000)
hdi = az.hdi(samples, hdi_prob=0.90)
print(f"90% HDI: [{hdi[0]:.3f}, {hdi[1]:.3f}]")
```

The HDI has a useful property: every point inside the interval has higher density (is more probable) than every point outside it.

For symmetric distributions (like a Normal), HDI and equal-tailed intervals are identical. For skewed distributions (common with small samples), HDI is more informative.

## Posterior Predictive Distribution

The credible interval tells you about the *parameter* (the true rate). But Marcus also wants to know: "If we enroll the next 100 patients in treatment B, how many will be readmitted?"

That's the **posterior predictive distribution** — it accounts for both parameter uncertainty AND sampling variability:

```python
# Posterior predictive: for each possible rate, simulate outcomes
n_future = 100  # Next 100 patients
rate_samples = post_B.rvs(10_000)  # Sample possible rates
predictions = np.array([
    np.random.binomial(n_future, rate) for rate in rate_samples
])

print(f"Expected readmissions (next 100 patients): {predictions.mean():.1f}")
print(f"90% prediction interval: [{np.percentile(predictions, 5):.0f}, {np.percentile(predictions, 95):.0f}]")
```

```
Expected readmissions (next 100 patients): 15.4
90% prediction interval: [6, 26]
```

The prediction interval is wider than the credible interval because it includes two sources of uncertainty:
1. We don't know the exact rate (parameter uncertainty)
2. Even if we knew the rate, outcomes vary (sampling noise)

## Communicating Uncertainty

Dr. Okafor needs to make decisions. Marcus needs to explain results to stakeholders. How do you present Bayesian results clearly?

### For Clinicians

```
Treatment B readmission rate:
  Most likely: 15%
  Plausible range: 8% to 25% (90% credible interval)
  Probability B is better than A: 94%
  Expected improvement: 5-15 percentage points
```

### For Executives

```
If we switch to Treatment B:
  - We expect ~15 readmissions per 100 patients (vs ~27 with A)
  - Could be as few as 6 or as many as 26 per 100
  - 94% confident it's an improvement
  - Recommend: expand trial to 200 patients to narrow uncertainty
```

### Visualizing Uncertainty

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: posterior distributions
x = np.linspace(0, 0.5, 200)
axes[0].fill_between(x, post_A.pdf(x), alpha=0.3, color="red", label="Treatment A")
axes[0].fill_between(x, post_B.pdf(x), alpha=0.3, color="blue", label="Treatment B")
axes[0].axvline(post_A.mean(), color="red", linestyle="--", alpha=0.7)
axes[0].axvline(post_B.mean(), color="blue", linestyle="--", alpha=0.7)

# Shade HDI for B
hdi_mask = (x >= hdi[0]) & (x <= hdi[1])
axes[0].fill_between(x[hdi_mask], post_B.pdf(x[hdi_mask]), alpha=0.5, color="blue")
axes[0].set_xlabel("Readmission Rate")
axes[0].set_ylabel("Density")
axes[0].set_title("Posterior Distributions with 90% HDI")
axes[0].legend()

# Right: posterior predictive
axes[1].hist(predictions, bins=range(0, 40), density=True, alpha=0.7, color="blue")
axes[1].axvline(predictions.mean(), color="red", linestyle="--", label=f"Mean: {predictions.mean():.1f}")
axes[1].set_xlabel("Readmissions (next 100 patients)")
axes[1].set_ylabel("Probability")
axes[1].set_title("Posterior Predictive: What to Expect")
axes[1].legend()

plt.tight_layout()
plt.show()
```

## PyMC: Posterior Predictive Checks

```python
import pymc as pm
import arviz as az

with pm.Model() as model:
    rate_B = pm.Beta("rate_B", alpha=1, beta=1)
    obs = pm.Binomial("obs", n=50, p=rate_B, observed=7)

    trace = pm.sample(2000, cores=2, random_seed=42)

    # Posterior predictive: simulate future data
    ppc = pm.sample_posterior_predictive(trace, random_seed=42)

# Summary with credible intervals
print(az.summary(trace, hdi_prob=0.90))

# Plot posterior with HDI
az.plot_posterior(trace, var_names=["rate_B"], hdi_prob=0.90)
plt.show()
```

## When Intervals Are Wide

Wide intervals aren't a failure — they're honest. A wide interval says "we don't know yet." That's valuable information.

```
50 patients:  90% CI = [0.076, 0.253]  — wide, uncertain
200 patients: 90% CI = [0.098, 0.192]  — narrower
1000 patients: 90% CI = [0.121, 0.167] — precise
```

The interval narrows as √n. To halve the width, you need 4x the data. This tells you how much more data you need for a given precision.

## Decision Rules

Marcus: "When is the interval narrow enough to decide?"

Common decision rules:

```python
# Rule 1: ROPE (Region of Practical Equivalence)
# If the entire credible interval is outside the ROPE, decide.
rope = (-0.02, 0.02)  # Less than 2% difference is "practically equivalent"
diff_samples = post_A.rvs(100_000) - post_B.rvs(100_000)
hdi_diff = az.hdi(diff_samples, hdi_prob=0.90)

if hdi_diff[0] > rope[1]:
    print("B is meaningfully better — decide now")
elif hdi_diff[1] < rope[0]:
    print("A is meaningfully better — decide now")
elif hdi_diff[0] > rope[0] and hdi_diff[1] < rope[1]:
    print("Practically equivalent — either is fine")
else:
    print("Uncertain — collect more data")
```

## What You Learned

- **Credible intervals** — "90% probability the parameter is in this range"
- **HDI** — narrowest interval containing X% of posterior mass
- **Posterior predictive** — what to expect for future observations
- **Communicating uncertainty** — different audiences need different framings
- **Interval width** — narrows with √n, tells you how much data you need
- **ROPE** — Region of Practical Equivalence for decision-making

Marcus can now explain to stakeholders: "The new protocol probably reduces readmissions by 5-15 percentage points. We're 94% confident it's better. We recommend expanding the trial to get a tighter estimate."

But there's a problem. The Beta-Binomial model had a closed-form posterior. Most real models don't. When you add covariates, hierarchical structure, or non-conjugate priors, you can't solve the math analytically.

You need a way to approximate posteriors for arbitrary models. That's MCMC.

---

[← Chapter 1: Coin Flip](chapter-01-coin-flip.md) | [Chapter 3: MCMC →](chapter-03-mcmc.md)
