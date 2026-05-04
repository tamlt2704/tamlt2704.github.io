# Chapter 4: Real-time Updates — SSE & Live UI

[← Chapter 3: Talking to the Backend](chapter-03-data-fetching.md) | [Chapter 5: Clean Architecture →](chapter-05-architecture.md)

---

## The Problem

Captain Deadline submits a job. Stares at the TV. Five seconds pass. The job appears. "Why is there a delay? I want to see it *instantly*."

You're polling every 5 seconds. That means up to 5 seconds of stale data. For a "war room screen," that's unacceptable.

The backend already has an SSE endpoint (Chapter 7 of the backend series). Time to consume it.

## `EventSource`: The Browser's SSE Client

SSE (Server-Sent Events) is built into every browser. No library needed.

```tsx
// src/hooks/useJobStream.ts
import { useEffect, useRef } from "react";
import type { Job } from "../types";

interface JobEvent {
  jobId: string;
  status: Job["status"];
  result?: string;
  progress?: number;
  timestamp: string;
}

export function useJobStream(onEvent: (event: JobEvent) => void) {
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    const es = new EventSource("/api/jobs/stream");
    eventSourceRef.current = es;

    es.addEventListener("job-update", (e) => {
      const event: JobEvent = JSON.parse(e.data);
      onEvent(event);
    });

    es.onerror = () => {
      es.close();
      // Reconnect after 3 seconds
      setTimeout(() => {
        eventSourceRef.current = new EventSource("/api/jobs/stream");
      }, 3000);
    };

    return () => es.close();
  }, [onEvent]);
}
```

The browser keeps the connection open. The server pushes events as they happen. If the connection drops, we reconnect after 3 seconds.

## Merging SSE Events into State

The initial load comes from `fetch`. Updates come from SSE. You need to merge them:

```tsx
// src/hooks/useJobs.ts — updated
import { useState, useEffect, useCallback } from "react";
import type { Job } from "../types";
import { useJobStream } from "./useJobStream";

export function useJobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initial fetch
  useEffect(() => {
    async function fetchJobs() {
      try {
        const res = await fetch("/api/jobs");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        setJobs(await res.json());
        setError(null);
      } catch (e) {
        setError((e as Error).message);
      } finally {
        setLoading(false);
      }
    }
    fetchJobs();
  }, []);

  // Live updates via SSE
  const handleEvent = useCallback((event: { jobId: string; status: string; result?: string }) => {
    setJobs((prev) => {
      const idx = prev.findIndex((j) => j.id === event.jobId);
      if (idx === -1) {
        // New job — fetch it fully
        fetch(`/api/jobs/${event.jobId}`)
          .then((r) => r.json())
          .then((job) => setJobs((p) => [job, ...p]));
        return prev;
      }
      // Update existing job
      const updated = [...prev];
      updated[idx] = { ...updated[idx], status: event.status as Job["status"], result: event.result };
      return updated;
    });
  }, []);

  useJobStream(handleEvent);

  return { jobs, loading, error };
}
```

Pattern: fetch once on mount, then apply SSE patches. The list stays in sync without polling.

## Live Status Transitions

When a job transitions from RUNNING to COMPLETED, the badge should update instantly. With the SSE hook above, it does. But let's add a visual flourish — a brief highlight when a job updates:

```tsx
// src/components/JobCard.tsx — add highlight on update
import { useState, useEffect } from "react";
import type { Job } from "../types";
import { StatusBadge } from "./StatusBadge";

export function JobCard({ job }: { job: Job }) {
  const [highlight, setHighlight] = useState(false);

  useEffect(() => {
    setHighlight(true);
    const timer = setTimeout(() => setHighlight(false), 1000);
    return () => clearTimeout(timer);
  }, [job.status]); // re-run when status changes

  return (
    <div className={`bg-gray-900 border rounded-lg p-4 transition-all duration-300
      ${highlight ? "border-blue-500 ring-1 ring-blue-500/30" : "border-gray-800"}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-sm text-blue-400">{job.type}</span>
        <StatusBadge status={job.status} />
      </div>
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>#{job.id.slice(0, 8)}</span>
        <span>{new Date(job.createdAt).toLocaleTimeString()}</span>
      </div>
      {job.result && (
        <p className="mt-2 text-xs text-gray-400 font-mono truncate">{job.result}</p>
      )}
    </div>
  );
}
```

When a job's status changes, the card gets a blue ring for 1 second. On the 65-inch TV, you can see jobs completing in real time — blue pulses rippling across the grid.

## Progress Bar

For long-running jobs like CSV_IMPORT, show a progress bar:

```tsx
// src/components/ProgressBar.tsx
export function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="w-full bg-gray-800 rounded-full h-1.5 mt-2">
      <div
        className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
        style={{ width: `${Math.min(progress, 100)}%` }}
      />
    </div>
  );
}
```

Wire it into `JobCard`:

```tsx
{job.status === "RUNNING" && job.progress !== undefined && (
  <ProgressBar progress={job.progress} />
)}
```

## Verify

1. Open the dashboard
2. In another terminal: `curl -X POST http://localhost:8080/jobs -d '{"type":"CSV_IMPORT","payload":"{\"file\":\"big.csv\"}"}'`
3. Watch the dashboard — the job appears instantly, transitions through PENDING → RUNNING → COMPLETED, with a progress bar filling up

No refresh. No polling. No delay.

Captain Deadline watches a CSV import complete in real time on the TV. The progress bar fills. The badge turns green. He nods.

"Now I need to cancel jobs from the UI."

That's Chapter 6. But first, the code is getting messy — Chapter 5 cleans it up.

---

[← Chapter 3: Talking to the Backend](chapter-03-data-fetching.md) | [Chapter 5: Clean Architecture →](chapter-05-architecture.md)
