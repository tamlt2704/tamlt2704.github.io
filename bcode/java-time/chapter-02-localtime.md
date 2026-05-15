# Chapter 2 — LocalTime: Time Without Date

[← LocalDate](./chapter-01-localdate.md) | [Next: LocalDateTime →](./chapter-03-localdatetime.md)

---

## The Problem

MeetSync lets businesses set their available hours: "We take meetings from 9:00 to 17:00." Simple enough. The intern stored them as strings:

```java
String openTime = "9:00";
String closeTime = "17:00";

// Check if a requested time is within business hours
String requestedTime = "10:30";
if (requestedTime.compareTo(openTime) >= 0 && requestedTime.compareTo(closeTime) <= 0) {
    // Looks fine... until someone requests "9:05"
}
```

This works by accident for some inputs. But string comparison is lexicographic: `"9:05"` is greater than `"17:00"` because `'9' > '1'`. A 9:05 AM request gets rejected as "after hours."

The fix: stop treating time as text. Use `LocalTime`.

---

## LocalTime: Hours, Minutes, Seconds

`LocalTime` represents a time of day — no date, no timezone. It's what a clock on the wall shows.

```java
import java.time.LocalTime;

// Creating times
LocalTime morning = LocalTime.of(9, 0);          // 09:00
LocalTime afternoon = LocalTime.of(14, 30);       // 14:30
LocalTime precise = LocalTime.of(10, 15, 30);     // 10:15:30
LocalTime parsed = LocalTime.parse("09:30");       // 09:30

System.out.println(LocalTime.now()); // current time
System.out.println(LocalTime.MIDNIGHT); // 00:00
System.out.println(LocalTime.NOON);     // 12:00
```

---

## Fixing the Business Hours Bug

```java
public class BusinessHours {
    private final LocalTime open;
    private final LocalTime close;

    public BusinessHours(LocalTime open, LocalTime close) {
        this.open = open;
        this.close = close;
    }

    public boolean isAvailable(LocalTime requested) {
        return !requested.isBefore(open) && !requested.isAfter(close);
    }
}

// Usage
BusinessHours hours = new BusinessHours(
    LocalTime.of(9, 0),
    LocalTime.of(17, 0)
);

System.out.println(hours.isAvailable(LocalTime.of(9, 5)));   // true ✓
System.out.println(hours.isAvailable(LocalTime.of(18, 0)));  // false
System.out.println(hours.isAvailable(LocalTime.of(8, 59)));  // false
```

`isBefore()` and `isAfter()` compare actual time values, not character codes.

---

## Time Slot Availability

MeetSync divides the day into 30-minute slots. We need to generate available slots:

```java
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

public List<LocalTime> generateSlots(LocalTime start, LocalTime end, Duration slotLength) {
    List<LocalTime> slots = new ArrayList<>();
    LocalTime current = start;

    while (current.plus(slotLength).isBefore(end) 
           || current.plus(slotLength).equals(end)) {
        slots.add(current);
        current = current.plus(slotLength);
    }
    return slots;
}

// Generate 30-minute slots from 9:00 to 12:00
List<LocalTime> slots = generateSlots(
    LocalTime.of(9, 0),
    LocalTime.of(12, 0),
    Duration.ofMinutes(30)
);
// [09:00, 09:30, 10:00, 10:30, 11:00, 11:30]
```

---

## Duration Between Times

How long is a meeting? How much time until lunch?

```java
import java.time.Duration;
import java.time.temporal.ChronoUnit;

LocalTime meetingStart = LocalTime.of(10, 0);
LocalTime meetingEnd = LocalTime.of(11, 30);

Duration duration = Duration.between(meetingStart, meetingEnd);
System.out.println(duration);              // PT1H30M
System.out.println(duration.toMinutes());  // 90

// Using ChronoUnit directly
long minutes = ChronoUnit.MINUTES.between(meetingStart, meetingEnd);
System.out.println(minutes + " minutes"); // 90 minutes
```

---

## Time Arithmetic

```java
LocalTime now = LocalTime.of(14, 30);

LocalTime later = now.plusHours(2);          // 16:30
LocalTime earlier = now.minusMinutes(45);    // 13:45
LocalTime rounded = now.plusMinutes(15);     // 14:45

// What happens at midnight boundary?
LocalTime lateNight = LocalTime.of(23, 30);
LocalTime wrapped = lateNight.plusHours(2);  // 01:30 (wraps around)
```

Note: `LocalTime` wraps around midnight. It doesn't track "next day" — it's just a wall clock.

---

## Truncating Time

MeetSync rounds meeting times to the nearest quarter hour for display:

```java
import java.time.temporal.ChronoUnit;

LocalTime exact = LocalTime.of(10, 47, 23);

LocalTime toHour = exact.truncatedTo(ChronoUnit.HOURS);     // 10:00
LocalTime toMinute = exact.truncatedTo(ChronoUnit.MINUTES); // 10:47
LocalTime toSecond = exact.truncatedTo(ChronoUnit.SECONDS); // 10:47:23

// Round to nearest 15 minutes (custom logic)
public LocalTime roundToQuarter(LocalTime time) {
    int minute = time.getMinute();
    int rounded = ((minute + 7) / 15) * 15;
    return time.truncatedTo(ChronoUnit.HOURS).plusMinutes(rounded % 60)
               .plusHours(rounded / 60);
}

System.out.println(roundToQuarter(LocalTime.of(10, 47))); // 10:45
System.out.println(roundToQuarter(LocalTime.of(10, 53))); // 11:00
```

---

## Comparing and Sorting

```java
LocalTime t1 = LocalTime.of(9, 0);
LocalTime t2 = LocalTime.of(14, 30);
LocalTime t3 = LocalTime.of(9, 0);

System.out.println(t1.isBefore(t2)); // true
System.out.println(t1.isAfter(t2));  // false
System.out.println(t1.equals(t3));   // true

// Sorting a list of times
List<LocalTime> times = List.of(
    LocalTime.of(14, 0),
    LocalTime.of(9, 30),
    LocalTime.of(11, 0)
);
List<LocalTime> sorted = times.stream().sorted().toList();
// [09:30, 11:00, 14:00] — natural ordering works correctly
```

---

## Extracting Components

```java
LocalTime time = LocalTime.of(14, 30, 45);

int hour = time.getHour();     // 14
int minute = time.getMinute(); // 30
int second = time.getSecond(); // 45

// Convert to seconds since midnight
int secondOfDay = time.toSecondOfDay(); // 52245
// Reconstruct from seconds
LocalTime fromSeconds = LocalTime.ofSecondOfDay(52245); // 14:30:45
```

---

## What You Learned

- `LocalTime` represents a wall-clock time with no date or timezone
- Use it for business hours, schedules, time-of-day rules
- `isBefore()` / `isAfter()` compare correctly (unlike string comparison)
- `Duration.between()` calculates elapsed time between two `LocalTime` values
- `plusHours()` / `minusMinutes()` wraps around midnight — it's a clock, not a timeline
- `truncatedTo()` rounds down to a given precision
- Natural ordering means `sorted()` just works on collections

---

*Next up: What if you need both a date AND a time? [Chapter 3](./chapter-03-localdatetime.md) introduces `LocalDateTime` — and warns you about its biggest trap.*
