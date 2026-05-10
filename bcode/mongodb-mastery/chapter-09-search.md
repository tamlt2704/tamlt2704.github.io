# Chapter 9: Atlas Search

[← Ch 8](chapter-08-streams.md) | [Ch 10 →](chapter-10-performance.md)

---

## The Problem

> **The Client:** "Users type in a search box and expect Google-like results: fuzzy matching, typo tolerance, autocomplete suggestions, and faceted filtering by department and status. Your basic `$text` index returns garbage results."

MongoDB's `$text` is limited — no fuzzy matching, no scoring control, no autocomplete. **Atlas Search** is a Lucene-powered engine built into MongoDB Atlas.

---

## $text vs Atlas Search

| Feature | $text (basic) | Atlas Search (Lucene) |
|---|---|---|
| Fuzzy matching | ❌ | ✅ |
| Autocomplete | ❌ | ✅ |
| Custom scoring | ❌ | ✅ |
| Facets | ❌ | ✅ |
| Highlighting | ❌ | ✅ |
| Compound queries | Limited | Full boolean |
| Analyzers | Basic stemming | Custom analyzers |

---

## Creating a Search Index

In Atlas UI or via `mongosh`:

```javascript
// Create search index (Atlas CLI / UI)
db.contracts.createSearchIndex("default", {
  mappings: {
    dynamic: false,
    fields: {
      title: { type: "string", analyzer: "lucene.standard" },
      client: { type: "string", analyzer: "lucene.standard" },
      status: { type: "stringFacet" },
      "clauses.text": { type: "string", analyzer: "lucene.english" },
      "metadata.department": { type: "stringFacet" },
      value: { type: "number" }
    }
  }
})

// Autocomplete index
db.contracts.createSearchIndex("autocomplete", {
  mappings: {
    fields: {
      title: {
        type: "autocomplete",
        tokenization: "edgeGram",
        minGrams: 2,
        maxGrams: 15
      }
    }
  }
})
```

---

## Basic Text Search with $search

```javascript
db.contracts.aggregate([
  { $search: {
    index: "default",
    text: {
      query: "enterprise license agreement",
      path: ["title", "clauses.text"]
    }
  }},
  { $limit: 10 },
  { $project: { title: 1, client: 1, score: { $meta: "searchScore" } } }
])
```

---

## Fuzzy Matching — Typo Tolerance

```javascript
db.contracts.aggregate([
  { $search: {
    index: "default",
    text: {
      query: "licnese agreemnt",  // Typos!
      path: "title",
      fuzzy: {
        maxEdits: 2,        // Levenshtein distance
        prefixLength: 2     // First 2 chars must match
      }
    }
  }},
  { $project: { title: 1, score: { $meta: "searchScore" } } }
])
```

---

## Autocomplete

```javascript
db.contracts.aggregate([
  { $search: {
    index: "autocomplete",
    autocomplete: {
      query: "ent",
      path: "title",
      tokenOrder: "sequential"
    }
  }},
  { $limit: 5 },
  { $project: { title: 1, _id: 0 } }
])
// Results: "Enterprise License", "Enterprise NDA", "Entity Agreement"
```

---

## Compound Queries — Boolean Logic

```javascript
db.contracts.aggregate([
  { $search: {
    index: "default",
    compound: {
      must: [
        { text: { query: "SLA", path: "clauses.text" } }
      ],
      should: [
        { text: { query: "enterprise", path: "title" } }
      ],
      filter: [
        { equals: { path: "status", value: "active" } }
      ],
      mustNot: [
        { text: { query: "expired cancelled", path: "status" } }
      ]
    }
  }},
  { $limit: 20 },
  { $project: { title: 1, client: 1, status: 1, score: { $meta: "searchScore" } } }
])
```

| Clause | Behavior | Affects Score? |
|---|---|---|
| `must` | Required | Yes |
| `should` | Boosts if present | Yes |
| `filter` | Required | No (faster) |
| `mustNot` | Excluded | No |

---

## Facets — Aggregated Counts

```javascript
db.contracts.aggregate([
  { $searchMeta: {
    index: "default",
    facet: {
      operator: {
        text: { query: "agreement", path: "title" }
      },
      facets: {
        statusFacet: { type: "string", path: "status" },
        departmentFacet: { type: "string", path: "metadata.department" }
      }
    }
  }}
])
// Returns: { statusFacet: { buckets: [{ _id: "active", count: 45 }, ...] } }
```

---

## Highlighting — Show Matched Text

```javascript
db.contracts.aggregate([
  { $search: {
    index: "default",
    text: { query: "payment terms", path: "clauses.text" },
    highlight: { path: "clauses.text" }
  }},
  { $project: {
    title: 1,
    highlights: { $meta: "searchHighlights" }
  }},
  { $limit: 5 }
])
// highlights: [{ path: "clauses.text", texts: [
//   { value: "Net 30 ", type: "text" },
//   { value: "payment terms", type: "hit" }
// ]}]
```

---

## Scoring and Boosting

```javascript
db.contracts.aggregate([
  { $search: {
    index: "default",
    compound: {
      should: [
        {
          text: {
            query: "enterprise",
            path: "title",
            score: { boost: { value: 3 } }  // Title matches worth 3x
          }
        },
        {
          text: {
            query: "enterprise",
            path: "clauses.text",
            score: { boost: { value: 1 } }
          }
        }
      ]
    }
  }},
  { $limit: 10 }
])
```

---

## Python Example

```python
from pymongo import MongoClient

client = MongoClient("mongodb+srv://user:pass@cluster.mongodb.net/")
db = client.docuflow

# Full-text search with fuzzy matching
results = db.contracts.aggregate([
    {"$search": {
        "index": "default",
        "text": {
            "query": "enterprise agreement",
            "path": ["title", "clauses.text"],
            "fuzzy": {"maxEdits": 1}
        }
    }},
    {"$limit": 10},
    {"$project": {"title": 1, "client": 1, "score": {"$meta": "searchScore"}}}
])

for doc in results:
    print(f"{doc['title']} (score: {doc['score']:.2f})")
```

---

## What You Learned

- Atlas Search uses Lucene under the hood — far more powerful than `$text`
- Search indexes define which fields are searchable and how they're analyzed
- `$search` stage in aggregation pipeline for full-text queries
- Fuzzy matching handles typos with `maxEdits` (Levenshtein distance)
- Autocomplete with edge n-grams for type-ahead suggestions
- Compound queries combine must/should/filter/mustNot clauses
- Facets return aggregated counts for filter UIs
- Highlighting shows which parts of text matched

---

[← Ch 8: Change Streams](chapter-08-streams.md) | [Ch 10: Performance →](chapter-10-performance.md)
