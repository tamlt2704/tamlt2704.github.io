# Chapter 12: Trees All the Way Down — Composite

[← Chapter 11: State](chapter-11-state.md) | [Chapter 13: Proxy →](chapter-13-proxy.md)

---

## The Pain

PlugBoard lets users group blocks into sections, and sections into chapters. But the code treats individual blocks and groups completely differently:

```java
public class Renderer {
    public String render(Object node) {
        if (node instanceof Block block) {
            return renderBlock(block);
        } else if (node instanceof BlockGroup group) {
            StringBuilder sb = new StringBuilder();
            sb.append("<section class=\"").append(group.getStyle()).append("\">");
            for (Object child : group.getChildren()) {
                if (child instanceof Block b) {
                    sb.append(renderBlock(b));
                } else if (child instanceof BlockGroup g) {
                    sb.append(render(g));  // Recursive, but ugly
                }
            }
            sb.append("</section>");
            return sb.toString();
        }
        throw new IllegalArgumentException("Unknown node type");
    }

    public int wordCount(Object node) {
        if (node instanceof Block block) {
            return block.getTextContent().split("\\s+").length;
        } else if (node instanceof BlockGroup group) {
            int total = 0;
            for (Object child : group.getChildren()) {
                if (child instanceof Block b) {
                    total += b.getTextContent().split("\\s+").length;
                } else if (child instanceof BlockGroup g) {
                    total += wordCount(g);
                }
            }
            return total;
        }
        return 0;
    }
    // Every operation duplicates this instanceof check pattern
}
```

Every operation — render, word count, export, search, selection — has the same `instanceof` ladder. Adding a new node type means editing every operation. Dev added `ColumnLayout` last week and missed three places.

## The Pattern: Composite

Treat individual objects and compositions uniformly through a shared interface:

```java
public sealed interface DocumentNode
    permits LeafBlock, GroupNode {

    String render();
    int wordCount();
    List<DocumentNode> children();  // Leaf returns empty list
    void accept(NodeVisitor visitor);
}

// Leaf nodes — no children
public record LeafBlock(String type, String content, Map<String, String> attrs)
    implements DocumentNode {

    @Override
    public String render() {
        return switch (type) {
            case "paragraph" -> "<p>" + content + "</p>";
            case "heading" -> "<h2>" + content + "</h2>";
            case "code" -> "<pre><code>" + content + "</code></pre>";
            default -> "<div>" + content + "</div>";
        };
    }

    @Override public int wordCount() {
        return content.isBlank() ? 0 : content.split("\\s+").length;
    }

    @Override public List<DocumentNode> children() { return List.of(); }

    @Override public void accept(NodeVisitor visitor) { visitor.visitLeaf(this); }
}

// Composite node — contains children (which can be leaves or other composites)
public final class GroupNode implements DocumentNode {
    private final String name;
    private final String tag;
    private final List<DocumentNode> children;

    public GroupNode(String name, String tag, List<DocumentNode> children) {
        this.name = name;
        this.tag = tag;
        this.children = new ArrayList<>(children);
    }

    @Override
    public String render() {
        String inner = children.stream()
            .map(DocumentNode::render)
            .collect(Collectors.joining("\n"));
        return "<%s class=\"%s\">\n%s\n</%s>".formatted(tag, name, inner, tag);
    }

    @Override
    public int wordCount() {
        return children.stream().mapToInt(DocumentNode::wordCount).sum();
    }

    @Override public List<DocumentNode> children() { return Collections.unmodifiableList(children); }

    @Override public void accept(NodeVisitor visitor) {
        visitor.visitGroupStart(this);
        children.forEach(child -> child.accept(visitor));
        visitor.visitGroupEnd(this);
    }

    public void addChild(DocumentNode node) { children.add(node); }
    public void removeChild(int index) { children.remove(index); }
    public String name() { return name; }
}
```

## Building a Document Tree

```java
// A chapter with sections containing blocks
DocumentNode chapter = new GroupNode("chapter", "article", List.of(
    new LeafBlock("heading", "Introduction", Map.of()),
    new LeafBlock("paragraph", "Welcome to PlugBoard", Map.of()),
    new GroupNode("section", "section", List.of(
        new LeafBlock("heading", "Getting Started", Map.of()),
        new LeafBlock("paragraph", "First install the app", Map.of()),
        new LeafBlock("code", "npm install plugboard", Map.of("lang", "bash"))
    )),
    new GroupNode("section", "section", List.of(
        new LeafBlock("heading", "Configuration", Map.of()),
        new LeafBlock("paragraph", "Edit your config file", Map.of())
    ))
));

// Uniform operations — no instanceof checks
String html = chapter.render();       // Recursively renders entire tree
int words = chapter.wordCount();      // Recursively counts all words
```

## Operations on the Tree

Because the interface is uniform, operations work on any node without knowing if it's a leaf or group:

```java
// Find all nodes matching a predicate — works on any subtree
public List<DocumentNode> findAll(DocumentNode root, Predicate<DocumentNode> predicate) {
    List<DocumentNode> results = new ArrayList<>();
    if (predicate.test(root)) results.add(root);
    for (DocumentNode child : root.children()) {
        results.addAll(findAll(child, predicate));
    }
    return results;
}

// Usage
var headings = findAll(chapter, node ->
    node instanceof LeafBlock lb && lb.type().equals("heading"));

var sections = findAll(chapter, node ->
    node instanceof GroupNode gn && gn.name().equals("section"));
```

## PlugBoard After Composite

Before: Every operation has instanceof checks for blocks vs groups. Adding a node type means editing every operation. Nested structures require recursive special-casing.

After: One interface, uniform operations. Recursion is built into the composite. New node types implement the interface — existing code works unchanged.

```java
// Plugin adds a new composite type — existing operations just work
public final class ColumnLayout implements DocumentNode {
    private final List<DocumentNode> columns;

    @Override public String render() {
        return columns.stream()
            .map(col -> "<div class=\"col\">" + col.render() + "</div>")
            .collect(Collectors.joining("", "<div class=\"row\">", "</div>"));
    }

    @Override public int wordCount() {
        return columns.stream().mapToInt(DocumentNode::wordCount).sum();
    }

    @Override public List<DocumentNode> children() { return List.copyOf(columns); }
    @Override public void accept(NodeVisitor visitor) { /* ... */ }
}
```

## When NOT to Use Composite

| Situation | Why Not | Alternative |
|---|---|---|
| Leaf and group have very different APIs | Forced to add no-op methods to leaves | Separate hierarchies |
| Tree is only one level deep | Composite adds complexity for flat lists | Simple list |
| Operations differ drastically by type | Uniform interface becomes meaningless | Visitor pattern |
| Performance-critical traversal | Virtual dispatch on every node | Flat array with type tags |

## What You Learned

- **Composite** — compose objects into tree structures, treat uniformly
- **Recursive structure** — groups contain nodes, which can be groups
- **Uniform interface** — clients don't distinguish leaves from composites
- **Sealed interface** — compiler knows all node types
- **Natural recursion** — operations on composites delegate to children

Next: PlugBoard loads all document images eagerly. A 200-image document uses 2GB of RAM on open. We need lazy loading — that's Proxy.

---

[← Chapter 11: State](chapter-11-state.md) | [Chapter 13: Proxy →](chapter-13-proxy.md)
