# Chapter 0: Before You Start

[Chapter 1: Facts and Queries →](chapter-01-facts.md)

---

## The Story

You're a knowledge engineer at **InferLaw**, a legal-tech startup building an automated compliance checker. Financial institutions send you their transaction data, and your system must answer questions like:

- "Is this transaction legal under regulation X?"
- "Who is authorized to approve this?"
- "Are there any conflicts of interest?"
- "List all violations in this quarter's filings."

The previous developer tried to build this with Java. The result: 15,000 lines of nested if-else statements, a 200-case switch for regulation types, and a `ComplianceEngine` class that nobody can modify without breaking something.

Your CTO, **Dr. Vasquez**, a former AI researcher, suggests a different approach:

"These are logical rules. 'A person can approve a transaction if they are a director AND the amount is under their limit AND they have no conflict of interest.' That's not an algorithm — it's a declaration. Use a language designed for declarations."

She points you to Prolog.

Over 14 chapters, you'll rebuild InferLaw's compliance engine in Prolog — a language where you state facts and rules, and the system figures out the answers through logical inference.

## What Is Prolog?

Prolog is a **logic programming language**. Instead of telling the computer *how* to compute something (step by step), you tell it *what* is true, and it figures out the rest.

### Imperative (Java) — How to check authorization:

```java
boolean canApprove(Person p, Transaction t) {
    if (!p.isDirector()) return false;
    if (t.getAmount() > p.getApprovalLimit()) return false;
    if (hasConflict(p, t)) return false;
    return true;
}
```

### Declarative (Prolog) — What authorization means:

```prolog
can_approve(Person, Transaction) :-
    director(Person),
    amount(Transaction, Amount),
    approval_limit(Person, Limit),
    Amount =< Limit,
    \+ conflict_of_interest(Person, Transaction).
```

Same logic. But the Prolog version is a *rule* — you can also ask "WHO can approve this transaction?" and Prolog will find all valid answers by searching through possibilities. The Java version only checks one person at a time.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Knowledge Engineer | Recovering imperative programmer |
| **Dr. Vasquez** | CTO | "If you can't state it as a rule, you don't understand it." |
| **Jordan** | Compliance Officer | Provides the rules in English. "It's simple, really..." |
| **The Auditor** | External | "Prove your system is correct." |
| **Legacy Java** | The old system | 15,000 lines of if-else. Haunts your dreams. |

## Prerequisites

### SWI-Prolog 9+

The most widely used Prolog implementation. Free, cross-platform, excellent documentation.

```bash
# Check installation
swipl --version
# SWI-Prolog version 9.x.x
```

**Installation:**
- Windows: Download from https://www.swi-prolog.org/download/stable
- macOS: `brew install swi-prolog`
- Linux: `sudo apt install swi-prolog`

### Running Prolog

```bash
# Start the interactive interpreter
swipl

# Load a file
?- [compliance].    % loads compliance.pl

# Ask a query
?- can_approve(alice, transaction_42).
true.

# Find all answers
?- can_approve(Who, transaction_42).
Who = alice ;
Who = bob ;
false.

# Exit
?- halt.
```

The `?-` prompt means Prolog is waiting for a query. The `;` means "are there more answers?" and `false` (or `no`) means "no more answers."

### Key Syntax (Just Enough to Start)

```prolog
% This is a comment

% A fact: Alice is a director
director(alice).

% A rule: X can_approve Y if...
can_approve(X, Y) :- director(X), amount(Y, A), A =< 10000.

% A query (at the ?- prompt):
?- director(alice).
% true.
```

- **Lowercase** = atoms (constants): `alice`, `transaction_42`
- **Uppercase** = variables: `X`, `Person`, `Amount`
- **`:-`** = "if" (read right to left: "head is true if body is true")
- **`,`** = "and"
- **`.`** = end of statement

That's all you need for Chapter 1.

## The Mental Shift

Coming from imperative programming, Prolog requires a mental shift:

| Imperative | Prolog |
|---|---|
| You write steps | You write rules |
| You control execution order | Prolog searches for solutions |
| Variables are boxes you put values in | Variables are unknowns to be solved |
| Functions return one answer | Queries can return many answers |
| You handle "not found" | Prolog returns `false` |

The hardest part isn't the syntax — it's letting go of control. You don't tell Prolog *how* to find the answer. You tell it what the answer *looks like*, and it searches.

## The Roadmap

| Ch | The Problem | The Prolog Concept |
|---|---|---|
| 1 | "Is Alice a director?" | Facts and queries |
| 2 | "Can Alice approve this?" | Rules |
| 3 | "Who can approve transactions over $10K?" | Unification and variables |
| 4 | "Is Alice above Bob in the org chart?" | Recursion |
| 5 | "List all violations" | Lists |
| 6 | "Is the total over the threshold?" | Arithmetic |
| 7 | "Find ALL valid approvers" | Backtracking |
| 8 | "Is there NO conflict?" | Negation |
| 9 | "Generate a report" | I/O |
| 10 | "Model a complex transaction" | Structures |
| 11 | "Parse legal clauses" | DCGs |
| 12 | "Rules that generate rules" | Meta-programming |
| 13 | "Schedule with constraints" | CLP(FD) |
| 14 | "Ship it" | Production Prolog |

Let's state our first facts.

---

[Chapter 1: Facts and Queries →](chapter-01-facts.md)
