# Chapter 13: Stand-In — Proxy

[← Chapter 12: Composite](chapter-12-composite.md) | [Chapter 14: Iterator →](chapter-14-iterator.md)

---

## The Pain

PlugBoard loads every image when a document opens. A user's 200-page product manual with screenshots:

```java
public class ImageBlock {
    private final byte[] imageData;  // Loaded immediately — 5-50MB each

    public ImageBlock(String path) {
        this.imageData = Files.readAllBytes(Path.of(path));  // Blocks on open
    }

    public byte[] getData() { return imageData; }
    public int getWidth() { return decodeWidth(imageData); }
    public int getHeight() { return decodeHeight(imageData); }
}

public class Document {
    public Document(Path file) {
        // Opening a 200-image document loads ALL images into RAM
        for (BlockData bd : parseBlocks(file)) {
            if (bd.type().equals("image")) {
                blocks.add(new ImageBlock(bd.path()));  // 200 × 10MB = 2GB
            }
        }
    }
}
```

Bug report: "PlugBoard crashes with OutOfMemoryError when I open my product manual." Users only see 3-4 images at a time, but all 200 are loaded. Startup takes 30 seconds.

## The Pattern: Virtual Proxy

A proxy stands in for the real image. It loads data only when actually needed:

```java
public interface Image {
    byte[] getData();
    int getWidth();
    int getHeight();
    String getPath();
}

// The real, expensive object
public class RealImage implements Image {
    private final String path;
    private final byte[] data;
    private final int width;
    private final int height;

    public RealImage(String path) {
        this.path = path;
        this.data = loadFromDisk(path);  // Expensive
        this.width = decodeWidth(data);
        this.height = decodeHeight(data);
    }

    @Override public byte[] getData() { return data; }
    @Override public int getWidth() { return width; }
    @Override public int getHeight() { return height; }
    @Override public String getPath() { return path; }
}

// Virtual proxy — defers loading until data is accessed
public class LazyImageProxy implements Image {
    private final String path;
    private final int width;   // From metadata — cheap to read
    private final int height;
    private RealImage realImage;  // null until needed

    public LazyImageProxy(String path, int width, int height) {
        this.path = path;
        this.width = width;
        this.height = height;
    }

    @Override
    public byte[] getData() {
        if (realImage == null) {
            realImage = new RealImage(path);  // Load on first access
        }
        return realImage.getData();
    }

    @Override public int getWidth() { return width; }    // No loading needed
    @Override public int getHeight() { return height; }  // No loading needed
    @Override public String getPath() { return path; }
}
```

Now opening a 200-image document reads only metadata (dimensions from headers). Actual pixel data loads when the user scrolls to that image.

## Protection Proxy: Access Control

Some documents are shared with view-only permissions. A protection proxy enforces access:

```java
public class ProtectedDocument implements Document {
    private final Document real;
    private final User currentUser;
    private final Permission permission;

    public ProtectedDocument(Document real, User currentUser, Permission permission) {
        this.real = real;
        this.currentUser = currentUser;
        this.permission = permission;
    }

    @Override
    public String getContent() {
        return real.getContent();  // Reading always allowed
    }

    @Override
    public void edit(String content) {
        if (permission == Permission.READ_ONLY) {
            throw new AccessDeniedException(
                "User %s has read-only access".formatted(currentUser.name()));
        }
        real.edit(content);
    }

    @Override
    public void delete() {
        if (permission != Permission.OWNER) {
            throw new AccessDeniedException("Only owners can delete");
        }
        real.delete();
    }
}
```

## Caching Proxy: Expensive Computations

Rendering a block to HTML is expensive. A caching proxy avoids re-rendering unchanged blocks:

```java
public class CachingBlockRenderer implements BlockRenderer {
    private final BlockRenderer real;
    private final Map<Integer, String> cache = new HashMap<>();

    public CachingBlockRenderer(BlockRenderer real) {
        this.real = real;
    }

    @Override
    public String render(Block block) {
        int hash = block.hashCode();
        return cache.computeIfAbsent(hash, k -> real.render(block));
    }

    public void invalidate(Block block) {
        cache.remove(block.hashCode());
    }

    public void clearCache() {
        cache.clear();
    }
}
```

## PlugBoard After Proxy

Before: 200 images loaded eagerly — 2GB RAM, 30-second startup. No access control on shared documents. Redundant re-rendering.

After: Images load on demand — 50MB at startup. Access control is transparent. Rendering is cached.

```java
// Document opening is instant — only metadata loaded
var doc = documentLoader.open("product-manual.pb");
// Images are LazyImageProxy instances — no data loaded yet

// When user scrolls to page 47, that image loads
Image img = doc.getBlock(147).getImage();
byte[] pixels = img.getData();  // NOW it loads from disk
```

## When NOT to Use Proxy

| Situation | Why Not | Alternative |
|---|---|---|
| Object is cheap to create | Proxy adds indirection for no gain | Direct instantiation |
| All data is always needed | Lazy loading never saves anything | Eager loading |
| Proxy logic is trivial | One-line check doesn't need a class | Inline check |
| Too many proxy layers | Debugging becomes impossible | Single wrapper |

## What You Learned

- **Virtual Proxy** — defer expensive creation until actually needed
- **Protection Proxy** — control access without modifying the real object
- **Caching Proxy** — avoid redundant expensive operations
- **Same interface** — clients can't tell proxy from real object
- **Metadata trick** — store cheap data (dimensions) in proxy, defer expensive data (pixels)

Next: PlugBoard's document tree needs different traversal orders — depth-first for rendering, breadth-first for search, reverse for undo. They're all hardcoded. That's Iterator.

---

[← Chapter 12: Composite](chapter-12-composite.md) | [Chapter 14: Iterator →](chapter-14-iterator.md)
