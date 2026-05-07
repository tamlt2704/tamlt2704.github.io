# Chapter 12: Production Deployment

[← Chapter 11: Incremental Solving](chapter-11-incremental.md)

---

## The Problem

The solver works on your laptop. Now it needs to work in production — handling requests from a web API, validating messy input data, respecting SLAs, and failing gracefully when things go wrong.

Nadia: "I don't care if it's optimal. I care that it responds in 30 seconds, never crashes, and tells the user something useful when it can't solve."

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│   API Layer  │────▶│   Solver    │
│  (React)    │◀────│  (FastAPI)   │◀────│  (OR-Tools) │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  Database   │
                    │ (schedules) │
                    └─────────────┘
```

The solver runs synchronously for small problems (< 5s) and asynchronously for large ones (> 5s).

## Input Validation

Never trust user input. Validate before building the model:

```python
from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum

class ShiftType(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"

class NurseAvailability(BaseModel):
    nurse_id: str
    unavailable_days: list[int] = []  # 0=Mon, 6=Sun
    max_shifts_per_week: int = 5
    preferred_shifts: list[ShiftType] = []
    certifications: list[str] = []

class ScheduleRequest(BaseModel):
    nurses: list[NurseAvailability]
    num_days: int = 7
    shifts_per_day: dict[ShiftType, int]  # e.g., {"morning": 3, "afternoon": 3, "night": 2}
    constraints: dict = {}
    time_limit_seconds: float = 30.0

    @validator("nurses")
    def validate_nurses(cls, v):
        if len(v) < 1:
            raise ValueError("At least 1 nurse required")
        if len(v) > 500:
            raise ValueError("Maximum 500 nurses supported")
        return v

    @validator("num_days")
    def validate_days(cls, v):
        if v < 1 or v > 28:
            raise ValueError("Schedule must be 1-28 days")
        return v

    @validator("time_limit_seconds")
    def validate_time_limit(cls, v):
        if v < 1 or v > 300:
            raise ValueError("Time limit must be 1-300 seconds")
        return v
```

## Feasibility Pre-Check

Before running the solver, catch obvious problems:

```python
def pre_check(request: ScheduleRequest) -> tuple[bool, str]:
    """Quick feasibility check before solving."""

    total_slots_needed = sum(request.shifts_per_day.values()) * request.num_days
    total_slots_available = sum(
        n.max_shifts_per_week * (request.num_days / 7)
        for n in request.nurses
    )

    if total_slots_available < total_slots_needed * 0.9:
        deficit = total_slots_needed - int(total_slots_available)
        return False, (
            f"Insufficient staff: need {total_slots_needed} shift-slots, "
            f"have ~{int(total_slots_available)} available. "
            f"Add {deficit // request.num_days + 1} more nurses or reduce coverage."
        )

    # Check if any day is impossible
    available_per_day = {}
    for d in range(request.num_days):
        available = sum(1 for n in request.nurses if d % 7 not in n.unavailable_days)
        needed = sum(request.shifts_per_day.values())
        if available < needed:
            day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d % 7]
            return False, (
                f"Day {d} ({day_name}): only {available} nurses available, "
                f"need {needed}. Check unavailability settings."
            )

    return True, "Pre-check passed"
```

## The API

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from datetime import datetime
import uuid

app = FastAPI(title="ShiftRight Scheduler API")

# In-memory store (use a real DB in production)
solve_results = {}

@app.post("/schedule/solve")
async def solve_schedule(request: ScheduleRequest, background_tasks: BackgroundTasks):
    """Submit a scheduling request."""

    # Pre-check
    feasible, message = pre_check(request)
    if not feasible:
        raise HTTPException(status_code=422, detail=message)

    # For small problems, solve synchronously
    estimated_time = estimate_solve_time(request)

    if estimated_time < 5:
        result = run_solver(request)
        return {
            "status": result["status"],
            "schedule": result.get("schedule"),
            "metrics": result.get("metrics"),
            "message": result.get("message"),
        }
    else:
        # Large problem: solve asynchronously
        job_id = str(uuid.uuid4())
        solve_results[job_id] = {"status": "running", "submitted": datetime.now().isoformat()}
        background_tasks.add_task(solve_async, job_id, request)
        return {"status": "accepted", "job_id": job_id, "estimated_seconds": estimated_time}

@app.get("/schedule/status/{job_id}")
async def get_status(job_id: str):
    """Check the status of an async solve."""
    if job_id not in solve_results:
        raise HTTPException(status_code=404, detail="Job not found")
    return solve_results[job_id]

def estimate_solve_time(request: ScheduleRequest) -> float:
    """Rough estimate of solve time based on problem size."""
    num_vars = len(request.nurses) * request.num_days * len(request.shifts_per_day)
    if num_vars < 500:
        return 1
    elif num_vars < 5000:
        return 10
    else:
        return 60
```

## The Solver Wrapper

```python
from ortools.sat.python import cp_model
import time

def run_solver(request: ScheduleRequest) -> dict:
    """Build and solve the scheduling model."""
    start_time = time.time()

    try:
        model, variables = build_model(request)
    except ModelBuildError as e:
        return {"status": "error", "message": f"Model build failed: {e}"}

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = min(request.time_limit_seconds, 300)
    solver.parameters.num_workers = 8
    solver.parameters.relative_gap_limit = 0.05  # 5% gap is acceptable

    status = solver.solve(model)
    elapsed = time.time() - start_time

    if status == cp_model.OPTIMAL:
        schedule = extract_schedule(solver, variables, request)
        return {
            "status": "optimal",
            "schedule": schedule,
            "metrics": {
                "solve_time_seconds": elapsed,
                "objective_value": solver.objective_value,
                "gap": 0.0,
            },
        }
    elif status == cp_model.FEASIBLE:
        schedule = extract_schedule(solver, variables, request)
        gap = abs(solver.objective_value - solver.best_objective_bound) / max(1, abs(solver.objective_value))
        return {
            "status": "feasible",
            "schedule": schedule,
            "metrics": {
                "solve_time_seconds": elapsed,
                "objective_value": solver.objective_value,
                "gap": gap,
            },
            "message": f"Solution found but not proven optimal (gap: {gap:.1%})",
        }
    elif status == cp_model.INFEASIBLE:
        # Try to diagnose
        diagnosis = diagnose_infeasibility(request)
        return {
            "status": "infeasible",
            "message": "No valid schedule exists with current constraints",
            "diagnosis": diagnosis,
        }
    else:
        return {
            "status": "timeout",
            "message": f"Solver did not find a solution within {request.time_limit_seconds}s",
            "suggestion": "Try increasing time_limit_seconds or reducing problem size",
        }
```

## Error Handling

```python
class ModelBuildError(Exception):
    """Raised when the model can't be constructed."""
    pass

def build_model(request: ScheduleRequest):
    """Build the CP-SAT model from a request. Raises ModelBuildError on failure."""

    model = cp_model.CpModel()
    nurses = range(len(request.nurses))
    days = range(request.num_days)
    shift_types = list(request.shifts_per_day.keys())
    shifts = range(len(shift_types))

    # Validate shift requirements
    for shift_type, count in request.shifts_per_day.items():
        if count < 0:
            raise ModelBuildError(f"Negative nurse count for {shift_type}: {count}")
        if count > len(request.nurses):
            raise ModelBuildError(
                f"Shift {shift_type} requires {count} nurses but only "
                f"{len(request.nurses)} exist"
            )

    # Build variables and constraints...
    x = {}
    for n in nurses:
        for d in days:
            for s in shifts:
                x[(n, d, s)] = model.new_bool_var(f"x_{n}_{d}_{s}")

    # ... (constraints as in previous chapters) ...

    return model, {"x": x, "nurses": request.nurses, "shifts": shift_types, "days": days}
```

## Timeout Handling

The solver must respect time limits strictly:

```python
import signal
import threading

class SolverTimeout(Exception):
    pass

def solve_with_hard_timeout(model, max_seconds):
    """Solve with a hard timeout (kills the process if needed)."""
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_seconds

    # CP-SAT respects max_time_in_seconds, but add a safety margin
    result = {"status": None, "solver": solver}

    def solve_thread():
        result["status"] = solver.solve(model)

    thread = threading.Thread(target=solve_thread)
    thread.start()
    thread.join(timeout=max_seconds + 5)  # 5s grace period

    if thread.is_alive():
        # Solver didn't stop in time — this shouldn't happen with CP-SAT
        # but handle it gracefully
        return None, "Solver exceeded hard timeout"

    return result["status"], result["solver"]
```

## Monitoring & Observability

```python
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("scheduler")

@dataclass
class SolveMetrics:
    request_id: str
    num_nurses: int
    num_days: int
    num_variables: int
    num_constraints: int
    solve_time_seconds: float
    status: str
    objective_value: float | None
    gap: float | None
    timestamp: datetime

def log_solve(request, model, solver, status, elapsed):
    """Log solve metrics for monitoring."""
    metrics = SolveMetrics(
        request_id=str(uuid.uuid4()),
        num_nurses=len(request.nurses),
        num_days=request.num_days,
        num_variables=model.proto.variables.__len__(),
        num_constraints=model.proto.constraints.__len__(),
        solve_time_seconds=elapsed,
        status=solver.status_name(status),
        objective_value=solver.objective_value if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
        gap=None,  # Compute if needed
        timestamp=datetime.now(),
    )

    logger.info(f"Solve completed: {metrics}")

    # Alert if solve time exceeds SLA
    if elapsed > 30:
        logger.warning(f"Solve exceeded 30s SLA: {elapsed:.1f}s for {metrics.num_nurses} nurses")

    # Alert if infeasible (might indicate data issue)
    if status == cp_model.INFEASIBLE:
        logger.error(f"Infeasible model: {metrics.num_nurses} nurses, {metrics.num_days} days")

    return metrics
```

## Response Format

```python
def extract_schedule(solver, variables, request):
    """Convert solver output to a clean API response."""
    x = variables["x"]
    nurses = variables["nurses"]
    shift_types = variables["shifts"]
    days = variables["days"]

    schedule = []
    for d in days:
        day_schedule = {"day": d, "shifts": {}}
        for s_idx, shift_type in enumerate(shift_types):
            assigned = []
            for n_idx, nurse in enumerate(nurses):
                if solver.value(x[(n_idx, d, s_idx)]):
                    assigned.append({
                        "nurse_id": nurse.nurse_id,
                        "shift": shift_type.value,
                        "day": d,
                    })
            day_schedule["shifts"][shift_type.value] = assigned
        schedule.append(day_schedule)

    return schedule
```

## Testing the Solver

```python
import pytest

def test_basic_schedule():
    """Verify a simple schedule is feasible."""
    request = ScheduleRequest(
        nurses=[NurseAvailability(nurse_id=f"nurse_{i}") for i in range(12)],
        num_days=7,
        shifts_per_day={ShiftType.MORNING: 3, ShiftType.AFTERNOON: 3, ShiftType.NIGHT: 2},
    )
    result = run_solver(request)
    assert result["status"] in ("optimal", "feasible")
    assert result["schedule"] is not None

def test_infeasible_detected():
    """Verify infeasibility is caught."""
    request = ScheduleRequest(
        nurses=[NurseAvailability(nurse_id=f"nurse_{i}") for i in range(3)],
        num_days=7,
        shifts_per_day={ShiftType.MORNING: 3, ShiftType.AFTERNOON: 3, ShiftType.NIGHT: 2},
    )
    result = run_solver(request)
    assert result["status"] == "infeasible"

def test_respects_unavailability():
    """Verify nurses aren't scheduled on unavailable days."""
    nurses = [NurseAvailability(nurse_id=f"nurse_{i}") for i in range(12)]
    nurses[0].unavailable_days = [0, 1, 2, 3, 4, 5, 6]  # Unavailable all week

    request = ScheduleRequest(
        nurses=nurses,
        num_days=7,
        shifts_per_day={ShiftType.MORNING: 3, ShiftType.AFTERNOON: 3, ShiftType.NIGHT: 2},
    )
    result = run_solver(request)

    if result["status"] in ("optimal", "feasible"):
        # Nurse 0 should not appear in any shift
        for day in result["schedule"]:
            for shift_name, assignments in day["shifts"].items():
                for assignment in assignments:
                    assert assignment["nurse_id"] != "nurse_0"

def test_timeout_respected():
    """Verify solver respects time limit."""
    request = ScheduleRequest(
        nurses=[NurseAvailability(nurse_id=f"nurse_{i}") for i in range(200)],
        num_days=28,
        shifts_per_day={ShiftType.MORNING: 20, ShiftType.AFTERNOON: 20, ShiftType.NIGHT: 10},
        time_limit_seconds=5.0,
    )
    start = time.time()
    result = run_solver(request)
    elapsed = time.time() - start

    assert elapsed < 10  # Should finish within 2x the limit
```

## Deployment Checklist

1. ✅ **Input validation** — reject garbage before it hits the solver
2. ✅ **Pre-check** — catch arithmetic infeasibility instantly
3. ✅ **Time limits** — never let the solver run forever
4. ✅ **Graceful degradation** — return partial results on timeout
5. ✅ **Error messages** — tell users *why* it failed and *what to do*
6. ✅ **Monitoring** — track solve times, success rates, infeasibility rates
7. ✅ **Testing** — unit tests for feasibility, infeasibility, and edge cases
8. ✅ **Async for large problems** — don't block the API on 60-second solves
9. ✅ **Resource limits** — cap memory and CPU per solve
10. ✅ **Versioning** — track which model version produced each schedule

## The Journey Complete

You started with a crashed spreadsheet and ended with a production scheduling engine that:

- Handles 200+ nurses across 4-week horizons
- Respects safety constraints (no dangerous shift patterns)
- Balances fairness across multiple dimensions
- Solves job-shop scheduling for manufacturing
- Optimizes delivery routes with time windows
- Re-optimizes incrementally when things change
- Runs as a reliable API with proper error handling

The spreadsheet is dead. Long live the solver.

---

## Where to Go Next

| Topic | Resource |
|---|---|
| OR-Tools documentation | [developers.google.com/optimization](https://developers.google.com/optimization) |
| CP-SAT primer | [github.com/google/or-tools/blob/main/ortools/sat/docs](https://github.com/google/or-tools) |
| Scheduling research | "Handbook of Constraint Programming" (Rossi et al.) |
| VRP variants | "The Vehicle Routing Problem" (Toth & Vigo) |
| MIP modeling | "Model Building in Mathematical Programming" (Williams) |
| Community | [groups.google.com/g/or-tools-discuss](https://groups.google.com/g/or-tools-discuss) |

---

[← Chapter 11: Incremental Solving](chapter-11-incremental.md)
