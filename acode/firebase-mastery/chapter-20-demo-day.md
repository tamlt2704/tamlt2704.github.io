# Chapter 20: Demo Day — "The Investor Asks Questions"

[← Chapter 19: Emulator Suite](chapter-19-emulator-suite.md)

---

## The Scene

Demo day. You've shipped SnapTask in 5 weeks. Real-time collaborative task management. No backend team. No DevOps. Just Firebase.

The investor, **Sarah**, watches the demo. Tasks update in real-time across devices. File attachments work. Push notifications fire. Offline mode handles the subway scenario. She's impressed.

Then the questions start.

---

## "How does this scale?"

**Sarah:** "You have 50 users now. What happens at 50,000?"

**You:**

Firestore scales automatically. It's the same infrastructure that runs Google's own products. There's no server to upgrade, no database to shard, no load balancer to configure.

Specific numbers:
- Firestore handles 10,000 writes/second per database (soft limit, can be increased)
- Reads scale horizontally — no practical limit
- Each document can be updated ~1 time/second (per-document limit)
- Real-time listeners scale to millions of concurrent connections

What we'd need to change at 50K users:
- Distributed counters for high-write fields (likes, views)
- More aggressive pagination (currently loading 50 tasks, might need 20)
- CDN for static assets (Firebase Hosting already does this)
- Possibly move to multi-region for global users

What we DON'T need to change:
- Architecture
- Security rules
- Data model (already denormalized for our query patterns)
- Deployment process

---

## "What about security?"

**Sarah:** "How do you prevent one user from reading another team's data?"

**You:**

Security Rules. Every client request passes through a declarative rule engine before touching the database. Let me show you:

```
match /teams/{teamId}/tasks/{taskId} {
  allow read: if request.auth != null
    && request.auth.uid in get(/databases/$(database)/documents/teams/$(teamId)).data.members;
}
```

This means:
1. User must be authenticated (signed in)
2. User's ID must be in the team's `members` array
3. If either condition fails, the read is denied — no data returned

We also validate writes:
- Users can't impersonate others (`createdBy == request.auth.uid`)
- Status must be a valid enum value
- Title length is capped at 200 characters
- Immutable fields can't be changed after creation

We test these rules in CI with automated tests that verify both allowed and denied access patterns.

---

## "What's your monthly cost at scale?"

**Sarah:** "Give me a number. 50,000 users."

**You:**

Let me break it down:

```
50,000 users × 3 sessions/day × 100 reads/session × 30 days
= 450,000,000 reads/month
= $270/month (Firestore reads)

50,000 users × 3 sessions/day × 10 writes/session × 30 days
= 45,000,000 writes/month
= $81/month (Firestore writes)

Storage: ~50 GB = $9/month
Bandwidth: ~200 GB = $24/month
Functions: ~5M invocations = $2/month
Hosting: ~100 GB = $15/month

Total: ~$400/month for 50,000 active users
```

That's $0.008 per user per month. Compare to running your own infrastructure: 3 servers, a managed database, a load balancer, DevOps engineer time — easily $2,000-5,000/month for the same scale.

---

## "What's the vendor lock-in risk?"

**Sarah:** "What if Google raises prices? What if Firebase shuts down?"

**You:**

Real talk: there is lock-in. Our data model, security rules, and real-time listeners are Firebase-specific. Migration would take 2-3 months of engineering.

Mitigations:
1. **Data is exportable** — Firestore data can be exported to BigQuery or GCS at any time
2. **Business logic is in Cloud Functions** — standard Node.js, portable to any serverless platform
3. **Frontend is React** — the Firebase SDK is a thin layer we could swap
4. **Auth supports standard protocols** — Firebase Auth uses standard JWTs

The realistic risk: Firebase has been around since 2012 (acquired by Google in 2014). It's a core Google Cloud product. The risk of shutdown is low. Price increases are possible but historically modest.

The tradeoff: we shipped in 5 weeks instead of 5 months. That speed-to-market advantage is worth the lock-in risk at this stage.

---

## "What can't you do with this architecture?"

**Sarah:** "What are the limitations?"

**You:**

Honest limitations:

1. **No complex queries** — no JOINs, no GROUP BY, no subqueries. We denormalize instead.
2. **No full-text search** — we'd need Algolia or Typesense for search functionality.
3. **1 write/second per document** — a single document can't be updated more than once per second. We use distributed counters for hot paths.
4. **1 MB document size limit** — large documents must be split.
5. **No server-side rendering** — Firebase Hosting serves static files. We'd need Cloud Run for SSR.
6. **Limited analytics** — no built-in query analytics. We'd add BigQuery export for business intelligence.

None of these are blockers for SnapTask. They'd become relevant if we pivoted to a data-heavy analytics product.

---

## "Show me the security audit"

**Sarah:** "Have you done a security review?"

**You:**

Here's our security posture:

### Authentication
- ✅ Firebase Auth with email verification
- ✅ Google OAuth for social login
- ✅ Session persistence in IndexedDB (not cookies)
- ✅ Automatic token refresh (1-hour expiry)
- ✅ Rate limiting on auth attempts (Firebase built-in)

### Authorization
- ✅ Security Rules on every collection
- ✅ Team membership verified on every read/write
- ✅ No `allow read, write: if true` anywhere
- ✅ Write validation (field types, required fields, enums)
- ✅ Immutable fields protected (createdBy, createdAt)
- ✅ Automated rule tests in CI

### Data Protection
- ✅ All data encrypted at rest (Google default)
- ✅ All connections over HTTPS/TLS
- ✅ No secrets in client code (API key is not a secret)
- ✅ Storage rules enforce file size and type limits
- ✅ Download URLs have access tokens (revocable)

### Operational Security
- ✅ Emulator for development (no production access during dev)
- ✅ Billing alerts at $10, $50, $100
- ✅ Admin SDK only in Cloud Functions (not client)
- ✅ No raw database access from client (all through SDK + rules)

### What We'd Add for Enterprise
- Multi-factor authentication
- IP allowlisting (via Cloud Armor)
- Audit logging (via Cloud Logging)
- SOC 2 compliance documentation (Firebase is SOC 2 certified)
- Data residency controls (multi-region configuration)

---

## "What's your deployment process?"

**Sarah:** "How do you ship updates?"

**You:**

```bash
# One command deploys everything
firebase deploy
```

In practice, our CI/CD pipeline:

```yaml
# On merge to main:
1. Run tests with emulators (firebase emulators:exec "npm test")
2. Build frontend (npm run build)
3. Deploy indexes first (firebase deploy --only firestore:indexes)
4. Wait 5 minutes for indexes to build
5. Deploy rules (firebase deploy --only firestore:rules,storage)
6. Deploy functions (firebase deploy --only functions)
7. Deploy hosting (firebase deploy --only hosting)
```

Rollback: Firebase Hosting keeps previous versions. One click in the console reverts to any previous deploy. Functions can be rolled back by redeploying the previous version.

Zero-downtime deployments. No maintenance windows. No blue-green complexity.

---

## "What's next on the roadmap?"

**Sarah:** "If I invest, what do you build in the next 3 months?"

**You:**

| Priority | Feature | Firebase Service |
|----------|---------|-----------------|
| 1 | Team workspaces (multi-team) | Firestore data model |
| 2 | Full-text search | Algolia + Cloud Functions |
| 3 | Activity feed | Firestore + denormalization |
| 4 | File previews (PDF, images) | Storage + Cloud Functions |
| 5 | Integrations (Slack, email) | Cloud Functions + webhooks |
| 6 | Analytics dashboard | BigQuery export |
| 7 | Mobile app (iOS/Android) | Same Firebase backend, React Native |

The mobile app is the key insight: **the entire backend is already built**. Firebase SDKs work on iOS, Android, and web. The mobile app just needs a new frontend — same auth, same database, same real-time sync, same push notifications.

---

## The Pitch Summary

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  SnapTask: Built in 5 weeks. No backend team.               │
│                                                              │
│  ✅ Real-time collaboration (Firestore listeners)            │
│  ✅ Works offline (persistence + sync)                       │
│  ✅ Push notifications (FCM)                                 │
│  ✅ File attachments (Storage)                               │
│  ✅ Secure (Security Rules, tested in CI)                    │
│  ✅ Scales automatically (serverless)                        │
│  ✅ $400/month at 50K users                                  │
│  ✅ Mobile-ready (same backend)                              │
│  ✅ One-command deploy                                       │
│                                                              │
│  Tradeoffs accepted:                                         │
│  • Vendor lock-in (mitigated by data export)                │
│  • No complex queries (mitigated by denormalization)        │
│  • No full-text search (will add Algolia)                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## What You've Learned

Over 20 chapters, you built a production app with:

| Chapter | Service | Key Concept |
|---------|---------|-------------|
| 1 | Hosting, CLI | Project setup, emulators |
| 2 | Auth | Sign in, session, onAuthStateChanged |
| 3 | Firestore | Documents, collections, CRUD |
| 4 | Firestore | Real-time listeners, onSnapshot |
| 5 | Security Rules | Access control, data validation |
| 6 | Storage | File upload, download, storage rules |
| 7 | Firestore | Queries, filters, operators |
| 8 | Firestore | Composite indexes, limitations |
| 9 | Functions | Triggers, events, callable |
| 10 | FCM | Push notifications, tokens, topics |
| 11 | Firestore | NoSQL data modeling, denormalization |
| 12 | Firestore | Offline persistence, conflict resolution |
| 13 | Firestore | Aggregation, distributed counters |
| 14 | Firestore | Transactions, batched writes |
| 15 | Firestore | Cursor-based pagination |
| 16 | Functions | Cold starts, optimization |
| 17 | All | Cost optimization, billing |
| 18 | Functions | REST API, Express, auth middleware |
| 19 | Emulators | Local dev, testing, CI |
| 20 | All | Architecture review, scaling, security |

---

## The Traps You Avoided

1. ~~`allow read, write: if true`~~ → Proper security rules from Chapter 5
2. ~~Reading entire collections~~ → Pagination and limits from Chapter 15
3. ~~No offline support~~ → Persistence enabled from Chapter 12
4. ~~$30K bill~~ → Cost optimization from Chapter 17
5. ~~Unindexed queries in production~~ → Index management from Chapter 8
6. ~~Cold start latency~~ → minInstances and optimization from Chapter 16
7. ~~Testing against production~~ → Emulator Suite from Chapter 19
8. ~~N+1 reads~~ → Denormalization from Chapter 11

---

## Final Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SnapTask (Production)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  React SPA ──── Firebase Hosting (CDN, HTTPS, global)                   │
│      │                                                                   │
│      ├── Auth (email, Google, session persistence)                       │
│      ├── Firestore (real-time, offline, security rules)                 │
│      ├── Storage (files, thumbnails, access control)                    │
│      └── FCM (push notifications, topics)                               │
│                                                                          │
│  Cloud Functions                                                         │
│      ├── Triggers (onTaskAssigned, onCommentCreated)                    │
│      ├── Scheduled (dailyDigest, cleanup)                               │
│      ├── Callable (joinTeam, createTeam)                                │
│      └── HTTP API (Express, partner integrations)                       │
│                                                                          │
│  Security Rules                                                          │
│      ├── Firestore (team membership, data validation)                   │
│      └── Storage (file size, content type, team access)                 │
│                                                                          │
│  CI/CD                                                                   │
│      ├── Emulator tests (rules, functions)                              │
│      └── firebase deploy (one command, zero downtime)                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

No servers. No Docker. No Kubernetes. No DevOps hire. Just Firebase.

---

Sarah nods. "I'm in. Let's talk terms."

Lena grins. Marco high-fives you under the table.

You shipped it. 🚀

---

[← Chapter 19: Emulator Suite](chapter-19-emulator-suite.md)
