# Chapter 8: Acids & Bases — The pH Scale

[← Chapter 7: Thermochemistry](chapter-07-thermochemistry.md) | [Chapter 9: Gases →](chapter-09-gases.md)

---

## The Kit Idea

MoleCraft's eighth product: **pH Indicator Rainbow**. Kids extract natural indicators from red cabbage, then test household liquids to create a full rainbow of colors — each color mapping to a pH value.

Dr. Kenji: "Red cabbage juice changes color across the entire pH spectrum. It's nature's universal indicator."

## The Failed Prototype

You design the kit with cabbage indicator and 10 test liquids. Beta testers line them up expecting a smooth rainbow gradient.

**What goes wrong:** The "rainbow" has gaps. Lemon juice and vinegar are both red (similar pH). Baking soda and soap are both green. The testers can't tell them apart. Worse, one tester mixes the acid and base samples together and the color goes wild — shifting through three colors in seconds.

Sam: "Also, we labeled bleach as 'safe to test.' It's pH 12. That's caustic. We need clear danger zones."

The problem: you didn't explain the pH scale, what the numbers mean, or why mixing acids and bases is its own reaction.

## The pH Scale

pH measures how acidic or basic a solution is:

```
pH = -log₁₀[H⁺]

where [H⁺] = concentration of hydrogen ions (mol/L)
```

```
 pH  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14
     ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
     │◄── ACIDIC ──►│ NEUTRAL │◄── BASIC (alkaline) ──►│
     │               │         │                        │
  Battery  Lemon  Coffee  Water  Baking   Ammonia  Bleach
   acid    juice                  soda
```

Each step = 10× difference in H⁺ concentration. pH 3 is 10× more acidic than pH 4.

## Acids and Bases: What They Do

| Property | Acid | Base |
|----------|------|------|
| Produces | H⁺ ions | OH⁻ ions |
| Tastes | Sour | Bitter/soapy |
| Feels | Stinging | Slippery |
| pH | < 7 | > 7 |
| Examples | HCl, vinegar, citric acid | NaOH, baking soda, soap |

```python
import math

def ph_from_concentration(h_plus_molarity):
    """Calculate pH from hydrogen ion concentration."""
    return -math.log10(h_plus_molarity)

def h_plus_from_ph(ph):
    """Calculate H⁺ concentration from pH."""
    return 10 ** (-ph)

# Common substances
substances = {
    "Stomach acid": 0.01,      # [H⁺] = 0.01 M
    "Lemon juice": 0.005,
    "Coffee": 0.00001,
    "Pure water": 0.0000001,
    "Baking soda": 0.000000001,
    "Bleach": 0.00000000001,
}

print(f"{'Substance':<15} {'[H⁺] (M)':<12} {'pH':<5} {'Type'}")
print("-" * 50)
for name, h_conc in substances.items():
    ph = ph_from_concentration(h_conc)
    acid_base = "Acid" if ph < 7 else "Base" if ph > 7 else "Neutral"
    print(f"{name:<15} {h_conc:<12.1e} {ph:<5.1f} {acid_base}")
```

## Neutralization: Acid Meets Base

When an acid and base mix, they neutralize each other:

```
HCl + NaOH → NaCl + H₂O
(acid + base → salt + water)
```

The H⁺ and OH⁻ combine to form water. The pH moves toward 7.

```python
def neutralization(acid_volume_mL, acid_molarity, base_volume_mL, base_molarity):
    """Simulate acid-base neutralization."""
    moles_acid = acid_volume_mL * acid_molarity / 1000
    moles_base = base_volume_mL * base_molarity / 1000
    
    excess = moles_acid - moles_base
    total_volume_L = (acid_volume_mL + base_volume_mL) / 1000
    
    if abs(excess) < 1e-10:
        ph = 7.0
        status = "NEUTRALIZED ⚖️"
    elif excess > 0:
        h_conc = excess / total_volume_L
        ph = -math.log10(h_conc)
        status = "Still acidic"
    else:
        oh_conc = abs(excess) / total_volume_L
        poh = -math.log10(oh_conc)
        ph = 14 - poh
        status = "Still basic"
    
    print(f"Acid: {acid_volume_mL}mL × {acid_molarity}M = {moles_acid:.4f} mol H⁺")
    print(f"Base: {base_volume_mL}mL × {base_molarity}M = {moles_base:.4f} mol OH⁻")
    print(f"Result: pH = {ph:.1f} — {status}")
    return ph

# Tester mixing acid and base samples:
neutralization(50, 0.1, 25, 0.1)   # Half-neutralized, still acidic
neutralization(50, 0.1, 50, 0.1)   # Perfectly neutralized
```

## Buffers: Resisting pH Change

A **buffer** is a solution that resists pH changes when small amounts of acid or base are added. Your blood is buffered at pH 7.4 — if it shifts even 0.5, you're in trouble.

```python
def buffer_demo(buffer_present=True):
    """Show how buffers resist pH change."""
    print(f"{'With' if buffer_present else 'Without'} buffer:")
    print(f"  Start pH: 7.0")
    
    # Add acid drops
    for drops in [1, 2, 3, 5, 10]:
        if buffer_present:
            # Buffer absorbs most of the acid
            ph_change = drops * 0.05  # small change
        else:
            # No buffer — pH drops fast
            ph_change = drops * 0.4
        
        new_ph = 7.0 - ph_change
        bar = "█" * int((7 - new_ph) * 5)
        print(f"  +{drops:2d} drops acid → pH {new_ph:.1f} {bar}")

buffer_demo(buffer_present=False)
print()
buffer_demo(buffer_present=True)
```

## Indicators: Colors That Tell pH

The cabbage indicator contains **anthocyanins** — molecules that change structure (and color) depending on H⁺ concentration:

```
pH:    2      4      6      7      8      10     12
Color: RED    PINK   PURPLE VIOLET BLUE   GREEN  YELLOW
       ████   ████   ████   ████   ████   ████   ████
```

## The "Whoa" Moment: The Invisible Ink Reveal

Write a message with baking soda solution (invisible when dry). Spray with cabbage indicator — the message appears in blue/green against the purple background. Spray with vinegar — the whole thing turns pink and the message vanishes.

Chemistry as magic trick. The pH difference between the "ink" and the paper creates visible color contrast only when the indicator is present.

## The Working Kit Design

1. **Red cabbage powder** — just add water to make indicator
2. **Test liquids** — carefully chosen to span the full pH range with no gaps
3. **pH color chart** — maps indicator color to pH number
4. **Neutralization challenge** — add base drops to acid until color hits purple (pH 7)
5. **Invisible ink supplies** — baking soda pen + spray bottle
6. **Safety card** — red zone (pH 0-2, 12-14) = don't touch without gloves

## What You Learned

- **pH** = -log₁₀[H⁺], scale from 0 (strong acid) to 14 (strong base)
- Each pH unit = 10× difference in H⁺ concentration
- **Neutralization**: acid + base → salt + water
- **Buffers** resist pH change (critical in biology)
- **Indicators** change color at specific pH values
- Natural indicators (cabbage) work across the full spectrum

The rainbow is complete. But the next kit involves gas — and gas behaves very differently from liquids. How do you predict what a gas will do?

---

[← Chapter 7: Thermochemistry](chapter-07-thermochemistry.md) | [Chapter 9: Gases →](chapter-09-gases.md)
