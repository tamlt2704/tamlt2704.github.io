# Chapter 3: Talking to the Backend — State & Data Fetching

[← Chapter 2: Making It Pretty](chapter-02-tailwind.md) | [Chapter 4: Real-time Updates →](chapter-04-real-time.md)

---

## The Problem

The dashboard looks great. With fake data. Captain Deadline submits a real job via curl and looks at the TV. Nothing changes. "It's lying to me."

Time to connect to the real backend.

## `useState`: Remembering Things

React components are functions. Functions don't remember anything between calls. `useState` gives them memory.

```tsx
const [jobs, setJobs] = useState<Job[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

Three pieces of state: the data, whether we're loading, and any error. This is the pattern for every API call you'll ever make.

## `useEffect`: Doing Things on Mount

`useEffect` runs code when the component mounts (appears on screen). Perfect for fetching data.

```tsx
// src/hooks/useJobs.ts
import { useState, useEffect } from "react";
import type { Job } from "../types";

const API = "http://localhost:8080";

export function useJobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchJobs() {
      try {
        const res = await fetch(`${API}/jobs`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: Job[] = await res.json();
        if (!cancelled) {
          setJobs(data);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) setError((e as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchJobs();
    return () => { cancelled = true; }; // cleanup on unmount
  }, []);

  return { jobs, loading, error };
}
```

The `cancelled` flag prevents setting state on an unmounted component — a common React bug that causes "Can't perform a React state update on an unmounted component" warnings.

## `useStats` Hook

Same pattern for stats:

```tsx
// src/hooks/useStats.ts
import { useState, useEffect } from "react";
import type { Stats } from "../types";

const API = "http://localhost:8080";

export function useStats() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    async function fetchStats() {
      const res = await fetch(`${API}/stats`);
      if (res.ok) setStats(await res.json());
    }
    fetchStats();
    const interval = setInterval(fetchStats, 5000); // poll every 5s
    return () => clearInterval(interval);
  }, []);

  return stats;
}
```

Polling every 5 seconds. Crude, but it works. We'll replace it with SSE in Chapter 4.

## Loading & Error States

Never show a blank screen. Always show *something*.

```tsx
// src/App.tsx
import { JobList } from "./components/JobList";
import { StatsBar } from "./components/StatsBar";
import { useJobs } from "./hooks/useJobs";
import { useStats } from "./hooks/useStats";

export default function App() {
  const { jobs, loading, error } = useJobs();
  const stats = useStats();

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-xl font-mono font-bold">ShopZilla Job Engine</h1>
      </header>
      <main className="p-6 max-w-7xl mx-auto">
        {stats && <StatsBar stats={stats} />}

        {loading && (
          <p className="text-gray-500 text-center py-12 animate-pulse">
            Loading jobs...
          </p>
        )}

        {error && (
          <div className="bg-red-950 border border-red-800 rounded-lg p-4 mb-4">
            <p className="text-red-400 font-mono text-sm">
              ✗ Failed to load jobs: {error}
            </p>
            <p className="text-red-500 text-xs mt-1">
              Is the backend running at localhost:8080?
            </p>
          </div>
        )}

        {!loading && !error && <JobList jobs={jobs} />}
      </main>
    </div>
  );
}
```

Three states, three UI branches:
1. **Loading** → pulsing "Loading jobs..."
2. **Error** → red box with the error message and a hint
3. **Success** → the job list

## CORS: The First Wall

You start the frontend. It loads. Then: `Access to fetch at 'http://localhost:8080/jobs' has been blocked by CORS policy`.

The browser blocks requests from `localhost:5173` (Vite) to `localhost:8080` (Spring Boot) because they're different origins. This is a security feature, not a bug.

Fix it on the backend:

```java
// Add to Spring Boot
@Bean
public WebMvcConfigurer corsConfigurer() {
    return new WebMvcConfigurer() {
        @Override
        public void addCorsMappings(CorsRegistry registry) {
            registry.addMapping("/**")
                .allowedOrigins("http://localhost:5173")
                .allowedMethods("*")
                .allowedHeaders("*");
        }
    };
}
```

Or use Vite's proxy (no backend changes needed):

```ts
// vite.config.ts
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8080",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

Then change your fetch URLs from `http://localhost:8080/jobs` to `/api/jobs`.

## Verify

1. Start the backend: `./gradlew bootRun`
2. Submit some jobs: `curl -X POST http://localhost:8080/jobs -d '{"type":"CSV_IMPORT","payload":"{}"}'`
3. Start the frontend: `npm run dev`
4. Open `http://localhost:5173`

Real jobs. Real statuses. Real data. The mock data is gone.

Captain Deadline submits a job via curl. Looks at the TV. Waits 5 seconds (the polling interval). The job appears. "Why is there a delay?"

That's Chapter 4.

---

[← Chapter 2: Making It Pretty](chapter-02-tailwind.md) | [Chapter 4: Real-time Updates →](chapter-04-real-time.md)
