# Chapter 12: Survival Analysis — When Will They Return?

[← Chapter 11: Mixture Models](chapter-11-mixtures.md) | [Chapter 13: Causal Inference →](chapter-13-causal.md)

---

## The Problem

MedPulse's readmission model predicts *whether* a patient will be readmitted (binary: yes/no). But the clinical team needs more: *when* will they be readmitted?

A patient readmitted in 3 days needs different intervention than one readmitted in 60 days. And there's a fundamental data problem: for patients who haven't been readmitted yet, you don't know their readmission time — you only know it's *at least* as long as the observation period.

Patient A: discharged 90 days ago, readmitted on day 12. Time = 12 days. ✓
Patient B: discharged 45 days ago, not yet readmitted. Time = ??? (at least 45 days).

Patient B is **right-censored**. You can't drop them (biases toward shorter times). You can't set their time to 45 (that's wrong — they might come back on day 200). You need survival analysis.

## Censoring: The Core Challenge

```python
import pymc as pm
import arviz as az
import numpy as np
import matplotlib.pyplot as plt

# Simulated time-to-readmission data
np.random.seed(42)
n = 250

age = np.random.normal(70, 10, n)
severity = np.random.uniform(1, 8, n)
has_followup = np.random.binomial(1, 0.5, n)

# True Weibull survival times
shape = 1.5  # Increasing hazard (risk grows over time)
scale = np.exp(4.5 - 0.02 * age - 0.15 * severity + 0.5 * has_followup)
true_times = np.random.weibull(shape, n) * scale

# Censoring: observation window is 90 days
censor_time = 90
observed_time = np.minimum(true_times, censor_time)
event_observed = (true_times <= censor_time).astype(int)

print(f"Readmitted within 90 days: {event_observed.sum()} ({event_observed.mean():.1%})")
print(f"Censored (still event-free): {(1-event_observed).sum()}")
print(f"Median observed time: {observed_time[event_observed==1].mean():.1f} days")
```

```
Readmitted within 90 days: 142 (56.8%)
Censored (still event-free): 108
Median observed time: 38.2 days
```

## The Weibull Survival Model

The Weibull distribution is flexible: it can model increasing hazard (shape > 1), decreasing hazard (shape < 1), or constant hazard (shape = 1, which is exponential).

```python
# Standardize predictors
age_z = (age - age.mean()) / age.std()
sev_z = (severity - severity.mean()) / severity.std()

with pm.Model() as survival_model:
    # Priors
    beta_0 = pm.Normal("beta_0", mu=4, sigma=1)
    beta_age = pm.Normal("beta_age", mu=0, sigma=0.5)
    beta_sev = pm.Normal("beta_sev", mu=0, sigma=0.5)
    beta_followup = pm.Normal("beta_followup", mu=0, sigma=0.5)

    # Weibull shape parameter
    alpha = pm.HalfNormal("alpha", sigma=2)  # shape

    # Log-linear model for scale
    log_scale = beta_0 + beta_age * age_z + beta_sev * sev_z + beta_followup * has_followup
    scale_param = pm.math.exp(log_scale)

    # For observed events: Weibull log-likelihood
    # For censored: survival function (probability of surviving past censor time)

    # Observed events contribute the density
    event_idx = np.where(event_observed == 1)[0]
    censor_idx = np.where(event_observed == 0)[0]

    # Log-likelihood for observed events: log f(t)
    # Weibull: f(t) = (alpha/lambda) * (t/lambda)^(alpha-1) * exp(-(t/lambda)^alpha)
    t_event = observed_time[event_idx]
    scale_event = scale_param[event_idx]

    log_lik_event = (pm.math.log(alpha) - alpha * pm.math.log(scale_event) +
                     (alpha - 1) * pm.math.log(t_event) -
                     (t_event / scale_event)**alpha)

    # Log-likelihood for censored: log S(t) = -(t/lambda)^alpha
    t_censor = observed_time[censor_idx]
    scale_censor = scale_param[censor_idx]
    log_lik_censor = -(t_censor / scale_censor)**alpha

    # Total log-likelihood
    pm.Potential("log_lik", log_lik_event.sum() + log_lik_censor.sum())

    trace_surv = pm.sample(2000, tune=1000, cores=2, random_seed=42,
                           target_accept=0.9)

print(az.summary(trace_surv, hdi_prob=0.90))
```

## Interpreting the Results

```python
# Effect of follow-up appointment
beta_fu = trace_surv.posterior["beta_followup"].values.flatten()
print(f"Follow-up effect on log-scale: {beta_fu.mean():.2f}")
print(f"Time ratio: {np.exp(beta_fu.mean()):.2f}")
# Time ratio > 1 means longer time to readmission (protective)

# Weibull shape
alpha_samples = trace_surv.posterior["alpha"].values.flatten()
print(f"Shape parameter: {alpha_samples.mean():.2f}")
# > 1: hazard increases over time (risk accumulates)
# < 1: hazard decreases (if you survive early, you're likely fine)
# = 1: constant hazard (exponential/memoryless)
```

A time ratio of 1.65 for follow-up means: patients with follow-up appointments take 65% longer to be readmitted (on average). That's the survival-analysis equivalent of "follow-up is protective."

## Survival Curves for Individual Patients

```python
def predict_survival_curve(trace, age_val, severity_val, followup_val, t_grid):
    """Compute posterior survival curve for a specific patient."""
    age_z_val = (age_val - age.mean()) / age.std()
    sev_z_val = (severity_val - severity.mean()) / severity.std()

    b0 = trace.posterior["beta_0"].values.flatten()
    b_age = trace.posterior["beta_age"].values.flatten()
    b_sev = trace.posterior["beta_sev"].values.flatten()
    b_fu = trace.posterior["beta_followup"].values.flatten()
    alpha_s = trace.posterior["alpha"].values.flatten()

    log_scale = b0 + b_age * age_z_val + b_sev * sev_z_val + b_fu * followup_val
    scale_s = np.exp(log_scale)

    # S(t) = exp(-(t/scale)^alpha) for each posterior sample
    survival = np.exp(-(t_grid[None, :] / scale_s[:, None])**alpha_s[:, None])
    return survival

t_grid = np.linspace(0.1, 120, 100)

# High-risk patient: old, severe, no follow-up
surv_high = predict_survival_curve(trace_surv, 80, 7, 0, t_grid)

# Low-risk patient: younger, mild, with follow-up
surv_low = predict_survival_curve(trace_surv, 60, 2, 1, t_grid)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(t_grid, surv_high.mean(axis=0), color="red", label="High-risk (80yo, severity 7, no follow-up)")
ax.fill_between(t_grid, np.percentile(surv_high, 5, axis=0),
                np.percentile(surv_high, 95, axis=0), alpha=0.2, color="red")
ax.plot(t_grid, surv_low.mean(axis=0), color="blue", label="Low-risk (60yo, severity 2, follow-up)")
ax.fill_between(t_grid, np.percentile(surv_low, 5, axis=0),
                np.percentile(surv_low, 95, axis=0), alpha=0.2, color="blue")
ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5, label="Median survival")
ax.set_xlabel("Days since discharge")
ax.set_ylabel("Probability of NOT being readmitted")
ax.legend()
ax.set_title("Patient-Specific Survival Curves")
plt.show()
```

The high-risk patient has a 50% chance of readmission by day 25. The low-risk patient: by day 80. These curves communicate risk far better than a binary "high risk / low risk" label.

## Hazard Functions

The hazard function h(t) is the instantaneous risk of the event at time t, given survival to t:

```python
# Weibull hazard: h(t) = (alpha / scale) * (t / scale)^(alpha-1)
def weibull_hazard(t, alpha, scale):
    return (alpha / scale) * (t / scale)**(alpha - 1)

# Plot hazard for average patient
b0_mean = trace_surv.posterior["beta_0"].values.flatten().mean()
alpha_mean = alpha_samples.mean()
scale_mean = np.exp(b0_mean)

hazard = weibull_hazard(t_grid, alpha_mean, scale_mean)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(t_grid, hazard, color="darkred", linewidth=2)
ax.set_xlabel("Days since discharge")
ax.set_ylabel("Hazard rate")
ax.set_title(f"Weibull Hazard (shape={alpha_mean:.2f} — increasing risk over time)")
plt.show()
```

Shape > 1 means the hazard increases — the longer a patient has been out, the higher their daily risk of readmission. This might reflect deteriorating health without hospital support.

## Cox Proportional Hazards (Bayesian)

The Cox model doesn't assume a specific baseline hazard shape:

```python
# Bayesian Cox model using piecewise-constant baseline hazard
n_intervals = 6
cutpoints = np.linspace(0, 90, n_intervals + 1)

with pm.Model() as cox_model:
    # Piecewise-constant baseline hazard
    log_baseline = pm.Normal("log_baseline", mu=-3, sigma=1, shape=n_intervals)

    # Covariate effects (log hazard ratios)
    beta_age = pm.Normal("beta_age", mu=0, sigma=0.5)
    beta_sev = pm.Normal("beta_sev", mu=0, sigma=0.5)
    beta_followup = pm.Normal("beta_followup", mu=0, sigma=0.5)

    # Linear predictor
    eta = beta_age * age_z + beta_sev * sev_z + beta_followup * has_followup

    # Hazard ratios
    hr_followup = pm.Deterministic("hr_followup", pm.math.exp(beta_followup))
    # HR < 1 means protective (lower hazard)
```

Hazard ratio interpretation: HR = 0.6 for follow-up means patients with follow-up have 40% lower instantaneous risk of readmission at any time point.

## What You Learned

- **Right censoring** — patients not yet readmitted contribute information (they survived at least this long)
- **Weibull model** — flexible parametric survival with shape and scale
- **Time ratios** — how covariates stretch or compress time to event
- **Survival curves** — patient-specific probability of remaining event-free over time
- **Hazard functions** — instantaneous risk at each time point
- **Cox model** — semi-parametric, doesn't assume a baseline hazard shape

Dr. Okafor: "So for this patient, there's a 70% chance they'll be readmitted within 30 days?"

You: "Exactly. And the follow-up appointment shifts that curve — with follow-up, the 70% mark moves to day 50. That's 20 extra days of event-free time."

But wait — does the follow-up appointment *cause* the improvement? Or are healthier patients more likely to attend follow-up? That's a causal question, and it needs different tools.

---

[← Chapter 11: Mixture Models](chapter-11-mixtures.md) | [Chapter 13: Causal Inference →](chapter-13-causal.md)
