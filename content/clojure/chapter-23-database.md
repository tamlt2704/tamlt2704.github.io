# Chapter 23: Practical — A Database Layer

[prev: Java Interop](chapter-22-java-interop.md) | [next: ClojureScript](chapter-24-clojurescript.md)

## What We're Building

A complete database access layer: connection pooling, queries, migrations, and transactions using `next.jdbc` — the standard Clojure database library.

## Setup

```clojure
{:deps {org.clojure/clojure {:mvn/version "1.12.0"}
        com.github.seancorfield/next.jdbc {:mvn/version "1.3.939"}
        com.zaxxer/HikariCP {:mvn/version "5.1.0"}
        org.postgresql/postgresql {:mvn/version "42.7.4"}}}
```

## Connection Pool

```clojure
(ns myapp.db
  (:require [next.jdbc :as jdbc]
            [next.jdbc.result-set :as rs]
            [next.jdbc.sql :as sql]))

(def db-spec {:dbtype "postgresql"
              :host "localhost"
              :port 5432
              :dbname "myapp"
              :user "dev"
              :password "dev123"})

(def datasource
  (jdbc/get-datasource
    (assoc db-spec
      :maximumPoolSize 10
      :connectionTimeout 30000)))
```

## Basic Queries

```clojure
;; Execute raw SQL
(jdbc/execute! datasource ["SELECT * FROM users WHERE active = ?" true])
;=> [{:users/id 1, :users/name "Alice", :users/active true} ...]

;; Single result
(jdbc/execute-one! datasource ["SELECT * FROM users WHERE id = ?" 42])
;=> {:users/id 42, :users/name "Alice", ...}

;; With custom row builder (unqualified keys)
(jdbc/execute! datasource ["SELECT * FROM users"]
  {:builder-fn rs/as-unqualified-maps})
;=> [{:id 1, :name "Alice", :active true} ...]
```

## CRUD Operations

```clojure
;; Insert
(sql/insert! datasource :users {:name "Bob" :email "bob@test.com" :active true})
;=> {:users/id 5}

;; Insert multiple
(sql/insert-multi! datasource :users [:name :email]
  [["Alice" "alice@t.com"] ["Bob" "bob@t.com"]])

;; Update
(sql/update! datasource :users {:active false} {:id 42})

;; Delete
(sql/delete! datasource :users {:id 42})

;; Find by keys
(sql/find-by-keys datasource :users {:active true})
;=> [{:id 1, :name "Alice"} ...]
```

## Transactions

```clojure
(jdbc/with-transaction [tx datasource]
  (let [user (sql/insert! tx :users {:name "Alice" :email "a@b.com"})
        user-id (:users/id user)]
    (sql/insert! tx :profiles {:user_id user-id :bio "Hello!"})
    (sql/insert! tx :settings {:user_id user-id :theme "dark"})
    user-id))
;; All three inserts succeed or all fail
```

## Building a Repository

```clojure
(ns myapp.repo.users
  (:require [next.jdbc :as jdbc]
            [next.jdbc.sql :as sql]
            [next.jdbc.result-set :as rs]))

(def opts {:builder-fn rs/as-unqualified-maps})

(defn find-all [ds]
  (sql/find-by-keys ds :users :all opts))

(defn find-by-id [ds id]
  (sql/get-by-id ds :users id opts))

(defn find-by-email [ds email]
  (first (sql/find-by-keys ds :users {:email email} opts)))

(defn create! [ds user]
  (sql/insert! ds :users user opts))

(defn update! [ds id changes]
  (sql/update! ds :users changes {:id id} opts))

(defn delete! [ds id]
  (sql/delete! ds :users {:id id}))

(defn search [ds query]
  (jdbc/execute! ds
    ["SELECT * FROM users WHERE name ILIKE ? OR email ILIKE ?"
     (str "%" query "%") (str "%" query "%")]
    opts))
```

## Migrations

```clojure
(ns myapp.migrations
  (:require [next.jdbc :as jdbc]))

(def migrations
  [{:id 1
    :up "CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE, active BOOLEAN DEFAULT true, created_at TIMESTAMP DEFAULT NOW())"
    :down "DROP TABLE users"}
   {:id 2
    :up "CREATE TABLE posts (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), title TEXT, body TEXT, created_at TIMESTAMP DEFAULT NOW())"
    :down "DROP TABLE posts"}
   {:id 3
    :up "CREATE INDEX idx_posts_user_id ON posts(user_id)"
    :down "DROP INDEX idx_posts_user_id"}])

(defn ensure-migrations-table! [ds]
  (jdbc/execute! ds ["CREATE TABLE IF NOT EXISTS schema_migrations (id INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT NOW())"]))

(defn applied-migrations [ds]
  (set (map :id (jdbc/execute! ds ["SELECT id FROM schema_migrations"]))))

(defn migrate! [ds]
  (ensure-migrations-table! ds)
  (let [applied (applied-migrations ds)]
    (doseq [{:keys [id up]} migrations
            :when (not (applied id))]
      (println "Applying migration" id)
      (jdbc/with-transaction [tx ds]
        (jdbc/execute! tx [up])
        (jdbc/execute! tx ["INSERT INTO schema_migrations (id) VALUES (?)" id])))))

(defn rollback! [ds]
  (let [applied (applied-migrations ds)
        last-id (apply max applied)
        {:keys [down]} (first (filter #(= (:id %) last-id) migrations))]
    (jdbc/with-transaction [tx ds]
      (jdbc/execute! tx [down])
      (jdbc/execute! tx ["DELETE FROM schema_migrations WHERE id = ?" last-id]))
    (println "Rolled back migration" last-id)))
```

## Query Builder Pattern

```clojure
(defn build-where [conditions]
  (when (seq conditions)
    (let [clauses (map (fn [[k v]] (str (name k) " = ?")) conditions)
          values (vals conditions)]
      {:where (str "WHERE " (clojure.string/join " AND " clauses))
       :params (vec values)})))

(defn find-users [ds & {:keys [active name limit offset] :as opts}]
  (let [conditions (select-keys opts [:active :name])
        {:keys [where params]} (build-where conditions)
        sql (str "SELECT * FROM users " (or where "")
                 (when limit (str " LIMIT " limit))
                 (when offset (str " OFFSET " offset)))]
    (jdbc/execute! ds (into [sql] params)
      {:builder-fn rs/as-unqualified-maps})))
```

## Key Takeaways

- `next.jdbc` is minimal: execute SQL, get maps back
- HikariCP for connection pooling (production must-have)
- Transactions with `jdbc/with-transaction` — automatic rollback on exception
- Migrations as data (vector of maps with `:up`/`:down` SQL)
- Repository pattern: one namespace per entity with CRUD functions
- Qualified keys (`:users/name`) or unqualified (`:name`) — your choice
