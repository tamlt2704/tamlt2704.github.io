# Chapter 10 — Database & JSON

[← Daylight Saving Traps](./chapter-09-dst.md) | [Next: Legacy Interop →](./chapter-11-legacy.md)

---

## The Problem

MeetSync stores meeting times in Postgres. The schema uses `TIMESTAMP WITHOUT TIME ZONE`:

```sql
CREATE TABLE meetings (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255),
    start_time TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE
);
```

A London user creates a meeting at 9:00 AM GMT. It's stored as `2024-03-20 09:00:00`. A New York user queries it and sees `09:00:00` — but is that 9 AM London or 9 AM New York? The database doesn't know. The offset information was lost at insertion.

---

## The Storage Strategy

The fix: store everything as UTC, convert at the application layer.

```sql
-- Better schema
CREATE TABLE meetings (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255),
    start_time TIMESTAMP WITH TIME ZONE,  -- stores as UTC internally
    organizer_zone VARCHAR(50),            -- "Europe/London"
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

Postgres `TIMESTAMP WITH TIME ZONE` converts to UTC on storage and back on retrieval. It doesn't store the original offset — it normalizes to UTC.

---

## JDBC Mapping

Modern JDBC (4.2+) maps Java Time types directly:

```java
import java.sql.*;
import java.time.*;

// Writing an Instant as TIMESTAMP WITH TIME ZONE
public void saveMeeting(Connection conn, String title, Instant startTime, ZoneId zone) 
        throws SQLException {
    String sql = "INSERT INTO meetings (title, start_time, organizer_zone) VALUES (?, ?, ?)";
    try (PreparedStatement ps = conn.prepareStatement(sql)) {
        ps.setString(1, title);
        ps.setObject(2, startTime.atOffset(ZoneOffset.UTC)); // OffsetDateTime
        ps.setString(3, zone.getId());
        ps.executeUpdate();
    }
}

// Reading back
public MeetingRecord loadMeeting(Connection conn, long id) throws SQLException {
    String sql = "SELECT title, start_time, organizer_zone FROM meetings WHERE id = ?";
    try (PreparedStatement ps = conn.prepareStatement(sql)) {
        ps.setLong(1, id);
        ResultSet rs = ps.executeQuery();
        if (rs.next()) {
            String title = rs.getString("title");
            OffsetDateTime odt = rs.getObject("start_time", OffsetDateTime.class);
            ZoneId zone = ZoneId.of(rs.getString("organizer_zone"));
            return new MeetingRecord(title, odt.toInstant(), zone);
        }
    }
    return null;
}
```

---

## The OffsetDateTime Bridge

JDBC works best with `OffsetDateTime`. Here's the conversion pattern:

```java
// Instant → OffsetDateTime (for JDBC writes)
Instant instant = Instant.now();
OffsetDateTime forDb = instant.atOffset(ZoneOffset.UTC);

// OffsetDateTime → Instant (after JDBC reads)
OffsetDateTime fromDb = rs.getObject("start_time", OffsetDateTime.class);
Instant restored = fromDb.toInstant();

// Display in user's timezone
ZonedDateTime userView = restored.atZone(ZoneId.of("America/New_York"));
```

---

## LocalDate and LocalTime in JDBC

```java
// Store a date-only field (birthdays, deadlines)
LocalDate birthday = LocalDate.of(1990, 5, 15);
ps.setObject(1, birthday); // maps to DATE column

// Read back
LocalDate fromDb = rs.getObject("birthday", LocalDate.class);

// Store a time-only field (business hours)
LocalTime openTime = LocalTime.of(9, 0);
ps.setObject(1, openTime); // maps to TIME column

// Read back
LocalTime fromDb = rs.getObject("open_time", LocalTime.class);
```

---

## Jackson Serialization

MeetSync's REST API uses Jackson. Without configuration, Java Time types serialize poorly:

```java
// Without JavaTimeModule — BROKEN
// {"startTime":{"seconds":1710957600,"nanos":0}}  ← useless object dump

// With JavaTimeModule — CORRECT
// {"startTime":"2024-03-20T18:00:00Z"}  ← clean ISO string
```

Setup:

```java
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

ObjectMapper mapper = new ObjectMapper();
mapper.registerModule(new JavaTimeModule());
mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
```

---

## Jackson Configuration in Spring Boot

```java
@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .disable(DeserializationFeature.ADJUST_DATES_TO_CONTEXT_TIME_ZONE);
    }
}
```

Or in `application.yml`:

```yaml
spring:
  jackson:
    serialization:
      write-dates-as-timestamps: false
    deserialization:
      adjust-dates-to-context-time-zone: false
```

---

## DTO Patterns

```java
public record MeetingResponse(
    Long id,
    String title,
    Instant startTime,        // Serializes as "2024-03-20T18:00:00Z"
    String organizerZone,     // "Europe/London"
    LocalDate date,           // Serializes as "2024-03-20"
    Duration duration         // Serializes as "PT1H" (ISO duration)
) {}

public record CreateMeetingRequest(
    String title,
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    LocalDateTime localTime,  // User's local time
    String timezone           // User's timezone ID
) {
    public Instant toInstant() {
        ZoneId zone = ZoneId.of(timezone);
        return localTime.atZone(zone).toInstant();
    }
}
```

---

## Custom Serializers

When the API contract requires a specific format:

```java
public class EpochMilliSerializer extends JsonSerializer<Instant> {
    @Override
    public void serialize(Instant value, JsonGenerator gen, SerializerProvider provider) 
            throws IOException {
        gen.writeNumber(value.toEpochMilli());
    }
}

public class EpochMilliDeserializer extends JsonDeserializer<Instant> {
    @Override
    public Instant deserialize(JsonParser p, DeserializationContext ctx) 
            throws IOException {
        return Instant.ofEpochMilli(p.getLongValue());
    }
}

// Usage on a field
public record LegacyEvent(
    @JsonSerialize(using = EpochMilliSerializer.class)
    @JsonDeserialize(using = EpochMilliDeserializer.class)
    Instant timestamp
) {}
// {"timestamp": 1710957600000}
```

---

## The Complete Storage Pattern

```java
@Entity
@Table(name = "meetings")
public class MeetingEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @Column(name = "start_time", columnDefinition = "TIMESTAMP WITH TIME ZONE")
    private Instant startTime;

    @Column(name = "organizer_zone")
    private String organizerZone;

    @Column(name = "created_at", columnDefinition = "TIMESTAMP WITH TIME ZONE")
    private Instant createdAt;

    @PrePersist
    void onCreate() {
        this.createdAt = Instant.now();
    }

    // Convert to user-facing view
    public ZonedDateTime getStartTimeInZone(ZoneId viewerZone) {
        return startTime.atZone(viewerZone);
    }

    public ZonedDateTime getStartTimeForOrganizer() {
        return startTime.atZone(ZoneId.of(organizerZone));
    }
}
```

---

## What You Learned

- Use `TIMESTAMP WITH TIME ZONE` in Postgres — it normalizes to UTC
- JDBC 4.2+ maps `OffsetDateTime` directly to timestamp columns
- Pattern: store as `Instant` (UTC), convert to `ZonedDateTime` for display
- Store the user's timezone ID separately if you need to reconstruct their local view
- Jackson's `JavaTimeModule` serializes Java Time types as ISO strings
- Disable `WRITE_DATES_AS_TIMESTAMPS` to get strings instead of numeric arrays
- Use `@JsonFormat` for field-level format control
- `LocalDate` maps to SQL `DATE`, `LocalTime` maps to SQL `TIME`

---

*Next up: Your codebase still has `java.util.Date` everywhere. [Chapter 11](./chapter-11-legacy.md) shows how to bridge old and new without a big-bang rewrite.*
