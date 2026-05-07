# Chapter 5: Fairness & Symmetry

[← Chapter 4: Debugging](chapter-04-debugging.md) | [Chapter 6: Job-Shop Scheduling →](chapter-06-job-shop.md)

---

## The Problem

The schedule is balanced by total shifts. But Nurse Johnson always gets weekends off while Nurse Williams always works Saturday night. The solver found an optimal solution — but it's the *same* optimal solution every time. It has no reason to vary.

With 200 nurses at Memorial General, this becomes a real issue. The solver picks favorites — not intentionally, but because its internal search order is deterministic. Nurse 0 gets first pick. Nurse 199 gets the leftovers.

## Symmetry in Optimization

When multiple solutions have the same objective value, the solver picks one arbitrarily. This creates **unfair symmetry** — some nurses consistently get better assignments because of their index.

Solutions:

1. **Rotate the objective** — change what "good" means each week
2. **Add fairness constraints** — explicitly balance undesirable shifts
3. **Break symmetry** — randomize the solver's search order
4. **Track history** — use last week's schedule to inform this week's

## Approach 1: Balance Night Shifts

```python
from ortools.sat.python import cp_model

def schedule_fair_nights():
    model = cp_model.CpModel()

    num_nurses = 12
    num_days = 7
    num_shifts = 3
    nurses = range(num_nurses)
    days = range(num_days)
    shifts = range(num_shifts)
    nurses_per_shift = [3, 3, 2]
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

    # Hard constraints (abbreviated — same as before)
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
        model.add(sum(works[(n, d)] for d in days) <= 5)

    # --- Fairness: balance night shifts ---
    night_count = {}
    for n in nurses:
        night_count[n] = model.new_int_var(0, 7, f"nights_{n}")
        model.add(night_count[n] == sum(x[(n, d, NIGHT)] for d in days))

    # Minimize the maximum night shifts any nurse works
    max_nights = model.new_int_var(0, 7, "max_nights")
    min_nights = model.new_int_var(0, 7, "min_nights")
    for n in nurses:
        model.add(max_nights >= night_count[n])
        model.add(min_nights <= night_count[n])

    # --- Fairness: balance weekend work ---
    SAT, SUN = 5, 6
    weekend_count = {}
    for n in nurses:
        weekend_count[n] = model.new_int_var(0, 2, f"weekends_{n}")
        model.add(weekend_count[n] == works[(n, SAT)] + works[(n, SUN)])

    max_weekends = model.new_int_var(0, 2, "max_weekends")
    min_weekends = model.new_int_var(0, 2, "min_weekends")
    for n in nurses:
        model.add(max_weekends >= weekend_count[n])
        model.add(min_weekends <= weekend_count[n])

    # Objective: minimize unfairness
    model.minimize(
        (max_nights - min_nights) * 10 +
        (max_weekends - min_weekends) * 8 +
        max_nights * 3  # Also minimize total night burden
    )

    # Solve
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"✓ Fair schedule (objective: {solver.objective_value})")
        print(f"  Night spread: {solver.value(min_nights)}-{solver.value(max_nights)}")
        print(f"  Weekend spread: {solver.value(min_weekends)}-{solver.value(max_weekends)}\n")

        for n in nurses:
            nights = solver.value(night_count[n])
            weekends = solver.value(weekend_count[n])
            print(f"  Nurse {n:>2}: {nights} nights, {weekends} weekend days")

schedule_fair_nights()
```

## Approach 2: Historical Fairness

Real fairness spans weeks. If Nurse A worked 3 nights last week, they should get fewer this week.

```python
def schedule_with_history(last_week_nights: dict):
    """
    last_week_nights: {nurse_id: number_of_night_shifts_last_week}
    """
    model = cp_model.CpModel()
    # ... (setup) ...

    # Cumulative night count (last week + this week)
    cumulative_nights = {}
    for n in nurses:
        this_week = sum(x[(n, d, NIGHT)] for d in days)
        cumulative_nights[n] = model.new_int_var(0, 14, f"cum_nights_{n}")
        model.add(cumulative_nights[n] == last_week_nights.get(n, 0) + this_week)

    # Minimize max cumulative nights
    max_cum = model.new_int_var(0, 14, "max_cum_nights")
    for n in nurses:
        model.add(max_cum >= cumulative_nights[n])

    model.minimize(max_cum)
    # ...
```

This naturally rotates night shifts — nurses who worked nights last week get priority for day shifts this week.

## Approach 3: Randomized Symmetry Breaking

Add random preferences to break ties differently each run:

```python
import random

def schedule_with_randomization():
    model = cp_model.CpModel()
    # ... (setup + hard constraints) ...

    # Random tie-breaking: small random penalties
    random.seed()  # Different each run
    penalty = 0
    for n in nurses:
        for d in days:
            for s in shifts:
                # Random weight between 0 and 1
                weight = random.randint(0, 100)
                penalty += x[(n, d, s)] * weight

    # Main objective + tiny random perturbation
    model.minimize(main_objective * 10000 + penalty)
```

The random penalties are small enough not to affect the real objective but large enough to break symmetry. Different runs produce different (equally good) schedules.

## Approach 4: Nurse Preferences

Let nurses express preferences, then balance satisfaction:

```python
# Preferences: 1 = want to work, -1 = prefer off, 0 = no preference
preferences = {
    (0, 5, MORNING): -1,   # Nurse 0 prefers Saturday morning off
    (0, 6, MORNING): -1,   # Nurse 0 prefers Sunday morning off
    (3, 0, NIGHT): 1,      # Nurse 3 likes Monday nights
    (7, 5, AFTERNOON): -1, # Nurse 7 prefers Saturday afternoon off
    # ...
}

# Satisfaction score per nurse
satisfaction = {}
for n in nurses:
    nurse_prefs = []
    for (pn, pd, ps), pref in preferences.items():
        if pn == n:
            if pref == 1:
                nurse_prefs.append(x[(n, pd, ps)])      # +1 if assigned
            elif pref == -1:
                nurse_prefs.append(x[(n, pd, ps)] * -1) # -1 if assigned
    satisfaction[n] = model.new_int_var(-10, 10, f"sat_{n}")
    if nurse_prefs:
        model.add(satisfaction[n] == sum(nurse_prefs))
    else:
        model.add(satisfaction[n] == 0)

# Maximize minimum satisfaction (Rawlsian fairness)
min_satisfaction = model.new_int_var(-10, 10, "min_sat")
for n in nurses:
    model.add(min_satisfaction <= satisfaction[n])

model.maximize(min_satisfaction)
```

This is **maximin fairness** — maximize the happiness of the least happy person.

## Scaling to 200 Nurses

Memorial General has 200 nurses. The model now has 200 × 7 × 3 = 4,200 variables. Still fast for CP-SAT, but fairness constraints add complexity.

Tips for scaling:

```python
# 1. Use symmetry breaking: fix one nurse's schedule to reduce search space
# (Only if nurses are truly interchangeable)
model.add(x[(0, 0, MORNING)] == 1)  # Nurse 0 works Monday morning

# 2. Limit the search time and accept near-optimal
solver.parameters.max_time_in_seconds = 30.0

# 3. Use solution hints from last week's schedule
for n in nurses:
    for d in days:
        for s in shifts:
            if last_week_solution.get((n, d, s)):
                model.add_hint(x[(n, d, s)], 1)

# 4. Use workers (parallel search)
solver.parameters.num_workers = 8
```

## The Fairness Metrics Dashboard

```python
def print_fairness_report(solver, nurses, days, shifts, x, works):
    """Print fairness metrics after solving."""
    NIGHT = 2
    SAT, SUN = 5, 6

    night_counts = [sum(solver.value(x[(n, d, NIGHT)]) for d in days) for n in nurses]
    weekend_counts = [solver.value(works[(n, SAT)]) + solver.value(works[(n, SUN)]) for n in nurses]
    total_counts = [sum(solver.value(works[(n, d)]) for d in days) for n in nurses]

    print("Fairness Report:")
    print(f"  Total shifts:  min={min(total_counts)}, max={max(total_counts)}, "
          f"std={std(total_counts):.2f}")
    print(f"  Night shifts:  min={min(night_counts)}, max={max(night_counts)}, "
          f"std={std(night_counts):.2f}")
    print(f"  Weekend days:  min={min(weekend_counts)}, max={max(weekend_counts)}, "
          f"std={std(weekend_counts):.2f}")

def std(values):
    """Standard deviation."""
    mean = sum(values) / len(values)
    return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
```

## Key Concepts

| Concept | What It Means |
|---|---|
| **Symmetry** | Multiple equally-good solutions; solver picks arbitrarily |
| **Fairness constraint** | Explicitly balance undesirable assignments |
| **Maximin** | Maximize the minimum (help the worst-off person) |
| **Historical balance** | Use past data to inform current optimization |
| **Symmetry breaking** | Add constraints/randomness to explore different solutions |
| **Solution hints** | Suggest a starting point to speed up search |

## What's Next

ShiftRight lands a new client — a manufacturing plant. The problem isn't "who works when" but "which job runs on which machine, and in what order." Tasks have durations, dependencies, and machines can only do one thing at a time.

Time to learn job-shop scheduling.

---

[← Chapter 4: Debugging](chapter-04-debugging.md) | [Chapter 6: Job-Shop Scheduling →](chapter-06-job-shop.md)
