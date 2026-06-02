# Chapter 17: Spec and Validation

[prev: Error Handling](chapter-16-errors.md) | [next: A Spam Filter](chapter-18-spam-filter.md)

## What Is Spec?

`clojure.spec` lets you describe the shape of your data and functions, then use those descriptions for validation, error reporting, generative testing, and documentation — all from one definition.

## Basic Specs

```clojure
(require '[clojure.spec.alpha :as s])

;; Predicates as specs
(s/valid? int? 42)         ;=> true
(s/valid? string? 42)      ;=> false
(s/valid? #(> % 0) 5)      ;=> true

;; Register named specs
(s/def ::name (s/and string? #(pos? (count %))))
(s/def ::age (s/and int? #(<= 0 % 150)))
(s/def ::email (s/and string? #(re-matches #".+@.+\..+" %)))

(s/valid? ::name "Alice")  ;=> true
(s/valid? ::name "")       ;=> false
(s/valid? ::age 30)        ;=> true
```

## Map Specs

```clojure
(s/def ::user (s/keys :req-un [::name ::email]
                      :opt-un [::age ::phone]))

(s/valid? ::user {:name "Alice" :email "a@b.com"})           ;=> true
(s/valid? ::user {:name "Alice"})                            ;=> false (missing email)
(s/valid? ::user {:name "Alice" :email "a@b.com" :age 30})   ;=> true
```

## `explain` — Why Did It Fail?

```clojure
(s/explain ::user {:name "" :email "bad" :age -5})
;; val: "" fails spec: ::name predicate: (pos? (count %))
;; val: "bad" fails spec: ::email predicate: (re-matches ...)
;; val: -5 fails spec: ::age predicate: (<= 0 % 150)
```

```clojure
;; Machine-readable
(s/explain-data ::user {:name "" :email "bad"})
;=> {:clojure.spec.alpha/problems [...] :clojure.spec.alpha/value {...}}
```

## Collection Specs

```clojure
(s/def ::scores (s/coll-of int? :min-count 1 :max-count 100))
(s/def ::tags (s/coll-of string? :kind set?))
(s/def ::matrix (s/coll-of (s/coll-of number?)))

(s/valid? ::scores [85 90 78])       ;=> true
(s/valid? ::tags #{"clojure" "jvm"}) ;=> true
```

## Composing Specs

```clojure
;; s/and — all must pass
(s/def ::positive-int (s/and int? pos?))

;; s/or — one must pass (labeled branches)
(s/def ::id (s/or :numeric int? :string string?))
(s/conform ::id 42)       ;=> [:numeric 42]
(s/conform ::id "abc")    ;=> [:string "abc"]

;; s/nilable — value or nil
(s/def ::optional-name (s/nilable ::name))
```

## Function Specs

```clojure
(defn calculate-tax [income rate]
  (* income rate))

(s/fdef calculate-tax
  :args (s/cat :income (s/and number? pos?)
               :rate (s/and number? #(<= 0 % 1)))
  :ret number?
  :fn #(< (:ret %) (-> % :args :income)))  ;; tax < income
```

## Generative Testing

Spec can generate random valid data for testing:

```clojure
(require '[clojure.spec.gen.alpha :as gen])

(gen/sample (s/gen ::name) 5)
;=> ("a" "xK" "mQ2" "hello" "testing")

(gen/sample (s/gen ::user) 3)
;=> ({:name "aB" :email "x@y.com" :age 4}
;    {:name "test" :email "foo@bar.net"}
;    {:name "kL" :email "a@b.co" :age 87})
```

### Property-based testing with `stest`

```clojure
(require '[clojure.spec.test.alpha :as stest])

(stest/check `calculate-tax)
;; Runs 1000 random inputs, checks :ret and :fn specs
```

## Coercion (Parsing Strings)

Spec validates but doesn't coerce. Use `conform` with custom specs:

```clojure
(s/def ::int-string
  (s/conformer
    (fn [v]
      (try (Long/parseLong v)
           (catch Exception _ ::s/invalid)))))

(s/conform ::int-string "42")    ;=> 42
(s/conform ::int-string "abc")   ;=> :clojure.spec.alpha/invalid
```

## API Validation Pattern

```clojure
(defn validate-request [spec data]
  (if (s/valid? spec data)
    {:ok (s/conform spec data)}
    {:error (s/explain-data spec data)}))

(defn create-user-handler [{:keys [body-params]}]
  (let [{:keys [ok error]} (validate-request ::user body-params)]
    (if ok
      {:status 201 :body (db/insert-user! ok)}
      {:status 400 :body {:errors (mapv #(select-keys % [:path :pred :val])
                                        (::s/problems error))}})))
```

## Key Takeaways

- Specs describe data shape using predicates and composition
- `s/keys` for maps, `s/coll-of` for collections, `s/cat` for sequences
- `explain` gives human-readable failure reasons
- `gen/sample` creates random valid test data
- `stest/check` does property-based testing from function specs
- Spec is opt-in — use it where validation matters most (API boundaries, config)
