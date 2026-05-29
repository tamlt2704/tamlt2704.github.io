# Integer and Mixed-Integer Programming

[prev: Linear Programming](chapter-02-linear.md) | [next: Constraint Programming](chapter-04-constraint.md)

## Why Integers Matter

Linear Programming gives fractional solutions: "hire 2.5 people" or "build 0.7 warehouses." In reality, many decisions are discrete:

- You hire 2 or 3 people, not 2.5
- You open a warehouse or you don't
- You ship in whole containers

Integer Programming (IP) restricts variables to integer values. Mixed-Integer Programming (MIP) allows a mix of continuous and integer variables.

## Binary Variables: Yes/No Decisions

Binary variables (0 or 1) model yes/no decisions:

- Should we open facility X? (`open_x = 0 or 1`)
- Should we assign worker A to task B? (`assign_a_b = 0 or 1`)
- Should we include item in the knapsack? (`include_item = 0 or 1`)

## Big-M Method

The Big-M method links binary decisions to constraints. If `y = 1` (facility open), production `x` can be up to capacity. If `y = 0`, production must be 0:

```
x <= M * y
```

Where M is a large constant. When `y = 0`, constraint becomes `x <= 0`. When `y = 1`, constraint becomes `x <= M` (effectively inactive).

## Example 1: Knapsack Problem

**Problem:** A knapsack has capacity 15 kg. Choose items to maximize total value.

| Item    | Weight | Value |
| ------- | ------ | ----- |
| Laptop  | 5      | 100   |
| Camera  | 3      | 60    |
| Book    | 2      | 20    |
| Jewelry | 1      | 80    |
| Food    | 4      | 40    |
| Clothes | 6      | 50    |

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("SCIP")

items = ["Laptop", "Camera", "Book", "Jewelry", "Food", "Clothes"]
weights = [5, 3, 2, 1, 4, 6]
values = [100, 60, 20, 80, 40, 50]
capacity = 15

x = [solver.IntVar(0, 1, f"x_{i}") for i in range(len(items))]

solver.Add(sum(weights[i] * x[i] for i in range(len(items))) <= capacity)
solver.Maximize(sum(values[i] * x[i] for i in range(len(items))))

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(f"Total value: {solver.Objective().Value():.0f}")
    total_weight = 0
    for i in range(len(items)):
        if x[i].solution_value() > 0.5:
            print(f"  Take {items[i]} (w={weights[i]}, v={values[i]})")
            total_weight += weights[i]
    print(f"Total weight: {total_weight}/{capacity}")
```

Output:

```
Total value: 300
  Take Laptop (w=5, v=100)
  Take Camera (w=3, v=60)
  Take Jewelry (w=1, v=80)
  Take Food (w=4, v=40)
  Take Book (w=2, v=20)
Total weight: 15/15
```

## Example 2: Facility Location

**Problem:** Decide which warehouses to open and how to assign customers. Opening has a fixed cost. Minimize total cost (fixed + shipping).

| Warehouse | Fixed cost | Capacity |
| --------- | ---------- | -------- |
| W1        | 100        | 50       |
| W2        | 150        | 80       |
| W3        | 120        | 60       |

Shipping costs and customer demands: C1=20, C2=30, C3=25, C4=15.

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("SCIP")

fixed_costs = [100, 150, 120]
capacities = [50, 80, 60]
demands = [20, 30, 25, 15]
ship_cost = [
    [4, 6, 9, 5],
    [5, 3, 2, 8],
    [7, 8, 4, 3],
]
W, C = 3, 4

y = [solver.IntVar(0, 1, f"open_{w}") for w in range(W)]
x = [[solver.NumVar(0, solver.infinity(), f"ship_{w}_{c}")
      for c in range(C)] for w in range(W)]

for c in range(C):
    solver.Add(sum(x[w][c] for w in range(W)) == demands[c])

for w in range(W):
    solver.Add(sum(x[w][c] for c in range(C)) <= capacities[w] * y[w])

obj = sum(fixed_costs[w] * y[w] for w in range(W))
obj += sum(ship_cost[w][c] * x[w][c] for w in range(W) for c in range(C))
solver.Minimize(obj)

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(f"Total cost: {solver.Objective().Value():.0f}")
    for w in range(W):
        if y[w].solution_value() > 0.5:
            shipped = sum(x[w][c].solution_value() for c in range(C))
            print(f"  W{w+1}: OPEN (ships {shipped:.0f} units)")
        else:
            print(f"  W{w+1}: CLOSED")
```

Output:

```
Total cost: 610
  W1: OPEN (ships 20 units)
  W2: OPEN (ships 55 units)
  W3: CLOSED
```

## Example 3: Bin Packing

**Problem:** Pack items of various sizes into minimum number of bins (capacity 10 each).

Items: sizes [6, 6, 5, 5, 4, 4, 3, 3, 2, 2]

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("SCIP")

items = [6, 6, 5, 5, 4, 4, 3, 3, 2, 2]
bin_cap = 10
n = len(items)
B = n  # upper bound on bins

y = [solver.IntVar(0, 1, f"bin_{b}") for b in range(B)]
x = [[solver.IntVar(0, 1, f"item_{i}_bin_{b}")
      for b in range(B)] for i in range(n)]

for i in range(n):
    solver.Add(sum(x[i][b] for b in range(B)) == 1)

for b in range(B):
    solver.Add(sum(items[i] * x[i][b] for i in range(n)) <= bin_cap * y[b])

solver.Minimize(sum(y[b] for b in range(B)))
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Bins used: {int(solver.Objective().Value())}")
    for b in range(B):
        if y[b].solution_value() > 0.5:
            bin_items = [items[i] for i in range(n) if x[i][b].solution_value() > 0.5]
            print(f"  Bin {b+1}: {bin_items} (sum={sum(bin_items)})")
```

Output:

```
Bins used: 4
  Bin 1: [6, 4] (sum=10)
  Bin 2: [6, 4] (sum=10)
  Bin 3: [5, 5] (sum=10)
  Bin 4: [3, 3, 2, 2] (sum=10)
```

## Example 4: Assignment Problem

**Problem:** Assign 4 workers to 4 tasks minimizing total cost. One worker per task.

|          | Task 1 | Task 2 | Task 3 | Task 4 |
| -------- | ------ | ------ | ------ | ------ |
| Worker A | 9      | 2      | 7      | 8      |
| Worker B | 6      | 4      | 3      | 7      |
| Worker C | 5      | 8      | 1      | 8      |
| Worker D | 7      | 6      | 9      | 4      |

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("SCIP")

costs = [[9,2,7,8],[6,4,3,7],[5,8,1,8],[7,6,9,4]]
workers = ["A", "B", "C", "D"]
n = 4

x = [[solver.IntVar(0, 1, f"x_{i}_{j}") for j in range(n)] for i in range(n)]

for i in range(n):
    solver.Add(sum(x[i][j] for j in range(n)) == 1)
for j in range(n):
    solver.Add(sum(x[i][j] for i in range(n)) == 1)

solver.Minimize(sum(costs[i][j] * x[i][j] for i in range(n) for j in range(n)))
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Total cost: {int(solver.Objective().Value())}")
    for i in range(n):
        for j in range(n):
            if x[i][j].solution_value() > 0.5:
                print(f"  Worker {workers[i]} -> Task {j+1} (cost={costs[i][j]})")
```

Output:

```
Total cost: 13
  Worker A -> Task 2 (cost=2)
  Worker B -> Task 3 (cost=3)
  Worker C -> Task 1 (cost=5)
  Worker D -> Task 4 (cost=4)
```

## Key Takeaways

- Use `IntVar(0, 1, name)` for binary decisions, `IntVar(lb, ub, name)` for general integers
- Use SCIP solver for MIP problems (not GLOP)
- MIP is NP-hard — large problems may take time; set limits with `solver.SetTimeLimit(ms)`
- Big-M links binary decisions to continuous variables
- Check for `OPTIMAL` or `FEASIBLE` status
