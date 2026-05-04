# Docker 101 — Animated with Manim

Visual explanations of Docker concepts. Each episode is a ~5 minute Manim animation showing what actually happens when you run Docker commands — containers as boxes, images as layers, networks as pipes.

## Episodes

| # | Title | The Visual | Concepts |
|---|---|---|---|
| 00 | What is Docker? | App trapped in "works on my machine" → container saves it | Problem Docker solves, containers vs VMs |
| 01 | Images & Containers | Image = blueprint (layers stacking), Container = running instance | `docker pull`, `docker run`, `docker ps` |
| 02 | The Dockerfile | Lines of code → layers building on top of each other | `FROM`, `COPY`, `RUN`, `CMD`, `docker build` |
| 03 | Volumes | Container dies → data gone. Volume = external hard drive plugged in | `-v`, named volumes, bind mounts |
| 04 | Networking | Containers as houses, networks as roads connecting them | `bridge`, `host`, port mapping `-p` |
| 05 | Docker Compose | Orchestra conductor waving baton, services start in order | `docker-compose.yml`, `up`, `down`, `depends_on` |
| 06 | Multi-stage Builds | Fat image → diet → slim image (layers shrinking) | Build stage vs runtime stage, image size |
| 07 | Docker Hub & Registry | Warehouse shelves with image boxes, push/pull arrows | `docker push`, `docker pull`, tags, private registry |
| 08 | Health Checks & Logs | Heartbeat monitor on container, log stream flowing | `HEALTHCHECK`, `docker logs`, restart policies |
| 09 | Docker in Production | Single container → swarm of containers across servers | Scaling, load balancing, orchestration intro |

## Render

```bash
pip install manim
manim -pqh ep00_what_is_docker.py WhatIsDocker
```

## Visual Style

- Dark background (`#0d0d0d`)
- Containers = rounded rectangles with colored borders
- Images = stacked layers (like a cake)
- Networks = dashed lines connecting containers
- Commands = monospace code appearing on screen
- Arrows show data flow
