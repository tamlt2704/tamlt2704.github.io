# Chapter 10: Spread the Word — Observer

[← Chapter 9: Command](chapter-09-command.md) | [Chapter 11: State →](chapter-11-state.md)

---

## The Pain

When a document changes, multiple components need to react: the word count updates, the outline panel refreshes, the autosave triggers, the collaboration cursor moves. Dev wired them directly:

```java
public class Document {
    private List<Block> blocks;
    private WordCountPanel wordCount;
    private OutlinePanel outline;
    private AutoSaver autoSaver;
    private CollabSync collabSync;
    private UndoManager undoManager;
    private SearchIndex searchIndex;

    public void addBlock(Block block) {
        blocks.add(block);
        // Manually notify everyone
        wordCount.update(this);
        outline.refresh(this);
        autoSaver.markDirty(this);
        collabSync.broadcast(this);
        undoManager.snapshot(this);
        searchIndex.reindex(this);
    }

    public void removeBlock(int index) {
        blocks.remove(index);
        // Same six calls, copy-pasted
        wordCount.update(this);
        outline.refresh(this);
        autoSaver.markDirty(this);
        collabSync.broadcast(this);
        undoManager.snapshot(this);
        searchIndex.reindex(this);
    }
}
```

Problems: Document knows about every listener. Adding a new listener means editing Document. Plugin authors can't subscribe to changes. Forgetting one notification call creates silent bugs.

## The Pattern: Observer

Document publishes events. Listeners subscribe without Document knowing who they are:

```java
public interface DocumentListener {
    void onDocumentChanged(DocumentEvent event);
}

public sealed interface DocumentEvent {
    Document document();

    record BlockAdded(Document document, Block block, int position) implements DocumentEvent {}
    record BlockRemoved(Document document, Block block, int position) implements DocumentEvent {}
    record BlockModified(Document document, Block block) implements DocumentEvent {}
    record MetadataChanged(Document document, String key) implements DocumentEvent {}
}

public class Document {
    private final List<Block> blocks = new ArrayList<>();
    private final List<DocumentListener> listeners = new CopyOnWriteArrayList<>();

    public void addListener(DocumentListener listener) {
        listeners.add(listener);
    }

    public void removeListener(DocumentListener listener) {
        listeners.remove(listener);
    }

    public void addBlock(Block block, int position) {
        blocks.add(position, block);
        fire(new DocumentEvent.BlockAdded(this, block, position));
    }

    public void removeBlock(int position) {
        Block removed = blocks.remove(position);
        fire(new DocumentEvent.BlockRemoved(this, removed, position));
    }

    private void fire(DocumentEvent event) {
        listeners.forEach(l -> l.onDocumentChanged(event));
    }
}
```

## Listeners Are Independent

Each listener handles only what it cares about:

```java
public class WordCountPanel implements DocumentListener {
    @Override
    public void onDocumentChanged(DocumentEvent event) {
        int count = event.document().getBlocks().stream()
            .mapToInt(b -> b.getTextContent().split("\\s+").length)
            .sum();
        display(count);
    }
}

public class AutoSaver implements DocumentListener {
    private final ScheduledExecutorService scheduler;
    private ScheduledFuture<?> pending;

    @Override
    public void onDocumentChanged(DocumentEvent event) {
        // Debounce: save 2 seconds after last change
        if (pending != null) pending.cancel(false);
        pending = scheduler.schedule(
            () -> save(event.document()),
            2, TimeUnit.SECONDS
        );
    }
}

public class OutlinePanel implements DocumentListener {
    @Override
    public void onDocumentChanged(DocumentEvent event) {
        // Only rebuild outline when blocks are added/removed
        if (event instanceof DocumentEvent.BlockAdded
            || event instanceof DocumentEvent.BlockRemoved) {
            rebuildOutline(event.document());
        }
    }
}
```

## Event Bus: Decoupled Further

For cross-cutting events (not just document changes), an event bus decouples publishers from subscribers entirely:

```java
public class EventBus {
    private final Map<Class<?>, List<Consumer<?>>> handlers = new ConcurrentHashMap<>();

    public <T> void subscribe(Class<T> eventType, Consumer<T> handler) {
        handlers.computeIfAbsent(eventType, k -> new CopyOnWriteArrayList<>())
            .add(handler);
    }

    @SuppressWarnings("unchecked")
    public <T> void publish(T event) {
        List<Consumer<?>> list = handlers.get(event.getClass());
        if (list != null) {
            list.forEach(h -> ((Consumer<T>) h).accept(event));
        }
    }
}

// Usage
eventBus.subscribe(DocumentEvent.BlockAdded.class, event -> {
    searchIndex.index(event.block());
});

eventBus.subscribe(ThemeChangedEvent.class, event -> {
    toolbar.repaint();
    sidebar.repaint();
});
```

## PlugBoard After Observer

Before: Document directly calls 6 components. Adding a listener means editing Document. Plugins can't subscribe.

After: Document fires events. Any component subscribes. Plugins hook in without touching core code.

```java
// Plugin subscribing to document changes
public class AnalyticsPlugin implements Plugin {
    @Override
    public void onLoad(PluginContext ctx) {
        ctx.eventBus().subscribe(DocumentEvent.BlockAdded.class, event -> {
            trackEvent("block_added", event.block().getType());
        });
    }
}
```

## When NOT to Use Observer

| Situation | Why Not | Alternative |
|---|---|---|
| One publisher, one subscriber | Observer adds indirection | Direct method call |
| Order of notification matters | Observer doesn't guarantee order | Explicit chain |
| Listeners modify the subject | Cascading updates, infinite loops | Command or mediator |
| Debugging event flow | Hard to trace who reacted to what | Explicit calls with logging |

## What You Learned

- **Observer** — define a one-to-many dependency so dependents update automatically
- **Sealed events** — type-safe event hierarchy with pattern matching
- **CopyOnWriteArrayList** — safe iteration while listeners add/remove themselves
- **Event bus** — fully decoupled pub/sub for cross-cutting concerns
- **Debouncing** — observers can throttle their reactions independently

Next: PlugBoard documents have a lifecycle — Draft, Review, Published, Archived. The current code is a maze of nested if-else checking the current status. That's the State pattern.

---

[← Chapter 9: Command](chapter-09-command.md) | [Chapter 11: State →](chapter-11-state.md)
