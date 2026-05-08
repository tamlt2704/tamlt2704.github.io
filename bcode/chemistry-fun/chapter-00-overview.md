# Chapter 0: Before You Start

[Chapter 1: Building Blocks →](chapter-01-atoms.md)

---

## The Story

You're a product designer at **MoleCraft Labs**, a startup that makes educational chemistry kits for curious teenagers and adults. Each kit teaches one chemistry concept through a hands-on experiment — something you can do in a kitchen with household materials.

The catch: you need to understand the science deeply enough to make the kit safe, spectacular, and educational. A volcano that fizzles teaches nothing. A pH indicator that doesn't change color is a waste of money. A hand warmer that gets too hot is a lawsuit.

Your boss, **Dr. Kenji**, a former chemistry professor turned entrepreneur, sets the bar:

"Every kit must have a 'whoa' moment. The moment where the learner sees something unexpected and asks 'why did that happen?' That's where learning lives."

Over 12 chapters, you'll design 12 kits — and learn the chemistry behind each one. Every concept is introduced because your kit doesn't work without it.

## How This Works

Each chapter follows the same loop:

1. **The kit idea** — what you're trying to build
2. **The failed prototype** — what goes wrong without understanding the science
3. **The chemistry** — the concept that explains why
4. **The working version** — the kit, now that you understand the science
5. **The "whoa" moment** — what makes the learner's eyes go wide

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Kit Designer | Creative, impatient, learns by breaking things |
| **Dr. Kenji** | Founder / Chemist | "What's the molecular explanation?" |
| **Sam** | Safety Officer | "Will this explode? No? Will it stain? Also no? Proceed." |
| **Beta Testers** | Teenagers | Brutally honest. "This is boring." |

## Safety First

This is a chemistry course. Some experiments involve:
- Vinegar and baking soda (safe, messy)
- Rubbing alcohol (flammable — no open flames)
- Hydrogen peroxide (3% household concentration only)
- Red cabbage juice (safe, stains everything purple)

Rules:
- Work in a ventilated area
- Wear old clothes (stains happen)
- Never mix chemicals not specified in the instructions
- Keep experiments away from eyes and mouth
- Adult supervision for anything involving heat

## Prerequisites

### Curiosity

No chemistry background needed. We start from atoms.

### Kitchen Supplies (for optional experiments)

- Vinegar, baking soda, salt, sugar
- Red cabbage (for pH indicator)
- Hydrogen peroxide (3%, from pharmacy)
- Dish soap, food coloring
- Cups, spoons, thermometer (optional)

### Python 3.10+ (optional, for simulations)

Some chapters include Python simulations of molecular behavior:

```bash
python3 --version
# Python 3.10.x or higher
```

The simulations are optional — you can learn all the chemistry without code.

## The Periodic Table as a Map

You don't need to memorize the periodic table. Think of it as a map:

```
         ← Metals                    Nonmetals →
    ┌─────────────────────────────────────────────┐
  1 │ H                                        He │  ← Noble gases (don't react)
  2 │ Li Be                    B  C  N  O  F  Ne │
  3 │ Na Mg                    Al Si P  S  Cl Ar │
  4 │ K  Ca Sc Ti V  Cr Mn Fe Co Ni Cu Zn Ga... │
    └─────────────────────────────────────────────┘
         ↑                              ↑
    Very reactive                  Getting less reactive
    (want to give                  (want to take
     electrons away)                electrons)
```

- **Left side**: metals that desperately want to give away electrons
- **Right side**: nonmetals that desperately want to take electrons
- **Far right**: noble gases that want nothing to do with anyone
- **Chemistry happens** when the left side meets the right side

We'll revisit this map in every chapter. For now, just know it exists.

## The Roadmap

| Ch | The Kit | The Chemistry |
|---|---|---|
| 1 | Atom model kit | Atomic structure, subatomic particles |
| 2 | Molecular building set | Chemical bonds (ionic, covalent) |
| 3 | Element trading cards | Periodic trends |
| 4 | Color-changing drinks | Solutions and concentration |
| 5 | Volcano kit | Chemical reactions and equations |
| 6 | Glow stick hacking | Reaction rates and catalysts |
| 7 | Hand warmer design | Thermochemistry |
| 8 | pH indicator rainbow | Acids, bases, and pH |
| 9 | Balloon rocket launcher | Gas laws |
| 10 | Lemon battery | Redox and electrochemistry |
| 11 | Soap making | Organic chemistry intro |
| 12 | Geiger counter demo | Nuclear chemistry |

Let's build some atoms.

---

[Chapter 1: Building Blocks →](chapter-01-atoms.md)
