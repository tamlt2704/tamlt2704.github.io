# Chapter 13: Networking Basics

Ursina includes an experimental networking module for multiplayer prototypes. It uses a simple client/server model where the server relays messages between connected clients. Keep in mind this is experimental and best suited for LAN or small-scale projects.

```python
from ursina import *
from ursina.networking import *

# === SERVER (run in one terminal) ===
# server.py
app = Ursina(borderless=False)

server = EasyServer(port=25565)
players = {}

def on_client_connected(client):
    players[client] = Entity(model='cube', color=color.random_color())
    print(f'Player connected: {client}')

def on_client_disconnected(client):
    destroy(players.pop(client, None))

def on_message(client, message):
    if 'position' in message:
        players[client].position = message['position']
        # Relay to all other clients
        for c in server.clients:
            if c != client:
                server.send(c, {'id': str(client), 'position': message['position']})

server.on_client_connected = on_client_connected
server.on_client_disconnected = on_client_disconnected
server.on_message = on_message
app.run()
```

```python
# === CLIENT (run in another terminal) ===
# client.py
from ursina import *
from ursina.networking import *

app = Ursina(borderless=False)
client = EasyClient(host='localhost', port=25565)
player = Entity(model='cube', color=color.orange)

def update():
    player.x += (held_keys['d'] - held_keys['a']) * 5 * time.dt
    player.z += (held_keys['w'] - held_keys['s']) * 5 * time.dt
    client.send({'position': (player.x, player.y, player.z)})

EditorCamera()
app.run()
```

## Key Points

- **EasyServer(port)**: creates a server that listens for connections
- **EasyClient(host, port)**: connects to a server
- **server.send(client, message)**: send a dict to a specific client
- **client.send(message)**: send a dict to the server
- Messages are Python dicts — keep them small for performance
- Ursina networking is **experimental** — fine for prototypes, not production

## What You Learned

- How to set up a basic client/server architecture in Ursina
- How to sync entity positions between players
- The callback pattern for connection/disconnection/messages
- That Ursina networking is experimental and best for LAN play

---

[← Chapter 12: Particles & Effects](chapter-12-particles.md) | [Next → Chapter 14: Build & Distribute](chapter-14-build.md)
