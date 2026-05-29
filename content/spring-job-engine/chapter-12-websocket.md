# Chapter 12: WebSocket Real-Time Updates

[← Chapter 11: Next.js Frontend](/blog/spring-job-engine/chapter-11-nextjs-frontend) | [Chapter 13: Scheduled Jobs →](/blog/spring-job-engine/chapter-13-scheduled-jobs)

---

## The Story

Users submit a job and stare at the screen hitting refresh. The dashboard polls every 5 seconds — wasteful and laggy. You need real-time: when a job hits 50%, the progress bar moves instantly.

WebSocket gives you a persistent, bidirectional connection between server and client.

## How It Fits

```
Current (polling):
  Client ──GET /api/jobs/id──▶ Server (every 5s)
  Client ◀── {progress: 30} ── Server
  Client ──GET /api/jobs/id──▶ Server (5s later)
  Client ◀── {progress: 35} ── Server

With WebSocket:
  Client ◀══════ persistent connection ══════▶ Server
  Server pushes: {progress: 30}
  Server pushes: {progress: 35}
  Server pushes: {progress: 40}  ← instant, no polling
```

## Step 1: WebSocket Configuration

```java
// config/WebSocketConfig.java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // Clients subscribe to /topic/* to receive messages
        registry.enableSimpleBroker("/topic");
        // Clients send messages to /app/* (handled by @MessageMapping)
        registry.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // WebSocket handshake endpoint — client connects here first
        registry.addEndpoint("/ws")
            .setAllowedOrigins("*")  // restrict in production
            .withSockJS();           // fallback for browsers without WebSocket
    }
}
```

### STOMP Protocol

WebSocket is just a transport — raw bytes. **STOMP** (Simple Text Oriented Messaging Protocol) adds structure on top:

| Concept                          | Purpose                                   |
| -------------------------------- | ----------------------------------------- |
| `CONNECT`                        | Client opens connection                   |
| `SUBSCRIBE /topic/jobs/job-7a3f` | Client says "I want updates for this job" |
| `SEND /app/...`                  | Client sends a message to server          |
| `MESSAGE`                        | Server pushes data to subscribed clients  |

Think of it as pub/sub over WebSocket.

## Step 2: Push Progress Updates

```java
// service/JobProgressNotifier.java
@Service
@RequiredArgsConstructor
public class JobProgressNotifier {

    private final SimpMessagingTemplate messaging;

    // Called from JobExecutor whenever progress changes
    public void notifyProgress(String jobId, int progress, JobStatus status) {
        messaging.convertAndSend(
            "/topic/jobs/" + jobId,
            Map.of(
                "jobId", jobId,
                "progress", progress,
                "status", status.name(),
                "timestamp", Instant.now()
            )
        );
    }

    // Broadcast to all subscribers watching the job list
    public void notifyAll(Job job) {
        messaging.convertAndSend("/topic/jobs", Map.of(
            "jobId", job.getId(),
            "status", job.getStatus().name(),
            "progress", job.getProgress()
        ));
    }
}
```

## Step 3: Integrate with Job Executor

Wire the notifier into the existing `doWork()` loop from Chapter 3:

```java
private void doWork(Job job) throws InterruptedException {
    for (int i = 0; i <= 100; i += 10) {
        if (Thread.currentThread().isInterrupted()) {
            throw new InterruptedException("Job cancelled");
        }
        job.setProgress(i);
        jobService.updateProgress(job.getId(), i);
        // Push to WebSocket subscribers instantly
        progressNotifier.notifyProgress(job.getId(), i, JobStatus.RUNNING);
        Thread.sleep(500);
    }
}
```

On completion/failure, notify status change:

```java
jobService.transition(job.getId(), JobStatus.COMPLETED);
progressNotifier.notifyProgress(job.getId(), 100, JobStatus.COMPLETED);
```

## Step 4: JWT Authentication for WebSocket

WebSocket connections need auth too. The handshake is an HTTP upgrade — intercept it:

```java
// security/WebSocketAuthInterceptor.java
@Component
public class WebSocketAuthInterceptor implements ChannelInterceptor {

    private final JwtTokenProvider tokenProvider;

    @Override
    public Message<?> preSend(Message<?> message, MessageChannel channel) {
        StompHeaderAccessor accessor = StompHeaderAccessor.wrap(message);

        if (StompCommand.CONNECT.equals(accessor.getCommand())) {
            String token = accessor.getFirstNativeHeader("Authorization");
            if (token != null && token.startsWith("Bearer ")) {
                Claims claims = tokenProvider.parseToken(token.substring(7));
                accessor.setUser(new StompPrincipal(claims.getSubject()));
            }
        }
        return message;
    }
}
```

```java
// security/StompPrincipal.java
public record StompPrincipal(String name) implements java.security.Principal {
    @Override
    public String getName() { return name; }
}
```

```java
// Register the interceptor
@Override
public void configureClientInboundChannel(ChannelRegistration registration) {
    registration.interceptors(webSocketAuthInterceptor);
}
```

## Step 5: Frontend (Next.js + STOMP)

```typescript
// hooks/useJobProgress.ts
import { Client } from "@stomp/stompjs";
import { useEffect, useState } from "react";

export function useJobProgress(jobId: string) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("QUEUED");

  useEffect(() => {
    const client = new Client({
      brokerURL: "ws://localhost:8080/ws",
      connectHeaders: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      onConnect: () => {
        client.subscribe(`/topic/jobs/${jobId}`, (message) => {
          const data = JSON.parse(message.body);
          setProgress(data.progress);
          setStatus(data.status);
        });
      },
    });

    client.activate();
    return () => {
      client.deactivate();
    };
  }, [jobId]);

  return { progress, status };
}
```

```tsx
// components/JobProgressBar.tsx
function JobProgressBar({ jobId }: { jobId: string }) {
  const { progress, status } = useJobProgress(jobId);

  return (
    <div>
      <div className="progress-bar" style={{ width: `${progress}%` }} />
      <span>
        {status} — {progress}%
      </span>
    </div>
  );
}
```

## Step 6: Spring Integration + WebSocket

You can also wire WebSocket as an outbound channel in your integration flow:

```java
@Bean
public IntegrationFlow webSocketNotificationFlow() {
    return IntegrationFlow
        .from("jobCompletionChannel")
        .handle(message -> {
            Job job = (Job) message.getPayload();
            progressNotifier.notifyAll(job);
        })
        .get();
}
```

Now every job completion automatically pushes to all connected WebSocket clients.

## Key Concepts

| Concept               | What                                                               |
| --------------------- | ------------------------------------------------------------------ |
| WebSocket             | Persistent bidirectional TCP connection                            |
| STOMP                 | Messaging protocol on top of WebSocket (subscribe/publish)         |
| SimpMessagingTemplate | Spring's API to push messages to subscribers                       |
| SockJS                | Fallback for environments that block WebSocket (uses long-polling) |
| /topic/\*             | Broadcast destinations (one-to-many)                               |
| /queue/\*             | Point-to-point destinations (one-to-one)                           |

## Scaling WebSocket

With multiple instances, a client connects to Instance A but the job runs on Instance B. Solutions:

| Approach                  | How                                                                          |
| ------------------------- | ---------------------------------------------------------------------------- |
| **Redis pub/sub broker**  | Replace simple broker with Redis — all instances share subscriptions         |
| **RabbitMQ/Kafka broker** | Use a full external broker as the STOMP relay                                |
| **Sticky sessions**       | Load balancer routes same client to same instance (simplest, least scalable) |

```java
// Use Redis as the message broker (production setup)
@Override
public void configureMessageBroker(MessageBrokerRegistry registry) {
    registry.enableStompBrokerRelay("/topic", "/queue")
        .setRelayHost("redis-host")
        .setRelayPort(61613);
}
```

---

[Chapter 13: Scheduled & Recurring Jobs →](/blog/spring-job-engine/chapter-13-scheduled-jobs)
