# Chapter 12: The Nucleus — Radioactivity & Nuclear Chemistry

[← Chapter 11: Organic](chapter-11-organic.md) | [Course Overview →](chapter-00-overview.md)

---

## The Kit Idea

MoleCraft's twelfth and final product: **Geiger Counter Demo Kit**. Kids build a simple radiation detector and measure background radiation from everyday objects — bananas, granite countertops, old pottery. They learn that radioactivity is natural, measurable, and governed by predictable math.

Dr. Kenji: "Nuclear chemistry is where atoms transform into *different* elements. It's alchemy that actually works — but with rules."

## The Failed Prototype

You design the kit with a DIY Geiger counter circuit and a collection of "test objects." Beta testers build the detector and start scanning everything.

**What goes wrong:** The detector clicks randomly even with no source nearby. Kids think it's broken. One tester points it at a banana and gets a reading — panics that bananas are dangerous. Another tester asks "If this stuff is decaying, why hasn't it all decayed already?"

Sam: "We need to explain: (1) background radiation is normal, (2) the clicks are random but the *average* is predictable, and (3) 'radioactive' doesn't mean 'instant death.'"

The problem: without understanding half-life and decay types, kids can't interpret what the detector is telling them.

## Radioactive Decay: Unstable Nuclei

Some atomic nuclei are **unstable** — they have too many protons, too many neutrons, or too much energy. They stabilize by emitting radiation:

| Type | What's Emitted | Symbol | Stopped By | Danger |
|------|---------------|--------|------------|--------|
| **Alpha (α)** | 2 protons + 2 neutrons | ⁴₂He | Paper | Low (external) |
| **Beta (β)** | Electron (or positron) | e⁻ | Aluminum | Medium |
| **Gamma (γ)** | High-energy photon | γ | Lead/concrete | High |

```
Alpha:  ²³⁸U → ²³⁴Th + ⁴He    (loses 2p + 2n)
         92      90      2

Beta:   ¹⁴C → ¹⁴N + e⁻         (neutron → proton + electron)
         6     7

Gamma:  Excited nucleus → same nucleus + γ photon
```

## Half-Life: The Decay Clock

**Half-life (t½)** = time for half the radioactive atoms to decay.

It's not "all atoms decay at once" — it's probabilistic. Each atom has a *chance* of decaying each second.

```python
def half_life_simulation(initial_atoms, half_life, time_periods):
    """Simulate radioactive decay over time."""
    print(f"Initial atoms: {initial_atoms}")
    print(f"Half-life: {half_life} years")
    print(f"\n{'Time':>8} {'Remaining':>10} {'Decayed':>8} {'Bar'}")
    print("-" * 50)
    
    remaining = initial_atoms
    for period in range(time_periods + 1):
        time = period * half_life
        bar = "█" * int(remaining / initial_atoms * 30)
        decayed = initial_atoms - remaining
        print(f"{time:>6} yr {remaining:>10.0f} {decayed:>8.0f}  {bar}")
        remaining *= 0.5
    
    return remaining

# Carbon-14: half-life = 5,730 years (used for dating)
half_life_simulation(1000, 5730, 6)
```

```
Initial atoms: 1000
Half-life: 5730 years

    Time  Remaining  Decayed  Bar
--------------------------------------------------
     0 yr       1000        0  ██████████████████████████████
  5730 yr        500      500  ███████████████
 11460 yr        250      750  ███████
 17190 yr        125      875  ███
 22920 yr         62      938  █
 28650 yr         31      969  
 34380 yr         16      984  
```

## Half-Lives of Common Isotopes

```python
half_lives = {
    "Polonium-214": "0.000164 seconds",
    "Radon-222": "3.8 days",
    "Iodine-131": "8 days",
    "Cobalt-60": "5.3 years",
    "Carbon-14": "5,730 years",
    "Uranium-235": "704 million years",
    "Uranium-238": "4.5 billion years",
}

print("Isotope Half-Lives (shortest to longest):")
print("-" * 45)
for isotope, hl in half_lives.items():
    print(f"  {isotope:<18} {hl}")

print("\n★ This is why uranium still exists — it decays")
print("  so slowly that half is still here from when")
print("  Earth formed 4.5 billion years ago!")
```

## Fission: Splitting Heavy Atoms

**Nuclear fission** = splitting a heavy nucleus into lighter ones, releasing enormous energy.

```
²³⁵U + neutron → ¹⁴¹Ba + ⁹²Kr + 3 neutrons + ENERGY
 92              56      36

The 3 neutrons can split 3 more uranium atoms → chain reaction!
```

```python
def fission_energy_comparison():
    """Compare nuclear vs chemical energy."""
    # Energy per reaction
    chemical = 4.0      # eV (burning coal, C + O₂)
    nuclear = 200e6     # eV (uranium fission)
    
    ratio = nuclear / chemical
    
    print("Energy comparison:")
    print(f"  Chemical (coal): {chemical} eV per reaction")
    print(f"  Nuclear (U-235): {nuclear/1e6:.0f} million eV per reaction")
    print(f"  Nuclear is {ratio:.0f}x more energy per atom!")
    print(f"\n  1 kg uranium = ~{ratio * 1 / 1e6:.0f} tons of coal equivalent")
    print(f"  That's why nuclear plants are so compact.")

fission_energy_comparison()
```

## Fusion: Joining Light Atoms

**Nuclear fusion** = combining light nuclei into heavier ones. Powers the sun.

```
²H + ³H → ⁴He + neutron + ENERGY
(deuterium + tritium → helium + 17.6 MeV)
```

Fusion releases even more energy per gram than fission, but requires extreme temperatures (100 million °C) to overcome proton-proton repulsion.

```python
def stellar_fusion():
    """The sun's fusion process (simplified)."""
    print("The Sun's Power Source:")
    print("  4 hydrogen → 1 helium + energy")
    print()
    
    mass_4_hydrogen = 4 * 1.00794  # atomic mass units
    mass_helium = 4.00260
    mass_lost = mass_4_hydrogen - mass_helium
    
    # E = mc² (mass in kg, c in m/s)
    c = 3e8
    energy_per_reaction = mass_lost * 1.66e-27 * c**2  # joules
    
    print(f"  Mass of 4 H:  {mass_4_hydrogen:.5f} amu")
    print(f"  Mass of He:   {mass_helium:.5f} amu")
    print(f"  Mass lost:    {mass_lost:.5f} amu")
    print(f"  Energy (E=mc²): {energy_per_reaction:.2e} J per reaction")
    print(f"\n  The Sun converts 4 million tons of mass to energy every second.")

stellar_fusion()
```

## The "Whoa" Moment: The Banana Equivalent Dose

A banana contains potassium-40 (radioactive isotope). The Geiger counter clicks near a banana — proof that radioactivity is everywhere, natural, and usually harmless.

```python
def banana_equivalent_dose():
    """Radiation exposure in banana units."""
    exposures = {
        "1 banana": 0.1,
        "Dental X-ray": 5.0,
        "Flight NYC→LA": 40.0,
        "Chest CT scan": 7000.0,
        "Annual background": 3000.0,
        "Fukushima evacuation zone": 20000.0,
    }
    
    print("Radiation Doses (in microsieverts):")
    print("-" * 50)
    for source, dose in exposures.items():
        bananas = dose / 0.1
        bar = "🍌" * min(int(bananas / 100), 20)
        print(f"  {source:<25} {dose:>8.1f} µSv  ({bananas:.0f} bananas) {bar}")

banana_equivalent_dose()
```

Kids realize: you'd need to eat 10 million bananas at once for radiation to be dangerous. Context matters.

## The Working Kit Design

1. **Geiger counter module** — pre-built detector with speaker (clicks) and counter
2. **Test objects** — banana, granite tile, potassium salt, old ceramic glaze
3. **Background measurement** — count clicks per minute with no source (establishes baseline)
4. **Half-life simulation** — dice game (roll 100 dice, remove all 6s = "decayed" atoms, repeat)
5. **Shielding experiment** — paper, aluminum, lead sheet between source and detector
6. **Scale card** — banana equivalent doses for context

## What You Learned

- **Radioactive decay** = unstable nuclei emitting alpha, beta, or gamma radiation
- **Half-life** = time for half the atoms to decay (predictable average, random individual)
- **Fission** = splitting heavy atoms → chain reaction → nuclear power
- **Fusion** = joining light atoms → powers the sun → future energy?
- **Background radiation** is natural and usually harmless
- Nuclear energy is millions of times more concentrated than chemical energy

## Course Complete!

You've designed 12 chemistry kits, each teaching a fundamental concept through failure, understanding, and redesign. From atoms to nuclei, from solutions to soap, from pH to PV=nRT — chemistry is the science of *why things behave the way they do*.

Dr. Kenji: "Every kit that failed taught us more than the ones that worked the first time. That's science."

Sam: "And nobody got hurt. Mostly."

---

[← Chapter 11: Organic](chapter-11-organic.md) | [Course Overview →](chapter-00-overview.md)
