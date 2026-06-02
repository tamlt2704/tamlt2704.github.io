# Chapter 16: Error Handling

[prev: A Testing Framework](chapter-15-testing-framework.md) | [next: Spec and Validation](chapter-17-spec.md)

## Exceptions on the JVM

Clojure runs on the JVM, so it uses Java exceptions. But idiomatic Clojure prefers data over exception hierarchies.

## Basic try/catch

```clojure
(try
  (/ 10 0)
  (catch ArithmeticException e
    (println "Can't divide by zero:" (.getMessage e))
    :error))
;=> :error
```

### Multiple catch clauses

```clojure
(try
  (do-something)
  (catch java.io.FileNotFoundException e
    {:error :not-found :msg (.getMessage e)})
  (catch java.io.IOException e
    {:error :io-error :msg (.getMessage e)})
  (catch Exception e
    {:error :unknown :msg (.getMessage e)})
  (finally
    (cleanup!)))
```

## `ex-info` and `ex-data` — Exceptions as Data

Clojure's idiomatic way: throw exceptions carrying structured data.

```clojure
;; Throw with data
(throw (ex-info "User not found"
                {:type :not-found
                 :user-id 42
                 :searched-at (java.time.Instant/now)}))

;; Catch and extract data
(try
  (find-user! 42)
  (catch clojure.lang.ExceptionInfo e
    (let [{:keys [type user-id]} (ex-data e)]
      (case type
        :not-found (println "No user with id" user-id)
        :forbidden (println "Access denied")
        (throw e)))))  ;; re-throw if we can't handle it
```

## Returning Errors as Values

Often better than throwing — makes error handling explicit in the return type:

```clojure
;; Convention: return {:ok value} or {:error reason}
(defn parse-int [s]
  (try
    {:ok (Long/parseLong s)}
    (catch NumberFormatException _
      {:error {:type :invalid-number :input s}})))

(parse-int "42")    ;=> {:ok 42}
(parse-int "abc")   ;=> {:error {:type :invalid-number, :input "abc"}}

;; Chain with pattern matching
(let [{:keys [ok error]} (parse-int input)]
  (if ok
    (process ok)
    (handle-error error)))
```

## Error Threading

```clojure
(defn try-> [val & fns]
  (reduce (fn [acc f]
            (if (:error acc) acc (f acc)))
          {:ok val}
          fns))

(defn validate-age [{:keys [ok]}]
  (if (>= ok 0) {:ok ok} {:error "Age must be positive"}))

(defn validate-max [{:keys [ok]}]
  (if (<= ok 150) {:ok ok} {:error "Age too large"}))

(try-> 25 validate-age validate-max)   ;=> {:ok 25}
(try-> -1 validate-age validate-max)   ;=> {:error "Age must be positive"}
```

## Conditions and Restarts (CL-inspired)

Common Lisp's condition system lets callers decide how to handle errors. In Clojure, you can approximate this with dynamic vars:

```clojure
(def ^:dynamic *on-error* :throw)

(defn parse-record [line]
  (try
    (let [[name age] (clojure.string/split line #",")]
      {:name name :age (parse-long age)})
    (catch Exception e
      (case *on-error*
        :throw (throw e)
        :skip nil
        :default {:name "UNKNOWN" :age 0}))))

;; Caller decides policy:
(binding [*on-error* :skip]
  (keep parse-record ["Alice,30" "BAD_LINE" "Bob,25"]))
;=> ({:name "Alice", :age 30} {:name "Bob", :age 25})

(binding [*on-error* :default]
  (map parse-record ["Alice,30" "BAD_LINE" "Bob,25"]))
;=> ({:name "Alice", :age 30} {:name "UNKNOWN", :age 0} {:name "Bob", :age 25})
```

## Validation with Predicates

```clojure
(defn validate [data rules]
  (let [errors (keep (fn [[field pred msg]]
                       (when-not (pred (get data field))
                         {:field field :message msg}))
                     rules)]
    (if (seq errors)
      {:errors errors}
      {:ok data})))

(validate {:name "" :age -5 :email "bad"}
  [[:name #(pos? (count %)) "Name required"]
   [:age pos? "Age must be positive"]
   [:email #(re-matches #".+@.+" %) "Invalid email"]])
;=> {:errors [{:field :name, :message "Name required"}
;             {:field :age, :message "Age must be positive"}
;             {:field :email, :message "Invalid email"}]}
```

## Logging Errors

```clojure
(require '[clojure.tools.logging :as log])

(defn safe-process [item]
  (try
    (process! item)
    (catch Exception e
      (log/error e "Failed to process item" {:item-id (:id item)})
      {:error (.getMessage e) :item item})))
```

## Key Takeaways

- Use `ex-info`/`ex-data` for exceptions carrying structured data
- Prefer returning error values (`{:ok v}` / `{:error e}`) for expected failures
- Reserve exceptions for truly unexpected situations
- Dynamic vars can approximate Common Lisp's condition/restart pattern
- Validation functions return data describing all errors, not just the first
- `try`/`catch`/`finally` works like Java but returns a value
