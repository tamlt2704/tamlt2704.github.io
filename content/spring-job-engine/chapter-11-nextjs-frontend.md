# Chapter 11: Next.js Frontend Dashboard

[← Chapter 10: Final](/blog/spring-job-engine/chapter-10-final) | [Overview](/blog/spring-job-engine/chapter-00-overview)

---

## The Story

The backend is solid. But users don't curl APIs — they need a dashboard. You'll build a Next.js frontend with best practices: server components, optimistic updates, responsive mobile-first design with Tailwind CSS, and real-time WebSocket updates.

## Best Practices Applied

| Practice          | Implementation                                        |
| ----------------- | ----------------------------------------------------- |
| Server Components | Layout, static parts rendered on server               |
| Client Components | Only interactive parts (`"use client"`)               |
| SWR               | Data fetching with cache, revalidation, optimistic UI |
| Suspense          | Loading states without layout shift                   |
| Mobile-first      | Tailwind responsive (`sm:`, `md:`, `lg:`)             |
| Token storage     | httpOnly cookie (not localStorage)                    |
| Code splitting    | Dynamic imports for heavy components                  |
| Debounce          | Prevent rapid API calls                               |

## Project Structure

```
app/
├── layout.tsx              ← Server Component (shell)
├── page.tsx                ← Redirect to /dashboard
├── login/page.tsx          ← Client Component
├── dashboard/
│   ├── layout.tsx          ← Auth guard (Server)
│   ├── page.tsx            ← Job list (Client)
│   └── components/
│       ├── JobList.tsx
│       ├── JobCard.tsx
│       ├── SubmitForm.tsx
│       └── ProgressBar.tsx
└── lib/
    ├── api.ts              ← Fetch wrapper
    ├── hooks.ts            ← useSWR hooks
    └── ws.ts               ← WebSocket client
```

## Step 1: API Client with Error Handling

```typescript
// lib/api.ts
const API = process.env.NEXT_PUBLIC_API_URL!;

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = document.cookie.match(/token=([^;]+)/)?.[1];
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json();
}

export const api = {
  login: (email: string, password: string) =>
    request<{ token: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  getJobs: () => request<Job[]>("/api/jobs"),
  submitJob: (data: SubmitJobRequest) =>
    request<Job>("/api/jobs", { method: "POST", body: JSON.stringify(data) }),
  pauseJob: (id: string) => request<Job>(`/api/jobs/${id}/pause`, { method: "POST" }),
  resumeJob: (id: string) => request<Job>(`/api/jobs/${id}/resume`, { method: "POST" }),
  cancelJob: (id: string) => request<Job>(`/api/jobs/${id}/cancel`, { method: "POST" }),
};
```

## Step 2: SWR Hooks (Cache + Revalidation)

```typescript
// lib/hooks.ts
import useSWR from "swr";
import { api } from "./api";

export function useJobs() {
  const { data, error, mutate } = useSWR("jobs", api.getJobs, {
    refreshInterval: 3000, // poll every 3s as fallback
    revalidateOnFocus: true, // refresh when tab regains focus
    dedupingInterval: 1000, // dedupe rapid calls
  });

  return {
    jobs: data ?? [],
    isLoading: !data && !error,
    error,
    mutate,
  };
}
```

SWR gives you:

- **Stale-while-revalidate** — show cached data instantly, update in background
- **Optimistic UI** — update local state before server confirms
- **Deduplication** — multiple components using `useJobs()` share one request
- **Focus revalidation** — data refreshes when user returns to tab

## Step 3: Responsive Dashboard Layout

```tsx
// app/dashboard/page.tsx
"use client";

import { useJobs } from "@/lib/hooks";
import { SubmitForm } from "./components/SubmitForm";
import { JobCard } from "./components/JobCard";

export default function DashboardPage() {
  const { jobs, isLoading, mutate } = useJobs();

  const active = jobs.filter((j) => !j.status.match(/COMPLETED|FAILED|CANCELLED/));
  const done = jobs.filter((j) => j.status === "COMPLETED").slice(0, 10);

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Submit — full width on mobile, constrained on desktop */}
      <SubmitForm onSubmit={() => mutate()} />

      {/* Stats bar — responsive grid */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Active" value={active.length} color="blue" />
        <StatCard
          label="Queued"
          value={jobs.filter((j) => j.status === "QUEUED").length}
          color="yellow"
        />
        <StatCard label="Completed" value={done.length} color="green" />
        <StatCard
          label="Failed"
          value={jobs.filter((j) => j.status === "FAILED").length}
          color="red"
        />
      </div>

      {/* Active jobs — stack on mobile, grid on desktop */}
      <section className="mt-6">
        <h2 className="text-lg font-semibold">Active Jobs</h2>
        {isLoading ? (
          <div className="mt-4 space-y-3">
            {[...Array(3)].map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : (
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {active.map((job) => (
              <JobCard key={job.id} job={job} onAction={() => mutate()} />
            ))}
          </div>
        )}
      </section>

      {/* Completed — simple list */}
      <section className="mt-8">
        <h2 className="text-lg font-semibold">Recent Completed</h2>
        <div className="mt-3 divide-y rounded-lg border">
          {done.map((job) => (
            <div key={job.id} className="flex items-center gap-3 px-4 py-3 text-sm">
              <span className="text-green-500">✅</span>
              <span className="font-mono text-xs">{job.id}</span>
              <span className="hidden sm:inline">{job.type}</span>
              <span className="ml-auto text-xs text-gray-400">
                {new Date(job.completedAt).toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const colors: Record<string, string> = {
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    yellow: "bg-yellow-50 text-yellow-700 border-yellow-200",
    green: "bg-green-50 text-green-700 border-green-200",
    red: "bg-red-50 text-red-700 border-red-200",
  };
  return (
    <div className={`rounded-lg border p-3 text-center ${colors[color]}`}>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-xs">{label}</div>
    </div>
  );
}

function SkeletonCard() {
  return <div className="h-24 animate-pulse rounded-lg bg-gray-100" />;
}
```

## Step 4: Job Card with Optimistic Updates

```tsx
// components/JobCard.tsx
"use client";

import { api } from "@/lib/api";
import { useState, useTransition } from "react";

interface Props {
  job: Job;
  onAction: () => void;
}

export function JobCard({ job, onAction }: Props) {
  const [isPending, startTransition] = useTransition();
  const [optimisticStatus, setOptimisticStatus] = useState(job.status);

  const handleAction = (action: "pause" | "resume" | "cancel") => {
    // Optimistic update — show new state immediately
    const nextStatus = { pause: "PAUSED", resume: "RUNNING", cancel: "CANCELLED" }[action];
    setOptimisticStatus(nextStatus);

    startTransition(async () => {
      try {
        await api[`${action}Job`](job.id);
        onAction(); // revalidate
      } catch {
        setOptimisticStatus(job.status); // rollback
      }
    });
  };

  const status = optimisticStatus;
  const statusColors: Record<string, string> = {
    QUEUED: "bg-gray-100 text-gray-600",
    RUNNING: "bg-blue-100 text-blue-700",
    PAUSED: "bg-yellow-100 text-yellow-700",
    FAILED: "bg-red-100 text-red-700",
  };

  return (
    <div className={`rounded-xl border p-4 transition-all ${isPending ? "opacity-60" : ""}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-gray-500">{job.id}</span>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[status] ?? ""}`}
        >
          {status}
        </span>
      </div>

      {/* Body */}
      <div className="mt-2">
        <p className="font-medium">{job.type.replace(/_/g, " ")}</p>
        <p className="text-xs text-gray-400">
          Priority:{" "}
          <span className={job.priority === "CRITICAL" ? "font-bold text-red-500" : ""}>
            {job.priority}
          </span>
        </p>
      </div>

      {/* Progress bar — only when running */}
      {status === "RUNNING" && (
        <div className="mt-3">
          <div className="mb-1 flex justify-between text-xs text-gray-500">
            <span>Progress</span>
            <span>{job.progress}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-gray-200">
            <div
              className="h-2 rounded-full bg-blue-500 transition-all duration-500"
              style={{ width: `${job.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Actions — responsive buttons */}
      <div className="mt-3 flex gap-2">
        {status === "RUNNING" && (
          <button
            onClick={() => handleAction("pause")}
            className="flex-1 rounded-lg bg-yellow-50 px-3 py-1.5 text-xs font-medium text-yellow-700 hover:bg-yellow-100 active:scale-95"
          >
            ⏸ Pause
          </button>
        )}
        {status === "PAUSED" && (
          <button
            onClick={() => handleAction("resume")}
            className="flex-1 rounded-lg bg-green-50 px-3 py-1.5 text-xs font-medium text-green-700 hover:bg-green-100 active:scale-95"
          >
            ▶ Resume
          </button>
        )}
        {!["COMPLETED", "FAILED", "CANCELLED"].includes(status) && (
          <button
            onClick={() => handleAction("cancel")}
            className="rounded-lg bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 active:scale-95"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
```

## Step 5: Submit Form (Mobile-Friendly)

```tsx
// components/SubmitForm.tsx
"use client";

import { api } from "@/lib/api";
import { useState, useTransition } from "react";

export function SubmitForm({ onSubmit }: { onSubmit: () => void }) {
  const [type, setType] = useState("RISK_REPORT");
  const [priority, setPriority] = useState("MEDIUM");
  const [isPending, startTransition] = useTransition();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    startTransition(async () => {
      await api.submitJob({ type, priority, params: "{}" });
      onSubmit();
    });
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border bg-white p-4 shadow-sm">
      <h2 className="mb-3 font-semibold">Submit Job</h2>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label className="text-xs text-gray-500">Type</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="mt-1 w-full rounded-lg border px-3 py-2 text-sm"
          >
            <option>RISK_REPORT</option>
            <option>DATA_EXPORT</option>
            <option>COMPLIANCE</option>
          </select>
        </div>
        <div className="flex-1">
          <label className="text-xs text-gray-500">Priority</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="mt-1 w-full rounded-lg border px-3 py-2 text-sm"
          >
            <option>LOW</option>
            <option>MEDIUM</option>
            <option>HIGH</option>
            <option>CRITICAL</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={isPending}
          className="w-full rounded-lg bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 active:scale-95 disabled:opacity-50 sm:w-auto"
        >
          {isPending ? "Submitting..." : "Submit Job"}
        </button>
      </div>
    </form>
  );
}
```

## Step 6: WebSocket for Real-Time Updates

```typescript
// lib/ws.ts
import { Client } from "@stomp/stompjs";
import SockJS from "sockjs-client";

let client: Client | null = null;

export function connectWS(onJobUpdate: (job: Job) => void) {
  if (client?.active) return;

  client = new Client({
    webSocketFactory: () => new SockJS(process.env.NEXT_PUBLIC_WS_URL!),
    reconnectDelay: 5000,
    onConnect: () => {
      client!.subscribe("/topic/jobs", (msg) => {
        onJobUpdate(JSON.parse(msg.body));
      });
    },
  });
  client.activate();
}

export function disconnectWS() {
  client?.deactivate();
  client = null;
}
```

Integrate with SWR for seamless updates:

```typescript
// In dashboard page
useEffect(() => {
  connectWS((updatedJob) => {
    // Merge WebSocket update into SWR cache
    mutate(
      (jobs) => jobs?.map((j) => (j.id === updatedJob.id ? updatedJob : j)),
      { revalidate: false }, // don't refetch, trust the WS data
    );
  });
  return () => disconnectWS();
}, [mutate]);
```

## Step 7: Performance Optimizations

```tsx
// 1. Dynamic import for heavy components (code splitting)
const AuditLog = dynamic(() => import("./components/AuditLog"), {
  loading: () => <SkeletonCard />,
});

// 2. Memoize expensive renders
const MemoizedJobCard = memo(
  JobCard,
  (prev, next) =>
    prev.job.id === next.job.id &&
    prev.job.status === next.job.status &&
    prev.job.progress === next.job.progress,
);

// 3. Virtual list for large job lists (if 1000+ jobs)
// npm install @tanstack/react-virtual
import { useVirtualizer } from "@tanstack/react-virtual";
```

## Responsive Breakpoints

```
Mobile (< 640px):
  - Single column layout
  - Full-width cards stacked
  - Submit form fields stacked vertically
  - Larger touch targets (py-2, active:scale-95)

Tablet (640px - 1024px):
  - 2-column job grid
  - Submit form inline

Desktop (> 1024px):
  - 3-column job grid
  - Stats bar 4-column
  - More info visible (timestamps, types)
```

## Tailwind Patterns Used

| Pattern          | Example                                     | Purpose                               |
| ---------------- | ------------------------------------------- | ------------------------------------- |
| Mobile-first     | `w-full sm:w-auto`                          | Full width on mobile, auto on desktop |
| Responsive grid  | `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3` | Adapt columns                         |
| Touch feedback   | `active:scale-95`                           | Tactile button press                  |
| Loading state    | `animate-pulse`                             | Skeleton screens                      |
| Optimistic       | `opacity-60` during transition              | Visual pending state                  |
| Hidden on mobile | `hidden sm:inline`                          | Show extra info on larger screens     |

---

## Gradle Commands

```bash
./gradlew bootRun              # Run backend
./gradlew build                # Compile + test
./gradlew bootJar              # Fat JAR for deployment
```

## The Full Stack

```
Mobile/Desktop Browser
        │
        ▼
┌─── Next.js (SSR + Client) ──────────────────────┐
│  Server Components: layout, auth guard           │
│  Client Components: dashboard, forms, cards      │
│  SWR: cache + revalidation + optimistic UI       │
│  WebSocket: real-time progress updates           │
│  Tailwind: responsive, mobile-first              │
└──────────────────────────────────────────────────┘
        │ REST + WebSocket
        ▼
┌─── Spring Boot (Gradle) ─────────────────────────┐
│  JWT Auth │ Spring Integration │ Thread Pool      │
│  Redis    │ Kafka              │ PostgreSQL       │
└──────────────────────────────────────────────────┘
```

[← Overview](/blog/spring-job-engine/chapter-00-overview)
