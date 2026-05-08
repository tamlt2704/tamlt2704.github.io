# Chapter 7: One Door — Facade

[← Chapter 6: Decorator](chapter-06-decorator.md) | [Chapter 8: Strategy →](chapter-08-strategy.md)

---

## The Pain

A plugin author posts in the PlugBoard Discord: "I just want to export a document to PDF. Why do I need to call 12 different classes?"

```java
// What plugin authors must do to export a document
public byte[] exportToPdf(Document doc) {
    // 1. Resolve styles
    StyleResolver resolver = new StyleResolver();
    ResolvedStyles styles = resolver.resolve(doc.getStyleSheet(), ThemeManager.current());

    // 2. Layout
    LayoutEngine layout = new LayoutEngine();
    PageLayout pages = layout.computeLayout(doc.getBlocks(), styles, PageSize.A4);

    // 3. Font subsetting
    FontSubsetter fonts = new FontSubsetter();
    SubsettedFonts subsetted = fonts.subset(pages.getUsedFonts());

    // 4. Image optimization
    ImageOptimizer images = new ImageOptimizer();
    OptimizedImages optimized = images.optimize(pages.getImages(), Resolution.PRINT);

    // 5. Render to intermediate format
    IntermediateRenderer renderer = new IntermediateRenderer();
    IRDocument ir = renderer.render(pages, subsetted, optimized);

    // 6. Table of contents
    TocGenerator toc = new TocGenerator();
    ir = toc.insertToc(ir, doc.getHeadings());

    // 7. Hyperlink resolution
    LinkResolver links = new LinkResolver();
    ir = links.resolveLinks(ir);

    // 8. Accessibility tags
    AccessibilityTagger a11y = new AccessibilityTagger();
    ir = a11y.tag(ir);

    // 9. PDF generation
    PdfGenerator pdf = new PdfGenerator();
    byte[] raw = pdf.generate(ir);

    // 10. Compression
    PdfCompressor compressor = new PdfCompressor();
    raw = compressor.compress(raw);

    // 11. Metadata
    MetadataWriter meta = new MetadataWriter();
    raw = meta.writeMetadata(raw, doc.getMetadata());

    // 12. Validation
    PdfValidator validator = new PdfValidator();
    validator.validate(raw);

    return raw;
}
```

Every plugin that exports must know this sequence. Get one step wrong and you get corrupted PDFs. Three different plugins have three different bugs because they each reimplemented this flow.

## The Pattern: Facade

One class, one method, hides the complexity:

```java
public class ExportFacade {
    private final StyleResolver styleResolver;
    private final LayoutEngine layoutEngine;
    private final FontSubsetter fontSubsetter;
    private final ImageOptimizer imageOptimizer;
    private final IntermediateRenderer renderer;
    private final TocGenerator tocGenerator;
    private final LinkResolver linkResolver;
    private final AccessibilityTagger a11yTagger;
    private final PdfGenerator pdfGenerator;
    private final PdfCompressor compressor;
    private final MetadataWriter metadataWriter;
    private final PdfValidator validator;

    public ExportFacade() {
        // Wire up defaults — or accept via constructor for testing
        this.styleResolver = new StyleResolver();
        this.layoutEngine = new LayoutEngine();
        this.fontSubsetter = new FontSubsetter();
        this.imageOptimizer = new ImageOptimizer();
        this.renderer = new IntermediateRenderer();
        this.tocGenerator = new TocGenerator();
        this.linkResolver = new LinkResolver();
        this.a11yTagger = new AccessibilityTagger();
        this.pdfGenerator = new PdfGenerator();
        this.compressor = new PdfCompressor();
        this.metadataWriter = new MetadataWriter();
        this.validator = new PdfValidator();
    }

    public byte[] exportPdf(Document doc) {
        return exportPdf(doc, ExportOptions.defaults());
    }

    public byte[] exportPdf(Document doc, ExportOptions options) {
        ResolvedStyles styles = styleResolver.resolve(doc.getStyleSheet(), options.theme());
        PageLayout pages = layoutEngine.computeLayout(doc.getBlocks(), styles, options.pageSize());
        SubsettedFonts fonts = fontSubsetter.subset(pages.getUsedFonts());
        OptimizedImages images = imageOptimizer.optimize(pages.getImages(), options.resolution());
        IRDocument ir = renderer.render(pages, fonts, images);

        if (options.includeToc()) ir = tocGenerator.insertToc(ir, doc.getHeadings());
        ir = linkResolver.resolveLinks(ir);
        if (options.accessible()) ir = a11yTagger.tag(ir);

        byte[] raw = pdfGenerator.generate(ir);
        if (options.compress()) raw = compressor.compress(raw);
        raw = metadataWriter.writeMetadata(raw, doc.getMetadata());
        validator.validate(raw);

        return raw;
    }
}

public record ExportOptions(
    Theme theme,
    PageSize pageSize,
    Resolution resolution,
    boolean includeToc,
    boolean accessible,
    boolean compress
) {
    public static ExportOptions defaults() {
        return new ExportOptions(
            Theme.current(), PageSize.A4, Resolution.PRINT,
            true, true, true
        );
    }
}
```

## Plugin Authors Now

```java
// Before: 30 lines of subsystem orchestration
// After: 1 line
byte[] pdf = exportFacade.exportPdf(document);

// With options
byte[] pdf = exportFacade.exportPdf(document, new ExportOptions(
    Theme.DARK, PageSize.LETTER, Resolution.SCREEN,
    false, true, false
));
```

## Facade Doesn't Hide Access

The subsystems are still available for advanced users:

```java
public class ExportFacade {
    // Facade method — simple path
    public byte[] exportPdf(Document doc) { ... }

    // Escape hatch — advanced users access subsystems directly
    public LayoutEngine layoutEngine() { return layoutEngine; }
    public PdfGenerator pdfGenerator() { return pdfGenerator; }
}
```

Aisha's rule: "Facade simplifies the common case. It doesn't prevent the complex case."

## PlugBoard After Facade

Before: Plugin authors must understand 12 subsystems and call them in the correct order. Three plugins, three different bugs.

After: One method call for the common case. Options for customization. Subsystems still accessible for power users.

## When NOT to Use Facade

| Situation | Why Not | Alternative |
|---|---|---|
| Only 2-3 steps | A method is enough | Regular method |
| Subsystem is already simple | Facade adds indirection | Use subsystem directly |
| Every caller needs different steps | Facade can't cover all cases | Let callers orchestrate |
| Facade becomes a god class | Too many responsibilities | Multiple focused facades |

## What You Learned

- **Facade** — provide a simple interface to a complex subsystem
- **Doesn't restrict** — advanced users can still access internals
- **Options pattern** — use records to configure facade behavior
- **Subsystem independence** — the subsystems don't know about the facade
- **Multiple facades** — one for export, one for import, one for rendering

Next: PlugBoard's search uses different algorithms (fuzzy, regex, semantic). They're hardcoded in a switch. Adding a new algorithm means editing the search engine. That's Strategy.

---

[← Chapter 6: Decorator](chapter-06-decorator.md) | [Chapter 8: Strategy →](chapter-08-strategy.md)
