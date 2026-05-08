# Chapter 11: Carbon Chemistry — Organic Intro

[← Chapter 10: Redox](chapter-10-redox.md) | [Chapter 12: The Nucleus →](chapter-12-nuclear.md)

---

## The Kit Idea

MoleCraft's eleventh product: **Soap Making Lab**. Kids make their own soap from oils and lye, learning why soap cleans things — and why carbon is the backbone of life's chemistry.

Dr. Kenji: "Organic chemistry sounds scary, but it's just carbon playing LEGO. And soap is the perfect first project — it's a molecule with a split personality."

## The Failed Prototype

You design the kit with coconut oil, sodium hydroxide (lye), and molds. Beta testers follow the recipe.

**What goes wrong:** One batch never solidifies — too much oil, not enough lye. Another batch is caustic and burns skin — too much lye, unreacted. A third tester asks "Why does soap clean grease if it's *made* from grease?" and you can't explain it clearly.

Sam: "Lye is dangerous. We need kids to understand the reaction completely before they touch it. And we need exact ratios."

The problem: soap making is a chemical reaction (saponification), and without understanding organic molecules, the ratios and the cleaning mechanism make no sense.

## Why Carbon Is Special

Carbon forms the backbone of organic molecules because it can:
- Make **4 bonds** (versatile connector)
- Bond to **itself** (chains, rings, branches)
- Form **single, double, and triple** bonds

```
Carbon bonding:

  H   H   H   H          H   H         H
  │   │   │   │          │   │         │
─ C ─ C ─ C ─ C ─    ─ C ═ C ─     ─ C ≡ C ─
  │   │   │   │          │   │         │
  H   H   H   H          H   H         H

  (single bonds)      (double bond)  (triple bond)
   Butane              Ethene         Ethyne
```

## Hydrocarbons: Carbon + Hydrogen

The simplest organic molecules — just C and H:

| Name | Formula | Structure | Type |
|------|---------|-----------|------|
| Methane | CH₄ | Single C, 4 H | Alkane |
| Ethane | C₂H₆ | C-C chain | Alkane |
| Propane | C₃H₈ | C-C-C chain | Alkane |
| Ethene | C₂H₄ | C=C double bond | Alkene |
| Ethyne | C₂H₂ | C≡C triple bond | Alkyne |

```python
def hydrocarbon_formula(carbons, bond_type="single"):
    """Calculate hydrogen count for a hydrocarbon."""
    if bond_type == "single":    # Alkane: CₙH₂ₙ₊₂
        hydrogens = 2 * carbons + 2
        suffix = "ane"
    elif bond_type == "double":  # Alkene: CₙH₂ₙ
        hydrogens = 2 * carbons
        suffix = "ene"
    elif bond_type == "triple":  # Alkyne: CₙH₂ₙ₋₂
        hydrogens = 2 * carbons - 2
        suffix = "yne"
    
    prefixes = {1: "meth", 2: "eth", 3: "prop", 4: "but",
                5: "pent", 6: "hex", 7: "hept", 8: "oct"}
    name = prefixes.get(carbons, f"C{carbons}") + suffix
    
    print(f"  {name}: C{carbons}H{hydrogens}")
    return f"C{carbons}H{hydrogens}"

print("Alkanes (single bonds):")
for c in range(1, 7):
    hydrocarbon_formula(c, "single")
```

## Functional Groups: Carbon's Accessories

What makes organic molecules *do* different things are **functional groups** — specific atom clusters attached to the carbon chain:

| Group | Structure | Found In | Properties |
|-------|-----------|----------|------------|
| **Hydroxyl** (-OH) | C-OH | Alcohols | Dissolves in water |
| **Carboxyl** (-COOH) | C(=O)OH | Acids, vinegar | Acidic, sour |
| **Ester** (-COO-) | C(=O)O-C | Fats, oils, fragrances | Slippery |
| **Amine** (-NH₂) | C-NH₂ | Proteins | Basic, fishy smell |

## Saponification: Making Soap

Soap is made by reacting a **fat** (ester) with a **base** (NaOH):

```
Fat (triglyceride) + 3 NaOH → 3 Soap molecules + Glycerol

    O                           O
    ‖                           ‖
R ─ C ─ O ─ (glycerol)  →  R ─ C ─ O⁻ Na⁺  +  glycerol
    (fat/oil)                   (soap)
```

```python
def saponification_ratio(oil_type):
    """Calculate NaOH needed for different oils (SAP values)."""
    # SAP value = mg KOH per gram of oil (converted to NaOH)
    sap_values = {
        "coconut oil": 0.178,     # grams NaOH per gram oil
        "olive oil": 0.134,
        "palm oil": 0.141,
        "castor oil": 0.128,
    }
    
    sap = sap_values.get(oil_type, 0.14)
    
    # For 100g of oil:
    oil_grams = 100
    naoh_grams = oil_grams * sap
    water_grams = naoh_grams * 2.3  # typical water ratio
    
    print(f"Oil: {oil_grams}g {oil_type}")
    print(f"NaOH needed: {naoh_grams:.1f}g")
    print(f"Water: {water_grams:.1f}g")
    print(f"Expected soap: ~{oil_grams + naoh_grams:.0f}g")
    
    # Safety: 5% superfat (use slightly less lye)
    safe_naoh = naoh_grams * 0.95
    print(f"Safe amount (5% superfat): {safe_naoh:.1f}g NaOH")
    return safe_naoh

print("=== Soap Recipe Calculator ===\n")
saponification_ratio("coconut oil")
print()
saponification_ratio("olive oil")
```

## Why Soap Cleans: The Split Personality

A soap molecule has two ends:

```
Hydrophilic          Hydrophobic
(loves water)        (loves grease)
                     
  O⁻ Na⁺            CH₂─CH₂─CH₂─CH₂─CH₂─CH₂─...
  │                  (long carbon tail)
  C═O
  │
  ─── polar head ─── ──────── nonpolar tail ──────────
```

In water with grease:
1. Tails stab into grease (like dissolves like)
2. Heads stay in water
3. Grease gets surrounded — pulled into a **micelle** (tiny sphere)
4. Micelle washes away with water

```python
def micelle_demo():
    """Visualize how soap surrounds grease."""
    print("Soap micelle trapping grease:\n")
    print("        Water")
    print("    ─O  ─O  ─O")
    print("   /   \\│/   \\")
    print("  ─O   ╔═══╗  O─")
    print("  │    ║GREA║   │")
    print("  ─O   ║ SE ║  O─")
    print("   \\   ╚═══╝  /")
    print("    ─O  ─O  ─O")
    print("        Water")
    print()
    print("─O = soap molecule (─ = tail in grease, O = head in water)")
    print("The grease is trapped and washes away!")

micelle_demo()
```

## The "Whoa" Moment: Pepper and Soap

Sprinkle pepper on water (it floats on surface tension). Touch the center with a soapy finger — pepper RACES to the edges instantly. Soap breaks surface tension by inserting between water molecules.

Kids see the invisible force (surface tension) made visible, then destroyed by a single molecule's dual nature.

## The Working Kit Design

1. **Measured oil packets** — coconut oil (makes hard, bubbly soap)
2. **Pre-measured lye** — exact amount with 5% superfat safety margin
3. **Molds and colorants** — natural pigments for custom shapes
4. **Fragrance oils** — esters! (connect back to functional groups)
5. **Cleaning challenge** — test soap vs water vs detergent on oil stains
6. **Molecule model** — snap-together pieces showing soap's dual structure

## What You Learned

- **Organic chemistry** = chemistry of carbon compounds
- Carbon makes 4 bonds, chains, rings — infinite variety
- **Hydrocarbons** = C + H only (alkanes, alkenes, alkynes)
- **Functional groups** give molecules specific properties
- **Saponification** = fat + base → soap + glycerol
- Soap works because it's **amphiphilic** — one end loves water, one loves grease

Carbon chemistry is the chemistry of life. But there's one more frontier: what happens inside the atom's nucleus? That's nuclear chemistry — and it's the most powerful (and dangerous) chemistry of all.

---

[← Chapter 10: Redox](chapter-10-redox.md) | [Chapter 12: The Nucleus →](chapter-12-nuclear.md)
