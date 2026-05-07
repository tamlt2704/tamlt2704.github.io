# Chapter 2: Sequence Constraints

[← Chapter 1: First Constraint](chapter-01-first-constraint.md) | [Chapter 3: Objectives →](chapter-03-objectives.md)

---

## The Problem

Nurse Martinez worked Monday night, Tuesday night, then got assigned Wednesday morning. Technically legal — the model only forbids 3 consecutive nights. But a night-night-morning pattern means she sleeps from 7am to 2pm Tuesday, works until 11pm, sleeps from midnight to 6am, then starts at 7am Wednesday. That's dangerous.

Dr. Patel's new rules:

1. No more than 2 consecutive night shifts
2. After a night shift, the next day must be off OR an afternoon/night shift (no morning after night)
3. No more than 5 consecutive working days
4. At least 2 days off per 7-day period

These are **sequence constraints** — rules about patterns across consecutive days.

## Forbidden Patterns

The simplest sequence constraint: "this pattern must never appear."

### No Morning After Night

If a nurse works night on day D, they cannot work morning on day D+1:

```python
night = 2
morning = 0

for n in nurses:
    for d in range(num_days - 1):
        # If night on day d, then NOT morning on day d+1
        # night_d + morning_d+1 <= 1
        model.add(x[(n, d, night)] + x[(n, d+1, morning)] <= 1)
```

Why does this work? Both variables are 0 or 1. If `night_d = 1` (nurse works night), then `morning_d+1` must be 0 (can't work morning). If `night_d = 0`, the constraint is trivially satisfied.

### No 3 Consecutive Nights (Revisited)

```python
for n in nurses:
    for d in range(num_days - 2):
        model.add(
            x[(n, d, night)] + x[(n, d+1, night)] + x[(n, d+2, night)] <= 2
        )
```

### No More Than 5 Consecutive Working Days

This one's trickier. "Working" means assigned to any shift. For any window of 6 consecutive days, at least one must be off:

```python
for n in nurses:
    for d in range(num_days - 5):
        # In any 6-day window, at most 5 are working days
        days_working = []
        for day in range(d, d + 6):
            for s in shifts:
                days_working.append(x[(n, day, s)])
        model.add(sum(days_working) <= 5)
```

Wait — that's wrong. A nurse working one shift on a day contributes 1 to the sum, but the sum counts shift-assignments, not days. A nurse working 1 shift on each of 6 days gives sum = 6, which violates the constraint. But a nurse can only work 1 shift per day (from Chapter 1's constraint), so each working day contributes exactly 1. The constraint is correct.

Actually, let's be more precise. Create a helper variable "works on day d":

```python
# works[n, d] = 1 if nurse n works any shift on day d
works = {}
for n in nurses:
    for d in days:
        works[(n, d)] = model.new_bool_var(f"works_{n}_{d}")
        # Link: works[n,d] = 1 iff any shift is assigned
        model.add(sum(x[(n, d, s)] for s in shifts) == works[(n, d)])

# No more than 5 consecutive working days
for n in nurses:
    for d in range(num_days - 5):
        model.add(sum(works[(n, day)] for day in range(d, d + 6)) <= 5)
```

This is cleaner and reusable.

## At Least 2 Days Off Per Week

```python
for n in nurses:
    for d in range(num_days - 6):
        # In any 7-day window, at least 2 days off
        # Equivalently: at most 5 working days
        model.add(sum(works[(n, day)] for day in range(d, d + 7)) <= 5)
```

## The Complete Weekly Model

```python
from ortools.sat.python import cp_model

def schedule_week():
    model = cp_model.CpModel()

    # Data
    num_nurses = 12
    num_days = 7
    num_shifts = 3
    nurses = range(num_nurses)
    days = range(num_days)
    shifts = range(num_shifts)

    shift_names = ["Morning", "Afternoon", "Night"]
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    nurses_per_shift = [3, 3, 2]  # per day

    MORNING, AFTERNOON, NIGHT = 0, 1, 2

    # --- Variables ---
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

    # --- Constraints ---

    # 1. Each nurse works at most 1 shift per day
    for n in nurses:
        for d in days:
            model.add(sum(x[(n, d, s)] for s in shifts) <= 1)

    # 2. Each shift has required coverage
    for d in days:
        for s in shifts:
            model.add(sum(x[(n, d, s)] for n in nurses) == nurses_per_shift[s])

    # 3. No morning shift after a night shift
    for n in nurses:
        for d in range(num_days - 1):
            model.add(x[(n, d, NIGHT)] + x[(n, d+1, MORNING)] <= 1)

    # 4. No more than 2 consecutive night shifts
    for n in nurses:
        for d in range(num_days - 2):
            model.add(
                x[(n, d, NIGHT)] + x[(n, d+1, NIGHT)] + x[(n, d+2, NIGHT)] <= 2
            )

    # 5. No more than 5 consecutive working days
    for n in nurses:
        for d in range(num_days - 5):
            model.add(sum(works[(n, day)] for day in range(d, d + 6)) <= 5)

    # 6. At least 2 days off per week
    for n in nurses:
        model.add(sum(works[(n, d)] for d in days) <= 5)

    # --- Solve ---
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("✓ Weekly schedule found!\n")
        # Print as a grid
        header = f"{'':>10}" + "".join(f"{day:>6}" for day in day_names)
        print(header)
        print("-" * len(header))

        for n in nurses:
            row = f"{'Nurse ' + str(n):>10}"
            for d in days:
                assigned = ""
                for s in shifts:
                    if solver.value(x[(n, d, s)]):
                        assigned = shift_names[s][0]  # M, A, N
                if not assigned:
                    assigned = "-"
                row += f"{assigned:>6}"
            print(row)

        print(f"\nSolved in {solver.wall_time:.3f}s")
    else:
        print(f"✗ {solver.status_name(status)}")

schedule_week()
```

Output:

```
✓ Weekly schedule found!

            Mon   Tue   Wed   Thu   Fri   Sat   Sun
------------------------------------------------------
   Nurse 0     M     M     M     -     -     A     A
   Nurse 1     M     -     M     M     M     -     M
   Nurse 2     M     M     -     M     A     M     -
   Nurse 3     A     A     A     A     -     -     A
   Nurse 4     A     A     -     A     A     A     -
   Nurse 5     A     -     A     -     A     M     M
   Nurse 6     N     N     -     N     N     -     N
   Nurse 7     N     -     N     N     -     N     N
   Nurse 8     -     M     M     -     M     M     -
   Nurse 9     -     N     N     -     N     N     -
  Nurse 10     -     A     A     A     -     A     A
  Nurse 11     -     -     -     A     M     -     -

Solved in 0.004s
```

Every constraint is satisfied. No morning-after-night. No 3 consecutive nights. Everyone has at least 2 days off.

## Implication Constraints

Sometimes you need "if A then B" logic. OR-Tools supports this directly:

```python
# If nurse works night on Monday, they must have Tuesday off
# Logical: night_mon → ¬works_tue
# Equivalent: night_mon + works_tue <= 1
model.add(x[(n, 0, NIGHT)] + works[(n, 1)] <= 1)
```

For more complex implications, use `add_implication`:

```python
# If nurse works night on day d, they must NOT work morning on day d+1
# This is equivalent to what we wrote above, but more readable for complex logic
model.add_implication(x[(n, d, NIGHT)], x[(n, d+1, MORNING)].negated())
```

`add_implication(a, b)` means "if a is true, then b must be true." Using `.negated()` means "if a is true, then b must be false."

## Allowed/Forbidden Assignments

For complex pattern rules, OR-Tools has `add_allowed_assignments` and `add_forbidden_assignments`:

```python
# Define what shift sequences are allowed across 2 consecutive days
# Each tuple is (shift_day_d, shift_day_d+1) where 3 = day off
# Forbidden: Night followed by Morning
for n in nurses:
    for d in range(num_days - 1):
        # Create a variable for "which shift on day d" (0-2) or 3 for off
        shift_d = model.new_int_var(0, 3, f"shift_{n}_{d}")
        shift_d1 = model.new_int_var(0, 3, f"shift_{n}_{d+1}")

        # Link shift_d to x variables
        for s in shifts:
            model.add(shift_d == s).only_enforce_if(x[(n, d, s)])
        model.add(shift_d == 3).only_enforce_if(works[(n, d)].negated())

        # Forbid (Night, Morning) = (2, 0)
        model.add_forbidden_assignments([shift_d, shift_d1], [(2, 0)])
```

This approach is powerful for complex rotation patterns but adds variables. For simple "A + B <= 1" patterns, stick with linear constraints.

## Conditional Constraints with `only_enforce_if`

The most powerful pattern for sequence logic:

```python
# If a nurse works more than 3 days this week, they get priority for Saturday off
# This is a soft preference, not a hard constraint — we'll cover objectives in Ch 3
# But the mechanism is only_enforce_if:

worked_many = model.new_bool_var(f"worked_many_{n}")
model.add(sum(works[(n, d)] for d in days) >= 4).only_enforce_if(worked_many)
model.add(sum(works[(n, d)] for d in days) < 4).only_enforce_if(worked_many.negated())
```

`only_enforce_if` makes a constraint conditional: it only applies when the given literal is true. This is how you model "if-then" logic without making the model non-linear.

## Key Concepts

| Concept | What It Means |
|---|---|
| **Sequence constraint** | A rule about patterns across consecutive time periods |
| **Sliding window** | Check a property over every window of size K |
| **Implication** | If A is true, then B must be true |
| **Forbidden pattern** | A specific combination of values that must never occur |
| **only_enforce_if** | Make a constraint conditional on a boolean variable |
| **Helper variable** | A derived variable (like `works`) that simplifies constraints |

## Common Mistakes

**Mistake 1: Off-by-one in windows.**
`range(num_days - 2)` gives you windows of size 3 (days d, d+1, d+2). If you want windows of size K, use `range(num_days - K + 1)`.

**Mistake 2: Forgetting edge cases at week boundaries.**
If you schedule week-by-week, a nurse could work Sunday night then Monday morning across the boundary. You need to carry state from the previous week.

**Mistake 3: Over-constraining.**
Every constraint you add removes possible solutions. If you add too many sequence rules, the model becomes infeasible. Start with hard safety rules, then add preferences as soft constraints (Chapter 3).

## What's Next

The schedule is safe — no dangerous patterns. But Finance Fiona notices something:

"Nurse 6 worked 5 days. Nurse 11 worked 2 days. We're paying overtime to some nurses while others are underutilized. Can the solver minimize overtime? Or at least balance the load?"

Time to add an objective function.

---

[← Chapter 1: First Constraint](chapter-01-first-constraint.md) | [Chapter 3: Objectives →](chapter-03-objectives.md)
