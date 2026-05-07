# Chapter 13: API Routes — Route Handlers

[← Chapter 12: Streaming](chapter-12-streaming.md) | [Chapter 14: Performance →](chapter-14-performance.md)

---

## The Task

Owen needs three things:
1. A webhook endpoint for the CMS to trigger revalidation
2. A proxy for the weather API (secret key can't be in the browser)
3. A search endpoint that the client-side SearchBar can call

---

## Route Handlers: API Endpoints in Next.js

Create a `route.ts` file (not `page.tsx`) in any app directory folder:

```
src/app/api/
├── weather/route.ts        → GET /api/weather
├── revalidate/route.ts     → POST /api/revalidate
└── search/route.ts         → GET /api/search
```

---

## GET: Weather Proxy

```tsx
// src/app/api/weather/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const lat = searchParams.get("lat");
  const lng = searchParams.get("lng");

  if (!lat || !lng) {
    return NextResponse.json({ error: "lat and lng required" }, { status: 400 });
  }

  // Secret key stays on the server — never exposed to browser
  const res = await fetch(
    `https://api.weather.com/v1/forecast?lat=${lat}&lng=${lng}&key=${process.env.WEATHER_API_KEY}`,
    { next: { revalidate: 600 } } // cache weather for 10 minutes
  );

  if (!res.ok) {
    return NextResponse.json({ error: "Weather API failed" }, { status: 502 });
  }

  const data = await res.json();
  return NextResponse.json(data);
}
```

The browser calls `/api/weather?lat=47.6&lng=-122.3`. The server adds the secret key and proxies to the weather API. The key never leaves the server.

---

## POST: Webhook for Revalidation

```tsx
// src/app/api/revalidate/route.ts
import { revalidateTag } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const secret = request.headers.get("x-webhook-secret");
  if (secret !== process.env.WEBHOOK_SECRET) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json();
  const { type, slug } = body;

  if (type === "trail_updated" && slug) {
    revalidateTag(`trail-${slug}`);
    return NextResponse.json({ revalidated: true, slug });
  }

  return NextResponse.json({ error: "Unknown event type" }, { status: 400 });
}
```

Owen's CMS calls `POST /api/revalidate` with the trail slug. The cached page regenerates immediately.

---

## GET: Search Endpoint

```tsx
// src/app/api/search/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams.get("q");
  if (!query || query.length < 2) {
    return NextResponse.json([]);
  }

  const res = await fetch(
    `http://localhost:4000/api/trails?q=${encodeURIComponent(query)}&limit=5`
  );
  const trails = await res.json();

  return NextResponse.json(trails);
}
```

The SearchBar client component calls this endpoint for live results.

---

## Dynamic Route Handlers

```tsx
// src/app/api/trails/[slug]/route.ts
import { NextRequest, NextResponse } from "next/server";

interface Context {
  params: Promise<{ slug: string }>;
}

export async function GET(request: NextRequest, { params }: Context) {
  const { slug } = await params;
  const trail = await getTrail(slug);

  if (!trail) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  return NextResponse.json(trail);
}
```

---

## Request & Response Helpers

```tsx
// Reading the request
const body = await request.json();           // JSON body
const formData = await request.formData();   // Form data
const text = await request.text();           // Raw text
request.headers.get("authorization");        // Headers
request.nextUrl.searchParams.get("q");       // Query params
request.cookies.get("token");                // Cookies

// Building the response
NextResponse.json(data);                     // JSON response
NextResponse.json(data, { status: 201 });    // With status code
NextResponse.redirect(new URL("/", request.url)); // Redirect
new NextResponse(stream, { headers: { "Content-Type": "text/event-stream" } }); // Streaming
```

---

## CORS (For External Clients)

```tsx
// src/app/api/public/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const data = { trails: 500, reviews: 12000 };

  return NextResponse.json(data, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET",
    },
  });
}

// Handle preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
```

---

## When to Use Route Handlers vs Server Actions

| Use Case | Route Handler | Server Action |
|---|---|---|
| External webhooks | ✅ | ❌ |
| Third-party API proxy | ✅ | ❌ |
| Client-side fetch (search, infinite scroll) | ✅ | ❌ |
| Form submissions | ❌ | ✅ |
| Mutations from UI | ❌ | ✅ |
| CORS / public API | ✅ | ❌ |

Rule: If it's triggered by a form or button in YOUR app, use Server Actions. If it's called by external systems or needs to be a traditional REST endpoint, use Route Handlers.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
File                            │ Endpoint
────────────────────────────────┼──────────────────────────────────────
app/api/x/route.ts              │ /api/x
app/api/x/[id]/route.ts         │ /api/x/:id
────────────────────────────────┼──────────────────────────────────────
export async function GET()     │ Handle GET requests
export async function POST()    │ Handle POST requests
export async function PUT()     │ Handle PUT requests
export async function DELETE()  │ Handle DELETE requests
export async function OPTIONS() │ Handle CORS preflight
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Raj: "Run Lighthouse. I want a 95+ score. Analyze the bundle. Find what's heavy. Make it fast."

---

[← Chapter 12: Streaming](chapter-12-streaming.md) | [Chapter 14: Performance →](chapter-14-performance.md)
