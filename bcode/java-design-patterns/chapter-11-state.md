# Chapter 11: Shape Shifter — State

[← Chapter 10: Observer](chapter-10-observer.md) | [Chapter 12: Composite →](chapter-12-composite.md)

---

## The Pain

PlugBoard documents have a lifecycle: Draft → Review → Published → Archived. Dev implemented it with status checks everywhere:

```java
public class Document {
    private String status = "draft"; // "draft", "review", "published", "archived"

    public void edit(String content) {
        if (status.equals("draft")) {
            this.content = content;
        } else if (status.equals("review")) {
            throw new IllegalStateException("Cannot edit during review");
        } else if (status.equals("published")) {
            throw new IllegalStateException("Cannot edit published document");
        } else if (status.equals("archived")) {
            throw new IllegalStateException("Archived documents are read-only");
        }
    }

    public void submitForReview() {
        if (status.equals("draft")) {
            status = "review";
            notifyReviewers();
        } else if (status.equals("review")) {
            throw new IllegalStateException("Already in review");
        } else if (status.equals("published")) {
            // Can resubmit published docs for re-review
            status = "review";
            notifyReviewers();
        } else {
            throw new IllegalStateException("Cannot submit archived doc");
        }
    }

    public void publish() {
        if (status.equals("review")) {
            status = "published";
            generatePermalink();
        } else {
            throw new IllegalStateException("Can only publish from review");
        }
    }

    // Every method has the same if-else ladder...
}
```

The class is 400 lines. Adding a new state ("Scheduled") means editing every method. Adding a new action means another if-else in every state. Bugs hide in forgotten branches.

## The Pattern: State

Each state is a class. The document delegates behavior to its current state:

```java
public sealed interface DocumentState
    permits DraftState, ReviewState, PublishedState, ArchivedState {

    void edit(DocumentContext ctx, String content);
    void submitForReview(DocumentContext ctx);
    void publish(DocumentContext ctx);
    void archive(DocumentContext ctx);
    String name();
}

// The context holds current state and provides transition methods
public class DocumentContext {
    private DocumentState state;
    private String content;
    private final List<DocumentListener> listeners = new ArrayList<>();

    public DocumentContext() {
        this.state = new DraftState();
    }

    public void edit(String content) { state.edit(this, content); }
    public void submitForReview() { state.submitForReview(this); }
    public void publish() { state.publish(this); }
    public void archive() { state.archive(this); }

    void transitionTo(DocumentState newState) {
        this.state = newState;
        listeners.forEach(l -> l.onStateChanged(newState));
    }

    void setContent(String content) { this.content = content; }
    String getContent() { return content; }
    String currentState() { return state.name(); }
}
```

## State Implementations

```java
public final class DraftState implements DocumentState {
    @Override public String name() { return "draft"; }

    @Override
    public void edit(DocumentContext ctx, String content) {
        ctx.setContent(content);  // Editing allowed in draft
    }

    @Override
    public void submitForReview(DocumentContext ctx) {
        if (ctx.getContent() == null || ctx.getContent().isBlank()) {
            throw new IllegalStateException("Cannot submit empty document");
        }
        ctx.transitionTo(new ReviewState());
    }

    @Override
    public void publish(DocumentContext ctx) {
        throw new IllegalStateException("Must go through review first");
    }

    @Override
    public void archive(DocumentContext ctx) {
        ctx.transitionTo(new ArchivedState());
    }
}

public final class ReviewState implements DocumentState {
    @Override public String name() { return "review"; }

    @Override
    public void edit(DocumentContext ctx, String content) {
        throw new IllegalStateException("Cannot edit during review");
    }

    @Override
    public void submitForReview(DocumentContext ctx) {
        throw new IllegalStateException("Already in review");
    }

    @Override
    public void publish(DocumentContext ctx) {
        ctx.transitionTo(new PublishedState());
    }

    @Override
    public void archive(DocumentContext ctx) {
        ctx.transitionTo(new ArchivedState());
    }
}

public final class PublishedState implements DocumentState {
    @Override public String name() { return "published"; }

    @Override
    public void edit(DocumentContext ctx, String content) {
        throw new IllegalStateException("Published documents are immutable");
    }

    @Override
    public void submitForReview(DocumentContext ctx) {
        // Re-review is allowed for published docs
        ctx.transitionTo(new ReviewState());
    }

    @Override
    public void publish(DocumentContext ctx) {
        throw new IllegalStateException("Already published");
    }

    @Override
    public void archive(DocumentContext ctx) {
        ctx.transitionTo(new ArchivedState());
    }
}

public final class ArchivedState implements DocumentState {
    @Override public String name() { return "archived"; }

    @Override
    public void edit(DocumentContext ctx, String content) {
        throw new IllegalStateException("Archived documents are read-only");
    }

    @Override
    public void submitForReview(DocumentContext ctx) {
        throw new IllegalStateException("Cannot submit archived document");
    }

    @Override
    public void publish(DocumentContext ctx) {
        throw new IllegalStateException("Cannot publish archived document");
    }

    @Override
    public void archive(DocumentContext ctx) {
        throw new IllegalStateException("Already archived");
    }
}
```

## Adding a New State: Scheduled

Mira wants scheduled publishing. With the State pattern, it's one new class — no existing code changes:

```java
public final class ScheduledState implements DocumentState {
    private final Instant publishAt;

    public ScheduledState(Instant publishAt) {
        this.publishAt = publishAt;
    }

    @Override public String name() { return "scheduled"; }

    @Override
    public void edit(DocumentContext ctx, String content) {
        throw new IllegalStateException("Cannot edit scheduled document");
    }

    @Override
    public void submitForReview(DocumentContext ctx) {
        // Cancel schedule, back to review
        ctx.transitionTo(new ReviewState());
    }

    @Override
    public void publish(DocumentContext ctx) {
        ctx.transitionTo(new PublishedState());
    }

    @Override
    public void archive(DocumentContext ctx) {
        ctx.transitionTo(new ArchivedState());
    }
}
```

## PlugBoard After State

Before: 400-line class with nested if-else in every method. Adding a state means editing every method. Transitions are scattered and inconsistent.

After: Each state is a focused class. Transitions are explicit. Adding a state is adding a class. Invalid transitions throw immediately with clear messages.

```java
var doc = new DocumentContext();
doc.edit("Hello world");       // Works — draft state
doc.submitForReview();         // Transitions to review
doc.edit("change");            // Throws — can't edit in review
doc.publish();                 // Transitions to published
```

## When NOT to Use State

| Situation | Why Not | Alternative |
|---|---|---|
| Only 2 states (on/off) | A boolean is simpler | Boolean flag |
| States don't have different behavior | Just tracking status | Enum field |
| Transitions are trivial | Pattern adds classes for no gain | Switch expression |
| State logic is 10 lines total | Over-engineering | If-else is fine |

## What You Learned

- **State** — let an object alter its behavior when its internal state changes
- **Sealed interface** — compiler enforces all states are handled
- **Context delegates** — the document doesn't contain behavior logic
- **Open/Closed** — new states don't modify existing state classes
- **Explicit transitions** — each state controls what transitions are valid

Next: PlugBoard's document tree has blocks, groups of blocks, and groups of groups. But the code treats singles and groups differently everywhere. That's Composite.

---

[← Chapter 10: Observer](chapter-10-observer.md) | [Chapter 12: Composite →](chapter-12-composite.md)
