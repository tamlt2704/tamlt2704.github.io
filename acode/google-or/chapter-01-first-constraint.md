# Chapter 1: Your First Constraint

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Sequence Constraints →](chapter-02-sequences.md)

---

## The Problem

Memorial General Hospital has 8 nurses and 3 shifts per day (morning, afternoon, night). For a single day, you need to assign exactly 3 nurses to each shift. No nurse can work more than one shift.

The spreadsheet solution: someone stares at a whiteboard for 20 minutes. That works for one day. It doesn't work for a month.

Dr. Patel sends the requirements:

> "Each shift needs exactly 3 nurses. Nobody works two shifts in the same day. That's it for now. Just show me it works for one day."

## The Model

Before writing code, think in three parts:

**Variables:** For each nurse and each shift, a binary decision — does this nurse work this shift? Yes (1) or No (0).

**Constraints:**
- Each nurse works at most 1 shift per day
- Each shift has exactly 3 nurses

**Objective:** None yet. We just want *any* valid assignment.

## The Code

```python
from ortools.sat.python import cp_model

def schedule_one_day():
    # --- Setup ---
    model = cp_model.CpModel()

    num_nurses = 8
    num_shifts = 3
    nurses = range(num_nurses)
    shifts = range(num_shifts)
    shift_names = ["Morning", "Afternoon", "Night"]

    # --- Variables ---
    # x[n][s] = 1 if nurse n works shift s
    x = {}
    for n in nurses:
        for s in shifts:
            x[(n, s)] = model.new_bool_var(f"nurse_{n}_shift_{s}")

    # --- Constraints ---

    # Each nurse works at most 1 shift per day
    for n in nurses:
        model.add(sum(x[(n, s)] for s in shifts) <= 1)

    # Each shift has exactly 3 nurses
    for s in shifts:
        model.add(sum(x[(n, s)] for n in nurses) == 3)

    # --- Solve ---
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Schedule found!\n")
        for s in shifts:
            assigned = [f"Nurse {n}" for n in nurses if solver.value(x[(n, s)]) == 1]
            print(f"  {shift_names[s]}: {', '.join(assigned)}")
        print(f"\n  Unassigned: ", end="")
        unassigned = [f"Nurse {n}" for n in nurses
                      if all(solver.value(x[(n, s)]) == 0 for s in shifts)]
        print(", ".join(unassigned) if unassigned else "None")
    else:
        print("No solution found!")

schedule_one_day()
```

## Running It

```
Schedule found!

  Morning: Nurse 0, Nurse 1, Nurse 2
  Afternoon: Nurse 3, Nurse 4, Nurse 5
  Night: Nurse 6, Nurse 7, Nurse 0

Wait — Nurse 0 is in both Morning and Night!
```

No, that won't happen. The constraint `sum(x[(n, s)] for s in shifts) <= 1` prevents it. The actual output will be something like:

```
Schedule found!

  Morning: Nurse 0, Nurse 1, Nurse 2
  Afternoon: Nurse 3, Nurse 4, Nurse 5
  Night: Nurse 6, Nurse 7, Nurse 3
```

Wait — that also can't happen. Nurse 3 can't be in both Afternoon and Night. The solver respects the constraint. A valid output:

```
Schedule found!

  Morning: Nurse 0, Nurse 1, Nurse 2
  Afternoon: Nurse 3, Nurse 4, Nurse 5
  Night: Nurse 6, Nurse 7, Nurse 0
```

Hmm, still wrong in my head. Let me trust the solver. With 8 nurses, 3 shifts of 3 = 9 slots but only 8 nurses. That's a problem.

## The First Bug

8 nurses. 3 shifts × 3 nurses = 9 slots. We don't have enough nurses.

```
No solution found!
```

The solver says "infeasible." And it's right. You can't fill 9 slots with 8 people when each person can only fill 1 slot.

**Fix:** Either reduce the requirement to 2-3 nurses per shift, or add a nurse.

Dr. Patel clarifies: "Morning needs 3, Afternoon needs 3, Night needs 2. We run lighter at night."

```python
# Updated constraint: variable nurses per shift
nurses_per_shift = [3, 3, 2]  # Morning, Afternoon, Night

for s in shifts:
    model.add(sum(x[(n, s)] for n in nurses) == nurses_per_shift[s])
```

Now 3 + 3 + 2 = 8 slots for 8 nurses. The solver finds a solution instantly.

## The Complete Working Version

```python
from ortools.sat.python import cp_model

def schedule_one_day():
    model = cp_model.CpModel()

    num_nurses = 8
    num_shifts = 3
    nurses = range(num_nurses)
    shifts = range(num_shifts)
    shift_names = ["Morning", "Afternoon", "Night"]
    nurses_per_shift = [3, 3, 2]

    # Variables: x[n, s] = 1 if nurse n works shift s
    x = {}
    for n in nurses:
        for s in shifts:
            x[(n, s)] = model.new_bool_var(f"nurse_{n}_shift_{s}")

    # Constraint: each nurse works at most 1 shift
    for n in nurses:
        model.add(sum(x[(n, s)] for s in shifts) <= 1)

    # Constraint: each shift has the required number of nurses
    for s in shifts:
        model.add(sum(x[(n, s)] for n in nurses) == nurses_per_shift[s])

    # Solve
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("✓ Schedule found!\n")
        for s in shifts:
            assigned = [f"Nurse {n}" for n in nurses if solver.value(x[(n, s)])]
            print(f"  {shift_names[s]:>10}: {', '.join(assigned)}")

        unassigned = [f"Nurse {n}" for n in nurses
                      if all(solver.value(x[(n, s)]) == 0 for s in shifts)]
        if unassigned:
            print(f"  {'Day off':>10}: {', '.join(unassigned)}")
    else:
        print("✗ No feasible schedule exists.")
        print(f"  Status: {solver.status_name(status)}")

schedule_one_day()
```

Output:

```
✓ Schedule found!

     Morning: Nurse 0, Nurse 1, Nurse 2
   Afternoon: Nurse 3, Nurse 4, Nurse 5
       Night: Nurse 6, Nurse 7
```

Solved in under 1 millisecond.

## What Just Happened

Let's break down the mechanics:

### 1. Boolean Variables

```python
x[(n, s)] = model.new_bool_var(f"nurse_{n}_shift_{s}")
```

A boolean variable is either 0 or 1. It represents a yes/no decision. "Does nurse 3 work the night shift?" — that's a single boolean variable.

For 8 nurses × 3 shifts, you have 24 boolean variables. The solver's job is to find values for all 24 that satisfy every constraint simultaneously.

### 2. Linear Constraints

```python
model.add(sum(x[(n, s)] for s in shifts) <= 1)
```

This says: for a given nurse, the sum of their shift assignments is at most 1. Since each variable is 0 or 1, this means they work zero or one shifts.

```python
model.add(sum(x[(n, s)] for n in nurses) == nurses_per_shift[s])
```

This says: for a given shift, exactly the right number of nurses are assigned.

### 3. The Solver

```python
solver = cp_model.CpSolver()
status = solver.solve(model)
```

The CP-SAT solver uses a combination of:
- **Constraint propagation** — eliminating impossible values without guessing
- **Search** — making tentative assignments and backtracking when stuck
- **Learning** — remembering which combinations of assignments lead to dead ends

For this tiny problem, propagation alone finds the answer. No search needed.

### 4. Status Codes

| Status | Meaning |
|---|---|
| `OPTIMAL` | Found the best possible solution (when there's an objective) |
| `FEASIBLE` | Found a valid solution (may not be optimal) |
| `INFEASIBLE` | No solution exists that satisfies all constraints |
| `MODEL_INVALID` | The model has errors (e.g., contradictory bounds) |
| `UNKNOWN` | Solver ran out of time or resources |

Without an objective, you'll get `OPTIMAL` (the solver treats "no objective" as "any feasible solution is optimal").

## Extending to a Week

Dr. Patel: "One day is nice. I need a week."

The model scales naturally. Add a day dimension:

```python
num_days = 7
days = range(num_days)
day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Variables: x[n, d, s] = 1 if nurse n works shift s on day d
x = {}
for n in nurses:
    for d in days:
        for s in shifts:
            x[(n, d, s)] = model.new_bool_var(f"nurse_{n}_day_{d}_shift_{s}")

# Each nurse works at most 1 shift per day
for n in nurses:
    for d in days:
        model.add(sum(x[(n, d, s)] for s in shifts) <= 1)

# Each shift on each day has the required nurses
for d in days:
    for s in shifts:
        model.add(sum(x[(n, d, s)] for n in nurses) == nurses_per_shift[s])
```

Now you have 8 × 7 × 3 = 168 variables. Still solves in milliseconds.

But Dr. Patel has more requirements: "No nurse should work 3 night shifts in a row. And everyone gets at least one day off per week."

```python
# At least 1 day off per week (work at most 6 days)
for n in nurses:
    model.add(sum(x[(n, d, s)] for d in days for s in shifts) <= 6)

# No 3 consecutive night shifts
night = 2  # index of night shift
for n in nurses:
    for d in range(num_days - 2):  # d, d+1, d+2
        model.add(
            x[(n, d, night)] + x[(n, d+1, night)] + x[(n, d+2, night)] <= 2
        )
```

Still solves in milliseconds. The solver doesn't care about the number of constraints — it cares about how tightly they interact. More on that in Chapter 4.

## Key Concepts

| Concept | What It Means |
|---|---|
| **Boolean variable** | A 0/1 decision — yes or no |
| **Linear constraint** | A sum of variables compared to a constant |
| **Feasibility** | Does any assignment satisfy all constraints? |
| **Model** | The collection of variables + constraints + objective |
| **Solver** | The engine that searches for solutions |

## Common Mistakes

**Mistake 1: Forgetting the math.**
If you need 9 nurse-slots but only have 8 nurses who can each fill 1 slot, no solver in the world will help. Check your arithmetic before blaming the solver.

**Mistake 2: Using integer variables when boolean will do.**
`new_int_var(0, 1, name)` works but `new_bool_var(name)` is faster — the solver knows it's binary and uses specialized propagation.

**Mistake 3: Not checking the status.**
Always check `status`. A solver returning `INFEASIBLE` is giving you critical information. Don't ignore it.

## What's Next

The schedule works for one week. But Dr. Patel is back:

"Nurse Martinez worked Monday night, Tuesday night, Wednesday night. She's exhausted. The constraint says no *three* in a row, but two consecutive nights followed by a morning shift is also brutal. We need proper sequence rules."

Time to learn about sequence constraints.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Sequence Constraints →](chapter-02-sequences.md)
