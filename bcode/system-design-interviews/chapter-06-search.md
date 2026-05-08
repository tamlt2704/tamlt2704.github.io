# Chapter 6: Design Web Search (Google)

[← File Storage](./chapter-05-storage.md) | [Next: Video Platform →](./chapter-07-video.md)

---

## The Question

> "Design a web-scale search engine like Google. Users type a query and get ranked results in under 200ms. The system needs to crawl billions of web pages, index them, and serve relevant results with autocomplete and spell correction."

---

## Step 1: Requirements & Scope

**Functional:**
- Crawl and index billions of web pages
- Full-text search with ranked results
- Autocomplete (query suggestions as you type)
- Spell correction ("Did you mean...?")
- Snippet generation (preview of matching content)

**Non-functional:**
- 10B pages indexed
- 100K search queries/sec
- Query latency <200ms (p99)
- Index freshness: popular pages re-crawled within hours
- High availability — search must never go down

**Out of scope:** Ads, image search, knowledge graph.

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Index size | 10B pages × 100KB avg (compressed) | ~200 TB (raw), ~20 TB (compressed) |
| Inverted index | 10B pages × 500 unique terms avg | ~5 trillion postings |
| Query QPS | 100K queries/sec | Need massive parallelism |
| Crawl rate | 10B pages / 7 days refresh | ~16,500 pages/sec |

---

## Step 3: API Design

```
GET /search?q=system+design&page=1&limit=10
Response: {
  "results": [
    { "url": "...", "title": "...", "snippet": "...", "rank": 1 }
  ],
  "spell_suggestion": null,
  "total_results": 1420000,
  "time_ms": 142
}

GET /autocomplete?prefix=syst&limit=5
Response: { "suggestions": ["system design", "system32", "systematic review"] }
```

---

## Step 4: Data Model

**Document Store (distributed — Bigtable/custom):**

| Field | Type |
|-------|------|
| doc_id (PK) | UINT64 |
| url | VARCHAR |
| title | VARCHAR |
| content | TEXT (compressed) |
| pagerank_score | FLOAT |
| last_crawled | TIMESTAMP |

**Inverted Index (custom distributed structure):**

```
term → [(doc_id, term_frequency, positions), (doc_id, tf, pos), ...]

Example:
"design" → [(doc_42, 5, [12,45,89]), (doc_99, 3, [7,23,56]), ...]
```

---

## Step 5: High-Level Architecture

```
┌──────────┐     ┌──────────────┐     ┌─────────────────┐
│  User    │────▶│ Load Balancer│────▶│  Query Server   │
└──────────┘     └──────────────┘     └────────┬────────┘
                                               │
                         ┌─────────────────────┼──────────────────┐
                         ▼                     ▼                   ▼
                ┌──────────────┐     ┌──────────────┐    ┌──────────────┐
                │  Index Shard │     │  Index Shard │    │  Index Shard │
                │  (partition) │     │  (partition) │    │  (partition) │
                └──────────────┘     └──────────────┘    └──────────────┘

                         ┌─────────────────────────────────────────┐
                         │            Offline Pipeline              │
                         │  Crawler → Parser → Indexer → PageRank  │
                         └─────────────────────────────────────────┘
```

---

## Step 6: Deep Dive

### Web Crawler

1. **URL Frontier:** Priority queue of URLs to crawl (BFS with politeness)
2. **Fetcher:** Download pages (respect robots.txt, rate limit per domain)
3. **Parser:** Extract text, links, metadata
4. **Deduplication:** Content hash to avoid indexing duplicate pages
5. **URL Extractor:** Discover new URLs, add to frontier

**Politeness:** Max 1 request/second per domain. Distribute crawl across domains.

### Inverted Index

Building the index:
1. Tokenize document → list of terms
2. For each term, add (doc_id, frequency, positions) to posting list
3. Shard index by term hash across machines

**Query processing:**
- "system design" → look up posting lists for "system" AND "design"
- Intersect posting lists → documents containing both terms
- Score and rank results

### PageRank (Simplified)

Core idea: A page is important if important pages link to it.

```
PR(page) = (1-d) + d × Σ(PR(linking_page) / outlinks(linking_page))
d = damping factor (0.85)
```

Iterative computation over the entire web graph. Converges in ~50 iterations. Computed offline in batch (MapReduce).

### Query Processing Pipeline

```
Query → Tokenize → Spell Check → Expand (synonyms)
     → Fetch posting lists from shards (parallel)
     → Intersect/Union → Score (TF-IDF + PageRank + freshness)
     → Rank top K → Generate snippets → Return
```

**Scoring:** `score = α×relevance(TF-IDF) + β×authority(PageRank) + γ×freshness`

### Autocomplete

- Trie data structure with top-K suggestions at each node
- Built from query logs (most popular completions)
- Served from in-memory cache (latency <50ms)
- Updated hourly from aggregated query logs

### Spell Correction

- Edit distance (Levenshtein) against dictionary
- "Did you mean" triggered when query has low result count
- N-gram based: break query into character n-grams, find similar terms

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| Index too large for one machine | Shard by term (or by document) |
| Query latency | Parallel fan-out to all shards |
| Crawler overwhelming sites | Politeness rules, distributed frontier |
| Stale index | Priority re-crawl (popular pages more often) |
| Hot queries | Result cache (same query → cached response) |

**Index partitioning strategies:**
- By document: Each shard has full index for subset of docs. Query hits all shards.
- By term: Each shard owns certain terms. Query hits fewer shards but skewed load.
- Hybrid: Partition by document, replicate hot terms.

---

## Key Talking Points

- Inverted index is the fundamental data structure for search
- PageRank separates web search from simple text matching
- Parallel shard fan-out keeps latency low despite massive index
- Offline pipeline (crawl → index → rank) vs online serving (query → results)
- Autocomplete from tries + query logs, not from the index itself

---

## Common Mistakes

- Trying to search by scanning all documents (no inverted index)
- Ignoring PageRank or authority signals (just using TF-IDF)
- Not discussing how to shard a trillion-entry index
- Forgetting crawler politeness (will get blocked/banned)
- Mixing offline indexing concerns with online query serving
- Not caching popular query results

---

[← File Storage](./chapter-05-storage.md) | [Next: Video Platform →](./chapter-07-video.md)
