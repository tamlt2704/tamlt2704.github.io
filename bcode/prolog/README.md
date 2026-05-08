# Prolog — Logic Programming from Zero

A narrative-driven course on Prolog. You're a knowledge engineer at **InferLaw**, a legal-tech startup building an automated compliance checker. The system must answer questions like "Is this transaction legal?" by reasoning over rules — not by writing if-else chains. Prolog is the perfect fit.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, declarative vs imperative, the cast |
| 01 | [Facts and Queries](chapter-01-facts.md) | "Is Alice a director?" — hardcoded lookups | Facts, queries, the knowledge base |
| 02 | [Rules](chapter-02-rules.md) | "Can Alice approve this?" — complex conditions | Rules, implication, conjunction |
| 03 | [Unification](chapter-03-unification.md) | "Who can approve transactions over $10K?" | Unification, pattern matching, variables |
| 04 | [Recursion](chapter-04-recursion.md) | "Is Alice above Bob in the org chart?" | Recursive rules, base cases, ancestor/descendant |
| 05 | [Lists](chapter-05-lists.md) | "List all violations in this filing" | List notation, head/tail, member, append |
| 06 | [Arithmetic](chapter-06-arithmetic.md) | "Is the total over the threshold?" | is/2, comparison operators, constraints |
| 07 | [Backtracking](chapter-07-backtracking.md) | "Find ALL valid approvers" | Backtracking, choice points, cut (!) |
| 08 | [Negation](chapter-08-negation.md) | "Is there NO conflict of interest?" | Negation as failure, \+, closed-world assumption |
| 09 | [Input/Output](chapter-09-io.md) | "Generate a compliance report" | read, write, file I/O, formatting |
| 10 | [Structures](chapter-10-structures.md) | "Model a transaction with nested fields" | Compound terms, functors, arity |
| 11 | [DCGs](chapter-11-dcg.md) | "Parse legal document clauses" | Definite Clause Grammars, parsing |
| 12 | [Meta-Programming](chapter-12-meta.md) | "Rules that generate rules" | assert, retract, call/N, meta-interpreters |
| 13 | [Constraint Logic](chapter-13-clp.md) | "Schedule hearings with constraints" | CLP(FD), constraint propagation, labeling |
| 14 | [Real-World Prolog](chapter-14-production.md) | "Ship the compliance engine" | Modules, testing, integration with Java/Python |

## Prerequisites

- SWI-Prolog 9+ (`swipl`)
- A terminal and text editor

## Philosophy

Every Prolog concept is introduced because imperative code can't express the rule cleanly. You'll see the tangled if-else version first, then the elegant Prolog declaration. The procedural pain comes first. The declarative clarity follows.
