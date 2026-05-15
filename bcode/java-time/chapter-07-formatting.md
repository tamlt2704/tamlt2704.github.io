# Chapter 7 — Formatting & Parsing

[← Duration & Period](./chapter-06-duration-period.md) | [Next: Temporal Adjusters →](./chapter-08-adjusters.md)

---

## The Problem

MeetSync's API returns meeting times as ISO strings:

```json
{ "startTime": "2024-03-20T14:00:00Z" }
```

The frontend team wants to display: **"March 20, 2024 at 2:00 PM"**. The Japanese localization team wants: **"2024年3月20日 14:00"**. The German team wants: **"20. März 2024 um 14:00 Uhr"**.

Parsing the ISO string is step one. Formatting it for humans — in their locale — is step two.

---

## Parsing ISO Strings

The built-in ISO formatters handle standard formats without any configuration:

```java
import java.time.*;
import java.time.format.DateTimeFormatter;

// Parse ISO instant (the Z suffix)
Instant instant = Instant.parse("2024-03-20T14:00:00Z");

// Parse ISO local date-time
LocalDateTime ldt = LocalDateTime.parse("2024-03-20T14:00:00");

// Parse ISO local date
LocalDate date = LocalDate.parse("2024-03-20");

// Parse ISO local time
LocalTime time = LocalTime.parse("14:30:00");

// Parse with offset
OffsetDateTime odt = OffsetDateTime.parse("2024-03-20T14:00:00+05:30");
```

These use `DateTimeFormatter.ISO_*` constants under the hood. No pattern needed.

---

## Custom Patterns with ofPattern

```java
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MMMM d, yyyy 'at' h:mm a");

LocalDateTime meeting = LocalDateTime.of(2024, 3, 20, 14, 0);
String display = meeting.format(formatter);
System.out.println(display); // March 20, 2024 at 2:00 PM
```

Common pattern letters:

| Pattern | Meaning | Example |
|---------|---------|---------|
| `yyyy` | Year | 2024 |
| `MM` | Month (number) | 03 |
| `MMM` | Month (short) | Mar |
| `MMMM` | Month (full) | March |
| `dd` | Day of month | 20 |
| `HH` | Hour (24h) | 14 |
| `hh` | Hour (12h) | 02 |
| `mm` | Minute | 00 |
| `ss` | Second | 00 |
| `a` | AM/PM | PM |
| `z` | Zone name | EST |
| `Z` | Zone offset | -0500 |
| `EEEE` | Day of week | Wednesday |

---

## Locale-Aware Formatting

MeetSync serves users worldwide. Same moment, different display:

```java
import java.util.Locale;

LocalDateTime meeting = LocalDateTime.of(2024, 3, 20, 14, 0);

// English (US)
DateTimeFormatter usFormat = DateTimeFormatter
    .ofPattern("MMMM d, yyyy 'at' h:mm a")
    .withLocale(Locale.US);
System.out.println(meeting.format(usFormat));
// March 20, 2024 at 2:00 PM

// Japanese
DateTimeFormatter jpFormat = DateTimeFormatter
    .ofPattern("yyyy年M月d日 HH:mm")
    .withLocale(Locale.JAPAN);
System.out.println(meeting.format(jpFormat));
// 2024年3月20日 14:00

// German
DateTimeFormatter deFormat = DateTimeFormatter
    .ofPattern("d. MMMM yyyy 'um' HH:mm 'Uhr'")
    .withLocale(Locale.GERMANY);
System.out.println(meeting.format(deFormat));
// 20. März 2024 um 14:00 Uhr
```

---

## Parsing Custom Formats

When external systems send non-ISO formats:

```java
// Parse "03/20/2024 2:00 PM"
DateTimeFormatter americanFormat = DateTimeFormatter.ofPattern("MM/dd/yyyy h:mm a");
LocalDateTime parsed = LocalDateTime.parse("03/20/2024 2:00 PM", americanFormat);
System.out.println(parsed); // 2024-03-20T14:00

// Parse "20-Mar-2024"
DateTimeFormatter shortFormat = DateTimeFormatter.ofPattern("dd-MMM-yyyy")
    .withLocale(Locale.ENGLISH);
LocalDate date = LocalDate.parse("20-Mar-2024", shortFormat);
System.out.println(date); // 2024-03-20
```

---

## Built-in Formatters

Java provides pre-built formatters for common standards:

```java
LocalDateTime dt = LocalDateTime.of(2024, 3, 20, 14, 30, 0);

System.out.println(dt.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
// 2024-03-20T14:30:00

System.out.println(dt.format(DateTimeFormatter.ISO_LOCAL_DATE));
// 2024-03-20

ZonedDateTime zdt = dt.atZone(ZoneId.of("America/New_York"));
System.out.println(zdt.format(DateTimeFormatter.ISO_ZONED_DATE_TIME));
// 2024-03-20T14:30:00-04:00[America/New_York]

System.out.println(zdt.format(DateTimeFormatter.RFC_1123_DATE_TIME));
// Wed, 20 Mar 2024 14:30:00 -0400
```

---

## Formatting Instants

`Instant` has no timezone, so you must provide one for formatting:

```java
Instant now = Instant.parse("2024-03-20T18:00:00Z");

// Must specify a zone for display
DateTimeFormatter formatter = DateTimeFormatter
    .ofPattern("yyyy-MM-dd HH:mm z")
    .withZone(ZoneId.of("America/New_York"));

System.out.println(formatter.format(now));
// 2024-03-20 14:00 EDT
```

---

## The MeetSync Formatter Utility

```java
public class TimeDisplay {
    
    private static final DateTimeFormatter MEETING_FORMAT = 
        DateTimeFormatter.ofPattern("EEEE, MMMM d 'at' h:mm a");
    
    private static final DateTimeFormatter SHORT_FORMAT = 
        DateTimeFormatter.ofPattern("MMM d, h:mm a");
    
    private static final DateTimeFormatter ISO_API = 
        DateTimeFormatter.ISO_INSTANT;

    public static String forMeetingInvite(Instant meeting, ZoneId zone, Locale locale) {
        ZonedDateTime local = meeting.atZone(zone);
        return local.format(MEETING_FORMAT.withLocale(locale));
    }

    public static String forNotification(Instant meeting, ZoneId zone) {
        ZonedDateTime local = meeting.atZone(zone);
        return local.format(SHORT_FORMAT);
    }

    public static String forApi(Instant meeting) {
        return ISO_API.format(meeting);
    }
}

Instant meeting = Instant.parse("2024-03-20T18:00:00Z");

System.out.println(TimeDisplay.forMeetingInvite(
    meeting, ZoneId.of("America/New_York"), Locale.US));
// Wednesday, March 20 at 2:00 PM

System.out.println(TimeDisplay.forNotification(
    meeting, ZoneId.of("Asia/Tokyo")));
// Mar 21, 3:00 AM

System.out.println(TimeDisplay.forApi(meeting));
// 2024-03-20T18:00:00Z
```

---

## Handling Parse Errors

```java
public Optional<LocalDate> safeParse(String input) {
    try {
        return Optional.of(LocalDate.parse(input));
    } catch (DateTimeParseException e) {
        log.warn("Invalid date: '{}' — {}", input, e.getMessage());
        return Optional.empty();
    }
}

// Try multiple formats
public Optional<LocalDate> parseFlexible(String input) {
    List<DateTimeFormatter> formats = List.of(
        DateTimeFormatter.ISO_LOCAL_DATE,                    // 2024-03-20
        DateTimeFormatter.ofPattern("MM/dd/yyyy"),          // 03/20/2024
        DateTimeFormatter.ofPattern("d-MMM-yyyy")           // 20-Mar-2024
    );
    
    for (DateTimeFormatter fmt : formats) {
        try {
            return Optional.of(LocalDate.parse(input, fmt));
        } catch (DateTimeParseException ignored) {}
    }
    return Optional.empty();
}
```

---

## What You Learned

- `DateTimeFormatter.ofPattern()` creates custom format patterns
- ISO strings parse automatically — no formatter needed for standard formats
- `withLocale()` adapts month names, day names, and AM/PM to the user's language
- `Instant` formatting requires `.withZone()` since instants have no inherent timezone
- Reuse `DateTimeFormatter` instances — they're thread-safe and expensive to create
- Wrap parsing in try-catch for `DateTimeParseException` when handling user input
- Store as ISO/Instant, format at the display layer

---

*Next up: "Next business day", "last Friday of the month" — how do you express complex date rules? [Chapter 8](./chapter-08-adjusters.md) introduces Temporal Adjusters.*
