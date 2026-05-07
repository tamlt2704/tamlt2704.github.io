# Chapter 17: Cost Optimization — "$200 Bill with 50 Users"

[← Chapter 16: Cold Starts](chapter-16-cold-starts.md) | [Chapter 18: REST API →](chapter-18-rest-api.md)

---

## The Task

Lena: "Our Firebase bill is $200 this month. We have 50 users. If we get 5,000 users at launch, that's $20,000/month. We'll be dead before demo day."

Time to understand what costs money and how to fix it.

---

## Firebase Pricing Model

| Service | Free Tier (Spark) | Pay-as-you-go (Blaze) |
|---------|-------------------|----------------------|
| Firestore reads | 50K/day | $0.06 per 100K |
| Firestore writes | 20K/day | $0.18 per 100K |
| Firestore deletes | 20K/day | $0.02 per 100K |
| Firestore storage | 1 GB | $0.18/GB/month |
| Storage (files) | 5 GB | $0.026/GB/month |
| Storage bandwidth | 1 GB/day | $0.12/GB |
| Functions invocations | 2M/month | $0.40 per million |
| Functions compute | 400K GB-seconds | $0.0000025/GB-second |
| Hosting bandwidth | 10 GB/month | $0.15/GB |
| Auth | Free (most methods) | Free |

The expensive ones: **Firestore reads** and **Storage bandwidth**.

---

## Finding the Problem

Firebase console → Usage and billing → Usage tab.

Common culprits for a $200 bill with 50 users:

1. **Uncontrolled listeners** — reading entire collections on every page load
2. **No pagination** — loading 1,000 documents when showing 20
3. **Redundant reads** — fetching the same data multiple times
4. **Large file downloads** — serving unoptimized images
5. **Runaway Cloud Functions** — infinite loops or excessive triggers

---

## Fix 1: Limit Your Reads

```typescript
// ❌ Reads ALL tasks every time the component mounts
onSnapshot(collection(db, "teams", teamId, "tasks"), callback);
// 1,000 tasks × 50 users × 10 page loads/day = 500,000 reads/day = $0.30/day

// ✅ Read only what's visible
onSnapshot(
  query(
    collection(db, "teams", teamId, "tasks"),
    where("status", "in", ["todo", "in_progress"]),
    orderBy("updatedAt", "desc"),
    limit(50)
  ),
  callback
);
// 50 tasks × 50 users × 10 page loads/day = 25,000 reads/day = $0.015/day
```

---

## Fix 2: Cache Aggressively

Firestore's offline persistence IS your cache. Once a document is read, subsequent reads come from the local cache (free):

```typescript
// First read: hits server (billed)
const doc = await getDoc(taskRef);

// Second read: from cache (free) if persistence is enabled
const doc2 = await getDoc(taskRef);
// doc2.metadata.fromCache === true
```

For data that rarely changes (team settings, user profiles), read once and let the cache handle it.

---

## Fix 3: Use getDoc Instead of onSnapshot for Static Data

```typescript
// ❌ Real-time listener for data that changes once a month
onSnapshot(doc(db, "teams", teamId), callback);
// Keeps a connection open, re-reads on any change

// ✅ One-time read for rarely-changing data
const teamDoc = await getDoc(doc(db, "teams", teamId));
// One read, done. Refresh manually when needed.
```

Use `onSnapshot` only for data that changes frequently and must update in real-time (task status, comments). Use `getDoc` for everything else.

---

## Fix 4: Denormalize to Reduce Reads

```typescript
// ❌ To show a task list with assignee names: 1 + N reads
const tasks = await getDocs(tasksQuery); // N reads
for (const task of tasks.docs) {
  const user = await getDoc(doc(db, "users", task.data().assignee)); // +1 read each
}
// 50 tasks = 51 reads

// ✅ Embed assignee name on the task document: 1 read for N tasks
// Task document: { ..., assignee: { uid: "x", displayName: "Lena" } }
const tasks = await getDocs(tasksQuery); // N reads, no extra fetches
// 50 tasks = 50 reads (saved 50 reads per page load)
```

---

## Fix 5: Optimize Images

Storage bandwidth is expensive. A 5MB photo served to 50 users = 250MB bandwidth.

```typescript
// Use Cloud Functions to generate thumbnails on upload
export const generateThumbnail = onObjectFinalized(async (event) => {
  const filePath = event.data.name;
  if (filePath.includes("thumb_")) return; // already a thumbnail

  const bucket = getStorage().bucket(event.data.bucket);
  const file = bucket.file(filePath);

  // Download, resize, upload thumbnail
  const sharp = await import("sharp");
  const [buffer] = await file.download();
  const thumbnail = await sharp(buffer).resize(200, 200).jpeg({ quality: 70 }).toBuffer();

  const thumbPath = `thumb_${filePath}`;
  await bucket.file(thumbPath).save(thumbnail, {
    metadata: { contentType: "image/jpeg" },
  });
});
```

Serve thumbnails in lists, full images only on detail views.

---

## Fix 6: Set Billing Alerts

Firebase console → Usage and billing → Budget alerts:

- Alert at $10 (something's wrong)
- Alert at $50 (investigate immediately)
- Alert at $100 (shut it down)

You can also set a budget cap on the Google Cloud Console to automatically disable billing (nuclear option — takes your app offline).

---

## Fix 7: Use Security Rules to Prevent Abuse

Without proper rules, a malicious user could:

```typescript
// Read your entire database
const everything = await getDocs(collectionGroup(db, "tasks"));
// Millions of reads, billed to YOU
```

Security rules prevent unauthorized reads. They're not just for security — they're for cost control.

---

## Fix 8: Batch Reads with getAll (Admin SDK)

In Cloud Functions, batch multiple reads:

```typescript
// ❌ Sequential reads (slow + more overhead)
const user1 = await db.doc("users/uid1").get();
const user2 = await db.doc("users/uid2").get();
const user3 = await db.doc("users/uid3").get();

// ✅ Batch read (one round-trip)
const [user1, user2, user3] = await db.getAll(
  db.doc("users/uid1"),
  db.doc("users/uid2"),
  db.doc("users/uid3")
);
```

Same number of billed reads, but faster execution = less compute time = lower function costs.

---

## Fix 9: Clean Up Unused Data

Archived tasks from 6 months ago? Delete them. Old file attachments? Remove them.

```typescript
// Scheduled cleanup function
export const cleanupOldData = onSchedule("every day 03:00", async () => {
  const sixMonthsAgo = new Date();
  sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

  // Delete old archived tasks
  const oldTasks = await db
    .collectionGroup("tasks")
    .where("status", "==", "archived")
    .where("updatedAt", "<", sixMonthsAgo)
    .limit(500)
    .get();

  const batch = db.batch();
  oldTasks.docs.forEach((doc) => batch.delete(doc.ref));
  await batch.commit();

  console.log(`Deleted ${oldTasks.size} old tasks`);
});
```

---

## Cost Estimation Formula

```
Monthly cost ≈
  (daily_active_users × reads_per_session × sessions_per_day × 30) / 100,000 × $0.06
  + (daily_writes × 30) / 100,000 × $0.18
  + storage_GB × $0.18
  + bandwidth_GB × $0.12
```

For SnapTask with 50 users:
- 50 users × 200 reads/session × 3 sessions/day × 30 = 900,000 reads/month = $0.54
- 50 users × 20 writes/session × 3 sessions/day × 30 = 90,000 writes/month = $0.16
- Storage: 2 GB = $0.36
- Bandwidth: 5 GB = $0.60

**Expected: ~$1.66/month**

If you're paying $200, something is very wrong. Check for:
- Listeners on large collections without `limit()`
- Cloud Functions in infinite loops
- Unoptimized images served repeatedly

---

## The Free Tier Strategy

The Spark (free) plan gives you:
- 50K reads/day = 1.5M reads/month
- 20K writes/day = 600K writes/month
- 1 GB Firestore storage
- 5 GB file storage

For a startup with <100 users, you can often stay on the free tier entirely. Switch to Blaze only when you need Cloud Functions or exceed limits.

---

## Common Mistakes

### 1. Listeners without limit()

The #1 cost killer. A listener on a collection with 10,000 documents reads all 10,000 on first load, then re-reads changed documents. Always use `limit()`.

### 2. Not using the emulator during development

Every read/write during development against production counts toward billing. Use the emulator — it's free and local.

### 3. Storing large files without compression

A 10MB PNG that could be a 200KB JPEG costs 50x more in bandwidth.

### 4. No billing alerts

You won't know about a cost spike until the monthly bill arrives. Set alerts at low thresholds.

---

## Quick Reference

```
────────────────────────────────────────┬──────────────────────────────────────
Strategy                                │ Savings
────────────────────────────────────────┼──────────────────────────────────────
limit() on all queries                  │ 10-100x fewer reads
Denormalize (embed related data)        │ Eliminate N+1 reads
getDoc for static data                  │ No persistent connection
Offline persistence (cache)             │ Repeat reads are free
Thumbnail images                        │ 10-50x less bandwidth
Billing alerts                          │ Catch problems early
Security rules                          │ Prevent abuse reads
Scheduled cleanup                       │ Reduce storage costs
Emulator for development                │ Zero dev costs
────────────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lena: "A partner wants to integrate with SnapTask. They need an API — REST endpoints they can call from their backend."

Cloud Functions as a REST API. Callable functions vs HTTP functions.

---

[← Chapter 16: Cold Starts](chapter-16-cold-starts.md) | [Chapter 18: REST API →](chapter-18-rest-api.md)
