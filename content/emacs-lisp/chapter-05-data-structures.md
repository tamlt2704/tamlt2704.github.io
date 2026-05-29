# Chapter 5: Data Structures

[prev: Control Flow](chapter-04-control-flow.md) | [next: Buffers and Text](chapter-06-buffers-text.md)

## Lists

Lists are the fundamental data structure in Elisp, built from cons cells.

### cons, car, cdr

```elisp
(cons 1 2)          ;; => (1 . 2)  — a cons cell (dotted pair)
(cons 1 '(2 3))    ;; => (1 2 3)  — prepend to list
(car '(a b c))     ;; => a        — first element
(cdr '(a b c))     ;; => (b c)    — rest of list
(cadr '(a b c))    ;; => b        — second element (car of cdr)
```

### Building and accessing lists

```elisp
(list 1 2 3)           ;; => (1 2 3)
(append '(1 2) '(3 4)) ;; => (1 2 3 4)
(nth 2 '(a b c d))     ;; => c (zero-indexed)
(length '(a b c))      ;; => 3
(last '(1 2 3))        ;; => (3)
(butlast '(1 2 3))     ;; => (1 2)
```

### Destructive vs non-destructive

```elisp
;; push modifies the variable (destructive)
(let ((lst '(2 3)))
  (push 1 lst)
  lst)
;; => (1 2 3)

;; nconc is destructive append
;; append creates a new list (non-destructive)
```

### Association lists (alists)

Alists are lists of key-value pairs:

```elisp
(setq my-alist '((name . "Alice")
                 (age . 30)
                 (city . "London")))

(assoc 'name my-alist)          ;; => (name . "Alice")
(cdr (assoc 'name my-alist))    ;; => "Alice"
(alist-get 'age my-alist)       ;; => 30

;; Add to alist
(push '(email . "a@b.com") my-alist)
```

### Property lists (plists)

Plists are flat lists alternating keys and values:

```elisp
(setq my-plist '(:name "Alice" :age 30 :city "London"))

(plist-get my-plist :name)   ;; => "Alice"
(plist-get my-plist :age)    ;; => 30
(plist-put my-plist :age 31) ;; => (:name "Alice" :age 31 :city "London")
```

### Alists vs Plists

- Alists: better for dynamic key-value stores, easy to shadow keys by prepending
- Plists: simpler syntax, commonly used for function keyword arguments and text properties
- Alists use `assoc`/`alist-get`, plists use `plist-get`/`plist-put`

## Strings

```elisp
(concat "hello" " " "world")   ;; => "hello world"
(format "Name: %s, Age: %d" "Alice" 30)  ;; => "Name: Alice, Age: 30"
(substring "hello world" 0 5)   ;; => "hello"
(length "hello")                ;; => 5
(upcase "hello")                ;; => "HELLO"
(downcase "HELLO")              ;; => "hello"
(string-trim "  hi  ")          ;; => "hi"
```

### String matching

```elisp
(string-match "wo" "hello world")  ;; => 6 (index of match)
(string-match "xyz" "hello world") ;; => nil

;; With capture groups
(string-match "\\(\\w+\\) \\(\\w+\\)" "hello world")
(match-string 1 "hello world")  ;; => "hello"
(match-string 2 "hello world")  ;; => "world"
```

### String replacement

```elisp
(replace-regexp-in-string "[0-9]+" "NUM" "abc123def456")
;; => "abcNUMdefNUM"

(replace-regexp-in-string "\\`\\s-+" "" "  hello")
;; => "hello" (trim leading whitespace)
```

### Split and join

```elisp
(split-string "a,b,c" ",")         ;; => ("a" "b" "c")
(string-join '("a" "b" "c") ", ")  ;; => "a, b, c"
```

## Hash Tables

Hash tables provide O(1) lookup:

```elisp
(setq ht (make-hash-table :test 'equal))

(puthash "name" "Alice" ht)
(puthash "age" 30 ht)

(gethash "name" ht)       ;; => "Alice"
(gethash "missing" ht)    ;; => nil
(gethash "missing" ht "default")  ;; => "default"

(remhash "age" ht)
(hash-table-count ht)     ;; => 1

;; Iterate
(maphash (lambda (k v)
           (message "%s: %s" k v))
         ht)
```

The `:test` argument determines key comparison:

- `eq` — symbol identity (default)
- `eql` — numbers by value, else identity
- `equal` — structural equality (use for strings)

## Vectors

Vectors are fixed-size, random-access arrays:

```elisp
[1 2 3]                    ;; => [1 2 3]
(make-vector 5 0)          ;; => [0 0 0 0 0]
(vector 'a 'b 'c)          ;; => [a b c]

(aref [10 20 30] 1)        ;; => 20 (access by index)
(let ((v (vector 1 2 3)))
  (aset v 1 99)
  v)
;; => [1 99 3] (set by index, destructive)

(length [1 2 3])            ;; => 3
```

Vectors vs lists:

- Vectors: O(1) access by index, fixed size
- Lists: O(n) access by index, dynamic size, easy to prepend

## Exercises

1. Write a function that takes an alist and returns a plist with the same data.
2. Use `string-match` and `match-string` to extract the domain from an email address.
3. Create a hash table mapping country codes to country names. Write a lookup function with a default value.
4. Write a function that takes a list of strings and returns the longest one.
5. Convert a vector to a list and back. (Hint: `append` and `vconcat`)
