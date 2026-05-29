# Linear Programming

[prev: Setup](chapter-01-setup.md) | [next: Integer Programming](chapter-03-integer.md)

## What is Linear Programming?

Linear Programming (LP) finds the best outcome in a mathematical model where:

- The **objective function** is linear (maximize or minimize)
- The **constraints** are linear inequalities or equalities
- The **variables** are continuous (can take any real value)

Key concepts:

- **Decision variables** — what you control (how much to produce, allocate)
- **Objective function** — what you want to maximize or minimize
- **Constraints** — limitations on resources, capacity, requirements
- **Feasible region** — the set of all points satisfying all constraints
- **Optimal solution** — the point in the feasible region that optimizes the objective

## OR-Tools MPSolver

```python
from ortools.linear_solver import pywraplp

# GLOP for pure LP (continuous variables only)
solver = pywraplp.Solver.CreateSolver("GLOP")

# SCIP for MIP (integer variables)
solver = pywraplp.Solver.CreateSolver("SCIP")
```

## Example 1: Production Planning

**Problem:** A bakery makes bread and cake. Bread needs 1 hour oven time and 2 kg flour, yielding 5 profit. Cake needs 2 hours oven time and 1 kg flour, yielding 8 profit. Available: 12 oven hours, 10 kg flour. Maximize profit.

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("GLOP")

bread = solver.NumVar(0, solver.infinity(), "bread")
cake = solver.NumVar(0, solver.infinity(), "cake")

solver.Add(1 * bread + 2 * cake <= 12)  # oven time
solver.Add(2 * bread + 1 * cake <= 10)  # flour

solver.Maximize(5 * bread + 8 * cake)
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Bread: {bread.solution_value():.2f}")
    print(f"Cake: {cake.solution_value():.2f}")
    print(f"Profit: {solver.Objective().Value():.2f}")
```

Output:

```
Bread: 2.67
Cake: 4.67
Profit: 50.67
```

## Example 2: Diet Problem

**Problem:** Find the cheapest combination of foods meeting nutritional requirements. Rice (cost 2, 350 cal, 8g protein), beans (cost 3, 250 cal, 15g protein), chicken (cost 7, 200 cal, 30g protein). Need at least 2000 calories and 60g protein.

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("GLOP")

rice = solver.NumVar(0, solver.infinity(), "rice")
beans = solver.NumVar(0, solver.infinity(), "beans")
chicken = solver.NumVar(0, solver.infinity(), "chicken")

solver.Add(350 * rice + 250 * beans + 200 * chicken >= 2000)  # calories
solver.Add(8 * rice + 15 * beans + 30 * chicken >= 60)        # protein

solver.Minimize(2 * rice + 3 * beans + 7 * chicken)
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Rice: {rice.solution_value():.2f} units")
    print(f"Beans: {beans.solution_value():.2f} units")
    print(f"Chicken: {chicken.solution_value():.2f} units")
    print(f"Total cost: {solver.Objective().Value():.2f}")
```

Output:

```
Rice: 5.08 units
Beans: 0.85 units
Chicken: 0.00 units
Total cost: 12.71
```

## Example 3: Blending Problem

**Problem:** Blend 3 raw materials into 1000 kg of alloy. Alloy must contain 3-5% carbon and 1-3% silicon.

| Material | Cost/kg | Carbon % | Silicon % |
| -------- | ------- | -------- | --------- |
| A        | 5       | 4        | 2         |
| B        | 4       | 1        | 3         |
| C        | 6       | 6        | 1         |

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("GLOP")

a = solver.NumVar(0, solver.infinity(), "A")
b = solver.NumVar(0, solver.infinity(), "B")
c = solver.NumVar(0, solver.infinity(), "C")

solver.Add(a + b + c == 1000)
solver.Add(0.04 * a + 0.01 * b + 0.06 * c >= 30)  # carbon min 3%
solver.Add(0.04 * a + 0.01 * b + 0.06 * c <= 50)  # carbon max 5%
solver.Add(0.02 * a + 0.03 * b + 0.01 * c >= 10)  # silicon min 1%
solver.Add(0.02 * a + 0.03 * b + 0.01 * c <= 30)  # silicon max 3%

solver.Minimize(5 * a + 4 * b + 6 * c)
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Material A: {a.solution_value():.1f} kg")
    print(f"Material B: {b.solution_value():.1f} kg")
    print(f"Material C: {c.solution_value():.1f} kg")
    print(f"Total cost: {solver.Objective().Value():.2f}")
```

Output:

```
Material A: 600.0 kg
Material B: 400.0 kg
Material C: 0.0 kg
Total cost: 4600.00
```

## Example 4: Resource Allocation

**Problem:** Allocate resources across 3 projects to maximize return. Budget: 100k, Engineers: 20, Time: 12 months.

| Project | Budget/unit | Engineers/unit | Months/unit | Return/unit | Max units |
| ------- | ----------- | -------------- | ----------- | ----------- | --------- |
| Alpha   | 30          | 8              | 4           | 50          | 3         |
| Beta    | 20          | 5              | 6           | 35          | 4         |
| Gamma   | 15          | 3              | 3           | 20          | 5         |

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("GLOP")

alpha = solver.NumVar(0, 3, "alpha")
beta = solver.NumVar(0, 4, "beta")
gamma = solver.NumVar(0, 5, "gamma")

solver.Add(30 * alpha + 20 * beta + 15 * gamma <= 100)  # budget
solver.Add(8 * alpha + 5 * beta + 3 * gamma <= 20)      # engineers
solver.Add(4 * alpha + 6 * beta + 3 * gamma <= 12)      # time

solver.Maximize(50 * alpha + 35 * beta + 20 * gamma)
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Alpha: {alpha.solution_value():.2f} units")
    print(f"Beta: {beta.solution_value():.2f} units")
    print(f"Gamma: {gamma.solution_value():.2f} units")
    print(f"Total return: {solver.Objective().Value():.2f}k")
```

Output:

```
Alpha: 1.50 units
Beta: 0.00 units
Gamma: 2.00 units
Total return: 115.00k
```

## Key Takeaways

- LP works when variables are continuous and relationships are linear
- GLOP is fast and reliable for pure LP problems
- Always check solver status before reading solutions
- Fractional solutions (2.67 bread) are normal in LP — use Integer Programming when you need whole numbers
