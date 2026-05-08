# Chapter 1: Facts and Queries

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Rules →](chapter-02-rules.md)

---

## The Problem

InferLaw's first task: answer simple questions about the company structure.

"Is Alice a director?"
"Is Bob in the compliance department?"
"Who are the directors?"

The Java version:

```java
boolean isDirector(String name) {
    return name.equals("alice") || name.equals("bob") || name.equals("carol");
}
```

Every time someone gets promoted, a developer edits the code, recompiles, and redeploys. Jordan (the compliance officer) can't update it herself. She has to file a ticket.

Dr. Vasquez: "The knowledge should be separate from the logic. State the facts. Let the system answer questions."

## Facts: Stating What's True

In Prolog, a **fact** is a statement that something is true. No conditions, no logic — just truth.

```prolog
% People and their roles
director(alice).
director(bob).
director(carol).

analyst(dave).
analyst(eve).

% Department membership
department(alice, legal).
department(bob, finance).
department(carol, compliance).
department(dave, compliance).
department(eve, finance).
```

That's it. Six facts about roles. Five facts about departments. Save this as `company.pl`.

### Anatomy of a Fact

```prolog
director(alice).
│        │    │
│        │    └── Period: ends every statement
│        └────── Argument: an atom (constant)
└─────────────── Functor: the relationship name
```

- **Functor**: the name of the relationship (`director`, `department`)
- **Arguments**: the things involved (`alice`, `legal`)
- **Period**: every Prolog statement ends with a `.`
- **Lowercase**: atoms (constants) are lowercase. `alice`, not `Alice`.

## Queries: Asking Questions

Load the file and ask questions:

```bash
$ swipl
?- [company].    % Load company.pl
true.
```

### "Is Alice a director?"

```prolog
?- director(alice).
true.
```

Prolog searches its knowledge base. It finds `director(alice).` — match! Returns `true`.

### "Is Dave a director?"

```prolog
?- director(dave).
false.
```

No fact `director(dave)` exists. Prolog returns `false` (meaning: "I can't prove this is true").

### "Is Alice in the legal department?"

```prolog
?- department(alice, legal).
true.
```

### "Is Alice in finance?"

```prolog
?- department(alice, finance).
false.
```

## Variables: Asking "Who?"

Uppercase names are **variables** — unknowns that Prolog fills in:

### "Who are the directors?"

```prolog
?- director(Who).
Who = alice ;
Who = bob ;
Who = carol ;
false.
```

Prolog finds every fact that matches `director(Who)` and reports each binding. Press `;` for the next answer. `false` means "no more answers."

### "What department is Bob in?"

```prolog
?- department(bob, Dept).
Dept = finance.
```

### "Who is in the compliance department?"

```prolog
?- department(Person, compliance).
Person = carol ;
Person = dave ;
false.
```

## Multiple Arguments

Facts can have any number of arguments:

```prolog
% transaction(ID, Person, Amount, Type)
transaction(t001, alice, 50000, transfer).
transaction(t002, bob, 120000, purchase).
transaction(t003, carol, 8000, transfer).
transaction(t004, dave, 250000, purchase).
```

### "What are all of Alice's transactions?"

```prolog
?- transaction(ID, alice, Amount, Type).
ID = t001, Amount = 50000, Type = transfer.
```

### "Which transactions are over $100,000?"

We can't do arithmetic comparisons yet (Chapter 6), but we can find specific amounts:

```prolog
?- transaction(ID, Person, 120000, Type).
ID = t002, Person = bob, Type = purchase.
```

## Compound Queries: Asking "And"

Use `,` (comma) for "and":

### "Who is a director AND in the compliance department?"

```prolog
?- director(Person), department(Person, compliance).
Person = carol.
```

Prolog finds someone who satisfies BOTH conditions. Only Carol is both a director and in compliance.

### "Who is a director AND in finance?"

```prolog
?- director(Person), department(Person, finance).
Person = bob.
```

## The Knowledge Base So Far

```prolog
% company.pl — InferLaw's first knowledge base

% Roles
director(alice).
director(bob).
director(carol).
analyst(dave).
analyst(eve).

% Departments
department(alice, legal).
department(bob, finance).
department(carol, compliance).
department(dave, compliance).
department(eve, finance).

% Transactions
transaction(t001, alice, 50000, transfer).
transaction(t002, bob, 120000, purchase).
transaction(t003, carol, 8000, transfer).
transaction(t004, dave, 250000, purchase).
transaction(t005, eve, 15000, transfer).
```

Jordan can now update this file directly — add a new director, a new transaction — without touching any logic code. The facts are data. The queries are questions. No recompilation needed.

## Prolog vs SQL

If this feels like a database, you're not wrong:

| SQL | Prolog |
|---|---|
| `SELECT * FROM directors WHERE name = 'alice'` | `director(alice).` |
| `SELECT name FROM directors` | `director(Name).` |
| `SELECT * FROM dept WHERE dept = 'compliance'` | `department(Person, compliance).` |
| `SELECT ... WHERE ... AND ...` | `goal1, goal2.` |

The difference becomes clear in Chapter 2: Prolog rules can be recursive, self-referential, and express logic that SQL can't.

## Exercises

1. Add facts for a new employee `frank` who is an analyst in the legal department. Query to verify.

2. Add a new relationship `reports_to(Subordinate, Manager)` with at least 4 facts. Query: "Who reports to Alice?"

3. Write a compound query: "Find all analysts in the finance department."

4. What happens if you query `director(X), analyst(X).`? Why?

## What You Learned

- **Facts** — unconditional truths: `director(alice).`
- **Queries** — questions to the knowledge base: `?- director(alice).`
- **Variables** — uppercase, Prolog fills them in: `director(Who).`
- **Compound queries** — comma means "and": `director(X), department(X, finance).`
- **Closed-world assumption** — if Prolog can't prove it, it's `false`
- **The knowledge base** — a collection of facts (and later, rules)

Jordan can now ask "who is a director in compliance?" without writing code. But she has a harder question: "Can Alice approve transaction t004?" That requires *rules* — conditions that must be checked. Chapter 2.

---

[← Chapter 0: Overview](chapter-00-overview.md) | [Chapter 2: Rules →](chapter-02-rules.md)
