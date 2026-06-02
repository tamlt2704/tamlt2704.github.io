# Chapter 18: Practical — A Spam Filter

[prev: Spec](chapter-17-spec.md) | [next: A Web Scraper](chapter-19-web-scraper.md)

## What We're Building

A Naive Bayes spam classifier in pure Clojure. Train it on labeled messages, then classify new ones as spam or ham. Mirrors chapter 23 of _Practical Common Lisp_.

## The Math (Simplified)

For each word, track how often it appears in spam vs ham. To classify a message, multiply the probabilities of its words being spam. The side with higher combined probability wins.

## The Classifier

```clojure
(ns spam.core
  (:require [clojure.string :as str]))

(defn tokenize [text]
  (->> (str/lower-case text)
       (re-seq #"[a-z]{3,}")
       frequencies))

(defn make-classifier []
  {:spam-count (atom 0)
   :ham-count (atom 0)
   :word-stats (atom {})})  ;; word -> {:spam n :ham n}

(defn train! [classifier text label]
  (let [{:keys [spam-count ham-count word-stats]} classifier
        tokens (tokenize text)]
    (case label
      :spam (swap! spam-count inc)
      :ham (swap! ham-count inc))
    (doseq [[word _count] tokens]
      (swap! word-stats update word
             (fn [stats]
               (let [s (or stats {:spam 0 :ham 0})]
                 (update s label + 1)))))))
```

## Scoring

```clojure
(defn word-spam-probability [{:keys [spam-count ham-count word-stats]} word]
  (let [stats (get @word-stats word {:spam 0 :ham 0})
        total-spam @spam-count
        total-ham @ham-count]
    (if (zero? (+ (:spam stats) (:ham stats)))
      0.5  ;; unknown word — neutral
      (let [spam-freq (/ (double (:spam stats)) (max 1 total-spam))
            ham-freq (/ (double (:ham stats)) (max 1 total-ham))]
        (/ spam-freq (+ spam-freq ham-freq))))))

(defn classify [classifier text]
  (let [tokens (keys (tokenize text))
        probs (map #(word-spam-probability classifier %) tokens)
        ;; Use log probabilities to avoid underflow
        spam-score (reduce + (map #(Math/log %) probs))
        ham-score (reduce + (map #(Math/log (- 1.0 %)) probs))]
    (if (> spam-score ham-score) :spam :ham)))

(defn spam-score [classifier text]
  (let [tokens (keys (tokenize text))
        probs (map #(word-spam-probability classifier %) tokens)]
    (if (empty? probs) 0.5
      (let [prod (reduce * probs)
            comp-prod (reduce * (map #(- 1.0 %) probs))]
        (/ prod (+ prod comp-prod))))))
```

## Training

```clojure
(def training-data
  [{:text "Buy cheap viagra now! Special offer!" :label :spam}
   {:text "Congratulations you won $1000000! Click here" :label :spam}
   {:text "Make money fast working from home" :label :spam}
   {:text "Free pills and discount pharmacy" :label :spam}
   {:text "Nigerian prince needs your bank details" :label :spam}
   {:text "Hey, are we still meeting for lunch tomorrow?" :label :ham}
   {:text "The project deadline has been moved to Friday" :label :ham}
   {:text "Can you review my pull request when you get a chance?" :label :ham}
   {:text "Reminder: team standup at 10am" :label :ham}
   {:text "I've attached the quarterly report for your review" :label :ham}])

(def classifier (make-classifier))

(doseq [{:keys [text label]} training-data]
  (train! classifier text label))
```

## Classifying New Messages

```clojure
(classify classifier "Free money! Click now for amazing offer!")
;=> :spam

(classify classifier "Hey, can we reschedule our meeting to 3pm?")
;=> :ham

(spam-score classifier "Buy discount pills cheap!")
;=> 0.92 (highly spammy)

(spam-score classifier "Please review the attached document")
;=> 0.08 (very likely ham)
```

## Training from Files

```clojure
(defn load-training-dir [classifier dir label]
  (let [files (file-seq (clojure.java.io/file dir))]
    (doseq [f files
            :when (.isFile f)]
      (train! classifier (slurp f) label))))

(defn train-from-corpus! [classifier spam-dir ham-dir]
  (load-training-dir classifier spam-dir :spam)
  (load-training-dir classifier ham-dir :ham)
  (printf "Trained on %d spam, %d ham messages%n"
          @(:spam-count classifier) @(:ham-count classifier)))
```

## Evaluation

```clojure
(defn evaluate [classifier test-data]
  (let [results (map (fn [{:keys [text label]}]
                       {:expected label
                        :predicted (classify classifier text)
                        :correct? (= label (classify classifier text))})
                     test-data)]
    {:accuracy (double (/ (count (filter :correct? results)) (count results)))
     :confusion {:true-pos (count (filter #(and (= :spam (:expected %)) (= :spam (:predicted %))) results))
                 :false-pos (count (filter #(and (= :ham (:expected %)) (= :spam (:predicted %))) results))
                 :true-neg (count (filter #(and (= :ham (:expected %)) (= :ham (:predicted %))) results))
                 :false-neg (count (filter #(and (= :spam (:expected %)) (= :ham (:predicted %))) results))}}))
```

## Persistence

```clojure
(defn save-classifier! [classifier filename]
  (spit filename (pr-str {:spam-count @(:spam-count classifier)
                          :ham-count @(:ham-count classifier)
                          :word-stats @(:word-stats classifier)})))

(defn load-classifier! [classifier filename]
  (let [data (read-string (slurp filename))]
    (reset! (:spam-count classifier) (:spam-count data))
    (reset! (:ham-count classifier) (:ham-count data))
    (reset! (:word-stats classifier) (:word-stats data))))
```

## What You Learned

| Concept        | Application                                   |
| -------------- | --------------------------------------------- |
| Atoms          | Mutable training state                        |
| `frequencies`  | Tokenization (word counting)                  |
| `reduce`       | Computing combined probabilities              |
| Maps           | Word statistics storage                       |
| Lazy sequences | Processing file collections                   |
| Pure functions | `classify`, `spam-score` are pure (read-only) |
| I/O            | File-based training corpus                    |
