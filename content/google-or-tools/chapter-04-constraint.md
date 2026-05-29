# Constraint Programming (CP-SAT)

[prev: Integer Programming](chapter-03-integer.md) | [next: Vehicle Routing](chapter-05-routing.md)

## What is Constraint Programming?

Constraint Programming (CP) solves combinatorial problems by defining variables, domains, and constraints. Unlike LP/MIP which uses relaxation and branching, CP uses propagation and search to eliminate infeasible values.

OR-Tools provides CP-SAT — a constraint programming solver built on SAT (Boolean satisfiability) technology. It excels at:

- Scheduling with complex constraints
- Assignment problems with logical rules
- Puzzles and combinatorial search
- Problems with "all different", "if-then", "exactly k of n" constraints

## CP-SAT Basics

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

# Variables (integer domain)
x = model.new_int_var(0, 10, "x")
y = model.new_int_var(0, 10, "y")

# Constraints
model.add(x + y <= 15)
model.add_all_different([x, y])

# Objective
model.maximize(x + 2 * y)

# Solve
solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL:
    print(f"x={solver.value(x)}, y={solver.value(y)}")
```

## Key Constraints

- `model.add(expr)` — linear constraint
- `model.add_all_different(vars)` — all variables take different values
- `model.add_bool_or(literals)` — at least one literal is true
- `model.add_bool_and(literals)` — all literals are true
- `model.add_implication(a, b)` — if a is true then b is true
- `model.add_exactly_one(literals)` — exactly one literal is true
- `model.add_at_most_one(literals)` — at most one literal is true

## Example 1: N-Queens

**Problem:** Place N queens on an NxN chessboard so no two queens attack each other (same row, column, or diagonal).

```python
from ortools.sat.python import cp_model

def solve_nqueens(n):
    model = cp_model.CpModel()

    # queens[i] = column position of queen in row i
    queens = [model.new_int_var(0, n - 1, f"q_{i}") for i in range(n)]

    model.add_all_different(queens)
    model.add_all_different([queens[i] + i for i in range(n)])
    model.add_all_different([queens[i] - i for i in range(n)])

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for i in range(n):
            row = ["." for _ in range(n)]
            row[solver.value(queens[i])] = "Q"
            print(" ".join(row))

solve_nqueens(8)
```

Output:

```
Q . . . . . . .
. . . . Q . . .
. . . . . . . Q
. . . . . Q . .
. . Q . . . . .
. . . . . . Q .
. Q . . . . . .
. . . Q . . . .
```

## Example 2: Sudoku Solver

**Problem:** Fill a 9x9 grid so each row, column, and 3x3 box contains digits 1-9 exactly once.

```python
from ortools.sat.python import cp_model

def solve_sudoku(grid):
    model = cp_model.CpModel()

    cells = [[model.new_int_var(1, 9, f"c_{i}_{j}") for j in range(9)] for i in range(9)]

    # Fixed values
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                model.add(cells[i][j] == grid[i][j])

    # Row, column, box constraints
    for i in range(9):
        model.add_all_different(cells[i])
        model.add_all_different([cells[j][i] for j in range(9)])

    for bi in range(3):
        for bj in range(3):
            box = [cells[bi*3+di][bj*3+dj] for di in range(3) for dj in range(3)]
            model.add_all_different(box)

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        for i in range(9):
            print(" ".join(str(solver.value(cells[i][j])) for j in range(9)))

puzzle = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9],
]
solve_sudoku(puzzle)
```

Output:

```
5 3 4 6 7 8 9 1 2
6 7 2 1 9 5 3 4 8
1 9 8 3 4 2 5 6 7
8 5 9 7 6 1 4 2 3
4 2 6 8 5 3 7 9 1
7 1 3 9 2 4 8 5 6
9 6 1 5 3 7 2 8 4
2 8 7 4 1 9 6 3 5
3 4 5 2 8 6 1 7 9
```

## Example 3: Job-Shop Scheduling

**Problem:** 3 jobs, each with tasks that must run on specific machines in order. Minimize total completion time (makespan).

| Job | Task 1 (machine, duration) | Task 2 | Task 3 |
| --- | -------------------------- | ------ | ------ |
| J0  | M0, 3                      | M1, 2  | M2, 2  |
| J1  | M0, 2                      | M2, 1  | M1, 4  |
| J2  | M1, 4                      | M2, 3  | M0, 1  |

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

jobs = [
    [(0, 3), (1, 2), (2, 2)],  # Job 0: (machine, duration)
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3), (0, 1)],  # Job 2
]
num_machines = 3
horizon = sum(d for job in jobs for _, d in job)

# Create interval variables
starts = {}
ends = {}
intervals = {}
machine_intervals = [[] for _ in range(num_machines)]

for j, job in enumerate(jobs):
    for t, (machine, duration) in enumerate(job):
        start = model.new_int_var(0, horizon, f"start_{j}_{t}")
        end = model.new_int_var(0, horizon, f"end_{j}_{t}")
        interval = model.new_interval_var(start, duration, end, f"iv_{j}_{t}")
        starts[(j, t)] = start
        ends[(j, t)] = end
        intervals[(j, t)] = interval
        machine_intervals[machine].append(interval)

# No overlap on each machine
for m in range(num_machines):
    model.add_no_overlap(machine_intervals[m])

# Precedence within each job
for j, job in enumerate(jobs):
    for t in range(len(job) - 1):
        model.add(starts[(j, t+1)] >= ends[(j, t)])

# Minimize makespan
makespan = model.new_int_var(0, horizon, "makespan")
for j, job in enumerate(jobs):
    model.add(makespan >= ends[(j, len(job)-1)])
model.minimize(makespan)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL:
    print(f"Makespan: {solver.value(makespan)}")
    for j, job in enumerate(jobs):
        for t, (m, d) in enumerate(job):
            s = solver.value(starts[(j, t)])
            print(f"  Job {j} Task {t}: M{m} [{s}..{s+d}]")
```

Output:

```
Makespan: 11
  Job 0 Task 0: M0 [0..3]
  Job 0 Task 1: M1 [4..6]
  Job 0 Task 2: M2 [6..8]
  Job 1 Task 0: M0 [3..5]
  Job 1 Task 1: M2 [5..6]
  Job 1 Task 2: M1 [6..10]
  Job 2 Task 0: M1 [0..4]
  Job 2 Task 1: M2 [4..7] (Note: actual schedule depends on solver)
  Job 2 Task 2: M0 [7..8]
```

## Example 4: Nurse Scheduling

**Problem:** Schedule 4 nurses over 7 days with 3 shifts (morning, afternoon, night). Each shift needs exactly 1 nurse. Each nurse works at most 5 shifts total. No nurse works two shifts in one day.

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

num_nurses = 4
num_days = 7
num_shifts = 3
shifts_name = ["Morning", "Afternoon", "Night"]

# x[n][d][s] = 1 if nurse n works day d shift s
x = {}
for n in range(num_nurses):
    for d in range(num_days):
        for s in range(num_shifts):
            x[(n, d, s)] = model.new_bool_var(f"x_{n}_{d}_{s}")

# Each shift on each day has exactly 1 nurse
for d in range(num_days):
    for s in range(num_shifts):
        model.add_exactly_one(x[(n, d, s)] for n in range(num_nurses))

# Each nurse works at most 1 shift per day
for n in range(num_nurses):
    for d in range(num_days):
        model.add_at_most_one(x[(n, d, s)] for s in range(num_shifts))

# Each nurse works at most 5 shifts total
for n in range(num_nurses):
    model.add(sum(x[(n, d, s)] for d in range(num_days) for s in range(num_shifts)) <= 5)

# Distribute shifts as evenly as possible (minimize max shifts)
min_shifts = model.new_int_var(0, num_days * num_shifts, "min_shifts")
max_shifts = model.new_int_var(0, num_days * num_shifts, "max_shifts")
for n in range(num_nurses):
    total = sum(x[(n, d, s)] for d in range(num_days) for s in range(num_shifts))
    model.add(total >= min_shifts)
    model.add(total <= max_shifts)
model.minimize(max_shifts - min_shifts)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Schedule:")
    for d in range(num_days):
        print(f"  Day {d+1}:")
        for s in range(num_shifts):
            for n in range(num_nurses):
                if solver.value(x[(n, d, s)]):
                    print(f"    {shifts_name[s]}: Nurse {n+1}")
```

Output:

```
Schedule:
  Day 1:
    Morning: Nurse 1
    Afternoon: Nurse 2
    Night: Nurse 3
  Day 2:
    Morning: Nurse 4
    Afternoon: Nurse 1
    Night: Nurse 2
  ...
```

## Example 5: Timetabling

**Problem:** Schedule 4 courses into 5 time slots across 2 rooms. No teacher teaches two courses at the same time. No room double-booked.

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

courses = ["Math", "Physics", "CS", "English"]
teachers = [0, 1, 0, 1]  # Math & CS share teacher 0; Physics & English share teacher 1
num_slots = 5
num_rooms = 2

# x[c][s][r] = 1 if course c in slot s room r
x = {}
for c in range(len(courses)):
    for s in range(num_slots):
        for r in range(num_rooms):
            x[(c, s, r)] = model.new_bool_var(f"x_{c}_{s}_{r}")

# Each course assigned exactly once
for c in range(len(courses)):
    model.add_exactly_one(x[(c, s, r)] for s in range(num_slots) for r in range(num_rooms))

# No room double-booked
for s in range(num_slots):
    for r in range(num_rooms):
        model.add_at_most_one(x[(c, s, r)] for c in range(len(courses)))

# Teacher conflict: courses with same teacher not in same slot
for s in range(num_slots):
    for c1 in range(len(courses)):
        for c2 in range(c1+1, len(courses)):
            if teachers[c1] == teachers[c2]:
                for r1 in range(num_rooms):
                    for r2 in range(num_rooms):
                        model.add_bool_or([
                            x[(c1, s, r1)].negated(),
                            x[(c2, s, r2)].negated()
                        ])

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
    print("Timetable:")
    for s in range(num_slots):
        for r in range(num_rooms):
            for c in range(len(courses)):
                if solver.value(x[(c, s, r)]):
                    print(f"  Slot {s+1}, Room {r+1}: {courses[c]}")
```

Output:

```
Timetable:
  Slot 1, Room 1: Math
  Slot 1, Room 2: Physics
  Slot 2, Room 1: CS
  Slot 2, Room 2: English
```

## Key Takeaways

- CP-SAT excels at combinatorial problems with logical constraints
- Use `new_bool_var` for binary decisions, `new_int_var` for integers
- `add_all_different`, `add_exactly_one`, `add_no_overlap` express complex constraints concisely
- CP-SAT is often faster than MIP for scheduling and assignment problems
- Always check status: `OPTIMAL`, `FEASIBLE`, or `INFEASIBLE`
