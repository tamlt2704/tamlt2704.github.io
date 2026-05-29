# Google OR-Tools: Solve Optimization Problems with Python

[next: Setup](chapter-01-setup.md)

## What is Operations Research?

Operations Research (OR) is the discipline of applying advanced analytical methods to make better decisions. It uses mathematical modeling and optimization to find the best possible solution to complex problems.

OR answers questions like:

- What is the shortest route for a delivery truck visiting 50 customers?
- How should we schedule 200 nurses across 3 shifts to be fair and meet demand?
- Which warehouse should fulfill each order to minimize shipping cost?

## What is Google OR-Tools?

Google OR-Tools is an open-source optimization library developed by Google. It provides solvers for:

- **Linear Programming (LP)** — optimize continuous variables with linear constraints
- **Integer Programming (MIP)** — optimize with integer/binary decision variables
- **Constraint Programming (CP-SAT)** — solve combinatorial problems with complex constraints
- **Vehicle Routing (VRP)** — optimize routes for fleets of vehicles
- **Graph Algorithms** — shortest paths, max flow, min cost flow, assignment

OR-Tools supports Python, C++, Java, and C#. This guide uses Python.

## Real-World Applications

**Logistics and Transportation**

- Delivery route optimization (Amazon, UPS, FedEx)
- Fleet management and vehicle dispatching
- Supply chain network design

**Scheduling**

- Employee shift scheduling (hospitals, call centers)
- Production line scheduling (manufacturing)
- Sports league fixture scheduling
- University timetabling

**Resource Allocation**

- Budget allocation across projects
- Workforce planning
- Inventory management
- Cutting stock problems in manufacturing

## Chapter Overview

1. [Setup and Installation](chapter-01-setup.md) — install OR-Tools, verify, first example
2. [Linear Programming](chapter-02-linear.md) — LP fundamentals, MPSolver, production planning
3. [Integer Programming](chapter-03-integer.md) — MIP, knapsack, facility location, bin packing
4. [Constraint Programming](chapter-04-constraint.md) — CP-SAT, N-Queens, scheduling, Sudoku
5. [Vehicle Routing](chapter-05-routing.md) — TSP, CVRP, time windows, multi-vehicle
6. [Scheduling](chapter-06-scheduling.md) — intervals, no-overlap, job-shop, shifts
7. [Graph Algorithms](chapter-07-graph.md) — shortest path, max flow, assignment
8. [Real Projects](chapter-08-projects.md) — complete end-to-end optimization projects

## Why OR-Tools?

| Feature                | OR-Tools        | PuLP              | scipy.optimize |
| ---------------------- | --------------- | ----------------- | -------------- |
| Linear Programming     | Yes             | Yes               | Yes            |
| Integer Programming    | Yes             | Yes               | Limited        |
| Constraint Programming | Yes (CP-SAT)    | No                | No             |
| Vehicle Routing        | Yes             | No                | No             |
| Graph Algorithms       | Yes             | No                | No             |
| Performance            | High (C++ core) | Depends on solver | Moderate       |

OR-Tools combines multiple solver types in one library with a consistent Python API, making it the most versatile free optimization toolkit available.
