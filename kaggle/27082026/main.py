"""
Kaggriculture v21 — Opponent-aware + randomized personality.

Features:
- Dynamic crop ROI based on market prices
- Opponent-aware: penalize crops they flood, dump to crash their prices
- Seed-based randomization: AGENT_SEED creates distinct variants for 5 daily submissions
- Coordinated hand planning with full 24-turn utilization
"""

import sys
import os
import json
import random

# ═══ AGENT PERSONALITY — random at runtime ═══
# Only TWO variants, both the proven Balanced strategy. Diagnostics showed the thematic
# personalities (animal-heavy, plant-heavy, early-expansion, late-bloomer) added variance
# without lifting the average, so they were dropped. The two variants differ ONLY in
# timing (endgame_day, sell_frequency) and the hire cap (hand_value) to give the daily
# submissions a little diversity without changing the core balanced plan.
# Diagnostics: set KAGG_SEED=0 or 1 to pin a variant for local testing.
_forced_seed = os.environ.get("KAGG_SEED")
if _forced_seed is not None and _forced_seed.strip().lstrip("-").isdigit():
    AGENT_SEED = int(_forced_seed)
else:
    AGENT_SEED = random.choices([0, 1], weights=[50, 50])[0]

# Two variants of the Balanced strategy. Same animals (2 cow / 2 sheep) and same wheat
# quick-cash buy; the seed picks the day-0 LONG-TERM crop between the two best crops only
# (melon vs strawberry) via crop_priority[0]. It also nudges timing (endgame_day,
# sell_frequency) and the hire cap (hand_value). No weak crops (wheat/carrot) are ever the
# lead — the per-turn ROI picker still adapts everything downstream.
PERSONALITIES = {
    0: {  # Balanced — MELON lead (day-10 income spike; matches the hours 1-3 extra-melon buys)
        "day0_animals": [["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2]],
        "endgame_day": 25,
        "crop_priority": ["MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"],
        "animal_shed_max": 1,  # conservative animal buying
        "diversify_split": 0.6,  # 60% best crop, 40% second
        "sell_frequency": 1.0,  # sell every turn
        "hand_value": 150,  # Fibonacci hire cap (~12 hands)
    },
    1: {  # Balanced — STRAWBERRY lead; slightly later endgame + tighter cap + gentler selling
        "day0_animals": [["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2]],
        "endgame_day": 26,  # plant one day longer
        "crop_priority": ["STRAWBERRY", "MELON", "TOMATO", "CARROT", "WHEAT"],
        "animal_shed_max": 1,
        "diversify_split": 0.6,
        "sell_frequency": 0.9,  # hold occasionally to avoid crashing own prices
        "hand_value": 130,  # slightly tighter hire cap (~11 hands)
    },
}

NUM_PERSONALITIES = len(PERSONALITIES)
P = PERSONALITIES[AGENT_SEED % NUM_PERSONALITIES]

def log(t, d):
    print(json.dumps({"t": t, **d}), file=sys.stderr)

BOARD_SIZE = 10
SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]
SHED_SET = set(SHED_TILES)
# Animal plan: 2 immediate pastures + 2 wheat-then-pasture tiles
# (3,4) and (4,3): reserved immediately for pastures (hands don't plant)
# (3,3) and (2,4): hands plant WHEAT here (harvests day 4, then farmer builds pasture)
PASTURE_SITES_IMMEDIATE = [(3, 4), (4, 3)]  # reserved from day 0
PASTURE_SITES_DELAYED = [(3, 3), (2, 4)]    # wheat first, pasture after day 4
PASTURE_SITES_DELAYED_SET = set(PASTURE_SITES_DELAYED)
PASTURE_SITES = PASTURE_SITES_IMMEDIATE + PASTURE_SITES_DELAYED
PASTURE_SITES_SET = set(PASTURE_SITES_IMMEDIATE)  # only block immediate sites from planting


# ═══ HIRE ECONOMICS (mirrors the environment) ═══
# The n-th hire of a day costs fib(n) with fib = 1,1,2,3,5,8,13,21,...  (n starts at 0).
# Hands reset every morning, so this cost curve restarts each day. We use it to decide how
# many hands we can AFFORD to hire right now — issuing a HIRE we can't pay for is a wasted
# market order (the env silently skips it), so we never over-order.
_FIB_CACHE = [1, 1]
def _fib(n):
    while len(_FIB_CACHE) <= n:
        _FIB_CACHE.append(_FIB_CACHE[-1] + _FIB_CACHE[-2])
    return _FIB_CACHE[n]

def affordable_hires(money, hires_today, want, reserve=0):
    """How many of `want` additional hands we can afford right now, given the Fibonacci
    cost curve, keeping `reserve` dollars aside for feed/seeds. Returns an int >= 0."""
    budget = money - reserve
    count = 0
    n = hires_today
    while count < want:
        cost = _fib(n)
        if budget < cost:
            break
        budget -= cost
        count += 1
        n += 1
    return count


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


def plan_hands(hands_positions, farm, plants, empty, seeds, day=0, weeds=None, private=None):
    """
    Role-based hand planning:
      Hand 0 = FEEDER  — pickup wheat from shed, sweep all unfed animals with FEED,
                         then join the plant workers when no animals need feeding.
      Hand 1 = CARER   — sweep all uncared animals with CARE, then join plant workers.
      Hands 2+ = PLANT WORKERS — greedy nearest water/plant/harvest (+ animal
                         collect/harvest and weeds at low priority).

    Rationale: hands own the per-day animal feed+care burden so the farmer can spend
    its 24 turns building pastures and placing animals (more animals = more income).
    Hand FEED requires wheat in the hand's own inventory, so the feeder picks up a
    batch of wheat from the shed (hands spawn adjacent to the shed) before feeding.

    End-game (day >= endgame_day): no planting; only water ongoing crops + harvest.
    Feed/care still run so animals keep producing.
    """
    num_hands = len(hands_positions)
    if num_hands == 0:
        return []
    tiles = farm["tiles"]
    total_seeds = sum(seeds.get(c, 0) for c in ["MELON", "WHEAT", "STRAWBERRY", "TOMATO", "CARROT"])
    endgame = day >= P["endgame_day"]
    inventories = private.get("inventories", []) if private else []
    shed_wheat = private.get("shed", {}).get("WHEAT", 0) if private else 0

    # ─── Scan animal tasks ───
    animal_feed_tasks = []
    animal_care_tasks = []
    animal_collect_tasks = []
    animal_harvest_tasks = []
    for y2 in range(10):
        for x2 in range(10):
            t2 = tiles[y2][x2]
            if isinstance(t2, dict) and "animal" in t2:
                if not t2.get("fed_today"): animal_feed_tasks.append((x2, y2))
                if not t2.get("cared_today"): animal_care_tasks.append((x2, y2))
                if t2.get("fertilizer_available"): animal_collect_tasks.append((x2, y2))
                if t2.get("yield_units", 0) > 0: animal_harvest_tasks.append((x2, y2))

    # ─── Plant-worker task pools (water / plant / harvest / collect / weeds) ───
    if endgame:
        water_tasks = [(px, py) for px, py, t in plants
                       if not t.get("watered_today") and t.get("crop") in ("TOMATO", "STRAWBERRY")]
        plant_tasks = []
    else:
        water_tasks = [(px, py) for px, py, t in plants if not t.get("watered_today")]
        water_tasks.sort(key=lambda t: min(manhattan(t, s) for s in SHED_TILES))
        plant_tasks = [t for t in empty if t not in PASTURE_SITES_SET] if total_seeds > 0 else []
        plant_tasks.sort(key=lambda t: min(manhattan(t, s) for s in SHED_TILES))
    harvest_tasks = [(px, py) for px, py, t in plants if t.get("yield_units", 0) > 0]

    assignments = [None] * num_hands
    assigned_hands = set()
    assigned_targets = set()

    # ─── Roles ───
    # Feeder = hand 0 (only meaningful when animals need feeding).
    # Carer = hand 1, but ONLY dedicate a whole hand to care when hands are plentiful
    # (>= 4). With few hands, care is handled by spare hands via the idle pool so we
    # don't starve early-game planting/watering by reserving two hands for animals.
    feeder_idx = 0 if (num_hands >= 1 and animal_feed_tasks) else None
    dedicate_carer = num_hands >= 4 and len(animal_care_tasks) > 0
    carer_idx = 1 if dedicate_carer else None
    role_of = {}
    if feeder_idx is not None:
        role_of[feeder_idx] = "FEEDER"
    if carer_idx is not None:
        role_of[carer_idx] = "CARER"

    def hand_wheat(hi):
        inv = inventories[hi + 1] if (hi + 1) < len(inventories) else {}
        return inv.get("WHEAT", 0)

    def nearest_shed(pos):
        return min(SHED_TILES, key=lambda s: manhattan(pos, s))

    def assign_tier(tasks, hand_pool):
        """Greedy nearest-first assignment over a specific pool of hands."""
        available_tasks = [t for t in tasks if t not in assigned_targets]
        available_hands = [i for i in hand_pool if i not in assigned_hands]
        while available_hands and available_tasks:
            best_dist, best_hand, best_task = 999, -1, None
            for hi in available_hands:
                for task in available_tasks:
                    d = manhattan(hands_positions[hi], task)
                    if d < best_dist:
                        best_dist, best_hand, best_task = d, hi, task
            if best_hand < 0:
                break
            assignments[best_hand] = best_task
            assigned_hands.add(best_hand)
            assigned_targets.add(best_task)
            available_hands.remove(best_hand)
            available_tasks.remove(best_task)

    # ─── FEEDER assignment ───
    # If unfed animals exist: if the feeder has wheat, target nearest unfed animal;
    # else target the shed to pick up wheat. If none unfed, feeder becomes a plant worker.
    if feeder_idx is not None and animal_feed_tasks:
        pos = hands_positions[feeder_idx]
        if hand_wheat(feeder_idx) > 0:
            tgt = min(animal_feed_tasks, key=lambda t: manhattan(pos, t))
            assignments[feeder_idx] = tgt
            assigned_hands.add(feeder_idx)
            assigned_targets.add(tgt)
        elif shed_wheat > 0:
            assignments[feeder_idx] = nearest_shed(pos)
            assigned_hands.add(feeder_idx)
        # else: no wheat anywhere — feeder falls through to plant work below

    # ─── CARER assignment ───
    if carer_idx is not None and animal_care_tasks:
        pos = hands_positions[carer_idx]
        tgt = min(animal_care_tasks, key=lambda t: manhattan(pos, t))
        assignments[carer_idx] = tgt
        assigned_hands.add(carer_idx)
        assigned_targets.add(tgt)

    # ─── PLANT WORKER assignment ───
    # Any unassigned hand (including feeder/carer with no animal work left) does plant work.
    idle_pool = [i for i in range(num_hands) if i not in assigned_hands]
    assign_tier(water_tasks, idle_pool)
    assign_tier(plant_tasks, idle_pool)
    assign_tier(harvest_tasks, idle_pool)
    # Low-priority animal upkeep for spare hands: care (if no dedicated carer), then
    # collect fertilizer, then harvest animal produce.
    if not dedicate_carer:
        assign_tier(animal_care_tasks, idle_pool)
    assign_tier(animal_collect_tasks, idle_pool)
    assign_tier(animal_harvest_tasks, idle_pool)
    if weeds:
        weed_tasks = list(weeds)
        weed_tasks.sort(key=lambda t: min(manhattan(t, s) for s in SHED_TILES))
        assign_tier(weed_tasks, idle_pool)

    # ─── Execute ───
    actions = []
    for hi in range(num_hands):
        pos = hands_positions[hi]
        x, y = pos
        on_shed = pos in SHED_SET
        tile = tiles[y][x] if not on_shed else None
        target = assignments[hi]
        role = role_of.get(hi)

        # Feeder at shed: pick up a batch of wheat (one per animal still needing feed, capped).
        if on_shed and role == "FEEDER" and animal_feed_tasks and shed_wheat > 0:
            if hand_wheat(hi) < len(animal_feed_tasks):
                grab = min(shed_wheat, len(animal_feed_tasks), 10)
                if grab > 0:
                    actions.append(["PICKUP", "WHEAT", grab]); continue

        # On assigned target: perform the action.
        if target and pos == target and not on_shed and isinstance(tile, dict):
            k = tile.get("kind")
            if "animal" in tile:
                if role == "FEEDER" and not tile.get("fed_today") and hand_wheat(hi) > 0:
                    actions.append(["FEED"]); continue
                # Any hand may CARE (dedicated carer or a spare plant worker assigned a care task).
                if not tile.get("cared_today"):
                    actions.append(["CARE"]); continue
                if tile.get("fertilizer_available"):
                    actions.append(["COLLECT_FERTILIZER"]); continue
                if tile.get("yield_units", 0) > 0:
                    actions.append(["HARVEST"]); continue
            if k == "PLANT" and not tile.get("watered_today"):
                actions.append(["WATER"]); continue
            if k == "PLANT" and tile.get("yield_units", 0) > 0:
                actions.append(["HARVEST"]); continue
            if k == "WEED":
                actions.append(["DIG"]); continue
        if target and pos == target and not on_shed and tile is None \
                and pos not in PASTURE_SITES_SET and total_seeds > 0 and not endgame:
            crop = next((c for c in P["crop_priority"] if seeds.get(c, 0) > 0), "WHEAT")
            if pos in PASTURE_SITES_DELAYED_SET and seeds.get("WHEAT", 0) > 0:
                crop = "WHEAT"
            actions.append(["PLANT", crop]); continue

        # Idle hand standing on a useful tile: act opportunistically.
        if not on_shed and target is None and isinstance(tile, dict):
            if tile.get("kind") == "PLANT" and not tile.get("watered_today"):
                actions.append(["WATER"]); continue
        if not on_shed and target is None and tile is None \
                and pos not in PASTURE_SITES_SET and total_seeds > 0 and not endgame:
            crop = next((c for c in P["crop_priority"] if seeds.get(c, 0) > 0), "WHEAT")
            if pos in PASTURE_SITES_DELAYED_SET and seeds.get("WHEAT", 0) > 0:
                crop = "WHEAT"
            actions.append(["PLANT", crop]); continue

        # Move toward assigned target.
        if target:
            m = move_toward(pos, target)
            actions.append([m] if m else ["PASS"])
        else:
            actions.append(["PASS"])

    return actions


def decide_farmer(pos, farm, private, plants, animals, empty, weeds, empty_pastures, day, endgame=False):
    """
    Farmer no longer feeds or cares for animals — those are owned by the FEEDER (hand 0)
    and CARER (hand 1). The farmer focuses on expanding the herd and light upkeep:
      - BUILD_PASTURE / BUILD_COOP on empty tiles when animals wait in the shed
      - PLACE animals from the shed onto empty pastures/coops
      - COLLECT_FERTILIZER and HARVEST on animals (produce pickup)
      - water nearby plants (within 4 of shed), then harvest ready plants
    Freeing the farmer from the 14-turn/day feed+care circuit lets it build more
    pastures -> more animals -> more income.
    """
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

    # ─── Tile actions on current tile ───
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
        # Farmer only does produce upkeep now (no FEED / no CARE)
        if tile.get("fertilizer_available"):
            return ["COLLECT_FERTILIZER"]
        if tile.get("yield_units", 0) > 0:
            return ["HARVEST"]
        # Nothing to do on this animal — fall through to movement
    if not on_shed and isinstance(tile, dict) and tile.get("kind") == "PLANT":
        if not tile.get("watered_today"): return ["WATER"]
        if tile.get("yield_units", 0) > 0: return ["HARVEST"]
    if on_shed:
        # Pick up an animal to place (no wheat pickup — feeding is the hands' job)
        if not carrying_animal and empty_pastures and animals_in_shed > 0:
            for aname in ["COW", "SHEEP", "GOOSE"]:
                if shed.get(aname, 0) > 0: return ["PICKUP", aname, 1]

    # ─── Movement ───
    if carrying_animal and empty_pastures:
        return [move_toward(pos, min(empty_pastures, key=lambda t: manhattan(pos, t)))]

    # Animal produce circuit: collect fertilizer + harvest animal produce (TSP order).
    animal_tasks = []
    for ax, ay, t in animals:
        if t.get("fertilizer_available"): animal_tasks.append((ax, ay))
        elif t.get("yield_units", 0) > 0: animal_tasks.append((ax, ay))

    if animal_tasks:
        # Nearest-neighbor: go to the closest animal needing produce pickup.
        return [move_toward(pos, min(animal_tasks, key=lambda t: manhattan(pos, t)))]
    if need_more_pastures and empty:
        # Cluster pastures: build adjacent to existing animals for a tight herd.
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
    # Farmer waters nearby unwatered plants (stay close to shed/animals, don't wander far)
    unwatered = [(px, py) for px, py, t in plants if not t.get("watered_today")]
    if unwatered:
        # Only water plants within 4 tiles of shed (farmer stays near animal ring)
        nearby_unwatered = [p for p in unwatered if min(manhattan(p, s) for s in SHED_TILES) <= 4]
        if nearby_unwatered:
            target = min(nearby_unwatered, key=lambda t: manhattan(pos, t))
            return [move_toward(pos, target)]
        # If no nearby unwatered, go to closest overall (still better than PASS)
        target = min(unwatered, key=lambda t: manhattan(pos, t))
        return [move_toward(pos, target)]
    # Only harvest if everything is watered
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
    
    # Day 29: sell ALL every turn (game ending, no point holding)
    if day == 29:
        for prod in ["FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"]:
            amt = shed.get(prod, 0)
            if amt > 0:
                market.append(["SELL", prod, amt])
    elif day == 0 and hour == 0:
        # Day 0: 5 hires + 4 animals + seeds (dynamic based on personality)
        # Always buy wheat (fast day-4 cash) + best long-term crop from personality
        best_crop = P["crop_priority"][0]  # varies by personality
        seed_cost = {"WHEAT": 10, "MELON": 80, "STRAWBERRY": 100, "TOMATO": 50, "CARROT": 20}
        # Budget for seeds: ~$700 (after hires $12 + animals $1400 + feed $150)
        seed_budget = 700
        wheat_count = 7  # always some wheat for quick cash
        remaining_budget = seed_budget - wheat_count * 10
        other_count = min(10, max(1, remaining_budget // seed_cost.get(best_crop, 80)))
        market = [["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
                  ["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2],
                  ["BUY_SEED", "WHEAT", wheat_count], ["BUY_SEED", best_crop, other_count],
                  ["BUY_PRODUCT", "WHEAT", 6]]
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

        # FEED — buy wheat for current + incoming animals
        total_to_feed = num_animals + animals_in_shed
        wheat_needed = total_to_feed * 2
        if day < 29 and shed.get("WHEAT", 0) < wheat_needed and money >= 50 and total_to_feed > 0:
            priority_orders.append(["BUY_PRODUCT", "WHEAT", wheat_needed + 5])

        # BUY ANIMALS — buy when farmer can keep up (shed <= 2 means placement is flowing)
        total_animals = num_animals + animals_in_shed
        if total_animals < 14 and animals_in_shed <= 2 and money >= 600 and days_left >= 8:
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
            tasks_remaining = len(unwatered_plants) + min(unplanted, len(empty)) + num_animals  # +animals for care/collect
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
            # ENDGAME TACTICS: adapt selling based on whether we're winning or losing
            opp_money = farms[1 - player].get("money", 0) if (1 - player) < len(farms) else 0
            we_are_ahead = money > opp_money
            
            wheat_reserve = num_animals * 2 if day < 29 else 0
            for prod in ["FERTILIZER", "MILK", "WOOL", "EGG", "MELON", "STRAWBERRY", "TOMATO", "CARROT"]:
                amt = shed.get(prod, 0)
                if amt > 0:
                    if prod in opp_products_coming:
                        # Always dump opponent's products (crash their income)
                        market.append(["SELL", prod, amt])
                    elif we_are_ahead:
                        # We're winning — sell small batches to maintain high prices
                        market.append(["SELL", prod, min(amt, 4)])
                    else:
                        # We're losing — sell everything fast, grab cash NOW
                        market.append(["SELL", prod, amt])
            sell_wheat = max(0, shed.get("WHEAT", 0) - wheat_reserve)
            if sell_wheat > 0:
                if we_are_ahead:
                    market.append(["SELL", "WHEAT", min(sell_wheat, 4)])
                else:
                    market.append(["SELL", "WHEAT", sell_wheat])
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

        # Mid-day investing: buy animals + seeds + hire when money arrives mid-day.
        # This matters when hour-0 had little cash (e.g. early days) but sells during the
        # day free up money — previously that money sat idle until the next day's hour 0.
        slots_free = 10 - len(market)

        # Buy animals mid-day (only when shed is clear — farmer keeping up)
        total_animals = num_animals + animals_in_shed
        if slots_free >= 1 and total_animals < 14 and animals_in_shed <= 2 and money >= 400 and day < 22 and hour % 4 == 0 and hour > 0:
            market.append(["BUY_ANIMAL", "COW", 1])
            slots_free -= 1

        # Buy wheat feed mid-day if running low
        if slots_free >= 1 and shed.get("WHEAT", 0) < num_animals and money >= 50 and num_animals > 0 and hour % 8 == 4:
            market.append(["BUY_PRODUCT", "WHEAT", num_animals * 2])
            slots_free -= 1

        # ─── DEMAND-BASED HIRE (workload-sized, affordability-gated) ───
        # Size hands to the day's REAL watering+planting load so plants get watered early,
        # not barely. A hand realistically clears only ~4-5 tiles/day once walking, feeding
        # and caring overhead are counted (measured: 4-5 hands take until ~hour 16 to water
        # 18 plants). We target the full daily load (every plant needs water each day), then
        # hire the shortfall we can AFFORD under the Fibonacci cost curve — so idle mid-day
        # money is spent on the workers we're short of, without wasting unaffordable orders.
        if slots_free >= 1 and day < 28 and money >= 2:
            plantable = min(
                sum(seeds.get(c, 0) for c in ["MELON", "WHEAT", "STRAWBERRY", "TOMATO", "CARROT"]),
                len(empty),
            )
            care_cnt = sum(1 for _, _, t in animals if not t.get("cared_today"))
            fert_cnt = sum(1 for _, _, t in animals if t.get("fertilizer_available"))
            unwatered_cnt = sum(1 for _, _, t in plants if not t.get("watered_today"))
            # Daily watering load = ALL plants (each needs water every day), plus tiles we
            # can still plant today. Per-hand coverage is modest and shrinks as the farm
            # spreads across quadrants (more walking between distant tiles).
            coverage = max(3, 6 - num_quadrants)        # 1q->5, 2q->4, 3q->3, 4q->3
            daily_load = num_plants + plantable
            hands_for_plants = (daily_load + coverage - 1) // coverage      # ceil
            hands_for_animals = 1 if (care_cnt + fert_cnt) > 0 else 0
            needed = hands_for_plants + hands_for_animals + 1               # +1 feeder
            # PROFIT CAP: each extra hand costs fib(n) that day (1,1,2,3,5,8,13,21,34,...),
            # so hands get exponentially expensive. A hand generates only ~$150/day of
            # marginal crop revenue, so hiring past ~hand 11 (fib=144) loses money even
            # though it would keep more plants watered. Cap the target to the profitable
            # count: the largest k where fib(k-1) <= a per-hand daily value. Early game the
            # cap rarely binds (few hands needed); mid/late game it prevents wage blowout.
            hand_value = P.get("hand_value", 150)
            max_profitable = 1
            while _fib(max_profitable) <= hand_value and max_profitable < 20:
                max_profitable += 1
            # max_profitable is the count where the NEXT hire would exceed hand_value.
            needed = min(needed, max_profitable)
            # Live work must exist right now (don't hire into an already-idle farm).
            has_live_work = (unwatered_cnt > 0) or (plantable > 0) or (care_cnt + fert_cnt > 2)
            shortfall = needed - num_hands
            if has_live_work and shortfall > 0:
                hires_today = farm.get("hires_today", num_hands)
                can_afford = affordable_hires(money, hires_today, shortfall, reserve=0)
                to_hire = min(can_afford, slots_free)
                for _ in range(max(0, to_hire)):
                    market.append(["HIRE"])

    # ═══ FARMER ═══
    farmer_pos = tuple(farm["farmer"])
    # End-game: don't build/place, just feed + harvest + collect
    endgame = day >= P["endgame_day"]
    farmer_action = decide_farmer(farmer_pos, farm, private, plants, animals, empty, weeds, empty_pastures, day, endgame)

    # ═══ HANDS ═══
    hands_positions = [tuple(hands[i]) for i in range(num_hands)]
    hands_actions = plan_hands(hands_positions, farm, plants, empty, seeds, day, weeds, private)

    if hour == 0:
        log("D", {"d": day, "$": int(money), "p": num_plants, "a": num_animals,
                  "h": num_hands, "sa": animals_in_shed,
                  "q": num_quadrants, "e": len(empty),
                  "ext": int(extraction_value)})

    return {"farmer": farmer_action, "hands": hands_actions, "market": market[:10]}
