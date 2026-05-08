# Chapter 9: I/O — Generating Reports

[← Chapter 8: Negation](chapter-08-negation.md) | [Chapter 10: Structures →](chapter-10-structures.md)

---

## The Problem

Jordan: "The board meeting is Thursday. I need a formatted compliance report — violations, totals, risk levels — written to a file I can email. Can your Prolog thing do that?"

Legacy Java had a `ReportGenerator` class with StringBuilder, template engines, and 300 lines of formatting code. Prolog's I/O is simpler.

## Basic Output: write and format

```prolog
?- write('Hello, World!'), nl.
Hello, World!
true.

?- writeln('Line with automatic newline').
Line with automatic newline
true.

% format/2 — printf-style formatting
?- format("Name: ~w, Amount: $~d~n", [alice, 50000]).
Name: alice, Amount: $50000
true.
```

### Format Codes

| Code | Meaning | Example |
|------|---------|---------|
| `~w` | Write (any term) | `~w` → `alice` |
| `~d` | Decimal integer | `~d` → `42` |
| `~f` | Float | `~f` → `3.140000` |
| `~a` | Atom | `~a` → `hello` |
| `~n` | Newline | |
| `~t~30|` | Tab to column 30 | |

## Reading Input

```prolog
?- write('Enter name: '), read(X).
Enter name: alice.
X = alice.

% read/1 expects a Prolog term ending with a period
% read_term/2 gives more control
?- read_term(X, []).
hello.
X = hello.
```

## File I/O

### Writing to a File

```prolog
write_report(Filename) :-
    open(Filename, write, Stream),
    format(Stream, "=== Compliance Report ===~n", []),
    format(Stream, "Generated: ~w~n~n", [today]),
    close(Stream).
```

### The Cleaner Way: setup_call_cleanup

```prolog
write_report(Filename) :-
    setup_call_cleanup(
        open(Filename, write, Stream),
        write_report_content(Stream),
        close(Stream)
    ).

write_report_content(Stream) :-
    format(Stream, "=== Compliance Report ===~n~n", []),
    write_violations(Stream),
    write_summary(Stream).
```

### Reading from a File

```prolog
read_transactions(Filename, Transactions) :-
    setup_call_cleanup(
        open(Filename, read, Stream),
        read_all_terms(Stream, Transactions),
        close(Stream)
    ).

read_all_terms(Stream, []) :-
    at_end_of_stream(Stream), !.
read_all_terms(Stream, [Term|Rest]) :-
    read(Stream, Term),
    read_all_terms(Stream, Rest).
```

## InferLaw's Compliance Report

```prolog
generate_report(Quarter, Filename) :-
    setup_call_cleanup(
        open(Filename, write, Stream),
        write_full_report(Stream, Quarter),
        close(Stream)
    ).

write_full_report(Stream, Quarter) :-
    format(Stream, "╔══════════════════════════════════╗~n", []),
    format(Stream, "║   INFERLAW COMPLIANCE REPORT     ║~n", []),
    format(Stream, "╚══════════════════════════════════╝~n~n", []),
    format(Stream, "Quarter: ~w~n", [Quarter]),
    format(Stream, "─────────────────────────────────────~n~n", []),
    write_violation_section(Stream, Quarter),
    write_totals_section(Stream, Quarter),
    write_risk_section(Stream, Quarter).

write_violation_section(Stream, Quarter) :-
    format(Stream, "VIOLATIONS:~n", []),
    forall(
        (filed_in(TID, Quarter), is_violation(TID, Type)),
        format(Stream, "  • ~w: ~w~n", [TID, Type])
    ),
    nl(Stream).

write_totals_section(Stream, Quarter) :-
    flagged_total(Quarter, Total),
    threshold(enhanced_disclosure, Limit),
    format(Stream, "FINANCIAL SUMMARY:~n", []),
    format(Stream, "  Flagged total:  $~d~n", [Total]),
    format(Stream, "  Threshold:      $~d~n", [Limit]),
    (Total > Limit
    ->  format(Stream, "  Status:         ⚠ OVER THRESHOLD~n", [])
    ;   format(Stream, "  Status:         ✓ Within limits~n", [])
    ),
    nl(Stream).

write_risk_section(Stream, Quarter) :-
    findall(TID, (filed_in(TID, Quarter), is_violation(TID, _)), Vs),
    length(Vs, Count),
    (Count > 5 -> Risk = critical
    ; Count > 2 -> Risk = high
    ; Count > 0 -> Risk = medium
    ; Risk = low),
    format(Stream, "RISK LEVEL: ~w (~d violations)~n", [Risk, Count]).
```

```prolog
?- generate_report(q1_2024, 'report_q1.txt').
true.
```

Output in `report_q1.txt`:
```
╔══════════════════════════════════╗
║   INFERLAW COMPLIANCE REPORT     ║
╚══════════════════════════════════╝

Quarter: q1_2024
─────────────────────────────────────

VIOLATIONS:
  • t001: over_limit
  • t003: self_approved
  • t005: conflict

FINANCIAL SUMMARY:
  Flagged total:  $525000
  Threshold:      $500000
  Status:         ⚠ OVER THRESHOLD

RISK LEVEL: high (3 violations)
```

## with_output_to: Capture Output as String

```prolog
% Build a string without writing to a file
violation_summary(Quarter, Summary) :-
    with_output_to(string(Summary),
        (findall(TID-Type,
            (filed_in(TID, Quarter), is_violation(TID, Type)),
            Violations),
         forall(member(TID-Type, Violations),
            format("~w: ~w~n", [TID, Type]))
        )).
```

## Exercises

1. Write `print_directors/0` that prints all directors with their approval limits.
2. Write `load_facts(File)` that reads Prolog terms from a file and asserts them.
3. Add a timestamp to the report using `get_time/1` and `format_time/3`.

## What You Learned

- **write/1, writeln/1** — basic output
- **format/2** — formatted output with `~w`, `~d`, `~n`
- **read/1** — read a Prolog term from input
- **open/3, close/1** — file handle management
- **setup_call_cleanup/3** — safe resource handling (like try-with-resources)
- **forall/2** — iterate and perform side effects
- **with_output_to/2** — capture output as a string

Jordan's happy with the report. But Dr. Vasquez looks at the transaction model: "A transaction isn't just an ID and amount. It has nested fields — parties, dates, sub-transactions. We need proper structures."

---

[← Chapter 8: Negation](chapter-08-negation.md) | [Chapter 10: Structures →](chapter-10-structures.md)
