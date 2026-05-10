# Chapter 6: Groups That Differ — Hierarchical Models

[← Chapter 5: Linear Regression](chapter-05-linear-regression.md) | [Chapter 7: Counts and Rates →](chapter-07-glm.md)

---

## The Problem

MedPulse operates across 20 hospitals. The readmission rates vary:

| Hospital | Patients | Readmissions | Rate |
|---|---|---|---|
| City General | 500 | 115 | 23.0% |
| St. Mary's | 450 | 85 | 18.9% |
| Rural Clinic A | 30 | 12 | 40.0% |
| Rural Clinic B | 25 | 3 | 12.0% |

Rural Clinic A has a 40% readmission rate. Is it really that bad, or is it just noise from 30 patients?

Two bad approaches:
1. **Complete pooling**: Ignore hospitals, fit one model. Loses real differences.
2. **No pooling**: Fit separate models per hospital. Rural clinics have huge uncertainty (n=30).

The right approach: **partial pooling** — share information across hospitals while allowing each to differ.

## The Hierarchical Model

```python
import pymc as pm
import arviz as az
import numpy as np

# Data: 20 hospitals
np.random.seed(42)
n_hospitals = 20
true_rates = np.random.beta(4, 16, n_hospitals)  # True rates ~20% with variation
n_patients = np.random.choice([30, 50, 100, 200, 500], n_hospitals)
readmissions = np.random.binomial(n_patients, true_rates)

hospital_names = [f"H{i:02d}" for i in range(n_hospitals)]

with pm.Model() as hierarchical_model:
    # Hyperpriors: the "population" distribution of rates
    mu = pm.Beta("mu", alpha=2, beta=8)  # Population mean rate
    kappa = pm.HalfNormal("kappa", sigma=20)  # Concentration (how similar hospitals are)

    # Hospital-level rates (drawn from population distribution)
    # Beta parameterized by mean and concentration
    alpha = mu * kappa
    beta_param = (1 - mu) * kappa
    rates = pm.Beta("rates", alpha=alpha, beta=beta_param, shape=n_hospitals)

    # Likelihood
    obs = pm.Binomial("obs", n=n_patients, p=rates, observed=readmissions)

    # Sample
    trace = pm.sample(2000, tune=1000, cores=2, random_seed=42)
```

## Shrinkage: The Key Insight

```python
# Compare raw rates vs. hierarchical estimates
raw_rates = readmissions / n_patients
posterior_rates = trace.posterior["rates"].mean(dim=["chain", "draw"]).values

print(f"{'Hospital':<10} {'N':>5} {'Raw Rate':>10} {'Hierarchical':>14} {'Shrinkage':>10}")
print("-" * 55)
for i in range(n_hospitals):
    shrink = raw_rates[i] - posterior_rates[i]
    print(f"{hospital_names[i]:<10} {n_patients[i]:>5} {raw_rates[i]:>10.1%} "
          f"{posterior_rates[i]:>14.1%} {shrink:>+10.1%}")
```

The hierarchical model **shrinks** extreme estimates toward the population mean:
- Rural Clinic A (40% from 30 patients) → shrunk toward ~25%
- Rural Clinic B (12% from 25 patients) → shrunk toward ~18%
- City General (23% from 500 patients) → barely changed

Small samples get pulled more. Large samples resist. This is **partial pooling** — the model borrows strength from other hospitals to stabilize noisy estimates.

## Why Shrinkage Is Good

Rural Clinic A's raw rate is 40%. But with only 30 patients, the 90% confidence interval is [23%, 59%]. The hierarchical model says "other hospitals are around 20%. This clinic probably isn't as extreme as 40% — more likely around 28%."

If you had to bet on the *next* 100 patients at Rural Clinic A, the hierarchical estimate (28%) would be more accurate than the raw rate (40%). This is the James-Stein phenomenon — shrinkage improves predictions for all groups simultaneously.

## Visualizing Partial Pooling

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 6))

# Sort by sample size
sort_idx = np.argsort(n_patients)

for i, idx in enumerate(sort_idx):
    # Raw rate
    ax.scatter(i, raw_rates[idx], color="red", marker="x", s=80, zorder=5)
    # Hierarchical estimate with HDI
    post_samples = trace.posterior["rates"].values[:, :, idx].flatten()
    hdi = az.hdi(post_samples, hdi_prob=0.90)
    ax.scatter(i, posterior_rates[idx], color="blue", s=60, zorder=5)
    ax.plot([i, i], hdi, color="blue", linewidth=2, alpha=0.5)
    # Arrow showing shrinkage
    ax.annotate("", xy=(i, posterior_rates[idx]), xytext=(i, raw_rates[idx]),
                arrowprops=dict(arrowstyle="->", color="gray", alpha=0.5))

# Population mean
pop_mean = trace.posterior["mu"].mean().values
ax.axhline(pop_mean, color="green", linestyle="--", alpha=0.5, label="Population mean")

ax.set_xticks(range(n_hospitals))
ax.set_xticklabels([f"{hospital_names[sort_idx[i]]}\n(n={n_patients[sort_idx[i]]})"
                    for i in range(n_hospitals)], fontsize=8)
ax.set_ylabel("Readmission Rate")
ax.set_title("Partial Pooling: Shrinkage Toward Population Mean")
ax.legend(["Population mean", "Raw rate (×)", "Hierarchical estimate (●)"])
plt.tight_layout()
plt.show()
```

## Adding Predictors

Hierarchical models can include covariates with varying slopes:

```python
with pm.Model() as hierarchical_regression:
    # Population-level effects
    mu_intercept = pm.Normal("mu_intercept", mu=0, sigma=2)
    mu_beta_age = pm.Normal("mu_beta_age", mu=0, sigma=1)

    # Between-hospital variation
    sigma_intercept = pm.HalfNormal("sigma_intercept", sigma=1)
    sigma_beta_age = pm.HalfNormal("sigma_beta_age", sigma=0.5)

    # Hospital-specific parameters
    intercepts = pm.Normal("intercepts", mu=mu_intercept, sigma=sigma_intercept,
                          shape=n_hospitals)
    betas_age = pm.Normal("betas_age", mu=mu_beta_age, sigma=sigma_beta_age,
                         shape=n_hospitals)

    # Each hospital has its own intercept and age effect
    # But they're all drawn from a common distribution
```

## When to Use Hierarchical Models

- Multiple groups with shared structure (hospitals, schools, patients)
- Some groups have little data (partial pooling helps)
- You want to estimate group-level AND population-level effects
- You want to predict for a NEW group (use population parameters)

## What You Learned

- **Hierarchical models** — parameters drawn from a population distribution
- **Partial pooling** — between complete pooling and no pooling
- **Shrinkage** — extreme estimates pulled toward population mean
- **Small sample benefit** — groups with little data borrow strength from others
- **Hyperpriors** — priors on the population-level parameters

Dr. Okafor: "So Rural Clinic A isn't as bad as the raw numbers suggest?"

You: "Probably not. With only 30 patients, the raw rate is noisy. The model estimates they're around 28%, not 40%. But we should still investigate — they're above average even after shrinkage."

Next: not everything is Gaussian. Patient counts, binary outcomes, and rates need different likelihood functions.

---

[← Chapter 5: Linear Regression](chapter-05-linear-regression.md) | [Chapter 7: Counts and Rates →](chapter-07-glm.md)
