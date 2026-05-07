# Chapter 14: Safe Deployments

[← Ch 13](chapter-13-consistency.md) | [Ch 15 →](chapter-15-observability.md)

---

## The Crisis

Wednesday, week three. Podcast in 2 days.

**Omar** (Slack, 4:15 PM):
> Last deploy caused a 4-minute outage. Here's what happened:
> 1. Database migration added a `file_type` column
> 2. New code deployed to Server 1 (expects `file_type`)
> 3. Server 2 still running old code (doesn't know about `file_type`)
> 4. Migration ran ALTER TABLE — locked the table for 90 seconds
> 5. All queries queued behind the lock → timeouts → 500s

**Sana**:
> We can't have a 4-minute outage on podcast day. We need to deploy the final performance fixes without any downtime.

**Amir**:
> What's our rollback plan if the podcast-day deploy goes wrong?

**You**:
> Right now? Revert the git commit and redeploy. That takes 12 minutes. We need instant rollback.

---

## Concept: Deployment Strategies

### 1. Blue-Green Deployment

Run two identical environments. Switch traffic instantly.

```
Before deploy:
┌──────────┐     ┌──────────────────┐
│    LB    │────→│  BLUE (current)  │  ← serving traffic
└──────────┘     └──────────────────┘
                 ┌──────────────────┐
                 │  GREEN (idle)    │  ← ready for new version
                 └──────────────────┘

After deploy:
┌──────────┐     ┌──────────────────┐
│    LB    │     │  BLUE (old)      │  ← idle (rollback target)
└──────────┘     └──────────────────┘
      │          ┌──────────────────┐
      └─────────→│  GREEN (new)     │  ← serving traffic
                 └──────────────────┘

Rollback: Switch LB back to BLUE (instant)
```

**Pros**: Instant rollback, zero downtime, full environment testing before switch
**Cons**: 2x infrastructure cost during deploy, database must be compatible with both versions

### 2. Canary Deployment

Route a small percentage of traffic to the new version. Monitor. Gradually increase.

```
Step 1: 5% → new version, 95% → old version
Step 2: Monitor errors, latency for 10 minutes
Step 3: 25% → new, 75% → old
Step 4: Monitor again
Step 5: 100% → new

If errors spike at any step: route 100% back to old (instant)
```

```
┌──────────┐     ┌──────────────────┐
│    LB    │──95%│  v2.3 (current)  │
│          │     └──────────────────┘
│          │     ┌──────────────────┐
│          │──5%→│  v2.4 (canary)   │
└──────────┘     └──────────────────┘
```

**Pros**: Low risk (only 5% of users affected if broken), real production testing
**Cons**: Slower rollout, need traffic splitting, two versions running simultaneously

### 3. Rolling Deployment

Update servers one at a time. Old and new versions coexist briefly.

```
t=0:  [v1] [v1] [v1] [v1]
t=1:  [v2] [v1] [v1] [v1]  ← Server 1 updated
t=2:  [v2] [v2] [v1] [v1]  ← Server 2 updated
t=3:  [v2] [v2] [v2] [v1]  ← Server 3 updated
t=4:  [v2] [v2] [v2] [v2]  ← Complete
```

**Pros**: No extra infrastructure, gradual
**Cons**: Mixed versions during rollout, slower rollback (must roll forward or back one by one)

### GhostDrop's Choice

**Canary** for the podcast deploy. Blue-green is too expensive (2x servers). Rolling is too slow to rollback. Canary gives us instant rollback with minimal risk.

---

## Concept: Feature Flags

Decouple deployment from release. Deploy code that's hidden behind a flag.

```python
# feature_flags.py
import launchdarkly_client as ld

def get_file_list(user_id: str):
    # New optimized query behind a flag
    if feature_flags.is_enabled("optimized_file_list", user_id):
        return get_files_v2(user_id)  # New code
    else:
        return get_files_v1(user_id)  # Old code

# Rollout plan:
# Day 1: Enable for internal team (10 users)
# Day 2: Enable for 5% of users
# Day 3: Enable for 50%
# Day 4: Enable for 100%
# Day 7: Remove flag and old code
```

### Feature Flag Use Cases

| Use Case | Example |
|----------|---------|
| Gradual rollout | New upload flow to 10% of users |
| Kill switch | Disable expensive feature during traffic spike |
| A/B testing | Show different UI to different cohorts |
| Ops toggle | Enable debug logging without redeploy |
| User targeting | Beta features for pro users only |

```python
# Kill switch for podcast day
@app.get("/api/files/{file_id}/preview")
def get_preview(file_id: str):
    if not feature_flags.is_enabled("file_previews"):
        return {"preview": None, "message": "Previews temporarily unavailable"}
    
    return generate_preview(file_id)  # CPU-intensive
```

---

## Concept: Database Migrations During Deploy

The hardest part of zero-downtime deploys: schema changes.

### The Problem

```
Old code expects: SELECT id, name, size FROM files
New code expects: SELECT id, name, size, file_type FROM files

If you add the column and deploy new code simultaneously:
- Old servers crash (unexpected column? no — they just don't use it)
- Actually: old code works fine with extra columns
- But what if you REMOVE a column? Old code breaks.
```

### Safe Migration Pattern: Expand and Contract

```
Phase 1: EXPAND (add new column, keep old)
  - Add `file_type` column (nullable, with default)
  - Deploy new code that writes to BOTH old and new columns
  - Old code still works (ignores new column)

Phase 2: MIGRATE (backfill data)
  - Background job fills `file_type` for existing rows
  - Both old and new code work

Phase 3: CONTRACT (remove old column)
  - Deploy code that only uses new column
  - Drop old column (only after all servers run new code)
```

### Non-Locking Migrations

```sql
-- BAD: Locks table for duration (minutes on large tables)
ALTER TABLE files ADD COLUMN file_type VARCHAR(50) NOT NULL DEFAULT 'unknown';

-- GOOD: Add nullable column (instant, no lock)
ALTER TABLE files ADD COLUMN file_type VARCHAR(50);

-- GOOD: Add default separately (no lock in Postgres 11+)
ALTER TABLE files ALTER COLUMN file_type SET DEFAULT 'unknown';

-- GOOD: Create index concurrently (no lock)
CREATE INDEX CONCURRENTLY idx_files_type ON files(file_type);
```

---

## Concept: Rollback Strategies

| Strategy | Speed | Complexity | Data Risk |
|----------|-------|-----------|-----------|
| **LB switch** (blue-green) | Instant | Low | None (old env intact) |
| **Traffic shift** (canary) | Instant | Low | None |
| **Redeploy old version** | 5-15 min | Medium | None |
| **Database rollback** | Dangerous | High | Data loss possible |
| **Feature flag off** | Instant | Low | None |

### GhostDrop's Rollback Plan for Podcast Day

```
Priority 1: Feature flags OFF (instant, no deploy needed)
Priority 2: Canary → 0% new version (instant traffic shift)
Priority 3: Redeploy previous version (12 minutes)
Priority 4: Database restore from snapshot (last resort, 30+ minutes)
```

---

## GhostDrop Implementation

### Canary Deploy Pipeline

```yaml
# .github/workflows/deploy.yml
name: Canary Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    steps:
      - name: Build and push image
        run: |
          docker build -t ghostdrop:${{ github.sha }} .
          docker push $ECR_REPO:${{ github.sha }}
      
      - name: Deploy canary (5%)
        run: |
          aws ecs update-service \
            --service ghostdrop-canary \
            --task-definition ghostdrop:${{ github.sha }}
          # ALB weighted target group: 5% to canary
          aws elbv2 modify-rule --rule-arn $RULE_ARN \
            --actions '[{"Type":"forward","ForwardConfig":{"TargetGroups":[
              {"TargetGroupArn":"'$STABLE_TG'","Weight":95},
              {"TargetGroupArn":"'$CANARY_TG'","Weight":5}
            ]}}]'
      
      - name: Monitor canary (10 minutes)
        run: |
          python scripts/monitor_canary.py \
            --duration 600 \
            --error-threshold 1.0 \
            --latency-threshold-p99 500
      
      - name: Promote to 100% (or rollback)
        run: |
          if [ "$CANARY_HEALTHY" = "true" ]; then
            aws elbv2 modify-rule --rule-arn $RULE_ARN \
              --actions '[{"Type":"forward","ForwardConfig":{"TargetGroups":[
                {"TargetGroupArn":"'$CANARY_TG'","Weight":100}
              ]}}]'
          else
            echo "Canary failed! Rolling back."
            aws elbv2 modify-rule --rule-arn $RULE_ARN \
              --actions '[{"Type":"forward","ForwardConfig":{"TargetGroups":[
                {"TargetGroupArn":"'$STABLE_TG'","Weight":100}
              ]}}]'
          fi
```

### Canary Health Monitor

```python
# scripts/monitor_canary.py
def check_canary_health(duration_seconds, error_threshold, latency_threshold):
    start = time.time()
    while time.time() - start < duration_seconds:
        metrics = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {"Id": "errors", "MetricStat": {...}},
                {"Id": "latency_p99", "MetricStat": {...}},
            ]
        )
        
        error_rate = metrics["errors"]
        p99_latency = metrics["latency_p99"]
        
        if error_rate > error_threshold:
            print(f"ERROR RATE {error_rate}% > {error_threshold}%")
            return False
        
        if p99_latency > latency_threshold:
            print(f"P99 LATENCY {p99_latency}ms > {latency_threshold}ms")
            return False
        
        time.sleep(30)
    
    return True
```

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Canary deploys | Low risk, instant rollback | Slower rollout (10+ min) |
| Feature flags | Decouple deploy from release | Flag management overhead, tech debt |
| Expand-contract migrations | Zero-downtime schema changes | 3 deploys instead of 1 |
| Automated canary monitoring | Catches issues without human | Must define good health metrics |

---

## Why Not Just...

**"Why not just deploy at 3 AM when nobody's using it?"**
GhostDrop has global users. There's no quiet time. Also, deploying when you're tired increases error risk.

**"Why not use database transactions to make migrations atomic?"**
DDL statements (ALTER TABLE) in PostgreSQL acquire locks. Even in a transaction, the lock blocks other queries. The expand-contract pattern avoids locks entirely.

**"Why not just test more before deploying?"**
Testing catches bugs in code logic. It doesn't catch performance issues at scale, infrastructure misconfigurations, or interactions with real production data. Canary deploys test in production with minimal blast radius.

---

## Exercise

GhostDrop needs to rename the `files.name` column to `files.display_name` (to distinguish from the S3 key). This is a breaking change — old code reads `name`, new code reads `display_name`.

Design a zero-downtime migration plan:
1. How many deploys does this require?
2. What does each deploy do?
3. What's the rollback plan at each stage?

<details>
<summary>Hint</summary>

Three deploys: (1) Add `display_name` column, deploy code that writes to BOTH `name` and `display_name`, reads from `name`. (2) Backfill `display_name` from `name` for existing rows. Deploy code that reads from `display_name` (falls back to `name`). (3) After all rows backfilled and all servers on new code: drop `name` column. Rollback at any stage: revert to previous deploy (old column still exists and has data).
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Blue-Green** | Two environments, instant switch |
| **Canary** | Small % of traffic to new version, gradual increase |
| **Rolling** | Update servers one at a time |
| **Feature Flag** | Runtime toggle to enable/disable features |
| **Expand-Contract** | Add new schema, migrate data, remove old schema |
| **Zero-Downtime Deploy** | Deploy without any user-visible interruption |
| **Rollback** | Reverting to the previous working version |
| **Kill Switch** | Feature flag that disables a feature instantly |

---

## What Breaks Next

Deployment strategy is solid. Canary deploys with automated monitoring. Feature flags for instant rollback. Zero-downtime migrations.

But Thursday night, 36 hours before the podcast, Omar asks: "How will we know if something is wrong during the podcast? Our monitoring shows server metrics, but we don't have end-to-end visibility. If uploads are slow for users in Europe, will we even know?"

You need observability.

[← Ch 13](chapter-13-consistency.md) | [Ch 15 →](chapter-15-observability.md)
