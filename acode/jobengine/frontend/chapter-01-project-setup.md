# Chapter 1: First Component — Project Setup

[← Chapter 0: Setting Up](chapter-00-setup.md) | [Chapter 2: Making It Pretty →](chapter-02-tailwind.md)

---

## The Problem

You have Node. You have VS Code. You have zero frontend code. Captain Deadline wants to see *something* on that TV by end of day.

## Scaffold the Project

One command:

```bash
npm create vite@latest dashboard -- --template react-ts
cd dashboard
npm install
```

This gives you:

```
dashboard/
├── src/
│   ├── App.tsx          ← your app starts here
│   ├── main.tsx         ← entry point (mounts React to the DOM)
│   └── vite-env.d.ts    ← TypeScript types for Vite
├── index.html           ← the single HTML page
├── package.json
├── tsconfig.json
└── vite.config.ts
```

Start the dev server:

```bash
npm run dev
# → Local: http://localhost:5173/
```

Open it. You see the Vite + React logo. It works. Delete everything in `src/` except `main.tsx` and `vite-env.d.ts`. We're starting from scratch.

## Your First Component

A React component is a function that returns HTML (well, JSX). That's it.

```tsx
// src/App.tsx
export default function App() {
  return (
    <div>
      <h1>ShopZilla Job Engine</h1>
      <p>Dashboard coming soon...</p>
    </div>
  );
}
```

Wire it up:

```tsx
// src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

Save. The browser updates instantly — that's Vite's Hot Module Replacement (HMR). No refresh needed.

## TypeScript: Catch Bugs Before Runtime

Why TypeScript? Because this:

```tsx
// JavaScript — bug hides until runtime
function JobCard({ job }) {
  return <p>{job.stauts}</p>; // typo: "stauts" instead of "status"
}
```

vs this:

```tsx
// TypeScript — bug caught immediately
interface Job {
  id: string;
  type: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  result?: string;
  errorMessage?: string;
}

function JobCard({ job }: { job: Job }) {
  return <p>{job.stauts}</p>;
  //              ^^^^^^ Property 'stauts' does not exist on type 'Job'
}
```

Red squiggly line. Before you save. Before you deploy. Before Karen reports it.

Create the types file:

```tsx
// src/types.ts
export interface Job {
  id: string;
  type: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED" | "DEAD";
  priority: number;
  result?: string;
  errorMessage?: string;
  retryCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface Stats {
  pending: number;
  running: number;
  completed: number;
  failed: number;
  dead: number;
  active: number;
}
```

## Props: Passing Data to Components

Components are functions. Props are their arguments.

```tsx
// src/components/JobCard.tsx
import type { Job } from "../types";

export function JobCard({ job }: { job: Job }) {
  return (
    <div>
      <span>{job.type}</span>
      <span>{job.status}</span>
      <span>{job.id.slice(0, 8)}</span>
    </div>
  );
}
```

Use it:

```tsx
// src/App.tsx
import { JobCard } from "./components/JobCard";
import type { Job } from "./types";

const mockJob: Job = {
  id: "abc-12345-def",
  type: "CSV_IMPORT",
  status: "COMPLETED",
  priority: 2,
  result: "500 rows imported",
  retryCount: 0,
  createdAt: "2026-05-04T10:00:00Z",
  updatedAt: "2026-05-04T10:00:05Z",
};

export default function App() {
  return (
    <div>
      <h1>ShopZilla Job Engine</h1>
      <JobCard job={mockJob} />
    </div>
  );
}
```

## Lists: Rendering Multiple Jobs

```tsx
// src/components/JobList.tsx
import type { Job } from "../types";
import { JobCard } from "./JobCard";

export function JobList({ jobs }: { jobs: Job[] }) {
  if (jobs.length === 0) {
    return <p>No jobs found.</p>;
  }

  return (
    <div>
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
}
```

The `key` prop tells React which items changed when the list updates. Without it, React re-renders everything. With it, React only updates the changed items.

## ESLint + Prettier Setup

```bash
npm install -D eslint @eslint/js typescript-eslint eslint-plugin-react-hooks
npm install -D prettier eslint-config-prettier
```

```js
// eslint.config.js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    plugins: { "react-hooks": reactHooks },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "@typescript-eslint/no-unused-vars": "error",
    },
  }
);
```

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": false,
  "trailingComma": "all",
  "tabWidth": 2
}
```

```bash
npx eslint src/
# → no errors (if you wrote clean code)
```

## Verify

```bash
npm run dev
```

You see "ShopZilla Job Engine" and a job card with mock data. It's ugly. It's unstyled. But it works.

Captain Deadline walks by. "Where are the colors?"

That's Chapter 2.

---

[← Chapter 0: Setting Up](chapter-00-setup.md) | [Chapter 2: Making It Pretty →](chapter-02-tailwind.md)
