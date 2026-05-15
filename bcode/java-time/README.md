# Java Time — Dates, Zones, and Durations Done Right

A narrative-driven course on Java's `java.time` API. You're a backend developer at a global scheduling platform where every timezone bug costs a missed meeting. Over 12 chapters, you'll master temporal programming — one off-by-one-hour disaster at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, why java.time, the cast |
| 01 | [LocalDate: Days Without Time](chapter-01-localdate.md) | Birthday stored as timestamp shows wrong day | LocalDate, parsing, formatting, Period |
| 02 | [LocalTime: Time Without Date](chapter-02-localtime.md) | "Meeting at 2pm" — but which 2pm? | LocalTime, truncation, between |
| 03 | [LocalDateTime: The Naive Pair](chapter-03-localdatetime.md) | Appointment stored without timezone shifts on deploy | LocalDateTime, combining, adjusting |
| 04 | [ZonedDateTime: The Full Picture](chapter-04-zoneddatetime.md) | User in Tokyo sees wrong meeting time | ZoneId, ZonedDateTime, conversion |
| 05 | [Instant: Machine Time](chapter-05-instant.md) | Logs from 3 servers can't be correlated | Instant, epoch, UTC, comparison |
| 06 | [Duration & Period: How Long?](chapter-06-duration-period.md) | "30 days" vs "1 month" gives different results | Duration (seconds), Period (calendar), between |
| 07 | [Formatting & Parsing](chapter-07-formatting.md) | API returns "2024-01-15T10:30:00+09:00" — how to parse? | DateTimeFormatter, patterns, ISO formats |
| 08 | [Temporal Adjusters](chapter-08-adjusters.md) | "Next business day", "last Friday of month" | TemporalAdjuster, built-in adjusters, custom |
| 09 | [Daylight Saving Traps](chapter-09-dst.md) | Scheduled job runs twice or skips on DST change | DST gaps/overlaps, ZoneRules, safe scheduling |
| 10 | [Database & JSON](chapter-10-persistence.md) | Timestamp in DB loses timezone info | JDBC mappings, Jackson config, storage strategies |
| 11 | [Legacy Interop](chapter-11-legacy.md) | Old code uses Date/Calendar everywhere | Conversion bridges, migration patterns |
| 12 | [Patterns & Best Practices](chapter-12-patterns.md) | Putting it all together | Clock injection, testing time, architecture rules |

## Prerequisites

- Java 17+ (java.time has been stable since Java 8, enhanced through 17)
- Basic Java (classes, methods, imports)

## Philosophy

Every concept is introduced because a timezone bug ruined someone's day. No API without a real scheduling disaster first. The wrong time comes first. The correct time follows.
