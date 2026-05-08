# Chapter 5: Clone Wars — Prototype

[← Chapter 4: Abstract Factory](chapter-04-abstract-factory.md) | [Chapter 6: Decorator →](chapter-06-decorator.md)

---

## The Pain

Users love "Duplicate Document." Dev implemented it:

```java
public class Document {
    private String title;
    private List<Block> blocks;
    private Map<String, String> metadata;
    private StyleSheet styles;

    public Document duplicate() {
        Document copy = new Document();
        copy.title = this.title + " (Copy)";
        copy.blocks = this.blocks;        // Shallow! Same list reference
        copy.metadata = this.metadata;    // Shallow! Same map reference
        copy.styles = this.styles;        // Shared mutable object
        return copy;
    }
}
```

Bug report from Mira: "I duplicated my quarterly report, edited the copy, and the original changed too." The blocks list is shared — adding a block to the copy adds it to the original. The metadata map is shared — changing a tag in the copy changes it everywhere.

Shallow copies of mutable objects are time bombs.

## The Pattern: Prototype (Copy Constructor)

Each class knows how to deep-copy itself:

```java
public sealed interface Block permits ParagraphBlock, ImageBlock, TableBlock, GroupBlock {
    Block deepCopy();
    String getType();
}

public record ParagraphBlock(String text, TextStyle style) implements Block {
    @Override
    public Block deepCopy() {
        return new ParagraphBlock(text, style.deepCopy());
    }
    @Override public String getType() { return "paragraph"; }
}

public class ImageBlock implements Block {
    private String url;
    private int width;
    private int height;
    private List<String> tags;

    // Copy constructor — the Java-preferred prototype approach
    public ImageBlock(ImageBlock other) {
        this.url = other.url;           // String is immutable, safe to share
        this.width = other.width;
        this.height = other.height;
        this.tags = new ArrayList<>(other.tags);  // Deep copy mutable list
    }

    @Override
    public Block deepCopy() {
        return new ImageBlock(this);
    }

    @Override public String getType() { return "image"; }
}
```

## Recursive Deep Copy

Tables contain cells, cells contain blocks — recursion handles nested structures:

```java
public class TableBlock implements Block {
    private List<List<Block>> cells;  // rows of columns of blocks

    public TableBlock(TableBlock other) {
        this.cells = other.cells.stream()
            .map(row -> row.stream()
                .map(Block::deepCopy)
                .toList())
            .collect(Collectors.toCollection(ArrayList::new));
    }

    @Override
    public Block deepCopy() { return new TableBlock(this); }
    @Override public String getType() { return "table"; }
}

public class GroupBlock implements Block {
    private String name;
    private List<Block> children;

    public GroupBlock(GroupBlock other) {
        this.name = other.name;
        this.children = other.children.stream()
            .map(Block::deepCopy)
            .collect(Collectors.toCollection(ArrayList::new));
    }

    @Override
    public Block deepCopy() { return new GroupBlock(this); }
    @Override public String getType() { return "group"; }
}
```

## The Document Copy

```java
public class Document {
    private String title;
    private List<Block> blocks;
    private Map<String, String> metadata;
    private StyleSheet styles;

    public Document(Document other) {
        this.title = other.title + " (Copy)";
        this.blocks = other.blocks.stream()
            .map(Block::deepCopy)
            .collect(Collectors.toCollection(ArrayList::new));
        this.metadata = new HashMap<>(other.metadata);
        this.styles = new StyleSheet(other.styles);  // StyleSheet has its own copy constructor
    }

    public Document deepCopy() {
        return new Document(this);
    }
}
```

## Prototype Registry: Templates

Users save documents as templates. The registry stores prototypes and clones on demand:

```java
public class TemplateRegistry {
    private final Map<String, Document> templates = new HashMap<>();

    public void register(String name, Document prototype) {
        templates.put(name, prototype);
    }

    public Document createFromTemplate(String name) {
        Document prototype = templates.get(name);
        if (prototype == null) throw new IllegalArgumentException("No template: " + name);
        return prototype.deepCopy();
    }
}

// Usage
registry.register("meeting-notes", meetingNotesDoc);
registry.register("project-brief", projectBriefDoc);

Document myNotes = registry.createFromTemplate("meeting-notes");
// Fully independent copy — edit freely
```

## PlugBoard After Prototype

Before: Duplicating a document creates a shallow copy. Edits to the copy corrupt the original. Templates are impossible.

After: Every block knows how to deep-copy itself. Document duplication is safe. Template registry clones prototypes on demand.

```java
// Safe duplication
Document original = loadDocument("quarterly-report");
Document copy = original.deepCopy();
copy.addBlock(new ParagraphBlock("New section", TextStyle.DEFAULT));
// original is untouched
```

## When NOT to Use Prototype

| Situation | Why Not | Alternative |
|---|---|---|
| Objects are immutable (records) | No need to copy — sharing is safe | Just share the reference |
| Simple flat objects | `new Foo(foo.x, foo.y)` is fine | Direct construction |
| Circular references | Deep copy becomes complex | Serialization-based copy |
| Performance-critical hot path | Deep copy is expensive | Copy-on-write or structural sharing |

## What You Learned

- **Prototype** — create new objects by copying existing ones
- **Copy constructors** — Java's preferred approach over `Cloneable`
- **Deep vs shallow** — mutable fields must be recursively copied
- **Prototype registry** — store templates, clone on demand
- **Immutable objects are free** — Strings, records with immutable fields don't need copying

Next: PlugBoard's text formatting has 6 features (bold, italic, underline, strikethrough, highlight, code). Combining them means 2⁶ = 64 subclasses. That's Decorator territory.

---

[← Chapter 4: Abstract Factory](chapter-04-abstract-factory.md) | [Chapter 6: Decorator →](chapter-06-decorator.md)
