# Chapter 3: The Periodic Neighborhood — Periodic Trends

[← Chapter 2: Bonding](chapter-02-bonding.md) | [Chapter 4: Mixing and Dissolving →](chapter-04-solutions.md)

---

## The Kit Idea

MoleCraft's third product: **Element Trading Cards**. Each card shows an element with its stats — like Pokémon cards but for atoms. Kids trade them, compare stats, and predict which elements will react with each other.

The prototype has random stats. Beta testers ask: "Why is sodium's reactivity 9/10 but gold's is 2/10? What makes some elements reactive and others inert?"

Dr. Kenji: "The periodic table isn't random. There are patterns — trends that predict behavior. The trading cards need to teach those trends."

## The Periodic Table: A Map, Not a List

The periodic table is organized by two axes:

- **Rows (periods)**: each row adds a new electron shell
- **Columns (groups)**: elements in the same column have the same number of outer electrons

```
Group:  1    2                          13  14  15  16  17  18
      ┌────┬────┐                      ┌───┬───┬───┬───┬───┬───┐
  1   │ H  │    │                      │   │   │   │   │   │He │
      ├────┼────┤                      ├───┼───┼───┼───┼───┼───┤
  2   │ Li │ Be │                      │ B │ C │ N │ O │ F │Ne │
      ├────┼────┤                      ├───┼───┼───┼───┼───┼───┤
  3   │ Na │ Mg │                      │Al │Si │ P │ S │Cl │Ar │
      ├────┼────┼────┬───┬───┬───┬───┬───┼───┼───┼───┼───┼───┤
  4   │ K  │ Ca │ Sc │...│...│...│...│...│Ga │Ge │As │Se │Br │Kr │
      └────┴────┴────┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
        ↑                                                    ↑
   Most reactive                                    Least reactive
   metals (give e⁻)                                 (noble gases)
```

Elements in the same column behave similarly because they have the same valence electron count.

## Trend 1: Atomic Radius (Size)

**Across a row (left → right): atoms get SMALLER**

Why? More protons pull electrons closer. Same shell, more pull.

**Down a column (top → bottom): atoms get BIGGER**

Why? More shells = electrons farther from nucleus.

```python
# Approximate atomic radii (picometers)
radii = {
    "Li": 152, "Be": 112, "B": 87, "C": 77, "N": 75, "O": 73, "F": 72,
    "Na": 186, "Mg": 160, "Al": 143, "Si": 117, "P": 110, "S": 104, "Cl": 99,
    "K": 227, "Ca": 197,
}

# Across row 2: getting smaller
row2 = ["Li", "Be", "B", "C", "N", "O", "F"]
print("Row 2 (left to right — shrinking):")
for elem in row2:
    bar = "█" * (radii[elem] // 10)
    print(f"  {elem:2s}: {radii[elem]:3d} pm  {bar}")

# Down group 1: getting bigger
group1 = ["Li", "Na", "K"]
print("\nGroup 1 (top to bottom — growing):")
for elem in group1:
    bar = "█" * (radii[elem] // 10)
    print(f"  {elem:2s}: {radii[elem]:3d} pm  {bar}")
```

```
Row 2 (left to right — shrinking):
  Li: 152 pm  ███████████████
  Be: 112 pm  ███████████
  B :  87 pm  ████████
  C :  77 pm  ███████
  N :  75 pm  ███████
  O :  73 pm  ███████
  F :  72 pm  ███████

Group 1 (top to bottom — growing):
  Li: 152 pm  ███████████████
  Na: 186 pm  ██████████████████
  K : 227 pm  ██████████████████████
```

## Trend 2: Ionization Energy (How Hard to Remove an Electron)

**Across a row: INCREASES** (harder to remove — atoms hold tighter)
**Down a column: DECREASES** (easier to remove — electron is farther away)

```python
# First ionization energy (kJ/mol)
ie = {
    "Li": 520, "Be": 900, "B": 801, "C": 1086, "N": 1402, "O": 1314, "F": 1681, "Ne": 2081,
    "Na": 496, "Mg": 738, "Al": 578, "Si": 786, "P": 1012, "S": 1000, "Cl": 1251, "Ar": 1521,
    "K": 419, "Ca": 590,
}

print("Ionization Energy — How hard to steal an electron:")
print("\nRow 2 (increases left → right):")
for elem in ["Li", "Be", "B", "C", "N", "O", "F", "Ne"]:
    bar = "█" * (ie[elem] // 100)
    print(f"  {elem:2s}: {ie[elem]:4d} kJ/mol  {bar}")
```

Low ionization energy = easy to lose an electron = reactive metal.
High ionization energy = hard to lose an electron = stable/noble gas.

## Trend 3: Electronegativity (Electron Greed)

**Across a row: INCREASES** (nonmetals pull harder)
**Down a column: DECREASES** (bigger atoms pull less effectively)

```python
# Pauling electronegativity scale
en = {
    "Li": 1.0, "Be": 1.6, "B": 2.0, "C": 2.5, "N": 3.0, "O": 3.5, "F": 4.0,
    "Na": 0.9, "Mg": 1.3, "Al": 1.6, "Si": 1.9, "P": 2.2, "S": 2.6, "Cl": 3.2,
    "K": 0.8, "Ca": 1.0,
}

# Fluorine is the most electronegative element (4.0)
# Francium is the least (0.7)
```

High electronegativity = wants electrons badly = good at forming negative ions.

## Trend 4: Reactivity

For **metals** (left side): reactivity INCREASES going down and left.
- Why? Easier to lose outer electrons (bigger atom, weaker hold)
- Most reactive metal: Francium (bottom-left)

For **nonmetals** (right side): reactivity INCREASES going up and right.
- Why? Stronger pull on electrons (smaller atom, closer to full shell)
- Most reactive nonmetal: Fluorine (top-right, excluding noble gases)

```python
def predict_reactivity(group, period, is_metal):
    """Predict relative reactivity from position."""
    if is_metal:
        # Metals: more reactive down and left
        return period * 2 + (4 - group)  # Higher = more reactive
    else:
        # Nonmetals: more reactive up and right
        return (8 - period) * 2 + (group - 13)

# Examples
print("Metal reactivity (higher = more reactive):")
print(f"  Li (period 2, group 1): {predict_reactivity(1, 2, True)}")
print(f"  Na (period 3, group 1): {predict_reactivity(1, 3, True)}")
print(f"  K  (period 4, group 1): {predict_reactivity(1, 4, True)}")

print("\nNonmetal reactivity:")
print(f"  F  (period 2, group 17): {predict_reactivity(17, 2, False)}")
print(f"  Cl (period 3, group 17): {predict_reactivity(17, 3, False)}")
```

## The "Whoa" Moment: Predicting Reactions

With these trends, you can predict which elements react violently:

- **Most reactive metal** (bottom-left) + **Most reactive nonmetal** (top-right) = VIOLENT reaction
- Sodium + Water → explosion (sodium is very reactive, water provides the nonmetal partner)
- Potassium + Water → bigger explosion (potassium is below sodium, more reactive)
- Francium + Water → theoretically the biggest explosion (never actually done safely)

```python
def will_react_violently(metal_en, nonmetal_en):
    """Bigger electronegativity difference = more violent ionic reaction."""
    diff = abs(nonmetal_en - metal_en)
    if diff > 2.5:
        return "💥 VIOLENT (strong ionic bond forms)"
    elif diff > 1.7:
        return "⚡ Reactive (ionic bond)"
    elif diff > 0.5:
        return "~ Mild (polar covalent)"
    else:
        return "😴 Barely reacts (nonpolar)"

print(will_react_violently(en["Na"], en["Cl"]))  # 💥 VIOLENT
print(will_react_violently(en["C"], en["O"]))    # ~ Mild
print(will_react_violently(en["C"], en["C"]))    # 😴 Barely
```

## The Working Trading Cards

Each card now has meaningful stats:

```
┌─────────────────────────┐
│  ⚛️  SODIUM (Na)         │
│  Atomic #: 11           │
│  Mass: 23               │
├─────────────────────────┤
│  Size:     ████████░░ 8 │
│  IE:       ██░░░░░░░░ 2 │
│  EN:       █░░░░░░░░░ 1 │
│  React:    █████████░ 9 │
├─────────────────────────┤
│  Type: Alkali Metal     │
│  Wants: LOSE 1 electron │
│  Reacts with: Halogens! │
│  Fun fact: Explodes in  │
│  water 💥               │
└─────────────────────────┘
```

Kids can now compare cards and predict: "Sodium (reactivity 9) + Fluorine (reactivity 10) = big reaction!" And they'd be right.

## Summary of Trends

| Property | Across row (→) | Down column (↓) |
|---|---|---|
| Atomic radius | Decreases | Increases |
| Ionization energy | Increases | Decreases |
| Electronegativity | Increases | Decreases |
| Metal reactivity | Decreases | Increases |
| Nonmetal reactivity | Increases | Decreases |

One underlying cause: **effective nuclear charge**. Across a row, more protons pull electrons tighter. Down a column, more shells shield the outer electrons from the nucleus.

## What You Learned

- **Periodic trends** are predictable patterns, not random
- **Atomic radius** — smaller across, bigger down
- **Ionization energy** — harder to remove electrons across, easier down
- **Electronegativity** — stronger pull across, weaker down
- **Reactivity** — metals reactive bottom-left, nonmetals reactive top-right
- **Predictions** — trends let you predict reactions without memorizing

The trading cards teach real chemistry through comparison. But the next kit needs a different concept: "Why does sugar dissolve in water but oil doesn't?" That's solutions and solubility.

---

[← Chapter 2: Bonding](chapter-02-bonding.md) | [Chapter 4: Mixing and Dissolving →](chapter-04-solutions.md)
