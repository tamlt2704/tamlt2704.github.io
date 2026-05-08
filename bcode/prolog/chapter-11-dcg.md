# Chapter 11: DCGs — Parsing Legal Language

[← Chapter 10: Structures](chapter-10-structures.md) | [Chapter 12: Meta-Programming →](chapter-12-meta.md)

---

## The Problem

Jordan drops a stack of regulation documents: "New regulations just dropped. Section 4(b)(ii) says 'The entity shall not transfer more than $100,000 without board approval.' Can your system parse these into rules automatically?"

Parsing structured language is a classic Prolog strength. **Definite Clause Grammars** (DCGs) let you write parsers that look like the grammar itself.

## DCG Basics

A DCG rule uses `-->` instead of `:-`:

```prolog
greeting --> [hello], name.
name --> [world].
name --> [prolog].
```

```prolog
?- phrase(greeting, [hello, world]).
true.

?- phrase(greeting, [hello, prolog]).
true.

?- phrase(greeting, [hi, world]).
false.
```

`phrase/2` runs a DCG rule against a list of tokens.

## How DCGs Work

DCGs are syntactic sugar over difference lists. The rule:

```prolog
greeting --> [hello], name.
```

Translates to:

```prolog
greeting(S0, S) :- S0 = [hello|S1], name(S1, S).
```

You don't need to manage the list threading — Prolog does it for you.

## Building Parse Trees

DCG rules can have arguments that build structure:

```prolog
sentence(S) --> noun_phrase(NP), verb_phrase(VP), { S = sentence(NP, VP) }.
noun_phrase(np(Det, N)) --> determiner(Det), noun(N).
verb_phrase(vp(V, NP)) --> verb(V), noun_phrase(NP).

determiner(the) --> [the].
determiner(a) --> [a].
noun(entity) --> [entity].
noun(amount) --> [amount].
verb(exceeds) --> [exceeds].
verb(transfers) --> [transfers].
```

```prolog
?- phrase(sentence(Tree), [the, entity, transfers, the, amount]).
Tree = sentence(np(the, entity), vp(transfers, np(the, amount))).
```

## Inline Prolog with { }

Curly braces embed regular Prolog goals inside DCG rules:

```prolog
number(N) --> [X], { number(X), N = X }.
threshold(T) --> [dollar], number(N), { T = usd(N) }.

% With constraints
large_amount(A) --> number(N), { N > 100000, A = N }.
```

## InferLaw's Regulation Parser

```prolog
% Parse: "entity shall not transfer more than 100000 without approval"
regulation(rule(Entity, Action, Limit, Condition)) -->
    entity_ref(Entity),
    modal,
    negation,
    action(Action),
    threshold_phrase(Limit),
    condition(Condition).

entity_ref(entity) --> [entity].
entity_ref(entity) --> [the, entity].

modal --> [shall].
modal --> [must].

negation --> [not].
negation --> [].    % Optional negation

action(transfer) --> [transfer].
action(transfer) --> [transfer, more, than].
action(exceed) --> [exceed].

threshold_phrase(limit(usd, N)) --> [dollar], number_token(N).
threshold_phrase(limit(usd, N)) --> number_token(N), [dollars].

number_token(N) --> [N], { number(N) }.

condition(requires(board_approval)) --> [without, board, approval].
condition(requires(director_approval)) --> [without, approval].
condition(none) --> [].
```

```prolog
?- phrase(regulation(Rule),
    [the, entity, shall, not, transfer, more, than, dollar, 100000,
     without, board, approval]).
Rule = rule(entity, transfer, limit(usd, 100000), requires(board_approval)).
```

## From Parse Tree to Prolog Rule

```prolog
% Convert parsed regulation to an executable compliance check
compile_rule(rule(entity, transfer, limit(Cur, Max), requires(Approval)),
             Rule) :-
    Rule = (violation(TID, exceeds_limit) :-
                transaction(TID, amount(Cur, Amount), _, _),
                Amount > Max,
                \+ has_approval(TID, Approval)).
```

## Tokenizing Input Text

Real text needs tokenization first:

```prolog
tokenize(Text, Tokens) :-
    split_string(Text, " ", " ", Words),
    maplist(atom_string, Tokens, Words).

parse_regulation(Text, Rule) :-
    tokenize(Text, Tokens),
    phrase(regulation(Rule), Tokens).
```

```prolog
?- parse_regulation("the entity shall not transfer more than dollar 100000 without board approval", Rule).
Rule = rule(entity, transfer, limit(usd, 100000), requires(board_approval)).
```

## Recursive Grammars

DCGs handle recursive structures naturally:

```prolog
% Parse section references: "section 4(b)(ii)"
section_ref(section(N, Subs)) --> [section], number_token(N), subsections(Subs).

subsections([Sub|Rest]) --> ['('], subsection_id(Sub), [')'], subsections(Rest).
subsections([]) --> [].

subsection_id(N) --> [N], { atom(N) }.
```

```prolog
?- phrase(section_ref(Ref), [section, 4, '(', b, ')', '(', ii, ')']).
Ref = section(4, [b, ii]).
```

## Exercises

1. Extend the parser to handle "or" conditions: "without board or committee approval."
2. Write a DCG that parses dates: "March 15, 2024" → `date(2024, 3, 15)`.
3. Parse "if amount exceeds 50000 then require director approval" into a rule structure.

## What You Learned

- **DCG notation** — `-->` rules for grammar definitions
- **phrase/2** — run a DCG against a token list
- **Terminal matching** — `[token]` matches a specific token
- **Building structure** — DCG arguments construct parse trees
- **{ Goals }** — embed Prolog conditions inside DCG rules
- **Recursive grammars** — DCGs naturally handle nested structures

Parsing regulations into rules is powerful. But what if we want rules that *generate* other rules at runtime? That's meta-programming — Prolog's secret weapon.

---

[← Chapter 10: Structures](chapter-10-structures.md) | [Chapter 12: Meta-Programming →](chapter-12-meta.md)
