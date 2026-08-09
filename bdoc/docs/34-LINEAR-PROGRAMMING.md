# Chapter 34: Linear Programming — Optimise Everything

## What you'll learn

- What linear programming (LP) is and when to use it
- Formulating real-world problems as LP models (objective + constraints)
- Graphical method (visualise 2-variable problems)
- The Simplex algorithm (how solvers work internally)
- Solving LP problems with Python (PuLP, SciPy)
- Integer programming (when variables must be whole numbers)
- Real applications: scheduling, resource allocation, logistics, portfolio optimisation
- Build: solve production planning, diet problem, and transportation problem

---

## PART 1: Fundamentals

## 34.1 What is linear programming?

Linear programming = finding the **best outcome** (maximum profit, minimum cost) subject to **constraints** (limited resources, requirements), where everything is expressed as **linear equations**.

```
Maximise:    objective function (what you want to optimise)
Subject to:  constraints (limits, requirements)
             variable bounds (non-negativity, ranges)
```

**"Linear" means:**
- No x², no xy, no sin(x), no if-then
- Only: `ax + by + cz = d` (constants × variables, summed)

**Real-world examples:**
| Problem | Objective | Constraints |
|---------|-----------|-------------|
| Factory production | Maximise profit | Machine hours, raw materials, storage space |
| Diet optimisation | Minimise cost | Minimum nutrients, maximum calories |
| Delivery routing | Minimise distance | Vehicle capacity, time windows |
| Portfolio allocation | Maximise return | Risk budget, diversification rules |
| Staff scheduling | Minimise cost | Shift coverage, labour laws, skills required |
| Network flow | Maximise throughput | Pipe/wire capacities |

## 34.2 Anatomy of an LP problem

**Example: A furniture factory makes tables and chairs.**

```
Each table: uses 4 hours of carpentry, 2 hours of finishing, profit = $70
Each chair: uses 3 hours of carpentry, 1 hour of finishing, profit = $50

Available: 240 hours of carpentry, 100 hours of finishing
```

**Formulation:**

```
Decision variables:
  x = number of tables to produce
  y = number of chairs to produce

Objective function (maximise):
  Maximise Z = 70x + 50y

Constraints:
  4x + 3y ≤ 240    (carpentry hours)
  2x + 1y ≤ 100    (finishing hours)
  x ≥ 0            (can't make negative tables)
  y ≥ 0            (can't make negative chairs)
```

## 34.3 Graphical method (2 variables)

Plot each constraint as a line. The **feasible region** is where all constraints overlap. The optimal solution is at a **corner point** (vertex) of the feasible region.

```
y (chairs)
100│
   │
 80│╲  feasible
   │  ╲  region
 60│    ╲........
   │    │........╲
 40│    │.........╲
   │    │..........│
 20│    │..........│
   │    │..........│
  0├────┴──────────┴──── x (tables)
   0   20   40   60

Constraint 1: 4x + 3y ≤ 240 → y ≤ (240 - 4x)/3
Constraint 2: 2x + 1y ≤ 100 → y ≤ 100 - 2x

Corner points (vertices):
  (0, 0)   → Z = 0
  (50, 0)  → Z = 3500
  (30, 40) → Z = 70(30) + 50(40) = 4100  ← OPTIMAL
  (0, 80)  → Z = 4000
```

> **Fundamental Theorem of LP:** If an optimal solution exists, it occurs at a vertex of the feasible region. You only need to check the corners — not every possible point.

## 34.4 Standard form

Every LP can be written in standard form:

```
Maximise:    c₁x₁ + c₂x₂ + ... + cₙxₙ

Subject to:  a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ ≤ b₁
             a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ ≤ b₂
             ...
             aₘ₁x₁ + aₘ₂x₂ + ... + aₘₙxₙ ≤ bₘ

             x₁, x₂, ..., xₙ ≥ 0
```

In matrix form:
```
Maximise:    cᵀx
Subject to:  Ax ≤ b
             x ≥ 0
```

Where:
- **c** = coefficients of objective function (profit/cost per unit)
- **x** = decision variables (what you're choosing)
- **A** = constraint coefficient matrix
- **b** = right-hand side (resource limits)

## 34.5 Key terminology

| Term | Meaning |
|------|---------|
| **Feasible region** | Set of all points satisfying ALL constraints |
| **Feasible solution** | Any point in the feasible region |
| **Optimal solution** | Feasible solution that maximises/minimises the objective |
| **Infeasible** | No solution satisfies all constraints simultaneously |
| **Unbounded** | Objective can increase/decrease without limit (missing constraint) |
| **Binding constraint** | Constraint that's exactly satisfied at the optimum (active, no slack) |
| **Slack** | Unused resource in a ≤ constraint (slack = b - Ax at that row) |
| **Shadow price** | How much the objective improves per unit increase in a constraint's RHS |

---

## PART 2: Solving with Python

## 34.6 PuLP — the practical LP solver

```bash
pip install pulp
```

```python
from pulp import *

# 1. Create the problem
prob = LpProblem("Furniture_Factory", LpMaximize)

# 2. Decision variables
x = LpVariable("Tables", lowBound=0, cat="Continuous")  # tables ≥ 0
y = LpVariable("Chairs", lowBound=0, cat="Continuous")  # chairs ≥ 0

# 3. Objective function
prob += 70*x + 50*y, "Total_Profit"

# 4. Constraints
prob += 4*x + 3*y <= 240, "Carpentry_Hours"
prob += 2*x + 1*y <= 100, "Finishing_Hours"

# 5. Solve
prob.solve(PULP_CBC_CMD(msg=0))  # suppress solver output

# 6. Results
print(f"Status: {LpStatus[prob.status]}")
print(f"Tables: {x.varValue}")
print(f"Chairs: {y.varValue}")
print(f"Max Profit: ${value(prob.objective)}")

# Output:
# Status: Optimal
# Tables: 30.0
# Chairs: 40.0
# Max Profit: $4100.0
```

## 34.7 Sensitivity analysis (shadow prices)

```python
# Which constraints are binding? What's the value of more resources?
for name, constraint in prob.constraints.items():
    print(f"{name}: slack = {constraint.slack}, shadow price = {constraint.pi}")

# Output:
# Carpentry_Hours: slack = 0.0, shadow price = 15.0
#   → Carpentry is fully used. Each extra hour of carpentry = $15 more profit.
# Finishing_Hours: slack = 0.0, shadow price = 5.0
#   → Finishing is fully used. Each extra hour of finishing = $5 more profit.

# Decision: if you can buy 1 extra hour, buy carpentry ($15 value > $5 for finishing)
```

## 34.8 SciPy alternative (for simple LPs)

```python
from scipy.optimize import linprog

# scipy minimises, so negate for maximisation
c = [-70, -50]  # negative because minimising

# Inequality constraints: Ax ≤ b
A_ub = [
    [4, 3],   # carpentry
    [2, 1],   # finishing
]
b_ub = [240, 100]

# Variable bounds
x_bounds = (0, None)
y_bounds = (0, None)

result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[x_bounds, y_bounds], method="highs")

print(f"Tables: {result.x[0]:.1f}")
print(f"Chairs: {result.x[1]:.1f}")
print(f"Max Profit: ${-result.fun:.1f}")  # negate back
```

---

## PART 3: Classic Problems

## 34.9 The Diet Problem (minimise cost meeting nutrition requirements)

```python
from pulp import *

# Foods available
foods = ["Bread", "Milk", "Cheese", "Fish", "Potato"]
costs = {"Bread": 2.0, "Milk": 3.5, "Cheese": 8.0, "Fish": 7.0, "Potato": 1.5}

# Nutrition content per unit
nutrition = {
    #            Protein  Fat   Carbs  Calories
    "Bread":    [3,       1,    50,    250],
    "Milk":     [8,       5,    12,    150],
    "Cheese":   [25,      9,    2,     350],
    "Fish":     [22,      1,    0,     170],
    "Potato":   [2,       0.1,  22,    100],
}

# Minimum daily requirements
min_protein = 55    # grams
min_fat = 30        # grams
min_carbs = 200     # grams
min_calories = 2000 # kcal

# Model
prob = LpProblem("Diet_Problem", LpMinimize)

# Variables: how many units of each food
x = {f: LpVariable(f"x_{f}", lowBound=0) for f in foods}

# Objective: minimise total cost
prob += lpSum(costs[f] * x[f] for f in foods), "Total_Cost"

# Constraints: meet minimum nutrition
prob += lpSum(nutrition[f][0] * x[f] for f in foods) >= min_protein, "Min_Protein"
prob += lpSum(nutrition[f][1] * x[f] for f in foods) >= min_fat, "Min_Fat"
prob += lpSum(nutrition[f][2] * x[f] for f in foods) >= min_carbs, "Min_Carbs"
prob += lpSum(nutrition[f][3] * x[f] for f in foods) >= min_calories, "Min_Calories"

# Solve
prob.solve(PULP_CBC_CMD(msg=0))

print(f"Status: {LpStatus[prob.status]}")
print(f"\nOptimal diet (minimum cost = ${value(prob.objective):.2f}/day):")
for f in foods:
    if x[f].varValue > 0.01:
        print(f"  {f}: {x[f].varValue:.2f} units")
```

## 34.10 The Transportation Problem

Ship goods from factories to warehouses at minimum cost:

```python
from pulp import *

# Factories and their supply
factories = ["Factory_A", "Factory_B", "Factory_C"]
supply = {"Factory_A": 300, "Factory_B": 400, "Factory_C": 500}

# Warehouses and their demand
warehouses = ["Warehouse_1", "Warehouse_2", "Warehouse_3", "Warehouse_4"]
demand = {"Warehouse_1": 250, "Warehouse_2": 350, "Warehouse_3": 400, "Warehouse_4": 200}

# Shipping cost per unit from factory i to warehouse j
costs = {
    ("Factory_A", "Warehouse_1"): 10, ("Factory_A", "Warehouse_2"): 8,
    ("Factory_A", "Warehouse_3"): 6,  ("Factory_A", "Warehouse_4"): 12,
    ("Factory_B", "Warehouse_1"): 7,  ("Factory_B", "Warehouse_2"): 11,
    ("Factory_B", "Warehouse_3"): 9,  ("Factory_B", "Warehouse_4"): 5,
    ("Factory_C", "Warehouse_1"): 4,  ("Factory_C", "Warehouse_2"): 5,
    ("Factory_C", "Warehouse_3"): 10, ("Factory_C", "Warehouse_4"): 8,
}

# Model
prob = LpProblem("Transportation", LpMinimize)

# Variables: units shipped from factory i to warehouse j
x = {}
for f in factories:
    for w in warehouses:
        x[(f, w)] = LpVariable(f"Ship_{f}_{w}", lowBound=0)

# Objective: minimise total shipping cost
prob += lpSum(costs[(f, w)] * x[(f, w)] for f in factories for w in warehouses)

# Supply constraints (can't ship more than produced)
for f in factories:
    prob += lpSum(x[(f, w)] for w in warehouses) <= supply[f], f"Supply_{f}"

# Demand constraints (must meet demand)
for w in warehouses:
    prob += lpSum(x[(f, w)] for f in factories) >= demand[w], f"Demand_{w}"

# Solve
prob.solve(PULP_CBC_CMD(msg=0))

print(f"Minimum shipping cost: ${value(prob.objective):.0f}")
print("\nShipping plan:")
for f in factories:
    for w in warehouses:
        if x[(f, w)].varValue > 0:
            print(f"  {f} → {w}: {x[(f, w)].varValue:.0f} units (cost: ${costs[(f,w)] * x[(f,w)].varValue:.0f})")
```

## 34.11 Staff scheduling

```python
from pulp import *

# Days of the week
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Minimum staff needed per day
min_staff = {"Mon": 14, "Tue": 13, "Wed": 15, "Thu": 16, "Fri": 19, "Sat": 18, "Sun": 11}

# Each worker works 5 consecutive days, then 2 off
# Variable: how many workers START their 5-day shift on day i
prob = LpProblem("Staff_Scheduling", LpMinimize)
x = {d: LpVariable(f"Start_{d}", lowBound=0, cat="Integer") for d in days}

# Objective: minimise total workers hired
prob += lpSum(x[d] for d in days)

# Constraint: for each day, workers present ≥ minimum
# Workers on duty on day j = sum of workers who started on days j, j-1, j-2, j-3, j-4
for j, day in enumerate(days):
    workers_on_day = lpSum(x[days[(j - k) % 7]] for k in range(5))
    prob += workers_on_day >= min_staff[day], f"Cover_{day}"

prob.solve(PULP_CBC_CMD(msg=0))

total_workers = int(value(prob.objective))
print(f"Minimum workers needed: {total_workers}")
print("\nHiring schedule:")
for d in days:
    print(f"  Workers starting on {d}: {int(x[d].varValue)}")
```

---

## PART 4: Integer Programming and Extensions

## 34.12 Integer Programming (IP)

When variables must be whole numbers (can't make 2.7 tables):

```python
# Just change the variable category:
x = LpVariable("Tables", lowBound=0, cat="Integer")   # integer
y = LpVariable("Hire", cat="Binary")                    # 0 or 1 only
```

**Types:**
| Type | Variables | Use case |
|------|-----------|----------|
| LP (Linear Programming) | Continuous (fractions OK) | Production quantities, flow rates |
| IP (Integer Programming) | All integers | Scheduling, assignment, routing |
| MIP (Mixed Integer) | Some integer, some continuous | Real-world problems (usually MIP) |
| Binary / 0-1 | Binary only | Yes/no decisions (build factory? assign task?) |

> **IPs are much harder than LPs.** LP → polynomial time (Simplex is fast in practice). IP → NP-hard (worst case exponential). Solvers use branch-and-bound, cutting planes, and heuristics.

## 34.13 Binary decisions — the knapsack problem

```python
from pulp import *

# Items with value and weight
items = ["Laptop", "Camera", "Book", "Phone", "Headphones", "Tablet"]
values = [60, 40, 10, 30, 20, 50]
weights = [5, 4, 1, 2, 1, 3]
capacity = 10  # kg

prob = LpProblem("Knapsack", LpMaximize)

# Binary variable: take item or not
x = [LpVariable(f"x_{i}", cat="Binary") for i in range(len(items))]

# Objective: maximise total value
prob += lpSum(values[i] * x[i] for i in range(len(items)))

# Constraint: total weight ≤ capacity
prob += lpSum(weights[i] * x[i] for i in range(len(items))) <= capacity

prob.solve(PULP_CBC_CMD(msg=0))

print(f"Maximum value: ${value(prob.objective):.0f}")
print(f"Items to take:")
total_weight = 0
for i in range(len(items)):
    if x[i].varValue == 1:
        print(f"  {items[i]} (value={values[i]}, weight={weights[i]})")
        total_weight += weights[i]
print(f"Total weight: {total_weight}/{capacity} kg")
```

## 34.14 The Simplex Algorithm (how solvers work)

You don't need to implement it, but understanding the concept helps:

```
1. Start at a corner point of the feasible region (usually the origin)
2. Look at adjacent corners — does moving there improve the objective?
3. Move to the best adjacent corner
4. Repeat until no adjacent corner is better → you're at the optimum

Analogy: climbing a hill by always walking uphill. Since the feasible region
is convex (LP guarantee), there's only one peak — you'll always find it.
```

**Complexity:** Worst case exponential, but average case is polynomial. In practice, Simplex solves problems with millions of variables in seconds.

**Interior point methods** (alternative): walk THROUGH the middle of the feasible region toward the optimum. Polynomial worst-case. Used in modern solvers alongside Simplex.

---

## PART 5: Practical Tips

## 34.15 Formulation patterns

| Real-world phrase | LP formulation |
|-------------------|----------------|
| "Maximise profit" | max cᵀx |
| "Minimise cost" | min cᵀx |
| "Can't use more than 100 hours" | ax ≤ 100 |
| "Must produce at least 50 units" | x ≥ 50 |
| "Exactly 3 workers assigned" | x₁ + x₂ + x₃ = 3 |
| "If we build factory A, it costs $1M" | Binary variable: y_A ∈ {0,1}, cost = 1M × y_A |
| "Produce B only if factory A is built" | x_B ≤ M × y_A (big-M method) |
| "Either X or Y, not both" | x + y ≤ 1 (binary) |
| "At least 2 of these 5 options" | x₁ + x₂ + x₃ + x₄ + x₅ ≥ 2 (binary) |
| "Ratio of A to B is at most 3:1" | x_A ≤ 3 × x_B → x_A - 3x_B ≤ 0 |

## 34.16 When LP doesn't work

| Problem type | Why LP fails | Alternative |
|-------------|-------------|-------------|
| Nonlinear objective/constraints | x² terms, products xy | Nonlinear programming (NLP) |
| Uncertain parameters | Costs/demands are random | Stochastic programming |
| Multi-objective | Maximise profit AND minimise risk | Pareto optimisation |
| Dynamic decisions over time | Decisions depend on future info | Dynamic programming |
| Combinatorial explosion | n! permutations | Constraint programming, heuristics |

## 34.17 Solver comparison

| Solver | Cost | Speed | Features |
|--------|------|-------|----------|
| CBC (PuLP default) | Free | Good for small/medium | LP, MIP |
| GLPK | Free | Moderate | LP, MIP |
| HiGHS (SciPy) | Free | Fast | LP, QP |
| Gurobi | Commercial ($) | Very fast | LP, MIP, QP — industry standard |
| CPLEX (IBM) | Commercial ($) | Very fast | LP, MIP, CP |
| OR-Tools (Google) | Free | Good | LP, MIP, CP, routing, scheduling |

For learning and small problems: **PuLP + CBC** (free, simple API).
For production at scale: **Gurobi** or **OR-Tools**.

---

## Summary

✅ LP fundamentals: objective function + constraints + variable bounds
✅ Formulating real problems as LP models (identify variables, write inequalities)
✅ Graphical method: feasible region, corner points, optimal vertex
✅ Solving with Python: PuLP (declarative) and SciPy (matrix-based)
✅ Sensitivity analysis: shadow prices, slack, binding constraints
✅ Classic problems: diet, transportation, staff scheduling
✅ Integer programming: binary decisions, knapsack, when/why it's harder
✅ Simplex algorithm: move between adjacent vertices, always improving
✅ Practical formulation patterns (real-world phrases → math)

## Key takeaways

**LP is about formulation, not solving.** The solver handles the maths. Your job is translating the real problem into variables, an objective, and constraints. That's the hard part — and the creative part.

**The optimal solution is always at a corner.** This is why LP is tractable — you don't search infinite continuous space. You check a finite (though potentially large) number of vertices.

**Shadow prices tell you where to invest.** If carpentry has a shadow price of $15/hour and finishing has $5/hour, buying more carpentry time is 3× more valuable. This is LP's real power in business — it tells you not just WHAT to do, but WHERE more resources would help most.

**Integer programming is exponentially harder** but usually necessary for real decisions (you can't hire 2.7 people or build 0.4 of a factory). Solvers handle it, but be prepared for longer run times on large problems.

---

→ [Back to Chapter 33: Chess](./33-CHESS.md)
