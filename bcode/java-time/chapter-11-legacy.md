# Chapter 11 — Legacy Interop

[← Database & JSON](./chapter-10-persistence.md) | [Next: Patterns & Best Practices →](./chapter-12-patterns.md)

---

## The Problem

MeetSync's codebase is 8 years old. The original scheduling engine was written in 2016 and passes `java.util.Date` everywhere:

```java
// Legacy service interface — can't change without breaking 40 consumers
public interface LegacyCalendarService {
    Date getNextAvailableSlot(String userId);
    void bookMeeting(String userId, Date startTime, Date endTime);
    List<Date> getBlockedTimes(String userId, Date rangeStart, Date rangeEnd);
}
```

New code uses `Instant` and `ZonedDateTime`. You can't rewrite everything at once. You need a bridge.

---

## java.util.Date ↔ Instant

`Date` and `Instant` both represent a point on the timeline. The conversion is direct:

```java
import java.util.Date;
import java.time.Instant;

// Date → Instant
Date legacyDate = new Date(); // from old API
Instant modern = legacyDate.toInstant();

// Instant → Date
Instant now = Instant.now();
Date backToLegacy = Date.from(now);

// Round-trip is lossless (both are millisecond precision)
Date original = new Date(1710957600000L);
Instant converted = original.toInstant();
Date restored = Date.from(converted);
System.out.println(original.equals(restored)); // true
```

---

## java.util.Calendar ↔ ZonedDateTime

```java
import java.util.Calendar;
import java.util.TimeZone;
import java.time.ZonedDateTime;
import java.time.ZoneId;

// Calendar → ZonedDateTime
Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("America/New_York"));
cal.set(2024, Calendar.MARCH, 20, 14, 0, 0);
ZonedDateTime zdt = cal.toInstant().atZone(cal.getTimeZone().toZoneId());

// ZonedDateTime → Calendar
ZonedDateTime meeting = ZonedDateTime.of(2024, 3, 20, 14, 0, 0, 0,
    ZoneId.of("America/New_York"));
Calendar backToCal = Calendar.getInstance();
backToCal.setTimeInMillis(meeting.toInstant().toEpochMilli());
backToCal.setTimeZone(TimeZone.getTimeZone(meeting.getZone()));
```

---

## java.sql.Timestamp ↔ Instant / LocalDateTime

```java
import java.sql.Timestamp;

// Timestamp → Instant
Timestamp sqlTs = Timestamp.valueOf("2024-03-20 14:00:00");
Instant instant = sqlTs.toInstant();

// Instant → Timestamp
Timestamp backToSql = Timestamp.from(Instant.now());

// Timestamp → LocalDateTime (no timezone conversion)
LocalDateTime ldt = sqlTs.toLocalDateTime();

// LocalDateTime → Timestamp
Timestamp fromLdt = Timestamp.valueOf(LocalDateTime.of(2024, 3, 20, 14, 0));
```

Note: `java.sql.Timestamp` extends `java.util.Date` but adds nanosecond precision.

---

## java.sql.Date ↔ LocalDate

```java
import java.sql.Date as SqlDate;

// sql.Date → LocalDate
java.sql.Date sqlDate = java.sql.Date.valueOf("2024-03-20");
LocalDate localDate = sqlDate.toLocalDate();

// LocalDate → sql.Date
java.sql.Date backToSql = java.sql.Date.valueOf(LocalDate.of(2024, 3, 20));
```

---

## The Bridge Pattern

Wrap the legacy service with a modern interface:

```java
// Modern interface
public interface CalendarService {
    Instant getNextAvailableSlot(String userId);
    void bookMeeting(String userId, Instant startTime, Instant endTime);
    List<Instant> getBlockedTimes(String userId, Instant rangeStart, Instant rangeEnd);
}

// Bridge implementation
public class CalendarServiceBridge implements CalendarService {
    private final LegacyCalendarService legacy;

    public CalendarServiceBridge(LegacyCalendarService legacy) {
        this.legacy = legacy;
    }

    @Override
    public Instant getNextAvailableSlot(String userId) {
        Date result = legacy.getNextAvailableSlot(userId);
        return result != null ? result.toInstant() : null;
    }

    @Override
    public void bookMeeting(String userId, Instant startTime, Instant endTime) {
        legacy.bookMeeting(userId, Date.from(startTime), Date.from(endTime));
    }

    @Override
    public List<Instant> getBlockedTimes(String userId, Instant rangeStart, Instant rangeEnd) {
        List<Date> legacyTimes = legacy.getBlockedTimes(
            userId, Date.from(rangeStart), Date.from(rangeEnd));
        return legacyTimes.stream()
            .map(Date::toInstant)
            .toList();
    }
}
```

---

## Gradual Migration Strategy

```java
// Step 1: Add modern methods alongside legacy ones
public class MeetingRepository {
    
    // Legacy method — keep for now, mark deprecated
    @Deprecated(since = "2.0", forRemoval = true)
    public Date getMeetingTime(long meetingId) {
        return Date.from(getMeetingInstant(meetingId));
    }

    // New method — all new code uses this
    public Instant getMeetingInstant(long meetingId) {
        // actual implementation
        return queryDatabase(meetingId);
    }
}
```

```java
// Step 2: Utility class for the transition period
public final class TimeConversions {
    private TimeConversions() {}

    public static Instant fromLegacy(Date date) {
        return date != null ? date.toInstant() : null;
    }

    public static Date toLegacy(Instant instant) {
        return instant != null ? Date.from(instant) : null;
    }

    public static ZonedDateTime fromLegacy(Calendar cal) {
        if (cal == null) return null;
        return cal.toInstant().atZone(cal.getTimeZone().toZoneId());
    }

    public static LocalDate fromLegacy(java.sql.Date sqlDate) {
        return sqlDate != null ? sqlDate.toLocalDate() : null;
    }
}
```

---

## Handling Third-Party Libraries

Some libraries still return `Date`. Wrap at the boundary:

```java
// JWT library returns Date for expiration
public class TokenService {
    
    public Instant getTokenExpiry(String token) {
        Claims claims = Jwts.parser()
            .setSigningKey(key)
            .parseClaimsJws(token)
            .getBody();
        
        // JWT library returns java.util.Date
        Date expiration = claims.getExpiration();
        return expiration.toInstant();
    }

    public boolean isTokenExpired(String token) {
        Instant expiry = getTokenExpiry(token);
        return Instant.now().isAfter(expiry);
    }
}
```

---

## TimeZone ↔ ZoneId

```java
import java.util.TimeZone;
import java.time.ZoneId;

// TimeZone → ZoneId
TimeZone legacyTz = TimeZone.getTimeZone("America/New_York");
ZoneId modern = legacyTz.toZoneId();

// ZoneId → TimeZone
ZoneId zone = ZoneId.of("Europe/London");
TimeZone backToLegacy = TimeZone.getTimeZone(zone);

// Watch out: invalid TimeZone silently returns GMT
TimeZone bad = TimeZone.getTimeZone("Invalid/Zone");
System.out.println(bad.getID()); // "GMT" — no error!

// ZoneId throws an exception for invalid zones
// ZoneId.of("Invalid/Zone"); // ZoneRulesException!
```

---

## Common Pitfalls

```java
// PITFALL 1: Date.getHours() uses system timezone
Date date = new Date(1710957600000L);
int hour = date.getHours(); // Depends on JVM timezone! Don't use.

// CORRECT: Convert to ZonedDateTime first
int hour = date.toInstant()
    .atZone(ZoneId.of("America/New_York"))
    .getHour();

// PITFALL 2: SimpleDateFormat is not thread-safe
// WRONG: shared static instance
static SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");

// CORRECT: DateTimeFormatter IS thread-safe
static DateTimeFormatter fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd");

// PITFALL 3: Calendar months are 0-indexed
Calendar cal = Calendar.getInstance();
cal.set(2024, 2, 20); // This is MARCH, not February!

// Modern API: months are 1-indexed (sane)
LocalDate date = LocalDate.of(2024, 3, 20); // March 20
```

---

## What You Learned

- `Date.toInstant()` and `Date.from(Instant)` are your primary bridge methods
- `Calendar` converts via `.toInstant().atZone(zone)`
- `java.sql.Timestamp` has `toInstant()` and `toLocalDateTime()`
- Wrap legacy APIs with a bridge class that exposes modern types
- Migrate gradually: add modern methods, deprecate old ones, remove later
- `TimeZone.getTimeZone()` silently returns GMT for invalid zones — `ZoneId.of()` throws
- `DateTimeFormatter` is thread-safe; `SimpleDateFormat` is not
- Convert at the boundary, use modern types internally

---

*Next up: The grand finale. [Chapter 12](./chapter-12-patterns.md) pulls everything together with architecture patterns, testable time code, and the complete MeetSync time strategy.*
