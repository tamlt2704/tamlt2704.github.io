# Chapter 7: Counts and Rates — Generalized Linear Models

[← Chapter 6: Hierarchical Models](chapter-06-hierarchical.md) | [Chapter 8: Time Series →](chapter-08-time-series.md)

---

## The Problem

MedPulse wants to predict how many ER visits a patient will have in the next 90 days. The current approach: linear regression.

```
ER_visits = 0.8 + 0.3 × comorbidities + 0.1 × age_over_65
```

Problem: this predicts 2.3 visits for a typical patient. But it also predicts -0.4 visits for a healthy 30-year-old. Negative visits don't exist. And the residuals aren't Gaussian — most patients have 0 or 1 visits, a few have 8+. The distribution is discrete, non-negative, and right-skewed.

Dr. Okafor: "Your model says some patients will have negative ER visits. That's not inspiring confidence."

You can't fix this by clipping predictions to zero. The problem is structural — you're using the wrong likelihood.

## Link Functions: The Core Idea

A Generalized Linear Model (GLM) has three parts:

1. **Linear predictor**: η = β₀ + β₁x₁ + β₂x₂ (same as before)
2. **Link function**: connects the linear predictor to the parameter of interest
3. **Likelihood**: the distribution that matches your data

For counts, use Poisson likelihood with a **log link**:

```
log(λ) = β₀ + β₁x₁ + β₂x₂
λ = exp(β₀ + β₁x₁ + β₂x₂)
```

The exponential ensures λ is always positive. No more negative predictions.

## Poisson Regression in PyMC

```python
import pymc as pm
import arviz as az
import numpy as np

# Simulated patient data
np.random.seed(42)
n = 300
comorbidities = np.random.poisson(2, n)  # 0-8 comorbidities
age_over_65 = np.random.binomial(1, 0.4, n)
prior_visits = np.random.poisson(1, n)

# True relationship (log-linear)
log_lambda = 0.2 + 0.3 * comorbidities + 0.4 * age_over_65 + 0.2 * prior_visits
true_lambda = np.exp(log_lambda)
er_visits = np.random.poisson(true_lambda)

print(f"ER visits range: {er_visits.min()} to {er_visits.max()}")
print(f"Mean: {er_visits.mean():.1f}, Variance: {er_visits.var():.1f}")
```

```python
with pm.Model() as poisson_model:
    # Priors on coefficients
    beta_0 = pm.Normal("beta_0", mu=0, sigma=1)
    beta_comorbid = pm.Normal("beta_comorbid", mu=0, sigma=0.5)
    beta_age = pm.Normal("beta_age", mu=0, sigma=0.5)
    beta_prior = pm.Normal("beta_prior", mu=0, sigma=0.5)

    # Log-linear model
    log_mu = (beta_0 + beta_comorbid * comorbidities +
              beta_age * age_over_65 + beta_prior * prior_visits)

    # Poisson likelihood (log link is built in)
    visits = pm.Poisson("visits", mu=pm.math.exp(log_mu), observed=er_visits)

    trace = pm.sample(2000, tune=1000, cores=2, random_seed=42)

print(az.summary(trace, hdi_prob=0.90))
```

## Interpreting Coefficients

In Poisson regression, coefficients are on the log scale. A coefficient of 0.3 means:

```python
# Each additional comorbidity multiplies expected visits by:
rate_ratio = np.exp(0.3)
print(f"Rate ratio per comorbidity: {rate_ratio:.2f}")
# → 1.35: each comorbidity increases expected visits by 35%
```

This is multiplicative, not additive. A patient with 4 comorbidities vs. 2:
- Expected ratio: exp(0.3 × 2) = 1.82 — nearly double the visits.

## The Overdispersion Problem

Poisson assumes mean = variance. Real patient data rarely cooperates:

```python
print(f"Sample mean: {er_visits.mean():.2f}")
print(f"Sample variance: {er_visits.var():.2f}")
print(f"Ratio (should be ~1 for Poisson): {er_visits.var() / er_visits.mean():.2f}")
```

If variance >> mean, you have **overdispersion**. Causes: unobserved heterogeneity (patients differ in ways you haven't measured), clustering, or zero-inflation.

Ignoring overdispersion → confidence intervals too narrow → false discoveries.

## Negative Binomial: Handling Overdispersion

The Negative Binomial adds a dispersion parameter that lets variance exceed the mean:

```python
with pm.Model() as negbin_model:
    # Priors
    beta_0 = pm.Normal("beta_0", mu=0, sigma=1)
    beta_comorbid = pm.Normal("beta_comorbid", mu=0, sigma=0.5)
    beta_age = pm.Normal("beta_age", mu=0, sigma=0.5)
    beta_prior = pm.Normal("beta_prior", mu=0, sigma=0.5)

    # Dispersion parameter (smaller = more overdispersion)
    alpha = pm.HalfNormal("alpha", sigma=5)

    # Log-linear model
    mu = pm.math.exp(beta_0 + beta_comorbid * comorbidities +
                     beta_age * age_over_65 + beta_prior * prior_visits)

    # Negative Binomial likelihood
    visits = pm.NegativeBinomial("visits", mu=mu, alpha=alpha, observed=er_visits)

    trace_nb = pm.sample(2000, tune=1000, cores=2, random_seed=42)

# Compare models
print(az.summary(trace_nb, var_names=["alpha"], hdi_prob=0.90))
```

If the posterior for `alpha` is large (say > 20), the data is approximately Poisson. If it's small (< 5), overdispersion is substantial.

## Logistic Regression: Binary Outcomes

Not all outcomes are counts. "Was the patient readmitted? Yes/No" is binary.

```python
# Binary outcome: readmitted within 30 days
np.random.seed(42)
n = 400
los = np.random.exponential(5, n)  # Length of stay
age = np.random.normal(68, 12, n)
has_followup = np.random.binomial(1, 0.6, n)

# True logistic model
logit_p = -2.0 + 0.03 * age + 0.1 * los - 0.8 * has_followup
prob_readmit = 1 / (1 + np.exp(-logit_p))
readmitted = np.random.binomial(1, prob_readmit)

print(f"Readmission rate: {readmitted.mean():.1%}")

with pm.Model() as logistic_model:
    # Priors
    b0 = pm.Normal("b0", mu=0, sigma=2)
    b_age = pm.Normal("b_age", mu=0, sigma=0.1)
    b_los = pm.Normal("b_los", mu=0, sigma=0.5)
    b_followup = pm.Normal("b_followup", mu=0, sigma=1)

    # Logit link
    logit_p = b0 + b_age * age + b_los * los + b_followup * has_followup

    # Bernoulli likelihood
    y = pm.Bernoulli("y", logit_p=logit_p, observed=readmitted)

    trace_logistic = pm.sample(2000, tune=1000, cores=2, random_seed=42)

# Odds ratios
b_followup_samples = trace_logistic.posterior["b_followup"].values.flatten()
or_followup = np.exp(b_followup_samples)
print(f"Follow-up OR: {or_followup.mean():.2f} [{np.percentile(or_followup, 5):.2f}, "
      f"{np.percentile(or_followup, 95):.2f}]")
```

A follow-up appointment odds ratio of 0.45 means: patients with follow-up have 55% lower odds of readmission.

## Choosing the Right GLM

| Data Type | Distribution | Link | Example |
|---|---|---|---|
| Continuous, positive | Normal | Identity | Length of stay |
| Counts | Poisson | Log | ER visits |
| Counts (overdispersed) | Negative Binomial | Log | ER visits (real data) |
| Binary (0/1) | Bernoulli | Logit | Readmitted yes/no |
| Proportions | Beta | Logit | Bed occupancy rate |

## What You Learned

- **GLMs** — extend regression to non-Gaussian outcomes via link functions
- **Poisson regression** — for count data, log link ensures positive predictions
- **Rate ratios** — exponentiated coefficients give multiplicative effects
- **Overdispersion** — when variance > mean, Poisson is too restrictive
- **Negative Binomial** — adds dispersion parameter to handle overdispersion
- **Logistic regression** — for binary outcomes, logit link maps to probabilities

Dr. Okafor: "So the model now predicts 3.2 visits for this patient — and that's always a positive number?"

You: "Exactly. And the Negative Binomial accounts for the fact that some patients are frequent flyers for reasons we haven't measured. The uncertainty intervals are honest."

Next: MedPulse's readmission rate isn't static. It changes over time. You need models that respect temporal structure.

---

[← Chapter 6: Hierarchical Models](chapter-06-hierarchical.md) | [Chapter 8: Time Series →](chapter-08-time-series.md)
