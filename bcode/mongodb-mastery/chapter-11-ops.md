# Chapter 11: Security & Ops

[← Ch 10](chapter-10-performance.md) | [Ch 12 →](chapter-12-integration.md)

---

## The Problem

> **Priya:** "We're going to production. The security team wants authentication, role-based access, encrypted connections, automated backups, and monitoring dashboards. No more `mongod` with no auth on port 27017."

Production MongoDB means locking down access, setting up replication for high availability, and monitoring everything.

---

## Authentication — SCRAM

SCRAM-SHA-256 is the default authentication mechanism.

```javascript
// Connect to admin database
use admin

// Create admin user
db.createUser({
  user: "admin",
  pwd: "securePassword123!",
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
})

// Create application user with limited access
use docuflow
db.createUser({
  user: "docuflow_app",
  pwd: "appSecret456!",
  roles: [
    { role: "readWrite", db: "docuflow" },
    { role: "read", db: "analytics" }
  ]
})

// Connect with auth
// mongosh "mongodb://docuflow_app:appSecret456!@localhost:27017/docuflow"
```

Enable auth in `mongod.conf`:

```yaml
security:
  authorization: enabled
```

---

## Authentication — x.509 Certificates

For service-to-service auth without passwords:

```javascript
// Create user authenticated by certificate subject
db.getSiblingDB("$external").createUser({
  user: "CN=docuflow-api,O=DocuFlow,ST=CA,C=US",
  roles: [{ role: "readWrite", db: "docuflow" }]
})
```

Connection string:

```
mongodb://host:27017/?authMechanism=MONGODB-X509&tls=true&tlsCertificateKeyFile=/path/to/client.pem
```

---

## Authorization — Roles and Privileges

```javascript
// Built-in roles
// read, readWrite, dbAdmin, userAdmin, clusterAdmin, root

// Custom role: can read contracts but only update status field
db.createRole({
  role: "contractReviewer",
  privileges: [
    {
      resource: { db: "docuflow", collection: "contracts" },
      actions: ["find"]
    },
    {
      resource: { db: "docuflow", collection: "contracts" },
      actions: ["update"],
      // Note: field-level restriction requires app-level enforcement
    }
  ],
  roles: []
})

// Assign custom role
db.createUser({
  user: "reviewer_bot",
  pwd: "reviewPass!",
  roles: [{ role: "contractReviewer", db: "docuflow" }]
})

// View user roles
db.getUser("docuflow_app")

// Grant additional role
db.grantRolesToUser("docuflow_app", [{ role: "dbAdmin", db: "docuflow" }])
```

---

## Replica Sets — High Availability

A replica set: one primary (writes), secondaries (reads/failover), optional arbiter (voting).

```javascript
// Initiate replica set (run on primary)
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017", priority: 2 },
    { _id: 1, host: "mongo2:27017", priority: 1 },
    { _id: 2, host: "mongo3:27017", priority: 1 }
  ]
})

// Check status
rs.status()

// Add a member
rs.add("mongo4:27017")

// Add an arbiter (votes but holds no data)
rs.addArb("arbiter1:27017")

// Step down primary (trigger election)
rs.stepDown()
```

Connection string for replica set:

```
mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0
```

---

## Backup — mongodump / mongorestore

```bash
# Full backup
mongodump --uri="mongodb://admin:pass@localhost:27017" --out=/backups/$(date +%Y%m%d)

# Single database
mongodump --db=docuflow --out=/backups/docuflow_backup

# Restore
mongorestore --uri="mongodb://admin:pass@localhost:27017" /backups/20240115/

# Restore single collection
mongorestore --db=docuflow --collection=contracts /backups/docuflow/contracts.bson
```

**Atlas Backup** (managed):

```javascript
// Atlas provides:
// - Continuous backup with point-in-time recovery
// - Scheduled snapshots (hourly, daily, weekly)
// - Cross-region backup storage
// - One-click restore to any point in time

// Check backup status via Atlas CLI:
// atlas backups list --projectId <id>
```

---

## Monitoring

### Atlas Metrics (managed)

Atlas provides dashboards for: operations/sec, query targeting, connections, disk I/O, replication lag, and index hit ratio.

### Self-Hosted Monitoring

```bash
# Real-time stats (like top for MongoDB)
mongostat --uri="mongodb://admin:pass@localhost:27017"

# Per-collection stats
mongotop --uri="mongodb://admin:pass@localhost:27017"
```

```javascript
// Server status (comprehensive)
db.serverStatus()

// Key metrics to watch
const status = db.serverStatus();
print("Connections:", status.connections.current);
print("Opcounters:", JSON.stringify(status.opcounters));
print("Replication lag:", rs.printSecondaryReplicationInfo());

// Collection-level stats
db.contracts.stats()

// Current operations
db.currentOp({ active: true, secs_running: { $gt: 2 } })
```

---

## Connection String Options

```
mongodb://user:pass@host1:27017,host2:27017,host3:27017/docuflow?
  replicaSet=rs0&
  authSource=admin&
  tls=true&
  tlsCAFile=/path/to/ca.pem&
  retryWrites=true&
  w=majority&
  readPreference=secondaryPreferred&
  maxPoolSize=50&
  connectTimeoutMS=10000&
  serverSelectionTimeoutMS=5000
```

| Option | Purpose |
|---|---|
| `replicaSet` | Name of replica set |
| `tls=true` | Encrypt connections |
| `retryWrites=true` | Auto-retry on network errors |
| `w=majority` | Write to majority of nodes |
| `readPreference` | Where to route reads |
| `maxPoolSize` | Connection pool limit |

---

## Security Checklist

```javascript
// 1. Auth enabled?
db.adminCommand({ getParameter: 1, authenticationMechanisms: 1 })

// 2. No default/test users?
db.getUsers()

// 3. Network binding (not 0.0.0.0 in production)
db.adminCommand({ getCmdLineOpts: 1 })

// 4. Audit log enabled? (Enterprise)
db.adminCommand({ getParameter: 1, auditLog: 1 })
```

---

## Node.js Example — Secure Connection

```javascript
const { MongoClient } = require('mongodb');

const client = new MongoClient(
  'mongodb+srv://docuflow_app:secret@cluster0.abc.mongodb.net/docuflow', {
    tls: true,
    retryWrites: true,
    w: 'majority',
    maxPoolSize: 50,
    serverSelectionTimeoutMS: 5000
  }
);

async function healthCheck() {
  const admin = client.db().admin();
  const status = await admin.serverStatus();
  console.log(`Connections: ${status.connections.current}/${status.connections.available}`);
  console.log(`Uptime: ${Math.floor(status.uptime / 3600)}h`);
}
```

---

## What You Learned

- SCRAM-SHA-256 for password auth, x.509 for certificate-based service auth
- Custom roles restrict access to specific databases, collections, and actions
- Replica sets provide automatic failover (primary → secondary promotion)
- `mongodump`/`mongorestore` for self-hosted backups; Atlas has continuous backup
- `mongostat`, `mongotop`, and `db.serverStatus()` for monitoring
- Connection strings encode auth, TLS, pool size, and read/write preferences
- Always enable auth, TLS, and bind to specific IPs in production

---

[← Ch 10: Performance](chapter-10-performance.md) | [Ch 12: Integration →](chapter-12-integration.md)
