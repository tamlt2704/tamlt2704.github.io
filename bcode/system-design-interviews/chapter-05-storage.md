# Chapter 5: Design File Storage (Dropbox/Google Drive)

[← News Feed](./chapter-04-newsfeed.md) | [Next: Web Search →](./chapter-06-search.md)

---

## The Question

> "Design a cloud file storage and synchronization service like Dropbox or Google Drive. Users can upload files, sync them across devices, and share with others. When a file changes on one device, it should appear on all other devices within seconds."

---

## Step 1: Requirements & Scope

**Functional:**
- Upload, download, and delete files
- Sync files across multiple devices automatically
- File versioning (undo changes)
- Share files/folders with other users
- Offline editing with sync on reconnect

**Non-functional:**
- 500M users, 100M DAU
- Average file size: 1 MB, max: 10 GB
- Sync latency <5 seconds for small files
- Strong consistency for file metadata
- High durability (never lose a file — 99.999999999% / 11 nines)

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Files stored | 500M users × 200 files avg | 100B files |
| Total storage | 100B × 1 MB avg | ~100 PB |
| Daily uploads | 100M DAU × 2 files/day | 200M uploads/day |
| Upload QPS | 200M / 86400 | ~2,300 uploads/sec |
| Sync events/sec | 200M × 3 devices | ~7,000 sync/sec |

---

## Step 3: API Design

```
POST /api/v1/files/upload
  Headers: Content-Type: multipart/form-data
  Body: { file_data, path: "/docs/report.pdf", parent_id: "folder_123" }
  Response: { "file_id": "f_789", "version": 3, "checksum": "abc123" }

GET /api/v1/files/{file_id}/download?version=3
  Response: file binary stream

GET /api/v1/sync/changes?cursor=<last_sync_cursor>
  Response: { "changes": [...], "cursor": "new_cursor", "has_more": false }

POST /api/v1/files/{file_id}/share
  Body: { "user_id": "u_456", "permission": "edit" }
```

---

## Step 4: Data Model

**File Metadata (SQL — needs ACID for consistency):**

| Field | Type |
|-------|------|
| file_id (PK) | UUID |
| user_id | UUID |
| file_name | VARCHAR |
| path | VARCHAR |
| size_bytes | BIGINT |
| checksum | VARCHAR |
| version | INT |
| is_deleted | BOOLEAN |
| updated_at | TIMESTAMP |

**File Chunks (Object Storage — S3):**

| Field | Type |
|-------|------|
| chunk_id (PK) | UUID |
| file_id | UUID |
| chunk_index | INT |
| checksum | VARCHAR |
| storage_path | VARCHAR |

---

## Step 5: High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Client  │────▶│ Load Balancer│────▶│  API Server     │────▶│  Metadata DB │
│  (App)   │     └──────────────┘     └────────┬────────┘     │  (Postgres)  │
└────┬─────┘                                   │              └──────────────┘
     │                                         │
     │ (chunked upload)                        ▼
     │                              ┌─────────────────┐
     └─────────────────────────────▶│  Block Server   │
                                    │  (chunking)     │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Object Storage │
                                    │  (S3)           │
                                    └─────────────────┘

     ┌─────────────────────────────────────────────────┐
     │           Notification Service                   │
     │  (WebSocket / Long-polling for sync events)     │
     └─────────────────────────────────────────────────┘
```

---

## Step 6: Deep Dive

### File Chunking

Split files into 4 MB chunks before upload:
- Only upload changed chunks (delta sync)
- Resume interrupted uploads (upload chunk by chunk)
- Deduplication: same chunk content → same chunk_id (content-addressable)

**Chunking algorithm:** Rolling hash (Rabin fingerprint) for content-defined chunking. Boundaries shift with content, minimizing re-uploads on small edits.

### Deduplication

```
chunk_checksum = SHA256(chunk_data)
if chunk_checksum exists in storage:
    reference existing chunk (no upload needed)
else:
    upload new chunk
```

Saves 30-50% storage in practice (many users store same files).

### Sync Protocol

**Client maintains a local sync cursor.** On each sync:

1. Client calls `GET /sync/changes?cursor=last_cursor`
2. Server returns list of changes since cursor
3. Client applies changes locally, updates cursor
4. For conflicts: last-write-wins OR keep both versions

**Real-time notification:** Server pushes "something changed" via WebSocket. Client then pulls the actual changes (push notification, pull data).

### Conflict Resolution

When two devices edit the same file offline:

| Strategy | Behavior |
|----------|----------|
| Last-write-wins | Latest timestamp wins, other is lost |
| Keep both | Save as "file (conflict copy)" |
| Merge | Only works for specific formats (text, CRDT) |

Dropbox uses "keep both" — safest for binary files.

### Notification of Changes

```
User A edits file → Block Server saves chunks → Metadata updated
    → Notification Service → Push to all User A's devices
    → Push to shared users' devices
```

Long-polling fallback for clients that can't maintain WebSocket.

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| Large file uploads | Chunking + parallel chunk upload |
| Storage cost (100 PB) | Deduplication + compression + cold storage tiers |
| Metadata DB load | Shard by user_id, read replicas |
| Sync storms (many devices) | Rate limit sync, batch notifications |
| Network bandwidth | Upload only changed chunks (delta sync) |

**Storage tiers:**
- Hot: Frequently accessed files (SSD-backed S3)
- Warm: Files not accessed in 30 days (standard S3)
- Cold: Files not accessed in 90 days (Glacier)

---

## Key Talking Points

- Chunking is the core insight — enables delta sync, dedup, and resumable uploads
- Content-addressable storage (hash as key) enables deduplication
- Push notification + pull data pattern for sync
- Conflict resolution: "keep both" is safest for general file storage
- Storage tiering dramatically reduces cost at scale

---

## Common Mistakes

- Uploading entire files on every change (no chunking)
- Not addressing conflict resolution for concurrent edits
- Ignoring deduplication (massive storage waste)
- Using only polling for sync (too slow or too expensive)
- Not discussing offline editing and reconnection
- Storing file content in the database instead of object storage

---

[← News Feed](./chapter-04-newsfeed.md) | [Next: Web Search →](./chapter-06-search.md)
