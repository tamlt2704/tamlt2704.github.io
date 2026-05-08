# Chapter 3: Unification — Pattern Matching

[← Chapter 2: Rules](chapter-02-rules.md) | [Chapter 4: Recursion →](chapter-04-recursion.md)

---

## The Problem

Jordan asks a general question: "Who can approve transactions over $10,000?"

She doesn't have a specific transaction in mind. She wants to know the general policy — which people have the authority for large transactions.

In Java, you'd write a query method. In Prolog, you just ask:

```prolog
?- can_approve(Who, TransID),
   transaction(TransID, Amount, _, _),
   Amount > 10000.
```

But how does Prolog find the answer? It uses **unification** — its core pattern-matching mechanism.

## What Is Unification?

Unification is Prolog's way of making two terms identical by finding variable bindings:

```prolog
?- X = hello.
X = hello.          % X is bound to 'hello'

?- f(X, b) = f(a, Y).
X = a, Y = b.      % X must be 'a', Y must be 'b' for terms to match

?- f(X, X) = f(a, b).
false.              % X can't be both 'a' and 'b'
```

Unification answers: "Can these two terms be made identical by substituting variables?"

## Unification Rules

1. **A variable unifies with anything** (and becomes bound to it)
2. **An atom unifies only with the same atom**
3. **A compound term unifies with another compound term** if they have the same functor, same arity, and all arguments unify

```prolog
% Variables unify with anything
?- X = 42.              % X = 42 ✓
?- X = hello.           % X = hello ✓
?- X = f(a, b).         % X = f(a, b) ✓

% Atoms unify only with themselves
?- hello = hello.       % ✓
?- hello = world.       % ✗ (different atoms)

% Compound terms: same functor, same arity, args unify
?- date(2024, 1, X) = date(2024, 1, 15).
X = 15.                 % ✓

?- date(2024, X, 15) = date(Y, 3, 15).
X = 3, Y = 2024.       % ✓

?- point(X, Y) = point(3).
false.                  % Different arity (2 vs 1)
```

## How Prolog Uses Unification

When you ask a query, Prolog tries to unify it with each fact and rule head in order:

```prolog
% Knowledge base:
likes(alice, cats).
likes(bob, dogs).
likes(alice, dogs).

% Query:
?- likes(alice, What).
```

Prolog tries each fact:
1. `likes(alice, What)` unifies with `likes(alice, cats)` → `What = cats` ✓
2. Press `;` → backtrack, try next: `likes(bob, dogs)` → `alice ≠ bob` ✗
3. Try next: `likes(alice, dogs)` → `What = dogs` ✓

## Unification in InferLaw's Rules

```prolog
% Facts
transaction(t001, 50000, transfer, dave).
transaction(t002, 120000, purchase, bob).
approval_limit(alice, 100000).
approval_limit(carol, 200000).

% Rule
can_approve(Person, TransID) :-
    director(Person),
    transaction(TransID, Amount, _, Originator),
    approval_limit(Person, Limit),
    Amount =< Limit,
    Person \= Originator.
```

Query: `?- can_approve(Who, t002).`

Prolog's process:
1. Try to unify `can_approve(Who, t002)` with rule head `can_approve(Person, TransID)`
   - `Who = Person`, `TransID = t002` ✓
2. Now prove the body with `TransID = t002`:
   - `director(Person)` → try `Person = alice` ✓
   - `transaction(t002, Amount, _, Originator)` → `Amount = 120000, Originator = bob` ✓
   - `approval_limit(alice, Limit)` → `Limit = 100000` ✓
   - `120000 =< 100000` → ✗ FAIL!
3. Backtrack: try `Person = bob`
   - `director(bob)` ✓
   - `transaction(t002, 120000, _, bob)` → `Originator = bob` ✓
   - `approval_limit(bob, Limit)` → no fact! ✗ FAIL!
4. Backtrack: try `Person = carol`
   - `director(carol)` ✓
   - `transaction(t002, 120000, _, bob)` ✓
   - `approval_limit(carol, 200000)` → `Limit = 200000` ✓
   - `120000 =< 200000` ✓
   - `carol \= bob` ✓
   - **SUCCESS!** `Who = carol`

## The Anonymous Variable: _

When you don't care about a value, use `_`:

```prolog
% "Find all transaction amounts" (don't care about ID, type, or originator)
?- transaction(_, Amount, _, _).
Amount = 50000 ;
Amount = 120000 ;
...
```

Each `_` is independent — they don't have to match each other:

```prolog
% This means "any ID, any amount, any type, any originator"
transaction(_, _, _, _).

% NOT the same as:
transaction(X, X, X, X).  % This means all four fields must be EQUAL
```

## Partial Matching: Flexible Queries

Unification lets you query with any combination of known/unknown fields:

```prolog
% "All transfers"
?- transaction(ID, Amount, transfer, Who).

% "All transactions by Dave"
?- transaction(ID, Amount, Type, dave).

% "All transactions over $100K" (need arithmetic, but the pattern matching part:)
?- transaction(ID, Amount, Type, Who), Amount > 100000.

% "All purchase transactions by Bob"
?- transaction(ID, Amount, purchase, bob).
```

No special query language needed. Just put variables where you want answers and constants where you have constraints.

## Unification Failures (Debugging)

When a query returns `false`, it means unification failed somewhere. Common causes:

```prolog
% Typo in atom name
?- director(allice).    % 'allice' ≠ 'alice'
false.

% Wrong arity
?- transaction(t001, 50000).  % Fact has 4 args, query has 2
false.

% Conflicting bindings
?- X = 5, X = 10.      % X can't be both 5 and 10
false.
```

## The Occurs Check

A subtle point: can a variable unify with a term containing itself?

```prolog
?- X = f(X).
% In standard Prolog: X = f(f(f(f(...)))) — infinite term!
% SWI-Prolog allows this (creates a cyclic term)
% With occurs check: unify_with_occurs_check(X, f(X)) → false
```

In practice, this rarely matters. But if you get infinite loops, the occurs check might be the issue.

## Jordan's General Policy Query

Back to the original question: "Who can approve transactions over $10,000?"

```prolog
% "Find all Person-Transaction pairs where Person can approve and amount > 10000"
?- can_approve(Person, TransID),
   transaction(TransID, Amount, _, _),
   Amount > 10000.

Person = carol, TransID = t002, Amount = 120000 ;
Person = alice, TransID = t001, Amount = 50000... 
% Wait, 50000 > 10000, so this is valid too
```

Or more specifically: "Which directors have limits over $10,000?"

```prolog
?- director(Person), approval_limit(Person, Limit), Limit > 10000.
Person = alice, Limit = 100000 ;
Person = carol, Limit = 200000 ;
false.
```

Jordan: "Perfect. Alice and Carol can handle large transactions. Bob needs a limit increase."

## Exercises

1. Given `person(name, age, city)` facts, write queries to find:
   - All people in "london"
   - All people over 30
   - All people in the same city as alice

2. What does `f(X, Y) = f(Y, X)` unify to? What about `f(X, a) = f(b, X)`?

3. Write a fact `address(person, street, city, zip)` and query for all people on the same street.

## What You Learned

- **Unification** — making two terms identical by binding variables
- **Variables** unify with anything; **atoms** only with themselves
- **Compound terms** unify if same functor, same arity, all args unify
- **Anonymous variable `_`** — matches anything, each `_` is independent
- **Prolog's search** — tries each fact/rule in order, backtracks on failure
- **Flexible queries** — put variables where you want answers, constants where you have constraints

Unification handles flat queries well. But Jordan's next question involves hierarchy: "Is Alice above Bob in the org chart?" That requires following chains of relationships — which means recursion.

---

[← Chapter 2: Rules](chapter-02-rules.md) | [Chapter 4: Recursion →](chapter-04-recursion.md)
