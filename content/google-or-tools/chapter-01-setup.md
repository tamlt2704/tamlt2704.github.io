# Setup and Installation

[prev: Overview](chapter-00-overview.md) | [next: Linear Programming](chapter-02-linear.md)

## Install OR-Tools

```python
pip install ortools
```

## Verify Installation

```python
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from ortools.graph.python import min_cost_flow

print("OR-Tools imported successfully!")
```

## OR-Tools Components

**Linear Solver (MPSolver)**
Solves linear and mixed-integer programming problems. Wraps multiple backends:

- GLOP — Google's linear programming solver
- SCIP — mixed-integer programming
- CBC — open-source MIP solver

**Constraint Solver (CP-SAT)**
Solves combinatorial optimization with complex constraints. Best for:

- Scheduling problems
- Assignment problems
- Puzzles (Sudoku, N-Queens)
- Problems with logical constraints (if-then, all-different)

**Routing Solver**
Specialized for vehicle routing problems:

- Traveling Salesman Problem (TSP)
- Capacitated Vehicle Routing (CVRP)
- Vehicle Routing with Time Windows (VRPTW)

**Graph Algorithms**
Classic network optimization:

- Shortest path
- Maximum flow
- Minimum cost flow
- Linear sum assignment

## First Example: Simple Linear Optimization

**Problem:** A factory makes chairs and tables. Each chair gives 20 profit and uses 1 hour of labor and 4 units of wood. Each table gives 30 profit and uses 2 hours of labor and 3 units of wood. Available: 40 hours of labor, 120 units of wood. Maximize profit.

```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("GLOP")

chairs = solver.NumVar(0, solver.infinity(), "chairs")
tables = solver.NumVar(0, solver.infinity(), "tables")

# Constraints
solver.Add(1 * chairs + 2 * tables <= 40)   # labor hours
solver.Add(4 * chairs + 3 * tables <= 120)  # wood units

# Objective: maximize profit
solver.Maximize(20 * chairs + 30 * tables)

status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print(f"Chairs: {chairs.solution_value():.1f}")
    print(f"Tables: {tables.solution_value():.1f}")
    print(f"Profit: {solver.Objective().Value():.1f}")
else:
    print("No optimal solution found.")
```

Output:

```
Chairs: 24.0
Tables: 8.0
Profit: 720.0
```

The solver found that making 24 chairs and 8 tables maximizes profit at 720, using all available labor and wood.

## Solver Status Codes

Always check the status before reading solution values:

```python
# For MPSolver (LP/MIP)
pywraplp.Solver.OPTIMAL      # found optimal solution
pywraplp.Solver.FEASIBLE     # found a solution (may not be optimal for MIP)
pywraplp.Solver.INFEASIBLE   # no solution exists
pywraplp.Solver.UNBOUNDED    # objective can grow without bound

# For CP-SAT
cp_model.OPTIMAL             # proven optimal
cp_model.FEASIBLE            # found solution, optimality not proven
cp_model.INFEASIBLE          # no solution
cp_model.MODEL_INVALID       # model has errors
```
