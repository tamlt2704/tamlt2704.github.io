# Chapter 3 — LocalDateTime: The Naive Pair

[← LocalTime](./chapter-02-localtime.md) | [Next: ZonedDateTime →](./chapter-04-zoneddatetime.md)

---

## The Problem

MeetSync stores appointments as `LocalDateTime`. Everything works perfectly — until the ops team migrates the server from `us-east-1` (New York) to `eu-west-1` (Ireland).

```java
// Stored in database
LocalDateTime appointment = LocalDateTime.of(2024, 3, 20, 14, 0); // "2:00 PM"
```

Before migration: server in New York, `LocalDateTime.now()` returns Eastern time. The 2:00 PM appointment displays correctly for New York users.

After migration: server in Ireland, `LocalDateTime.now()` returns GMT. That same 2:00 PM appointment now appears to be at 2:00 PM GMT — which is 10:00 AM Eastern. Users see their meetings shifted by 4-5 hours.

**The root cause:** `LocalDateTime` has no timezone. It's just a date and time floating in space. It means whatever timezone the reader assumes.

---

## What LocalDateTime Actually Is

`LocalDateTime` is simply a `LocalDate` + `LocalTime` glued together. Nothing more.

```java
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.LocalDateTime;

// Three ways to create
LocalDateTime dt1 = LocalDateTime.of(2024, 3, 20, 14, 30);
LocalDateTime dt2 = LocalDateTime.of(
    LocalDate.of(2024, 3, 20),
    LocalTime.of(14, 30)
);
LocalDateTime dt3 = LocalDateTime.parse("2024-03-20T14:30:00");

System.out.println(dt1); // 2024-03-20T14:30
```

It answers the question: "What does the calendar on the wall and the clock on the wall show?" But it does NOT answer: "What moment in time is this?"

---

## When LocalDateTime Is Correct

It's not useless — it's correct for things that are inherently local:

```java
// ✓ "The store opens at 9 AM" (in whatever timezone the store is in)
LocalDateTime storeOpening = LocalDateTime.of(2024, 3, 20, 9, 0);

// ✓ "The exam starts at 2 PM local time" (each testing center, their own clock)
LocalDateTime examStart = LocalDateTime.of(2024, 6, 15, 14, 0);

// ✓ Alarm clock: "Wake me at 7:00 AM" (wherever I am)
LocalDateTime alarm = LocalDateTime.of(2024, 3, 21, 7, 0);
```

---

## When LocalDateTime Is WRONG

```java
// ✗ Meeting between people in different timezones
LocalDateTime meeting = LocalDateTime.of(2024, 3, 20, 14, 0);
// 2 PM... where? New York? London? Tokyo?

// ✗ Event timestamps (when did this happen?)
LocalDateTime createdAt = LocalDateTime.now();
// If server moves, this becomes meaningless

// ✗ Scheduling across regions
LocalDateTime deadline = LocalDateTime.of(2024, 3, 31, 23, 59);
// Deadline in which timezone?
```

---

## Combining Date and Time

```java
LocalDate date = LocalDate.of(2024, 3, 20);
LocalTime time = LocalTime.of(14, 30);

// Combine
LocalDateTime combined = LocalDateTime.of(date, time);
LocalDateTime alsoWorks = date.atTime(time);
LocalDateTime withHourMinute = date.atTime(14, 30);

// Extract
LocalDate extractedDate = combined.toLocalDate();  // 2024-03-20
LocalTime extractedTime = combined.toLocalTime();  // 14:30
```

---

## Arithmetic Works the Same Way

```java
LocalDateTime now = LocalDateTime.of(2024, 3, 20, 14, 30);

LocalDateTime later = now.plusHours(3);        // 2024-03-20T17:30
LocalDateTime tomorrow = now.plusDays(1);      // 2024-03-21T14:30
LocalDateTime nextWeek = now.plusWeeks(1);     // 2024-03-27T14:30

// Crosses midnight naturally
LocalDateTime lateNight = LocalDateTime.of(2024, 3, 20, 23, 0);
LocalDateTime afterMidnight = lateNight.plusHours(3); // 2024-03-21T02:00
```

Unlike `LocalTime`, adding hours to `LocalDateTime` rolls over into the next day correctly.

---

## The Escape Hatch: atZone()

When you realize a `LocalDateTime` needs timezone context, `atZone()` is your bridge:

```java
import java.time.ZoneId;
import java.time.ZonedDateTime;

LocalDateTime naive = LocalDateTime.of(2024, 3, 20, 14, 0);

// "This 2:00 PM is in New York"
ZonedDateTime inNewYork = naive.atZone(ZoneId.of("America/New_York"));

// "This 2:00 PM is in Tokyo"
ZonedDateTime inTokyo = naive.atZone(ZoneId.of("Asia/Tokyo"));

System.out.println(inNewYork); // 2024-03-20T14:00-04:00[America/New_York]
System.out.println(inTokyo);   // 2024-03-20T14:00+09:00[Asia/Tokyo]

// These are DIFFERENT moments in time!
System.out.println(inNewYork.toInstant()); // 2024-03-20T18:00:00Z
System.out.println(inTokyo.toInstant());   // 2024-03-20T05:00:00Z
```

---

## Fixing the MeetSync Bug

The appointment system should never have used `LocalDateTime` for cross-timezone meetings:

```java
// BEFORE (broken): timezone depends on server location
LocalDateTime appointment = LocalDateTime.of(2024, 3, 20, 14, 0);

// AFTER (correct): explicitly tied to a timezone
ZonedDateTime appointment = ZonedDateTime.of(
    2024, 3, 20, 14, 0, 0, 0,
    ZoneId.of("America/New_York")
);
// Now it doesn't matter where the server runs
```

---

## Adjusting Fields

```java
LocalDateTime dt = LocalDateTime.of(2024, 3, 20, 14, 30);

// Replace specific fields
LocalDateTime atNoon = dt.withHour(12).withMinute(0);     // 2024-03-20T12:00
LocalDateTime firstOfMonth = dt.withDayOfMonth(1);         // 2024-03-01T14:30
LocalDateTime inJune = dt.withMonth(6);                    // 2024-06-20T14:30

// Comparison
LocalDateTime other = LocalDateTime.of(2024, 3, 21, 9, 0);
System.out.println(dt.isBefore(other)); // true
```

---

## The Rule of Thumb

| Use Case | Type |
|----------|------|
| Birthday, holiday | `LocalDate` |
| Store hours, alarm | `LocalTime` |
| "2 PM on the wall clock" (no zone needed) | `LocalDateTime` |
| Meeting between people in different zones | `ZonedDateTime` |
| "When did this event happen?" | `Instant` |

If two people in different timezones need to agree on the same moment, `LocalDateTime` is the wrong choice.

---

## What You Learned

- `LocalDateTime` = `LocalDate` + `LocalTime`, nothing more
- It has **no timezone** — it's a reading on a wall clock, not a point on the timeline
- Correct for inherently local concepts (alarms, store hours, local events)
- **Wrong** for scheduling across timezones, event timestamps, or anything shared
- `atZone()` converts to `ZonedDateTime` when you need to anchor it to a timezone
- If your server's timezone matters to your code, you have a bug

---

*Next up: How do we properly handle "9 AM in London is 6 PM in Tokyo"? [Chapter 4](./chapter-04-zoneddatetime.md) gives us the full picture with `ZonedDateTime`.*
