# Chapter 15: Deployment — Ship It

[← Chapter 14: Performance](chapter-14-performance.md)

---

## The Task

Raj: "It's been two weeks. Deploy it. I want a URL I can show investors by 5 PM."

---

## Option 1: Vercel (Fastest Path)

Vercel built Next.js. The integration is seamless.

```bash
npm install -g vercel
vercel
```

That's it. Vercel detects Next.js, builds it, deploys it, gives you a URL. Zero config.

### What Vercel Handles

- Automatic HTTPS
- Global CDN (edge network)
- Serverless functions for SSR/API routes
- Image optimization (built-in)
- ISR (automatic)
- Preview deployments (per PR)
- Analytics and speed insights

### Environment Variables

```bash
vercel env add WEATHER_API_KEY
vercel env add WEBHOOK_SECRET
vercel env add API_URL
```

Or set them in the Vercel dashboard: Settings → Environment Variables.

### Production Deploy

```bash
vercel --prod
```

Or connect your GitHub repo — every push to `main` auto-deploys.

---

## Option 2: Docker (Self-Hosted)

For teams that need full control or can't use Vercel.

```ts
// next.config.ts
const nextConfig: NextConfig = {
  output: "standalone", // creates a minimal production server
};
```

```dockerfile
# Dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy only what's needed to run
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

```bash
docker build -t trailblazer .
docker run -p 3000:3000 \
  -e API_URL=http://api:4000 \
  -e WEATHER_API_KEY=xxx \
  trailblazer
```

Deploy this container to: AWS ECS, Google Cloud Run, Railway, Fly.io, or any container platform.

---

## Option 3: Node.js Server (Simple)

```bash
npm run build
npm start
```

Runs a Node.js server on port 3000. Put it behind Nginx or a load balancer.

```nginx
# /etc/nginx/sites-available/trailblazer
server {
    listen 80;
    server_name trailblazer.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Environment Variables

```bash
# .env.local (development — never commit this)
API_URL=http://localhost:4000
WEATHER_API_KEY=dev_key_123
WEBHOOK_SECRET=dev_secret
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

| Prefix | Available Where | Use For |
|---|---|---|
| (none) | Server only | API keys, secrets, database URLs |
| `NEXT_PUBLIC_` | Server + browser | Public config (site URL, feature flags) |

⚠️ Never put secrets in `NEXT_PUBLIC_` variables. They're embedded in the client bundle.

---

## Production Checklist

### Before Deploy

```
✅ npm run build succeeds with no errors
✅ npm run lint passes
✅ All environment variables set in production
✅ Images configured (remotePatterns in next.config)
✅ Metadata set for all public pages
✅ sitemap.ts and robots.ts configured
✅ Error boundaries (error.tsx) in place
✅ 404 page (not-found.tsx) customized
✅ Lighthouse score > 90
```

### After Deploy

```
✅ All pages load correctly
✅ Auth flow works (login → protected page → logout)
✅ Forms submit successfully
✅ Images optimize correctly
✅ SEO: view source shows full HTML content
✅ Social previews work (share a trail on Twitter)
✅ Webhook revalidation works
✅ Error monitoring connected (Sentry, etc.)
```

---

## Monitoring

```tsx
// src/instrumentation.ts (Next.js 15+)
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    // Initialize server-side monitoring
    const Sentry = await import("@sentry/nextjs");
    Sentry.init({ dsn: process.env.SENTRY_DSN });
  }
}
```

### Key Metrics to Watch

| Metric | Tool | Alert When |
|---|---|---|
| Error rate | Sentry | > 1% of requests |
| Response time (p95) | Vercel Analytics / Datadog | > 2 seconds |
| Core Web Vitals | Vercel Speed Insights | LCP > 2.5s |
| Build time | CI/CD | > 5 minutes |
| Bundle size | Bundle analyzer | Grows > 10% |

---

## The Architecture (Final)

```
┌─────────────────────────────────────────────────────────────┐
│                    TrailBlazer (Next.js)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Static Pages (CDN)          Server-Rendered Pages           │
│  ├── / (home)                ├── /trails/:slug (ISR 60s)    │
│  ├── /about                  ├── /profile (dynamic)          │
│  └── /trails (ISR 5min)     └── /admin (dynamic)            │
│                                                              │
│  API Routes                  Server Actions                   │
│  ├── /api/weather (proxy)    ├── submitReview()              │
│  ├── /api/revalidate (hook)  ├── login()                    │
│  └── /api/search             └── logout()                   │
│                                                              │
│  Middleware                                                   │
│  └── Auth guard (protected routes)                           │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Owen's API (http://api:4000)                                │
│  └── REST endpoints for trails, reviews, auth                │
└─────────────────────────────────────────────────────────────┘
```

---

## What You Built (The Full Journey)

| Chapter | What You Learned |
|---|---|
| 1 | App Router, layouts, file-based routing |
| 2 | Dynamic routes, catch-all, route groups |
| 3 | Server-side data fetching, caching, revalidation |
| 4 | Tailwind, next/font, dark mode, CSS Modules |
| 5 | Link, loading.tsx, error.tsx, navigation |
| 6 | SEO metadata, sitemap, Open Graph, JSON-LD |
| 7 | Client vs Server Components, "use client" boundary |
| 8 | Server Actions, forms, validation, progressive enhancement |
| 9 | Middleware, auth, cookies, protected routes |
| 10 | next/image, optimization, blur placeholders |
| 11 | Static generation, ISR, on-demand revalidation |
| 12 | Streaming, Suspense boundaries, parallel loading |
| 13 | Route Handlers, API proxies, webhooks |
| 14 | Bundle analysis, Core Web Vitals, performance |
| 15 | Deployment, Docker, monitoring, production |

---

## 5:00 PM

Raj opens the URL on his phone. The home page loads in 800ms. He clicks a trail — instant navigation, skeleton appears, content streams in. He shares a trail on Slack — rich preview with image and description.

"Ship it to the investors."

Priya checks Google. "Mount Rainier hiking trail TrailBlazer" — first page.

Owen checks his API logs. Traffic is down 90% — ISR and caching handle most requests without hitting his server.

Mika opens Lighthouse. Score: 97.

You close your laptop. Two weeks. One framework. Production-ready.

---

[← Chapter 14: Performance](chapter-14-performance.md)
