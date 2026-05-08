# Chapter 2: Building Complex Objects — Builder

[← Chapter 1: Singleton](chapter-01-singleton.md) | [Chapter 3: Factory Method →](chapter-03-factory-method.md)

---

## The Pain

PlugBoard's `Document` class has grown. A document has a title, content, author, creation date, tags, permissions, template, export format, version, language, and more. The constructor:

```java
public class Document {
    public Document(String title, String content, String author,
                    LocalDateTime createdAt, List<String> tags,
                    Permissions permissions, Template template,
                    ExportFormat format, int version, String language,
                    boolean draft, boolean archived, String parentId,
                    Map<String, String> metadata, Theme theme) {
        // 15 parameters...
    }
}
```

Creating a document:

```java
Document doc = new Document(
    "Q4 Report", "...", "alice",
    LocalDateTime.now(), List.of("finance", "q4"),
    Permissions.DEFAULT, null, ExportFormat.PDF,
    1, "en", true, false, null,
    Map.of(), Theme.LIGHT
);
```

Which parameter is which? What's that `null`? What's `true, false`? This is unreadable, error-prone, and impossible to maintain.

Dev: "I just added a new field and now I have to update 47 constructor calls across the codebase."

## Telescoping Constructors (The Failed Fix)

The first attempt: multiple constructors with different parameter counts:

```java
public Document(String title, String content) { ... }
public Document(String title, String content, String author) { ... }
public Document(String title, String content, String author, List<String> tags) { ... }
// ... 12 more overloads
```

This "telescoping constructor" pattern explodes combinatorially. What if you want tags but not author? You can't skip parameters.

## The Pattern: Builder

A Builder separates object construction from its representation. You set fields by name, in any order, and build the final object when ready:

```java
Document doc = Document.builder()
    .title("Q4 Report")
    .author("alice")
    .tags(List.of("finance", "q4"))
    .draft(true)
    .format(ExportFormat.PDF)
    .build();
```

Every field is named. Order doesn't matter. Optional fields are simply omitted (they get defaults).

## Implementation

```java
public class Document {
    private final String title;
    private final String content;
    private final String author;
    private final LocalDateTime createdAt;
    private final List<String> tags;
    private final Permissions permissions;
    private final ExportFormat format;
    private final boolean draft;
    private final String language;

    // Private constructor — only Builder can create Documents
    private Document(Builder builder) {
        this.title = builder.title;
        this.content = builder.content;
        this.author = builder.author;
        this.createdAt = builder.createdAt;
        this.tags = List.copyOf(builder.tags);  // Defensive copy
        this.permissions = builder.permissions;
        this.format = builder.format;
        this.draft = builder.draft;
        this.language = builder.language;
    }

    public static Builder builder() {
        return new Builder();
    }

    // Getters...
    public String title() { return title; }
    public String author() { return author; }
    public boolean isDraft() { return draft; }

    public static class Builder {
        // Required fields
        private String title;

        // Optional fields with defaults
        private String content = "";
        private String author = "anonymous";
        private LocalDateTime createdAt = LocalDateTime.now();
        private List<String> tags = new ArrayList<>();
        private Permissions permissions = Permissions.DEFAULT;
        private ExportFormat format = ExportFormat.MARKDOWN;
        private boolean draft = false;
        private String language = "en";

        public Builder title(String title) {
            this.title = Objects.requireNonNull(title);
            return this;  // Return this for chaining
        }

        public Builder content(String content) {
            this.content = content;
            return this;
        }

        public Builder author(String author) {
            this.author = author;
            return this;
        }

        public Builder tags(List<String> tags) {
            this.tags = new ArrayList<>(tags);
            return this;
        }

        public Builder addTag(String tag) {
            this.tags.add(tag);
            return this;
        }

        public Builder permissions(Permissions permissions) {
            this.permissions = permissions;
            return this;
        }

        public Builder format(ExportFormat format) {
            this.format = format;
            return this;
        }

        public Builder draft(boolean draft) {
            this.draft = draft;
            return this;
        }

        public Builder language(String language) {
            this.language = language;
            return this;
        }

        public Document build() {
            // Validate required fields
            if (title == null || title.isBlank()) {
                throw new IllegalStateException("Document title is required");
            }
            return new Document(this);
        }
    }
}
```

## Usage: Clean and Readable

```java
// Minimal document (only required fields)
Document simple = Document.builder()
    .title("Meeting Notes")
    .build();

// Full document (all options)
Document full = Document.builder()
    .title("Q4 Financial Report")
    .content("Revenue increased by 23%...")
    .author("alice")
    .tags(List.of("finance", "quarterly", "2024"))
    .permissions(Permissions.TEAM_ONLY)
    .format(ExportFormat.PDF)
    .draft(false)
    .language("en")
    .build();

// Incremental building
Document.Builder builder = Document.builder().title("Draft");
if (user.isAuthenticated()) {
    builder.author(user.getName());
}
if (request.hasParam("tags")) {
    builder.tags(request.getParams("tags"));
}
Document doc = builder.build();
```

## Immutability: The Builder Bonus

Notice the `Document` class has only `final` fields and no setters. Once built, a Document cannot be modified. This is **immutable by construction** — the Builder is the only way to set values, and it does so before the object exists.

Immutable objects are:
- Thread-safe (no synchronization needed)
- Safe to share (no defensive copies needed)
- Easy to reason about (state never changes)

### Modifying an Immutable Object: toBuilder()

```java
// Add a toBuilder() method for "modify and rebuild"
public Builder toBuilder() {
    return new Builder()
        .title(this.title)
        .content(this.content)
        .author(this.author)
        .tags(new ArrayList<>(this.tags))
        .permissions(this.permissions)
        .format(this.format)
        .draft(this.draft)
        .language(this.language);
}

// Usage: create a modified copy
Document published = draft.toBuilder()
    .draft(false)
    .build();
```

## Validation in build()

The `build()` method is the perfect place for validation:

```java
public Document build() {
    if (title == null || title.isBlank()) {
        throw new IllegalStateException("Title is required");
    }
    if (content.length() > 1_000_000) {
        throw new IllegalStateException("Content exceeds 1MB limit");
    }
    if (draft && format != ExportFormat.MARKDOWN) {
        throw new IllegalStateException("Drafts must use Markdown format");
    }
    return new Document(this);
}
```

Validation happens once, at construction time. After that, the object is guaranteed valid.

## When NOT to Use Builder

| Situation | Why Not | Alternative |
|---|---|---|
| 2-3 parameters | Over-engineering | Simple constructor |
| All fields required | No benefit over constructor | Constructor or record |
| Mutable object | Builder implies immutability | Setters are fine |
| Performance-critical hot path | Builder allocates an extra object | Direct construction |

```java
// Don't use Builder for this — a record is perfect
public record Point(int x, int y) {}
var p = new Point(3, 4);  // Clear, simple, immutable
```

## PlugBoard After Builder

Before: 47 constructor calls with 15 positional parameters, half of them `null`.

After: readable, self-documenting construction with sensible defaults. Adding a new optional field requires zero changes to existing code — it just gets a default value in the Builder.

## What You Learned

- **Builder** — separate construction from representation
- **Fluent API** — method chaining with `return this`
- **Defaults** — optional fields get sensible defaults in the Builder
- **Validation** — `build()` enforces invariants
- **Immutability** — Builder enables immutable objects naturally
- **toBuilder()** — create modified copies of immutable objects
- **When to skip it** — simple objects with few fields don't need Builder

The Document construction is clean. But PlugBoard supports 47 block types (paragraph, heading, image, code, table...), and creating them requires a massive switch statement. That's a Factory Method problem.

---

[← Chapter 1: Singleton](chapter-01-singleton.md) | [Chapter 3: Factory Method →](chapter-03-factory-method.md)
