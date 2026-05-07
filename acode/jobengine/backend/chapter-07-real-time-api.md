# Chapter 7: The War Room Screen — Real-time API

[← Chapter 6: The Clone Wars](chapter-06-multiple-instances.md) | [Chapter 8: The Audit →](chapter-08-observability.md)

---

## The Incident

Captain Deadline installs a 65-inch TV in the office. "I want to see all jobs. Live. Green for done, red for failed, pulsing for running."

Right now, the only way to check job status is `curl http://localhost:8080/jobs/abc-123` in a loop. Karen has 12 terminal tabs doing exactly that. Every tab hits the database once per second. 12 tabs × 50 visible jobs = 600 DB queries per second from one person.

"That's barbaric," says Captain Deadline. "Push the data to me. Don't make me ask."

He's describing Server-Sent Events.

## SSE: The Server Pushes to You

### The Test

```java
@Test
void sseStream_shouldPushStatusChanges() {
    List<JobEvent> events = new CopyOnWriteArrayList<>();
    sseClient.connect("/jobs/stream", event -> events.add(event));

    Job job = jobRepository.save(new Job("CSV_IMPORT",
        "{\"file\": \"src/test/resources/small.csv\"}"));

    await().atMost(10, SECONDS).untilAsserted(() -> {
        List<String> statuses = events.stream()
            .filter(e -> e.getJobId().equals(job.getId()))
            .map(JobEvent::getStatus)
            .toList();
        assertTrue(statuses.contains("RUNNING"));
        assertTrue(statuses.contains("COMPLETED"));
    });
}
```

### The Fix

Spring's `SseEmitter` — the server holds the connection open and pushes events as they happen:

```java
@GetMapping(value = "/jobs/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public SseEmitter stream() {
    SseEmitter emitter = new SseEmitter(0L); // no timeout
    emitters.add(emitter);
    emitter.onCompletion(() -> emitters.remove(emitter));
    emitter.onTimeout(() -> emitters.remove(emitter));
    return emitter;
}

// Called whenever a job status changes
public void broadcast(JobEvent event) {
    for (SseEmitter emitter : emitters) {
        try {
            emitter.send(SseEmitter.event()
                .name("job-update")
                .data(event));
        } catch (IOException e) {
            emitters.remove(emitter);
        }
    }
}
```

Try it with curl — one terminal listens, another submits:

```bash
# Terminal 1: listen to the stream (stays open)
curl -N http://localhost:8080/jobs/stream

# Terminal 2: submit a job
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"CSV_IMPORT","payload":"{\"file\":\"orders.csv\"}"}'

# Terminal 1 prints:
# event: job-update
# data: {"jobId":"abc-123","status":"PENDING","timestamp":"..."}
#
# event: job-update
# data: {"jobId":"abc-123","status":"RUNNING","timestamp":"..."}
#
# event: job-update
# data: {"jobId":"abc-123","status":"COMPLETED","result":"500 rows","timestamp":"..."}
```

No polling. No wasted queries. Events arrive the instant they happen.

## Progress Streaming

### The Test

```java
@Test
void progressEvents_shouldStreamDuringImport() {
    List<JobEvent> events = new CopyOnWriteArrayList<>();
    sseClient.connect("/jobs/stream", event -> events.add(event));

    jobRepository.save(new Job("CSV_IMPORT",
        "{\"file\": \"src/test/resources/big.csv\", \"rows\": 10000}"));

    await().atMost(15, SECONDS).untilAsserted(() -> {
        List<JobEvent> progress = events.stream()
            .filter(e -> e.getProgress() != null)
            .toList();
        assertTrue(progress.size() > 3);
    });
}
```

The handler broadcasts progress every 1,000 rows:

```java
if (count % 1000 == 0) {
    eventBroadcaster.broadcast(new JobEvent(
        job.getId(), "PROGRESS", count + "/" + total));
}
```

```bash
# Terminal 1 output during a 10,000-row import:
# data: {"jobId":"abc-123","status":"PROGRESS","message":"1000/10000"}
# data: {"jobId":"abc-123","status":"PROGRESS","message":"2000/10000"}
# ...
# data: {"jobId":"abc-123","status":"COMPLETED","result":"10000 rows imported"}
```

## The Full API Cheat Sheet

Everything you can do with curl:

```bash
# Submit
curl -X POST http://localhost:8080/jobs \
  -d '{"type":"CSV_IMPORT","payload":"{\"file\":\"orders.csv\"}"}'

# Status
curl http://localhost:8080/jobs/abc-123

# Cancel / Pause / Resume
curl -X POST http://localhost:8080/jobs/abc-123/cancel
curl -X POST http://localhost:8080/jobs/abc-123/pause
curl -X POST http://localhost:8080/jobs/abc-123/resume

# Dead letter
curl http://localhost:8080/jobs?status=DEAD
curl -X POST http://localhost:8080/jobs/abc-123/resurrect

# Workflow DAG
curl http://localhost:8080/workflows/wf-001/dag

# Workers
curl http://localhost:8080/workers

# Stats
curl http://localhost:8080/stats

# Live stream
curl -N http://localhost:8080/jobs/stream
```

## What You Learned

- **Server-Sent Events** — `SseEmitter` for real-time push, no polling
- **Event broadcasting** — fan-out to all connected clients
- **Progress streaming** — live updates during long-running jobs
- **curl as a dashboard** — everything is API-first, frontend comes later

Captain Deadline hooks the 65-inch TV to a terminal running `curl -N`. It's not pretty, but it's real-time. He's satisfied. (The React dashboard is a separate project for another day.)

Next chapter: Captain Deadline hires a consultant who asks "where are your metrics?"

---

[← Chapter 6: The Clone Wars](chapter-06-multiple-instances.md) | [Chapter 8: The Audit →](chapter-08-observability.md)
