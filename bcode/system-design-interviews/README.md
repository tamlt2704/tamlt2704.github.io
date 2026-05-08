# System Design Interviews — From Blank Whiteboard to Offer

A focused course for developers preparing for system design interviews at top companies. Each chapter is one complete mock interview — 45 minutes, structured approach, real trade-offs. Designed to study in short bursts (one chapter = one naptime session).

## Episodes

| # | Title | The Question | Key Concepts |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | The framework, how to structure 45 minutes |
| 01 | [URL Shortener](chapter-01-url-shortener.md) | Design bit.ly | Hashing, base62, read-heavy, caching |
| 02 | [Rate Limiter](chapter-02-rate-limiter.md) | Design an API rate limiter | Token bucket, sliding window, Redis |
| 03 | [Chat System](chapter-03-chat.md) | Design WhatsApp | WebSockets, message queues, presence |
| 04 | [News Feed](chapter-04-newsfeed.md) | Design Twitter's feed | Fan-out, push vs pull, ranking |
| 05 | [File Storage](chapter-05-storage.md) | Design Dropbox | Chunking, dedup, sync, metadata |
| 06 | [Search Engine](chapter-06-search.md) | Design Google search | Inverted index, ranking, crawling |
| 07 | [Video Streaming](chapter-07-video.md) | Design YouTube | CDN, transcoding, adaptive bitrate |
| 08 | [Notification System](chapter-08-notifications.md) | Design push notifications | Priority queues, delivery guarantees, templates |
| 09 | [Payment System](chapter-09-payments.md) | Design Stripe | Idempotency, ledger, reconciliation |
| 10 | [Distributed Cache](chapter-10-cache.md) | Design Redis cluster | Consistent hashing, eviction, replication |
| 11 | [Job Scheduler](chapter-11-scheduler.md) | Design cron at scale | Exactly-once, dead letter, priority |
| 12 | [Ride Sharing](chapter-12-rideshare.md) | Design Uber matching | Geospatial index, real-time matching, ETA |

## Prerequisites

- 2+ years of backend development experience
- Basic understanding of databases, APIs, and networking
- 30-45 minutes per chapter (one naptime or commute)

## Philosophy

System design interviews test breadth, not depth. You don't need to know everything — you need a structured approach and the ability to discuss trade-offs. Each chapter gives you a reusable framework: requirements → estimation → API → data model → architecture → deep dive → bottlenecks.
