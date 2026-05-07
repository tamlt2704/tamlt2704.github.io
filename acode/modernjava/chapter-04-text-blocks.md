# Chapter 4: The String Butcher

[← Chapter 3: The Switch From Hell](chapter-03-switch-expressions.md) | [Chapter 5: The Null Minefield →](chapter-05-null-safety.md)

---

## The Incident

Marcus opens `EmailTemplateBuilder.java`. 140 lines. Most of it is string concatenation:

```java
String body = "Dear " + customer.getName() + ",\n\n"
    + "Your payment of $" + amount + " " + currency + " has been processed.\n"
    + "Transaction ID: " + txId + "\n"
    + "Date: " + date.format(DateTimeFormatter.ISO_LOCAL_DATE) + "\n\n"
    + "If you have questions, contact support@finpulse.com.\n\n"
    + "Best regards,\n"
    + "The FinPulse Team";
```

Then he opens `ReportQueryBuilder.java`. 40 lines of `StringBuilder`:

```java
StringBuilder sql = new StringBuilder();
sql.append("SELECT t.id, t.amount, t.currency,\n");
sql.append("       t.status, t.created_at,\n");
sql.append("       c.name AS customer_name\n");
sql.append("FROM transactions t\n");
sql.append("JOIN customers c ON c.id = t.customer_id\n");
sql.append("WHERE t.status = 'COMPLETED'\n");
sql.append("  AND t.created_at >= '").append(startDate).append("'\n");
sql.append("  AND t.created_at < '").append(endDate).append("'\n");
sql.append("ORDER BY t.created_at DESC");
```

Then the JSON test fixtures. Escaped quotes everywhere:

```java
String json = "{\"transactionId\": \"tx-1\", \"amount\": 42.50, \"currency\": \"USD\"}";
```

Priya: "Text blocks. All of these."

---

## Text Blocks: Multi-Line Strings

Triple quotes `"""` open a text block. Everything between the opening and closing `"""` is the string, with newlines preserved:

```java
String email = """
    Dear Customer,

    Your payment has been processed.
    Transaction ID: TX-12345

    Best regards,
    The FinPulse Team
    """;
```

No `\n`. No `+`. No `StringBuilder`. Just the text as it looks.

### The Test

```java
@Test
void textBlock_shouldPreserveNewlines() {
    String email = """
        Line one
        Line two
        Line three
        """;

    assertEquals(3, email.strip().lines().count());
    assertThat(email).contains("Line one\nLine two\nLine three");
}
```

---

## Indentation Control

The closing `"""` controls indentation. The compiler strips common leading whitespace:

```java
// Closing """ at column 0 → no stripping
String a = """
Hello
World
""";

// Closing """ indented → strips that much from every line
String b = """
        Hello
        World
        """;

// Both produce "Hello\nWorld\n"
```

The rule: the compiler finds the leftmost line (including the closing `"""`), and strips that many spaces from every line.

```
Source code:                    Resulting string:

    String s = """              "Hello\n"
        Hello                   "  World\n"
        """;                    

    String s = """              "Hello\n"
    Hello                       "World\n"
    """;
```

### The Test

```java
@Test
void textBlock_indentation_controlledByClosingQuotes() {
    String indented = """
            Hello
              World
            """;

    assertEquals("Hello\n  World\n", indented);
}
```

---

## Text Blocks for SQL

The `StringBuilder` query becomes readable:

```java
String sql = """
    SELECT t.id, t.amount, t.currency,
           t.status, t.created_at,
           c.name AS customer_name
    FROM transactions t
    JOIN customers c ON c.id = t.customer_id
    WHERE t.status = 'COMPLETED'
      AND t.created_at >= ?
      AND t.created_at < ?
    ORDER BY t.created_at DESC
    """;
```

Copy this SQL into any database tool and it runs. No escaping. No `.append()`.

---

## Text Blocks for JSON

Test fixtures become readable:

```java
// Before:
String json = "{\"transactionId\": \"tx-1\", \"amount\": 42.50, \"currency\": \"USD\"}";

// After:
String json = """
    {
        "transactionId": "tx-1",
        "amount": 42.50,
        "currency": "USD"
    }
    """;
```

No escaped quotes. Copy-paste from any JSON tool.

### The Test

```java
@Test
void textBlock_json_shouldParseCorrectly() throws Exception {
    String json = """
        {
            "transactionId": "tx-1",
            "amount": 42.50,
            "currency": "USD"
        }
        """;

    var mapper = new ObjectMapper();
    var node = mapper.readTree(json);

    assertEquals("tx-1", node.get("transactionId").asText());
    assertEquals(42.50, node.get("amount").asDouble());
}
```

---

## formatted(): String Interpolation (Sort Of)

Text blocks support `formatted()` — the same as `String.format()` but chainable:

```java
String email = """
    Dear %s,

    Your payment of $%.2f %s has been processed.
    Transaction ID: %s
    Date: %s

    Best regards,
    The FinPulse Team
    """.formatted(customerName, amount, currency, txId, date);
```

### The Test

```java
@Test
void formatted_shouldInterpolateValues() {
    String result = """
        Hello %s, you have %d messages.
        """.formatted("Priya", 5);

    assertThat(result).contains("Hello Priya").contains("5 messages");
}
```

---

## Escape Sequences

Two special escapes for text blocks:

| Escape | What It Does |
|---|---|
| `\s` | Explicit space — prevents trailing whitespace stripping |
| `\` (at end of line) | Line continuation — suppresses the newline |

```java
// \s preserves trailing spaces
String aligned = """
    Name:   \s
    Amount: \s
    """;

// \ at end of line joins lines
String oneLiner = """
    This is a very long string that \
    we want on one line in the output.\
    """;
```

### The Test

```java
@Test
void lineContinuation_shouldJoinLines() {
    String result = """
        Hello \
        World\
        """;

    assertEquals("Hello World", result);
}
```

---

## Text Blocks for HTML

```java
String html = """
    <html>
    <body>
        <h1>Payment Confirmation</h1>
        <p>Transaction: %s</p>
        <p>Amount: $%.2f</p>
    </body>
    </html>
    """.formatted(txId, amount);
```

---

## When NOT to Use Text Blocks

| Use Text Blocks For | Don't Use Text Blocks For |
|---|---|
| SQL queries | Single-line strings |
| JSON/XML test fixtures | Strings with no newlines |
| Email templates | Dynamic strings built in loops |
| HTML snippets | Strings where indentation is data |
| Log message templates | |

```java
// Overkill — just use a regular string
String name = """
    Alice""";  // don't do this

// Fine
String name = "Alice";
```

---

## What You Learned

| Concept | One-liner |
|---|---|
| Text blocks `"""` | Multi-line strings with preserved formatting |
| Indentation stripping | Closing `"""` position controls leading whitespace removal |
| `formatted()` | `String.format()` but chainable on text blocks |
| `\s` | Explicit space — prevents trailing whitespace stripping |
| `\` (end of line) | Line continuation — suppresses newline |
| No escaped quotes | `"` inside text blocks doesn't need `\"` |

---

## The Foreshadow

The string butchery is cleaned up. But Jenkins fails the nightly build. The stack trace:

```
java.lang.NullPointerException
    at com.finpulse.service.PaymentService.process(PaymentService.java:47)
```

Line 47: `payment.getCustomer().getAddress().getCity().toUpperCase()`

Which one is null? `payment`? `getCustomer()`? `getAddress()`? `getCity()`? The old NPE doesn't tell you. You spend 20 minutes adding breakpoints.

Priya: "Java 14 fixed this. And we have bigger null problems to solve."

That's **helpful NPEs** and **null safety patterns**.

---

[← Chapter 3: The Switch From Hell](chapter-03-switch-expressions.md) | [Chapter 5: The Null Minefield →](chapter-05-null-safety.md)
