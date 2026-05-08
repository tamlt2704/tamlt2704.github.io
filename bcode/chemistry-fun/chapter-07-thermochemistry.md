# Chapter 7: Heat — Thermochemistry

[← Chapter 6: Kinetics](chapter-06-kinetics.md) | [Chapter 8: Acids & Bases →](chapter-08-ph.md)

---

## The Kit Idea

MoleCraft's seventh product: **Design Your Own Hand Warmer**. Kids mix chemicals in a sealed pouch and create a hand warmer that heats up on demand. They experiment with different mixtures to control temperature and duration.

Dr. Kenji: "Every chemical reaction either releases heat or absorbs it. Hand warmers are exothermic reactions you can hold in your palm."

## The Failed Prototype

You design a kit with iron powder, salt, and water in a pouch. Beta testers activate it and...

**What goes wrong:** The first batch gets dangerously hot — one tester drops it yelping "OW!" (65°C). The second batch barely warms up. A third tester makes a "cold pack" by accident using the wrong chemicals and their hands get *colder*.

Sam: "We need to predict the temperature BEFORE kids touch it. This is a safety issue."

The problem: you didn't calculate how much heat the reaction produces or how to control it.

## Exothermic vs. Endothermic

Every reaction either releases or absorbs energy:

| Type | Energy Flow | Feels Like | Sign |
|------|-------------|------------|------|
| **Exothermic** | Energy OUT → surroundings | Hot | ΔH < 0 (negative) |
| **Endothermic** | Energy IN ← surroundings | Cold | ΔH > 0 (positive) |

```
EXOTHERMIC                    ENDOTHERMIC
Energy                        Energy
  │                             │
  │── Reactants                 │         ── Products
  │         ╲                   │        ╱
  │          ╲  heat OUT →      │       ╱  ← heat IN
  │           ╲                 │      ╱
  │            ── Products      │── Reactants
  └─────────────────            └─────────────────
```

Hand warmer = exothermic. Cold pack = endothermic. Same kit, opposite chemistry.

## Enthalpy (ΔH): Measuring Heat

**Enthalpy change (ΔH)** = heat released or absorbed at constant pressure.

```
ΔH = H_products - H_reactants
```

- Negative ΔH → exothermic (products have less energy, difference released as heat)
- Positive ΔH → endothermic (products have more energy, absorbed from surroundings)

```python
# Common reactions and their enthalpy changes
reactions = {
    "Iron oxidation (hand warmer)": -826,    # kJ/mol
    "Dissolving NH₄NO₃ (cold pack)": +25.7,  # kJ/mol
    "Combustion of methane": -890,            # kJ/mol
    "Photosynthesis": +2803,                  # kJ/mol (per glucose)
    "Neutralization (acid+base)": -57,        # kJ/mol
}

print("Reaction Enthalpy Values:")
print("-" * 55)
for reaction, dh in reactions.items():
    rtype = "EXOTHERMIC 🔥" if dh < 0 else "ENDOTHERMIC ❄️"
    print(f"  {reaction:35s} ΔH = {dh:>+7.1f} kJ/mol  {rtype}")
```

## Calorimetry: Measuring Heat in Practice

A **calorimeter** measures heat by tracking temperature change in water:

```
q = m × c × ΔT

q = heat (joules)
m = mass of water (grams)
c = specific heat capacity (4.184 J/g·°C for water)
ΔT = temperature change (°C)
```

```python
def calorimeter(mass_water_g, temp_initial, temp_final):
    """Calculate heat from calorimetry data."""
    c_water = 4.184  # J/(g·°C)
    delta_t = temp_final - temp_initial
    q = mass_water_g * c_water * delta_t
    
    print(f"Water mass: {mass_water_g}g")
    print(f"Temp change: {temp_initial}°C → {temp_final}°C (ΔT = {delta_t}°C)")
    print(f"Heat {'released' if q < 0 else 'absorbed'}: {abs(q):.1f} J ({abs(q)/1000:.2f} kJ)")
    return q

# Beta tester's too-hot hand warmer:
# 100g water equivalent, heated from 20°C to 65°C
print("=== Too-hot prototype ===")
calorimeter(100, 20, 65)

print("\n=== Properly designed warmer ===")
# Target: 20°C → 40°C (comfortable warmth)
calorimeter(100, 20, 40)
```

## Designing the Safe Hand Warmer

```python
def design_hand_warmer(target_temp, ambient_temp, mass_pouch_g):
    """Calculate how much iron powder needed for target temperature."""
    c_pouch = 3.5  # approximate specific heat of pouch contents (J/g·°C)
    delta_t = target_temp - ambient_temp
    
    # Heat needed
    q_needed = mass_pouch_g * c_pouch * delta_t  # joules
    
    # Iron oxidation: 4Fe + 3O₂ → 2Fe₂O₃, ΔH = -1648 kJ per 4 mol Fe
    # Per gram of Fe (molar mass 55.85): -1648000 / (4 * 55.85) = -7375 J/g
    heat_per_gram_fe = 7375  # J/g
    
    grams_iron = q_needed / heat_per_gram_fe
    
    print(f"Target: {ambient_temp}°C → {target_temp}°C")
    print(f"Pouch mass: {mass_pouch_g}g")
    print(f"Heat needed: {q_needed:.0f} J")
    print(f"Iron powder needed: {grams_iron:.1f}g")
    print(f"Safety margin: use {grams_iron * 0.8:.1f}g (80% for heat loss)")
    return grams_iron

design_hand_warmer(target_temp=40, ambient_temp=20, mass_pouch_g=50)
```

## The "Whoa" Moment: Instant Hot Ice

Sodium acetate supersaturated solution: pour it out and it crystallizes instantly, releasing heat. The liquid turns to warm "ice" in seconds. It's exothermic crystallization — the reverse of dissolving.

Kids can trigger it by touching the liquid with a crystal seed. The tower of warm crystals grows in their hands. Reusable by reheating to dissolve again.

## The Working Kit Design

1. **Iron-based warmer** — pre-measured iron, salt, vermiculite, activated charcoal
2. **Cold pack** — ammonium nitrate + water (endothermic dissolving)
3. **Thermometer strip** — color-changing temperature indicator on the pouch
4. **Design card** — calculate your own ratios for different temperatures
5. **Hot ice demo** — sodium acetate for the crystallization finale

Kids learn: chemistry isn't just about *what* forms, but *how much energy* moves.

## What You Learned

- **Exothermic** reactions release heat (ΔH negative) — hand warmers, combustion
- **Endothermic** reactions absorb heat (ΔH positive) — cold packs, photosynthesis
- **Enthalpy (ΔH)** quantifies heat flow in a reaction
- **Calorimetry** (q = mcΔT) measures heat experimentally
- **Designing** a safe product means calculating heat output before building

The hand warmer works. But a beta tester asks: "What if I mix the wrong chemicals and make something acidic? How do I know if it's dangerous?" Time for pH.

---

[← Chapter 6: Kinetics](chapter-06-kinetics.md) | [Chapter 8: Acids & Bases →](chapter-08-ph.md)
