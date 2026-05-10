# Chapter 10: Which Model Is Better? — Model Comparison

[← Chapter 9: Missing Data](chapter-09-missing-data.md) | [Chapter 11: Mixture Models →](chapter-11-mixtures.md)

---

## The Problem

MedPulse now has three models predicting length of stay:

1. **Linear**: LOS ~ age + severity (Chapter 5)
2. **Quadratic**: LOS ~ age + severity + severity² (maybe LOS plateaus at high severity)
3. **Hierarchical**: LOS ~ age + severity, varying by hospital (Chapter 6)

All three fit the training data reasonably well. The quadratic model has the lowest residuals. But does that mean it's the best model? Or is it just overfitting?

You can't use R² — it always favors more complex models. You can't use p-values — this is Bayesian. You need tools that balance fit against complexity.

## Posterior Predictive Checks: Does the Model Make Sense?

Before comparing models, check if each one generates data that looks like reality:

```python
import pymc as pm
import arviz as az
import numpy as np
import matplotlib.pyplot as plt

# Simulated LOS data
np.random.seed(42)
n = 200
age = np.random.normal(68, 12, n)
severity = np.random.uniform(1, 8, n)

# True relationship: slightly nonlinear
true_los = 2.0 + 0.04 * age + 1.5 * severity + 0.1 * severity**2
los = true_los + np.random.normal(0, 2.5, n)
los = np.maximum(los, 0.5)

# Standardize
age_z = (age - age.mean()) / age.std()
sev_z = (severity - severity.mean()) / severity.std()
sev_z2 = sev_z**2
```

```python
# Fit three models
with pm.Model() as linear_model:
    b0 = pm.Normal("b0", mu=10, sigma=5)
    b_age = pm.Normal("b_age", mu=0, sigma=2)
    b_sev = pm.Normal("b_sev", mu=0, sigma=2)
    sigma = pm.HalfNormal("sigma", sigma=3)
    mu = b0 + b_age * age_z + b_sev * sev_z
    y = pm.Normal("y", mu=mu, sigma=sigma, observed=los)
    trace_linear = pm.sample(2000, tune=1000, cores=2, random_seed=42)
    ppc_linear = pm.sample_posterior_predictive(trace_linear, random_seed=42)

with pm.Model() as quadratic_model:
    b0 = pm.Normal("b0", mu=10, sigma=5)
    b_age = pm.Normal("b_age", mu=0, sigma=2)
    b_sev = pm.Normal("b_sev", mu=0, sigma=2)
    b_sev2 = pm.Normal("b_sev2", mu=0, sigma=2)
    sigma = pm.HalfNormal("sigma", sigma=3)
    mu = b0 + b_age * age_z + b_sev * sev_z + b_sev2 * sev_z2
    y = pm.Normal("y", mu=mu, sigma=sigma, observed=los)
    trace_quad = pm.sample(2000, tune=1000, cores=2, random_seed=42)
    ppc_quad = pm.sample_posterior_predictive(trace_quad, random_seed=42)
```

```python
# Posterior predictive check: compare observed vs simulated data
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

az.plot_ppc(az.from_pymc3(posterior_predictive=ppc_linear, model=linear_model),
            ax=axes[0], num_pp_samples=100)
axes[0].set_title("Linear Model: Posterior Predictive Check")

az.plot_ppc(az.from_pymc3(posterior_predictive=ppc_quad, model=quadratic_model),
            ax=axes[1], num_pp_samples=100)
axes[1].set_title("Quadratic Model: Posterior Predictive Check")
plt.tight_layout()
plt.show()
```

If the simulated data (light blue) doesn't overlap the observed data (dark blue), the model is misspecified. Fix the model before comparing.

## WAIC: Widely Applicable Information Criterion

WAIC estimates out-of-sample predictive accuracy without actually holding out data:

```python
# Compute WAIC for each model
waic_linear = az.waic(trace_linear, linear_model)
waic_quad = az.waic(trace_quad, quadratic_model)

print("Linear model WAIC:", waic_linear)
print("Quadratic model WAIC:", waic_quad)

# Compare directly
comparison = az.compare({"linear": trace_linear, "quadratic": trace_quad})
print(comparison)
```

Lower WAIC = better predictive accuracy. WAIC automatically penalizes complexity — a model with more parameters needs to fit substantially better to win.

## LOO-CV: Leave-One-Out Cross-Validation

LOO-CV is often preferred over WAIC. It estimates how well the model predicts each observation when that observation is left out:

```python
# LOO-CV (uses Pareto-smoothed importance sampling — no refitting needed)
loo_linear = az.loo(trace_linear, linear_model)
loo_quad = az.loo(trace_quad, quadratic_model)

print("Linear LOO:", loo_linear)
print("Quadratic LOO:", loo_quad)

# Full comparison with standard errors
comparison = az.compare(
    {"linear": trace_linear, "quadratic": trace_quad},
    ic="loo"
)
print(comparison)
```

```
          rank  loo    p_loo  d_loo   weight  se     dse    warning
quadratic  0   -452.3  4.1   0.0     0.78    12.3   0.0    False
linear     1   -458.7  3.0   6.4     0.22    12.1   4.2    False
```

Key columns:
- **rank**: best model first
- **d_loo**: difference from best (0 = best)
- **dse**: standard error of the difference
- **weight**: stacking weight (how much to trust each model)
- **warning**: True if some observations are influential (Pareto k > 0.7)

## Interpreting the Comparison

The quadratic model wins by 6.4 elpd points with a standard error of 4.2. Is that decisive?

```python
# Rule of thumb: difference > 2*dse suggests meaningful improvement
d_loo = 6.4
dse = 4.2
print(f"Difference: {d_loo:.1f} ± {dse:.1f}")
print(f"Ratio: {d_loo/dse:.1f}")  # > 2 suggests real difference
```

A ratio of 1.5 is suggestive but not conclusive. The quadratic model is probably better, but you can't be certain. This is where model stacking helps.

## Model Stacking: Use Both

When models are close, don't pick one — combine them:

```python
# Stacking weights from az.compare
# weight = 0.78 for quadratic, 0.22 for linear
# This means: use 78% quadratic predictions + 22% linear predictions

# In practice:
ppc_linear_samples = ppc_linear.posterior_predictive["y"].values.reshape(-1, n)
ppc_quad_samples = ppc_quad.posterior_predictive["y"].values.reshape(-1, n)

# Stacked predictions
w_quad, w_linear = 0.78, 0.22
n_samples = min(ppc_linear_samples.shape[0], ppc_quad_samples.shape[0])

# Randomly select from each model according to weights
n_from_quad = int(n_samples * w_quad)
n_from_linear = n_samples - n_from_quad

stacked_ppc = np.vstack([
    ppc_quad_samples[:n_from_quad],
    ppc_linear_samples[:n_from_linear]
])

print(f"Stacked prediction mean: {stacked_ppc.mean():.2f}")
print(f"Stacked prediction std: {stacked_ppc.std():.2f}")
```

Stacking hedges your bets. If you're wrong about which model is better, the stacked prediction is still reasonable.

## Diagnosing LOO Problems

Sometimes LOO warns about influential observations (Pareto k > 0.7):

```python
# Check for problematic observations
loo_result = az.loo(trace_quad, quadratic_model, pointwise=True)
pareto_k = loo_result.pareto_k.values

n_bad = (pareto_k > 0.7).sum()
print(f"Observations with Pareto k > 0.7: {n_bad}")

if n_bad > 0:
    bad_idx = np.where(pareto_k > 0.7)[0]
    print(f"Problematic patients: {bad_idx}")
    print(f"Their LOS values: {los[bad_idx]}")
    # These are outliers that strongly influence the model
```

High Pareto k means the model is surprised by that observation. Options:
1. Use a heavier-tailed likelihood (Student-t instead of Normal)
2. Investigate those patients — are they data errors?
3. Use moment-matching or refitting for those points

## Bayes Factors (Use with Caution)

Bayes factors compare the marginal likelihood of two models:

```python
# Bayes factors are hard to compute reliably
# Use only for simple nested models
# For most practical work, LOO-CV is preferred

# If you must: use bridge sampling or harmonic mean estimator
# But be aware these are numerically unstable for complex models
```

Bayes factors are sensitive to prior choices (even vague priors matter). LOO-CV is more robust for applied work.

## What You Learned

- **Posterior predictive checks** — verify the model generates realistic data before comparing
- **WAIC** — information criterion that penalizes complexity automatically
- **LOO-CV** — leave-one-out cross-validation via importance sampling (preferred)
- **Model stacking** — combine models weighted by predictive performance
- **Pareto k diagnostics** — detect observations that are too influential
- **Bayes factors** — theoretically elegant but practically fragile

Dr. Okafor: "So which model do we use?"

You: "The quadratic model is slightly better at prediction, but the difference isn't huge. I'd use stacking — 78% quadratic, 22% linear. That way we get the benefit of the nonlinearity without fully committing to it."

Next: the posterior predictive checks revealed something odd — the LOS distribution is bimodal. Some patients stay 3 days, others stay 12 days, with few in between. A single model can't capture this. You need mixture models.

---

[← Chapter 9: Missing Data](chapter-09-missing-data.md) | [Chapter 11: Mixture Models →](chapter-11-mixtures.md)
