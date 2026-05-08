# Chapter 5: Eruptions — Chemical Reactions & Equations

[← Chapter 4: Solutions](chapter-04-solutions.md) | [Chapter 6: Speed Control →](chapter-06-kinetics.md)

---

## The Kit Idea

MoleCraft's fifth product: **The Ultimate Volcano Kit**. Not the boring baking-soda-and-vinegar volcano from every science fair — a *real* chemistry volcano with multiple eruption styles, colored lava, and actual gas production kids can measure.

Dr. Kenji: "Every kid has done the vinegar volcano. Ours needs to teach *why* it works and what's actually happening at the molecular level."

## The Failed Prototype

You design a volcano with three "eruption modes" using different chemical packets. Beta testers mix packet A with packet B and get... a sad fizz. They expected an explosion.

**What goes wrong:** The ratios are off. Too much of one reactant, not enough of the other. One eruption produces so much gas the volcano lid pops off and hits the ceiling. Another produces a weird smell because you used the wrong type of reaction.

Sam: "We need to know *exactly* how much of each chemical reacts. No guessing."

The fix requires understanding chemical equations and balancing them.

## Chemical Equations: The Recipe

A chemical equation is a recipe showing what goes in and what comes out:

```
Reactants  →  Products

CH₄ + 2O₂  →  CO₂ + 2H₂O
(methane + oxygen → carbon dioxide + water)
```

The arrow means "reacts to form." The numbers in front (coefficients) tell you the ratio.

## Balancing: Atoms In = Atoms Out

Atoms aren't created or destroyed (conservation of mass). Both sides must have the same count:

```
UNBALANCED:  H₂ + O₂ → H₂O
             (2H + 2O → 2H + 1O)  ← oxygen doesn't match!

BALANCED:    2H₂ + O₂ → 2H₂O
             (4H + 2O → 4H + 2O)  ✓
```

```python
def check_balanced(equation_str, element_counts_left, element_counts_right):
    """Check if a chemical equation is balanced."""
    print(f"Equation: {equation_str}")
    balanced = True
    for element in element_counts_left:
        left = element_counts_left[element]
        right = element_counts_right.get(element, 0)
        status = "✓" if left == right else "✗"
        if left != right:
            balanced = False
        print(f"  {element}: {left} left, {right} right {status}")
    return balanced

# The volcano reaction: baking soda + vinegar
# NaHCO₃ + CH₃COOH → NaCH₃COO + H₂O + CO₂
check_balanced(
    "NaHCO₃ + CH₃COOH → NaCH₃COO + H₂O + CO₂",
    {"Na": 1, "H": 5, "C": 3, "O": 5},
    {"Na": 1, "H": 5, "C": 3, "O": 5}
)
# All balanced ✓
```

## Types of Reactions

The volcano kit uses different reaction types for different eruption modes:

| Type | Pattern | Kit Use |
|------|---------|---------|
| **Synthesis** | A + B → AB | Building calciumite crystals |
| **Decomposition** | AB → A + B | Hydrogen peroxide → oxygen gas |
| **Single replacement** | A + BC → AC + B | Zinc + acid → hydrogen gas |
| **Double replacement** | AB + CD → AD + CB | Baking soda + vinegar |
| **Combustion** | Fuel + O₂ → CO₂ + H₂O | (Demo only — Dr. Kenji does this one) |

```python
def classify_reaction(reactants, products):
    """Classify a reaction by type."""
    r_count = len(reactants)
    p_count = len(products)
    
    if r_count == 2 and p_count == 1:
        return "Synthesis (A + B → AB)"
    elif r_count == 1 and p_count == 2:
        return "Decomposition (AB → A + B)"
    elif r_count == 2 and p_count == 2:
        # Check if elements swapped
        return "Double Replacement (AB + CD → AD + CB)"
    elif r_count == 2 and p_count >= 2:
        return "Single Replacement or Combustion"
    else:
        return "Complex reaction"

# Volcano eruption mode 1: decomposition
print(classify_reaction(["H₂O₂"], ["H₂O", "O₂"]))
# Decomposition (AB → A + B)

# Volcano eruption mode 2: double replacement (acid-base)
print(classify_reaction(["NaHCO₃", "CH₃COOH"], ["NaCH₃COO", "H₂O + CO₂"]))
# Double Replacement
```

## Stoichiometry: Getting the Ratios Right

**Stoichiometry** = using the balanced equation to calculate exact amounts.

The volcano failed because the ratios were wrong. Here's how to fix it:

```python
def volcano_stoichiometry(grams_baking_soda):
    """Calculate how much vinegar needed for baking soda volcano."""
    # NaHCO₃ + CH₃COOH → NaCH₃COO + H₂O + CO₂
    # Molar masses: NaHCO₃ = 84, CH₃COOH = 60, CO₂ = 44
    
    moles_soda = grams_baking_soda / 84
    moles_vinegar_needed = moles_soda  # 1:1 ratio from equation
    grams_vinegar = moles_vinegar_needed * 60
    
    # Vinegar is ~5% acetic acid
    mL_vinegar = (grams_vinegar / 0.05) / 1.0  # density ~1 g/mL
    
    # CO₂ produced
    moles_co2 = moles_soda  # 1:1 ratio
    liters_co2 = moles_co2 * 22.4  # at STP
    
    print(f"Baking soda: {grams_baking_soda}g")
    print(f"Vinegar needed: {mL_vinegar:.0f} mL")
    print(f"CO₂ produced: {liters_co2:.2f} L")
    print(f"That's {liters_co2 * 1000:.0f} mL of gas — enough to inflate a balloon!")
    return mL_vinegar, liters_co2

volcano_stoichiometry(10)  # 10g baking soda
```

## The "Whoa" Moment: The Elephant Toothpaste Eruption

Eruption mode 3 uses **decomposition** of hydrogen peroxide with a catalyst:

```
2H₂O₂ → 2H₂O + O₂ (with MnO₂ catalyst)
```

The oxygen gas gets trapped in soap, creating a massive foam eruption that looks like a giant tube of toothpaste being squeezed. The balanced equation predicts exactly how much foam you'll get.

Kids measure the foam volume and compare it to the predicted O₂ volume from stoichiometry. Chemistry becomes *testable*.

## The Working Volcano Kit

Three eruption modes, each a different reaction type:

1. **Classic fizz** (double replacement) — baking soda + citric acid → CO₂
2. **Foam eruption** (decomposition) — H₂O₂ + catalyst → O₂ foam
3. **Color change** (single replacement) — metal + acid → hydrogen + color shift

Each packet is pre-measured using stoichiometry. No more ceiling hits.

## What You Learned

- **Chemical equations** show reactants → products
- **Balancing** ensures atoms in = atoms out (conservation of mass)
- **Reaction types**: synthesis, decomposition, single/double replacement, combustion
- **Stoichiometry** = using ratios to calculate exact amounts
- **Coefficients** are the recipe — get them wrong and the reaction fails (or explodes)

The volcano works perfectly now. But beta testers ask: "Can we make it erupt *faster*?" That's reaction kinetics — next chapter.

---

[← Chapter 4: Solutions](chapter-04-solutions.md) | [Chapter 6: Speed Control →](chapter-06-kinetics.md)
