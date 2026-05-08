# Chapter 1: Building Blocks — Atoms

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Why Things Stick →](chapter-02-bonding.md)

---

## The Kit Idea

MoleCraft's first product: an **Atom Model Kit**. Snap-together pieces representing protons, neutrons, and electrons. Kids build atoms of different elements and see how they differ.

The prototype has colored balls: red for protons, blue for neutrons, yellow for electrons. But the beta testers are confused:

"Why does hydrogen have 1 red ball and carbon has 6? What decides the number?"

Dr. Kenji: "If they don't understand what makes one element different from another, the kit is just colored balls. We need to teach atomic structure."

## The Failed Prototype

The first version just said "Hydrogen: 1 proton, 0 neutrons, 1 electron. Carbon: 6 protons, 6 neutrons, 6 electrons." A table of numbers. The testers memorized nothing.

The problem: numbers without meaning. Why those numbers? What do they *do*?

## What Is an Atom?

Everything around you — the air, your phone, your coffee — is made of atoms. An atom is the smallest unit of an element that still behaves like that element.

An atom has three parts:

```
                    ┌─────────────────┐
                    │     NUCLEUS     │
                    │  ⊕ protons (+)  │
                    │  ○ neutrons (0) │
                    └────────┬────────┘
                             │
              ───────────────┼───────────────
             /               │               \
            ⊖               ⊖               ⊖
         electrons (-)   in "shells"    orbiting the nucleus
```

| Particle | Charge | Mass | Location |
|---|---|---|---|
| Proton | +1 | 1 amu | Nucleus |
| Neutron | 0 | 1 amu | Nucleus |
| Electron | -1 | ~0 (1/1836 amu) | Shells around nucleus |

**amu** = atomic mass unit. Protons and neutrons weigh about the same. Electrons are so light they barely count for mass.

## The Atomic Number: Identity Card

The **atomic number** = number of protons. This is what makes an element *that element*.

- 1 proton → Hydrogen (always)
- 6 protons → Carbon (always)
- 79 protons → Gold (always)

Change the number of protons, you change the element. Period.

```python
# Simulation: What defines an element?
elements = {
    1: "Hydrogen",
    2: "Helium",
    6: "Carbon",
    7: "Nitrogen",
    8: "Oxygen",
    26: "Iron",
    79: "Gold",
}

def identify_element(protons):
    """The number of protons IS the element."""
    return elements.get(protons, f"Element {protons}")

print(identify_element(6))   # Carbon
print(identify_element(79))  # Gold
```

## Neutrons: The Glue

Neutrons hold the nucleus together. Without them, the positively-charged protons would repel each other and the nucleus would fly apart.

Most elements have roughly equal protons and neutrons (for light elements) or more neutrons than protons (for heavy elements):

| Element | Protons | Neutrons | Why |
|---|---|---|---|
| Hydrogen | 1 | 0 | Only 1 proton, nothing to repel |
| Carbon | 6 | 6 | Equal works for light elements |
| Iron | 26 | 30 | Needs extra glue |
| Gold | 79 | 118 | Heavy elements need lots of glue |

### Isotopes: Same Element, Different Neutrons

Change the neutron count and you get an **isotope** — same element, slightly different mass:

- Carbon-12: 6 protons, 6 neutrons (normal)
- Carbon-13: 6 protons, 7 neutrons (stable, rare)
- Carbon-14: 6 protons, 8 neutrons (radioactive — used for dating)

All three are carbon. All behave chemically the same. But Carbon-14 is unstable and decays over time (Chapter 12).

## Electrons: The Social Butterflies

Electrons determine how an atom **interacts** with other atoms. They live in shells (energy levels) around the nucleus:

```
Shell 1: holds up to 2 electrons
Shell 2: holds up to 8 electrons
Shell 3: holds up to 18 electrons (but often fills to 8 first)
```

```python
def electron_shells(atomic_number):
    """Distribute electrons into shells (simplified)."""
    shells = []
    remaining = atomic_number
    capacities = [2, 8, 8, 18, 18, 32, 32]  # Simplified

    for cap in capacities:
        if remaining <= 0:
            break
        electrons_in_shell = min(remaining, cap)
        shells.append(electrons_in_shell)
        remaining -= electrons_in_shell

    return shells

# Examples
print(f"Hydrogen (1):  {electron_shells(1)}")   # [1]
print(f"Helium (2):    {electron_shells(2)}")    # [2]
print(f"Carbon (6):    {electron_shells(6)}")    # [2, 4]
print(f"Neon (10):     {electron_shells(10)}")   # [2, 8]
print(f"Sodium (11):   {electron_shells(11)}")   # [2, 8, 1]
```

The **outermost shell** (valence shell) is everything. It determines:
- How the atom bonds with others (Chapter 2)
- Whether the atom is reactive or inert
- The element's chemical personality

## The "Whoa" Moment

Here's what makes the kit click: **the periodic table is organized by electron shells.**

- Row 1: filling shell 1 (H, He — 2 elements, shell holds 2)
- Row 2: filling shell 2 (Li through Ne — 8 elements, shell holds 8)
- Row 3: filling shell 3 (Na through Ar — 8 elements)

The table isn't arbitrary. It's a map of electron configurations. Elements in the same column have the same number of outer electrons — that's why they behave similarly.

```python
# Elements in the same column behave alike
group_1 = {
    "Lithium": [2, 1],    # 1 outer electron
    "Sodium": [2, 8, 1],  # 1 outer electron
    "Potassium": [2, 8, 8, 1],  # 1 outer electron
}
# All are reactive metals that explode in water!
```

## The Working Kit

The redesigned kit includes:
1. **Nucleus board** — slots for protons (red) and neutrons (gray)
2. **Shell rings** — concentric rings that snap around the nucleus
3. **Electron pegs** — yellow pegs that fit into shell ring slots
4. **Element cards** — show the target configuration

Activity: "Build a sodium atom. How many electrons are in the outer shell? Now build chlorine. What happens if sodium gives its outer electron to chlorine?" (Spoiler: table salt. Chapter 2.)

## Key Takeaways

| Concept | The Rule |
|---|---|
| Atomic number | = protons = defines the element |
| Mass number | = protons + neutrons |
| Isotopes | Same protons, different neutrons |
| Electron shells | Fill from inside out: 2, 8, 8, 18... |
| Valence electrons | Outer shell electrons = chemical behavior |
| Neutral atom | protons = electrons (charges balance) |

## What You Learned

- **Atoms** have protons (identity), neutrons (stability), electrons (behavior)
- **Atomic number** = number of protons = what element it is
- **Electron shells** fill in order: 2, 8, 8, 18...
- **Valence electrons** (outer shell) determine how atoms interact
- **The periodic table** is organized by electron configuration
- **Isotopes** = same element, different neutron count

The atom model kit now teaches *why* elements are different, not just *that* they're different. But the beta testers have a new question: "Why do atoms stick together?" That's bonding — Chapter 2.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Why Things Stick →](chapter-02-bonding.md)
