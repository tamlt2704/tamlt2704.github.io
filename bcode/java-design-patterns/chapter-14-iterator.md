# Chapter 14: Walk the Tree — Iterator

[← Chapter 13: Proxy](chapter-13-proxy.md) | [Chapter 15: Adapter →](chapter-15-adapter.md)

---

## The Pain

PlugBoard's document tree needs different traversal orders. Rendering needs depth-first. Search needs breadth-first (find closest match first). Export needs reverse order for footnotes. Dev hardcoded each:

```java
public class DocumentTree {
    private final DocumentNode root;

    // Depth-first traversal — hardcoded
    public List<DocumentNode> getAllNodesDepthFirst() {
        List<DocumentNode> result = new ArrayList<>();
        depthFirst(root, result);
        return result;
    }

    private void depthFirst(DocumentNode node, List<DocumentNode> result) {
        result.add(node);
        for (DocumentNode child : node.children()) {
            depthFirst(child, result);
        }
    }

    // Breadth-first — another hardcoded traversal
    public List<DocumentNode> getAllNodesBreadthFirst() {
        List<DocumentNode> result = new ArrayList<>();
        Queue<DocumentNode> queue = new LinkedList<>();
        queue.add(root);
        while (!queue.isEmpty()) {
            DocumentNode node = queue.poll();
            result.add(node);
            queue.addAll(node.children());
        }
        return result;
    }

    // Leaves only — yet another traversal
    public List<DocumentNode> getLeavesOnly() {
        List<DocumentNode> result = new ArrayList<>();
        collectLeaves(root, result);
        return result;
    }

    // Every new traversal order = new method + new internal helper
}
```

Problems: The tree class grows with every traversal. All nodes are collected into a list upfront — wasteful for large documents. Can't compose traversals with filtering. Plugin authors can't add custom traversals.

## The Pattern: Iterator

Separate traversal logic from the collection. Each traversal is its own iterator:

```java
public class DepthFirstIterator implements Iterator<DocumentNode> {
    private final Deque<DocumentNode> stack = new ArrayDeque<>();

    public DepthFirstIterator(DocumentNode root) {
        stack.push(root);
    }

    @Override
    public boolean hasNext() {
        return !stack.isEmpty();
    }

    @Override
    public DocumentNode next() {
        if (!hasNext()) throw new NoSuchElementException();
        DocumentNode node = stack.pop();
        // Push children in reverse so leftmost is processed first
        List<DocumentNode> children = node.children();
        for (int i = children.size() - 1; i >= 0; i--) {
            stack.push(children.get(i));
        }
        return node;
    }
}

public class BreadthFirstIterator implements Iterator<DocumentNode> {
    private final Queue<DocumentNode> queue = new ArrayDeque<>();

    public BreadthFirstIterator(DocumentNode root) {
        queue.add(root);
    }

    @Override
    public boolean hasNext() {
        return !queue.isEmpty();
    }

    @Override
    public DocumentNode next() {
        if (!hasNext()) throw new NoSuchElementException();
        DocumentNode node = queue.poll();
        queue.addAll(node.children());
        return node;
    }
}
```

## Making It Iterable: Java Integration

Implement `Iterable` to use enhanced for-loops and streams:

```java
public class DocumentTree implements Iterable<DocumentNode> {
    private final DocumentNode root;

    public DocumentTree(DocumentNode root) {
        this.root = root;
    }

    // Default iteration is depth-first
    @Override
    public Iterator<DocumentNode> iterator() {
        return new DepthFirstIterator(root);
    }

    // Named iterables for other traversals
    public Iterable<DocumentNode> breadthFirst() {
        return () -> new BreadthFirstIterator(root);
    }

    public Iterable<DocumentNode> leavesOnly() {
        return () -> new LeavesIterator(root);
    }

    // Stream support
    public Stream<DocumentNode> stream() {
        return StreamSupport.stream(spliterator(), false);
    }
}

// Usage — clean, composable
DocumentTree tree = new DocumentTree(chapter);

// Default depth-first
for (DocumentNode node : tree) {
    System.out.println(node);
}

// Breadth-first
for (DocumentNode node : tree.breadthFirst()) {
    System.out.println(node);
}

// Stream + filter — find all code blocks
List<DocumentNode> codeBlocks = tree.stream()
    .filter(n -> n instanceof LeafBlock lb && lb.type().equals("code"))
    .toList();
```

## Lazy Evaluation: Leaves Iterator

The leaves iterator skips group nodes without collecting everything first:

```java
public class LeavesIterator implements Iterator<DocumentNode> {
    private final Deque<DocumentNode> stack = new ArrayDeque<>();

    public LeavesIterator(DocumentNode root) {
        stack.push(root);
        advanceToNextLeaf();
    }

    private void advanceToNextLeaf() {
        while (!stack.isEmpty() && !stack.peek().children().isEmpty()) {
            DocumentNode node = stack.pop();
            List<DocumentNode> children = node.children();
            for (int i = children.size() - 1; i >= 0; i--) {
                stack.push(children.get(i));
            }
        }
    }

    @Override public boolean hasNext() { return !stack.isEmpty(); }

    @Override
    public DocumentNode next() {
        if (!hasNext()) throw new NoSuchElementException();
        DocumentNode leaf = stack.pop();
        advanceToNextLeaf();
        return leaf;
    }
}
```

## Internal Iterator: Visitor-Style

Sometimes you want the collection to drive the iteration (internal iterator):

```java
public class DocumentTree {
    // External: caller controls iteration
    public Iterator<DocumentNode> iterator() { ... }

    // Internal: tree controls iteration, caller provides action
    public void forEach(Consumer<DocumentNode> action) {
        forEachDepthFirst(root, action);
    }

    public void forEachFiltered(Predicate<DocumentNode> filter, Consumer<DocumentNode> action) {
        forEach(node -> {
            if (filter.test(node)) action.accept(node);
        });
    }

    private void forEachDepthFirst(DocumentNode node, Consumer<DocumentNode> action) {
        action.accept(node);
        node.children().forEach(child -> forEachDepthFirst(child, action));
    }
}

// Usage
tree.forEachFiltered(
    node -> node instanceof LeafBlock,
    node -> exporter.export(node)
);
```

## PlugBoard After Iterator

Before: Every traversal order is a new method on DocumentTree. All nodes collected eagerly. No composition with filtering.

After: Traversals are independent iterator classes. Lazy evaluation — only visit nodes you need. Composable with Java streams.

```java
// Plugin adds a custom traversal
public class ReverseDepthFirstIterator implements Iterator<DocumentNode> {
    // Visits children right-to-left, bottom-up
    // Plugin authors implement Iterator — no core changes
}
```

## When NOT to Use Iterator

| Situation | Why Not | Alternative |
|---|---|---|
| Simple list with one traversal | `List` already implements `Iterable` | Use the list directly |
| Random access needed | Iterators are sequential | Index-based access |
| Collection is tiny (< 10 items) | Iterator overhead not justified | `for` loop over array |
| Traversal needs mutation | Iterator shouldn't modify structure | Collect then mutate |

## What You Learned

- **Iterator** — access elements sequentially without exposing internal structure
- **External vs internal** — caller controls (Iterator) vs collection controls (forEach)
- **Java Iterable** — implement for enhanced for-loops and stream support
- **Lazy evaluation** — iterators compute next element on demand
- **Separation** — traversal logic lives outside the collection

Last chapter: PlugBoard's plugin API changed in v2, but dozens of v1 plugins still exist. We need both to work. That's Adapter.

---

[← Chapter 13: Proxy](chapter-13-proxy.md) | [Chapter 15: Adapter →](chapter-15-adapter.md)
