# Chapter 15: Bridge the Gap — Adapter

[← Chapter 14: Iterator](chapter-14-iterator.md) | [Chapter 0: Overview →](chapter-00-overview.md)

---

## The Pain

PlugBoard shipped its plugin marketplace. 47 plugins use the v1 API. Then Aisha redesigned the plugin interface for v2 — cleaner, async-first, type-safe. But v1 plugins still need to work:

```java
// V1 Plugin API (legacy — 47 plugins use this)
public interface PluginV1 {
    String getName();
    void initialize(Map<String, Object> config);
    void onDocumentOpen(Document doc);
    void onDocumentSave(Document doc);
    String[] getSupportedBlocks();
    Object createBlock(String type, Map<String, Object> data);
}

// V2 Plugin API (new — cleaner, type-safe)
public interface PluginV2 {
    PluginMetadata metadata();
    CompletableFuture<Void> initialize(PluginConfig config);
    void onEvent(PluginEvent event);
    List<BlockFactory> blockFactories();
}

public record PluginMetadata(String name, String version, String author) {}
public record PluginConfig(Map<String, String> settings, Path dataDir) {}
```

The plugin loader only speaks v2. Mira says: "We are NOT breaking 47 plugins. Make them work." You can't modify the v1 plugins — they're third-party code.

## The Pattern: Adapter

Wrap the old interface to make it look like the new one:

```java
public class PluginV1Adapter implements PluginV2 {
    private final PluginV1 legacy;

    public PluginV1Adapter(PluginV1 legacy) {
        this.legacy = legacy;
    }

    @Override
    public PluginMetadata metadata() {
        return new PluginMetadata(legacy.getName(), "1.x", "unknown");
    }

    @Override
    public CompletableFuture<Void> initialize(PluginConfig config) {
        // V1 is synchronous — wrap in a completed future
        return CompletableFuture.runAsync(() -> {
            Map<String, Object> legacyConfig = new HashMap<>(config.settings());
            legacy.initialize(legacyConfig);
        });
    }

    @Override
    public void onEvent(PluginEvent event) {
        // Translate v2 events to v1 method calls
        switch (event) {
            case PluginEvent.DocumentOpened e -> legacy.onDocumentOpen(e.document());
            case PluginEvent.DocumentSaved e -> legacy.onDocumentSave(e.document());
            default -> {} // V1 plugins don't handle other events
        }
    }

    @Override
    public List<BlockFactory> blockFactories() {
        // Adapt v1's string-based block creation to v2's typed factories
        return Arrays.stream(legacy.getSupportedBlocks())
            .map(type -> new BlockFactory() {
                @Override public String getType() { return type; }
                @Override public Block create(Map<String, Object> data) {
                    Object raw = legacy.createBlock(type, data);
                    return adaptBlock(raw);  // Convert Object to Block
                }
            })
            .toList();
    }

    private Block adaptBlock(Object raw) {
        if (raw instanceof Block b) return b;
        if (raw instanceof Map<?, ?> map) return new GenericBlock(map);
        throw new PluginException("V1 plugin returned invalid block: " + raw.getClass());
    }
}
```

## The Plugin Loader

```java
public class PluginLoader {
    private final List<PluginV2> plugins = new ArrayList<>();

    public void load(PluginV2 plugin) {
        plugins.add(plugin);
    }

    // Load a legacy plugin through the adapter
    public void loadLegacy(PluginV1 legacyPlugin) {
        plugins.add(new PluginV1Adapter(legacyPlugin));
    }

    public CompletableFuture<Void> initializeAll(PluginConfig config) {
        var futures = plugins.stream()
            .map(p -> p.initialize(config))
            .toArray(CompletableFuture[]::new);
        return CompletableFuture.allOf(futures);
    }

    public void broadcast(PluginEvent event) {
        plugins.forEach(p -> p.onEvent(event));
    }
}
```

## Object Adapter vs Class Adapter

The example above is an **object adapter** — it wraps an instance. Java also supports **class adapters** via inheritance (less common, less flexible):

```java
// Object adapter (preferred) — wraps via composition
public class PluginV1Adapter implements PluginV2 {
    private final PluginV1 legacy;  // Composition
    // ...
}

// Class adapter — inherits from adaptee (only works with classes, not interfaces)
public class MarkdownExporterAdapter extends LegacyMarkdownExporter implements Exporter {
    @Override
    public byte[] export(Document doc) {
        // Call inherited legacy method, adapt the result
        String markdown = super.convertToMarkdown(doc.getContent());
        return markdown.getBytes(StandardCharsets.UTF_8);
    }
}
```

Object adapters are preferred because they:
- Work with interfaces (not just classes)
- Can adapt multiple objects
- Don't couple you to the adaptee's implementation

## Two-Way Adapter: Bridging Both Directions

Some v2 features need to call back into v1 plugin territory:

```java
public class TwoWayPluginAdapter implements PluginV2, PluginV1 {
    private final PluginV1 legacyImpl;

    public TwoWayPluginAdapter(PluginV1 legacyImpl) {
        this.legacyImpl = legacyImpl;
    }

    // V2 interface — delegates to V1
    @Override public PluginMetadata metadata() {
        return new PluginMetadata(legacyImpl.getName(), "1.x", "unknown");
    }

    // V1 interface — passes through
    @Override public String getName() { return legacyImpl.getName(); }
    @Override public void initialize(Map<String, Object> config) {
        legacyImpl.initialize(config);
    }

    // ... both interfaces fully implemented
}
```

## PlugBoard After Adapter

Before: V2 plugin loader can't load v1 plugins. 47 plugins broken. Mira is unhappy.

After: Adapter wraps v1 plugins transparently. Plugin loader sees only v2 interfaces. All 47 legacy plugins work without modification.

```java
// Loading plugins — loader doesn't care about version
PluginLoader loader = new PluginLoader();
loader.load(new AnalyticsPluginV2());          // Native v2
loader.loadLegacy(new OldSpellCheckPlugin());  // V1 via adapter
loader.loadLegacy(new OldEmojiPlugin());       // V1 via adapter

// All plugins receive events uniformly
loader.broadcast(new PluginEvent.DocumentOpened(doc));
```

## When NOT to Use Adapter

| Situation | Why Not | Alternative |
|---|---|---|
| You control both interfaces | Just change one to match | Refactor directly |
| Interfaces are too different | Adapter becomes complex translation layer | Rewrite the client |
| Only one call site | Adapter class is overkill | Inline conversion |
| Performance-critical path | Extra indirection adds latency | Direct integration |

## What You Learned

- **Adapter** — convert one interface to another that clients expect
- **Object adapter** — composition-based, flexible, preferred in Java
- **Class adapter** — inheritance-based, limited to single class adaptation
- **Transparency** — clients don't know they're talking to an adapter
- **Legacy integration** — keep old code working while evolving the API
- **Two-way adapter** — bridge both directions when needed

## Course Complete

You've refactored PlugBoard from a tangled monolith into a plugin-friendly architecture using 15 design patterns:

| Pattern | What It Fixed |
|---|---|
| Singleton | Config loader conflicts |
| Builder | Complex document construction |
| Factory Method | 47-case switch for block creation |
| Abstract Factory | Mismatched theme components |
| Prototype | Shallow copy corruption |
| Decorator | 64-subclass explosion |
| Facade | 12-step export complexity |
| Strategy | Hardcoded search algorithms |
| Command | No undo/redo |
| Observer | Manual notification spaghetti |
| State | Nested if-else for lifecycle |
| Composite | Groups vs singles treated differently |
| Proxy | 2GB memory on document open |
| Iterator | Hardcoded traversal orders |
| Adapter | Broken legacy plugins |

Mira got her plugin marketplace. Dev learned when to reach for a pattern — and when not to. Aisha still thinks some of it is over-engineered. She's probably right about two of them.

---

[← Chapter 14: Iterator](chapter-14-iterator.md) | [Chapter 0: Overview →](chapter-00-overview.md)
