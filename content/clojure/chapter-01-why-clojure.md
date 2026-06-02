# Chapter 1: Why Clojure?

[next: The REPL](chapter-02-repl.md) | [Overview](chapter-00-overview.md)

## A Lisp for the Real World

Clojure is a modern Lisp that runs on the JVM. It was created by Rich Hickey in 2007 to solve problems he kept hitting in production systems: managing state in concurrent programs, dealing with information that changes over time, and building systems that are simple enough to reason about.

Unlike Common Lisp (which is a standard with many implementations), Clojure is one language with one implementation and a laser focus on practical programming.

## What Makes Clojure Different

### Immutable by Default

In most languages, data structures are mutable — you change them in place. In Clojure, data never changes. When you "add" to a map, you get a new map. The old one still exists, unchanged.

```clojure
(def person {:name "Alice" :age 30})
(def older (assoc person :age 31))

person  ;=> {:name "Alice", :age 30}  — unchanged
older   ;=> {:name "Alice", :age 31}  — new value
```

This eliminates entire categories of bugs around shared mutable state.

### Functional First

Functions are the primary building block. You compose small functions into larger ones. Data flows through transformations rather than being mutated in place.

```clojure
(->> transactions
     (filter #(= (:type %) :purchase))
     (map :amount)
     (reduce +))
```

### Hosted on the JVM

Clojure runs on the same JVM as Java. You get:

- Access to every Java library ever written
- Battle-tested garbage collection and JIT compilation
- Deployment to anywhere Java runs

```clojure
;; Use Java directly
(.toUpperCase "hello")          ;=> "HELLO"
(java.time.LocalDate/now)       ;=> #object[java.time.LocalDate "2024-01-15"]
```

### Designed for Concurrency

Clojure provides managed references (atoms, refs, agents) that give you safe, coordinated access to mutable state without manual locking.

```clojure
(def counter (atom 0))
(swap! counter inc)  ;=> 1 — thread-safe, no locks
```

### REPL-Driven Development

You develop Clojure interactively. Write a function, evaluate it immediately, see the result, refine. No compile-wait-run cycle. The feedback loop is measured in milliseconds.

## Clojure vs Common Lisp

If you've read _Practical Common Lisp_, here's how Clojure differs:

| Aspect          | Common Lisp                   | Clojure                                 |
| --------------- | ----------------------------- | --------------------------------------- |
| Platform        | Native implementations        | JVM (also JS, CLR)                      |
| Data structures | Mutable lists, arrays         | Immutable persistent data               |
| Concurrency     | Implementation-specific       | Built-in (atoms, refs, STM)             |
| OOP             | CLOS (classes + multimethods) | Protocols + multimethods                |
| Macros          | Yes (hygienic by convention)  | Yes (with syntax-quote)                 |
| Ecosystem       | Quicklisp (~2K libs)          | Maven/Clojars (~30K libs) + all of Java |
| Strings         | Not Unicode-first             | Java strings (UTF-16)                   |
| REPL            | Yes                           | Yes (nREPL, socket REPL)                |

## What Clojure Is Good For

- **Data processing** — ETL, analytics, transformation pipelines
- **Web services** — APIs, microservices (Ring/Pedestal)
- **Concurrent systems** — Real-time data, event processing
- **Scripting** — Babashka runs Clojure scripts instantly
- **Full-stack** — ClojureScript shares code with the backend

## What Clojure Is Not

- Not ideal for systems programming (use Rust/C)
- Not great for mobile apps (though possible via React Native)
- Not the best for game engines requiring raw performance
- Not mainstream — smaller job market than Java/Python

## Companies Using Clojure

- **Nubank** — World's largest digital bank (entire backend)
- **Walmart** — Checkout and pricing systems
- **Netflix** — Data pipeline infrastructure
- **Apple** — Internal tools
- **Metabase** — Open-source BI tool (full Clojure stack)

## Your First Taste

```clojure
;; A function that greets someone
(defn greet [name]
  (str "Hello, " name "!"))

(greet "World")  ;=> "Hello, World!"

;; Processing a list of numbers
(def numbers [1 2 3 4 5 6 7 8 9 10])

(->> numbers
     (filter odd?)
     (map #(* % %))
     (reduce +))
;=> 165 (sum of squares of odd numbers)
```

If this looks alien, don't worry. By chapter 5, you'll be reading it as naturally as any other language. The parentheses aren't noise — they're the key to Clojure's power.

Let's get started.
