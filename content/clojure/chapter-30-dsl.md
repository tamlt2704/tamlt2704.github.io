# Chapter 30: Practical — Building a DSL

[prev: HTML Generation](chapter-29-html-generation.md) | [next: Production Deployment](chapter-31-production.md)

## What We're Building

A domain-specific language for defining data transformation pipelines — showing how macros let you extend Clojure's syntax for your domain. This is Lisp's superpower.

## The Problem

You have ETL pipelines described in config that you want to execute:

```clojure
;; Users describe transformations declaratively:
(defpipeline customer-import
  (source :csv "customers.csv")
  (validate {:name string? :email #(re-matches #".+@.+" %)})
  (transform :email clojure.string/lower-case)
  (transform :name clojure.string/trim)
  (filter-rows #(not (empty? (:name %))))
  (deduplicate :email)
  (sink :jdbc {:table "customers" :mode :upsert}))
```

## Step 1: Define the Pipeline Macro

```clojure
(ns dsl.pipeline)

(defmacro defpipeline [name & steps]
  `(def ~name
     {:name ~(str name)
      :steps [~@(map (fn [step] `'~step) steps)]
      :compiled (fn [data#]
                  (-> data# ~@(map compile-step steps)))}))
```

## Step 2: Step Compiler

```clojure
(defmulti compile-step first)

(defmethod compile-step 'source [[_ type & args]]
  (case type
    :csv `(read-csv ~(first args))
    :jdbc `(query-db ~(first args))
    :json `(read-json ~(first args))))

(defmethod compile-step 'validate [[_ schema]]
  `(validate-records ~schema))

(defmethod compile-step 'transform [[_ field f]]
  `(mapv #(update % ~field ~f)))

(defmethod compile-step 'filter-rows [[_ pred]]
  `(filterv ~pred))

(defmethod compile-step 'deduplicate [[_ field]]
  `(deduplicate-by ~field))

(defmethod compile-step 'sink [[_ type opts]]
  `(write-sink ~type ~opts))
```

## Step 3: Runtime Functions

```clojure
(ns dsl.runtime
  (:require [clojure.data.csv :as csv]
            [clojure.java.io :as io]))

(defn read-csv [filename]
  (with-open [r (io/reader filename)]
    (let [data (csv/read-csv r)
          headers (map keyword (first data))]
      (mapv #(zipmap headers %) (rest data)))))

(defn validate-records [schema records]
  (mapv (fn [record]
          (let [errors (keep (fn [[field pred]]
                               (when-not (pred (get record field))
                                 {:field field :value (get record field)}))
                             schema)]
            (assoc record :__errors errors :__valid (empty? errors))))
        records))

(defn deduplicate-by [field records]
  (vals (reduce (fn [acc r] (assoc acc (get r field) r)) {} records)))

(defn write-sink [type opts records]
  (case type
    :jdbc (do (println (format "Writing %d records to %s" (count records) (:table opts)))
              records)
    :file (do (spit (:path opts) (pr-str records))
              records)))
```

## Step 4: Execution

```clojure
(defn run-pipeline! [pipeline]
  (println (str "▶ Running: " (:name pipeline)))
  (let [start (System/currentTimeMillis)
        result ((:compiled pipeline) nil)
        elapsed (- (System/currentTimeMillis) start)]
    (printf "✓ %s completed in %dms (%d records)%n"
            (:name pipeline) elapsed (count result))
    result))

(run-pipeline! customer-import)
```

## A Query DSL

```clojure
(defmacro query [& clauses]
  (let [parsed (reduce (fn [acc [k & v]]
                         (assoc acc k v))
                       {} (partition-by keyword? clauses))]
    `(-> ~(:from parsed)
         ~@(when-let [w (:where parsed)]
             [`(filter (fn [~'row] ~@w))])
         ~@(when-let [s (:select parsed)]
             [`(map #(select-keys % [~@s]))])
         ~@(when-let [o (:order-by parsed)]
             [`(sort-by ~@o)])
         ~@(when-let [l (:limit parsed)]
             [`(take ~@l)])
         vec)))

;; Usage:
(query
  :from users
  :where (> (:age row) 18)
  :select [:name :email]
  :order-by :name
  :limit 10)
```

## A Configuration DSL

```clojure
(defmacro defconfig [name & body]
  (let [config (reduce (fn [acc [k v]] (assoc acc k v))
                       {} (partition 2 body))]
    `(def ~name ~config)))

(defconfig db-settings
  :host "localhost"
  :port 5432
  :database "myapp"
  :pool-size 10
  :ssl true)

;; db-settings => {:host "localhost", :port 5432, :database "myapp", ...}
```

## A Test DSL

```clojure
(defmacro scenario [description & steps]
  `(do
     (println ~(str "Scenario: " description))
     ~@(map (fn [[action & args]]
              (case action
                'given `(println ~(str "  Given " ~@args))
                'when `(println ~(str "  When " ~@args))
                'then `(do (println ~(str "  Then " ~@args))
                           (assert ~@args))))
            steps)))

(scenario "User login"
  (given "a registered user")
  (when "they enter valid credentials")
  (then (= 200 (:status (login "alice" "pass123")))))
```

## DSL Design Guidelines

1. **Start with data.** Define what the user writes first, then make it work.
2. **Macros for syntax, functions for logic.** Keep macros thin.
3. **Make it readable to non-Clojure developers** — that's the point of a DSL.
4. **Provide good error messages** when the DSL is misused.
5. **Keep it composable** — users should combine DSL pieces freely.

## Key Takeaways

- DSLs in Clojure are just macros that expand to regular code
- Multimethods dispatch on step type for extensibility
- The "interpreter" pattern: store DSL as data, interpret at runtime
- The "compiler" pattern: macros expand DSL to optimized code at compile time
- Lisp macros make DSLs trivial — no parser needed, code IS the AST
