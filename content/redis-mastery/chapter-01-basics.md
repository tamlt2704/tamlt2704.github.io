# Chapter 1: Redis Basics & Data Types

[← Overview](./chapter-00-overview.md) | [Next: Spring Data Redis →](./chapter-02-spring-redis.md)

---

## 1.1 Strings

The simplest Redis data type. Stores text, numbers, or binary data up to 512MB.

```bash
# Set and get
redis-cli SET user:1:name "Alice"
redis-cli GET user:1:name
# "Alice"

# Numeric operations
redis-cli SET counter 10
redis-cli INCR counter
# (integer) 11
redis-cli INCRBY counter 5
# (integer) 16

# Set with expiration (seconds)
redis-cli SET session:abc "data" EX 3600

# Set only if not exists
redis-cli SETNX lock:resource "owner1"

# Multiple set/get
redis-cli MSET key1 "val1" key2 "val2"
redis-cli MGET key1 key2
```

## 1.2 Lists

Ordered collections of strings. Supports push/pop from both ends.

```bash
# Push elements
redis-cli LPUSH queue "task1"
redis-cli LPUSH queue "task2"
redis-cli RPUSH queue "task3"

# List contents (0-based index, -1 means last)
redis-cli LRANGE queue 0 -1
# 1) "task2"  2) "task1"  3) "task3"

# Pop elements
redis-cli LPOP queue
redis-cli RPOP queue

# Blocking pop (timeout 5 seconds)
redis-cli BLPOP queue 5
```

## 1.3 Sets

Unordered collections of unique strings.

```bash
# Add members
redis-cli SADD tags:post:1 "redis" "database" "nosql"
redis-cli SADD tags:post:2 "redis" "caching" "performance"

# Members and cardinality
redis-cli SMEMBERS tags:post:1
redis-cli SCARD tags:post:1

# Set operations
redis-cli SINTER tags:post:1 tags:post:2
# 1) "redis"
redis-cli SUNION tags:post:1 tags:post:2
redis-cli SDIFF tags:post:1 tags:post:2
```

## 1.4 Sorted Sets

Like Sets but each member has a score for ordering.

```bash
# Add with scores
redis-cli ZADD leaderboard 100 "alice"
redis-cli ZADD leaderboard 85 "bob"
redis-cli ZADD leaderboard 92 "charlie"

# Range by rank (descending)
redis-cli ZREVRANGE leaderboard 0 -1 WITHSCORES

# Range by score
redis-cli ZRANGEBYSCORE leaderboard 90 100

# Rank and increment
redis-cli ZREVRANK leaderboard "alice"
redis-cli ZINCRBY leaderboard 15 "bob"
```

## 1.5 Hashes

Maps of field-value pairs, ideal for representing objects.

```bash
# Set fields
redis-cli HSET user:1 name "Alice" email "alice@example.com" age "30"

# Get fields
redis-cli HGET user:1 name
redis-cli HGETALL user:1

# Increment numeric field
redis-cli HINCRBY user:1 age 1

# Delete field
redis-cli HDEL user:1 age
```

## 1.6 Key Management

```bash
redis-cli KEYS "user:*"
redis-cli EXISTS user:1
redis-cli EXPIRE user:1 3600
redis-cli TTL user:1
redis-cli DEL user:1
redis-cli UNLINK user:1  # async delete
redis-cli TYPE user:1
```

## Exercises

1. Create a hash representing a product with fields: id, name, price, stock. Increment stock by 10.
2. Build a task queue using a list. Push 5 tasks, pop them one by one.
3. Create two sets representing user interests. Find common interests using SINTER.
4. Build a leaderboard with 5 players. Find the top 3 players by score.
5. Set a key with a 60-second TTL. Check remaining TTL after 10 seconds.

---

[← Overview](./chapter-00-overview.md) | [Next: Spring Data Redis →](./chapter-02-spring-redis.md)
