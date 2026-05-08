# Chapter 10: Structures — Modeling Complex Data

[← Chapter 9: I/O](chapter-09-io.md) | [Chapter 11: DCGs →](chapter-11-dcg.md)

---

## The Problem

Dr. Vasquez reviews the transaction model: "A real transaction isn't just an ID and amount. It has parties, dates, sub-transactions, metadata. We need to model this properly — without creating a 20-table relational schema."

Legacy Java had `Transaction.java` with 47 fields, 12 nested objects, and a `TransactionBuilder` with 200 lines. Prolog's compound terms handle this naturally.

## Compound Terms (Structures)

In Prolog, structures are just terms with a **functor** and **arguments**:

```prolog
% functor: date, arity: 3
date(2024, 3, 15).

% functor: person, arity: 3
person(alice, smith, director).

% functor: address, arity: 3
address('123 Main St', springfield, '62704').
```

There's no class definition needed. You just use them.

## Functors and Arity

```prolog
% functor/arity is the "type signature"
?- functor(date(2024, 3, 15), F, A).
F = date, A = 3.

?- functor(hello, F, A).
F = hello, A = 0.    % Atoms are functors with arity 0

% Decompose a term
?- date(2024, 3, 15) =.. List.
List = [date, 2024, 3, 15].    % "univ" operator
```

## Nested Structures

```prolog
% A transaction with nested fields
transaction(
    id(t2024_0042),
    amount(usd, 250000),
    parties(
        originator(person(dave, wilson, analyst)),
        beneficiary(company(acme_corp, us))
    ),
    dates(
        initiated(date(2024, 3, 10)),
        due(date(2024, 3, 17))
    ),
    type(wire_transfer)
).
```

## Accessing Nested Fields via Unification

No getters needed — just pattern match:

```prolog
% Get the amount currency and value
transaction_amount(Trans, Currency, Value) :-
    Trans = transaction(_, amount(Currency, Value), _, _, _).

% Get the originator's name
originator_name(Trans, First, Last) :-
    Trans = transaction(_, _, parties(originator(person(First, Last, _)), _), _, _).

% Or more readably, use intermediate variables:
originator_role(Trans, Role) :-
    Trans = transaction(_, _, Parties, _, _),
    Parties = parties(originator(person(_, _, Role)), _).
```

```prolog
?- transaction(T), transaction_amount(T, Cur, Val).
Cur = usd, Val = 250000.

?- transaction(T), originator_name(T, First, Last).
First = dave, Last = wilson.
```

## InferLaw's Transaction Model

```prolog
% Store transactions as facts with structured terms
:- dynamic filing/1.

filing(transaction(
    id(t001),
    amount(usd, 150000),
    parties(from(person(dave, analyst)), to(company(acme))),
    meta(date(2024,1,15), wire_transfer, q1_2024)
)).

filing(transaction(
    id(t002),
    amount(usd, 500000),
    parties(from(person(bob, director)), to(company(globex))),
    meta(date(2024,2,20), purchase, q1_2024)
)).

% Rules that work on structured transactions
high_value(Trans) :-
    Trans = transaction(_, amount(_, Value), _, _),
    Value > 100000.

same_quarter(Trans, Quarter) :-
    Trans = transaction(_, _, _, meta(_, _, Quarter)).

needs_review(Trans) :-
    high_value(Trans),
    Trans = transaction(_, _, parties(from(person(_, Role)), _), _),
    Role \= director.
```

```prolog
?- filing(T), high_value(T), T = transaction(id(ID), _, _, _).
ID = t001 ;
ID = t002.

?- filing(T), needs_review(T), T = transaction(id(ID), _, _, _).
ID = t001.   % Dave is an analyst, not a director
```

## Operator Notation for Readability

You can define operators to make structures more readable:

```prolog
:- op(700, xfx, owes).
:- op(700, xfx, to).

% Now you can write:
?- assert(dave owes 5000 to acme).
?- X owes Amount to acme.
X = dave, Amount = 5000.
```

## copy_term/2 — Template Instantiation

```prolog
% Create a transaction template
transaction_template(
    transaction(id(_), amount(usd, _), parties(from(_), to(_)), meta(_, _, _))
).

% Validate structure matches template
valid_structure(Trans) :-
    transaction_template(Template),
    copy_term(Template, Copy),
    Trans = Copy.
```

## Exercises

1. Model a `regulation(id, name, threshold, effective_date, jurisdiction)` structure.
2. Write `involves_company(Trans, Company)` that checks either party.
3. Write `transaction_age(Trans, Today, Days)` using the date structure.

## What You Learned

- **Compound terms** — `functor(arg1, arg2, ...)` are Prolog's structures
- **Functor/arity** — identifies the "type" of a structure
- **Nested structures** — structures can contain other structures freely
- **Pattern matching** — access fields through unification, no getters needed
- **=.. (univ)** — decompose a term into a list `[functor | args]`
- **Operator notation** — custom syntax for domain readability

The structures model data well. But Jordan brings a new challenge: "We get regulation text as documents. Can Prolog parse 'Section 4(b)(ii): The entity shall not exceed...' into structured rules?" Enter DCGs.

---

[← Chapter 9: I/O](chapter-09-io.md) | [Chapter 11: DCGs →](chapter-11-dcg.md)
