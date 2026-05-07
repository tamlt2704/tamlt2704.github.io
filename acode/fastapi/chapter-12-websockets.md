# Chapter 12: WebSockets — Real-Time Updates

[← Chapter 11: Background Tasks](chapter-11-background-tasks.md) | [Chapter 13: Testing →](chapter-13-testing.md)

---

## The Task

Marcus: "When someone moves a task to 'done', everyone viewing that project board should see it update instantly. No refresh. Real-time."

---

## WebSocket Endpoint

```python
# app/routers/ws.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json


class ConnectionManager:
    def __init__(self):
        # project_id → set of connected websockets
        self.connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: int):
        await websocket.accept()
        if project_id not in self.connections:
            self.connections[project_id] = set()
        self.connections[project_id].add(websocket)

    def disconnect(self, websocket: WebSocket, project_id: int):
        self.connections.get(project_id, set()).discard(websocket)

    async def broadcast(self, project_id: int, message: dict):
        connections = self.connections.get(project_id, set())
        for ws in connections.copy():
            try:
                await ws.send_json(message)
            except Exception:
                connections.discard(ws)


manager = ConnectionManager()


@router.websocket("/ws/projects/{project_id}")
async def project_websocket(websocket: WebSocket, project_id: int):
    await manager.connect(websocket, project_id)
    try:
        while True:
            # Keep connection alive, receive pings
            data = await websocket.receive_text()
            # Could handle client messages here
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
```

---

## Broadcasting Changes

When a task is updated, notify all connected clients:

```python
@router.patch("/{task_id}")
async def update_task(task_id: int, update: TaskUpdate, ...):
    # ... update the task ...

    # Broadcast to all viewers of this project
    await manager.broadcast(task.project_id, {
        "type": "task_updated",
        "task": TaskResponse.model_validate(task).model_dump(mode="json"),
    })

    return task
```

---

## Frontend Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/projects/1');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'task_updated') {
        updateTaskInUI(data.task);
    }
};
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
@router.websocket("/ws/...")     │ WebSocket endpoint
websocket.accept()              │ Accept the connection
websocket.send_json(data)       │ Send data to client
websocket.receive_text()        │ Wait for client message
WebSocketDisconnect             │ Client disconnected
ConnectionManager               │ Track & broadcast to connections
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 11: Background Tasks](chapter-11-background-tasks.md) | [Chapter 13: Testing →](chapter-13-testing.md)
