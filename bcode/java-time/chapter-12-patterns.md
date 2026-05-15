# Chapter 12 — Patterns & Best Practices

[← Legacy Interop](./chapter-11-legacy.md)

---

## The Problem

MeetSync's test suite is flaky. Tests that check "meeting is in the future" pass at 10 AM but fail at 11:59 PM. Tests that verify "subscription expires in 30 days" break on the last day of the month. The root cause: code calls `Instant.now()` and `LocalDate.now()` directly, making it impossible to control time in tests.

```java
// This test is a ticking time bomb
@Test
void meetingShouldBeInFuture() {
    Meeting meeting = new Meeting(
        LocalDateTime.of(2024, 3, 20, 14, 0) // hardcoded date
    );
    assertTrue(meeting.isInFuture()); // fails after March 20, 2024
}
```

---

## Clock Injection

Java's `Clock` class is the solution. Instead of calling `now()` directly, inject a `Clock`:

```java
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;

public class MeetingService {
    private final Clock clock;

    // Production: inject Clock.systemUTC()
    public MeetingService(Clock clock) {
        this.clock = clock;
    }

    public boolean isMeetingInFuture(Instant meetingTime) {
        return meetingTime.isAfter(Instant.now(clock));
    }

    public Instant getCurrentTime() {
        return Instant.now(clock);
    }
}
```

---

## Clock.fixed() for Testing

```java
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;

@Test
void meetingInFuture_whenBeforeMeetingTime_returnsTrue() {
    // Fix time to March 20, 2024 at 10:00 UTC
    Clock fixedClock = Clock.fixed(
        Instant.parse("2024-03-20T10:00:00Z"),
        ZoneOffset.UTC
    );
    
    MeetingService service = new MeetingService(fixedClock);
    Instant meetingAt2pm = Instant.parse("2024-03-20T14:00:00Z");
    
    assertTrue(service.isMeetingInFuture(meetingAt2pm)); // always passes
}

@Test
void meetingInFuture_whenAfterMeetingTime_returnsFalse() {
    Clock fixedClock = Clock.fixed(
        Instant.parse("2024-03-20T16:00:00Z"),
        ZoneOffset.UTC
    );
    
    MeetingService service = new MeetingService(fixedClock);
    Instant meetingAt2pm = Instant.parse("2024-03-20T14:00:00Z");
    
    assertFalse(service.isMeetingInFuture(meetingAt2pm)); // always passes
}
```

---

## Clock Types

```java
// System clock (production)
Clock system = Clock.systemUTC();
Clock systemDefault = Clock.systemDefaultZone();
Clock systemTokyo = Clock.system(ZoneId.of("Asia/Tokyo"));

// Fixed clock (testing)
Clock fixed = Clock.fixed(Instant.parse("2024-01-01T00:00:00Z"), ZoneOffset.UTC);

// Offset clock (simulate time travel)
Clock twoHoursAhead = Clock.offset(Clock.systemUTC(), Duration.ofHours(2));

// Tick clock (reduce precision)
Clock tickSeconds = Clock.tickSeconds(ZoneOffset.UTC); // truncates to seconds
Clock tickMinutes = Clock.tickMinutes(ZoneOffset.UTC); // truncates to minutes
```

---

## Spring Boot Configuration

```java
@Configuration
public class TimeConfig {

    @Bean
    public Clock clock() {
        return Clock.systemUTC();
    }
}

@Service
public class SubscriptionService {
    private final Clock clock;
    private final SubscriptionRepository repo;

    public SubscriptionService(Clock clock, SubscriptionRepository repo) {
        this.clock = clock;
        this.repo = repo;
    }

    public boolean isExpired(Subscription sub) {
        return Instant.now(clock).isAfter(sub.getExpiresAt());
    }

    public Subscription createTrial(String userId) {
        Instant now = Instant.now(clock);
        Instant trialEnd = now.plus(Duration.ofDays(14));
        return repo.save(new Subscription(userId, now, trialEnd));
    }
}
```

Test:

```java
@Test
void trialExpires14DaysAfterCreation() {
    Clock fixed = Clock.fixed(
        Instant.parse("2024-03-01T00:00:00Z"), ZoneOffset.UTC);
    SubscriptionService service = new SubscriptionService(fixed, mockRepo);

    Subscription trial = service.createTrial("user-123");

    assertEquals(
        Instant.parse("2024-03-15T00:00:00Z"),
        trial.getExpiresAt()
    );
}
```

---

## Architecture Rules

The MeetSync team established these rules after years of timezone bugs:

### Rule 1: Store as Instant, Display as ZonedDateTime

```java
// In the database layer
@Column(columnDefinition = "TIMESTAMP WITH TIME ZONE")
private Instant startTime;

// In the API layer
public ZonedDateTime getStartTimeForUser(ZoneId userZone) {
    return startTime.atZone(userZone);
}
```

### Rule 2: Never Call now() Without a Clock

```java
// BAD — untestable
public boolean isExpired() {
    return Instant.now().isAfter(this.expiresAt);
}

// GOOD — testable
public boolean isExpired(Clock clock) {
    return Instant.now(clock).isAfter(this.expiresAt);
}
```

### Rule 3: Accept User's Zone, Don't Assume It

```java
// BAD — assumes server timezone
ZonedDateTime.now()

// GOOD — explicit zone from user profile
ZonedDateTime.now(ZoneId.of(user.getTimezone()))
```

### Rule 4: Use Named Zones, Not Offsets

```java
// BAD — doesn't handle DST
ZoneId zone = ZoneId.of("+05:00");

// GOOD — handles DST transitions automatically
ZoneId zone = ZoneId.of("America/New_York");
```

---

## Common Mistakes

```java
// MISTAKE 1: Using LocalDateTime for cross-timezone scheduling
LocalDateTime meeting = LocalDateTime.now(); // Which timezone?!

// MISTAKE 2: Comparing dates with == instead of equals/isBefore/isAfter
if (date1 == date2) // WRONG — compares references

// MISTAKE 3: Ignoring DST when adding hours
ZonedDateTime zdt = ZonedDateTime.now(ZoneId.of("America/New_York"));
zdt.plusHours(24); // Not the same as plusDays(1) during DST!

// MISTAKE 4: Formatting without locale
DateTimeFormatter.ofPattern("MMMM d"); // Month name in which language?

// MISTAKE 5: Parsing user input without error handling
LocalDate.parse(userInput); // Throws DateTimeParseException!
```

---

## The Complete MeetSync Time Architecture

```java
/**
 * MeetSync Time Architecture:
 *
 * STORAGE:     Instant (UTC) in TIMESTAMP WITH TIME ZONE columns
 * INTERNAL:    Instant for all business logic
 * CONVERSION:  ZonedDateTime at the API boundary
 * DISPLAY:     Formatted string with user's locale and timezone
 * TESTING:     Clock injection everywhere
 * LEGACY:      Bridge classes at integration boundaries
 */

public class MeetingSyncArchitecture {
    private final Clock clock;
    private final MeetingRepository repo;

    // 1. User creates meeting in their local time
    public Meeting createMeeting(CreateMeetingRequest request) {
        ZoneId userZone = ZoneId.of(request.timezone());
        ZonedDateTime userTime = request.localTime().atZone(userZone);
        Instant utcTime = userTime.toInstant(); // normalize to UTC

        Meeting meeting = new Meeting();
        meeting.setStartTime(utcTime);
        meeting.setOrganizerZone(request.timezone());
        meeting.setCreatedAt(Instant.now(clock));
        return repo.save(meeting);
    }

    // 2. Another user views the meeting in their timezone
    public MeetingView getMeetingForUser(long meetingId, String viewerTimezone) {
        Meeting meeting = repo.findById(meetingId);
        ZoneId viewerZone = ZoneId.of(viewerTimezone);
        ZonedDateTime localView = meeting.getStartTime().atZone(viewerZone);

        return new MeetingView(
            meeting.getTitle(),
            localView,
            formatForDisplay(localView, viewerZone)
        );
    }

    // 3. Check if meeting is upcoming
    public boolean isUpcoming(Meeting meeting) {
        return meeting.getStartTime().isAfter(Instant.now(clock));
    }

    // 4. Format for display
    private String formatForDisplay(ZonedDateTime time, ZoneId zone) {
        return time.format(
            DateTimeFormatter.ofPattern("EEEE, MMMM d 'at' h:mm a (z)")
        );
    }
}
```

---

## Decision Flowchart

When choosing a type, ask:

1. **Is it just a date?** (birthday, holiday) → `LocalDate`
2. **Is it just a time?** (store hours, alarm) → `LocalTime`
3. **Is it a wall-clock reading with no zone needed?** → `LocalDateTime`
4. **Do multiple people in different zones need to agree?** → `ZonedDateTime` or `Instant`
5. **Is it a machine timestamp?** (logs, created_at) → `Instant`
6. **Is it for storage/comparison?** → `Instant`
7. **Is it for display to a human?** → `ZonedDateTime`

---

## What You Learned

- Inject `Clock` into services — never call `now()` directly in business logic
- `Clock.fixed()` makes time-dependent tests deterministic and fast
- Store as `Instant` (UTC), display as `ZonedDateTime` (user's zone)
- Use named zones (`"America/New_York"`) not offsets (`"-05:00"`)
- Accept the user's timezone explicitly — never assume the server's zone
- Bridge legacy `Date`/`Calendar` at integration boundaries
- The right type depends on the question: "when on the timeline?" vs "what does the clock show?"

---

## The MeetSync Journey: Complete

You started with a birthday bug and ended with a production-grade time architecture. Along the way:

| Chapter | Key Insight |
|---------|-------------|
| 1. LocalDate | A birthday is a date, not a timestamp |
| 2. LocalTime | Time comparison needs types, not strings |
| 3. LocalDateTime | No timezone = no point on the timeline |
| 4. ZonedDateTime | Same moment, different clocks |
| 5. Instant | The universal machine timestamp |
| 6. Duration & Period | "1 month" ≠ "30 days" |
| 7. Formatting | Store ISO, display human-readable |
| 8. Adjusters | Complex date rules without loops |
| 9. DST | 2:30 AM might not exist |
| 10. Persistence | UTC in, local out |
| 11. Legacy | Bridge, don't rewrite |
| 12. Patterns | Inject the clock, test with confidence |

Time is hard. But with the right types and patterns, it doesn't have to be a source of bugs.
