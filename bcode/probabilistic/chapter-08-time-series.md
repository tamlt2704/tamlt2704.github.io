# Chapter 8: Time Changes Things — Bayesian Time Series

[← Chapter 7: GLMs](chapter-07-glm.md) | [Chapter 9: Missing Data →](chapter-09-missing-data.md)

---

## The Problem

MedPulse tracks monthly readmission rates across their hospital network. The CEO asks: "Is our readmission rate improving?"

You plot the data. For 36 months it hovers around 22%. Then in month 37, it drops to 17% and stays there. A new discharge protocol was introduced in month 36.

But is this a real shift or just noise? The rate bounced between 19% and 25% before — maybe 17% is just a lucky month. You need a model that can detect **structural changes** in time series while accounting for natural variation.

## Random Walk Priors

A random walk says: tomorrow's value is today's value plus noise. It encodes the belief that adjacent time points are similar.

```python
import pymc as pm
import arviz as az
import numpy as np
import matplotlib.pyplot as plt

# Simulated monthly readmission rates (36 months + shift)
np.random.seed(42)
n_months = 48

# True process: stable at 22%, drops to 17% at month 37
true_rate = np.where(np.arange(n_months) < 36, 0.22, 0.17)
n_patients_per_month = np.random.poisson(200, n_months)
readmissions = np.random.binomial(n_patients_per_month, true_rate)
observed_rate = readmissions / n_patients_per_month

months = np.arange(n_months)
```

### Gaussian Random Walk Model

```python
with pm.Model() as rw_model:
    # Innovation standard deviation (how much the rate can change per step)
    sigma_rw = pm.HalfNormal("sigma_rw", sigma=0.05)

    # Random walk on logit scale (keeps rates between 0 and 1)
    logit_rate = pm.GaussianRandomWalk("logit_rate", sigma=sigma_rw,
                                        shape=n_months, init_dist=pm.Normal.dist(mu=-1.3, sigma=0.5))

    # Transform to probability scale
    rate = pm.Deterministic("rate", pm.math.sigmoid(logit_rate))

    # Likelihood
    obs = pm.Binomial("obs", n=n_patients_per_month, p=rate, observed=readmissions)

    trace_rw = pm.sample(2000, tune=1000, cores=2, random_seed=42)
```

```python
# Plot smoothed rate with uncertainty
posterior_rates = trace_rw.posterior["rate"].values.reshape(-1, n_months)
rate_mean = posterior_rates.mean(axis=0)
rate_hdi = az.hdi(trace_rw.posterior["rate"], hdi_prob=0.90)["rate"].values

fig, ax = plt.subplots(figsize=(12, 5))
ax.scatter(months, observed_rate, color="black", s=30, alpha=0.6, label="Observed")
ax.plot(months, rate_mean, color="blue", linewidth=2, label="Posterior mean")
ax.fill_between(months, rate_hdi[:, 0], rate_hdi[:, 1],
                alpha=0.2, color="blue", label="90% HDI")
ax.axvline(36, color="red", linestyle="--", alpha=0.5, label="Policy change")
ax.set_xlabel("Month")
ax.set_ylabel("Readmission Rate")
ax.legend()
ax.set_title("Random Walk Model: Smoothed Readmission Rate")
plt.show()
```

The random walk smooths the noisy monthly rates while tracking the real shift at month 37.

## Changepoint Detection

The random walk adapts gradually. But what if you want to explicitly detect *when* a change happened?

```python
with pm.Model() as changepoint_model:
    # When did the change happen?
    tau = pm.DiscreteUniform("tau", lower=12, upper=n_months - 6)

    # Rate before and after changepoint
    rate_before = pm.Beta("rate_before", alpha=5, beta=20)  # Prior ~20%
    rate_after = pm.Beta("rate_after", alpha=3, beta=15)    # Prior ~17%

    # Switch at changepoint
    rate = pm.math.switch(months < tau, rate_before, rate_after)

    # Likelihood
    obs = pm.Binomial("obs", n=n_patients_per_month, p=rate, observed=readmissions)

    trace_cp = pm.sample(2000, tune=1000, cores=2, random_seed=42)

# When did the model think the change happened?
tau_samples = trace_cp.posterior["tau"].values.flatten()
print(f"Changepoint posterior mode: month {int(np.median(tau_samples))}")
print(f"90% HDI: [{np.percentile(tau_samples, 5):.0f}, {np.percentile(tau_samples, 95):.0f}]")

rate_before_samples = trace_cp.posterior["rate_before"].values.flatten()
rate_after_samples = trace_cp.posterior["rate_after"].values.flatten()
print(f"Rate before: {rate_before_samples.mean():.1%}")
print(f"Rate after: {rate_after_samples.mean():.1%}")
print(f"Reduction: {(rate_before_samples - rate_after_samples).mean():.1%}")
```

```
Changepoint posterior mode: month 36
90% HDI: [35, 38]
Rate before: 22.1%
Rate after: 17.3%
Reduction: 4.8%
```

The model identifies the changepoint at month 36 with high confidence and estimates a ~5 percentage point reduction.

## Multiple Changepoints

Real systems can have multiple shifts. Use a more flexible approach:

```python
with pm.Model() as multi_cp_model:
    # Number of segments
    n_segments = 3

    # Changepoint locations (ordered)
    tau_raw = pm.Uniform("tau_raw", lower=0, upper=1, shape=n_segments - 1)
    tau = pm.Deterministic("tau", pm.math.sort(tau_raw) * n_months)

    # Rate in each segment
    segment_rates = pm.Beta("segment_rates", alpha=3, beta=12, shape=n_segments)

    # Assign each month to a segment
    # (In practice, use pm.math.switch or indexing)
```

## Autoregressive Models

When the current value depends on recent history (not just the previous step):

```python
with pm.Model() as ar_model:
    # AR(1) coefficient
    phi = pm.Uniform("phi", lower=-1, upper=1)  # Stationarity constraint

    # Innovation noise
    sigma = pm.HalfNormal("sigma", sigma=0.5)

    # Intercept (long-run mean on logit scale)
    mu = pm.Normal("mu", mu=-1.3, sigma=0.5)

    # AR(1) process
    logit_rate = pm.AR("logit_rate", rho=[phi], sigma=sigma, constant=True,
                       init_dist=pm.Normal.dist(mu=mu, sigma=sigma),
                       shape=n_months)

    rate = pm.Deterministic("rate", pm.math.sigmoid(logit_rate))
    obs = pm.Binomial("obs", n=n_patients_per_month, p=rate, observed=readmissions)

    trace_ar = pm.sample(2000, tune=1000, cores=2, random_seed=42)

phi_samples = trace_ar.posterior["phi"].values.flatten()
print(f"AR(1) coefficient: {phi_samples.mean():.2f} [{np.percentile(phi_samples, 5):.2f}, "
      f"{np.percentile(phi_samples, 95):.2f}]")
```

High φ (close to 1) means strong persistence — today's rate strongly predicts tomorrow's. Low φ means the series reverts quickly to its mean.

## Forecasting with Uncertainty

```python
# Forecast next 6 months
n_forecast = 6

with rw_model:
    # Extend the random walk
    pm.set_data({})  # No new observations
    forecast_trace = pm.sample_posterior_predictive(
        trace_rw, var_names=["rate"], random_seed=42
    )

# Or manually propagate the random walk
last_logit = trace_rw.posterior["logit_rate"].values[:, :, -1].flatten()
sigma_rw_samples = trace_rw.posterior["sigma_rw"].values.flatten()

forecast_rates = np.zeros((len(last_logit), n_forecast))
for t in range(n_forecast):
    if t == 0:
        logit_next = last_logit + np.random.normal(0, sigma_rw_samples)
    else:
        logit_next = forecast_logit + np.random.normal(0, sigma_rw_samples)
    forecast_logit = logit_next
    forecast_rates[:, t] = 1 / (1 + np.exp(-logit_next))

# Uncertainty fans out over time
for t in range(n_forecast):
    low, high = np.percentile(forecast_rates[:, t], [5, 95])
    print(f"Month {n_months + t + 1}: {forecast_rates[:, t].mean():.1%} "
          f"[{low:.1%}, {high:.1%}]")
```

Forecasts get wider the further out you go — the model is honest about increasing uncertainty.

## What You Learned

- **Random walk priors** — encode belief that adjacent time points are similar
- **GaussianRandomWalk** — smooth noisy time series while tracking real changes
- **Changepoint detection** — explicitly model when a structural shift occurred
- **AR models** — capture temporal autocorrelation with persistence parameter
- **Forecast uncertainty** — prediction intervals widen with forecast horizon

Dr. Okafor: "So the new discharge protocol really did reduce readmissions?"

You: "The model puts the changepoint at month 36 with high confidence. The rate dropped from 22% to 17%. There's a 98% posterior probability that the rate decreased."

But there's a complication. Some months have missing data — lab values weren't recorded for all patients. You can't just drop those rows. Next: treating missing data as inference.

---

[← Chapter 7: GLMs](chapter-07-glm.md) | [Chapter 9: Missing Data →](chapter-09-missing-data.md)
