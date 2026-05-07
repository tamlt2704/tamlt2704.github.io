# Chapter 14: Middleware, CORS & Rate Limiting

[← Chapter 13: Testing](chapter-13-testing.md) | [Chapter 15: Deployment →](chapter-15-deployment.md)

---

## The Task

Nia: "The frontend is on `localhost:3000`, the API on `localhost:8000`. CORS blocks everything. Also, I need request logging, rate limiting, and security headers. Before you deploy."

---

## CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://pulseboard.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Custom Middleware: Request Logging

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)"
        )
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        return response

app.add_middleware(LoggingMiddleware)
```

---

## Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, ...):
    ...
```

5 login attempts per minute per IP. Prevents brute-force attacks.

---

## Security Headers

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

---

## Middleware Execution Order

```
Request → SecurityHeaders → Logging → CORS → Route Handler
Response ← SecurityHeaders ← Logging ← CORS ← Route Handler
```

Middleware wraps like layers. Last added = outermost (runs first on request, last on response).

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Middleware                      │ What It Does
────────────────────────────────┼──────────────────────────────────────
CORSMiddleware                  │ Allow cross-origin requests
BaseHTTPMiddleware              │ Custom request/response processing
@limiter.limit("N/period")      │ Rate limiting per IP
Security headers                │ Prevent XSS, clickjacking, etc.
app.add_middleware(Class)       │ Register middleware
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 13: Testing](chapter-13-testing.md) | [Chapter 15: Deployment →](chapter-15-deployment.md)
