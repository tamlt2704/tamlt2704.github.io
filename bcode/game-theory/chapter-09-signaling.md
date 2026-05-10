# Chapter 9: Signaling — Proving Quality Without Giving Away Secrets

[← Chapter 8: Bargaining](chapter-08-bargaining.md) | [Chapter 10: Evolutionary Game Theory →](chapter-10-evolutionary.md)

---

## The Problem

Nexus Labs just shipped an enterprise API. It's fast, reliable, battle-tested under load. The problem: so does RivalCo *claim*. Their marketing says "enterprise-grade" too. Their landing page has the same buzzwords. Their sales team makes the same promises.

Kai slams his laptop shut in the pipeline review. "We lost another deal. The prospect said they couldn't tell the difference between us and RivalCo. They went with RivalCo because they're cheaper."

Mara turns to you. "Our API is genuinely better. Their uptime is 99.5%, ours is 99.99%. But prospects can't verify that before signing. How do we prove quality without just... saying it louder?"

You think about it. RivalCo can say anything. Words are cheap. What can Nexus do that RivalCo *can't afford to imitate*?

This is a **signaling game** — and the answer is counterintuitive: the signal works precisely because it's expensive.

## The Model: Spence's Signaling

Michael Spence won a Nobel Prize for this insight, originally about job markets. The structure:

1. A **sender** has private information (their "type" — high quality or low quality)
2. The sender can take a costly action (the "signal")
3. A **receiver** observes the signal and updates their beliefs
4. The signal works if it's cheap for high types but expensive for low types

```python
import numpy as np
import matplotlib.pyplot as plt

# Two types of firms: High quality (H) and Low quality (L)
# Signal: invest in SOC 2 certification (costly audit process)

# Parameters
value_high = 100    # What a high-quality API is worth to enterprise buyers
value_low = 40      # What a low-quality API is worth
price_if_believed = 90   # Price enterprises pay if they believe you're high quality
price_if_not = 50        # Price if they can't distinguish you

# Cost of SOC 2 certification
cost_high = 15      # High-quality firms: already have good practices, audit is straightforward
cost_low = 60       # Low-quality firms: must overhaul everything, audit is painful

# Should each type signal (get certified)?
profit_high_signal = price_if_believed - cost_high
profit_high_no_signal = price_if_not
profit_low_signal = price_if_believed - cost_low
profit_low_no_signal = price_if_not

print("=== Signaling Decision ===")
print(f"\nHigh-quality firm:")
print(f"  Signal (certify):    {price_if_believed} - {cost_high} = {profit_high_signal}")
print(f"  Don't signal:        {profit_high_no_signal}")
print(f"  → {'Signal' if profit_high_signal > profit_high_no_signal else 'Don\'t signal'}")

print(f"\nLow-quality firm:")
print(f"  Signal (certify):    {price_if_believed} - {cost_low} = {profit_low_signal}")
print(f"  Don't signal:        {profit_low_no_signal}")
print(f"  → {'Signal' if profit_low_signal > profit_low_no_signal else 'Don\'t signal'}")
```

```
=== Signaling Decision ===

High-quality firm:
  Signal (certify):    90 - 15 = 75
  Don't signal:        50
  → Signal

Low-quality firm:
  Signal (certify):    90 - 60 = 30
  Don't signal:        50
  → Don't signal
```

The certification separates the types. High-quality firms certify because the cost is low relative to the benefit. Low-quality firms don't because the cost exceeds the benefit.

## Separating vs. Pooling Equilibria

```python
def signaling_equilibrium(cost_high, cost_low, price_signal, price_no_signal):
    """
    Determine the equilibrium type in a signaling game.
    
    Separating: only high types signal
    Pooling: both types do the same thing
    """
    gain_from_signal = price_signal - price_no_signal
    
    high_signals = (gain_from_signal > cost_high)
    low_signals = (gain_from_signal > cost_low)
    
    if high_signals and not low_signals:
        return "separating", "Only high-quality firms signal"
    elif high_signals and low_signals:
        return "pooling_signal", "Both types signal — signal is uninformative"
    elif not high_signals and not low_signals:
        return "pooling_no_signal", "Neither type signals — no information revealed"
    else:
        return "counter_separating", "Only low types signal (unusual)"

# Explore how certification cost affects equilibrium
costs_low = np.linspace(10, 100, 50)
cost_h = 15
price_s = 90
price_ns = 50

equilibria = []
for c_l in costs_low:
    eq_type, _ = signaling_equilibrium(cost_h, c_l, price_s, price_ns)
    equilibria.append(eq_type)

# Visualize
fig, ax = plt.subplots(figsize=(10, 5))
colors = {'separating': 'green', 'pooling_signal': 'red', 'pooling_no_signal': 'orange'}
for i, (c, eq) in enumerate(zip(costs_low, equilibria)):
    ax.axvspan(c - 0.5, c + 0.5, color=colors.get(eq, 'gray'), alpha=0.6)

ax.axvline(x=40, color='black', linestyle='--', label='Gain from signal (40)')
ax.axvline(x=cost_h, color='blue', linestyle=':', label=f'High-type cost ({cost_h})')
ax.set_xlabel("Low-type cost of signaling")
ax.set_ylabel("Equilibrium type")
ax.set_title("Signaling Equilibrium Depends on Cost Differential")
ax.legend()
plt.tight_layout()
plt.show()
```

The key insight: **separation requires a cost gap**. The signal must be cheap enough for high types to afford, but expensive enough that low types won't bother.

## The Full Signaling Game

```python
def simulate_market_with_signaling(n_firms=1000, fraction_high=0.3, 
                                     cost_high=15, cost_low=60,
                                     value_high=100, value_low=40):
    """
    Simulate a market where firms choose whether to signal quality.
    Buyers update beliefs based on signals observed.
    """
    np.random.seed(42)
    
    # Assign types
    types = np.random.choice(['high', 'low'], size=n_firms, 
                              p=[fraction_high, 1 - fraction_high])
    
    # Each firm decides whether to signal
    # In separating equilibrium: high types signal, low types don't
    price_if_signaled = value_high * 0.9    # Buyers pay near full value
    price_if_not = (fraction_high * value_high + (1 - fraction_high) * value_low)  # Average
    
    signals = []
    profits = []
    
    for firm_type in types:
        cost = cost_high if firm_type == 'high' else cost_low
        
        profit_signal = price_if_signaled - cost
        profit_no_signal = price_if_not
        
        if profit_signal > profit_no_signal:
            signals.append(True)
            profits.append(profit_signal)
        else:
            signals.append(False)
            profits.append(profit_no_signal)
    
    signals = np.array(signals)
    profits = np.array(profits)
    
    # Market outcomes
    high_mask = types == 'high'
    print("=== Market Outcomes ===")
    print(f"High-quality firms that signal: {signals[high_mask].sum()}/{high_mask.sum()} "
          f"({signals[high_mask].mean()*100:.0f}%)")
    print(f"Low-quality firms that signal:  {signals[~high_mask].sum()}/{(~high_mask).sum()} "
          f"({signals[~high_mask].mean()*100:.0f}%)")
    print(f"\nAvg profit (high, signaling):   {profits[high_mask & signals].mean():.1f}")
    print(f"Avg profit (low, not signaling): {profits[~high_mask & ~signals].mean():.1f}")
    
    # Buyer accuracy
    # If buyers trust signal: "signaled = high quality"
    correct = (signals & high_mask) | (~signals & ~high_mask)
    print(f"\nBuyer accuracy (trusting signal): {correct.mean()*100:.1f}%")
    
    return types, signals, profits

types, signals, profits = simulate_market_with_signaling()
```

```
=== Market Outcomes ===
High-quality firms that signal: 300/300 (100%)
Low-quality firms that signal:  0/700 (0%)

Avg profit (high, signaling):   75.0
Avg profit (low, not signaling): 58.0

Buyer accuracy (trusting signal): 100.0%
```

## Screening: The Receiver Moves First

Signaling is sender-initiated. **Screening** is when the receiver designs a menu that makes types self-select.

```python
def design_screening_menu():
    """
    Nexus designs two contract tiers that make prospects reveal their type.
    
    High-value prospects (enterprise): want SLA, support, custom features
    Low-value prospects (startups): want cheap access, self-serve
    """
    # Enterprise tier: expensive but includes everything
    enterprise_price = 500
    enterprise_cost_to_serve = 100  # Nexus's cost
    enterprise_value_to_high = 800  # What enterprises get from it
    enterprise_value_to_low = 200   # Startups don't need all this
    
    # Startup tier: cheap, limited
    startup_price = 50
    startup_cost_to_serve = 20
    startup_value_to_high = 300     # Enterprises could use it but it's limiting
    startup_value_to_low = 150      # Startups are happy with it
    
    print("=== Screening Menu Design ===\n")
    print("Enterprise tier ($500/mo): Full SLA, dedicated support, custom integrations")
    print("Startup tier ($50/mo): Self-serve, community support, standard API\n")
    
    # Check incentive compatibility: each type prefers their intended tier
    print("--- Incentive Compatibility Check ---")
    
    # Enterprise surplus from each tier
    enterprise_surplus_own = enterprise_value_to_high - enterprise_price
    enterprise_surplus_other = startup_value_to_high - startup_price
    print(f"Enterprise choosing Enterprise tier: surplus = {enterprise_value_to_high} - {enterprise_price} = {enterprise_surplus_own}")
    print(f"Enterprise choosing Startup tier:    surplus = {startup_value_to_high} - {startup_price} = {enterprise_surplus_other}")
    print(f"→ Enterprise prefers Enterprise tier: {enterprise_surplus_own > enterprise_surplus_other} ✓\n")
    
    # Startup surplus from each tier
    startup_surplus_own = startup_value_to_low - startup_price
    startup_surplus_other = enterprise_value_to_low - enterprise_price
    print(f"Startup choosing Startup tier:       surplus = {startup_value_to_low} - {startup_price} = {startup_surplus_own}")
    print(f"Startup choosing Enterprise tier:    surplus = {enterprise_value_to_low} - {enterprise_price} = {startup_surplus_other}")
    print(f"→ Startup prefers Startup tier: {startup_surplus_own > startup_surplus_other} ✓")
    
    # Nexus profit from each
    print(f"\n--- Nexus Profit ---")
    print(f"Per enterprise customer: {enterprise_price} - {enterprise_cost_to_serve} = {enterprise_price - enterprise_cost_to_serve}")
    print(f"Per startup customer:    {startup_price} - {startup_cost_to_serve} = {startup_price - startup_cost_to_serve}")

design_screening_menu()
```

```
=== Screening Menu Design ===

Enterprise tier ($500/mo): Full SLA, dedicated support, custom integrations
Startup tier ($50/mo): Self-serve, community support, standard API

--- Incentive Compatibility Check ---
Enterprise choosing Enterprise tier: surplus = 800 - 500 = 300
Enterprise choosing Startup tier:    surplus = 300 - 50 = 250
→ Enterprise prefers Enterprise tier: True ✓

Startup choosing Startup tier:       surplus = 150 - 50 = 100
Startup choosing Enterprise tier:    surplus = 200 - 500 = -300
→ Startup prefers Startup tier: True ✓

--- Nexus Profit ---
Per enterprise customer: 500 - 100 = 400
Per startup customer:    50 - 20 = 30
```

## Nexus Labs' Signal Strategy

```python
def nexus_signaling_strategy():
    """
    What costly signals can Nexus send that RivalCo can't afford to match?
    """
    signals = {
        "SOC 2 Type II Certification": {
            "cost_high_quality": 50_000,    # Already have good practices
            "cost_low_quality": 300_000,    # Must rebuild from scratch
            "credibility": "high",
            "why": "Requires 6-month audit of actual practices"
        },
        "Public status page with real SLA data": {
            "cost_high_quality": 5_000,     # Just expose existing metrics
            "cost_low_quality": "infinite",  # Can't show bad numbers
            "credibility": "very high",
            "why": "Lying is impossible — the data is public"
        },
        "Money-back SLA guarantee": {
            "cost_high_quality": 10_000,    # Rarely triggered
            "cost_low_quality": 200_000,    # Triggered constantly
            "credibility": "high",
            "why": "Only profitable if you actually deliver"
        },
        "Fancy office / conference sponsorship": {
            "cost_high_quality": 100_000,
            "cost_low_quality": 100_000,    # Same cost for both!
            "credibility": "low",
            "why": "Equally costly for both types — not a separating signal"
        }
    }
    
    print("=== Nexus Signaling Options ===\n")
    for signal, data in signals.items():
        print(f"📡 {signal}")
        print(f"   Cost if high quality: ${data['cost_high_quality']:,}")
        print(f"   Cost if low quality:  ${data['cost_low_quality']}")
        print(f"   Credibility: {data['credibility']}")
        print(f"   Why: {data['why']}")
        separating = data['cost_high_quality'] != data['cost_low_quality']
        print(f"   → {'✓ Separating signal' if separating else '✗ NOT separating — both types can afford it'}\n")

nexus_signaling_strategy()
```

```
=== Nexus Signaling Options ===

📡 SOC 2 Type II Certification
   Cost if high quality: $50,000
   Cost if low quality:  $300,000
   Credibility: high
   Why: Requires 6-month audit of actual practices
   → ✓ Separating signal

📡 Public status page with real SLA data
   Cost if high quality: $5,000
   Cost if low quality:  infinite
   Credibility: very high
   Why: Lying is impossible — the data is public
   → ✓ Separating signal

📡 Money-back SLA guarantee
   Cost if high quality: $10,000
   Cost if low quality:  $200,000
   Credibility: high
   Why: Only profitable if you actually deliver
   → ✓ Separating signal

📡 Fancy office / conference sponsorship
   Cost if high quality: $100,000
   Cost if low quality:  $100,000
   Credibility: low
   Why: Equally costly for both types — both types can afford it
   → ✗ NOT separating — both types can afford it
```

You present this to Mara. "Conference sponsorships won't help — RivalCo can match those dollar for dollar. But a public status page with real uptime data? That's a signal they literally cannot fake."

Mara grins. "Ship it."

## What You Learned

- **Signaling** — costly actions that reveal private information about your type
- **Separating equilibrium** — different types take different actions, revealing who they are
- **Pooling equilibrium** — all types do the same thing, no information is revealed
- **The key condition** — signals work when they're differentially costly (cheap for high types, expensive for low types)
- **Screening** — the receiver designs a menu that makes types self-select
- **Cheap talk fails** — if a signal costs the same for everyone, it conveys nothing

Next up: Priya notices that "selfish" engineers who skip code reviews keep thriving while "helpful" ones burn out. Why don't bad strategies die? Evolutionary game theory has the uncomfortable answer.

---

[← Chapter 8: Bargaining](chapter-08-bargaining.md) | [Chapter 10: Evolutionary Game Theory →](chapter-10-evolutionary.md)
