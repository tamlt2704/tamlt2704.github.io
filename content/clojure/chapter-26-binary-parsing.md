# Chapter 26: Practical — Parsing Binary Files

[prev: core.async Patterns](chapter-25-async.md) | [next: An MP3 Database](chapter-27-mp3-database.md)

## What We're Building

A binary file parser that reads structured binary formats (like PNG headers, ZIP files, ID3 tags). Mirrors _Practical Common Lisp_ chapter 24.

## Reading Bytes

```clojure
(ns binary.core
  (:require [clojure.java.io :as io])
  (:import [java.io RandomAccessFile DataInputStream FileInputStream]
           [java.nio ByteBuffer ByteOrder]))

(defn read-bytes [file offset length]
  (with-open [raf (RandomAccessFile. file "r")]
    (.seek raf offset)
    (let [buf (byte-array length)]
      (.readFully raf buf)
      buf)))

(defn bytes->int [bytes & {:keys [order] :or {order :big}}]
  (let [bb (ByteBuffer/wrap bytes)]
    (when (= order :little) (.order bb ByteOrder/LITTLE_ENDIAN))
    (case (count bytes)
      1 (.get bb)
      2 (.getShort bb)
      4 (.getInt bb)
      8 (.getLong bb))))

(defn bytes->string [bytes]
  (String. bytes "UTF-8"))
```

## Declarative Binary Format DSL

```clojure
(defn read-field [stream {:keys [type length]}]
  (let [buf (byte-array length)]
    (.readFully stream buf)
    (case type
      :bytes buf
      :string (String. (byte-array (take-while #(not= % 0) buf)) "ISO-8859-1")
      :uint8 (bit-and 0xFF (aget buf 0))
      :uint16 (bytes->int buf)
      :uint32 (bytes->int buf)
      :uint16-le (bytes->int buf :order :little)
      :uint32-le (bytes->int buf :order :little))))

(defn read-struct [stream fields]
  (reduce (fn [acc {:keys [name] :as field}]
            (assoc acc name (read-field stream field)))
          {}
          fields))
```

## PNG Header Parser

```clojure
(def png-signature [137 80 78 71 13 10 26 10])

(def ihdr-fields
  [{:name :width    :type :uint32 :length 4}
   {:name :height   :type :uint32 :length 4}
   {:name :bit-depth :type :uint8 :length 1}
   {:name :color-type :type :uint8 :length 1}
   {:name :compression :type :uint8 :length 1}
   {:name :filter :type :uint8 :length 1}
   {:name :interlace :type :uint8 :length 1}])

(defn parse-png [file]
  (with-open [stream (DataInputStream. (FileInputStream. file))]
    ;; Check signature
    (let [sig (byte-array 8)]
      (.readFully stream sig)
      (assert (= (vec sig) (mapv byte png-signature)) "Not a PNG file"))
    ;; Read IHDR chunk
    (let [chunk-length (.readInt stream)
          chunk-type (let [b (byte-array 4)] (.readFully stream b) (String. b))]
      (assert (= chunk-type "IHDR") "First chunk must be IHDR")
      (read-struct stream ihdr-fields))))

(parse-png "test.png")
;=> {:width 1920, :height 1080, :bit-depth 8, :color-type 6, ...}
```

## ID3v2 Tag Parser (MP3 Metadata)

```clojure
(defn parse-syncsafe-int [bytes]
  (reduce (fn [acc b] (+ (bit-shift-left acc 7) (bit-and b 0x7F)))
          0 bytes))

(def id3-header-fields
  [{:name :magic   :type :string :length 3}
   {:name :version :type :bytes :length 2}
   {:name :flags   :type :uint8 :length 1}
   {:name :size    :type :bytes :length 4}])

(defn parse-id3-frame [stream]
  (let [frame-id (let [b (byte-array 4)] (.readFully stream b) (String. b))
        size (.readInt stream)
        _flags (byte-array 2)]
    (.readFully stream _flags)
    (when (pos? size)
      (let [data (byte-array size)]
        (.readFully stream data)
        {:id frame-id
         :data (String. data 1 (dec size) "UTF-8")}))))

(defn parse-id3 [file]
  (with-open [stream (DataInputStream. (FileInputStream. file))]
    (let [header (read-struct stream id3-header-fields)
          tag-size (parse-syncsafe-int (:size header))]
      (assert (= (:magic header) "ID3") "No ID3 tag found")
      (loop [frames [] bytes-read 0]
        (if (>= bytes-read (- tag-size 10))
          (assoc header :frames frames)
          (if-let [frame (parse-id3-frame stream)]
            (recur (conj frames frame) (+ bytes-read 10 (count (:data frame))))
            (assoc header :frames frames)))))))
```

## ZIP File Reader

```clojure
(def zip-local-header-fields
  [{:name :signature :type :uint32-le :length 4}
   {:name :version   :type :uint16-le :length 2}
   {:name :flags     :type :uint16-le :length 2}
   {:name :method    :type :uint16-le :length 2}
   {:name :mod-time  :type :uint16-le :length 2}
   {:name :mod-date  :type :uint16-le :length 2}
   {:name :crc32     :type :uint32-le :length 4}
   {:name :compressed-size   :type :uint32-le :length 4}
   {:name :uncompressed-size :type :uint32-le :length 4}
   {:name :name-length :type :uint16-le :length 2}
   {:name :extra-length :type :uint16-le :length 2}])

(defn list-zip-entries [file]
  (with-open [stream (DataInputStream. (FileInputStream. file))]
    (loop [entries []]
      (let [header (read-struct stream zip-local-header-fields)]
        (if (not= (:signature header) 0x04034b50)
          entries
          (let [name-buf (byte-array (:name-length header))
                _ (.readFully stream name-buf)
                _ (.skipBytes stream (:extra-length header))
                _ (.skipBytes stream (:compressed-size header))
                entry-name (String. name-buf)]
            (recur (conj entries (assoc header :filename entry-name)))))))))
```

## Key Takeaways

- `DataInputStream` for sequential reads, `RandomAccessFile` for seeking
- `ByteBuffer` handles endianness (big-endian vs little-endian)
- Declarative field specs (`{:name :x :type :uint32 :length 4}`) make formats readable
- `read-struct` pattern: reduce over field specs, building a map
- Real binary formats (PNG, ID3, ZIP) are just sequences of typed fields
