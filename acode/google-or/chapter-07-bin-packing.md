# Chapter 7: Bin Packing & Linear Programming

[← Chapter 6: Job-Shop](chapter-06-job-shop.md) | [Chapter 8: Vehicle Routing →](chapter-08-vrp.md)

---

## The Problem

SteelWorks receives steel bars in standard lengths: 6 meters and 12 meters. Customer orders require custom cuts:

```python
orders = [
    3.5, 3.5, 2.0, 2.0, 2.0, 4.5, 4.5, 1.5, 1.5, 1.5,
    5.0, 5.0, 3.0, 3.0, 3.0, 2.5, 2.5, 6.0, 4.0, 4.0,
]  # meters
```

Each cut must come from a single bar (no welding). Leftover material is scrap. A 6m bar costs $50. A 12m bar costs $90. The goal: fill all orders while minimizing cost (equivalently, minimizing waste).

This is the **cutting stock problem** — a variant of bin packing.

## Bin Packing with CP-SAT

First approach: model it as bin packing. Each bar is a "bin" with capacity equal to its length. Each order is an "item" that must fit in exactly one bin.

```python
from ortools.sat.python import cp_model

def cutting_stock_cpsat():
    model = cp_model.CpModel()

    orders = [35, 35, 20, 20, 20, 45, 45, 15, 15, 15,
              50, 50, 30, 30, 30, 25, 25, 60, 40, 40]  # in decimeters (avoid floats)
    num_orders = len(orders)

    # Available bar types
    bar_lengths = [60, 120]  # decimeters
    bar_costs = [50, 90]     # dollars

    # Upper bound: one bar per order (worst case)
    max_bars = num_orders
    bars = range(max_bars)

    # Variables
    # bar_used[b] = 1 if bar b is used
    bar_used = [model.new_bool_var(f"bar_used_{b}") for b in bars]

    # bar_type[b] = 0 for 6m, 1 for 12m
    bar_type = [model.new_int_var(0, 1, f"bar_type_{b}") for b in bars]

    # assign[i][b] = 1 if order i is cut from bar b
    assign = {}
    for i in range(num_orders):
        for b in bars:
            assign[(i, b)] = model.new_bool_var(f"assign_{i}_{b}")

    # --- Constraints ---

    # Each order assigned to exactly one bar
    for i in range(num_orders):
        model.add(sum(assign[(i, b)] for b in bars) == 1)

    # If any order is assigned to bar b, bar b is used
    for b in bars:
        for i in range(num_orders):
            model.add_implication(assign[(i, b)], bar_used[b])

    # Orders on a bar must fit within its length
    for b in bars:
        total_on_bar = sum(assign[(i, b)] * orders[i] for i in range(num_orders))

        # If bar_type = 0, capacity = 60. If bar_type = 1, capacity = 120.
        capacity = model.new_int_var(0, 120, f"capacity_{b}")
        model.add(capacity == 60).only_enforce_if(bar_type[b] == 0)  # Won't work directly

        # Better: use two boolean variables for type
        is_6m = model.new_bool_var(f"is_6m_{b}")
        is_12m = model.new_bool_var(f"is_12m_{b}")
        model.add_exactly_one([is_6m, is_12m])

        # Capacity constraint for 6m bars
        model.add(total_on_bar <= 60).only_enforce_if(is_6m)
        # Capacity constraint for 12m bars
        model.add(total_on_bar <= 120).only_enforce_if(is_12m)

        # Link bar_type to is_6m/is_12m for cost calculation
        model.add(bar_type[b] == 0).only_enforce_if(is_6m)
        model.add(bar_type[b] == 1).only_enforce_if(is_12m)

    # Symmetry breaking: use bars in order, prefer smaller bars first
    for b in range(max_bars - 1):
        model.add_implication(bar_used[b].negated(), bar_used[b + 1].negated())

    # --- Objective: minimize cost ---
    cost = sum(
        bar_used[b] * 50 + bar_type[b] * bar_used[b] * 40  # 50 + 40 = 90 for 12m
        for b in bars
    )
    # Hmm, can't multiply two variables directly. Linearize:

    # cost_b = 50 if 6m bar used, 90 if 12m bar used, 0 if unused
    bar_cost = []
    for b in bars:
        cost_b = model.new_int_var(0, 90, f"cost_{b}")
        # cost_b = 50 * is_6m * bar_used + 90 * is_12m * bar_used
        # Since is_6m + is_12m = 1 and bar_used controls everything:
        model.add(cost_b == 50).only_enforce_if([bar_used[b], is_6m])
        model.add(cost_b == 90).only_enforce_if([bar_used[b], is_12m])
        model.add(cost_b == 0).only_enforce_if(bar_used[b].negated())
        bar_cost.append(cost_b)

    model.minimize(sum(bar_cost))

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        total_cost = solver.objective_value
        print(f"✓ Total cost: ${total_cost:.0f}")
        print(f"  Status: {solver.status_name(status)}\n")

        for b in bars:
            if solver.value(bar_used[b]):
                length = 60 if solver.value(bar_type[b]) == 0 else 120
                items = [orders[i] for i in range(num_orders) if solver.value(assign[(i, b)])]
                waste = length - sum(items)
                print(f"  Bar {b} ({length/10:.0f}m): cuts={[x/10 for x in items]}, "
                      f"waste={waste/10:.1f}m")

        total_material = sum(
            (60 if solver.value(bar_type[b]) == 0 else 120)
            for b in bars if solver.value(bar_used[b])
        )
        total_used = sum(orders)
        print(f"\n  Total material: {total_material/10:.0f}m")
        print(f"  Total used: {total_used/10:.1f}m")
        print(f"  Total waste: {(total_material - total_used)/10:.1f}m")
        print(f"  Efficiency: {total_used/total_material*100:.1f}%")

cutting_stock_cpsat()
```

## The Problem with CP-SAT for Bin Packing

The model above works but has issues:
- `max_bars = num_orders` creates too many variables
- The symmetry between bars makes search slow
- For large instances (500+ orders), CP-SAT struggles

This is where **Linear Programming (LP)** and **Mixed-Integer Programming (MIP)** shine.

## Linear Programming Basics

LP solves problems of the form:
- Minimize a linear objective
- Subject to linear constraints
- Variables are continuous (real numbers)

**MIP** adds integer variables — some or all variables must be whole numbers.

OR-Tools provides the `pywraplp` module for LP/MIP:

```python
from ortools.linear_solver import pywraplp

def cutting_stock_mip():
    # Use SCIP solver (MIP)
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        print("SCIP solver not available")
        return

    orders = [3.5, 3.5, 2.0, 2.0, 2.0, 4.5, 4.5, 1.5, 1.5, 1.5,
              5.0, 5.0, 3.0, 3.0, 3.0, 2.5, 2.5, 6.0, 4.0, 4.0]
    num_orders = len(orders)
    max_bars = 15  # Reasonable upper bound

    # Variables
    # bar_used[b] = 1 if bar b is used (binary)
    bar_used = [solver.IntVar(0, 1, f"used_{b}") for b in range(max_bars)]

    # bar_is_12m[b] = 1 if bar b is 12m (binary)
    bar_is_12m = [solver.IntVar(0, 1, f"is12m_{b}") for b in range(max_bars)]

    # assign[i][b] = 1 if order i goes to bar b (binary)
    assign = {}
    for i in range(num_orders):
        for b in range(max_bars):
            assign[(i, b)] = solver.IntVar(0, 1, f"a_{i}_{b}")

    # Constraints
    # Each order in exactly one bar
    for i in range(num_orders):
        solver.Add(sum(assign[(i, b)] for b in range(max_bars)) == 1)

    # Capacity: orders in bar b must fit
    for b in range(max_bars):
        total = sum(assign[(i, b)] * orders[i] for i in range(num_orders))
        # capacity = 6 + 6 * bar_is_12m[b]  (6m or 12m)
        solver.Add(total <= 6 * bar_used[b] + 6 * bar_is_12m[b])

    # bar_is_12m only if bar_used
    for b in range(max_bars):
        solver.Add(bar_is_12m[b] <= bar_used[b])

    # Symmetry breaking
    for b in range(max_bars - 1):
        solver.Add(bar_used[b] >= bar_used[b + 1])

    # Objective: minimize cost
    # 6m bar = $50, 12m bar = $90
    cost = sum(50 * bar_used[b] + 40 * bar_is_12m[b] for b in range(max_bars))
    solver.Minimize(cost)

    # Solve
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print(f"✓ Optimal cost: ${solver.Objective().Value():.0f}\n")

        for b in range(max_bars):
            if bar_used[b].solution_value() > 0.5:
                is_12 = bar_is_12m[b].solution_value() > 0.5
                length = 12 if is_12 else 6
                items = [orders[i] for i in range(num_orders)
                         if assign[(i, b)].solution_value() > 0.5]
                waste = length - sum(items)
                print(f"  Bar {b} ({length}m, ${90 if is_12 else 50}): "
                      f"cuts={items}, waste={waste:.1f}m")
    elif status == pywraplp.Solver.FEASIBLE:
        print(f"Feasible (not proven optimal): ${solver.Objective().Value():.0f}")
    else:
        print("No solution found")

cutting_stock_mip()
```

## CP-SAT vs Linear Solver: When to Use Which

| Feature | CP-SAT | Linear Solver (MIP) |
|---|---|---|
| **Variable types** | Integer, Boolean | Continuous, Integer, Binary |
| **Constraint types** | Rich (no-overlap, circuit, table) | Linear only |
| **Best for** | Scheduling, combinatorial | Cost optimization, allocation |
| **Handles** | Logical constraints naturally | Needs linearization tricks |
| **Performance** | Great for tight combinatorial | Great for large LP relaxations |

**Rule of thumb:**
- If the problem has "no overlap," "sequences," or "if-then" logic → CP-SAT
- If the problem is mostly "minimize cost subject to linear constraints" → MIP
- If unsure → try CP-SAT first (it's more expressive)

## The Knapsack Problem

A simpler variant: you have one container with limited capacity. Which items do you include to maximize value?

```python
from ortools.sat.python import cp_model

def knapsack():
    model = cp_model.CpModel()

    # Items: (weight, value)
    items = [(10, 60), (20, 100), (30, 120), (15, 75), (25, 90)]
    capacity = 50
    n = len(items)

    # Variables: include[i] = 1 if item i is included
    include = [model.new_bool_var(f"item_{i}") for i in range(n)]

    # Constraint: total weight <= capacity
    model.add(sum(include[i] * items[i][0] for i in range(n)) <= capacity)

    # Objective: maximize total value
    model.maximize(sum(include[i] * items[i][1] for i in range(n)))

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL:
        print(f"✓ Max value: {solver.objective_value}")
        total_weight = 0
        for i in range(n):
            if solver.value(include[i]):
                print(f"  Item {i}: weight={items[i][0]}, value={items[i][1]}")
                total_weight += items[i][0]
        print(f"  Total weight: {total_weight}/{capacity}")

knapsack()
```

## Multi-Dimensional Bin Packing

Real problems often have multiple dimensions — weight AND volume AND fragility:

```python
def multi_dim_packing():
    model = cp_model.CpModel()

    # Items: (weight_kg, volume_liters)
    items = [(5, 10), (8, 15), (3, 8), (7, 12), (4, 6),
             (6, 14), (9, 20), (2, 5), (5, 11), (7, 13)]

    # Bins: capacity (weight_kg, volume_liters)
    bin_weight_cap = 20
    bin_volume_cap = 40
    max_bins = 5

    num_items = len(items)

    # Variables
    assign = {}
    for i in range(num_items):
        for b in range(max_bins):
            assign[(i, b)] = model.new_bool_var(f"assign_{i}_{b}")

    bin_used = [model.new_bool_var(f"bin_{b}") for b in range(max_bins)]

    # Each item in exactly one bin
    for i in range(num_items):
        model.add_exactly_one(assign[(i, b)] for b in range(max_bins))

    # Capacity constraints (both dimensions)
    for b in range(max_bins):
        model.add(sum(assign[(i, b)] * items[i][0] for i in range(num_items)) <= bin_weight_cap)
        model.add(sum(assign[(i, b)] * items[i][1] for i in range(num_items)) <= bin_volume_cap)

    # Link bin_used
    for b in range(max_bins):
        for i in range(num_items):
            model.add_implication(assign[(i, b)], bin_used[b])

    # Minimize bins used
    model.minimize(sum(bin_used))

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL:
        print(f"✓ Bins needed: {int(solver.objective_value)}")
        for b in range(max_bins):
            if solver.value(bin_used[b]):
                bin_items = [i for i in range(num_items) if solver.value(assign[(i, b)])]
                w = sum(items[i][0] for i in bin_items)
                v = sum(items[i][1] for i in bin_items)
                print(f"  Bin {b}: items={bin_items}, weight={w}/{bin_weight_cap}, "
                      f"volume={v}/{bin_volume_cap}")

multi_dim_packing()
```

## Key Concepts

| Concept | What It Means |
|---|---|
| **Bin packing** | Fit items into minimum number of bins |
| **Cutting stock** | Cut material with minimum waste |
| **Knapsack** | Select items to maximize value within capacity |
| **Linear programming** | Optimize linear objective with linear constraints |
| **MIP** | LP with some integer variables |
| **LP relaxation** | Solve without integrality — gives a lower bound |

## What's Next

Tomás from logistics calls: "I have 15 delivery trucks, 200 packages, and 8 hours. Each package has a delivery window. Each truck has a weight limit. Find me routes that deliver everything on time with minimum total distance."

This isn't bin packing — it's the **Vehicle Routing Problem**. And OR-Tools has a dedicated solver for it.

---

[← Chapter 6: Job-Shop](chapter-06-job-shop.md) | [Chapter 8: Vehicle Routing →](chapter-08-vrp.md)
