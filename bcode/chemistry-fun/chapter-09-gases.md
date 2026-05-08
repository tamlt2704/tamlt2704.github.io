# Chapter 9: Under Pressure — Gas Laws

[← Chapter 8: pH](chapter-08-ph.md) | [Chapter 10: Electron Transfer →](chapter-10-redox.md)

---

## The Kit Idea

MoleCraft's ninth product: **Balloon Rocket Launcher**. Kids generate gas from chemical reactions, capture it in a balloon, then release it through a nozzle to launch a small rocket. The challenge: predict how much gas you need for a target distance.

Dr. Kenji: "Gases are predictable. If you know the math, you can engineer the perfect launch."

## The Failed Prototype

You design the kit with baking soda + vinegar in a sealed bottle connected to a balloon. Beta testers generate gas and try to launch rockets.

**What goes wrong:** First tester's balloon barely inflates — not enough reactant. Second tester's bottle explodes because the sealed container couldn't handle the pressure. Third tester does it on a hot day and the balloon is way bigger than expected.

Sam: "We need to predict pressure, volume, AND temperature effects. One kid's bottle cap hit the neighbor's fence."

The problem: gas behavior depends on three linked variables, and changing one changes the others.

## Boyle's Law: Pressure × Volume

At constant temperature, pressure and volume are inversely related:

```
P₁V₁ = P₂V₂

Squeeze a gas smaller → pressure goes UP
Let it expand → pressure goes DOWN
```

```python
def boyles_law(p1, v1, v2):
    """Calculate new pressure when volume changes (constant T)."""
    p2 = (p1 * v1) / v2
    return p2

# Balloon at 1 atm, 2L. Squeeze to 1L:
p_new = boyles_law(1.0, 2.0, 1.0)
print(f"Squeeze 2L → 1L: pressure goes from 1.0 atm to {p_new:.1f} atm")

# Bottle at 1 atm, 0.5L. Gas generation doubles volume to 1L:
p_bottle = boyles_law(2.0, 0.5, 1.0)
print(f"Sealed bottle, gas doubles: {p_bottle:.1f} atm")
```

## Charles's Law: Volume & Temperature

At constant pressure, volume and temperature are directly related:

```
V₁/T₁ = V₂/T₂    (T in Kelvin!)

Heat a gas → it expands
Cool a gas → it shrinks
```

```python
def charles_law(v1, t1_celsius, t2_celsius):
    """Calculate new volume when temperature changes (constant P)."""
    t1_k = t1_celsius + 273.15
    t2_k = t2_celsius + 273.15
    v2 = v1 * (t2_k / t1_k)
    return v2

# Balloon inflated to 1L at 20°C. Hot day at 40°C:
v_hot = charles_law(1.0, 20, 40)
print(f"Balloon at 20°C: 1.0L → at 40°C: {v_hot:.2f}L")

# Same balloon in freezer at -10°C:
v_cold = charles_law(1.0, 20, -10)
print(f"Balloon at 20°C: 1.0L → at -10°C: {v_cold:.2f}L")
```

This explains why the hot-day launch was overpowered — the gas expanded beyond predictions.

## The Ideal Gas Law: PV = nRT

The master equation combining everything:

```
PV = nRT

P = pressure (atm)
V = volume (liters)
n = moles of gas
R = 0.0821 L·atm/(mol·K)
T = temperature (Kelvin)
```

```python
def ideal_gas(n=None, P=None, V=None, T_celsius=None):
    """Solve PV=nRT for the missing variable."""
    R = 0.0821  # L·atm/(mol·K)
    T = T_celsius + 273.15 if T_celsius is not None else None
    
    if n is None:
        n = (P * V) / (R * T)
        print(f"Moles of gas: {n:.4f} mol")
    elif P is None:
        P = (n * R * T) / V
        print(f"Pressure: {P:.2f} atm")
    elif V is None:
        V = (n * R * T) / P
        print(f"Volume: {V:.3f} L")
    elif T_celsius is None:
        T = (P * V) / (n * R)
        print(f"Temperature: {T - 273.15:.1f}°C ({T:.1f} K)")
    
    return n, P, V, T

# How much gas does our reaction produce?
# NaHCO₃ + HCl → NaCl + H₂O + CO₂
# 10g baking soda = 10/84 = 0.119 mol CO₂

print("=== Rocket Launcher Calculations ===")
print("\nCO₂ from 10g baking soda at room temp (25°C), 1 atm:")
ideal_gas(n=0.119, P=1.0, T_celsius=25)

print("\nSame gas in sealed 0.5L bottle:")
ideal_gas(n=0.119, V=0.5, T_celsius=25)
```

## Putting It Together: Launch Engineering

```python
def rocket_launch_calc(grams_baking_soda, nozzle_diameter_cm, temp_celsius=25):
    """Calculate rocket launch parameters."""
    R = 0.0821
    T = temp_celsius + 273.15
    
    # Moles of CO₂ produced (1:1 with NaHCO₃)
    moles_co2 = grams_baking_soda / 84.0
    
    # Volume at 1 atm
    volume_L = moles_co2 * R * T / 1.0
    volume_mL = volume_L * 1000
    
    # Thrust estimate (simplified)
    nozzle_area = 3.14159 * (nozzle_diameter_cm / 2) ** 2  # cm²
    # More gas + smaller nozzle = more thrust
    relative_thrust = volume_mL / nozzle_area
    
    print(f"Baking soda: {grams_baking_soda}g")
    print(f"CO₂ produced: {moles_co2:.3f} mol = {volume_mL:.0f} mL")
    print(f"Nozzle: {nozzle_diameter_cm}cm diameter")
    print(f"Relative thrust: {relative_thrust:.0f} units")
    
    if relative_thrust > 500:
        print("⚠️  TOO MUCH — reduce baking soda or widen nozzle!")
    elif relative_thrust < 100:
        print("😴 Not enough — add more baking soda or narrow nozzle")
    else:
        print("✓ Good launch parameters!")

rocket_launch_calc(5, 0.5)   # Small amount, narrow nozzle
rocket_launch_calc(20, 0.5)  # Too much!
rocket_launch_calc(10, 1.0)  # Just right
```

## The "Whoa" Moment: The Imploding Can

Boil water in an empty soda can (steam pushes air out). Flip it upside down into cold water. The steam condenses instantly — volume drops — and atmospheric pressure CRUSHES the can flat with a loud BANG.

No chemicals needed. Just gas law physics. The can implodes because the gas inside suddenly occupies almost zero volume, and the outside air pressure (14.7 psi) has nothing pushing back.

## The Working Kit Design

1. **Reaction chamber** — bottle with pressure-release valve (Sam's requirement)
2. **Measured packets** — pre-calculated baking soda + citric acid amounts
3. **Balloon capture** — stretches over bottle mouth to collect gas safely
4. **Nozzle attachments** — 3 sizes to experiment with thrust
5. **Launch pad** — guides the balloon-rocket straight
6. **Calculation card** — PV=nRT worksheet to predict before launching

## What You Learned

- **Boyle's Law**: P₁V₁ = P₂V₂ (pressure and volume trade off)
- **Charles's Law**: V₁/T₁ = V₂/T₂ (heat expands gas)
- **Ideal Gas Law**: PV = nRT (the master equation)
- **Gas from reactions** can be predicted with stoichiometry + gas laws
- **Engineering** means calculating before building (no more exploding bottles)

Gas launches are fun, but the next kit involves something subtler: making electricity from chemistry. Electrons flowing between metals — that's redox.

---

[← Chapter 8: pH](chapter-08-ph.md) | [Chapter 10: Electron Transfer →](chapter-10-redox.md)
