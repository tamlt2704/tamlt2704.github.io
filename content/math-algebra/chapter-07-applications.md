# Chapter 8: Real-World Applications

## Linear Models

### Example: Phone Plan

Monthly cost = `30 base + `0.10 per text

```
C(t) = 30 + 0.10t

At 200 texts: C(200) = 30 + 20 = $50
Break-even with $55 plan: 30 + 0.10t = 55 → t = 250 texts
```

### Example: Distance-Rate-Time

```
d = rt

Two cars leave same point, opposite directions at 60 and 45 mph.
When are they 420 miles apart?
60t + 45t = 420 → 105t = 420 → t = 4 hours
```

## Quadratic Models

### Example: Projectile

Ball thrown up at 20 m/s from 5m height:

```
h(t) = -5t² + 20t + 5

Max height: t = -20/(2×-5) = 2s
h(2) = -20 + 40 + 5 = 25 m

Hits ground: -5t² + 20t + 5 = 0
t = (-20 ± √(400+100))/-10 = (-20 ± 22.36)/-10
t = 4.24 s (positive answer)
```

### Example: Area Optimization

Fence 3 sides of a rectangle with 100m of fencing (wall on 4th side):

```
2w + l = 100 → l = 100 - 2w
A = w × l = w(100-2w) = 100w - 2w²

Max at w = -100/(2×-2) = 25m
l = 50m, A_max = 1250 m²
```

## Exponential Models

### Example: Population Growth

```
P(t) = P₀ × (1 + r)ᵗ

City of 50,000 growing 3%/year:
P(10) = 50000(1.03)¹⁰ = 67,196
```

### Example: Compound Interest

```
A = P(1 + r/n)^(nt)

$1000 at 5% compounded monthly for 10 years:
A = 1000(1 + 0.05/12)^120 = $1,647.01
```

## Systems of Equations (Real World)

### Example: Mixture Problem

Mix 20% and 50% acid solutions to get 10L of 35%:

```
x + y = 10         (total volume)
0.20x + 0.50y = 3.5  (acid content)

x = 10 - y
0.20(10-y) + 0.50y = 3.5
2 - 0.20y + 0.50y = 3.5
0.30y = 1.5 → y = 5L of 50%, x = 5L of 20%
```

## Practice Problems

**P1.** A taxi charges `3 base + `2.50/mile. Write cost function. Cost for 8 miles?

> **Solution:**
> C(m) = 3 + 2.50m
> C(8) = 3 + 20 = $23

**P2.** Investment doubles every 7 years. Starting with $5000, value after 21 years?

> **Solution:**
> Doubles 3 times: 5000 × 2³ = $40,000

**P3.** Rectangle perimeter = 36. Express area as function of width. Maximum area?

> **Solution:**
> 2w + 2l = 36 → l = 18-w
> A(w) = w(18-w) = 18w - w²
> Max at w = 9: A = 81 (it's a square!)

**P4.** Store sells shirts (`15) and pants (`25). Sold 40 items for $700. How many of each?

> **Solution:**
> s + p = 40, 15s + 25p = 700
> 15(40-p) + 25p = 700 → 600 + 10p = 700 → p = 10
> s = 30 shirts, p = 10 pants
