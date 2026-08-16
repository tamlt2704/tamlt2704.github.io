"""Kaggriculture agent — Optimal Play: Melon Rush + Animal CARE Economy.

Strategy learned from best-play analysis:
- Melon = $118/day/tile (6x better than wheat!)
- Cow+Care = $105/day/tile (indefinite production, CARE doubles output)
- Sheep+Care = $93/day/tile
- Fertilizer from animals doubles melon yield (6→12 per tile)

Phases:
1. Day 0-1: Buy land, buy melon seeds, hire hands, build structures
2. Day 0-12: Plant melons everywhere, water during bonus window (days 5-12)
   Meanwhile: place animals, start FEED+CARE+COLLECT_FERTILIZER loop
3. Day 12+: Harvest melons (6 units × $250 = $1,500/tile), sell
4. Day 12-30: Replant with best available crop, maintain animal economy
"""

from collections import deque
import random as _random

# ─── Constants ───────────────────────────────────────────────────────────────

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


# ─── Utility ─────────────────────────────────────────────────────────────────

def get_farm(obs): return obs["farms"][obs["player"]]
def get_opp_farm(obs): return obs["farms"][1 - obs["player"]]

def shed_tiles(bs):
    h = bs // 2
    return [(h-1, h-1), (h, h-1), (h-1, h), (h, h)]

def is_shed_adj(pos, bs): return tuple(pos) in set(shed_tiles(bs))

def manhattan(p1, p2): return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

def bfs_step(start, target, bs):
    if start == target: return "PASS"
    parent = {start: None}
    q = deque([start])
    while q:
        x, y = q.popleft()
        if (x, y) == target: break
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < bs and 0 <= ny < bs and (nx, ny) not in parent:
                parent[(nx, ny)] = (x, y)
                q.append((nx, ny))
    if target not in parent: return "PASS"
    pos = target
    while parent[pos] != start: pos = parent[pos]
    dx, dy = pos[0]-start[0], pos[1]-start[1]
    if dx == 1: return "EAST"
    if dx == -1: return "WEST"
    if dy == 1: return "SOUTH"
    if dy == -1: return "NORTH"
    return "PASS"

def find_tiles(farm, pred):
    bs = len(farm["tiles"])
    r = []
    for y in range(bs):
        for x in range(bs):
            t = farm["tiles"][y][x]
            if pred(t): r.append((x, y, t))
    return r


# ─── Task Generation (Priority-based) ────────────────────────────────────────

def gen_tasks(farm, private, obs):
    """Generate tasks sorted by priority. Melon/animal-aware."""
    tasks = []
    bs = len(farm["tiles"])
    day = obs["day"]
    seeds = private.get("seeds", {})
    shed = private.get("shed", {})

    for y in range(bs):
        for x in range(bs):
            t = farm["tiles"][y][x]

            # HARVEST: highest priority — get product off tiles
            if isinstance(t, dict) and t.get("yield_units", 0) > 0:
                if t.get("kind") == "PLANT":
                    cd = CROPS.get(t.get("crop",""), {})
                    if day - t.get("planted_day", 0) >= cd.get("first_yield_day", 999):
                        # Melons are worth more — prioritize them
                        prio = 100 if t.get("crop") == "MELON" else 95
                        tasks.append((x, y, "HARVEST", prio))
                elif "animal" in t:
                    tasks.append((x, y, "HARVEST", 98))

            # FEED: critical — animals escape after 2 unfed days
            if isinstance(t, dict) and "animal" in t and not t.get("fed_today"):
                tasks.append((x, y, "FEED", 92))

            # CARE: huge value — doubles animal production
            if isinstance(t, dict) and "animal" in t and not t.get("cared_today"):
                tasks.append((x, y, "CARE", 88))

            # COLLECT_FERTILIZER: free fertilizer from animals
            if isinstance(t, dict) and "animal" in t and t.get("fertilizer_available"):
                tasks.append((x, y, "COLLECT_FERTILIZER", 60))

            # WATER: essential for plants
            if isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today"):
                cons = t.get("consecutive_unwatered", 0)
                # Dying plants (1 day unwatered) get highest water priority
                prio = 90 if cons >= 1 else 75
                # Melons in bonus window get extra priority
                if t.get("crop") == "MELON":
                    age = day - t.get("planted_day", 0)
                    if 5 <= age <= 12:  # Melon bonus window
                        prio = max(prio, 85)
                tasks.append((x, y, "WATER", prio))

            # FERTILIZE: use fertilizer on melons in bonus window
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                age = day - t.get("planted_day", 0)
                fert_day = t.get("fertilized_until_day", -1)
                if 5 <= age <= 12 and fert_day < day:
                    tasks.append((x, y, "FERTILIZE", 65))

            # PLANT: fill empty tiles
            if t is None and any(seeds.get(c, 0) > 0 for c in CROPS):
                tasks.append((x, y, "PLANT", 40))

            # BUILD: structures for animals in shed
            if t is None and any(shed.get(a, 0) > 0 for a in ANIMALS):
                for aname, adata in ANIMALS.items():
                    if shed.get(aname, 0) > 0:
                        tasks.append((x, y, "BUILD_" + adata["structure"], 55))
                        break

            # PLACE: animals onto structures
            if isinstance(t, dict) and t.get("kind") in ("COOP","PASTURE") and "animal" not in t:
                for aname, adata in ANIMALS.items():
                    if shed.get(aname, 0) > 0 and adata["structure"] == t["kind"]:
                        tasks.append((x, y, "PLACE_ANIMAL", 70))
                        break

            # DIG weeds
            if isinstance(t, dict) and t.get("kind") == "WEED":
                tasks.append((x, y, "DIG", 15))

    tasks.sort(key=lambda t: t[3], reverse=True)
    return tasks


# ─── Worker Assignment ────────────────────────────────────────────────────────

def assign_workers(workers, tasks):
    assignments = {}
    claimed = set()
    for tidx, (tx, ty, action, prio) in enumerate(tasks):
        best_w, best_d = None, 999
        for wi, (wx, wy) in enumerate(workers):
            if wi in assignments: continue
            d = manhattan((wx, wy), (tx, ty))
            if d < best_d: best_d, best_w = d, wi
        if best_w is not None:
            assignments[best_w] = (tx, ty, action)
            claimed.add(tidx)
    return assignments


def exec_task(wpos, tx, ty, action, farm, private, widx, obs, bs):
    """Execute assigned task or move toward it."""
    if wpos == (tx, ty):
        t = farm["tiles"][ty][tx]
        if action == "HARVEST": return ["HARVEST"]
        if action == "WATER": return ["WATER"]
        if action == "CARE": return ["CARE"]
        if action == "DIG": return ["DIG"]
        if action == "COLLECT_FERTILIZER": return ["COLLECT_FERTILIZER"]
        if action == "FERTILIZE":
            inv = private.get("inventories", [{}])
            wi = inv[widx] if widx < len(inv) else {}
            if wi.get("FERTILIZER", 0) > 0:
                return ["FERTILIZE"]
            # Pick up from shed
            if private.get("shed", {}).get("FERTILIZER", 0) > 0 and is_shed_adj(wpos, bs):
                return ["PICKUP", "FERTILIZER", 3]
            st = shed_tiles(bs)
            nearest = min(st, key=lambda s: manhattan(wpos, s))
            return [bfs_step(wpos, nearest, bs)]
        if action == "FEED":
            inv = private.get("inventories", [{}])
            wi = inv[widx] if widx < len(inv) else {}
            if wi.get("WHEAT", 0) > 0:
                return ["FEED"]
            if private.get("shed", {}).get("WHEAT", 0) > 0 and is_shed_adj(wpos, bs):
                return ["PICKUP", "WHEAT", 5]
            st = shed_tiles(bs)
            nearest = min(st, key=lambda s: manhattan(wpos, s))
            return [bfs_step(wpos, nearest, bs)]
        if action == "PLANT":
            seeds = private.get("seeds", {})
            best = _best_seed(seeds, obs)
            return ["PLANT", best] if best else ["PASS"]
        if action.startswith("BUILD_"):
            return [action]
        if action == "PLACE_ANIMAL":
            inv = private.get("inventories", [{}])
            wi = inv[widx] if widx < len(inv) else {}
            for a in ANIMALS:
                if wi.get(a, 0) > 0: return ["PLACE", a]
            if is_shed_adj(wpos, bs):
                for a in ANIMALS:
                    if private.get("shed", {}).get(a, 0) > 0:
                        return ["PICKUP", a, 1]
            st = shed_tiles(bs)
            nearest = min(st, key=lambda s: manhattan(wpos, s))
            return [bfs_step(wpos, nearest, bs)]
        return ["PASS"]
    return [bfs_step(wpos, (tx, ty), bs)]


def _best_seed(seeds, obs):
    """Pick best seed. Melon early, wheat/carrot late."""
    day = obs["day"]
    remaining = TOTAL_DAYS - day - 1
    # Prioritize melon if early enough to mature
    if seeds.get("MELON", 0) > 0 and remaining >= 12:
        return "MELON"
    if seeds.get("CARROT", 0) > 0 and remaining >= 3:
        return "CARROT"
    if seeds.get("WHEAT", 0) > 0 and remaining >= 2:
        return "WHEAT"
    # Fallback: any available seed that can still yield
    for c, cd in CROPS.items():
        if seeds.get(c, 0) > 0 and remaining >= cd["first_yield_day"]:
            return c
    return None


# ─── Market Planning ──────────────────────────────────────────────────────────

def plan_market(obs, farm, private):
    """Optimal market strategy: melon+animal economy."""
    orders = []
    day = obs["day"]
    remaining = TOTAL_DAYS - day - 1
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    money = farm["money"]
    num_hands = len(farm.get("hands", []))
    num_quads = len(farm.get("unlocked_quadrants", []))
    animals_on_farm = len(find_tiles(farm, lambda t: isinstance(t, dict) and "animal" in t))
    spent = 0

    # ── SELL products ──
    wheat_reserve = animals_on_farm * 2
    for product in PRODUCTS:
        qty = shed.get(product, 0)
        if qty <= 0: continue
        if product == "WHEAT":
            sellable = max(0, qty - wheat_reserve)
        elif product == "FERTILIZER":
            # Keep fertilizer for own melons
            melon_count = len(find_tiles(farm, lambda t: isinstance(t, dict) and t.get("crop") == "MELON"))
            sellable = max(0, qty - melon_count)
        else:
            sellable = qty
        sell_qty = min(sellable, 8 if remaining <= 5 else 5)
        if sell_qty > 0:
            orders.append(["SELL", product, sell_qty])

    # Sell unplaceable animals
    for aname, adata in ANIMALS.items():
        in_shed = shed.get(aname, 0)
        if in_shed > 0:
            empty = len(find_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == adata["structure"] and "animal" not in t))
            excess = in_shed - empty
            if excess > 0:
                orders.append(["SELL", aname, excess])

    # ── BUY LAND (aggressive early — more tiles = more melons) ──
    if num_quads < 4 and remaining > 12:
        cost = LAND_PRICES[num_quads - 1]
        if money - spent >= cost + 300:
            orders.append(["BUY_LAND"])
            spent += cost

    # ── BUY MELON SEEDS (primary crop) ──
    plantable = len(find_tiles(farm, lambda t: t is None))
    if remaining >= 13:  # Melons need 12 days + 1 to harvest
        melon_seeds_have = seeds.get("MELON", 0)
        melon_need = min(plantable, 10) - melon_seeds_have
        if melon_need > 0 and money - spent >= 80 * melon_need:
            orders.append(["BUY_SEED", "MELON", melon_need])
            spent += 80 * melon_need

    # ── BUY ANIMALS (cow/sheep are $100+/day/tile with CARE) ──
    # Only buy if we can build structures for them
    if remaining > 10 and money - spent >= 500:
        empty_pastures = len(find_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PASTURE" and "animal" not in t))
        cows_in_shed = shed.get("COW", 0)
        if empty_pastures > cows_in_shed and money - spent >= 400:
            orders.append(["BUY_ANIMAL", "COW", 1])
            spent += 400

    # ── BUY WHEAT/CARROT seeds for late game (after melon harvest) ──
    if remaining < 13 and remaining >= 3:
        carrot_have = seeds.get("CARROT", 0)
        wheat_have = seeds.get("WHEAT", 0)
        need = min(plantable, 8) - carrot_have - wheat_have
        if need > 0:
            # Carrot is slightly better ROI than wheat
            buy = min(need, int((money - spent) // 20))
            if buy > 0:
                orders.append(["BUY_SEED", "CARROT", buy])
                spent += buy * 20

    # ── BUY WHEAT for animal feed ──
    if animals_on_farm > 0 and shed.get("WHEAT", 0) < animals_on_farm * 2:
        need = animals_on_farm * 2 - shed.get("WHEAT", 0)
        wheat_price = obs["market"]["prices"].get("WHEAT", 25)
        if money - spent >= wheat_price * need:
            orders.append(["BUY_PRODUCT", "WHEAT", min(need, 5)])
            spent += wheat_price * min(need, 5)

    # ── HIRE hands (cheap and massively boost throughput) ──
    active_plants = len(find_tiles(farm, lambda t: isinstance(t, dict) and t.get("kind") == "PLANT"))
    workload = active_plants + animals_on_farm * 3  # Animals need FEED+CARE+COLLECT
    if num_hands == 0 and workload >= 2 and remaining > 2:
        fib = _fib(farm.get("hires_today", 0))
        if money - spent >= fib:
            orders.append(["HIRE"])
            spent += fib
            # Second hand
            fib2 = _fib(farm.get("hires_today", 0) + 1)
            if workload >= 5 and money - spent >= fib2:
                orders.append(["HIRE"])
                spent += fib2
                # Third hand for heavy workloads
                fib3 = _fib(farm.get("hires_today", 0) + 2)
                if workload >= 10 and money - spent >= fib3:
                    orders.append(["HIRE"])
                    spent += fib3

    return orders[:10]


def _fib(n):
    a, b = 1, 1
    for _ in range(n): a, b = b, a + b
    return a


# ─── Main Agent ───────────────────────────────────────────────────────────────

def agent(obs, config=None):
    farm = get_farm(obs)
    private = obs.get("private", {})
    bs = len(farm["tiles"])

    # Task generation
    tasks = gen_tasks(farm, private, obs)

    # Workers
    farmer_pos = tuple(farm["farmer"])
    hands = farm.get("hands", [])
    workers = [farmer_pos] + [tuple(h) for h in hands]
    inventories = private.get("inventories", [{}])

    # Actions
    actions = [None] * len(workers)

    # Drop-off at shed if carrying items
    for wi, wpos in enumerate(workers):
        if wi < len(inventories):
            inv = inventories[wi]
            if inv and sum(inv.values()) > 0 and is_shed_adj(wpos, bs):
                actions[wi] = ["DROP"]

    # Assign free workers to tasks
    avail = [(i, workers[i]) for i in range(len(workers)) if actions[i] is None]
    if avail and tasks:
        avail_pos = [p for _, p in avail]
        avail_idx = [i for i, _ in avail]
        asgn = assign_workers(avail_pos, tasks)
        for li, (tx, ty, act) in asgn.items():
            gi = avail_idx[li]
            cmd = exec_task(workers[gi], tx, ty, act, farm, private, gi, obs, bs)
            actions[gi] = cmd

    # Idle workers go to shed
    for wi in range(len(workers)):
        if actions[wi] is None:
            inv = inventories[wi] if wi < len(inventories) else {}
            if inv and sum(inv.values()) > 0:
                st = shed_tiles(bs)
                nearest = min(st, key=lambda s: manhattan(workers[wi], s))
                actions[wi] = [bfs_step(workers[wi], nearest, bs)]
            else:
                actions[wi] = ["PASS"]

    # Market
    market_orders = plan_market(obs, farm, private)

    return {
        "farmer": actions[0] if actions else ["PASS"],
        "hands": actions[1:] if len(actions) > 1 else [],
        "market": market_orders,
    }
