"""
Kaggriculture v21 — Opponent-aware + randomized personality.

Features:
- Dynamic crop ROI based on market prices
- Opponent-aware: penalize crops they flood, dump to crash their prices
- Seed-based randomization: AGENT_SEED creates distinct variants for 5 daily submissions
- Coordinated hand planning with full 24-turn utilization
"""

import sys
import json
import random

# ═══ AGENT PERSONALITY SEED ═══
# Change this for each of 5 daily submissions: 0, 1, 2, 3, 4
AGENT_SEED = 4

# 5 distinct strategies — each emphasizes different income sources
PERSONALITIES = {
    0: {  # Balanced (proven baseline)
        "day0_animals": [["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2]],
        "day0_seeds": [["BUY_SEED", "MELON", 8]],
        "endgame_day": 25,
        "crop_priority": ["STRAWBERRY", "TOMATO", "MELON", "CARROT", "WHEAT"],
        "animal_shed_max": 1,  # conservative animal buying
        "diversify_split": 0.6,  # 60% best crop, 40% second
        "sell_frequency": 1.0,  # sell every turn
    },
    1: {  # Animal-heavy (more cows, fewer plants)
        "day0_animals": [["BUY_ANIMAL", "COW", 3], ["BUY_ANIMAL", "SHEEP", 1]],
        "day0_seeds": [["BUY_SEED", "MELON", 6]],
        "endgame_day": 26,
        "crop_priority": ["TOMATO", "STRAWBERRY", "MELON", "WHEAT", "CARROT"],
        "animal_shed_max": 2,  # aggressive animal buying
        "diversify_split": 0.7,
        "sell_frequency": 0.8,
    },
    2: {  # Plant-heavy (tomato focus, ongoing income)
        "day0_animals": [["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2]],
        "day0_seeds": [["BUY_SEED", "TOMATO", 6], ["BUY_SEED", "MELON", 3]],
        "endgame_day": 24,
        "crop_priority": ["TOMATO", "MELON", "STRAWBERRY", "CARROT", "WHEAT"],
        "animal_shed_max": 1,
        "diversify_split": 0.5,  # most diverse
        "sell_frequency": 1.0,
    },
    3: {  # Early expansion (save money for fast BUY_LAND)
        "day0_animals": [["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 1]],
        "day0_seeds": [["BUY_SEED", "MELON", 6]],
        "endgame_day": 25,
        "crop_priority": ["STRAWBERRY", "MELON", "TOMATO", "WHEAT", "CARROT"],
        "animal_shed_max": 1,
        "diversify_split": 0.8,  # mostly best crop
        "sell_frequency": 0.7,  # hold products sometimes
    },
    4: {  # Late bloomer (wheat early for quick cash, strawberry mid-game)
        "day0_animals": [["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2]],
        "day0_seeds": [["BUY_SEED", "WHEAT", 8], ["BUY_SEED", "MELON", 5]],
        "endgame_day": 27,
        "crop_priority": ["WHEAT", "STRAWBERRY", "TOMATO", "MELON", "CARROT"],
        "animal_shed_max": 2,
        "diversify_split": 0.6,
        "sell_frequency": 0.9,
    },
}

P = PERSONALITIES[AGENT_SEED % 5]

def log(t, d):
    print(json.dumps({"t": t, **d}), file=sys.stderr)

BOARD_SIZE = 10
SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]
SHED_SET = set(SHED_TILES)
# Reserve these NW tiles for pastures — hands don't plant here
PASTURE_SITES = [(3, 4), (4, 3), (3, 3), (2, 4)]
PASTURE_SITES_SET = set(PASTURE_SITES)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def move_toward(pos, target):
    dx, dy = target[0] - pos[0], target[1] - pos[1]
    if dx == 0 and dy == 0:
        return None
    if abs(dx) >= abs(dy):
        return "EAST" if dx > 0 else "WEST"
    return "SOUTH" if dy > 0 else "NORTH"


def scan(farm):
    plants, animals, empty, weeds = [], [], [], []
    empty_pastures = []
    unlocked = set(farm.get("unlocked_quadrants", ["NW"]))
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            half = BOARD_SIZE // 2
            quad = ("N" if y < half else "S") + ("W" if x < half else "E")
            if quad not in unlocked or (x, y) in SHED_SET:
                continue
            t = farm["tiles"][y][x]
            if t is None:
                empty.append((x, y))
            elif isinstance(t, dict):
                k = t.get("kind")
                if k == "PLANT":
                    plants.append((x, y, t))
                elif k == "WEED":
                    weeds.append((x, y))
                elif k == "PASTURE":
                    if "animal" in t:
                        animals.append((x, y, t))
                    else:
                        empty_pastures.append((x, y))
                elif k == "COOP":
                    if "animal" in t:
                        animals.append((x, y, t))
                    else:
                        empty_pastures.append((x, y))  # coop also holds animals
    return plants, animals, empty, weeds, empty_pastures


def plan_hands(hands_positions, farm, plants, empty, seeds, day=0):
    """
    Each turn: assign each hand a unique task, then either act (if on target) or move toward it.
    Hands ONLY act on their assigned target — they don't stop for random tiles they pass through.
    End-game (day >= 25): only water ongoing crops + harvest. No planting.
    """
    num_hands = len(hands_positions)
    if num_hands == 0:
        return []
    tiles = farm["tiles"]
    total_seeds = sum(seeds.get(c, 0) for c in ["MELON", "WHEAT", "STRAWBERRY", "TOMATO", "CARROT"])
    endgame = day >= P["endgame_day"]
    
    if endgame:
        # Only water ongoing crops that will produce at least 1 more harvest
        # Tomato: yields every day (always worth watering until day 29)
        # Strawberry: yields every 2 days (worth watering until day 28)
        water_tasks = [(px, py) for px, py, t in plants 
                       if not t.get("watered_today") and t.get("crop") in ("TOMATO", "STRAWBERRY")]
        plant_tasks = []
    else:
        water_tasks = [(px, py) for px, py, t in plants if not t.get("watered_today")]
        # Prioritize watering plants CLOSE to shed — hands reach them efficiently
        # Far plants may die but close ones produce reliably
        water_tasks.sort(key=lambda t: min(manhattan(t, s) for s in SHED_TILES))
        plant_tasks = [t for t in empty if t not in PASTURE_SITES_SET] if total_seeds > 0 else []
        # Plant NEAR shed first — hands reach faster, fewer weeds from watering delay
        plant_tasks.sort(key=lambda t: min(manhattan(t, s) for s in SHED_TILES))
    harvest_tasks = [(px, py) for px, py, t in plants if t.get("yield_units", 0) > 0]
    assignments = [None] * num_hands
    assigned_hands = set()
    assigned_targets = set()

    def assign_tier(tasks):
        """Greedy nearest-first assignment. Assigns each hand to the closest
        available task, ensuring no two hands get the same task."""
        available_tasks = [t for t in tasks if t not in assigned_targets]
        available_hands = [i for i in range(num_hands) if i not in assigned_hands]
        while available_hands and available_tasks:
            best_dist = 999
            best_hand = -1
            best_task = None
            for hi in available_hands:
                for task in available_tasks:
                    d = manhattan(hands_positions[hi], task)
                    if d < best_dist:
                        best_dist = d
                        best_hand = hi
                        best_task = task
            if best_hand < 0:
                break
            assignments[best_hand] = best_task
            assigned_hands.add(best_hand)
            assigned_targets.add(best_task)
            available_hands.remove(best_hand)
            available_tasks.remove(best_task)

    assign_tier(water_tasks)
    assign_tier(plant_tasks)
    assign_tier(harvest_tasks)

    actions = []
    for hi in range(num_hands):
        pos = hands_positions[hi]
        x, y = pos
        on_shed = pos in SHED_SET
        tile = tiles[y][x] if not on_shed else None
        target = assignments[hi]

        # If on assigned target: perform the action
        if target and pos == target and not on_shed:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today"):
                actions.append(["WATER"]); continue
            if tile is None and pos not in PASTURE_SITES_SET and total_seeds > 0:
                crop = next((c for c in P["crop_priority"] if seeds.get(c, 0) > 0), "WHEAT")
                actions.append(["PLANT", crop]); continue
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("yield_units", 0) > 0:
                actions.append(["HARVEST"]); continue
            if isinstance(tile, dict) and tile.get("kind") == "WEED":
                actions.append(["DIG"]); continue

        # If no assignment, act on current tile if useful
        if not on_shed and target is None:
            if isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today"):
                actions.append(["WATER"]); continue
            if tile is None and pos not in PASTURE_SITES_SET and total_seeds > 0:
                crop = next((c for c in P["crop_priority"] if seeds.get(c, 0) > 0), "WHEAT")
                actions.append(["PLANT", crop]); continue

        # Move toward assigned target
        if target:
            m = move_toward(pos, target)
            actions.append([m] if m else ["PASS"])
        else:
            actions.append(["PASS"])

    return actions


def decide_farmer(pos, farm, private, plants, animals, empty, weeds, empty_pastures, day, endgame=False):
    shed = private.get("shed", {})
    inventories = private.get("inventories", [])
    farmer_inv = inventories[0] if inventories else {}
    x, y = pos
    on_shed = (x, y) in SHED_SET
    tile = farm["tiles"][y][x] if not on_shed else None
    carrying_animal = None
    for aname in ["COW", "SHEEP", "GOOSE"]:
        if farmer_inv.get(aname, 0) > 0:
            carrying_animal = aname; break
    animals_in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0) + shed.get("GOOSE", 0)
    existing_pastures = len(animals) + len(empty_pastures)
    need_more_pastures = (not endgame) and existing_pastures < (len(animals) + animals_in_shed) and animals_in_shed > 0

    # Tile actions
    if not on_shed and tile is None and need_more_pastures:
        # Build appropriate structure: coop for geese, pasture for cow/sheep
        if shed.get("GOOSE", 0) > 0 and shed.get("COW", 0) == 0 and shed.get("SHEEP", 0) == 0:
            return ["BUILD_COOP"]
        elif shed.get("GOOSE", 0) > 0 and not empty_pastures:
            return ["BUILD_COOP"]
        else:
            return ["BUILD_PASTURE"]
    if not on_shed and isinstance(tile, dict) and tile.get("kind") in ("PASTURE", "COOP") and "animal" not in tile and carrying_animal:
        return ["PLACE", carrying_animal, 1]
    if not on_shed and isinstance(tile, dict) and "animal" in tile:
        if not tile.get("fed_today"): return ["FEED"]
        if not tile.get("cared_today"): return ["CARE"]
        if tile.get("fertilizer_available"): return ["COLLECT_FERTILIZER"]
        if tile.get("yield_units", 0) > 0: return ["HARVEST"]
    if not on_shed and isinstance(tile, dict) and tile.get("kind") == "PLANT":
        if not tile.get("watered_today"): return ["WATER"]
        if tile.get("yield_units", 0) > 0: return ["HARVEST"]
    if on_shed:
        unfed = [a for a in animals if not a[2].get("fed_today")]
        if unfed and shed.get("WHEAT", 0) > 0 and farmer_inv.get("WHEAT", 0) < len(unfed):
            return ["PICKUP", "WHEAT", min(shed["WHEAT"], len(unfed) + 2)]
        if not carrying_animal and empty_pastures and animals_in_shed > 0:
            for aname in ["COW", "SHEEP", "GOOSE"]:
                if shed.get(aname, 0) > 0: return ["PICKUP", aname, 1]

    # Movement
    if carrying_animal and empty_pastures:
        return [move_toward(pos, min(empty_pastures, key=lambda t: manhattan(pos, t)))] 
    
    # FARMER CIRCUIT: visit all animals needing attention in TSP order
    # Combine all animal tasks into one route: feed → care → collect → harvest
    animal_tasks = []
    for ax, ay, t in animals:
        if not t.get("fed_today"): animal_tasks.append((ax, ay, "FEED"))
        elif not t.get("cared_today"): animal_tasks.append((ax, ay, "CARE"))
        elif t.get("fertilizer_available"): animal_tasks.append((ax, ay, "FERT"))
        elif t.get("yield_units", 0) > 0: animal_tasks.append((ax, ay, "HARV"))
    
    if animal_tasks:
        # Need wheat for feeding?
        feed_tasks = [(ax, ay) for ax, ay, task in animal_tasks if task == "FEED"]
        if feed_tasks and farmer_inv.get("WHEAT", 0) == 0 and shed.get("WHEAT", 0) > 0 and not on_shed:
            return [move_toward(pos, min(SHED_TILES, key=lambda s: manhattan(pos, s)))]
        
        # Nearest-neighbor TSP: sort tasks by walking order from current position
        remaining = [(ax, ay) for ax, ay, _ in animal_tasks]
        route = []
        current = pos
        while remaining:
            nearest = min(remaining, key=lambda t: manhattan(current, t))
            route.append(nearest)
            remaining.remove(nearest)
            current = nearest
        
        # Go to first stop in route
        return [move_toward(pos, route[0])]
    if need_more_pastures and empty:
        # Cluster pastures: build adjacent to existing animals for tight feed route
        if animals:
            build_target = min(empty, key=lambda t: min(manhattan(t, (ax, ay)) for ax, ay, _ in animals))
        else:
            # First pastures: use PASTURE_SITES near shed
            build_target = None
            tiles_grid = farm["tiles"]
            for (px, py) in PASTURE_SITES:
                if tiles_grid[py][px] is None:
                    build_target = (px, py)
                    break
            if not build_target:
                build_target = min(empty, key=lambda t: min(manhattan(t, s) for s in SHED_TILES))
        return [move_toward(pos, build_target)]
    if not carrying_animal and animals_in_shed > 0 and empty_pastures and not on_shed:
        return [move_toward(pos, min(SHED_TILES, key=lambda s: manhattan(pos, s)))]
    unwatered = [(px, py) for px, py, t in plants if not t.get("watered_today")]
    if unwatered:
        return [move_toward(pos, min(unwatered, key=lambda t: manhattan(pos, t)))]
    harvestable_p = [(px, py) for px, py, t in plants if t.get("yield_units", 0) > 0]
    if harvestable_p:
        return [move_toward(pos, min(harvestable_p, key=lambda t: manhattan(pos, t)))]
    return ["PASS"]


def agent(obs):
    player = obs.get("player", 0)
    farms = obs.get("farms", [])
    private = obs.get("private", {}) or {}
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    if not farms or player >= len(farms):
        return {"farmer": ["PASS"], "hands": [], "market": []}
    farm = farms[player]
    money = farm.get("money", 0)
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    hands = farm.get("hands", [])
    num_hands = len(hands)
    plants, animals, empty, weeds, empty_pastures = scan(farm)
    num_animals = len(animals)
    num_plants = len(plants)
    animals_in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0) + shed.get("GOOSE", 0)
    unlocked = farm.get("unlocked_quadrants", ["NW"])
    num_quadrants = len(unlocked)
    
    # ═══ EXTRACTION PROJECTION ═══
    # Calculate guaranteed future income from current assets without further investment
    days_left = 29 - day
    market_prices = obs.get("market", {}).get("prices", {})
    
    # Animal income projection (what we'll earn from existing placed animals)
    # Cows: milk every 2 days × milk_price, sheep: wool every 2 days × wool_price
    milk_p = market_prices.get("MILK", 160)
    wool_p = market_prices.get("WOOL", 200)
    fert_p = market_prices.get("FERTILIZER", 100)
    animal_future_income = 0
    for ax, ay, at in animals:
        a_type = at.get("animal")
        remaining_harvests = days_left // 2  # every 2 days
        if a_type == "COW":
            animal_future_income += remaining_harvests * 7 * milk_p  # 6 base + care bonus
        elif a_type == "SHEEP":
            animal_future_income += remaining_harvests * 5 * wool_p
        # All animals produce fertilizer
        animal_future_income += remaining_harvests * fert_p
    
    # Plant income projection (ongoing crops keep yielding)
    plant_future_income = 0
    for px, py, pt in plants:
        crop = pt.get("crop", "")
        if crop == "TOMATO":
            # Yields 4 units every day after maturity
            tp = market_prices.get("TOMATO", 60)
            harvests_remaining = days_left  # daily
            plant_future_income += harvests_remaining * 4 * tp
        elif crop == "STRAWBERRY":
            sp = market_prices.get("STRAWBERRY", 120)
            harvests_remaining = days_left // 2  # every 2 days
            plant_future_income += harvests_remaining * 4 * sp
        elif crop == "MELON" and pt.get("yield_units", 0) > 0:
            mp = market_prices.get("MELON", 250)
            plant_future_income += pt["yield_units"] * mp  # one-time, ready now
        elif crop in ("WHEAT", "CARROT") and pt.get("yield_units", 0) > 0:
            p = market_prices.get(crop, 30)
            plant_future_income += pt["yield_units"] * p
    
    # Products already in shed (ready to sell)
    shed_value = 0
    for prod in ["FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT"]:
        shed_value += shed.get(prod, 0) * market_prices.get(prod, 50)
    
    # Total extraction value = what we'd earn by just harvesting/selling, no new investment
    extraction_value = money + shed_value + animal_future_income + plant_future_income
    
    # Watering cost for remaining days (ongoing crops need daily water = 1 hand/plant/day)
    ongoing_plants = sum(1 for _, _, t in plants if t.get("crop") in ("TOMATO", "STRAWBERRY"))
    water_cost = ongoing_plants * days_left  # $1 per hand per day

    # ═══ MARKET ═══
    market = []
    
    # Day 29 last hour: sell ALL including wheat reserve (game ending)
    if day == 29 and hour >= 20:
        for prod in ["FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
            amt = shed.get(prod, 0)
            if amt > 0:
                market.append(["SELL", prod, amt])
    elif day == 0 and hour == 0:
        # Day 0 hour 0: core setup (varies by personality)
        market = [["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"]] + P["day0_animals"] + P["day0_seeds"] + [["BUY_PRODUCT", "WHEAT", 8]]
    elif day == 0 and hour <= 3:
        # Day 0 hours 1-3: spend remaining money on more melons (day-10 income spike)
        if money >= 160:
            market = [["BUY_SEED", "MELON", min(money // 80, 10)]]
    elif hour == 0:
        # Hour 0: INVEST only (hire/buy/unlock). Sells happen every other hour.
        priority_orders = []
        
        # ─── SHARED: consumption prediction for crop + animal ROI ───
        market_inv = obs.get("market", {}).get("inventory", {})
        town_shops = obs.get("town", {}).get("unlocked_shops", [])
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
        consumption_per_day = {}
        for shop in town_shops:
            products = SHOPS.get(shop, [])
            mult = 2 if len(products) == 1 else 1
            for p in products:
                consumption_per_day[p] = consumption_per_day.get(p, 0) + mult * 6
        # Town center: +1/day for all products except fertilizer
        for p in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"]:
            consumption_per_day[p] = consumption_per_day.get(p, 0) + 1
        
        # Probabilistic future shop consumption:
        # Each future shop is drawn randomly from 8 types. 
        # Expected consumption boost per product = P(shop consumes it) × 6 ticks/day × mult
        # Probability each product appears in a random shop:
        PRODUCT_SHOP_PROBABILITY = {
            "WHEAT": 5/8,       # BAKERY, PIZZA, BRUNCH, ICE_CREAM, FARMERS
            "STRAWBERRY": 4/8,  # BRUNCH, ICE_CREAM, SMOOTHIE, FARMERS
            "MILK": 3/8,        # PIZZA, ICE_CREAM, SMOOTHIE
            "EGG": 2/8,         # BAKERY, BRUNCH
            "TOMATO": 2/8,      # PIZZA, FARMERS
            "CARROT": 2/8,      # PET_CAFE, FARMERS
            "WOOL": 1/8,        # YARN_STORE
            "MELON": 0,         # no shop consumes melon
        }
        # How many more shops will open after today
        current_shop_count = len(town_shops)
        max_shops = 8
        future_shops = max(0, max_shops - current_shop_count)
        # Each future shop adds expected consumption when it opens
        # Average days a future shop will be active = days_left / 2 (opens uniformly across remaining time)
        for p, prob in PRODUCT_SHOP_PROBABILITY.items():
            # Expected additional consumption from future shops (averaged over their active time)
            expected_new_shops_consuming = future_shops * prob
            # Each consuming shop adds 6 units/day (mult=1 for multi-product, most common)
            consumption_per_day[p] = consumption_per_day.get(p, 0) + expected_new_shops_consuming * 3  # 3 = 6 * 0.5 (half active on avg)
        
        def predicted_sell_price(product, sell_day):
            current_inv = market_inv.get(product, 10000)
            days_until_sell = max(0, sell_day - day)
            future_inv = current_inv - consumption_per_day.get(product, 1) * days_until_sell
            current_price = market_prices.get(product, 50)
            inv_drop = max(0, current_inv - future_inv)
            price_boost = 1.0 + (inv_drop / 1000) * 0.3
            return min(current_price * price_boost, current_price * 2)

        # UNLOCK — only if expected income from new tiles > unlock cost
        # New quadrant = 21 plantable tiles. Best ongoing crop profit × 21 tiles
        best_ongoing_profit = 0
        tp_price = market_prices.get("TOMATO", 60)
        if days_left >= 9:
            best_ongoing_profit = max(best_ongoing_profit, (days_left - 8) * 4 * tp_price - 50 - days_left)
        sp_price = market_prices.get("STRAWBERRY", 120)
        if days_left >= 12:
            best_ongoing_profit = max(best_ongoing_profit, ((days_left - 10) // 2) * 4 * sp_price - 100 - days_left)
        
        quadrant_value = 21 * best_ongoing_profit  # 21 tiles × profit per tile
        
        if quadrant_value > 2500 and "NE" not in unlocked and money >= 2500:
            priority_orders.append(["BUY_LAND"])
        elif quadrant_value > 3500 and "SW" not in unlocked and "NE" in unlocked and money >= 3500:
            priority_orders.append(["BUY_LAND"])
        elif quadrant_value > 5000 and "SE" not in unlocked and "SW" in unlocked and money >= 5000:
            priority_orders.append(["BUY_LAND"])

        # FEED — always (animals die without it)
        wheat_needed = num_animals * 2
        if shed.get("WHEAT", 0) < wheat_needed and money >= 50 and num_animals > 0:
            priority_orders.append(["BUY_PRODUCT", "WHEAT", wheat_needed + 5])

        # BUY ANIMALS — compare cow vs sheep vs goose based on predicted prices
        # Cow: $400, milk every 2 days after day 8, care bonus
        # Sheep: $300(?), wool every 2 days after day 8, care bonus  
        # Goose: $300, egg every day after day 4, care bonus
        if animals_in_shed <= P["animal_shed_max"] and money >= 600:
            milk_price = market_prices.get("MILK", 160)
            wool_price = market_prices.get("WOOL", 200)
            egg_price = market_prices.get("EGG", 50)
            
            # Use predicted future prices based on shop consumption
            milk_future = predicted_sell_price("MILK", min(29, day + 8 + days_left // 2))
            wool_future = predicted_sell_price("WOOL", min(29, day + 8 + days_left // 2))
            egg_future = predicted_sell_price("EGG", min(29, day + 4 + days_left // 2))
            
            cow_harvests = max(0, (days_left - 8) // 2)
            cow_profit = cow_harvests * 7 * milk_future - 400 - days_left * 2
            
            sheep_harvests = max(0, (days_left - 8) // 2)
            sheep_profit = sheep_harvests * 5 * wool_future - 300 - days_left * 2
            
            goose_harvests = max(0, days_left - 4)
            goose_profit = goose_harvests * 4 * egg_future - 300 - days_left * 2
            
            best_animal_profit = max(cow_profit, sheep_profit, goose_profit)
            if best_animal_profit > 0:
                if cow_profit >= sheep_profit and cow_profit >= goose_profit:
                    priority_orders.append(["BUY_ANIMAL", "COW", 2])
                elif sheep_profit >= goose_profit:
                    priority_orders.append(["BUY_ANIMAL", "SHEEP", 2])
                else:
                    priority_orders.append(["BUY_ANIMAL", "GOOSE", 2])

        # BUY SEEDS — exact profitability: revenue - (seed_cost + watering_cost)
        # Each plant needs 1 hand-turn per day for watering. Hands cost $1/day.
        # Only plant if net_profit > 0 in remaining game time.
        unplanted = seeds.get("MELON", 0) + seeds.get("WHEAT", 0) + seeds.get("STRAWBERRY", 0) + seeds.get("TOMATO", 0) + seeds.get("CARROT", 0)
        if unplanted < len(empty) and money >= 200:
            market_prices = obs.get("market", {}).get("prices", {})
            days_left = 29 - day
            turns_left = days_left * 24
            
            # Scan opponent crops
            opp_idx = 1 - player
            opp_farm = farms[opp_idx] if opp_idx < len(farms) else None
            opp_crops = {}
            if opp_farm:
                for row in opp_farm.get("tiles", []):
                    for t in row:
                        if isinstance(t, dict) and t.get("kind") == "PLANT":
                            c = t.get("crop", "")
                            opp_crops[c] = opp_crops.get(c, 0) + 1
            
            
            has_fertilizer = shed.get("FERTILIZER", 0) > 0
            crop_profit = {}
            
            # WHEAT: harvests on day+4, one-time
            wp = predicted_sell_price("WHEAT", day + 4)
            if days_left >= 4:
                units = 6 if has_fertilizer else 4
                crop_profit["WHEAT"] = units * wp - 10 - 4
            
            # CARROT: harvests on day+3, one-time
            cp = predicted_sell_price("CARROT", day + 3)
            if days_left >= 3:
                units = 4 if has_fertilizer else 3
                crop_profit["CARROT"] = units * cp - 20 - 3
            
            # MELON: harvests on day+10, one-time
            mp = predicted_sell_price("MELON", day + 10)
            if days_left >= 10:
                crop_profit["MELON"] = 6 * mp - 80 - 10
            
            # STRAWBERRY: first harvest day+12, then every 2 days
            if days_left >= 12:
                harvests = (days_left - 10) // 2
                avg_sell_day = day + 10 + (harvests // 2) * 2  # midpoint
                sp = predicted_sell_price("STRAWBERRY", min(29, avg_sell_day))
                crop_profit["STRAWBERRY"] = harvests * 4 * sp - 100 - days_left
            
            # TOMATO: first harvest day+9, then every day
            if days_left >= 9:
                harvests = days_left - 8
                avg_sell_day = day + 8 + harvests // 2
                tp = predicted_sell_price("TOMATO", min(29, avg_sell_day))
                crop_profit["TOMATO"] = harvests * 4 * tp - 50 - days_left
            
            # Remove unprofitable crops
            crop_profit = {c: p for c, p in crop_profit.items() if p > 0}
            
            # Penalize crops opponent is flooding
            for c in crop_profit:
                opp_count = opp_crops.get(c, 0)
                if opp_count > 10:
                    crop_profit[c] *= 0.5
                elif opp_count > 5:
                    crop_profit[c] *= 0.75
            
            if crop_profit:
                # Buy a MIX of top profitable crops (diversification protects against price crashes)
                sorted_crops = sorted(crop_profit, key=crop_profit.get, reverse=True)
                buy_amt = min(len(empty) - unplanted, 20)
                if buy_amt > 0:
                    if len(sorted_crops) >= 2 and crop_profit[sorted_crops[1]] > 0:
                        amt1 = max(1, int(buy_amt * P["diversify_split"]))
                        amt2 = buy_amt - amt1
                        priority_orders.append(["BUY_SEED", sorted_crops[0], amt1])
                        if amt2 > 0:
                            priority_orders.append(["BUY_SEED", sorted_crops[1], amt2])
                    else:
                        priority_orders.append(["BUY_SEED", sorted_crops[0], buy_amt])

        # HIRE — calculate exact number needed based on plant distances
        # Each hand: 24 turns. Walk D to first plant, then (walk 1 + water 1) per plant = 2 turns/plant
        # Coverage per hand = (24 - D_first) // 2, where D_first = distance to assigned cluster
        # Sort plants by distance from shed, divide into clusters for each hand
        slots_left = 10 - len(priority_orders)
        
        unwatered_plants = [(px, py) for px, py, t in plants if not t.get("watered_today")]
        unwatered_plants.sort(key=lambda t: min(manhattan(t, s) for s in SHED_TILES))
        
        if unwatered_plants or unplanted > 0:
            # Simulate: how many hands needed to cover all tasks?
            tasks_remaining = len(unwatered_plants) + min(unplanted, len(empty))
            hands_needed = 0
            tasks_covered = 0
            
            while tasks_covered < tasks_remaining and hands_needed < 20:
                # Next hand walks to the farthest uncovered task cluster
                if tasks_covered < len(unwatered_plants):
                    # Get distance to the next plant this hand would service
                    first_task_idx = tasks_covered
                    first_dist = min(manhattan(unwatered_plants[min(first_task_idx, len(unwatered_plants)-1)], s) for s in SHED_TILES)
                else:
                    first_dist = 3  # estimate for planting (avg empty tile distance)
                
                # This hand covers: (24 - walk_to_first) // 3 tasks (realistic: walk ~2 + water 1)
                coverage = max(1, (24 - first_dist) // 3)
                tasks_covered += coverage
                hands_needed += 1
            
            hire_count = hands_needed
        else:
            hire_count = 0
        
        if day >= 28:
            hire_count = max(hire_count, num_plants + 5)
        actual_hires = min(hire_count, slots_left)
        for _ in range(max(0, actual_hires)):
            priority_orders.append(["HIRE"])

        market = priority_orders
    else:
        # Non-hour-0: sell first, then hire extra if slots remain
        
        # Selling strategy:
        # - Normal days: sell immediately (opponent-aware)
        # - Days 28-29: sell in small batches to avoid crashing prices
        # - Last turn (day 29, hour 23): dump everything remaining
        
        rng = random.Random(AGENT_SEED * 10000 + day * 24 + hour)
        opp_idx = 1 - player
        opp_farm = farms[opp_idx] if opp_idx < len(farms) else None
        
        # Scan opponent
        opp_products_coming = set()
        if opp_farm:
            for row in opp_farm.get("tiles", []):
                for t in row:
                    if isinstance(t, dict):
                        if t.get("kind") == "PLANT" and t.get("yield_units", 0) > 0:
                            opp_products_coming.add(t.get("crop", ""))
                        if "animal" in t:
                            a = t["animal"]
                            if a == "COW": opp_products_coming.add("MILK")
                            elif a == "SHEEP": opp_products_coming.add("WOOL")
                            elif a == "GOOSE": opp_products_coming.add("EGG")
        
        # Last turn: dump everything
        if day == 29 and hour == 23:
            for prod in ["FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
                amt = shed.get(prod, 0)
                if amt > 0:
                    market.append(["SELL", prod, amt])
        elif day >= 28:
            # Batch selling: sell max 3 units per product per turn (keeps prices stable)
            # Sell products opponent is growing (crash them) at full volume
            # Sell our unique products in small batches (maintain our price)
            wheat_reserve = num_animals * 2 if day < 29 else 0
            for prod in ["FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT"]:
                amt = shed.get(prod, 0)
                if amt > 0:
                    if prod in opp_products_coming:
                        market.append(["SELL", prod, amt])  # dump to crash opponent
                    else:
                        sell_amt = min(amt, 4)  # small batch to keep price high
                        market.append(["SELL", prod, sell_amt])
            sell_wheat = max(0, shed.get("WHEAT", 0) - wheat_reserve)
            if sell_wheat > 0:
                market.append(["SELL", "WHEAT", min(sell_wheat, 4)])
        else:
            # Normal days: sell with randomized timing
            sell_frequency = P["sell_frequency"]
            if rng.random() > sell_frequency and hour < 20:
                pass  # Hold
            else:
                wheat_reserve = num_animals * 2 + 5
                # Dump opponent's products (crash their price)
                for prod in opp_products_coming:
                    if prod == "WHEAT": continue
                    amt = shed.get(prod, 0)
                    if amt > 0:
                        market.append(["SELL", prod, amt])
                # Sell our products
                for prod in ["FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT"]:
                    if prod in opp_products_coming: continue
                    amt = shed.get(prod, 0)
                    if amt > 0:
                        market.append(["SELL", prod, amt])
                sell_wheat = max(0, shed.get("WHEAT", 0) - wheat_reserve)
                if sell_wheat > 0:
                    market.append(["SELL", "WHEAT", sell_wheat])

        # Mid-day hire: extra hand at hour 4 when plants outpace hands
        if 10 - len(market) >= 1 and hour == 4 and day < 28 and num_hands < num_plants - 3 and money >= 20:
            market.append(["HIRE"])

    # ═══ FARMER ═══
    farmer_pos = tuple(farm["farmer"])
    # End-game: don't build/place, just feed + harvest + collect
    endgame = day >= P["endgame_day"]
    farmer_action = decide_farmer(farmer_pos, farm, private, plants, animals, empty, weeds, empty_pastures, day, endgame)

    # ═══ HANDS ═══
    hands_positions = [tuple(hands[i]) for i in range(num_hands)]
    hands_actions = plan_hands(hands_positions, farm, plants, empty, seeds, day)

    if hour == 0:
        log("D", {"d": day, "$": int(money), "p": num_plants, "a": num_animals,
                  "h": num_hands, "sa": animals_in_shed,
                  "q": num_quadrants, "e": len(empty),
                  "ext": int(extraction_value)})

    return {"farmer": farmer_action, "hands": hands_actions, "market": market[:10]}
