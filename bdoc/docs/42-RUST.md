# Chapter 42: Rust — Systems Programming Without the Footguns

## What you'll learn

- Why Rust exists (memory safety without garbage collection)
- Ownership, borrowing, and lifetimes (the core innovation)
- Types: primitives, structs, enums, Option, Result
- Pattern matching and error handling
- Traits (like interfaces, but more powerful)
- Collections: Vec, HashMap, String
- Concurrency: fearless parallelism
- Build a CLI tool and a web API (Axum)
- Cargo: the build system and package manager

---

## PART 1: Why Rust?

## 42.1 The problem Rust solves

```
C/C++:  Fast + control, but:
        - Use-after-free (crash, security hole)
        - Double free (crash)
        - Buffer overflow (security hole)
        - Data races (undefined behaviour)
        - Null pointer dereference (crash)
        → Bugs that cost billions (CVEs, exploits, outages)

Java/Go: Safe (GC handles memory), but:
        - GC pauses (unpredictable latency)
        - Higher memory usage (GC overhead)
        - Less control (can't do OS/embedded/drivers)

Rust:   Fast + control + safe:
        - No garbage collector (deterministic cleanup)
        - No null (Option type instead)
        - No data races (compiler prevents them)
        - No use-after-free (ownership system prevents it)
        - Zero-cost abstractions (as fast as C)
        → Memory bugs caught at COMPILE TIME, not runtime
```

## 42.2 Setup

```bash
# Install Rust (rustup manages versions)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Verify
rustc --version    # compiler
cargo --version    # build tool + package manager

# Create a new project
cargo new hello-rust
cd hello-rust

# Run
cargo run          # compile + run
cargo build        # compile only
cargo test         # run tests
cargo build --release  # optimised build (slow compile, fast binary)
```

**Project structure:**
```
hello-rust/
├── Cargo.toml     ← dependencies + project metadata (like package.json)
├── Cargo.lock     ← exact dependency versions (like package-lock.json)
└── src/
    └── main.rs    ← entry point
```

## 42.3 Basics — variables, types, functions

```rust
fn main() {
    // Variables are immutable by default
    let x = 5;         // inferred type: i32
    // x = 6;          // ERROR: cannot assign twice to immutable variable

    let mut y = 10;    // `mut` makes it mutable
    y = 20;            // OK

    // Type annotations
    let age: u32 = 25;           // unsigned 32-bit integer
    let temperature: f64 = 36.6; // 64-bit float
    let active: bool = true;
    let letter: char = 'A';      // Unicode character (4 bytes)
    let name: &str = "Alice";    // string slice (reference to string data)

    // String (heap-allocated, growable) vs &str (borrowed slice)
    let owned: String = String::from("Hello");
    let slice: &str = "Hello";   // points to static memory

    // Tuples
    let point: (f64, f64) = (3.0, 4.0);
    let (x, y) = point;  // destructuring

    // Arrays (fixed size, stack allocated)
    let numbers: [i32; 5] = [1, 2, 3, 4, 5];
    let first = numbers[0];

    // Printing
    println!("Name: {}, Age: {}", name, age);
    println!("Debug: {:?}", numbers);  // debug format
}

// Functions
fn add(a: i32, b: i32) -> i32 {
    a + b  // no semicolon = return value (expression, not statement)
}

fn greet(name: &str) -> String {
    format!("Hello, {}!", name)  // returns a new String
}
```

**Numeric types:**
```
Signed:   i8, i16, i32, i64, i128, isize
Unsigned: u8, u16, u32, u64, u128, usize
Float:    f32, f64
```
`isize`/`usize` = pointer-sized (64-bit on 64-bit systems). Used for indexing.

---

## PART 2: Ownership — The Core Concept

## 42.4 Ownership rules

```
Rule 1: Each value has exactly ONE owner (a variable)
Rule 2: When the owner goes out of scope, the value is dropped (freed)
Rule 3: Ownership can be MOVED (transferred) or BORROWED (lent)
```

```rust
fn main() {
    let s1 = String::from("hello");  // s1 owns the String
    let s2 = s1;                      // ownership MOVES to s2
    // println!("{}", s1);            // ERROR: s1 no longer owns it!
    println!("{}", s2);               // OK: s2 is the owner

    // For types that implement Copy (primitives, small stack types):
    let n1 = 42;
    let n2 = n1;   // COPIES (not moves) — both are valid
    println!("{} {}", n1, n2);  // OK: integers are Copy
}
```

**What "move" means in memory:**
```
Stack:          Heap:
s1: [ptr, len, cap]  →  "hello" bytes
     ↓ move
s2: [ptr, len, cap]  →  "hello" bytes
s1: INVALID (compiler knows this)
```

No double-free possible — only one owner can drop the memory.

## 42.5 Borrowing — references without ownership transfer

```rust
fn main() {
    let s = String::from("hello");

    // IMMUTABLE borrow (&): "you can look, but not touch"
    let len = calculate_length(&s);  // borrow s (doesn't take ownership)
    println!("{} has length {}", s, len);  // s is still valid!

    // MUTABLE borrow (&mut): "you can modify it"
    let mut s = String::from("hello");
    append_world(&mut s);
    println!("{}", s);  // "hello world"
}

fn calculate_length(s: &String) -> usize {
    s.len()  // can read, but can't modify or drop
}

fn append_world(s: &mut String) {
    s.push_str(" world");  // can modify because we have &mut
}
```

**Borrowing rules (enforced at compile time):**
```
Rule 1: You can have EITHER:
        - Any number of immutable references (&T)   ← multiple readers OK
        - OR exactly ONE mutable reference (&mut T) ← one writer, no readers

Rule 2: References must always be valid (no dangling pointers)
```

```rust
let mut s = String::from("hello");

let r1 = &s;      // OK: immutable borrow
let r2 = &s;      // OK: multiple immutable borrows
// let r3 = &mut s;  // ERROR: can't have mutable while immutable exist

println!("{} {}", r1, r2);  // r1, r2 last used here
let r3 = &mut s;            // OK now: r1, r2 are no longer used
r3.push_str("!");
```

> **This is how Rust prevents data races at compile time.** If multiple threads could simultaneously have `&mut` to the same data, you'd have a data race. The compiler makes this impossible.

## 42.6 Lifetimes (brief intro)

Lifetimes tell the compiler how long a reference is valid:

```rust
// The compiler infers lifetimes most of the time. You only need to annotate
// when the compiler can't figure it out (functions returning references).

fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
// 'a means: the returned reference lives as long as the SHORTER of x and y

fn main() {
    let s1 = String::from("long string");
    let result;
    {
        let s2 = String::from("hi");
        result = longest(&s1, &s2);
        println!("{}", result);  // OK: both s1 and s2 are alive here
    }
    // println!("{}", result);  // ERROR: s2 was dropped, result might point to it
}
```

**Don't panic about lifetimes.** The compiler tells you when you need them, and 90% of the time elision rules handle it automatically.

---

## PART 3: Structs, Enums, Pattern Matching

## 42.7 Structs

```rust
// Define a struct
struct User {
    name: String,
    email: String,
    age: u32,
    active: bool,
}

// Create an instance
let user = User {
    name: String::from("Alice"),
    email: String::from("alice@example.com"),
    age: 30,
    active: true,
};

// Access fields
println!("{}", user.name);

// Implement methods
impl User {
    // Constructor (convention: `new`)
    fn new(name: &str, email: &str, age: u32) -> Self {
        User {
            name: name.to_string(),
            email: email.to_string(),
            age,
            active: true,
        }
    }

    // Method (takes &self — immutable borrow of the instance)
    fn display(&self) -> String {
        format!("{} <{}>", self.name, self.email)
    }

    // Method that modifies (takes &mut self)
    fn deactivate(&mut self) {
        self.active = false;
    }

    // Associated function (no self — like a static method)
    fn default_email(name: &str) -> String {
        format!("{}@company.com", name.to_lowercase())
    }
}

let mut alice = User::new("Alice", "alice@example.com", 30);
println!("{}", alice.display());
alice.deactivate();
```

## 42.8 Enums — more powerful than Java/C enums

Rust enums can hold DATA inside each variant:

```rust
// Simple enum (like Java)
enum Direction {
    North,
    South,
    East,
    West,
}

// Enum with data (algebraic data types!)
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
    Triangle { base: f64, height: f64 },
}

// The most important enums in Rust:
enum Option<T> {
    Some(T),    // has a value
    None,       // no value (replaces null!)
}

enum Result<T, E> {
    Ok(T),      // success with value
    Err(E),     // error with error info
}
```

## 42.9 Pattern matching (match)

```rust
fn area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
        Shape::Rectangle { width, height } => width * height,
        Shape::Triangle { base, height } => 0.5 * base * height,
    }
}

// Option handling (no null!)
fn find_user(id: u32) -> Option<User> {
    if id == 1 {
        Some(User::new("Alice", "alice@example.com", 30))
    } else {
        None
    }
}

fn main() {
    match find_user(1) {
        Some(user) => println!("Found: {}", user.display()),
        None => println!("User not found"),
    }

    // Or use if-let for single pattern
    if let Some(user) = find_user(1) {
        println!("Found: {}", user.display());
    }

    // Unwrap shortcuts (panic if None — only for prototyping!)
    let user = find_user(1).unwrap();           // panics if None
    let user = find_user(1).expect("User 1 must exist");  // panics with message
    let user = find_user(1).unwrap_or_default(); // fallback value
}
```

## 42.10 Error handling with Result

```rust
use std::fs;
use std::io;

// Function that can fail
fn read_config(path: &str) -> Result<String, io::Error> {
    fs::read_to_string(path)  // returns Result<String, io::Error>
}

fn main() {
    // Explicit match
    match read_config("config.toml") {
        Ok(content) => println!("Config: {}", content),
        Err(e) => eprintln!("Error: {}", e),
    }

    // The ? operator: propagate errors concisely
    let content = read_config("config.toml")?;
    // If Err → return the error from the current function
    // If Ok → unwrap the value and continue
}

// Real-world: chain fallible operations with ?
fn process_config() -> Result<Config, Box<dyn std::error::Error>> {
    let content = fs::read_to_string("config.toml")?;
    let config: Config = toml::from_str(&content)?;
    validate_config(&config)?;
    Ok(config)
}
```

`?` replaces `try/catch` — errors propagate UP cleanly without exception overhead.



---

## PART 4: Traits, Collections, Iterators

## 42.11 Traits (like interfaces, but better)

```rust
// Define a trait (interface)
trait Describable {
    fn describe(&self) -> String;

    // Default implementation (can be overridden)
    fn summary(&self) -> String {
        format!("Object: {}", self.describe())
    }
}

// Implement trait for a type
impl Describable for User {
    fn describe(&self) -> String {
        format!("{} ({})", self.name, self.email)
    }
}

impl Describable for Shape {
    fn describe(&self) -> String {
        match self {
            Shape::Circle { radius } => format!("Circle r={}", radius),
            Shape::Rectangle { width, height } => format!("Rect {}×{}", width, height),
            Shape::Triangle { .. } => "Triangle".to_string(),
        }
    }
}

// Use traits as function parameters (generics with trait bounds)
fn print_description(item: &impl Describable) {
    println!("{}", item.describe());
}

// Or with explicit generic syntax:
fn print_all<T: Describable>(items: &[T]) {
    for item in items {
        println!("{}", item.summary());
    }
}

// Multiple trait bounds
fn process<T: Describable + Clone + std::fmt::Debug>(item: &T) { ... }
```

**Common standard traits:**
| Trait | Purpose | Example |
|-------|---------|---------|
| `Clone` | Deep copy | `item.clone()` |
| `Copy` | Implicit copy (small types) | Primitives, tuples of Copy types |
| `Debug` | `{:?}` formatting | `println!("{:?}", item)` |
| `Display` | `{}` formatting (human-readable) | `println!("{}", item)` |
| `PartialEq` / `Eq` | Equality comparison | `a == b` |
| `PartialOrd` / `Ord` | Ordering | `a < b`, sorting |
| `Hash` | Use as HashMap key | `HashMap<MyType, V>` |
| `Default` | Default value | `MyType::default()` |
| `From` / `Into` | Type conversion | `String::from("hi")` |
| `Iterator` | Iteration protocol | `for item in collection` |

```rust
// Derive common traits automatically
#[derive(Debug, Clone, PartialEq, Hash)]
struct Point {
    x: f64,
    y: f64,
}
```

## 42.12 Collections

```rust
use std::collections::HashMap;

// Vec<T> — dynamic array (like ArrayList)
let mut numbers: Vec<i32> = Vec::new();
numbers.push(1);
numbers.push(2);
numbers.push(3);
let first = numbers[0];             // panics if out of bounds!
let first = numbers.get(0);         // returns Option<&i32> (safe)
let last = numbers.pop();           // removes and returns last: Option<i32>
let len = numbers.len();
let slice = &numbers[1..3];         // slice: &[i32] = [2, 3]

// Vec macro shorthand
let nums = vec![1, 2, 3, 4, 5];

// HashMap<K, V> — key-value store
let mut scores: HashMap<String, i32> = HashMap::new();
scores.insert("Alice".to_string(), 95);
scores.insert("Bob".to_string(), 87);

let alice_score = scores.get("Alice");  // Option<&i32>

// Entry API (like computeIfAbsent)
scores.entry("Carol".to_string()).or_insert(0);
*scores.entry("Alice".to_string()).or_insert(0) += 5;  // increment

// Iterate
for (name, score) in &scores {
    println!("{}: {}", name, score);
}

// String — UTF-8, heap allocated, growable
let mut s = String::from("Hello");
s.push_str(", world");
s.push('!');
let length = s.len();       // bytes (not characters!)
let chars = s.chars();      // iterator over Unicode characters

// HashSet<T>
use std::collections::HashSet;
let mut seen: HashSet<i32> = HashSet::new();
seen.insert(1);
seen.insert(2);
seen.contains(&1);  // true
```

## 42.13 Iterators — Rust's superpower

```rust
let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Chain operations (lazy — only executes when consumed)
let result: Vec<i32> = numbers.iter()
    .filter(|&&n| n % 2 == 0)      // keep even numbers
    .map(|&n| n * n)                // square each
    .collect();                      // execute and collect into Vec
// result = [4, 16, 36, 64, 100]

// Sum
let total: i32 = numbers.iter().sum();

// Find
let first_big = numbers.iter().find(|&&n| n > 5);  // Option<&&i32>

// Fold (reduce)
let product = numbers.iter().fold(1, |acc, &n| acc * n);

// Enumerate (index + value)
for (i, val) in numbers.iter().enumerate() {
    println!("[{}] = {}", i, val);
}

// Zip (combine two iterators)
let names = vec!["Alice", "Bob", "Carol"];
let ages = vec![30, 25, 35];
let pairs: Vec<_> = names.iter().zip(ages.iter()).collect();
// [("Alice", 30), ("Bob", 25), ("Carol", 35)]

// Chaining into HashMap
let word_counts: HashMap<&str, usize> = text.split_whitespace()
    .fold(HashMap::new(), |mut map, word| {
        *map.entry(word).or_insert(0) += 1;
        map
    });
```

**Iterators are zero-cost abstractions.** The compiler optimises iterator chains into the same machine code as a hand-written loop. No overhead.

---

## PART 5: Concurrency

## 42.14 Fearless concurrency

Rust's ownership system makes data races impossible at compile time:

```rust
use std::thread;
use std::sync::{Arc, Mutex};

// Spawn threads
let handle = thread::spawn(|| {
    println!("Hello from thread!");
});
handle.join().unwrap();  // wait for thread to finish

// Sharing data between threads: Arc<Mutex<T>>
// Arc = atomic reference count (shared ownership across threads)
// Mutex = mutual exclusion (only one thread accesses data at a time)
let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);  // clone the Arc (not the data)
    let handle = thread::spawn(move || {
        let mut num = counter.lock().unwrap();  // acquire lock
        *num += 1;
        // lock automatically released when `num` goes out of scope
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
println!("Final count: {}", *counter.lock().unwrap());  // 10
```

**Why the compiler prevents data races:**
```rust
let mut data = vec![1, 2, 3];

// ❌ This won't compile: can't send &mut to multiple threads
thread::spawn(|| { data.push(4); });  // ERROR: data moved here
thread::spawn(|| { data.push(5); });  // ERROR: data already moved

// ✅ Use Arc<Mutex<T>> to share safely
```

## 42.15 Channels (message passing)

```rust
use std::sync::mpsc;  // multi-producer, single-consumer

let (tx, rx) = mpsc::channel();

// Sender thread
thread::spawn(move || {
    tx.send("Hello from thread!").unwrap();
    tx.send("Another message").unwrap();
});

// Receiver (main thread)
for message in rx {
    println!("Received: {}", message);
}
```

## 42.16 Async/Await (Tokio)

```rust
// Cargo.toml: tokio = { version = "1", features = ["full"] }

use tokio;

#[tokio::main]
async fn main() {
    let result = fetch_data("https://api.example.com/data").await;
    println!("{}", result);

    // Concurrent tasks
    let (a, b) = tokio::join!(
        fetch_data("https://api.example.com/users"),
        fetch_data("https://api.example.com/posts"),
    );
}

async fn fetch_data(url: &str) -> String {
    let response = reqwest::get(url).await.unwrap();
    response.text().await.unwrap()
}
```

---

## PART 6: Build — CLI Tool + Web API

## 42.17 CLI tool with clap

```toml
# Cargo.toml
[dependencies]
clap = { version = "4", features = ["derive"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

```rust
// src/main.rs
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "taskctl", about = "Task management CLI")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Add a new task
    Add {
        #[arg(short, long)]
        title: String,
        #[arg(short, long, default_value = "medium")]
        priority: String,
    },
    /// List all tasks
    List {
        #[arg(short, long)]
        status: Option<String>,
    },
    /// Complete a task
    Done { id: u32 },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Add { title, priority } => {
            println!("Adding task: {} [{}]", title, priority);
            // save to file/db
        }
        Commands::List { status } => {
            println!("Listing tasks (filter: {:?})", status);
            // read from file/db
        }
        Commands::Done { id } => {
            println!("Marking task {} as done", id);
        }
    }
}
```

```bash
cargo run -- add --title "Learn Rust" --priority high
cargo run -- list --status todo
cargo run -- done 1
```

## 42.18 Web API with Axum

```toml
# Cargo.toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tower-http = { version = "0.5", features = ["cors"] }
```

```rust
use axum::{
    extract::{Path, State, Json},
    http::StatusCode,
    routing::{get, post, delete},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Task {
    id: u32,
    title: String,
    done: bool,
}

#[derive(Deserialize)]
struct CreateTask {
    title: String,
}

type AppState = Arc<Mutex<HashMap<u32, Task>>>;

#[tokio::main]
async fn main() {
    let state: AppState = Arc::new(Mutex::new(HashMap::new()));

    let app = Router::new()
        .route("/tasks", get(list_tasks).post(create_task))
        .route("/tasks/{id}", get(get_task).delete(delete_task))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Server running on http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}

async fn list_tasks(State(state): State<AppState>) -> Json<Vec<Task>> {
    let tasks = state.lock().unwrap();
    Json(tasks.values().cloned().collect())
}

async fn create_task(
    State(state): State<AppState>,
    Json(input): Json<CreateTask>,
) -> (StatusCode, Json<Task>) {
    let mut tasks = state.lock().unwrap();
    let id = tasks.len() as u32 + 1;
    let task = Task { id, title: input.title, done: false };
    tasks.insert(id, task.clone());
    (StatusCode::CREATED, Json(task))
}

async fn get_task(
    State(state): State<AppState>,
    Path(id): Path<u32>,
) -> Result<Json<Task>, StatusCode> {
    let tasks = state.lock().unwrap();
    tasks.get(&id).cloned().map(Json).ok_or(StatusCode::NOT_FOUND)
}

async fn delete_task(
    State(state): State<AppState>,
    Path(id): Path<u32>,
) -> StatusCode {
    let mut tasks = state.lock().unwrap();
    if tasks.remove(&id).is_some() {
        StatusCode::NO_CONTENT
    } else {
        StatusCode::NOT_FOUND
    }
}
```

```bash
cargo run
# POST http://localhost:3000/tasks  {"title": "Learn Rust"}
# GET  http://localhost:3000/tasks
# GET  http://localhost:3000/tasks/1
# DELETE http://localhost:3000/tasks/1
```

---

## PART 7: Cargo & Ecosystem

## 42.19 Cargo.toml essentials

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"    # Rust edition (language version features)
authors = ["You <you@example.com>"]

[dependencies]
serde = { version = "1.0", features = ["derive"] }  # with feature flags
tokio = { version = "1", features = ["full"] }
axum = "0.7"

[dev-dependencies]  # only for tests
mockall = "0.12"
tempfile = "3"

[build-dependencies]  # for build scripts
tonic-build = "0.11"

[[bin]]              # multiple binaries
name = "server"
path = "src/server.rs"

[[bin]]
name = "cli"
path = "src/cli.rs"
```

## 42.20 Essential crates (libraries)

| Category | Crate | Purpose |
|----------|-------|---------|
| **Web** | `axum` | Web framework (by Tokio team) |
| **Web** | `actix-web` | High-performance web framework |
| **Async** | `tokio` | Async runtime (standard) |
| **Serialization** | `serde` + `serde_json` | JSON/TOML/YAML serialization |
| **HTTP client** | `reqwest` | HTTP requests |
| **Database** | `sqlx` | Async SQL (compile-time checked queries!) |
| **ORM** | `diesel` | Type-safe ORM |
| **CLI** | `clap` | Argument parsing |
| **Error** | `anyhow` | Easy error handling (applications) |
| **Error** | `thiserror` | Custom error types (libraries) |
| **Logging** | `tracing` | Structured logging + spans |
| **Testing** | `mockall` | Mock generation |
| **Config** | `config` | Configuration from files/env |

## 42.21 Cargo commands

```bash
cargo new project-name       # create new project
cargo init                   # init in existing directory
cargo build                  # compile (debug)
cargo build --release        # compile (optimised)
cargo run                    # compile + run
cargo test                   # run all tests
cargo test test_name         # run specific test
cargo bench                  # run benchmarks
cargo doc --open             # generate and open docs
cargo clippy                 # linter (catches common mistakes)
cargo fmt                    # format code
cargo update                 # update deps to latest compatible
cargo add serde              # add dependency (like npm install)
cargo tree                   # dependency tree
```

---

## Summary

✅ Why Rust: memory safety without GC, zero-cost abstractions, no null, no data races
✅ Ownership: each value has one owner, ownership moves, dropped when owner ends
✅ Borrowing: immutable `&T` (many readers) OR mutable `&mut T` (one writer)
✅ Structs + Enums: data with methods, enums carry data (algebraic types)
✅ Pattern matching: `match` exhaustively handles all variants
✅ Error handling: `Result<T, E>` + `?` operator (no exceptions)
✅ Traits: like interfaces with default methods + derive macros
✅ Iterators: zero-cost functional chains (filter/map/collect)
✅ Concurrency: Arc<Mutex<T>> for shared state, channels for message passing, async/await with Tokio
✅ Built: CLI tool (clap) + REST API (Axum)
✅ Cargo: build, test, format, lint, dependency management

## Key takeaways

**The compiler is your pair programmer.** Rust's famous "fighting the borrow checker" is really "the compiler catching bugs you'd find in production in other languages." Once it compiles, it's likely correct.

**Ownership is the breakthrough idea.** It replaces: garbage collection, manual malloc/free, reference counting (as default), and null pointers — with a single unified concept enforced at compile time with zero runtime cost.

**`Result` + `?` replaces try/catch.** Errors are values, not exceptions. You can't forget to handle them (the compiler won't let you). The `?` operator makes error propagation as concise as exceptions but explicit.

**Start with `cargo clippy` and `cargo fmt`.** Clippy catches hundreds of common mistakes and suggests idiomatic alternatives. Fmt ensures consistent style. Together they make learning Rust faster because you get immediate feedback.

---

→ [Back to Chapter 41: Gradle for Spring Boot](./41-GRADLE-SPRING-BOOT.md)
