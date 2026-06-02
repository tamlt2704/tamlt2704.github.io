# Chapter 14: Macros — Code as Data

[prev: Concurrency](chapter-13-concurrency.md) | [next: A Testing Framework](chapter-15-testing-framework.md)

## Why Macros

Functions operate on values. Macros operate on **code** — they receive unevaluated source code as data, transform it, and return new code. This lets you extend the language itself.

## Code Is Data (Homoiconicity)

Clojure code is made of the same data structures you manipulate daily:

```clojure
;; This code:
(+ 1 2 3)

;; Is literally a list containing a symbol and numbers:
(type '(+ 1 2 3))  ;=> clojure.lang.PersistentList
(first '(+ 1 2 3)) ;=> +
(rest '(+ 1 2 3))  ;=> (1 2 3)
```

## Your First Macro

```clojure
(defmacro unless [condition & body]
  `(if (not ~condition)
     (do ~@body)))

(unless false
  (println "this runs!")
  42)
;; this runs!
;=> 42
```

### What happened:

1. `unless` receives the unevaluated forms: `false`, `(println "this runs!")`, `42`
2. It returns new code: `(if (not false) (do (println "this runs!") 42))`
3. That code gets evaluated

## Syntax-Quote, Unquote, Splice

```clojure
;; ` (syntax-quote): template for code
;; ~ (unquote): insert a value into the template
;; ~@ (unquote-splice): insert a list, spreading its elements

(let [x 5]
  `(+ 1 ~x))           ;=> (clojure.core/+ 1 5)

(let [args [2 3 4]]
  `(+ 1 ~@args))        ;=> (clojure.core/+ 1 2 3 4)
```

## `macroexpand` — See What a Macro Produces

```clojure
(macroexpand '(unless false (println "hi")))
;=> (if (clojure.core/not false) (do (println "hi")))

(macroexpand-1 '(when true (println "hi")))
;=> (if true (do (println "hi")))
```

Always use `macroexpand` when writing macros. It's your debugger.

## Practical Macros

### `with-timing` — Measure execution time

```clojure
(defmacro with-timing [label & body]
  `(let [start# (System/nanoTime)
         result# (do ~@body)
         elapsed# (/ (- (System/nanoTime) start#) 1e6)]
     (printf "%s: %.2fms%n" ~label elapsed#)
     result#))

(with-timing "fetch"
  (Thread/sleep 100)
  :done)
;; fetch: 100.23ms
;=> :done
```

The `#` suffix generates unique symbols (gensym) to avoid variable capture.

### `defapi` — Reduce handler boilerplate

```clojure
(defmacro defapi [name method path & body]
  `(defn ~name [request#]
     (try
       {:status 200
        :body (let [~'params (:params request#)
                    ~'body (:body-params request#)]
                ~@body)}
       (catch Exception e#
         {:status 500
          :body {:error (.getMessage e#)}}))))

(defapi get-users :get "/users"
  (db/find-all-users))

(defapi create-user :post "/users"
  (db/insert-user! body))
```

### `with-retry` — Retry on failure

```clojure
(defmacro with-retry [n & body]
  `(loop [attempts# ~n]
     (let [result# (try {:ok (do ~@body)}
                        (catch Exception e#
                          (if (pos? attempts#)
                            {:retry e#}
                            (throw e#))))]
       (if (:retry result#)
         (recur (dec attempts#))
         (:ok result#)))))

(with-retry 3
  (fetch-from-api "/data"))
```

### `defonce-fn` — Cached function results

```clojure
(defmacro defmemo [name args & body]
  `(def ~name (memoize (fn ~args ~@body))))

(defmemo fibonacci [n]
  (if (<= n 1) n
    (+ (fibonacci (- n 1)) (fibonacci (- n 2)))))

(fibonacci 40)  ;=> 102334155 (instant, cached)
```

## Macro Rules

1. **Don't write a macro if a function will do.** Functions compose better.
2. **Use macros for:** new control flow, compile-time transforms, eliminating boilerplate.
3. **Always test with `macroexpand`.**
4. **Use `gensym` (auto-gensym `#`)** to avoid capturing user variables.
5. **Keep macros thin** — put logic in helper functions, use the macro only for syntax.

## When Functions Can't Do It

Functions evaluate their arguments before being called. Macros receive raw code:

```clojure
;; This CAN'T be a function (args would be evaluated):
(defmacro lazy-or [& exprs]
  (if (empty? exprs)
    nil
    `(let [v# ~(first exprs)]
       (if v# v# (lazy-or ~@(rest exprs))))))

(lazy-or nil false (do (println "evaluated!") 42))
;; evaluated!
;=> 42
;; Only the third expr was evaluated!
```

## Anaphoric Macros

Introduce implicit bindings:

```clojure
(defmacro aif [test then else]
  `(let [~'it ~test]
     (if ~'it ~then ~else)))

(aif (find-user "alice")
  (println "Found:" (:name it))
  (println "Not found"))
```

## Key Takeaways

- Macros transform code at compile time — they receive and return data structures
- Use syntax-quote (`` ` ``), unquote (`~`), and splice (`~@`) to build code templates
- Auto-gensym (`name#`) prevents variable capture
- `macroexpand` is essential for debugging macros
- Prefer functions over macros — only use macros when you need to control evaluation
- Common use cases: control flow, DSLs, boilerplate elimination
