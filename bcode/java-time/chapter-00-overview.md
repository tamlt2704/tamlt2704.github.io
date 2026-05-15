# Chapter 0: Before You Start

[Chapter 1: LocalDate →](chapter-01-localdate.md)

---

## The Story

You're a backend developer at **MeetSync**, a global scheduling platform. Users in New York book meetings with users in Tokyo. Recurring events span daylight saving transitions. Reminders fire "30 minutes before" — but 30 minutes in whose timezone?

Your tech lead, **Rina**, drops a bug report on your desk:

"A user in London booked a 9 AM meeting. The user in Sydney sees it at 9 AM too — their local 9 AM. That's wrong. It should be 6 PM Sydney time. The meeting is in 2 hours and both people will show up at different times. Fix it."

You check the code:

```java
// The crime scene
String meetingTime = "2024-03-15 09:00:00";
// Stored as a string. No timezone. No offset. Just vibes.
```

Over the next 12 chapters, you'll rebuild MeetSync's time handling from broken strings to correct temporal types. Every class in `java.time` solves a specific problem — and using the wrong one creates bugs that only appear when users cross timezone boundaries.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Developer | "What do you mean 2 AM happens twice?" |
| **Rina** | Tech Lead | "Store UTC. Display local. Always." |
| **The User in Tokyo** | Customer | Missed 3 meetings this month. Furious. |
| **The Legacy Code** | `java.util.Date` | Born in 1996. Mutable. Confused about timezones. |
| **DST** | The Villain | Strikes twice a year. Shows no mercy. |

## The java.time Landscape

```
                    ┌─────────────────────────────────────────┐
                    │           java.time (since Java 8)       │
                    └─────────────────────────────────────────┘

  No timezone                              With timezone
  ┌──────────────┐  ┌────────────────┐    ┌──────────────────┐
  │  LocalDate   │  │ LocalDateTime  │    │  ZonedDateTime   │
  │  2024-03-15  │  │ 2024-03-15    │    │  2024-03-15      │
  │              │  │   T09:00:00    │    │   T09:00:00      │
  │              │  │                │    │   +00:00[Europe/  │
  │              │  │                │    │         London]   │
  └──────────────┘  └────────────────┘    └──────────────────┘
  ┌──────────────┐                        ┌──────────────────┐
  │  LocalTime   │                        │     Instant      │
  │   09:00:00   │                        │  (epoch millis)  │
  └──────────────┘                        └──────────────────┘

  How long?
  ┌──────────────┐  ┌────────────────┐
  │   Duration   │  │     Period     │
  │  (seconds)   │  │ (years/months/ │
  │  PT2H30M     │  │  days)         │
  └──────────────┘  └────────────────┘
```

## When to Use What

| Type | Use When | Example |
|---|---|---|
| `LocalDate` | Date only, no time, no zone | Birthday, holiday, due date |
| `LocalTime` | Time only, no date, no zone | Store opens at 9:00 |
| `LocalDateTime` | Date + time, no zone | "The event is March 15 at 9 AM" (ambiguous without zone) |
| `ZonedDateTime` | Full date + time + timezone | Meeting at 9 AM London time |
| `Instant` | Machine timestamp, always UTC | Log entry, created_at, event ordering |
| `Duration` | Elapsed time in seconds/nanos | "Took 2.5 seconds", "timeout after 30 minutes" |
| `Period` | Calendar-based difference | "3 months from now", "every 2 weeks" |

## The Golden Rules

Rina's rules, learned from years of timezone bugs:

1. **Store UTC** — database columns hold `Instant` or `TIMESTAMP WITH TIME ZONE`
2. **Display local** — convert to user's timezone only at the presentation layer
3. **Never use strings for time** — parse immediately, format at the last moment
4. **LocalDateTime is almost always wrong** — if you're storing it, you've lost timezone info
5. **Test with DST transitions** — if your code doesn't handle March/November, it's broken

## Prerequisites

### Java 17+

```bash
java --version
# openjdk 17.0.x or higher
```

### Quick Check

```java
import java.time.*;

public class TimeCheck {
    public static void main(String[] args) {
        System.out.println("Now (UTC):   " + Instant.now());
        System.out.println("Now (local): " + LocalDateTime.now());
        System.out.println("Now (zoned): " + ZonedDateTime.now());
        System.out.println("Zone:        " + ZoneId.systemDefault());
    }
}
```

```bash
javac TimeCheck.java && java TimeCheck
```

If that prints timestamps, you're ready.

## The Legacy Mess (What We're Replacing)

```java
// java.util.Date — mutable, timezone-confused, deprecated methods
Date date = new Date();           // "now" but... in what timezone?
date.setHours(9);                 // deprecated since Java 1.1

// java.util.Calendar — verbose, mutable, month is 0-indexed
Calendar cal = Calendar.getInstance();
cal.set(Calendar.MONTH, 2);       // March (0=Jan, 1=Feb, 2=Mar) 🤦

// SimpleDateFormat — not thread-safe, silent failures
SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
Date parsed = sdf.parse("not-a-date");  // throws at runtime
```

`java.time` fixes all of this: immutable, clear semantics, thread-safe, timezone-aware.

Let's start with the simplest case — a date without time.

---

[Chapter 1: LocalDate →](chapter-01-localdate.md)
