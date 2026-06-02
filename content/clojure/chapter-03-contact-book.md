# Chapter 3: Practical — A Contact Book

[prev: The REPL](chapter-02-repl.md) | [next: Syntax and Evaluation](chapter-04-syntax.md)

## What We're Building

A command-line contact book that can add, search, list, and delete contacts. Along the way you'll learn atoms (mutable state), maps (data), and basic I/O.

## The Data Model

Contacts are maps. The "database" is an atom holding a vector of maps.

```clojure
(ns contacts.core
  (:require [clojure.string :as str]))

(def db (atom []))
```

An atom is a thread-safe mutable reference. You read it with `@` (deref) and update it with `swap!`.

## Adding Contacts

```clojure
(defn add-contact! [name email phone]
  (let [contact {:id (random-uuid)
                 :name name
                 :email email
                 :phone phone
                 :created-at (java.time.Instant/now)}]
    (swap! db conj contact)
    contact))
```

Try it:

```clojure
(add-contact! "Alice" "alice@example.com" "555-1234")
;=> {:id #uuid "a1b2c3...", :name "Alice", :email "alice@example.com", ...}

(add-contact! "Bob" "bob@example.com" "555-5678")
```

## Listing Contacts

```clojure
(defn list-contacts []
  @db)

(defn print-contacts []
  (doseq [c (list-contacts)]
    (printf "%-20s %-30s %s%n" (:name c) (:email c) (:phone c))))
```

## Searching

```clojure
(defn search [query]
  (let [q (str/lower-case query)]
    (filter (fn [c]
              (or (str/includes? (str/lower-case (:name c)) q)
                  (str/includes? (str/lower-case (:email c)) q)))
            @db)))
```

```clojure
(search "alice")
;=> ({:name "Alice", :email "alice@example.com", ...})
```

## Deleting

```clojure
(defn delete-contact! [id]
  (swap! db (fn [contacts]
              (vec (remove #(= (:id %) id) contacts)))))
```

## Persistence: Save to File

```clojure
(defn save! [filename]
  (spit filename (pr-str @db)))

(defn load! [filename]
  (when (.exists (java.io.File. filename))
    (reset! db (read-string (slurp filename)))))
```

`spit` writes a string to a file. `slurp` reads a file into a string. `pr-str` serializes Clojure data to a string. `read-string` parses it back.

## The Interactive Loop

```clojure
(defn prompt [msg]
  (print msg)
  (flush)
  (read-line))

(defn run []
  (load! "contacts.edn")
  (println "📇 Contact Book (type 'help' for commands)")
  (loop []
    (let [input (prompt "> ")]
      (when input
        (let [parts (str/split (str/trim input) #"\s+" 2)
              cmd (first parts)
              arg (second parts)]
          (case cmd
            "add"    (let [[n e p] (str/split arg #"\s+")]
                       (add-contact! n e p)
                       (println "✓ Added."))
            "list"   (print-contacts)
            "search" (doseq [c (search arg)]
                       (printf "  %s <%s>%n" (:name c) (:email c)))
            "save"   (do (save! "contacts.edn") (println "✓ Saved."))
            "quit"   (do (save! "contacts.edn") (println "Bye!") (System/exit 0))
            "help"   (println "Commands: add <name> <email> <phone> | list | search <query> | save | quit")
            (println "Unknown command. Type 'help'"))
          (recur))))))

(defn -main []
  (run))
```

## Running It

```bash
clj -M -m contacts.core
```

```
📇 Contact Book (type 'help' for commands)
> add Alice alice@test.com 555-1234
✓ Added.
> add Bob bob@test.com 555-5678
✓ Added.
> list
Alice                alice@test.com                 555-1234
Bob                  bob@test.com                   555-5678
> search alice
  Alice <alice@test.com>
> save
✓ Saved.
> quit
Bye!
```

## What You Learned

| Concept                   | Example                            |
| ------------------------- | ---------------------------------- |
| Atoms (mutable state)     | `(def db (atom []))`               |
| Reading atoms             | `@db` or `(deref db)`              |
| Updating atoms            | `(swap! db conj item)`             |
| Maps (data)               | `{:name "Alice" :email "a@b.com"}` |
| Keyword access            | `(:name contact)`                  |
| Filtering                 | `(filter pred coll)`               |
| String ops                | `str/lower-case`, `str/includes?`  |
| File I/O                  | `spit`, `slurp`                    |
| Serialization             | `pr-str`, `read-string`            |
| Loops                     | `(loop [] ... (recur))`            |
| Pattern matching on input | `(case cmd "add" ... "list" ...)`  |

## Exercises

1. Add an "edit" command that updates a contact's email
2. Add a "count" command that shows how many contacts exist
3. Make the search also match phone numbers
4. Add a "sort" command (alphabetical by name)
