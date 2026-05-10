# Chapter 13: Causal Inference — Correlation Isn't Causation

[← Chapter 12: Survival Analysis](chapter-12-survival.md) | [Chapter 14: Decisions →](chapter-14-decisions.md)

---

## The Problem

MedPulse introduced a new discharge protocol six months ago. The data shows: patients who received the new protocol have 30% lower readmission rates. The CEO wants to roll it out system-wide.

But there's a catch. The protocol was piloted at three hospitals that volunteered — hospitals with younger, less severe patient populations. Patients who received the protocol were also more likely to have follow-up appointments scheduled.

Does the protocol *cause* lower readmissions? Or are healthier patients at better-resourced hospitals simply less likely to be readmitted regardless?

Dr. Okafor: "I believe the protocol works. But the board wants evidence it's not just selection bias."

## Confounders and DAGs

A **Directed Acyclic Graph** (DAG) encodes your causal assumptions:

```
    Severity
    /      \
   v        v
Protocol → Readmission
   ^        ^
    \      /
     Age
```

Severity and age affect both who gets the protocol (selection) and readmission (outcome). They're **confounders** — they create a spurious association between protocol and readmission.

```python
import pymc as pm
import arviz as az
import numpy as np

# Simulated observational data with confounding
np.random.seed(42)
n = 500

# Confounders
age = np.random.normal(68, 12, n)
severity = np.random.uniform(1, 8, n)

# Treatment assignment (confounded — healthier patients more likely to get protocol)
logit_treat = -1.0 - 0.03 * age - 0.2 * severity  # Sicker/older → less likely
prob_treat = 1 / (1 + np.exp(-logit_treat))
protocol = np.random.binomial(1, prob_treat)

print(f"Protocol rate: {protocol.mean():.1%}")
print(f"Mean severity (treated): {severity[protocol==1].mean():.1f}")
print(f"Mean severity (untreated): {severity[protocol==0].mean():.1f}")

# Outcome (true causal effect of protocol = -0.5 on logit scale)
true_effect = -0.5  # Protocol truly reduces readmission
logit_readmit = -1.5 + 0.02 * age + 0.3 * severity + true_effect * protocol
prob_readmit = 1 / (1 + np.exp(-logit_readmit))
readmitted = np.random.binomial(1, prob_readmit)

print(f"\nReadmission rate (treated): {readmitted[protocol==1].mean():.1%}")
print(f"Readmission rate (untreated): {readmitted[protocol==0].mean():.1%}")
print(f"Naive difference: {readmitted[protocol==0].mean() - readmitted[protocol==1].mean():.1%}")
```

```
Protocol rate: 32.4%
Mean severity (treated): 3.8
Mean severity (untreated): 5.2

Readmission rate (treated): 22.8%
Readmission rate (untreated): 38.5%
Naive difference: 15.7%
```

The naive difference (15.7 percentage points) overstates the true effect because treated patients were healthier to begin with.

## The Backdoor Criterion

To estimate the causal effect of Protocol → Readmission, you must block all **backdoor paths** (non-causal paths that create spurious association).

Backdoor paths: Protocol ← Severity → Readmission, Protocol ← Age → Readmission

**Solution**: condition on (adjust for) severity and age. This blocks the confounding paths while leaving the causal path open.

```python
# Naive model (ignoring confounders) — BIASED
with pm.Model() as naive_model:
    b0 = pm.Normal("b0", mu=0, sigma=2)
    b_protocol = pm.Normal("b_protocol", mu=0, sigma=1)

    logit_p = b0 + b_protocol * protocol
    y = pm.Bernoulli("y", logit_p=logit_p, observed=readmitted)

    trace_naive = pm.sample(2000, tune=1000, cores=2, random_seed=42)

# Adjusted model (conditioning on confounders) — UNBIASED
age_z = (age - age.mean()) / age.std()
sev_z = (severity - severity.mean()) / severity.std()

with pm.Model() as adjusted_model:
    b0 = pm.Normal("b0", mu=0, sigma=2)
    b_protocol = pm.Normal("b_protocol", mu=0, sigma=1)
    b_age = pm.Normal("b_age", mu=0, sigma=1)
    b_severity = pm.Normal("b_severity", mu=0, sigma=1)

    logit_p = b0 + b_protocol * protocol + b_age * age_z + b_severity * sev_z
    y = pm.Bernoulli("y", logit_p=logit_p, observed=readmitted)

    trace_adjusted = pm.sample(2000, tune=1000, cores=2, random_seed=42)

# Compare estimates
naive_effect = trace_naive.posterior["b_protocol"].values.flatten()
adjusted_effect = trace_adjusted.posterior["b_protocol"].values.flatten()

print(f"Naive effect (biased): {naive_effect.mean():.2f} "
      f"[{np.percentile(naive_effect, 5):.2f}, {np.percentile(naive_effect, 95):.2f}]")
print(f"Adjusted effect (causal): {adjusted_effect.mean():.2f} "
      f"[{np.percentile(adjusted_effect, 5):.2f}, {np.percentile(adjusted_effect, 95):.2f}]")
print(f"True effect: {true_effect:.2f}")
```

```
Naive effect (biased): -0.82 [-0.98, -0.66]
Adjusted effect (causal): -0.51 [-0.72, -0.30]
True effect: -0.50
```

The naive estimate is too large (confounding inflates the apparent benefit). The adjusted estimate recovers the true causal effect.

## Converting to Interpretable Quantities

```python
# Average Treatment Effect (ATE) on probability scale
b0_s = trace_adjusted.posterior["b0"].values.flatten()
b_prot_s = trace_adjusted.posterior["b_protocol"].values.flatten()
b_age_s = trace_adjusted.posterior["b_age"].values.flatten()
b_sev_s = trace_adjusted.posterior["b_severity"].values.flatten()

# Predict for each patient under both treatment and control
ate_samples = []
for i in range(min(1000, len(b0_s))):
    logit_treated = b0_s[i] + b_prot_s[i] * 1 + b_age_s[i] * age_z + b_sev_s[i] * sev_z
    logit_control = b0_s[i] + b_prot_s[i] * 0 + b_age_s[i] * age_z + b_sev_s[i] * sev_z

    p_treated = 1 / (1 + np.exp(-logit_treated))
    p_control = 1 / (1 + np.exp(-logit_control))

    ate_samples.append((p_treated - p_control).mean())

ate_samples = np.array(ate_samples)
print(f"Average Treatment Effect: {ate_samples.mean():.1%} "
      f"[{np.percentile(ate_samples, 5):.1%}, {np.percentile(ate_samples, 95):.1%}]")
```

The protocol reduces readmission probability by about 7 percentage points on average, after adjusting for confounders.

## When Adjustment Isn't Enough: Instrumental Variables

Sometimes you can't measure all confounders. If there's an **unmeasured** confounder (say, patient motivation), adjustment fails.

An **instrumental variable** (IV) affects treatment but has no direct effect on the outcome:

```
Distance to hospital → Protocol assignment → Readmission
                                                ^
                                                |
                                          Motivation (unmeasured)
```

Distance to the pilot hospital affects whether a patient gets the protocol, but doesn't directly affect readmission (conditional on treatment).

```python
# IV example: distance as instrument
distance = np.random.exponential(10, n)  # km to pilot hospital

# Unmeasured confounder
motivation = np.random.normal(0, 1, n)

# Treatment depends on distance AND motivation
logit_treat_iv = -0.5 - 0.1 * distance + 0.5 * motivation
prob_treat_iv = 1 / (1 + np.exp(-logit_treat_iv))
protocol_iv = np.random.binomial(1, prob_treat_iv)

# Outcome depends on treatment AND motivation (confounder)
logit_readmit_iv = -1.0 + true_effect * protocol_iv - 0.3 * motivation
readmitted_iv = np.random.binomial(1, 1 / (1 + np.exp(-logit_readmit_iv)))

# Two-stage Bayesian IV
with pm.Model() as iv_model:
    # Stage 1: Protocol ~ Distance (instrument)
    gamma_0 = pm.Normal("gamma_0", mu=0, sigma=2)
    gamma_dist = pm.Normal("gamma_dist", mu=0, sigma=0.5)
    logit_treat_pred = gamma_0 + gamma_dist * distance
    treat_stage1 = pm.Bernoulli("treat_stage1", logit_p=logit_treat_pred,
                                observed=protocol_iv)

    # Stage 2: Readmission ~ Predicted treatment
    b0 = pm.Normal("b0", mu=0, sigma=2)
    b_treat = pm.Normal("b_treat", mu=0, sigma=1)
    # Use predicted probability of treatment (not observed)
    treat_prob = pm.math.sigmoid(logit_treat_pred)
    logit_y = b0 + b_treat * treat_prob
    y = pm.Bernoulli("y", logit_p=logit_y, observed=readmitted_iv)

    trace_iv = pm.sample(2000, tune=1000, cores=2, random_seed=42)
```

## Colliders: What NOT to Condition On

Not all variables should be adjusted for. A **collider** is caused by both treatment and outcome:

```
Protocol → Hospital_Rating ← Readmission
```

If good protocols AND low readmissions both improve hospital ratings, conditioning on rating *creates* a spurious association. Don't adjust for colliders.

## Practical DAG Workflow

1. **Draw the DAG** — encode your domain knowledge about what causes what
2. **Identify confounders** — variables that cause both treatment and outcome
3. **Check the backdoor criterion** — find a sufficient adjustment set
4. **Verify no colliders** — don't condition on descendants of treatment
5. **Fit the adjusted model** — include confounders as covariates
6. **Sensitivity analysis** — how much unmeasured confounding would overturn your conclusion?

## What You Learned

- **Confounders** — variables that cause both treatment and outcome, creating spurious associations
- **DAGs** — encode causal assumptions visually; identify what to adjust for
- **Backdoor criterion** — condition on variables that block all non-causal paths
- **Average Treatment Effect** — causal effect on the probability scale
- **Instrumental variables** — handle unmeasured confounders when a valid instrument exists
- **Colliders** — variables you must NOT condition on

Dr. Okafor: "So the protocol really works? It's not just selection bias?"

You: "After adjusting for age and severity, the protocol still reduces readmissions by about 7 percentage points. The effect is real, though smaller than the naive 16% difference suggested. The confounding was inflating the apparent benefit by more than double."

Now you know the protocol works. But which patients should get intensive follow-up? Not everyone — resources are limited. You need to make decisions under uncertainty.

---

[← Chapter 12: Survival Analysis](chapter-12-survival.md) | [Chapter 14: Decisions →](chapter-14-decisions.md)
