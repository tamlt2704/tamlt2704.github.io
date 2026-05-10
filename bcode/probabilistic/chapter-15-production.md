# Chapter 15: Production Bayes — From Notebook to Deployment

[← Chapter 14: Decisions](chapter-14-decisions.md)

---

## The Problem

MedPulse's readmission model works beautifully in a Jupyter notebook. It samples in 3 minutes, produces calibrated predictions, and makes cost-effective decisions.

But the clinical team needs predictions in real-time — when a patient is being discharged. They can't wait 3 minutes for MCMC. They can't install PyMC on the hospital's EHR system. And six months from now, the patient population might shift, making the model's predictions unreliable.

Dr. Okafor: "The model is great in your notebook. But I need a number in the discharge summary *now*, and I need to know it's still accurate next month."

## The Production Workflow

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ 1. Develop  │ →  │ 2. Validate  │ →  │ 3. Serve    │ →  │ 4. Monitor   │
│ (notebook)  │    │ (diagnostics)│    │ (API)       │    │ (drift)      │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
```

## Step 1: Prior Predictive Checks (Before Fitting)

Never fit a model without checking that your priors are reasonable:

```python
import pymc as pm
import arviz as az
import numpy as np
import json

# The production model
def build_model(age_z, severity_z, has_followup, observed=None):
    with pm.Model() as model:
        # Priors
        b0 = pm.Normal("b0", mu=-1, sigma=1)
        b_age = pm.Normal("b_age", mu=0, sigma=0.5)
        b_severity = pm.Normal("b_severity", mu=0, sigma=0.5)
        b_followup = pm.Normal("b_followup", mu=0, sigma=0.5)
        
        logit_p = b0 + b_age * age_z + b_severity * severity_z + b_followup * has_followup
        y = pm.Bernoulli("y", logit_p=logit_p, observed=observed)
    return model

# Prior predictive check
np.random.seed(42)
n = 200
age_z = np.random.normal(0, 1, n)
severity_z = np.random.normal(0, 1, n)
has_followup = np.random.binomial(1, 0.5, n)

model = build_model(age_z, severity_z, has_followup)
with model:
    prior_pred = pm.sample_prior_predictive(500, random_seed=42)

# Check: do prior predictions span a reasonable range?
prior_rates = prior_pred.prior_predictive["y"].values.mean(axis=-1).flatten()
print(f"Prior predictive readmission rate: {prior_rates.mean():.1%} "
      f"[{np.percentile(prior_rates, 5):.1%}, {np.percentile(prior_rates, 95):.1%}]")

# Should be wide but not absurd (e.g., 5%-80%, not 0.001%-99.9%)
```

If prior predictions are unreasonable, fix priors before fitting. This catches modeling errors early.

## Step 2: Model Diagnostics Checklist

After fitting, run every diagnostic before deploying:

```python
# Fit the model
readmitted = np.random.binomial(1, 0.25, n)  # Placeholder
model = build_model(age_z, severity_z, has_followup, observed=readmitted)

with model:
    trace = pm.sample(2000, tune=1000, cores=2, random_seed=42)

# === DIAGNOSTIC CHECKLIST ===

# 1. Convergence: R-hat should be < 1.01 for all parameters
rhat = az.rhat(trace)
max_rhat = max(rhat[var].values.max() for var in rhat.data_vars)
print(f"✓ Max R-hat: {max_rhat:.4f} {'(PASS)' if max_rhat < 1.01 else '(FAIL)'}")

# 2. Effective sample size: should be > 400 for reliable estimates
ess = az.ess(trace)
min_ess = min(ess[var].values.min() for var in ess.data_vars)
print(f"✓ Min ESS: {min_ess:.0f} {'(PASS)' if min_ess > 400 else '(FAIL)'}")

# 3. Divergences: should be 0
n_divergences = trace.sample_stats["diverging"].values.sum()
print(f"✓ Divergences: {n_divergences} {'(PASS)' if n_divergences == 0 else '(FAIL)'}")

# 4. Energy: Bayesian fraction of missing information
bfmi = az.bfmi(trace)
print(f"✓ BFMI: {bfmi.min():.3f} {'(PASS)' if bfmi.min() > 0.3 else '(FAIL)'}")

# 5. Posterior predictive check
with model:
    ppc = pm.sample_posterior_predictive(trace, random_seed=42)
ppc_rate = ppc.posterior_predictive["y"].values.mean(axis=-1).flatten()
obs_rate = readmitted.mean()
print(f"✓ Observed rate: {obs_rate:.1%}, PPC mean: {ppc_rate.mean():.1%}")
```

**Deploy only if all checks pass.** If R-hat > 1.01 or divergences > 0, the model hasn't converged — predictions are unreliable.

## Step 3: Serving Predictions (Without MCMC at Runtime)

The key insight: run MCMC once during training, then use the posterior samples for fast predictions at serving time.

```python
# === TRAINING TIME: Save posterior samples ===
def export_posterior(trace, filepath="model_posterior.json"):
    """Export posterior samples for serving."""
    posterior = {
        "b0": trace.posterior["b0"].values.flatten().tolist(),
        "b_age": trace.posterior["b_age"].values.flatten().tolist(),
        "b_severity": trace.posterior["b_severity"].values.flatten().tolist(),
        "b_followup": trace.posterior["b_followup"].values.flatten().tolist(),
    }
    # Store only 500 samples (enough for predictions)
    posterior = {k: v[:500] for k, v in posterior.items()}
    
    with open(filepath, "w") as f:
        json.dump(posterior, f)
    print(f"Saved {len(posterior['b0'])} posterior samples to {filepath}")

export_posterior(trace)
```

```python
# === SERVING TIME: Fast predictions (no PyMC needed) ===
class ReadmissionPredictor:
    """Lightweight predictor using stored posterior samples."""
    
    def __init__(self, posterior_path, standardization_params):
        with open(posterior_path) as f:
            self.posterior = json.load(f)
        self.params = standardization_params
        self.n_samples = len(self.posterior["b0"])
    
    def predict(self, age, severity, has_followup):
        """Return prediction with uncertainty."""
        # Standardize inputs
        age_z = (age - self.params["age_mean"]) / self.params["age_std"]
        sev_z = (severity - self.params["sev_mean"]) / self.params["sev_std"]
        
        # Compute predictions for all posterior samples
        b0 = np.array(self.posterior["b0"])
        b_age = np.array(self.posterior["b_age"])
        b_sev = np.array(self.posterior["b_severity"])
        b_fu = np.array(self.posterior["b_followup"])
        
        logit_p = b0 + b_age * age_z + b_sev * sev_z + b_fu * has_followup
        probs = 1 / (1 + np.exp(-logit_p))
        
        return {
            "mean": float(probs.mean()),
            "std": float(probs.std()),
            "hdi_90": [float(np.percentile(probs, 5)),
                       float(np.percentile(probs, 95))],
            "p_above_threshold": float((probs > 0.067).mean()),
        }

# Usage (milliseconds, no MCMC)
predictor = ReadmissionPredictor(
    "model_posterior.json",
    {"age_mean": 68, "age_std": 12, "sev_mean": 4.5, "sev_std": 2.0}
)

result = predictor.predict(age=75, severity=6, has_followup=0)
print(f"P(readmission): {result['mean']:.1%} [{result['hdi_90'][0]:.1%}, {result['hdi_90'][1]:.1%}]")
print(f"Recommend intervention: {result['p_above_threshold']:.0%} of posterior above threshold")
```

This runs in <1ms — fast enough for real-time clinical decisions.

## Step 4: Monitoring for Data Drift

Models degrade when the patient population changes. Monitor continuously:

```python
class DriftMonitor:
    """Detect when incoming data no longer matches training distribution."""
    
    def __init__(self, training_stats, alert_threshold=2.0):
        self.training_stats = training_stats  # mean, std of features
        self.alert_threshold = alert_threshold
        self.recent_predictions = []
        self.recent_outcomes = []
    
    def check_input_drift(self, features):
        """Flag if inputs are outside training distribution."""
        alerts = []
        for name, value in features.items():
            if name in self.training_stats:
                z_score = abs(value - self.training_stats[name]["mean"]) / \
                          self.training_stats[name]["std"]
                if z_score > self.alert_threshold:
                    alerts.append(f"{name}: z={z_score:.1f}")
        return alerts
    
    def check_calibration(self, window=100):
        """Check if predicted probabilities match observed rates."""
        if len(self.recent_predictions) < window:
            return None
        
        recent_preds = np.array(self.recent_predictions[-window:])
        recent_outcomes = np.array(self.recent_outcomes[-window:])
        
        # Bin predictions and check calibration
        bins = [0, 0.1, 0.2, 0.3, 0.5, 1.0]
        for i in range(len(bins) - 1):
            mask = (recent_preds >= bins[i]) & (recent_preds < bins[i+1])
            if mask.sum() > 10:
                predicted = recent_preds[mask].mean()
                observed = recent_outcomes[mask].mean()
                if abs(predicted - observed) > 0.1:
                    return f"Miscalibrated in [{bins[i]:.0%}, {bins[i+1]:.0%}]: " \
                           f"predicted {predicted:.1%}, observed {observed:.1%}"
        return None
    
    def log_prediction(self, predicted_prob, actual_outcome):
        """Log for ongoing monitoring."""
        self.recent_predictions.append(predicted_prob)
        self.recent_outcomes.append(actual_outcome)

# Setup monitoring
monitor = DriftMonitor(
    training_stats={
        "age": {"mean": 68, "std": 12},
        "severity": {"mean": 4.5, "std": 2.0},
    }
)

# In production loop:
# alerts = monitor.check_input_drift({"age": patient_age, "severity": patient_severity})
# if alerts: log_warning(f"Input drift detected: {alerts}")
# calibration = monitor.check_calibration()
# if calibration: trigger_retrain_alert(calibration)
```

## When to Retrain

Retrain the model when:
1. **Calibration degrades** — predicted 20% but observing 35%
2. **Input distribution shifts** — new patient demographics
3. **New data available** — enough new observations to improve estimates
4. **Clinical context changes** — new treatments, policies, or protocols

Don't retrain on a schedule — retrain when monitoring signals degradation.

## The Full Pipeline

```python
# Production deployment checklist:
DEPLOYMENT_CHECKLIST = """
□ Prior predictive check passes (predictions in reasonable range)
□ All R-hat < 1.01
□ All ESS > 400
□ Zero divergences
□ BFMI > 0.3
□ Posterior predictive check matches observed data
□ LOO-CV shows no high Pareto-k observations
□ Calibration plot looks good (predicted ≈ observed rates)
□ Posterior samples exported and versioned
□ Standardization parameters saved with model
□ Drift monitoring configured
□ Alerting thresholds set
□ Rollback plan documented
"""
print(DEPLOYMENT_CHECKLIST)
```

## What You Learned

- **Prior predictive checks** — validate priors before fitting (catches errors early)
- **Diagnostic checklist** — R-hat, ESS, divergences, BFMI (all must pass)
- **Posterior export** — save samples for fast serving without MCMC at runtime
- **Lightweight predictor** — millisecond predictions using stored posterior samples
- **Drift monitoring** — detect when the model no longer matches reality
- **Calibration checks** — verify predicted probabilities match observed rates

Dr. Okafor: "So the model runs instantly when I discharge a patient?"

You: "Yes. We run MCMC once during training — that takes minutes. At serving time, we just do matrix multiplication against stored samples. Sub-millisecond. And we're monitoring every prediction. If the patient population shifts or the model starts miscalibrating, we get an alert and retrain."

---

This is the end of the probabilistic programming course. You've gone from flipping coins to deploying production Bayesian models that make real clinical decisions under uncertainty. The key insight throughout: **uncertainty is not a bug — it's the most valuable output your model produces.**

---

[← Chapter 14: Decisions](chapter-14-decisions.md)
