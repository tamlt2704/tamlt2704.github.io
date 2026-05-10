# Chapter 0: Before You Start

[Chapter 1: The Coin That Isn't Fair →](chapter-01-coin-flip.md)

---

## The Story

This is a series about probabilistic programming — but not the kind where you memorize "Bayes' theorem is P(A|B) = P(B|A)P(A)/P(B)" and move on.

You're a data scientist at **MedPulse**, a health-tech startup that predicts patient readmission risk. The company's models are logistic regressions trained on 50,000 patient records. They output a single number: "This patient has a 73% chance of readmission within 30 days."

The problem? That 73% is a lie. Not because the model is wrong — because it's hiding how uncertain it is. A patient with 10 prior visits and complete lab work gets 73%. A patient with 1 prior visit and half their data missing also gets 73%. The model is equally confident about both, and that confidence is killing people.

Your medical director, **Dr. Okafor**, corners you after a mortality review:

"We discharged a patient based on your model's low-risk score. They came back in 48 hours with sepsis. Your model said 12% risk. What it should have said was 'I have no idea — I've never seen a patient like this.' I need models that know what they don't know."

You nod. You took a statistics class. You've heard of Bayesian inference. How hard can it be?

Over the next 15 chapters, you'll rebuild MedPulse's prediction system from point estimates to full posterior distributions. Every model you build solves a real problem — quantifying uncertainty, borrowing strength across hospitals, handling missing data, comparing treatments. And every naive approach will fail in a way that teaches you why probabilistic thinking exists.

The sampler will diverge. The prior will dominate when you have little data. The hierarchical model will shrink too aggressively. The mixture model will swap labels between runs. The causal model will confuse correlation with intervention.

Each failure teaches you something about reasoning under uncertainty that no textbook could.

By the end, you'll have working implementations of Bayesian inference, MCMC sampling, hierarchical models, GLMs, time series, mixture models, survival analysis, and causal inference — and you'll understand *when* and *why* to reach for each one.

## How to Read This

Every chapter is the same loop:

1. A point estimate fails — it's overconfident, misleading, or dangerous
2. You identify what's missing — uncertainty, structure, or mechanism
3. You learn the probabilistic model that captures it
4. You implement it, step by step
5. You interpret the results — and discover the next limitation

No model shows up before you need it. You won't hear about hierarchical models until you have 20 hospitals with 50 patients each and pooling them all together gives nonsense. You won't touch NUTS until Metropolis-Hastings takes 4 hours to converge.

The overconfident answer comes first. The honest uncertainty follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Data Scientist | Trained in ML. New to Bayes. |
| **Dr. Okafor** | Medical Director | "I don't want a number. I want to know how much you trust that number." |
| **Priya** | ML Engineer | "Your model takes 20 minutes to fit. The old one takes 2 seconds." |
| **Marcus** | Product Manager | "Can you explain a posterior distribution to a nurse?" |
| **The Dashboard** | Your creation | Shows uncertainty. Confuses everyone at first. Saves lives later. |
| **The Old Model** | Logistic regression | Fast. Confident. Sometimes fatally wrong. |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | A/B test gives wrong answer with small sample | Bayes' theorem, priors, posteriors, updating |
| 2 | Point estimate hides uncertainty | Credible intervals, HDI, posterior predictive checks |
| 3 | Posterior has no closed-form solution | MCMC, Metropolis-Hastings, convergence diagnostics |
| 4 | Metropolis is too slow for complex models | HMC, NUTS, divergences, effective sample size |
| 5 | Linear regression gives no uncertainty on predictions | Bayesian regression, posterior predictive bands |
| 6 | Not enough data per hospital to fit separate models | Hierarchical models, partial pooling, shrinkage |
| 7 | Patient counts aren't Gaussian | GLMs, Poisson regression, logistic regression |
| 8 | Readmission rate changes over time | Time series, autoregressive priors, changepoints |
| 9 | 30% of lab values are missing | Missing data as parameters, imputation as inference |
| 10 | Two models both seem reasonable | Model comparison, WAIC, LOO-CV, stacking |
| 11 | Patient population has hidden subgroups | Mixture models, label switching, identifiability |
| 12 | "When will the patient come back?" | Survival analysis, censoring, hazard models |
| 13 | Treatment effect is confounded | Causal DAGs, do-calculus, instrumental variables |
| 14 | Good predictions but bad decisions | Decision theory, loss functions, value of information |
| 15 | Model works in notebook, fails in production | Prior predictive checks, deployment, monitoring |

## Prerequisites

Three things: Python 3, PyMC, and comfort with uncertainty.

### Python 3.10+

```bash
python3 --version
# Python 3.10.x or higher
```

### Dependencies

```bash
pip install pymc arviz numpy matplotlib pandas
```

| Package | Why |
|---|---|
| `pymc` | Probabilistic programming framework (builds and samples models) |
| `arviz` | Visualization and diagnostics for Bayesian models |
| `numpy` | Numerical computation |
| `matplotlib` | Plotting posteriors, traces, predictions |
| `pandas` | Data manipulation |

PyMC handles the hard parts — building computational graphs, running NUTS, computing diagnostics. You focus on model structure and interpretation.

### Quick Check

```python
import pymc as pm
import arviz as az

print(f"PyMC version: {pm.__version__}")
print(f"ArviZ version: {az.__version__}")

# Minimal model — sample from a Normal
with pm.Model() as test:
    x = pm.Normal("x", mu=0, sigma=1)
    trace = pm.sample(100, cores=1, progressbar=False)

print(f"Posterior mean of x: {trace.posterior['x'].mean().values:.3f}")
print("Ready to go")
```

If that runs without errors and prints a number near 0, you're set.

### Optional: Jupyter

Probabilistic programming is exploratory. Notebooks let you see trace plots, posterior distributions, and diagnostics inline. Highly recommended.

```bash
pip install jupyterlab
```

## The Key Idea

Classical statistics asks: "Given this model, how likely is the data?"

Bayesian statistics asks: "Given this data, how likely is each possible model?"

The difference is everything:

| | Classical (Frequentist) | Bayesian |
|---|---|---|
| Parameters | Fixed but unknown numbers | Random variables with distributions |
| Uncertainty | Confidence intervals (about the procedure) | Credible intervals (about the parameter) |
| Prior knowledge | Not formally included | Encoded as prior distributions |
| Output | Point estimate + p-value | Full posterior distribution |
| Small data | "Insufficient sample size" | "Wide posterior — we're uncertain" |
| Prediction | Single predicted value | Distribution of predicted values |

A frequentist model says: "The readmission rate is 0.23."
A Bayesian model says: "The readmission rate is probably between 0.15 and 0.31, with 0.23 being most likely, but we're not very sure because we only have 40 patients from this hospital."

Dr. Okafor wants the second answer. So do you.

## Notation

| Symbol | Meaning |
|---|---|
| θ (theta) | Parameter(s) of the model |
| P(θ) | Prior — what we believe before seeing data |
| P(D\|θ) | Likelihood — how probable is the data given parameters |
| P(θ\|D) | Posterior — what we believe after seeing data |
| D | Observed data |
| ŷ | Predicted value |
| HDI | Highest Density Interval (most compact credible interval) |
| MCMC | Markov Chain Monte Carlo (sampling algorithm) |

Don't memorize these. They'll become intuition as you use them.

## The Mental Model

Think of Bayesian inference as a conversation:

1. **Prior**: "Before I see any data, here's what I believe about the world." (Maybe readmission rates are usually between 5% and 40%.)

2. **Data**: "Here's what actually happened." (Out of 100 patients, 23 were readmitted.)

3. **Posterior**: "Now that I've seen the data, here's my updated belief." (The rate is probably between 15% and 31%.)

4. **More data**: "200 more patients, 48 readmitted."

5. **Updated posterior**: "Now I'm more confident — probably between 20% and 26%."

The posterior gets narrower (more certain) as you see more data. With infinite data, Bayesians and frequentists agree. With small data, Bayesians give you honest uncertainty instead of false precision.

That's the whole game. Let's play it.

---

[Chapter 1: The Coin That Isn't Fair →](chapter-01-coin-flip.md)
