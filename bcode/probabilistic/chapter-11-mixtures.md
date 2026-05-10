# Chapter 11: Mixture Models — Hidden Subgroups

[← Chapter 10: Model Comparison](chapter-10-model-comparison.md) | [Chapter 12: Survival Analysis →](chapter-12-survival.md)

---

## The Problem

MedPulse's posterior predictive check (Chapter 10) revealed something the linear model missed: the length-of-stay distribution is **bimodal**. There's a peak around 3 days and another around 11 days, with a valley in between.

A single Gaussian can't capture this. The model predicts 7 days for everyone — wrong for both groups.

Dr. Okafor has a hypothesis: "Surgical patients stay longer than medical patients. But our data doesn't always have clean labels for admission type."

You need a model that discovers these hidden subgroups from the data itself.

## Gaussian Mixture Model

A mixture model says: each observation comes from one of K components, but we don't know which.

```python
import pymc as pm
import arviz as az
import numpy as np
import matplotlib.pyplot as plt

# Simulated bimodal LOS data
np.random.seed(42)
n = 300

# Two subgroups: medical (short stay) and surgical (long stay)
group = np.random.binomial(1, 0.4, n)  # 40% surgical
los_medical = np.random.normal(3.5, 1.2, n)
los_surgical = np.random.normal(11.0, 2.5, n)
los = np.where(group == 0, los_medical, los_surgical)
los = np.maximum(los, 0.5)  # Floor at 0.5 days

# In practice, we DON'T observe the group labels
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(los, bins=30, density=True, alpha=0.7, color="steelblue")
ax.set_xlabel("Length of Stay (days)")
ax.set_title("Bimodal LOS Distribution — Two Hidden Subgroups?")
plt.show()
```

## Fitting a 2-Component Mixture

```python
with pm.Model() as mixture_model:
    # Mixture weights
    w = pm.Dirichlet("w", a=np.ones(2))  # Uniform prior on proportions

    # Component means (ordered to prevent label switching)
    mu = pm.Normal("mu", mu=[4, 10], sigma=3, shape=2,
                   transform=pm.distributions.transforms.ordered)

    # Component standard deviations
    sigma = pm.HalfNormal("sigma", sigma=3, shape=2)

    # Mixture likelihood
    y = pm.Mixture("y",
                   w=w,
                   comp_dists=[pm.Normal.dist(mu=mu[0], sigma=sigma[0]),
                               pm.Normal.dist(mu=mu[1], sigma=sigma[1])],
                   observed=los)

    trace_mix = pm.sample(2000, tune=2000, cores=2, random_seed=42,
                          target_accept=0.9)

print(az.summary(trace_mix, var_names=["w", "mu", "sigma"], hdi_prob=0.90))
```

```
        mean    sd    hdi_5%  hdi_95%
w[0]    0.61   0.03   0.56    0.66
w[1]    0.39   0.03   0.34    0.44
mu[0]   3.48   0.09   3.33    3.63
mu[1]  10.92   0.17  10.64   11.20
sigma[0] 1.18  0.07   1.07    1.30
sigma[1] 2.43  0.13   2.22    2.65
```

The model recovered the two subgroups: 61% short-stay (mean 3.5 days) and 39% long-stay (mean 10.9 days).

## The Label Switching Problem

Mixture models have a symmetry problem: swapping component 1 and component 2 (with their weights) gives the same likelihood. The sampler can jump between these modes, making posteriors uninterpretable.

Solutions:

```python
# Solution 1: Ordered means (used above)
# Force mu[0] < mu[1] via ordered transform

# Solution 2: Informative priors that break symmetry
# pm.Normal("mu", mu=[3, 10], sigma=1, shape=2)  # Prior knowledge about locations

# Solution 3: Post-hoc relabeling
# Sort components by mean in each posterior sample
```

The ordered transform is simplest and works well for 2-3 components.

## Assigning Patients to Clusters

After fitting, compute the posterior probability that each patient belongs to each component:

```python
# Posterior cluster assignment probabilities
with mixture_model:
    # Component log-probabilities for each observation
    mu_samples = trace_mix.posterior["mu"].mean(dim=["chain", "draw"]).values
    sigma_samples = trace_mix.posterior["sigma"].mean(dim=["chain", "draw"]).values
    w_samples = trace_mix.posterior["w"].mean(dim=["chain", "draw"]).values

from scipy.stats import norm

# P(component k | observation i) via Bayes' rule
log_lik_0 = norm.logpdf(los, mu_samples[0], sigma_samples[0]) + np.log(w_samples[0])
log_lik_1 = norm.logpdf(los, mu_samples[1], sigma_samples[1]) + np.log(w_samples[1])

# Normalize
log_total = np.logaddexp(log_lik_0, log_lik_1)
prob_surgical = np.exp(log_lik_1 - log_total)

# Patients with LOS around 6-8 days have uncertain assignment
uncertain = (prob_surgical > 0.2) & (prob_surgical < 0.8)
print(f"Patients with uncertain cluster assignment: {uncertain.sum()}")
print(f"Their LOS values: {los[uncertain][:10].round(1)}")
```

Patients in the overlap region get soft assignments — the model is honest about ambiguity.

## Choosing the Number of Components

How do you know it's 2 groups and not 3? Use LOO-CV:

```python
# Fit models with K=1, 2, 3 components
models = {}
traces = {}

for k in [1, 2, 3]:
    with pm.Model() as model:
        if k == 1:
            mu = pm.Normal("mu", mu=7, sigma=5)
            sigma = pm.HalfNormal("sigma", sigma=5)
            y = pm.Normal("y", mu=mu, sigma=sigma, observed=los)
        else:
            w = pm.Dirichlet("w", a=np.ones(k))
            mu = pm.Normal("mu", mu=np.linspace(3, 12, k), sigma=3, shape=k,
                          transform=pm.distributions.transforms.ordered)
            sigma = pm.HalfNormal("sigma", sigma=3, shape=k)
            comp_dists = [pm.Normal.dist(mu=mu[i], sigma=sigma[i]) for i in range(k)]
            y = pm.Mixture("y", w=w, comp_dists=comp_dists, observed=los)

        trace = pm.sample(2000, tune=2000, cores=2, random_seed=42,
                         target_accept=0.9)
        models[f"K={k}"] = model
        traces[f"K={k}"] = trace

# Compare
comparison = az.compare({name: traces[name] for name in traces}, ic="loo")
print(comparison)
```

K=2 should win decisively over K=1 (bimodal data). K=3 might be slightly better or slightly worse — if it's close, prefer the simpler model.

## Adding Covariates to Mixtures

Make the mixture weights depend on patient characteristics:

```python
# Age might predict which subgroup a patient belongs to
age = np.random.normal(68, 12, n)
age_z = (age - age.mean()) / age.std()

with pm.Model() as covariate_mixture:
    # Mixture weight depends on age (logistic regression on component membership)
    alpha = pm.Normal("alpha", mu=0, sigma=1)
    beta_age = pm.Normal("beta_age", mu=0, sigma=0.5)

    # P(surgical) as function of age
    logit_p = alpha + beta_age * age_z
    w_surgical = pm.math.sigmoid(logit_p)
    w = pm.math.stack([1 - w_surgical, w_surgical]).T

    # Component parameters
    mu = pm.Normal("mu", mu=[4, 10], sigma=2, shape=2,
                   transform=pm.distributions.transforms.ordered)
    sigma = pm.HalfNormal("sigma", sigma=3, shape=2)

    # Mixture (per-observation weights)
    comp_dists = [pm.Normal.dist(mu=mu[0], sigma=sigma[0]),
                  pm.Normal.dist(mu=mu[1], sigma=sigma[1])]
    y = pm.Mixture("y", w=w, comp_dists=comp_dists, observed=los)

    trace_cov = pm.sample(2000, tune=2000, cores=2, random_seed=42,
                          target_accept=0.9)
```

Now the model says: "Older patients are more likely to be in the long-stay subgroup." This is more useful than unsupervised clustering — it connects the subgroups to observable features.

## What You Learned

- **Mixture models** — model data as coming from K hidden subgroups
- **Label switching** — symmetry problem solved by ordering constraints
- **Soft clustering** — posterior probability of cluster membership per observation
- **Model selection for K** — use LOO-CV to choose number of components
- **Covariate-dependent mixtures** — let patient features predict subgroup membership

Dr. Okafor: "So there really are two types of patients hiding in the data?"

You: "The model strongly supports two subgroups — short-stay (mean 3.5 days, likely medical admissions) and long-stay (mean 11 days, likely surgical). Older patients are more likely to be in the long-stay group. We can now give each subgroup its own prediction model."

Next: predicting *how long* until a patient is readmitted — not just whether they will be. That's survival analysis, and it has a unique challenge: censored data.

---

[← Chapter 10: Model Comparison](chapter-10-model-comparison.md) | [Chapter 12: Survival Analysis →](chapter-12-survival.md)
