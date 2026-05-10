# Chapter 14: Decision Under Uncertainty — From Model to Action

[← Chapter 13: Causal Inference](chapter-13-causal.md) | [Chapter 15: Production →](chapter-15-production.md)

---

## The Problem

MedPulse's readmission model works. It gives posterior probabilities: "This patient has a 35% chance of readmission within 30 days." But what do you *do* with that number?

The current policy: if P(readmission) > 25%, assign intensive follow-up (nurse calls, home visits). This costs $800 per patient. A readmission costs $12,000.

Problem: the 25% threshold was chosen arbitrarily. Some patients at 24% would benefit from follow-up. Some at 30% have low-cost readmissions (planned procedures). The threshold ignores costs, benefits, and uncertainty.

Dr. Okafor: "We're spending $800 on patients who were never going to be readmitted, and missing patients who will be. Can we do better?"

## Loss Functions: Making Costs Explicit

A **loss function** quantifies the cost of each decision-outcome pair:

| | Patient readmitted | Patient NOT readmitted |
|---|---|---|
| **Intervene** (follow-up) | $800 (intervention cost, but avoided $12,000) | $800 (wasted) |
| **Don't intervene** | $12,000 (readmission cost) | $0 (correct) |

Net losses:
- Intervene + readmitted: $800 (spent on follow-up, but saved $12,000 — net benefit)
- Intervene + not readmitted: $800 (wasted money)
- Don't intervene + readmitted: $12,000 (full cost)
- Don't intervene + not readmitted: $0

```python
import numpy as np
import matplotlib.pyplot as plt

# Loss matrix
cost_intervention = 800
cost_readmission = 12000

# Expected loss as function of P(readmission)
p_range = np.linspace(0, 1, 100)

# Expected loss of intervening: cost_intervention (always pay)
loss_intervene = np.full_like(p_range, cost_intervention)

# Expected loss of NOT intervening: p * cost_readmission
loss_no_intervene = p_range * cost_readmission

# Optimal decision: intervene when loss_intervene < loss_no_intervene
# 800 < p * 12000 → p > 800/12000 = 0.067
optimal_threshold = cost_intervention / cost_readmission
print(f"Optimal threshold: {optimal_threshold:.1%}")

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(p_range, loss_intervene, label="Intervene", color="blue", linewidth=2)
ax.plot(p_range, loss_no_intervene, label="Don't intervene", color="red", linewidth=2)
ax.axvline(optimal_threshold, color="green", linestyle="--",
           label=f"Optimal threshold ({optimal_threshold:.1%})")
ax.axvline(0.25, color="gray", linestyle=":", label="Current threshold (25%)")
ax.set_xlabel("P(readmission)")
ax.set_ylabel("Expected Loss ($)")
ax.legend()
ax.set_title("Decision Analysis: When to Intervene")
plt.show()
```

The optimal threshold is 6.7% — far lower than the current 25%. With a 15:1 cost ratio, you should intervene aggressively.

## Incorporating Posterior Uncertainty

The model doesn't give a single probability — it gives a posterior distribution over probabilities. Use the full posterior for decisions:

```python
import pymc as pm
import arviz as az

# Simulated posterior predictions for 5 patients
np.random.seed(42)

# Each patient has 4000 posterior samples of P(readmission)
patients = {
    "Patient A": np.random.beta(3, 7, 4000),      # ~30%, fairly certain
    "Patient B": np.random.beta(1.5, 8, 4000),    # ~15%, uncertain
    "Patient C": np.random.beta(0.8, 12, 4000),   # ~6%, very uncertain
    "Patient D": np.random.beta(15, 35, 4000),    # ~30%, very certain
    "Patient E": np.random.beta(2, 2, 4000),      # ~50%, maximally uncertain
}

# Expected loss for each patient under each action
print(f"{'Patient':<12} {'Mean P':>8} {'E[Loss|Intervene]':>18} "
      f"{'E[Loss|No Intervene]':>20} {'Decision':>10}")
print("-" * 75)

for name, p_samples in patients.items():
    # Expected loss integrates over posterior uncertainty
    el_intervene = cost_intervention  # Fixed cost
    el_no_intervene = (p_samples * cost_readmission).mean()

    decision = "Intervene" if el_intervene < el_no_intervene else "Don't"
    print(f"{name:<12} {p_samples.mean():>8.1%} {el_intervene:>18,.0f} "
          f"{el_no_intervene:>20,.0f} {decision:>10}")
```

```
Patient      Mean P  E[Loss|Intervene]  E[Loss|No Intervene]   Decision
---------------------------------------------------------------------------
Patient A     30.1%                800                3,612   Intervene
Patient B     15.8%                800                1,896   Intervene
Patient C      6.3%                800                  756   Don't
Patient D     30.0%                800                3,600   Intervene
Patient E     50.2%                800                6,024   Intervene
```

## Value of Information: Should You Get More Data?

Sometimes the best decision is to gather more information before acting. The **Expected Value of Perfect Information** (EVPI) tells you the maximum you should pay for a perfect test:

```python
def compute_evpi(p_samples, cost_intervention, cost_readmission):
    """How much would perfect information about this patient be worth?"""
    # Current best decision (without more info)
    el_intervene = cost_intervention
    el_no_intervene = (p_samples * cost_readmission).mean()
    current_best_loss = min(el_intervene, el_no_intervene)

    # With perfect info: intervene only when patient WILL be readmitted
    # Loss with perfect info = P(readmit) * cost_intervention + P(no readmit) * 0
    # (intervene only for true positives, never waste on true negatives)
    perfect_info_loss = (p_samples * cost_intervention).mean()

    evpi = current_best_loss - perfect_info_loss
    return evpi

print(f"{'Patient':<12} {'Mean P':>8} {'EVPI':>10}")
print("-" * 35)
for name, p_samples in patients.items():
    evpi = compute_evpi(p_samples, cost_intervention, cost_readmission)
    print(f"{name:<12} {p_samples.mean():>8.1%} {evpi:>10,.0f}")
```

High EVPI means the patient is near the decision boundary — more information would change your action. Low EVPI means you'd make the same decision regardless of additional data.

## Asymmetric Losses: Not All Errors Are Equal

In healthcare, false negatives (missing a readmission) are often worse than false positives (unnecessary follow-up):

```python
# What if readmission for some patients costs $30,000 (ICU readmission)?
# Personalize the loss function per patient

def personalized_decision(p_samples, patient_cost_readmit, cost_intervention=800):
    """Different patients have different readmission costs."""
    el_intervene = cost_intervention
    el_no_intervene = (p_samples * patient_cost_readmit).mean()
    return "Intervene" if el_intervene < el_no_intervene else "Don't"

# Patient with heart failure: readmission costs $30,000
decision_hf = personalized_decision(
    np.random.beta(1, 15, 4000),  # Only 6% risk
    patient_cost_readmit=30000
)
print(f"Heart failure patient (6% risk, $30k cost): {decision_hf}")

# Patient with minor procedure: readmission costs $5,000
decision_minor = personalized_decision(
    np.random.beta(3, 7, 4000),  # 30% risk
    patient_cost_readmit=5000
)
print(f"Minor procedure patient (30% risk, $5k cost): {decision_minor}")
```

The heart failure patient gets intervention at 6% risk (because the cost of missing them is enormous). The minor procedure patient might not get intervention even at 30% risk (because readmission is cheap).

## Multi-Action Decisions

Real decisions aren't binary. MedPulse has three options:

1. **No intervention**: $0 cost
2. **Phone follow-up**: $200 cost, reduces readmission by 20%
3. **Home visit**: $800 cost, reduces readmission by 50%

```python
def multi_action_decision(p_samples, cost_readmission=12000):
    """Choose among multiple interventions."""
    actions = {
        "No intervention": {
            "cost": 0,
            "risk_reduction": 0.0
        },
        "Phone follow-up": {
            "cost": 200,
            "risk_reduction": 0.20
        },
        "Home visit": {
            "cost": 800,
            "risk_reduction": 0.50
        }
    }

    best_action = None
    best_loss = float("inf")

    for action_name, params in actions.items():
        # Adjusted readmission probability
        adjusted_p = p_samples * (1 - params["risk_reduction"])
        expected_loss = params["cost"] + (adjusted_p * cost_readmission).mean()

        if expected_loss < best_loss:
            best_loss = expected_loss
            best_action = action_name

    return best_action, best_loss

# Decision for different risk levels
for risk_alpha, risk_beta in [(1, 20), (2, 10), (4, 6), (6, 4)]:
    p_samples = np.random.beta(risk_alpha, risk_beta, 4000)
    action, loss = multi_action_decision(p_samples)
    print(f"P(readmit) ≈ {p_samples.mean():.1%}: {action} (expected loss: ${loss:,.0f})")
```

```
P(readmit) ≈ 4.8%: No intervention (expected loss: $576)
P(readmit) ≈ 16.7%: Phone follow-up (expected loss: $1,800)
P(readmit) ≈ 40.0%: Home visit (expected loss: $3,200)
P(readmit) ≈ 60.0%: Home visit (expected loss: $4,400)
```

The model automatically selects the right intensity of intervention based on risk level and cost-effectiveness.

## What You Learned

- **Loss functions** — make costs of decisions explicit and quantifiable
- **Optimal thresholds** — derived from cost ratios, not arbitrary cutoffs
- **Posterior integration** — use full uncertainty for decisions, not point estimates
- **Value of information** — quantify whether more data would change your decision
- **Asymmetric losses** — different patients have different costs of error
- **Multi-action decisions** — choose among several interventions based on expected utility

Dr. Okafor: "So we should intervene on almost everyone?"

You: "With a 15:1 cost ratio, yes — the threshold is much lower than 25%. But we can be smarter: phone follow-up for moderate risk, home visits for high risk, nothing for very low risk. The model tells us which patients get which intervention."

The model works, the decisions are principled. Now: how do you get this out of a Jupyter notebook and into production?

---

[← Chapter 13: Causal Inference](chapter-13-causal.md) | [Chapter 15: Production →](chapter-15-production.md)
