# Chapter 27: Practical — An MP3 Database

[prev: Parsing Binary Files](chapter-26-binary-parsing.md) | [next: A Web App](chapter-28-web-app.md)

## What We're Building

Scan a music directory, extract ID3 metadata from MP3 files, store it in an in-memory database, and provide search/filter/statistics. Mirrors PCL chapters 25+27.

## Scanning Files

```clojure
(ns mp3db.core
  (:require [clojure.java.io :as io]
            [clojure.string :as str]
            [mp3db.id3 :refer [parse-id3]]))

(defn mp3-files [dir]
  (->> (file-seq (io/file dir))
       (filter #(.isFile %))
       (filter #(str/ends-with? (str/lower-case (.getName %)) ".mp3"))))

(defn scan-directory [dir]
  (let [files (mp3-files dir)]
    (printf "Found %d MP3 files%n" (count files))
    (mapv (fn [f]
            (try
              (let [tags (parse-id3 (.getPath f))
                    frames (into {} (map (juxt :id :data) (:frames tags)))]
                {:file (.getPath f)
                 :size (.length f)
                 :title (get frames "TIT2" "Unknown")
                 :artist (get frames "TPE1" "Unknown")
                 :album (get frames "TALB" "Unknown")
                 :year (get frames "TDRC" "")
                 :genre (get frames "TCON" "")
                 :track (get frames "TRCK" "")})
              (catch Exception e
                {:file (.getPath f) :error (.getMessage e)})))
          files)))
```

## The Database

```clojure
(def db (atom {:tracks [] :index {}}))

(defn build-index [tracks]
  {:by-artist (group-by :artist tracks)
   :by-album (group-by :album tracks)
   :by-genre (group-by :genre tracks)
   :by-year (group-by :year tracks)})

(defn load-db! [dir]
  (let [tracks (remove :error (scan-directory dir))
        index (build-index tracks)]
    (reset! db {:tracks tracks :index index})
    (printf "Loaded %d tracks%n" (count tracks))))
```

## Querying

```clojure
(defn search [query]
  (let [q (str/lower-case query)]
    (filter (fn [{:keys [title artist album]}]
              (or (str/includes? (str/lower-case title) q)
                  (str/includes? (str/lower-case artist) q)
                  (str/includes? (str/lower-case album) q)))
            (:tracks @db))))

(defn by-artist [artist]
  (get-in @db [:index :by-artist artist] []))

(defn by-album [album]
  (get-in @db [:index :by-album album] []))

(defn artists []
  (sort (keys (get-in @db [:index :by-artist]))))

(defn albums []
  (sort (keys (get-in @db [:index :by-album]))))

(defn albums-by [artist]
  (->> (by-artist artist)
       (map :album)
       distinct
       sort))
```

## Statistics

```clojure
(defn stats []
  (let [tracks (:tracks @db)]
    {:total-tracks (count tracks)
     :total-size (reduce + (map :size tracks))
     :artists (count (distinct (map :artist tracks)))
     :albums (count (distinct (map :album tracks)))
     :genres (frequencies (map :genre tracks))
     :decades (->> tracks
                   (map #(when (seq (:year %))
                           (str (subs (:year %) 0 3) "0s")))
                   (remove nil?)
                   frequencies
                   (sort-by key))}))

(defn top-artists [n]
  (->> (:tracks @db)
       (group-by :artist)
       (map (fn [[artist tracks]] {:artist artist :count (count tracks)}))
       (sort-by :count >)
       (take n)))
```

## CLI Interface

```clojure
(defn print-tracks [tracks]
  (doseq [{:keys [title artist album]} tracks]
    (printf "  %-30s %-25s %s%n" title artist album)))

(defn -main [& args]
  (let [dir (or (first args) ".")]
    (load-db! dir)
    (println)
    (let [{:keys [total-tracks artists albums]} (stats)]
      (printf "📊 %d tracks, %d artists, %d albums%n%n" total-tracks artists albums))
    (println "Top 5 Artists:")
    (doseq [{:keys [artist count]} (top-artists 5)]
      (printf "  %-30s %d tracks%n" artist count))
    (println "\nType a search query:")
    (loop []
      (print "> ") (flush)
      (when-let [q (read-line)]
        (if (= q "quit")
          (println "Bye!")
          (do (print-tracks (take 20 (search q)))
              (recur)))))))
```

## Persistence with EDN

```clojure
(defn save-db! [filename]
  (spit filename (pr-str (:tracks @db))))

(defn load-from-cache! [filename]
  (when (.exists (io/file filename))
    (let [tracks (read-string (slurp filename))]
      (reset! db {:tracks tracks :index (build-index tracks)})
      true)))
```

## Key Takeaways

- `file-seq` for recursive directory traversal
- `group-by` creates instant indexes over any field
- `frequencies` for counting occurrences (genre distribution, decades)
- Atom holds the entire "database" — indexed maps in memory
- Combine binary parsing (chapter 26) with data processing (chapter 8)
- EDN serialization for caching parsed metadata
