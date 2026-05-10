# Probabilistic Programming — Thinking in Distributions

A narrative-driven course on probabilistic programming and Bayesian inference. You're a data scientist at a health-tech startup where point estimates keep failing. Over 15 chapters, you'll replace fragile predictions with honest uncertainty — one broken model at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, Bayesian intuition, the cast |
| 01 | [The Coin That Isn't Fair](chapter-01-coin-flip.md) | A/B test gives wrong answer | Bayes' theorem, prior, likelihood, posterior |
| 02 | [How Confident Are We?](chapter-02-credible-intervals.md) | Point estimate hides uncertainty | Credible intervals, HDI, posterior predictive |
| 03 | [Sampling the Impossible](chapter-03-mcmc.md) | Posterior has no closed form | MCMC, Metropolis-Hastings, trace plots |
| 04 | [A Better Sampler](chapter-04-nuts.md) | Metropolis is too slow | HMC, NUTS, divergences, tuning |
| 05 | [Regression with Doubt](chapter-05-linear-regression.md) | OLS gives no uncertainty on predictions | Bayesian linear regression, posterior slopes |
| 06 | [Groups That Differ](chapter-06-hierarchical.md) | Not enough data per hospital | Hierarchical models, partial pooling, shrinkage |
| 07 | [Counts and Rates](chapter-07-glm.md) | Patient events aren't Gaussian | Poisson regression, logistic regression, link functions |
| 08 | [Time Changes Things](chapter-08-time-series.md) | Readmission rate is trending | Autoregressive models, changepoint detection |
| 09 | [Missing Data](chapter-09-missing-data.md) | 30% of lab values are missing | Imputation as inference, MAR/MCAR/MNAR |
| 10 | [Which Model Is Better?](chapter-10-model-comparison.md) | Two models, both plausible | WAIC, LOO-CV, Bayes factors |
| 11 | [Mixture Models](chapter-11-mixtures.md) | Patient population isn't homogeneous | Gaussian mixtures, label switching, clustering |
| 12 | [Survival Analysis](chapter-12-survival.md) | "When will the patient return?" | Censoring, hazard functions, Cox model |
| 13 | [Causal Inference](chapter-13-causal.md) | Correlation isn't causation | DAGs, do-calculus, confounders, instruments |
| 14 | [Decision Under Uncertainty](chapter-14-decisions.md) | Model is good but decisions are bad | Loss functions, expected utility, value of information |
| 15 | [Production Bayes](chapter-15-production.md) | Model works in notebook, not in prod | Prior predictive checks, diagnostics, deployment |

## Prerequisites

- Python 3.10+
- `pip install pymc arviz numpy matplotlib`

## Philosophy

Every model is introduced because a point estimate failed someone. No priors without a reason. No math without a problem. The wrong answer comes first. The honest uncertainty follows.
