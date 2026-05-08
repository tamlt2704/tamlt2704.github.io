# Chapter 2: Rules

[← Chapter 1: Facts and Queries](chapter-01-facts.md) | [Chapter 3: Unification →](chapter-03-unification.md)

---

## The Problem

Jordan asks: "Can Alice approve transaction t002?"

You check the compliance manual:
> "A person can approve a transaction if they are a director AND the transaction amount is within their approval limit AND they are not the transaction's originator."

In Java, this becomes another if-else chain:

```java
boolean canApprove(String person, String transactionId) {
    if (!isDirector(person)) return false;
    Transaction t = getTransaction(transactionId);
    if (t.amount > getApprovalLimit(person)) return false;
    if (t.originator.equals(person)) return false;
    return true;
}
```

Every new rule means more code, more tests, more deployment. Jordan can't read Java. She can't verify the rules are correct.

Dr. Vasquez: "Write it as a Prolog rule. Jordan should be able to read it and say 'yes, that's correct.'"

## Rules: If-Then Declarations

A Prolog **rule** says "X is true IF Y and Z are true":

```prolog
% can_approve(Person, Transaction) is true if:
%   - Person is a director
%   - Person is not the originator of Transaction
can_approve(Person, Transaction) :-
    director(Person),
    originator(Transaction, Originator),
    Person \= Originator.
```

Read `:-` as "if" (right to left): "Person can approve Transaction IF Person is a director AND the originator of Transaction is someone different from Person."

### Anatomy of a Rule

```prolog
can_approve(Person, Transaction) :- director(Person), Person \= Originator.
│                                │   │                                      │
│         HEAD                   │   │              BODY                    │
│  (what we're defining)         │   │  (conditions that must be true)     │
│                                │   │                                      │
└── "this is true"               │   └── "if all of these are true"        │
                                 │
                              "if"
```

- **Head**: what the rule defines
- **`:-`**: "if"
- **Body**: comma-separated conditions (all must be true)
- **`.`**: end of rule

## Building the Knowledge Base

```prolog
% company.pl — Extended with rules

% Facts: roles
director(alice).
director(bob).
director(carol).
analyst(dave).
analyst(eve).

% Facts: approval limits
approval_limit(alice, 100000).
approval_limit(bob, 50000).
approval_limit(carol, 200000).

% Facts: transactions
transaction(t001, 50000, transfer, dave).    % (ID, Amount, Type, Originator)
transaction(t002, 120000, purchase, bob).
transaction(t003, 8000, transfer, eve).
transaction(t004, 250000, purchase, dave).

% Helper: get transaction amount
amount(TransID, Amount) :-
    transaction(TransID, Amount, _, _).

% Helper: get transaction originator
originator(TransID, Person) :-
    transaction(TransID, _, _, Person).

% RULE: Can a person approve a transaction?
can_approve(Person, TransID) :-
    director(Person),                          % Must be a director
    transaction(TransID, Amount, _, Originator), % Get transaction details
    approval_limit(Person, Limit),             % Get their limit
    Amount =< Limit,                           % Amount within limit
    Person \= Originator.                      % Can't approve own transaction
```

## Querying Rules

```prolog
?- [company].
true.

% "Can Alice approve t001?"
?- can_approve(alice, t001).
true.
% Alice is a director, t001 is $50K (under her $100K limit), originated by Dave (not Alice). ✓

% "Can Alice approve t002?"
?- can_approve(alice, t002).
false.
% t002 is $120K — over Alice's $100K limit. ✗

% "Can Carol approve t002?"
?- can_approve(carol, t002).
true.
% Carol is a director, t002 is $120K (under her $200K limit), originated by Bob. ✓

% "Can Bob approve t002?"
?- can_approve(bob, t002).
false.
% Bob is the originator of t002 — can't approve your own transaction. ✗

% "WHO can approve t002?"
?- can_approve(Who, t002).
Who = carol ;
false.
% Only Carol can approve t002.
```

Jordan reads the rule and confirms: "Yes, that's exactly what the compliance manual says." No Java knowledge required.

## Multiple Rules: Same Head, Different Conditions

What if analysts can also approve small transactions (under $5,000)?

```prolog
% Directors: full approval power (up to their limit)
can_approve(Person, TransID) :-
    director(Person),
    transaction(TransID, Amount, _, Originator),
    approval_limit(Person, Limit),
    Amount =< Limit,
    Person \= Originator.

% Analysts: can approve transactions under $5000
can_approve(Person, TransID) :-
    analyst(Person),
    transaction(TransID, Amount, _, Originator),
    Amount =< 5000,
    Person \= Originator.
```

Two rules with the same head (`can_approve`). Prolog tries both — if either succeeds, the query succeeds. This is like an OR:

"Person can approve TransID IF (they're a director with sufficient limit) OR (they're an analyst and amount ≤ $5000)."

```prolog
% "Who can approve t003?" ($8000, originated by Eve)
?- can_approve(Who, t003).
Who = alice ;    % Director, $8K < $100K limit
Who = bob ;      % Director, $8K < $50K limit
Who = carol ;    % Director, $8K < $200K limit
false.
% Analysts can't — $8K > $5K threshold

% Add a $3000 transaction
?- assert(transaction(t005, 3000, transfer, alice)).

% "Who can approve t005?"
?- can_approve(Who, t005).
Who = bob ;      % Director, not originator
Who = carol ;    % Director, not originator
Who = dave ;     % Analyst, $3K < $5K, not originator
Who = eve ;      % Analyst, $3K < $5K, not originator
false.
% Alice can't — she's the originator
```

## Rules Calling Rules

Rules can use other rules in their body:

```prolog
% A person is authorized if they can approve AND are in the right department
authorized(Person, TransID) :-
    can_approve(Person, TransID),
    transaction(TransID, _, Type, _),
    handles_type(Person, Type).

% Which departments handle which transaction types
handles_type(Person, transfer) :- department(Person, finance).
handles_type(Person, purchase) :- department(Person, legal).
handles_type(Person, purchase) :- department(Person, compliance).
```

Now `authorized` checks approval power AND departmental responsibility. Rules compose naturally.

## Jordan's Verification

Jordan reads the rules and provides feedback:

"The approval rule is correct, but you're missing one thing: transactions over $500,000 need TWO directors to approve. Can Prolog handle that?"

```prolog
% Dual approval for large transactions
needs_dual_approval(TransID) :-
    transaction(TransID, Amount, _, _),
    Amount > 500000.

% Two different directors must both approve
dual_approved(TransID) :-
    needs_dual_approval(TransID),
    can_approve(Approver1, TransID),
    can_approve(Approver2, TransID),
    Approver1 \= Approver2.
```

```prolog
?- dual_approved(t004).  % $250K — doesn't need dual approval
false.

% Add a $600K transaction
?- assert(transaction(t006, 600000, transfer, dave)).
?- assert(approval_limit(carol, 700000)).  % Update Carol's limit

?- dual_approved(t006).
% Depends on who has sufficient limits...
```

## What You Learned

- **Rules** — `head :- body.` means "head is true if body is true"
- **`:-`** — read as "if"
- **`,`** — read as "and" (all conditions must hold)
- **Multiple rules** — same head = OR (either rule can satisfy)
- **Rules calling rules** — natural composition
- **`\=`** — "not equal" (not unifiable)
- **Jordan can read it** — rules are close to natural language

The compliance engine handles simple authorization. But Jordan's next question is harder: "Who can approve transactions over $10K?" — she doesn't know the specific transaction, she wants a general answer. That requires **unification** — Prolog's pattern matching engine.

---

[← Chapter 1: Facts and Queries](chapter-01-facts.md) | [Chapter 3: Unification →](chapter-03-unification.md)
