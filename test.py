"""Kaggriculture agent — LP + Monte Carlo Simulation + Hidden Markov Opponent Model.

Architecture:
1. HMM Opponent Model: Infers opponent strategy state from observable farm
2. Monte Carlo Price Simulator: Predicts future prices given both players' production
3. LP Planner: Solves crop/animal allocation using MC-predicted prices
4. Task Scheduler: BFS pathfinding + greedy worker assignment
5. Market Engine: Sell timing informed by price predictions
"""

from collections import deque
import random as _random

# ─── Game Constants ──────────────────────────────────────────────────────────

CROPS = {
    "WHEAT": {"seed": 10, "first_yield_day": 2, "max_yield_day": 4, "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT": {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO": {"seed": 50, "first_yield_day": 8, "max_yield_day": 8, "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON": {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}

ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP", "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW": {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
TOTAL_DAYS = 30
TURNS_PER_DAY = 24
LAND_PRICES = [1000, 2000, 4000]
MARKET_I0 = 10000

# Shops and their products (for demand prediction)
SHOPS = {
    "BAKERY": ["EGG", "WHEAT"],
    "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE": ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# HIDDEN MARKOV OPPONENT MODEL
# ═══════════════════════════════════════════════════════════════════════════════
# States: CROPS_ONLY, MIXED (crops+animals), ANIMALS_HEAVY, PASSIVE
# Observations: opponent's visible farm state (plants, structures, money changes)

class OpponentModel:
    """HMM-based opponent strategy predictor."""

    # Hidden states
    STATES = ["CROPS_ONLY", "MIXED", "ANIMALS_HEAVY", "PASSIVE"]

    # Transition probabilities (rows=from, cols=to)
    # Most opponents stick with their strategy, occasionally adapt
    TRANSITIONS = {
        "CROPS_ONLY":    {"CROPS_ONLY": 0.7, "MIXED": 0.2, "ANIMALS_HEAVY": 0.05, "PASSIVE": 0.05},
        "MIXED":         {"CROPS_ONLY": 0.1, "MIXED": 0.7, "ANIMALS_HEAVY": 0.15, "PASSIVE": 0.05},
        "ANIMALS_HEAVY": {"CROPS_ONLY": 0.05, "MIXED": 0.15, "ANIMALS_HEAVY": 0.7, "PASSIVE": 0.1},
        "PASSIVE":       {"CROPS_ONLY": 0.1, "MIXED": 0.1, "ANIMALS_HEAVY": 0.05, "PASSIVE": 0.75},
    }

    def __init__(self):
        # Belief state: probability of each hidden state
        self.belief = {"CROPS_ONLY": 0.4, "MIXED": 0.3, "ANIMALS_HEAVY": 0.1, "PASSIVE": 0.2}
        self.prev_opp_money = 3000
        self.prev_opp_plants = 0
        self.prev_opp_animals = 0

    def update(self, opp_farm):
        """Update belief based on observable opponent state."""
        plants = sum(1 for row in opp_farm["tiles"] for t in row
                     if isinstance(t, dict) and t.get("kind") == "PLANT")
        animals = sum(1 for row in opp_farm["tiles"] for t in row
                      if isinstance(t, dict) and "animal" in t)
        structures = sum(1 for row in opp_farm["tiles"] for t in row
                        if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and "animal" not in t)
        money = opp_farm["money"]
        quadrants = len(opp_farm.get("unlocked_quadrants", []))

        # Emission probabilities: P(observation | state)
        emissions = {}
        emissions["CROPS_ONLY"] = self._emit_crops_only(plants, animals, structures)
        emissions["MIXED"] = self._emit_mixed(plants, animals, structures)
        emissions["ANIMALS_HEAVY"] = self._emit_animals_heavy(plants, animals, structures)
        emissions["PASSIVE"] = self._emit_passive(plants, animals, money)

        # Forward step: belief' = normalize(emission * sum(transition * belief))
        new_belief = {}
        for state in self.STATES:
            predicted = sum(self.TRANSITIONS[prev][state] * self.belief[prev] for prev in self.STATES)
            new_belief[state] = predicted * emissions[state]

        # Normalize
        total = sum(new_belief.values())
        if total > 0:
            self.belief = {s: v / total for s, v in new_belief.items()}

        self.prev_opp_money = money
        self.prev_opp_plants = plants
        self.prev_opp_animals = animals

    def _emit_crops_only(self, plants, animals, structures):
        if animals == 0 and structures == 0:
            return 0.8 if plants > 3 else 0.4
        return 0.1

    def _emit_mixed(self, plants, animals, structures):
        if plants > 0 and (animals > 0 or structures > 0):
            return 0.7
        return 0.2

    def _emit_animals_heavy(self, plants, animals, structures):
        if animals >= 2 or structures >= 3:
            return 0.7
        if animals >= 1:
            return 0.4
        return 0.1

    def _emit_passive(self, plants, animals, money):
        if plants <= 1 and animals == 0 and money > 2500:
            return 0.7
        return 0.1

    def predict_production(self, opp_farm, days_ahead=5):
        """Predict opponent's likely production over next N days by product."""
        production = {p: 0.0 for p in PRODUCTS}

        # Count their crops about to yield
        for row in opp_farm["tiles"]:
            for tile in row:
                if not isinstance(tile, dict):
                    continue
                if tile.get("kind") == "PLANT":
                    crop_name = tile.get("crop", "")
                    if crop_name in CROPS:
                        crop = CROPS[crop_name]
                        # Estimate yield coming in next N days
                        if crop["ongoing"]:
                            production[crop_name] += 1.0 * days_ahead / max(1, crop["interval"])
                        else:
                            production[crop_name] += crop["max_yield"] * 0.5
                elif "animal" in tile:
                    animal_name = tile["animal"]
                    if animal_name in ANIMALS:
                        product = ANIMALS[animal_name]["product"]
                        interval = ANIMALS[animal_name]["interval"]
                        production[product] += days_ahead / max(1, interval)

        # Scale by strategy belief — aggressive opponents sell faster
        sell_speed = (self.belief["CROPS_ONLY"] * 0.8 +
                     self.belief["MIXED"] * 0.6 +
                     self.belief["ANIMALS_HEAVY"] * 0.5 +
                     self.belief["PASSIVE"] * 0.3)

        return {p: v * sell_speed for p, v in production.items()}

    def most_likely_state(self):
        return max(self.belief, key=self.belief.get)


# ═══════════════════════════════════════════════════════════════════════════════
# MONTE CARLO PRICE SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

def mc_simulate_prices(current_inventory, my_production, opp_production,
                       town_shops, day, n_sims=20, horizon_days=5):
    """
    Monte Carlo simulation of future market prices.
    Simulates supply/demand over horizon with stochastic shop unlocks.

    Returns: dict {product: (mean_price, std_price, trend)} for each product
    """
    import math

    results = {p: [] for p in PRODUCTS}
    shop_interval = 3
    shop_sell_interval = 4
    ticks_per_day = TURNS_PER_DAY // shop_sell_interval

    rng = _random.Random(day * 7919)  # Deterministic per-day for reproducibility

    for _ in range(n_sims):
        # Clone inventory
        inv = dict(current_inventory)

        # Simulate days forward
        for d in range(horizon_days):
            future_day = day + d + 1
            if future_day >= TOTAL_DAYS:
                break

            # My production arrives
            for product, qty in my_production.items():
                daily = qty / max(1, horizon_days)
                inv[product] = inv.get(product, MARKET_I0) + int(daily)

            # Opponent production arrives (with noise from HMM uncertainty)
            for product, qty in opp_production.items():
                daily = qty / max(1, horizon_days)
                noisy = max(0, daily * (0.7 + rng.random() * 0.6))  # ±30% noise
                inv[product] = inv.get(product, MARKET_I0) + int(noisy)

            # Town demand: existing shops consume
            for shop_name in town_shops:
                products = SHOPS.get(shop_name, [])
                mult = 2 if len(products) == 1 else 1
                for p in products:
                    inv[p] = inv.get(p, MARKET_I0) - mult * ticks_per_day

            # New shop unlock (stochastic)
            if future_day > 0 and future_day % shop_interval == 0:
                new_shop = rng.choice(sorted(SHOPS.keys()))
                products = SHOPS[new_shop]
                mult = 2 if len(products) == 1 else 1
                for p in products:
                    inv[p] = inv.get(p, MARKET_I0) - mult * ticks_per_day

            # Town center consumes 1 of each non-fertilizer per day
            for p in PRODUCTS:
                if p != "FERTILIZER":
                    inv[p] = inv.get(p, MARKET_I0) - 1

        # Record final simulated prices
        for product in PRODUCTS:
            price = _simple_price(product, inv.get(product, MARKET_I0))
            results[product].append(price)

    # Compute statistics
    price_stats = {}
    for product in PRODUCTS:
        prices_list = results[product]
        if prices_list:
            mean_p = sum(prices_list) / len(prices_list)
            variance = sum((p - mean_p) ** 2 for p in prices_list) / len(prices_list)
            std_p = variance ** 0.5
            current_p = _simple_price(product, current_inventory.get(product, MARKET_I0))
            trend = (mean_p - current_p) / max(1, current_p)  # % change expected
            price_stats[product] = (mean_p, std_p, trend)
        else:
            price_stats[product] = (0, 0, 0)

    return price_stats


def _simple_price(product, inventory):
    """Simplified price calculation (mirrors game logic without full curve params)."""
    import math
    base_prices = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120,
                   "MELON": 250, "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100}
    base = base_prices.get(product, 50)
    diff = MARKET_I0 - inventory
    # Simplified: linear approximation of price curve
    sensitivity = base * 0.001  # Price moves ~0.1% per unit of inventory change
    price = base + diff * sensitivity
    return max(1, int(price))


# ═══════════════════════════════════════════════════════════════════════════════
# LP PLANNER (with MC-adjusted prices)
# ═══════════════════════════════════════════════════════════════════════════════

def estimate_crop_profit(crop_name, day, current_price, price_stats=None):
    """Expected profit using MC-predicted future prices if available."""
    crop = CROPS[crop_name]
    remaining = TOTAL_DAYS - day - 1

    # Use predicted future price if available (when crop will actually be sold)
    if price_stats and crop_name in price_stats:
        mean_price, _, trend = price_stats[crop_name]
        # Blend current and predicted — predicted is when we'll actually sell
        sell_price = int(current_price * (1 + trend * 0.7))
        sell_price = max(1, sell_price)
    else:
        sell_price = current_price

    if crop["ongoing"]:
        if remaining < crop["first_yield_day"] + 1:
            return -crop["seed"]
        harvests_possible = (remaining - crop["first_yield_day"]) // crop["interval"] + 1
        harvests = min(harvests_possible, crop["max_yield"])
        effective_harvests = max(1, int(harvests * 0.8))
        return effective_harvests * sell_price - crop["seed"]
    else:
        if remaining < crop["first_yield_day"]:
            return -crop["seed"]
        window_start = (crop["max_yield_day"] + 1) // 2
        window_end = crop["max_yield_day"]
        if day + window_end >= TOTAL_DAYS:
            available_window = max(0, TOTAL_DAYS - day - window_start)
            yield_est = min(crop["max_yield"], available_window)
        else:
            window_len = window_end - window_start + 1
            yield_est = min(crop["max_yield"], int(window_len * 0.8))
        return max(1, yield_est) * sell_price - crop["seed"]


def estimate_animal_profit(animal_name, day, prices, price_stats=None):
    """Expected profit using MC-predicted prices."""
    animal = ANIMALS[animal_name]
    remaining = TOTAL_DAYS - day - 1
    product = animal["product"]
    current_price = prices.get(product, 0)

    if price_stats and product in price_stats:
        mean_price, _, trend = price_stats[product]
        sell_price = int(current_price * (1 + trend * 0.7))
        sell_price = max(1, sell_price)
    else:
        sell_price = current_price

    if remaining < animal["first_yield_day"]:
        return -animal["cost"]

    production_days = remaining - animal["first_yield_day"]
    harvests = production_days // animal["interval"] + 1
    harvests = min(harvests, animal["max_held"])
    feed_cost = remaining * 10
    revenue = harvests * sell_price
    return revenue - animal["cost"] - feed_cost


def lp_allocate(budget, tiles_available, day, prices, current_seeds, current_shed, num_structures, price_stats=None):
    """LP-relaxed knapsack with MC-adjusted profit estimates."""
    candidates = []

    for crop_name, crop_data in CROPS.items():
        profit = estimate_crop_profit(crop_name, day, prices.get(crop_name, 0), price_stats)
        if profit <= 0:
            continue
        cost = crop_data["seed"]
        already_have = current_seeds.get(crop_name, 0)
        max_units = max(0, min(tiles_available, 8) - already_have)
        if max_units > 0 and cost > 0:
            candidates.append((profit / cost, cost, max_units, crop_name, "seed"))

    for animal_name, animal_data in ANIMALS.items():
        profit = estimate_animal_profit(animal_name, day, prices, price_stats)
        if profit <= 0:
            continue
        cost = animal_data["cost"]
        struct_type = animal_data["structure"]
        available_structures = num_structures.get(struct_type, 0)
        already_in_shed = current_shed.get(animal_name, 0)
        max_units = max(0, available_structures - already_in_shed)
        if max_units > 0 and cost > 0:
            candidates.append((profit / cost, cost, max_units, animal_name, "animal"))

    candidates.sort(key=lambda x: x[0], reverse=True)

    allocation = {}
    remaining_budget = budget
    remaining_tiles = tiles_available

    for roi, cost, max_units, name, item_type in candidates:
        if remaining_budget < cost:
            continue
        if item_type == "seed" and remaining_tiles <= 0:
            continue
        affordable = int(remaining_budget // cost)
        if item_type == "seed":
            units = min(affordable, max_units, remaining_tiles)
            remaining_tiles -= units
        else:
            units = min(affordable, max_units)
        if units > 0:
            allocation[(name, item_type)] = units
            remaining_budget -= units * cost

    return allocation


# ═══════════════════════════════════════════════════════════════════════════════
# BFS PATHFINDING
# ═══════════════════════════════════════════════════════════════════════════════

def bfs_next_step(start, target, board_size):
    """BFS shortest path, return first step direction."""
    if start == target:
        return "PASS"
    parent = {}
    queue = deque([start])
    parent[start] = None
    while queue:
        x, y = queue.popleft()
        if (x, y) == target:
            break
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < board_size and 0 <= ny < board_size and (nx, ny) not in parent:
                parent[(nx, ny)] = (x, y)
                queue.append((nx, ny))
    if target not in parent:
        return "PASS"
    pos = target
    while parent[pos] != start:
        pos = parent[pos]
    dx, dy = pos[0] - start[0], pos[1] - start[1]
    if dx == 1: return "EAST"
    if dx == -1: return "WEST"
    if dy == 1: return "SOUTH"
    if dy == -1: return "NORTH"
    return "PASS"


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_farm(obs):
    return obs["farms"][obs["player"]]

def get_opponent_farm(obs):
    return obs["farms"][1 - obs["player"]]

def shed_adjacent_tiles(board_size):
    half = board_size // 2
    return [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]

def is_shed_adjacent(pos, board_size):
    return tuple(pos) in set(shed_adjacent_tiles(board_size))

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def find_tiles(farm, predicate):
    board_size = len(farm["tiles"])
    results = []
    for y in range(board_size):
        for x in range(board_size):
            tile = farm["tiles"][y][x]
            if predicate(tile):
                results.append((x, y, tile))
    return results

def count_animals(farm):
    return len(find_tiles(farm, lambda t: isinstance(t, dict) and "animal" in t))

def count_structures(farm, structure_type):
    return len(find_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == structure_type and "animal" not in t))


# ═══════════════════════════════════════════════════════════════════════════════
# TASK GENERATION & WORKER ASSIGNMENT
# ═══════════════════════════════════════════════════════════════════════════════

def generate_tasks(farm, private, obs):
    """Generate prioritized tasks."""
    tasks = []
    board_size = len(farm["tiles"])
    day = obs["day"]
    seeds = private.get("seeds", {})
    inventories = private.get("inventories", [{}])

    for y in range(board_size):
        for x in range(board_size):
            tile = farm["tiles"][y][x]

            if isinstance(tile, dict) and tile.get("yield_units", 0) > 0:
                if tile.get("kind") == "PLANT":
                    crop_data = CROPS.get(tile.get("crop", ""), {})
                    if day - tile.get("planted_day", 0) >= crop_data.get("first_yield_day", 999):
                        tasks.append((x, y, "HARVEST", 100))
                elif "animal" in tile:
                    tasks.append((x, y, "HARVEST", 95))

            if isinstance(tile, dict) and "animal" in tile and tile.get("fertilizer_available"):
                tasks.append((x, y, "COLLECT_FERTILIZER", 50))

            if isinstance(tile, dict) and "animal" in tile and not tile.get("fed_today"):
                tasks.append((x, y, "FEED", 90))

            if isinstance(tile, dict) and "animal" in tile and not tile.get("cared_today"):
                tasks.append((x, y, "CARE", 40))

            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today"):
                consecutive = tile.get("consecutive_unwatered", 0)
                priority = 85 if consecutive >= 1 else 70
                tasks.append((x, y, "WATER", priority))

            if tile is None and any(seeds.get(c, 0) > 0 for c in CROPS):
                tasks.append((x, y, "PLANT", 30))

            if isinstance(tile, dict) and tile.get("kind") == "WEED":
                tasks.append((x, y, "DIG", 10))

            if tile is None:
                shed = private.get("shed", {})
                for animal_name, animal_data in ANIMALS.items():
                    if shed.get(animal_name, 0) > 0:
                        struct = animal_data["structure"]
                        if count_structures(farm, struct) == 0:
                            tasks.append((x, y, f"BUILD_{struct}", 60))
                            break

            if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE") and "animal" not in tile:
                for inv in inventories:
                    for animal_name, animal_data in ANIMALS.items():
                        if inv.get(animal_name, 0) > 0 and animal_data["structure"] == tile["kind"]:
                            tasks.append((x, y, "PLACE_ANIMAL", 65))

    tasks.sort(key=lambda t: t[3], reverse=True)
    return tasks


def assign_workers(workers, tasks, board_size):
    """Greedy task assignment by priority then distance."""
    assignments = {}
    claimed = set()
    for task_idx, (tx, ty, action, priority) in enumerate(tasks):
        if task_idx in claimed:
            continue
        best_w = None
        best_dist = 999
        for w_idx, (wx, wy) in enumerate(workers):
            if w_idx in assignments:
                continue
            d = manhattan_distance((wx, wy), (tx, ty))
            if d < best_dist:
                best_dist = d
                best_w = w_idx
        if best_w is not None:
            assignments[best_w] = (tx, ty, action)
            claimed.add(task_idx)
    return assignments


def execute_assignment(worker_pos, tx, ty, action, farm, private, worker_idx, obs, board_size):
    """Convert assignment to action command."""
    if worker_pos == (tx, ty):
        tile = farm["tiles"][ty][tx]
        if action == "HARVEST": return ["HARVEST"]
        if action == "WATER": return ["WATER"]
        if action == "FEED":
            inv = private.get("inventories", [{}])[worker_idx] if worker_idx < len(private.get("inventories", [{}])) else {}
            if inv.get("WHEAT", 0) > 0:
                return ["FEED"]
            if private.get("shed", {}).get("WHEAT", 0) > 0 and is_shed_adjacent(worker_pos, board_size):
                return ["PICKUP", "WHEAT", 3]
            shed_tiles = shed_adjacent_tiles(board_size)
            nearest = min(shed_tiles, key=lambda s: manhattan_distance(worker_pos, s))
            return [bfs_next_step(worker_pos, nearest, board_size)]
        if action == "CARE": return ["CARE"]
        if action == "COLLECT_FERTILIZER": return ["COLLECT_FERTILIZER"]
        if action == "PLANT":
            seeds = private.get("seeds", {})
            best = _pick_best_seed(seeds, obs)
            return ["PLANT", best] if best else ["PASS"]
        if action == "DIG": return ["DIG"]
        if action.startswith("BUILD_"):
            struct = action.replace("BUILD_", "")
            return [f"BUILD_{struct}"]
        if action == "PLACE_ANIMAL":
            inv = private.get("inventories", [{}])[worker_idx] if worker_idx < len(private.get("inventories", [{}])) else {}
            for a in ANIMALS:
                if inv.get(a, 0) > 0:
                    return ["PLACE", a]
            if is_shed_adjacent(worker_pos, board_size):
                for a in ANIMALS:
                    if private.get("shed", {}).get(a, 0) > 0:
                        return ["PICKUP", a, 1]
            shed_tiles = shed_adjacent_tiles(board_size)
            nearest = min(shed_tiles, key=lambda s: manhattan_distance(worker_pos, s))
            return [bfs_next_step(worker_pos, nearest, board_size)]
        return ["PASS"]
    return [bfs_next_step(worker_pos, (tx, ty), board_size)]


def _pick_best_seed(seeds, obs):
    day = obs["day"]
    prices = obs["market"]["prices"]
    best, best_p = None, -999999
    for c in CROPS:
        if seeds.get(c, 0) <= 0:
            continue
        p = estimate_crop_profit(c, day, prices.get(c, 0))
        if p > best_p:
            best_p = p
            best = c
    return best


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET ENGINE (MC-informed sell timing)
# ═══════════════════════════════════════════════════════════════════════════════

def plan_market(obs, farm, private, lp_plan, price_stats):
    """Market orders with MC-informed sell timing."""
    orders = []
    prices = obs["market"]["prices"]
    day = obs["day"]
    remaining = TOTAL_DAYS - day - 1
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    money = farm["money"]
    num_hands = len(farm.get("hands", []))
    num_quadrants = len(farm.get("unlocked_quadrants", []))
    animals_count = count_animals(farm)

    # ── SELL: Use MC price predictions to decide timing ──
    wheat_reserve = animals_count * 2

    for product in PRODUCTS:
        qty = shed.get(product, 0)
        if qty <= 0:
            continue

        if product == "WHEAT":
            sellable = max(0, qty - wheat_reserve)
        elif product == "FERTILIZER":
            ongoing = len(find_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT"
                                     and CROPS.get(t.get("crop", ""), {}).get("ongoing", False)))
            sellable = max(0, qty - ongoing)
        else:
            sellable = qty

        if sellable <= 0:
            continue

        # MC-informed sell decision: sell now if price trending down or game ending
        _, _, trend = price_stats.get(product, (0, 0, 0))

        if remaining <= 3:
            # End game: dump everything
            sell_qty = sellable
        elif trend < -0.05:
            # Price dropping — sell aggressively now
            sell_qty = min(sellable, 8)
        elif trend > 0.1 and remaining > 5:
            # Price rising significantly — hold (sell minimum)
            sell_qty = min(sellable, 2)
        else:
            # Neutral — sell moderate batches
            sell_qty = min(sellable, 5)

        if sell_qty > 0:
            orders.append(["SELL", product, sell_qty])

    # ── SELL unused animals ──
    for animal_name, animal_data in ANIMALS.items():
        in_shed = shed.get(animal_name, 0)
        if in_shed > 0:
            empty_structs = count_structures(farm, animal_data["structure"])
            excess = in_shed - empty_structs
            if excess > 0:
                orders.append(["SELL", animal_name, min(excess, 3)])

    # ── BUY per LP plan ──
    reserve = max(100, money * 0.2)
    buy_budget = money - reserve
    spent = 0

    for (name, item_type), qty in lp_plan.items():
        if item_type == "seed":
            need = max(0, qty - seeds.get(name, 0))
            cost_each = CROPS[name]["seed"]
            affordable = min(need, int((buy_budget - spent) // cost_each))
            if affordable > 0:
                orders.append(["BUY_SEED", name, affordable])
                spent += affordable * cost_each
        elif item_type == "animal":
            cost_each = ANIMALS[name]["cost"]
            if buy_budget - spent >= cost_each:
                orders.append(["BUY_ANIMAL", name, 1])
                spent += cost_each

    # ── HIRE ──
    active_plants = len(find_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT"))
    workload = active_plants + animals_count * 2

    fib_cost = _fib_cost(farm.get("hires_today", 0))
    if num_hands == 0 and workload >= 2 and money - spent >= fib_cost and remaining > 2:
        orders.append(["HIRE"])
        spent += fib_cost
        fib_cost2 = _fib_cost(farm.get("hires_today", 0) + 1)
        if workload >= 6 and money - spent >= fib_cost2:
            orders.append(["HIRE"])
            spent += fib_cost2
            fib_cost3 = _fib_cost(farm.get("hires_today", 0) + 2)
            if workload >= 12 and money - spent >= fib_cost3:
                orders.append(["HIRE"])
                spent += fib_cost3

    # ── BUY LAND ──
    if num_quadrants < 4 and remaining > 10:
        land_cost = LAND_PRICES[num_quadrants - 1]
        if money - spent >= land_cost + 200:
            orders.append(["BUY_LAND"])
            spent += land_cost

    # ── BUY WHEAT for feeding ──
    if animals_count > 0 and shed.get("WHEAT", 0) < animals_count:
        wheat_needed = animals_count - shed.get("WHEAT", 0)
        wheat_price = prices.get("WHEAT", 25)
        if money - spent >= wheat_price * wheat_needed:
            orders.append(["BUY_PRODUCT", "WHEAT", min(wheat_needed, 5)])

    return orders[:10]


def _fib_cost(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ═══════════════════════════════════════════════════════════════════════════════
# PERSISTENT STATE (survives across turns via module globals)
# ═══════════════════════════════════════════════════════════════════════════════

_opponent_model = None
_last_day = -1


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AGENT
# ═══════════════════════════════════════════════════════════════════════════════

def agent(obs, config=None):
    """Main agent: LP + Monte Carlo + HMM opponent prediction."""
    global _opponent_model, _last_day

    farm = get_farm(obs)
    opp_farm = get_opponent_farm(obs)
    private = obs.get("private", {})
    board_size = len(farm["tiles"])
    day = obs["day"]
    prices = obs["market"]["prices"]
    market_inv = obs["market"]["inventory"]
    seeds = private.get("seeds", {})
    shed = private.get("shed", {})
    town_shops = obs.get("town", {}).get("unlocked_shops", [])

    # ── Initialize/Update Opponent Model ──
    if _opponent_model is None:
        _opponent_model = OpponentModel()

    # Update HMM once per day (avoid excessive computation)
    if day != _last_day:
        _opponent_model.update(opp_farm)
        _last_day = day

    # ── Monte Carlo Price Simulation ──
    # Estimate my own upcoming production
    my_production = {p: 0 for p in PRODUCTS}
    for row in farm["tiles"]:
        for tile in row:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                crop_name = tile.get("crop", "")
                if crop_name in CROPS:
                    crop = CROPS[crop_name]
                    if crop["ongoing"]:
                        my_production[crop_name] += 5.0 / max(1, crop["interval"])
                    else:
                        my_production[crop_name] += crop["max_yield"] * 0.5
            elif isinstance(tile, dict) and "animal" in tile:
                animal_name = tile["animal"]
                product = ANIMALS[animal_name]["product"]
                my_production[product] += 5.0 / max(1, ANIMALS[animal_name]["interval"])

    # Predict opponent production using HMM
    opp_production = _opponent_model.predict_production(opp_farm, days_ahead=5)

    # Run MC simulation (lightweight: 20 sims, 5-day horizon)
    price_stats = mc_simulate_prices(market_inv, my_production, opp_production,
                                     town_shops, day, n_sims=20, horizon_days=5)

    # ── LP Planning with MC-adjusted prices ──
    plantable_count = len(find_tiles(farm, lambda t: t is None))
    budget = farm["money"] * 0.5
    num_structures = {
        "COOP": count_structures(farm, "COOP"),
        "PASTURE": count_structures(farm, "PASTURE"),
    }
    lp_plan = lp_allocate(budget, plantable_count, day, prices, seeds, shed, num_structures, price_stats)

    # ── Task Generation & Assignment ──
    tasks = generate_tasks(farm, private, obs)
    farmer_pos = tuple(farm["farmer"])
    hands = farm.get("hands", [])
    workers = [farmer_pos] + [tuple(h) for h in hands]

    worker_actions = [None] * len(workers)
    inventories = private.get("inventories", [{}])

    # Drop-off if carrying items at shed
    for w_idx, wpos in enumerate(workers):
        if w_idx < len(inventories):
            inv = inventories[w_idx]
            if inv and sum(inv.values()) > 0 and is_shed_adjacent(wpos, board_size):
                worker_actions[w_idx] = ["DROP"]

    # Assign remaining workers
    available = [(i, workers[i]) for i in range(len(workers)) if worker_actions[i] is None]
    if available and tasks:
        avail_pos = [pos for _, pos in available]
        avail_idx = [i for i, _ in available]
        assignments = assign_workers(avail_pos, tasks, board_size)
        for local_idx, (tx, ty, action) in assignments.items():
            global_idx = avail_idx[local_idx]
            cmd = execute_assignment(workers[global_idx], tx, ty, action, farm, private, global_idx, obs, board_size)
            worker_actions[global_idx] = cmd

    # Idle workers
    for w_idx in range(len(workers)):
        if worker_actions[w_idx] is None:
            inv = inventories[w_idx] if w_idx < len(inventories) else {}
            if inv and sum(inv.values()) > 0:
                shed_tiles = shed_adjacent_tiles(board_size)
                nearest = min(shed_tiles, key=lambda s: manhattan_distance(workers[w_idx], s))
                worker_actions[w_idx] = [bfs_next_step(workers[w_idx], nearest, board_size)]
            else:
                worker_actions[w_idx] = ["PASS"]

    # ── Market Orders ──
    market_orders = plan_market(obs, farm, private, lp_plan, price_stats)

    return {
        "farmer": worker_actions[0] if worker_actions else ["PASS"],
        "hands": worker_actions[1:] if len(worker_actions) > 1 else [],
        "market": market_orders,
    }
