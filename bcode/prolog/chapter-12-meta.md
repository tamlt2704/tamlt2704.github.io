# Chapter 12: Meta-Programming — Rules That Write Rules

[← Chapter 11: DCGs](chapter-11-dcg.md) | [Chapter 13: CLP(FD) →](chapter-13-clp.md)

---

## The Problem

Dr. Vasquez: "Regulations change quarterly. We can't redeploy every time a threshold changes or a new rule is added. I need rules that can be added, modified, and removed at runtime — rules that generate rules."

Legacy Java had a `RuleEngine` with XML configuration, a custom DSL parser, and a 2000-line interpreter. Prolog IS a rule engine.

## Dynamic Predicates: assert and retract

```prolog
:- dynamic threshold/2.
:- dynamic director/1.

% Add facts at runtime
?- assert(threshold(wire_transfer, 50000)).
true.

?- assert(director(frank)).
true.

% Query them normally
?- threshold(wire_transfer, Limit).
Limit = 50000.

% Remove facts
?- retract(threshold(wire_transfer, 50000)).
true.

?- threshold(wire_transfer, _).
false.
```

### assertz vs asserta

```prolog
?- assertz(color(red)).    % Add at the END
?- assertz(color(blue)).
?- asserta(color(green)).  % Add at the BEGINNING

?- findall(C, color(C), Colors).
Colors = [green, red, blue].
```

## Adding Rules Dynamically

```prolog
% Assert an entire rule (not just a fact)
?- assert((can_approve(frank, T) :- transaction(T, Amount, _, _), Amount =< 75000)).
true.

?- can_approve(frank, t_small).  % Works if t_small amount =< 75000
true.
```

## call/N — Higher-Order Predicates

`call` invokes a goal stored as a term:

```prolog
?- Goal = member(X, [a, b, c]), call(Goal).
X = a ; X = b ; X = c.

% call/N adds arguments:
?- call(succ, 3, X).    % Calls succ(3, X)
X = 4.

% Useful for passing predicates as arguments:
apply_check(Check, TransID) :-
    call(Check, TransID).

?- apply_check(high_value, t001).
true.
```

## InferLaw's Dynamic Rule Engine

```prolog
:- dynamic compliance_rule/3.  % rule(ID, Description, Goal)

% Load rules from configuration
load_regulation(RegID, Desc, Condition) :-
    assert(compliance_rule(RegID, Desc, Condition)).

% Check all active rules against a transaction
check_compliance(TransID, Violations) :-
    findall(
        violation(RegID, Desc),
        (compliance_rule(RegID, Desc, Check),
         call(Check, TransID)),
        Violations
    ).

% Add rules at runtime
?- load_regulation(reg_47b,
       'Transfer exceeds threshold',
       exceeds_threshold).
?- load_regulation(reg_12a,
       'Self-approval detected',
       self_approved).

% Define what the checks do
exceeds_threshold(TransID) :-
    transaction(TransID, Amount, _, _),
    threshold(enhanced_disclosure, Limit),
    Amount > Limit.

self_approved(TransID) :-
    transaction(TransID, _, _, Originator),
    approved_by(TransID, Originator).
```

```prolog
?- check_compliance(t001, Violations).
Violations = [violation(reg_47b, 'Transfer exceeds threshold')].
```

## Meta-Interpreters

A meta-interpreter is a Prolog program that interprets Prolog itself. The simplest:

```prolog
% Vanilla meta-interpreter
solve(true).
solve((A, B)) :- solve(A), solve(B).
solve(Goal) :- clause(Goal, Body), solve(Body).
```

### Adding Explanation (Proof Trees)

```prolog
% Meta-interpreter that builds an explanation
solve(true, true).
solve((A, B), (ProofA, ProofB)) :-
    solve(A, ProofA),
    solve(B, ProofB).
solve(Goal, Goal :- Proof) :-
    clause(Goal, Body),
    solve(Body, Proof).
```

```prolog
?- solve(can_approve(alice, t001), Proof).
Proof = can_approve(alice, t001) :-
    (director(alice) :- true,
     transaction(t001, 50000, transfer, dave) :- true,
     approval_limit(alice, 100000) :- true,
     ...).
```

This gives the Auditor a complete proof trail of WHY a decision was made.

## Updating Rules Without Restart

```prolog
% Quarterly regulation update
update_threshold(RegType, NewLimit) :-
    retractall(threshold(RegType, _)),
    assert(threshold(RegType, NewLimit)),
    format("Updated ~w threshold to $~d~n", [RegType, NewLimit]).

% Deactivate a rule
deactivate_rule(RegID) :-
    retract(compliance_rule(RegID, _, _)),
    format("Rule ~w deactivated~n", [RegID]).

% Reload all rules from a file
reload_rules(File) :-
    retractall(compliance_rule(_, _, _)),
    consult(File),
    findall(ID, compliance_rule(ID, _, _), IDs),
    length(IDs, N),
    format("Loaded ~d rules from ~w~n", [N, File]).
```

## maplist and Higher-Order Patterns

```prolog
% Apply a check to every transaction
?- findall(T, transaction(T, _, _, _), Ts),
   maplist(check_single, Ts).

check_single(TransID) :-
    check_compliance(TransID, Vs),
    (Vs = [] -> true ; format("~w has violations: ~w~n", [TransID, Vs])).

% Transform a list
?- maplist([X, Y]>>(Y is X * 2), [1,2,3], Doubled).
Doubled = [2, 4, 6].
```

## Exercises

1. Write `add_director(Name, Limit)` that asserts both `director/1` and `approval_limit/2`.
2. Extend the meta-interpreter to track depth and reject proofs deeper than N.
3. Write `rule_count/1` that returns how many compliance rules are currently active.

## What You Learned

- **assert/retract** — add and remove facts/rules at runtime
- **:- dynamic** — declare predicates that can be modified
- **call/N** — invoke goals stored as terms (higher-order programming)
- **Meta-interpreters** — Prolog programs that interpret Prolog
- **Proof trees** — meta-interpreters can explain WHY a conclusion holds
- **maplist/2-4** — apply a goal to every element of a list

Dynamic rules handle changing regulations. But Jordan has a scheduling nightmare: "We have 12 hearings, 4 rooms, 6 judges, and 50 constraints. Find a valid schedule." That's constraint logic programming.

---

[← Chapter 11: DCGs](chapter-11-dcg.md) | [Chapter 13: CLP(FD) →](chapter-13-clp.md)
