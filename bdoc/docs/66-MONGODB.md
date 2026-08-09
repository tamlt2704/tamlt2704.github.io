# Chapter 66: MongoDB — NoSQL Mastery by Building a Content Platform

## What you'll learn

- Document model: why NoSQL, when to use it (and when NOT to)
- CRUD: insert, find, update, delete with rich query operators
- Schema design: embedding vs referencing, one-to-many patterns
- Indexing: single, compound, text, TTL, partial — and when each matters
- Aggregation pipeline: the MongoDB superpower (GROUP, JOIN, TRANSFORM)
- Transactions, change streams, and Atlas Search
- Build: a complete content platform (posts, comments, tags, users, analytics)
- Performance: profiling slow queries, explain plans, index optimisation

---

## PART 1: Why MongoDB?

## 66.1 Document model vs relational

```
RELATIONAL (PostgreSQL):               DOCUMENT (MongoDB):

users table:                           users collection:
┌────┬───────┬──────────────┐          {
│ id │ name  │ email        │            _id: ObjectId("..."),
├────┼───────┼──────────────┤            name: "Alice",
│ 1  │ Alice │ alice@ex.com │            email: "alice@ex.com",
└────┴───────┴──────────────┘            profile: {
                                           bio: "Developer",
posts table:                               avatar: "https://..."
┌────┬─────────┬─────────┬────┐          },
│ id │ title   │ content │uid │          posts: [
├────┼─────────┼─────────┼────┤            { title: "Hello", tags: ["intro"] },
│ 1  │ Hello   │ ...     │ 1  │            { title: "MongoDB", tags: ["db"] }
│ 2  │ MongoDB │ ...     │ 1  │          ]
└────┴─────────┴─────────┴────┘        }
                                       
tags table + post_tags join table...   ← No joins needed! Everything in one document.
```

**Use MongoDB when:**
- Flexible/evolving schema (startup, prototyping, content systems)
- Hierarchical/nested data (user profiles, product catalogs, CMS)
- High write throughput (logs, IoT, analytics events)
- Horizontal scaling needed (sharding built-in)
- Document-per-entity makes sense (each "thing" is self-contained)

**Use PostgreSQL instead when:**
- Complex relationships with many joins (social graph, ERP)
- ACID transactions across multiple entities (banking, inventory)
- You need SQL (reporting, ad-hoc queries, BI tools)
- Data is highly relational (order → items → products → categories)

## 66.2 Setup

```bash
# Local (Docker — recommended)
docker run -d --name mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -v mongo_data:/data/db \
  mongo:7

# Or MongoDB Atlas (free tier — 512MB, no credit card):
# https://www.mongodb.com/cloud/atlas/register

# MongoDB Shell
mongosh "mongodb://admin:secret@localhost:27017"

# Node.js driver
npm install mongodb
# Or with Mongoose (ODM — schema + validation):
npm install mongoose
```

---

## PART 2: CRUD Operations

## 66.3 Insert

```javascript
// Connect (Node.js)
const { MongoClient, ObjectId } = require("mongodb");
const client = new MongoClient("mongodb://admin:secret@localhost:27017");
const db = client.db("contentplatform");

// Insert one
const result = await db.collection("users").insertOne({
  name: "Alice",
  email: "alice@example.com",
  role: "author",
  profile: {
    bio: "Full-stack developer and writer",
    avatar: "https://example.com/alice.jpg",
    social: { twitter: "@alice", github: "alice" },
  },
  joinedAt: new Date(),
  postCount: 0,
});
console.log("Inserted:", result.insertedId); // ObjectId

// Insert many
await db.collection("posts").insertMany([
  {
    title: "Getting Started with MongoDB",
    slug: "getting-started-mongodb",
    content: "MongoDB is a document database...",
    author: result.insertedId,
    tags: ["mongodb", "database", "tutorial"],
    status: "published",
    likes: 42,
    comments: [],
    metadata: { readTime: 8, wordCount: 1500 },
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    title: "Advanced Aggregation Pipelines",
    slug: "advanced-aggregation",
    content: "The aggregation framework...",
    author: result.insertedId,
    tags: ["mongodb", "advanced", "aggregation"],
    status: "draft",
    likes: 0,
    comments: [],
    metadata: { readTime: 12, wordCount: 2800 },
    createdAt: new Date(),
    updatedAt: new Date(),
  },
]);
```

## 66.4 Find (Query)

```javascript
// Find one
const user = await db.collection("users").findOne({ email: "alice@example.com" });

// Find many (with filter)
const published = await db.collection("posts")
  .find({ status: "published" })
  .sort({ createdAt: -1 })    // newest first
  .limit(10)
  .skip(0)                     // pagination
  .toArray();

// Projection (only return specific fields — like SELECT columns)
const titles = await db.collection("posts")
  .find({ status: "published" }, { projection: { title: 1, slug: 1, createdAt: 1 } })
  .toArray();

// --- QUERY OPERATORS ---

// Comparison
await db.collection("posts").find({ likes: { $gt: 10 } });           // greater than
await db.collection("posts").find({ likes: { $gte: 10, $lte: 100 } }); // range
await db.collection("posts").find({ status: { $in: ["published", "featured"] } });
await db.collection("posts").find({ status: { $ne: "draft" } });      // not equal

// Array queries
await db.collection("posts").find({ tags: "mongodb" });                // array contains
await db.collection("posts").find({ tags: { $all: ["mongodb", "tutorial"] } }); // contains ALL
await db.collection("posts").find({ tags: { $size: 3 } });            // array length = 3

// Nested document
await db.collection("users").find({ "profile.social.twitter": "@alice" });

// Text search (requires text index)
await db.collection("posts").find({ $text: { $search: "mongodb aggregation" } });

// Exists
await db.collection("posts").find({ "metadata.readTime": { $exists: true } });

// Regex
await db.collection("posts").find({ title: { $regex: /mongodb/i } });

// Logical
await db.collection("posts").find({
  $or: [{ status: "published" }, { likes: { $gt: 100 } }],
});
await db.collection("posts").find({
  $and: [{ status: "published" }, { tags: "tutorial" }],
});
```

## 66.5 Update

```javascript
// Update one
await db.collection("posts").updateOne(
  { slug: "getting-started-mongodb" },  // filter
  {
    $set: { status: "featured", updatedAt: new Date() },
    $inc: { likes: 1 },  // increment
  }
);

// Update many
await db.collection("posts").updateMany(
  { status: "draft", createdAt: { $lt: new Date("2024-01-01") } },
  { $set: { status: "archived" } }
);

// Array operations
await db.collection("posts").updateOne(
  { slug: "getting-started-mongodb" },
  {
    $push: {
      comments: {
        _id: new ObjectId(),
        author: "Bob",
        text: "Great article!",
        createdAt: new Date(),
      },
    },
  }
);

// Remove from array
await db.collection("posts").updateOne(
  { slug: "getting-started-mongodb" },
  { $pull: { tags: "tutorial" } }  // remove "tutorial" from tags
);

// Add to array only if not exists
await db.collection("posts").updateOne(
  { slug: "getting-started-mongodb" },
  { $addToSet: { tags: "beginner" } }  // won't add duplicates
);

// Upsert (insert if not found)
await db.collection("analytics").updateOne(
  { postSlug: "getting-started-mongodb", date: "2024-08-01" },
  { $inc: { views: 1 } },
  { upsert: true }  // creates document if filter doesn't match
);
```

## 66.6 Delete

```javascript
await db.collection("posts").deleteOne({ slug: "old-post" });
await db.collection("posts").deleteMany({ status: "archived" });

// Soft delete (better — keep data, mark as deleted)
await db.collection("posts").updateOne(
  { slug: "old-post" },
  { $set: { deletedAt: new Date(), status: "deleted" } }
);
```

---

## PART 3: Schema Design

## 66.7 Embedding vs Referencing

```javascript
// EMBED: put related data INSIDE the document
// Use when: data is always accessed together, one-to-few relationship
{
  _id: ObjectId("..."),
  title: "My Post",
  author: {                    // ← embedded (always need author with post)
    name: "Alice",
    avatar: "https://..."
  },
  comments: [                  // ← embedded (max ~100, always shown with post)
    { author: "Bob", text: "Great!", createdAt: new Date() },
    { author: "Carol", text: "Thanks!", createdAt: new Date() },
  ]
}

// REFERENCE: store just the ID, look up separately
// Use when: data accessed independently, one-to-many (unbounded), many-to-many
{
  _id: ObjectId("..."),
  title: "My Post",
  authorId: ObjectId("user123"),  // ← reference (look up user separately)
  commentIds: [ObjectId("c1"), ObjectId("c2")],  // ← references
}
```

**Decision table:**

| Pattern | Embed | Reference |
|---------|-------|-----------|
| One-to-few (post → 5 tags) | ✅ Embed | |
| One-to-many (user → 100 posts) | Sometimes | ✅ Reference |
| One-to-millions (post → 1M likes) | | ✅ Reference (separate collection) |
| Always accessed together | ✅ Embed | |
| Accessed independently | | ✅ Reference |
| Data changes frequently | | ✅ Reference (avoid update in many places) |
| Unbounded growth | | ✅ Reference (documents have 16MB limit) |

## 66.8 Content platform schema

```javascript
// USERS collection
{
  _id: ObjectId,
  username: "alice",
  email: "alice@example.com",
  passwordHash: "...",
  role: "author",  // "admin", "author", "reader"
  profile: {
    displayName: "Alice Dev",
    bio: "Building things with code",
    avatar: "https://...",
    social: { twitter: "...", github: "..." },
  },
  stats: { postCount: 15, totalLikes: 342, followers: 89 },
  createdAt: ISODate,
  lastLoginAt: ISODate,
}

// POSTS collection
{
  _id: ObjectId,
  title: "Getting Started with MongoDB",
  slug: "getting-started-mongodb",  // URL-friendly, unique
  content: "Full markdown content here...",
  excerpt: "First 200 characters...",
  authorId: ObjectId,  // reference to users
  status: "published",  // draft, published, featured, archived
  tags: ["mongodb", "database", "tutorial"],
  category: "Backend",
  metadata: {
    readTime: 8,
    wordCount: 1500,
    featuredImage: "https://...",
  },
  stats: { views: 1520, likes: 42, comments: 8 },
  publishedAt: ISODate,
  createdAt: ISODate,
  updatedAt: ISODate,
}

// COMMENTS collection (separate — can grow unbounded)
{
  _id: ObjectId,
  postId: ObjectId,    // reference to posts
  authorId: ObjectId,  // reference to users
  parentId: ObjectId | null,  // null = top-level, ObjectId = reply
  content: "Great article!",
  likes: 5,
  createdAt: ISODate,
}

// ANALYTICS collection (high-volume writes — separate)
{
  _id: ObjectId,
  postId: ObjectId,
  date: "2024-08-01",   // one doc per post per day
  views: 145,
  uniqueVisitors: 89,
  avgReadTime: 4.2,
  referrers: { google: 50, twitter: 30, direct: 9 },
}
```

---

## PART 4: Indexes

## 66.9 Creating indexes

```javascript
// Single field (most common)
await db.collection("posts").createIndex({ slug: 1 }, { unique: true });
await db.collection("posts").createIndex({ authorId: 1 });
await db.collection("posts").createIndex({ createdAt: -1 });  // -1 = descending

// Compound index (multi-field — ORDER MATTERS)
await db.collection("posts").createIndex({ status: 1, createdAt: -1 });
// Supports: find({status: "published"}).sort({createdAt: -1})
// Does NOT help: find({createdAt: ...}) without status

// Text index (full-text search)
await db.collection("posts").createIndex(
  { title: "text", content: "text", tags: "text" },
  { weights: { title: 10, tags: 5, content: 1 } }  // title matches rank higher
);

// TTL index (auto-delete after time — great for sessions, logs)
await db.collection("sessions").createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 86400 }  // delete after 24 hours
);

// Partial index (only index documents matching a condition)
await db.collection("posts").createIndex(
  { publishedAt: -1 },
  { partialFilterExpression: { status: "published" } }
  // Only published posts are indexed — smaller + faster
);

// Check existing indexes
await db.collection("posts").indexes();

// Explain query (see if index is used)
await db.collection("posts")
  .find({ status: "published" })
  .sort({ createdAt: -1 })
  .explain("executionStats");
// Look for: "IXSCAN" (good!) vs "COLLSCAN" (bad — full collection scan)
```

---

## PART 5: Aggregation Pipeline

## 66.10 The aggregation framework (MongoDB's superpower)

```javascript
// Aggregation = chain of stages that transform documents
// Like Unix pipes: collection | $match | $group | $sort | $project → result

// Top authors by total likes
const topAuthors = await db.collection("posts").aggregate([
  { $match: { status: "published" } },                    // filter published only
  { $group: {
      _id: "$authorId",                                   // group by author
      totalLikes: { $sum: "$stats.likes" },               // sum all likes
      postCount: { $sum: 1 },                             // count posts
      avgReadTime: { $avg: "$metadata.readTime" },        // average read time
  }},
  { $sort: { totalLikes: -1 } },                          // most likes first
  { $limit: 10 },                                          // top 10
  { $lookup: {                                            // JOIN with users collection
      from: "users",
      localField: "_id",
      foreignField: "_id",
      as: "author",
  }},
  { $unwind: "$author" },                                  // flatten array to object
  { $project: {                                           // shape output
      _id: 0,
      name: "$author.profile.displayName",
      totalLikes: 1,
      postCount: 1,
      avgReadTime: { $round: ["$avgReadTime", 1] },
  }},
]).toArray();

// Posts per month (time-series)
const postsPerMonth = await db.collection("posts").aggregate([
  { $match: { status: "published" } },
  { $group: {
      _id: { $dateToString: { format: "%Y-%m", date: "$publishedAt" } },
      count: { $sum: 1 },
      totalViews: { $sum: "$stats.views" },
  }},
  { $sort: { _id: 1 } },
]).toArray();

// Tag popularity
const tagStats = await db.collection("posts").aggregate([
  { $match: { status: "published" } },
  { $unwind: "$tags" },               // explode array: one doc per tag
  { $group: {
      _id: "$tags",
      count: { $sum: 1 },
      avgLikes: { $avg: "$stats.likes" },
  }},
  { $sort: { count: -1 } },
  { $limit: 20 },
]).toArray();

// Full-text search with relevance scoring
const searchResults = await db.collection("posts").aggregate([
  { $match: { $text: { $search: "mongodb aggregation tutorial" } } },
  { $addFields: { relevance: { $meta: "textScore" } } },
  { $sort: { relevance: -1 } },
  { $limit: 10 },
  { $project: { title: 1, slug: 1, excerpt: 1, relevance: 1, tags: 1 } },
]).toArray();
```

---

## PART 6: Mongoose (Node.js ODM)

## 66.11 Schema + Model definition

```javascript
const mongoose = require("mongoose");

// User schema
const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true, lowercase: true, trim: true },
  email: { type: String, required: true, unique: true, lowercase: true },
  passwordHash: { type: String, required: true, select: false }, // excluded from queries by default
  role: { type: String, enum: ["admin", "author", "reader"], default: "reader" },
  profile: {
    displayName: String,
    bio: { type: String, maxlength: 500 },
    avatar: String,
  },
  stats: {
    postCount: { type: Number, default: 0 },
    totalLikes: { type: Number, default: 0 },
  },
}, { timestamps: true }); // auto-adds createdAt + updatedAt

// Post schema
const postSchema = new mongoose.Schema({
  title: { type: String, required: true, maxlength: 200 },
  slug: { type: String, required: true, unique: true },
  content: { type: String, required: true },
  excerpt: String,
  author: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  status: { type: String, enum: ["draft", "published", "featured", "archived"], default: "draft" },
  tags: [{ type: String, lowercase: true }],
  category: String,
  metadata: {
    readTime: Number,
    wordCount: Number,
    featuredImage: String,
  },
  stats: {
    views: { type: Number, default: 0 },
    likes: { type: Number, default: 0 },
    commentCount: { type: Number, default: 0 },
  },
  publishedAt: Date,
}, { timestamps: true });

// Indexes
postSchema.index({ slug: 1 }, { unique: true });
postSchema.index({ author: 1, status: 1 });
postSchema.index({ status: 1, publishedAt: -1 });
postSchema.index({ tags: 1 });
postSchema.index({ title: "text", content: "text", tags: "text" });

// Virtual (computed field — not stored)
postSchema.virtual("url").get(function () {
  return `/blog/${this.slug}`;
});

// Pre-save hook (auto-generate slug + excerpt)
postSchema.pre("save", function (next) {
  if (this.isModified("title")) {
    this.slug = this.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }
  if (this.isModified("content")) {
    this.excerpt = this.content.substring(0, 200) + "...";
    this.metadata.wordCount = this.content.split(/\s+/).length;
    this.metadata.readTime = Math.ceil(this.metadata.wordCount / 200);
  }
  next();
});

const User = mongoose.model("User", userSchema);
const Post = mongoose.model("Post", postSchema);
```

## 66.12 Queries with Mongoose

```javascript
// Find with populate (JOIN)
const posts = await Post.find({ status: "published" })
  .populate("author", "username profile.displayName profile.avatar")
  .sort({ publishedAt: -1 })
  .limit(10)
  .lean(); // .lean() returns plain objects (faster — no Mongoose overhead)

// Pagination helper
async function getPosts({ page = 1, limit = 10, status = "published", tag, search }) {
  const filter = { status };
  if (tag) filter.tags = tag;
  if (search) filter.$text = { $search: search };

  const [posts, total] = await Promise.all([
    Post.find(filter)
      .populate("author", "username profile.displayName")
      .sort({ publishedAt: -1 })
      .skip((page - 1) * limit)
      .limit(limit)
      .lean(),
    Post.countDocuments(filter),
  ]);

  return {
    posts,
    pagination: {
      page, limit, total,
      totalPages: Math.ceil(total / limit),
      hasNext: page * limit < total,
    },
  };
}
```

---

## Summary

✅ Document model: flexible schema, nested data, no joins needed for common access patterns
✅ CRUD: insert, find (with rich operators), update ($set, $inc, $push, $pull), delete
✅ Schema design: embed (always accessed together, bounded) vs reference (independent, unbounded)
✅ Indexes: single, compound, text, TTL, partial — explain() to verify usage
✅ Aggregation: $match → $group → $sort → $lookup (JOIN) → $project (the pipeline superpower)
✅ Mongoose: schema validation, virtuals, hooks, populate (reference resolution), lean queries
✅ Built: complete content platform schema (users, posts, comments, analytics)

## Key takeaways

**Schema design is THE most important decision.** A good MongoDB schema means most queries need zero joins (fast). A bad schema means you're fighting the database constantly. Design around your ACCESS PATTERNS, not your data relationships.

**Aggregation replaces 80% of what you'd use SQL for.** GROUP BY, JOIN, HAVING, window functions — aggregation pipeline does all of it. Learn it deeply; it's MongoDB's greatest strength.

**Indexes make or break performance.** Without an index, MongoDB scans every document (COLLSCAN). With one, it jumps directly to matching documents (IXSCAN). Always `explain()` your queries. If you see COLLSCAN on a large collection → add an index.

**Embed by default, reference when forced.** Start by putting everything in one document. Split into separate collections only when: data grows unbounded (16MB doc limit), data is accessed independently, or data changes frequently (avoid updating in many places).

---

→ [Back to Chapter 65: Local AI with Ollama](./65-LOCAL-AI-OLLAMA.md)
