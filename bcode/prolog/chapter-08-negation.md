# Chapter 8: Negation — Proving Absence

[← Chapter 7: Backtracking](chapter-07-backtracking.md) | [Chapter 9: I/O →](chapter-09-io.md)

---

## The Problem

The Auditor leans forward: "Prove there is NO conflict of interest for this approval. Not 'you didn't find one' — prove it doesn't exist."

This is philosophically tricky. Prolog uses the **Closed-World Assumption**: if something can't be proven true, it's assumed false. That's actually perfect for compliance — if we can't find a conflict, there isn't one (in our system).

## Negation as Failure: \+

Prolog's negation operator is `\+` (read: "not provable"):

```prolog
?- \+ member(x, [a, b, c]).
true.    % x is NOT a member of [a, b, c]

?- \+ member(a, [a, b, c]).
false.   % a IS a member, so "not member" fails
```

`\+ Goal` succeeds if `Goal` **fails**, and fails if `Goal` **succeeds**.

## The Closed-World Assumption

```prolog
% We only state what IS true:
has_conflict(alice, acme_corp).
has_conflict(bob, globex).

% Anything not stated is assumed false:
?- has_conflict(carol, acme_corp).
false.   % Not stated → assumed not true

?- \+ has_conflict(carol, acme_corp).
true.    % Carol has no conflict with Acme
```

This is exactly how compliance works: you declare known conflicts, and absence of a declaration means no conflict.

## InferLaw's Conflict Check

```prolog
% Known conflicts of interest
conflict(alice, acme_corp).
conflict(bob, globex).
conflict(bob, initech).

% A transaction involves a company
involves(t001, acme_corp).
involves(t002, globex).
involves(t003, wayne_ent).

% Conflict of interest exists if approver has conflict with involved company
conflict_of_interest(Person, TransID) :-
    conflict(Person, Company),
    involves(TransID, Company).

% Safe to approve: no conflict exists
safe_to_approve(Person, TransID) :-
    director(Person),
    \+ conflict_of_interest(Person, TransID).
```

```prolog
?- safe_to_approve(alice, t001).
false.   % Alice has conflict with Acme, t001 involves Acme

?- safe_to_approve(alice, t003).
true.    % Alice has no conflict with Wayne Enterprises

?- safe_to_approve(carol, t001).
true.    % Carol has no conflicts at all
```

## The Variable Trap

**Warning:** `\+` does NOT bind variables:

```prolog
?- \+ member(X, [a, b, c]).
false.   % WRONG intuition! X CAN be a member (X=a works), so \+ fails

% What you probably meant:
?- \+ member(d, [a, b, c]).
true.    % d specifically is not a member
```

Rule: **Always ground your variables before negation**, or use negation only on fully instantiated goals.

```prolog
% WRONG: Who has no conflict? (X is unbound)
?- \+ conflict(X, _).
false.   % conflict(alice, acme_corp) succeeds, so \+ fails

% RIGHT: Check a specific person
no_conflicts(Person) :-
    director(Person),           % Bind Person first!
    \+ conflict(Person, _).    % Then negate

?- no_conflicts(carol).
true.
```

## Combining Negation with Rules

```prolog
% Complete approval rule with negation
can_approve(Person, TransID) :-
    director(Person),
    transaction(TransID, Amount, _, Originator),
    approval_limit(Person, Limit),
    Amount =< Limit,
    Person \= Originator,
    \+ conflict_of_interest(Person, TransID).

% Find all people who CANNOT approve (for audit trail)
cannot_approve(Person, TransID, Reason) :-
    director(Person),
    transaction(TransID, Amount, _, _),
    approval_limit(Person, Limit),
    Amount > Limit,
    Reason = over_limit.

cannot_approve(Person, TransID, Reason) :-
    director(Person),
    transaction(TransID, _, _, Person),
    Reason = self_approval.

cannot_approve(Person, TransID, Reason) :-
    director(Person),
    conflict_of_interest(Person, TransID),
    Reason = conflict.
```

```prolog
?- cannot_approve(bob, t002, Why).
Why = conflict.

?- findall(P-R, cannot_approve(P, t001, R), Issues).
Issues = [alice-conflict, bob-over_limit].
```

## if-then-else: ( Cond -> Then ; Else )

```prolog
approval_status(Person, TransID, Status) :-
    (conflict_of_interest(Person, TransID)
    ->  Status = blocked
    ;   (can_approve(Person, TransID)
        ->  Status = approved
        ;   Status = insufficient_authority
        )
    ).
```

## Exercises

1. Write `clean_record(Person)` — true if Person has no violations in any quarter.
2. Why does `?- \+ X = 1.` return `false`? Explain.
3. Write `all_clear(TransID)` — true if NO director has a conflict with the transaction.

## What You Learned

- **`\+` (negation as failure)** — succeeds when the goal cannot be proven
- **Closed-World Assumption** — unstated facts are assumed false
- **Variable trap** — always bind variables before negating
- **Negation in rules** — use `\+` to express "no conflict exists"
- **if-then-else** — `( Cond -> Then ; Else )` for conditional logic

The Auditor is satisfied — for now. Jordan has a new request: "Can you generate a formatted compliance report I can email to the board?" Time for I/O.

---

[← Chapter 7: Backtracking](chapter-07-backtracking.md) | [Chapter 9: I/O →](chapter-09-io.md)
