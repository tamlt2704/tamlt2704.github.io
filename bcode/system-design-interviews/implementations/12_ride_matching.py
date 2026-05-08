"""
Ride Matching — Core Implementation
=====================================
Demonstrates: Geohash encoding/decoding, spatial index, nearest-driver
matching, ETA estimation, surge pricing.

In a real system:
- Spatial index: Redis GEO commands (GEOADD, GEORADIUS) backed by sorted set
- Matching: dispatch service queries nearby drivers, ranks by ETA + rating
- ETA: OSRM or Google Maps Directions API (real road network routing)
- Surge: real-time demand/supply ratio per geohash cell, updated every minute
- Driver locations: streamed via Kafka, indexed in Redis with TTL
"""

import math
import time
from dataclasses import dataclass, field
from typing import Optional


# ─── Geohash Encoding/Decoding ───────────────────────────────────────────────

# Base32 alphabet used by geohash
GEOHASH_CHARS = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash_encode(lat: float, lon: float, precision: int = 6) -> str:
    """
    Encode lat/lon into a geohash string.
    Each character narrows the bounding box. Nearby points share prefixes.

    Precision 6 ≈ 1.2km × 0.6km cell — good for ride matching.
    """
    lat_range = (-90.0, 90.0)
    lon_range = (-180.0, 180.0)
    bits = 0
    bit_count = 0
    geohash = []
    is_lon = True  # Alternate between lon and lat bits

    while len(geohash) < precision:
        if is_lon:
            mid = (lon_range[0] + lon_range[1]) / 2
            if lon >= mid:
                bits = (bits << 1) | 1
                lon_range = (mid, lon_range[1])
            else:
                bits = (bits << 1) | 0
                lon_range = (lon_range[0], mid)
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat >= mid:
                bits = (bits << 1) | 1
                lat_range = (mid, lat_range[1])
            else:
                bits = (bits << 1) | 0
                lat_range = (lat_range[0], mid)

        is_lon = not is_lon
        bit_count += 1

        if bit_count == 5:
            geohash.append(GEOHASH_CHARS[bits])
            bits = 0
            bit_count = 0

    return "".join(geohash)


def geohash_decode(geohash: str) -> tuple[float, float]:
    """Decode a geohash string back to approximate lat/lon (center of cell)."""
    lat_range = (-90.0, 90.0)
    lon_range = (-180.0, 180.0)
    is_lon = True

    for char in geohash:
        idx = GEOHASH_CHARS.index(char)
        for bit in range(4, -1, -1):
            if is_lon:
                mid = (lon_range[0] + lon_range[1]) / 2
                if (idx >> bit) & 1:
                    lon_range = (mid, lon_range[1])
                else:
                    lon_range = (lon_range[0], mid)
            else:
                mid = (lat_range[0] + lat_range[1]) / 2
                if (idx >> bit) & 1:
                    lat_range = (mid, lat_range[1])
                else:
                    lat_range = (lat_range[0], mid)
            is_lon = not is_lon

    lat = (lat_range[0] + lat_range[1]) / 2
    lon = (lon_range[0] + lon_range[1]) / 2
    return lat, lon


def geohash_neighbors(geohash: str) -> list[str]:
    """Get the 8 neighboring geohash cells (for boundary queries)."""
    lat, lon = geohash_decode(geohash)
    precision = len(geohash)
    # Approximate cell size at this precision
    dlat = 180.0 / (2 ** (precision * 5 // 2))
    dlon = 360.0 / (2 ** (precision * 5 // 2 + precision * 5 % 2))

    neighbors = []
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dy == 0 and dx == 0:
                continue
            nlat = lat + dy * dlat
            nlon = lon + dx * dlon
            if -90 <= nlat <= 90 and -180 <= nlon <= 180:
                neighbors.append(geohash_encode(nlat, nlon, precision))
    return neighbors


# ─── Distance Calculations ────────────────────────────────────────────────────

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two points."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def manhattan_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Manhattan distance approximation (better for city grids)."""
    km_per_lat = 111.0
    km_per_lon = 111.0 * math.cos(math.radians((lat1 + lat2) / 2))
    return abs(lat2 - lat1) * km_per_lat + abs(lon2 - lon1) * km_per_lon


# ─── Driver & Ride Models ────────────────────────────────────────────────────

@dataclass
class Driver:
    id: str
    lat: float
    lon: float
    available: bool = True
    rating: float = 4.8
    geohash: str = field(init=False)

    def __post_init__(self):
        self.geohash = geohash_encode(self.lat, self.lon, precision=6)


@dataclass
class RideRequest:
    rider_id: str
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    timestamp: float = field(default_factory=time.time)


# ─── Spatial Index ────────────────────────────────────────────────────────────

class SpatialIndex:
    """
    Geohash-based spatial index for finding nearby drivers.
    Maps geohash prefix → set of drivers in that cell.

    Production: Redis GEO (GEOADD + GEORADIUS) or PostGIS.
    """

    def __init__(self, precision: int = 6):
        self.precision = precision
        self.cells: dict[str, set[str]] = {}  # geohash → driver IDs
        self.drivers: dict[str, Driver] = {}

    def update_driver(self, driver: Driver):
        """Update driver location in the index."""
        # Remove from old cell
        if driver.id in self.drivers:
            old_hash = self.drivers[driver.id].geohash
            if old_hash in self.cells:
                self.cells[old_hash].discard(driver.id)

        # Add to new cell
        driver.geohash = geohash_encode(driver.lat, driver.lon, self.precision)
        self.drivers[driver.id] = driver
        if driver.geohash not in self.cells:
            self.cells[driver.geohash] = set()
        self.cells[driver.geohash].add(driver.id)

    def find_nearby(self, lat: float, lon: float, radius_km: float = 3.0) -> list[Driver]:
        """Find available drivers within radius. Searches cell + neighbors."""
        center_hash = geohash_encode(lat, lon, self.precision)
        search_cells = [center_hash] + geohash_neighbors(center_hash)

        candidates = []
        for cell in search_cells:
            for driver_id in self.cells.get(cell, set()):
                driver = self.drivers[driver_id]
                if not driver.available:
                    continue
                dist = haversine_distance(lat, lon, driver.lat, driver.lon)
                if dist <= radius_km:
                    candidates.append((dist, driver))

        candidates.sort(key=lambda x: x[0])
        return [d for _, d in candidates]


# ─── Matching Algorithm ──────────────────────────────────────────────────────

def estimate_eta(driver: Driver, pickup_lat: float, pickup_lon: float,
                 avg_speed_kmh: float = 30.0) -> float:
    """ETA in minutes using Manhattan distance (city grid approximation)."""
    dist = manhattan_distance_km(driver.lat, driver.lon, pickup_lat, pickup_lon)
    return (dist / avg_speed_kmh) * 60  # Convert to minutes


def match_ride(index: SpatialIndex, request: RideRequest,
               max_radius_km: float = 5.0) -> Optional[tuple[Driver, float]]:
    """
    Match a ride request to the nearest available driver.
    Returns (driver, eta_minutes) or None.

    Production: considers ETA, driver rating, acceptance rate, vehicle type.
    """
    nearby = index.find_nearby(request.pickup_lat, request.pickup_lon, max_radius_km)
    if not nearby:
        return None

    # Score by ETA (nearest first, could also factor in rating)
    best_driver = None
    best_eta = float('inf')
    for driver in nearby:
        eta = estimate_eta(driver, request.pickup_lat, request.pickup_lon)
        if eta < best_eta:
            best_eta = eta
            best_driver = driver

    if best_driver:
        best_driver.available = False  # Claim the driver
        return best_driver, best_eta
    return None


# ─── Surge Pricing ────────────────────────────────────────────────────────────

class SurgePricing:
    """
    Dynamic pricing based on demand/supply ratio per area.
    Surge multiplier = demand / supply (clamped to range).

    Production: computed per geohash cell every 1-2 minutes.
    """

    def __init__(self, base_rate: float = 2.0, min_multiplier: float = 1.0,
                 max_multiplier: float = 5.0):
        self.base_rate = base_rate  # $/km
        self.min_mult = min_multiplier
        self.max_mult = max_multiplier
        self.demand: dict[str, int] = {}  # geohash → request count
        self.supply: dict[str, int] = {}  # geohash → available drivers

    def record_demand(self, lat: float, lon: float):
        gh = geohash_encode(lat, lon, precision=4)  # Coarser for pricing
        self.demand[gh] = self.demand.get(gh, 0) + 1

    def record_supply(self, lat: float, lon: float):
        gh = geohash_encode(lat, lon, precision=4)
        self.supply[gh] = self.supply.get(gh, 0) + 1

    def get_multiplier(self, lat: float, lon: float) -> float:
        gh = geohash_encode(lat, lon, precision=4)
        demand = self.demand.get(gh, 1)
        supply = max(self.supply.get(gh, 1), 1)
        ratio = demand / supply
        return min(max(ratio, self.min_mult), self.max_mult)

    def estimate_fare(self, pickup_lat: float, pickup_lon: float,
                      dropoff_lat: float, dropoff_lon: float) -> dict:
        dist = manhattan_distance_km(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
        multiplier = self.get_multiplier(pickup_lat, pickup_lon)
        base_fare = dist * self.base_rate
        return {
            "distance_km": round(dist, 2),
            "base_fare": round(base_fare, 2),
            "surge_multiplier": round(multiplier, 2),
            "total_fare": round(base_fare * multiplier, 2),
        }


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Ride Matching Demo ===\n")

    # --- Geohash ---
    print("--- Geohash Encoding ---")
    locations = [
        ("Times Square NYC", 40.7580, -73.9855),
        ("Central Park", 40.7829, -73.9654),
        ("Brooklyn Bridge", 40.7061, -73.9969),
    ]
    for name, lat, lon in locations:
        gh = geohash_encode(lat, lon, precision=7)
        decoded = geohash_decode(gh)
        print(f"  {name:<18} ({lat:.4f}, {lon:.4f}) → '{gh}'")
    # Show prefix sharing
    gh1 = geohash_encode(40.7580, -73.9855, 7)
    gh2 = geohash_encode(40.7590, -73.9850, 7)
    shared = 0
    for a, b in zip(gh1, gh2):
        if a == b:
            shared += 1
        else:
            break
    print(f"  Nearby points share {shared} prefix chars → same cell at lower precision")

    # --- Spatial Index & Matching ---
    print("\n--- Spatial Index & Matching ---")
    index = SpatialIndex(precision=6)

    # Place drivers around Manhattan
    drivers = [
        Driver("d1", 40.7580, -73.9855),  # Times Square
        Driver("d2", 40.7614, -73.9776),  # Near Rockefeller
        Driver("d3", 40.7484, -73.9857),  # Near Penn Station
        Driver("d4", 40.7831, -73.9712),  # Upper West Side
        Driver("d5", 40.7282, -73.7949, available=False),  # Queens (unavailable)
    ]
    for d in drivers:
        index.update_driver(d)

    # Rider requests pickup near Bryant Park
    request = RideRequest("rider_1", 40.7536, -73.9832, 40.7061, -73.9969)
    nearby = index.find_nearby(request.pickup_lat, request.pickup_lon, radius_km=2.0)
    print(f"  Drivers within 2km of Bryant Park: {len(nearby)}")
    for d in nearby:
        dist = haversine_distance(request.pickup_lat, request.pickup_lon, d.lat, d.lon)
        eta = estimate_eta(d, request.pickup_lat, request.pickup_lon)
        print(f"    {d.id}: {dist:.2f}km away, ETA {eta:.1f}min")

    # Match best driver
    result = match_ride(index, request)
    if result:
        driver, eta = result
        print(f"\n  ✓ Matched: {driver.id} (ETA: {eta:.1f} min)")

    # --- Surge Pricing ---
    print("\n--- Surge Pricing ---")
    surge = SurgePricing(base_rate=2.50)

    # Simulate high demand in Times Square area
    for _ in range(20):
        surge.record_demand(40.758, -73.985)
    for _ in range(5):
        surge.record_supply(40.758, -73.985)

    # Normal demand in Upper West Side
    for _ in range(3):
        surge.record_demand(40.783, -73.971)
    for _ in range(8):
        surge.record_supply(40.783, -73.971)

    fare_surge = surge.estimate_fare(40.758, -73.985, 40.706, -73.997)
    fare_normal = surge.estimate_fare(40.783, -73.971, 40.706, -73.997)

    print(f"  Times Square (high demand):")
    print(f"    Distance: {fare_surge['distance_km']}km")
    print(f"    Surge: {fare_surge['surge_multiplier']}x")
    print(f"    Fare: ${fare_surge['total_fare']}")
    print(f"  Upper West Side (normal):")
    print(f"    Distance: {fare_normal['distance_km']}km")
    print(f"    Surge: {fare_normal['surge_multiplier']}x")
    print(f"    Fare: ${fare_normal['total_fare']}")

    # --- Distance comparison ---
    print("\n--- Distance Methods ---")
    lat1, lon1 = 40.7580, -73.9855  # Times Square
    lat2, lon2 = 40.7061, -73.9969  # Brooklyn Bridge
    hav = haversine_distance(lat1, lon1, lat2, lon2)
    man = manhattan_distance_km(lat1, lon1, lat2, lon2)
    print(f"  Times Square → Brooklyn Bridge:")
    print(f"    Haversine (straight): {hav:.2f}km")
    print(f"    Manhattan (grid):     {man:.2f}km")
    print(f"    → Manhattan better approximates actual driving distance")
