# Chapter 13: CLP(FD) — Scheduling Under Constraints

[← Chapter 12: Meta-Programming](chapter-12-meta.md) | [Chapter 14: Production →](chapter-14-production.md)

---

## The Problem

Jordan is panicking: "We have 12 compliance hearings to schedule this week. 4 rooms, 6 judges, and about 50 constraints — Judge Martinez can't do Mondays, Room B is unavailable Tuesday afternoon, no judge can do back-to-back hearings, and parties in related cases can't overlap. The spreadsheet isn't working."

In Java, this would be a brute-force search with exponential complexity, or you'd pull in a heavyweight solver library. In Prolog, there's CLP(FD) — Constraint Logic Programming over Finite Domains.

## Loading CLP(FD)

```prolog
:- use_module(library(clpfd)).
```

## Basic Constraints

CLP(FD) lets you state constraints on integer variables, and Prolog finds values that satisfy ALL of them:

```prolog
?- use_module(library(clpfd)).
?- X in 1..10, X > 5.
X in 6..10.

?- X in 1..5, Y in 1..5, X + Y #= 7.
X in 2..5, Y in 2..5, X+Y#=7.

?- X in 1..5, Y in 1..5, X + Y #= 7, label([X, Y]).
X = 2, Y = 5 ;
X = 3, Y = 4 ;
X = 4, Y = 3 ;
X = 5, Y = 2.
```

## CLP(FD) Operators

| Operator | Meaning |
|----------|---------|
| `#=` | Equal |
| `#\=` | Not equal |
| `#<` | Less than |
| `#>` | Greater than |
| `#=<` | Less or equal |
| `#>=` | Greater or equal |
| `in` | Domain membership |

## The Power: Constraint Propagation

CLP(FD) doesn't just brute-force. It **propagates** constraints to prune impossible values before searching:

```prolog
?- [X, Y, Z] ins 1..3, all_different([X, Y, Z]), X #= 1.
X = 1, Y in 2..3, Z in 2..3.
% Prolog immediately knows Y and Z can't be 1
```

## InferLaw's Hearing Scheduler

```prolog
:- use_module(library(clpfd)).

% Encode: Day (1-5 = Mon-Fri), Slot (1-4 = morning/afternoon slots)
% Each hearing gets a Day, Slot, Room, and Judge

schedule_hearings(Schedule) :-
    length(Schedule, 12),  % 12 hearings
    maplist(hearing_vars, Schedule),
    apply_constraints(Schedule),
    label_schedule(Schedule).

hearing_vars(hearing(Day, Slot, Room, Judge)) :-
    Day in 1..5,
    Slot in 1..4,
    Room in 1..4,
    Judge in 1..6.

% No two hearings in the same room at the same time
apply_constraints(Schedule) :-
    no_room_conflicts(Schedule),
    no_judge_conflicts(Schedule),
    judge_availability(Schedule),
    related_case_constraints(Schedule).

no_room_conflicts([]).
no_room_conflicts([H|Rest]) :-
    maplist(no_room_conflict(H), Rest),
    no_room_conflicts(Rest).

no_room_conflict(hearing(D1, S1, R1, _), hearing(D2, S2, R2, _)) :-
    (D1 #= D2 #/\ S1 #= S2) #==> R1 #\= R2.

% No judge does two hearings in the same slot
no_judge_conflicts([]).
no_judge_conflicts([H|Rest]) :-
    maplist(no_judge_conflict(H), Rest),
    no_judge_conflicts(Rest).

no_judge_conflict(hearing(D1, S1, _, J1), hearing(D2, S2, _, J2)) :-
    (D1 #= D2 #/\ S1 #= S2) #==> J1 #\= J2.

% Judge 3 (Martinez) unavailable Monday
judge_availability(Schedule) :-
    maplist(martinez_not_monday, Schedule).

martinez_not_monday(hearing(Day, _, _, Judge)) :-
    (Judge #= 3) #==> (Day #\= 1).

% No back-to-back for same judge
no_back_to_back(hearing(D1, S1, _, J1), hearing(D2, S2, _, J2)) :-
    (J1 #= J2 #/\ D1 #= D2) #==> abs(S1 - S2) #> 1.

label_schedule(Schedule) :-
    maplist(label_hearing, Schedule).

label_hearing(hearing(Day, Slot, Room, Judge)) :-
    label([Day, Slot, Room, Judge]).
```

```prolog
?- schedule_hearings(Schedule).
Schedule = [hearing(1,1,1,1), hearing(1,1,2,2), hearing(1,2,1,3), ...].
```

## A Simpler Example: Room Assignment

```prolog
assign_rooms(Rooms) :-
    Rooms = [R1, R2, R3, R4],
    Rooms ins 1..4,
    all_different(Rooms),
    R1 #\= 2,          % Hearing 1 can't use Room 2
    R3 #\= R4,         % Hearings 3 and 4 need different rooms
    label(Rooms).

?- assign_rooms(Rooms).
Rooms = [1, 2, 3, 4] ;
Rooms = [1, 3, 2, 4] ;
...
```

## Optimization: Minimize Gaps

```prolog
% Find schedule that minimizes total days used
optimal_schedule(Schedule, Cost) :-
    length(Schedule, 12),
    maplist(hearing_vars, Schedule),
    apply_constraints(Schedule),
    maplist(hearing_day, Schedule, Days),
    max_list_clp(Days, MaxDay),
    Cost #= MaxDay,
    labeling([min(Cost)], [Cost|AllVars]).

hearing_day(hearing(Day, _, _, _), Day).
```

## Exercises

1. Add a constraint: "Hearing 5 must happen before Hearing 8" (same or earlier day).
2. Write a simpler puzzle: place 4 non-attacking rooks on a 4×4 board using CLP(FD).
3. Add room capacity constraints: Room 1 holds 20 people, some hearings need 30+.

## What You Learned

- **CLP(FD)** — Constraint Logic Programming over Finite Domains
- **`in` and `ins`** — declare variable domains
- **Constraint operators** — `#=`, `#\=`, `#<`, `#>`, `#==>` (reification)
- **all_different/1** — all variables must have distinct values
- **label/1** — search for concrete values satisfying all constraints
- **Constraint propagation** — prunes impossible values before searching
- **labeling options** — `min(X)`, `max(X)` for optimization

The scheduler works. The compliance engine is feature-complete. Now Dr. Vasquez asks the big question: "How do we ship this? Modules, tests, and integration with our Java/Python stack."

---

[← Chapter 12: Meta-Programming](chapter-12-meta.md) | [Chapter 14: Production →](chapter-14-production.md)
