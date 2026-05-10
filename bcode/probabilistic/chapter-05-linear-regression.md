# Chapter 5: Regression with Doubt — Bayesian Linear Regression

[← Chapter 4: NUTS](chapter-04-nuts.md) | [Chapter 6: Hierarchical Models →](chapter-06-hierarchical.md)

---

## The Problem

MedPulse's current model predicts length of stay (LOS) from patient age and severity score. The OLS regression gives:

```
LOS = 2.1 + 0.05 × age + 1.8 × severity
```

A 70-year-old with severity 3: predicted LOS = 2.1 + 3.5 + 5.4 = **11.0 days**.

But how confident is that prediction? OLS gives a single number. No uncertainty band. No "this patient is unusual and we're less sure." A patient with severity 8 (rare in training data) gets the same confidence as severity 3 (common).

Dr. Okafor: "Your model says 11 days. Is that 11 ± 1 or 11 ± 5? It matters for discharge planning."

## Bayesian Linear Regression

Same model structure as OLS, but every parameter has a distribution:

```python
import pymc as pm
import arviz as az
import numpy as np
import matplotlib.pyplot as plt

# Simulated hospital data
np.random.seed(42)
n = 150
age = np.random.normal(65, 12, n)
severity = np.random.uniform(1, 6, n)

# True relationship (with noise)
true_intercept = 2.0
true_beta_age = 0.05
true_beta_severity = 1.8
true_sigma = 2.5

los = (true_intercept + true_beta_age * age + true_beta_severity * severity +
       np.random.normal(0, true_sigma, n))
los = np.maximum(los, 0.5)  # LOS can't be negative

# Standardize predictors
age_mean, age_std = age.mean(), age.std()
sev_mean, sev_std = severity.mean(), severity.std()
age_z = (age - age_mean) / age_std
sev_z = (severity - sev_mean) / sev_std
```

### The Model

```python
with pm.Model() as los_model:
    # Priors
    intercept = pm.Normal("intercept", mu=10, sigma=5)
    beta_age = pm.Normal("beta_age", mu=0, sigma=2)
    beta_severity = pm.Normal("beta_severity", mu=0, sigma=2)
    sigma = pm.HalfNormal("sigma", sigma=3)  # Noise must be positive

    # Linear predictor
    mu = intercept + beta_age * age_z + beta_severity * sev_z

    # Likelihood
    y = pm.Normal("y", mu=mu, sigma=sigma, observed=los)

    # Sample
    trace = pm.sample(2000, tune=1000, cores=2, random_seed=42)

print(az.summary(trace, hdi_prob=0.90))
```

## Posterior Predictive Bands

The key advantage: uncertainty on predictions.

```python
with los_model:
    # Predict for new patients
    pm.set_data({"age_z": age_z, "sev_z": sev_z})  # Use observed data
    ppc = pm.sample_posterior_predictive(trace, random_seed=42)

# Plot: predictions with uncertainty
fig, ax = plt.subplots(figsize=(10, 6))

# Sort by severity for clean plotting
sort_idx = np.argsort(severity)
sev_sorted = severity[sort_idx]
los_sorted = los[sort_idx]

# Posterior predictive samples
ppc_samples = ppc.posterior_predictive["y"].values.reshape(-1, n)[:, sort_idx]

# Mean prediction
pred_mean = ppc_samples.mean(axis=0)

# 90% prediction interval
pred_low = np.percentile(ppc_samples, 5, axis=0)
pred_high = np.percentile(ppc_samples, 95, axis=0)

ax.scatter(sev_sorted, los_sorted, alpha=0.4, s=20, label="Observed")
ax.plot(sev_sorted, pred_mean, color="red", label="Mean prediction")
ax.fill_between(sev_sorted, pred_low, pred_high, alpha=0.2, color="red",
                label="90% prediction interval")
ax.set_xlabel("Severity Score")
ax.set_ylabel("Length of Stay (days)")
ax.legend()
ax.set_title("Bayesian Regression: Predictions with Uncertainty")
plt.show()
```

The prediction band is wider where data is sparse (high severity) and narrower where data is dense. This is exactly what Dr. Okafor needs — the model communicates its own uncertainty.

## Uncertainty Decomposition

Two sources of uncertainty in predictions:

1. **Epistemic** (parameter uncertainty): We don't know the exact slope/intercept
2. **Aleatoric** (noise): Even with perfect parameters, patients vary

```python
# Epistemic only (uncertainty in the mean prediction)
with los_model:
    # Sample mu (without noise)
    mu_samples = (trace.posterior["intercept"].values.flatten()[:, None] +
                  trace.posterior["beta_age"].values.flatten()[:, None] * age_z[None, :] +
                  trace.posterior["beta_severity"].values.flatten()[:, None] * sev_z[None, :])

mu_mean = mu_samples.mean(axis=0)
mu_low = np.percentile(mu_samples, 5, axis=0)
mu_high = np.percentile(mu_samples, 95, axis=0)

# Epistemic band is MUCH narrower than full prediction band
# Full band = epistemic + aleatoric
```

For discharge planning:
- **Epistemic uncertainty** → "We need more data from patients like this"
- **Aleatoric uncertainty** → "Patients inherently vary, even similar ones"

## Individual Patient Predictions

```python
def predict_patient(trace, age_val, severity_val):
    """Predict LOS for a single patient with full uncertainty."""
    age_z_val = (age_val - age_mean) / age_std
    sev_z_val = (severity_val - sev_mean) / sev_std

    intercepts = trace.posterior["intercept"].values.flatten()
    betas_age = trace.posterior["beta_age"].values.flatten()
    betas_sev = trace.posterior["beta_severity"].values.flatten()
    sigmas = trace.posterior["sigma"].values.flatten()

    # Mean prediction (epistemic uncertainty only)
    mu_pred = intercepts + betas_age * age_z_val + betas_sev * sev_z_val

    # Full prediction (epistemic + aleatoric)
    y_pred = np.random.normal(mu_pred, sigmas)

    return {
        "mean": mu_pred.mean(),
        "epistemic_90": (np.percentile(mu_pred, 5), np.percentile(mu_pred, 95)),
        "full_90": (np.percentile(y_pred, 5), np.percentile(y_pred, 95)),
    }

# Patient A: typical (age 65, severity 3)
pred_A = predict_patient(trace, 65, 3)
print(f"Patient A (typical): {pred_A['mean']:.1f} days")
print(f"  Epistemic 90% CI: [{pred_A['epistemic_90'][0]:.1f}, {pred_A['epistemic_90'][1]:.1f}]")
print(f"  Full 90% PI:      [{pred_A['full_90'][0]:.1f}, {pred_A['full_90'][1]:.1f}]")

# Patient B: unusual (age 90, severity 7)
pred_B = predict_patient(trace, 90, 7)
print(f"\nPatient B (unusual): {pred_B['mean']:.1f} days")
print(f"  Epistemic 90% CI: [{pred_B['epistemic_90'][0]:.1f}, {pred_B['epistemic_90'][1]:.1f}]")
print(f"  Full 90% PI:      [{pred_B['full_90'][0]:.1f}, {pred_B['full_90'][1]:.1f}]")
```

```
Patient A (typical): 10.8 days
  Epistemic 90% CI: [10.2, 11.4]
  Full 90% PI:      [6.7, 14.9]

Patient B (unusual): 17.2 days
  Epistemic 90% CI: [15.1, 19.3]
  Full 90% PI:      [12.8, 21.6]
```

Patient B has wider epistemic uncertainty — the model has seen fewer patients like this. The full prediction interval is always wide (patients vary), but the epistemic component tells you where the model is less sure about the *average*.

## Prior Predictive Checks

Before fitting, check if your priors produce reasonable predictions:

```python
with pm.Model() as prior_check:
    intercept = pm.Normal("intercept", mu=10, sigma=5)
    beta_age = pm.Normal("beta_age", mu=0, sigma=2)
    beta_severity = pm.Normal("beta_severity", mu=0, sigma=2)
    sigma = pm.HalfNormal("sigma", sigma=3)

    mu = intercept + beta_age * age_z + beta_severity * sev_z
    y = pm.Normal("y", mu=mu, sigma=sigma, observed=los)

    prior_pred = pm.sample_prior_predictive(500, random_seed=42)

# Do prior predictions look reasonable?
prior_y = prior_pred.prior_predictive["y"].values.flatten()
print(f"Prior predictive range: [{prior_y.min():.0f}, {prior_y.max():.0f}]")
print(f"Prior predictive mean: {prior_y.mean():.1f}")
```

If prior predictions include LOS of -50 or 500, your priors are too vague. Tighten them.

## What You Learned

- **Bayesian linear regression** — same as OLS but with distributions on parameters
- **Posterior predictive bands** — uncertainty that widens where data is sparse
- **Epistemic vs. aleatoric** — parameter uncertainty vs. inherent noise
- **Individual predictions** — full distribution per patient, not just a point
- **Prior predictive checks** — verify priors produce sensible predictions before fitting

OLS says "11 days." Bayesian regression says "probably 7-15 days, and we're less sure about unusual patients." That's the difference between a number and an honest answer.

But there's a problem: MedPulse has 20 hospitals. Each hospital has different patient populations. Fitting one model to all hospitals ignores differences. Fitting separate models per hospital doesn't work — some hospitals have only 30 patients.

You need a model that shares information across hospitals while respecting their differences. That's hierarchical modeling.

---

[← Chapter 4: NUTS](chapter-04-nuts.md) | [Chapter 6: Hierarchical Models →](chapter-06-hierarchical.md)
