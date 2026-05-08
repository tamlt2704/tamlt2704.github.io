# Chapter 12: Design Rideshare Matching (Uber)

[← Job Scheduler](./chapter-11-scheduler.md) | [Back to Overview →](./chapter-00-overview.md)

---

## The Question

> "Design Uber's real-time matching system. When a rider requests a ride, the system finds the best available driver nearby, calculates ETA, handles surge pricing, and manages the state machine for both drivers and riders throughout the trip lifecycle."

---

## Step 1: Requirements & Scope

**Functional:**
- Rider requests ride → system matches with nearest available driver
- Real-time driver location tracking (every 3-5 seconds)
- ETA calculation for pickup and destination
- Surge pricing based on supply/demand ratio
- Driver/rider state machines (available, matching, en-route, on-trip)

**Non-functional:**
- 20M rides/day, 5M concurrent drivers
- Match latency <5 seconds
- Location updates: 5M drivers × every 4 sec = 1.25M updates/sec
- High availability (ride requests must never fail)
- Geo-distributed (per-city deployment)

---

## Step 2: Estimation

| Metric | Calculation | Result |
|--------|-------------|--------|
| Ride requests/sec | 20M / 86400 | ~230 req/sec |
| Peak requests/sec | 230 × 5 (rush hour) | ~1,150 req/sec |
| Location updates/sec | 5M drivers / 4 sec | ~1.25M updates/sec |
| Active trips | avg 20 min × 230/sec | ~275,000 concurrent |
| Location storage | 5M × 100 bytes | ~500 MB (in-memory) |

---

## Step 3: API Design

```
POST /api/v1/rides/request
  Body: { "rider_id": "r_123", "pickup": { "lat": 37.7, "lng": -122.4 },
          "destination": { "lat": 37.8, "lng": -122.3 }, "ride_type": "uberx" }
  Response: { "ride_id": "ride_001", "status": "matching", "surge": 1.5 }

POST /api/v1/drivers/{driver_id}/location
  Body: { "lat": 37.7749, "lng": -122.4194, "timestamp": "..." }

POST /api/v1/rides/{ride_id}/accept   (driver accepts)
POST /api/v1/rides/{ride_id}/arrive   (driver arrived at pickup)
POST /api/v1/rides/{ride_id}/start    (trip started)
POST /api/v1/rides/{ride_id}/complete (trip ended)

GET /api/v1/rides/{ride_id}/eta
  Response: { "pickup_eta_min": 4, "trip_eta_min": 18 }
```

---

## Step 4: Data Model

**Rides (SQL):**

| Field | Type |
|-------|------|
| ride_id (PK) | UUID |
| rider_id | UUID |
| driver_id | UUID |
| status | ENUM (matching, accepted, arriving, in_progress, completed, cancelled) |
| pickup_location | POINT |
| destination | POINT |
| surge_multiplier | DECIMAL |
| fare_cents | INT |
| created_at | TIMESTAMP |

**Driver Locations (In-memory geospatial index — Redis GEO or custom):**

```
Key: drivers:available:{city}
Type: Geospatial index
Entry: (driver_id, latitude, longitude, timestamp)
```

---

## Step 5: High-Level Architecture

```
┌──────────┐                              ┌──────────┐
│  Rider   │                              │  Driver  │
│  App     │                              │  App     │
└────┬─────┘                              └────┬─────┘
     │                                         │
     │ request ride                            │ location updates (every 4s)
     ▼                                         ▼
┌──────────────┐                      ┌──────────────────┐
│ Ride Service │                      │ Location Service │
└──────┬───────┘                      └────────┬─────────┘
       │                                       │
       ▼                                       ▼
┌──────────────────┐              ┌──────────────────────┐
│ Matching Engine  │◀────────────▶│  Geospatial Index    │
└──────┬───────────┘              │  (Redis GEO / custom)│
       │                          └──────────────────────┘
       ▼
┌──────────────────┐              ┌──────────────────┐
│  Pricing Engine  │              │  ETA Service     │
│  (surge calc)    │              │  (routing/maps)  │
└──────────────────┘              └──────────────────┘
```

---

## Step 6: Deep Dive

### Geospatial Indexing

**Option A: Geohash**
- Encode lat/lng into string prefix (e.g., "9q8yyk")
- Nearby locations share prefix → range query on string index
- Precision: 6 chars ≈ 1.2 km × 0.6 km cell
- Query: find all drivers with geohash prefix matching rider's cell + neighbors

**Option B: Quadtree**
- Recursively divide space into 4 quadrants
- Leaf nodes contain driver lists
- Dynamic: subdivide when too many drivers in one cell
- Better for non-uniform distribution (dense cities)

**Option C: Redis GEOADD/GEORADIUS**
- Built-in geospatial commands
- `GEOADD drivers:available:sf driver_1 -122.4 37.7`
- `GEORADIUS drivers:available:sf -122.4 37.7 5 km COUNT 10`
- Simple, fast, good enough for most scales

### Real-Time Matching Algorithm

```
1. Rider requests ride at location L
2. Query geospatial index: find K nearest available drivers (K=10)
3. For each candidate driver:
   - Calculate ETA to pickup (routing service)
   - Check driver preferences (ride type, destination direction)
   - Score = f(distance, ETA, driver_rating, acceptance_rate)
4. Sort by score, offer to best driver
5. Driver has 15 seconds to accept
6. If declined/timeout → offer to next driver
7. If all K decline → expand radius, retry
```

### ETA Calculation

- **Simple:** Haversine distance / average speed (inaccurate)
- **Better:** Pre-computed road network graph + Dijkstra/A*
- **Best:** Historical travel time data by road segment, time of day, traffic
- Cache common routes. Update with real-time GPS data from active drivers.

### Surge Pricing

```
surge_multiplier = demand / supply

demand = ride_requests in cell in last 5 min
supply = available_drivers in cell

if surge > 1.0:
  fare = base_fare × surge_multiplier
```

- Calculated per geohash cell (or hexagonal grid)
- Updated every 1-2 minutes
- Capped at maximum (e.g., 5x)
- Smoothed to avoid oscillation (exponential moving average)

### Driver/Rider State Machines

```
DRIVER STATES:
  OFFLINE → AVAILABLE → MATCHING → EN_ROUTE_PICKUP → ON_TRIP → AVAILABLE
                ↑                                                    │
                └────────────────────────────────────────────────────┘

RIDER STATES:
  IDLE → REQUESTING → MATCHED → WAITING_PICKUP → ON_TRIP → IDLE
           │                                                  ▲
           └──── (timeout/cancel) ────────────────────────────┘
```

Each state transition triggers events: notifications, ETA updates, fare calculation.

---

## Step 7: Bottlenecks & Scaling

| Bottleneck | Solution |
|-----------|----------|
| 1.25M location updates/sec | Shard by city/region, in-memory index |
| Hot cells (airport, downtown) | Dedicated index partitions for hot areas |
| Matching latency | Pre-filter by geohash, limit candidates to K |
| ETA accuracy | ML model trained on historical trip data |
| Surge oscillation | Smoothing + minimum surge duration (5 min) |

**Per-city deployment:** Each city is an independent shard. Drivers don't cross city boundaries frequently. Simplifies scaling and reduces blast radius.

**Consistency:** Driver can only be in one state. Use optimistic locking on state transitions to prevent double-matching (two riders matched to same driver).

---

## Key Talking Points

- Geohash or quadtree for spatial indexing — trade-offs in uniformity vs adaptability
- Matching is a scoring problem, not just nearest-neighbor
- Surge pricing = simple supply/demand ratio per geographic cell
- State machines enforce valid transitions for both driver and rider
- Per-city sharding is natural and effective for rideshare

---

## Common Mistakes

- Linear scan of all drivers (no spatial index)
- Matching purely on distance without ETA (a nearby driver across a river is far)
- Not handling the case where no drivers are available
- Surge pricing without smoothing (causes oscillation)
- Single global deployment (latency for location updates)
- Not preventing double-matching (race condition on driver assignment)

---

[← Job Scheduler](./chapter-11-scheduler.md) | [Back to Overview →](./chapter-00-overview.md)
