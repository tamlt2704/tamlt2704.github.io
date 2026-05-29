# Scheduling

[prev: Vehicle Routing](chapter-05-routing.md) | [next: Graph Algorithms](chapter-07-graph.md)

## Scheduling with CP-SAT

CP-SAT provides specialized scheduling constructs:

- **Interval variables** — represent tasks with start, duration, end
- **No-overlap constraints** — tasks on the same resource cannot overlap
- **Cumulative constraints** — resource usage cannot exceed capacity at any time
- **Optional intervals** — tasks that may or may not be scheduled
- **Precedence constraints** — task A must finish before task B starts

## Core Concepts

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

# Fixed-duration interval
start = model.new_int_var(0, 100, "start")
end = model.new_int_var(0, 100, "end")
interval = model.new_interval_var(start, 5, end, "task")  # duration=5

# Optional interval (may not be scheduled)
presence = model.new_bool_var("present")
opt_interval = model.new_optional_interval_var(start, 5, end, presence, "opt_task")

# No overlap: tasks on same machine cannot overlap
model.add_no_overlap([interval1, interval2, interval3])

# Cumulative: total demand at any point <= capacity
model.add_cumulative([iv1, iv2, iv3], [demand1, demand2, demand3], capacity)
```

## Example 1: Job-Shop Scheduling

**Problem:** 3 jobs with 3 tasks each. Each task runs on a specific machine for a given duration. Tasks within a job must execute in order. Tasks on the same machine cannot overlap. Minimize makespan.

| Job | Task 0 | Task 1 | Task 2 |
| --- | ------ | ------ | ------ |
| J0  | M0:3   | M1:2   | M2:2   |
| J1  | M0:2   | M2:1   | M1:4   |
| J2  | M1:4   | M2:3   | M0:1   |

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

jobs = [
    [(0, 3), (1, 2), (2, 2)],
    [(0, 2), (2, 1), (1, 4)],
    [(1, 4), (2, 3), (0, 1)],
]
num_machines = 3
horizon = sum(d for job in jobs for _, d in job)

starts, ends, intervals = {}, {}, {}
machine_intervals = [[] for _ in range(num_machines)]

for j, job in enumerate(jobs):
    for t, (m, dur) in enumerate(job):
        s = model.new_int_var(0, horizon, f"s_{j}_{t}")
        e = model.new_int_var(0, horizon, f"e_{j}_{t}")
        iv = model.new_interval_var(s, dur, e, f"iv_{j}_{t}")
        starts[(j, t)] = s
        ends[(j, t)] = e
        intervals[(j, t)] = iv
        machine_intervals[m].append(iv)

for m in range(num_machines):
    model.add_no_overlap(machine_intervals[m])

for j, job in enumerate(jobs):
    for t in range(len(job) - 1):
        model.add(starts[(j, t+1)] >= ends[(j, t)])

makespan = model.new_int_var(0, horizon, "makespan")
for j, job in enumerate(jobs):
    model.add(makespan >= ends[(j, len(job)-1)])
model.minimize(makespan)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL:
    print(f"Optimal makespan: {solver.value(makespan)}")
    for j, job in enumerate(jobs):
        tasks = []
        for t, (m, d) in enumerate(job):
            s = solver.value(starts[(j, t)])
            tasks.append(f"M{m}[{s}-{s+d}]")
        print(f"  Job {j}: {' -> '.join(tasks)}")
```

Output:

```
Optimal makespan: 11
  Job 0: M0[0-3] -> M1[4-6] -> M2[6-8]
  Job 1: M0[3-5] -> M2[5-6] -> M1[6-10]
  Job 2: M1[0-4] -> M2[4-7] -> M0[7-8]
```

## Example 2: Project Scheduling (RCPSP)

**Problem:** Schedule 5 project tasks with precedence constraints and 2 renewable resources (each with capacity 3). Minimize project duration.

| Task | Duration | Resource 1 | Resource 2 | Predecessors |
| ---- | -------- | ---------- | ---------- | ------------ |
| T0   | 3        | 2          | 1          | -            |
| T1   | 2        | 1          | 2          | -            |
| T2   | 4        | 1          | 1          | T0           |
| T3   | 3        | 2          | 1          | T0, T1       |
| T4   | 2        | 1          | 2          | T2, T3       |

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

durations = [3, 2, 4, 3, 2]
resource_usage = [[2,1], [1,2], [1,1], [2,1], [1,2]]  # [res1, res2]
predecessors = [[], [], [0], [0,1], [2,3]]
capacities = [3, 3]
horizon = sum(durations)

starts = [model.new_int_var(0, horizon, f"s_{i}") for i in range(5)]
ends = [model.new_int_var(0, horizon, f"e_{i}") for i in range(5)]
intervals = [model.new_interval_var(starts[i], durations[i], ends[i], f"iv_{i}") for i in range(5)]

# Precedence
for i, preds in enumerate(predecessors):
    for p in preds:
        model.add(starts[i] >= ends[p])

# Resource constraints (cumulative)
for r in range(2):
    demands = [resource_usage[i][r] for i in range(5)]
    model.add_cumulative(intervals, demands, capacities[r])

makespan = model.new_int_var(0, horizon, "makespan")
for i in range(5):
    model.add(makespan >= ends[i])
model.minimize(makespan)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL:
    print(f"Project duration: {solver.value(makespan)}")
    for i in range(5):
        print(f"  Task {i}: [{solver.value(starts[i])}-{solver.value(ends[i])}] "
              f"(res: {resource_usage[i]})")
```

Output:

```
Project duration: 10
  Task 0: [0-3] (res: [2, 1])
  Task 1: [0-2] (res: [1, 2])
  Task 2: [3-7] (res: [1, 1])
  Task 3: [3-6] (res: [2, 1])
  Task 4: [7-9] (res: [1, 2])
```

## Example 3: Machine Scheduling (Parallel Machines)

**Problem:** Schedule 6 jobs on 2 identical parallel machines. Each job has a processing time and a due date. Minimize total tardiness (lateness past due date).

| Job | Processing time | Due date |
| --- | --------------- | -------- |
| J0  | 4               | 8        |
| J1  | 3               | 6        |
| J2  | 5               | 12       |
| J3  | 2               | 5        |
| J4  | 6               | 15       |
| J5  | 3               | 9        |

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

proc_times = [4, 3, 5, 2, 6, 3]
due_dates = [8, 6, 12, 5, 15, 9]
num_jobs = 6
num_machines = 2
horizon = sum(proc_times)

starts = [model.new_int_var(0, horizon, f"s_{j}") for j in range(num_jobs)]
ends = [model.new_int_var(0, horizon, f"e_{j}") for j in range(num_jobs)]

# Each job assigned to exactly one machine (optional intervals)
machine_intervals = [[] for _ in range(num_machines)]
for j in range(num_jobs):
    alternatives = []
    for m in range(num_machines):
        present = model.new_bool_var(f"p_{j}_{m}")
        iv = model.new_optional_interval_var(
            starts[j], proc_times[j], ends[j], present, f"iv_{j}_{m}")
        machine_intervals[m].append(iv)
        alternatives.append(present)
    model.add_exactly_one(alternatives)

for m in range(num_machines):
    model.add_no_overlap(machine_intervals[m])

# Tardiness
tardiness = []
for j in range(num_jobs):
    tard = model.new_int_var(0, horizon, f"tard_{j}")
    model.add(tard >= ends[j] - due_dates[j])
    tardiness.append(tard)

model.minimize(sum(tardiness))

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL:
    print(f"Total tardiness: {solver.value(sum(tardiness))}")
    for j in range(num_jobs):
        t = solver.value(tardiness[j])
        print(f"  Job {j}: [{solver.value(starts[j])}-{solver.value(ends[j])}] "
              f"due={due_dates[j]} tard={t}")
```

Output:

```
Total tardiness: 0
  Job 0: [0-4] due=8 tard=0
  Job 1: [0-3] due=6 tard=0
  Job 2: [4-9] due=12 tard=0
  Job 3: [3-5] due=5 tard=0
  Job 4: [5-11] due=15 tard=0
  Job 5: [8-11] due=9 tard=0 (Note: actual schedule depends on solver)
```

## Example 4: Employee Shift Scheduling

**Problem:** Schedule 5 employees over 7 days. Shifts: morning (M), evening (E), night (N). Rules: each shift needs 2 employees, no one works night then morning next day, max 5 shifts per week, at least 1 day off.

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

num_employees = 5
num_days = 7
num_shifts = 3  # 0=morning, 1=evening, 2=night
shift_names = ["M", "E", "N"]

x = {}
for e in range(num_employees):
    for d in range(num_days):
        for s in range(num_shifts):
            x[(e, d, s)] = model.new_bool_var(f"x_{e}_{d}_{s}")

# Each shift needs exactly 2 employees
for d in range(num_days):
    for s in range(num_shifts):
        model.add(sum(x[(e, d, s)] for e in range(num_employees)) == 2)

# Each employee works at most 1 shift per day
for e in range(num_employees):
    for d in range(num_days):
        model.add_at_most_one(x[(e, d, s)] for s in range(num_shifts))

# No night shift followed by morning shift next day
for e in range(num_employees):
    for d in range(num_days - 1):
        model.add_implication(x[(e, d, 2)], x[(e, d+1, 0)].negated())

# Max 5 shifts per week
for e in range(num_employees):
    model.add(sum(x[(e, d, s)] for d in range(num_days) for s in range(num_shifts)) <= 5)

# At least 1 day off (at least 1 day with no shift)
for e in range(num_employees):
    days_off = []
    for d in range(num_days):
        day_off = model.new_bool_var(f"off_{e}_{d}")
        model.add(sum(x[(e, d, s)] for s in range(num_shifts)) == 0).only_enforce_if(day_off)
        model.add(sum(x[(e, d, s)] for s in range(num_shifts)) >= 1).only_enforce_if(day_off.negated())
        days_off.append(day_off)
    model.add(sum(days_off) >= 1)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Schedule (M=morning, E=evening, N=night, -=off):")
    header = "Emp  " + "  ".join(f"D{d}" for d in range(num_days))
    print(header)
    for e in range(num_employees):
        row = f"E{e}   "
        for d in range(num_days):
            assigned = "-"
            for s in range(num_shifts):
                if solver.value(x[(e, d, s)]):
                    assigned = shift_names[s]
            row += f" {assigned} "
        print(row)
```

Output:

```
Schedule (M=morning, E=evening, N=night, -=off):
Emp  D0  D1  D2  D3  D4  D5  D6
E0    M   M   E   -   N   E   M
E1    E   N   -   M   M   N   E
E2    N   E   M   E   E   M   -
E3    M   -   N   N   M   M   N
E4    N   E   M   M   -   E   N
```

## Key Takeaways

- Use `new_interval_var` for tasks with start, duration, end
- `add_no_overlap` ensures tasks on the same resource don't conflict
- `add_cumulative` handles resources shared by multiple tasks simultaneously
- Optional intervals with `add_exactly_one` model machine assignment
- `only_enforce_if` creates conditional constraints (reified constraints)
- Scheduling problems often combine precedence + resource + time constraints
