# Chapter 8: Practical — A Data Pipeline

[prev: Sequences and Laziness](chapter-07-sequences.md) | [next: Namespaces](chapter-09-namespaces.md)

## What We're Building

A data processing pipeline that reads CSV files, transforms records, aggregates statistics, and outputs results — using everything from chapters 5-7.

## Project Setup

`deps.edn`:

```clojure
{:deps {org.clojure/clojure {:mvn/version "1.12.0"}
        org.clojure/data.csv {:mvn/version "1.1.0"}}
 :paths ["src" "resources"]}
```

Sample `resources/sales.csv`:

```
date,product,category,quantity,price,region
2024-01-15,Widget A,Electronics,5,29.99,North
2024-01-15,Gadget B,Electronics,3,49.99,South
2024-01-15,Book C,Books,10,14.99,North
2024-01-16,Widget A,Electronics,2,29.99,East
2024-01-16,Snack D,Food,20,3.99,South
2024-01-16,Book C,Books,7,14.99,West
2024-01-17,Gadget B,Electronics,1,49.99,North
2024-01-17,Snack D,Food,15,3.99,East
```

## Reading CSV

```clojure
(ns pipeline.core
  (:require [clojure.data.csv :as csv]
            [clojure.java.io :as io]
            [clojure.string :as str]))

(defn read-csv [filename]
  (with-open [reader (io/reader filename)]
    (let [data (csv/read-csv reader)
          headers (map keyword (first data))
          rows (rest data)]
      (mapv #(zipmap headers %) rows))))
```

```clojure
(read-csv "resources/sales.csv")
;=> [{:date "2024-01-15", :product "Widget A", :category "Electronics", :quantity "5", :price "29.99", :region "North"}
;    ...]
```

## Parsing and Cleaning

```clojure
(defn parse-record [record]
  (-> record
      (update :quantity parse-long)
      (update :price parse-double)
      (update :date java.time.LocalDate/parse)
      (assoc :revenue (* (parse-long (:quantity record))
                         (parse-double (:price record))))))

(defn parse-all [records]
  (mapv parse-record records))
```

## Filtering

```clojure
(defn filter-by-category [category records]
  (filter #(= (:category %) category) records))

(defn filter-by-date-range [start end records]
  (filter (fn [{:keys [date]}]
            (and (not (.isBefore date start))
                 (not (.isAfter date end))))
          records))

(defn high-value-sales [min-revenue records]
  (filter #(>= (:revenue %) min-revenue) records))
```

## Aggregation

```clojure
(defn total-revenue [records]
  (reduce + (map :revenue records)))

(defn revenue-by-category [records]
  (->> records
       (group-by :category)
       (map (fn [[cat recs]]
              {:category cat
               :total-revenue (reduce + (map :revenue recs))
               :total-quantity (reduce + (map :quantity recs))
               :order-count (count recs)}))
       (sort-by :total-revenue >)))

(defn revenue-by-region [records]
  (->> records
       (group-by :region)
       (map (fn [[region recs]]
              {:region region
               :revenue (reduce + (map :revenue recs))
               :items (reduce + (map :quantity recs))}))
       (sort-by :revenue >)))

(defn top-products [n records]
  (->> records
       (group-by :product)
       (map (fn [[product recs]]
              {:product product
               :total-revenue (reduce + (map :revenue recs))}))
       (sort-by :total-revenue >)
       (take n)))
```

## The Pipeline (Composing It All)

```clojure
(defn run-pipeline [filename]
  (let [raw (read-csv filename)
        records (parse-all raw)]
    {:summary {:total-records (count records)
               :total-revenue (total-revenue records)
               :date-range [(apply min (map :date records))
                            (apply max (map :date records))]}
     :by-category (revenue-by-category records)
     :by-region (revenue-by-region records)
     :top-3-products (top-products 3 records)}))
```

```clojure
(run-pipeline "resources/sales.csv")
;=> {:summary {:total-records 8, :total-revenue 769.12, ...}
;    :by-category [{:category "Electronics", :total-revenue 559.89, ...} ...]
;    :by-region [{:region "North", :revenue 319.84, ...} ...]
;    :top-3-products [{:product "Widget A", :total-revenue 209.93} ...]}
```

## Using Transducers for Large Files

For files with millions of rows, avoid intermediate sequences:

```clojure
(defn process-large-file [filename]
  (with-open [reader (io/reader filename)]
    (let [lines (csv/read-csv reader)
          headers (map keyword (first lines))
          xf (comp
               (map #(zipmap headers %))
               (map parse-record)
               (filter #(= (:category %) "Electronics")))]
      (transduce xf
                 (fn
                   ([] {:revenue 0 :count 0})
                   ([acc] acc)
                   ([acc record]
                    (-> acc
                        (update :revenue + (:revenue record))
                        (update :count inc))))
                 (rest lines)))))
```

## Writing Output

```clojure
(defn write-csv [filename headers records]
  (with-open [writer (io/writer filename)]
    (csv/write-csv writer
      (cons (map name headers)
            (map (fn [r] (map #(str (get r %)) headers)) records)))))

(defn report->csv [result filename]
  (write-csv filename
    [:category :total-revenue :total-quantity :order-count]
    (:by-category result)))
```

## Putting It Together

```clojure
(defn -main [& args]
  (let [input (or (first args) "resources/sales.csv")
        result (run-pipeline input)]
    (println "=== Sales Report ===")
    (printf "Records: %d | Revenue: $%.2f%n"
            (get-in result [:summary :total-records])
            (get-in result [:summary :total-revenue]))
    (println "\nBy Category:")
    (doseq [{:keys [category total-revenue order-count]} (:by-category result)]
      (printf "  %-15s $%8.2f  (%d orders)%n" category total-revenue order-count))
    (println "\nTop Products:")
    (doseq [{:keys [product total-revenue]} (:top-3-products result)]
      (printf "  %-15s $%.2f%n" product total-revenue))
    (report->csv result "output/report.csv")
    (println "\n✓ CSV written to output/report.csv")))
```

## Run It

```bash
clj -M -m pipeline.core resources/sales.csv
```

## What You Learned

| Concept         | Used For                                     |
| --------------- | -------------------------------------------- |
| `group-by`      | Aggregating by category/region               |
| `reduce`        | Summing, counting, accumulating              |
| `->>` threading | Readable data pipelines                      |
| Transducers     | Single-pass processing of large data         |
| `with-open`     | Safe resource management                     |
| `zipmap`        | Converting headers + row → map               |
| Immutable data  | Each step produces new data, no side effects |

## Exercises

1. Add a `--filter` flag to filter by region from the command line
2. Add average order value per category
3. Add day-over-day growth percentage
4. Process multiple CSV files and merge results
