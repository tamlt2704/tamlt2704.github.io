# Chapter 21: Practical — A Build Tool

[prev: A Chat Server](chapter-20-chat-server.md) | [next: Java Interop](chapter-22-java-interop.md)

## What We're Building

A miniature build tool (like Make/Lein/Babashka tasks) that resolves task dependencies, runs them in correct order, and supports incremental builds. This exercises graphs, topological sort, and file system operations.

## Task Definition

```clojure
(ns build.core
  (:require [clojure.java.io :as io]
            [clojure.string :as str]))

(def tasks (atom {}))

(defmacro deftask [name opts & body]
  `(swap! tasks assoc ~(keyword name)
     {:name ~(keyword name)
      :deps ~(:deps opts [])
      :doc ~(:doc opts "")
      :fn (fn [] ~@body)}))

;; Define tasks
(deftask clean {:doc "Remove build artifacts"}
  (let [dir (io/file "target")]
    (when (.exists dir)
      (doseq [f (reverse (file-seq dir))]
        (.delete f)))
    (println "✓ Cleaned target/")))

(deftask compile {:doc "Compile source files" :deps [:clean]}
  (println "Compiling...")
  (.mkdirs (io/file "target/classes"))
  (Thread/sleep 500)
  (println "✓ Compiled"))

(deftask test {:doc "Run tests" :deps [:compile]}
  (println "Running tests...")
  (Thread/sleep 300)
  (println "✓ 42 tests passed"))

(deftask jar {:doc "Build JAR" :deps [:compile :test]}
  (println "Packaging JAR...")
  (Thread/sleep 200)
  (println "✓ target/app.jar"))

(deftask deploy {:doc "Deploy to server" :deps [:jar]}
  (println "Deploying...")
  (println "✓ Deployed to production"))
```

## Dependency Resolution (Topological Sort)

```clojure
(defn resolve-deps [task-name all-tasks]
  (let [visited (atom #{})
        order (atom [])]
    (letfn [(visit [name]
              (when-not (@visited name)
                (swap! visited conj name)
                (let [task (get all-tasks name)]
                  (when-not task
                    (throw (ex-info (str "Unknown task: " name) {:task name})))
                  (doseq [dep (:deps task)]
                    (visit dep))
                  (swap! order conj name))))]
      (visit task-name)
      @order)))
```

```clojure
(resolve-deps :deploy @tasks)
;=> [:clean :compile :test :jar :deploy]
```

## Running Tasks

```clojure
(defn run-task! [task-name]
  (let [execution-order (resolve-deps task-name @tasks)
        start (System/currentTimeMillis)]
    (printf "Running: %s (deps: %s)%n" task-name (str/join " → " execution-order))
    (println "─────────────────────")
    (doseq [t execution-order]
      (let [task (get @tasks t)
            t-start (System/currentTimeMillis)]
        ((:fn task))
        (printf "  [%s: %dms]%n" (name t) (- (System/currentTimeMillis) t-start))))
    (println "─────────────────────")
    (printf "Done in %dms%n" (- (System/currentTimeMillis) start))))
```

## Incremental Builds (File Timestamps)

```clojure
(defn newer-than? [source target]
  (let [src-file (io/file source)
        tgt-file (io/file target)]
    (or (not (.exists tgt-file))
        (> (.lastModified src-file) (.lastModified tgt-file)))))

(defn needs-rebuild? [sources target]
  (some #(newer-than? % target) sources))

(deftask compile-incremental
  {:doc "Only recompile changed files" :deps [:clean]}
  (let [sources (filter #(str/ends-with? (.getName %) ".clj")
                        (file-seq (io/file "src")))
        changed (filter #(newer-than? % "target/.compiled") sources)]
    (if (empty? changed)
      (println "✓ Nothing to compile")
      (do
        (printf "Compiling %d files...%n" (count changed))
        (doseq [f changed] (println "  " (.getPath f)))
        (spit "target/.compiled" (str (System/currentTimeMillis)))
        (println "✓ Done")))))
```

## Parallel Task Execution

```clojure
(defn parallel-tasks [task-names]
  (let [futures (mapv #(future (run-task! %)) task-names)]
    (mapv deref futures)))
```

## CLI Interface

```clojure
(defn list-tasks []
  (println "Available tasks:")
  (doseq [[name {:keys [doc deps]}] (sort @tasks)]
    (printf "  %-15s %s%s%n" (clojure.core/name name) doc
            (if (seq deps) (str " [deps: " (str/join ", " (map clojure.core/name deps)) "]") ""))))

(defn -main [& args]
  (if (empty? args)
    (list-tasks)
    (let [task (keyword (first args))]
      (if (contains? @tasks task)
        (run-task! task)
        (println "Unknown task:" (first args) "\nRun without args to see available tasks.")))))
```

## Key Takeaways

- `deftask` macro turns task definition into data stored in an atom
- Topological sort resolves dependency order (no task runs before its deps)
- File timestamps enable incremental builds (skip unchanged files)
- `future` + `deref` for parallel independent tasks
- The entire build system is ~80 lines — Clojure's conciseness at work
