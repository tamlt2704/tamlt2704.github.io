"""
MicroManager Bot v2 — Replan Every Turn
========================================
Core philosophy: REPLAN EVERY SINGLE TURN from current board state.
No stale plans. No state machines. Pure reactive micro-management.

Each turn:
  1. Scan board → generate task list
  2. Assign tasks to workers with exact move costs
  3. Return: one action per worker (the first step of their assigned path)

Market decisions happen in parallel every turn.
"""

import sys
from collections import deque

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

TOTAL_DAYS = 30
HOURS_PER_DAY = 24
SHED = [(4, 4), (5, 4), (4, 5), (5, 5)]
SHED_SET = set(SHED)

# Animal ring — tiles for pastures (near shed for short farmer circuit)
ANIMAL_RING = [
    (3, 4), (6, 4), (4, 3), (5, 3),
    (3, 3), (6, 3), (3, 5), (6, 5), (4, 6), (5, 6),
    (4, 2), (5, 2), (2, 4), (7, 4),
    (2, 3), (7, 3), (2, 5), (7, 5),
]


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def nearest_shed(pos):
    return min(SHED, key=lambda s: dist(pos, s))


def bfs_path(src, dst, bs):
    """BFS shortest path, return full list of directions."""
    if src == dst:
        return []
    parent = {src: None}
    q = deque([src])
    while q:
        cx, cy = q.popleft()
        if (cx, cy) == dst:
            break
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < bs and 0 <= ny < bs and (nx, ny) not in parent:
                parent[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
    if dst not in parent:
        return []
    path = []
    cur = dst
    while parent[cur] is not None:
        prev = parent[cur]
        dx, dy = cur[0] - prev[0], cur[1] - prev[1]
        path.append({(1, 0): "EAST", (-1, 0): "WEST", (0, 1): "SOUTH", (0, -1): "NORTH"}[(dx, dy)])
        cur = prev
    path.reverse()
    return path


def first_step(src, dst, bs):
    """Return just the first move direction toward dst."""
    if src == dst:
        return None
    path = bfs_path(src, dst, bs)
    return path[0] if path else None


def fib_cost(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ═══════════════════════════════════════════════════════════════════════════════
# TASK SYSTEM — scan board, generate prioritized task list
# ═══════════════════════════════════════════════════════════════════════════════

def generate_tasks(tiles, bs, shed, seeds, day, remaining, unlocked_quads, num_animals, prices=None, straw_demand=0):
    """Generate ALL actionable tasks this turn.
    
    ENDGAME (remaining <= 2): Focus on extracting maximum value.
    - Harvest all ready crops (top priority)
    - Collect all fertilizer (top priority)
    - Feed animals (keeps them producing)
    - No planting, minimal watering
    """
    tasks = []
    empty_tiles = []
    empty_pastures = []
    animals_in_shed = shed.get("COW", 0) + shed.get("SHEEP", 0)
    is_endgame = remaining <= 1  # only last day is pure harvest mode

    for y in range(bs):
        for x in range(bs):
            t = tiles[y][x]
            if t is None:
                qn = ('N' if y < bs // 2 else 'S') + ('W' if x < bs // 2 else 'E')
                if qn in unlocked_quads and (x, y) not in SHED_SET:
                    empty_tiles.append((x, y))
                continue
            if not isinstance(t, dict):
                continue

            kind = t.get("kind")

            # === ANIMAL TASKS — chained ===
            if "animal" in t:
                chain = []
                needs_wheat = False
                if not t.get("fed_today"):
                    chain.append("FEED")
                    needs_wheat = True
                if not t.get("cared_today"):
                    chain.append("CARE")
                if t.get("fertilizer_available"):
                    chain.append("COLLECT_FERTILIZER")
                if t.get("yield_units", 0) > 0:
                    chain.append("HARVEST")

                if chain:
                    if is_endgame:
                        prio = 300
                    else:
                        # FEED is critical (escape risk) → 300
                        # CARE is high value (unlocks milk/wool/fertilizer) → 270
                        # COLLECT_FERTILIZER alone → 200
                        if "FEED" in chain:
                            prio = 300
                        elif "CARE" in chain:
                            prio = 270  # CARE unlocks production — must happen every day
                        elif "COLLECT_FERTILIZER" in chain:
                            prio = 200
                        else:
                            prio = 180
                    pre = "NEED_WHEAT" if needs_wheat else None
                    tasks.append((prio, "ANIMAL_CHAIN", (x, y), "|".join(chain), pre))

            # === PLANT TASKS ===
            elif kind == "PLANT":
                if not t.get("watered_today"):
                    if is_endgame:
                        # Endgame: only water urgently dying plants that have upcoming yield
                        if t.get("consecutive_unwatered", 0) > 0:
                            tasks.append((100, "WATER", (x, y), "WATER", None))
                    else:
                        urgency = t.get("consecutive_unwatered", 0)
                        # When animal products crash, crops are main revenue — water is CRITICAL
                        milk_p = float(prices.get("MILK", 150)) if prices else 150
                        wool_p = float(prices.get("WOOL", 200)) if prices else 200
                        animal_crash = milk_p < 80 and wool_p < 100
                        # Urgent: plant about to die → 290 (just below FEED 300)
                        # Animal crash: all water is urgent → 285
                        # Normal: daily water → 270 (same priority as CARE)
                        if urgency > 0:
                            prio = 290
                        elif animal_crash:
                            prio = 285  # crops are life — water everything NOW
                        else:
                            prio = 270
                        tasks.append((prio, "WATER", (x, y), "WATER", None))
                if t.get("yield_units", 0) > 0:
                    # Endgame: harvest is TOP priority. Normal: lowest priority (crops wait)
                    prio = 290 if is_endgame else 100
                    tasks.append((prio, "HARVEST_CROP", (x, y), "HARVEST", None))
                # FERTILIZE ongoing crops — doubles their yield on next production!
                # Only for TOMATO and STRAWBERRY (ongoing=True), and only if not already fertilized
                crop = t.get("crop", "")
                if crop in ("TOMATO", "STRAWBERRY") and not is_endgame:
                    fert_until = t.get("fertilized_until_day", -1)
                    if fert_until < day:  # not currently fertilized
                        # Low priority — only fertilize when nothing else to do
                        tasks.append((150, "FERTILIZE", (x, y), "FERTILIZE", "NEED_FERT"))

            # === PASTURE without animal ===
            elif kind in ("PASTURE", "COOP") and "animal" not in t:
                empty_pastures.append((x, y))

            # === WEEDS (skip in endgame) ===
            elif kind == "WEED" and not is_endgame:
                # Weeds spread! Each weed can infect adjacent tiles. Kill early.
                tasks.append((160, "DIG", (x, y), "DIG", None))

    # === PLACE animals (not in endgame) ===
    if not is_endgame and animals_in_shed > 0 and empty_pastures:
        placed = 0
        for px, py in empty_pastures:
            if placed >= animals_in_shed:
                break
            animal_type = "COW" if shed.get("COW", 0) > placed else "SHEEP"
            tasks.append((280, "PLACE", (px, py), f"PLACE {animal_type}", f"PICKUP_{animal_type}"))
            placed += 1

    # === BUILD + PLACE (not in endgame) ===
    if not is_endgame and animals_in_shed > len(empty_pastures):
        need_build = animals_in_shed - len(empty_pastures)
        built = 0
        for ax, ay in ANIMAL_RING:
            if built >= need_build:
                break
            if 0 <= ax < bs and 0 <= ay < bs and tiles[ay][ax] is None:
                qn = ('N' if ay < bs // 2 else 'S') + ('W' if ax < bs // 2 else 'E')
                if qn in unlocked_quads:
                    tasks.append((275, "BUILD", (ax, ay), "BUILD_PASTURE", None))
                    built += 1

    # === PLANT (not in endgame) ===
    if not is_endgame and remaining > 2:
        total_seeds = sum(seeds.values())
        if total_seeds > 0:
            pastures_needed = max(0, 14 - num_animals - len(empty_pastures))
            reserved = set(ANIMAL_RING[:pastures_needed])
            shed_center = (4, 4)
            plantable = [(x, y) for x, y in empty_tiles
                         if (x, y) not in reserved]
            plantable.sort(key=lambda p: dist(p, shed_center))

            # PLANT priority is ALWAYS high when empty tiles exist
            # Empty tiles spawn weeds every day — planting is urgent every day
            # Priority 250: below WATER(270) and CARE(270) but above normal tasks
            plant_prio = 250

            planted = 0
            for ex, ey in plantable:
                crop = _pick_crop(seeds, day, remaining, planted, prices, straw_demand=straw_demand)
                if crop is None:
                    break
                tasks.append((plant_prio, "PLANT", (ex, ey), f"PLANT {crop}", None))
                planted += 1
                if planted >= total_seeds:
                    break

    return tasks


def _pick_crop(seeds, day, remaining, already_planned, prices=None, straw_demand=0):
    """Pick best crop given timing and market prices + shop demand."""
    if remaining < 4:
        return None
    if prices is None:
        prices = {}
    
    straw_price = float(prices.get("STRAWBERRY", 150))
    milk_p = float(prices.get("MILK", 150))
    wool_p = float(prices.get("WOOL", 200))
    animal_crash = milk_p < 80 and wool_p < 100
    straw_attractive = straw_price >= 120 or straw_demand >= 6
    
    if day <= 5:
        order = ["MELON", "WHEAT", "STRAWBERRY", "CARROT"]
    elif animal_crash and remaining >= 12:
        order = ["STRAWBERRY", "TOMATO", "WHEAT", "CARROT"]
    elif day <= 15 and remaining >= 12:
        if straw_attractive:
            order = ["STRAWBERRY", "TOMATO", "WHEAT", "CARROT"]
        else:
            order = ["WHEAT", "TOMATO", "STRAWBERRY", "CARROT"]
    elif remaining >= 5:
        order = ["WHEAT", "CARROT"]
    else:
        order = ["WHEAT", "CARROT"]

    for crop in order:
        if seeds.get(crop, 0) > already_planned:
            return crop
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE-TURN PLANNER — assign one action per worker per turn
# ═══════════════════════════════════════════════════════════════════════════════

def assign_actions(tasks, positions, inventories, shed, bs):
    """Assign one task to each worker for THIS turn only.
    
    Returns list of actions (one per worker).
    Uses greedy: highest-priority task → nearest available worker.
    """
    num_workers = len(positions)
    actions = [None] * num_workers
    assigned = [False] * num_workers  # worker already has a task this turn

    # Sort by priority descending
    tasks.sort(key=lambda t: t[0], reverse=True)

    # Track which targets are claimed (no two workers on same target)
    claimed_targets = set()

    for prio, kind, target, action_at_target, pre_action in tasks:
        if target in claimed_targets:
            continue

        # Find nearest available worker
        best_worker = -1
        best_dist = 999

        for wi in range(num_workers):
            if assigned[wi]:
                continue
            pos = positions[wi]
            inv = inventories[wi] if wi < len(inventories) else {}

            # If task needs wheat, worker must either have it or be near shed
            if pre_action == "NEED_WHEAT":
                if inv.get("WHEAT", 0) <= 0:
                    # Must go to shed first — add shed distance
                    sd = dist(pos, nearest_shed(pos))
                    td = sd + 1 + dist(nearest_shed(pos), target)  # shed + pickup + target
                else:
                    td = dist(pos, target)
            elif pre_action and pre_action.startswith("PICKUP_"):
                # Must go to shed to pickup animal
                sd = dist(pos, nearest_shed(pos))
                td = sd + 1 + dist(nearest_shed(pos), target)
            else:
                td = dist(pos, target)

            if td < best_dist:
                best_dist = td
                best_worker = wi

        if best_worker < 0:
            continue

        wi = best_worker
        pos = positions[wi]
        inv = inventories[wi] if wi < len(inventories) else {}
        assigned[wi] = True
        claimed_targets.add(target)

        # Determine the ONE action this worker takes this turn
        if pre_action == "NEED_WHEAT" and inv.get("WHEAT", 0) <= 0:
            # Need to get wheat first
            shed_pos = nearest_shed(pos)
            if pos in SHED_SET or pos == shed_pos:
                # At shed — pickup wheat
                wheat_avail = shed.get("WHEAT", 0)
                qty = min(8, wheat_avail)
                if qty > 0:
                    actions[wi] = ["PICKUP", "WHEAT", qty]
                else:
                    actions[wi] = ["PASS"]  # no wheat available
            else:
                # Move toward shed
                step = first_step(pos, shed_pos, bs)
                actions[wi] = [step] if step else ["PASS"]

        elif pre_action and pre_action.startswith("PICKUP_"):
            animal_type = pre_action.split("_")[1]
            if inv.get(animal_type, 0) > 0:
                # Already carrying — go to target
                if pos == target:
                    actions[wi] = _parse_action(action_at_target)
                else:
                    step = first_step(pos, target, bs)
                    actions[wi] = [step] if step else ["PASS"]
            else:
                # Need to pickup from shed
                shed_pos = nearest_shed(pos)
                if pos in SHED_SET or pos == shed_pos:
                    actions[wi] = ["PICKUP", animal_type, 1]
                else:
                    step = first_step(pos, shed_pos, bs)
                    actions[wi] = [step] if step else ["PASS"]

        elif pos == target:
            # At target — do the action
            actions[wi] = _parse_action(action_at_target)
        else:
            # Move toward target
            step = first_step(pos, target, bs)
            actions[wi] = [step] if step else ["PASS"]

    # Workers with no task: go drop items at shed, or PASS
    for wi in range(num_workers):
        if actions[wi] is None:
            inv = inventories[wi] if wi < len(inventories) else {}
            carried = sum(v for k, v in inv.items()) if isinstance(inv, dict) else 0
            pos = positions[wi]
            if carried > 0:
                # Go drop
                shed_pos = nearest_shed(pos)
                if pos in SHED_SET or pos == shed_pos:
                    actions[wi] = ["DROP"]
                else:
                    step = first_step(pos, shed_pos, bs)
                    actions[wi] = [step] if step else ["PASS"]
            else:
                actions[wi] = ["PASS"]

    return actions


def _parse_action(action_str):
    """Convert action string to action list."""
    if not action_str or action_str == "PASS":
        return ["PASS"]
    parts = action_str.split()
    if parts[0] == "PLANT" and len(parts) >= 2:
        return ["PLANT", parts[1]]
    elif parts[0] == "PLACE" and len(parts) >= 2:
        return ["PLACE", parts[1]]
    elif parts[0] == "PICKUP" and len(parts) >= 3:
        return ["PICKUP", parts[1], int(parts[2])]
    else:
        return [parts[0]]


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET DECISIONS
# ═══════════════════════════════════════════════════════════════════════════════

def decide_market(obs, day, hour, remaining, num_animals, num_plants, num_hands, bs):
    """Market orders every turn. Sell everything, hire aggressively, scale animals."""
    player = obs["player"]
    farm = obs["farms"][player]
    priv = obs.get("private", {})
    money = farm["money"]
    shed = priv.get("shed", {})
    seeds = priv.get("seeds", {})
    hires_today = farm.get("hires_today", 0)
    prices = obs.get("market", {}).get("prices", {})
    tiles = farm["tiles"]
    nq = len(farm.get("unlocked_quadrants", ["NW"]))
    unlocked_quads = set(farm.get("unlocked_quadrants", ["NW"]))

    orders = []
    spent = 0

    # === OPPONENT INTELLIGENCE ===
    # We can see opponent's farm — count their animals to predict what they'll sell
    opp_idx = 1 - player
    opp_farm = obs["farms"][opp_idx] if opp_idx < len(obs["farms"]) else {}
    opp_tiles = opp_farm.get("tiles", [])
    opp_bs = len(opp_tiles)
    opp_cows = 0
    opp_sheep = 0
    for oy in range(opp_bs):
        for ox in range(opp_bs):
            ot = opp_tiles[oy][ox]
            if isinstance(ot, dict) and "animal" in ot:
                if ot["animal"] == "COW":
                    opp_cows += 1
                elif ot["animal"] == "SHEEP":
                    opp_sheep += 1
    
    # Opponent's likely revenue stream:
    # Many cows -> they'll flood MILK -> we should go ALL SHEEP (different product)
    # Many sheep -> they'll flood WOOL -> we should go ALL COWS (different product)
    # STRATEGY 5 (Product Switching): NEVER compete on the same product!
    # If we sell the same thing, we crash each other's prices. Go opposite.
    opp_milk_heavy = opp_cows >= 5  # opponent will flood milk
    opp_wool_heavy = opp_sheep >= 5  # opponent will flood wool
    # Shops consume products every 4 steps (6/day per shop per product)
    # More shops consuming a product = higher sustained demand = price stays high
    SHOP_PRODUCTS = {
        "BAKERY": ["EGG", "WHEAT"],
        "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
        "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
        "YARN_STORE": ["WOOL"],  # single-product = 2x consumption
        "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
        "PET_CAFE": ["CARROT"],
        "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"],
        "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
    }
    town = obs.get("town", {})
    unlocked_shops = town.get("unlocked_shops", [])
    
    # Calculate drain rate per product (units consumed per day by shops)
    # Each shop consumes 6/day per product (every 4 of 24 steps)
    # Single-product shops consume 2x = 12/day
    shop_drain = {}  # product -> daily drain from shops
    for shop_name in unlocked_shops:
        products = SHOP_PRODUCTS.get(shop_name, [])
        multiplier = 2 if len(products) == 1 else 1
        for prod in products:
            shop_drain[prod] = shop_drain.get(prod, 0) + 6 * multiplier
    
    # High demand products = shops drain > 6/day (more than 1 shop consuming)
    milk_demand = shop_drain.get("MILK", 0)
    wool_demand = shop_drain.get("WOOL", 0)
    straw_demand = shop_drain.get("STRAWBERRY", 0)

    # === DAY 0 OPENING ===
    animals_on_board = sum(1 for y in range(bs) for x in range(bs)
                          if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x])
    if day == 0 and hour == 0 and animals_on_board == 0:
        # Proven opening: melon for D10 windfall + wheat for quick fill + animals
        # Tomato added from day 3+ when budget allows (too expensive for D0)
        return [
            ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
            ["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2],
            ["BUY_SEED", "MELON", 4], ["BUY_SEED", "WHEAT", 14],
            ["BUY_PRODUCT", "WHEAT", 10],
        ]

    # === SELL with price awareness ===
    # On hour 0, limit sells to leave slots for hires (max 4 sell orders)
    # On other hours, sells can use all available slots
    max_sell_slots = 4 if hour == 0 else 8
    
    # Price thresholds — hold premium products when price crashes
    # ADAPTIVE: adjust thresholds based on remaining time and market conditions
    # Late game: lower thresholds (better to sell cheap than hold and liquidate)
    milk_price = float(prices.get("MILK", 150))
    wool_price = float(prices.get("WOOL", 200))
    straw_price_now = float(prices.get("STRAWBERRY", 150))
    
    # Late-game pressure: lower thresholds as days run out
    # Day 25+: accept lower prices rather than risk liquidation at bottom
    if remaining <= 5:
        time_pressure = max(30, 100 - (5 - remaining) * 15)  # 100→30 over last 5 days
    else:
        time_pressure = 100  # normal threshold
    
    milk_threshold = time_pressure
    wool_threshold = time_pressure
    
    # If one product is dead, be more aggressive selling the other (it's our revenue)
    if wool_price < 30:
        milk_threshold = min(milk_threshold, 50)  # sell milk at any decent price
    if milk_price < 30:
        wool_threshold = min(wool_threshold, 50)  # sell wool at any decent price
    
    SELL_THRESHOLDS = {
        "MILK": milk_threshold,
        "WOOL": wool_threshold,
        "STRAWBERRY": min(80, time_pressure),
        "MELON": min(50, time_pressure),
    }
    # Always sell immediately regardless of price:
    # FERTILIZER: price barely drops even at high volume ($100->$80 at +100 units)
    # WHEAT: log curve, almost flat ($25->$20 at +300)
    ALWAYS_SELL = ["FERTILIZER", "EGG", "CARROT"]
    
    for prod in ALWAYS_SELL:
        q = shed.get(prod, 0)
        if q > 0 and len(orders) < max_sell_slots:
            orders.append(["SELL", prod, q])
    
    # Price-sensitive products: SHOP-DRAIN AWARE selling
    # CORE STRATEGY: Sell LESS than shops drain → price keeps RISING every day
    # If we sell 3 wool/day and YARN_STORE drains 12/day → net -9/day → price rises!
    # If no shops drain a product → sell minimum to avoid crashing our own price
    #
    # MARKET CORNERING: First 5 days after shops unlock for a product, HOLD entirely
    # to let shops drain inventory and inflate the price. Then sell at premium.
    #
    # SABOTAGE: Against heavy opponents, one-time dump their product to crash it
    
    def drain_aware_rate(prod, current_price, base_price, daily_drain, is_opp_product, day):
        """Sell at a rate that keeps net inventory dropping (price rising).
        
        Key formula: if we sell X/hour and shops drain Y/day (Y/24 per hour),
        then net inventory change = X - Y/24 per hour.
        For price to rise: X < Y/24 → sell fewer than shops drain per hour.
        """
        # How many can we safely sell per market order (per hour)?
        # Shops drain this product at `daily_drain` units per day = drain/24 per hour
        # We want: our_sell_per_hour < drain_per_hour (so price keeps rising)
        # But we also need to actually sell our products for revenue!
        # Sweet spot: sell at 50-70% of drain rate → price rises slowly, we get revenue
        drain_per_hour = daily_drain / 24.0
        
        if daily_drain >= 12:
            # Strong shop demand → sell up to 70% of drain (price still rises)
            safe_rate = max(1, int(drain_per_hour * 0.7))
        elif daily_drain >= 6:
            # Moderate demand → sell up to 50% of drain
            safe_rate = max(1, int(drain_per_hour * 0.5))
        else:
            # No/weak shop demand → sell very carefully (1-2 per order)
            safe_rate = 1
        
        # Price-based adjustment: if price is already crashing, sell even less
        ratio = current_price / max(base_price, 1)
        if ratio < 0.5:
            safe_rate = 0  # price dead, hold
        elif ratio < 0.7:
            safe_rate = min(safe_rate, 1)  # price low, minimum only
        
        # No early-game hold — revenue is needed for hiring and animal purchases
        # The drain-aware rate already limits overselling sufficiently
        
        # Sabotage: dump opponent's product faster to crash their revenue
        if is_opp_product and ratio >= 0.7:
            safe_rate = max(safe_rate, 3)  # override: sell at least 3 to damage them
        
        # Cap at product-specific max (avoid self-crash from quadratic curves)
        PRODUCT_MAX = {"WOOL": 3, "MILK": 3, "STRAWBERRY": 3, "MELON": 5}
        return min(safe_rate, PRODUCT_MAX.get(prod, 3))
    
    BASES = {"WOOL": 200, "MILK": 160, "STRAWBERRY": 120, "MELON": 250}
    
    price_sensitive = []
    for prod, base in BASES.items():
        q = shed.get(prod, 0)
        if q <= 0:
            continue
        price = float(prices.get(prod, 0))
        threshold = SELL_THRESHOLDS.get(prod, 50)
        demand = shop_drain.get(prod, 0)
        is_opp_product = (prod == "MILK" and opp_milk_heavy) or (prod == "WOOL" and opp_wool_heavy)
        max_batch = drain_aware_rate(prod, price, base, demand, is_opp_product, day)
        # Sell if: rate > 0 AND (price above threshold OR last days OR shed overflow OR sabotage)
        if max_batch > 0 and (price >= threshold or remaining <= 2 or q > 30 or is_opp_product):
            sell_qty = min(q, max_batch)
            if remaining <= 2:
                sell_qty = q  # liquidation
            price_sensitive.append((price * sell_qty, prod, sell_qty))
    
    price_sensitive.sort(reverse=True)
    for _, prod, q in price_sensitive:
        if len(orders) >= max_sell_slots:
            break
        orders.append(["SELL", prod, q])
    
    # Sell excess wheat (keep what's needed for feeding animals + buffer for day 0-2)
    if day >= 2:
        wheat_keep = num_animals + 2
        wheat_sell = shed.get("WHEAT", 0) - wheat_keep
        if wheat_sell > 0 and len(orders) < max_sell_slots + 1:
            orders.append(["SELL", "WHEAT", wheat_sell])

    # === LIQUIDATION (last day — sell everything in shed) ===
    if remaining <= 0:
        orders = []
        for prod in ["FERTILIZER", "WHEAT", "MILK", "WOOL", "MELON", "STRAWBERRY", "CARROT", "EGG"]:
            q = shed.get(prod, 0)
            if q > 0 and len(orders) < 10:
                orders.append(["SELL", prod, q])
        return orders[:10]

    # === ENDGAME (days 28-29): sell everything, still hire to harvest/collect ===
    if remaining <= 2:
        # Sell ALL shed contents
        orders = []
        for prod in ["FERTILIZER", "MILK", "WOOL", "MELON", "STRAWBERRY", "CARROT", "EGG"]:
            q = shed.get(prod, 0)
            if q > 0 and len(orders) < 6:
                orders.append(["SELL", prod, q])
        # Sell wheat ABOVE what we need for feeding (keep num_animals for feed)
        wheat_keep = num_animals if remaining > 0 else 0
        wheat_sell = shed.get("WHEAT", 0) - wheat_keep
        if wheat_sell > 0 and len(orders) < 7:
            orders.append(["SELL", "WHEAT", wheat_sell])
        # Still hire workers to harvest/collect/feed
        if hour == 0:
            sell_rev = sum(o[2] * prices.get(o[1], 50) for o in orders if o[0] == "SELL") * 0.7
            endgame_budget = money + int(sell_rev)
            for i in range(8):
                cost = fib_cost(hires_today + i)
                if endgame_budget >= cost and len(orders) < 10:
                    orders.append(["HIRE"])
                    endgame_budget -= cost
        # Buy wheat for feed if needed (to keep animals producing fertilizer)
        if shed.get("WHEAT", 0) < num_animals and len(orders) < 10:
            wp = max(1, int(prices.get("WHEAT", 25)))
            qty = min(num_animals, (money - 50) // wp) if money > 50 else 0
            if qty > 0:
                orders.append(["BUY_PRODUCT", "WHEAT", qty])
        return orders[:10]

    # Budget = money + sell revenue from THIS turn's sells
    sell_rev = sum(o[2] * prices.get(o[1], 50) for o in orders if o[0] == "SELL") * 0.7
    budget = money + int(sell_rev)
    spent = 0

    # === HIRE (always maximum — workers generate more value than they cost) ===
    # From day 7+, hire aggressively to reach 12 workers. Fib cost resets daily.
    # CRITICAL: Hire FIRST (before buys) because we can only submit 10 orders total.
    # On hour 0, reserve slots for hires. Other hours just do sells + buys.
    if hour == 0:
        target_hires = 12 if day >= 7 else (8 if day >= 2 else 5)
        for i in range(target_hires):
            cost = fib_cost(hires_today + i)
            if budget - spent >= cost and len(orders) < 10:
                orders.append(["HIRE"])
                spent += cost
            else:
                break

    # === BUY WHEAT FOR FEED (every turn, minimal buffer) ===
    # CRITICAL: animals MUST be fed or they escape after 2 days. Always keep minimum wheat.
    if num_animals > 0 and len(orders) < 10:
        wheat_have = shed.get("WHEAT", 0)
        wheat_need = num_animals + 2
        deficit = wheat_need - wheat_have
        if deficit > 0:
            wp = max(1, int(prices.get("WHEAT", 25)))
            max_qty = max(0, (budget - spent - 50) // wp)
            qty = min(deficit, max_qty, num_animals + 2)
            if qty > 0 and len(orders) < 10:
                orders.append(["BUY_PRODUCT", "WHEAT", qty])
                spent += wp * qty
        # EMERGENCY: if shed has 0 wheat and we can afford even 1, buy it
        elif wheat_have == 0 and budget - spent >= 25:
            orders.append(["BUY_PRODUCT", "WHEAT", 1])
            spent += 25

    # === BUY ANIMALS — scale to 14 max by day 15 ===
    # Only delay animals on days 2-4 when budget is tight and workforce needs priority
    # From day 5+, always buy animals (revenue from animals funds more hiring)
    total_animals = num_animals + shed.get("COW", 0) + shed.get("SHEEP", 0)
    workforce_ready = num_hands >= 8 or day <= 1 or day >= 5
    if total_animals < 14 and day <= 15 and workforce_ready and len(orders) < 10:
        cost_cow = 400
        cost_sheep = 500
        n_cows = shed.get("COW", 0) + sum(1 for y in range(bs) for x in range(bs)
                                           if isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "COW")
        n_sheep = shed.get("SHEEP", 0) + sum(1 for y in range(bs) for x in range(bs)
                                              if isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "SHEEP")
        # Buy based on PRODUCT SWITCHING strategy + shop demand + opponent counter
        # RULE: Go OPPOSITE from opponent. They crash their own market, we get ours clean.
        # If opponent has 5+ cows → they'll flood milk → we go ALL SHEEP (wool stays clean)
        # If opponent has 5+ sheep → they'll flood wool → we go ALL COWS (milk stays clean)
        reserve = 50
        milk_price = float(prices.get("MILK", 150))
        wool_price = float(prices.get("WOOL", 200))
        
        # Product switching: go opposite from opponent (highest priority)
        if opp_milk_heavy:
            # Opponent floods milk → we go ALL SHEEP (wool market stays clean for us)
            prefer_sheep = True
            all_in = True
        elif opp_wool_heavy:
            # Opponent floods wool → we go ALL COWS (milk market stays clean for us)
            prefer_sheep = False
            all_in = True
        else:
            # No strong opponent signal → use price + demand scoring
            milk_score = milk_price + milk_demand * 5
            wool_score = wool_price + wool_demand * 5
            if wool_score >= milk_score * 1.2:
                prefer_sheep = True
                all_in = False
            elif milk_score >= wool_score * 1.2:
                prefer_sheep = False
                all_in = False
            else:
                prefer_sheep = n_cows > n_sheep  # balance
                all_in = False
        
        while total_animals < 14 and len(orders) < 10:
            if prefer_sheep and budget - spent >= cost_sheep + reserve:
                orders.append(["BUY_ANIMAL", "SHEEP", 1])
                spent += cost_sheep
                n_sheep += 1
                total_animals += 1
                if not all_in:
                    prefer_sheep = False  # alternate
            elif (not prefer_sheep) and budget - spent >= cost_cow + reserve:
                orders.append(["BUY_ANIMAL", "COW", 1])
                spent += cost_cow
                n_cows += 1
                total_animals += 1
                if not all_in:
                    prefer_sheep = True  # alternate
            elif budget - spent >= cost_cow + reserve:
                # Fallback: cow is cheaper
                orders.append(["BUY_ANIMAL", "COW", 1])
                spent += cost_cow
                n_cows += 1
                total_animals += 1
            elif budget - spent >= cost_sheep + reserve:
                orders.append(["BUY_ANIMAL", "SHEEP", 1])
                spent += cost_sheep
                n_sheep += 1
                total_animals += 1
            else:
                break

    # === BUY SEEDS (proactively — always keep seeds stocked) ===
    # CRITICAL: Empty tiles spawn weeds. ALWAYS maintain seed stock.
    # Guaranteed minimum: if empty tiles exist and seeds < 5, buy wheat seeds UNCONDITIONALLY.
    if remaining > 3 and len(orders) < 10:
        total_seeds = sum(seeds.values())
        n_empty = sum(1 for y in range(bs) for x in range(bs) if tiles[y][x] is None)
        n_weeds = sum(1 for y in range(bs) for x in range(bs)
                      if isinstance(tiles[y][x], dict) and tiles[y][x].get('kind') == 'WEED')
        # Count plants that will be harvested soon (harvestable = yield_units > 0)
        n_harvestable = sum(1 for y in range(bs) for x in range(bs)
                           if isinstance(tiles[y][x], dict) and tiles[y][x].get('yield_units', 0) > 0
                           and tiles[y][x].get('kind') == 'PLANT')
        # Need seeds for: current empty + current weeds + upcoming harvested tiles
        seeds_needed = n_empty + n_weeds + n_harvestable
        seeds_wanted = max(0, seeds_needed - total_seeds)

        # GUARANTEED MINIMUM: always keep at least 5 seeds in stock
        # This costs only $50 (5 wheat × $10) but prevents catastrophic weed explosions
        if total_seeds < 5:
            seeds_wanted = max(seeds_wanted, 5 - total_seeds)
        # If many empty tiles exist, force-buy even more
        if n_empty > 5 and total_seeds < n_empty:
            seeds_wanted = max(seeds_wanted, min(10, n_empty - total_seeds))

        if seeds_wanted > 0 and len(orders) < 10:
            SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "MELON": 80, "STRAWBERRY": 100}
            
            # Guaranteed minimum: always afford at least 5 wheat seeds ($50)
            # Even if budget is tight, this is non-negotiable (weed prevention)
            min_seed_budget = 50
            
            straw_price = float(prices.get("STRAWBERRY", 150))
            melon_price = float(prices.get("MELON", 250))
            milk_p = float(prices.get("MILK", 150))
            wool_p = float(prices.get("WOOL", 200))
            
            # Detect animal product crash — pivot budget to crops
            animal_crash = milk_p < 80 and wool_p < 100 and milk_demand < 6 and wool_demand < 6
            # Strawberry is attractive if: high price OR shops consuming it (sustains price)
            straw_attractive = straw_price >= 120 or straw_demand >= 6
            # Increase seed budget when animal products are weak
            seed_budget_pct = 0.6 if animal_crash else 0.4
            seed_budget = max(min_seed_budget, int((budget - spent) * seed_budget_pct))
            
            if day <= 3 and remaining >= 12:
                # Early: melon windfall + wheat filler (proven combo)
                buy_list = [("MELON", 6), ("WHEAT", 12)]
            elif day <= 8 and remaining >= 12:
                # Mid: add tomato (ongoing, produces daily D8+) + strawberry
                if animal_crash or straw_attractive:
                    buy_list = [("STRAWBERRY", 6), ("TOMATO", 4), ("WHEAT", 6)]
                else:
                    buy_list = [("TOMATO", 4), ("WHEAT", 10), ("STRAWBERRY", 4)]
            elif remaining >= 12:
                if animal_crash or straw_attractive:
                    buy_list = [("STRAWBERRY", 8), ("TOMATO", 4), ("WHEAT", 4)]
                else:
                    buy_list = [("WHEAT", 10), ("TOMATO", 4), ("STRAWBERRY", 4)]
            elif remaining >= 5:
                buy_list = [("WHEAT", 12), ("CARROT", 4)]
            else:
                buy_list = [("WHEAT", 10)]

            for crop, max_qty in buy_list:
                cost = SEED_COST.get(crop, 50)
                qty = min(max_qty, seeds_wanted, seed_budget // max(cost, 1))
                if qty > 0 and budget - spent >= cost * qty and len(orders) < 10:
                    orders.append(["BUY_SEED", crop, qty])
                    spent += cost * qty
                    seeds_wanted -= qty

    # === BUY LAND (only expand when we can fill it immediately) ===
    # Each new quadrant adds ~21 empty tiles (25 - 4 shed). Without seeds to fill,
    # those tiles become weeds within 2-3 days and destroy the game.
    if nq < 4 and len(orders) < 10:
        land_costs = [1000, 2000, 4000]
        cost = land_costs[nq - 1] if nq <= 3 else 99999
        total_seeds = sum(seeds.values())
        n_current_weeds = sum(1 for y in range(bs) for x in range(bs)
                              if isinstance(tiles[y][x], dict) and tiles[y][x].get('kind') == 'WEED')
        # Only expand if: workforce ready, few weeds, AND have seeds to fill new land
        workforce_ready = (
            (nq == 1 and num_hands >= 6) or
            (nq == 2 and num_hands >= 8 and day >= 12) or
            (nq == 3 and num_hands >= 10 and day >= 16)
        )
        seeds_ready = total_seeds >= 10  # need some seeds for new quadrant
        weeds_controlled = n_current_weeds <= 10  # don't expand while heavily infested
        if workforce_ready and seeds_ready and weeds_controlled and budget - spent >= cost + 500:
            orders.append(["BUY_LAND"])
            spent += cost

    # Reorder: SELL first (generates cash), then HIRE, then buys
    sell_orders = [o for o in orders if o[0] == "SELL"]
    hire_orders = [o for o in orders if o[0] == "HIRE"]
    buy_orders = [o for o in orders if o[0] not in ("SELL", "HIRE")]
    orders = sell_orders + hire_orders + buy_orders

    return orders[:10]


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class MicroManager:
    def __init__(self):
        # Sticky assignments: track what each worker is heading toward
        self.assignments = {}
        # Day log for analytics
        self.day_log = []
        self._last_log_day = -1

    def __call__(self, obs, cfg=None):
        player = obs["player"]
        farm = obs["farms"][player]
        priv = obs.get("private", {})
        tiles = farm["tiles"]
        bs = len(tiles)
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        remaining = TOTAL_DAYS - day - 1
        hands = farm.get("hands", [])
        farmer_pos = tuple(farm["farmer"])
        hand_positions = [tuple(h) for h in hands]
        all_positions = [farmer_pos] + hand_positions
        num_workers = len(all_positions)
        shed = priv.get("shed", {})
        seeds = priv.get("seeds", {})
        inventories = priv.get("inventories", [{}])
        unlocked_quads = set(farm.get("unlocked_quadrants", ["NW"]))

        # Count state
        num_animals = 0
        num_plants = 0
        for y in range(bs):
            for x in range(bs):
                t = tiles[y][x]
                if isinstance(t, dict):
                    if "animal" in t:
                        num_animals += 1
                    elif t.get("kind") == "PLANT":
                        num_plants += 1

        # === MARKET (every turn) ===
        market_orders = decide_market(obs, day, hour, remaining, num_animals, num_plants,
                                      len(hands), bs)

        # === DAY LOG (hour 0 only) ===
        if hour == 0 and day != self._last_log_day:
            self._last_log_day = day
            shed_items = {k: v for k, v in shed.items() if v > 0}
            seed_items = {k: v for k, v in seeds.items() if v > 0}
            n_empty = sum(1 for y in range(bs) for x in range(bs) if tiles[y][x] is None)
            n_unwatered = sum(1 for y in range(bs) for x in range(bs)
                              if isinstance(tiles[y][x], dict) and tiles[y][x].get('kind') == 'PLANT'
                              and not tiles[y][x].get('watered_today'))
            n_unfed = sum(1 for y in range(bs) for x in range(bs)
                          if isinstance(tiles[y][x], dict) and 'animal' in tiles[y][x]
                          and not tiles[y][x].get('fed_today'))
            n_fert_avail = sum(1 for y in range(bs) for x in range(bs)
                               if isinstance(tiles[y][x], dict) and 'animal' in tiles[y][x]
                               and tiles[y][x].get('fertilizer_available'))
            n_harvestable = sum(1 for y in range(bs) for x in range(bs)
                                if isinstance(tiles[y][x], dict) and tiles[y][x].get('yield_units', 0) > 0)
            animals_in_shed = shed.get('COW', 0) + shed.get('SHEEP', 0)

            # Market order breakdown
            mkt_hires = sum(1 for m in market_orders if m[0] == 'HIRE')
            mkt_sells = [(m[1], m[2]) for m in market_orders if m[0] == 'SELL']
            mkt_buys = [(m[0], m[1] if len(m) > 1 else '', m[2] if len(m) > 2 else 0) for m in market_orders if m[0].startswith('BUY')]

            self.day_log.append({
                'day': day,
                'money': farm['money'],
                'hands': len(hands),
                'animals_board': num_animals,
                'animals_shed': animals_in_shed,
                'plants': num_plants,
                'empty': n_empty,
                'unwatered': n_unwatered,
                'unfed': n_unfed,
                'fert_avail': n_fert_avail,
                'harvestable': n_harvestable,
                'shed': shed_items,
                'seeds': seed_items,
                'market_hires': mkt_hires,
                'market_sells': mkt_sells,
                'market_buys': mkt_buys,
                'market_orders_used': len(market_orders),
            })

        # === CLEAN stale assignments ===
        # Keep sticky for multi-step tasks, clear HARVEST (over-consumes, not urgent)
        self.assignments = {k: v for k, v in self.assignments.items()
                           if k < num_workers and v[1] != "HARVEST_CROP"
                           and self._task_still_valid(v[0], v[1], tiles, bs, shed)}

        # === GENERATE TASKS ===
        # Calculate strawberry shop demand for task planning
        _shop_prods = {
            "BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
            "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"], "YARN_STORE": ["WOOL"],
            "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
            "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
        }
        _town = obs.get("town", {})
        _straw_demand = sum(6 * (2 if len(_shop_prods.get(s, [])) == 1 else 1)
                           for s in _town.get("unlocked_shops", [])
                           if "STRAWBERRY" in _shop_prods.get(s, []))

        tasks = generate_tasks(tiles, bs, shed, seeds, day, remaining,
                               unlocked_quads, num_animals,
                               obs.get("market", {}).get("prices", {}),
                               straw_demand=_straw_demand)
        is_endgame = remaining <= 1  # only last day is pure harvest mode

        # === EXECUTE assigned workers (they continue toward their target) ===
        actions = [None] * num_workers
        claimed_targets = set()

        for wi, (target, task_type, action_at, pre_action) in list(self.assignments.items()):
            claimed_targets.add(target)
            pos = all_positions[wi]
            inv = inventories[wi] if wi < len(inventories) else {}
            actions[wi] = self._execute_step(wi, pos, target, action_at, pre_action, inv, shed, bs, tiles)

        # === PRE-ASSIGN: Workers drop ONLY when inventory is FULL (7+) ===
        # KEY OPTIMIZATION: Workers should serve ALL nearby animals before returning to shed.
        # Old behavior (drop at 4+ items) caused 518 PICKUPs/game = 3.6 tasks per trip.
        # New behavior (drop at 7+) = workers serve 7+ animals per trip = ~150 PICKUPs/game.
        # Workers carrying wheat NEVER forced to drop (they're mid-circuit serving animals).
        for wi in range(num_workers):
            if wi in self.assignments:
                continue
            inv = inventories[wi] if wi < len(inventories) else {}
            if not isinstance(inv, dict):
                continue
            carried = sum(v for v in inv.values())
            has_wheat = inv.get("WHEAT", 0) > 0
            has_animal = inv.get("COW", 0) > 0 or inv.get("SHEEP", 0) > 0
            # Only drop when: inventory FULL (7+) AND no wheat (done feeding)
            # Workers with wheat stay in field — they'll get assigned next animal task
            should_drop = (not has_animal) and (not has_wheat) and carried >= 7
            if should_drop:
                pos = all_positions[wi]
                shed_pos = nearest_shed(pos)
                if pos in SHED_SET:
                    actions[wi] = ["DROP"]
                else:
                    self.assignments[wi] = (shed_pos, "DROP_ITEMS", "DROP", None)
                    step = first_step(pos, shed_pos, bs)
                    actions[wi] = [step] if step else ["PASS"]

        # === ASSIGN unassigned workers to remaining tasks ===
        # ZONE-BASED: Each worker prefers tasks NEAR THEM (within 3 tiles).
        # This prevents cross-board travel that wastes 57% of turns on movement.
        # Phase 1: assign high-priority tasks (FEED/WATER) to nearest worker within zone
        # Phase 2: assign remaining tasks to any worker
        tasks.sort(key=lambda t: t[0], reverse=True)

        # Phase 1: Zone-restricted assignment (tasks within 3 tiles of a worker)
        for prio, kind, target, action_at_target, pre_action in tasks:
            if target in claimed_targets:
                continue

            best_worker = -1
            best_score = 999

            for wi in range(num_workers):
                if actions[wi] is not None:
                    continue
                pos = all_positions[wi]
                inv = inventories[wi] if wi < len(inventories) else {}

                if pre_action == "NEED_WHEAT" and inv.get("WHEAT", 0) <= 0:
                    td = dist(pos, nearest_shed(pos)) + 1 + dist(nearest_shed(pos), target)
                elif pre_action == "NEED_FERT" and inv.get("FERTILIZER", 0) <= 0:
                    td = dist(pos, nearest_shed(pos)) + 1 + dist(nearest_shed(pos), target)
                elif pre_action and pre_action.startswith("PICKUP_"):
                    td = dist(pos, nearest_shed(pos)) + 1 + dist(nearest_shed(pos), target)
                else:
                    td = dist(pos, target)

                # No zone restriction — all workers can reach any task
                # The greedy nearest-worker selection naturally minimizes travel
                if td < best_score:
                    best_score = td
                    best_worker = wi

            if best_worker < 0:
                continue

            wi = best_worker
            pos = all_positions[wi]
            inv = inventories[wi] if wi < len(inventories) else {}
            claimed_targets.add(target)

            # Assign and take first step
            self.assignments[wi] = (target, kind, action_at_target, pre_action)
            actions[wi] = self._execute_step(wi, pos, target, action_at_target, pre_action, inv, shed, bs, tiles)

        # Unassigned workers: drop items at shed, or PASS
        # SECOND PASS: any idle worker grabs nearest unclaimed task (worker-first)
        # This catches everything the zone-restricted first pass missed
        remaining_tasks = [(p, k, t, a_t, pre) for p, k, t, a_t, pre in tasks
                           if t not in claimed_targets]
        for wi in range(num_workers):
            if actions[wi] is not None:
                continue
            inv = inventories[wi] if wi < len(inventories) else {}
            pos = all_positions[wi]

            # Find nearest remaining task this worker can do
            best_task = None
            best_d = 999
            for prio, kind, target, act, pre in remaining_tasks:
                if target in claimed_targets:
                    continue
                if pre == "NEED_WHEAT" and inv.get("WHEAT", 0) <= 0:
                    td = dist(pos, nearest_shed(pos)) + 1 + dist(nearest_shed(pos), target)
                elif pre == "NEED_FERT" and inv.get("FERTILIZER", 0) <= 0:
                    td = dist(pos, nearest_shed(pos)) + 1 + dist(nearest_shed(pos), target)
                elif pre and pre.startswith("PICKUP_"):
                    td = dist(pos, nearest_shed(pos)) + 1 + dist(nearest_shed(pos), target)
                else:
                    td = dist(pos, target)
                if td < best_d:
                    best_d = td
                    best_task = (target, kind, act, pre)

            if best_task:
                target, kind, act, pre = best_task
                claimed_targets.add(target)
                self.assignments[wi] = (target, kind, act, pre)
                actions[wi] = self._execute_step(wi, pos, target, act, pre, inv, shed, bs, tiles)
                continue

            # Fallback: drop only when inventory FULL (7+) and no wheat, otherwise PASS
            carried = sum(v for v in inv.values()) if isinstance(inv, dict) else 0
            has_wheat = inv.get("WHEAT", 0) > 0 if isinstance(inv, dict) else False
            has_animal = (inv.get("COW", 0) > 0 or inv.get("SHEEP", 0) > 0) if isinstance(inv, dict) else False
            if not has_animal and not has_wheat and carried >= 7:
                shed_pos = nearest_shed(pos)
                if pos in SHED_SET:
                    actions[wi] = ["DROP"]
                else:
                    step = first_step(pos, shed_pos, bs)
                    actions[wi] = [step] if step else ["PASS"]
            else:
                actions[wi] = ["PASS"]

        farmer_action = actions[0] if actions else ["PASS"]
        hand_actions = actions[1:] if len(actions) > 1 else []

        # === STDERR LOGGING (for Kaggle analysis) ===
        # Track actions this turn
        if not hasattr(self, '_turn_actions'):
            self._turn_actions = {}
            self._day_sells = {}
        if day not in self._turn_actions:
            self._turn_actions[day] = {}
            self._day_sells[day] = {}
        for act in [farmer_action] + hand_actions:
            if act:
                a0 = act[0]
                self._turn_actions[day][a0] = self._turn_actions[day].get(a0, 0) + 1
        for m in market_orders:
            if m and m[0] == 'SELL' and len(m) >= 3:
                self._day_sells[day][m[1]] = self._day_sells[day].get(m[1], 0) + m[2]

        # Print day summary at end of day (hour 23 only)
        if hour == 23:
            ac = self._turn_actions.get(day, {})
            sells = self._day_sells.get(day, {})
            sells_str = " ".join("%s:%d" % (k[:4], v) for k, v in sorted(sells.items(), key=lambda x: -x[1])[:4])
            print("D%02d $%5d|A:%d P:%d H:%d|F:%d C:%d W:%d Co:%d H:%d Pl:%d Pa:%d|S[%s]" % (
                day, farm['money'], num_animals, num_plants, num_workers - 1,
                ac.get('FEED', 0), ac.get('CARE', 0), ac.get('WATER', 0),
                ac.get('COLLECT_FERTILIZER', 0), ac.get('HARVEST', 0),
                ac.get('PLANT', 0), ac.get('PASS', 0),
                sells_str), file=sys.stderr)

        return {"farmer": farmer_action, "hands": hand_actions, "market": market_orders}

    def _execute_step(self, wi, pos, target, action_at_target, pre_action, inv, shed, bs, tiles):
        """Execute one step toward completing the assigned task.
        
        action_at_target can be a chain: "FEED|CARE|COLLECT_FERTILIZER"
        Worker executes one action per turn from the chain, staying at tile.
        
        OPPORTUNISTIC: If standing on unwatered plant and NOT already doing a water task,
        water it for free (costs 1 turn but saves a dedicated water worker trip).
        """
        # Opportunistic water: DISABLED — delays high-value collect runs
        # The dedicated WATER task assignment handles this better

        # Need wheat first?
        if pre_action == "NEED_WHEAT" and inv.get("WHEAT", 0) <= 0:
            shed_pos = nearest_shed(pos)
            if pos in SHED_SET:
                wheat_avail = shed.get("WHEAT", 0)
                qty = min(8, max(1, wheat_avail))  # pickup up to 8
                if qty > 0 and wheat_avail > 0:
                    return ["PICKUP", "WHEAT", qty]
                else:
                    if wi in self.assignments:
                        del self.assignments[wi]
                    return ["PASS"]
            else:
                step = first_step(pos, shed_pos, bs)
                return [step] if step else ["PASS"]

        # Need fertilizer for FERTILIZE action?
        if pre_action == "NEED_FERT" and inv.get("FERTILIZER", 0) <= 0:
            shed_pos = nearest_shed(pos)
            if pos in SHED_SET:
                fert_avail = shed.get("FERTILIZER", 0)
                if fert_avail > 0:
                    return ["PICKUP", "FERTILIZER", 1]
                else:
                    # No fertilizer in shed — cancel task
                    if wi in self.assignments:
                        del self.assignments[wi]
                    return ["PASS"]
            else:
                step = first_step(pos, shed_pos, bs)
                return [step] if step else ["PASS"]

        # Need to pickup animal?
        if pre_action and pre_action.startswith("PICKUP_"):
            animal_type = pre_action.split("_")[1]
            if inv.get(animal_type, 0) > 0:
                pass  # have it, fall through
            else:
                shed_pos = nearest_shed(pos)
                if pos in SHED_SET:
                    if shed.get(animal_type, 0) > 0:
                        return ["PICKUP", animal_type, 1]
                    else:
                        if wi in self.assignments:
                            del self.assignments[wi]
                        return ["PASS"]
                else:
                    step = first_step(pos, shed_pos, bs)
                    return [step] if step else ["PASS"]

        # At target? Execute next action in chain
        if pos == target:
            actions_chain = action_at_target.split("|")
            # Pop first action from chain
            current_action = actions_chain[0]
            remaining_chain = "|".join(actions_chain[1:]) if len(actions_chain) > 1 else ""

            if remaining_chain:
                # Update assignment with remaining chain (no pre_action needed for subsequent)
                self.assignments[wi] = (target, self.assignments[wi][1], remaining_chain, None)
            else:
                # Chain done — clear assignment
                if wi in self.assignments:
                    del self.assignments[wi]

            return _parse_action(current_action)

        # Move toward target
        step = first_step(pos, target, bs)
        return [step] if step else ["PASS"]

    def _task_still_valid(self, target, task_type, tiles, bs, shed):
        """Check if the task at target is still needed."""
        x, y = target
        if not (0 <= x < bs and 0 <= y < bs):
            return False
        t = tiles[y][x]

        if task_type == "ANIMAL_CHAIN":
            # Valid as long as animal is there and has pending work
            if not isinstance(t, dict) or "animal" not in t:
                return False
            # At least one action still needed
            return (not t.get("fed_today") or not t.get("cared_today")
                    or t.get("fertilizer_available") or t.get("yield_units", 0) > 0)
        elif task_type == "FEED":
            return isinstance(t, dict) and "animal" in t and not t.get("fed_today")
        elif task_type == "CARE":
            return isinstance(t, dict) and "animal" in t and not t.get("cared_today")
        elif task_type == "COLLECT":
            return isinstance(t, dict) and "animal" in t and t.get("fertilizer_available")
        elif task_type == "WATER":
            return isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today")
        elif task_type == "FERTILIZE":
            return (isinstance(t, dict) and t.get("kind") == "PLANT"
                    and t.get("crop") in ("STRAWBERRY", "MELON"))
        elif task_type in ("HARVEST_CROP", "HARVEST_ANIMAL"):
            return isinstance(t, dict) and t.get("yield_units", 0) > 0
        elif task_type == "PLANT":
            return t is None  # tile still empty
        elif task_type == "BUILD":
            return t is None
        elif task_type == "PLACE":
            return isinstance(t, dict) and t.get("kind") in ("PASTURE", "COOP") and "animal" not in t
        elif task_type == "DIG":
            return isinstance(t, dict) and t.get("kind") == "WEED"
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

_agent = None


def agent(obs, cfg=None):
    global _agent
    if _agent is None:
        _agent = MicroManager()
    return _agent(obs, cfg)
