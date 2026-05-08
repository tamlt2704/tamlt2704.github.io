# Chapter 3: Object Factory — Factory Method

[← Chapter 2: Builder](chapter-02-builder.md) | [Chapter 4: Abstract Factory →](chapter-04-abstract-factory.md)

---

## The Pain

PlugBoard supports 47 block types: paragraph, heading, image, code, table, quote, divider, embed, and more. Creating a block from user input:

```java
public class BlockFactory {
    public Block createBlock(String type, Map<String, Object> data) {
        switch (type) {
            case "paragraph": return new ParagraphBlock(data);
            case "heading": return new HeadingBlock(data);
            case "image": return new ImageBlock(data);
            case "code": return new CodeBlock(data);
            case "table": return new TableBlock(data);
            case "quote": return new QuoteBlock(data);
            case "divider": return new DividerBlock(data);
            case "embed": return new EmbedBlock(data);
            // ... 39 more cases
            default: throw new IllegalArgumentException("Unknown block: " + type);
        }
    }
}
```

Every time a plugin author adds a new block type, they must:
1. Create the block class
2. Edit this switch statement
3. Recompile the core application

Mira's plugin marketplace vision is dead on arrival. External developers can't modify this switch statement.

## The Pattern: Factory Method

Instead of one giant switch, let each block type register its own creation logic:

```java
// The factory method interface
public interface BlockFactory {
    Block create(Map<String, Object> data);
    String getType();  // What type string this factory handles
}

// Each block type provides its own factory
public class ParagraphBlockFactory implements BlockFactory {
    @Override
    public String getType() { return "paragraph"; }

    @Override
    public Block create(Map<String, Object> data) {
        String text = (String) data.getOrDefault("text", "");
        return new ParagraphBlock(text);
    }
}

public class CodeBlockFactory implements BlockFactory {
    @Override
    public String getType() { return "code"; }

    @Override
    public Block create(Map<String, Object> data) {
        String code = (String) data.getOrDefault("code", "");
        String language = (String) data.getOrDefault("language", "plain");
        return new CodeBlock(code, language);
    }
}
```

## The Registry: No More Switch

```java
public class BlockRegistry {
    private final Map<String, BlockFactory> factories = new HashMap<>();

    public void register(BlockFactory factory) {
        factories.put(factory.getType(), factory);
    }

    public Block create(String type, Map<String, Object> data) {
        BlockFactory factory = factories.get(type);
        if (factory == null) {
            throw new IllegalArgumentException("Unknown block type: " + type);
        }
        return factory.create(data);
    }

    public Set<String> getRegisteredTypes() {
        return Collections.unmodifiableSet(factories.keySet());
    }
}
```

Registration:

```java
BlockRegistry registry = new BlockRegistry();
registry.register(new ParagraphBlockFactory());
registry.register(new CodeBlockFactory());
registry.register(new ImageBlockFactory());
// Plugins register their own:
registry.register(new MermaidDiagramBlockFactory());  // Plugin!
registry.register(new KanbanBlockFactory());          // Plugin!
```

Now plugins can add block types without touching core code. They just implement `BlockFactory` and register it.

## Simplification with Lambdas

For simple blocks, a full factory class is overkill. Use lambdas:

```java
public class BlockRegistry {
    private final Map<String, Function<Map<String, Object>, Block>> factories = new HashMap<>();

    public void register(String type, Function<Map<String, Object>, Block> factory) {
        factories.put(type, factory);
    }

    public Block create(String type, Map<String, Object> data) {
        var factory = factories.get(type);
        if (factory == null) throw new IllegalArgumentException("Unknown: " + type);
        return factory.apply(data);
    }
}

// Registration with lambdas
registry.register("paragraph", data -> new ParagraphBlock((String) data.get("text")));
registry.register("divider", data -> new DividerBlock());
registry.register("code", data -> new CodeBlock(
    (String) data.get("code"),
    (String) data.getOrDefault("language", "plain")
));
```

## The Block Hierarchy

```java
public sealed interface Block permits ParagraphBlock, HeadingBlock, CodeBlock,
                                      ImageBlock, DividerBlock, CustomBlock {
    String getType();
    String render();
    Map<String, Object> serialize();
}

public record ParagraphBlock(String text) implements Block {
    @Override public String getType() { return "paragraph"; }
    @Override public String render() { return "<p>" + text + "</p>"; }
    @Override public Map<String, Object> serialize() {
        return Map.of("type", "paragraph", "text", text);
    }
}

public record CodeBlock(String code, String language) implements Block {
    @Override public String getType() { return "code"; }
    @Override public String render() {
        return "<pre><code class=\"language-" + language + "\">" + code + "</code></pre>";
    }
    @Override public Map<String, Object> serialize() {
        return Map.of("type", "code", "code", code, "language", language);
    }
}
```

Using `sealed interface` means the compiler knows all core block types. Plugins use `CustomBlock` as their base:

```java
public non-sealed class CustomBlock implements Block {
    // Plugin blocks extend this
}
```

## Static Factory Methods (Simpler Variant)

For cases where you don't need a registry, static factory methods on the class itself work well:

```java
public class Notification {
    private final String message;
    private final Level level;
    private final Duration ttl;

    private Notification(String message, Level level, Duration ttl) {
        this.message = message;
        this.level = level;
        this.ttl = ttl;
    }

    // Static factory methods — named constructors
    public static Notification info(String message) {
        return new Notification(message, Level.INFO, Duration.ofSeconds(5));
    }

    public static Notification error(String message) {
        return new Notification(message, Level.ERROR, Duration.ofSeconds(30));
    }

    public static Notification warning(String message) {
        return new Notification(message, Level.WARNING, Duration.ofSeconds(10));
    }
}

// Usage: clear and readable
Notification.info("Document saved");
Notification.error("Export failed: disk full");
```

Advantages over constructors:
- **Named**: `Notification.error(...)` is clearer than `new Notification(..., Level.ERROR, ...)`
- **Can return subtypes**: the method can decide which class to instantiate
- **Can cache**: return existing instances instead of creating new ones

## When NOT to Use Factory Method

| Situation | Why Not | Alternative |
|---|---|---|
| Only 2-3 types, unlikely to grow | Over-engineering | Simple switch or if-else |
| Types known at compile time | No extensibility needed | Sealed interface + switch |
| No polymorphism needed | Factory adds indirection for nothing | Direct construction |

## PlugBoard After Factory Method

Before: 47-case switch statement that only core developers can modify.

After: A registry that plugins populate at startup. Adding a new block type is one class + one `register()` call. No core code changes.

```java
// Plugin manifest
public class MermaidPlugin implements Plugin {
    @Override
    public void onLoad(PluginContext ctx) {
        ctx.blockRegistry().register("mermaid",
            data -> new MermaidBlock((String) data.get("source")));
    }
}
```

Mira: "So plugin authors just implement one interface and register? That's the marketplace API?"

You: "That's the marketplace API."

## What You Learned

- **Factory Method** — delegate object creation to subclasses/implementations
- **Registry pattern** — map type strings to factory functions
- **Static factory methods** — named constructors on the class itself
- **Open/Closed principle** — open for extension (new factories), closed for modification (no switch edits)
- **Lambdas simplify** — simple factories don't need full classes
- **When to skip** — few types, no extensibility needed, no polymorphism

The block registry works for individual blocks. But PlugBoard's theming system needs coordinated sets of objects — a dark theme needs dark buttons, dark cards, dark inputs that all match. Creating them individually risks mismatched combinations. That's Abstract Factory.

---

[← Chapter 2: Builder](chapter-02-builder.md) | [Chapter 4: Abstract Factory →](chapter-04-abstract-factory.md)
