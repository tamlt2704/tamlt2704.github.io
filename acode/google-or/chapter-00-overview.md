# Chapter 0: Before You Start

[Chapter 1: Your First Constraint →](chapter-01-first-constraint.md)

---

## The Story

This is a series about Google OR-Tools — but not the kind where you memorize "it's a constraint solver" and move on.

You're an operations engineer at **ShiftRight**, a workforce management startup that schedules nurses, drivers, and warehouse workers for mid-size companies. The company started with a spreadsheet. Then the spreadsheet got macros. Then the macros got macros. Now you have a 14,000-line VBA monster that takes 3 hours to produce a weekly schedule — and the schedule is usually wrong.

Your CTO, **Nadia**, calls an emergency meeting:

"Memorial General Hospital just signed. 200 nurses. 3 shifts. 40 constraints — certifications, overtime limits, consecutive day caps, weekend fairness, vacation blackouts. The spreadsheet crashed. Excel literally said 'not enough memory.' We need a real solver. We need it in two weeks."

You nod. You've heard of optimization. Linear programming. Constraint satisfaction. How hard can it be?

Over the next 12 chapters, you'll take OR-Tools from "I can solve a toy puzzle" to running a production scheduling engine that handles thousands of variables and hundreds of constraints in seconds. Along the way, everything will break in instructive ways. The solver will say "infeasible" when you know a solution exists. It'll return a technically valid schedule that puts the same nurse on 7 night shifts in a row. It'll take 45 minutes on a problem that should take 5 seconds.

Each disaster teaches you something about modeling, constraint propagation, search strategies, or objective design that no API reference could. You'll fix every bug, understand why it happened, and build the intuition to model new problems from scratch.

By the end, you'll have a production-grade scheduling system with constraint programming, linear programming, vehicle routing, bin packing, and job-shop scheduling — and you'll understand *when* to reach for each tool.

## How to Read This

Every chapter is the same loop:

1. A client has a scheduling or optimization problem that can't be solved by hand
2. You model the problem — variables, constraints, objective
3. You learn the OR-Tools component that solves it
4. You implement the solution
5. You verify it works — then discover the model is wrong in some subtle way

No concept shows up before you need it. You won't hear about linear programming until constraint programming can't optimize cost. You won't touch vehicle routing until a client needs delivery optimization and building it from scratch would take months.

The broken schedule comes first. The solver follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Operations Engineer | Analytical, allergic to manual processes |
| **Nadia** | CTO | "If it can't scale to 10 clients, don't build it." |
| **Dr. Patel** | Hospital Admin | "Nurse fatigue kills patients. Get the schedule right." |
| **Tomás** | Logistics Manager | "My drivers are doing 300km when 180km is possible." |
| **Finance Fiona** | CFO | "Overtime is 47% of labor cost. Fix it." |
| **The Intern** | Summer hire | Built the original spreadsheet. It was supposed to be temporary. |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | Assign 8 nurses to shifts without conflicts | CP-SAT basics — variables, constraints, solving |
| 2 | No nurse works 3 nights in a row | Sequence constraints, forbidden patterns |
| 3 | Minimize overtime while covering all shifts | Objectives — minimization, soft constraints |
| 4 | "Infeasible" but a solution clearly exists | Debugging models, conflicting constraints, assumptions |
| 5 | Fair weekend distribution across 200 nurses | Symmetry breaking, load balancing, multi-objective |
| 6 | Assign tasks to machines, minimize makespan | Job-shop scheduling, intervals, no-overlap |
| 7 | Cut steel bars with minimal waste | Bin packing, knapsack, linear programming |
| 8 | Route 15 delivery trucks across a city | Vehicle Routing Problem (VRP), distance matrices |
| 9 | VRP with time windows and capacity | Constraints on routes — pickup/delivery, breaks |
| 10 | The solver takes 45 minutes | Search strategies, hints, parallelism, tuning |
| 11 | Requirements change mid-solve | Incremental solving, warm starts, re-optimization |
| 12 | Ship it: API, validation, monitoring | Production deployment — input validation, timeouts, fallbacks |

## Prerequisites

Three things: Python 3, OR-Tools, and a problem worth solving.

### Python 3.10+

```bash
python3 --version
# Python 3.10.x or higher
```

### Google OR-Tools

Install the Python package:

```bash
pip install ortools
```

Verify:

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()
x = model.new_int_var(0, 10, "x")
model.add(x >= 5)

solver = cp_model.CpSolver()
status = solver.solve(model)
print(f"x = {solver.value(x)}")  # x = 5
```

If that prints `x = 5`, you're in business.

### What IS OR-Tools?

Google OR-Tools is an open-source suite for combinatorial optimization. It includes:

| Component | Solves | Example |
|---|---|---|
| **CP-SAT** | Constraint satisfaction & optimization | Scheduling, puzzles, assignment |
| **Linear Solver** | Linear/mixed-integer programming | Cost minimization, resource allocation |
| **Routing** | Vehicle routing problems | Delivery routes, TSP |
| **Graph algorithms** | Network flows, assignment | Min-cost flow, matching |

CP-SAT is the workhorse. You'll spend 80% of your time there. It's fast, expressive, and handles most real-world scheduling problems. The other components exist for problems with specific structure that CP-SAT can solve but not as efficiently.

### The Mental Model

Every OR-Tools problem has three parts:

1. **Variables** — the decisions you're making ("Which nurse works Tuesday night?")
2. **Constraints** — the rules that must hold ("No nurse works more than 5 days in a row")
3. **Objective** — what you're optimizing ("Minimize total overtime hours")

If you can express your problem in these three parts, OR-Tools can solve it. The hard part isn't the API — it's the modeling. Turning a messy real-world requirement into clean variables, constraints, and objectives. That's what this series teaches.

### Optional: Graphviz

For visualizing schedules and routes in later chapters:

```bash
pip install graphviz matplotlib
```

### Quick Check

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()
solver = cp_model.CpSolver()

# Can we find x, y where x + y = 10 and x > y?
x = model.new_int_var(0, 10, "x")
y = model.new_int_var(0, 10, "y")
model.add(x + y == 10)
model.add(x > y)

status = solver.solve(model)
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"x={solver.value(x)}, y={solver.value(y)} ✓")
else:
    print("Something's wrong with your install")
```

If you see values where x + y = 10 and x > y, you're ready.

## Why Not Just Use a Spreadsheet?

The spreadsheet works until it doesn't. Here's the math:

A hospital with 50 nurses, 3 shifts, and 7 days has **50 × 3 × 7 = 1,050** binary decisions (does nurse N work shift S on day D?). That's 2^1050 possible schedules — more than atoms in the observable universe. A spreadsheet tries random swaps. A solver uses constraint propagation and intelligent search to find optimal solutions in seconds.

The difference between "works for 10 nurses" and "works for 200 nurses" isn't better hardware. It's better algorithms.

Let's schedule some nurses.

---

[Chapter 1: Your First Constraint →](chapter-01-first-constraint.md)
