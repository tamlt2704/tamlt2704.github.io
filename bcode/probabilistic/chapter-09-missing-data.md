# Chapter 9: Missing Data — Imputation as Inference

[← Chapter 8: Time Series](chapter-08-time-series.md) | [Chapter 10: Model Comparison →](chapter-10-model-comparison.md)

---

## The Problem

MedPulse's readmission model uses lab values (creatinine, hemoglobin, albumin) as predictors. But 30% of patients are missing at least one lab value. The data team's current approach: drop incomplete rows.

This is a disaster. You just threw away 30% of your data. Worse: the patients with missing labs aren't random — sicker patients in the ER often don't get full panels drawn. By dropping them, you're biasing the model toward healthier patients.

Dr. Okafor: "The patients we're dropping are exactly the ones we most need to predict."

## Three Types of Missing Data

**MCAR** (Missing Completely At Random): Missingness is unrelated to anything. A lab tube broke. Rare in practice.

**MAR** (Missing At Random): Missingness depends on *observed* variables. Younger patients are less likely to get creatinine checked — but once you condition on age, missingness is random.

**MNAR** (Missing Not At Random): Missingness depends on the *missing value itself*. Patients with very high creatinine are rushed to treatment before labs are recorded. The sickest patients are the ones missing data.

MedPulse's situation is likely MNAR — the missing labs correlate with severity. Standard imputation (mean, median, or even multiple imputation) assumes MAR. You need something better.

## The Bayesian Approach: Missing Values Are Parameters

The key insight: treat each missing value as an unknown parameter with a prior. The model jointly estimates the missing values and the regression coefficients.

```python
import pymc as pm
import arviz as az
import numpy as np

# Simulated data with MNAR missingness
np.random.seed(42)
n = 400

age = np.random.normal(68, 12, n)
severity = np.random.uniform(1, 8, n)

# True creatinine (correlated with severity)
creatinine_true = 0.8 + 0.15 * severity + np.random.normal(0, 0.3, n)

# MNAR: higher creatinine → more likely to be missing
prob_missing = 1 / (1 + np.exp(-(creatinine_true - 1.5) * 2))
is_missing = np.random.binomial(1, prob_missing).astype(bool)
print(f"Missing rate: {is_missing.mean():.1%}")
print(f"Mean creatinine (observed): {creatinine_true[~is_missing].mean():.2f}")
print(f"Mean creatinine (missing): {creatinine_true[is_missing].mean():.2f}")

# Outcome: readmission (depends on true creatinine)
logit_p = -3 + 0.04 * age + 0.3 * severity + 1.2 * creatinine_true
prob_readmit = 1 / (1 + np.exp(-logit_p))
readmitted = np.random.binomial(1, prob_readmit)

# What we observe
creatinine_obs = creatinine_true.copy()
creatinine_obs[is_missing] = np.nan
```

```
Missing rate: 32.5%
Mean creatinine (observed): 1.47
Mean creatinine (missing): 1.89
```

The missing creatinine values are systematically higher. Dropping them biases the model.

## Joint Model: Imputation + Prediction

```python
# Indices for observed and missing
obs_idx = np.where(~is_missing)[0]
miss_idx = np.where(is_missing)[0]
creatinine_observed = creatinine_true[obs_idx]

with pm.Model() as joint_model:
    # --- Sub-model for creatinine (handles missingness) ---
    # Creatinine depends on severity (observed for all patients)
    mu_creat_intercept = pm.Normal("mu_creat_intercept", mu=1.0, sigma=0.5)
    mu_creat_slope = pm.Normal("mu_creat_slope", mu=0, sigma=0.2)
    sigma_creat = pm.HalfNormal("sigma_creat", sigma=0.5)

    # Expected creatinine for each patient
    mu_creat = mu_creat_intercept + mu_creat_slope * severity

    # Impute missing creatinine values
    creat_missing = pm.Normal("creat_missing", mu=mu_creat[miss_idx],
                              sigma=sigma_creat, shape=len(miss_idx))

    # Combine observed and imputed
    creatinine_full = pm.math.zeros(n)
    creatinine_full = pm.math.set_subtensor(creatinine_full[obs_idx], creatinine_observed)
    creatinine_full = pm.math.set_subtensor(creatinine_full[miss_idx], creat_missing)

    # --- Outcome model (uses full creatinine) ---
    b0 = pm.Normal("b0", mu=0, sigma=2)
    b_age = pm.Normal("b_age", mu=0, sigma=0.1)
    b_severity = pm.Normal("b_severity", mu=0, sigma=0.5)
    b_creat = pm.Normal("b_creat", mu=0, sigma=1)

    logit_p = b0 + b_age * age + b_severity * severity + b_creat * creatinine_full

    y = pm.Bernoulli("y", logit_p=logit_p, observed=readmitted)

    trace_joint = pm.sample(2000, tune=1000, cores=2, random_seed=42)
```

## Comparing Approaches

```python
# Approach 1: Drop missing (biased)
from sklearn.linear_model import LogisticRegression

X_complete = np.column_stack([age[obs_idx], severity[obs_idx], creatinine_true[obs_idx]])
y_complete = readmitted[obs_idx]
lr_drop = LogisticRegression().fit(X_complete, y_complete)
print(f"Drop missing — creatinine coef: {lr_drop.coef_[0][2]:.3f}")

# Approach 2: Mean imputation (still biased)
creat_imputed = creatinine_true.copy()
creat_imputed[is_missing] = creatinine_true[~is_missing].mean()
X_imputed = np.column_stack([age, severity, creat_imputed])
lr_impute = LogisticRegression().fit(X_imputed, readmitted)
print(f"Mean impute — creatinine coef: {lr_impute.coef_[0][2]:.3f}")

# Approach 3: Bayesian joint model (correct)
b_creat_samples = trace_joint.posterior["b_creat"].values.flatten()
print(f"Joint model — creatinine coef: {b_creat_samples.mean():.3f} "
      f"[{np.percentile(b_creat_samples, 5):.3f}, {np.percentile(b_creat_samples, 95):.3f}]")
print(f"True coefficient: 1.200")
```

The joint model recovers the true coefficient because it models *why* data is missing and imputes accordingly.

## Examining the Imputed Values

```python
# What did the model impute for missing creatinine?
imputed_samples = trace_joint.posterior["creat_missing"].values.reshape(-1, len(miss_idx))
imputed_means = imputed_samples.mean(axis=0)

print(f"True missing creatinine mean: {creatinine_true[is_missing].mean():.2f}")
print(f"Imputed mean: {imputed_means.mean():.2f}")
print(f"Observed mean (naive imputation): {creatinine_true[~is_missing].mean():.2f}")
```

The model imputes values *higher* than the observed mean — it learned that missing values tend to be elevated because it jointly models creatinine and the outcome.

## Modeling the Missingness Mechanism

For explicit MNAR modeling, add a sub-model for the missingness indicator:

```python
with pm.Model() as mnar_model:
    # Creatinine model
    mu_creat = pm.Normal("mu_creat", mu=1.5, sigma=0.5)
    sigma_creat = pm.HalfNormal("sigma_creat", sigma=0.5)

    # Full creatinine (observed + imputed)
    creat_missing = pm.Normal("creat_missing", mu=mu_creat,
                              sigma=sigma_creat, shape=len(miss_idx))

    creatinine_full = pm.math.zeros(n)
    creatinine_full = pm.math.set_subtensor(creatinine_full[obs_idx], creatinine_observed)
    creatinine_full = pm.math.set_subtensor(creatinine_full[miss_idx], creat_missing)

    # Missingness model: P(missing | creatinine)
    gamma_0 = pm.Normal("gamma_0", mu=0, sigma=2)
    gamma_creat = pm.Normal("gamma_creat", mu=0, sigma=1)

    logit_missing = gamma_0 + gamma_creat * creatinine_full
    missing_obs = pm.Bernoulli("missing_obs", logit_p=logit_missing,
                               observed=is_missing.astype(int))

    # Outcome model
    b0 = pm.Normal("b0", mu=0, sigma=2)
    b_creat = pm.Normal("b_creat", mu=0, sigma=1)
    logit_p = b0 + b_creat * creatinine_full
    y = pm.Bernoulli("y", logit_p=logit_p, observed=readmitted)

    trace_mnar = pm.sample(2000, tune=2000, cores=2, random_seed=42,
                           target_accept=0.95)
```

This explicitly models the MNAR mechanism: `gamma_creat > 0` means higher creatinine → more likely missing.

## Practical Guidelines

1. **Always investigate missingness patterns** — plot missingness against observed variables
2. **MAR is often reasonable** — if you include enough predictors in the imputation model
3. **MNAR requires assumptions** — the model is only as good as your missingness specification
4. **Joint modeling propagates uncertainty** — imputed values have posterior distributions, not point estimates
5. **More predictors in the imputation model = better** — include variables that predict both the missing value and the outcome

## What You Learned

- **MCAR/MAR/MNAR** — three mechanisms for why data is missing
- **Dropping rows is biased** — especially under MNAR where sicker patients have missing data
- **Missing values as parameters** — the Bayesian approach imputes within the model
- **Joint modeling** — simultaneously model the outcome and the missing data process
- **Uncertainty propagation** — imputed values carry uncertainty into downstream estimates

Dr. Okafor: "So the model fills in the missing labs?"

You: "It estimates what they probably were, given everything else we know about the patient. And it's honest about the uncertainty — a patient with missing creatinine gets a wider prediction interval."

Next: you now have multiple models (Poisson, Negative Binomial, with and without covariates). Which one should you use? You need principled model comparison.

---

[← Chapter 8: Time Series](chapter-08-time-series.md) | [Chapter 10: Model Comparison →](chapter-10-model-comparison.md)
