# Chapter 1: Docker Basics

[← Overview](./chapter-00-overview.md) | [Next: Docker Images →](./chapter-02-images.md)

---

## What is Docker?

Docker is a platform that packages applications and their dependencies into lightweight, portable **containers**. A container runs the same way regardless of the host environment — solving the "it works on my machine" problem.

## Containers vs Virtual Machines

| Feature     | Container          | Virtual Machine          |
| ----------- | ------------------ | ------------------------ |
| Boot time   | Seconds            | Minutes                  |
| Size        | MBs                | GBs                      |
| OS          | Shares host kernel | Full guest OS            |
| Isolation   | Process-level      | Hardware-level           |
| Performance | Near-native        | Overhead from hypervisor |

Containers share the host OS kernel and isolate processes using namespaces and cgroups. VMs run a full guest OS on top of a hypervisor.

## Installing Docker Desktop

**Windows:**

1. Download Docker Desktop from https://docs.docker.com/desktop/install/windows-install/
2. Run the installer
3. Enable WSL 2 backend when prompted
4. Restart your machine
5. Verify:

```bash
docker --version
```

**macOS:**

1. Download from https://docs.docker.com/desktop/install/mac-install/
2. Drag to Applications
3. Launch Docker Desktop
4. Verify:

```bash
docker --version
```

**Linux (Ubuntu):**

```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker your-username
```

Log out and back in, then verify:

```bash
docker --version
```

## Your First Container

```bash
docker run hello-world
```

This command:

1. Checks for the `hello-world` image locally
2. Pulls it from Docker Hub if not found
3. Creates a container from the image
4. Runs the container (prints a message)
5. Container exits

## Key Commands

### Run a container

```bash
# Run an interactive Ubuntu container
docker run -it ubuntu bash

# Run nginx in the background (detached)
docker run -d -p 8080:80 --name my-nginx nginx

# Run and auto-remove when stopped
docker run --rm -it alpine sh
```

### List containers

```bash
# Running containers
docker ps

# All containers (including stopped)
docker ps -a
```

### Stop and remove containers

```bash
# Stop a running container
docker stop my-nginx

# Remove a stopped container
docker rm my-nginx

# Force remove a running container
docker rm -f my-nginx

# Remove all stopped containers
docker container prune
```

### Manage images

```bash
# List local images
docker images

# Pull an image
docker pull python:3.12

# Remove an image
docker rmi python:3.12

# Remove unused images
docker image prune
```

### Inspect and logs

```bash
# View container logs
docker logs my-nginx

# Follow logs in real-time
docker logs -f my-nginx

# Inspect container details
docker inspect my-nginx

# Execute a command in a running container
docker exec -it my-nginx bash
```

## Exercises

1. Run an nginx container on port 9090 and visit http://localhost:9090 in your browser
2. Run a Python container interactively and execute `print("Hello Docker")`
3. List all running containers, stop them, then remove them
4. Pull the `alpine` image and check its size with `docker images`
5. Run two nginx containers with different names and ports, then clean them both up

---

[← Overview](./chapter-00-overview.md) | [Next: Docker Images →](./chapter-02-images.md)
