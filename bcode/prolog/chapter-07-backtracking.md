# Chapter 7: Backtracking — Finding All Approvers

[← Chapter 6: Arithmetic](chapter-06-arithmetic.md) | [Chapter 8: Negation →](chapter-08-negation.md)

---

## The Problem

The Auditor arrives for the quarterly review: "For transaction T-2024-0042, show me ALL valid approvers. Not just the first one — every person who COULD have approved it."

In Java, you'd write a loop, collect results into an `ArrayList`, handle duplicates. In Prolog, backtracking is built into the engine.

## How Backtracking Works

When Prolog finds a solution, it doesn't stop. If you ask for more (with `;`), it **backtracks** — undoes its last choice and tries the next option:

```prolog
color(red).
color(green).
color(blue).

?- color(X).
X = red ;      % first solution
X = green ;    % backtrack, try next
X = blue ;     % backtrack, try next
false.         % no more options
```

## Choice Points

A **choice point** is created whenever Prolog has multiple clauses to try:

```prolog
director(alice).
director(bob).
director(carol).

approval_limit(alice, 100000).
approval_limit(bob, 50000).
approval_limit(carol, 200000).

can_approve(Person, Amount) :-
    director(Person),          % choice point: 3 directors to try
    approval_limit(Person, Limit),
    Amount =< Limit.
```

```prolog
?- can_approve(Who, 75000).
Who = alice ;    % 75000 =< 100000 ✓
Who = carol ;    % 75000 =< 200000 ✓
false.           % bob's limit is 50000, fails
```

Prolog tried bob, failed at `75000 =< 50000`, and backtracked to try carol.

## Visualizing the Search Tree

For `can_approve(Who, 75000)`:

```
can_approve(Who, 75000)
├── director(alice) → limit(alice, 100000) → 75000 =< 100000 ✓ → Who = alice
├── director(bob)   → limit(bob, 50000)    → 75000 =< 50000  ✗ → BACKTRACK
└── director(carol) → limit(carol, 200000) → 75000 =< 200000 ✓ → Who = carol
```

## The Cut: ! (Pruning the Search)

Sometimes you want to STOP backtracking. The **cut** (`!`) commits to the current choice:

```prolog
% Without cut: finds all matching categories
category(Amount, high)   :- Amount > 100000.
category(Amount, medium) :- Amount > 10000.
category(Amount, low)    :- Amount =< 10000.

?- category(500000, Cat).
Cat = high ;
Cat = medium ;    % Oops — 500000 also matches medium!
false.

% With cut: commits to first match
category(Amount, high)   :- Amount > 100000, !.
category(Amount, medium) :- Amount > 10000, !.
category(Amount, low).

?- category(500000, Cat).
Cat = high.       % Cut prevents trying other clauses
```

## Green Cut vs Red Cut

- **Green cut** — doesn't change the logic, just improves efficiency:
  ```prolog
  max(X, Y, X) :- X >= Y, !.  % No need to try second clause
  max(_, Y, Y).
  ```

- **Red cut** — changes the meaning (use with caution):
  ```prolog
  % Without the cut, this would give wrong answers
  category(Amount, high) :- Amount > 100000, !.
  category(_, low).  % Relies on cut to exclude high amounts
  ```

## InferLaw: The Auditor's Query

```prolog
% Complete approval rules
can_approve_transaction(Person, TransID) :-
    director(Person),
    transaction(TransID, Amount, _Type, Originator),
    approval_limit(Person, Limit),
    Amount =< Limit,
    Person \= Originator,
    \+ conflict_of_interest(Person, TransID).

% The Auditor wants ALL approvers
?- findall(Person, can_approve_transaction(Person, t2024_0042), Approvers).
Approvers = [alice, carol, diana].
```

## once/1 — Find Only the First Solution

```prolog
% "Just tell me IF someone can approve — I don't need all of them"
?- once(can_approve_transaction(_, t2024_0042)).
true.

% Equivalent to:
has_valid_approver(TransID) :-
    can_approve_transaction(_, TransID), !.
```

## Controlling Backtracking in Practice

```prolog
% Find the BEST approver (highest limit, first match)
best_approver(TransID, Person) :-
    transaction(TransID, Amount, _, _),
    approval_limit(Person, Limit),
    Limit >= Amount,
    director(Person),
    \+ conflict_of_interest(Person, TransID),
    !.  % Commit to first valid match

% Find approvers with a minimum level
approvers_above_level(TransID, MinLevel, Approvers) :-
    findall(P,
        (can_approve_transaction(P, TransID),
         levels_above(P, _, N), N >= MinLevel),
        Approvers).
```

## Exercises

1. Write `first_violation(Quarter, V)` that finds only the first violation (using cut or once).
2. Trace through `can_approve(Who, 150000)` manually — which directors fail and why?
3. Write a `classify_risk/2` predicate with green cuts for low/medium/high/critical.

## What You Learned

- **Backtracking** — Prolog automatically tries all alternatives on failure
- **Choice points** — created when multiple clauses match
- **`;` at the prompt** — asks for the next solution
- **Cut `!`** — commits to current choice, prunes remaining alternatives
- **Green vs red cuts** — efficiency optimization vs logic change
- **once/1** — find just the first solution
- **findall/3** — collect all backtracking solutions into a list

The Auditor nods. "Good, you can find all approvers. Now prove there's NO conflict of interest." That requires negation — and it's trickier than you'd think.

---

[← Chapter 6: Arithmetic](chapter-06-arithmetic.md) | [Chapter 8: Negation →](chapter-08-negation.md)
