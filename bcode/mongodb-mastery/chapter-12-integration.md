# Chapter 12: With Your Stack

[← Ch 11](chapter-11-ops.md) | [README →](README.md)

---

## The Problem

> **Priya:** "We've mastered mongosh. Now we need to connect from our actual services — Node.js for the API, Python for the data pipeline, and the Java team wants Spring Data. Each needs connection pooling, error handling, and retry logic."

The shell is for exploration. Production code uses drivers with schemas, middleware, and proper error handling.

---

## Mongoose (Node.js) — Schema + Middleware

### Connection

```javascript
const mongoose = require('mongoose');

mongoose.connect('mongodb://localhost:27017/docuflow', {
  maxPoolSize: 50,
  serverSelectionTimeoutMS: 5000,
  retryWrites: true
});

mongoose.connection.on('connected', () => console.log('MongoDB connected'));
mongoose.connection.on('error', (err) => console.error('MongoDB error:', err));
```

### Schema Definition

```javascript
const contractSchema = new mongoose.Schema({
  title: { type: String, required: true, index: true },
  client: { type: String, required: true },
  status: {
    type: String,
    enum: ['draft', 'pending', 'active', 'signed', 'expired'],
    default: 'draft'
  },
  value: { type: Number, min: 0 },
  orgId: { type: mongoose.Schema.Types.ObjectId, ref: 'Organization' },
  clauses: [{
    text: { type: String, required: true },
    type: { type: String, required: true }
  }],
  signatures: [{
    name: String,
    role: { type: String, enum: ['client', 'vendor'] },
    signedAt: Date
  }],
  metadata: { type: Map, of: mongoose.Schema.Types.Mixed }
}, { timestamps: true });

// Compound index
contractSchema.index({ status: 1, createdAt: -1 });

const Contract = mongoose.model('Contract', contractSchema);
```

### Middleware (Hooks)

```javascript
// Pre-save: auto-set version
contractSchema.pre('save', function(next) {
  if (this.isModified('clauses')) {
    this.version = (this.version || 0) + 1;
  }
  next();
});

// Post-save: audit log
contractSchema.post('save', function(doc) {
  console.log(`[AUDIT] Contract ${doc._id} saved — status: ${doc.status}`);
});

// Pre-find: exclude expired by default
contractSchema.pre('find', function() {
  if (!this.getQuery().status) {
    this.where({ status: { $ne: 'expired' } });
  }
});
```

### CRUD with Mongoose

```javascript
// Create
const contract = await Contract.create({
  title: 'Enterprise License',
  client: 'Acme Corp',
  status: 'draft',
  value: 48000,
  clauses: [{ text: 'Net 30 payment', type: 'payment' }]
});

// Read with populate (JOIN)
const contracts = await Contract.find({ status: 'active' })
  .populate('orgId', 'name plan')
  .sort({ createdAt: -1 })
  .limit(20)
  .lean();  // Returns plain objects (faster)

// Update
await Contract.findByIdAndUpdate(contract._id, {
  $set: { status: 'signed' },
  $push: { signatures: { name: 'Jane', role: 'client', signedAt: new Date() } }
}, { new: true, runValidators: true });

// Delete
await Contract.deleteMany({ status: 'expired', createdAt: { $lt: oneYearAgo } });
```

---

## PyMongo (Python) — With Type Hints

### Connection

```python
from pymongo import MongoClient, errors
from pymongo.read_preferences import ReadPreference
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

client = MongoClient(
    "mongodb://localhost:27017",
    maxPoolSize=50,
    serverSelectionTimeoutMS=5000,
    retryWrites=True
)
db = client.docuflow
```

### Typed Data Classes

```python
@dataclass
class Clause:
    text: str
    type: str

@dataclass
class Contract:
    title: str
    client: str
    status: str
    value: float
    clauses: list[Clause]
    created_at: datetime
    _id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "client": self.client,
            "status": self.status,
            "value": self.value,
            "clauses": [{"text": c.text, "type": c.type} for c in self.clauses],
            "createdAt": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Contract":
        return cls(
            _id=str(data.get("_id")),
            title=data["title"],
            client=data["client"],
            status=data["status"],
            value=data["value"],
            clauses=[Clause(**c) for c in data.get("clauses", [])],
            created_at=data["createdAt"]
        )
```

### CRUD with Error Handling

```python
def create_contract(contract: Contract) -> str:
    try:
        result = db.contracts.insert_one(contract.to_dict())
        return str(result.inserted_id)
    except errors.DuplicateKeyError:
        raise ValueError("Contract already exists")
    except errors.ServerSelectionTimeoutError:
        raise ConnectionError("Database unavailable")

def find_active_contracts(limit: int = 20) -> list[Contract]:
    cursor = db.contracts.find(
        {"status": "active"},
        {"clauses": 0}  # Exclude large field
    ).sort("createdAt", -1).limit(limit)

    return [Contract.from_dict(doc) for doc in cursor]

def update_status(contract_id: str, new_status: str) -> bool:
    from bson import ObjectId
    result = db.contracts.update_one(
        {"_id": ObjectId(contract_id)},
        {"$set": {"status": new_status, "updatedAt": datetime.now()}}
    )
    return result.modified_count > 0
```

---

## Spring Data MongoDB (Java) — Repository Pattern

### Configuration

```java
@Configuration
public class MongoConfig extends AbstractMongoClientConfiguration {
    @Override
    protected String getDatabaseName() { return "docuflow"; }

    @Override
    public MongoClient mongoClient() {
        return MongoClients.create(MongoClientSettings.builder()
            .applyConnectionString(new ConnectionString(
                "mongodb://localhost:27017/docuflow"))
            .applyToConnectionPoolSettings(builder ->
                builder.maxSize(50).minSize(5))
            .retryWrites(true)
            .build());
    }
}
```

### Document Model

```java
@Document(collection = "contracts")
public class Contract {
    @Id private String id;
    @Indexed private String title;
    private String client;
    private String status;
    private double value;
    private List<Clause> clauses;
    private List<Signature> signatures;
    @CreatedDate private Instant createdAt;
    @LastModifiedDate private Instant updatedAt;
}
```

### Repository

```java
public interface ContractRepository extends MongoRepository<Contract, String> {
    List<Contract> findByStatus(String status);
    List<Contract> findByClientAndValueGreaterThan(String client, double value);

    @Query("{ 'status': ?0, 'value': { $gt: ?1 } }")
    List<Contract> findActiveHighValue(String status, double minValue);

    @Query(value = "{ 'status': 'active' }", sort = "{ 'createdAt': -1 }")
    Page<Contract> findActiveContracts(Pageable pageable);
}
```

### Service with Error Handling

```java
@Service
public class ContractService {
    @Autowired private ContractRepository repo;
    @Autowired private MongoTemplate mongoTemplate;

    @Retryable(value = MongoException.class, maxAttempts = 3)
    public Contract create(Contract contract) {
        contract.setStatus("draft");
        return repo.save(contract);
    }

    public long countByStatus(String status) {
        Query query = new Query(Criteria.where("status").is(status));
        return mongoTemplate.count(query, Contract.class);
    }
}
```

---

## Retry Logic Pattern

```javascript
// Node.js — exponential backoff
async function withRetry(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === maxRetries) throw err;
      if (err.code === 11600 || err.message.includes('not primary')) {
        const delay = Math.pow(2, attempt) * 100;
        await new Promise(r => setTimeout(r, delay));
        continue;
      }
      throw err; // Non-retryable error
    }
  }
}

// Usage
const contract = await withRetry(() =>
  Contract.findByIdAndUpdate(id, update, { new: true })
);
```

---

## Connection Pooling Best Practices

| Setting | Development | Production |
|---|---|---|
| `maxPoolSize` | 5 | 50-100 |
| `minPoolSize` | 1 | 5-10 |
| `maxIdleTimeMS` | 60000 | 30000 |
| `connectTimeoutMS` | 30000 | 10000 |
| `serverSelectionTimeoutMS` | 30000 | 5000 |

> **One client per application.** Don't create a new `MongoClient` per request.

---

## What You Learned

- **Mongoose** (Node.js): schemas with validation, middleware hooks, `populate()` for JOINs, `.lean()` for performance
- **PyMongo** (Python): dataclasses for type safety, explicit error handling, connection pooling
- **Spring Data** (Java): `@Document` annotations, repository pattern, `@Query` for custom queries
- Retry logic with exponential backoff for transient failures
- One `MongoClient` instance per app — reuse the connection pool
- Always handle `ServerSelectionTimeoutError` and `DuplicateKeyError`

---

[← Ch 11: Security & Ops](chapter-11-ops.md) | [README →](README.md)
