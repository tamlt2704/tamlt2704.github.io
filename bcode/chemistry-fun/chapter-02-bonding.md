# Chapter 2: Why Things Stick — Chemical Bonding

[← Chapter 1: Atoms](chapter-01-atoms.md) | [Chapter 3: The Periodic Neighborhood →](chapter-03-periodic-table.md)

---

## The Kit Idea

MoleCraft's second product: a **Molecular Building Set**. Snap-together atoms that form molecules — water, salt, carbon dioxide. Kids build molecules and see why atoms combine in specific ratios.

The prototype has atoms with generic connectors. Beta testers build "H₇O₃" and "NaCl₅" — molecules that can't exist. The kit doesn't enforce the rules.

Dr. Kenji: "The connectors need to reflect valence. Hydrogen gets one connector. Oxygen gets two. Carbon gets four. The kit should make it *impossible* to build a wrong molecule."

## The Failed Prototype

The first version let any atom connect to any other atom in any quantity. Result: kids built nonsense molecules and learned nothing about why water is H₂O and not H₃O.

The question: **why do atoms bond at all, and why in specific ratios?**

## Why Atoms Bond: The Octet Rule

Atoms "want" a full outer shell. For most atoms, that means **8 electrons** in the outer shell (2 for hydrogen and helium).

```
Neon (10): [2, 8]     ← Full outer shell. Happy. Doesn't react.
Sodium (11): [2, 8, 1] ← One extra electron. Desperate to lose it.
Chlorine (17): [2, 8, 7] ← One electron short. Desperate to gain one.
```

Atoms bond to achieve a full outer shell. The method depends on who's involved.

## Bond Type 1: Ionic Bonds (Give and Take)

When a metal meets a nonmetal, one gives electrons and the other takes:

```
Sodium [2, 8, 1]  →  gives 1 electron  →  Na⁺ [2, 8]     (full!)
Chlorine [2, 8, 7] →  takes 1 electron  →  Cl⁻ [2, 8, 8]  (full!)
```

The resulting ions (Na⁺ and Cl⁻) have opposite charges and attract each other. That attraction IS the ionic bond. The result: NaCl (table salt).

```python
def ionic_bond(metal_valence, nonmetal_valence):
    """
    Determine the ratio for an ionic compound.
    Metal gives electrons, nonmetal takes them.
    """
    metal_gives = metal_valence          # Electrons to give
    nonmetal_needs = 8 - nonmetal_valence  # Electrons to take

    # Find the ratio (LCM)
    from math import gcd
    lcm = (metal_gives * nonmetal_needs) // gcd(metal_gives, nonmetal_needs)

    num_metals = lcm // metal_gives
    num_nonmetals = lcm // nonmetal_needs

    return num_metals, num_nonmetals

# NaCl: sodium (1 valence e⁻) + chlorine (7 valence e⁻)
print(ionic_bond(1, 7))  # (1, 1) → NaCl

# MgCl₂: magnesium (2 valence e⁻) + chlorine (7 valence e⁻)
print(ionic_bond(2, 7))  # (1, 2) → MgCl₂

# Al₂O₃: aluminum (3 valence e⁻) + oxygen (6 valence e⁻)
print(ionic_bond(3, 6))  # (2, 3) → Al₂O₃
```

### Properties of Ionic Compounds
- Hard, brittle crystals (salt, rust)
- High melting points (NaCl melts at 801°C)
- Conduct electricity when dissolved in water (ions move freely)

## Bond Type 2: Covalent Bonds (Sharing)

When two nonmetals meet, neither wants to give up electrons. Instead, they **share**:

```
Hydrogen [1] + Hydrogen [1]
Each has 1 electron, needs 2 for a full shell.
Solution: share both electrons. Each "sees" 2.

H : H  →  H—H  (single bond, shared pair)
```

```
Oxygen [2, 6] + 2× Hydrogen [1]
Oxygen needs 2 more electrons. Each hydrogen needs 1.
Solution: oxygen shares one electron with each hydrogen.

H—O—H  (water!)
```

```python
def covalent_bonds_needed(valence_electrons):
    """How many bonds does this atom form?"""
    if valence_electrons <= 4:
        return valence_electrons  # Carbon: 4 bonds
    else:
        return 8 - valence_electrons  # Oxygen: 2 bonds, Fluorine: 1 bond

# This is why the kit connectors work:
elements = {
    "H": 1,   # 1 bond (1 connector)
    "O": 6,   # 2 bonds (2 connectors)
    "N": 5,   # 3 bonds (3 connectors)
    "C": 4,   # 4 bonds (4 connectors)
    "F": 7,   # 1 bond (1 connector)
}

for elem, valence in elements.items():
    bonds = covalent_bonds_needed(valence)
    print(f"{elem}: {valence} valence e⁻ → forms {bonds} bond(s)")
```

Output:
```
H: 1 valence e⁻ → forms 1 bond(s)
O: 6 valence e⁻ → forms 2 bond(s)
N: 5 valence e⁻ → forms 3 bond(s)
C: 4 valence e⁻ → forms 4 bond(s)
F: 7 valence e⁻ → forms 1 bond(s)
```

Now the kit makes sense: hydrogen atoms have 1 connector, oxygen has 2, carbon has 4. You *can't* build H₃O because oxygen only has 2 connectors.

### Single, Double, and Triple Bonds

Atoms can share more than one pair:

```
O=O     (double bond: 2 shared pairs) — oxygen gas
N≡N     (triple bond: 3 shared pairs) — nitrogen gas
O=C=O   (two double bonds) — carbon dioxide
```

Double and triple bonds are shorter and stronger than single bonds.

## Bond Type 3: Metallic Bonds (Electron Sea)

In metals, atoms share electrons with ALL their neighbors — a "sea" of electrons flowing freely:

```
┌─────────────────────────┐
│  Cu⁺  Cu⁺  Cu⁺  Cu⁺   │
│    e⁻  e⁻  e⁻  e⁻     │  ← electrons flow freely
│  Cu⁺  Cu⁺  Cu⁺  Cu⁺   │
│    e⁻  e⁻  e⁻  e⁻     │
└─────────────────────────┘
```

This explains why metals:
- Conduct electricity (electrons flow)
- Are malleable (layers slide over each other)
- Are shiny (free electrons reflect light)

## Electronegativity: Who Pulls Harder?

Not all sharing is equal. **Electronegativity** measures how strongly an atom pulls on shared electrons:

```
F (4.0) > O (3.5) > N (3.0) > C (2.5) > H (2.1) > Na (0.9)
```

- **Equal sharing** (nonpolar covalent): H—H, O=O (same atom, same pull)
- **Unequal sharing** (polar covalent): H—O (oxygen pulls harder, gets more electron time)
- **Complete transfer** (ionic): Na—Cl (chlorine pulls so hard it takes the electron entirely)

```python
def bond_type(electronegativity_diff):
    """Classify bond type by electronegativity difference."""
    if electronegativity_diff < 0.5:
        return "Nonpolar covalent (equal sharing)"
    elif electronegativity_diff < 1.7:
        return "Polar covalent (unequal sharing)"
    else:
        return "Ionic (electron transfer)"

# Examples
print(bond_type(abs(2.1 - 2.1)))  # H-H: Nonpolar covalent
print(bond_type(abs(3.5 - 2.1)))  # O-H: Polar covalent
print(bond_type(abs(3.0 - 0.9)))  # Na-Cl: Ionic
```

## The "Whoa" Moment

Water (H₂O) is a polar molecule — oxygen pulls electrons toward itself, making the oxygen end slightly negative and the hydrogen ends slightly positive:

```
      δ⁻
       O
      / \
    H     H
   δ⁺     δ⁺
```

This polarity is why:
- Water dissolves salt (pulls ions apart)
- Water beads on wax (polar water avoids nonpolar wax)
- Ice floats (hydrogen bonds create an open crystal structure)

One concept — electronegativity — explains all of it.

## The Working Kit

The redesigned molecular building set:
- **Atom balls** with the correct number of connectors (H=1, O=2, N=3, C=4)
- **Bond sticks**: single (one stick), double (two sticks), triple (three sticks)
- **Color coding**: red=oxygen, white=hydrogen, black=carbon, blue=nitrogen
- **Challenge cards**: "Build water," "Build methane (CH₄)," "Build CO₂"

The kit physically prevents wrong molecules. You can't attach 3 hydrogens to oxygen because oxygen only has 2 holes.

## What You Learned

- **Atoms bond to fill their outer shell** (octet rule)
- **Ionic bonds** — metal gives electrons to nonmetal (NaCl)
- **Covalent bonds** — nonmetals share electrons (H₂O)
- **Metallic bonds** — electron sea shared by all metal atoms
- **Electronegativity** — determines who pulls harder on shared electrons
- **Bond polarity** — unequal sharing creates partial charges
- **Valence = connectors** — determines how many bonds an atom forms

The molecular building set works. But beta testers ask: "Why is sodium so reactive but gold isn't? Why does fluorine react with everything?" That's periodic trends — Chapter 3.

---

[← Chapter 1: Atoms](chapter-01-atoms.md) | [Chapter 3: The Periodic Neighborhood →](chapter-03-periodic-table.md)
