# Chapter 10: Performance Tuning

[← Chapter 9: VRP Constraints](chapter-09-vrp-constraints.md) | [Chapter 11: Incremental Solving →](chapter-11-incremental.md)

---

## The Problem

Memorial General scaled to 200 nurses. The CP-SAT model now has 200 × 28 × 3 = 16,800 variables (4-week schedule). The solver runs for 45 minutes and returns `FEASIBLE` — not `OPTIMAL`. Nadia: "We can't wait 45 minutes every time someone calls in sick."

Meanwhile, Tomás's VRP with 500 delivery locations takes 5 minutes to converge. "The drivers are waiting. I need routes in 30 seconds."

## CP-SAT: Solver Parameters

```python
solver = cp_model.CpSolver()

# Parallel search: use all CPU cores
solver.parameters.num_workers = 8

# Time limit
solver.parameters.max_time_in_seconds = 30.0

# Log progress (see improvement over time)
solver.parameters.log_search_progress = True

# Stop early if solution is "good enough"
# (within 5% of optimal)
solver.parameters.relative_gap_limit = 0.05
```

### Understanding the Log

```
#1   0.02s  obj:847  bounds:[612..847]  gap:27.7%
#2   0.15s  obj:723  bounds:[612..723]  gap:15.4%
#3   0.89s  obj:689  bounds:[618..689]  gap:10.3%
#4   3.21s  obj:654  bounds:[625..654]  gap:4.4%
```

- `obj` — best solution found so far
- `bounds` — proven lower bound (no solution can be better than this)
- `gap` — how far the best solution might be from optimal

When the gap is small enough for your use case, stop.

## Solution Hints

Give the solver a starting point — last week's schedule, a greedy heuristic, or the previous solution with small modifications:

```python
def solve_with_hint(model, x, previous_solution):
    """Use last week's schedule as a hint."""
    for (n, d, s), var in x.items():
        if (n, d, s) in previous_solution:
            model.add_hint(var, previous_solution[(n, d, s)])

    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 8
    solver.parameters.max_time_in_seconds = 30.0
    return solver.solve(model)
```

Hints don't constrain the solver — they just suggest where to start searching. A good hint can reduce solve time by 10-100x.

## Decision Strategy

Control the order in which the solver assigns variables:

```python
from ortools.sat.python import cp_model

# Prioritize night shift assignments (hardest to fill)
night_vars = [x[(n, d, NIGHT)] for n in nurses for d in days]
model.add_decision_strategy(
    night_vars,
    cp_model.CHOOSE_FIRST,           # Variable selection
    cp_model.SELECT_MAX_VALUE        # Value selection (try 1 first)
)
```

Strategies:
- `CHOOSE_FIRST` — assign variables in the order given
- `CHOOSE_LOWEST_MIN` — assign the most constrained variable first
- `SELECT_MIN_VALUE` — try 0 first (don't assign)
- `SELECT_MAX_VALUE` — try 1 first (do assign)

## Model Reformulation

Sometimes the model itself is the bottleneck. Common improvements:

### 1. Reduce Variable Count

Instead of `x[nurse, day, shift]` (3 variables per nurse-day), use one integer variable:

```python
# Instead of 3 booleans per nurse-day:
# x[(n, d, 0)], x[(n, d, 1)], x[(n, d, 2)]

# Use one integer: shift_assignment[n, d] ∈ {0, 1, 2, 3} where 3 = day off
shift_assignment = {}
for n in nurses:
    for d in days:
        shift_assignment[(n, d)] = model.new_int_var(0, 3, f"shift_{n}_{d}")

# Coverage: count nurses assigned to each shift
for d in days:
    for s in shifts:
        assigned_to_s = []
        for n in nurses:
            is_s = model.new_bool_var(f"is_{n}_{d}_{s}")
            model.add(shift_assignment[(n, d)] == s).only_enforce_if(is_s)
            model.add(shift_assignment[(n, d)] != s).only_enforce_if(is_s.negated())
            assigned_to_s.append(is_s)
        model.add(sum(assigned_to_s) == nurses_per_shift[s])
```

This trades variable count for constraint complexity. Profile both approaches.

### 2. Symmetry Breaking

If nurses are interchangeable (same skills, same availability), the solver wastes time exploring equivalent solutions:

```python
# Break symmetry: nurse 0's first shift must be <= nurse 1's first shift
# (lexicographic ordering)
for n in range(num_nurses - 1):
    # First working day of nurse n must be <= first working day of nurse n+1
    # (This is complex to model — simpler version:)
    # Nurse n works at least as many shifts as nurse n+1
    model.add(
        sum(works[(n, d)] for d in days) >=
        sum(works[(n+1, d)] for d in days)
    )
```

### 3. Implied Constraints

Add constraints that are logically redundant but help the solver prune:

```python
# We know: 8 shifts/day × 7 days = 56 total shifts
# This is implied by coverage constraints, but stating it explicitly helps:
model.add(sum(works[(n, d)] for n in nurses for d in days) == 56)
```

## Parallelism

CP-SAT's `num_workers` parameter runs multiple search strategies in parallel:

```python
solver.parameters.num_workers = 0  # Auto-detect (use all cores)
```

Each worker uses a different search strategy. The first one to find a good solution shares it with others. On an 8-core machine, this typically gives 3-5x speedup.

## Incremental Solving Pattern

Don't rebuild the model from scratch when one nurse calls in sick:

```python
def solve_incrementally(base_model, base_solution, changes):
    """
    Modify an existing solution rather than resolving from scratch.
    
    changes: dict of {(nurse, day, shift): forced_value}
    """
    model = base_model.clone()  # CP-SAT doesn't support clone — rebuild

    # Actually, CP-SAT doesn't support incremental solving directly.
    # Instead: use the previous solution as a hint and add new constraints.

    new_model = rebuild_model()

    # Fix known assignments
    for (n, d, s), value in changes.items():
        new_model.add(x[(n, d, s)] == value)

    # Hint from previous solution
    for key, var in x.items():
        if key not in changes:
            new_model.add_hint(var, base_solution.get(key, 0))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0  # Much shorter with hints
    solver.parameters.num_workers = 8
    return solver.solve(new_model)
```

## VRP Performance

The routing solver has different tuning knobs:

```python
search_params = pywrapcp.DefaultRoutingSearchParameters()

# More time = better solutions
search_params.time_limit.seconds = 60

# Solution limit: stop after finding N solutions
search_params.solution_limit = 100

# Log
search_params.log_search = True

# Guided Local Search is usually best
search_params.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
)

# For very large instances, use AUTOMATIC
search_params.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
)
```

### VRP-Specific Tips

1. **Reduce the distance matrix.** If locations are clustered, solve clusters independently.
2. **Use initial routes.** If you have yesterday's routes, provide them as a starting solution.
3. **Limit vehicle count.** Fewer vehicles = smaller search space.
4. **Tighten time windows.** Paradoxically, tighter windows can be faster (more pruning).

## Benchmarking Pattern

```python
import time

def benchmark_solver(model, configs):
    """Try multiple configurations and report results."""
    results = []

    for name, params in configs.items():
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = params.get("time", 30)
        solver.parameters.num_workers = params.get("workers", 1)

        start = time.time()
        status = solver.solve(model)
        elapsed = time.time() - start

        results.append({
            "config": name,
            "status": solver.status_name(status),
            "objective": solver.objective_value if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
            "time": elapsed,
            "gap": abs(solver.objective_value - solver.best_objective_bound) / max(1, abs(solver.objective_value))
                   if status == cp_model.FEASIBLE else 0,
        })

    # Print comparison
    print(f"{'Config':<20} {'Status':<12} {'Obj':<8} {'Time':<8} {'Gap':<8}")
    print("-" * 56)
    for r in results:
        obj = f"{r['objective']:.0f}" if r['objective'] else "N/A"
        print(f"{r['config']:<20} {r['status']:<12} {obj:<8} {r['time']:<8.2f} {r['gap']:<8.1%}")

# Example configs
configs = {
    "1 worker, 10s": {"workers": 1, "time": 10},
    "4 workers, 10s": {"workers": 4, "time": 10},
    "8 workers, 10s": {"workers": 8, "time": 10},
    "8 workers, 30s": {"workers": 8, "time": 30},
    "8 workers, 60s": {"workers": 8, "time": 60},
}
```

## When CP-SAT Is Too Slow

If CP-SAT can't solve your problem in acceptable time:

1. **Decompose.** Split the 4-week schedule into 4 one-week problems with linking constraints.
2. **Relax and fix.** Solve a relaxed version, fix some variables, solve the rest.
3. **Use a different solver.** For pure LP/MIP problems, dedicated solvers (Gurobi, CPLEX) can be faster.
4. **Heuristic first.** Build a greedy solution, then use CP-SAT to improve it locally.

```python
def decompose_and_solve(nurses, weeks):
    """Solve week by week, carrying state forward."""
    previous_week_state = {}

    for week in weeks:
        model = build_week_model(nurses, week, previous_week_state)

        # Add linking constraints from previous week
        if previous_week_state:
            add_cross_week_constraints(model, previous_week_state)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10.0
        solver.parameters.num_workers = 8
        status = solver.solve(model)

        # Extract state for next week
        previous_week_state = extract_week_end_state(solver, model)
```

## Key Concepts

| Concept | What It Means |
|---|---|
| **num_workers** | Parallel search threads |
| **Solution hint** | Starting point for the solver |
| **Decision strategy** | Order of variable/value selection |
| **Optimality gap** | Distance between best solution and proven bound |
| **Symmetry breaking** | Eliminate equivalent solutions from search |
| **Decomposition** | Split large problems into smaller subproblems |
| **Implied constraint** | Redundant but helps propagation |

## The Performance Checklist

1. ✅ Set `num_workers = 0` (auto-detect cores)
2. ✅ Provide solution hints when available
3. ✅ Set `relative_gap_limit` for "good enough" solutions
4. ✅ Add symmetry-breaking constraints
5. ✅ Add implied constraints
6. ✅ Profile: is the model too large, or is the search too slow?
7. ✅ Consider decomposition for multi-period problems
8. ✅ Benchmark different configurations

## What's Next

The scheduler is fast enough. But requirements change constantly — a nurse swaps shifts, a new constraint is added mid-week, a holiday changes the rules. Rebuilding and resolving from scratch every time is wasteful.

Time to learn about incremental solving, warm starts, and re-optimization.

---

[← Chapter 9: VRP Constraints](chapter-09-vrp-constraints.md) | [Chapter 11: Incremental Solving →](chapter-11-incremental.md)
