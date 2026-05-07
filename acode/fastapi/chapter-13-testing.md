# Chapter 13: Testing — TestClient & Fixtures

[← Chapter 12: WebSockets](chapter-12-websockets.md) | [Chapter 14: Middleware →](chapter-14-middleware.md)

---

## The Task

Dani: "No tests, no deploy. I need unit tests for validation, integration tests for endpoints, and a test database that doesn't touch production."

---

## Setup

```bash
pip install pytest pytest-asyncio httpx
```

---

## TestClient: Integration Tests

```python
# tests/test_projects.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db, Base, engine


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_client(client: AsyncClient):
    # Register and login
    await client.post("/auth/register", json={
        "email": "test@test.com", "name": "Test", "password": "Test1234"
    })
    response = await client.post("/auth/login", data={
        "username": "test@test.com", "password": "Test1234"
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.mark.asyncio
async def test_create_project(auth_client: AsyncClient):
    response = await auth_client.post("/projects", json={
        "name": "Test Project",
        "description": "A test",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_project_validation(auth_client: AsyncClient):
    response = await auth_client.post("/projects", json={
        "name": "",  # too short
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_project_not_found(auth_client: AsyncClient):
    response = await auth_client.get("/projects/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_without_token(client: AsyncClient):
    response = await client.post("/projects", json={"name": "X"})
    assert response.status_code == 401
```

---

## Running Tests

```bash
pytest -v
```

```
tests/test_projects.py::test_create_project PASSED
tests/test_projects.py::test_create_project_validation PASSED
tests/test_projects.py::test_get_project_not_found PASSED
tests/test_projects.py::test_unauthorized_without_token PASSED
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Tool                            │ What It Does
────────────────────────────────┼──────────────────────────────────────
AsyncClient(transport=ASGITransport) │ Test FastAPI without running server
@pytest.fixture                 │ Setup/teardown for tests
@pytest.mark.asyncio            │ Mark async test functions
assert response.status_code     │ Check HTTP status
response.json()                 │ Parse response body
Override Depends()              │ Swap real DB for test DB
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 12: WebSockets](chapter-12-websockets.md) | [Chapter 14: Middleware →](chapter-14-middleware.md)
