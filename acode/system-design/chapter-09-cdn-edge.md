# Chapter 9: CDN Deep Dive

[← Ch 8](chapter-08-service-decomposition.md) | [Ch 10 →](chapter-10-rate-limiting.md)

---

## The Crisis

GhostDrop is growing internationally. 30% of users are now outside North America.

**Kai** (Slack, Thursday 2:00 PM):
> Users in Tokyo are reporting 800ms page loads. Singapore is even worse — 1.2 seconds. Our competitors load in 200ms.

**Omar**:
> I ran traceroute from Tokyo. 180ms round-trip just to reach us-east-1. Every asset request pays that penalty. A page with 20 assets = 20 × 180ms if not parallelized.

**Sana**:
> We set up CloudFront for file downloads in Chapter 3, but we're only using it for uploaded files. Static assets (JS, CSS, images), thumbnails, and API responses still come from origin.

**Amir**:
> The podcast audience is global. If Tokyo users get 800ms, we'll lose them in the first 3 seconds.

---

## Architecture (Before)

```
┌──────────┐                              ┌──────────┐
│  Tokyo   │──── 180ms RTT ─────────────→│  Origin  │
│  User    │                              │us-east-1 │
└──────────┘                              └──────────┘

┌──────────┐                              ┌──────────┐
│ São Paulo│──── 140ms RTT ─────────────→│  Origin  │
│  User    │                              │us-east-1 │
└──────────┘                              └──────────┘

Every request crosses the ocean.
```

## Architecture (After)

```
┌──────────┐     ┌──────────┐
│  Tokyo   │──5ms│  Tokyo   │
│  User    │────→│  Edge    │──── cache hit (90%) → respond immediately
└──────────┘     └──────────┘
                      │
                      │ cache miss (10%) → fetch from origin
                      ▼
                 ┌──────────┐
                 │  Origin  │
                 │us-east-1 │
                 └──────────┘

┌──────────┐     ┌──────────┐
│ São Paulo│──8ms│São Paulo │
│  User    │────→│  Edge    │──── cache hit → respond immediately
└──────────┘     └──────────┘
```

---

## Concept: How CDNs Work

A CDN is a network of servers (edge locations) distributed globally. They cache content close to users.

```
Request flow:
1. User requests cdn.ghostdrop.io/assets/app.js
2. DNS resolves to nearest edge location (anycast)
3. Edge checks local cache:
   - HIT: Return cached response (5ms)
   - MISS: Fetch from origin, cache it, return (180ms + origin time)
4. Subsequent requests from same region: cache HIT
```

### CDN Edge Locations (CloudFront Example)

```
┌─────────────────────────────────────────────────────────┐
│                    CloudFront Network                     │
│                                                           │
│  North America: 30 edge locations                        │
│  Europe: 25 edge locations                               │
│  Asia-Pacific: 20 edge locations                         │
│  South America: 5 edge locations                         │
│  Africa/Middle East: 5 edge locations                    │
│                                                           │
│  Total: ~400+ points of presence                         │
└─────────────────────────────────────────────────────────┘
```

---

## Concept: Cache Headers

The CDN decides what to cache based on HTTP headers from your origin.

### Key Headers

| Header | Purpose | Example |
|--------|---------|---------|
| `Cache-Control` | How long to cache | `max-age=31536000` (1 year) |
| `ETag` | Content fingerprint | `"abc123"` |
| `Vary` | Cache varies by header | `Vary: Accept-Encoding` |
| `s-maxage` | CDN-specific TTL | `s-maxage=3600` (1 hour at CDN) |

### GhostDrop's Cache Policy

```python
# Static assets (JS, CSS, images) — immutable, hashed filenames
@app.get("/assets/{filename}")
def serve_asset(filename: str):
    return FileResponse(
        f"static/{filename}",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            # Cache for 1 year. Filename changes when content changes.
        }
    )

# File thumbnails — stable but might regenerate
@app.get("/thumbs/{file_id}")
def serve_thumbnail(file_id: str):
    return FileResponse(
        get_thumbnail_path(file_id),
        headers={
            "Cache-Control": "public, max-age=86400, s-maxage=604800",
            # Browser: 1 day. CDN: 7 days.
            "ETag": f'"{file_id}-v{thumbnail_version}"',
        }
    )

# API responses — short or no cache
@app.get("/api/files")
def list_files(user: User):
    return JSONResponse(
        get_user_files(user.id),
        headers={
            "Cache-Control": "private, no-store",
            # Never cache user-specific API responses at CDN
        }
    )
```

---

## Concept: Cache Invalidation (Purging)

When content changes, you need to remove stale copies from edge caches.

### Strategies

| Strategy | How | Speed | Cost |
|----------|-----|-------|------|
| **TTL expiry** | Wait for cache to expire | Slow (minutes-hours) | Free |
| **Versioned URLs** | New URL = new cache entry | Instant | No purge needed |
| **Explicit purge** | API call to invalidate | 5-15 seconds | $0.005/path |
| **Wildcard purge** | Invalidate `/thumbs/*` | 5-15 seconds | $0.005/request |

### GhostDrop's Approach

```python
# Versioned URLs for static assets (never purge)
# app.js?v=abc123 → app.js?v=def456 (new deploy = new URL)

# Explicit purge for thumbnails (rare)
def regenerate_thumbnail(file_id: str):
    create_new_thumbnail(file_id)
    cloudfront.create_invalidation(
        DistributionId=CF_DIST_ID,
        InvalidationBatch={
            'Paths': {'Items': [f'/thumbs/{file_id}'], 'Quantity': 1},
            'CallerReference': str(uuid4()),
        }
    )
```

---

## Concept: Dynamic vs Static Content

| Content Type | Cacheable? | Strategy |
|-------------|-----------|----------|
| JS/CSS bundles | Yes (immutable) | Cache forever, versioned filenames |
| Uploaded files | Yes (immutable keys) | Cache forever |
| Thumbnails | Yes (rarely changes) | Cache 7 days, purge on change |
| User avatars | Yes (with revalidation) | Cache 1 hour, ETag |
| API: file list | No (user-specific) | Don't cache at CDN |
| API: public stats | Maybe | Cache 60 seconds |
| HTML pages | Depends | Cache 5 min for anonymous, skip for logged-in |

---

## Concept: Geo-Routing

For dynamic content that can't be cached, route users to the nearest origin.

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│  Tokyo   │────→│  Tokyo   │────→│ Origin:      │
│  User    │     │  Edge    │     │ ap-northeast │
└──────────┘     └──────────┘     └──────────────┘

┌──────────┐     ┌──────────┐     ┌──────────────┐
│  London  │────→│  London  │────→│ Origin:      │
│  User    │     │  Edge    │     │ eu-west-1    │
└──────────┘     └──────────┘     └──────────────┘
```

**GhostDrop today**: Single origin in us-east-1. CDN caches static content globally.

**GhostDrop future**: Multi-region origins. CDN routes to nearest origin for cache misses. (This requires multi-region database — complex, not needed yet.)

---

## GhostDrop CDN Implementation

### CloudFront Distribution Config

```yaml
# terraform/cloudfront.tf (simplified)
resource "aws_cloudfront_distribution" "main" {
  enabled = true
  aliases = ["cdn.ghostdrop.io"]

  # Origin 1: Static assets (S3)
  origin {
    domain_name = aws_s3_bucket.assets.bucket_regional_domain_name
    origin_id   = "s3-assets"
  }

  # Origin 2: API (ALB)
  origin {
    domain_name = aws_lb.ghostdrop.dns_name
    origin_id   = "alb-api"
    custom_origin_config {
      http_port  = 80
      https_port = 443
      origin_protocol_policy = "https-only"
    }
  }

  # Behavior: Static assets
  ordered_cache_behavior {
    path_pattern     = "/assets/*"
    target_origin_id = "s3-assets"
    cache_policy_id  = "658327ea-f89d-4fab-a63d-7e88639e58f6" # CachingOptimized
    compress         = true
  }

  # Behavior: File downloads
  ordered_cache_behavior {
    path_pattern     = "/files/*"
    target_origin_id = "s3-assets"
    cache_policy_id  = "658327ea-f89d-4fab-a63d-7e88639e58f6"
  }

  # Default: API (no cache)
  default_cache_behavior {
    target_origin_id = "alb-api"
    cache_policy_id  = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad" # CachingDisabled
  }
}
```

### Latency Results

| Region | Before (no CDN) | After (CDN) | Improvement |
|--------|-----------------|-------------|-------------|
| US East | 50ms | 45ms | 10% |
| US West | 120ms | 25ms | 79% |
| Europe | 180ms | 30ms | 83% |
| Tokyo | 800ms | 35ms | 96% |
| São Paulo | 650ms | 40ms | 94% |

*For cached content. API calls still hit origin.*

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| CDN for static assets | Global low latency | $0.085/GB transfer |
| Immutable filenames | Never invalidate, perfect caching | Build pipeline must hash filenames |
| No CDN cache for API | Always fresh data | API latency unchanged for distant users |
| Single origin (for now) | Simple architecture | API latency still high for Asia-Pacific |

---

## Why Not Just...

**"Why not cache API responses at the CDN?"**
User-specific responses (file lists, profiles) can't be cached — you'd serve User A's files to User B. Public endpoints (landing page, pricing) can be cached briefly.

**"Why not deploy the app in every region?"**
Multi-region requires multi-region database (replication, conflict resolution, routing). That's a massive undertaking. CDN handles 90% of the latency problem for 10% of the effort.

**"Why not use a multi-CDN strategy?"**
At GhostDrop's scale, one CDN is fine. Multi-CDN (CloudFront + Fastly + Akamai) helps at Netflix scale where a single CDN's capacity in a region might be insufficient.

---

## Exercise

GhostDrop's landing page (ghostdrop.io) is server-rendered and shows different content for logged-in vs anonymous users. Currently it's not cached at all.

1. Can you cache it at the CDN? How would you handle the logged-in vs anonymous difference?
2. What cache TTL would you use?
3. How do you handle A/B tests that show different page variants?

<details>
<summary>Hint</summary>

Cache the anonymous version at the CDN (5-minute TTL). For logged-in users, use `Cache-Control: private` or `Vary: Cookie` to bypass CDN cache. For A/B tests, use `Vary: X-AB-Group` header and have the CDN forward that header to origin. Each variant gets its own cache entry. Alternatively, serve a static shell and hydrate user-specific content via API calls from the client.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **CDN** | Content Delivery Network — caches at edge locations globally |
| **Edge Location** | CDN server geographically close to users |
| **Cache Hit** | Content served from edge cache (fast) |
| **Cache Miss** | Content fetched from origin (slow) |
| **Origin** | Your actual server behind the CDN |
| **Purge/Invalidation** | Removing content from CDN cache |
| **Anycast** | DNS routing to nearest edge location |
| **s-maxage** | Cache-Control directive for shared caches (CDN) |
| **Immutable** | Content that never changes (safe to cache forever) |

---

## What Breaks Next

CDN is serving static content globally. Tokyo users are happy. Page loads dropped from 800ms to 35ms for cached content.

But the podcast promo is generating buzz. Bots are scraping share links. Someone is brute-forcing the API trying random file IDs. One IP is making 10,000 requests per minute.

"We need to limit this," Omar says. "Before they take us down."

You need rate limiting.

[← Ch 8](chapter-08-service-decomposition.md) | [Ch 10 →](chapter-10-rate-limiting.md)
