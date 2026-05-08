# Chapter 6: Speed Control — Reaction Kinetics

[← Chapter 5: Reactions](chapter-05-reactions.md) | [Chapter 7: Heat →](chapter-07-thermochemistry.md)

---

## The Kit Idea

MoleCraft's sixth product: **Glow Stick Hacking**. Kids crack glow sticks and experiment with making them glow brighter, dimmer, longer, or shorter. They learn to control reaction speed by changing conditions.

Dr. Kenji: "A glow stick is a chemical reaction you can see in real time. Change the speed, change the glow."

## The Failed Prototype

You ship glow sticks with instructions: "Crack and observe for 30 minutes." Beta testers get bored after 5 minutes of dim glow.

**What goes wrong:** One tester puts a glow stick in hot water — it blazes bright but dies in 3 minutes. Another puts one in the freezer — it barely glows but lasts all night. A third tester crushes the stick into tiny pieces and it flares up instantly.

Sam: "Nobody followed the instructions. But honestly, their experiments were more interesting than ours."

You realize: the *hacking* is the lesson. Kids need to understand what controls reaction speed.

## Reaction Rate: How Fast Chemistry Happens

**Reaction rate** = how quickly reactants turn into products.

```
Rate = Change in concentration / Change in time
```

Some reactions are fast (explosions: microseconds), some are slow (rusting: years).

## Factors That Affect Rate

| Factor | Effect | Glow Stick Example |
|--------|--------|-------------------|
| **Temperature** | Higher = faster | Hot water → bright but short |
| **Concentration** | Higher = faster | Fresh stick > old stick |
| **Surface area** | More = faster | Crushed stick flares up |
| **Catalyst** | Lowers energy barrier | (Used in next kit) |

```python
import math

def glow_intensity(temp_celsius, time_minutes, initial_concentration=1.0):
    """Model glow stick intensity based on temperature and time."""
    # Arrhenius-inspired: rate doubles roughly every 10°C
    rate_multiplier = 2 ** ((temp_celsius - 25) / 10)
    
    # First-order decay of reactant
    k = 0.01 * rate_multiplier  # rate constant
    concentration = initial_concentration * math.exp(-k * time_minutes)
    
    # Intensity proportional to rate of reaction
    intensity = k * concentration
    return intensity, concentration

# Compare hot vs cold vs room temp
temps = [5, 25, 50]
print("Glow intensity over time:")
print(f"{'Time':>5} | {'5°C (freezer)':>13} | {'25°C (room)':>11} | {'50°C (hot)':>10}")
print("-" * 50)

for t in [0, 5, 10, 20, 30, 60]:
    values = []
    for temp in temps:
        intensity, _ = glow_intensity(temp, t)
        bar = "█" * int(intensity * 50)
        values.append(f"{intensity:.3f}")
    print(f"{t:>4}m | {values[0]:>13} | {values[1]:>11} | {values[2]:>10}")
```

```
Glow intensity over time:
 Time |  5°C (freezer) |   25°C (room) |  50°C (hot)
--------------------------------------------------
   0m |         0.003  |        0.010  |      0.057
   5m |         0.002  |        0.010  |      0.041
  10m |         0.002  |        0.009  |      0.030
  20m |         0.002  |        0.008  |      0.016
  30m |         0.002  |        0.007  |      0.008
  60m |         0.002  |        0.005  |      0.002
```

Hot = bright but short. Cold = dim but long. Same total light, different distribution.

## Activation Energy: The Hill to Climb

Every reaction needs a minimum energy to start — the **activation energy (Eₐ)**.

```
Energy
  │
  │      ╱╲  ← Activation energy (Eₐ)
  │     ╱  ╲
  │    ╱    ╲
  │───╱      ╲
  │  Reactants ╲───── Products
  │              (energy released)
  └──────────────────────── Reaction progress
```

- **Higher Eₐ** = harder to start (need more energy)
- **Lower Eₐ** = easier to start

Cracking the glow stick breaks an inner vial, mixing chemicals that overcome Eₐ.

## Catalysts: Cheating the Energy Hill

A **catalyst** lowers the activation energy without being consumed:

```
Energy
  │
  │      ╱╲  Without catalyst
  │     ╱  ╲
  │    ╱ ╱╲ ╲  ← With catalyst (lower hill!)
  │───╱─╱  ╲─╲───── Products
  │  Reactants
  └──────────────────────── Reaction progress
```

```python
def time_to_complete(activation_energy, temperature_c):
    """Estimate relative reaction time using Arrhenius equation."""
    # Simplified Arrhenius: k = A * exp(-Ea / RT)
    R = 8.314  # J/(mol·K)
    T = temperature_c + 273.15
    A = 1e10  # pre-exponential factor (simplified)
    
    k = A * math.exp(-activation_energy / (R * T))
    time = 1 / k  # relative time (arbitrary units)
    return time

# Without catalyst: Ea = 75,000 J/mol
# With catalyst: Ea = 50,000 J/mol
t_no_cat = time_to_complete(75000, 25)
t_with_cat = time_to_complete(50000, 25)

print(f"Without catalyst: {t_no_cat:.2e} time units")
print(f"With catalyst:    {t_with_cat:.2e} time units")
print(f"Catalyst makes it {t_no_cat / t_with_cat:.0f}x faster!")
```

## The Collision Theory

For a reaction to happen, molecules must:
1. **Collide** (meet each other)
2. With enough **energy** (≥ activation energy)
3. In the right **orientation** (hit the reactive spot)

This explains all the factors:
- **Temperature** → molecules move faster → more energetic collisions
- **Concentration** → more molecules → more collisions
- **Surface area** → more exposed molecules → more collision opportunities
- **Catalyst** → lowers the energy needed → more collisions succeed

## The "Whoa" Moment: The Freeze-and-Revive Trick

Put a glowing stick in the freezer. It goes nearly dark. Pull it out hours later, warm it up — it glows again! The reaction didn't stop, it just slowed to a crawl. The reactants are still there, waiting.

Kids realize: **you can pause chemistry with temperature**. This is how food preservation works, how cryogenics works, how life slows down in winter.

## The Working Kit Design

The Glow Stick Hacking kit includes:
1. **6 glow sticks** (same chemistry, different experiments)
2. **Temperature challenge** — hot water, ice water, room temp comparison
3. **Timer card** — record brightness vs. time at each temperature
4. **Graph paper** — plot decay curves
5. **Catalyst demo** — a separate vial that speeds up a color-change reaction

Kids discover the rules themselves, then the manual explains the science.

## What You Learned

- **Reaction rate** = how fast reactants become products
- **Temperature, concentration, surface area, catalysts** all affect rate
- **Activation energy** = minimum energy needed to start a reaction
- **Catalysts** lower activation energy (speed up without being consumed)
- **Collision theory** explains why these factors matter
- You can **control** reactions by controlling conditions

The glow sticks show speed. But beta testers notice: "The hot water glow stick made the water warm. Where did that heat come from?" That's thermochemistry.

---

[← Chapter 5: Reactions](chapter-05-reactions.md) | [Chapter 7: Heat →](chapter-07-thermochemistry.md)
