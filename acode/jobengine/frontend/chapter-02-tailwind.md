# Chapter 2: Making It Pretty — Tailwind CSS

[← Chapter 1: First Component](chapter-01-project-setup.md) | [Chapter 3: Talking to the Backend →](chapter-03-data-fetching.md)

---

## The Problem

Your dashboard looks like a 1997 Geocities page. No colors, no layout, no spacing. Captain Deadline won't put this on the TV. Old Greg says "just use CSS." You open a CSS file. You close it. There has to be a better way.

## Install Tailwind

```bash
npm install tailwindcss @tailwindcss/vite
```

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

```css
/* src/index.css */
@import "tailwindcss";
```

```tsx
// src/main.tsx — add the import
import "./index.css";
```

That's it. No `tailwind.config.js` needed with Tailwind v4. Classes just work.

## How Tailwind Works

Instead of writing CSS in a separate file, you put utility classes directly on elements:

```tsx
// ❌ Traditional CSS
<div className="job-card">  // then go write .job-card { ... } somewhere

// ✅ Tailwind
<div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
```

Every class does one thing: `bg-gray-800` = dark background, `rounded-lg` = rounded corners, `p-4` = padding. You compose them like Lego.

## Dark Mode Dashboard

The TV in the office is in a dark room. Dark mode it is.

```tsx
// src/App.tsx
import { JobList } from "./components/JobList";
import { mockJobs } from "./mock-data";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-xl font-mono font-bold text-white">
          ShopZilla Job Engine
        </h1>
        <p className="text-sm text-gray-500">Dashboard</p>
      </header>
      <main className="p-6">
        <JobList jobs={mockJobs} />
      </main>
    </div>
  );
}
```

## Status Badges

Jobs need color-coded status badges. Green for done, red for failed, yellow for running.

```tsx
// src/components/StatusBadge.tsx
import type { Job } from "../types";

const statusStyles: Record<Job["status"], string> = {
  PENDING: "bg-gray-700 text-gray-300",
  RUNNING: "bg-blue-900 text-blue-300 animate-pulse",
  COMPLETED: "bg-green-900 text-green-300",
  FAILED: "bg-red-900 text-red-300",
  CANCELLED: "bg-yellow-900 text-yellow-300",
  DEAD: "bg-red-950 text-red-400 border border-red-800",
};

export function StatusBadge({ status }: { status: Job["status"] }) {
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-mono ${statusStyles[status]}`}>
      {status}
    </span>
  );
}
```

`animate-pulse` makes RUNNING badges glow. Captain Deadline will love it.

## The Job Card

```tsx
// src/components/JobCard.tsx
import type { Job } from "../types";
import { StatusBadge } from "./StatusBadge";

export function JobCard({ job }: { job: Job }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4
                    hover:border-gray-600 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="font-mono text-sm text-blue-400">{job.type}</span>
        <StatusBadge status={job.status} />
      </div>
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>#{job.id.slice(0, 8)}</span>
        <span>{new Date(job.createdAt).toLocaleTimeString()}</span>
      </div>
      {job.result && (
        <p className="mt-2 text-xs text-gray-400 font-mono truncate">
          {job.result}
        </p>
      )}
      {job.errorMessage && (
        <p className="mt-2 text-xs text-red-400 font-mono truncate">
          ✗ {job.errorMessage}
        </p>
      )}
    </div>
  );
}
```

## The Job List (Grid Layout)

```tsx
// src/components/JobList.tsx
import type { Job } from "../types";
import { JobCard } from "./JobCard";

export function JobList({ jobs }: { jobs: Job[] }) {
  if (jobs.length === 0) {
    return (
      <p className="text-gray-500 text-center py-12">No jobs found.</p>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
}
```

`grid-cols-1 md:grid-cols-2 lg:grid-cols-3` — 1 column on mobile, 2 on tablet, 3 on desktop. Responsive with zero media queries.

## Stats Bar

```tsx
// src/components/StatsBar.tsx
import type { Stats } from "../types";

export function StatsBar({ stats }: { stats: Stats }) {
  const items = [
    { label: "Pending", value: stats.pending, color: "text-gray-400" },
    { label: "Running", value: stats.running, color: "text-blue-400" },
    { label: "Completed", value: stats.completed, color: "text-green-400" },
    { label: "Failed", value: stats.failed, color: "text-red-400" },
    { label: "Dead", value: stats.dead, color: "text-red-500" },
  ];

  return (
    <div className="flex gap-6 mb-6">
      {items.map((item) => (
        <div key={item.label} className="text-center">
          <div className={`text-2xl font-bold font-mono ${item.color}`}>
            {item.value}
          </div>
          <div className="text-xs text-gray-500">{item.label}</div>
        </div>
      ))}
    </div>
  );
}
```

## Mock Data

```tsx
// src/mock-data.ts
import type { Job, Stats } from "./types";

export const mockStats: Stats = {
  pending: 12, running: 5, completed: 1423, failed: 3, dead: 1, active: 5,
};

export const mockJobs: Job[] = [
  { id: "a1b2c3d4", type: "CSV_IMPORT", status: "COMPLETED", priority: 2,
    result: "500 rows imported", retryCount: 0,
    createdAt: "2026-05-04T10:00:00Z", updatedAt: "2026-05-04T10:00:05Z" },
  { id: "e5f6g7h8", type: "IMAGE_RESIZE", status: "RUNNING", priority: 2,
    retryCount: 0,
    createdAt: "2026-05-04T10:01:00Z", updatedAt: "2026-05-04T10:01:00Z" },
  { id: "i9j0k1l2", type: "PRICE_CALCULATION", status: "FAILED", priority: 1,
    errorMessage: "ConnectException: Connection refused", retryCount: 3,
    createdAt: "2026-05-04T09:00:00Z", updatedAt: "2026-05-04T09:05:00Z" },
  { id: "m3n4o5p6", type: "EMAIL_DISPATCH", status: "DEAD", priority: 2,
    errorMessage: "Exhausted 5 retries", retryCount: 5,
    createdAt: "2026-05-04T08:00:00Z", updatedAt: "2026-05-04T08:30:00Z" },
];
```

## Put It Together

```tsx
// src/App.tsx
import { JobList } from "./components/JobList";
import { StatsBar } from "./components/StatsBar";
import { mockJobs, mockStats } from "./mock-data";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-xl font-mono font-bold">ShopZilla Job Engine</h1>
      </header>
      <main className="p-6 max-w-7xl mx-auto">
        <StatsBar stats={mockStats} />
        <JobList jobs={mockJobs} />
      </main>
    </div>
  );
}
```

Save. Look at the browser. Dark background. Color-coded badges. RUNNING pulses blue. DEAD has a red border. The grid is responsive.

Captain Deadline walks by. Pauses. "Put it on the TV."

It's still mock data. But it looks real. That's Chapter 3 — connecting to the actual backend.

---

[← Chapter 1: First Component](chapter-01-project-setup.md) | [Chapter 3: Talking to the Backend →](chapter-03-data-fetching.md)
