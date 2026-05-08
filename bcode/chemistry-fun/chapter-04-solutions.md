# Chapter 4: Mixing and Dissolving — Solutions & Solubility

[← Chapter 3: Periodic Table](chapter-03-periodic-table.md) | [Chapter 5: Eruptions →](chapter-05-reactions.md)

---

## The Kit Idea

MoleCraft's fourth product: **Color-Changing Drinks**. Kids mix powders into water and watch the liquid shift colors as concentration changes. A "magic lemonade" that turns from clear to deep purple as you add more powder.

Dr. Kenji: "It's basically a solubility and concentration demo disguised as a party trick."

## The Failed Prototype

You design the kit with three colored powders. Beta testers dump all the powder in at once.

**What goes wrong:** The powder sits at the bottom in a soggy lump. No color change — just a murky mess. One tester heats the water and suddenly it dissolves, but when it cools, crystals form on the spoon.

Sam (safety officer): "Also, one kid tried to dissolve powder in oil instead of water. Nothing happened. They said the kit was broken."

The problem: you never explained *why* things dissolve, *how much* can dissolve, or *what affects it*.

## Solutions: The Chemistry of Mixing

A **solution** has two parts:

| Term | Role | Example |
|------|------|---------|
| **Solvent** | Does the dissolving (larger amount) | Water |
| **Solute** | Gets dissolved (smaller amount) | Sugar, salt, powder |

**"Like dissolves like"** — the golden rule:
- Polar solvents (water) dissolve polar/ionic solutes (salt, sugar)
- Nonpolar solvents (oil) dissolve nonpolar solutes (grease, wax)

That's why the powder wouldn't dissolve in oil — it's a polar solute in a nonpolar solvent.

## Concentration and Molarity

**Concentration** = how much solute is in a given amount of solution.

**Molarity (M)** = moles of solute per liter of solution:

```
M = moles of solute / liters of solution
```

One mole = 6.022 × 10²³ particles (Avogadro's number).

```python
def molarity(mass_grams, molar_mass, volume_liters):
    """Calculate molarity from mass, molar mass, and volume."""
    moles = mass_grams / molar_mass
    return moles / volume_liters

# Example: dissolve 58.4g NaCl (molar mass 58.4) in 1L water
m = molarity(58.4, 58.4, 1.0)
print(f"NaCl molarity: {m:.2f} M")  # 1.00 M

# Kit example: 10g of color powder (molar mass ~200) in 0.5L
m_kit = molarity(10, 200, 0.5)
print(f"Kit powder molarity: {m_kit:.2f} M")  # 0.10 M
```

## Saturation: The Dissolving Limit

Every solute has a **solubility limit** — the max amount that dissolves at a given temperature.

| State | Meaning |
|-------|---------|
| **Unsaturated** | More solute can still dissolve |
| **Saturated** | Maximum dissolved — no more will dissolve |
| **Supersaturated** | More than max dissolved (unstable!) |

```python
import random

def dissolving_simulation(solubility_limit, amount_added, temp_factor=1.0):
    """Simulate dissolving with a solubility limit."""
    effective_limit = solubility_limit * temp_factor
    dissolved = min(amount_added, effective_limit)
    undissolved = max(0, amount_added - effective_limit)
    
    if amount_added < effective_limit * 0.9:
        state = "Unsaturated"
    elif amount_added <= effective_limit:
        state = "Saturated"
    else:
        state = "Supersaturated (crystals forming!)"
    
    return dissolved, undissolved, state

# At room temp: solubility = 36g per 100mL
# Beta tester dumps 60g into 100mL
dissolved, leftover, state = dissolving_simulation(36, 60)
print(f"Dissolved: {dissolved}g | Leftover: {leftover}g | State: {state}")
# Dissolved: 36g | Leftover: 24g | State: Supersaturated (crystals forming!)

# Heat it up (temp_factor increases solubility)
dissolved, leftover, state = dissolving_simulation(36, 60, temp_factor=2.0)
print(f"Hot water — Dissolved: {dissolved}g | Leftover: {leftover}g | State: {state}")
# Dissolved: 60g | Leftover: 0g | State: Unsaturated
```

## Temperature and Solubility

Most solids dissolve **more** in hot water (molecules move faster, break apart solute).

```
Solubility
(g/100mL)
    │
 80 │              ╱ KNO₃
    │            ╱
 60 │          ╱
    │        ╱
 40 │      ╱
    │    ╱───────────── NaCl (barely changes!)
 20 │  ╱
    │╱
  0 ├──────────────────── Temperature (°C)
    0    20   40   60   80
```

This explains the beta tester's experience: hot water dissolved everything, but cooling made it supersaturated → crystals crashed out.

## The "Whoa" Moment: Instant Crystallization

A **supersaturated** solution is unstable. Drop in one tiny seed crystal and — WHOOSH — the entire solution crystallizes instantly. It's like a chain reaction of molecules snapping into place.

The kit's grand finale: kids make a supersaturated solution, cool it carefully, then drop in a single crystal. Instant crystal tower grows before their eyes.

## The Working Kit Design

1. **Powder A** (high solubility) — dissolves easily, light color
2. **Powder B** (medium solubility) — color deepens as you add more
3. **Powder C** (low solubility) — shows saturation limit visually (excess sits at bottom)
4. **Temperature card** — shows kids to try warm vs cold water
5. **Seed crystal** — for the supersaturation finale

Color intensity = concentration. Kids can *see* molarity.

## What You Learned

- **Solutions** = solvent + solute; "like dissolves like"
- **Molarity** = moles/liter, the chemist's unit of concentration
- **Saturation** = the dissolving limit at a given temperature
- **Temperature** increases solubility for most solids
- **Supersaturation** = unstable state that crystallizes on disturbance
- Color intensity is a visual proxy for concentration

Next up: what happens when dissolved chemicals actually *react* with each other? Time for the volcano kit.

---

[← Chapter 3: Periodic Table](chapter-03-periodic-table.md) | [Chapter 5: Eruptions →](chapter-05-reactions.md)
