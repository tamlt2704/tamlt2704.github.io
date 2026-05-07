# Chapter 3: Object Storage

[← Ch 2](chapter-02-load-balancer.md) | [Ch 4 →](chapter-04-database-separation.md)

---

## The Crisis

Load balancer is live. Three app servers. Traffic is balanced. Then:

**Kai** (Slack, 11:42 AM):
> User uploaded a file. Got a share link. Sent it to a friend. Friend clicks it. 404.

**Sana**:
> The upload went to Server 2. The download request hit Server 3. The file is on Server 2's local disk.

**Omar**:
> Also, each server has 500GB EBS. We're at 420GB on the original server. We'll be full in 6 days.

**Amir**:
> Files can't live on app servers anymore. Where do they go?

---

## Architecture (Before)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Users   │────→│    LB    │──┬─→│ Server 1 │──→ /data/files/ (local)
└──────────┘     └──────────┘  │  └──────────┘
                               ├─→│ Server 2 │──→ /data/files/ (local)
                               │  └──────────┘
                               └─→│ Server 3 │──→ /data/files/ (local)
                                  └──────────┘

Problem: File uploaded to Server 2 doesn't exist on Server 1 or 3
```

## Architecture (After)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Users   │────→│    LB    │──┬─→│ Server 1 │
└──────────┘     └──────────┘  │  └──────────┘
      │                        ├─→│ Server 2 │──→ All servers read/write
      │                        │  └──────────┘    to the same S3 bucket
      │                        └─→│ Server 3 │
      │                           └──────────┘
      │                                 │
      │         ┌───────────────────────┘
      │         ▼
      │    ┌──────────┐     ┌──────────┐
      │    │    S3     │     │   CDN    │
      │    │  (files)  │────→│(CloudFr.)│
      │    └──────────┘     └──────────┘
      │                          │
      └──────────────────────────┘
            (downloads via CDN)
```

---

## Concept: Object Storage

Object storage (S3, MinIO, GCS) stores files as flat key-value pairs:

```
Key:   "uploads/user_4821/photo_abc123.jpg"
Value: [binary file data]
Metadata: {content-type: "image/jpeg", uploaded-at: "2024-01-15"}
```

### Object Storage vs File System vs Block Storage

| Feature | File System (EBS) | Block Storage (EBS raw) | Object Storage (S3) |
|---------|-------------------|------------------------|---------------------|
| Access | POSIX paths | Raw blocks | HTTP API (GET/PUT) |
| Scale | Limited by disk | Limited by volume | Virtually unlimited |
| Sharing | One server | One server | Any server, any region |
| Cost (1TB) | ~$100/mo | ~$80/mo | ~$23/mo |
| Durability | 99.8% | 99.999% | 99.999999999% (11 nines) |

### Why S3 for GhostDrop?

- **Unlimited storage**: No more "disk full in 6 days"
- **Shared access**: All app servers read/write the same bucket
- **11 nines durability**: You'd lose 1 file per 10 million years
- **No server dependency**: Files survive even if all app servers die

---

## Concept: Signed URLs

**Sana**: "If files are in S3, do uploads go through our servers? That's a lot of bandwidth."

No. Use **signed URLs** — temporary, pre-authenticated URLs that let clients talk directly to S3.

### Upload Flow (Signed URL)

```
1. Client → App Server: "I want to upload photo.jpg (5MB)"
2. App Server generates signed PUT URL (expires in 15 min)
3. App Server → Client: "PUT to this URL: https://s3.../signed..."
4. Client → S3 directly: PUT file (5MB never touches app server)
5. S3 → App Server (via event/webhook): "Upload complete"
6. App Server saves metadata to database
```

```python
# Generate a signed upload URL
import boto3
from datetime import timedelta

s3 = boto3.client('s3')

def create_upload_url(user_id: str, filename: str, content_type: str):
    key = f"uploads/{user_id}/{uuid4()}/{filename}"
    
    url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': 'ghostdrop-files',
            'Key': key,
            'ContentType': content_type,
        },
        ExpiresIn=900,  # 15 minutes
    )
    return {"upload_url": url, "key": key}
```

### Download Flow (CDN + Signed URL)

```
1. Client → App Server: "I want to download file abc123"
2. App Server checks permissions
3. App Server generates signed CloudFront URL (expires in 1 hour)
4. Client → CDN: GET file (served from edge, never hits app server)
```

```python
# Generate a signed download URL via CloudFront
from cryptography.hazmat.primitives import serialization
import datetime

def create_download_url(file_key: str):
    expire_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    url = cloudfront_signer.generate_presigned_url(
        f"https://cdn.ghostdrop.io/{file_key}",
        date_less_than=expire_at,
    )
    return {"download_url": url}
```

---

## Concept: CDN for Downloads

70% of GhostDrop's traffic is downloads. A CDN caches files at edge locations worldwide.

```
Without CDN:
  Tokyo user → us-east-1 (200ms RTT) → download 50MB = 12 seconds

With CDN:
  Tokyo user → Tokyo edge (5ms RTT) → download 50MB = 2 seconds
```

### CDN Cache Behavior

| Content | Cache Strategy | TTL |
|---------|---------------|-----|
| Uploaded files | Cache forever (immutable keys) | 1 year |
| Thumbnails | Cache aggressively | 24 hours |
| API responses | Don't cache | 0 |
| User avatars | Cache with revalidation | 1 hour |

**Key insight**: If file keys include a hash or UUID, files are immutable. A new version gets a new key. You never need to invalidate.

```
uploads/user_4821/a3f8c2e1-photo.jpg   ← this key never changes
uploads/user_4821/b7d1e4f2-photo.jpg   ← new upload = new key
```

---

## Concept: Separating Files from App Servers

The migration plan:

```
Phase 1: New uploads go to S3 (app servers stop writing to disk)
Phase 2: Downloads check S3 first, fall back to local disk
Phase 3: Background job migrates old files from disk to S3
Phase 4: Remove local file storage code
```

**Sana**: "Can we do this without downtime?"

Yes. The dual-read approach:

```python
def get_file(file_id: str):
    file_meta = db.get_file_metadata(file_id)
    
    if file_meta.storage == "s3":
        return redirect(create_download_url(file_meta.s3_key))
    else:
        # Legacy: still on local disk, serve directly
        return send_file(f"/data/files/{file_meta.local_path}")
```

---

## GhostDrop Implementation

### S3 Bucket Configuration

```yaml
# terraform/s3.tf
resource "aws_s3_bucket" "files" {
  bucket = "ghostdrop-files-prod"
}

resource "aws_s3_bucket_versioning" "files" {
  bucket = aws_s3_bucket.files.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "files" {
  bucket = aws_s3_bucket.files.id

  rule {
    id     = "move-to-glacier"
    status = "Enabled"
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}
```

### Cost Comparison

| Metric | Before (EBS) | After (S3 + CDN) |
|--------|-------------|-------------------|
| Storage (2TB) | $200/mo | $46/mo |
| Bandwidth (10TB/mo) | $920/mo (EC2 egress) | $170/mo (CloudFront) |
| Disk full risk | 6 days | Never |
| Server dependency | Files die with server | Files independent |

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| S3 over local disk | Unlimited, shared, durable | API latency (~50ms), eventual consistency |
| Signed URLs | Offload bandwidth from app servers | URL management complexity |
| CDN | Global low-latency downloads | Cache invalidation complexity |
| Immutable keys | Never invalidate cache | Need metadata DB to map user files to keys |

---

## Why Not Just...

**"Why not use NFS/EFS shared across servers?"**
EFS costs $0.30/GB/mo (vs $0.023 for S3). At 2TB that's $600/mo vs $46/mo. EFS also has higher latency for large files and doesn't give you CDN integration.

**"Why not store files in the database?"**
PostgreSQL can store binary data (BYTEA/Large Objects), but it destroys database performance. Your 2TB of files would make backups take hours and queries compete with file I/O.

**"Why not just use CloudFront without S3?"**
CloudFront is a cache, not storage. It needs an origin. S3 is the origin. CloudFront caches what S3 stores.

---

## Exercise

A user uploads a 10GB file. Your signed URL expires in 15 minutes, but the upload takes 25 minutes on their connection.

1. What happens when the URL expires mid-upload?
2. How would you solve this? (Hint: multipart uploads)
3. What if the upload fails at 8GB — does the user start over?

<details>
<summary>Hint</summary>

S3 multipart uploads split large files into parts (5MB-5GB each). Each part gets its own signed URL. If one part fails, only that part retries. The upload can take hours — individual part URLs just need to last long enough for that part. Call CompleteMultipartUpload when all parts succeed, or AbortMultipartUpload to clean up.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Object Storage** | Flat key-value store for files (S3, GCS, MinIO) |
| **Signed URL** | Temporary authenticated URL for direct client-to-storage access |
| **CDN** | Content Delivery Network — caches content at edge locations |
| **Edge Location** | CDN server geographically close to users |
| **Immutable Key** | File key that never changes (new version = new key) |
| **Multipart Upload** | Upload large files in parallel chunks |
| **Origin** | The source server behind a CDN |
| **11 nines** | 99.999999999% durability — S3's guarantee |

---

## What Breaks Next

Files are in S3. Downloads go through CloudFront. App servers are stateless for file storage.

But the database is still on the same box as Server 1 (the original instance). It's competing for CPU and RAM with the app. And there's no backup strategy — if that disk dies, all metadata is gone.

You need to separate the database.

[← Ch 2](chapter-02-load-balancer.md) | [Ch 4 →](chapter-04-database-separation.md)
