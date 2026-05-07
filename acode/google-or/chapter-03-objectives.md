# Chapter 3: Objectives

[← Chapter 2: Sequences](chapter-02-sequences.md) | [Chapter 4: Debugging Infeasibility →](chapter-04-debugging.md)

---

## The Problem

The schedule is valid. No dangerous patterns. But look at the distribution:

```
Nurse 0:  5 shifts
Nurse 1:  5 shifts
Nurse 6:  5 shifts
Nurse 11: 2 shifts
Nurse 9:  3 shifts
```

Finance Fiona: "Nurses 0, 1, and 6 are hitting overtime. Nurses 9 and 11 are underutilized. We're paying 1.5x for overtime hours while some nurses want more shifts. This is costing us $12,000/month in unnecessary overtime."

The solver found *a* valid schedule. But not a *good* one. We need an objective.

## Hard vs Soft Constraints

Until now, every constraint was **hard** — violating it makes the schedule invalid. But "balance the workload" isn't binary. A schedule with a 1-shift difference between nurses is better than a 3-shift difference, but both are valid.

**Hard constraint:** Must be satisfied. "No morning after night."
**Soft constraint:** Should be satisfied. "Balance workload across nurses." Violations are penalized, not forbidden.

OR-Tools handles soft constraints through the **objective function** — a value the solver minimizes or maximizes.

## Minimizing Overtime

First approach: minimize the maximum number of shifts any nurse works.

```python
from ortools.sat.python import cp_model

def schedule_balanced():
    model = cp_model.CpModel()

    num_nurses = 12
    num_days = 7
    num_shifts = 3
    nurses = range(num_nurses)
    days = range(num_days)
    shifts = range(num_shifts)
    nurses_per_shift = [3, 3, 2]  # 8 shifts per day, 56 per week

    MORNING, AFTERNOON, NIGHT = 0, 1, 2

    # Variables
    x = {}
    for n in nurses:
        for d in days:
            for s in shifts:
                x[(n, d, s)] = model.new_bool_var(f"x_{n}_{d}_{s}")

    works = {}
    for n in nurses:
        for d in days:
            works[(n, d)] = model.new_bool_var(f"works_{n}_{d}")
            model.add(sum(x[(n, d, s)] for s in shifts) == works[(n, d)])

    # Hard constraints (same as before)
    for n in nurses:
        for d in days:
            model.add(sum(x[(n, d, s)] for s in shifts) <= 1)

    for d in days:
        for s in shifts:
            model.add(sum(x[(n, d, s)] for n in nurses) == nurses_per_shift[s])

    for n in nurses:
        for d in range(num_days - 1):
            model.add(x[(n, d, NIGHT)] + x[(n, d+1, MORNING)] <= 1)

    for n in nurses:
        for d in range(num_days - 2):
            model.add(
                x[(n, d, NIGHT)] + x[(n, d+1, NIGHT)] + x[(n, d+2, NIGHT)] <= 2
            )

    for n in nurses:
        model.add(sum(works[(n, d)] for d in days) <= 5)

    # --- Objective: minimize the spread ---
    # Total shifts per nurse
    total_shifts = {}
    for n in nurses:
        total_shifts[n] = model.new_int_var(0, num_days, f"total_{n}")
        model.add(total_shifts[n] == sum(works[(n, d)] for d in days))

    # Minimize the maximum shifts any nurse works
    max_shifts = model.new_int_var(0, num_days, "max_shifts")
    for n in nurses:
        model.add(max_shifts >= total_shifts[n])

    # Maximize the minimum shifts any nurse works
    min_shifts = model.new_int_var(0, num_days, "min_shifts")
    for n in nurses:
        model.add(min_shifts <= total_shifts[n])

    # Objective: minimize (max - min)
    model.minimize(max_shifts - min_shifts)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL:
        print(f"✓ Optimal schedule found! Spread: {solver.value(max_shifts) - solver.value(min_shifts)}")
        print(f"  Min shifts: {solver.value(min_shifts)}, Max shifts: {solver.value(max_shifts)}\n")

        for n in nurses:
            print(f"  Nurse {n:>2}: {solver.value(total_shifts[n])} shifts")
    else:
        print(f"Status: {solver.status_name(status)}")

schedule_balanced()
```

Output:

```
✓ Optimal schedule found! Spread: 1
  Min shifts: 4, Max shifts: 5

  Nurse  0: 5 shifts
  Nurse  1: 5 shifts
  Nurse  2: 5 shifts
  Nurse  3: 5 shifts
  Nurse  4: 5 shifts
  Nurse  5: 5 shifts
  Nurse  6: 5 shifts
  Nurse  7: 5 shifts
  Nurse  8: 4 shifts
  Nurse  9: 4 shifts
  Nurse 10: 4 shifts
  Nurse 11: 4 shifts
```

The math checks out: 8 shifts/day × 7 days = 56 total shifts. 56 ÷ 12 nurses = 4.67. So the best possible spread is 4-5 shifts. The solver found it.

## Weighted Objectives

Real life isn't one objective. Fiona wants low overtime. Dr. Patel wants safe patterns. Nurses want weekend days off. You need to combine multiple goals.

```python
# Weighted multi-objective
penalty = 0

# Penalty 1: Overtime (shifts > 4 per week cost extra)
overtime_threshold = 4
for n in nurses:
    overtime = model.new_int_var(0, num_days, f"overtime_{n}")
    model.add_max_equality(overtime, [total_shifts[n] - overtime_threshold, 0])
    penalty += overtime * 10  # weight: 10 per overtime shift

# Penalty 2: Weekend work (nurses prefer weekends off)
SAT, SUN = 5, 6
for n in nurses:
    penalty += works[(n, SAT)] * 3  # weight: 3 per Saturday shift
    penalty += works[(n, SUN)] * 3  # weight: 3 per Sunday shift

# Penalty 3: Night shifts (less desirable)
for n in nurses:
    for d in days:
        penalty += x[(n, d, NIGHT)] * 2  # weight: 2 per night shift

model.minimize(penalty)
```

The weights encode priorities:
- Overtime (10) matters most — it's expensive
- Weekend work (3) matters — nurses value time off
- Night shifts (2) are undesirable but necessary

## Soft Constraints as Penalties

Some constraints shouldn't be hard. "Every nurse gets at least one weekend day off" might be impossible during a staffing shortage. Make it soft:

```python
# Soft: prefer at least 1 weekend day off
for n in nurses:
    weekend_off = model.new_bool_var(f"weekend_off_{n}")
    # weekend_off = 1 if nurse has at least one weekend day off
    model.add(works[(n, SAT)] + works[(n, SUN)] <= 1).only_enforce_if(weekend_off)
    model.add(works[(n, SAT)] + works[(n, SUN)] >= 2).only_enforce_if(weekend_off.negated())

    # Penalize NOT having a weekend day off
    penalty += weekend_off.negated() * 20  # heavy penalty
```

Wait — that's getting complicated. Simpler approach:

```python
# Soft: penalize working both weekend days
for n in nurses:
    both_weekend = model.new_bool_var(f"both_weekend_{n}")
    model.add(works[(n, SAT)] + works[(n, SUN)] == 2).only_enforce_if(both_weekend)
    model.add(works[(n, SAT)] + works[(n, SUN)] <= 1).only_enforce_if(both_weekend.negated())
    penalty += both_weekend * 20
```

Actually, even simpler — since `works[(n, SAT)]` and `works[(n, SUN)]` are already 0/1:

```python
# Penalize each weekend day worked (already done above with weight 3)
# Add extra penalty for working BOTH days
for n in nurses:
    # If both are 1, their product is 1. But CP-SAT doesn't do multiplication directly.
    # Use: both = 1 iff SAT=1 AND SUN=1
    both_weekend = model.new_bool_var(f"both_weekend_{n}")
    model.add_bool_and([works[(n, SAT)], works[(n, SUN)]]).only_enforce_if(both_weekend)
    model.add_bool_or([works[(n, SAT)].negated(), works[(n, SUN)].negated()]).only_enforce_if(both_weekend.negated())
    penalty += both_weekend * 15
```

## The Practical Pattern

Here's the clean pattern for multi-objective scheduling:

```python
from ortools.sat.python import cp_model

def schedule_multi_objective():
    model = cp_model.CpModel()

    num_nurses = 12
    num_days = 7
    num_shifts = 3
    nurses = range(num_nurses)
    days = range(num_days)
    shifts = range(num_shifts)
    nurses_per_shift = [3, 3, 2]
    MORNING, AFTERNOON, NIGHT = 0, 1, 2
    SAT, SUN = 5, 6

    # Variables
    x = {}
    for n in nurses:
        for d in days:
            for s in shifts:
                x[(n, d, s)] = model.new_bool_var(f"x_{n}_{d}_{s}")

    works = {}
    for n in nurses:
        for d in days:
            works[(n, d)] = model.new_bool_var(f"works_{n}_{d}")
            model.add(sum(x[(n, d, s)] for s in shifts) == works[(n, d)])

    # Hard constraints
    for n in nurses:
        for d in days:
            model.add(sum(x[(n, d, s)] for s in shifts) <= 1)

    for d in days:
        for s in shifts:
            model.add(sum(x[(n, d, s)] for n in nurses) == nurses_per_shift[s])

    for n in nurses:
        for d in range(num_days - 1):
            model.add(x[(n, d, NIGHT)] + x[(n, d+1, MORNING)] <= 1)

    for n in nurses:
        for d in range(num_days - 2):
            model.add(x[(n, d, NIGHT)] + x[(n, d+1, NIGHT)] + x[(n, d+2, NIGHT)] <= 2)

    for n in nurses:
        model.add(sum(works[(n, d)] for d in days) <= 5)

    # Soft objectives (penalties to minimize)
    penalties = []

    # 1. Balance: penalize deviation from ideal (56/12 ≈ 4.67 shifts)
    for n in nurses:
        total = sum(works[(n, d)] for d in days)
        # Penalize having 5 shifts (above ideal)
        above = model.new_bool_var(f"above_{n}")
        model.add(total >= 5).only_enforce_if(above)
        model.add(total <= 4).only_enforce_if(above.negated())
        penalties.append(above * 5)

    # 2. Weekend: penalize weekend work
    for n in nurses:
        penalties.append(works[(n, SAT)] * 3)
        penalties.append(works[(n, SUN)] * 4)  # Sunday slightly worse

    # 3. Night shifts: distribute fairly
    night_count = {}
    for n in nurses:
        night_count[n] = model.new_int_var(0, 7, f"nights_{n}")
        model.add(night_count[n] == sum(x[(n, d, NIGHT)] for d in days))

    max_nights = model.new_int_var(0, 7, "max_nights")
    for n in nurses:
        model.add(max_nights >= night_count[n])
    penalties.append(max_nights * 8)  # Minimize worst-case night load

    # Objective
    model.minimize(sum(penalties))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"✓ Schedule found! (Objective: {solver.objective_value})")
        print(f"  Status: {solver.status_name(status)}\n")

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        shift_chars = ["M", "A", "N"]

        header = f"{'':>10}" + "".join(f"{d:>5}" for d in day_names) + "  Total"
        print(header)

        for n in nurses:
            row = f"{'Nurse ' + str(n):>10}"
            total = 0
            for d in days:
                ch = "-"
                for s in shifts:
                    if solver.value(x[(n, d, s)]):
                        ch = shift_chars[s]
                        total += 1
                row += f"{ch:>5}"
            row += f"  {total:>3}"
            print(row)

        print(f"\n  Max nights by any nurse: {solver.value(max_nights)}")
        print(f"  Solved in {solver.wall_time:.3f}s")
    else:
        print(f"✗ {solver.status_name(status)}")

schedule_multi_objective()
```

## Maximize vs Minimize

- `model.minimize(expr)` — find the solution with the smallest value of `expr`
- `model.maximize(expr)` — find the solution with the largest value of `expr`

You can only have ONE objective. To handle multiple goals, combine them into a single weighted sum (as above) or use lexicographic optimization (solve for the most important objective first, then fix it and optimize the next).

### Lexicographic Optimization

```python
# Step 1: Minimize overtime (most important)
model.minimize(total_overtime)
solver.solve(model)
best_overtime = solver.objective_value

# Step 2: Fix overtime, minimize weekend work
model.add(total_overtime <= best_overtime)
model.minimize(total_weekend_work)  # Replaces previous objective
solver.solve(model)
```

This guarantees overtime is optimal before considering weekend preferences.

## Objective Value Interpretation

```python
if status == cp_model.OPTIMAL:
    print(f"Proven optimal: {solver.objective_value}")
elif status == cp_model.FEASIBLE:
    print(f"Best found: {solver.objective_value}")
    print(f"Best possible: {solver.best_objective_bound}")
    gap = abs(solver.objective_value - solver.best_objective_bound) / max(1, abs(solver.objective_value))
    print(f"Optimality gap: {gap:.1%}")
```

- `OPTIMAL` means the solver proved no better solution exists
- `FEASIBLE` means it found a good solution but couldn't prove optimality (usually due to time limit)
- The **gap** tells you how far from optimal you might be

## Key Concepts

| Concept | What It Means |
|---|---|
| **Objective function** | A value to minimize or maximize |
| **Hard constraint** | Must be satisfied — violation = infeasible |
| **Soft constraint** | Preferred — violation = penalty in objective |
| **Weighted sum** | Combine multiple objectives with importance weights |
| **Lexicographic** | Optimize objectives in priority order |
| **Optimality gap** | How far the best solution might be from true optimal |

## Choosing Weights

Weights are the hardest part of multi-objective optimization. Some guidelines:

1. **Start with ratios.** If overtime costs $50/hour and weekend premium is $20/hour, use weights 50 and 20.
2. **Normalize.** If one penalty ranges 0-100 and another 0-5, the first dominates regardless of weight. Scale them.
3. **Iterate with stakeholders.** Show Fiona and Dr. Patel the results. "Is this schedule acceptable?" Adjust weights based on feedback.
4. **Use lexicographic for non-negotiables.** If safety always trumps cost, don't weight them — solve safety first.

## What's Next

You ship the balanced schedule. Monday morning, the solver returns:

```
✗ INFEASIBLE
```

Three nurses called in sick. The model says no valid schedule exists. But you *know* one exists — you just need to relax some constraints. Which ones? The solver won't tell you.

Time to learn how to debug infeasibility.

---

[← Chapter 2: Sequences](chapter-02-sequences.md) | [Chapter 4: Debugging Infeasibility →](chapter-04-debugging.md)
