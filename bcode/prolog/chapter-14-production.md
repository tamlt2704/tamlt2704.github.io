# Chapter 14: Production — Shipping the Compliance Engine

[← Chapter 13: CLP(FD)](chapter-13-clp.md) | [Course Overview](chapter-00-overview.md)

---

## The Problem

Dr. Vasquez: "The prototype works. Now ship it. I need modules so the team can work in parallel, tests so we don't break things, and integration with our Java API and Python data pipeline. This isn't a toy anymore."

## Modules

SWI-Prolog modules prevent name collisions and define public interfaces:

```prolog
% File: compliance_engine.pl
:- module(compliance_engine, [
    check_transaction/2,    % check_transaction(+TransID, -Violations)
    can_approve/2,          % can_approve(+Person, +TransID)
    flagged_total/2         % flagged_total(+Quarter, -Total)
]).

:- use_module(library(lists)).
:- use_module(transaction_store).
:- use_module(regulation_rules).

check_transaction(TransID, Violations) :-
    findall(V, is_violation(TransID, V), Violations).

can_approve(Person, TransID) :-
    director(Person),
    transaction(TransID, Amount, _, Originator),
    approval_limit(Person, Limit),
    Amount =< Limit,
    Person \= Originator,
    \+ conflict_of_interest(Person, TransID).
```

```prolog
% File: transaction_store.pl
:- module(transaction_store, [
    transaction/4,
    add_transaction/4,
    filed_in/2
]).

:- dynamic transaction/4.

add_transaction(ID, Amount, Type, Quarter) :-
    assert(transaction(ID, Amount, Type, Quarter)),
    assert(filed_in(ID, Quarter)).
```

## Unit Testing with PlUnit

```prolog
% File: test_compliance.pl
:- use_module(compliance_engine).
:- use_module(library(plunit)).

:- begin_tests(approval).

test(director_can_approve_under_limit) :-
    can_approve(alice, t_small).

test(analyst_cannot_approve, [fail]) :-
    can_approve(dave, t_small).

test(over_limit_rejected, [fail]) :-
    can_approve(bob, t_huge).

test(self_approval_rejected, [fail]) :-
    can_approve(dave, t_dave_originated).

test(finds_all_violations) :-
    check_transaction(t_bad, Violations),
    length(Violations, N),
    N > 0.

:- end_tests(approval).

:- begin_tests(threshold).

test(q1_over_threshold) :-
    flagged_total(q1_2024, Total),
    Total > 500000.

test(q2_under_threshold) :-
    flagged_total(q2_2024, Total),
    Total =< 500000.

:- end_tests(threshold).
```

Run tests:
```bash
$ swipl -g run_tests -t halt test_compliance.pl
% PL-Unit: approval ..... done
% PL-Unit: threshold .. done
% All 7 tests passed
```

## Integration with Java (JPL)

SWI-Prolog's JPL library provides bidirectional Java-Prolog communication:

```java
// Java side: query the Prolog engine
import org.jpl7.*;

public class ComplianceService {
    
    static {
        // Load the Prolog knowledge base
        Query.hasSolution("consult('compliance_engine.pl')");
    }
    
    public List<String> getViolations(String transactionId) {
        String query = String.format(
            "check_transaction(%s, Violations)", transactionId);
        Query q = new Query(query);
        
        if (q.hasSolution()) {
            Term violations = q.oneSolution().get("Violations");
            return termToList(violations);
        }
        return Collections.emptyList();
    }
    
    public boolean canApprove(String person, String transId) {
        String query = String.format(
            "can_approve(%s, %s)", person, transId);
        return Query.hasSolution(query);
    }
}
```

## Integration with Python (pyswip)

```python
# Python side: query Prolog from the data pipeline
from pyswip import Prolog

prolog = Prolog()
prolog.consult("compliance_engine.pl")

# Check a transaction
violations = list(prolog.query(
    f"check_transaction(t001, Violations)"
))
print(violations)
# [{'Violations': ['over_limit', 'conflict']}]

# Find all approvers
approvers = list(prolog.query(
    "can_approve(Person, t001)"
))
for result in approvers:
    print(f"  {result['Person']} can approve")

# Batch processing
def check_quarter(quarter):
    results = list(prolog.query(
        f"filed_in(TID, {quarter}), check_transaction(TID, Vs), Vs \\= []"
    ))
    return [(r['TID'], r['Vs']) for r in results]
```

## REST API Wrapper

```prolog
% File: compliance_api.pl — HTTP endpoint using SWI-Prolog's HTTP library
:- use_module(library(http/thread_httpd)).
:- use_module(library(http/http_dispatch)).
:- use_module(library(http/http_json)).
:- use_module(compliance_engine).

:- http_handler('/api/check', handle_check, []).
:- http_handler('/api/approve', handle_approve, []).

server(Port) :- http_server(http_dispatch, [port(Port)]).

handle_check(Request) :-
    http_parameters(Request, [transaction(TID, [atom])]),
    check_transaction(TID, Violations),
    reply_json_dict(_{transaction: TID, violations: Violations}).

handle_approve(Request) :-
    http_parameters(Request, [
        person(Person, [atom]),
        transaction(TID, [atom])
    ]),
    (can_approve(Person, TID)
    ->  reply_json_dict(_{approved: true, person: Person})
    ;   reply_json_dict(_{approved: false, reason: "Not authorized"})
    ).
```

```bash
$ swipl -g "server(8080)" compliance_api.pl
% Started server on port 8080

$ curl localhost:8080/api/check?transaction=t001
{"transaction": "t001", "violations": ["over_limit"]}

$ curl "localhost:8080/api/approve?person=alice&transaction=t001"
{"approved": true, "person": "alice"}
```

## Project Structure

```
inferlaw/
├── src/
│   ├── compliance_engine.pl    % Main module
│   ├── transaction_store.pl    % Data layer
│   ├── regulation_rules.pl     % Business rules
│   ├── report_generator.pl     % I/O and formatting
│   ├── hearing_scheduler.pl    % CLP(FD) scheduler
│   └── regulation_parser.pl    % DCG parser
├── test/
│   ├── test_compliance.pl
│   ├── test_scheduler.pl
│   └── test_parser.pl
├── api/
│   └── compliance_api.pl       % HTTP interface
├── data/
│   ├── regulations_q1.pl       % Quarterly rule updates
│   └── seed_data.pl            % Test fixtures
├── Makefile
└── README.md
```

```makefile
# Makefile
.PHONY: test run clean

test:
	swipl -g run_tests -t halt test/test_compliance.pl
	swipl -g run_tests -t halt test/test_scheduler.pl

run:
	swipl -g "server(8080)" api/compliance_api.pl

load:
	swipl -l src/compliance_engine.pl
```

## Performance Tips

```prolog
% Index on first argument (automatic in SWI-Prolog)
% Put the most selective argument first:
transaction(t001, ...).  % Good: ID is first, unique lookups are O(1)

% Use tabling (memoization) for expensive recursive queries
:- table above/2.
above(X, Y) :- manages(X, Y).
above(X, Y) :- manages(X, Z), above(Z, Y).

% Compile-time optimizations
:- set_prolog_flag(optimise, true).
```

## What You Learned

- **Modules** — `:- module(Name, [Exports])` for encapsulation
- **PlUnit** — `begin_tests/end_tests` for unit testing
- **JPL** — bidirectional Java↔Prolog integration
- **pyswip** — Python↔Prolog bridge
- **HTTP server** — SWI-Prolog's built-in web server for REST APIs
- **Project structure** — organize a real Prolog application
- **Tabling** — memoization for recursive predicates
- **First-argument indexing** — Prolog's automatic optimization

## The Journey Complete

You started with 15,000 lines of Java if-else statements. You now have:

- **~200 lines of Prolog rules** that express the same compliance logic
- A system that can **explain its decisions** (meta-interpreter proof trees)
- **Dynamic rules** that update without redeployment
- A **constraint solver** for scheduling
- A **parser** that reads regulation documents
- **Tests, modules, and API integration** for production use

Dr. Vasquez smiles. Jordan can update rules without a developer. The Auditor gets proof trees. And Legacy Java? Retired.

Welcome to logic programming.

---

[← Chapter 13: CLP(FD)](chapter-13-clp.md) | [Course Overview](chapter-00-overview.md)
