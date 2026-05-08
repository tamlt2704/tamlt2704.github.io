# Chapter 8: Pick Your Algorithm — Strategy

[← Chapter 7: Facade](chapter-07-facade.md) | [Chapter 9: Command →](chapter-09-command.md)

---

## The Pain

PlugBoard's search supports three modes: exact match, fuzzy, and regex. Dev hardcoded them:

```java
public class SearchEngine {
    public List<SearchResult> search(String query, String mode, List<Block> blocks) {
        List<SearchResult> results = new ArrayList<>();
        for (Block block : blocks) {
            String text = block.getTextContent();
            boolean matches = switch (mode) {
                case "exact" -> text.contains(query);
                case "fuzzy" -> fuzzyMatch(text, query, 0.7);
                case "regex" -> Pattern.compile(query).matcher(text).find();
                case "semantic" -> semanticSearch(text, query); // Added last week
                default -> throw new IllegalArgumentException("Unknown mode: " + mode);
            };
            if (matches) results.add(new SearchResult(block, computeScore(text, query, mode)));
        }
        return results;
    }

    private boolean fuzzyMatch(String text, String query, double threshold) {
        // 40 lines of Levenshtein distance calculation
    }

    private boolean semanticSearch(String text, String query) {
        // 60 lines of embedding comparison
    }

    private double computeScore(String text, String query, String mode) {
        // Another switch statement with scoring logic per mode
    }
}
```

Problems: `SearchEngine` is 300 lines and growing. Every new algorithm touches this class. Plugin authors want to add custom search (e.g., CJK-aware search) but can't without modifying core code. Testing one algorithm means instantiating the entire engine.

## The Pattern: Strategy

Extract each algorithm into its own class behind a common interface:

```java
public interface SearchStrategy {
    List<SearchResult> search(String query, List<Block> blocks);
    String name();
}

public class ExactMatchStrategy implements SearchStrategy {
    @Override
    public String name() { return "exact"; }

    @Override
    public List<SearchResult> search(String query, List<Block> blocks) {
        return blocks.stream()
            .filter(b -> b.getTextContent().contains(query))
            .map(b -> new SearchResult(b, 1.0))
            .toList();
    }
}

public class FuzzySearchStrategy implements SearchStrategy {
    private final double threshold;

    public FuzzySearchStrategy(double threshold) {
        this.threshold = threshold;
    }

    @Override
    public String name() { return "fuzzy"; }

    @Override
    public List<SearchResult> search(String query, List<Block> blocks) {
        return blocks.stream()
            .map(b -> new SearchResult(b, similarity(b.getTextContent(), query)))
            .filter(r -> r.score() >= threshold)
            .sorted(Comparator.comparingDouble(SearchResult::score).reversed())
            .toList();
    }

    private double similarity(String text, String query) {
        // Levenshtein-based similarity — isolated, testable
        int distance = levenshtein(text.toLowerCase(), query.toLowerCase());
        return 1.0 - (double) distance / Math.max(text.length(), query.length());
    }
}

public class RegexSearchStrategy implements SearchStrategy {
    @Override
    public String name() { return "regex"; }

    @Override
    public List<SearchResult> search(String query, List<Block> blocks) {
        Pattern pattern = Pattern.compile(query, Pattern.CASE_INSENSITIVE);
        return blocks.stream()
            .filter(b -> pattern.matcher(b.getTextContent()).find())
            .map(b -> new SearchResult(b, 1.0))
            .toList();
    }
}
```

## The Context: SearchEngine Simplified

```java
public class SearchEngine {
    private final Map<String, SearchStrategy> strategies = new HashMap<>();
    private SearchStrategy activeStrategy;

    public void register(SearchStrategy strategy) {
        strategies.put(strategy.name(), strategy);
    }

    public void setStrategy(String name) {
        activeStrategy = strategies.get(name);
        if (activeStrategy == null) throw new IllegalArgumentException("Unknown: " + name);
    }

    public List<SearchResult> search(String query, List<Block> blocks) {
        return activeStrategy.search(query, blocks);
    }
}
```

## Plugin-Provided Strategies

```java
public class CjkSearchPlugin implements Plugin {
    @Override
    public void onLoad(PluginContext ctx) {
        ctx.searchEngine().register(new CjkSearchStrategy());
    }
}

public class CjkSearchStrategy implements SearchStrategy {
    @Override public String name() { return "cjk"; }

    @Override
    public List<SearchResult> search(String query, List<Block> blocks) {
        // Character-level n-gram matching for Chinese/Japanese/Korean
        // No word boundaries needed
        return blocks.stream()
            .map(b -> new SearchResult(b, ngramScore(b.getTextContent(), query)))
            .filter(r -> r.score() > 0)
            .sorted(Comparator.comparingDouble(SearchResult::score).reversed())
            .toList();
    }
}
```

## Strategy with Lambdas

For simple strategies, functional interfaces work:

```java
// Strategy as a functional interface
@FunctionalInterface
public interface SortStrategy<T> {
    List<T> sort(List<T> items);
}

// Usage with lambdas
SortStrategy<Block> byDate = blocks ->
    blocks.stream().sorted(Comparator.comparing(Block::createdAt)).toList();

SortStrategy<Block> byRelevance = blocks ->
    blocks.stream().sorted(Comparator.comparingDouble(Block::score).reversed()).toList();
```

## PlugBoard After Strategy

Before: 300-line SearchEngine with hardcoded algorithms. Adding search modes means editing core code. Untestable in isolation.

After: Each algorithm is a standalone class. Plugins register custom strategies. Testing is trivial — instantiate one strategy, pass test data.

```java
// Testing a strategy in isolation
var strategy = new FuzzySearchStrategy(0.6);
var results = strategy.search("helo", List.of(
    new ParagraphBlock("hello world"),
    new ParagraphBlock("goodbye")
));
assertEquals(1, results.size());
```

## When NOT to Use Strategy

| Situation | Why Not | Alternative |
|---|---|---|
| Only one algorithm, won't change | Unnecessary abstraction | Inline the logic |
| Algorithm selection is compile-time only | No runtime flexibility needed | Method overloading |
| Strategies share 90% of code | Duplication across strategies | Template Method |
| Two lines of differing logic | Interface + class is overkill | Lambda or parameter |

## What You Learned

- **Strategy** — define a family of algorithms, encapsulate each, make them interchangeable
- **Context class** — holds a reference to the current strategy, delegates to it
- **Open/Closed** — new algorithms don't modify existing code
- **Testability** — each strategy is independently testable
- **Lambdas** — simple strategies don't need full classes

Next: PlugBoard has no undo. Users lose work constantly. We need to encapsulate actions as objects — that's Command.

---

[← Chapter 7: Facade](chapter-07-facade.md) | [Chapter 9: Command →](chapter-09-command.md)
