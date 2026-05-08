# Chapter 6: Wrapping Gifts — Decorator

[← Chapter 5: Prototype](chapter-05-prototype.md) | [Chapter 7: Facade →](chapter-07-facade.md)

---

## The Pain

PlugBoard's text rendering supports formatting options: bold, italic, underline, strikethrough, highlight, and code. Dev started with subclasses:

```java
public class BoldText extends Text { ... }
public class ItalicText extends Text { ... }
public class BoldItalicText extends Text { ... }
public class BoldUnderlineText extends Text { ... }
public class BoldItalicUnderlineText extends Text { ... }
public class BoldItalicUnderlineStrikethroughText extends Text { ... }
// 2^6 = 64 possible combinations
```

Aisha's PR review: "We have 23 subclasses and we're not even halfway. What happens when we add `superscript`? 128 classes?"

The real killer: feature flags. Marketing wants to A/B test highlight colors. With inheritance, that means duplicating half the class hierarchy.

## The Pattern: Decorator

Wrap objects to add behavior. Stack wrappers for combinations:

```java
public interface TextRenderer {
    String render(String text);
}

// Base implementation — no formatting
public class PlainTextRenderer implements TextRenderer {
    @Override
    public String render(String text) {
        return text;
    }
}

// Abstract decorator — holds a reference to the wrapped renderer
public abstract class TextDecorator implements TextRenderer {
    protected final TextRenderer wrapped;

    protected TextDecorator(TextRenderer wrapped) {
        this.wrapped = wrapped;
    }
}

// Concrete decorators
public class BoldDecorator extends TextDecorator {
    public BoldDecorator(TextRenderer wrapped) { super(wrapped); }

    @Override
    public String render(String text) {
        return "<strong>" + wrapped.render(text) + "</strong>";
    }
}

public class ItalicDecorator extends TextDecorator {
    public ItalicDecorator(TextRenderer wrapped) { super(wrapped); }

    @Override
    public String render(String text) {
        return "<em>" + wrapped.render(text) + "</em>";
    }
}

public class HighlightDecorator extends TextDecorator {
    private final String color;

    public HighlightDecorator(TextRenderer wrapped, String color) {
        super(wrapped);
        this.color = color;
    }

    @Override
    public String render(String text) {
        return "<mark style=\"background:" + color + "\">"
            + wrapped.render(text) + "</mark>";
    }
}
```

## Stacking Decorators

```java
// Bold + Italic + Highlighted
TextRenderer renderer = new HighlightDecorator(
    new BoldDecorator(
        new ItalicDecorator(
            new PlainTextRenderer()
        )
    ),
    "#FFE066"
);

String result = renderer.render("important");
// <mark style="background:#FFE066"><strong><em>important</em></strong></mark>
```

Six decorators cover all 64 combinations — and adding `superscript` is one new class, not 64.

## Builder for Readable Stacking

Nested constructors get ugly. A builder helps:

```java
public class TextRendererBuilder {
    private TextRenderer renderer = new PlainTextRenderer();

    public TextRendererBuilder bold() {
        renderer = new BoldDecorator(renderer);
        return this;
    }
    public TextRendererBuilder italic() {
        renderer = new ItalicDecorator(renderer);
        return this;
    }
    public TextRendererBuilder underline() {
        renderer = new UnderlineDecorator(renderer);
        return this;
    }
    public TextRendererBuilder highlight(String color) {
        renderer = new HighlightDecorator(renderer, color);
        return this;
    }
    public TextRenderer build() { return renderer; }
}

// Usage
TextRenderer renderer = new TextRendererBuilder()
    .bold()
    .italic()
    .highlight("#FFE066")
    .build();
```

## Real PlugBoard Use: Export Decorators

The pattern extends beyond text. Export pipelines use decorators too:

```java
public interface Exporter {
    byte[] export(Document doc);
}

public class PdfExporter implements Exporter { ... }

public class WatermarkDecorator extends ExportDecorator {
    private final String watermark;

    public WatermarkDecorator(Exporter wrapped, String watermark) {
        super(wrapped);
        this.watermark = watermark;
    }

    @Override
    public byte[] export(Document doc) {
        byte[] pdf = wrapped.export(doc);
        return addWatermark(pdf, watermark);
    }
}

public class EncryptionDecorator extends ExportDecorator {
    private final String password;

    public EncryptionDecorator(Exporter wrapped, String password) {
        super(wrapped);
        this.password = password;
    }

    @Override
    public byte[] export(Document doc) {
        byte[] data = wrapped.export(doc);
        return encrypt(data, password);
    }
}

// Watermarked + encrypted PDF
Exporter exporter = new EncryptionDecorator(
    new WatermarkDecorator(new PdfExporter(), "DRAFT"),
    "secret123"
);
```

## PlugBoard After Decorator

Before: 23 subclasses and growing. Adding one feature doubles the hierarchy. Feature flags are impossible.

After: 6 decorator classes cover all combinations. New features are one class. Feature flags toggle decorators at runtime.

## When NOT to Use Decorator

| Situation | Why Not | Alternative |
|---|---|---|
| Order of wrapping matters and is confusing | Debugging nested wrappers is hard | Pipeline/Chain pattern |
| Only one or two combinations exist | Over-engineering | Simple subclass |
| Need to inspect the wrapped object | Decorators hide identity | Composition with explicit fields |
| Performance-critical inner loop | Each layer adds a method call | Flat implementation |

## What You Learned

- **Decorator** — attach new behavior by wrapping, not inheriting
- **Composition over inheritance** — N decorators cover 2^N combinations
- **Same interface** — decorators are transparent to clients
- **Stackable** — wrap decorators in decorators for combined behavior
- **Builder pattern synergy** — builders make decorator stacking readable

Next: exporting a document requires calling 12 subsystems in the right order. Plugin authors are drowning in complexity. We need a Facade.

---

[← Chapter 5: Prototype](chapter-05-prototype.md) | [Chapter 7: Facade →](chapter-07-facade.md)
