# Chapter 6: Arithmetic — Thresholds and Totals

[← Chapter 5: Lists](chapter-05-lists.md) | [Chapter 7: Backtracking →](chapter-07-backtracking.md)

---

## The Problem

Jordan: "Regulation 47B says if the total value of flagged transactions exceeds $500,000 in a quarter, we must file an enhanced disclosure. Is Q1 over the threshold?"

Legacy Java had a `ThresholdCalculator` with a `BigDecimal` accumulator, null checks on every field, and a 50-line method. You need one rule.

## Arithmetic in Prolog: is/2

Prolog doesn't evaluate arithmetic automatically. `3 + 4` is just a term — a structure with functor `+` and arguments `3` and `4`. To evaluate it, use `is/2`:

```prolog
?- X = 3 + 4.
X = 3+4.        % NOT 7! It's a term.

?- X is 3 + 4.
X = 7.          % is/2 evaluates the right side

?- X is 2 ** 10.
X = 1024.

?- X is sqrt(144).
X = 12.0.
```

**Critical rule:** The right side of `is` must be fully instantiated (no unbound variables).

```prolog
?- X is Y + 1.
% ERROR: Arguments are not sufficiently instantiated
```

## Comparison Operators

```prolog
?- 5 > 3.       true.
?- 5 < 3.       false.
?- 5 >= 5.      true.
?- 5 =< 5.      true.    % Note: =< not <=
?- 5 =:= 2+3.   true.    % Arithmetic equality
?- 5 =\= 6.     true.    % Arithmetic inequality
```

Note: `=<` (not `<=`) and `=:=` (arithmetic equal, not `==` which is structural).

## Summing a List

```prolog
sum_list([], 0).
sum_list([H|T], Sum) :-
    sum_list(T, Rest),
    Sum is H + Rest.

?- sum_list([100, 200, 300], Total).
Total = 600.
```

Or use the built-in `sum_list/2` (SWI-Prolog) / `sumlist/2`:

```prolog
?- sum_list([1000, 2500, 7500], Total).
Total = 11000.
```

## InferLaw's Threshold Check

```prolog
% Transaction facts
transaction(t001, 250000, transfer, q1_2024).
transaction(t002, 180000, purchase, q1_2024).
transaction(t003, 95000, transfer, q1_2024).
transaction(t004, 50000, payment, q2_2024).

flagged(t001).
flagged(t002).
flagged(t003).

% Sum all flagged transaction amounts in a quarter
flagged_total(Quarter, Total) :-
    findall(Amount,
        (transaction(TID, Amount, _, Quarter), flagged(TID)),
        Amounts),
    sum_list(Amounts, Total).

% Check against regulatory threshold
over_threshold(Quarter) :-
    flagged_total(Quarter, Total),
    threshold(enhanced_disclosure, Limit),
    Total > Limit.

threshold(enhanced_disclosure, 500000).
```

```prolog
?- flagged_total(q1_2024, Total).
Total = 525000.

?- over_threshold(q1_2024).
true.

?- over_threshold(q2_2024).
false.
```

Jordan: "525K. We need to file the enhanced disclosure."

## Aggregate Calculations

```prolog
% Average transaction amount
average_amount(Quarter, Avg) :-
    findall(A, transaction(_, A, _, Quarter), Amounts),
    sum_list(Amounts, Total),
    length(Amounts, Count),
    Count > 0,
    Avg is Total / Count.

% Maximum transaction
max_transaction(Quarter, MaxID, MaxAmount) :-
    transaction(MaxID, MaxAmount, _, Quarter),
    \+ (transaction(_, Other, _, Quarter), Other > MaxAmount).
```

```prolog
?- average_amount(q1_2024, Avg).
Avg = 175000.0.

?- max_transaction(q1_2024, ID, Amount).
ID = t001, Amount = 250000.
```

## Percentage and Rounding

```prolog
% What percentage of Q1 transactions are flagged?
flagged_percentage(Quarter, Pct) :-
    findall(T, transaction(T, _, _, Quarter), All),
    findall(T, (transaction(T, _, _, Quarter), flagged(T)), Flagged),
    length(All, Total),
    length(Flagged, FlagCount),
    Total > 0,
    Pct is (FlagCount * 100) / Total.

?- flagged_percentage(q1_2024, Pct).
Pct = 100.    % All 3 Q1 transactions are flagged — yikes
```

## Accumulator Pattern (Tail Recursion)

For large lists, use an accumulator for efficiency:

```prolog
sum_acc(List, Sum) :- sum_acc(List, 0, Sum).
sum_acc([], Acc, Acc).
sum_acc([H|T], Acc, Sum) :-
    NewAcc is Acc + H,
    sum_acc(T, NewAcc, Sum).
```

## Exercises

1. Write `transaction_count(Quarter, Count)` that counts transactions per quarter.
2. Write `amount_between(Low, High, TID)` that finds transactions in a range.
3. Write `total_by_type(Quarter, Type, Total)` that sums amounts grouped by type.

## What You Learned

- **is/2** — evaluates arithmetic expressions (right side must be ground)
- **Comparison** — `>`, `<`, `>=`, `=<`, `=:=`, `=\=`
- **sum_list/2** — built-in for summing a list of numbers
- **Aggregation pattern** — findall to collect, then compute over the list
- **Accumulator** — tail-recursive pattern for efficient computation

The threshold check works for one answer. But what if Jordan asks "Find ALL people who could approve this"? Prolog can do that — through backtracking.

---

[← Chapter 5: Lists](chapter-05-lists.md) | [Chapter 7: Backtracking →](chapter-07-backtracking.md)
