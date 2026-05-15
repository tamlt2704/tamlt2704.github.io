# Chapter 9 — Daylight Saving Traps

[← Temporal Adjusters](./chapter-08-adjusters.md) | [Next: Database & JSON →](./chapter-10-persistence.md)

---

## The Problem

MeetSync runs a cron job at 2:30 AM US Eastern to send daily digest emails. On the second Sunday of March (spring forward), 2:30 AM doesn't exist — clocks jump from 1:59 AM to 3:00 AM. The job never fires.

On the first Sunday of November (fall back), 2:30 AM happens twice — clocks go from 2:59 AM back to 2:00 AM. The job fires twice. Users get duplicate emails.

```
Spring Forward (March 10, 2024):
  1:00 AM → 1:30 AM → 1:59 AM → 3:00 AM  (2:00-2:59 doesn't exist)

Fall Back (November 3, 2024):
  1:00 AM → 1:30 AM → 2:00 AM → 2:30 AM → 2:00 AM → 2:30 AM → 3:00 AM
                                            ↑ clocks reset here
```

---

## The Gap: Spring Forward

When clocks spring forward, a range of local times simply doesn't exist:

```java
import java.time.*;
import java.time.zone.ZoneRules;
import java.time.zone.ZoneOffsetTransition;

ZoneId eastern = ZoneId.of("America/New_York");
ZoneRules rules = eastern.getRules();

// March 10, 2024: clocks jump from 2:00 AM to 3:00 AM
LocalDateTime gapTime = LocalDateTime.of(2024, 3, 10, 2, 30);

// What happens when we try to create this ZonedDateTime?
ZonedDateTime result = gapTime.atZone(eastern);
System.out.println(result);
// 2024-03-10T03:30-04:00[America/New_York]
// Java pushes it FORWARD into the gap — 2:30 becomes 3:30
```

Java doesn't throw an exception. It silently adjusts. This is why your 2:30 AM cron job runs at 3:30 AM instead — or not at all, depending on your scheduler.

---

## The Overlap: Fall Back

When clocks fall back, a range of local times occurs twice:

```java
ZoneId eastern = ZoneId.of("America/New_York");

// November 3, 2024: clocks go back from 2:00 AM to 1:00 AM
LocalDateTime overlapTime = LocalDateTime.of(2024, 11, 3, 1, 30);

// This time exists TWICE — once in EDT (-04:00) and once in EST (-05:00)
ZonedDateTime result = overlapTime.atZone(eastern);
System.out.println(result);
// 2024-11-03T01:30-04:00[America/New_York]
// Java picks the EARLIER offset (EDT) by default

// To get the later occurrence (EST):
ZonedDateTime laterOccurrence = result.withLaterOffsetAtOverlap();
System.out.println(laterOccurrence);
// 2024-11-03T01:30-05:00[America/New_York]
```

---

## Detecting Transitions

```java
ZoneId eastern = ZoneId.of("America/New_York");
ZoneRules rules = eastern.getRules();

// Check if a specific local time is in a gap
LocalDateTime springForward = LocalDateTime.of(2024, 3, 10, 2, 30);
boolean isValid = rules.isValidOffset(
    springForward, 
    ZoneOffset.ofHours(-5)  // EST
);
System.out.println("Valid in EST? " + isValid); // false

// Get the transition
ZoneOffsetTransition transition = rules.getTransition(springForward);
if (transition != null) {
    System.out.println("Gap: " + transition.isGap());       // true
    System.out.println("Overlap: " + transition.isOverlap()); // false
    System.out.println("Before: " + transition.getOffsetBefore()); // -05:00
    System.out.println("After: " + transition.getOffsetAfter());   // -04:00
}
```

---

## Safe Scheduling: Use Instants

The fix for MeetSync's cron job: schedule in UTC, not local time.

```java
// WRONG: Schedule at "2:30 AM Eastern" — breaks during DST
// cron: "30 2 * * * America/New_York"

// RIGHT: Schedule at a fixed UTC time
// cron: "30 7 * * * UTC"  (7:30 UTC = 2:30 AM EST / 3:30 AM EDT)

// Or better: schedule by Instant and convert for display
public Instant nextDigestTime(Instant after) {
    // Always run at 07:30 UTC
    ZonedDateTime utcTime = after.atZone(ZoneId.of("UTC"))
        .withHour(7).withMinute(30).withSecond(0).withNano(0);
    
    if (utcTime.toInstant().isBefore(after)) {
        utcTime = utcTime.plusDays(1);
    }
    return utcTime.toInstant();
}
```

---

## Wall Clock Time vs Instant

The core confusion: do you mean "2:30 on the wall clock" or "the moment that is 2:30 today"?

```java
ZoneId eastern = ZoneId.of("America/New_York");

// "I want to do something at 2:30 PM wall clock time every day"
// This is safe — 2:30 PM is never in a DST transition (transitions happen at 2 AM)
LocalTime dailyTask = LocalTime.of(14, 30);
ZonedDateTime todayAt230pm = ZonedDateTime.of(
    LocalDate.now(), dailyTask, eastern);

// "I want to do something exactly 24 hours from now"
// Use Instant — DST doesn't affect it
Instant now = Instant.now();
Instant in24Hours = now.plus(Duration.ofHours(24));

// Note: "tomorrow at the same time" ≠ "24 hours from now" during DST
ZonedDateTime tomorrow = ZonedDateTime.now(eastern).plusDays(1);
// plusDays(1) keeps wall clock time (2:30 PM → 2:30 PM)
// but the actual duration might be 23 or 25 hours
```

---

## Duration Across DST

```java
ZoneId eastern = ZoneId.of("America/New_York");

// Day before spring forward
ZonedDateTime saturday = ZonedDateTime.of(
    2024, 3, 9, 12, 0, 0, 0, eastern);

// Day of spring forward
ZonedDateTime sunday = saturday.plusDays(1);

// How many hours between them?
Duration gap = Duration.between(saturday, sunday);
System.out.println(gap); // PT23H (not 24! We lost an hour)

// Fall back: the day is 25 hours long
ZonedDateTime satNov = ZonedDateTime.of(
    2024, 11, 2, 12, 0, 0, 0, eastern);
ZonedDateTime sunNov = satNov.plusDays(1);
Duration overlap = Duration.between(satNov, sunNov);
System.out.println(overlap); // PT25H (gained an hour)
```

---

## MeetSync: Safe Meeting Scheduling

```java
public class SafeScheduler {

    /**
     * Schedule a meeting at a specific wall-clock time.
     * Handles DST gaps by pushing forward, overlaps by picking earlier offset.
     */
    public ZonedDateTime scheduleMeeting(
            LocalDate date, LocalTime time, ZoneId zone) {
        
        LocalDateTime ldt = LocalDateTime.of(date, time);
        ZoneRules rules = zone.getRules();
        ZoneOffsetTransition transition = rules.getTransition(ldt);
        
        if (transition != null && transition.isGap()) {
            // Time doesn't exist — push to after the gap
            LocalDateTime adjusted = transition.getDateTimeAfter();
            System.out.println("Warning: " + time + " doesn't exist on " + date 
                + " in " + zone + ". Adjusted to " + adjusted.toLocalTime());
            return adjusted.atZone(zone);
        }
        
        return ldt.atZone(zone); // Normal case or overlap (picks earlier)
    }
}

SafeScheduler scheduler = new SafeScheduler();

// Normal day — works fine
ZonedDateTime normal = scheduler.scheduleMeeting(
    LocalDate.of(2024, 3, 15), LocalTime.of(2, 30),
    ZoneId.of("America/New_York"));
// 2024-03-15T02:30-04:00[America/New_York]

// DST gap day — adjusted
ZonedDateTime gapDay = scheduler.scheduleMeeting(
    LocalDate.of(2024, 3, 10), LocalTime.of(2, 30),
    ZoneId.of("America/New_York"));
// Warning: 02:30 doesn't exist on 2024-03-10. Adjusted to 03:00
// 2024-03-10T03:00-04:00[America/New_York]
```

---

## Zones Without DST

Not every zone has DST. Some are safe havens:

```java
// No DST — ever
ZoneId tokyo = ZoneId.of("Asia/Tokyo");       // JST +09:00 always
ZoneId utc = ZoneId.of("UTC");                // +00:00 always
ZoneId kolkata = ZoneId.of("Asia/Kolkata");   // IST +05:30 always

// Has DST
ZoneId newYork = ZoneId.of("America/New_York"); // EST/EDT
ZoneId london = ZoneId.of("Europe/London");     // GMT/BST
ZoneId sydney = ZoneId.of("Australia/Sydney");  // AEST/AEDT
```

---

## What You Learned

- DST creates **gaps** (spring forward: times don't exist) and **overlaps** (fall back: times occur twice)
- Java silently adjusts gap times forward — no exception thrown
- For overlaps, Java picks the earlier offset by default; use `withLaterOffsetAtOverlap()` for the later one
- `ZoneRules.getTransition()` detects if a time falls in a gap or overlap
- Schedule recurring jobs in UTC to avoid DST issues entirely
- `plusDays(1)` preserves wall clock time; `plus(Duration.ofHours(24))` adds exact hours
- A "day" can be 23 or 25 hours during DST transitions
- Always test scheduling logic around March and November boundaries

---

*Next up: You've mastered the types — now how do you store them? [Chapter 10](./chapter-10-persistence.md) covers database mapping and JSON serialization.*
