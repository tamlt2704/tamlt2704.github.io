# Chapter 4 — ZonedDateTime: The Full Picture

[← LocalDateTime](./chapter-03-localdatetime.md) | [Next: Instant →](./chapter-05-instant.md)

---

## The Problem

MeetSync's core feature: scheduling meetings across timezones. A London user books a meeting at 9:00 AM. A Tokyo colleague opens the invite and sees... 9:00 AM.

```java
// The broken code
LocalDateTime meetingTime = LocalDateTime.of(2024, 3, 20, 9, 0);
// Sent to both users as "9:00 AM" — no conversion happens
```

The Tokyo user shows up at 9:00 AM Tokyo time. The London user is at 9:00 AM London time. They're 8 hours apart. The meeting never happens.

The fix: store the meeting with its timezone, then convert for each viewer.

---

## ZonedDateTime: Date + Time + Zone

`ZonedDateTime` is the complete package. It represents an unambiguous moment in time, displayed in a specific timezone.

```java
import java.time.ZonedDateTime;
import java.time.ZoneId;

// 9:00 AM in London
ZonedDateTime londonMeeting = ZonedDateTime.of(
    2024, 3, 20, 9, 0, 0, 0,
    ZoneId.of("Europe/London")
);

System.out.println(londonMeeting);
// 2024-03-20T09:00+00:00[Europe/London]
```

---

## Converting Between Zones

The key method: `withZoneSameInstant()`. Same moment, different clock.

```java
ZonedDateTime londonMeeting = ZonedDateTime.of(
    2024, 3, 20, 9, 0, 0, 0,
    ZoneId.of("Europe/London")
);

// What time is this in Tokyo?
ZonedDateTime tokyoView = londonMeeting.withZoneSameInstant(ZoneId.of("Asia/Tokyo"));
System.out.println(tokyoView);
// 2024-03-20T18:00+09:00[Asia/Tokyo]

// What about New York?
ZonedDateTime nyView = londonMeeting.withZoneSameInstant(ZoneId.of("America/New_York"));
System.out.println(nyView);
// 2024-03-20T05:00-04:00[America/New_York]
```

9:00 AM London = 6:00 PM Tokyo = 5:00 AM New York. Same moment, three clocks.

---

## Fixing the MeetSync Bug

```java
public class MeetingService {

    public MeetingDTO createMeeting(LocalDateTime userTime, ZoneId userZone) {
        // Anchor the user's local time to their timezone
        ZonedDateTime meeting = userTime.atZone(userZone);
        // Store as UTC instant in database
        Instant storedInstant = meeting.toInstant();
        return new MeetingDTO(storedInstant, meeting.getZone());
    }

    public ZonedDateTime getForUser(Instant meetingInstant, ZoneId viewerZone) {
        // Convert stored instant to viewer's timezone
        return meetingInstant.atZone(viewerZone);
    }
}

// London user creates meeting at 9:00 AM their time
ZoneId london = ZoneId.of("Europe/London");
MeetingService service = new MeetingService();
MeetingDTO dto = service.createMeeting(LocalDateTime.of(2024, 3, 20, 9, 0), london);

// Tokyo user views it
ZonedDateTime tokyoView = service.getForUser(dto.instant(), ZoneId.of("Asia/Tokyo"));
System.out.println(tokyoView.toLocalTime()); // 18:00 ✓
```

---

## ZoneId: Named Zones vs Offsets

```java
// Named zones (preferred) — handle DST automatically
ZoneId london = ZoneId.of("Europe/London");      // GMT or BST depending on date
ZoneId newYork = ZoneId.of("America/New_York");  // EST or EDT depending on date
ZoneId tokyo = ZoneId.of("Asia/Tokyo");          // JST always (no DST)

// Fixed offsets (use sparingly)
ZoneId utcPlus5 = ZoneId.of("+05:00");
ZoneId utc = ZoneId.of("UTC");

// System default (avoid in server code)
ZoneId system = ZoneId.systemDefault();
```

Always use named zones like `"America/New_York"` instead of `"EST"`. Named zones know about DST transitions. Fixed offsets don't.

---

## Listing Available Zones

```java
import java.util.Set;

// All available zone IDs
Set<String> zones = ZoneId.getAvailableZoneIds();
System.out.println(zones.size()); // ~600

// Filter for a region
zones.stream()
    .filter(z -> z.startsWith("America/"))
    .sorted()
    .forEach(System.out::println);
// America/Adak, America/Anchorage, America/Chicago, ...
```

---

## withZoneSameInstant vs withZoneSameLocal

These two methods sound similar but do completely different things:

```java
ZonedDateTime london9am = ZonedDateTime.of(
    2024, 3, 20, 9, 0, 0, 0, ZoneId.of("Europe/London")
);

// withZoneSameInstant: same MOMENT, different display
ZonedDateTime tokyoSameInstant = london9am.withZoneSameInstant(ZoneId.of("Asia/Tokyo"));
System.out.println(tokyoSameInstant); // 2024-03-20T18:00+09:00[Asia/Tokyo]

// withZoneSameLocal: same WALL CLOCK reading, different moment
ZonedDateTime tokyoSameLocal = london9am.withZoneSameLocal(ZoneId.of("Asia/Tokyo"));
System.out.println(tokyoSameLocal); // 2024-03-20T09:00+09:00[Asia/Tokyo]
```

`withZoneSameInstant` = "What time is it there right now?" (usually what you want)
`withZoneSameLocal` = "Make it 9:00 AM in Tokyo too" (rare, usually wrong for scheduling)

---

## Creating from Components

```java
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.LocalDateTime;

// From individual fields
ZonedDateTime zdt1 = ZonedDateTime.of(2024, 3, 20, 9, 0, 0, 0, ZoneId.of("Europe/London"));

// From LocalDateTime + Zone
LocalDateTime ldt = LocalDateTime.of(2024, 3, 20, 9, 0);
ZonedDateTime zdt2 = ldt.atZone(ZoneId.of("Europe/London"));

// From LocalDate + LocalTime + Zone
LocalDate date = LocalDate.of(2024, 3, 20);
LocalTime time = LocalTime.of(9, 0);
ZonedDateTime zdt3 = ZonedDateTime.of(date, time, ZoneId.of("Europe/London"));

// Current time in a specific zone
ZonedDateTime nowInTokyo = ZonedDateTime.now(ZoneId.of("Asia/Tokyo"));
```

---

## Arithmetic with ZonedDateTime

```java
ZonedDateTime meeting = ZonedDateTime.of(
    2024, 3, 20, 9, 0, 0, 0, ZoneId.of("Europe/London")
);

ZonedDateTime nextWeek = meeting.plusWeeks(1);
ZonedDateTime inTwoHours = meeting.plusHours(2);
ZonedDateTime tomorrow = meeting.plusDays(1);

// DST-aware! Adding 1 day across a DST boundary adjusts correctly
ZonedDateTime beforeDST = ZonedDateTime.of(
    2024, 3, 30, 9, 0, 0, 0, ZoneId.of("Europe/London")
);
ZonedDateTime afterDST = beforeDST.plusDays(1);
System.out.println(afterDST); // 2024-03-31T09:00+01:00[Europe/London]
// Still 9:00 AM wall clock time, but offset changed from +00:00 to +01:00
```

---

## The MeetSync Display Pattern

```java
public String formatForUser(Instant meetingInstant, ZoneId userZone, Locale userLocale) {
    ZonedDateTime userTime = meetingInstant.atZone(userZone);
    DateTimeFormatter formatter = DateTimeFormatter
        .ofPattern("EEEE, MMMM d 'at' h:mm a (z)")
        .withLocale(userLocale);
    return userTime.format(formatter);
}

Instant meeting = Instant.parse("2024-03-20T09:00:00Z");

System.out.println(formatForUser(meeting, ZoneId.of("Europe/London"), Locale.UK));
// Wednesday, March 20 at 9:00 AM (GMT)

System.out.println(formatForUser(meeting, ZoneId.of("Asia/Tokyo"), Locale.JAPAN));
// 水曜日, 3月 20 at 6:00 PM (JST)
```

---

## What You Learned

- `ZonedDateTime` = date + time + timezone — the full picture for scheduling
- `withZoneSameInstant()` converts between timezones (same moment, different clock)
- Use named zones (`"America/New_York"`) not abbreviations (`"EST"`)
- Store as `Instant` (UTC), display as `ZonedDateTime` in the user's zone
- `withZoneSameLocal` keeps the wall clock reading (rarely what you want)
- Arithmetic is DST-aware — adding 1 day keeps the wall clock time stable

---

*Next up: If `ZonedDateTime` is for humans, what's for machines? [Chapter 5](./chapter-05-instant.md) introduces `Instant` — the universal timestamp.*
