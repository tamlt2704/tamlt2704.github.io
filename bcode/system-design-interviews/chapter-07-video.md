# Chapter 7: Design a Video Platform (YouTube)

[← Web Search](./chapter-06-search.md) | [Next: Notification System →](./chapter-08-notifications.md)

---

## The Question

> "Design a video sharing platform like YouTube. Users upload videos, which are transcoded into multiple resolutions and distributed globally. Viewers stream videos with adaptive bitrate. Include a basic recommendation engine."

---

## Step 1: Requirements & Scope

**Functional:**
- Upload videos (up to 1 hour, max 10 GB)
- Transcode to multiple resolutions (360p, 720p, 1080p, 4K)
- Stream videos with adaptive bitrate
- Video metadata (title, description, thumbnails)
- Basic recommendations ("up next")

**Non-functional:**
- 2B MAU, 500M videos watched/day
- 500K new videos uploaded/day
- Playback start latency <2 seconds
- Global distribution (low latency worldwide)
- High availability for streaming, eventual consistency for uploads

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Stream QPS | 500M views / 86400 | ~6,000 streams/sec |
| Upload QPS | 500K / 86400 | ~6 uploads/sec |
| Storage/day (raw) | 500K × 500 MB avg | ~250 TB/day |
| Storage/day (all resolutions) | 250 TB × 4 resolutions | ~1 PB/day |
| CDN bandwidth | 500M × 200 MB avg × 8 bits | ~10 Pbps peak |

---

## Step 3: API Design

```
POST /api/v1/videos/upload
  Body: multipart (video file + metadata)
  Response: { "video_id": "v_123", "upload_url": "https://upload.cdn.com/..." }

GET /api/v1/videos/{video_id}
  Response: { "title": "...", "streams": { "720p": "url", "1080p": "url" } }

GET /api/v1/videos/{video_id}/stream?resolution=720p
  Response: HLS/DASH manifest file

GET /api/v1/recommendations?video_id=v_123&limit=10
  Response: { "videos": [...] }
```

---

## Step 4: Data Model

**Video Metadata (SQL):**

| Field | Type |
|-------|------|
| video_id (PK) | UUID |
| user_id | UUID |
| title | VARCHAR |
| description | TEXT |
| status | ENUM (uploading, processing, ready, failed) |
| duration_sec | INT |
| view_count | BIGINT |
| created_at | TIMESTAMP |

**Video Files (Object Storage):**

```
s3://videos/raw/{video_id}/original.mp4
s3://videos/transcoded/{video_id}/720p/segment_001.ts
s3://videos/transcoded/{video_id}/720p/segment_002.ts
s3://videos/thumbnails/{video_id}/thumb_001.jpg
```

---

## Step 5: High-Level Architecture

```
                    UPLOAD PATH                          STREAMING PATH
┌──────────┐    ┌──────────────┐              ┌──────────┐    ┌─────────┐
│ Creator  │───▶│ Upload Server│              │  Viewer  │───▶│   CDN   │
└──────────┘    └──────┬───────┘              └──────────┘    └────┬────┘
                       │                                          │
                       ▼                                          │ (cache miss)
              ┌──────────────┐                                    ▼
              │ Object Store │◀──────────────────────────┌──────────────┐
              │ (raw video)  │                           │ Origin Server│
              └──────┬───────┘                           └──────────────┘
                     │
                     ▼
              ┌──────────────┐     ┌──────────────┐
              │ Message Queue│────▶│ Transcoding  │
              │ (task queue) │     │ Workers      │
              └──────────────┘     └──────┬───────┘
                                          │
                                          ▼
                                 ┌──────────────┐
                                 │ Object Store │
                                 │ (transcoded) │
                                 └──────────────┘
```

---

## Step 6: Deep Dive

### Video Upload Pipeline

1. **Client** splits video into chunks, uploads via resumable upload protocol
2. **Upload server** reassembles chunks in object storage
3. **Message queue** triggers transcoding job
4. **Transcoding workers** process video:
   - Decode → resize → encode at each resolution
   - Split into segments (2-10 sec each) for streaming
   - Generate thumbnails at key frames
5. **Metadata service** updates video status to "ready"

### Transcoding (Multiple Resolutions)

Each video produces multiple variants:

| Resolution | Bitrate | Use Case |
|-----------|---------|----------|
| 360p | 0.5 Mbps | Mobile/slow connection |
| 720p | 2.5 Mbps | Standard |
| 1080p | 5 Mbps | Desktop |
| 4K | 15 Mbps | Smart TV |

**Parallelization:** Each resolution transcoded independently. Further split: each segment transcoded in parallel. A 1-hour video can be transcoded in minutes.

### Adaptive Bitrate Streaming (ABR)

Protocol: HLS (Apple) or DASH (standard).

1. Video split into 2-10 second segments at each quality level
2. Client downloads a manifest file listing all segments and qualities
3. Client monitors bandwidth, switches quality per-segment
4. Buffer 2-3 segments ahead to handle fluctuations

```
manifest.m3u8:
  #EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360
  360p/playlist.m3u8
  #EXT-X-STREAM-INF:BANDWIDTH=2500000,RESOLUTION=1280x720
  720p/playlist.m3u8
```

### CDN Distribution

- Videos cached at edge locations worldwide (~200 PoPs)
- Popular videos: cached everywhere (hot content)
- Long-tail videos: cached on-demand, evicted quickly
- Origin pull: CDN fetches from origin on cache miss

**Cost optimization:** Pre-push viral/trending videos to all PoPs. Let long-tail content be pulled on demand.

### Recommendation Engine (Overview)

Simple approach: collaborative filtering + content signals.

```
score = w1×watch_history_similarity + w2×content_similarity + w3×engagement_rate
```

- **Collaborative:** "Users who watched X also watched Y"
- **Content-based:** Same category, creator, tags
- **Engagement:** Videos with high watch-through rate

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| Transcoding compute | Auto-scaling worker pool, spot instances |
| Storage cost (PB scale) | Tiered storage, delete low-view old videos |
| CDN bandwidth cost | Peer-to-peer for live events, compression |
| Hot videos (viral) | Pre-warm CDN caches, dedicated origin |
| Upload reliability | Resumable chunked uploads |

**View count accuracy:** Use approximate counters (HyperLogLog for unique views). Batch-update counts every few minutes, not per-view.

---

## Key Talking Points

- Separate upload path (async, heavy) from streaming path (sync, fast)
- Transcoding is embarrassingly parallel — split by resolution AND segment
- ABR streaming adapts to network conditions per-segment
- CDN is essential — you can't serve video from origin at scale
- Resumable uploads handle unreliable networks gracefully

---

## Common Mistakes

- Not separating upload/processing from serving (different scaling needs)
- Forgetting adaptive bitrate (serving single resolution)
- Ignoring CDN — trying to serve video directly from origin
- Not making uploads resumable (users on mobile will fail)
- Transcoding synchronously (user waits minutes for upload to "complete")
- Storing all resolutions for all videos regardless of popularity

---

[← Web Search](./chapter-06-search.md) | [Next: Notification System →](./chapter-08-notifications.md)
