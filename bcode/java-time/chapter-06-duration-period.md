# Chapter 6 — Duration & Period: How Long?

[← Instant](./chapter-05-instant.md) | [Next: Formatting & Parsing →](./chapter-07-formatting.md)

---

## The Problem

MeetSync offers monthly subscriptions. A user signs up on January 31st. When does their subscription renew?

```java
// Developer A: "Add 1 month"
LocalDate signup = LocalDate.of(2024, 1, 31);
LocalDate renewA = signup.plusMonths(1);
System.out.println(renewA); // 2024-02-29 (leap year)

// Developer B: "Add 30 days"
LocalDate renewB = signup.plusDays(30);
System.out.println(renewB); // 2024-03-01
```

Two different answers. Which is correct? It depends on what "one month" means to your business. Java gives you two distinct types for this reason: `Period` (calendar-based) and `Duration` (time-based).

---

## Period: Calendar Amounts

`Period` measures time in years, months, and days. It's human-calendar math.

```java
import java.time.Period;
import java.time.LocalDate;

// Creating periods
Period oneMonth = Period.ofMonths(1);
Period twoWeeks = Period.ofWeeks(2);        // stored as 14 days
Period complex = Period.of(1, 2, 3);        // 1 year, 2 months, 3 days
Period parsed = Period.parse("P1Y2M3D");    // ISO format

System.out.println(oneMonth); // P1M
System.out.println(complex);  // P1Y2M3D
```

---

## Period.between: Age and Date Differences

```java
LocalDate birth = LocalDate.of(1990, 5, 15);
LocalDate today = LocalDate.of(2024, 3, 20);

Period age = Period.between(birth, today);
System.out.println(age.getYears());  // 33
System.out.println(age.getMonths()); // 10
System.out.println(age.getDays());   // 5
// "33 years, 10 months, and 5 days old"

// Subscription duration
LocalDate subscriptionStart = LocalDate.of(2024, 1, 15);
LocalDate subscriptionEnd = LocalDate.of(2024, 7, 15);
Period subLength = Period.between(subscriptionStart, subscriptionEnd);
System.out.println(subLength); // P6M
```

---

## Duration: Exact Time Amounts

`Duration` measures time in seconds and nanoseconds. It's machine-precise.

```java
import java.time.Duration;
import java.time.Instant;

// Creating durations
Duration twoHours = Duration.ofHours(2);
Duration ninetyMinutes = Duration.ofMinutes(90);
Duration halfSecond = Duration.ofMillis(500);
Duration parsed = Duration.parse("PT2H30M");  // ISO format

System.out.println(twoHours);       // PT2H
System.out.println(ninetyMinutes);  // PT1H30M (normalized)
```

---

## Duration.between: Elapsed Time

```java
Instant start = Instant.parse("2024-03-20T10:00:00Z");
Instant end = Instant.parse("2024-03-20T11:30:00Z");

Duration elapsed = Duration.between(start, end);
System.out.println(elapsed);              // PT1H30M
System.out.println(elapsed.toMinutes());  // 90
System.out.println(elapsed.toSeconds());  // 5400

// Meeting duration
LocalTime meetingStart = LocalTime.of(14, 0);
LocalTime meetingEnd = LocalTime.of(15, 30);
Duration meetingLength = Duration.between(meetingStart, meetingEnd);
System.out.println("Meeting: " + meetingLength.toMinutes() + " min"); // 90 min
```

---

## Period vs Duration: The Key Difference

```java
// Period: "1 month" means different things depending on WHEN
LocalDate jan31 = LocalDate.of(2024, 1, 31);
LocalDate feb29 = jan31.plus(Period.ofMonths(1)); // 2024-02-29
LocalDate mar31 = feb29.plus(Period.ofMonths(1)); // 2024-03-29 (not 31!)

// Duration: "30 days" is always exactly 30 days
LocalDate plus30 = jan31.plus(Duration.ofDays(30)); 
// UnsupportedTemporalTypeException! Duration doesn't work with LocalDate

// Use ChronoUnit for fixed day counts with LocalDate
LocalDate plus30days = jan31.plusDays(30); // 2024-03-01
```

| | Period | Duration |
|---|--------|----------|
| Measures | Years, months, days | Hours, minutes, seconds, nanos |
| Works with | `LocalDate`, `LocalDateTime` | `Instant`, `LocalTime`, `LocalDateTime` |
| "1 month" | Calendar month (28-31 days) | N/A |
| "24 hours" | N/A | Exactly 86,400 seconds |
| DST-aware | Yes (via calendar) | No (fixed seconds) |

---

## ChronoUnit: The Bridge

When you need a single unit of measurement:

```java
import java.time.temporal.ChronoUnit;

LocalDate start = LocalDate.of(2024, 1, 1);
LocalDate end = LocalDate.of(2024, 12, 31);

long days = ChronoUnit.DAYS.between(start, end);     // 365
long months = ChronoUnit.MONTHS.between(start, end); // 11
long weeks = ChronoUnit.WEEKS.between(start, end);   // 52

// Works with time too
Instant t1 = Instant.now();
Instant t2 = t1.plus(Duration.ofHours(3));
long hours = ChronoUnit.HOURS.between(t1, t2);       // 3
long minutes = ChronoUnit.MINUTES.between(t1, t2);   // 180
```

---

## MeetSync Subscription Logic

```java
public class SubscriptionService {

    public LocalDate calculateRenewal(LocalDate startDate, Period billingCycle) {
        return startDate.plus(billingCycle);
    }

    public boolean isExpired(LocalDate expiryDate) {
        return LocalDate.now().isAfter(expiryDate);
    }

    public long daysRemaining(LocalDate expiryDate) {
        long days = ChronoUnit.DAYS.between(LocalDate.now(), expiryDate);
        return Math.max(0, days);
    }
}

// Monthly subscription
SubscriptionService svc = new SubscriptionService();
LocalDate start = LocalDate.of(2024, 1, 31);
LocalDate renewal = svc.calculateRenewal(start, Period.ofMonths(1));
System.out.println(renewal); // 2024-02-29

// Annual subscription
LocalDate annualRenewal = svc.calculateRenewal(start, Period.ofYears(1));
System.out.println(annualRenewal); // 2025-01-31
```

---

## Duration Arithmetic

```java
Duration meeting = Duration.ofMinutes(60);
Duration buffer = Duration.ofMinutes(15);

Duration totalBlock = meeting.plus(buffer);
System.out.println(totalBlock); // PT1H15M

// Multiply (useful for repeated slots)
Duration threeSlots = meeting.multipliedBy(3);
System.out.println(threeSlots); // PT3H

// Compare
System.out.println(meeting.compareTo(buffer) > 0); // true (60 > 15)

// Negative durations
Duration negative = Duration.between(
    LocalTime.of(14, 0), LocalTime.of(13, 0)
);
System.out.println(negative);          // PT-1H
System.out.println(negative.isNegative()); // true
System.out.println(negative.abs());    // PT1H
```

---

## Formatting Durations for Humans

Java doesn't have a built-in "pretty print" for durations, so MeetSync rolls its own:

```java
public String humanReadable(Duration duration) {
    long hours = duration.toHours();
    long minutes = duration.toMinutesPart();

    if (hours > 0 && minutes > 0) {
        return hours + "h " + minutes + "m";
    } else if (hours > 0) {
        return hours + "h";
    } else {
        return minutes + "m";
    }
}

System.out.println(humanReadable(Duration.ofMinutes(90)));  // 1h 30m
System.out.println(humanReadable(Duration.ofHours(2)));     // 2h
System.out.println(humanReadable(Duration.ofMinutes(45)));  // 45m
```

---

## What You Learned

- `Period` = calendar-based (years, months, days) — "1 month" varies by month
- `Duration` = time-based (hours, minutes, seconds) — always exact
- `Period.between()` for date differences, `Duration.between()` for time differences
- `ChronoUnit` bridges both worlds with single-unit measurements
- Adding a `Period` of 1 month to Jan 31 gives Feb 29 (or 28) — calendar-aware
- `Duration` cannot be added to `LocalDate` (no concept of "hours" in a date)
- Use `Period` for billing cycles, `Duration` for meeting lengths and timeouts

---

*Next up: You've got the data — now how do you display it? [Chapter 7](./chapter-07-formatting.md) covers parsing API strings and formatting for humans.*
