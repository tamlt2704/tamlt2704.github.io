# Chapter 5: Lists — Collecting Violations

[← Chapter 4: Recursion](chapter-04-recursion.md) | [Chapter 6: Arithmetic →](chapter-06-arithmetic.md)

---

## The Problem

Jordan slams a filing on your desk: "I don't just need to know IF there's a violation. I need ALL violations in this quarter's filing — as a list I can hand to the auditor."

Legacy Java had a `ViolationCollector` class with 400 lines of iterator logic. You need one predicate.

## List Notation

Prolog lists use square brackets:

```prolog
% A list of atoms
[apple, banana, cherry].

% A list of numbers
[1, 2, 3, 4, 5].

% An empty list
[].

% A list can contain anything — even other lists
[alice, 42, [nested, list], transaction(t001)].
```

## Head and Tail: The `[H|T]` Pattern

Every non-empty list has a **head** (first element) and a **tail** (everything else):

```prolog
?- [H|T] = [a, b, c, d].
H = a,
T = [b, c, d].

?- [First, Second | Rest] = [1, 2, 3, 4, 5].
First = 1,
Second = 2,
Rest = [3, 4, 5].

?- [X|_] = [hello, world].
X = hello.

?- [_|T] = [only_one].
T = [].
```

## Essential List Predicates

### member/2 — Is X in the list?

```prolog
member(X, [X|_]).           % X is the head
member(X, [_|T]) :- member(X, T).  % X is in the tail

?- member(b, [a, b, c]).
true.

?- member(X, [alice, bob, carol]).
X = alice ; X = bob ; X = carol ; false.
```

### append/3 — Concatenate two lists

```prolog
append([], L, L).
append([H|T1], L2, [H|T3]) :- append(T1, L2, T3).

?- append([1, 2], [3, 4], Result).
Result = [1, 2, 3, 4].

% append works in reverse too!
?- append(X, [4, 5], [1, 2, 3, 4, 5]).
X = [1, 2, 3].
```

### length/2 — How many elements?

```prolog
?- length([a, b, c], N).
N = 3.
```

## findall/3 — Collecting All Solutions

This is the key predicate for Jordan's request:

```prolog
% findall(Template, Goal, List)
% Collects all instances of Template where Goal succeeds

% Facts
violation(q1_2024, filing_001, late_submission).
violation(q1_2024, filing_001, missing_signature).
violation(q1_2024, filing_002, amount_mismatch).
violation(q2_2024, filing_003, late_submission).

% Collect all violations for Q1
?- findall(V, violation(q1_2024, _, V), Violations).
Violations = [late_submission, missing_signature, amount_mismatch].

% Collect violations with their filing IDs
?- findall(Filing-Type, violation(q1_2024, Filing, Type), Results).
Results = [filing_001-late_submission, filing_001-missing_signature,
           filing_002-amount_mismatch].
```

## InferLaw's Violation Report

```prolog
% Rules that define what counts as a violation
is_violation(TransID, over_limit) :-
    transaction(TransID, Amount, _, _),
    Amount > 100000,
    \+ has_approval(TransID).

is_violation(TransID, self_approved) :-
    transaction(TransID, _, _, Originator),
    approved_by(TransID, Originator).

is_violation(TransID, conflict) :-
    transaction(TransID, _, _, _),
    conflict_of_interest(TransID).

% Collect all violations for a quarter
quarterly_violations(Quarter, Report) :-
    findall(
        violation(TransID, Type),
        (filed_in(TransID, Quarter), is_violation(TransID, Type)),
        Report
    ).
```

```prolog
?- quarterly_violations(q1_2024, Report).
Report = [violation(t001, over_limit), violation(t003, self_approved),
          violation(t005, conflict)].

?- quarterly_violations(q1_2024, Report), length(Report, Count).
Count = 3.
```

## Processing Lists Recursively

```prolog
% Count violations by type
count_type(_, [], 0).
count_type(Type, [violation(_, Type)|Rest], N) :-
    count_type(Type, Rest, N1),
    N is N1 + 1.
count_type(Type, [violation(_, Other)|Rest], N) :-
    Type \= Other,
    count_type(Type, Rest, N).
```

## bagof/3 and setof/3

```prolog
% bagof — like findall but fails if no solutions (and respects ^)
?- bagof(V, violation(q1_2024, _, V), Vs).
Vs = [late_submission, missing_signature, amount_mismatch].

% setof — like bagof but sorted and deduplicated
?- setof(V, F^violation(q1_2024, F, V), UniqueTypes).
UniqueTypes = [amount_mismatch, late_submission, missing_signature].
```

The `F^` means "there exists some F" — it existentially quantifies over Filing.

## Exercises

1. Write `last(List, X)` that finds the last element of a list.
2. Write `count_violations(Quarter, Type, Count)` using findall and length.
3. Use `setof` to find all unique violation types across all quarters.

## What You Learned

- **List notation** — `[a, b, c]` and the empty list `[]`
- **Head|Tail** — `[H|T]` destructures a list into first element and rest
- **member/2** — check or generate list elements
- **append/3** — concatenate lists (works in multiple directions)
- **findall/3** — collect all solutions into a list
- **bagof/3, setof/3** — alternatives with different failure/sorting behavior

Jordan nods at the violation list. "Good. Now tell me — is the TOTAL amount of flagged transactions over the regulatory threshold?" Time for arithmetic.

---

[← Chapter 4: Recursion](chapter-04-recursion.md) | [Chapter 6: Arithmetic →](chapter-06-arithmetic.md)
