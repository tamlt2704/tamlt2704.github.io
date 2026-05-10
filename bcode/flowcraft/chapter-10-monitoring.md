# Chapter 10: Live Monitoring via WebSocket

[← Chapter 9: Deploy from UI](chapter-09-deploy-ui.md) | [Chapter 11: Error Handling →](chapter-11-error-handling.md)

---

## Goal

Show real-time metrics on the canvas — messages flowing through edges, throughput counters on nodes, error indicators. By the end: when a message passes through a deployed flow, the UI animates it live.

## Architecture

```
Spring Integration Flow
    │ (message passes through)
    ▼
Micrometer Metrics + Channel Interceptor
    │ (captures event)
    ▼
WebSocket (STOMP)
    │ (pushes to browser)
    ▼
React Flow Canvas
    │ (animates edge, updates counter)
    ▼
User sees live data flow
```

## Step 1: WebSocket Configuration (Backend)

**src/main/kotlin/com/flowcraft/config/WebSocketConfig.kt:**
```kotlin
package com.flowcraft.config

import org.springframework.context.annotation.Configuration
import org.springframework.messaging.simp.config.MessageBrokerRegistry
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker
import org.springframework.web.socket.config.annotation.StompEndpointRegistry
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer

@Configuration
@EnableWebSocketMessageBroker
class WebSocketConfig : WebSocketMessageBrokerConfigurer {

    override fun configureMessageBroker(registry: MessageBrokerRegistry) {
        registry.enableSimpleBroker("/topic")  // Clients subscribe here
        registry.setApplicationDestinationPrefixes("/app")
    }

    override fun registerStompEndpoints(registry: StompEndpointRegistry) {
        registry.addEndpoint("/ws")
            .setAllowedOrigins("http://localhost:5173")
            .withSockJS()
    }
}
```

## Step 2: Flow Event Model

**src/main/kotlin/com/flowcraft/monitoring/FlowEvent.kt:**
```kotlin
package com.flowcraft.monitoring

import java.time.Instant

data class FlowEvent(
    val flowId: String,
    val nodeId: String,
    val type: EventType,
    val timestamp: Instant = Instant.now(),
    val payload: String? = null,      // Truncated payload preview
    val durationMs: Long? = null,     // Processing time
    val error: String? = null,
)

enum class EventType {
    MESSAGE_RECEIVED,   // Message entered a node
    MESSAGE_SENT,       // Message left a node
    MESSAGE_FILTERED,   // Message was discarded by filter
    ERROR,              // Processing error
}
```

## Step 3: Channel Interceptor (Capture Events)

Spring Integration lets you intercept messages on any channel:

**src/main/kotlin/com/flowcraft/monitoring/FlowMonitorInterceptor.kt:**
```kotlin
package com.flowcraft.monitoring

import org.springframework.integration.channel.interceptor.GlobalChannelInterceptor
import org.springframework.messaging.Message
import org.springframework.messaging.MessageChannel
import org.springframework.messaging.simp.SimpMessagingTemplate
import org.springframework.messaging.support.ChannelInterceptor
import org.springframework.stereotype.Component
import java.time.Instant

@Component
@GlobalChannelInterceptor(patterns = ["flow-*"])  // Only intercept flow channels
class FlowMonitorInterceptor(
    private val messagingTemplate: SimpMessagingTemplate,
) : ChannelInterceptor {

    override fun preSend(message: Message<*>, channel: MessageChannel): Message<*> {
        // Extract flow and node info from channel name or message headers
        val channelName = channel.toString()
        val flowId = message.headers["flowcraft.flowId"] as? String ?: "unknown"
        val nodeId = message.headers["flowcraft.nodeId"] as? String ?: "unknown"

        val event = FlowEvent(
            flowId = flowId,
            nodeId = nodeId,
            type = EventType.MESSAGE_RECEIVED,
            payload = message.payload.toString().take(200), // Truncate for safety
        )

        // Push to WebSocket subscribers
        messagingTemplate.convertAndSend("/topic/flow/$flowId", event)

        return message
    }

    override fun afterSendCompletion(
        message: Message<*>,
        channel: MessageChannel,
        sent: Boolean,
        ex: Exception?
    ) {
        val flowId = message.headers["flowcraft.flowId"] as? String ?: return

        if (ex != null) {
            val event = FlowEvent(
                flowId = flowId,
                nodeId = message.headers["flowcraft.nodeId"] as? String ?: "unknown",
                type = EventType.ERROR,
                error = ex.message,
            )
            messagingTemplate.convertAndSend("/topic/flow/$flowId", event)
        }
    }
}
```

## Step 4: Inject Tracking Headers in Compiler

Update the flow compiler to add tracking headers at each node:

```kotlin
// In FlowCompiler, wrap each node's adapter call:
private fun applyNodeWithTracking(
    flow: IntegrationFlowDefinition<*>,
    node: NodeDefinition,
    flowId: String
) {
    // Add tracking headers before the node processes
    flow.enrich { enricher ->
        enricher.header("flowcraft.flowId", flowId)
        enricher.header("flowcraft.nodeId", node.id)
        enricher.header("flowcraft.nodeType", node.type)
    }

    // Apply the actual node logic
    applyNode(flow, node)
}
```

## Step 5: Frontend WebSocket Client

**src/hooks/useFlowEvents.ts:**
```ts
import { useEffect, useRef, useCallback } from 'react';
import { Client } from '@stomp/stompjs';
import SockJS from 'sockjs-client';

export interface FlowEvent {
  flowId: string;
  nodeId: string;
  type: 'MESSAGE_RECEIVED' | 'MESSAGE_SENT' | 'MESSAGE_FILTERED' | 'ERROR';
  timestamp: string;
  payload?: string;
  durationMs?: number;
  error?: string;
}

export function useFlowEvents(
  flowId: string | null,
  onEvent: (event: FlowEvent) => void
) {
  const clientRef = useRef<Client | null>(null);

  useEffect(() => {
    if (!flowId) return;

    const client = new Client({
      webSocketFactory: () => new SockJS('http://localhost:8080/ws'),
      onConnect: () => {
        client.subscribe(`/topic/flow/${flowId}`, (message) => {
          const event: FlowEvent = JSON.parse(message.body);
          onEvent(event);
        });
      },
      onStompError: (frame) => {
        console.error('STOMP error:', frame.headers['message']);
      },
    });

    client.activate();
    clientRef.current = client;

    return () => {
      client.deactivate();
    };
  }, [flowId, onEvent]);
}
```

Install dependencies:
```bash
npm install @stomp/stompjs sockjs-client
npm install -D @types/sockjs-client
```

## Step 6: Animate the Canvas

Update nodes to show live counters and edges to pulse on message flow:

**src/hooks/useFlowMonitor.ts:**
```ts
import { useState, useCallback } from 'react';
import { useFlowEvents, type FlowEvent } from './useFlowEvents';
import { useFlowStore } from '../store/flowStore';

interface NodeMetrics {
  messageCount: number;
  lastMessage: string | null;
  hasError: boolean;
  lastEventTime: number;
}

export function useFlowMonitor(flowId: string | null) {
  const [metrics, setMetrics] = useState<Record<string, NodeMetrics>>({});
  const [activeEdges, setActiveEdges] = useState<Set<string>>(new Set());

  const edges = useFlowStore(s => s.edges);

  const handleEvent = useCallback((event: FlowEvent) => {
    // Update node metrics
    setMetrics(prev => ({
      ...prev,
      [event.nodeId]: {
        messageCount: (prev[event.nodeId]?.messageCount ?? 0) + 1,
        lastMessage: event.payload ?? null,
        hasError: event.type === 'ERROR',
        lastEventTime: Date.now(),
      },
    }));

    // Animate the incoming edge
    if (event.type === 'MESSAGE_RECEIVED') {
      const incomingEdge = edges.find(e => e.target === event.nodeId);
      if (incomingEdge) {
        setActiveEdges(prev => new Set([...prev, incomingEdge.id]));
        // Remove animation after 500ms
        setTimeout(() => {
          setActiveEdges(prev => {
            const next = new Set(prev);
            next.delete(incomingEdge.id);
            return next;
          });
        }, 500);
      }
    }
  }, [edges]);

  useFlowEvents(flowId, handleEvent);

  return { metrics, activeEdges };
}
```

## Step 7: Live Node Component

Update the node components to show metrics:

```tsx
// In InputNode.tsx (and similar for Process/Output):
export function InputNode({ data, id }: NodeProps) {
  const metrics = useFlowStore(s => s.nodeMetrics?.[id]);

  return (
    <div className={`... ${metrics?.hasError ? 'border-red-500 animate-pulse' : ''}`}>
      {/* ... existing content ... */}

      {/* Live counter badge */}
      {metrics && metrics.messageCount > 0 && (
        <div className="absolute -top-2 -right-2 bg-blue-500 text-white
          text-xs rounded-full w-5 h-5 flex items-center justify-center">
          {metrics.messageCount}
        </div>
      )}

      {/* Pulse animation on recent activity */}
      {metrics && Date.now() - metrics.lastEventTime < 1000 && (
        <div className="absolute inset-0 rounded-lg border-2 border-blue-400
          animate-ping opacity-30 pointer-events-none" />
      )}

      {/* ... handles ... */}
    </div>
  );
}
```

## Step 8: Animated Edge on Message Flow

Update the FlowEdge to pulse when a message passes:

```tsx
export function FlowEdge({ id, ...props }: EdgeProps) {
  const isActive = useFlowStore(s => s.activeEdges?.has(id));

  return (
    <>
      <BaseEdge
        path={edgePath}
        style={{
          strokeWidth: isActive ? 3 : 2,
          stroke: isActive ? '#3b82f6' : '#6b7280',
          transition: 'all 0.3s ease',
        }}
      />
      {/* Fast-moving dot when active */}
      {isActive && (
        <circle r="5" fill="#3b82f6">
          <animateMotion dur="0.5s" repeatCount="1" path={edgePath} />
        </circle>
      )}
    </>
  );
}
```

## What It Looks Like

```
Flow is deployed and receiving requests:

  ┌──────────┐         ┌──────────┐         ┌──────────┐
  │ 🌐 HTTP  │───●────→│ 🔄 Trans │───●────→│ 🗄️ DB   │
  │  [42] ✓  │  pulse  │  [42] ✓  │  pulse  │  [42] ✓  │
  └──────────┘         └──────────┘         └──────────┘

  ● = animated dot traveling along edge
  [42] = message counter badge
  ✓ = healthy (green border)
```

When an error occurs:
```
  ┌──────────┐         ┌──────────┐         ┌──────────┐
  │ 🌐 HTTP  │─────────│ 🔄 Trans │─────────│ 🗄️ DB   │
  │  [43] ✓  │         │  [43] ⚠️  │  RED    │  [42] ✓  │
  └──────────┘         └──────────┘         └──────────┘
                        ↑ pulsing red border
```

## Key Takeaways

1. **WebSocket (STOMP)** pushes events from backend to frontend in real-time
2. **Channel interceptors** capture message flow without modifying business logic
3. **Tracking headers** let us correlate events to specific nodes and flows
4. **CSS animations** (pulse, ping) give visual feedback without heavy JS
5. **SVG animateMotion** moves dots along edges with zero JS overhead
6. **This is the "wow factor"** — seeing data flow live through your visual pipeline

---

[← Chapter 9: Deploy from UI](chapter-09-deploy-ui.md) | [Chapter 11: Error Handling →](chapter-11-error-handling.md)
