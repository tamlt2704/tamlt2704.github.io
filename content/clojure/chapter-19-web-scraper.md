# Chapter 19: Practical — A Web Scraper

[prev: A Spam Filter](chapter-18-spam-filter.md) | [next: A Chat Server](chapter-20-chat-server.md)

## What We're Building

A concurrent web scraper that fetches pages, extracts data, respects rate limits, and handles errors gracefully.

## Dependencies

```clojure
{:deps {org.clojure/clojure {:mvn/version "1.12.0"}
        org.clojure/core.async {:mvn/version "1.6.681"}
        clj-http/clj-http {:mvn/version "3.13.0"}
        hickory/hickory {:mvn/version "0.7.4"}}}
```

## Fetching Pages

```clojure
(ns scraper.core
  (:require [clj-http.client :as http]
            [hickory.core :as h]
            [hickory.select :as s]
            [clojure.core.async :as async :refer [go chan <! >! <!!]]
            [clojure.string :as str]))

(defn fetch [url]
  (try
    {:url url
     :body (:body (http/get url {:headers {"User-Agent" "ClojureScraper/1.0"}
                                  :socket-timeout 10000
                                  :connection-timeout 5000}))}
    (catch Exception e
      {:url url :error (.getMessage e)})))
```

## Parsing HTML

```clojure
(defn parse-html [html]
  (-> html h/parse h/as-hickory))

(defn extract-links [parsed base-url]
  (->> (s/select (s/tag :a) parsed)
       (map #(get-in % [:attrs :href]))
       (filter some?)
       (map #(if (str/starts-with? % "http") % (str base-url %)))
       distinct))

(defn extract-text [parsed selector]
  (->> (s/select selector parsed)
       (map (fn [el] (apply str (filter string? (tree-seq map? :content el)))))
       (map str/trim)
       (remove empty?)))
```

## Rate-Limited Concurrent Fetcher

```clojure
(defn scrape-urls [urls {:keys [concurrency delay-ms] :or {concurrency 5 delay-ms 1000}}]
  (let [input (chan (count urls))
        output (chan (count urls))]
    ;; Feed URLs
    (doseq [url urls] (async/>!! input url))
    (async/close! input)

    ;; Workers
    (dotimes [_ concurrency]
      (go (loop []
            (when-let [url (<! input)]
              (let [result (fetch url)]
                (>! output result))
              (async/<! (async/timeout delay-ms))
              (recur)))))

    ;; Collect results
    (loop [results [] remaining (count urls)]
      (if (zero? remaining)
        results
        (recur (conj results (<!! output)) (dec remaining))))))
```

## Full Scraping Pipeline

```clojure
(defn scrape-product-page [url]
  (let [{:keys [body error]} (fetch url)]
    (when-not error
      (let [parsed (parse-html body)]
        {:url url
         :title (first (extract-text parsed (s/class "product-title")))
         :price (first (extract-text parsed (s/class "price")))
         :description (first (extract-text parsed (s/tag :p)))}))))

(defn crawl [seed-url max-pages]
  (loop [visited #{}
         queue [seed-url]
         results []]
    (if (or (empty? queue) (>= (count results) max-pages))
      results
      (let [url (first queue)]
        (if (visited url)
          (recur visited (rest queue) results)
          (let [{:keys [body error] :as result} (fetch url)]
            (Thread/sleep 500)
            (if error
              (recur (conj visited url) (rest queue) results)
              (let [parsed (parse-html body)
                    links (extract-links parsed url)]
                (recur (conj visited url)
                       (into (vec (rest queue)) (remove visited links))
                       (conj results result))))))))))
```

## Saving Results

```clojure
(defn results->csv [results filename]
  (with-open [w (clojure.java.io/writer filename)]
    (.write w "url,title,price\n")
    (doseq [{:keys [url title price]} results]
      (.write w (str (pr-str url) "," (pr-str title) "," (pr-str price) "\n")))))
```

## Key Takeaways

- `clj-http` for HTTP requests with timeouts and headers
- Hickory for HTML parsing with CSS selector-like queries
- core.async channels for bounded concurrency (no thread explosion)
- Rate limiting via `async/timeout` between requests
- Crawl loop with visited set prevents infinite cycles
