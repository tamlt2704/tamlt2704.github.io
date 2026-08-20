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

def generate_tasks(tiles, bs, shed, seeds, day, remaining, unlocked_quads, num_animals):
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
                        prio = 300 if "FEED" in chain else (200 if "COLLECT_FERTILIZER" in chain else 180)
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
                        prio = 280 if urgency > 0 else 265  # plants MUST be watered daily
                        tasks.append((prio, "WATER", (x, y), "WATER", None))
                if t.get("yield_units", 0) > 0:
                    # Endgame: harvest is TOP priority. Normal: lowest priority (crops wait)
                    prio = 290 if is_endgame else 100
                    tasks.append((prio, "HARVEST_CROP", (x, y), "HARVEST", None))

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

            planted = 0
            for ex, ey in plantable:
                crop = _pick_crop(seeds, day, remaining, planted)
                if crop is None:
                    break
                tasks.append((180, "PLANT", (ex, ey), f"PLANT {crop}", None))
                planted += 1
                if planted >= total_seeds:
                    break

    return tasks


def _pick_crop(seeds, day, remaining, already_planned):
    """Pick best crop given timing and market dynamics.
    
    KEY INSIGHT from bestplay:
    - WHEAT: 132 seeds/game! #2 revenue. 3-day cycle, price rises $25->$48.
    - STRAWBERRY: 39 seeds/game. Best mid-game ($120-230). 12-day cycle.
    - MELON: 16 seeds/game. Day 0-5 only (day-10 windfall then crashes to $1).
    - CARROT: 10 seeds/game. Late game only (fast 3-day cycle).
    
    Strategy: WHEAT is the workhorse crop. Plant it everywhere.
    Strawberry for premium tiles. Melon early only.
    """
    if remaining < 4:
        return None

    if day <= 5:
        # Early: melon for day-10 windfall, wheat to fill tiles
        order = ["MELON", "WHEAT", "STRAWBERRY", "CARROT"]
    elif day <= 12 and remaining >= 12:
        # Mid: strawberry has best price ($150-230), wheat as filler
        order = ["STRAWBERRY", "WHEAT", "CARROT"]
    elif remaining >= 5:
        # Late-mid: wheat is reliable (price rising), strawberry if time
        if remaining >= 12:
            order = ["STRAWBERRY", "WHEAT", "CARROT"]
        else:
            order = ["WHEAT", "CARROT"]
    else:
        # Very late: only fast crops
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

    # === DAY 0 OPENING ===
    animals_on_board = sum(1 for y in range(bs) for x in range(bs)
                          if isinstance(tiles[y][x], dict) and "animal" in tiles[y][x])
    if day == 0 and hour == 0 and animals_on_board == 0:
        # Reduced melon (can't reliably water 8 with 5 workers). More wheat for guaranteed revenue.
        # $3000: hires=$12, 2cow=$800, 2sheep=$1000, melon=$320, wheat_seed=$80, feed=$250 = $2462
        # Leaves $538 for day 1-2 hires (critical for plant survival)
        return [
            ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
            ["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 2],
            ["BUY_SEED", "MELON", 4], ["BUY_SEED", "WHEAT", 8],
            ["BUY_PRODUCT", "WHEAT", 10],
        ]

    # === SELL ALL immediately (cash flow > price timing) ===
    for prod in ["FERTILIZER", "MILK", "WOOL", "MELON", "STRAWBERRY", "EGG", "CARROT"]:
        q = shed.get(prod, 0)
        if q > 0 and len(orders) < 8:
            orders.append(["SELL", prod, q])
    # Sell wheat from day 3+
    if day >= 3:
        wheat_keep = num_animals * 2 + 4
        wheat_sell = shed.get("WHEAT", 0) - wheat_keep
        if wheat_sell > 0 and len(orders) < 9:
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

    # === HIRE (THE #1 investment — workers generate revenue) ===
    # 12 hires costs $376. Each worker does ~8 useful actions/day worth ~$25 each = $200/day ROI.
    # ALWAYS hire maximum affordable. Workers pay for themselves same day.
    if hour == 0:
        # Target: always max out at 12 if affordable
        target_hires = 12
        if day == 0:
            target_hires = 5  # opening is fixed

        for i in range(target_hires):
            cost = fib_cost(hires_today + i)
            if budget - spent >= cost and len(orders) < 10:
                orders.append(["HIRE"])
                spent += cost
            else:
                break  # can't afford more

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

    # === BUY ANIMALS — scale to 14 max by day 13 ===
    total_animals = num_animals + shed.get("COW", 0) + shed.get("SHEEP", 0)
    if total_animals < 14 and day <= 13 and len(orders) < 10:
        # Earlier is better — don't hold cash, invest in animals immediately
        cost_cow = 400
        cost_sheep = 500
        n_cows = shed.get("COW", 0) + sum(1 for y in range(bs) for x in range(bs)
                                           if isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "COW")
        n_sheep = shed.get("SHEEP", 0) + sum(1 for y in range(bs) for x in range(bs)
                                              if isinstance(tiles[y][x], dict) and tiles[y][x].get("animal") == "SHEEP")
        # Buy balanced: alternate cow/sheep. Sheep more valuable (wool > milk).
        reserve = 50
        while total_animals < 14 and len(orders) < 10:
            if n_sheep < n_cows and budget - spent >= cost_sheep + reserve:
                orders.append(["BUY_ANIMAL", "SHEEP", 1])
                spent += cost_sheep
                n_sheep += 1
                total_animals += 1
            elif n_cows <= n_sheep and budget - spent >= cost_cow + reserve:
                orders.append(["BUY_ANIMAL", "COW", 1])
                spent += cost_cow
                n_cows += 1
                total_animals += 1
            elif budget - spent >= cost_cow + reserve:
                orders.append(["BUY_ANIMAL", "COW", 1])
                spent += cost_cow
                n_cows += 1
                total_animals += 1
            else:
                break

    # === BUY SEEDS (every turn — empty tiles and cleared weeds need planting) ===
    if remaining > 3 and len(orders) < 10:
        total_seeds = sum(seeds.values())
        n_empty = sum(1 for y in range(bs) for x in range(bs) if tiles[y][x] is None)
        n_weeds = sum(1 for y in range(bs) for x in range(bs)
                      if isinstance(tiles[y][x], dict) and tiles[y][x].get('kind') == 'WEED')
        # Need seeds for empty tiles + weeds that will be cleared
        seeds_wanted = max(0, (n_empty + n_weeds) - total_seeds)

        if seeds_wanted > 0 and budget - spent >= 20:
            seed_budget = int((budget - spent) * 0.4)  # up to 40% on seeds
            SEED_COST = {"WHEAT": 10, "CARROT": 20, "MELON": 80, "STRAWBERRY": 100}

            if day <= 3 and remaining >= 12:
                buy_list = [("MELON", 8), ("WHEAT", 10)]
            elif day <= 8 and remaining >= 12:
                buy_list = [("WHEAT", 10), ("STRAWBERRY", 6)]
            elif remaining >= 12:
                buy_list = [("WHEAT", 10), ("STRAWBERRY", 8)]
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

    # === BUY LAND (only expand when workforce can handle new tiles) ===
    if nq < 4 and len(orders) < 10:
        land_costs = [1000, 2000, 4000]
        cost = land_costs[nq - 1] if nq <= 3 else 99999
        # Scale land with workforce: more workers = can service more tiles
        workforce_ready = (
            (nq == 1 and num_hands >= 6) or  # expand to Q2 when 6+ workers
            (nq == 2 and num_hands >= 8 and day >= 12) or  # Q3 when 8+ and mid-game
            (nq == 3 and num_hands >= 10 and day >= 16)  # Q4 when 10+ and late-mid
        )
        if workforce_ready and budget - spent >= cost + 500:
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
        # Remove assignments for workers that no longer exist (hands expired)
        self.assignments = {k: v for k, v in self.assignments.items() if k < num_workers}

        # Remove assignments whose target is no longer valid
        # (task already done by someone else, or tile state changed)
        stale_keys = []
        for wi, (target, task_type, action, pre) in self.assignments.items():
            if not self._task_still_valid(target, task_type, tiles, bs, shed):
                stale_keys.append(wi)
        for k in stale_keys:
            del self.assignments[k]

        # === GENERATE TASKS ===
        tasks = generate_tasks(tiles, bs, shed, seeds, day, remaining,
                               unlocked_quads, num_animals)
        is_endgame = remaining <= 1  # only last day is pure harvest mode

        # === EXECUTE assigned workers (they continue toward their target) ===
        actions = [None] * num_workers
        claimed_targets = set()

        for wi, (target, task_type, action_at, pre_action) in list(self.assignments.items()):
            claimed_targets.add(target)
            pos = all_positions[wi]
            inv = inventories[wi] if wi < len(inventories) else {}
            actions[wi] = self._execute_step(wi, pos, target, action_at, pre_action, inv, shed, bs, tiles)

        # === PRE-ASSIGN: Workers carrying fertilizer → fertilize premium plants ===
        if day >= 10 and not is_endgame:
            for wi in range(num_workers):
                if wi in self.assignments:
                    continue  # already has a task
                inv = inventories[wi] if wi < len(inventories) else {}
                if not isinstance(inv, dict) or inv.get("FERTILIZER", 0) <= 0:
                    continue
                pos = all_positions[wi]
                # Find nearest premium plant within 3 tiles
                best_plant = None
                best_d = 999
                for py in range(bs):
                    for px in range(bs):
                        pt = tiles[py][px]
                        if (isinstance(pt, dict) and pt.get("kind") == "PLANT"
                                and pt.get("crop") in ("STRAWBERRY", "MELON")
                                and (px, py) not in claimed_targets):
                            d = dist(pos, (px, py))
                            if d < best_d and d <= 1:
                                best_d = d
                                best_plant = (px, py)
                if best_plant:
                    claimed_targets.add(best_plant)
                    if pos == best_plant:
                        actions[wi] = ["FERTILIZE"]
                    else:
                        self.assignments[wi] = (best_plant, "FERTILIZE", "FERTILIZE", None)
                        step = first_step(pos, best_plant, bs)
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

                # Zone restriction: keep workers near their work area (reduces 57% movement)
                # Only FEED/BUILD/PLACE (prio>=275) bypass zone — they're critical infrastructure
                if prio < 275 and td > 3:
                    continue  # skip — too far, second pass handles it

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

        # Unassigned workers: fertilize premium plants if carrying fert, else drop items or pass
        # SECOND PASS: any idle worker grabs nearest unclaimed task (worker-first)
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

            # If carrying fertilizer and day >= 10, look for nearby premium plant
            if (inv.get("FERTILIZER", 0) > 0 and day >= 10 and not is_endgame):
                best_plant = None
                best_d = 999
                for py in range(bs):
                    for px in range(bs):
                        pt = tiles[py][px]
                        if (isinstance(pt, dict) and pt.get("kind") == "PLANT"
                                and pt.get("crop") in ("STRAWBERRY", "MELON")
                                and (px, py) not in claimed_targets):
                            d = dist(pos, (px, py))
                            if d < best_d and d <= 1:  # only adjacent
                                best_d = d
                                best_plant = (px, py)
                if best_plant:
                    claimed_targets.add(best_plant)
                    self.assignments[wi] = (best_plant, "FERTILIZE", "FERTILIZE", None)
                    if pos == best_plant:
                        del self.assignments[wi]
                        actions[wi] = ["FERTILIZE"]
                    else:
                        step = first_step(pos, best_plant, bs)
                        actions[wi] = [step] if step else ["PASS"]
                    continue

            # Fallback: drop items if carrying 3+ (get them to shed for selling)
            carried = sum(v for v in inv.values()) if isinstance(inv, dict) else 0
            if carried >= 3:
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
