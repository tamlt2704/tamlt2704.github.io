# Chapter 4: Theme Families — Abstract Factory

[← Chapter 3: Factory Method](chapter-03-factory-method.md) | [Chapter 5: Prototype →](chapter-05-prototype.md)

---

## The Pain

PlugBoard supports themes. Dev built it with individual factories:

```java
public class ThemeManager {
    public Button createButton(String theme) {
        return switch (theme) {
            case "dark" -> new DarkButton();
            case "light" -> new LightButton();
            case "highContrast" -> new HighContrastButton();
            default -> throw new IllegalArgumentException(theme);
        };
    }

    public Card createCard(String theme) {
        return switch (theme) {
            case "dark" -> new DarkCard();
            case "light" -> new LightCard();
            case "highContrast" -> new HighContrastCard();
            default -> throw new IllegalArgumentException(theme);
        };
    }

    public TextField createTextField(String theme) {
        return switch (theme) {
            case "dark" -> new DarkTextField();
            case "light" -> new LightTextField();
            case "highContrast" -> new HighContrastTextField();
            default -> throw new IllegalArgumentException(theme);
        };
    }
}
```

The bug that triggered this refactor: someone called `createButton("dark")` and `createCard("light")` in the same panel. A dark button on a light card — invisible border, unreadable text. Nothing enforces that components come from the same family.

## The Pattern: Abstract Factory

Group related object creation into a single factory. You can only get components that belong together:

```java
public interface ThemeFactory {
    Button createButton();
    Card createCard();
    TextField createTextField();
    Icon createIcon(String name);
    String themeName();
}

public class DarkThemeFactory implements ThemeFactory {
    @Override public Button createButton() { return new DarkButton(); }
    @Override public Card createCard() { return new DarkCard(); }
    @Override public TextField createTextField() { return new DarkTextField(); }
    @Override public Icon createIcon(String name) { return new DarkIcon(name); }
    @Override public String themeName() { return "dark"; }
}

public class LightThemeFactory implements ThemeFactory {
    @Override public Button createButton() { return new LightButton(); }
    @Override public Card createCard() { return new LightCard(); }
    @Override public TextField createTextField() { return new LightTextField(); }
    @Override public Icon createIcon(String name) { return new LightIcon(name); }
    @Override public String themeName() { return "light"; }
}
```

## Using the Factory

Panels receive a factory — they can't mix themes:

```java
public class ToolbarPanel {
    private final ThemeFactory theme;

    public ToolbarPanel(ThemeFactory theme) {
        this.theme = theme;
    }

    public void render() {
        Button save = theme.createButton();
        save.setText("Save");

        Button export = theme.createButton();
        export.setText("Export");

        TextField search = theme.createTextField();
        search.setPlaceholder("Search blocks...");

        // All components guaranteed to be from the same theme
    }
}
```

## Plugin Themes

Plugin authors create complete theme families:

```java
public class NordThemeFactory implements ThemeFactory {
    private static final String BG = "#2E3440";
    private static final String FG = "#ECEFF4";
    private static final String ACCENT = "#88C0D0";

    @Override public Button createButton() {
        return new StyledButton(BG, FG, ACCENT, "0.3rem");
    }
    @Override public Card createCard() {
        return new StyledCard(BG, FG, "0.4rem", "none");
    }
    @Override public TextField createTextField() {
        return new StyledTextField(BG, FG, ACCENT);
    }
    @Override public Icon createIcon(String name) {
        return new SvgIcon(name, FG);
    }
    @Override public String themeName() { return "nord"; }
}
```

Registration:

```java
public class NordThemePlugin implements Plugin {
    @Override
    public void onLoad(PluginContext ctx) {
        ctx.themeRegistry().register(new NordThemeFactory());
    }
}
```

## PlugBoard After Abstract Factory

Before: Mix-and-match components from different themes. Visual bugs. Every new theme means editing three switch statements.

After: One factory per theme. Components are always consistent. Plugins ship complete themes.

```java
// Switching themes is one line
ThemeFactory theme = themeRegistry.get(userPreference);
var toolbar = new ToolbarPanel(theme);
var sidebar = new SidebarPanel(theme);
// Everything matches — guaranteed
```

## When NOT to Use Abstract Factory

| Situation | Why Not | Alternative |
|---|---|---|
| Only one product type | No family to coordinate | Factory Method |
| Families rarely change | Static creation is fine | Direct instantiation |
| Products don't need to match | No consistency constraint | Independent factories |
| Two products total | Over-engineering | Simple if-else |

## What You Learned

- **Abstract Factory** — create families of related objects without specifying concrete classes
- **Consistency guarantee** — you can't accidentally mix components from different families
- **Plugin extensibility** — new themes are new factory implementations, no core changes
- **Trade-off** — adding a new product type (e.g., `createTooltip()`) forces changes to every factory

Next problem: users duplicate complex documents, but the copies share mutable state with the original. Editing the copy corrupts the original. We need deep copying — that's Prototype.

---

[← Chapter 3: Factory Method](chapter-03-factory-method.md) | [Chapter 5: Prototype →](chapter-05-prototype.md)
