# Chapter 22: Java Interop

[prev: A Build Tool](chapter-21-build-tool.md) | [next: A Database Layer](chapter-23-database.md)

## Clojure ♥ Java

Clojure runs on the JVM and has seamless Java interop. No wrappers, no FFI — you call Java directly. This gives you access to every Java library ever written.

## Calling Java Methods

```clojure
;; Instance methods: (.method object args)
(.toUpperCase "hello")               ;=> "HELLO"
(.length "hello")                    ;=> 5
(.contains "hello world" "world")    ;=> true

;; Static methods: (Class/method args)
(Math/pow 2 10)                      ;=> 1024.0
(Integer/parseInt "42")              ;=> 42
(System/getenv "HOME")               ;=> "/home/user"
(UUID/randomUUID)                    ;=> #uuid "a1b2c3..."

;; Constructors: (ClassName. args)
(java.util.Date.)                    ;=> #inst "2024-..."
(java.io.File. "/tmp/test.txt")
(StringBuilder. "hello")
```

## Accessing Fields

```clojure
;; Instance fields
(.-length (int-array [1 2 3]))  ;; doesn't work for arrays, use alength

;; Static fields
Integer/MAX_VALUE    ;=> 2147483647
Math/PI              ;=> 3.141592653589793
```

## The Dot-Dot Macro (`..`)

Chain method calls:

```clojure
;; Instead of:
(.toString (.append (.append (StringBuilder. "") "hello") " world"))

;; Use:
(.. (StringBuilder. "") (append "hello") (append " world") toString)
;=> "hello world"
```

## `doto` — Mutate and Return

```clojure
(doto (java.util.HashMap.)
  (.put "a" 1)
  (.put "b" 2)
  (.put "c" 3))
;=> {"a" 1, "b" 2, "c" 3}

(doto (StringBuilder.)
  (.append "Hello")
  (.append " ")
  (.append "World"))
;=> StringBuilder: "Hello World"
```

## Working with Java Collections

```clojure
;; Clojure seqs over Java collections
(seq (java.util.ArrayList. [1 2 3]))  ;=> (1 2 3)
(into [] (java.util.LinkedList. [1 2 3]))  ;=> [1 2 3]

;; Convert Clojure → Java
(java.util.ArrayList. [1 2 3])
(java.util.HashMap. {:a 1 :b 2})

;; Arrays
(into-array String ["a" "b" "c"])
(int-array [1 2 3 4 5])
(alength (int-array [1 2 3]))  ;=> 3
(aget (int-array [10 20 30]) 1)  ;=> 20
```

## Implementing Java Interfaces

### `reify` — Anonymous implementation

```clojure
(def my-comparator
  (reify java.util.Comparator
    (compare [_ a b]
      (- (count b) (count a)))))  ;; sort by length descending

(sort my-comparator ["hi" "hello" "hey"])
;=> ("hello" "hey" "hi")
```

### `proxy` — When you need a class, not just interface

```clojure
(def my-thread
  (proxy [Thread] []
    (run []
      (println "Running in thread:" (.getName (Thread/currentThread))))))

(.start my-thread)
```

## Using Popular Java Libraries

### java.time (Date/Time)

```clojure
(import '[java.time LocalDate LocalDateTime Duration Instant])

(def today (LocalDate/now))
(def tomorrow (.plusDays today 1))
(def formatted (.format today (java.time.format.DateTimeFormatter/ofPattern "dd/MM/yyyy")))

(.between (java.time.temporal.ChronoUnit/DAYS) today tomorrow)  ;=> 1
```

### java.nio.file (File System)

```clojure
(import '[java.nio.file Files Paths Path])

(def path (Paths/get "src" (into-array String ["myapp" "core.clj"])))
(Files/exists path (into-array java.nio.file.LinkOption []))
(Files/readString path)
(Files/list (Paths/get "src" (into-array String [])))
```

### HTTP Client (Java 11+)

```clojure
(import '[java.net.http HttpClient HttpRequest HttpResponse$BodyHandlers]
        '[java.net URI])

(def client (HttpClient/newHttpClient))

(defn http-get [url]
  (let [request (-> (HttpRequest/newBuilder)
                    (.uri (URI/create url))
                    (.build))
        response (.send client request (HttpResponse$BodyHandlers/ofString))]
    {:status (.statusCode response)
     :body (.body response)}))

(http-get "https://httpbin.org/get")
```

## Type Hints (Performance)

When Clojure can't infer the type, it uses reflection (slow). Type hints fix this:

```clojure
;; Slow (reflection):
(defn upper [s] (.toUpperCase s))

;; Fast (direct method call):
(defn upper [^String s] (.toUpperCase s))

;; Check for reflection warnings:
(set! *warn-on-reflection* true)
```

## Exception Handling with Java

```clojure
(try
  (Integer/parseInt "not a number")
  (catch NumberFormatException e
    (println "Bad number:" (.getMessage e)))
  (catch Exception e
    (println "Other error:" (type e))))
```

## Key Takeaways

- `.method` for instance, `Class/method` for static, `Class.` for constructors
- `doto` for Java mutation patterns, `..` for method chaining
- `reify` for interfaces, `proxy` for classes
- Type hints (`^String`) eliminate reflection for performance
- Every Java library is one `import` away — no wrappers needed
- Clojure collections implement Java interfaces (List, Map, etc.) automatically
