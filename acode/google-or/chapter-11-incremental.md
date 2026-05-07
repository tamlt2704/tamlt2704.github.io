# Chapter 11: Incremental Solving & Re-Optimization

[← Chapter 10: Performance](chapter-10-performance.md) | [Chapter 12: Production Deployment →](chapter-12-production.md)

---

## The Problem

It's Wednesday. The schedule was published Monday. Now:

- Nurse Rivera swapped Thursday's shift with Nurse Kim (mutual agreement)
- A new constraint arrived: Nurse Park can't work Friday (family emergency)
- The hospital added a requirement: minimum 2 senior nurses per night shift

You could rebuild the entire model and solve from scratch. But that might produce a completely different schedule — disrupting everyone's plans. You want **minimal changes** to the existing schedule.

## The Re-Optimization Pattern

```python
from ortools.sat.python import cp_model

def reoptimize(original_schedule, changes, new_constraints):
    """
    Produce a new schedule that:
    1. Satisfies all constraints (including new ones)
    2. Minimizes changes from the original schedule
    """
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

    # Standard hard constraints
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

    # --- Apply fixed changes ---
    for (nurse, day, shift), value in changes.items():
        model.add(x[(nurse, day, shift)] == value)

    # --- Apply new constraints ---
    for constraint_fn in new_constraints:
        constraint_fn(model, x, works)

    # --- Objective: minimize deviation from original schedule ---
    deviations = []
    for n in nurses:
        for d in days:
            for s in shifts:
                original_value = original_schedule.get((n, d, s), 0)
                if original_value == 1:
                    # Was assigned — penalize removing
                    deviations.append(x[(n, d, s)].negated())
                else:
                    # Was not assigned — penalize adding
                    deviations.append(x[(n, d, s)])

    # Each deviation is a bool: 1 if different from original
    # Wait — that's not quite right. Let's use explicit diff variables:
    diff = {}
    for n in nurses:
        for d in days:
            for s in shifts:
                original_value = original_schedule.get((n, d, s), 0)
                diff[(n, d, s)] = model.new_bool_var(f"diff_{n}_{d}_{s}")
                if original_value == 1:
                    # diff = 1 if x = 0 (was 1, now 0)
                    model.add(diff[(n, d, s)] == 1).only_enforce_if(x[(n, d, s)].negated())
                    model.add(diff[(n, d, s)] == 0).only_enforce_if(x[(n, d, s)])
                else:
                    # diff = 1 if x = 1 (was 0, now 1)
                    model.add(diff[(n, d, s)] == 1).only_enforce_if(x[(n, d, s)])
                    model.add(diff[(n, d, s)] == 0).only_enforce_if(x[(n, d, s)].negated())

    # Minimize total changes
    model.minimize(sum(diff[(n, d, s)] for n in nurses for d in days for s in shifts))

    # Hint: use original schedule
    for (n, d, s), value in original_schedule.items():
        model.add_hint(x[(n, d, s)], value)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 8
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        num_changes = int(solver.objective_value)
        print(f"✓ Re-optimized with {num_changes} changes\n")

        # Show what changed
        for n in nurses:
            for d in days:
                for s in shifts:
                    if solver.value(diff[(n, d, s)]):
                        old = original_schedule.get((n, d, s), 0)
                        new = solver.value(x[(n, d, s)])
                        action = "ADDED" if new == 1 else "REMOVED"
                        shift_names = ["Morning", "Afternoon", "Night"]
                        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                        print(f"  {action}: Nurse {n}, {day_names[d]} {shift_names[s]}")

        return {(n, d, s): solver.value(x[(n, d, s)])
                for n in nurses for d in days for s in shifts}
    else:
        print(f"✗ {solver.status_name(status)}")
        return None

# Example usage:
original = {
    # ... (the published schedule as a dict)
}

changes = {
    # Rivera (nurse 3) and Kim (nurse 7) swap Thursday afternoon
    (3, 3, 1): 0,  # Remove Rivera from Thu afternoon
    (7, 3, 1): 1,  # Add Kim to Thu afternoon
    (3, 3, 0): 1,  # Add Rivera to Thu morning (Kim's old shift)
    (7, 3, 0): 0,  # Remove Kim from Thu morning
}

def park_unavailable_friday(model, x, works):
    """Nurse Park (nurse 5) can't work Friday."""
    for s in range(3):
        model.add(x[(5, 4, s)] == 0)

new_schedule = reoptimize(original, changes, [park_unavailable_friday])
```

## Fixing Past Days

Once a day has passed, its schedule is fixed. Don't let the solver change it:

```python
def fix_past_days(model, x, original_schedule, today):
    """Fix all assignments for days that have already passed."""
    for n in nurses:
        for d in range(today):  # Days 0..today-1 are in the past
            for s in shifts:
                value = original_schedule.get((n, d, s), 0)
                model.add(x[(n, d, s)] == value)
```

## Rolling Horizon

For multi-week scheduling, use a rolling window:

```python
def rolling_horizon_schedule(weeks_ahead=4, solve_window=2):
    """
    Schedule 4 weeks ahead, but only commit to the first 2 weeks.
    Re-solve every week with updated information.
    """
    committed_schedule = {}

    for current_week in range(total_weeks):
        # Build model for weeks [current_week, current_week + weeks_ahead)
        model = build_model(
            start_week=current_week,
            end_week=current_week + weeks_ahead,
            fixed_schedule=committed_schedule
        )

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        solver.solve(model)

        # Commit only the first solve_window weeks
        for week in range(current_week, current_week + solve_window):
            for assignment in extract_week(solver, week):
                committed_schedule[assignment] = 1

        # Next iteration will have updated availability, preferences, etc.
```

## Warm Starting the Routing Solver

For VRP, provide initial routes:

```python
def vrp_warm_start(routing, manager, initial_routes):
    """
    initial_routes: list of routes, e.g. [[0, 3, 5, 0], [0, 1, 4, 2, 0]]
    """
    # Convert node routes to routing indices
    initial_solution = routing.ReadAssignmentFromRoutes(
        initial_routes, True  # ignore_inactive_nodes
    )

    if initial_solution:
        # Use as starting point for local search
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_params.time_limit.seconds = 30

        solution = routing.SolveFromAssignmentWithParameters(
            initial_solution, search_params
        )
        return solution
```

## Event-Driven Re-Optimization

In production, changes trigger re-optimization automatically:

```python
class ScheduleManager:
    def __init__(self, nurses, days, shifts):
        self.current_schedule = {}
        self.constraints = []
        self.nurses = nurses
        self.days = days
        self.shifts = shifts

    def publish_schedule(self, schedule):
        """Publish a new schedule."""
        self.current_schedule = schedule
        self.notify_nurses(schedule)

    def handle_sick_call(self, nurse_id, day):
        """A nurse calls in sick."""
        # Fix: nurse can't work that day
        changes = {(nurse_id, day, s): 0 for s in self.shifts}

        # Re-optimize with minimal changes
        new_schedule = reoptimize(
            self.current_schedule,
            changes,
            self.constraints
        )

        if new_schedule:
            # Notify affected nurses
            affected = self.find_affected_nurses(self.current_schedule, new_schedule)
            self.notify_nurses_of_changes(affected, new_schedule)
            self.current_schedule = new_schedule
        else:
            self.alert_manager("Cannot cover shifts — need agency staff")

    def handle_swap_request(self, nurse_a, nurse_b, day, shift_a, shift_b):
        """Two nurses want to swap shifts."""
        # Verify the swap doesn't violate constraints
        changes = {
            (nurse_a, day, shift_a): 0,
            (nurse_a, day, shift_b): 1,
            (nurse_b, day, shift_b): 0,
            (nurse_b, day, shift_a): 1,
        }

        new_schedule = reoptimize(
            self.current_schedule,
            changes,
            self.constraints
        )

        if new_schedule:
            self.current_schedule = new_schedule
            return True, "Swap approved"
        else:
            return False, "Swap would violate constraints"

    def find_affected_nurses(self, old, new):
        """Find nurses whose schedule changed."""
        affected = set()
        for (n, d, s) in old:
            if old.get((n, d, s), 0) != new.get((n, d, s), 0):
                affected.add(n)
        return affected
```

## Multi-Scenario Optimization

Sometimes you want a schedule that's robust to multiple possible futures:

```python
def robust_schedule(scenarios):
    """
    Find a schedule that works well across multiple scenarios.
    
    scenarios: list of (probability, constraint_set) tuples
    """
    model = cp_model.CpModel()
    # ... (base variables and constraints) ...

    # For each scenario, compute the penalty
    total_expected_penalty = 0

    for prob, scenario_constraints in scenarios:
        # Scenario-specific slack variables
        scenario_penalty = compute_scenario_penalty(model, x, scenario_constraints)
        total_expected_penalty += int(prob * 100) * scenario_penalty

    model.minimize(total_expected_penalty)
```

## Key Concepts

| Concept | What It Means |
|---|---|
| **Re-optimization** | Modify an existing solution minimally |
| **Deviation penalty** | Cost of changing from the published schedule |
| **Rolling horizon** | Solve a window, commit part, slide forward |
| **Warm start** | Provide an initial solution to speed up search |
| **Fix-and-optimize** | Fix some variables, optimize the rest |
| **Robust optimization** | Find solutions that work across scenarios |

## What's Next

The scheduling engine works. It's fast, handles changes gracefully, and produces fair schedules. Now you need to ship it — as an API that validates input, handles errors, respects timeouts, and doesn't crash when someone sends garbage data.

Time to build the production system.

---

[← Chapter 10: Performance](chapter-10-performance.md) | [Chapter 12: Production Deployment →](chapter-12-production.md)
