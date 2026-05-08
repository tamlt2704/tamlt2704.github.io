"""
Job Scheduler — Core Implementation
=====================================
Demonstrates: Priority queue with delayed execution, exactly-once
semantics (claim with lease), dead letter queue, retry with
exponential backoff, cron expression parser.

In a real system:
- Job queue: Redis sorted set (score = execution time) or SQS
- Exactly-once: Redis BRPOPLPUSH + lease timeout, or SQS visibility timeout
- Dead letter: separate queue for jobs that exceed max retries
- Cron: systemd timers, Kubernetes CronJobs, or Temporal workflows
- Persistence: PostgreSQL for job state, Redis for the hot queue
"""

import heapq
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


# ─── Job States ───────────────────────────────────────────────────────────────

class JobState(Enum):
    PENDING = "pending"
    CLAIMED = "claimed"       # Worker picked it up (lease active)
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DEAD = "dead"             # Moved to dead letter queue


@dataclass(order=True)
class Job:
    """A scheduled job with priority and execution time."""
    execute_at: float                          # When to run (Unix timestamp)
    priority: int = field(compare=True)        # Lower = higher priority
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8], compare=False)
    name: str = field(default="", compare=False)
    payload: dict = field(default_factory=dict, compare=False)
    state: JobState = field(default=JobState.PENDING, compare=False)
    attempts: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)
    lease_expires: float = field(default=0, compare=False)
    last_error: str = field(default="", compare=False)
    created_at: float = field(default_factory=time.time, compare=False)


# ─── Priority Queue with Delayed Execution ──────────────────────────────────

class JobQueue:
    """
    Min-heap priority queue. Jobs sorted by (execute_at, priority).
    Only dequeues jobs whose execute_at <= now.

    Production: Redis ZRANGEBYSCORE with score = execute_at.
    """

    def __init__(self):
        self.heap: list[Job] = []
        self.job_map: dict[str, Job] = {}  # For lookup by ID

    def enqueue(self, job: Job):
        heapq.heappush(self.heap, job)
        self.job_map[job.id] = job

    def dequeue_ready(self, now: float = None) -> Optional[Job]:
        """Get the highest-priority job that's ready to execute."""
        now = now or time.time()
        while self.heap:
            if self.heap[0].execute_at <= now and self.heap[0].state == JobState.PENDING:
                job = heapq.heappop(self.heap)
                return job
            elif self.heap[0].state != JobState.PENDING:
                heapq.heappop(self.heap)  # Remove completed/dead jobs
            else:
                break  # Next job isn't ready yet
        return None

    def size(self) -> int:
        return sum(1 for j in self.heap if j.state == JobState.PENDING)


# ─── Exactly-Once: Claim with Lease ─────────────────────────────────────────

class LeaseManager:
    """
    Prevents double-processing: worker claims a job with a time-limited lease.
    If worker crashes, lease expires and job becomes available again.

    Production: Redis SET with EX (expiry), or SQS visibility timeout.
    """

    def __init__(self, lease_duration: float = 30.0):
        self.lease_duration = lease_duration
        self.active_leases: dict[str, float] = {}  # job_id → expires_at

    def claim(self, job: Job) -> bool:
        """Attempt to claim a job. Returns False if already claimed."""
        now = time.time()
        # Check if lease is still active
        if job.id in self.active_leases:
            if self.active_leases[job.id] > now:
                return False  # Someone else has it
            # Lease expired — reclaim
        job.state = JobState.CLAIMED
        job.lease_expires = now + self.lease_duration
        self.active_leases[job.id] = job.lease_expires
        return True

    def release(self, job_id: str):
        """Release a lease (job completed or failed)."""
        self.active_leases.pop(job_id, None)

    def get_expired_leases(self) -> list[str]:
        """Find jobs with expired leases (worker probably crashed)."""
        now = time.time()
        expired = [jid for jid, exp in self.active_leases.items() if exp <= now]
        return expired


# ─── Dead Letter Queue ────────────────────────────────────────────────────────

class DeadLetterQueue:
    """
    Jobs that exceed max retries go here for manual inspection.
    Production: separate SQS queue, or PostgreSQL table with alerts.
    """

    def __init__(self):
        self.jobs: list[Job] = []

    def add(self, job: Job):
        job.state = JobState.DEAD
        self.jobs.append(job)

    def size(self) -> int:
        return len(self.jobs)


# ─── Retry with Exponential Backoff ──────────────────────────────────────────

def calculate_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """
    Exponential backoff: delay = base * 2^attempt (capped at max).
    In production, add jitter: delay * random(0.5, 1.5) to prevent thundering herd.
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    return delay


# ─── Cron Expression Parser (simplified) ─────────────────────────────────────

class CronSchedule:
    """
    Simplified cron parser supporting: minute, hour, day_of_month, month, day_of_week.
    Supports: *, specific values, ranges (1-5), steps (*/5).

    Full cron: "30 2 * * 1-5" = 2:30 AM on weekdays.
    """

    def __init__(self, expression: str):
        parts = expression.split()
        assert len(parts) == 5, "Cron needs 5 fields: min hour dom month dow"
        self.minute = self._parse_field(parts[0], 0, 59)
        self.hour = self._parse_field(parts[1], 0, 23)
        self.dom = self._parse_field(parts[2], 1, 31)
        self.month = self._parse_field(parts[3], 1, 12)
        self.dow = self._parse_field(parts[4], 0, 6)

    def _parse_field(self, field: str, min_val: int, max_val: int) -> set[int]:
        """Parse a single cron field into a set of valid values."""
        if field == "*":
            return set(range(min_val, max_val + 1))
        if "/" in field:
            base, step = field.split("/")
            start = min_val if base == "*" else int(base)
            return set(range(start, max_val + 1, int(step)))
        if "-" in field:
            start, end = field.split("-")
            return set(range(int(start), int(end) + 1))
        if "," in field:
            return {int(v) for v in field.split(",")}
        return {int(field)}

    def matches(self, t: time.struct_time) -> bool:
        """Check if a given time matches this cron schedule."""
        return (t.tm_min in self.minute and
                t.tm_hour in self.hour and
                t.tm_mday in self.dom and
                t.tm_mon in self.month and
                t.tm_wday in self.dow)

    def describe(self) -> str:
        """Human-readable description."""
        return f"min={sorted(self.minute)[:3]}... hour={sorted(self.hour)[:3]}..."


# ─── Job Scheduler (orchestrator) ────────────────────────────────────────────

class JobScheduler:
    """Ties together queue, leases, retries, and DLQ."""

    def __init__(self):
        self.queue = JobQueue()
        self.leases = LeaseManager(lease_duration=30.0)
        self.dlq = DeadLetterQueue()
        self.completed: list[Job] = []

    def submit(self, name: str, payload: dict = None, delay: float = 0,
               priority: int = 5, max_retries: int = 3) -> Job:
        """Submit a job for execution."""
        job = Job(
            execute_at=time.time() + delay,
            priority=priority,
            name=name,
            payload=payload or {},
            max_retries=max_retries,
        )
        self.queue.enqueue(job)
        return job

    def process_next(self, worker_fn: Callable[[Job], bool]) -> Optional[Job]:
        """Worker picks up next job, executes it, handles failure."""
        job = self.queue.dequeue_ready()
        if not job:
            return None

        if not self.leases.claim(job):
            return None  # Someone else got it

        job.state = JobState.RUNNING
        job.attempts += 1

        try:
            success = worker_fn(job)
            if success:
                job.state = JobState.SUCCEEDED
                self.completed.append(job)
            else:
                raise RuntimeError("Job returned failure")
        except Exception as e:
            job.last_error = str(e)
            if job.attempts >= job.max_retries:
                self.dlq.add(job)
            else:
                # Retry with backoff
                backoff = calculate_backoff(job.attempts)
                job.state = JobState.PENDING
                job.execute_at = time.time() + backoff
                self.queue.enqueue(job)
        finally:
            self.leases.release(job.id)

        return job


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Job Scheduler Demo ===\n")
    scheduler = JobScheduler()

    # --- Submit jobs with different priorities and delays ---
    print("--- Submitting Jobs ---")
    j1 = scheduler.submit("send_email", {"to": "user@example.com"}, priority=3)
    j2 = scheduler.submit("process_payment", {"amount": 99}, priority=1)  # High priority
    j3 = scheduler.submit("generate_report", delay=2.0, priority=5)  # Delayed
    j4 = scheduler.submit("resize_image", {"size": "thumb"}, priority=3)

    print(f"  Submitted 4 jobs (1 delayed by 2s)")
    print(f"  Queue size: {scheduler.queue.size()}")

    # --- Process jobs (simulated workers) ---
    print("\n--- Processing Jobs ---")
    def good_worker(job: Job) -> bool:
        print(f"  ✓ Executed: {job.name} (priority={job.priority}, attempt={job.attempts})")
        return True

    # Process available jobs (j3 is delayed, won't run yet)
    for _ in range(4):
        scheduler.process_next(good_worker)

    print(f"  Completed: {len(scheduler.completed)}")
    print(f"  Remaining in queue: {scheduler.queue.size()} (delayed job)")

    # --- Retry with exponential backoff ---
    print("\n--- Retry with Exponential Backoff ---")
    fail_count = 0
    def flaky_worker(job: Job) -> bool:
        global fail_count
        fail_count += 1
        if fail_count <= 2:
            raise RuntimeError(f"Transient error #{fail_count}")
        return True

    j5 = scheduler.submit("flaky_task", max_retries=3, priority=1)
    for i in range(4):
        result = scheduler.process_next(flaky_worker)
        if result:
            backoff = calculate_backoff(result.attempts) if result.state == JobState.PENDING else 0
            print(f"  Attempt {result.attempts}: {result.state.value}"
                  f"{f' (retry in {backoff:.1f}s)' if backoff else ''}")
            # Fast-forward time for demo
            if result.state == JobState.PENDING:
                result.execute_at = time.time()

    # --- Dead Letter Queue ---
    print("\n--- Dead Letter Queue ---")
    def always_fails(job: Job) -> bool:
        raise RuntimeError("Permanent failure")

    j6 = scheduler.submit("doomed_task", max_retries=2, priority=1)
    for _ in range(3):
        result = scheduler.process_next(always_fails)
        if result and result.state == JobState.PENDING:
            result.execute_at = time.time()  # Fast-forward

    print(f"  DLQ size: {scheduler.dlq.size()}")
    for job in scheduler.dlq.jobs:
        print(f"  ☠ {job.name}: {job.attempts} attempts, last error: {job.last_error}")

    # --- Exponential Backoff Values ---
    print("\n--- Backoff Schedule ---")
    for attempt in range(6):
        delay = calculate_backoff(attempt)
        print(f"  Attempt {attempt}: wait {delay:.1f}s")

    # --- Cron Parser ---
    print("\n--- Cron Expression Parser ---")
    schedules = [
        ("*/15 * * * *", "Every 15 minutes"),
        ("0 9 * * 1-5", "9 AM on weekdays"),
        ("30 2 1 * *", "2:30 AM on 1st of month"),
        ("0 */2 * * *", "Every 2 hours"),
    ]
    for expr, desc in schedules:
        cron = CronSchedule(expr)
        print(f"  '{expr}' → {desc}")
        print(f"    Minutes: {sorted(cron.minute)[:5]}{'...' if len(cron.minute) > 5 else ''}")
        print(f"    Hours: {sorted(cron.hour)[:5]}{'...' if len(cron.hour) > 5 else ''}")
