# Chapter 6: __getattr__ and Dynamic Dispatch

[← Chapter 5: Metaclasses](chapter-05-metaclasses.md) | [Chapter 7: Context Managers →](chapter-07-context-managers.md)

---

## The Problem

FrameForge needs an API client. The backend has 50 endpoints:

```
GET  /users
GET  /users/{id}
POST /users
GET  /orders
GET  /orders/{id}/items
POST /orders/{id}/cancel
```

The naive approach: write a method for every endpoint.

```python
class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_users(self):
        return requests.get(f"{self.base_url}/users").json()

    def get_user(self, user_id):
        return requests.get(f"{self.base_url}/users/{user_id}").json()

    def create_user(self, data):
        return requests.post(f"{self.base_url}/users", json=data).json()

    def get_orders(self):
        return requests.get(f"{self.base_url}/orders").json()

    def get_order_items(self, order_id):
        return requests.get(f"{self.base_url}/orders/{order_id}/items").json()

    # ... 45 more methods, all following the same pattern
```

50 methods that all do the same thing: build a URL and call `requests`. When the API adds a new endpoint, you add a new method.

Vera: "The client should build itself from the URL structure. `client.users.list()`, `client.orders[order_id].items.list()` — no predefined methods."

## __getattr__: The Fallback Hook

`__getattr__` is called when normal attribute lookup fails:

```python
class Demo:
    x = 10

    def __getattr__(self, name):
        # Only called if 'name' is NOT found normally
        return f"You asked for '{name}', which doesn't exist"

d = Demo()
d.x          # 10 — found normally, __getattr__ NOT called
d.anything   # "You asked for 'anything', which doesn't exist"
```

Key: `__getattr__` is the **fallback**. It only fires when the attribute isn't found through normal lookup (instance dict → class → bases).

## Solution: Dynamic API Client

```python
import requests

class APINode:
    """A chainable URL builder that executes HTTP requests."""

    def __init__(self, base_url, path_parts=None):
        self._base_url = base_url
        self._path_parts = path_parts or []

    def __getattr__(self, name):
        """Chain attribute access into URL path segments."""
        if name.startswith('_'):
            raise AttributeError(name)
        return APINode(self._base_url, self._path_parts + [name])

    def __getitem__(self, key):
        """Support client.users[user_id] for path parameters."""
        return APINode(self._base_url, self._path_parts + [str(key)])

    def _build_url(self):
        path = "/".join(self._path_parts)
        return f"{self._base_url}/{path}"

    def get(self, **params):
        return requests.get(self._build_url(), params=params).json()

    def post(self, data=None, **kwargs):
        return requests.post(self._build_url(), json=data, **kwargs).json()

    def put(self, data=None, **kwargs):
        return requests.put(self._build_url(), json=data, **kwargs).json()

    def delete(self, **kwargs):
        return requests.delete(self._build_url(), **kwargs).json()

    def __repr__(self):
        return f"APINode({self._build_url()!r})"


# Usage:
client = APINode("https://api.example.com/v1")

client.users.get()                    # GET /v1/users
client.users[42].get()                # GET /v1/users/42
client.users.post(data={"name": "Alice"})  # POST /v1/users
client.orders[7].items.get()          # GET /v1/orders/7/items
client.orders[7].cancel.post()        # POST /v1/orders/7/cancel
```

Zero predefined methods. The client handles any endpoint the API exposes — now and in the future.

## __getattribute__: Intercept Everything

`__getattribute__` is called on **every** attribute access, even for attributes that exist:

```python
class Logged:
    def __init__(self, x):
        # Must use object.__setattr__ to avoid recursion
        object.__setattr__(self, 'x', x)

    def __getattribute__(self, name):
        print(f"Accessing: {name}")
        return object.__getattribute__(self, name)

obj = Logged(42)
obj.x  # prints "Accessing: x", returns 42
```

### The Infinite Recursion Trap

```python
class Broken:
    def __getattribute__(self, name):
        # DANGER: self.anything triggers __getattribute__ again!
        print(f"Accessing {self.log_prefix}: {name}")  # INFINITE RECURSION
        return object.__getattribute__(self, name)

class Fixed:
    def __getattribute__(self, name):
        # Use object.__getattribute__ to bypass the hook
        prefix = object.__getattribute__(self, 'log_prefix')
        print(f"Accessing {prefix}: {name}")
        return object.__getattribute__(self, name)
```

**Rule**: Inside `__getattribute__`, always use `object.__getattribute__(self, ...)` to access your own attributes.

## Solution: Lazy Proxy

Load expensive objects only when first accessed:

```python
class LazyProxy:
    """Delays object creation until first attribute access."""

    def __init__(self, factory):
        object.__setattr__(self, '_factory', factory)
        object.__setattr__(self, '_instance', None)

    def _get_instance(self):
        instance = object.__getattribute__(self, '_instance')
        if instance is None:
            factory = object.__getattribute__(self, '_factory')
            instance = factory()
            object.__setattr__(self, '_instance', instance)
        return instance

    def __getattr__(self, name):
        return getattr(self._get_instance(), name)

    def __setattr__(self, name, value):
        setattr(self._get_instance(), name, value)

    def __repr__(self):
        return repr(self._get_instance())


# Usage:
def expensive_connection():
    print("Connecting to database...")  # Only happens on first access
    import time
    time.sleep(2)
    return {"connection": "active", "pool_size": 5}

db = LazyProxy(expensive_connection)
# No connection yet — nothing printed

print(db.pool_size)
# "Connecting to database..." — NOW it connects
# 5
```

## Solution: Attribute-Based Config Access

```python
class Config:
    """Access nested dict config with dot notation."""

    def __init__(self, data):
        object.__setattr__(self, '_data', data)

    def __getattr__(self, name):
        data = object.__getattribute__(self, '_data')
        if name not in data:
            raise AttributeError(f"No config key: {name}")
        value = data[name]
        if isinstance(value, dict):
            return Config(value)  # Wrap nested dicts
        return value

    def __setattr__(self, name, value):
        data = object.__getattribute__(self, '_data')
        data[name] = value

    def __repr__(self):
        data = object.__getattribute__(self, '_data')
        return f"Config({data})"


config = Config({
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "user": "admin",
            "password": "secret"
        }
    },
    "debug": True
})

config.debug                        # True
config.database.host                # "localhost"
config.database.credentials.user    # "admin"
config.database.port = 3306         # Modify nested values
```

## __missing__: Custom Dict Behavior

For dict subclasses, `__missing__` is called when a key isn't found:

```python
class DefaultDict:
    """Like collections.defaultdict but with a custom message."""

    def __init__(self, factory):
        self._data = {}
        self._factory = factory

    def __getitem__(self, key):
        if key not in self._data:
            self._data[key] = self._factory(key)
        return self._data[key]

# Or subclass dict directly:
class AutoDict(dict):
    """Dict that auto-creates nested dicts."""

    def __missing__(self, key):
        value = AutoDict()
        self[key] = value
        return value

data = AutoDict()
data["users"]["alice"]["age"] = 30  # No KeyError — creates nested dicts
print(data)  # {'users': {'alice': {'age': 30}}}
```

## Solution: Chainable Query Builder

```python
class Query:
    """Chainable query builder using __getattr__."""

    def __init__(self, model_name, filters=None, ordering=None, limit_val=None):
        self._model = model_name
        self._filters = filters or []
        self._ordering = ordering or []
        self._limit_val = limit_val

    def filter(self, **kwargs):
        new_filters = self._filters + list(kwargs.items())
        return Query(self._model, new_filters, self._ordering, self._limit_val)

    def order_by(self, *fields):
        new_ordering = self._ordering + list(fields)
        return Query(self._model, self._filters, new_ordering, self._limit_val)

    def limit(self, n):
        return Query(self._model, self._filters, self._ordering, n)

    def to_sql(self):
        sql = f"SELECT * FROM {self._model}"
        if self._filters:
            conditions = " AND ".join(f"{k} = :{k}" for k, v in self._filters)
            sql += f" WHERE {conditions}"
        if self._ordering:
            sql += f" ORDER BY {', '.join(self._ordering)}"
        if self._limit_val:
            sql += f" LIMIT {self._limit_val}"
        return sql

    def __repr__(self):
        return f"Query({self.to_sql()!r})"


# Chainable API:
query = (
    Query("users")
    .filter(active=True, role="admin")
    .order_by("created_at")
    .limit(10)
)
print(query.to_sql())
# SELECT * FROM users WHERE active = :active AND role = :role ORDER BY created_at LIMIT 10
```

## Danger Zone: When Not to Use These

```python
# DON'T use __getattribute__ unless you truly need to intercept ALL access
# DON'T use __getattr__ if a simple dict or named attributes would work
# DON'T forget that IDE autocomplete won't work with dynamic attributes
# DON'T make debugging impossible — add __repr__ and logging

# DO use __getattr__ for: proxy objects, API clients, lazy loading
# DO use __getattribute__ for: logging/auditing frameworks (rarely)
# DO use __missing__ for: auto-vivifying dicts, default factories
```

## What You Learned

- **`__getattr__`** is the fallback — called only when normal lookup fails
- **`__getattribute__`** intercepts ALL attribute access — use with extreme caution
- **`__missing__`** handles missing keys in dict subclasses
- **Dynamic API clients** use `__getattr__` to build URLs from attribute chains
- **Lazy proxies** delay expensive initialization until first access
- **Config objects** wrap nested dicts with dot-notation access
- **Always use `object.__getattribute__`** inside `__getattribute__` to avoid infinite recursion

## Key Insight

> Dynamic dispatch lets you build objects that respond to attributes that don't exist yet. But what about managing resources — things that need setup and teardown? Database connections, file handles, locks, temporary state? That's context managers.

---

[Chapter 7: Context Managers Beyond Files →](chapter-07-context-managers.md)
