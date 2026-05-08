# Chapter 1: One and Only — Singleton

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Builder →](chapter-02-builder.md)

---

## The Pain

PlugBoard has a configuration system. It loads settings from a YAML file — theme, font size, autosave interval, plugin paths. Three different parts of the codebase load this config independently:

```java
public class EditorPanel {
    public EditorPanel() {
        Config config = new Config("settings.yaml");  // Loads from disk
        this.fontSize = config.getInt("font.size");
    }
}

public class PluginLoader {
    public void loadPlugins() {
        Config config = new Config("settings.yaml");  // Loads AGAIN
        this.pluginDir = config.getString("plugins.directory");
    }
}

public class AutoSaver {
    public void start() {
        Config config = new Config("settings.yaml");  // And AGAIN
        this.interval = config.getInt("autosave.interval");
    }
}
```

Three problems:
1. **Wasted I/O** — reads the same file three times
2. **Inconsistency** — if the file changes between reads, different parts of the app see different values
3. **No single source of truth** — who "owns" the config?

Aisha's code review: "Why are we loading config in 14 different places? There should be one config object for the entire application."

## The Pattern: Singleton

A Singleton ensures a class has **exactly one instance** and provides a global access point to it.

### The Classic Implementation

```java
public class AppConfig {
    private static AppConfig instance;

    private final Map<String, Object> settings;

    // Private constructor — nobody else can create instances
    private AppConfig() {
        this.settings = loadFromDisk("settings.yaml");
    }

    // Global access point
    public static AppConfig getInstance() {
        if (instance == null) {
            instance = new AppConfig();
        }
        return instance;
    }

    public String getString(String key) {
        return (String) settings.get(key);
    }

    public int getInt(String key) {
        return (int) settings.get(key);
    }

    private Map<String, Object> loadFromDisk(String path) {
        // ... load YAML file
        return Map.of(
            "font.size", 14,
            "plugins.directory", "/home/user/.plugboard/plugins",
            "autosave.interval", 30
        );
    }
}
```

Usage:
```java
// Anywhere in the codebase — same instance every time
int fontSize = AppConfig.getInstance().getInt("font.size");
```

### Why Private Constructor?

```java
private AppConfig() { ... }
```

If the constructor is private, nobody can write `new AppConfig()`. The only way to get an instance is through `getInstance()`. This guarantees exactly one instance exists.

## The Problem: Thread Safety

The classic implementation has a race condition:

```java
public static AppConfig getInstance() {
    if (instance == null) {          // Thread A checks: null ✓
        // Thread B also checks: null ✓ (hasn't been assigned yet)
        instance = new AppConfig();  // Thread A creates instance
        // Thread B ALSO creates instance — two instances exist!
    }
    return instance;
}
```

In PlugBoard, the editor panel and plugin loader initialize on different threads during startup. Without synchronization, you can get two config instances with different load times.

## Thread-Safe Solutions

### Solution 1: Synchronized Method (Simple, Slow)

```java
public static synchronized AppConfig getInstance() {
    if (instance == null) {
        instance = new AppConfig();
    }
    return instance;
}
```

Thread-safe, but every call to `getInstance()` acquires a lock — even after the instance is created. Unnecessary overhead for a hot path.

### Solution 2: Double-Checked Locking (Fast, Correct)

```java
public class AppConfig {
    private static volatile AppConfig instance;

    public static AppConfig getInstance() {
        if (instance == null) {                    // First check (no lock)
            synchronized (AppConfig.class) {
                if (instance == null) {            // Second check (with lock)
                    instance = new AppConfig();
                }
            }
        }
        return instance;
    }
}
```

The `volatile` keyword is essential — without it, Thread B might see a partially constructed instance due to instruction reordering.

### Solution 3: Eager Initialization (Simplest)

```java
public class AppConfig {
    private static final AppConfig INSTANCE = new AppConfig();

    public static AppConfig getInstance() {
        return INSTANCE;
    }

    private AppConfig() { ... }
}
```

Created when the class loads. Thread-safe by the JVM class loading guarantee. Downside: created even if never used (usually fine for config).

### Solution 4: Enum Singleton (Recommended by Effective Java)

```java
public enum AppConfig {
    INSTANCE;

    private final Map<String, Object> settings;

    AppConfig() {
        this.settings = loadFromDisk("settings.yaml");
    }

    public String getString(String key) {
        return (String) settings.get(key);
    }

    public int getInt(String key) {
        return (int) settings.get(key);
    }

    private Map<String, Object> loadFromDisk(String path) {
        return Map.of("font.size", 14, "autosave.interval", 30);
    }
}

// Usage
int fontSize = AppConfig.INSTANCE.getInt("font.size");
```

Why enum? The JVM guarantees exactly one instance. It's thread-safe, serialization-safe, and reflection-proof. Joshua Bloch (Effective Java) calls this the best approach.

## PlugBoard After Singleton

```java
public class EditorPanel {
    public EditorPanel() {
        this.fontSize = AppConfig.INSTANCE.getInt("font.size");
    }
}

public class PluginLoader {
    public void loadPlugins() {
        this.pluginDir = AppConfig.INSTANCE.getString("plugins.directory");
    }
}

public class AutoSaver {
    public void start() {
        this.interval = AppConfig.INSTANCE.getInt("autosave.interval");
    }
}
```

One load. One instance. Consistent values everywhere.

## When NOT to Use Singleton

Singleton is the most overused pattern. Don't use it for:

| Situation | Why Not | Alternative |
|---|---|---|
| User session | Multiple users = multiple sessions | Dependency injection |
| Database connection | Need connection pooling, not one connection | Connection pool |
| "I need global access" | That's not a reason for Singleton | Pass as parameter |
| Testing | Singletons are hard to mock | Interface + injection |

The test for whether you need a Singleton: **would having two instances cause a bug?** If yes, Singleton. If no, just use dependency injection.

## Singleton vs Dependency Injection

Modern Java applications often prefer DI over Singleton:

```java
// Singleton: class controls its own lifecycle
AppConfig.INSTANCE.getInt("font.size");

// DI: someone else provides the dependency
public class EditorPanel {
    private final Config config;

    public EditorPanel(Config config) {  // Injected
        this.fontSize = config.getInt("font.size");
    }
}
```

DI is more testable (inject a mock config) and more flexible (different configs for different contexts). Use Singleton when you genuinely need one global instance that manages its own lifecycle.

## What You Learned

- **Singleton** — exactly one instance, global access point
- **Private constructor** — prevents external instantiation
- **Thread safety matters** — lazy initialization has race conditions
- **Enum Singleton** — simplest correct implementation in Java
- **Don't overuse it** — most "singletons" should be injected dependencies
- **The test** — "would two instances cause a bug?"

PlugBoard's config is fixed. But the next pain point is worse: the `Document` constructor takes 15 parameters, half of them optional. That's a Builder problem.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Builder →](chapter-02-builder.md)
