# Chapter 15: Practical — A Testing Framework

[prev: Macros](chapter-14-macros.md) | [next: Error Handling](chapter-16-errors.md)

## What We're Building

A miniature testing framework (like `clojure.test`) from scratch using macros. This shows the power of code-as-data — in ~50 lines, we'll build `deftest`, `is`, `testing`, and a test runner.

## Starting Simple: `is`

The core assertion macro. It evaluates an expression and reports pass/fail with context:

```clojure
(ns minitest.core)

(def ^:dynamic *results* (atom []))

(defmacro is [expr]
  `(let [result# ~expr]
     (swap! *results* conj
       {:pass result#
        :form '~expr
        :file ~*file*
        :line ~(:line (meta &form))})
     (when-not result#
       (printf "  FAIL: %s%n" '~expr))
     result#))
```

```clojure
(is (= 1 1))      ;; passes silently
(is (= 1 2))      ;; FAIL: (= 1 2)
```

## Better Failure Messages

When `(= expected actual)` fails, show both values:

```clojure
(defmacro is [expr]
  (if (and (seq? expr) (= '= (first expr)))
    ;; Special handling for equality assertions
    (let [[_ expected actual] expr]
      `(let [e# ~expected
             a# ~actual
             pass# (= e# a#)]
         (swap! *results* conj {:pass pass# :form '~expr})
         (when-not pass#
           (printf "  FAIL: %s%n    expected: %s%n    actual:   %s%n"
                   '~expr (pr-str e#) (pr-str a#)))
         pass#))
    ;; Generic assertion
    `(let [result# ~expr]
       (swap! *results* conj {:pass result# :form '~expr})
       (when-not result#
         (printf "  FAIL: %s%n" '~expr))
       result#)))
```

Now:

```clojure
(is (= 4 (+ 2 3)))
;; FAIL: (= 4 (+ 2 3))
;;   expected: 4
;;   actual:   5
```

## `testing` — Group assertions with a label

```clojure
(defmacro testing [description & body]
  `(do
     (println (str "  " ~description))
     ~@body))
```

## `deftest` — Define a named test

```clojure
(def tests (atom {}))

(defmacro deftest [name & body]
  `(swap! tests assoc '~name
     (fn []
       (println (str "Running: " '~name))
       (binding [*results* (atom [])]
         ~@body
         @*results*))))
```

## The Test Runner

```clojure
(defn run-tests []
  (let [all-results (atom {:pass 0 :fail 0 :total 0})]
    (doseq [[test-name test-fn] @tests]
      (let [results (test-fn)
            passes (count (filter :pass results))
            fails (count (remove :pass results))]
        (swap! all-results update :pass + passes)
        (swap! all-results update :fail + fails)
        (swap! all-results update :total + (count results))))
    (println "\n─────────────────────")
    (printf "Results: %d passed, %d failed, %d total%n"
            (:pass @all-results) (:fail @all-results) (:total @all-results))
    (when (pos? (:fail @all-results))
      (System/exit 1))))
```

## Using Our Framework

```clojure
(ns myapp.test
  (:require [minitest.core :refer [deftest testing is run-tests]]))

(deftest math-basics
  (testing "addition"
    (is (= 4 (+ 2 2)))
    (is (= 0 (+ -1 1))))
  (testing "multiplication"
    (is (= 6 (* 2 3)))
    (is (= 0 (* 0 100)))))

(deftest string-ops
  (testing "concatenation"
    (is (= "hello world" (str "hello" " " "world"))))
  (testing "case"
    (is (= "HELLO" (clojure.string/upper-case "hello")))
    (is (= "hello" (clojure.string/lower-case "HELLO")))))

(deftest failing-test
  (is (= 1 2))
  (is (nil? "not nil")))

(run-tests)
```

Output:

```
Running: math-basics
  addition
  multiplication
Running: string-ops
  concatenation
  case
Running: failing-test
  FAIL: (= 1 2)
    expected: 1
    actual:   2
  FAIL: (nil? "not nil")

─────────────────────
Results: 7 passed, 2 failed, 9 total
```

## Adding `is-thrown?`

Test that code throws an exception:

```clojure
(defmacro is-thrown? [exception-class & body]
  `(let [pass# (try
                 (do ~@body)
                 false
                 (catch ~exception-class e#
                   true))]
     (swap! *results* conj {:pass pass# :form '(is-thrown? ~exception-class ~@body)})
     (when-not pass#
       (printf "  FAIL: expected %s to be thrown%n" '~exception-class))
     pass#))

;; Usage:
(deftest error-handling
  (is-thrown? ArithmeticException (/ 1 0))
  (is-thrown? NullPointerException (.length nil)))
```

## Adding `are` — Table-driven tests

```clojure
(defmacro are [argv expr & args]
  `(do ~@(for [row (partition (count argv) args)]
           `(let [~argv (vector ~@row)]
              (is ~expr)))))

;; Usage:
(deftest arithmetic-table
  (are [a b expected]
    (= expected (+ a b))
    1 2 3
    0 0 0
    -1 1 0
    100 200 300))
```

## The Real `clojure.test`

Our framework covers the same concepts as `clojure.test`:

| Our framework | `clojure.test`     |
| ------------- | ------------------ |
| `deftest`     | `deftest`          |
| `testing`     | `testing`          |
| `is`          | `is`               |
| `is-thrown?`  | `is (thrown? ...)` |
| `are`         | `are`              |
| `run-tests`   | `run-tests`        |

The real one adds fixtures, test selectors, and reporter protocols — but the core is exactly what we built.

## What You Learned

- Macros receive unevaluated code as data structures
- `'~expr` captures the source form for error messages
- `&form` metadata gives you file/line information
- Dynamic vars (`^:dynamic`) + `binding` create test isolation
- ~50 lines of macro code = a complete testing framework
- The pattern: macro for syntax → function for logic

## Exercises

1. Add a `before-each` / `after-each` fixture mechanism
2. Add colorized output (green for pass, red for fail)
3. Add a `--filter` option to run only tests matching a pattern
4. Track execution time per test
