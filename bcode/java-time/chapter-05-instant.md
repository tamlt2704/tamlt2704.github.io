# Chapter 5 — Instant: Machine Time

[← ZonedDateTime](./chapter-04-zoneddatetime.md) | [Next: Duration & Period →](./chapter-06-duration-period.md)

---

## The Problem

MeetSync runs servers in three regions: `us-east-1` (Virginia), `eu-west-1` (Ireland), and `ap-northeast-1` (Tokyo). Each server logs events with timestamps. When an incident happens, the SRE team needs to reconstruct the timeline:

```
[us-east-1]  2024-03-20 14:05:03 — Payment service timeout
[eu-west-1]  2024-03-20 19:05:01 — Database connection spike
[ap-northeast-1] 2024-03-21 04:05:02 — Cache miss rate 95%
```

Which happened first? You can't sort these — they're in different timezones. The Virginia log looks earliest but it's actually the same moment as the others. Without a common reference point, chronological ordering is impossible.

The fix: log everything as `Instant` — a point on the UTC timeline, independent of any timezone.

---

## Instant: A Point on the Timeline

`Instant` represents a single moment in time, measured as seconds (and nanoseconds) since the Unix epoch: January 1, 1970, 00:00:00 UTC.

```java
import java.time.Instant;

// Current moment
Instant now = Instant.now();
System.out.println(now); // 2024-03-20T18:05:03.123456Z (always UTC)

// From epoch
Instant epoch = Instant.EPOCH; // 1970-01-01T00:00:00Z
Instant fromSeconds = Instant.ofEpochSecond(1710957903);
Instant fromMillis = Instant.ofEpochMilli(1710957903000L);

// Parse ISO string
Instant parsed = Instant.parse("2024-03-20T18:05:03Z");
```

The `Z` suffix means Zulu time (UTC). An `Instant` is always UTC. No ambiguity.

---

## Fixing the Log Ordering Problem

```java
public record ServerEvent(String region, Instant timestamp, String message) 
    implements Comparable<ServerEvent> {
    
    @Override
    public int compareTo(ServerEvent other) {
        return this.timestamp.compareTo(other.timestamp);
    }
}

// All events stored as Instant — timezone irrelevant
List<ServerEvent> events = List.of(
    new ServerEvent("us-east-1", Instant.parse("2024-03-20T18:05:03Z"), "Payment timeout"),
    new ServerEvent("eu-west-1", Instant.parse("2024-03-20T18:05:01Z"), "DB spike"),
    new ServerEvent("ap-northeast-1", Instant.parse("2024-03-20T18:05:02Z"), "Cache miss")
);

events.stream().sorted().forEach(e ->
    System.out.println(e.timestamp() + " [" + e.region() + "] " + e.message())
);
// 2024-03-20T18:05:01Z [eu-west-1] DB spike
// 2024-03-20T18:05:02Z [ap-northeast-1] Cache miss
// 2024-03-20T18:05:03Z [us-east-1] Payment timeout
```

Now the timeline is clear. The database spike came first, then the cache miss, then the payment timeout.

---

## Epoch Conversions

Many APIs and databases work with epoch milliseconds:

```java
Instant now = Instant.now();

// To epoch values
long epochSecond = now.getEpochSecond();    // 1710957903
long epochMilli = now.toEpochMilli();       // 1710957903123

// From epoch values
Instant fromSec = Instant.ofEpochSecond(1710957903);
Instant fromMs = Instant.ofEpochMilli(1710957903123L);

// Useful for database BIGINT columns
public Instant fromDatabase(long storedMillis) {
    return Instant.ofEpochMilli(storedMillis);
}

public long toDatabase(Instant instant) {
    return instant.toEpochMilli();
}
```

---

## Measuring Elapsed Time

MeetSync tracks API response times:

```java
import java.time.Duration;

Instant start = Instant.now();

// ... do some work ...
processPayment(order);

Instant end = Instant.now();
Duration elapsed = Duration.between(start, end);

System.out.println("Took: " + elapsed.toMillis() + "ms");  // Took: 247ms
System.out.println("Took: " + elapsed);                     // PT0.247S

if (elapsed.toMillis() > 500) {
    log.warn("Slow payment processing: {}ms", elapsed.toMillis());
}
```

---

## Comparing Instants

```java
Instant created = Instant.parse("2024-03-20T10:00:00Z");
Instant modified = Instant.parse("2024-03-20T14:30:00Z");
Instant now = Instant.now();

// Comparison
System.out.println(created.isBefore(modified)); // true
System.out.println(modified.isAfter(created));  // true

// Check if something is stale (older than 1 hour)
Duration age = Duration.between(modified, now);
boolean isStale = age.toHours() > 1;

// Check if a token has expired
Instant tokenExpiry = Instant.parse("2024-03-20T18:00:00Z");
boolean expired = Instant.now().isAfter(tokenExpiry);
```

---

## Instant ↔ ZonedDateTime

`Instant` is for storage and comparison. `ZonedDateTime` is for display. Convert between them:

```java
import java.time.ZoneId;
import java.time.ZonedDateTime;

Instant eventTime = Instant.parse("2024-03-20T18:00:00Z");

// Instant → ZonedDateTime (for display to user)
ZonedDateTime inTokyo = eventTime.atZone(ZoneId.of("Asia/Tokyo"));
System.out.println(inTokyo); // 2024-03-21T03:00+09:00[Asia/Tokyo]

ZonedDateTime inNY = eventTime.atZone(ZoneId.of("America/New_York"));
System.out.println(inNY); // 2024-03-20T14:00-04:00[America/New_York]

// ZonedDateTime → Instant (for storage)
ZonedDateTime userInput = ZonedDateTime.of(2024, 3, 20, 14, 0, 0, 0,
    ZoneId.of("America/New_York"));
Instant stored = userInput.toInstant();
System.out.println(stored); // 2024-03-20T18:00:00Z
```

---

## Arithmetic with Instants

```java
Instant now = Instant.now();

// Add/subtract durations
Instant inOneHour = now.plusSeconds(3600);
Instant fiveMinutesAgo = now.minusSeconds(300);
Instant tomorrow = now.plus(Duration.ofDays(1));

// You CANNOT add months or years to an Instant
// (months have variable length — needs calendar context)
// now.plus(Period.ofMonths(1)); // UnsupportedTemporalTypeException!
```

`Instant` only understands fixed durations (seconds, millis, nanos). For calendar math, convert to `ZonedDateTime` first.

---

## The MeetSync Timestamp Pattern

```java
public class AuditLog {
    private final Instant createdAt;
    private final Instant updatedAt;
    private final String action;
    private final String userId;

    public AuditLog(String action, String userId) {
        this.createdAt = Instant.now();
        this.updatedAt = this.createdAt;
        this.action = action;
        this.userId = userId;
    }

    public String displayFor(ZoneId viewerZone) {
        DateTimeFormatter fmt = DateTimeFormatter
            .ofPattern("yyyy-MM-dd HH:mm:ss z")
            .withZone(viewerZone);
        return fmt.format(this.createdAt);
    }
}
```

Store as `Instant`. Display in the viewer's timezone. Always.

---

## What You Learned

- `Instant` is a point on the UTC timeline — no timezone ambiguity
- Use it for timestamps, event ordering, elapsed time measurement
- `toEpochMilli()` / `ofEpochMilli()` bridges to database BIGINT storage
- `Duration.between(start, end)` measures elapsed time precisely
- Convert to `ZonedDateTime` for display: `instant.atZone(userZone)`
- Convert from `ZonedDateTime` for storage: `zdt.toInstant()`
- You cannot add months/years to an `Instant` — use `ZonedDateTime` for calendar math
- Log everything as `Instant` and your multi-region timeline will always sort correctly

---

*Next up: "Add 1 month" vs "add 30 days" — they're not the same thing. [Chapter 6](./chapter-06-duration-period.md) explains `Duration` and `Period`.*
