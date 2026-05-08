# Chapter 4: Recursion — Climbing the Org Chart

[← Chapter 3: Unification](chapter-03-unification.md) | [Chapter 5: Lists →](chapter-05-lists.md)

---

## The Problem

Jordan pulls up the org chart: "Is Alice above Bob? Not directly — Alice manages Carol, who manages Dave, who manages Bob. We need to check the whole chain."

In Legacy Java, someone wrote this:

```java
boolean isAbove(String a, String b) {
    Set<String> visited = new HashSet<>();
    Queue<String> queue = new LinkedList<>();
    queue.add(a);
    while (!queue.isEmpty()) {
        String current = queue.poll();
        if (visited.contains(current)) continue;
        visited.add(current);
        for (String report : getDirectReports(current)) {
            if (report.equals(b)) return true;
            queue.add(report);
        }
    }
    return false;
}
```

BFS, visited sets, queues. For a question that's really just: "Is there a chain of manages-relationships from A to B?"

## The Prolog Way: Recursive Rules

```prolog
% Facts: direct management relationships
manages(alice, carol).
manages(carol, dave).
manages(dave, bob).
manages(alice, eve).

% Base case: X is above Y if X directly manages Y
above(X, Y) :- manages(X, Y).

% Recursive case: X is above Y if X manages someone who is above Y
above(X, Y) :- manages(X, Z), above(Z, Y).
```

```prolog
?- above(alice, bob).
true.

?- above(alice, Who).
Who = carol ;
Who = dave ;
Who = bob ;
Who = eve ;
false.

?- above(Who, bob).
Who = dave ;
Who = carol ;
Who = alice ;
false.
```

Three lines of Prolog replace 15 lines of Java. No queues, no visited sets — Prolog's search handles the traversal.

## How Recursion Works

When Prolog evaluates `above(alice, bob)`:

1. Try rule 1: `above(alice, bob) :- manages(alice, bob)` → `manages(alice, bob)` is not a fact. FAIL.
2. Try rule 2: `above(alice, bob) :- manages(alice, Z), above(Z, bob)`.
   - `manages(alice, Z)` → `Z = carol` ✓
   - Now prove `above(carol, bob)`:
     - Try rule 1: `manages(carol, bob)` → not a fact. FAIL.
     - Try rule 2: `manages(carol, Z2), above(Z2, bob)`
       - `Z2 = dave` ✓
       - Prove `above(dave, bob)`:
         - Try rule 1: `manages(dave, bob)` → ✓ **SUCCESS!**

## Base Case First

Always put the base case before the recursive case:

```prolog
% GOOD: base case first
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

% BAD: recursive case first (may loop on failure)
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
ancestor(X, Y) :- parent(X, Y).
```

## Counting Levels

Dr. Vasquez asks: "How many levels apart are they?"

```prolog
% levels_above(X, Y, N) — X is N levels above Y
levels_above(X, Y, 1) :- manages(X, Y).
levels_above(X, Y, N) :-
    manages(X, Z),
    levels_above(Z, Y, N1),
    N is N1 + 1.
```

```prolog
?- levels_above(alice, bob, N).
N = 3.

?- levels_above(alice, carol, N).
N = 1.
```

## Avoiding Infinite Loops

If the org chart had a cycle (`manages(bob, alice)`), recursion would loop forever. Guard against it:

```prolog
above_safe(X, Y) :- above_safe(X, Y, [X]).

above_safe(X, Y, _Visited) :- manages(X, Y).
above_safe(X, Y, Visited) :-
    manages(X, Z),
    \+ member(Z, Visited),
    above_safe(Z, Y, [Z|Visited]).
```

## InferLaw's Approval Chain

Jordan's real rule: "A transaction needs approval from someone at least 2 levels above the originator."

```prolog
needs_higher_approval(TransID) :-
    transaction(TransID, _Amount, _Type, Originator),
    \+ (levels_above(Approver, Originator, N),
        N >= 2,
        can_approve(Approver, TransID)).
```

```prolog
?- needs_higher_approval(t001).
false.   % Someone 2+ levels up CAN approve — we're fine

?- needs_higher_approval(t099).
true.    % No one high enough can approve — flag it
```

## Exercises

1. Add `manages(eve, frank)` and query `above(alice, frank)`.
2. Write `same_team(X, Y)` — true if X and Y share a common manager.
3. Write `chain(X, Y, Path)` that returns the list of people between X and Y.

## What You Learned

- **Recursive rules** — a predicate that calls itself with a smaller problem
- **Base case** — the non-recursive clause that stops recursion
- **Rule ordering** — base case first prevents unnecessary looping
- **Accumulator pattern** — carrying state (like visited lists) through recursion
- Prolog's search naturally traverses hierarchies without explicit graph algorithms

Jordan's next question: "Don't just tell me IF there are violations — give me the LIST." That means we need Prolog's list data structure.

---

[← Chapter 3: Unification](chapter-03-unification.md) | [Chapter 5: Lists →](chapter-05-lists.md)
