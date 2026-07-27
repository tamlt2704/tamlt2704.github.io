# Building a Data Dashboard — Page Design, UI/UX, Charts

---

## What We're Building

A dashboard that displays government data with interactive charts. Think:

```
┌─────────────────────────────────────────────────────────────────┐
│  Dashboard Title                          [Filter ▼] [Date ▼]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Stat Card│ │ Stat Card│ │ Stat Card│ │ Stat Card│           │
│  │  1,234   │ │   567    │ │  +12%    │ │  89.2%   │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                  │
│  ┌─────────────────────────────┐ ┌────────────────────────┐     │
│  │                             │ │                        │     │
│  │      Line Chart             │ │     Pie / Donut        │     │
│  │      (trends over time)     │ │     (breakdown)        │     │
│  │                             │ │                        │     │
│  └─────────────────────────────┘ └────────────────────────┘     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                           │   │
│  │                 Bar Chart (comparison)                     │   │
│  │                                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Data Table (detailed view)                               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Chart Library: Recharts

| Library | Pros | Cons |
|---------|------|------|
| **Recharts** ✓ | Built for React, declarative, responsive, great docs | Not the fastest for 10k+ data points |
| Chart.js (react-chartjs-2) | Familiar, canvas-based, fast | Imperative API, less React-native |
| D3.js | Maximum flexibility | Steep learning curve, low-level |
| Nivo | Beautiful defaults, many chart types | Heavier bundle |
| Tremor | Dashboard-focused, pre-built layouts | Less customisable |

**Recharts** is the best balance of simplicity, React integration, and customisation for a dashboard.

---

## Step 1: Install

```bash
npm install recharts
```

---

## Step 2: Dashboard Layout

Create `app/dashboard/page.tsx`:

```tsx
export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Government data overview</p>
      </div>

      {/* Stat Cards */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* cards go here */}
      </div>

      {/* Charts Row */}
      <div className="mb-8 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">{/* wide chart */}</div>
        <div>{/* narrow chart */}</div>
      </div>

      {/* Full Width Chart */}
      <div className="mb-8">{/* bar chart */}</div>
    </div>
  )
}
```

**Layout classes explained:**

| Class | What it does |
|-------|-------------|
| `max-w-7xl` | Maximum width ~80rem — content doesn't stretch on ultra-wide screens |
| `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` | 1 column on mobile → 2 on tablet → 4 on desktop |
| `gap-4` | Space between grid items |
| `lg:col-span-2` | This item takes 2 columns on large screens |

---

## Step 3: Stat Cards

The top row — key numbers at a glance.

```tsx
interface StatCardProps {
  title: string
  value: string
  change?: string
  trend?: "up" | "down"
}

function StatCard({ title, value, change, trend }: StatCardProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <p className="text-sm text-muted-foreground">{title}</p>
      <p className="mt-2 text-3xl font-bold text-foreground">{value}</p>
      {change && (
        <p className={`mt-1 text-sm ${trend === "up" ? "text-green-500" : "text-red-500"}`}>
          {trend === "up" ? "↑" : "↓"} {change}
        </p>
      )}
    </div>
  )
}
```

Usage:

```tsx
<div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
  <StatCard title="Total Records" value="1,234,567" change="+12.3%" trend="up" />
  <StatCard title="Active Regions" value="42" />
  <StatCard title="Avg Response Time" value="2.4s" change="-8%" trend="up" />
  <StatCard title="Completion Rate" value="89.2%" change="-1.2%" trend="down" />
</div>
```

---

## Step 4: Line Chart (Trends Over Time)

```tsx
"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

const data = [
  { month: "Jan", value: 400 },
  { month: "Feb", value: 300 },
  { month: "Mar", value: 600 },
  { month: "Apr", value: 800 },
  { month: "May", value: 500 },
  { month: "Jun", value: 900 },
]

function TrendChart() {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <h3 className="mb-4 text-lg font-semibold text-foreground">Monthly Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} />
          <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="hsl(var(--primary))"
            strokeWidth={2}
            dot={{ fill: "hsl(var(--primary))" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
```

**Key concepts:**

| Component | What it does |
|-----------|-------------|
| `ResponsiveContainer` | Makes the chart fill its parent width (responsive) |
| `LineChart` | The chart wrapper — pass `data` as prop |
| `XAxis` / `YAxis` | The axes — `dataKey` maps to a field in your data |
| `CartesianGrid` | The grey grid lines behind the chart |
| `Tooltip` | Shows values on hover |
| `Line` | The actual line — `dataKey` = which field to plot |

---

## Step 5: Bar Chart (Comparison)

```tsx
"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

const data = [
  { region: "North", population: 4200 },
  { region: "South", population: 3800 },
  { region: "East", population: 5100 },
  { region: "West", population: 2900 },
  { region: "Central", population: 6200 },
]

function ComparisonChart() {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <h3 className="mb-4 text-lg font-semibold text-foreground">By Region</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis dataKey="region" stroke="hsl(var(--muted-foreground))" fontSize={12} />
          <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
            }}
          />
          <Bar dataKey="population" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
```

**`radius={[4, 4, 0, 0]}`** — rounds the top corners of each bar. `[top-left, top-right, bottom-right, bottom-left]`.

---

## Step 6: Pie/Donut Chart (Breakdown)

```tsx
"use client"

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"

const data = [
  { name: "Education", value: 35 },
  { name: "Healthcare", value: 25 },
  { name: "Transport", value: 20 },
  { name: "Defence", value: 15 },
  { name: "Other", value: 5 },
]

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
]

function BreakdownChart() {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <h3 className="mb-4 text-lg font-semibold text-foreground">Spending Breakdown</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
```

**Donut vs Pie:**
- `innerRadius={0}` = Pie (filled circle)
- `innerRadius={60}` = Donut (hole in the middle) — looks more modern

**`COLORS`** — uses the chart color variables from your shadcn `globals.css`. They work in both light and dark mode.

---

## Step 7: Multiple Lines (Compare Datasets)

```tsx
const data = [
  { month: "Jan", thisYear: 400, lastYear: 300 },
  { month: "Feb", thisYear: 300, lastYear: 400 },
  { month: "Mar", thisYear: 600, lastYear: 500 },
  { month: "Apr", thisYear: 800, lastYear: 600 },
]

<LineChart data={data}>
  <Line type="monotone" dataKey="thisYear" stroke="hsl(var(--chart-1))" strokeWidth={2} />
  <Line type="monotone" dataKey="lastYear" stroke="hsl(var(--chart-2))" strokeWidth={2} strokeDasharray="5 5" />
  <Legend />
</LineChart>
```

`strokeDasharray="5 5"` makes the second line dashed — easy to distinguish.

---

## Step 8: Chart Card Wrapper (Reusable)

Extract the card pattern into a reusable component:

```tsx
interface ChartCardProps {
  title: string
  description?: string
  children: React.ReactNode
  className?: string
}

function ChartCard({ title, description, children, className }: ChartCardProps) {
  return (
    <div className={`rounded-lg border border-border bg-card p-6 ${className ?? ""}`}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      {children}
    </div>
  )
}
```

Usage:

```tsx
<ChartCard title="Monthly Trend" description="Records processed per month">
  <ResponsiveContainer width="100%" height={300}>
    <LineChart data={data}>...</LineChart>
  </ResponsiveContainer>
</ChartCard>
```

---

## Step 9: Dark Mode Support for Charts

Recharts doesn't read CSS variables directly in all cases. Use your theme colors:

```tsx
// These work because they resolve to actual color values at render time
stroke="hsl(var(--border))"
fill="hsl(var(--primary))"
```

If you need to pass colors as JS values (e.g. for Tooltip styles), create a helper:

```tsx
const chartTheme = {
  grid: "hsl(var(--border))",
  axis: "hsl(var(--muted-foreground))",
  tooltip: {
    backgroundColor: "hsl(var(--card))",
    border: "1px solid hsl(var(--border))",
    borderRadius: "8px",
    color: "hsl(var(--foreground))",
  },
}
```

---

## Step 10: Loading CSV Data

Since you're exporting to GitHub Pages (static site), you can't use server-side APIs. Load CSV files at **build time** or from the `public/` folder at runtime.

### Option A: CSV in `public/` (runtime loading)

Put your CSV file in `public/data/population.csv`:

```csv
region,population,year
North,4200,2024
South,3800,2024
East,5100,2024
West,2900,2024
```

Install a CSV parser:

```bash
npm install papaparse
npm install -D @types/papaparse
```

Load and parse it in your component:

```tsx
"use client"

import { useEffect, useState } from "react"
import Papa from "papaparse"

interface Row {
  region: string
  population: number
  year: number
}

export function DataChart() {
  const [data, setData] = useState<Row[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("/data/population.csv")
      .then((res) => res.text())
      .then((csv) => {
        const result = Papa.parse<Row>(csv, {
          header: true,          // first row = column names
          dynamicTyping: true,   // auto-convert numbers
          skipEmptyLines: true,
        })
        setData(result.data)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="h-[300px] animate-pulse rounded-lg bg-muted" />
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="region" />
        <YAxis />
        <Bar dataKey="population" fill="hsl(var(--primary))" />
      </BarChart>
    </ResponsiveContainer>
  )
}
```

**Papaparse options:**

| Option | What it does |
|--------|-------------|
| `header: true` | Uses first row as keys (`region`, `population`, `year`) |
| `dynamicTyping: true` | Converts `"4200"` → `4200` (number, not string) |
| `skipEmptyLines: true` | Ignores blank rows |

### Option B: Import CSV at Build Time (Smaller Bundle)

If the CSV doesn't change at runtime, process it during build. Create a script or use Next.js `generateStaticParams`.

For simplicity, convert your CSV to JSON once:

```bash
npx papaparse public/data/population.csv --header --out public/data/population.json
```

Or just keep a `data.ts` file:

```ts
// data/population.ts
export const populationData = [
  { region: "North", population: 4200, year: 2024 },
  { region: "South", population: 3800, year: 2024 },
  // ...
]
```

Then import directly — no fetch, no loading state, works with static export:

```tsx
import { populationData } from "@/data/population"
```

### Option C: Multiple CSVs (Recommended for Gov Data)

```
public/
└── data/
    ├── population.csv
    ├── spending.csv
    ├── education.csv
    └── transport.csv
```

Create a reusable hook:

```tsx
"use client"

import { useEffect, useState } from "react"
import Papa from "papaparse"

export function useCsvData<T>(path: string) {
  const [data, setData] = useState<T[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(path)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load ${path}`)
        return res.text()
      })
      .then((csv) => {
        const result = Papa.parse<T>(csv, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
        })
        setData(result.data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [path])

  return { data, loading, error }
}
```

Usage:

```tsx
const { data, loading } = useCsvData<PopulationRow>("/data/population.csv")
const { data: spending } = useCsvData<SpendingRow>("/data/spending.csv")
```

---

## Step 11: Static Export for GitHub Pages

GitHub Pages only serves static files — no Node.js server. Next.js supports this with `output: "export"`.

### Configure Next.js for static export

Update `next.config.ts`:

```ts
import createMDX from "@next/mdx"

const withMDX = createMDX({})

const nextConfig = {
  output: "export",
  pageExtensions: ["ts", "tsx", "md", "mdx"],
  images: {
    unoptimized: true,  // GitHub Pages can't run image optimization
  },
  basePath: "/your-repo-name",  // IMPORTANT: must match your GitHub repo name
}

export default withMDX(nextConfig)
```

**Key settings:**

| Setting | Why |
|---------|-----|
| `output: "export"` | Generates static HTML/CSS/JS in `out/` folder |
| `images: { unoptimized: true }` | Next.js image optimization needs a server — disable it |
| `basePath: "/your-repo-name"` | GitHub Pages serves from `https://username.github.io/repo-name/` |

### Build and preview

```bash
npm run build
```

This creates an `out/` folder with all your static files. Preview locally:

```bash
npx serve out
```

### Deploy to GitHub Pages

**Option A: GitHub Actions (recommended)**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: out

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

**Option B: Manual deploy**

```bash
npm run build
npx gh-pages -d out
```

Install `gh-pages`:

```bash
npm install -D gh-pages
```

Add to `package.json` scripts:

```json
{
  "scripts": {
    "deploy": "npm run build && gh-pages -d out"
  }
}
```

Then just:

```bash
npm run deploy
```

### Enable GitHub Pages in repo settings

1. Go to your repo → Settings → Pages
2. Source: **GitHub Actions** (if using the workflow) or **Deploy from a branch** → `gh-pages`

### Things that DON'T work with static export

| Feature | Why | Workaround |
|---------|-----|-----------|
| `next/image` optimization | Needs a server | Set `unoptimized: true` |
| API routes (`app/api/`) | Needs a server | Fetch external APIs or use static data |
| Server Components fetching data | No server at runtime | Use `"use client"` + fetch from `public/` |
| Dynamic routes without `generateStaticParams` | Needs server routing | Define all paths at build time |
| Middleware | Needs a server | None — use client-side logic |

### BasePath fix for links and assets

With `basePath: "/your-repo-name"`, all links and assets automatically prefix. But if you hardcode paths, prefix them:

```tsx
// ❌ Won't work on GitHub Pages
fetch("/data/population.csv")

// ✅ Works with basePath
fetch(`${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/data/population.csv`)
```

Or add to `.env.local`:

```
NEXT_PUBLIC_BASE_PATH=/your-repo-name
```

And in your `useCsvData` hook:

```tsx
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? ""
fetch(`${basePath}${path}`)
```

---

## Updated Project Structure

```
javizhome/
├── .github/
│   └── workflows/
│       └── deploy.yml          ← Auto-deploy on push to main
├── app/
│   ├── dashboard/
│   │   └── page.tsx            ← Dashboard with charts
│   ├── blog/
│   │   └── bubble-sort/
│   │       └── page.mdx
│   └── layout.tsx
├── components/
│   ├── charts/
│   │   ├── trend-chart.tsx
│   │   ├── comparison-chart.tsx
│   │   ├── breakdown-chart.tsx
│   │   └── stat-card.tsx
│   └── demos/
│       └── bubble-sort-demo.tsx
├── hooks/
│   └── use-csv-data.ts         ← Reusable CSV loading hook
├── public/
│   └── data/
│       ├── population.csv      ← Your gov.data CSV files
│       ├── spending.csv
│       └── education.csv
├── next.config.ts              ← output: "export" + basePath
└── out/                        ← Generated static site (gitignored)
```

---

## Dashboard UX Principles

### Layout Rules

| Rule | Why |
|------|-----|
| **Stats at the top** | Key numbers visible without scrolling |
| **Wide charts for trends** | Time-series need horizontal space |
| **Narrow charts for breakdowns** | Pie/donut don't need much width |
| **Full-width for comparison** | Bar charts comparing many items need room |
| **Table at the bottom** | Detailed data for those who want to dig deeper |

### Visual Hierarchy

```
1. TITLE + FILTERS (what am I looking at?)
2. STAT CARDS (what's the headline?)
3. TREND CHART (is it going up or down?)
4. BREAKDOWN (where's it coming from?)
5. DETAIL TABLE (show me the numbers)
```

Users scan top-to-bottom: overview → detail.

### Color

| Use | Color |
|-----|-------|
| Primary data | `hsl(var(--primary))` — your brand color |
| Secondary line | `hsl(var(--chart-2))` — distinct but not dominant |
| Positive change | Green (`text-green-500`) |
| Negative change | Red (`text-red-500`) |
| Grid / axes | `hsl(var(--border))` — subtle, don't distract |

**Rules:**
- Maximum 5 colors in one chart — more becomes unreadable
- Use the `--chart-1` through `--chart-5` variables from shadcn (already dark-mode aware)
- Keep axes and grid subtle — the data is the star

### Responsive Design

| Screen | Layout |
|--------|--------|
| Mobile (`< 640px`) | Everything stacked in 1 column |
| Tablet (`640-1024px`) | Stat cards 2-wide, charts stacked |
| Desktop (`> 1024px`) | Stat cards 4-wide, charts side by side |

The grid classes handle this automatically:

```tsx
grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4
```

### Interactivity Tips

| Feature | How |
|---------|-----|
| Hover tooltip | Built into Recharts `<Tooltip />` |
| Click to filter | `onClick` on chart elements → update state → re-render other charts |
| Date range picker | Filter at the top → all charts update |
| Zoom on time-series | Recharts `<Brush />` component |
| Animate on load | Recharts `isAnimationActive={true}` (default) |

---

## Putting It All Together

```tsx
"use client"

import { /* all your chart components */ } from "./components"

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Government Data Dashboard</h1>
          <p className="text-muted-foreground">Public records overview — 2026</p>
        </div>
        <div className="flex gap-2">
          {/* Filters go here */}
        </div>
      </div>

      {/* Stat Cards */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Records" value="1,234,567" change="+12.3%" trend="up" />
        <StatCard title="Regions" value="42" />
        <StatCard title="Updated" value="2h ago" />
        <StatCard title="Completeness" value="89.2%" change="-1.2%" trend="down" />
      </div>

      {/* Charts Row 1: Trend + Breakdown */}
      <div className="mb-8 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ChartCard title="Monthly Trend" className="lg:col-span-2">
          <TrendChart />
        </ChartCard>
        <ChartCard title="Spending Breakdown">
          <BreakdownChart />
        </ChartCard>
      </div>

      {/* Charts Row 2: Full width comparison */}
      <ChartCard title="By Region" description="Population distribution">
        <ComparisonChart />
      </ChartCard>
    </div>
  )
}
```

---

## Which Chart for Which Data?

| Data type | Best chart | Example |
|-----------|-----------|---------|
| Change over time | Line chart | Monthly revenue, yearly population |
| Compare categories | Bar chart (vertical) | Region comparison, department spending |
| Rank / top N | Horizontal bar chart | Top 10 cities by population |
| Part of whole | Pie / Donut | Budget allocation percentages |
| Distribution | Histogram | Age distribution, income brackets |
| Correlation | Scatter plot | GDP vs life expectancy |
| Geographic | Map / Choropleth | Population density by region |

---

## Next Steps

1. **Add filters** — shadcn `Select` or `DatePicker` at the top
2. **Add a data table** — shadcn `Table` + `@tanstack/react-table` for sorting/pagination
3. **Connect real data** — fetch from gov.data API
4. **Add loading skeletons** — `animate-pulse` placeholders while data loads
5. **Make charts clickable** — click a bar → filter other charts by that category
