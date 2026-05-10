# Chapter 5: Aggregation Pipeline

[← Ch 4](chapter-04-indexes.md) | [Ch 6 →](chapter-06-updates.md)

---

## The Problem

> **The Client:** "I need a monthly revenue report: total contract value grouped by month, top 5 clients by spend, and document counts by status. Can your database do that, or do I need a separate analytics tool?"

MongoDB's aggregation pipeline processes documents through stages — like Unix pipes for data. Each stage transforms the stream.

---

## Pipeline Basics

```javascript
db.contracts.aggregate([
  { $match: { status: "active" } },       // Filter first (uses indexes)
  { $group: { _id: "$client", total: { $sum: "$value" } } },
  { $sort: { total: -1 } },
  { $limit: 5 }
])
```

> **Rule:** Put `$match` early. It's the only stage that uses indexes.

---

## $match — Filter Documents

```javascript
{ $match: { status: "active", value: { $gt: 10000 } } }
```

---

## $group — Aggregate Values

```javascript
// Total revenue by client
db.contracts.aggregate([
  { $group: {
    _id: "$client",
    totalValue: { $sum: "$value" },
    contractCount: { $count: {} },
    avgValue: { $avg: "$value" },
    maxValue: { $max: "$value" }
  }}
])

// Monthly revenue
db.contracts.aggregate([
  { $group: {
    _id: { $dateToString: { format: "%Y-%m", date: "$createdAt" } },
    revenue: { $sum: "$value" },
    count: { $count: {} }
  }},
  { $sort: { _id: -1 } }
])
```

---

## $project — Reshape Documents

```javascript
db.contracts.aggregate([
  { $project: {
    title: 1,
    client: 1,
    valueInK: { $divide: ["$value", 1000] },
    clauseCount: { $size: "$clauses" },
    year: { $year: "$createdAt" }
  }}
])
```

---

## $addFields — Add Without Removing

```javascript
db.contracts.aggregate([
  { $addFields: {
    isHighValue: { $gte: ["$value", 100000] },
    daysSinceCreated: {
      $dateDiff: { startDate: "$createdAt", endDate: "$$NOW", unit: "day" }
    }
  }}
])
```

---

## $unwind — Flatten Arrays

```javascript
// Explode clauses array — one document per clause
db.contracts.aggregate([
  { $unwind: "$clauses" },
  { $group: {
    _id: "$clauses.type",
    count: { $sum: 1 }
  }},
  { $sort: { count: -1 } }
])
// Result: { _id: "payment", count: 45 }, { _id: "sla", count: 32 }, ...
```

---

## $lookup — JOIN Collections

```javascript
// Join contracts with their organization details
db.contracts.aggregate([
  { $lookup: {
    from: "organizations",
    localField: "orgId",
    foreignField: "_id",
    as: "org"
  }},
  { $unwind: "$org" },
  { $project: {
    title: 1,
    value: 1,
    orgName: "$org.name",
    orgPlan: "$org.plan"
  }}
])
```

---

## $bucket — Group into Ranges

```javascript
// Group contracts by value ranges
db.contracts.aggregate([
  { $bucket: {
    groupBy: "$value",
    boundaries: [0, 10000, 50000, 100000, 500000],
    default: "500k+",
    output: {
      count: { $sum: 1 },
      contracts: { $push: "$title" }
    }
  }}
])
```

---

## $count

```javascript
db.contracts.aggregate([
  { $match: { status: "active" } },
  { $count: "activeContracts" }
])
// { activeContracts: 247 }
```

---

## Real Example: Monthly Revenue Report

```javascript
db.contracts.aggregate([
  { $match: { status: { $in: ["active", "signed"] } } },
  { $group: {
    _id: {
      year: { $year: "$createdAt" },
      month: { $month: "$createdAt" }
    },
    revenue: { $sum: "$value" },
    contracts: { $count: {} },
    avgDeal: { $avg: "$value" }
  }},
  { $sort: { "_id.year": -1, "_id.month": -1 } },
  { $limit: 12 },
  { $project: {
    _id: 0,
    period: { $concat: [
      { $toString: "$_id.year" }, "-",
      { $cond: [{ $lt: ["$_id.month", 10] }, { $concat: ["0", { $toString: "$_id.month" }] }, { $toString: "$_id.month" }] }
    ]},
    revenue: 1,
    contracts: 1,
    avgDeal: { $round: ["$avgDeal", 2] }
  }}
])
```

---

## Python Example

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.docuflow

# Top 5 clients by total contract value
pipeline = [
    {"$match": {"status": {"$in": ["active", "signed"]}}},
    {"$group": {"_id": "$client", "total": {"$sum": "$value"}}},
    {"$sort": {"total": -1}},
    {"$limit": 5}
]

for doc in db.contracts.aggregate(pipeline):
    print(f"{doc['_id']}: ${doc['total']:,.0f}")
```

---

## What You Learned

- Pipelines process documents through ordered stages
- `$match` first for index usage and early filtering
- `$group` with accumulators: `$sum`, `$avg`, `$count`, `$max`, `$min`, `$push`
- `$unwind` flattens arrays for per-element aggregation
- `$lookup` performs left outer joins between collections
- `$bucket` groups continuous values into ranges
- `$project` / `$addFields` reshape output documents

---

[← Ch 4: Indexes](chapter-04-indexes.md) | [Ch 6: Updates & Operators →](chapter-06-updates.md)
