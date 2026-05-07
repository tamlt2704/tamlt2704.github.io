# Chapter 4: Debugging Infeasibility

[← Chapter 3: Objectives](chapter-03-objectives.md) | [Chapter 5: Fairness & Symmetry →](chapter-05-fairness.md)

---

## The Problem

Monday morning. Three nurses called in sick. You run the scheduler:

```
✗ INFEASIBLE
```

But you *know* a schedule exists. Last week, when two nurses were out, the charge nurse made a schedule by hand in 20 minutes. The solver says it's impossible. Someone is wrong.

Spoiler: it's your model.

## Why Models Become Infeasible

Infeasibility means: no assignment of variables satisfies ALL constraints simultaneously. Common causes:

1. **Arithmetic impossibility** — not enough resources (Chapter 1's 8 nurses / 9 slots)
2. **Conflicting constraints** — two rules that can't both be true
3. **Over-constrained edge cases** — rules that work for 12 nurses but fail for 9
4. **Data errors** — a nurse marked as unavailable who shouldn't be

The solver won't tell you *which* constraints conflict. It just says "no." Your job is to find out why.

## Strategy 1: Binary Search on Constraints

Remove half the constraints. Does it solve? If yes, the conflict is in the removed half. If no, it's in the remaining half. Repeat.

```python
def debug_infeasible(model, constraints_by_name):
    """Find minimal set of conflicting constraints."""
    solver = cp_model.CpSolver()

    # Try removing groups of constraints
    for name, constraint_list in constraints_by_name.items():
        # Create a copy without this group
        test_model = cp_model.CpModel()
        # ... rebuild without constraint_list ...
        status = solver.solve(test_model)
        if status != cp_model.INFEASIBLE:
            print(f"Removing '{name}' makes it feasible!")
```

This is tedious. Let's do better.

## Strategy 2: Soft Constraint Relaxation

Turn every hard constraint into a soft constraint with a penalty. The solver will violate the minimum number of constraints to find a solution. The violated constraints are your conflict.

```python
from ortools.sat.python import cp_model

def debug_with_relaxation():
    model = cp_model.CpModel()

    num_nurses = 9  # 3 called in sick!
    num_days = 7
    num_shifts = 3
    nurses = range(num_nurses)
    days = range(num_days)
    shifts = range(num_shifts)
    nurses_per_shift = [3, 3, 2]  # Still need 8 per day
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

    # Hard: one shift per day (this is logical, can't relax)
    for n in nurses:
        for d in days:
            model.add(sum(x[(n, d, s)] for s in shifts) <= 1)

    # --- Relaxable constraints with violation indicators ---
    violations = []
    violation_names = []

    # Coverage: each shift needs nurses (RELAXABLE)
    coverage_violations = {}
    for d in days:
        for s in shifts:
            # Allow under-staffing, but track it
            shortfall = model.new_int_var(0, nurses_per_shift[s], f"short_{d}_{s}")
            model.add(
                sum(x[(n, d, s)] for n in nurses) + shortfall == nurses_per_shift[s]
            )
            violations.append(shortfall * 100)  # Heavy penalty
            violation_names.append(f"Coverage day {d} shift {s}")

    # Max 5 days per week (RELAXABLE)
    for n in nurses:
        over_5 = model.new_int_var(0, 2, f"over5_{n}")
        model.add(sum(works[(n, d)] for d in days) <= 5 + over_5)
        violations.append(over_5 * 50)
        violation_names.append(f"Nurse {n} max 5 days")

    # No morning after night (RELAXABLE)
    for n in nurses:
        for d in range(num_days - 1):
            night_morning = model.new_bool_var(f"nm_{n}_{d}")
            model.add(
                x[(n, d, NIGHT)] + x[(n, d+1, MORNING)] <= 1 + night_morning
            )
            violations.append(night_morning * 30)
            violation_names.append(f"Nurse {n} night-morning day {d}")

    # No 3 consecutive nights (RELAXABLE)
    for n in nurses:
        for d in range(num_days - 2):
            triple_night = model.new_bool_var(f"tn_{n}_{d}")
            model.add(
                x[(n, d, NIGHT)] + x[(n, d+1, NIGHT)] + x[(n, d+2, NIGHT)] <= 2 + triple_night
            )
            violations.append(triple_night * 40)
            violation_names.append(f"Nurse {n} 3-nights day {d}")

    # Objective: minimize total violations
    model.minimize(sum(violations))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        total_penalty = solver.objective_value
        if total_penalty == 0:
            print("✓ No violations needed! Model is feasible.")
        else:
            print(f"⚠ Feasible with violations (penalty: {total_penalty}):\n")
            # Show which constraints were violated
            for i, v in enumerate(violations):
                # Extract the variable from the penalty expression
                # (simplified — in practice, track variables separately)
                pass

            # Better: check shortfalls directly
            print("Coverage shortfalls:")
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            shift_names = ["Morning", "Afternoon", "Night"]
            for d in days:
                for s in shifts:
                    short_var = model.get_int_var_from_proto_index(
                        # This is pseudocode — actual API differs
                    )
            # Let's just print the schedule and check manually
            print("\nSchedule (with potential violations):")
            for n in nurses:
                total = solver.value(sum(works[(n, d)] for d in days))
                # Actually, sum of solver values:
                total = sum(solver.value(works[(n, d)]) for d in days)
                print(f"  Nurse {n}: {total} days")

    print(f"\n  9 nurses × 5 max days = 45 available slots")
    print(f"  8 shifts/day × 7 days = 56 required slots")
    print(f"  Deficit: 11 shifts cannot be covered!")

debug_with_relaxation()
```

## The Real Diagnosis

The math is clear:
- 9 available nurses × 5 max working days = 45 nurse-days available
- (3 + 3 + 2) shifts × 7 days = 56 nurse-days required
- **Deficit: 11 shifts can't be covered**

No solver can create nurses that don't exist. The model is infeasible because the *problem* is infeasible given the current constraints.

## Strategy 3: Assumption-Based Debugging

CP-SAT supports **assumptions** — temporary constraints you can add and retract:

```python
from ortools.sat.python import cp_model

def debug_with_assumptions():
    model = cp_model.CpModel()

    # ... (build the model) ...

    # Add assumptions as boolean variables
    assume_full_coverage = model.new_bool_var("assume_full_coverage")
    assume_max_5_days = model.new_bool_var("assume_max_5_days")
    assume_no_night_morning = model.new_bool_var("assume_no_night_morning")

    # Make constraints conditional on assumptions
    for d in days:
        for s in shifts:
            model.add(
                sum(x[(n, d, s)] for n in nurses) >= nurses_per_shift[s]
            ).only_enforce_if(assume_full_coverage)

    for n in nurses:
        model.add(
            sum(works[(n, d)] for d in days) <= 5
        ).only_enforce_if(assume_max_5_days)

    # Solve with all assumptions active
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.INFEASIBLE:
        # Try dropping assumptions one at a time
        assumptions_to_try = [
            ("Full coverage", assume_full_coverage),
            ("Max 5 days", assume_max_5_days),
            ("No night→morning", assume_no_night_morning),
        ]

        for name, assumption in assumptions_to_try:
            # Solve without this assumption
            solver2 = cp_model.CpSolver()
            # Add all OTHER assumptions as hard constraints
            # Skip the current one
            # ... (rebuild or use assumptions parameter)
            pass
```

## The Practical Solution: Graceful Degradation

In production, infeasibility isn't a bug — it's a signal. Your system should handle it:

```python
def schedule_with_fallback(nurses_available, days, shifts, nurses_per_shift):
    """Try progressively relaxed models until one works."""

    # Level 0: Full constraints
    model = build_full_model(nurses_available, days, shifts, nurses_per_shift)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return solver, "Full constraints satisfied"

    # Level 1: Allow 6 days per week (instead of 5)
    model = build_model_relaxed_days(nurses_available, days, shifts, nurses_per_shift, max_days=6)
    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return solver, "⚠ Some nurses working 6 days (overtime required)"

    # Level 2: Reduce coverage requirements
    reduced_coverage = [max(1, n - 1) for n in nurses_per_shift]
    model = build_model_relaxed_days(nurses_available, days, shifts, reduced_coverage, max_days=6)
    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return solver, "⚠⚠ Reduced coverage + overtime"

    # Level 3: Emergency — drop sequence constraints
    model = build_emergency_model(nurses_available, days, shifts, reduced_coverage)
    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return solver, "🚨 Emergency schedule — safety constraints relaxed"

    return None, "🚨🚨 Cannot schedule — need more staff"
```

## Sufficient Statistics Check

Before even running the solver, check basic feasibility:

```python
def check_feasibility(num_nurses, num_days, nurses_per_shift, max_days_per_nurse):
    """Quick arithmetic check before solving."""
    total_slots_needed = sum(nurses_per_shift) * num_days
    total_slots_available = num_nurses * max_days_per_nurse

    print(f"Slots needed:    {total_slots_needed}")
    print(f"Slots available: {total_slots_available}")

    if total_slots_available < total_slots_needed:
        deficit = total_slots_needed - total_slots_available
        print(f"⚠ Deficit of {deficit} shifts. Model WILL be infeasible.")
        print(f"  Options:")
        print(f"    - Add {deficit // num_days + 1} more nurses")
        print(f"    - Increase max days to {total_slots_needed // num_nurses + 1}")
        print(f"    - Reduce coverage by {deficit // num_days + 1} per day")
        return False
    else:
        surplus = total_slots_available - total_slots_needed
        print(f"✓ Surplus of {surplus} slots. Feasibility likely (not guaranteed).")
        return True

# With 3 sick nurses:
check_feasibility(9, 7, [3, 3, 2], 5)
```

Output:

```
Slots needed:    56
Slots available: 45
⚠ Deficit of 11 shifts. Model WILL be infeasible.
  Options:
    - Add 2 more nurses
    - Increase max days to 7
    - Reduce coverage by 2 per day
```

Note: passing the arithmetic check doesn't guarantee feasibility. Sequence constraints (no night→morning, no 3 consecutive nights) further restrict the solution space. But failing the arithmetic check guarantees infeasibility.

## Solver Logging

Enable logging to see what the solver is doing:

```python
solver = cp_model.CpSolver()
solver.parameters.log_search_progress = True
solver.parameters.max_time_in_seconds = 5.0

status = solver.solve(model)
```

For infeasible models, the log shows the solver exhausting the search space:

```
...
#Conflicts  #Branches  #Propagations  ...
     1247       3891         89234    ...
...
Status: INFEASIBLE (proven)
```

"Proven" means the solver checked every possibility. It's not a timeout — it's a mathematical proof that no solution exists.

## Key Concepts

| Concept | What It Means |
|---|---|
| **Infeasibility** | No solution satisfies all constraints |
| **Arithmetic check** | Quick supply/demand calculation before solving |
| **Constraint relaxation** | Turn hard constraints into soft ones to find conflicts |
| **Graceful degradation** | Try progressively weaker models |
| **Assumptions** | Temporary constraints that can be retracted |
| **Proven infeasible** | Solver exhaustively verified no solution exists |

## The Debugging Checklist

When the solver says INFEASIBLE:

1. **Check the arithmetic.** Supply ≥ demand?
2. **Check the data.** Are availability flags correct? Any typos in nurse IDs?
3. **Remove constraints one group at a time.** Which group makes it feasible?
4. **Use relaxation.** Which constraints get violated in the relaxed solution?
5. **Check edge cases.** Does the model work for 12 nurses but fail for 9? Why?

## What's Next

The scheduler handles sick days gracefully now. But a new complaint arrives from the nursing staff:

"Nurse Johnson always gets weekends off. Nurse Williams always works Saturday night. The schedule is technically fair on paper — everyone works 4-5 days — but the *quality* of those days isn't equal."

Time to tackle fairness, symmetry breaking, and multi-dimensional balance.

---

[← Chapter 3: Objectives](chapter-03-objectives.md) | [Chapter 5: Fairness & Symmetry →](chapter-05-fairness.md)
