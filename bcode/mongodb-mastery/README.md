# MongoDB Mastery — From Documents to Production Clusters

A narrative-driven course on MongoDB. You're a backend engineer at **DocuFlow**, a document management SaaS. The product stores contracts, invoices, and forms — each with different fields, nested structures, and evolving schemas. Relational databases fight you at every turn. MongoDB embraces the chaos.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, documents vs tables, when to use MongoDB |
| 01 | [First Documents](chapter-01-crud.md) | Store a contract with nested fields | insertOne/Many, find, updateOne, deleteOne |
| 02 | [Querying](chapter-02-queries.md) | Find contracts by nested fields | Comparison, logical, element, regex, projection |
| 03 | [Schema Design](chapter-03-schema.md) | Model users, orgs, and documents | Embedding vs referencing, one-to-many patterns |
| 04 | [Indexes](chapter-04-indexes.md) | Queries are slow at 1M documents | Single, compound, multikey, text, explain() |
| 05 | [Aggregation Pipeline](chapter-05-aggregation.md) | Monthly revenue report | $match, $group, $sort, $lookup, $unwind |
| 06 | [Updates & Operators](chapter-06-updates.md) | Modify nested arrays without replacing | $set, $push, $pull, $inc, arrayFilters |
| 07 | [Transactions](chapter-07-transactions.md) | Transfer credits between accounts | Multi-document ACID, sessions, retries |
| 08 | [Change Streams](chapter-08-streams.md) | Real-time notifications on changes | Watch collections, resume tokens, triggers |
| 09 | [Atlas Search](chapter-09-search.md) | Full-text search across documents | Search indexes, fuzzy, autocomplete, facets |
| 10 | [Performance](chapter-10-performance.md) | Slow queries under load | Profiler, covered queries, sharding intro |
| 11 | [Security & Ops](chapter-11-ops.md) | Production readiness | Auth, backup, replica sets, monitoring |
| 12 | [With Your Stack](chapter-12-integration.md) | Connect from Node/Python/Java | Mongoose, PyMongo, Spring Data MongoDB |

## Prerequisites

- MongoDB 7+ (local install or free Atlas cluster)
- `mongosh` (MongoDB Shell)
- Any language driver (examples in mongosh + Python/Node)

## Philosophy

Every MongoDB feature is introduced because the relational approach fails for this use case. You'll feel the pain of rigid schemas first, then see how documents solve it. The SQL pain comes first. The document freedom follows.
